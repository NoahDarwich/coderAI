"""
Extraction agent — thin LangChain wrapper around extraction logic.

This module re-exports the existing TextExtractionService through a LangChain-aware
interface for consistency with the agents package. The core extraction logic
remains in src/services/text_extraction_service.py.
"""
import logging
from typing import Any, Dict, List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.core.config import settings
from src.models.variable import Variable
from src.services.text_extraction_service import TextExtractionService, create_extraction_service

logger = logging.getLogger(__name__)


class ExtractionAgent:
    """
    LangChain-based extraction agent.

    Wraps TextExtractionService to provide a unified agent interface.
    For now delegates to the existing service; future versions may use
    LangChain chains or tool-calling for complex extraction.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.service = create_extraction_service(api_key=api_key)
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL or "gpt-4",
            temperature=0.1,
            api_key=api_key or settings.OPENAI_API_KEY,
        )

    async def extract(
        self,
        text: str,
        variable: Variable,
        prompt_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Extract a single variable from text."""
        return await self.service.extract_variable(
            text=text,
            variable=variable,
            prompt_text=prompt_text,
        )

    async def extract_all(
        self,
        text: str,
        variables: List[Variable],
        prompts: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """Extract all variables from text."""
        return await self.service.extract_all_variables(
            text=text,
            variables=variables,
            prompts=prompts,
        )

    async def identify_entities(
        self,
        text: str,
        entity_pattern: str,
    ) -> List[Dict[str, Any]]:
        """Identify entities in text."""
        return await self.service.identify_entities(
            text=text,
            entity_pattern=entity_pattern,
        )
