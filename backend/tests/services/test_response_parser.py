"""
Tests for the response parser service.
"""
import pytest

from src.services.response_parser import clean_response, parse_extraction_response


class TestCleanResponse:
    """Tests for clean_response function."""

    def test_none_input(self):
        assert clean_response(None) is None

    def test_valid_json(self):
        result = clean_response('{"value": "test", "confidence": 90}')
        assert result == {"value": "test", "confidence": 90}

    def test_strips_markdown_code_fence(self):
        result = clean_response('```json\n{"value": "test"}\n```')
        assert result == {"value": "test"}

    def test_strips_code_fence_no_language(self):
        result = clean_response('```\n{"value": "test"}\n```')
        assert result == {"value": "test"}

    def test_normalizes_python_booleans(self):
        result = clean_response('{"value": True, "active": False}')
        assert result == {"value": True, "active": False}

    def test_normalizes_python_none(self):
        result = clean_response('{"value": None}')
        assert result == {"value": None}

    def test_handles_newlines_in_json(self):
        result = clean_response('{\n  "value": "test",\n  "confidence": 85\n}')
        assert result == {"value": "test", "confidence": 85}

    def test_fallback_brace_matching(self):
        result = clean_response('Here is the result: {"value": "test"} end.')
        assert result == {"value": "test"}

    def test_invalid_json_returns_none(self):
        assert clean_response("not json at all") is None

    def test_array_response_returns_none(self):
        # We only accept dicts, not arrays
        assert clean_response('[1, 2, 3]') is None

    def test_nested_json(self):
        result = clean_response('{"value": {"key": "nested"}, "confidence": 80}')
        assert result == {"value": {"key": "nested"}, "confidence": 80}

    def test_empty_string(self):
        assert clean_response("") is None

    def test_whitespace_only(self):
        assert clean_response("   \n  ") is None


class TestParseExtractionResponse:
    """Tests for parse_extraction_response function."""

    def test_valid_response(self):
        response = '{"value": "2024-01-15", "confidence": 95, "source_text": "January 15, 2024"}'
        result = parse_extraction_response(response)
        assert result["value"] == "2024-01-15"
        assert result["confidence"] == 95
        assert result["source_text"] == "January 15, 2024"
        assert result["raw_response"] == response

    def test_missing_confidence_defaults_to_50(self):
        result = parse_extraction_response('{"value": "test"}')
        assert result["confidence"] == 50

    def test_confidence_clamped_to_100(self):
        result = parse_extraction_response('{"value": "x", "confidence": 150}')
        assert result["confidence"] == 100

    def test_confidence_clamped_to_0(self):
        result = parse_extraction_response('{"value": "x", "confidence": -10}')
        assert result["confidence"] == 0

    def test_invalid_confidence_type(self):
        result = parse_extraction_response('{"value": "x", "confidence": "high"}')
        assert result["confidence"] == 50

    def test_null_value(self):
        result = parse_extraction_response('{"value": null, "confidence": 20}')
        assert result["value"] is None
        assert result["confidence"] == 20

    def test_unparseable_response(self):
        result = parse_extraction_response("not json")
        assert result["value"] is None
        assert result["confidence"] == 0
        assert "error" in result

    def test_markdown_wrapped_response(self):
        response = '```json\n{"value": "protest", "confidence": 88, "source_text": "a protest"}\n```'
        result = parse_extraction_response(response)
        assert result["value"] == "protest"
        assert result["confidence"] == 88
