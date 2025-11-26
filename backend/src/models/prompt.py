"""
Prompt model - represents a generated LLM prompt for a variable.
"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from src.core.database import Base


class Prompt(Base):
    """
    Prompt model.

    Represents a generated LLM prompt for a variable (with versioning).
    """
    __tablename__ = "prompts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    variable_id = Column(UUID(as_uuid=True), ForeignKey("variables.id", ondelete="CASCADE"), nullable=False)
    prompt_text = Column(Text, nullable=False)
    model_config = Column(JSONB, nullable=False)
    version = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    variable = relationship("Variable", back_populates="prompts")

    def __repr__(self) -> str:
        return f"<Prompt(id={self.id}, variable_id={self.variable_id}, version={self.version})>"
