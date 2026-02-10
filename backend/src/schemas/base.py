"""
Base Pydantic schemas with common configuration.

All API schemas should inherit from these base classes for consistent
serialization behavior, especially camelCase conversion for frontend.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel as PydanticBaseModel, ConfigDict


class BaseSchema(PydanticBaseModel):
    """
    Base schema with common Pydantic configuration.
    
    Features:
    - Converts snake_case field names to camelCase in JSON output
    - Enables ORM mode for SQLAlchemy model compatibility
    - Validates default values during schema definition
    """
    
    model_config = ConfigDict(
        # Convert snake_case to camelCase for JSON serialization
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split('_'))
        ),
        populate_by_name=True,  # Allow both snake_case and camelCase inputs
        from_attributes=True,  # Enable ORM mode for SQLAlchemy models
        validate_default=True,  # Validate default values
        use_enum_values=False,  # Return enum objects, not values
    )


class TimestampSchema(BaseSchema):
    """
    Schema with common timestamp fields.
    
    Attributes:
        created_at: When the entity was created
        updated_at: When the entity was last updated
    """
    
    created_at: datetime
    updated_at: datetime


class EntitySchema(TimestampSchema):
    """
    Schema with ID and timestamp fields for entities.
    
    Attributes:
        id: Entity UUID primary key
        created_at: When the entity was created
        updated_at: When the entity was last updated
    """
    
    id: UUID


class PaginationParams(BaseSchema):
    """
    Schema for pagination query parameters.
    
    Attributes:
        skip: Number of records to skip
        limit: Maximum number of records to return
    """
    
    skip: int = 0
    limit: int = 100


class PaginatedResponse(BaseSchema):
    """
    Schema for paginated API responses.
    
    Attributes:
        total: Total number of records
        skip: Number of records skipped
        limit: Maximum records returned
        items: List of items (override with specific type in subclasses)
    """
    
    total: int
    skip: int
    limit: int
    items: list
