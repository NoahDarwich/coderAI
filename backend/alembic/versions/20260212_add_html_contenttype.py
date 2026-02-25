"""Add HTML to ContentType enum.

Revision ID: 20260212_html
Revises: 20260211_spec
Create Date: 2026-02-12
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '20260212_html'
down_revision = '20260211_spec'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE contenttype ADD VALUE IF NOT EXISTS 'HTML'")


def downgrade() -> None:
    # PostgreSQL does not support removing values from enums.
    # To downgrade, the enum would need to be recreated without HTML.
    pass
