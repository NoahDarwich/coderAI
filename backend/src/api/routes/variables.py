"""
API routes for variable management (CRUD operations).
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db
from src.models.project import Project, ProjectStatus
from src.models.user import User
from src.models.prompt import Prompt
from src.models.variable import Variable
from src.schemas.variable import (
    GoldenExampleCreate,
    PromptInfo,
    Variable as VariableSchema,
    VariableCreate,
    VariableDetail,
    VariableUpdate,
)
from src.services.prompt_generator import generate_prompt

router = APIRouter(tags=["variables"])


@router.get("/api/v1/projects/{project_id}/variables", response_model=List[VariableSchema])
async def list_variables(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[VariableSchema]:
    """
    List all variables for a project, ordered by 'order' field.

    Args:
        project_id: Project UUID
        db: Database session

    Returns:
        List of variables

    Raises:
        HTTPException: 404 if project not found
    """
    # Verify project exists and belongs to user
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )

    # Get all variables for project
    result = await db.execute(
        select(Variable)
        .where(Variable.project_id == project_id)
        .order_by(Variable.order)
    )
    variables = result.scalars().all()

    return [VariableSchema.model_validate(variable) for variable in variables]


@router.post("/api/v1/projects/{project_id}/variables", response_model=VariableSchema, status_code=status.HTTP_201_CREATED)
async def create_variable(
    project_id: UUID,
    variable_data: VariableCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VariableSchema:
    """
    Create a new variable and auto-generate its initial prompt.

    Args:
        project_id: Project UUID
        variable_data: Variable creation data
        db: Database session

    Returns:
        Created variable

    Raises:
        HTTPException: 404 if project not found
        HTTPException: 409 if variable order already exists
    """
    # Verify project exists and belongs to user
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )

    # Check if order already exists
    result = await db.execute(
        select(Variable)
        .where(Variable.project_id == project_id)
        .where(Variable.order == variable_data.order)
    )
    existing_variable = result.scalar_one_or_none()

    if existing_variable:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Variable with order {variable_data.order} already exists in project"
        )

    # Create variable
    variable = Variable(
        project_id=project_id,
        name=variable_data.name,
        type=variable_data.type,
        instructions=variable_data.instructions,
        classification_rules=variable_data.classification_rules,
        uncertainty_handling=variable_data.uncertainty_handling.model_dump() if variable_data.uncertainty_handling else None,
        edge_cases=variable_data.edge_cases.model_dump() if variable_data.edge_cases else None,
        order=variable_data.order,
    )

    db.add(variable)
    await db.flush()  # Get variable.id before commit

    # Auto-generate prompt using prompt_generator service
    prompt_data = generate_prompt(variable, project)
    prompt = Prompt(
        variable_id=variable.id,
        prompt_text=prompt_data["prompt_text"],
        model_config=prompt_data["model_config"],
        version=1,
    )

    db.add(prompt)
    await db.commit()
    await db.refresh(variable)

    # Update project status to SCHEMA_DEFINED if this is the first variable
    if project.status == ProjectStatus.CREATED:
        project.status = ProjectStatus.SCHEMA_DEFINED
        await db.commit()

    return VariableSchema.model_validate(variable)


@router.get("/api/v1/variables/{variable_id}", response_model=VariableDetail)
async def get_variable(
    variable_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VariableDetail:
    """
    Get variable details including current prompt.

    Args:
        variable_id: Variable UUID
        db: Database session

    Returns:
        Variable details with current prompt

    Raises:
        HTTPException: 404 if variable not found
    """
    # Get variable
    result = await db.execute(
        select(Variable).where(Variable.id == variable_id)
    )
    variable = result.scalar_one_or_none()

    if not variable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variable with id {variable_id} not found"
        )

    # Get current prompt (highest version)
    result = await db.execute(
        select(Prompt)
        .where(Prompt.variable_id == variable_id)
        .order_by(Prompt.version.desc())
        .limit(1)
    )
    current_prompt = result.scalar_one_or_none()

    # Build response
    variable_dict = variable.__dict__.copy()
    if current_prompt:
        variable_dict["current_prompt"] = PromptInfo(
            version=current_prompt.version,
            prompt_text=current_prompt.prompt_text,
            llm_config=current_prompt.model_config,
        )
    else:
        variable_dict["current_prompt"] = None

    return VariableDetail.model_validate(variable_dict)


@router.put("/api/v1/variables/{variable_id}", response_model=VariableSchema)
async def update_variable(
    variable_id: UUID,
    variable_data: VariableUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VariableSchema:
    """
    Update variable details and regenerate prompt if instructions changed.

    Args:
        variable_id: Variable UUID
        variable_data: Variable update data
        db: Database session

    Returns:
        Updated variable

    Raises:
        HTTPException: 404 if variable not found
        HTTPException: 409 if new order conflicts with existing variable
    """
    # Get variable
    result = await db.execute(
        select(Variable).where(Variable.id == variable_id)
    )
    variable = result.scalar_one_or_none()

    if not variable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variable with id {variable_id} not found"
        )

    # Check if new order conflicts with existing variable
    if variable_data.order is not None and variable_data.order != variable.order:
        result = await db.execute(
            select(Variable)
            .where(Variable.project_id == variable.project_id)
            .where(Variable.order == variable_data.order)
            .where(Variable.id != variable_id)
        )
        existing_variable = result.scalar_one_or_none()

        if existing_variable:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Variable with order {variable_data.order} already exists in project"
            )

    # Track if instructions changed (for prompt regeneration)
    instructions_changed = (
        variable_data.instructions is not None
        and variable_data.instructions != variable.instructions
    )

    # Update fields (only if provided)
    update_data = variable_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(variable, field, value)

    await db.flush()

    # Regenerate prompt if instructions changed
    if instructions_changed:
        # Get project for context
        result = await db.execute(
            select(Project).where(Project.id == variable.project_id)
        )
        project = result.scalar_one_or_none()

        # Get current highest version
        result = await db.execute(
            select(Prompt.version)
            .where(Prompt.variable_id == variable_id)
            .order_by(Prompt.version.desc())
            .limit(1)
        )
        current_version = result.scalar_one_or_none() or 0

        # Generate new prompt using prompt_generator service
        prompt_data = generate_prompt(variable, project)
        new_prompt = Prompt(
            variable_id=variable.id,
            prompt_text=prompt_data["prompt_text"],
            model_config=prompt_data["model_config"],
            version=current_version + 1,
        )

        db.add(new_prompt)

    await db.commit()
    await db.refresh(variable)

    return VariableSchema.model_validate(variable)


@router.delete("/api/v1/variables/{variable_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_variable(
    variable_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a variable and all related data (cascading delete).

    Args:
        variable_id: Variable UUID
        db: Database session

    Raises:
        HTTPException: 404 if variable not found
    """
    # Get variable
    result = await db.execute(
        select(Variable).where(Variable.id == variable_id)
    )
    variable = result.scalar_one_or_none()

    if not variable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variable with id {variable_id} not found"
        )

    # Delete variable (cascade deletes related records)
    await db.delete(variable)
    await db.commit()


@router.post(
    "/api/v1/variables/{variable_id}/examples",
    response_model=VariableSchema,
    status_code=status.HTTP_200_OK,
)
async def add_golden_example(
    variable_id: UUID,
    example: GoldenExampleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VariableSchema:
    """
    Pin a golden (few-shot) example to a variable.

    Appends the example to the variable's golden_examples JSONB list.
    When use_in_prompt=True, the prompt is regenerated to include it.

    Args:
        variable_id: Variable UUID
        example: The example to add (source_text, value, document_name, use_in_prompt)
        db: Database session

    Returns:
        Updated variable

    Raises:
        HTTPException: 404 if variable not found or not owned by current user
    """
    # Load variable, verify ownership via project
    result = await db.execute(
        select(Variable)
        .join(Variable.project)
        .where(Variable.id == variable_id, Variable.project.has(user_id=current_user.id))
    )
    variable = result.scalar_one_or_none()

    if not variable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variable with id {variable_id} not found",
        )

    # Append to golden_examples list (create if missing)
    existing = list(variable.golden_examples or [])
    existing.append(example.model_dump())
    variable.golden_examples = existing

    # Regenerate prompt if the new example should appear in future extractions
    if example.use_in_prompt:
        result_proj = await db.execute(
            select(Variable.project).where(Variable.id == variable_id)
        )
        from src.models.project import Project
        proj_result = await db.execute(
            select(Project).where(Project.id == variable.project_id)
        )
        project = proj_result.scalar_one_or_none()

        current_version_result = await db.execute(
            select(Prompt.version)
            .where(Prompt.variable_id == variable_id, Prompt.is_active.is_(True))
        )
        current_version = current_version_result.scalar_one_or_none() or 0

        # Deactivate current prompt
        await db.execute(
            select(Prompt)
            .where(Prompt.variable_id == variable_id, Prompt.is_active.is_(True))
        )
        active_prompts = await db.execute(
            select(Prompt).where(Prompt.variable_id == variable_id, Prompt.is_active.is_(True))
        )
        for p in active_prompts.scalars().all():
            p.is_active = False

        prompt_data = generate_prompt(variable, project)
        new_prompt = Prompt(
            variable_id=variable.id,
            prompt_text=prompt_data["prompt_text"],
            model_config=prompt_data["model_config"],
            version=current_version + 1,
            is_active=True,
        )
        db.add(new_prompt)

    await db.commit()
    await db.refresh(variable)
    return VariableSchema.model_validate(variable)
