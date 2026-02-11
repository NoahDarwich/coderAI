"""
ARQ worker for prompt refinement based on user feedback.

Analyzes feedback patterns and creates refined prompt versions.
"""
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.variable import Variable
from src.services.feedback_analyzer import FeedbackAnalyzer

logger = logging.getLogger(__name__)


async def process_refinement_job(ctx: dict, variable_id: str) -> dict:
    """
    ARQ task: analyze feedback for a variable and refine its prompt.

    Args:
        ctx: ARQ context with session_factory
        variable_id: Variable UUID string

    Returns:
        Dict with status and optional new prompt version
    """
    var_uuid = UUID(variable_id)
    session_factory = ctx["session_factory"]

    async with session_factory() as db:
        try:
            # Verify variable exists
            result = await db.execute(
                select(Variable).where(Variable.id == var_uuid)
            )
            variable = result.scalar_one_or_none()

            if not variable:
                logger.error(f"Variable {variable_id} not found")
                return {"status": "error", "message": "Variable not found"}

            # Analyze feedback patterns
            analyzer = FeedbackAnalyzer(db)
            pattern = await analyzer.analyze_variable_feedback(var_uuid)

            if not pattern:
                logger.info(f"Not enough feedback for variable {variable_id}")
                return {"status": "skipped", "message": "Not enough feedback for analysis"}

            if not pattern.suggested_refinement:
                logger.info(f"No refinement needed for variable {variable_id}")
                return {"status": "skipped", "message": "No refinement needed"}

            # Create refined prompt
            new_prompt = await analyzer.refine_prompt_from_feedback(
                var_uuid, pattern
            )

            if new_prompt:
                logger.info(
                    f"Created refined prompt v{new_prompt.version} for variable {variable_id}"
                )
                return {
                    "status": "completed",
                    "prompt_id": str(new_prompt.id),
                    "version": new_prompt.version,
                }

            return {"status": "skipped", "message": "Refinement produced no changes"}

        except Exception as e:
            logger.exception(f"Refinement job failed for variable {variable_id}: {e}")
            return {"status": "failed", "error": str(e)}
