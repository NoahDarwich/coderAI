"""
ExtractionFeedback model - represents user feedback on extraction quality.
"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.core.database import Base


class ExtractionFeedback(Base):
    """
    ExtractionFeedback model.

    Represents user feedback on extraction quality (for prompt refinement).
    """
    __tablename__ = "extraction_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    extraction_id = Column(UUID(as_uuid=True), ForeignKey("extractions.id", ondelete="CASCADE"), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    correct_value = Column(Text, nullable=True)  # User-provided correct value when is_correct=False
    user_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    extraction = relationship("Extraction", back_populates="feedback")

    def __repr__(self) -> str:
        return f"<ExtractionFeedback(id={self.id}, is_correct={self.is_correct})>"
