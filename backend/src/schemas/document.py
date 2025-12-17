"""
Pydantic schemas for Document API requests and responses.
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.document import ContentType


class DocumentCreate(BaseModel):
    """Schema for creating a new document (used with multipart/form-data)."""
    name: str = Field(..., min_length=1, max_length=500, description="Original filename")
    content: str = Field(..., min_length=1, description="Extracted document text")
    content_type: ContentType = Field(..., description="Document file type (PDF, DOCX, TXT)")
    size_bytes: int = Field(..., gt=0, le=10485760, description="File size in bytes (max 10MB)")


class TextDocumentCreate(BaseModel):
    """Schema for creating a document from raw text input (MVP feature)."""
    name: str = Field(..., min_length=1, max_length=500, description="Document name")
    content: str = Field(..., min_length=1, description="Raw text content")


class Document(BaseModel):
    """Schema for document response."""
    id: UUID
    project_id: UUID
    name: str
    content_type: ContentType
    size_bytes: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


class DocumentDetail(Document):
    """Schema for detailed document response with content preview."""
    content_preview: str = Field(description="First 500 characters of document content")

    class Config:
        from_attributes = True
