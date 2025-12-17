"""
ProcessingJob model - represents a batch processing job.
"""
import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from src.core.database import Base


class JobType(str, enum.Enum):
    """Job type enumeration."""
    SAMPLE = "SAMPLE"
    FULL = "FULL"


class JobStatus(str, enum.Enum):
    """Job status enumeration."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ProcessingJob(Base):
    """
    ProcessingJob model.

    Represents a batch processing job (sample or full).
    """
    __tablename__ = "processing_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    job_type = Column(Enum(JobType), nullable=False)
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.PENDING)
    document_ids = Column(JSONB, nullable=False)
    progress = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="processing_jobs")
    extractions = relationship("Extraction", back_populates="job", cascade="all, delete-orphan")
    processing_logs = relationship("ProcessingLog", back_populates="job", cascade="all, delete-orphan")

    # Valid state transitions
    _VALID_TRANSITIONS = {
        JobStatus.PENDING: [JobStatus.PROCESSING, JobStatus.CANCELLED],
        JobStatus.PROCESSING: [JobStatus.COMPLETE, JobStatus.FAILED, JobStatus.CANCELLED],
        JobStatus.COMPLETE: [],  # Terminal state
        JobStatus.FAILED: [],    # Terminal state
        JobStatus.CANCELLED: [], # Terminal state
    }

    def can_transition_to(self, new_status: JobStatus) -> bool:
        """
        Check if the job can transition to the given status.

        Args:
            new_status: The target status

        Returns:
            True if transition is valid, False otherwise
        """
        return new_status in self._VALID_TRANSITIONS.get(self.status, [])

    def transition_to(self, new_status: JobStatus) -> None:
        """
        Transition the job to a new status with validation.

        Args:
            new_status: The target status

        Raises:
            ValueError: If the transition is invalid
        """
        if not self.can_transition_to(new_status):
            raise ValueError(
                f"Invalid status transition from {self.status.value} to {new_status.value}"
            )
        self.status = new_status

        # Update timestamps
        if new_status == JobStatus.PROCESSING and not self.started_at:
            self.started_at = datetime.utcnow()
        elif new_status in [JobStatus.COMPLETE, JobStatus.FAILED, JobStatus.CANCELLED]:
            if not self.completed_at:
                self.completed_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<ProcessingJob(id={self.id}, type={self.job_type}, status={self.status})>"
