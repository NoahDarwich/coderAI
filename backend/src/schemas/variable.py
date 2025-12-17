"""
Pydantic schemas for Variable API requests and responses.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.models.variable import VariableType


class VariableCreate(BaseModel):
    """Schema for creating a new variable."""
    name: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-zA-Z0-9_]+$", description="Variable name (alphanumeric + underscores)")
    type: VariableType = Field(..., description="Variable data type")
    instructions: str = Field(..., min_length=10, max_length=5000, description="Extraction instructions")
    classification_rules: Optional[Dict[str, Any]] = Field(None, description="Classification rules (for CATEGORY type)")
    order: int = Field(..., ge=1, description="Display order in schema")

    @field_validator("classification_rules")
    def validate_classification_rules(cls, v, info):
        """Validate classification rules are required for CATEGORY type."""
        if info.data.get("type") == VariableType.CATEGORY and not v:
            raise ValueError("classification_rules required for CATEGORY type")
        return v


class VariableUpdate(BaseModel):
    """Schema for updating a variable."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, pattern=r"^[a-zA-Z0-9_]+$")
    instructions: Optional[str] = Field(None, min_length=10, max_length=5000)
    classification_rules: Optional[Dict[str, Any]] = None
    order: Optional[int] = Field(None, ge=1)


class Variable(BaseModel):
    """Schema for variable response."""
    id: UUID
    project_id: UUID
    name: str
    type: VariableType
    instructions: str
    classification_rules: Optional[Dict[str, Any]]
    order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PromptInfo(BaseModel):
    """Schema for prompt information."""
    version: int
    prompt_text: str
    llm_config: Dict[str, Any]  # Renamed from model_config to avoid Pydantic reserved word


class VariableDetail(Variable):
    """Schema for detailed variable response with current prompt."""
    current_prompt: Optional[PromptInfo] = None

    class Config:
        from_attributes = True
