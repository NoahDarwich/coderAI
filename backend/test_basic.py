#!/usr/bin/env python3
"""
Basic Backend Test Script

This script performs basic sanity checks on the backend without requiring
a database or external services.

Usage:
    python test_basic.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all core modules can be imported."""
    print("Testing imports...")

    try:
        from src.models import project, variable, document, extraction
        print("  ✓ Models import successfully")
    except Exception as e:
        print(f"  ✗ Models import failed: {e}")
        return False

    try:
        from src.schemas import project, variable, document, processing, export
        print("  ✓ Schemas import successfully")
    except Exception as e:
        print(f"  ✗ Schemas import failed: {e}")
        return False

    try:
        from src.services import prompt_generator
        print("  ✓ Services import successfully")
    except Exception as e:
        print(f"  ✗ Services import failed: {e}")
        return False

    try:
        from src.api.routes import projects, variables, documents, processing, exports
        print("  ✓ API routes import successfully")
    except Exception as e:
        print(f"  ✗ API routes import failed: {e}")
        return False

    return True


def test_enums():
    """Test that all enums are defined correctly."""
    print("\nTesting enums...")

    try:
        from src.models.project import ProjectScale, ProjectStatus
        assert len(ProjectScale) == 2, "ProjectScale should have 2 values"
        assert len(ProjectStatus) >= 4, "ProjectStatus should have at least 4 values"
        print(f"  ✓ ProjectScale: {[e.value for e in ProjectScale]}")
        print(f"  ✓ ProjectStatus: {[e.value for e in ProjectStatus]}")
    except Exception as e:
        print(f"  ✗ Project enums failed: {e}")
        return False

    try:
        from src.models.variable import VariableType
        assert len(VariableType) == 6, "VariableType should have 6 values (including LOCATION)"
        print(f"  ✓ VariableType: {[e.value for e in VariableType]}")
        print(f"  ✓ LOCATION type added successfully!")
    except Exception as e:
        print(f"  ✗ Variable enums failed: {e}")
        return False

    try:
        from src.models.processing_job import JobType, JobStatus
        assert len(JobType) == 2, "JobType should have 2 values"
        assert len(JobStatus) >= 5, "JobStatus should have at least 5 values"
        print(f"  ✓ JobType: {[e.value for e in JobType]}")
        print(f"  ✓ JobStatus: {[e.value for e in JobStatus]}")
    except Exception as e:
        print(f"  ✗ Job enums failed: {e}")
        return False

    return True


def test_schemas():
    """Test that Pydantic schemas can be instantiated."""
    print("\nTesting schemas...")

    try:
        from src.schemas.project import ProjectCreate
        project = ProjectCreate(
            name="Test Project",
            scale="SMALL",
            language="en",
            domain="test"
        )
        print(f"  ✓ ProjectCreate schema works: {project.name}")
    except Exception as e:
        print(f"  ✗ ProjectCreate failed: {e}")
        return False

    try:
        from src.schemas.variable import VariableCreate
        variable = VariableCreate(
            name="test_var",
            type="TEXT",
            instructions="Test instructions for extraction",
            order=1
        )
        print(f"  ✓ VariableCreate schema works: {variable.name}")
    except Exception as e:
        print(f"  ✗ VariableCreate failed: {e}")
        return False

    try:
        from src.schemas.export import ExportFormat, ExportConfig
        config = ExportConfig(
            format=ExportFormat.CSV_WIDE,
            include_confidence=True,
            include_source_text=False
        )
        print(f"  ✓ ExportConfig schema works: {config.format}")
    except Exception as e:
        print(f"  ✗ ExportConfig failed: {e}")
        return False

    return True


def test_prompt_generator():
    """Test the prompt generator service."""
    print("\nTesting prompt generator...")

    try:
        from src.models.variable import Variable, VariableType
        from src.services.prompt_generator import generate_prompt

        # Test TEXT variable
        text_var = Variable(
            name="test_text",
            type=VariableType.TEXT,
            instructions="Extract test information",
            order=1
        )
        prompt_data = generate_prompt(text_var)
        assert "prompt_text" in prompt_data
        assert "model_config" in prompt_data
        print(f"  ✓ TEXT prompt generated ({len(prompt_data['prompt_text'])} chars)")

        # Test LOCATION variable (newly added)
        location_var = Variable(
            name="test_location",
            type=VariableType.LOCATION,
            instructions="Extract the location of the event",
            order=1
        )
        prompt_data = generate_prompt(location_var)
        assert "location" in prompt_data["prompt_text"].lower()
        print(f"  ✓ LOCATION prompt generated ({len(prompt_data['prompt_text'])} chars)")

        # Test CATEGORY variable
        category_var = Variable(
            name="test_category",
            type=VariableType.CATEGORY,
            instructions="Classify the event type",
            classification_rules={
                "categories": ["protest", "riot", "demonstration"],
                "allow_multiple": False
            },
            order=1
        )
        prompt_data = generate_prompt(category_var)
        assert "protest" in prompt_data["prompt_text"].lower()
        print(f"  ✓ CATEGORY prompt generated ({len(prompt_data['prompt_text'])} chars)")

    except Exception as e:
        print(f"  ✗ Prompt generator failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_fastapi_app():
    """Test that FastAPI app can be created."""
    print("\nTesting FastAPI app...")

    try:
        from src.main import app
        assert app is not None
        print(f"  ✓ FastAPI app created: {app.title}")

        # Check routes are registered
        routes = [route.path for route in app.routes]
        expected_routes = [
            "/api/v1/projects",
            "/api/v1/projects/{project_id}",
            "/api/v1/projects/{project_id}/variables",
            "/api/v1/projects/{project_id}/documents",
            "/api/v1/projects/{project_id}/jobs",
            "/api/v1/projects/{project_id}/export",
        ]

        for expected in expected_routes:
            if expected in routes:
                print(f"  ✓ Route registered: {expected}")
            else:
                print(f"  ✗ Route missing: {expected}")
                return False

    except Exception as e:
        print(f"  ✗ FastAPI app failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Data Extraction Backend - Basic Tests")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Enums", test_enums),
        ("Schemas", test_schemas),
        ("Prompt Generator", test_prompt_generator),
        ("FastAPI App", test_fastapi_app),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All basic tests passed!")
        print("\nNext steps:")
        print("  1. Set up PostgreSQL database")
        print("  2. Configure .env file")
        print("  3. Run: alembic upgrade head")
        print("  4. Run: uvicorn src.main:app --reload")
        print("  5. Open: http://localhost:8000/docs")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix errors before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
