"""
Export service for aggregating extractions and generating export files.
"""
import json
import logging
from io import BytesIO
from typing import List, Optional
from uuid import UUID

import pandas as pd
from openpyxl import Workbook
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.document import Document
from src.models.extraction import Extraction
from src.models.project import Project
from src.models.variable import Variable

logger = logging.getLogger(__name__)


class ExportService:
    """
    Service for aggregating extractions and generating export files.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize export service.

        Args:
            db: Database session
        """
        self.db = db

    async def aggregate_extractions(
        self,
        project_id: UUID,
        include_confidence: bool = False,
        include_source_text: bool = False,
        min_confidence: Optional[float] = None,
    ) -> pd.DataFrame:
        """
        Aggregate all extractions for a project into a pandas DataFrame.

        Args:
            project_id: Project UUID
            include_confidence: Include confidence scores
            include_source_text: Include source text excerpts
            min_confidence: Optional minimum confidence threshold

        Returns:
            DataFrame with extractions

        Raises:
            ValueError: If project not found
        """
        # Verify project exists
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise ValueError(f"Project with id {project_id} not found")

        # Get all variables for project
        result = await self.db.execute(
            select(Variable)
            .where(Variable.project_id == project_id)
            .order_by(Variable.order)
        )
        variables = result.scalars().all()

        if not variables:
            raise ValueError(f"No variables defined for project {project_id}")

        # Get all documents for project
        result = await self.db.execute(
            select(Document)
            .where(Document.project_id == project_id)
            .order_by(Document.uploaded_at)
        )
        documents = result.scalars().all()

        if not documents:
            raise ValueError(f"No documents found for project {project_id}")

        # Build query for extractions
        query = (
            select(Extraction, Document, Variable)
            .join(Document, Extraction.document_id == Document.id)
            .join(Variable, Extraction.variable_id == Variable.id)
            .where(Document.project_id == project_id)
        )

        # Apply confidence filter if provided
        if min_confidence is not None:
            query = query.where(Extraction.confidence >= min_confidence)

        # Execute query
        result = await self.db.execute(query)
        rows = result.all()

        # Build data for DataFrame
        data = []
        for extraction, document, variable in rows:
            # Handle JSONB values: serialize complex types to string for export
            value = extraction.value
            if isinstance(value, (dict, list)):
                value = json.dumps(value, default=str)

            row = {
                "document_id": str(document.id),
                "document_name": document.name,
                "variable_name": variable.name,
                "value": value,
            }

            if include_confidence:
                row["confidence"] = extraction.confidence

            if include_source_text:
                row["source_text"] = extraction.source_text

            data.append(row)

        # Create DataFrame
        df = pd.DataFrame(data)

        logger.info(f"Aggregated {len(df)} extractions for project {project_id}")

        return df

    async def generate_csv_wide(
        self,
        project_id: UUID,
        include_confidence: bool = False,
        include_source_text: bool = False,
        min_confidence: Optional[float] = None,
    ) -> bytes:
        """
        Generate CSV export in wide format (1 row per document, columns = variables).

        Args:
            project_id: Project UUID
            include_confidence: Include confidence scores
            include_source_text: Include source text excerpts
            min_confidence: Optional minimum confidence threshold

        Returns:
            CSV file content as bytes
        """
        # Get aggregated data
        df = await self.aggregate_extractions(
            project_id=project_id,
            include_confidence=include_confidence,
            include_source_text=include_source_text,
            min_confidence=min_confidence,
        )

        # Pivot to wide format
        index_cols = ["document_id", "document_name"]
        value_cols = ["value"]

        if include_confidence:
            # Create separate columns for value and confidence
            pivot_value = df.pivot(
                index=index_cols,
                columns="variable_name",
                values="value"
            )

            pivot_confidence = df.pivot(
                index=index_cols,
                columns="variable_name",
                values="confidence"
            )

            # Rename confidence columns
            pivot_confidence.columns = [f"{col}_confidence" for col in pivot_confidence.columns]

            # Merge value and confidence pivots
            wide_df = pivot_value.join(pivot_confidence)
        else:
            # Simple pivot with just values
            wide_df = df.pivot(
                index=index_cols,
                columns="variable_name",
                values="value"
            )

        # Reset index to make document_id and document_name regular columns
        wide_df = wide_df.reset_index()

        # Convert to CSV
        csv_buffer = BytesIO()
        wide_df.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue()

        logger.info(f"Generated wide CSV with {len(wide_df)} rows")

        return csv_bytes

    async def generate_csv_long(
        self,
        project_id: UUID,
        include_confidence: bool = False,
        include_source_text: bool = False,
        min_confidence: Optional[float] = None,
    ) -> bytes:
        """
        Generate CSV export in long format (1 row per extraction).

        Args:
            project_id: Project UUID
            include_confidence: Include confidence scores
            include_source_text: Include source text excerpts
            min_confidence: Optional minimum confidence threshold

        Returns:
            CSV file content as bytes
        """
        # Get aggregated data (already in long format)
        df = await self.aggregate_extractions(
            project_id=project_id,
            include_confidence=include_confidence,
            include_source_text=include_source_text,
            min_confidence=min_confidence,
        )

        # Convert to CSV
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue()

        logger.info(f"Generated long CSV with {len(df)} rows")

        return csv_bytes

    async def generate_excel(
        self,
        project_id: UUID,
        include_confidence: bool = False,
        include_source_text: bool = False,
        min_confidence: Optional[float] = None,
    ) -> bytes:
        """
        Generate Excel export using openpyxl.

        Creates two sheets: one in wide format, one in long format.

        Args:
            project_id: Project UUID
            include_confidence: Include confidence scores
            include_source_text: Include source text excerpts
            min_confidence: Optional minimum confidence threshold

        Returns:
            Excel file content as bytes
        """
        # Get aggregated data
        df_long = await self.aggregate_extractions(
            project_id=project_id,
            include_confidence=include_confidence,
            include_source_text=include_source_text,
            min_confidence=min_confidence,
        )

        # Pivot to wide format (same logic as CSV wide)
        index_cols = ["document_id", "document_name"]

        if include_confidence:
            pivot_value = df_long.pivot(
                index=index_cols,
                columns="variable_name",
                values="value"
            )

            pivot_confidence = df_long.pivot(
                index=index_cols,
                columns="variable_name",
                values="confidence"
            )

            pivot_confidence.columns = [f"{col}_confidence" for col in pivot_confidence.columns]
            df_wide = pivot_value.join(pivot_confidence).reset_index()
        else:
            df_wide = df_long.pivot(
                index=index_cols,
                columns="variable_name",
                values="value"
            ).reset_index()

        # Create Excel file with two sheets
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_wide.to_excel(writer, sheet_name='Wide Format', index=False)
            df_long.to_excel(writer, sheet_name='Long Format', index=False)

        excel_bytes = excel_buffer.getvalue()

        logger.info(f"Generated Excel with {len(df_wide)} wide rows and {len(df_long)} long rows")

        return excel_bytes

    async def generate_json(
        self,
        project_id: UUID,
        include_confidence: bool = False,
        include_source_text: bool = False,
        min_confidence: Optional[float] = None,
    ) -> bytes:
        """
        Generate JSON export.

        Args:
            project_id: Project UUID
            include_confidence: Include confidence scores
            include_source_text: Include source text excerpts
            min_confidence: Optional minimum confidence threshold

        Returns:
            JSON file content as bytes
        """
        # Get aggregated data
        df = await self.aggregate_extractions(
            project_id=project_id,
            include_confidence=include_confidence,
            include_source_text=include_source_text,
            min_confidence=min_confidence,
        )

        # Convert to JSON (list of records)
        json_data = df.to_dict(orient='records')

        # Serialize to JSON bytes
        json_bytes = json.dumps(json_data, indent=2, default=str).encode('utf-8')

        logger.info(f"Generated JSON with {len(json_data)} records")

        return json_bytes
