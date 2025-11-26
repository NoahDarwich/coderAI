"""
ProcessingLog model - represents a log entry for processing events.
"""
import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.core.database import Base


class LogLevel(str, enum.Enum):
    """Log level enumeration."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class ProcessingLog(Base):
    """
    ProcessingLog model.

    Represents a log entry for processing events (debugging, error tracking).
    """
    __tablename__ = "processing_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("processing_jobs.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    variable_id = Column(UUID(as_uuid=True), ForeignKey("variables.id", ondelete="SET NULL"), nullable=True)
    log_level = Column(Enum(LogLevel), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    job = relationship("ProcessingJob", back_populates="processing_logs")

    def __repr__(self) -> str:
        return f"<ProcessingLog(id={self.id}, level={self.log_level}, message={self.message[:50]})>"
