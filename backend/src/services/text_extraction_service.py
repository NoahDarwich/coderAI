"""
Text Extraction Service using OpenAI API with circuit breaker protection.
"""
import asyncio
import logging
import time
from enum import Enum
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from src.core.config import settings
from src.models.variable import Variable, VariableType
from src.services.response_parser import parse_extraction_response

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    Circuit breaker for LLM API calls.

    - CLOSED: Normal operation. Failures increment counter.
    - OPEN: After failure_threshold reached. All calls fail fast for reset_timeout seconds.
    - HALF_OPEN: After reset_timeout, allow success_threshold calls through to test recovery.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: float = 30.0,
        success_threshold: int = 3,
    ):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.success_threshold = success_threshold
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float = 0

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if time.monotonic() - self._last_failure_time >= self.reset_timeout:
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0
                logger.info("Circuit breaker transitioning to HALF_OPEN")
        return self._state

    def record_success(self) -> None:
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.success_threshold:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                logger.info("Circuit breaker CLOSED (recovered)")
        else:
            self._failure_count = 0

    def record_failure(self) -> None:
        self._failure_count += 1
        self._last_failure_time = time.monotonic()
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            logger.warning("Circuit breaker re-OPENED from HALF_OPEN")
        elif self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            logger.warning(f"Circuit breaker OPENED after {self._failure_count} failures")

    def check(self) -> bool:
        """Return True if the call should proceed, False if circuit is open."""
        return self.state != CircuitState.OPEN


# Global circuit breaker instance
_circuit_breaker = CircuitBreaker()


class TextExtractionService:
    """Service for extracting structured data from text using OpenAI API."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key or settings.OPENAI_API_KEY)
        self.default_model = "gpt-4o"
        self.default_temperature = 0.1
        self.default_top_p = 0.2

    async def extract_variable(
        self,
        text: str,
        variable: Variable,
        prompt_text: Optional[str] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Extract a single variable from text using OpenAI.
        Includes circuit breaker check and exponential backoff retry.
        """
        # Circuit breaker check
        if not _circuit_breaker.check():
            logger.warning("Circuit breaker OPEN — skipping LLM call")
            return {
                "value": None,
                "confidence": 0,
                "source_text": None,
                "error": "Circuit breaker open — LLM temporarily unavailable",
            }

        if prompt_text:
            system_prompt = prompt_text
        else:
            system_prompt = self._build_system_prompt(variable)
        user_prompt = self._build_user_prompt(text, variable)

        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.default_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=self.default_temperature,
                    top_p=self.default_top_p,
                    response_format={"type": "json_object"},
                )

                response_text = response.choices[0].message.content
                if not response_text:
                    continue

                result = parse_extraction_response(response_text)
                _circuit_breaker.record_success()
                return result

            except Exception as e:
                _circuit_breaker.record_failure()
                if attempt < max_retries - 1:
                    delay = min(2 ** attempt, settings.LLM_RETRY_MAX_DELAY)
                    logger.warning(
                        f"API call failed (attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)

                    # Re-check circuit breaker before retry
                    if not _circuit_breaker.check():
                        logger.warning("Circuit breaker opened during retries")
                        return {
                            "value": None,
                            "confidence": 0,
                            "source_text": None,
                            "error": "Circuit breaker open — LLM temporarily unavailable",
                        }
                else:
                    logger.error(f"API call failed after {max_retries} attempts: {e}")
                    return {
                        "value": None,
                        "confidence": 0,
                        "source_text": None,
                        "error": str(e),
                    }

        return {
            "value": None,
            "confidence": 0,
            "source_text": None,
            "error": "Max retries exceeded",
        }

    async def identify_entities(
        self,
        text: str,
        entity_pattern: str,
        max_retries: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Identify entities in text using LLM with entity_identification_pattern.

        Args:
            text: Document text
            entity_pattern: Description of what constitutes an entity
            max_retries: Max retry attempts

        Returns:
            List of dicts with 'index', 'text' (entity excerpt), 'label'
        """
        if not _circuit_breaker.check():
            logger.warning("Circuit breaker OPEN — skipping entity identification")
            return []

        system_prompt = f"""You are an entity identification assistant. Your task is to identify distinct entities in the document.

Entity Definition: {entity_pattern}

Return a JSON object with this structure:
{{
    "entities": [
        {{"index": 0, "label": "short label for entity", "text": "relevant excerpt identifying this entity (max 200 chars)"}},
        {{"index": 1, "label": "short label for entity", "text": "relevant excerpt identifying this entity (max 200 chars)"}}
    ]
}}

Rules:
1. Each entity should be a distinct instance matching the pattern
2. Assign sequential index values starting at 0
3. Include enough text to uniquely identify each entity
4. If no entities found, return {{"entities": []}}
5. Respond ONLY with valid JSON
"""
        user_prompt = f"Identify all entities in this document:\n\n{text}"

        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.default_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"},
                )

                import json
                response_text = response.choices[0].message.content
                if not response_text:
                    continue

                result = json.loads(response_text)
                entities = result.get("entities", [])
                _circuit_breaker.record_success()
                return entities

            except Exception as e:
                _circuit_breaker.record_failure()
                if attempt < max_retries - 1:
                    delay = min(2 ** attempt, settings.LLM_RETRY_MAX_DELAY)
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Entity identification failed after {max_retries} attempts: {e}")
                    return []

        return []

    async def extract_variable_for_entity(
        self,
        text: str,
        variable: Variable,
        entity: Dict[str, Any],
        prompt_text: Optional[str] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Extract a variable for a specific entity within the text.

        Args:
            text: Document text
            variable: Variable to extract
            entity: Entity dict with 'index', 'text', 'label'
            prompt_text: Optional pre-built prompt
            max_retries: Max retry attempts

        Returns:
            Extraction result dict
        """
        # Build entity-aware user prompt
        entity_context = f"\n\nFocus on this specific entity: {entity.get('label', 'Unknown')}\nEntity context: {entity.get('text', '')}\n"

        if prompt_text:
            system_prompt = prompt_text + entity_context
        else:
            system_prompt = self._build_system_prompt(variable) + entity_context

        user_prompt = self._build_user_prompt(text, variable)

        if not _circuit_breaker.check():
            return {
                "value": None,
                "confidence": 0,
                "source_text": None,
                "error": "Circuit breaker open",
            }

        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.default_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=self.default_temperature,
                    top_p=self.default_top_p,
                    response_format={"type": "json_object"},
                )

                response_text = response.choices[0].message.content
                if not response_text:
                    continue

                result = parse_extraction_response(response_text)
                _circuit_breaker.record_success()
                return result

            except Exception as e:
                _circuit_breaker.record_failure()
                if attempt < max_retries - 1:
                    delay = min(2 ** attempt, settings.LLM_RETRY_MAX_DELAY)
                    await asyncio.sleep(delay)
                    if not _circuit_breaker.check():
                        return {
                            "value": None,
                            "confidence": 0,
                            "source_text": None,
                            "error": "Circuit breaker open",
                        }
                else:
                    return {
                        "value": None,
                        "confidence": 0,
                        "source_text": None,
                        "error": str(e),
                    }

        return {"value": None, "confidence": 0, "source_text": None, "error": "Max retries exceeded"}

    async def extract_all_variables(
        self,
        text: str,
        variables: List[Variable],
        prompts: Optional[Dict[str, str]] = None,
        parallel: bool = True,
        max_concurrency: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Extract all variables from text.

        Args:
            text: Document text
            variables: List of variables to extract
            prompts: Optional mapping of variable_id -> prompt_text
            parallel: If True, extract variables concurrently
            max_concurrency: Max concurrent LLM calls

        Returns:
            List of extraction result dicts
        """
        async def _extract_one(variable: Variable) -> Dict[str, Any]:
            prompt_text = prompts.get(str(variable.id)) if prompts else None
            extraction = await self.extract_variable(
                text, variable, prompt_text=prompt_text
            )
            extraction["variable_id"] = str(variable.id)
            extraction["variable_name"] = variable.name
            return extraction

        if parallel and len(variables) > 1:
            semaphore = asyncio.Semaphore(max_concurrency)

            async def _limited(variable: Variable) -> Dict[str, Any]:
                async with semaphore:
                    return await _extract_one(variable)

            results = await asyncio.gather(
                *[_limited(v) for v in variables],
                return_exceptions=True,
            )
            # Convert exceptions to error results
            final = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    final.append({
                        "variable_id": str(variables[i].id),
                        "variable_name": variables[i].name,
                        "value": None,
                        "confidence": 0,
                        "source_text": None,
                        "error": str(result),
                    })
                else:
                    final.append(result)
            return final
        else:
            results = []
            for variable in variables:
                extraction = await _extract_one(variable)
                results.append(extraction)
            return results

    def _build_system_prompt(self, variable: Variable) -> str:
        """Build system prompt based on variable type and instructions."""
        base_prompt = f"""You are a data extraction assistant. Your task is to extract specific information from text.

Variable to extract: {variable.name}
Variable type: {variable.type.value}
Instructions: {variable.instructions}

"""

        if variable.type == VariableType.DATE:
            base_prompt += """
Extract dates in ISO format (YYYY-MM-DD). If relative dates are mentioned (e.g., "yesterday", "last week"),
note them but also try to infer actual dates if context allows.

Return your response as JSON with this structure:
{
    "value": "extracted date in YYYY-MM-DD format or null if not found",
    "confidence": 85,  // confidence score 0-100
    "source_text": "the exact text segment where this information was found",
    "explanation": "brief explanation of your extraction"
}
"""

        elif variable.type == VariableType.CATEGORY:
            categories = []
            if variable.classification_rules:
                categories = variable.classification_rules.get("categories", [])

            base_prompt += f"""
Classify the text into one of these categories: {', '.join(categories)}

Return your response as JSON with this structure:
{{
    "value": "selected category or null if none match",
    "confidence": 85,  // confidence score 0-100
    "source_text": "the exact text segment that supports this classification",
    "explanation": "brief explanation of why this category was chosen"
}}
"""

        elif variable.type == VariableType.NUMBER:
            base_prompt += """
Extract numeric values. Return only the number without units unless specifically required.

Return your response as JSON with this structure:
{
    "value": "extracted number as string or null if not found",
    "confidence": 85,  // confidence score 0-100
    "source_text": "the exact text segment where this number was found",
    "explanation": "brief explanation"
}
"""

        elif variable.type == VariableType.BOOLEAN:
            base_prompt += """
Determine if the statement is true or false based on the text.

Return your response as JSON with this structure:
{
    "value": "true" or "false" or null if cannot determine,
    "confidence": 85,  // confidence score 0-100
    "source_text": "the exact text segment supporting this determination",
    "explanation": "brief explanation"
}
"""

        else:  # TEXT or default
            base_prompt += """
Extract the requested information as text.

Return your response as JSON with this structure:
{
    "value": "extracted text or null if not found",
    "confidence": 85,  // confidence score 0-100
    "source_text": "the exact text segment where this information was found",
    "explanation": "brief explanation"
}
"""

        base_prompt += """
IMPORTANT RULES:
1. Only extract information explicitly stated or strongly implied in the text
2. If information is not present, set value to null
3. Provide realistic confidence scores (0-100)
4. Always include the source_text showing where you found the information
5. Respond ONLY with valid JSON, no additional text
"""

        return base_prompt

    def _build_user_prompt(self, text: str, variable: Variable) -> str:
        """Build user prompt with the text to analyze."""
        return f"""Please analyze the following text and extract the requested information:

TEXT TO ANALYZE:
---
{text}
---

Extract: {variable.name}
Instructions: {variable.instructions}

Remember to respond with valid JSON only.
"""


def create_extraction_service(api_key: Optional[str] = None) -> TextExtractionService:
    """Create and return a TextExtractionService instance."""
    return TextExtractionService(api_key=api_key)
