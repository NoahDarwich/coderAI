"""
Post-processing service for extraction results.

Applies type coercion, validation, defaults, confidence checks,
and multi-value handling per CODERAI_REFERENCE.md Section 4.4.
"""
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.models.variable import Variable, VariableType

logger = logging.getLogger(__name__)


def coerce_type(value: Any, variable_type: VariableType) -> Any:
    """
    Coerce an extracted value to the correct type.

    Args:
        value: Raw extracted value
        variable_type: Target variable type

    Returns:
        Coerced value or original if coercion fails
    """
    if value is None:
        return None

    try:
        if variable_type == VariableType.NUMBER:
            # Handle string numbers, strip non-numeric chars (except . and -)
            if isinstance(value, str):
                cleaned = re.sub(r"[^\d.\-]", "", value)
                if not cleaned:
                    return None
                if "." in cleaned:
                    return float(cleaned)
                return int(cleaned)
            return value

        if variable_type == VariableType.DATE:
            if isinstance(value, str):
                # Try ISO format first
                for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y", "%d/%m/%Y"):
                    try:
                        dt = datetime.strptime(value.strip(), fmt)
                        return dt.strftime("%Y-%m-%d")
                    except ValueError:
                        continue
                # Return as-is if no format matches
                return value
            return value

        if variable_type == VariableType.BOOLEAN:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                lower = value.lower().strip()
                if lower in ("true", "yes", "1"):
                    return True
                if lower in ("false", "no", "0"):
                    return False
                return None
            return bool(value)

        # TEXT, CATEGORY, LOCATION — return as-is
        return value

    except (ValueError, TypeError) as e:
        logger.warning(f"Type coercion failed for {variable_type}: {e}")
        return value


def validate_value(
    value: Any,
    variable: Variable,
) -> tuple[bool, Optional[str]]:
    """
    Validate an extracted value against variable rules.

    Args:
        value: Extracted value
        variable: Variable with edge_cases config

    Returns:
        (is_valid, error_message)
    """
    if value is None:
        return True, None

    edge_cases = variable.edge_cases or {}
    rules = edge_cases.get("validation_rules", [])

    if not rules:
        return True, None

    for rule in rules:
        rule_type = rule.get("rule_type")
        params = rule.get("parameters", {})
        error_msg = rule.get("error_message", f"Validation failed: {rule_type}")

        if rule_type == "range":
            try:
                num_val = float(value)
                min_val = params.get("min")
                max_val = params.get("max")
                if min_val is not None and num_val < float(min_val):
                    return False, error_msg
                if max_val is not None and num_val > float(max_val):
                    return False, error_msg
            except (ValueError, TypeError):
                return False, f"Value is not numeric: {value}"

        elif rule_type == "regex":
            pattern = params.get("pattern")
            if pattern and isinstance(value, str):
                if not re.match(pattern, value):
                    return False, error_msg

        elif rule_type == "enum":
            allowed = params.get("values", [])
            if allowed and value not in allowed:
                return False, error_msg

    return True, None


def apply_default(value: Any, variable: Variable) -> Any:
    """
    Apply default value if extraction returned null.

    Args:
        value: Extracted value (may be None)
        variable: Variable with default_value

    Returns:
        Default value if value is None and default exists, else original value
    """
    if value is None and variable.default_value is not None:
        return variable.default_value
    return value


def check_confidence(
    confidence: int,
    variable: Variable,
) -> tuple[bool, str]:
    """
    Check if confidence meets threshold.

    Args:
        confidence: Confidence score (0-100)
        variable: Variable with uncertainty_handling config

    Returns:
        (meets_threshold, action) where action is 'flag', 'skip', or 'accept'
    """
    uncertainty = variable.uncertainty_handling or {}
    threshold = uncertainty.get("confidence_threshold")

    if threshold is None:
        return True, "accept"

    if confidence >= threshold:
        return True, "accept"

    action = uncertainty.get("if_uncertain_action", "flag")
    return False, action


def handle_multiple_values(
    values: List[Any],
    variable: Variable,
) -> Any:
    """
    Apply multi-value strategy based on variable config.

    Args:
        values: List of extracted values
        variable: Variable with uncertainty_handling config

    Returns:
        Processed value(s) according to strategy
    """
    if not values:
        return None

    uncertainty = variable.uncertainty_handling or {}
    strategy = uncertainty.get("multiple_values_action", "return_first")

    max_values = variable.max_values or 1

    if strategy == "return_all":
        return values[:max_values]
    elif strategy == "return_first":
        return values[0]
    elif strategy == "concatenate":
        str_values = [str(v) for v in values[:max_values] if v is not None]
        return ", ".join(str_values) if str_values else None
    else:
        return values[0]


def post_process_extraction(
    value: Any,
    confidence: int,
    variable: Variable,
) -> Dict[str, Any]:
    """
    Run the full post-processing pipeline on a single extraction.

    Args:
        value: Raw extracted value
        confidence: Confidence score (0-100)
        variable: Variable definition

    Returns:
        Dict with processed value, confidence, status flags
    """
    result = {
        "value": value,
        "confidence": confidence,
        "should_flag": False,
        "should_skip": False,
        "error_message": None,
    }

    # 1. Type coercion
    result["value"] = coerce_type(value, variable.type)

    # 2. Validation
    is_valid, error_msg = validate_value(result["value"], variable)
    if not is_valid:
        result["should_flag"] = True
        result["error_message"] = error_msg

    # 3. Apply default
    result["value"] = apply_default(result["value"], variable)

    # 4. Confidence check
    meets_threshold, action = check_confidence(confidence, variable)
    if not meets_threshold:
        if action == "flag":
            result["should_flag"] = True
            result["error_message"] = result["error_message"] or f"Confidence {confidence} below threshold"
        elif action == "skip":
            result["should_skip"] = True
            result["value"] = None

    return result
