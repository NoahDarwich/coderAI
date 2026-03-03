"""
Mock LLM client for development/testing without real API calls.

Activated automatically when OPENAI_API_KEY is unset, empty, or still the
placeholder value ("sk-your-...").  Returns realistic fake responses so every
feature of the UI can be exercised end-to-end at zero cost.
"""
import json
import logging
import re
from typing import Any, List

logger = logging.getLogger(__name__)


def is_mock_mode() -> bool:
    """Return True when no real OpenAI key is configured."""
    from src.core.config import settings
    key = settings.OPENAI_API_KEY or ""
    return not key or key.startswith("sk-your") or "placeholder" in key.lower()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _text_of(messages: list) -> tuple[str, str]:
    """Return (system_text, user_text) lowercased from a message list."""
    system, user = "", ""
    for msg in messages:
        # Support both dicts (OpenAI style) and LangChain message objects
        if hasattr(msg, "content"):
            content = msg.content or ""
            typ = type(msg).__name__.lower()
            if "system" in typ:
                system += content.lower()
            else:
                user += content.lower()
        else:
            role = (msg.get("role") or "").lower()
            content = (msg.get("content") or "").lower()
            if role == "system":
                system += content
            else:
                user += content
    return system, user


# ── Mock for AsyncOpenAI (used by TextExtractionService) ─────────────────────

class _MockMessage:
    def __init__(self, content: str):
        self.content = content


class _MockChoice:
    def __init__(self, content: str):
        self.message = _MockMessage(content)


class _MockCompletion:
    def __init__(self, content: str):
        self.choices = [_MockChoice(content)]


class _MockCompletions:
    async def create(self, model: str, messages: list, **kwargs) -> _MockCompletion:
        system, user = _text_of(messages)
        content = _build_extraction_json(system, user)
        logger.debug("[MockLLM] fake extraction response")
        return _MockCompletion(content)


class _MockChat:
    def __init__(self):
        self.completions = _MockCompletions()


class MockOpenAIClient:
    """Drop-in replacement for ``openai.AsyncOpenAI`` in TextExtractionService."""
    def __init__(self, **_kwargs):
        self.chat = _MockChat()


def _build_extraction_json(system: str, user: str) -> str:
    """Return a plausible extraction JSON based on variable type clues in system prompt."""

    # Entity identification call → different response shape
    if '"entities"' in system or ("entity" in system and "index" in system):
        return json.dumps({
            "entities": [
                {"index": 0, "label": "Entity A", "text": "First entity found in document"},
                {"index": 1, "label": "Entity B", "text": "Second entity found in document"},
            ]
        })

    source = (user[:120]).replace("\n", " ") or "Found in document text."

    if "yyyy-mm-dd" in system or ("date" in system and "iso" in system):
        value = "2024-03-15"
    elif "boolean" in system or ("true" in system and "false" in system and "null" in system):
        value = "true"
    elif "categor" in system:
        match = re.search(r"categories:\s*([^\n\r{]+)", system)
        if match:
            cats = [c.strip().strip("'\"") for c in match.group(1).split(",") if c.strip()]
            value = cats[0] if cats else "Category A"
        else:
            value = "Category A"
    elif "numeric" in system or ("number" in system and "units" in system):
        value = "42"
    elif "location" in system or "geographic" in system:
        value = "New York, NY"
    else:
        value = "Mock extracted value"

    return json.dumps({
        "value": value,
        "confidence": 82,
        "source_text": source,
        "explanation": "[Mock] No real API call — running in dev/mock mode.",
    })


# ── Mock for ChatOpenAI (used by LangChain agents) ────────────────────────────

class _MockAIMessage:
    def __init__(self, content: str):
        self.content = content


class MockChatOpenAI:
    """Drop-in replacement for ``langchain_openai.ChatOpenAI``."""
    def __init__(self, **_kwargs):
        pass

    async def ainvoke(self, messages: list) -> _MockAIMessage:
        system, user = _text_of(messages)
        content = _build_chat_response(system, user)
        logger.debug("[MockLLM] fake chat response")
        return _MockAIMessage(content)


def _build_chat_response(system: str, user: str) -> str:
    """Route to the right fake JSON or prose based on prompt intent."""
    combined = system + " " + user

    # Variable suggestions
    if "suggest" in combined and "variables" in combined and "json" in combined:
        return json.dumps({"variables": [
            {
                "name": "title",
                "type": "TEXT",
                "instructions": "Extract the document title or main heading.",
                "classification_rules": None,
            },
            {
                "name": "publication_date",
                "type": "DATE",
                "instructions": "Extract the primary publication or event date (YYYY-MM-DD).",
                "classification_rules": None,
            },
            {
                "name": "document_type",
                "type": "CATEGORY",
                "instructions": "Classify the document into one of the provided categories.",
                "classification_rules": {"categories": ["Policy", "Report", "Letter", "Other"]},
            },
            {
                "name": "author",
                "type": "TEXT",
                "instructions": "Extract the name(s) of the author(s) or issuing organization.",
                "classification_rules": None,
            },
        ]})

    # Unit of observation
    if "rows_per_document" in combined or "unit of observation" in combined:
        return json.dumps({
            "rows_per_document": "single",
            "entity_identification_pattern": None,
            "label": "One row per document",
            "explanation": "[Mock] Default single-row unit of observation for development mode.",
        })

    # Project defaults / smart suggestions
    if "project_name_pattern" in combined or "suggested_variable_types" in combined:
        return json.dumps({
            "project_name_pattern": "Research Extraction - {date}",
            "language": "en",
            "suggested_variable_types": [
                {"name": "title", "type": "TEXT", "description": "Document title"},
                {"name": "date", "type": "DATE", "description": "Document date"},
                {"name": "author", "type": "TEXT", "description": "Author or issuing body"},
            ],
            "explanation": "[Mock] Default suggestions — running in dev/mock mode.",
        })

    # Prompt refinement alternatives
    if "alternatives" in combined and "prompt" in combined and "focus" in combined:
        return json.dumps({"alternatives": [
            {
                "prompt_text": (
                    "Extract the requested information precisely. "
                    "Only include values explicitly stated in the text. "
                    "Return JSON: {\"value\": ..., \"confidence\": 0-100, \"source_text\": \"...\"}."
                ),
                "explanation": "[Mock] Alt 1: higher precision, fewer false positives.",
                "focus": "precision",
            },
            {
                "prompt_text": (
                    "Search broadly for any information related to the variable, "
                    "including indirect references and synonyms. "
                    "Return JSON: {\"value\": ..., \"confidence\": 0-100, \"source_text\": \"...\"}."
                ),
                "explanation": "[Mock] Alt 2: higher recall, broader matching.",
                "focus": "recall",
            },
        ]})

    # Generic copilot chat
    return (
        "I'm running in **mock mode** — no real OpenAI calls are being made.\n\n"
        "In production I can:\n"
        "- Suggest extraction variables based on your domain and sample documents\n"
        "- Refine extraction instructions for better accuracy\n"
        "- Recommend classification categories for CATEGORY variables\n"
        "- Answer questions about extraction strategy\n\n"
        "Add a real `OPENAI_API_KEY` to `.env` to enable full AI features."
    )
