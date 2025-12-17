"""
Basic test script to verify frontend-backend alignment changes.

This script performs basic imports and validation checks to ensure
all alignment changes are syntactically correct and properly integrated.
"""

def test_imports():
    """Test that all modified modules can be imported."""
    print("Testing imports...")

    # Test model imports
    from src.models.extraction import Extraction
    from src.models.project import Project, ProjectStatus

    # Test schema imports
    from src.schemas.processing import (
        Extraction as ExtractionSchema,
        FlagUpdate,
        ExtractionDataPoint,
        DocumentResult,
        ProjectResults,
    )
    from src.schemas.export import ExportConfig

    # Test service imports
    from src.services.prompt_generator import generate_prompt

    print("✓ All imports successful")


def test_extraction_model():
    """Test Extraction model has new fields."""
    print("\nTesting Extraction model...")

    from src.models.extraction import Extraction

    # Check that model has new fields
    assert hasattr(Extraction, 'flagged'), "Extraction model missing 'flagged' field"
    assert hasattr(Extraction, 'review_notes'), "Extraction model missing 'review_notes' field"
    assert hasattr(Extraction, 'confidence'), "Extraction model missing 'confidence' field"

    print("✓ Extraction model has all required fields")


def test_project_status():
    """Test Project model has new status."""
    print("\nTesting Project status...")

    from src.models.project import ProjectStatus

    # Check that SCHEMA_APPROVED status exists
    assert hasattr(ProjectStatus, 'SCHEMA_APPROVED'), "ProjectStatus missing 'SCHEMA_APPROVED'"
    assert ProjectStatus.SCHEMA_APPROVED.value == "SCHEMA_APPROVED"

    print("✓ Project status has SCHEMA_APPROVED")


def test_pydantic_schemas():
    """Test Pydantic schemas are valid."""
    print("\nTesting Pydantic schemas...")

    from pydantic import ValidationError
    from src.schemas.processing import FlagUpdate, ExtractionDataPoint

    # Test FlagUpdate schema
    flag_data = FlagUpdate(flagged=True, review_notes="Test note")
    assert flag_data.flagged == True
    assert flag_data.review_notes == "Test note"

    # Test ExtractionDataPoint schema with 0-100 confidence
    data_point = ExtractionDataPoint(value="test", confidence=95)
    assert data_point.confidence == 95

    # Test confidence validation (should fail for > 100)
    try:
        invalid_data = ExtractionDataPoint(value="test", confidence=101)
        assert False, "Should have raised validation error for confidence > 100"
    except ValidationError:
        pass  # Expected

    print("✓ Pydantic schemas validate correctly")


def test_prompt_generator():
    """Test prompt generator has updated confidence scales."""
    print("\nTesting prompt generator...")

    from src.services.prompt_generator import _generate_text_prompt
    from src.models.variable import Variable, VariableType

    # Create a test variable
    class MockVariable:
        name = "test_var"
        type = VariableType.TEXT
        instructions = "Extract test data"

    prompt = _generate_text_prompt(MockVariable(), "Test Project")

    # Check that prompt uses 0-100 scale
    assert '0-100 scale' in prompt, "Prompt should use 0-100 confidence scale"
    assert '"confidence": 95' in prompt, "Prompt should use integer confidence (95, not 0.95)"
    assert '0.0-1.0' not in prompt, "Prompt should not use old 0-1 scale"

    print("✓ Prompt generator uses 0-100 confidence scale")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Frontend-Backend Alignment Tests")
    print("=" * 60)

    try:
        test_imports()
        test_extraction_model()
        test_project_status()
        test_pydantic_schemas()
        test_prompt_generator()

        print("\n" + "=" * 60)
        print("✓ All alignment tests passed!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
