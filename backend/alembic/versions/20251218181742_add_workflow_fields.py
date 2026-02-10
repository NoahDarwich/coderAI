"""Add unit_of_observation, uncertainty_handling, and edge_cases fields

Revision ID: 002_add_workflow_fields
Revises: 15fcec0600fd
Create Date: 2025-12-18 18:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_add_workflow_fields'
down_revision: Union[str, None] = '15fcec0600fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add unit_of_observation to projects table
    op.add_column('projects', sa.Column(
        'unit_of_observation',
        postgresql.JSONB(astext_type=sa.Text()),
        nullable=True,
        comment='Unit of observation configuration: what_each_row_represents, rows_per_document, entity_identification_pattern'
    ))
    
    # Add uncertainty_handling to variables table
    op.add_column('variables', sa.Column(
        'uncertainty_handling',
        postgresql.JSONB(astext_type=sa.Text()),
        nullable=True,
        comment='Uncertainty handling config: confidence_threshold, if_uncertain_action, multiple_values_action'
    ))
    
    # Add edge_cases to variables table
    op.add_column('variables', sa.Column(
        'edge_cases',
        postgresql.JSONB(astext_type=sa.Text()),
        nullable=True,
        comment='Edge case handling: missing_field_action, validation_rules, specific_scenarios'
    ))


def downgrade() -> None:
    # Remove columns in reverse order
    op.drop_column('variables', 'edge_cases')
    op.drop_column('variables', 'uncertainty_handling')
    op.drop_column('projects', 'unit_of_observation')
