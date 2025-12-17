"""
Job manager service for creating and tracking processing jobs.

This service manages background processing jobs using FastAPI BackgroundTasks.
For production, this should be migrated to Arq + Redis for persistent job queue.
"""
import logging
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.processing_job import JobStatus, ProcessingJob
from src.models.processing_log import LogLevel, ProcessingLog
from src.models.project import Project
from src.models.variable import Variable
from src.services.extraction_service import ExtractionService
from src.services.llm_client import LLMClientError
from src.services.text_extraction_service import create_extraction_service
from src.models.document import Document
from src.models.extraction import Extraction

logger = logging.getLogger(__name__)


class JobManager:
    """
    Manager for creating and executing processing jobs.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize job manager.

        Args:
            db: Database session
        """
        self.db = db

    async def create_job(
        self,
        project_id: UUID,
        job_type: str,
        document_ids: List[UUID],
        background_tasks: BackgroundTasks,
    ) -> ProcessingJob:
        """
        Create a new processing job and schedule it for execution.

        Args:
            project_id: Project UUID
            job_type: Job type (SAMPLE or FULL)
            document_ids: List of document IDs to process
            background_tasks: FastAPI background tasks

        Returns:
            Created job

        Raises:
            ValueError: If project not found or no documents provided
        """
        # Verify project exists
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise ValueError(f"Project with id {project_id} not found")

        if not document_ids:
            raise ValueError("At least one document ID must be provided")

        # Create job (convert UUID objects to strings for JSON storage)
        job = ProcessingJob(
            project_id=project_id,
            job_type=job_type,
            status=JobStatus.PENDING,
            document_ids=[str(doc_id) for doc_id in document_ids],
            progress=0,
        )

        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)

        # Schedule job for background execution
        # Note: We need to pass the job_id, not the session
        background_tasks.add_task(
            process_job_background,
            job_id=job.id,
        )

        logger.info(f"Created job {job.id} with {len(document_ids)} documents")

        return job


async def process_job_background(job_id: UUID):
    """
    Background task to process a job.

    This function runs in the background and processes all documents in the job.

    Args:
        job_id: Job UUID
    """
    # Import here to avoid circular dependency
    from src.core.database import async_session_maker

    # Create new database session for background task
    async with async_session_maker() as db:
        try:
            # Get job
            result = await db.execute(
                select(ProcessingJob).where(ProcessingJob.id == job_id)
            )
            job = result.scalar_one_or_none()

            if not job:
                logger.error(f"Job {job_id} not found")
                return

            # Update job status to PROCESSING
            job.transition_to(JobStatus.PROCESSING)
            await db.commit()

            # Log start
            log = ProcessingLog(
                job_id=job.id,
                log_level=LogLevel.INFO,
                message=f"Started processing job with {len(job.document_ids)} documents",
            )
            db.add(log)
            await db.commit()

            # Get all variables for project
            result = await db.execute(
                select(Variable)
                .where(Variable.project_id == job.project_id)
                .order_by(Variable.order)
            )
            variables = result.scalars().all()

            if not variables:
                raise ValueError(f"No variables defined for project {job.project_id}")

            # Initialize extraction service (MVP: using text extraction service)
            text_extraction_service = create_extraction_service()
            # extraction_service = ExtractionService(db)  # Old service using prompts

            # Process each document
            total_documents = len(job.document_ids)
            documents_completed = 0

            for document_id in job.document_ids:
                # Convert document_id from string to UUID
                doc_uuid = UUID(document_id) if isinstance(document_id, str) else document_id

                # Check if job was cancelled
                await db.refresh(job)
                if job.status == JobStatus.CANCELLED:
                    logger.info(f"Job {job_id} was cancelled, stopping processing")
                    log = ProcessingLog(
                        job_id=job.id,
                        log_level=LogLevel.INFO,
                        message=f"Job cancelled after processing {documents_completed}/{total_documents} documents",
                    )
                    db.add(log)
                    await db.commit()
                    return

                # Get document
                doc_result = await db.execute(
                    select(Document).where(Document.id == doc_uuid)
                )
                document = doc_result.scalar_one_or_none()

                if not document:
                    logger.warning(f"Document {document_id} not found, skipping")
                    continue

                # MVP: Extract all variables at once using text extraction service
                try:
                    extractions = text_extraction_service.extract_all_variables(
                        text=document.content,
                        variables=list(variables),
                    )

                    # Save extractions to database
                    for extraction_data in extractions:
                        extraction = Extraction(
                            job_id=job.id,
                            document_id=doc_uuid,
                            variable_id=UUID(extraction_data["variable_id"]),
                            value=extraction_data.get("value"),
                            confidence=extraction_data.get("confidence"),
                            source_text=extraction_data.get("source_text"),
                        )
                        db.add(extraction)

                except Exception as e:
                    # Log error but continue processing
                    log = ProcessingLog(
                        job_id=job.id,
                        document_id=document_id,
                        log_level=LogLevel.ERROR,
                        message=f"Extraction failed: {str(e)}",
                    )
                    db.add(log)
                    logger.exception(f"Error extracting from document {document_id}")

                # Commit extractions and logs for this document
                await db.commit()

                # Update progress
                documents_completed += 1
                job.progress = int((documents_completed / total_documents) * 100)
                await db.commit()

                logger.info(f"Job {job_id}: {documents_completed}/{total_documents} documents complete")

            # Mark job as complete
            job.transition_to(JobStatus.COMPLETE)
            job.progress = 100
            await db.commit()

            # Log completion
            log = ProcessingLog(
                job_id=job.id,
                log_level=LogLevel.INFO,
                message=f"Job completed successfully: {documents_completed} documents processed",
            )
            db.add(log)
            await db.commit()

            logger.info(f"Job {job_id} completed successfully")

        except Exception as e:
            # Mark job as failed
            logger.exception(f"Job {job_id} failed with error: {str(e)}")

            try:
                job.transition_to(JobStatus.FAILED)
                await db.commit()

                # Log failure
                log = ProcessingLog(
                    job_id=job.id,
                    log_level=LogLevel.ERROR,
                    message=f"Job failed: {str(e)}",
                )
                db.add(log)
                await db.commit()
            except Exception:
                logger.exception(f"Failed to update job {job_id} status to FAILED")
