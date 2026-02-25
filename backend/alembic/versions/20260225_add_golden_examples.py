"""Add golden_examples JSONB column to variables table.

Revision ID: 20260225_golden_examples
Revises: 20260212_rls
Create Date: 2026-02-25
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260225_golden_examples'
down_revision = '20260212_rls'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'variables',
        sa.Column('golden_examples', postgresql.JSONB(), nullable=True,
                  comment='Few-shot examples: [{source_text, value, document_name, use_in_prompt}]'),
    )


def downgrade() -> None:
    op.drop_column('variables', 'golden_examples')
