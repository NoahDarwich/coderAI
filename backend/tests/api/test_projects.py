"""
API tests for project CRUD endpoints.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.models.project import Project, ProjectScale


@pytest.mark.asyncio
async def test_create_project(test_db, async_client):
    """Test creating a new project."""
    project_data = {
        "name": "New Project",
        "scale": "SMALL",
        "language": "en",
        "domain": "political science",
    }

    response = await async_client.post("/api/v1/projects", json=project_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == project_data["name"]
    assert data["scale"] == project_data["scale"]
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_list_projects(test_db, async_client, sample_project):
    """Test listing projects."""
    response = await async_client.get("/api/v1/projects")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == sample_project.name


@pytest.mark.asyncio
async def test_get_project(test_db, async_client, sample_project):
    """Test getting a single project."""
    response = await async_client.get(f"/api/v1/projects/{sample_project.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_project.id)
    assert data["name"] == sample_project.name


@pytest.mark.asyncio
async def test_get_project_not_found(test_db, async_client):
    """Test getting a non-existent project."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await async_client.get(f"/api/v1/projects/{fake_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_project(test_db, async_client, sample_project):
    """Test updating a project."""
    update_data = {
        "name": "Updated Project Name",
        "domain": "updated domain",
    }

    response = await async_client.put(
        f"/api/v1/projects/{sample_project.id}",
        json=update_data,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["domain"] == update_data["domain"]


@pytest.mark.asyncio
async def test_delete_project(test_db, async_client, sample_project):
    """Test deleting a project."""
    response = await async_client.delete(f"/api/v1/projects/{sample_project.id}")

    assert response.status_code == 204

    # Verify project is deleted
    result = await test_db.execute(
        select(Project).where(Project.id == sample_project.id)
    )
    project = result.scalar_one_or_none()
    assert project is None


@pytest.mark.asyncio
async def test_delete_project_not_found(test_db, async_client):
    """Test deleting a non-existent project."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await async_client.delete(f"/api/v1/projects/{fake_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_project_validation_error(test_db, async_client):
    """Test creating a project with invalid data."""
    project_data = {
        "name": "",  # Empty name should fail validation
        "scale": "SMALL",
    }

    response = await async_client.post("/api/v1/projects", json=project_data)

    assert response.status_code == 422
