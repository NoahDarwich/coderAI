"""
Text Extraction Service using OpenAI API.

This service mimics the pattern from reference_backend/response_openai.py
for extracting structured data from text using LLM prompts.
"""
import json
import os
import re
from typing import Any, Dict, List, Optional

from openai import OpenAI

from src.core.config import settings
from src.models.variable import Variable, VariableType


class TextExtractionService:
    """
    Service for extracting structured data from text using OpenAI API.

    Similar to ExtractInfoResponses from reference backend.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the extraction service with OpenAI client."""
        self.client = OpenAI(api_key=api_key or settings.OPENAI_API_KEY)
        self.default_model = "gpt-4o"  # Use GPT-4o for better extraction
        self.default_temperature = 0.1
        self.default_top_p = 0.2

    def extract_variable(
        self,
        text: str,
        variable: Variable,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Extract a single variable from text using OpenAI.

        Args:
            text: The text content to extract from
            variable: Variable definition with instructions
            max_retries: Maximum number of retry attempts

        Returns:
            Dict with keys: value, confidence (0-100), source_text, raw_response
        """
        # Build prompt based on variable type
        system_prompt = self._build_system_prompt(variable)
        user_prompt = self._build_user_prompt(text, variable)

        # Call OpenAI API with retries
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.default_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=self.default_temperature,
                    top_p=self.default_top_p,
                    response_format={"type": "json_object"},
                )

                # Parse response
                response_text = response.choices[0].message.content
                if not response_text:
                    continue

                result = self._parse_response(response_text, variable)
                return result

            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying...")
                    continue
                else:
                    print(f"API call failed after {max_retries} attempts: {e}")
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

    def extract_all_variables(
        self,
        text: str,
        variables: List[Variable],
    ) -> List[Dict[str, Any]]:
        """
        Extract all variables from text.

        Args:
            text: The text content to extract from
            variables: List of variable definitions

        Returns:
            List of extraction results, one per variable
        """
        results = []

        for variable in variables:
            extraction = self.extract_variable(text, variable)
            extraction["variable_id"] = str(variable.id)
            extraction["variable_name"] = variable.name
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

    def _parse_response(self, response_text: str, variable: Variable) -> Dict[str, Any]:
        """Parse and clean the API response."""
        # Clean response (remove markdown code blocks if present)
        cleaned_response = re.sub(r'```json\s*', '', response_text)
        cleaned_response = re.sub(r'```\s*$', '', cleaned_response)
        cleaned_response = cleaned_response.strip()

        try:
            parsed = json.loads(cleaned_response)

            # Ensure required fields exist
            result = {
                "value": parsed.get("value"),
                "confidence": int(parsed.get("confidence", 50)),  # 0-100 scale
                "source_text": parsed.get("source_text"),
                "explanation": parsed.get("explanation", ""),
                "raw_response": response_text,
            }

            # Validate confidence is in range
            result["confidence"] = max(0, min(100, result["confidence"]))

            return result

        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Response was: {response_text[:200]}...")

            return {
                "value": None,
                "confidence": 0,
                "source_text": None,
                "error": f"JSON parse error: {str(e)}",
                "raw_response": response_text,
            }


# Factory function
def create_extraction_service(api_key: Optional[str] = None) -> TextExtractionService:
    """Create and return a TextExtractionService instance."""
    return TextExtractionService(api_key=api_key)
