"""
Database configuration and session management.

This module sets up SQLAlchemy async engine and provides session management
for database operations. Engine creation is deferred to avoid import-time
failures when the async driver is not available (e.g. in tests).
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base

from .config import settings

# Base class for SQLAlchemy models (safe to import at any time)
Base = declarative_base()

# Lazy engine and session factory — created on first access
_engine = None
_async_session_local = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,
        )
    return _engine


def _get_session_factory():
    global _async_session_local
    if _async_session_local is None:
        _async_session_local = async_sessionmaker(
            _get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _async_session_local


# Proxy classes for backwards-compatible access as module attributes
class _EngineProxy:
    """Proxy to allow `from src.core.database import engine`."""
    def __getattr__(self, name):
        return getattr(_get_engine(), name)


class _SessionProxy:
    """Proxy to allow `from src.core.database import AsyncSessionLocal`."""
    def __call__(self, *args, **kwargs):
        return _get_session_factory()(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(_get_session_factory(), name)


engine = _EngineProxy()
AsyncSessionLocal = _SessionProxy()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.

    Usage in FastAPI routes:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...

    Yields:
        AsyncSession: Database session
    """
    factory = _get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database (create tables).

    Note: In production, use Alembic migrations instead.
    This is only for testing/development.
    """
    real_engine = _get_engine()
    async with real_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.

    Call this on application shutdown.
    """
    global _engine, _async_session_local
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_local = None
