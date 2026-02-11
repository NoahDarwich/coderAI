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

logger = logging.getLogger(__name__)

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

        response = await self.llm.ainvoke(messages)

        try:
            result = json.loads(response.content)
            return result.get("variables", [])
        except json.JSONDecodeError:
            logger.error(f"Failed to parse variable suggestions: {response.content[:200]}")
            return []

    async def clear_history(self, project_id: UUID) -> None:
        """Clear conversation history for a project."""
        if self.redis:
            key = f"copilot:{project_id}:history"
            await self.redis.delete(key)
