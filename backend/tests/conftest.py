"""
Pytest configuration and fixtures for backend tests.

Uses in-memory SQLite for fast, isolated tests. The production database module
is NOT imported — we create a dedicated test engine and Base here.
"""
import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import Base directly (this triggers the production engine, but only once)
from src.core.database import Base
from src.models.project import Project, ProjectScale
from src.models.variable import Variable, VariableType

# Database URL for testing (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session with in-memory SQLite.

    Creates all tables, yields a session, then tears down.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def sample_project(test_db: AsyncSession) -> Project:
    """Create a sample project for testing."""
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
    """Create sample variables for testing."""
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
            order=2,
        ),
        Variable(
            id=uuid4(),
            project_id=sample_project.id,
            name="participant_count",
            type=VariableType.NUMBER,
            instructions="Extract the estimated number of participants",
            order=3,
        ),
        Variable(
            id=uuid4(),
            project_id=sample_project.id,
            name="violence_reported",
            type=VariableType.BOOLEAN,
            instructions="Determine if violence was reported",
            order=4,
        ),
        Variable(
            id=uuid4(),
            project_id=sample_project.id,
            name="description",
            type=VariableType.TEXT,
            instructions="Extract a brief description of the event",
            order=5,
        ),
    ]

    for variable in variables:
        test_db.add(variable)

    await test_db.commit()

    for variable in variables:
        await test_db.refresh(variable)

    return variables
