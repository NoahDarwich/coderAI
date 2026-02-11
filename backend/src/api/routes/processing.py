"""
API routes for processing job management and extraction feedback.
"""
from collections import defaultdict
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db
from src.models.document import Document
from src.models.user import User
from src.models.extraction import Extraction
from src.models.extraction_feedback import ExtractionFeedback
from src.models.processing_job import JobStatus, ProcessingJob
from src.models.processing_log import ProcessingLog
from src.models.project import Project
from src.models.variable import Variable
from src.schemas.feedback import Feedback, FeedbackCreate
from src.schemas.processing import (
    DocumentResult,
    Extraction as ExtractionSchema,
    ExtractionDataPoint,
    ExtractionDetail,
    FlagUpdate,
    JobCreate,
    JobDetail,
    JobResults,
    JobStatistics,
    ProcessingJob as ProcessingJobSchema,
    ProcessingLogEntry,
    ProjectResults,
    VariableStatistics,
)
from src.services.feedback_analyzer import FeedbackAnalyzer
from src.services.job_manager import JobManager

router = APIRouter(tags=["processing"])


@router.post(
    "/api/v1/projects/{project_id}/jobs",
    response_model=ProcessingJobSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_job(
    project_id: UUID,
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProcessingJobSchema:
    """
    Create a new processing job (sample or full).

    Args:
        project_id: Project UUID
        job_data: Job creation data (type and document IDs)
        db: Database session

    Returns:
        Created job

    Raises:
        HTTPException: 404 if project not found
        HTTPException: 400 if no documents provided
    """
    # Verify project exists and belongs to user
    result = await db.execute(select(Project).where(Project.id == project_id, Project.user_id == current_user.id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Create job manager
    job_manager = JobManager(db)

    try:
        job = await job_manager.create_job(
            project_id=project_id,
            job_type=job_data.job_type,
            document_ids=job_data.document_ids,
        )

        return ProcessingJobSchema.model_validate(job)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/api/v1/projects/{project_id}/jobs", response_model=List[ProcessingJobSchema])
async def list_jobs(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ProcessingJobSchema]:
    """
    List all jobs for a project.

    Args:
        project_id: Project UUID
        db: Database session

    Returns:
        List of jobs

    Raises:
        HTTPException: 404 if project not found
    """
    # Verify project exists and belongs to user
    result = await db.execute(select(Project).where(Project.id == project_id, Project.user_id == current_user.id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Get all jobs for project
    result = await db.execute(
        select(ProcessingJob)
        .where(ProcessingJob.project_id == project_id)
        .order_by(ProcessingJob.started_at.desc().nulls_last())
    )
    jobs = result.scalars().all()

    return [ProcessingJobSchema.model_validate(job) for job in jobs]


@router.get("/api/v1/jobs/{job_id}", response_model=JobDetail)
async def get_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobDetail:
    """
    Get job details with progress and recent logs.

    Args:
        job_id: Job UUID
        db: Database session

    Returns:
        Job details with logs

    Raises:
        HTTPException: 404 if job not found
    """
    # Get job
    result = await db.execute(
        select(ProcessingJob).where(ProcessingJob.id == job_id)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )

    # Get recent logs (last 50)
    result = await db.execute(
        select(ProcessingLog)
        .where(ProcessingLog.job_id == job_id)
        .order_by(ProcessingLog.created_at.desc())
        .limit(50)
    )
    logs = result.scalars().all()

    # Count completed documents
    result = await db.execute(
        select(func.count(func.distinct(Extraction.document_id)))
        .where(Extraction.job_id == job_id)
    )
    documents_completed = result.scalar_one()

    # Build response
    job_dict = job.__dict__.copy()
    job_dict["recent_logs"] = [
        ProcessingLogEntry(
            log_level=log.log_level.value,
            message=log.message,
            created_at=log.created_at,
            document_id=log.document_id,
            variable_id=log.variable_id,
        )
        for log in reversed(logs)  # Reverse to show oldest first
    ]
    job_dict["documents_completed"] = documents_completed
    job_dict["documents_total"] = len(job.document_ids)

    return JobDetail.model_validate(job_dict)


@router.delete("/api/v1/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Cancel a processing job.

    Note: This only marks the job as CANCELLED. If the job is already processing,
    it will continue until the current document completes.

    Args:
        job_id: Job UUID
        db: Database session

    Raises:
        HTTPException: 404 if job not found
        HTTPException: 400 if job already completed
    """
    # Get job
    result = await db.execute(
        select(ProcessingJob).where(ProcessingJob.id == job_id)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )

    # Check if job can be cancelled
    if job.status in [JobStatus.COMPLETE, JobStatus.FAILED, JobStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status {job.status.value}",
        )

    # Mark as cancelled
    job.status = JobStatus.CANCELLED
    await db.commit()


@router.post("/api/v1/jobs/{job_id}/pause", response_model=ProcessingJobSchema)
async def pause_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProcessingJobSchema:
    """
    Pause a processing job. The job will stop after the current document completes.
    """
    result = await db.execute(
        select(ProcessingJob).where(ProcessingJob.id == job_id)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )

    if not job.can_transition_to(JobStatus.PAUSED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot pause job with status {job.status.value}",
        )

    job.transition_to(JobStatus.PAUSED)
    await db.commit()
    await db.refresh(job)

    return ProcessingJobSchema.model_validate(job)


@router.post("/api/v1/jobs/{job_id}/resume", response_model=ProcessingJobSchema)
async def resume_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProcessingJobSchema:
    """
    Resume a paused processing job. Re-enqueues the ARQ task.
    Already-processed documents will be skipped.
    """
    result = await db.execute(
        select(ProcessingJob).where(ProcessingJob.id == job_id)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )

    if job.status != JobStatus.PAUSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only resume PAUSED jobs, current status: {job.status.value}",
        )

    # Set to PENDING so the worker can transition to PROCESSING
    job.status = JobStatus.PENDING
    job.consecutive_failures = 0
    await db.commit()
    await db.refresh(job)

    # Re-enqueue ARQ job
    job_manager = JobManager(db)
    await job_manager._enqueue_extraction(job.id)

    return ProcessingJobSchema.model_validate(job)


@router.get("/api/v1/jobs/{job_id}/results", response_model=JobResults)
async def get_job_results(
    job_id: UUID,
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence threshold (0.0-1.0)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobResults:
    """
    Get extraction results for a job with optional confidence filtering.

    Args:
        job_id: Job UUID
        min_confidence: Optional minimum confidence threshold
        db: Database session

    Returns:
        Job results with extractions

    Raises:
        HTTPException: 404 if job not found
    """
    # Get job
    result = await db.execute(
        select(ProcessingJob).where(ProcessingJob.id == job_id)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )

    # Build query for extractions
    query = select(Extraction).where(Extraction.job_id == job_id)

    # Apply confidence filter if provided
    if min_confidence is not None:
        query = query.where(Extraction.confidence >= min_confidence)

    # Order by document, then variable
    query = query.order_by(Extraction.document_id, Extraction.variable_id)

    # Execute query
    result = await db.execute(query)
    extractions = result.scalars().all()

    return JobResults(
        job_id=job_id,
        extractions=[ExtractionSchema.model_validate(e) for e in extractions],
        total_extractions=len(extractions),
        min_confidence_filter=min_confidence,
    )


@router.post(
    "/api/v1/extractions/{extraction_id}/feedback",
    response_model=Feedback,
    status_code=status.HTTP_201_CREATED,
)
async def create_feedback(
    extraction_id: UUID,
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Feedback:
    """
    Create feedback on an extraction.

    This feedback can be used to refine prompts and improve extraction quality.

    Args:
        extraction_id: Extraction UUID
        feedback_data: Feedback data
        db: Database session

    Returns:
        Created feedback

    Raises:
        HTTPException: 404 if extraction not found
    """
    # Verify extraction exists
    result = await db.execute(
        select(Extraction).where(Extraction.id == extraction_id)
    )
    extraction = result.scalar_one_or_none()

    if not extraction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Extraction with id {extraction_id} not found",
        )

    # Create feedback
    feedback = ExtractionFeedback(
        extraction_id=extraction_id,
        feedback_type=feedback_data.feedback_type,
        corrected_value=feedback_data.corrected_value,
        user_comment=feedback_data.user_comment,
    )

    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    # Check if enough feedback has accumulated to trigger refinement
    feedback_count_result = await db.execute(
        select(func.count(ExtractionFeedback.id))
        .join(Extraction, ExtractionFeedback.extraction_id == Extraction.id)
        .where(Extraction.variable_id == extraction.variable_id)
    )
    feedback_count = feedback_count_result.scalar_one()

    if feedback_count >= 3:
        # Enqueue refinement job via ARQ
        try:
            from arq.connections import create_pool
            from src.workers.settings import parse_redis_url
            from src.core.config import settings as app_settings

            pool = await create_pool(parse_redis_url(app_settings.REDIS_URL))
            try:
                await pool.enqueue_job(
                    "process_refinement_job",
                    variable_id=str(extraction.variable_id),
                )
            finally:
                await pool.close()
        except Exception:
            pass  # Non-critical — refinement can be triggered manually

    return Feedback.model_validate(feedback)


@router.put("/api/v1/extractions/{extraction_id}/flag", response_model=ExtractionSchema)
async def flag_extraction(
    extraction_id: UUID,
    flag_data: FlagUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ExtractionSchema:
    """
    Flag or unflag an extraction for review.

    Args:
        extraction_id: Extraction UUID
        flag_data: Flag status and optional notes
        db: Database session

    Returns:
        Updated extraction

    Raises:
        HTTPException: 404 if extraction not found
    """
    # Get extraction
    result = await db.execute(
        select(Extraction).where(Extraction.id == extraction_id)
    )
    extraction = result.scalar_one_or_none()

    if not extraction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Extraction with id {extraction_id} not found",
        )

    # Update extraction status
    extraction.status = flag_data.status
    if flag_data.error_message is not None:
        extraction.error_message = flag_data.error_message

    await db.commit()
    await db.refresh(extraction)

    return ExtractionSchema.model_validate(extraction)


@router.get("/api/v1/projects/{project_id}/results", response_model=ProjectResults)
async def get_project_results(
    project_id: UUID,
    min_confidence: Optional[int] = Query(None, ge=0, le=100, description="Minimum confidence filter (0-100)"),
    flagged_only: bool = Query(False, description="Only return flagged results"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResults:
    """
    Get all extraction results for a project, grouped by document.

    Args:
        project_id: Project UUID
        min_confidence: Optional minimum confidence filter (0-100)
        flagged_only: Only return flagged results
        db: Database session

    Returns:
        Aggregated project results

    Raises:
        HTTPException: 404 if project not found
    """
    # Verify project exists and belongs to user
    result = await db.execute(select(Project).where(Project.id == project_id, Project.user_id == current_user.id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Get all extractions for project (join with documents and variables)
    query = (
        select(Extraction, Document, Variable)
        .join(Document, Extraction.document_id == Document.id)
        .join(Variable, Extraction.variable_id == Variable.id)
        .where(Document.project_id == project_id)
    )

    # Apply filters
    if min_confidence is not None:
        query = query.where(Extraction.confidence >= min_confidence)
    if flagged_only:
        from src.models.extraction import ExtractionStatus
        query = query.where(Extraction.status == ExtractionStatus.FLAGGED)

    query = query.order_by(Document.name, Variable.order)

    result = await db.execute(query)
    rows = result.all()

    # Group by document
    documents_map = {}
    for extraction, document, variable in rows:
        doc_id = str(document.id)

        if doc_id not in documents_map:
            documents_map[doc_id] = {
                "document_id": document.id,
                "document_name": document.name,
                "data": {},
                "flagged": False,
                "extracted_at": extraction.created_at,
            }

        # Add extraction to document
        documents_map[doc_id]["data"][variable.name] = ExtractionDataPoint(
            value=extraction.value,
            confidence=extraction.confidence if extraction.confidence is not None else 0,
            source_text=extraction.source_text,
        )

        # If any extraction is flagged, mark document as flagged
        from src.models.extraction import ExtractionStatus
        if extraction.status == ExtractionStatus.FLAGGED:
            documents_map[doc_id]["flagged"] = True

    # Convert to list
    results = [
        DocumentResult(**doc_data)
        for doc_data in documents_map.values()
    ]

    return ProjectResults(
        project_id=project_id,
        results=results,
        total_documents=len(results),
        total_extractions=len(rows),
    )


@router.post(
    "/api/v1/projects/{project_id}/processing/sample",
    response_model=ProcessingJobSchema,
    status_code=status.HTTP_201_CREATED,
)
async def start_sample_processing(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProcessingJobSchema:
    """
    Convenience endpoint to start sample processing (first 10 documents).

    Args:
        project_id: Project UUID
        db: Database session

    Returns:
        Created job

    Raises:
        HTTPException: 404 if project not found
        HTTPException: 400 if no documents found
    """
    # Verify project exists and belongs to user
    result = await db.execute(select(Project).where(Project.id == project_id, Project.user_id == current_user.id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Get first 10 documents
    result = await db.execute(
        select(Document)
        .where(Document.project_id == project_id)
        .order_by(Document.uploaded_at)
        .limit(10)
    )
    documents = result.scalars().all()

    if not documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents found for project",
        )

    document_ids = [doc.id for doc in documents]

    # Create job
    job_manager = JobManager(db)
    try:
        from src.models.processing_job import JobType
        job = await job_manager.create_job(
            project_id=project_id,
            job_type=JobType.SAMPLE,
            document_ids=document_ids,
        )

        return ProcessingJobSchema.model_validate(job)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/api/v1/projects/{project_id}/processing/full",
    response_model=ProcessingJobSchema,
    status_code=status.HTTP_201_CREATED,
)
async def start_full_processing(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProcessingJobSchema:
    """
    Convenience endpoint to start full processing (all documents).

    Args:
        project_id: Project UUID
        db: Database session

    Returns:
        Created job

    Raises:
        HTTPException: 404 if project not found
        HTTPException: 400 if no documents found
    """
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id, Project.user_id == current_user.id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Get all documents
    result = await db.execute(
        select(Document)
        .where(Document.project_id == project_id)
        .order_by(Document.uploaded_at)
    )
    documents = result.scalars().all()

    if not documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents found for project",
        )

    document_ids = [doc.id for doc in documents]

    # Create job
    job_manager = JobManager(db)
    try:
        from src.models.processing_job import JobType
        job = await job_manager.create_job(
            project_id=project_id,
            job_type=JobType.FULL,
            document_ids=document_ids,
        )

        return ProcessingJobSchema.model_validate(job)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/api/v1/extractions/{extraction_id}", response_model=ExtractionDetail)
async def get_extraction_detail(
    extraction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ExtractionDetail:
    """
    Get detailed information about a specific extraction.
    
    Includes source document name, variable name, value, confidence score,
    and source text excerpt.
    
    Args:
        extraction_id: Extraction UUID
        db: Database session
    
    Returns:
        Detailed extraction information
    
    Raises:
        HTTPException: 404 if extraction not found
    """
    # Get extraction with related document and variable
    result = await db.execute(
        select(Extraction, Document, Variable)
        .join(Document, Extraction.document_id == Document.id)
        .join(Variable, Extraction.variable_id == Variable.id)
        .where(Extraction.id == extraction_id)
    )
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Extraction with id {extraction_id} not found",
        )
    
    extraction, document, variable = row
    
    # Build detailed response
    extraction_dict = extraction.__dict__.copy()
    extraction_dict["document_name"] = document.name
    extraction_dict["variable_name"] = variable.name
    
    return ExtractionDetail.model_validate(extraction_dict)


@router.get("/api/v1/jobs/{job_id}/statistics", response_model=JobStatistics)
async def get_job_statistics(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobStatistics:
    """
    Get comprehensive statistics for a processing job.
    
    Includes overall success rates, per-variable statistics, average confidence
    scores, and common error patterns.
    
    Args:
        job_id: Job UUID
        db: Database session
    
    Returns:
        Job statistics
    
    Raises:
        HTTPException: 404 if job not found
    """
    # Verify job exists
    result = await db.execute(
        select(ProcessingJob).where(ProcessingJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )
    
    # Get all extractions for this job
    result = await db.execute(
        select(Extraction, Variable)
        .join(Variable, Extraction.variable_id == Variable.id)
        .where(Extraction.job_id == job_id)
    )
    extraction_rows = result.all()
    
    if not extraction_rows:
        # Job has no extractions yet
        return JobStatistics(
            job_id=job_id,
            total_documents=len(job.document_ids),
            documents_processed=0,
            total_extractions=0,
            successful_extractions=0,
            overall_success_rate=0.0,
            avg_confidence=None,
            flagged_count=0,
            variable_statistics=[],
            common_errors=[]
        )
    
    # Calculate overall statistics
    total_extractions = len(extraction_rows)
    successful_extractions = sum(1 for e, _ in extraction_rows if e.value is not None)
    from src.models.extraction import ExtractionStatus as ES
    flagged_count = sum(1 for e, _ in extraction_rows if e.status == ES.FLAGGED)
    
    # Calculate average confidence
    confidences = [e.confidence for e, _ in extraction_rows if e.confidence is not None]
    avg_confidence = sum(confidences) / len(confidences) if confidences else None
    
    # Calculate per-variable statistics
    variable_data = defaultdict(lambda: {
        'name': '',
        'total': 0,
        'successful': 0,
        'confidences': [],
        'flagged': 0
    })
    
    for extraction, variable in extraction_rows:
        var_id = str(variable.id)
        variable_data[var_id]['name'] = variable.name
        variable_data[var_id]['total'] += 1
        if extraction.value is not None:
            variable_data[var_id]['successful'] += 1
        if extraction.confidence is not None:
            variable_data[var_id]['confidences'].append(extraction.confidence)
        if extraction.status == ES.FLAGGED:
            variable_data[var_id]['flagged'] += 1
    
    variable_statistics = []
    for var_id, data in variable_data.items():
        avg_var_confidence = (
            sum(data['confidences']) / len(data['confidences'])
            if data['confidences'] else None
        )
        success_rate = data['successful'] / data['total'] if data['total'] > 0 else 0.0
        
        variable_statistics.append(VariableStatistics(
            variable_id=UUID(var_id),
            variable_name=data['name'],
            total_extractions=data['total'],
            successful_extractions=data['successful'],
            success_rate=success_rate,
            avg_confidence=avg_var_confidence,
            flagged_count=data['flagged']
        ))
    
    # Get unique document count
    unique_documents = len(set(e.document_id for e, _ in extraction_rows))
    
    # TODO: Implement common error detection from processing logs
    common_errors = []
    
    return JobStatistics(
        job_id=job_id,
        total_documents=len(job.document_ids),
        documents_processed=unique_documents,
        total_extractions=total_extractions,
        successful_extractions=successful_extractions,
        overall_success_rate=successful_extractions / total_extractions if total_extractions > 0 else 0.0,
        avg_confidence=avg_confidence,
        flagged_count=flagged_count,
        variable_statistics=variable_statistics,
        common_errors=common_errors
    )


@router.post(
    "/api/v1/variables/{variable_id}/refine",
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_refinement(
    variable_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Manually trigger prompt refinement for a variable based on accumulated feedback.

    Args:
        variable_id: Variable UUID
        db: Database session

    Returns:
        Acknowledgement with job status

    Raises:
        HTTPException: 404 if variable not found
    """
    # Verify variable exists and belongs to user's project
    result = await db.execute(
        select(Variable)
        .join(Project, Variable.project_id == Project.id)
        .where(Variable.id == variable_id, Project.user_id == current_user.id)
    )
    variable = result.scalar_one_or_none()

    if not variable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variable with id {variable_id} not found",
        )

    # Enqueue refinement job
    from arq.connections import create_pool
    from src.workers.settings import parse_redis_url
    from src.core.config import settings as app_settings

    pool = await create_pool(parse_redis_url(app_settings.REDIS_URL))
    try:
        await pool.enqueue_job(
            "process_refinement_job",
            variable_id=str(variable_id),
        )
    finally:
        await pool.close()

    return {"status": "accepted", "message": f"Refinement job enqueued for variable {variable_id}"}
