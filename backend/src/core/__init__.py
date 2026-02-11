"""
Core module for configuration, database setup, and logging.

Note: database objects are imported lazily to avoid triggering engine creation
at import time (which fails when no async DB driver is available, e.g. in tests).
Import directly from src.core.database instead.
"""

from .config import settings
from .logging import setup_logging, get_logger


def __getattr__(name: str):
    """Lazy import for database objects to avoid import-time engine creation."""
    _db_exports = {"Base", "engine", "AsyncSessionLocal", "get_db", "init_db", "close_db"}
    if name in _db_exports:
        from . import database
        return getattr(database, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "settings",
    "Base",
    "engine",
    "AsyncSessionLocal",
    "get_db",
    "init_db",
    "close_db",
    "setup_logging",
    "get_logger",
]
