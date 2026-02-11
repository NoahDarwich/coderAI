"""
API routes for project management (CRUD operations).
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db
from src.models.document import Document
from src.models.project import Project, ProjectStatus
from src.models.user import User
from src.models.variable import Variable
from src.schemas.project import (
    Project as ProjectSchema,
    ProjectCreate,
    ProjectDetail,
    ProjectUpdate,
)

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


@router.post("", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectSchema:
    """Create a new project."""
    project = Project(
        user_id=current_user.id,
        name=project_data.name,
        description=project_data.description,
        scale=project_data.scale,
        language=project_data.language,
        domain=project_data.domain,
        unit_of_observation=project_data.unit_of_observation.model_dump() if project_data.unit_of_observation else None,
        status=ProjectStatus.CREATED,
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    return ProjectSchema.model_validate(project)


@router.get("", response_model=List[ProjectSchema])
async def list_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status_filter: Optional[ProjectStatus] = Query(None, description="Filter by project status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ProjectSchema]:
    """List projects for the current user with pagination and optional filtering."""
    query = select(Project).where(Project.user_id == current_user.id)

    if status_filter:
        query = query.where(Project.status == status_filter)

    query = query.order_by(Project.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    projects = result.scalars().all()

    return [ProjectSchema.model_validate(project) for project in projects]


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectDetail:
    """Get project details by ID."""
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )

    variable_count_result = await db.execute(
        select(func.count(Variable.id)).where(Variable.project_id == project_id)
    )
    variable_count = variable_count_result.scalar_one()

    document_count_result = await db.execute(
        select(func.count(Document.id)).where(Document.project_id == project_id)
    )
    document_count = document_count_result.scalar_one()

    project_dict = {
        **project.__dict__,
        "variable_count": variable_count,
        "document_count": document_count,
    }

    return ProjectDetail.model_validate(project_dict)


@router.put("/{project_id}", response_model=ProjectSchema)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectSchema:
    """Update project details."""
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )

    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)

    return ProjectSchema.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a project and all related data (cascading delete)."""
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )

    await db.delete(project)
    await db.commit()


@router.post("/{project_id}/schema/approve", status_code=status.HTTP_204_NO_CONTENT)
async def approve_schema(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Approve project schema and mark ready for processing."""
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    result = await db.execute(
        select(func.count(Variable.id)).where(Variable.project_id == project_id)
    )
    variable_count = result.scalar_one()

    if variable_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot approve schema: no variables defined",
        )

    project.status = ProjectStatus.SCHEMA_APPROVED
    await db.commit()
