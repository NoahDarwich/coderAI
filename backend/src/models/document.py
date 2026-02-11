"""
Document model - represents an uploaded document.
"""
import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.core.database import Base


class ContentType(str, enum.Enum):
    """Document content type enumeration."""
    PDF = "PDF"
    DOCX = "DOCX"
    TXT = "TXT"


class DocumentStatus(str, enum.Enum):
    """Document processing status."""
    UPLOADED = "UPLOADED"
    PARSED = "PARSED"
    READY = "READY"
    FAILED = "FAILED"


class Document(Base):
    """
    Document model.

    Represents an uploaded document to be processed.
    """
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(Enum(ContentType), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    status = Column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.UPLOADED)
    word_count = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="documents")
    extractions = relationship("Extraction", back_populates="document", cascade="all, delete-orphan")
    processing_logs = relationship("ProcessingLog", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, name={self.name}, status={self.status})>"
