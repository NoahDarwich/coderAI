"""
ExtractionFeedback model - represents user feedback on extraction quality.
"""
import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from src.core.database import Base


class FeedbackType(str, enum.Enum):
    """Feedback type enumeration."""
    CORRECT = "CORRECT"
    INCORRECT = "INCORRECT"
    PARTIALLY_CORRECT = "PARTIALLY_CORRECT"


class ExtractionFeedback(Base):
    """
    ExtractionFeedback model.

    Represents user feedback on extraction quality (for prompt refinement).
    """
    __tablename__ = "extraction_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    extraction_id = Column(UUID(as_uuid=True), ForeignKey("extractions.id", ondelete="CASCADE"), nullable=False)
    feedback_type = Column(Enum(FeedbackType), nullable=False)
    corrected_value = Column(JSONB, nullable=True, comment="User-provided correct value")
    user_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    extraction = relationship("Extraction", back_populates="feedback")

    def __repr__(self) -> str:
        return f"<ExtractionFeedback(id={self.id}, feedback_type={self.feedback_type})>"
