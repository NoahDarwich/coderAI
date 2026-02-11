"""
Tests for the post-processing service.
"""
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from src.models.variable import VariableType
from src.services.post_processor import (
    apply_default,
    check_confidence,
    coerce_type,
    handle_multiple_values,
    post_process_extraction,
    validate_value,
)


def _make_variable(
    var_type=VariableType.TEXT,
    edge_cases=None,
    uncertainty_handling=None,
    max_values=1,
    default_value=None,
):
    """Create a mock Variable for testing."""
    var = MagicMock()
    var.id = uuid4()
    var.name = "test_var"
    var.type = var_type
    var.edge_cases = edge_cases
    var.uncertainty_handling = uncertainty_handling
    var.max_values = max_values
    var.default_value = default_value
    return var


class TestCoerceType:
    """Tests for coerce_type function."""

    def test_number_from_string(self):
        assert coerce_type("42", VariableType.NUMBER) == 42

    def test_number_float(self):
        assert coerce_type("3.14", VariableType.NUMBER) == 3.14

    def test_number_with_units(self):
        assert coerce_type("$500", VariableType.NUMBER) == 500

    def test_number_negative(self):
        assert coerce_type("-10", VariableType.NUMBER) == -10

    def test_number_none(self):
        assert coerce_type(None, VariableType.NUMBER) is None

    def test_number_empty_string(self):
        assert coerce_type("N/A", VariableType.NUMBER) is None

    def test_date_iso(self):
        assert coerce_type("2024-01-15", VariableType.DATE) == "2024-01-15"

    def test_date_us_format(self):
        assert coerce_type("01/15/2024", VariableType.DATE) == "2024-01-15"

    def test_date_passthrough(self):
        # Unknown format passes through
        assert coerce_type("January 15th", VariableType.DATE) == "January 15th"

    def test_boolean_true(self):
        assert coerce_type("true", VariableType.BOOLEAN) is True

    def test_boolean_false(self):
        assert coerce_type("false", VariableType.BOOLEAN) is False

    def test_boolean_yes(self):
        assert coerce_type("yes", VariableType.BOOLEAN) is True

    def test_boolean_no(self):
        assert coerce_type("no", VariableType.BOOLEAN) is False

    def test_boolean_none(self):
        assert coerce_type(None, VariableType.BOOLEAN) is None

    def test_boolean_ambiguous(self):
        assert coerce_type("maybe", VariableType.BOOLEAN) is None

    def test_text_passthrough(self):
        assert coerce_type("hello world", VariableType.TEXT) == "hello world"

    def test_category_passthrough(self):
        assert coerce_type("protest", VariableType.CATEGORY) == "protest"


class TestValidateValue:
    """Tests for validate_value function."""

    def test_no_rules(self):
        var = _make_variable()
        is_valid, msg = validate_value("anything", var)
        assert is_valid is True

    def test_range_valid(self):
        var = _make_variable(edge_cases={
            "validation_rules": [
                {"rule_type": "range", "parameters": {"min": 0, "max": 100}}
            ]
        })
        is_valid, _ = validate_value(50, var)
        assert is_valid is True

    def test_range_too_high(self):
        var = _make_variable(edge_cases={
            "validation_rules": [
                {"rule_type": "range", "parameters": {"min": 0, "max": 100}}
            ]
        })
        is_valid, msg = validate_value(150, var)
        assert is_valid is False

    def test_enum_valid(self):
        var = _make_variable(edge_cases={
            "validation_rules": [
                {"rule_type": "enum", "parameters": {"values": ["protest", "riot"]}}
            ]
        })
        is_valid, _ = validate_value("protest", var)
        assert is_valid is True

    def test_enum_invalid(self):
        var = _make_variable(edge_cases={
            "validation_rules": [
                {"rule_type": "enum", "parameters": {"values": ["protest", "riot"]}}
            ]
        })
        is_valid, _ = validate_value("party", var)
        assert is_valid is False

    def test_regex_valid(self):
        var = _make_variable(edge_cases={
            "validation_rules": [
                {"rule_type": "regex", "parameters": {"pattern": r"^\d{4}-\d{2}-\d{2}$"}}
            ]
        })
        is_valid, _ = validate_value("2024-01-15", var)
        assert is_valid is True

    def test_regex_invalid(self):
        var = _make_variable(edge_cases={
            "validation_rules": [
                {"rule_type": "regex", "parameters": {"pattern": r"^\d{4}-\d{2}-\d{2}$"}}
            ]
        })
        is_valid, _ = validate_value("Jan 15", var)
        assert is_valid is False

    def test_none_value_passes(self):
        var = _make_variable(edge_cases={
            "validation_rules": [
                {"rule_type": "range", "parameters": {"min": 0, "max": 100}}
            ]
        })
        is_valid, _ = validate_value(None, var)
        assert is_valid is True


class TestApplyDefault:
    """Tests for apply_default function."""

    def test_no_default(self):
        var = _make_variable(default_value=None)
        assert apply_default(None, var) is None

    def test_applies_default_when_none(self):
        var = _make_variable(default_value="N/A")
        assert apply_default(None, var) == "N/A"

    def test_keeps_value_when_present(self):
        var = _make_variable(default_value="N/A")
        assert apply_default("actual", var) == "actual"


class TestCheckConfidence:
    """Tests for check_confidence function."""

    def test_no_threshold(self):
        var = _make_variable(uncertainty_handling={})
        meets, action = check_confidence(50, var)
        assert meets is True
        assert action == "accept"

    def test_above_threshold(self):
        var = _make_variable(uncertainty_handling={
            "confidence_threshold": 70,
            "if_uncertain_action": "flag"
        })
        meets, action = check_confidence(80, var)
        assert meets is True

    def test_below_threshold_flag(self):
        var = _make_variable(uncertainty_handling={
            "confidence_threshold": 70,
            "if_uncertain_action": "flag"
        })
        meets, action = check_confidence(50, var)
        assert meets is False
        assert action == "flag"

    def test_below_threshold_skip(self):
        var = _make_variable(uncertainty_handling={
            "confidence_threshold": 70,
            "if_uncertain_action": "skip"
        })
        meets, action = check_confidence(50, var)
        assert meets is False
        assert action == "skip"


class TestHandleMultipleValues:
    """Tests for handle_multiple_values function."""

    def test_return_first(self):
        var = _make_variable(
            uncertainty_handling={"multiple_values_action": "return_first"},
            max_values=1,
        )
        assert handle_multiple_values(["a", "b", "c"], var) == "a"

    def test_return_all(self):
        var = _make_variable(
            uncertainty_handling={"multiple_values_action": "return_all"},
            max_values=3,
        )
        assert handle_multiple_values(["a", "b", "c"], var) == ["a", "b", "c"]

    def test_return_all_limited(self):
        var = _make_variable(
            uncertainty_handling={"multiple_values_action": "return_all"},
            max_values=2,
        )
        assert handle_multiple_values(["a", "b", "c"], var) == ["a", "b"]

    def test_concatenate(self):
        var = _make_variable(
            uncertainty_handling={"multiple_values_action": "concatenate"},
            max_values=3,
        )
        assert handle_multiple_values(["a", "b"], var) == "a, b"

    def test_empty_list(self):
        var = _make_variable()
        assert handle_multiple_values([], var) is None


class TestPostProcessExtraction:
    """Tests for post_process_extraction function."""

    def test_basic_text(self):
        var = _make_variable(var_type=VariableType.TEXT)
        result = post_process_extraction("hello", 90, var)
        assert result["value"] == "hello"
        assert result["confidence"] == 90
        assert result["should_flag"] is False

    def test_coerces_number(self):
        var = _make_variable(var_type=VariableType.NUMBER)
        result = post_process_extraction("$500", 85, var)
        assert result["value"] == 500

    def test_applies_default(self):
        var = _make_variable(var_type=VariableType.TEXT, default_value="unknown")
        result = post_process_extraction(None, 0, var)
        assert result["value"] == "unknown"

    def test_flags_low_confidence(self):
        var = _make_variable(
            var_type=VariableType.TEXT,
            uncertainty_handling={"confidence_threshold": 80, "if_uncertain_action": "flag"},
        )
        result = post_process_extraction("test", 50, var)
        assert result["should_flag"] is True

    def test_skips_low_confidence(self):
        var = _make_variable(
            var_type=VariableType.TEXT,
            uncertainty_handling={"confidence_threshold": 80, "if_uncertain_action": "skip"},
        )
        result = post_process_extraction("test", 50, var)
        assert result["should_skip"] is True
        assert result["value"] is None
