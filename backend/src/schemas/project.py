"""
Pydantic schemas for Project API requests and responses.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.models.project import ProjectScale, ProjectStatus


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    scale: ProjectScale = Field(..., description="Project scale (SMALL or LARGE)")
    language: str = Field(default="en", max_length=50, description="Source document language (ISO 639-1)")
    domain: Optional[str] = Field(None, max_length=255, description="Domain context (e.g., 'political science')")


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    domain: Optional[str] = Field(None, max_length=255, description="Domain context")


class Project(BaseModel):
    """Schema for project response."""
    id: UUID
    name: str
    scale: ProjectScale
    language: str
    domain: Optional[str]
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
