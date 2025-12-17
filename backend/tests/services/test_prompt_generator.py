"""
Service tests for prompt generation.
"""
import pytest

from src.models.variable import VariableType
from src.services.prompt_generator import PromptGenerator


@pytest.mark.asyncio
async def test_generate_text_prompt(sample_project, sample_variables):
    """Test generating a prompt for TEXT variable."""
    text_variable = next(v for v in sample_variables if v.type == VariableType.TEXT)

    prompt_generator = PromptGenerator()
    prompt_data = prompt_generator.generate_prompt(
        variable=text_variable,
        project_context={
            "project_name": sample_project.name,
            "language": sample_project.language,
            "domain": sample_project.domain,
        },
    )

    assert "prompt_text" in prompt_data
    assert "model_config" in prompt_data

    # Check that prompt includes variable name and instructions
    prompt_text = prompt_data["prompt_text"]
    assert text_variable.name in prompt_text
    assert text_variable.instructions in prompt_text

    # Check model config
    model_config = prompt_data["model_config"]
    assert model_config["model"] == "gpt-4"
    assert model_config["temperature"] <= 0.3  # Should be low for precision


@pytest.mark.asyncio
async def test_generate_category_prompt(sample_project, sample_variables):
    """Test generating a prompt for CATEGORY variable."""
    category_variable = next(
        v for v in sample_variables if v.type == VariableType.CATEGORY
    )

    prompt_generator = PromptGenerator()
    prompt_data = prompt_generator.generate_prompt(
        variable=category_variable,
        project_context={
            "project_name": sample_project.name,
            "language": sample_project.language,
            "domain": sample_project.domain,
        },
    )

    prompt_text = prompt_data["prompt_text"]

    # Check that prompt includes categories
    for category in category_variable.classification_rules["categories"]:
        assert category in prompt_text.lower()


@pytest.mark.asyncio
async def test_generate_number_prompt(sample_project, sample_variables):
    """Test generating a prompt for NUMBER variable."""
    number_variable = next(
        v for v in sample_variables if v.type == VariableType.NUMBER
    )

    prompt_generator = PromptGenerator()
    prompt_data = prompt_generator.generate_prompt(
        variable=number_variable,
        project_context={
            "project_name": sample_project.name,
            "language": sample_project.language,
            "domain": sample_project.domain,
        },
    )

    prompt_text = prompt_data["prompt_text"]

    # Check that prompt mentions numeric extraction
    assert "number" in prompt_text.lower() or "numeric" in prompt_text.lower()


@pytest.mark.asyncio
async def test_generate_date_prompt(sample_project, sample_variables):
    """Test generating a prompt for DATE variable."""
    date_variable = next(v for v in sample_variables if v.type == VariableType.DATE)

    prompt_generator = PromptGenerator()
    prompt_data = prompt_generator.generate_prompt(
        variable=date_variable,
        project_context={
            "project_name": sample_project.name,
            "language": sample_project.language,
            "domain": sample_project.domain,
        },
    )

    prompt_text = prompt_data["prompt_text"]

    # Check that prompt mentions date format
    assert "date" in prompt_text.lower()


@pytest.mark.asyncio
async def test_generate_boolean_prompt(sample_project, sample_variables):
    """Test generating a prompt for BOOLEAN variable."""
    boolean_variable = next(
        v for v in sample_variables if v.type == VariableType.BOOLEAN
    )

    prompt_generator = PromptGenerator()
    prompt_data = prompt_generator.generate_prompt(
        variable=boolean_variable,
        project_context={
            "project_name": sample_project.name,
            "language": sample_project.language,
            "domain": sample_project.domain,
        },
    )

    prompt_text = prompt_data["prompt_text"]

    # Check that prompt mentions boolean/yes/no
    assert (
        "true" in prompt_text.lower()
        or "false" in prompt_text.lower()
        or "yes" in prompt_text.lower()
        or "no" in prompt_text.lower()
    )


@pytest.mark.asyncio
async def test_prompt_includes_project_context(sample_project, sample_variables):
    """Test that generated prompt includes project context."""
    variable = sample_variables[0]

    prompt_generator = PromptGenerator()
    prompt_data = prompt_generator.generate_prompt(
        variable=variable,
        project_context={
            "project_name": sample_project.name,
            "language": sample_project.language,
            "domain": sample_project.domain,
        },
    )

    prompt_text = prompt_data["prompt_text"]

    # Check that prompt includes domain context if provided
    if sample_project.domain:
        assert sample_project.domain in prompt_text


@pytest.mark.asyncio
async def test_low_temperature_for_precision():
    """Test that prompts use low temperature for deterministic extraction."""
    from src.models.variable import Variable

    test_variable = Variable(
        name="test_var",
        type=VariableType.TEXT,
        instructions="Extract test data",
        order=1,
    )

    prompt_generator = PromptGenerator()
    prompt_data = prompt_generator.generate_prompt(
        variable=test_variable,
        project_context={
            "project_name": "Test",
            "language": "en",
        },
    )

    # Temperature should be low for deterministic extraction
    assert prompt_data["model_config"]["temperature"] <= 0.3


@pytest.mark.asyncio
async def test_appropriate_max_tokens():
    """Test that max_tokens is appropriate for variable type."""
    from src.models.variable import Variable

    prompt_generator = PromptGenerator()

    # TEXT variables should have higher max_tokens
    text_variable = Variable(
        name="description",
        type=VariableType.TEXT,
        instructions="Extract description",
        order=1,
    )

    text_prompt = prompt_generator.generate_prompt(
        variable=text_variable,
        project_context={"project_name": "Test", "language": "en"},
    )

    # NUMBER variables should have lower max_tokens
    number_variable = Variable(
        name="count",
        type=VariableType.NUMBER,
        instructions="Extract count",
        order=1,
    )

    number_prompt = prompt_generator.generate_prompt(
        variable=number_variable,
        project_context={"project_name": "Test", "language": "en"},
    )

    # TEXT should have more tokens than NUMBER
    assert text_prompt["model_config"]["max_tokens"] > number_prompt["model_config"][
        "max_tokens"
    ]
