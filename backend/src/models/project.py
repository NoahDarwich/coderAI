"""
Project model - represents a research project.
"""
import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from src.core.database import Base


class ProjectScale(str, enum.Enum):
    """Project scale enumeration."""
    SMALL = "SMALL"
    LARGE = "LARGE"


class ProjectStatus(str, enum.Enum):
    """Project status enumeration."""
    CREATED = "CREATED"
    SCHEMA_DEFINED = "SCHEMA_DEFINED"
    SCHEMA_APPROVED = "SCHEMA_APPROVED"  # Schema approved and ready for processing
    SAMPLE_TESTING = "SAMPLE_TESTING"
    READY = "READY"
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"


class Project(Base):
    """
    Project model.

    Represents a research project with metadata and configuration.

    Attributes:
        unit_of_observation: JSONB config defining what each row represents
            - what_each_row_represents: str (e.g., "document", "person", "event")
            - rows_per_document: str ("one" or "multiple")
            - entity_identification_pattern: Optional[str] (regex pattern for entity extraction)
    """
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scale = Column(Enum(ProjectScale), nullable=False)
    language = Column(String(50), nullable=False, default="en")
    domain = Column(String(255), nullable=True)
    unit_of_observation = Column(
        JSONB,
        nullable=True,
        comment="Unit of observation configuration: what_each_row_represents, rows_per_document, entity_identification_pattern"
    )
    status = Column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.CREATED)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="projects")
    variables = relationship("Variable", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    processing_jobs = relationship("ProcessingJob", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"
