"""
Base SQLAlchemy model with common fields for all entities.

All database models should inherit from BaseModel to get standard fields.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID

from src.core.database import Base


class BaseModel(Base):
    """
    Abstract base model with common fields for all database entities.
    
    Attributes:
        id: Primary key (UUID)
        created_at: Timestamp when record was created (auto-set)
        updated_at: Timestamp when record was last updated (auto-updated)
    """
    
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    def __repr__(self) -> str:
        """String representation showing class name and ID."""
        return f"<{self.__class__.__name__}(id={self.id})>"
