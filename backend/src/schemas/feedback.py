"""
Pydantic schemas for extraction feedback API requests and responses.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    """Schema for creating extraction feedback."""
    is_correct: bool = Field(..., description="Whether the extraction is correct")
    user_comment: Optional[str] = Field(None, max_length=1000, description="Optional user comment explaining what's wrong")


class Feedback(BaseModel):
    """Schema for feedback response."""
    id: UUID
    extraction_id: UUID
    is_correct: bool
    user_comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
