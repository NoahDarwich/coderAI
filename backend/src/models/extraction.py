"""
Extraction model - represents a single extracted value.
"""
import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, Enum, ForeignKey, Text, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from src.core.database import Base


class ExtractionStatus(str, enum.Enum):
    """Extraction quality status."""
    EXTRACTED = "EXTRACTED"
    VALIDATED = "VALIDATED"
    FLAGGED = "FLAGGED"
    FAILED = "FAILED"


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
    value = Column(JSONB, nullable=True)
    confidence = Column(Integer, nullable=True)  # 0-100 scale
    source_text = Column(Text, nullable=True)
    status = Column(Enum(ExtractionStatus), nullable=False, default=ExtractionStatus.EXTRACTED)
    error_message = Column(Text, nullable=True)
    entity_index = Column(Integer, nullable=True, comment="Index for multi-entity extraction")
    entity_text = Column(Text, nullable=True, comment="Entity text for entity-level extraction")
    prompt_version = Column(Integer, nullable=True, comment="Version of prompt used for extraction")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Constraints
    __table_args__ = (
        CheckConstraint("confidence >= 0 AND confidence <= 100", name="check_confidence_range"),
        UniqueConstraint("job_id", "document_id", "variable_id", "entity_index", name="uq_extraction_job_doc_var_entity"),
    )

    # Relationships
    job = relationship("ProcessingJob", back_populates="extractions")
    document = relationship("Document", back_populates="extractions")
    variable = relationship("Variable", back_populates="extractions")
    feedback = relationship("ExtractionFeedback", back_populates="extraction", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Extraction(id={self.id}, variable_id={self.variable_id}, status={self.status})>"
