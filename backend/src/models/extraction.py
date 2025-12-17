"""
Extraction model - represents a single extracted value.
"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, Boolean, ForeignKey, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.core.database import Base


class Extraction(Base):
    """
    Extraction model.

    Represents a single extracted value from a document for a variable.
    """
    __tablename__ = "extractions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("processing_jobs.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    variable_id = Column(UUID(as_uuid=True), ForeignKey("variables.id", ondelete="CASCADE"), nullable=False)
    value = Column(Text, nullable=True)
    confidence = Column(Integer, nullable=True)  # Changed from Float to Integer (0-100 scale)
    source_text = Column(Text, nullable=True)
    flagged = Column(Boolean, nullable=False, default=False)  # For flagging extractions for review
    review_notes = Column(Text, nullable=True)  # Optional notes when flagging
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Constraints
    __table_args__ = (
        CheckConstraint("confidence >= 0 AND confidence <= 100", name="check_confidence_range"),
    )

    # Relationships
    job = relationship("ProcessingJob", back_populates="extractions")
    document = relationship("Document", back_populates="extractions")
    variable = relationship("Variable", back_populates="extractions")
    feedback = relationship("ExtractionFeedback", back_populates="extraction", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Extraction(id={self.id}, variable_id={self.variable_id}, confidence={self.confidence})>"
