"""
MVP Processing Service for text extraction.

Simplified processing workflow that extracts variables from text documents
using OpenAI API.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.document import Document
from src.models.extraction import Extraction
from src.models.processing_job import JobStatus, ProcessingJob
from src.models.project import Project
from src.models.variable import Variable
from src.services.text_extraction_service import create_extraction_service


class MVPProcessingService:
    """
    Simplified processing service for MVP.

    Processes text documents and extracts variables using OpenAI.
    """

    def __init__(self, db: AsyncSession):
        """Initialize the processing service."""
        self.db = db
        self.extraction_service = create_extraction_service()

    async def process_documents(
        self,
        job: ProcessingJob,
        document_ids: List[UUID],
    ) -> None:
        """
        Process documents for a job.

        Args:
            job: The processing job
            document_ids: List of document IDs to process
        """
        try:
            # Update job status
            job.status = JobStatus.PROCESSING
            job.started_at = datetime.utcnow()
            await self.db.commit()

            # Get project and variables
            project_result = await self.db.execute(
                select(Project).where(Project.id == job.project_id)
            )
            project = project_result.scalar_one()

            variables_result = await self.db.execute(
                select(Variable)
                .where(Variable.project_id == project.id)
                .order_by(Variable.order)
            )
            variables = list(variables_result.scalars().all())

            if not variables:
                job.status = JobStatus.FAILED
                job.completed_at = datetime.utcnow()
                await self.db.commit()
                return

            # Process each document
            total_docs = len(document_ids)
            processed_count = 0

            for doc_id in document_ids:
                # Get document
                doc_result = await self.db.execute(
                    select(Document).where(Document.id == doc_id)
                )
                document = doc_result.scalar_one_or_none()

                if not document:
                    continue

                # Extract all variables from document text
                extractions = self.extraction_service.extract_all_variables(
                    text=document.content,
                    variables=variables,
                )

                # Save extractions to database
                for extraction_data in extractions:
                    extraction = Extraction(
                        job_id=job.id,
                        document_id=document.id,
                        variable_id=UUID(extraction_data["variable_id"]),
                        value=extraction_data.get("value"),
                        confidence=extraction_data.get("confidence"),
                        source_text=extraction_data.get("source_text"),
                    )
                    self.db.add(extraction)

                processed_count += 1

                # Update job progress
                job.progress = int((processed_count / total_docs) * 100)
                await self.db.commit()

            # Mark job as complete
            job.status = JobStatus.COMPLETE
            job.progress = 100
            job.completed_at = datetime.utcnow()
            await self.db.commit()

        except Exception as e:
            # Mark job as failed
            job.status = JobStatus.FAILED
            job.completed_at = datetime.utcnow()
            await self.db.commit()
            raise e


async def process_job_async(
    db: AsyncSession,
    job_id: UUID,
    document_ids: List[UUID],
) -> None:
    """
    Process a job asynchronously.

    Args:
        db: Database session
        job_id: Job ID to process
        document_ids: List of document IDs
    """
    # Get job
    result = await db.execute(
        select(ProcessingJob).where(ProcessingJob.id == job_id)
    )
    job = result.scalar_one()

    # Create processing service and run
    service = MVPProcessingService(db)
    await service.process_documents(job, document_ids)
