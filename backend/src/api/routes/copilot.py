"""
API routes for AI co-pilot interactions.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db
from src.models.document import Document
from src.models.project import Project
from src.models.user import User
from src.models.variable import Variable

router = APIRouter(tags=["copilot"])


# --- Schemas ---

class CopilotMessageRequest(BaseModel):
    """Request to send a message to the co-pilot."""
    message: str = Field(..., min_length=1, max_length=5000, description="User message")


class CopilotMessageResponse(BaseModel):
    """Co-pilot response."""
    response: str = Field(..., description="Co-pilot response text")


class SuggestVariablesRequest(BaseModel):
    """Request to suggest variables based on domain and samples."""
    domain: str = Field(..., min_length=1, max_length=500, description="Project domain description")
    sample_document_ids: Optional[List[UUID]] = Field(
        None, max_length=3, description="Optional document IDs to use as samples"
    )


class SuggestedVariable(BaseModel):
    """A suggested extraction variable."""
    name: str
    type: str
    instructions: str
    classification_rules: Optional[Dict[str, Any]] = None


class SuggestVariablesResponse(BaseModel):
    """Response with suggested variables."""
    variables: List[SuggestedVariable]


class RefineRequest(BaseModel):
    """Request to trigger LLM-based prompt refinement."""
    variable_id: UUID = Field(..., description="Variable to refine")


class PromptAlternativeResponse(BaseModel):
    """A suggested prompt alternative."""
    prompt_text: str
    explanation: str
    focus: str


class RefineResponse(BaseModel):
    """Response with prompt refinement alternatives."""
    alternatives: List[PromptAlternativeResponse]


class ApplyRefinementRequest(BaseModel):
    """Request to apply a specific refinement."""
    variable_id: UUID
    prompt_text: str
    focus: str = "general"


class ApplyRefinementResponse(BaseModel):
    """Response after applying refinement."""
    prompt_id: UUID
    version: int


# --- Routes ---

@router.post(
    "/api/v1/projects/{project_id}/copilot/message",
    response_model=CopilotMessageResponse,
)
async def copilot_message(
    project_id: UUID,
    request: CopilotMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CopilotMessageResponse:
    """
    Send a message to the AI co-pilot for a project.

    The co-pilot maintains conversation context per project via Redis.
    """
    # Verify project
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Load existing variables for context
    result = await db.execute(
        select(Variable)
        .where(Variable.project_id == project_id)
        .order_by(Variable.order)
    )
    variables = result.scalars().all()
    vars_dicts = [
        {"name": v.name, "type": v.type.value, "instructions": v.instructions}
        for v in variables
    ]

    # Get Redis connection
    from src.core.redis import get_redis
    redis = await get_redis()

    # Create co-pilot and get response
    from src.agents.copilot import CopilotAgent
    agent = CopilotAgent(redis=redis)

    response_text = await agent.chat(
        project_id=project_id,
        user_message=request.message,
        project_name=project.name,
        domain=project.domain,
        language=project.language,
        existing_variables=vars_dicts,
    )

    return CopilotMessageResponse(response=response_text)


@router.post(
    "/api/v1/copilot/suggest-variables",
    response_model=SuggestVariablesResponse,
)
async def suggest_variables(
    request: SuggestVariablesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuggestVariablesResponse:
    """
    Get AI-suggested extraction variables based on domain and optional sample documents.
    """
    sample_texts = []

    if request.sample_document_ids:
        for doc_id in request.sample_document_ids[:3]:
            result = await db.execute(
                select(Document)
                .join(Project, Document.project_id == Project.id)
                .where(Document.id == doc_id, Project.user_id == current_user.id)
            )
            doc = result.scalar_one_or_none()
            if doc and doc.content:
                sample_texts.append(doc.content[:3000])

    from src.core.redis import get_redis
    redis = await get_redis()

    from src.agents.copilot import CopilotAgent
    agent = CopilotAgent(redis=redis)

    suggestions = await agent.suggest_variables(
        domain=request.domain,
        sample_texts=sample_texts,
        language="en",
    )

    return SuggestVariablesResponse(
        variables=[SuggestedVariable(**s) for s in suggestions]
    )


@router.post(
    "/api/v1/copilot/refine",
    response_model=RefineResponse,
)
async def refine_prompt(
    request: RefineRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RefineResponse:
    """
    Generate LLM-based prompt refinement alternatives based on feedback.
    """
    # Verify variable belongs to user
    result = await db.execute(
        select(Variable)
        .join(Project, Variable.project_id == Project.id)
        .where(Variable.id == request.variable_id, Project.user_id == current_user.id)
    )
    variable = result.scalar_one_or_none()
    if not variable:
        raise HTTPException(status_code=404, detail="Variable not found")

    from src.agents.refiner import RefinerAgent
    refiner = RefinerAgent()

    alternatives = await refiner.analyze_and_refine(
        db=db,
        variable_id=request.variable_id,
    )

    if not alternatives:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough feedback to generate refinements",
        )

    return RefineResponse(
        alternatives=[
            PromptAlternativeResponse(
                prompt_text=alt.prompt_text,
                explanation=alt.explanation,
                focus=alt.focus,
            )
            for alt in alternatives
        ]
    )


@router.post(
    "/api/v1/copilot/refine/apply",
    response_model=ApplyRefinementResponse,
)
async def apply_refinement(
    request: ApplyRefinementRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApplyRefinementResponse:
    """
    Apply a selected prompt refinement as a new prompt version.
    """
    # Verify variable belongs to user
    result = await db.execute(
        select(Variable)
        .join(Project, Variable.project_id == Project.id)
        .where(Variable.id == request.variable_id, Project.user_id == current_user.id)
    )
    variable = result.scalar_one_or_none()
    if not variable:
        raise HTTPException(status_code=404, detail="Variable not found")

    from src.agents.refiner import RefinerAgent, PromptAlternative
    refiner = RefinerAgent()

    alternative = PromptAlternative(
        prompt_text=request.prompt_text,
        explanation="User-selected refinement",
        focus=request.focus,
    )

    new_prompt = await refiner.apply_alternative(
        db=db,
        variable_id=request.variable_id,
        alternative=alternative,
    )

    if not new_prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No existing prompt found for this variable",
        )

    return ApplyRefinementResponse(
        prompt_id=new_prompt.id,
        version=new_prompt.version,
    )
