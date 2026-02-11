"""
Job manager service for creating and tracking processing jobs.

This service manages background processing jobs using FastAPI BackgroundTasks.
Features:
- Atomic per-document transactions with savepoints
- Auto-pause on consecutive failures
- Job resumability (skip already-processed documents)
- Idempotent reprocessing (delete existing extractions before re-extraction)
- Structured event logging
- Prompt version tracking
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import BackgroundTasks
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.document import Document, DocumentStatus
from src.models.extraction import Extraction, ExtractionStatus
from src.models.processing_job import JobStatus, ProcessingJob
from src.models.processing_log import EventType, LogLevel, ProcessingLog
from src.models.prompt import Prompt
from src.models.project import Project
from src.models.variable import Variable
from src.services.post_processor import post_process_extraction
from src.services.text_extraction_service import create_extraction_service

logger = logging.getLogger(__name__)

MAX_CONSECUTIVE_FAILURES = 10


class JobManager:
    """
    Manager for creating and executing processing jobs.
    """

    def __init__(self, db: AsyncSession):
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
        """
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise ValueError(f"Project with id {project_id} not found")

        if not document_ids:
            raise ValueError("At least one document ID must be provided")

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

        background_tasks.add_task(
            process_job_background,
            job_id=job.id,
        )

        logger.info(f"Created job {job.id} with {len(document_ids)} documents")
        return job


def _create_log(
    job_id: UUID,
    level: LogLevel,
    event_type: EventType,
    message: str,
    document_id: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> ProcessingLog:
    """Helper to create a structured processing log entry."""
    return ProcessingLog(
        job_id=job_id,
        document_id=document_id,
        log_level=level,
        event_type=event_type,
        message=message,
        metadata_=metadata,
    )


async def _load_active_prompts(db: AsyncSession, variables: list) -> Dict[str, tuple]:
    """
    Load the active (highest version) prompt for each variable.

    Returns:
        Dict mapping variable_id (str) -> (prompt_text, version)
    """
    prompts: Dict[str, tuple] = {}
    for variable in variables:
        result = await db.execute(
            select(Prompt)
            .where(Prompt.variable_id == variable.id, Prompt.is_active == True)
            .order_by(Prompt.version.desc())
            .limit(1)
        )
        prompt = result.scalar_one_or_none()
        if prompt:
            prompts[str(variable.id)] = (prompt.prompt_text, prompt.version)
    return prompts


async def _get_processed_doc_ids(db: AsyncSession, job_id: UUID) -> set:
    """
    Get document IDs that already have extractions for this job.
    Used for resumability — skip already-processed documents.
    """
    result = await db.execute(
        select(Extraction.document_id)
        .where(Extraction.job_id == job_id)
        .distinct()
    )
    return {row[0] for row in result.all()}


async def process_job_background(job_id: UUID):
    """
    Background task to process a job.

    Features:
    - Atomic per-document savepoints
    - Auto-pause on consecutive failures
    - Skip already-processed documents (for resume)
    - Idempotent reprocessing (delete-before-insert)
    - Prompt version tracking
    - Structured event logging
    """
    from src.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            # Load job
            result = await db.execute(
                select(ProcessingJob).where(ProcessingJob.id == job_id)
            )
            job = result.scalar_one_or_none()

            if not job:
                logger.error(f"Job {job_id} not found")
                return

            # Transition to PROCESSING (handles PENDING->PROCESSING and PAUSED->PROCESSING)
            job.transition_to(JobStatus.PROCESSING)
            await db.commit()

            # Log start/resume
            is_resume = job.documents_processed > 0
            event = EventType.JOB_RESUMED if is_resume else EventType.JOB_STARTED
            db.add(_create_log(
                job_id=job.id,
                level=LogLevel.INFO,
                event_type=event,
                message=f"{'Resumed' if is_resume else 'Started'} processing job with {len(job.document_ids)} documents",
                metadata={"total_documents": len(job.document_ids), "already_processed": job.documents_processed},
            ))
            await db.commit()

            # Load variables
            result = await db.execute(
                select(Variable)
                .where(Variable.project_id == job.project_id)
                .order_by(Variable.order)
            )
            variables = result.scalars().all()

            if not variables:
                raise ValueError(f"No variables defined for project {job.project_id}")

            # Load active prompts for each variable
            active_prompts = await _load_active_prompts(db, variables)
            prompt_texts = {vid: pt for vid, (pt, _) in active_prompts.items()}
            prompt_versions = {vid: ver for vid, (_, ver) in active_prompts.items()}

            # Get already-processed document IDs (for resumability)
            processed_doc_ids = await _get_processed_doc_ids(db, job.id)

            # Build variable lookup by ID for post-processing
            variable_by_id = {str(v.id): v for v in variables}

            # Initialize extraction service
            text_extraction_service = create_extraction_service()

            total_documents = len(job.document_ids)

            for document_id in job.document_ids:
                doc_uuid = UUID(document_id) if isinstance(document_id, str) else document_id

                # Skip already-processed documents (resume support)
                if doc_uuid in processed_doc_ids:
                    continue

                # Check if job was cancelled or paused
                await db.refresh(job)
                if job.status == JobStatus.CANCELLED:
                    logger.info(f"Job {job_id} was cancelled, stopping")
                    db.add(_create_log(
                        job_id=job.id, level=LogLevel.INFO,
                        event_type=EventType.JOB_CANCELLED,
                        message=f"Job cancelled after {job.documents_processed}/{total_documents} documents",
                    ))
                    await db.commit()
                    return

                if job.status == JobStatus.PAUSED:
                    logger.info(f"Job {job_id} was paused, stopping")
                    db.add(_create_log(
                        job_id=job.id, level=LogLevel.INFO,
                        event_type=EventType.JOB_PAUSED,
                        message=f"Job paused after {job.documents_processed}/{total_documents} documents",
                    ))
                    await db.commit()
                    return

                # Load document
                doc_result = await db.execute(
                    select(Document).where(Document.id == doc_uuid)
                )
                document = doc_result.scalar_one_or_none()

                if not document:
                    logger.warning(f"Document {document_id} not found, skipping")
                    continue

                # Atomic per-document extraction using savepoint
                try:
                    async with db.begin_nested():
                        # Idempotent: delete existing extractions for this job+document
                        await db.execute(
                            delete(Extraction).where(
                                Extraction.job_id == job.id,
                                Extraction.document_id == doc_uuid,
                            )
                        )

                        # Extract all variables
                        extractions = await text_extraction_service.extract_all_variables(
                            text=document.content,
                            variables=list(variables),
                            prompts=prompt_texts if prompt_texts else None,
                        )

                        # Post-process and save extractions
                        for extraction_data in extractions:
                            var_id = extraction_data["variable_id"]
                            variable = variable_by_id.get(var_id)

                            raw_value = extraction_data.get("value")
                            raw_confidence = extraction_data.get("confidence", 0) or 0

                            # Apply post-processing (type coercion, validation, defaults, confidence check)
                            if variable:
                                pp = post_process_extraction(raw_value, raw_confidence, variable)
                                final_value = pp["value"]
                                final_confidence = pp["confidence"]
                                error_msg = pp.get("error_message") or extraction_data.get("error")

                                if pp["should_skip"]:
                                    ex_status = ExtractionStatus.FAILED
                                elif pp["should_flag"]:
                                    ex_status = ExtractionStatus.FLAGGED
                                elif final_value is not None:
                                    ex_status = ExtractionStatus.EXTRACTED
                                else:
                                    ex_status = ExtractionStatus.FAILED
                            else:
                                final_value = raw_value
                                final_confidence = raw_confidence
                                error_msg = extraction_data.get("error")
                                ex_status = ExtractionStatus.EXTRACTED if final_value is not None else ExtractionStatus.FAILED

                            extraction = Extraction(
                                job_id=job.id,
                                document_id=doc_uuid,
                                variable_id=UUID(var_id),
                                value=final_value,
                                confidence=final_confidence,
                                source_text=extraction_data.get("source_text"),
                                prompt_version=prompt_versions.get(var_id),
                                status=ex_status,
                                error_message=error_msg,
                            )
                            db.add(extraction)

                    # Savepoint succeeded — update counters
                    job.documents_processed += 1
                    job.consecutive_failures = 0

                    db.add(_create_log(
                        job_id=job.id, level=LogLevel.INFO,
                        event_type=EventType.DOC_COMPLETED,
                        message=f"Document processed: {document.name}",
                        document_id=document_id,
                        metadata={"extractions": len(extractions)},
                    ))

                except Exception as e:
                    # Savepoint rolled back — document failed
                    job.documents_failed += 1
                    job.consecutive_failures += 1

                    db.add(_create_log(
                        job_id=job.id, level=LogLevel.ERROR,
                        event_type=EventType.DOC_FAILED,
                        message=f"Document failed: {str(e)}",
                        document_id=document_id,
                    ))
                    logger.exception(f"Error processing document {document_id}")

                    # Auto-pause on too many consecutive failures
                    if job.consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                        logger.warning(f"Job {job_id}: auto-pausing after {MAX_CONSECUTIVE_FAILURES} consecutive failures")
                        job.transition_to(JobStatus.PAUSED)
                        db.add(_create_log(
                            job_id=job.id, level=LogLevel.WARNING,
                            event_type=EventType.JOB_PAUSED,
                            message=f"Auto-paused after {MAX_CONSECUTIVE_FAILURES} consecutive failures",
                            metadata={"consecutive_failures": job.consecutive_failures},
                        ))
                        await db.commit()
                        return

                # Update progress
                docs_done = job.documents_processed + job.documents_failed
                job.progress = int((docs_done / total_documents) * 100)
                await db.commit()

                logger.info(f"Job {job_id}: {docs_done}/{total_documents} documents done")

            # Mark job as complete
            job.transition_to(JobStatus.COMPLETE)
            job.progress = 100
            await db.commit()

            db.add(_create_log(
                job_id=job.id, level=LogLevel.INFO,
                event_type=EventType.JOB_COMPLETED,
                message=f"Job completed: {job.documents_processed} succeeded, {job.documents_failed} failed",
                metadata={
                    "documents_processed": job.documents_processed,
                    "documents_failed": job.documents_failed,
                },
            ))
            await db.commit()

            logger.info(f"Job {job_id} completed successfully")

        except Exception as e:
            logger.exception(f"Job {job_id} failed with error: {str(e)}")

            try:
                job.transition_to(JobStatus.FAILED)
                await db.commit()

                db.add(_create_log(
                    job_id=job.id, level=LogLevel.ERROR,
                    event_type=EventType.JOB_FAILED,
                    message=f"Job failed: {str(e)}",
                ))
                await db.commit()
            except Exception:
                logger.exception(f"Failed to update job {job_id} status to FAILED")
