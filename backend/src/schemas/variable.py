"""
Pydantic schemas for Variable API requests and responses.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.models.variable import VariableType


class UncertaintyHandling(BaseModel):
    """
    Schema for uncertainty handling configuration.

    Defines how to handle uncertain extractions.
    """
    confidence_threshold: float = Field(
        ...,
        ge=0,
        le=100,
        description="Minimum confidence score (0-100) to accept extraction"
    )
    if_uncertain_action: str = Field(
        ...,
        pattern="^(flag|skip|return_best_guess)$",
        description="Action to take if confidence is below threshold"
    )
    multiple_values_action: str = Field(
        ...,
        pattern="^(return_all|return_first|concatenate)$",
        description="How to handle multiple values found"
    )


class ValidationRule(BaseModel):
    """Schema for a single validation rule."""
    rule_type: str = Field(..., description="Type of validation (e.g., 'regex', 'range', 'enum')")
    parameters: Dict[str, Any] = Field(..., description="Rule-specific parameters")
    error_message: Optional[str] = Field(None, description="Custom error message")


class EdgeCases(BaseModel):
    """
    Schema for edge case handling configuration.

    Defines how to handle edge cases during extraction.
    """
    missing_field_action: str = Field(
        ...,
        pattern="^(return_null|return_na|flag)$",
        description="Action to take when field is missing from document"
    )
    validation_rules: Optional[List[ValidationRule]] = Field(
        None,
        description="Custom validation rules to apply"
    )
    specific_scenarios: Optional[Dict[str, str]] = Field(
        None,
        description="Scenario-specific handling instructions (key: scenario, value: instruction)"
    )


class VariableCreate(BaseModel):
    """Schema for creating a new variable."""
    name: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-zA-Z0-9_]+$", description="Variable name (alphanumeric + underscores)")
    type: VariableType = Field(..., description="Variable data type")
    instructions: str = Field(..., min_length=10, max_length=5000, description="Extraction instructions")
    classification_rules: Optional[Dict[str, Any]] = Field(None, description="Classification rules (for CATEGORY type)")
    uncertainty_handling: Optional[UncertaintyHandling] = Field(
        None,
        description="Configuration for handling uncertain extractions"
    )
    edge_cases: Optional[EdgeCases] = Field(
        None,
        description="Configuration for handling edge cases"
    )
    display_name: Optional[str] = Field(None, max_length=255, description="Human-readable display name")
    max_values: int = Field(1, ge=1, description="Maximum number of values to extract")
    default_value: Optional[str] = Field(None, description="Default value when extraction returns null")
    depends_on: Optional[List[UUID]] = Field(None, description="Variable IDs this depends on")
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
    uncertainty_handling: Optional[UncertaintyHandling] = None
    edge_cases: Optional[EdgeCases] = None
    display_name: Optional[str] = Field(None, max_length=255)
    max_values: Optional[int] = Field(None, ge=1)
    default_value: Optional[str] = None
    depends_on: Optional[List[UUID]] = None
    order: Optional[int] = Field(None, ge=1)


class GoldenExample(BaseModel):
    """A single few-shot extraction example pinned by the user."""
    source_text: str = Field(..., description="Verbatim excerpt from the source document")
    value: Any = Field(..., description="The correct extracted value for this variable")
    document_name: str = Field(..., description="Name of the source document")
    use_in_prompt: bool = Field(True, description="Include this example in the extraction prompt")


class GoldenExampleCreate(BaseModel):
    """Request body for pinning a new golden example."""
    source_text: str = Field(..., min_length=1, description="Verbatim excerpt from the source document")
    value: Any = Field(..., description="The correct extracted value")
    document_name: str = Field(..., min_length=1, description="Name of the source document")
    use_in_prompt: bool = Field(True, description="Include this example in the extraction prompt")


class Variable(BaseModel):
    """Schema for variable response."""
    id: UUID
    project_id: UUID
    name: str
    type: VariableType
    instructions: str
    classification_rules: Optional[Dict[str, Any]] = None
    uncertainty_handling: Optional[Dict[str, Any]] = None
    edge_cases: Optional[Dict[str, Any]] = None
    display_name: Optional[str] = None
    max_values: int = 1
    default_value: Optional[str] = None
    depends_on: Optional[List[Any]] = None
    golden_examples: Optional[List[GoldenExample]] = None
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
