"""
Job manager service for creating and tracking processing jobs.

This service manages job creation and enqueues ARQ tasks for processing.
"""
import logging
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.processing_job import JobStatus, ProcessingJob
from src.models.project import Project

logger = logging.getLogger(__name__)


class JobManager:
    """Manager for creating processing jobs and enqueuing them via ARQ."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_job(
        self,
        project_id: UUID,
        job_type: str,
        document_ids: List[UUID],
    ) -> ProcessingJob:
        """
        Create a new processing job and enqueue it via ARQ.
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

        # Enqueue ARQ job
        await self._enqueue_extraction(job.id)

        logger.info(f"Created job {job.id} with {len(document_ids)} documents")
        return job

    async def _enqueue_extraction(self, job_id: UUID) -> None:
        """Enqueue extraction job to ARQ via Redis."""
        from arq.connections import create_pool
        from src.workers.settings import parse_redis_url
        from src.core.config import settings

        pool = await create_pool(parse_redis_url(settings.REDIS_URL))
        try:
            await pool.enqueue_job(
                "process_extraction_job",
                job_id=str(job_id),
            )
            logger.info(f"Enqueued extraction job {job_id}")
        finally:
            await pool.close()
