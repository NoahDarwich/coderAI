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
    LOCATION = "LOCATION"


class Variable(Base):
    """
    Variable model.

    Represents a single extraction variable defined by the user.

    Attributes:
        uncertainty_handling: JSONB config for handling uncertain extractions
            - confidence_threshold: float (0-100, minimum confidence to accept)
            - if_uncertain_action: str ("flag", "skip", "return_best_guess")
            - multiple_values_action: str ("return_all", "return_first", "concatenate")
        edge_cases: JSONB config for edge case handling
            - missing_field_action: str ("return_null", "return_na", "flag")
            - validation_rules: List[dict] (custom validation rules)
            - specific_scenarios: dict (scenario-specific handling instructions)
    """
    __tablename__ = "variables"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(Enum(VariableType), nullable=False)
    instructions = Column(Text, nullable=False)
    classification_rules = Column(JSONB, nullable=True)
    uncertainty_handling = Column(
        JSONB,
        nullable=True,
        comment="Uncertainty handling config: confidence_threshold, if_uncertain_action, multiple_values_action"
    )
    edge_cases = Column(
        JSONB,
        nullable=True,
        comment="Edge case handling: missing_field_action, validation_rules, specific_scenarios"
    )
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="variables")
    prompts = relationship("Prompt", back_populates="variable", cascade="all, delete-orphan")
    extractions = relationship("Extraction", back_populates="variable")
    processing_logs = relationship("ProcessingLog", back_populates="variable")

    def __repr__(self) -> str:
        return f"<Variable(id={self.id}, name={self.name}, type={self.type})>"
