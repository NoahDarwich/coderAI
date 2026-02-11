"""
LLM-based prompt refinement agent.

Analyzes feedback patterns and generates improved prompt alternatives using LLM,
replacing the keyword-matching approach in feedback_analyzer.py.
"""
import json
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.models.extraction import Extraction
from src.models.extraction_feedback import ExtractionFeedback, FeedbackType
from src.models.prompt import Prompt
from src.models.variable import Variable

logger = logging.getLogger(__name__)


class PromptAlternative:
    """A suggested prompt refinement."""

    def __init__(self, prompt_text: str, explanation: str, focus: str):
        self.prompt_text = prompt_text
        self.explanation = explanation
        self.focus = focus  # e.g. "precision", "recall", "format"


class RefinerAgent:
    """
    LLM-based prompt refinement agent.

    Receives the current prompt text, incorrect extractions with user corrections,
    and generates 2-3 alternative refined prompts with explanations.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL or "gpt-4",
            temperature=0.4,
            api_key=settings.OPENAI_API_KEY,
        )

    async def analyze_and_refine(
        self,
        db: AsyncSession,
        variable_id: UUID,
        min_feedback_count: int = 3,
    ) -> Optional[List[PromptAlternative]]:
        """
        Analyze feedback for a variable and generate refined prompt alternatives.

        Args:
            db: Database session
            variable_id: Variable UUID
            min_feedback_count: Minimum feedback entries needed

        Returns:
            List of PromptAlternative or None if insufficient feedback
        """
        # Load variable
        result = await db.execute(
            select(Variable).where(Variable.id == variable_id)
        )
        variable = result.scalar_one_or_none()
        if not variable:
            return None

        # Load current prompt
        result = await db.execute(
            select(Prompt)
            .where(Prompt.variable_id == variable_id, Prompt.is_active == True)
            .order_by(Prompt.version.desc())
            .limit(1)
        )
        current_prompt = result.scalar_one_or_none()
        if not current_prompt:
            return None

        # Load feedback with extractions
        result = await db.execute(
            select(ExtractionFeedback, Extraction)
            .join(Extraction, ExtractionFeedback.extraction_id == Extraction.id)
            .where(Extraction.variable_id == variable_id)
        )
        feedback_rows = result.all()

        if len(feedback_rows) < min_feedback_count:
            return None

        # Build feedback summary for LLM
        incorrect_examples = []
        for feedback, extraction in feedback_rows:
            if feedback.feedback_type != FeedbackType.CORRECT:
                incorrect_examples.append({
                    "extracted_value": str(extraction.value) if extraction.value else "null",
                    "correct_value": str(feedback.corrected_value) if feedback.corrected_value else "not provided",
                    "feedback_type": feedback.feedback_type.value,
                    "user_comment": feedback.user_comment or "",
                    "source_text": (extraction.source_text or "")[:200],
                })

        if not incorrect_examples:
            return None

        # Call LLM to generate alternatives
        return await self._generate_alternatives(
            current_prompt_text=current_prompt.prompt_text,
            variable_name=variable.name,
            variable_type=variable.type.value,
            variable_instructions=variable.instructions,
            incorrect_examples=incorrect_examples[:10],  # Limit to 10 examples
        )

    async def _generate_alternatives(
        self,
        current_prompt_text: str,
        variable_name: str,
        variable_type: str,
        variable_instructions: str,
        incorrect_examples: List[Dict[str, Any]],
    ) -> List[PromptAlternative]:
        """Generate refined prompt alternatives using LLM."""

        examples_text = json.dumps(incorrect_examples, indent=2, default=str)

        system_msg = """You are a prompt engineering expert. Your task is to analyze extraction errors
and generate improved prompts. You will receive the current prompt, variable definition,
and examples of incorrect extractions with user corrections.

Generate 2-3 alternative prompts that address the identified issues. Each alternative
should focus on a different improvement strategy.

Respond with a JSON object:
{
    "alternatives": [
        {
            "prompt_text": "the full refined prompt text",
            "explanation": "what this version improves and why",
            "focus": "precision|recall|format|clarity"
        }
    ]
}"""

        user_msg = f"""Variable: {variable_name} (type: {variable_type})
Original instructions: {variable_instructions}

Current prompt:
---
{current_prompt_text[:3000]}
---

Incorrect extractions (extracted vs. correct):
{examples_text}

Generate 2-3 improved prompt alternatives that address these errors."""

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_msg),
                HumanMessage(content=user_msg),
            ])

            result = json.loads(response.content)
            alternatives = []
            for alt in result.get("alternatives", []):
                alternatives.append(PromptAlternative(
                    prompt_text=alt["prompt_text"],
                    explanation=alt.get("explanation", ""),
                    focus=alt.get("focus", "general"),
                ))
            return alternatives

        except Exception as e:
            logger.error(f"Refiner LLM call failed: {e}")
            return []

    async def apply_alternative(
        self,
        db: AsyncSession,
        variable_id: UUID,
        alternative: PromptAlternative,
    ) -> Optional[Prompt]:
        """
        Apply a selected alternative as a new prompt version.

        Args:
            db: Database session
            variable_id: Variable UUID
            alternative: Selected PromptAlternative

        Returns:
            New Prompt record or None
        """
        # Get current prompt version
        result = await db.execute(
            select(Prompt)
            .where(Prompt.variable_id == variable_id)
            .order_by(Prompt.version.desc())
            .limit(1)
        )
        current_prompt = result.scalar_one_or_none()

        if not current_prompt:
            return None

        # Deactivate current prompt
        current_prompt.is_active = False

        # Create new version
        new_prompt = Prompt(
            variable_id=variable_id,
            prompt_text=alternative.prompt_text,
            model_config_=current_prompt.model_config_,
            version=current_prompt.version + 1,
            is_active=True,
        )

        db.add(new_prompt)
        await db.commit()
        await db.refresh(new_prompt)

        logger.info(
            f"Applied refined prompt v{new_prompt.version} for variable {variable_id} "
            f"(focus: {alternative.focus})"
        )
        return new_prompt
