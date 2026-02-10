"""
FeedbackAnalyzer service for analyzing user feedback and refining prompts.

This service identifies patterns in user corrections to improve extraction quality.
"""
import logging
from collections import defaultdict
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.extraction import Extraction
from src.models.extraction_feedback import ExtractionFeedback
from src.models.prompt import Prompt
from src.models.variable import Variable

logger = logging.getLogger(__name__)


class FeedbackPattern:
    """
    Represents a pattern identified from user feedback.
    
    Attributes:
        variable_id: Variable UUID
        error_count: Number of incorrect extractions
        common_issues: List of common issues identified
        suggested_refinement: Suggested prompt refinement
    """
    def __init__(
        self,
        variable_id: UUID,
        error_count: int,
        common_issues: List[str],
        suggested_refinement: Optional[str] = None
    ):
        self.variable_id = variable_id
        self.error_count = error_count
        self.common_issues = common_issues
        self.suggested_refinement = suggested_refinement


class FeedbackAnalyzer:
    """
    Service for analyzing extraction feedback and refining prompts.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize feedback analyzer.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def analyze_variable_feedback(
        self,
        variable_id: UUID,
        min_feedback_count: int = 3
    ) -> Optional[FeedbackPattern]:
        """
        Analyze feedback for a specific variable to identify patterns.
        
        Args:
            variable_id: Variable UUID
            min_feedback_count: Minimum feedback entries needed for analysis
        
        Returns:
            FeedbackPattern if patterns found, None otherwise
        """
        # Get all feedback for this variable's extractions
        result = await self.db.execute(
            select(ExtractionFeedback, Extraction)
            .join(Extraction, ExtractionFeedback.extraction_id == Extraction.id)
            .where(Extraction.variable_id == variable_id)
        )
        feedback_rows = result.all()
        
        if len(feedback_rows) < min_feedback_count:
            return None
        
        # Analyze feedback
        error_count = 0
        incorrect_extractions = []
        
        for feedback, extraction in feedback_rows:
            if not feedback.is_correct:
                error_count += 1
                incorrect_extractions.append({
                    'extraction': extraction,
                    'feedback': feedback
                })
        
        # Identify common issues from comments
        common_issues = self._identify_common_issues(feedback_rows)
        
        # Calculate error rate
        error_rate = error_count / len(feedback_rows) if feedback_rows else 0
        
        # Generate refinement suggestion if error rate is significant
        suggested_refinement = None
        if error_rate > 0.3:  # More than 30% errors
            suggested_refinement = self._generate_refinement_suggestion(
                common_issues,
                incorrect_extractions
            )
        
        return FeedbackPattern(
            variable_id=variable_id,
            error_count=error_count,
            common_issues=common_issues,
            suggested_refinement=suggested_refinement
        )
    
    async def refine_prompt_from_feedback(
        self,
        variable_id: UUID,
        pattern: FeedbackPattern
    ) -> Optional[Prompt]:
        """
        Create a new prompt version based on feedback patterns.
        
        Args:
            variable_id: Variable UUID
            pattern: Feedback pattern with refinement suggestions
        
        Returns:
            New prompt version if created, None otherwise
        """
        if not pattern.suggested_refinement:
            logger.info(f"No refinement suggested for variable {variable_id}")
            return None
        
        # Get current prompt
        result = await self.db.execute(
            select(Prompt)
            .where(Prompt.variable_id == variable_id)
            .order_by(Prompt.version.desc())
            .limit(1)
        )
        current_prompt = result.scalar_one_or_none()
        
        if not current_prompt:
            logger.error(f"No prompt found for variable {variable_id}")
            return None
        
        # Create refined prompt
        refined_prompt_text = self._apply_refinement(
            current_prompt.prompt_text,
            pattern.suggested_refinement
        )
        
        # Create new prompt version
        new_prompt = Prompt(
            variable_id=variable_id,
            prompt_text=refined_prompt_text,
            model_config=current_prompt.model_config,
            version=current_prompt.version + 1
        )
        
        self.db.add(new_prompt)
        await self.db.commit()
        await self.db.refresh(new_prompt)
        
        logger.info(
            f"Created new prompt version {new_prompt.version} for variable {variable_id}"
        )
        
        return new_prompt
    
    def _identify_common_issues(
        self,
        feedback_rows: List[tuple]
    ) -> List[str]:
        """
        Identify common issues from feedback comments.
        
        Args:
            feedback_rows: List of (feedback, extraction) tuples
        
        Returns:
            List of common issue descriptions
        """
        issues = []
        issue_keywords = {
            'missing': 'extraction misses information',
            'wrong': 'extraction returns incorrect value',
            'format': 'extraction has formatting issues',
            'null': 'extraction returns null when value exists',
            'hallucination': 'extraction hallucinates non-existent information'
        }
        
        # Count keyword occurrences in comments
        keyword_counts = defaultdict(int)
        
        for feedback, extraction in feedback_rows:
            if not feedback.is_correct and feedback.user_comment:
                comment_lower = feedback.user_comment.lower()
                for keyword in issue_keywords:
                    if keyword in comment_lower:
                        keyword_counts[keyword] += 1
        
        # Add issues that appear in multiple feedback entries
        for keyword, count in keyword_counts.items():
            if count >= 2:  # At least 2 occurrences
                issues.append(issue_keywords[keyword])
        
        return issues
    
    def _generate_refinement_suggestion(
        self,
        common_issues: List[str],
        incorrect_extractions: List[Dict]
    ) -> str:
        """
        Generate prompt refinement suggestion based on common issues.
        
        Args:
            common_issues: List of identified common issues
            incorrect_extractions: List of incorrect extraction data
        
        Returns:
            Refinement suggestion text
        """
        suggestions = []
        
        if 'extraction misses information' in common_issues:
            suggestions.append(
                "Be more thorough when searching for the information. "
                "Check the entire document, including headers, footers, and tables."
            )
        
        if 'extraction returns incorrect value' in common_issues:
            suggestions.append(
                "Pay closer attention to the specific field being requested. "
                "Ensure the extracted value matches the exact criteria."
            )
        
        if 'extraction has formatting issues' in common_issues:
            suggestions.append(
                "Return the value in the exact format requested. "
                "Do not add extra formatting or modify the original format."
            )
        
        if 'extraction returns null when value exists' in common_issues:
            suggestions.append(
                "Search more carefully - the value may be in a different format "
                "or location than expected."
            )
        
        if 'extraction hallucinates non-existent information' in common_issues:
            suggestions.append(
                "CRITICAL: Only extract information that explicitly appears in the document. "
                "Never infer or guess. If unsure, return null."
            )
        
        return "\n\n".join(suggestions)
    
    def _apply_refinement(
        self,
        original_prompt: str,
        refinement: str
    ) -> str:
        """
        Apply refinement suggestion to existing prompt.
        
        Args:
            original_prompt: Original prompt text
            refinement: Refinement suggestion
        
        Returns:
            Refined prompt text
        """
        # Add refinement as additional instructions
        refined_prompt = f"{original_prompt}\n\n## Important Corrections Based on Feedback:\n{refinement}"
        
        return refined_prompt


async def analyze_and_refine_prompts(
    db: AsyncSession,
    variable_ids: Optional[List[UUID]] = None
) -> Dict[UUID, Optional[Prompt]]:
    """
    Convenience function to analyze feedback and refine prompts for multiple variables.
    
    Args:
        db: Database session
        variable_ids: List of variable IDs to analyze (None = all variables)
    
    Returns:
        Dictionary mapping variable_id to new prompt (if created)
    """
    analyzer = FeedbackAnalyzer(db)
    results = {}
    
    # Get variables to analyze
    if variable_ids:
        query = select(Variable).where(Variable.id.in_(variable_ids))
    else:
        query = select(Variable)
    
    result = await db.execute(query)
    variables = result.scalars().all()
    
    for variable in variables:
        try:
            # Analyze feedback
            pattern = await analyzer.analyze_variable_feedback(variable.id)
            
            # Refine prompt if pattern suggests it
            new_prompt = None
            if pattern and pattern.suggested_refinement:
                new_prompt = await analyzer.refine_prompt_from_feedback(
                    variable.id,
                    pattern
                )
            
            results[variable.id] = new_prompt
            
        except Exception as e:
            logger.exception(f"Error analyzing feedback for variable {variable.id}: {str(e)}")
            results[variable.id] = None
    
    return results
