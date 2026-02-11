"""
Pydantic schemas for Project API requests and responses.
"""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.project import ProjectScale, ProjectStatus


class UnitOfObservation(BaseModel):
    """
    Schema for unit of observation configuration.

    Defines what each row in the dataset represents.
    """
    what_each_row_represents: str = Field(
        ...,
        description="What each row represents (e.g., 'document', 'person', 'event')",
        examples=["document", "person", "organization"]
    )
    rows_per_document: str = Field(
        ...,
        description="Whether one document produces one row or multiple rows",
        pattern="^(one|multiple)$",
        examples=["one", "multiple"]
    )
    entity_identification_pattern: Optional[str] = Field(
        None,
        description="Regex pattern for identifying entities (required if rows_per_document='multiple')",
        examples=[r"Person: ([A-Z][a-z]+ [A-Z][a-z]+)"]
    )


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    scale: ProjectScale = Field(..., description="Project scale (SMALL or LARGE)")
    language: str = Field(default="en", max_length=50, description="Source document language (ISO 639-1)")
    domain: Optional[str] = Field(None, max_length=255, description="Domain context (e.g., 'political science')")
    unit_of_observation: Optional[UnitOfObservation] = Field(
        None,
        description="Unit of observation configuration defining what each row represents"
    )


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    domain: Optional[str] = Field(None, max_length=255, description="Domain context")
    unit_of_observation: Optional[UnitOfObservation] = Field(
        None,
        description="Unit of observation configuration defining what each row represents"
    )


class Project(BaseModel):
    """Schema for project response."""
    id: UUID
    user_id: Optional[UUID] = None
    name: str
    description: Optional[str] = None
    scale: ProjectScale
    language: str
    domain: Optional[str]
    unit_of_observation: Optional[Dict] = None
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectDetail(Project):
    """Schema for detailed project response with related data."""
    variable_count: int = Field(default=0, description="Number of variables in the project")
    document_count: int = Field(default=0, description="Number of documents in the project")

    class Config:
        from_attributes = True
