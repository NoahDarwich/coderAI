"""
Pydantic schemas for extraction feedback API requests and responses.
"""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.extraction_feedback import FeedbackType


class FeedbackCreate(BaseModel):
    """Schema for creating extraction feedback."""
    feedback_type: FeedbackType = Field(..., description="Feedback type: CORRECT, INCORRECT, or PARTIALLY_CORRECT")
    corrected_value: Optional[Any] = Field(None, description="User-provided correct value")
    user_comment: Optional[str] = Field(None, max_length=1000, description="Optional user comment")


class Feedback(BaseModel):
    """Schema for feedback response."""
    id: UUID
    extraction_id: UUID
    feedback_type: FeedbackType
    corrected_value: Optional[Any] = None
    user_comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
