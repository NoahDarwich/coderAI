"""
Database connection and session management.
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

# Convert database URL to async version
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite uses aiosqlite driver
    DATABASE_URL = settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
elif settings.DATABASE_URL.startswith("postgresql"):
    # PostgreSQL uses asyncpg driver
    DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    DATABASE_URL = settings.DATABASE_URL

# Create async engine with appropriate settings
engine_kwargs = {
    "echo": settings.DEBUG,
    "future": True,
}

# Add connection pooling for PostgreSQL only (SQLite doesn't support it)
if not DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 10,
        "pool_pre_ping": True,
    })

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Alias for background tasks (used in job_manager.py)
async_session_maker = AsyncSessionLocal

# Base class for ORM models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency for getting database sessions.

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
