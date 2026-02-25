"""
AI Co-pilot agent for guided project setup.

Uses LangChain ChatOpenAI to provide an interactive assistant that helps users
define variables, refine instructions, and configure extraction settings.
Conversation state is stored in Redis keyed by project_id.
"""
import json
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.core.config import settings
from src.core.tracing import get_tracer

logger = logging.getLogger(__name__)
_tracer = get_tracer(__name__)

# Maximum conversation turns to keep in context
MAX_HISTORY_TURNS = 20


def _build_system_prompt(
    project_name: str,
    domain: Optional[str],
    language: str,
    existing_variables: List[Dict[str, Any]],
) -> str:
    """Build the co-pilot system prompt with project context."""
    vars_desc = ""
    if existing_variables:
        vars_list = "\n".join(
            f"  - {v['name']} ({v['type']}): {v.get('instructions', '')[:100]}"
            for v in existing_variables
        )
        vars_desc = f"\n\nExisting variables:\n{vars_list}"

    return f"""You are an AI co-pilot for a data extraction platform called coderAI.
You help researchers set up extraction projects by suggesting variables, refining
extraction instructions, and configuring classification rules.

Current project: {project_name}
Domain: {domain or 'Not specified'}
Language: {language}
{vars_desc}

Your capabilities:
1. **Suggest variables** — Based on the domain and document samples, propose extraction variables
   with name, type (TEXT, NUMBER, DATE, CATEGORY, BOOLEAN, LOCATION), and instructions.
2. **Refine instructions** — Improve existing variable instructions for better extraction quality.
3. **Suggest classification rules** — For CATEGORY variables, propose categories and rules.
4. **Answer questions** — Explain extraction concepts, help debug quality issues.

Guidelines:
- Be concise and actionable
- When suggesting variables, output them as structured JSON
- Always consider the domain context when making suggestions
- If you need more information, ask specific questions
- Respond in the same language as the user's message"""


class CopilotAgent:
    """
    Co-pilot agent for interactive project setup assistance.

    Conversation history is stored in Redis for persistence across requests.
    """

    def __init__(self, redis=None):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL or "gpt-4",
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY,
        )
        self.redis = redis

    async def _load_history(self, project_id: UUID) -> List[Dict[str, str]]:
        """Load conversation history from Redis."""
        if not self.redis:
            return []
        key = f"copilot:{project_id}:history"
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return []

    async def _save_history(
        self, project_id: UUID, history: List[Dict[str, str]]
    ) -> None:
        """Save conversation history to Redis (keep last N turns)."""
        if not self.redis:
            return
        # Keep only last MAX_HISTORY_TURNS entries
        trimmed = history[-MAX_HISTORY_TURNS * 2 :]
        key = f"copilot:{project_id}:history"
        await self.redis.set(key, json.dumps(trimmed), ex=86400)  # 24h TTL

    async def chat(
        self,
        project_id: UUID,
        user_message: str,
        project_name: str,
        domain: Optional[str] = None,
        language: str = "en",
        existing_variables: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Send a message to the co-pilot and get a response.

        Args:
            project_id: Project UUID (used for conversation state)
            user_message: User's message
            project_name: Project name for context
            domain: Project domain
            language: Project language
            existing_variables: List of existing variable dicts

        Returns:
            Co-pilot response text
        """
        system_prompt = _build_system_prompt(
            project_name=project_name,
            domain=domain,
            language=language,
            existing_variables=existing_variables or [],
        )

        # Load history
        history = await self._load_history(project_id)

        # Build messages
        messages = [SystemMessage(content=system_prompt)]
        for entry in history:
            if entry["role"] == "user":
                messages.append(HumanMessage(content=entry["content"]))
            else:
                messages.append(AIMessage(content=entry["content"]))

        messages.append(HumanMessage(content=user_message))

        # Call LLM
        with _tracer.start_as_current_span("copilot.chat") as span:
            span.set_attribute("llm.model", settings.OPENAI_MODEL or "gpt-4")
            span.set_attribute("text.length", len(user_message))
            response = await self.llm.ainvoke(messages)
        assistant_text = response.content

        # Save updated history
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": assistant_text})
        await self._save_history(project_id, history)

        return assistant_text

    async def suggest_variables(
        self,
        domain: str,
        sample_texts: List[str],
        language: str = "en",
    ) -> List[Dict[str, Any]]:
        """
        Suggest extraction variables based on domain and sample documents.

        Args:
            domain: Project domain description
            sample_texts: List of sample document texts (truncated)
            language: Document language

        Returns:
            List of suggested variable dicts with name, type, instructions
        """
        samples_text = ""
        for i, text in enumerate(sample_texts[:3]):
            # Truncate each sample
            truncated = text[:2000] if len(text) > 2000 else text
            samples_text += f"\n--- Sample {i + 1} ---\n{truncated}\n"

        prompt = f"""Based on the following domain and sample documents, suggest extraction variables.

Domain: {domain}
Language: {language}

{samples_text}

Return a JSON object with this structure:
{{
    "variables": [
        {{
            "name": "variable_name",
            "type": "TEXT|NUMBER|DATE|CATEGORY|BOOLEAN|LOCATION",
            "instructions": "Clear extraction instructions",
            "classification_rules": null or {{"categories": ["cat1", "cat2"]}} for CATEGORY type
        }}
    ]
}}

Suggest 3-8 variables that would be most useful for this domain. Be specific in instructions."""

        messages = [
            SystemMessage(
                content="You are a data extraction expert. Suggest extraction variables based on document analysis. Respond only with valid JSON."
            ),
            HumanMessage(content=prompt),
        ]

        with _tracer.start_as_current_span("copilot.suggest_variables") as span:
            span.set_attribute("llm.model", settings.OPENAI_MODEL or "gpt-4")
            span.set_attribute("variables.sample_count", len(sample_texts))
            response = await self.llm.ainvoke(messages)

        try:
            result = json.loads(response.content)
            return result.get("variables", [])
        except json.JSONDecodeError:
            logger.error(f"Failed to parse variable suggestions: {response.content[:200]}")
            return []

    async def suggest_unit_of_observation(
        self,
        domain: str,
        document_type: Optional[str] = None,
        sample_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Suggest a unit of observation configuration for a project.

        Uses rule-based defaults by document type and domain keywords.
        If sample_text is provided, calls LLM for a smarter suggestion.

        Returns:
            Dict with 'suggestion', 'explanation', 'alternatives'
        """
        # Rule-based defaults
        single_row = {
            "rows_per_document": "single",
            "entity_identification_pattern": None,
            "label": "One row per document",
        }
        multi_row_people = {
            "rows_per_document": "multiple",
            "entity_identification_pattern": "Each person or individual mentioned",
            "label": "One row per person mentioned",
        }
        multi_row_items = {
            "rows_per_document": "multiple",
            "entity_identification_pattern": "Each distinct item, entry, or record",
            "label": "One row per item",
        }

        doc_type_lower = (document_type or "").lower()
        domain_lower = domain.lower()

        # Heuristic: contracts, reports, letters → single row
        single_keywords = ["contract", "report", "letter", "memo", "policy", "brief"]
        multi_people_keywords = ["news", "interview", "survey", "census", "biography"]
        multi_item_keywords = ["invoice", "ledger", "catalog", "inventory", "log", "table"]

        suggestion = single_row
        explanation = "Documents in this domain typically map to one row per document."
        alternatives = [multi_row_people, multi_row_items]

        for kw in multi_people_keywords:
            if kw in doc_type_lower or kw in domain_lower:
                suggestion = multi_row_people
                explanation = f"'{kw}' documents often contain multiple people or subjects."
                alternatives = [single_row, multi_row_items]
                break

        for kw in multi_item_keywords:
            if kw in doc_type_lower or kw in domain_lower:
                suggestion = multi_row_items
                explanation = f"'{kw}' documents often contain multiple distinct items."
                alternatives = [single_row, multi_row_people]
                break

        for kw in single_keywords:
            if kw in doc_type_lower or kw in domain_lower:
                suggestion = single_row
                explanation = f"'{kw}' documents typically represent a single record."
                alternatives = [multi_row_people, multi_row_items]
                break

        # LLM-enhanced suggestion when sample_text is provided
        if sample_text:
            try:
                prompt = f"""Analyze this document sample and suggest the best unit of observation.

Domain: {domain}
Document type: {document_type or 'unspecified'}

Sample text (first 2000 chars):
{sample_text[:2000]}

Should each document produce a single row of data, or multiple rows (one per entity)?
If multiple, what pattern identifies each entity?

Return JSON:
{{
    "rows_per_document": "single" or "multiple",
    "entity_identification_pattern": "pattern description or null",
    "label": "human-readable label",
    "explanation": "why this is the best choice"
}}"""

                messages = [
                    SystemMessage(content="You are a data extraction expert. Respond only with valid JSON."),
                    HumanMessage(content=prompt),
                ]
                response = await self.llm.ainvoke(messages)
                result = json.loads(response.content)

                suggestion = {
                    "rows_per_document": result.get("rows_per_document", suggestion["rows_per_document"]),
                    "entity_identification_pattern": result.get("entity_identification_pattern"),
                    "label": result.get("label", suggestion["label"]),
                }
                explanation = result.get("explanation", explanation)
            except Exception as e:
                logger.warning(f"LLM UoO suggestion failed, using rule-based: {e}")

        return {
            "suggestion": suggestion,
            "explanation": explanation,
            "alternatives": alternatives,
        }

    async def suggest_defaults(
        self,
        domain: str,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Suggest smart project defaults based on domain.

        Returns:
            Dict with project_name_pattern, language, suggested_variable_types, explanation
        """
        prompt = f"""For a data extraction project in the domain "{domain}", suggest:
1. A project name pattern (e.g., "{{domain}} Extraction - {{date}}")
2. The likely document language (given hint: {language or 'auto-detect'})
3. 3-5 recommended variable types with name and type for this domain

Variable types available: TEXT, NUMBER, DATE, CATEGORY, BOOLEAN, LOCATION

Return JSON:
{{
    "project_name_pattern": "suggested pattern",
    "language": "two-letter code",
    "suggested_variable_types": [
        {{"name": "variable name", "type": "TYPE", "description": "what it captures"}}
    ],
    "explanation": "brief explanation"
}}"""

        try:
            messages = [
                SystemMessage(content="You are a data extraction expert. Respond only with valid JSON."),
                HumanMessage(content=prompt),
            ]
            response = await self.llm.ainvoke(messages)
            result = json.loads(response.content)
            return {
                "project_name_pattern": result.get("project_name_pattern", f"{domain} Extraction"),
                "language": result.get("language", language or "en"),
                "suggested_variable_types": result.get("suggested_variable_types", []),
                "explanation": result.get("explanation", ""),
            }
        except Exception as e:
            logger.warning(f"LLM defaults suggestion failed: {e}")
            return {
                "project_name_pattern": f"{domain} Extraction",
                "language": language or "en",
                "suggested_variable_types": [],
                "explanation": "Could not generate AI suggestions; using basic defaults.",
            }

    async def clear_history(self, project_id: UUID) -> None:
        """Clear conversation history for a project."""
        if self.redis:
            key = f"copilot:{project_id}:history"
            await self.redis.delete(key)
