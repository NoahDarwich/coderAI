"""
Cross-database type compatibility.

Uses PostgreSQL-native types when connected to PostgreSQL, and falls back
to standard SQLAlchemy types for SQLite (local development).
"""
from sqlalchemy import JSON, String
from sqlalchemy.types import TypeDecorator
import uuid as _uuid


class JSONB(JSON):
    """JSONB on PostgreSQL, JSON (stored as TEXT) on SQLite."""
    pass


class UUID(TypeDecorator):
    """UUID stored as native UUID on PostgreSQL, CHAR(36) on SQLite."""
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return _uuid.UUID(str(value))

    def copy(self, **kw):
        return UUID()

    @property
    def python_type(self):
        return _uuid.UUID
