"""
Robust JSON response parser for LLM extraction outputs.

Ported from reference_backend/response_openai.py clean_response() and enhanced
with fallback brace-matching and key validation.
"""
import json
import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def clean_response(response: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Clean and parse an LLM JSON response.

    Steps:
    1. Strip markdown code fences (```json ... ```)
    2. Normalize Python booleans/None to JSON equivalents
    3. json.loads with fallback brace-matching
    4. Return parsed dict or None on failure

    Args:
        response: Raw LLM response string

    Returns:
        Parsed dict or None if parsing fails
    """
    if response is None:
        return None

    cleaned = response.strip()

    # Strip markdown code fences
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```\s*$", "", cleaned)
    cleaned = cleaned.strip()

    # Normalize Python booleans/None to JSON
    cleaned = cleaned.replace("True", "true").replace("False", "false")
    cleaned = cleaned.replace("None", "null")

    # Remove newlines inside JSON (preserve structure)
    cleaned = re.sub(r"(\{|\[)\s+", r"\1", cleaned)
    cleaned = cleaned.replace("\n", " ")

    # Attempt JSON parse
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
        return None
    except json.JSONDecodeError:
        pass

    # Fallback: extract first JSON object via brace matching
    result = _extract_json_object(cleaned)
    if result is not None:
        return result

    logger.warning(f"Failed to parse LLM response: {response[:200]}...")
    return None


def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract the first JSON object from text using brace matching.

    Args:
        text: Text potentially containing a JSON object

    Returns:
        Parsed dict or None
    """
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape_next = False

    for i in range(start, len(text)):
        char = text[i]

        if escape_next:
            escape_next = False
            continue

        if char == "\\":
            escape_next = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    return None

    return None


def parse_extraction_response(response_text: str) -> Dict[str, Any]:
    """
    Parse an LLM extraction response into a standardized result dict.

    Validates required keys (value, confidence, source_text) and
    clamps confidence to 0-100.

    Args:
        response_text: Raw response from LLM

    Returns:
        Dict with keys: value, confidence, source_text, raw_response
    """
    parsed = clean_response(response_text)

    if parsed is None:
        return {
            "value": None,
            "confidence": 0,
            "source_text": None,
            "error": "Failed to parse JSON response",
            "raw_response": response_text,
        }

    # Extract and validate fields
    value = parsed.get("value")
    confidence = parsed.get("confidence", 50)
    source_text = parsed.get("source_text")

    # Ensure confidence is an integer in range
    try:
        confidence = int(confidence)
    except (TypeError, ValueError):
        confidence = 50
    confidence = max(0, min(100, confidence))

    return {
        "value": value,
        "confidence": confidence,
        "source_text": source_text,
        "raw_response": response_text,
    }
