"""
Project model - represents a research project.
"""
import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
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
    """
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    scale = Column(Enum(ProjectScale), nullable=False)
    language = Column(String(50), nullable=False, default="en")
    domain = Column(String(255), nullable=True)
    status = Column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.CREATED)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    variables = relationship("Variable", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    processing_jobs = relationship("ProcessingJob", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"
