"""
Pytest configuration and fixtures for backend tests.
"""
import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.database import Base
from src.main import app
from src.models.project import Project, ProjectScale
from src.models.variable import Variable, VariableType
from src.services.llm_client import LLMClient


# Database URL for testing (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create an event loop for the test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP client for testing API endpoints.

    Args:
        test_db: Test database session

    Yields:
        AsyncClient for making HTTP requests
    """
    # Override the get_db dependency to use test_db
    from src.api.dependencies import get_db

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.

    This fixture creates an in-memory SQLite database for testing,
    applies all migrations, and provides a session for tests.

    Yields:
        AsyncSession for database operations
    """
    # Create async engine with in-memory SQLite
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session

    # Teardown: drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def mock_llm():
    """
    Mock LLM client for testing without making real API calls.

    Returns:
        Mock LLMClient with predefined responses
    """
    class MockLLMClient(LLMClient):
        """Mock LLM client for testing."""

        def __init__(self):
            # Don't call super().__init__() to avoid requiring API keys
            pass

        async def extract_value(self, prompt: str, document_text: str):
            """
            Mock extraction that returns predefined values.

            Returns a mock response based on the prompt content.
            """
            # Simple mock logic based on keywords in prompt
            if "date" in prompt.lower():
                return {
                    "value": "2024-01-15",
                    "confidence": 0.95,
                    "source_text": "The event occurred on January 15, 2024.",
                }
            elif "category" in prompt.lower() or "type" in prompt.lower():
                return {
                    "value": "protest",
                    "confidence": 0.88,
                    "source_text": "The protest involved approximately 500 participants.",
                }
            elif "number" in prompt.lower():
                return {
                    "value": "500",
                    "confidence": 0.92,
                    "source_text": "approximately 500 participants",
                }
            elif "boolean" in prompt.lower():
                return {
                    "value": "true",
                    "confidence": 0.90,
                    "source_text": "Violence was reported at the scene.",
                }
            else:
                return {
                    "value": "Sample extracted text",
                    "confidence": 0.85,
                    "source_text": "This is a sample excerpt from the document.",
                }

    return MockLLMClient()


@pytest.fixture
async def sample_project(test_db: AsyncSession) -> Project:
    """
    Create a sample project for testing.

    Args:
        test_db: Test database session

    Returns:
        Created project
    """
    project = Project(
        id=uuid4(),
        name="Test Project",
        scale=ProjectScale.SMALL,
        language="en",
        domain="political science",
    )

    test_db.add(project)
    await test_db.commit()
    await test_db.refresh(project)

    return project


@pytest.fixture
async def sample_variables(
    test_db: AsyncSession, sample_project: Project
) -> list[Variable]:
    """
    Create sample variables for testing.

    Args:
        test_db: Test database session
        sample_project: Sample project

    Returns:
        List of created variables
    """
    variables = [
        Variable(
            id=uuid4(),
            project_id=sample_project.id,
            name="event_type",
            type=VariableType.CATEGORY,
            instructions="Extract the type of political event",
            classification_rules={
                "categories": ["protest", "riot", "demonstration"],
                "allow_multiple": False,
                "allow_other": True,
            },
            order=1,
        ),
        Variable(
            id=uuid4(),
            project_id=sample_project.id,
            name="event_date",
            type=VariableType.DATE,
            instructions="Extract the date when the event occurred",
            classification_rules=None,
            order=2,
        ),
        Variable(
            id=uuid4(),
            project_id=sample_project.id,
            name="participant_count",
            type=VariableType.NUMBER,
            instructions="Extract the estimated number of participants",
            classification_rules=None,
            order=3,
        ),
        Variable(
            id=uuid4(),
            project_id=sample_project.id,
            name="violence_reported",
            type=VariableType.BOOLEAN,
            instructions="Determine if violence was reported",
            classification_rules=None,
            order=4,
        ),
        Variable(
            id=uuid4(),
            project_id=sample_project.id,
            name="description",
            type=VariableType.TEXT,
            instructions="Extract a brief description of the event",
            classification_rules=None,
            order=5,
        ),
    ]

    for variable in variables:
        test_db.add(variable)

    await test_db.commit()

    for variable in variables:
        await test_db.refresh(variable)

    return variables
