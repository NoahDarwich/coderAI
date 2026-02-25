"""
API routes for the guided setup wizard.

These endpoints support a frontend wizard flow that helps users configure
a new project. The frontend holds wizard state client-side and submits
the final project via the existing POST /projects endpoint.
"""
import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db
from src.models.user import User
from src.schemas.wizard import (
    SuggestDefaultsRequest,
    SuggestDefaultsResponse,
    SuggestUoORequest,
    SuggestUoOResponse,
    UnitOfObservationSuggestion,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["wizard"])


@router.post(
    "/api/v1/wizard/suggest-unit-of-observation",
    response_model=SuggestUoOResponse,
)
async def suggest_unit_of_observation(
    request: SuggestUoORequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuggestUoOResponse:
    """
    Suggest a unit of observation configuration for a new project.

    Uses rule-based defaults by document type + domain keywords.
    If sample_text is provided, calls LLM for a smarter suggestion.
    """
    from src.core.redis import get_redis
    from src.agents.copilot import CopilotAgent

    redis = await get_redis()
    agent = CopilotAgent(redis=redis)

    result = await agent.suggest_unit_of_observation(
        domain=request.domain,
        document_type=request.document_type,
        sample_text=request.sample_text,
    )

    return SuggestUoOResponse(
        suggestion=UnitOfObservationSuggestion(**result["suggestion"]),
        explanation=result["explanation"],
        alternatives=[UnitOfObservationSuggestion(**a) for a in result["alternatives"]],
    )


@router.post(
    "/api/v1/wizard/suggest-defaults",
    response_model=SuggestDefaultsResponse,
)
async def suggest_defaults(
    request: SuggestDefaultsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuggestDefaultsResponse:
    """
    Get smart project defaults based on domain.

    Returns suggested project name pattern, language detection hint,
    and recommended variable types for the domain.
    """
    from src.core.redis import get_redis
    from src.agents.copilot import CopilotAgent

    redis = await get_redis()
    agent = CopilotAgent(redis=redis)

    result = await agent.suggest_defaults(
        domain=request.domain,
        language=request.language,
    )

    return SuggestDefaultsResponse(
        project_name_pattern=result["project_name_pattern"],
        language=result["language"],
        suggested_variable_types=result["suggested_variable_types"],
        explanation=result["explanation"],
    )
