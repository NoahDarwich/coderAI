"""add_correct_value_to_extraction_feedback

Revision ID: c32a06030bf3
Revises: 002_add_workflow_fields
Create Date: 2025-12-18 18:35:07.277587

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c32a06030bf3'
down_revision: Union[str, None] = '002_add_workflow_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add correct_value column to extraction_feedback table
    op.add_column('extraction_feedback', sa.Column(
        'correct_value',
        sa.Text(),
        nullable=True,
        comment='User-provided correct value when extraction is marked incorrect'
    ))


def downgrade() -> None:
    # Remove correct_value column from extraction_feedback table
    op.drop_column('extraction_feedback', 'correct_value')
