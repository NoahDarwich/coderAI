"""
Extraction service for orchestrating LLM calls to extract values from documents.

This service coordinates the extraction process by:
1. Getting the document and variable
2. Loading the appropriate prompt
3. Calling the LLM with the prompt and document text
4. Storing the extraction result
"""
import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.document import Document
from src.models.extraction import Extraction
from src.models.prompt import Prompt
from src.models.variable import Variable
from src.services.llm_client import (
    LLMClient,
    LLMClientError,
    create_llm_client,
)

logger = logging.getLogger(__name__)


class ExtractionService:
    """
    Service for extracting values from documents using LLM.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize extraction service.

        Args:
            db: Database session
        """
        self.db = db

    async def extract_value(
        self,
        document_id: UUID,
        variable_id: UUID,
        job_id: UUID,
    ) -> Extraction:
        """
        Extract a single value from a document for a variable.

        Args:
            document_id: Document UUID
            variable_id: Variable UUID
            job_id: Processing job UUID (for tracking)

        Returns:
            Extraction record

        Raises:
            ValueError: If document or variable not found
            LLMClientError: If LLM extraction fails
        """
        # Get document
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise ValueError(f"Document with id {document_id} not found")

        # Get variable
        result = await self.db.execute(
            select(Variable).where(Variable.id == variable_id)
        )
        variable = result.scalar_one_or_none()

        if not variable:
            raise ValueError(f"Variable with id {variable_id} not found")

        # Get current prompt (highest version)
        result = await self.db.execute(
            select(Prompt)
            .where(Prompt.variable_id == variable_id)
            .order_by(Prompt.version.desc())
            .limit(1)
        )
        prompt = result.scalar_one_or_none()

        if not prompt:
            raise ValueError(
                f"No prompt found for variable {variable_id}. Variable must have at least one prompt."
            )

        # Create LLM client with prompt's model config
        llm_client = create_llm_client(prompt.model_config)

        # Call LLM to extract value
        try:
            result = await llm_client.extract(
                prompt_text=prompt.prompt_text,
                document_text=document.content,
            )

            # Convert value to string (for database storage)
            value_str = self._serialize_value(result.value)

            # Create extraction record
            extraction = Extraction(
                job_id=job_id,
                document_id=document_id,
                variable_id=variable_id,
                value=value_str,
                confidence=result.confidence,
                source_text=result.source_text[:2000] if result.source_text else None,  # Truncate to 2000 chars
            )

            self.db.add(extraction)
            await self.db.flush()

            logger.info(
                f"Extraction successful: document={document_id}, variable={variable_id}, confidence={result.confidence}"
            )

            return extraction

        except LLMClientError as e:
            # LLM extraction failed - create extraction with null value
            logger.error(
                f"Extraction failed: document={document_id}, variable={variable_id}, error={str(e)}"
            )

            extraction = Extraction(
                job_id=job_id,
                document_id=document_id,
                variable_id=variable_id,
                value=None,
                confidence=None,
                source_text=None,
            )

            self.db.add(extraction)
            await self.db.flush()

            # Re-raise error for job manager to log
            raise

    def _serialize_value(self, value: Optional[any]) -> Optional[str]:
        """
        Serialize extracted value to string for database storage.

        Args:
            value: Extracted value (can be string, number, boolean, list, or None)

        Returns:
            String representation of value, or None
        """
        if value is None:
            return None

        if isinstance(value, bool):
            # Store boolean as "true" or "false" (lowercase)
            return "true" if value else "false"

        if isinstance(value, (int, float)):
            # Store numbers as strings
            return str(value)

        if isinstance(value, list):
            # Store lists as JSON strings (for category arrays)
            import json
            return json.dumps(value)

        # Default: convert to string
        return str(value)
