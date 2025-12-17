"""
LLM client service with LangChain integration and retry logic.

This service provides a unified interface for calling LLM APIs (OpenAI, Anthropic)
with structured output parsing, retry logic, and error handling.
"""
import asyncio
import json
import logging
import random
from typing import Any, Dict, Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, ValidationError

from src.core.config import settings

logger = logging.getLogger(__name__)


class ExtractionResult(BaseModel):
    """Structured output format for LLM extractions."""

    value: Optional[Any] = Field(description="Extracted value (can be string, number, boolean, list, or null)")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    source_text: Optional[str] = Field(description="Source excerpt from document")


class LLMClientError(Exception):
    """Base exception for LLM client errors."""

    pass


class LLMRateLimitError(LLMClientError):
    """Raised when LLM API rate limit is exceeded."""

    pass


class LLMParseError(LLMClientError):
    """Raised when LLM response cannot be parsed."""

    pass


class LLMClient:
    """
    LLM client with retry logic and structured output parsing.
    """

    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.2,
        max_tokens: int = 1000,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
    ):
        """
        Initialize LLM client.

        Args:
            model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            max_retries: Maximum retry attempts (default: 3)
            base_delay: Base delay for exponential backoff in seconds (default: 1.0)
            max_delay: Maximum delay for exponential backoff in seconds (default: 10.0)
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

        # Initialize LangChain ChatOpenAI
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=settings.OPENAI_API_KEY,
            request_timeout=30.0,
        )

        # Initialize output parser for structured extraction
        self.output_parser = PydanticOutputParser(pydantic_object=ExtractionResult)

    async def extract(
        self, prompt_text: str, document_text: str
    ) -> ExtractionResult:
        """
        Extract structured information from document using LLM.

        Implements retry logic with exponential backoff and jitter.

        Args:
            prompt_text: Extraction prompt (contains {{document_text}} placeholder)
            document_text: Document content to extract from

        Returns:
            ExtractionResult with value, confidence, and source_text

        Raises:
            LLMClientError: If extraction fails after all retries
            LLMRateLimitError: If rate limit exceeded
            LLMParseError: If response cannot be parsed
        """
        # Replace placeholder in prompt
        full_prompt = prompt_text.replace("{{document_text}}", document_text)

        # Retry loop with exponential backoff
        last_error = None

        for attempt in range(self.max_retries):
            try:
                # Call LLM
                response = await self.llm.ainvoke(full_prompt)

                # Parse response
                result = self._parse_response(response.content)

                logger.info(f"Extraction successful on attempt {attempt + 1}")
                return result

            except LLMRateLimitError as e:
                # Rate limit error - always retry
                last_error = e
                logger.warning(
                    f"Rate limit exceeded on attempt {attempt + 1}/{self.max_retries}"
                )

            except LLMParseError as e:
                # Parse error - retry once, then fail
                last_error = e
                if attempt == 0:
                    logger.warning(
                        f"Parse error on attempt {attempt + 1}, retrying: {str(e)}"
                    )
                else:
                    logger.error(f"Parse error on attempt {attempt + 1}, giving up")
                    raise

            except Exception as e:
                # Other errors - check if retryable
                last_error = e

                if self._is_retryable_error(e):
                    logger.warning(
                        f"Retryable error on attempt {attempt + 1}/{self.max_retries}: {str(e)}"
                    )
                else:
                    logger.error(f"Non-retryable error: {str(e)}")
                    raise LLMClientError(f"LLM request failed: {str(e)}")

            # Calculate delay with exponential backoff and jitter
            if attempt < self.max_retries - 1:
                delay = self._calculate_backoff_delay(attempt)
                logger.info(f"Waiting {delay:.2f}s before retry {attempt + 2}")
                await asyncio.sleep(delay)

        # All retries exhausted
        raise LLMClientError(
            f"Extraction failed after {self.max_retries} attempts: {str(last_error)}"
        )

    def _parse_response(self, response_text: str) -> ExtractionResult:
        """
        Parse LLM response into ExtractionResult.

        Args:
            response_text: Raw LLM response

        Returns:
            Parsed ExtractionResult

        Raises:
            LLMParseError: If parsing fails
        """
        try:
            # Try to extract JSON from response
            # Handle cases where LLM adds explanatory text before/after JSON
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                raise LLMParseError("No JSON object found in response")

            json_text = response_text[json_start:json_end]

            # Parse JSON
            data = json.loads(json_text)

            # Validate with Pydantic
            result = ExtractionResult(**data)

            return result

        except json.JSONDecodeError as e:
            raise LLMParseError(f"Invalid JSON in response: {str(e)}")
        except ValidationError as e:
            raise LLMParseError(f"Response validation failed: {str(e)}")
        except Exception as e:
            raise LLMParseError(f"Failed to parse response: {str(e)}")

    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Determine if an error is retryable.

        Args:
            error: Exception raised during LLM call

        Returns:
            True if error is retryable, False otherwise
        """
        error_str = str(error).lower()

        # Retryable errors
        retryable_patterns = [
            "timeout",
            "connection",
            "503",  # Service unavailable
            "502",  # Bad gateway
            "500",  # Internal server error
            "429",  # Rate limit (handled separately)
        ]

        return any(pattern in error_str for pattern in retryable_patterns)

    def _calculate_backoff_delay(self, attempt: int) -> float:
        """
        Calculate delay for exponential backoff with jitter.

        Formula: min(base_delay * 2^attempt + jitter, max_delay)
        Jitter: random(0, delay * 0.1)

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        # Exponential backoff
        delay = self.base_delay * (2**attempt)

        # Add jitter (10% of delay)
        jitter = random.uniform(0, delay * 0.1)
        delay += jitter

        # Cap at max_delay
        return min(delay, self.max_delay)


def create_llm_client(model_config: Dict[str, Any]) -> LLMClient:
    """
    Factory function to create LLM client from model configuration.

    Args:
        model_config: Model configuration dictionary with keys:
            - model: Model name
            - temperature: Sampling temperature
            - max_tokens: Maximum tokens

    Returns:
        Configured LLMClient instance
    """
    return LLMClient(
        model=model_config.get("model", "gpt-4"),
        temperature=model_config.get("temperature", 0.2),
        max_tokens=model_config.get("max_tokens", 1000),
        max_retries=3,
        base_delay=1.0,
        max_delay=10.0,
    )
