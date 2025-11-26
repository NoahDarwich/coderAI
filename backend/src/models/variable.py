"""
Variable model - represents an extraction variable definition.
"""
import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from src.core.database import Base


class VariableType(str, enum.Enum):
    """Variable type enumeration."""
    TEXT = "TEXT"
    NUMBER = "NUMBER"
    DATE = "DATE"
    CATEGORY = "CATEGORY"
    BOOLEAN = "BOOLEAN"


class Variable(Base):
    """
    Variable model.

    Represents a single extraction variable defined by the user.
    """
    __tablename__ = "variables"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(Enum(VariableType), nullable=False)
    instructions = Column(Text, nullable=False)
    classification_rules = Column(JSONB, nullable=True)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="variables")
    prompts = relationship("Prompt", back_populates="variable", cascade="all, delete-orphan")
    extractions = relationship("Extraction", back_populates="variable")

    def __repr__(self) -> str:
        return f"<Variable(id={self.id}, name={self.name}, type={self.type})>"
