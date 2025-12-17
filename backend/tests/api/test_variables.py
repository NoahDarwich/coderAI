"""
API tests for variable CRUD endpoints.
"""
import pytest
from sqlalchemy import select

from src.models.variable import Variable, VariableType


@pytest.mark.asyncio
async def test_create_variable(test_db, async_client, sample_project):
    """Test creating a new variable."""
    variable_data = {
        "name": "test_variable",
        "type": "TEXT",
        "instructions": "Extract test information from the document",
        "order": 1,
    }

    response = await async_client.post(
        f"/api/v1/projects/{sample_project.id}/variables",
        json=variable_data,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == variable_data["name"]
    assert data["type"] == variable_data["type"]
    assert "id" in data
    assert "current_prompt" in data  # Should include generated prompt


@pytest.mark.asyncio
async def test_list_variables(test_db, async_client, sample_project, sample_variables):
    """Test listing variables for a project."""
    response = await async_client.get(
        f"/api/v1/projects/{sample_project.id}/variables"
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(sample_variables)


@pytest.mark.asyncio
async def test_get_variable(test_db, async_client, sample_variables):
    """Test getting a single variable."""
    variable = sample_variables[0]
    response = await async_client.get(f"/api/v1/variables/{variable.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(variable.id)
    assert data["name"] == variable.name


@pytest.mark.asyncio
async def test_update_variable(test_db, async_client, sample_variables):
    """Test updating a variable."""
    variable = sample_variables[0]
    update_data = {
        "instructions": "Updated instructions for extraction",
    }

    response = await async_client.put(
        f"/api/v1/variables/{variable.id}",
        json=update_data,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["instructions"] == update_data["instructions"]
    # Should have generated a new prompt version
    assert "current_prompt" in data


@pytest.mark.asyncio
async def test_delete_variable(test_db, async_client, sample_variables):
    """Test deleting a variable."""
    variable = sample_variables[0]
    response = await async_client.delete(f"/api/v1/variables/{variable.id}")

    assert response.status_code == 204

    # Verify variable is deleted
    result = await test_db.execute(
        select(Variable).where(Variable.id == variable.id)
    )
    deleted_variable = result.scalar_one_or_none()
    assert deleted_variable is None


@pytest.mark.asyncio
async def test_create_category_variable_with_rules(
    test_db, async_client, sample_project
):
    """Test creating a category variable with classification rules."""
    variable_data = {
        "name": "event_category",
        "type": "CATEGORY",
        "instructions": "Classify the event type",
        "classification_rules": {
            "categories": ["protest", "riot", "demonstration"],
            "allow_multiple": False,
            "allow_other": True,
        },
        "order": 1,
    }

    response = await async_client.post(
        f"/api/v1/projects/{sample_project.id}/variables",
        json=variable_data,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "CATEGORY"
    assert data["classification_rules"] == variable_data["classification_rules"]


@pytest.mark.asyncio
async def test_create_variable_validation_error(test_db, async_client, sample_project):
    """Test creating a variable with invalid data."""
    variable_data = {
        "name": "",  # Empty name should fail validation
        "type": "TEXT",
        "instructions": "Test",
        "order": 1,
    }

    response = await async_client.post(
        f"/api/v1/projects/{sample_project.id}/variables",
        json=variable_data,
    )

    assert response.status_code == 422
