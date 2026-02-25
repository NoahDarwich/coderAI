"""Add avg_seconds_per_doc to processing_jobs for ETA computation.

Revision ID: 20260225_eta_jobs
Revises: 20260225_golden_examples
Create Date: 2026-02-25
"""
import sqlalchemy as sa
from alembic import op

revision = '20260225_eta_jobs'
down_revision = '20260225_golden_examples'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'processing_jobs',
        sa.Column(
            'avg_seconds_per_doc',
            sa.Float(),
            nullable=True,
            comment='Rolling average seconds per document (used for ETA)',
        ),
    )


def downgrade() -> None:
    op.drop_column('processing_jobs', 'avg_seconds_per_doc')
