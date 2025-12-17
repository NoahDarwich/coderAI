"""
Pydantic schemas for processing job and extraction API requests and responses.
"""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.processing_job import JobType, JobStatus


class JobCreate(BaseModel):
    """Schema for creating a new processing job."""
    job_type: JobType = Field(..., description="Job type (SAMPLE or FULL)")
    document_ids: List[UUID] = Field(..., min_length=1, description="List of document IDs to process")


class ProcessingJob(BaseModel):
    """Schema for processing job response."""
    id: UUID
    project_id: UUID
    job_type: JobType
    status: JobStatus
    document_ids: List[UUID]
    progress: int = Field(ge=0, le=100, description="Progress percentage (0-100)")
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class Extraction(BaseModel):
    """Schema for extraction response."""
    id: UUID
    job_id: UUID
    document_id: UUID
    variable_id: UUID
    value: Optional[str]
    confidence: Optional[int] = Field(None, ge=0, le=100, description="Confidence score (0-100)")
    source_text: Optional[str]
    flagged: bool = False
    review_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProcessingLogEntry(BaseModel):
    """Schema for processing log entry."""
    log_level: str
    message: str
    created_at: datetime
    document_id: Optional[UUID] = None
    variable_id: Optional[UUID] = None


class JobDetail(ProcessingJob):
    """Schema for detailed job response with recent logs."""
    recent_logs: List[ProcessingLogEntry] = Field(default_factory=list, description="Recent log entries (last 50)")
    documents_completed: int = Field(default=0, description="Number of documents completed")
    documents_total: int = Field(default=0, description="Total number of documents to process")

    class Config:
        from_attributes = True


class JobResults(BaseModel):
    """Schema for job results response."""
    job_id: UUID
    extractions: List[Extraction]
    total_extractions: int
    min_confidence_filter: Optional[int] = Field(None, ge=0, le=100, description="Minimum confidence filter (0-100)")


class FlagUpdate(BaseModel):
    """Schema for flagging/unflagging an extraction."""
    flagged: bool = Field(..., description="Whether extraction is flagged for review")
    review_notes: Optional[str] = Field(None, max_length=1000, description="Optional review notes")


class ExtractionDataPoint(BaseModel):
    """Single extraction value with metadata."""
    value: Optional[str]
    confidence: int = Field(ge=0, le=100, description="Confidence score (0-100)")
    source_text: Optional[str] = None


class DocumentResult(BaseModel):
    """Aggregated extraction results for a single document."""
    document_id: UUID
    document_name: str
    data: Dict[str, ExtractionDataPoint]  # variable_name -> data point
    flagged: bool = False
    extracted_at: datetime


class ProjectResults(BaseModel):
    """All extraction results for a project."""
    project_id: UUID
    results: List[DocumentResult]
    total_documents: int
    total_extractions: int
