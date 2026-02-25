"""
Prompt generation service for creating optimized LLM prompts from variable definitions.

This service transforms user's natural language extraction instructions into
structured, optimized prompts for different LLM models.
"""
import json
from typing import Any, Dict, List, Optional

from src.models.project import Project
from src.models.variable import Variable, VariableType


def generate_prompt(variable: Variable, project: Optional[Project] = None) -> Dict[str, Any]:
    """
    Generate an optimized LLM prompt from a variable definition.

    Args:
        variable: Variable model with extraction instructions
        project: Optional project model for additional context

    Returns:
        Dictionary with 'prompt_text' and 'model_config' keys
    """
    # Get project context and UoO framing
    project_context = _build_project_context(project) if project else ""
    uoo_framing, input_label = _build_uoo_framing(project)

    # Generate prompt based on variable type
    if variable.type == VariableType.TEXT:
        prompt_text = _generate_text_prompt(variable, project_context, uoo_framing, input_label)
    elif variable.type == VariableType.CATEGORY:
        prompt_text = _generate_category_prompt(variable, project_context, uoo_framing, input_label)
    elif variable.type == VariableType.NUMBER:
        prompt_text = _generate_number_prompt(variable, project_context, uoo_framing, input_label)
    elif variable.type == VariableType.DATE:
        prompt_text = _generate_date_prompt(variable, project_context, uoo_framing, input_label)
    elif variable.type == VariableType.BOOLEAN:
        prompt_text = _generate_boolean_prompt(variable, project_context, uoo_framing, input_label)
    elif variable.type == VariableType.LOCATION:
        prompt_text = _generate_location_prompt(variable, project_context, uoo_framing, input_label)
    else:
        raise ValueError(f"Unknown variable type: {variable.type}")

    # Generate model configuration
    model_config = _generate_model_config(variable)

    return {
        "prompt_text": prompt_text,
        "model_config": model_config,
    }


def _build_project_context(project: Project) -> str:
    """
    Build context string from project metadata.

    Args:
        project: Project model

    Returns:
        Context string describing the project
    """
    context_parts = [f"Project: {project.name}"]

    if project.domain:
        context_parts.append(f"Domain: {project.domain}")

    if project.language and project.language != "en":
        context_parts.append(f"Document Language: {project.language}")

    context_parts.append(f"Project Scale: {project.scale.value}")

    # Add unit of observation context for document-level extraction only.
    # Entity-level projects get a dedicated framing section from _build_uoo_framing
    # to avoid rendering the same information twice in the prompt.
    if project.unit_of_observation:
        uoo = project.unit_of_observation
        rows_per_doc = uoo.get("rows_per_document", "one")
        if rows_per_doc != "multiple":
            what_represents = uoo.get("what_each_row_represents", "document")
            context_parts.append(f"\n**Unit of Observation:**")
            context_parts.append(f"Each row in the output dataset represents: {what_represents}")
            context_parts.append(f"Extraction Mode: One row per document (document-level extraction)")

    return "\n".join(context_parts)


def _build_uoo_framing(project: Optional[Project]) -> tuple[str, str]:
    """
    Build extraction scope framing based on unit of observation mode.

    Returns:
        (framing_section, input_label) where framing_section is injected into
        the prompt body and input_label replaces "Document" at the bottom.
        For document-level extraction both are empty/default.
    """
    if not project or not project.unit_of_observation:
        return "", "Document"

    uoo = project.unit_of_observation
    if uoo.get("rows_per_document", "one") != "multiple":
        return "", "Document"

    what_represents = uoo.get("what_each_row_represents", "entity")
    entity_pattern = uoo.get("entity_identification_pattern", "")

    lines = [
        "\n**Extraction Scope — Entity-Level Mode:**",
        f"The text below is a passage representing a single {what_represents}.",
        "Extract values for this specific entity only.",
        "Do not aggregate or summarise across multiple entities in the same document.",
    ]
    if entity_pattern:
        lines.append(f"Entity identification pattern: {entity_pattern}")

    return "\n".join(lines), "Entity Passage"


def _build_uncertainty_handling(variable: Variable) -> str:
    """
    Build uncertainty handling instructions from variable config.

    Args:
        variable: Variable model

    Returns:
        Uncertainty handling instructions string
    """
    if not variable.uncertainty_handling:
        return ""

    uh = variable.uncertainty_handling
    confidence_threshold = uh.get("confidence_threshold", 70)
    if_uncertain = uh.get("if_uncertain_action", "return_best_guess")
    multiple_values = uh.get("multiple_values_action", "return_first")

    instructions = ["\n**Uncertainty Handling:**"]
    instructions.append(f"- Minimum confidence threshold: {confidence_threshold}%")

    if if_uncertain == "flag":
        instructions.append(f"- If confidence < {confidence_threshold}%: Set a flag in your response and return best guess")
    elif if_uncertain == "skip":
        instructions.append(f"- If confidence < {confidence_threshold}%: Set value to null and explain in source_text")
    else:  # return_best_guess
        instructions.append(f"- If confidence < {confidence_threshold}%: Return best guess with low confidence score")

    if multiple_values == "return_all":
        instructions.append("- If multiple values found: Return all values as a list")
    elif multiple_values == "concatenate":
        instructions.append("- If multiple values found: Concatenate with semicolon separator")
    else:  # return_first
        instructions.append("- If multiple values found: Return only the first/most relevant value")

    return "\n".join(instructions)


def _build_edge_case_handling(variable: Variable) -> str:
    """
    Build edge case handling instructions from variable config.

    Args:
        variable: Variable model

    Returns:
        Edge case handling instructions string
    """
    if not variable.edge_cases:
        return ""

    ec = variable.edge_cases
    missing_action = ec.get("missing_field_action", "return_null")
    validation_rules = ec.get("validation_rules", [])
    scenarios = ec.get("specific_scenarios", {})

    instructions = ["\n**Edge Case Handling:**"]

    if missing_action == "return_null":
        instructions.append("- If field missing from document: Return null with confidence 0")
    elif missing_action == "return_na":
        instructions.append("- If field missing from document: Return 'N/A' with confidence 0")
    else:  # flag
        instructions.append("- If field missing from document: Return null and note in source_text")

    if validation_rules:
        instructions.append("\n**Validation Rules:**")
        for rule in validation_rules:
            rule_type = rule.get("rule_type", "unknown")
            params = rule.get("parameters", {})
            instructions.append(f"- {rule_type}: {params}")

    if scenarios:
        instructions.append("\n**Specific Scenarios:**")
        for scenario, instruction in scenarios.items():
            instructions.append(f"- {scenario}: {instruction}")

    return "\n".join(instructions)


def _build_golden_examples(variable: Variable) -> str:
    """
    Build few-shot examples section from variable's pinned golden examples.

    Args:
        variable: Variable model with optional golden_examples list

    Returns:
        Few-shot examples instructions string, or empty string if none
    """
    if not variable.golden_examples:
        return ""

    # Only include examples marked for use in prompt
    examples: List[Dict[str, Any]] = [
        ex for ex in variable.golden_examples if ex.get("use_in_prompt", True)
    ]
    if not examples:
        return ""

    lines = [
        "\n**Few-Shot Examples:**",
        "Here are verified examples of correct extractions to guide you:",
    ]
    for i, ex in enumerate(examples[:5], 1):
        source = ex.get("source_text", "")[:300]
        value = ex.get("value")
        lines.append(f"\nExample {i}:")
        lines.append(f'  Source text: "{source}"')
        lines.append(f"  Expected output: {json.dumps(value)}")

    return "\n".join(lines)


def _build_common_sections(variable: Variable) -> tuple[str, str, str]:
    """Return (uncertainty_instructions, edge_case_instructions, golden_examples_section)."""
    return (
        _build_uncertainty_handling(variable),
        _build_edge_case_handling(variable),
        _build_golden_examples(variable),
    )


def _generate_text_prompt(variable: Variable, project_context: str, uoo_framing: str = "", input_label: str = "Document") -> str:
    """
    Generate prompt for TEXT variable type.

    TEXT variables extract free-form text passages (e.g., descriptions, quotes, summaries).
    """
    uncertainty_instructions, edge_case_instructions, golden_examples_section = _build_common_sections(variable)

    prompt = f"""You are a precise data extraction assistant. Extract the following information from the provided {input_label.lower()}.

{project_context}
{uoo_framing}

**Extraction Task:**
Variable Name: {variable.name}
Variable Type: Text (free-form text)

**Instructions:**
{variable.instructions}
{uncertainty_instructions}
{edge_case_instructions}
{golden_examples_section}

**Output Format:**
You must respond with a valid JSON object in this exact format:
{{
    "value": "extracted text here",
    "confidence": 95,
    "source_text": "relevant excerpt from document that supports this extraction"
}}

**Guidelines:**
1. Extract the exact text as it appears in the document (preserve formatting, spelling, punctuation)
2. If multiple instances exist, extract the most relevant or comprehensive one
3. If information is not found or unclear, set value to null
4. confidence: 0-100 scale (100 = certain, 50 = moderate, 0 = not found)
5. source_text: Include the surrounding context (max 200 characters)
6. Be precise and faithful to the source document

**{input_label}:**
{{document_text}}
"""
    return prompt.strip()


def _generate_category_prompt(variable: Variable, project_context: str, uoo_framing: str = "", input_label: str = "Document") -> str:
    """
    Generate prompt for CATEGORY variable type.

    CATEGORY variables classify text into predefined categories.
    """
    uncertainty_instructions, edge_case_instructions, golden_examples_section = _build_common_sections(variable)

    # Extract classification rules
    rules = variable.classification_rules or {}
    categories = rules.get("categories", [])
    allow_multiple = rules.get("allow_multiple", False)
    allow_other = rules.get("allow_other", True)

    # Format categories list
    categories_list = "\n".join([f"- {cat}" for cat in categories])

    # Build selection instructions
    selection_type = "one or more categories" if allow_multiple else "exactly one category"
    other_option = "\n- You may respond with a category not in the list if 'allow_other' is true and none fit well" if allow_other else ""

    prompt = f"""You are a precise classification assistant. Categorize the following information from the provided {input_label.lower()}.

{project_context}
{uoo_framing}

**Classification Task:**
Variable Name: {variable.name}
Variable Type: Category (classification)

**Instructions:**
{variable.instructions}
{uncertainty_instructions}
{edge_case_instructions}
{golden_examples_section}

**Available Categories:**
{categories_list}{other_option}

**Selection Rules:**
- Select {selection_type} from the list above
- Base your decision strictly on evidence in the document
- If no category fits and 'allow_other' is false, respond with null

**Output Format:**
You must respond with a valid JSON object in this exact format:
{{
    "value": {"[\"category1\", \"category2\"]" if allow_multiple else "\"category_name\""},
    "confidence": 95,
    "source_text": "relevant excerpt from document that supports this classification"
}}

**Guidelines:**
1. confidence: 0-100 scale (100 = clear match, 50 = ambiguous, 0 = not found)
2. source_text: Include the passage that supports your classification (max 200 characters)
3. Be conservative - only classify if you have clear evidence
4. For ambiguous cases, reduce confidence score rather than forcing a category

**{input_label}:**
{{document_text}}
"""
    return prompt.strip()


def _generate_number_prompt(variable: Variable, project_context: str, uoo_framing: str = "", input_label: str = "Document") -> str:
    """
    Generate prompt for NUMBER variable type.

    NUMBER variables extract numerical values (integers or floats).
    """
    uncertainty_instructions, edge_case_instructions, golden_examples_section = _build_common_sections(variable)

    prompt = f"""You are a precise numerical data extraction assistant. Extract the following numerical value from the provided {input_label.lower()}.

{project_context}
{uoo_framing}

**Extraction Task:**
Variable Name: {variable.name}
Variable Type: Number (integer or decimal)

**Instructions:**
{variable.instructions}
{uncertainty_instructions}
{edge_case_instructions}
{golden_examples_section}

**Output Format:**
You must respond with a valid JSON object in this exact format:
{{
    "value": 42.5,
    "confidence": 95,
    "source_text": "relevant excerpt from document containing this number"
}}

**Guidelines:**
1. Extract only the numerical value (no currency symbols, units, or formatting)
2. Use decimal notation (e.g., 1234.56, not "1,234.56")
3. If multiple numbers exist, extract the one most relevant to the instructions
4. If the value is not found or ambiguous, set value to null
5. confidence: 0-100 scale (100 = explicit number, 50 = calculated/inferred, 0 = not found)
6. source_text: Include the exact phrase containing the number (max 200 characters)
7. Be precise - do not estimate or calculate unless explicitly instructed

**{input_label}:**
{{document_text}}
"""
    return prompt.strip()


def _generate_date_prompt(variable: Variable, project_context: str, uoo_framing: str = "", input_label: str = "Document") -> str:
    """
    Generate prompt for DATE variable type.

    DATE variables extract dates in ISO 8601 format (YYYY-MM-DD).
    """
    uncertainty_instructions, edge_case_instructions, golden_examples_section = _build_common_sections(variable)

    prompt = f"""You are a precise date extraction assistant. Extract the following date from the provided {input_label.lower()}.

{project_context}
{uoo_framing}

**Extraction Task:**
Variable Name: {variable.name}
Variable Type: Date

**Instructions:**
{variable.instructions}
{uncertainty_instructions}
{edge_case_instructions}
{golden_examples_section}

**Output Format:**
You must respond with a valid JSON object in this exact format:
{{
    "value": "2024-03-15",
    "confidence": 95,
    "source_text": "relevant excerpt from document containing this date"
}}

**Guidelines:**
1. Always format dates as YYYY-MM-DD (ISO 8601 standard)
2. If only year is available, use YYYY-01-01
3. If only year and month are available, use YYYY-MM-01
4. Convert all date formats (e.g., "March 15, 2024", "15/03/2024", "Mar 15 2024") to YYYY-MM-DD
5. If multiple dates exist, extract the one most relevant to the instructions
6. If date is not found or ambiguous, set value to null
7. confidence: 0-100 scale (100 = explicit date, 50 = partial/inferred, 0 = not found)
8. source_text: Include the exact phrase containing the date (max 200 characters)
9. Be careful with ambiguous formats (e.g., "03/04/2024" could be Mar 4 or Apr 3)

**{input_label}:**
{{document_text}}
"""
    return prompt.strip()


def _generate_boolean_prompt(variable: Variable, project_context: str, uoo_framing: str = "", input_label: str = "Document") -> str:
    """
    Generate prompt for BOOLEAN variable type.

    BOOLEAN variables extract yes/no or true/false values.
    """
    uncertainty_instructions, edge_case_instructions, golden_examples_section = _build_common_sections(variable)

    prompt = f"""You are a precise boolean assessment assistant. Determine whether the following condition is true or false based on the provided {input_label.lower()}.

{project_context}
{uoo_framing}

**Assessment Task:**
Variable Name: {variable.name}
Variable Type: Boolean (true/false)

**Instructions:**
{variable.instructions}
{uncertainty_instructions}
{edge_case_instructions}
{golden_examples_section}

**Output Format:**
You must respond with a valid JSON object in this exact format:
{{
    "value": true,
    "confidence": 95,
    "source_text": "relevant excerpt from document that supports this assessment"
}}

**Guidelines:**
1. Respond with true or false (boolean, not string)
2. true = condition is explicitly or implicitly present/affirmed in document
3. false = condition is explicitly denied or absent from document
4. If evidence is insufficient or contradictory, set value to null
5. confidence: 0-100 scale (100 = explicit statement, 50 = inferred, 0 = unclear)
6. source_text: Include the passage that supports your assessment (max 200 characters)
7. Be conservative - only return true/false if you have clear evidence
8. Do not assume or infer beyond what the document explicitly states

**{input_label}:**
{{document_text}}
"""
    return prompt.strip()


def _generate_location_prompt(variable: Variable, project_context: str, uoo_framing: str = "", input_label: str = "Document") -> str:
    """
    Generate prompt for LOCATION variable type.

    LOCATION variables extract geographical locations, addresses, or place names.
    """
    uncertainty_instructions, edge_case_instructions, golden_examples_section = _build_common_sections(variable)

    prompt = f"""You are a precise data extraction assistant. Extract geographical location information from the provided {input_label.lower()}.

{project_context}
{uoo_framing}

**Extraction Task:**
Variable Name: {variable.name}
Variable Type: Location (geographical location, address, or place name)

**Instructions:**
{variable.instructions}
{uncertainty_instructions}
{edge_case_instructions}
{golden_examples_section}

**Output Format:**
You must respond with a valid JSON object in this exact format:
{{
    "value": "extracted location here",
    "confidence": 95,
    "source_text": "relevant excerpt from document mentioning this location"
}}

**Guidelines:**
1. Extract the location name exactly as it appears in the document (preserve spelling, capitalization)
2. Locations may be:
   - Countries (e.g., "United States", "Jordan")
   - Cities/towns (e.g., "Amman", "New York City")
   - Regions/provinces (e.g., "Balqa Governorate", "California")
   - Addresses (e.g., "123 King Abdullah St, Amman")
   - Landmarks/buildings (e.g., "Parliament Building", "Central Market")
   - Geographical features (e.g., "Jordan River", "Dead Sea")
3. If multiple locations are mentioned, extract the most relevant one based on the instructions
4. If no location is found, set value to null
5. confidence: 0-100 scale (100 = explicitly mentioned, 50 = inferred from context, 0 = not found)
6. source_text: Include the full sentence or phrase mentioning the location (max 200 characters)
7. Be precise - only extract locations, not general directional terms (e.g., "north", "south")
8. Preserve original language/script if the document uses non-Latin characters

**{input_label}:**
{{document_text}}
"""
    return prompt.strip()


def _generate_model_config(variable: Variable) -> Dict[str, Any]:
    """
    Generate optimal model configuration based on variable type.

    Args:
        variable: Variable model

    Returns:
        Dictionary with model configuration parameters
    """
    # Base configuration for all types
    config = {
        "model": "gpt-4",
        "top_p": 1.0,
    }

    # Type-specific configuration
    if variable.type == VariableType.TEXT:
        # Text extraction: moderate temperature, longer output
        config["temperature"] = 0.2
        config["max_tokens"] = 2000

    elif variable.type == VariableType.CATEGORY:
        # Classification: very low temperature for consistency
        config["temperature"] = 0.1
        config["max_tokens"] = 500

    elif variable.type == VariableType.NUMBER:
        # Numerical extraction: lowest temperature for precision
        config["temperature"] = 0.0
        config["max_tokens"] = 300

    elif variable.type == VariableType.DATE:
        # Date extraction: lowest temperature for precision
        config["temperature"] = 0.0
        config["max_tokens"] = 300

    elif variable.type == VariableType.BOOLEAN:
        # Boolean assessment: very low temperature
        config["temperature"] = 0.1
        config["max_tokens"] = 300

    elif variable.type == VariableType.LOCATION:
        # Location extraction: low temperature for precision
        config["temperature"] = 0.1
        config["max_tokens"] = 500

    return config
