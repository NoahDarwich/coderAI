"""
Pydantic schemas for the guided setup wizard API.
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class UnitOfObservationSuggestion(BaseModel):
    """A suggested unit of observation configuration."""
    rows_per_document: str = Field(..., description="'single' or 'multiple'")
    entity_identification_pattern: Optional[str] = Field(
        None, description="Pattern for identifying entities when rows_per_document='multiple'"
    )
    label: str = Field(..., description="Human-readable label, e.g. 'One row per article'")


class SuggestUoORequest(BaseModel):
    """Request to suggest a unit of observation."""
    domain: str = Field(..., min_length=1, max_length=500, description="Project domain")
    document_type: Optional[str] = Field(
        None, max_length=200, description="Type of documents, e.g. 'news articles', 'contracts'"
    )
    sample_text: Optional[str] = Field(
        None, max_length=5000, description="Sample text for LLM-enhanced suggestion"
    )


class SuggestUoOResponse(BaseModel):
    """Response with unit of observation suggestion."""
    suggestion: UnitOfObservationSuggestion
    explanation: str
    alternatives: List[UnitOfObservationSuggestion]


class SuggestDefaultsRequest(BaseModel):
    """Request for smart project defaults."""
    domain: str = Field(..., min_length=1, max_length=500, description="Project domain")
    language: Optional[str] = Field(None, max_length=10, description="Language code, e.g. 'en'")


class SuggestedDefault(BaseModel):
    """A single suggested default value."""
    key: str
    value: Any
    explanation: str


class SuggestDefaultsResponse(BaseModel):
    """Response with smart project defaults."""
    project_name_pattern: str = Field(..., description="Suggested project name pattern")
    language: str = Field(..., description="Detected or suggested language")
    suggested_variable_types: List[Dict[str, str]] = Field(
        ..., description="Recommended variable types for the domain"
    )
    explanation: str
