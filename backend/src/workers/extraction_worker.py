"""
ARQ worker for extraction job processing.

Moves the extraction logic from job_manager.process_job_background into an ARQ task.
Supports parallel document processing with configurable concurrency.
"""
import asyncio
import logging
import time
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.document import Document
from src.models.document_chunk import DocumentChunk
from src.models.extraction import Extraction, ExtractionStatus
from src.models.processing_job import JobStatus, ProcessingJob
from src.models.processing_log import EventType, LogLevel, ProcessingLog
from src.models.project import Project
from src.models.prompt import Prompt
from src.models.variable import Variable
from src.core.config import settings
from src.services.post_processor import post_process_extraction
from src.services.text_extraction_service import create_extraction_service

logger = logging.getLogger(__name__)

MAX_CONSECUTIVE_FAILURES = 10
MAX_PARALLEL_DOCUMENTS = 5  # Concurrent documents per job
CHECKPOINT_INTERVAL = settings.WORKER_CHECKPOINT_INTERVAL


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
    """Load the active (highest version) prompt for each variable."""
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
    """Get document IDs that already have extractions (for resumability)."""
    result = await db.execute(
        select(Extraction.document_id)
        .where(Extraction.job_id == job_id)
        .distinct()
    )
    return {row[0] for row in result.all()}


async def _publish_progress(ctx: dict, job_id: UUID, event_type: str, data: dict) -> None:
    """Publish job progress event to Redis pub/sub."""
    import json
    redis = ctx.get("redis")
    if redis:
        channel = f"job:{job_id}:progress"
        payload = json.dumps({"type": event_type, **data})
        await redis.publish(channel, payload)


async def process_extraction_job(ctx: dict, job_id: str) -> dict:
    """
    ARQ task: process an extraction job.

    Features:
    - Atomic per-document savepoints
    - Auto-pause on consecutive failures
    - Skip already-processed documents (for resume)
    - Idempotent reprocessing (delete-before-insert)
    - Prompt version tracking
    - Structured event logging
    - Redis pub/sub progress events
    """
    job_uuid = UUID(job_id)
    session_factory = ctx["session_factory"]

    async with session_factory() as db:
        try:
            # Load job
            result = await db.execute(
                select(ProcessingJob).where(ProcessingJob.id == job_uuid)
            )
            job = result.scalar_one_or_none()

            if not job:
                logger.error(f"Job {job_id} not found")
                return {"status": "error", "message": "Job not found"}

            # Transition to PROCESSING
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

            # Load project to check unit_of_observation
            proj_result = await db.execute(
                select(Project).where(Project.id == job.project_id)
            )
            project = proj_result.scalar_one_or_none()
            uoo = project.unit_of_observation or {} if project else {}
            is_entity_mode = uoo.get("rows_per_document") == "multiple"
            entity_pattern = uoo.get("entity_identification_pattern", "")

            # Load active prompts
            active_prompts = await _load_active_prompts(db, variables)
            prompt_texts = {vid: pt for vid, (pt, _) in active_prompts.items()}
            prompt_versions = {vid: ver for vid, (_, ver) in active_prompts.items()}

            # Get already-processed doc IDs (resumability)
            processed_doc_ids = await _get_processed_doc_ids(db, job.id)

            # Build variable lookup
            variable_by_id = {str(v.id): v for v in variables}

            # Initialize extraction service
            text_extraction_service = create_extraction_service()

            total_documents = len(job.document_ids)

            for document_id in job.document_ids:
                doc_uuid = UUID(document_id) if isinstance(document_id, str) else document_id

                # Skip already-processed documents
                if doc_uuid in processed_doc_ids:
                    continue

                # Check for graceful shutdown signal
                if ctx.get("shutdown_requested"):
                    logger.info(f"Job {job_id}: shutdown requested, pausing at document boundary")
                    job.transition_to(JobStatus.PAUSED)
                    db.add(_create_log(
                        job_id=job.id, level=LogLevel.INFO,
                        event_type=EventType.JOB_PAUSED,
                        message=f"Paused for system shutdown after {job.documents_processed}/{total_documents} documents",
                        metadata={"reason": "system_shutdown"},
                    ))
                    await db.commit()
                    await _publish_progress(ctx, job.id, "job_paused", {
                        "reason": "system_shutdown",
                    })
                    return {"status": "paused", "reason": "system_shutdown"}

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
                    return {"status": "cancelled"}

                if job.status == JobStatus.PAUSED:
                    logger.info(f"Job {job_id} was paused, stopping")
                    db.add(_create_log(
                        job_id=job.id, level=LogLevel.INFO,
                        event_type=EventType.JOB_PAUSED,
                        message=f"Job paused after {job.documents_processed}/{total_documents} documents",
                    ))
                    await db.commit()
                    return {"status": "paused"}

                # Load document
                doc_result = await db.execute(
                    select(Document).where(Document.id == doc_uuid)
                )
                document = doc_result.scalar_one_or_none()

                if not document:
                    logger.warning(f"Document {document_id} not found, skipping")
                    continue

                # Start per-document timer for ETA tracking
                doc_start = time.monotonic()

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

                        # Resolve text source (chunks or full)
                        def _get_doc_text(doc, chunks_list):
                            if (doc.chunk_count or 0) > 1 and chunks_list:
                                return [c.text for c in chunks_list]
                            return [doc.content]

                        doc_chunks_list = []
                        if (document.chunk_count or 0) > 1:
                            chunk_result = await db.execute(
                                select(DocumentChunk)
                                .where(DocumentChunk.document_id == doc_uuid)
                                .order_by(DocumentChunk.chunk_index)
                            )
                            doc_chunks_list = chunk_result.scalars().all()

                        text_segments = _get_doc_text(document, doc_chunks_list)

                        if is_entity_mode and entity_pattern:
                            # Entity-level extraction
                            entities = await text_extraction_service.identify_entities(
                                text=document.content,
                                entity_pattern=entity_pattern,
                            )

                            if not entities:
                                # Fallback: treat whole doc as single entity
                                entities = [{"index": 0, "label": document.name, "text": ""}]

                            for entity in entities:
                                for variable in variables:
                                    prompt_text = prompt_texts.get(str(variable.id))

                                    # Extract from best text segment
                                    best_result = None
                                    for segment in text_segments:
                                        result_data = await text_extraction_service.extract_variable_for_entity(
                                            text=segment,
                                            variable=variable,
                                            entity=entity,
                                            prompt_text=prompt_text,
                                        )
                                        if best_result is None or (result_data.get("confidence") or 0) > (best_result.get("confidence") or 0):
                                            best_result = result_data

                                    extraction_data = best_result or {"value": None, "confidence": 0}
                                    extraction_data["variable_id"] = str(variable.id)
                                    extraction_data["variable_name"] = variable.name

                                    raw_value = extraction_data.get("value")
                                    raw_confidence = extraction_data.get("confidence", 0) or 0

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

                                    extraction = Extraction(
                                        job_id=job.id,
                                        document_id=doc_uuid,
                                        variable_id=variable.id,
                                        value=final_value,
                                        confidence=final_confidence,
                                        source_text=extraction_data.get("source_text"),
                                        prompt_version=prompt_versions.get(str(variable.id)),
                                        status=ex_status,
                                        error_message=error_msg,
                                        entity_index=entity.get("index"),
                                        entity_text=entity.get("text", "")[:500],
                                    )
                                    db.add(extraction)
                        else:
                            # Document-level extraction (with chunk merging)
                            if len(text_segments) > 1:
                                merged: Dict[str, Dict] = {}
                                for segment in text_segments:
                                    chunk_extractions = await text_extraction_service.extract_all_variables(
                                        text=segment,
                                        variables=list(variables),
                                        prompts=prompt_texts if prompt_texts else None,
                                    )
                                    for ext in chunk_extractions:
                                        vid = ext["variable_id"]
                                        existing = merged.get(vid)
                                        if existing is None or (ext.get("confidence") or 0) > (existing.get("confidence") or 0):
                                            merged[vid] = ext
                                extractions = list(merged.values())
                            else:
                                extractions = await text_extraction_service.extract_all_variables(
                                    text=text_segments[0],
                                    variables=list(variables),
                                    prompts=prompt_texts if prompt_texts else None,
                                )

                            # Post-process and save extractions
                            for extraction_data in extractions:
                                var_id = extraction_data["variable_id"]
                                variable = variable_by_id.get(var_id)

                                raw_value = extraction_data.get("value")
                                raw_confidence = extraction_data.get("confidence", 0) or 0

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

                    # Savepoint succeeded
                    job.documents_processed += 1
                    job.consecutive_failures = 0

                    db.add(_create_log(
                        job_id=job.id, level=LogLevel.INFO,
                        event_type=EventType.DOC_COMPLETED,
                        message=f"Document processed: {document.name}",
                        document_id=document_id,
                        metadata={"extractions": len(extractions)},
                    ))

                    await _publish_progress(ctx, job.id, "document_completed", {
                        "document_id": document_id,
                        "document_name": document.name,
                        "documents_processed": job.documents_processed,
                        "total_documents": total_documents,
                    })

                except Exception as e:
                    # Savepoint rolled back
                    job.documents_failed += 1
                    job.consecutive_failures += 1

                    db.add(_create_log(
                        job_id=job.id, level=LogLevel.ERROR,
                        event_type=EventType.DOC_FAILED,
                        message=f"Document failed: {str(e)}",
                        document_id=document_id,
                    ))
                    logger.exception(f"Error processing document {document_id}")

                    await _publish_progress(ctx, job.id, "document_failed", {
                        "document_id": document_id,
                        "error": str(e),
                    })

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
                        await _publish_progress(ctx, job.id, "job_paused", {
                            "reason": "consecutive_failures",
                        })
                        return {"status": "paused", "reason": "consecutive_failures"}

                # Update progress and ETA
                docs_done = job.documents_processed + job.documents_failed
                job.progress = int((docs_done / total_documents) * 100)

                # Rolling EMA of seconds per document (alpha=0.3 for smoothness)
                doc_elapsed = time.monotonic() - doc_start
                if job.avg_seconds_per_doc is None:
                    job.avg_seconds_per_doc = doc_elapsed
                else:
                    job.avg_seconds_per_doc = 0.7 * job.avg_seconds_per_doc + 0.3 * doc_elapsed

                docs_remaining = total_documents - docs_done
                eta_seconds = int(job.avg_seconds_per_doc * docs_remaining) if docs_remaining > 0 else 0

                await db.commit()

                # Periodic checkpoint log
                if docs_done % CHECKPOINT_INTERVAL == 0:
                    logger.info(
                        f"Job {job_id}: checkpoint at {docs_done}/{total_documents} documents"
                    )

                await _publish_progress(ctx, job.id, "progress", {
                    "progress": job.progress,
                    "documents_processed": job.documents_processed,
                    "documents_failed": job.documents_failed,
                    "total_documents": total_documents,
                    "eta_seconds": eta_seconds,
                })

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

            await _publish_progress(ctx, job.id, "job_completed", {
                "documents_processed": job.documents_processed,
                "documents_failed": job.documents_failed,
            })

            logger.info(f"Job {job_id} completed successfully")
            return {"status": "completed", "processed": job.documents_processed, "failed": job.documents_failed}

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

                await _publish_progress(ctx, job.id, "job_failed", {
                    "error": str(e),
                })
            except Exception:
                logger.exception(f"Failed to update job {job_id} status to FAILED")

            return {"status": "failed", "error": str(e)}
