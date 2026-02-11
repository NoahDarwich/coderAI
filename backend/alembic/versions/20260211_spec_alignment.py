"""Align models with CODERAI_REFERENCE spec.

- Document: add status, word_count, error_message
- Variable: add display_name, max_values, default_value, depends_on
- ProcessingJob: add PAUSED status, documents_processed, documents_failed, consecutive_failures
- Extraction: value Text->JSONB, add status enum, entity_index, entity_text, prompt_version, error_message; drop flagged, review_notes; add unique constraint
- Prompt: add is_active, response_schema
- ExtractionFeedback: is_correct->feedback_type enum, correct_value->corrected_value JSONB

Revision ID: 20260211_spec
Revises: 20251218181742
Create Date: 2026-02-11
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260211_spec'
down_revision = '20251218181742'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- New enum types ---
    document_status = postgresql.ENUM('UPLOADED', 'PARSED', 'READY', 'FAILED', name='documentstatus', create_type=False)
    document_status.create(op.get_bind(), checkfirst=True)

    extraction_status = postgresql.ENUM('EXTRACTED', 'VALIDATED', 'FLAGGED', 'FAILED', name='extractionstatus', create_type=False)
    extraction_status.create(op.get_bind(), checkfirst=True)

    feedback_type = postgresql.ENUM('CORRECT', 'INCORRECT', 'PARTIALLY_CORRECT', name='feedbacktype', create_type=False)
    feedback_type.create(op.get_bind(), checkfirst=True)

    # --- Document: add status, word_count, error_message ---
    op.add_column('documents', sa.Column('status', sa.Enum('UPLOADED', 'PARSED', 'READY', 'FAILED', name='documentstatus'), nullable=True))
    op.execute("UPDATE documents SET status = 'READY'")
    op.alter_column('documents', 'status', nullable=False)
    op.add_column('documents', sa.Column('word_count', sa.Integer(), nullable=True))
    op.add_column('documents', sa.Column('error_message', sa.Text(), nullable=True))

    # --- Variable: add display_name, max_values, default_value, depends_on ---
    op.add_column('variables', sa.Column('display_name', sa.String(255), nullable=True))
    op.add_column('variables', sa.Column('max_values', sa.Integer(), nullable=True))
    op.execute("UPDATE variables SET max_values = 1")
    op.alter_column('variables', 'max_values', nullable=False, server_default='1')
    op.add_column('variables', sa.Column('default_value', sa.Text(), nullable=True))
    op.add_column('variables', sa.Column('depends_on', postgresql.JSONB(), nullable=True))

    # --- ProcessingJob: add PAUSED to enum, add tracking fields ---
    # Add PAUSED to jobstatus enum
    op.execute("ALTER TYPE jobstatus ADD VALUE IF NOT EXISTS 'PAUSED' AFTER 'PROCESSING'")

    op.add_column('processing_jobs', sa.Column('documents_processed', sa.Integer(), nullable=True))
    op.execute("UPDATE processing_jobs SET documents_processed = 0")
    op.alter_column('processing_jobs', 'documents_processed', nullable=False, server_default='0')

    op.add_column('processing_jobs', sa.Column('documents_failed', sa.Integer(), nullable=True))
    op.execute("UPDATE processing_jobs SET documents_failed = 0")
    op.alter_column('processing_jobs', 'documents_failed', nullable=False, server_default='0')

    op.add_column('processing_jobs', sa.Column('consecutive_failures', sa.Integer(), nullable=True))
    op.execute("UPDATE processing_jobs SET consecutive_failures = 0")
    op.alter_column('processing_jobs', 'consecutive_failures', nullable=False, server_default='0')

    # --- Extraction: value Text->JSONB, add fields, drop flagged/review_notes ---
    # Data migration: wrap existing text values as JSON strings
    op.execute("""
        ALTER TABLE extractions
        ALTER COLUMN value TYPE jsonb
        USING CASE
            WHEN value IS NULL THEN NULL
            ELSE to_jsonb(value)
        END
    """)

    # Add new columns
    op.add_column('extractions', sa.Column('status', sa.Enum('EXTRACTED', 'VALIDATED', 'FLAGGED', 'FAILED', name='extractionstatus'), nullable=True))
    # Migrate flagged -> status
    op.execute("""
        UPDATE extractions SET status = CASE
            WHEN flagged = true THEN 'FLAGGED'
            ELSE 'EXTRACTED'
        END
    """)
    op.alter_column('extractions', 'status', nullable=False)

    op.add_column('extractions', sa.Column('error_message', sa.Text(), nullable=True))
    op.add_column('extractions', sa.Column('entity_index', sa.Integer(), nullable=True))
    op.add_column('extractions', sa.Column('entity_text', sa.Text(), nullable=True))
    op.add_column('extractions', sa.Column('prompt_version', sa.Integer(), nullable=True))

    # Drop old columns
    op.drop_column('extractions', 'flagged')
    op.drop_column('extractions', 'review_notes')

    # Add unique constraint for idempotent reprocessing
    op.create_unique_constraint(
        'uq_extraction_job_doc_var_entity',
        'extractions',
        ['job_id', 'document_id', 'variable_id', 'entity_index']
    )

    # --- Prompt: add is_active, response_schema ---
    op.add_column('prompts', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.execute("UPDATE prompts SET is_active = true")
    op.alter_column('prompts', 'is_active', nullable=False, server_default='true')
    op.add_column('prompts', sa.Column('response_schema', postgresql.JSONB(), nullable=True))

    # --- ExtractionFeedback: is_correct->feedback_type, correct_value->corrected_value JSONB ---
    op.add_column('extraction_feedback', sa.Column('feedback_type', sa.Enum('CORRECT', 'INCORRECT', 'PARTIALLY_CORRECT', name='feedbacktype'), nullable=True))
    # Migrate is_correct -> feedback_type
    op.execute("""
        UPDATE extraction_feedback SET feedback_type = CASE
            WHEN is_correct = true THEN 'CORRECT'
            ELSE 'INCORRECT'
        END
    """)
    op.alter_column('extraction_feedback', 'feedback_type', nullable=False)
    op.drop_column('extraction_feedback', 'is_correct')

    # Rename correct_value -> corrected_value and change to JSONB
    op.execute("""
        ALTER TABLE extraction_feedback
        ALTER COLUMN correct_value TYPE jsonb
        USING CASE
            WHEN correct_value IS NULL THEN NULL
            ELSE to_jsonb(correct_value)
        END
    """)
    op.alter_column('extraction_feedback', 'correct_value', new_column_name='corrected_value')

    # --- ProcessingLog: add event_type, metadata ---
    event_type_enum = postgresql.ENUM(
        'JOB_STARTED', 'DOC_STARTED', 'DOC_COMPLETED', 'DOC_FAILED',
        'JOB_COMPLETED', 'JOB_FAILED', 'JOB_PAUSED', 'JOB_RESUMED', 'JOB_CANCELLED',
        name='eventtype', create_type=False
    )
    event_type_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('processing_logs', sa.Column('event_type', sa.Enum(
        'JOB_STARTED', 'DOC_STARTED', 'DOC_COMPLETED', 'DOC_FAILED',
        'JOB_COMPLETED', 'JOB_FAILED', 'JOB_PAUSED', 'JOB_RESUMED', 'JOB_CANCELLED',
        name='eventtype'), nullable=True))
    op.add_column('processing_logs', sa.Column('metadata', postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    # --- ProcessingLog: revert ---
    op.drop_column('processing_logs', 'metadata')
    op.drop_column('processing_logs', 'event_type')

    # --- ExtractionFeedback: revert ---
    op.alter_column('extraction_feedback', 'corrected_value', new_column_name='correct_value')
    op.execute("ALTER TABLE extraction_feedback ALTER COLUMN correct_value TYPE text USING correct_value::text")
    op.add_column('extraction_feedback', sa.Column('is_correct', sa.Boolean(), nullable=True))
    op.execute("""
        UPDATE extraction_feedback SET is_correct = CASE
            WHEN feedback_type = 'CORRECT' THEN true
            ELSE false
        END
    """)
    op.alter_column('extraction_feedback', 'is_correct', nullable=False)
    op.drop_column('extraction_feedback', 'feedback_type')

    # --- Prompt: revert ---
    op.drop_column('prompts', 'response_schema')
    op.drop_column('prompts', 'is_active')

    # --- Extraction: revert ---
    op.drop_constraint('uq_extraction_job_doc_var_entity', 'extractions', type_='unique')
    op.drop_column('extractions', 'prompt_version')
    op.drop_column('extractions', 'entity_text')
    op.drop_column('extractions', 'entity_index')
    op.drop_column('extractions', 'error_message')
    op.add_column('extractions', sa.Column('review_notes', sa.Text(), nullable=True))
    op.add_column('extractions', sa.Column('flagged', sa.Boolean(), nullable=True, server_default='false'))
    op.execute("""
        UPDATE extractions SET flagged = CASE
            WHEN status = 'FLAGGED' THEN true
            ELSE false
        END
    """)
    op.alter_column('extractions', 'flagged', nullable=False)
    op.drop_column('extractions', 'status')
    op.execute("ALTER TABLE extractions ALTER COLUMN value TYPE text USING value::text")

    # --- ProcessingJob: revert ---
    op.drop_column('processing_jobs', 'consecutive_failures')
    op.drop_column('processing_jobs', 'documents_failed')
    op.drop_column('processing_jobs', 'documents_processed')

    # --- Variable: revert ---
    op.drop_column('variables', 'depends_on')
    op.drop_column('variables', 'default_value')
    op.drop_column('variables', 'max_values')
    op.drop_column('variables', 'display_name')

    # --- Document: revert ---
    op.drop_column('documents', 'error_message')
    op.drop_column('documents', 'word_count')
    op.drop_column('documents', 'status')

    # --- Drop enum types ---
    op.execute("DROP TYPE IF EXISTS eventtype")
    op.execute("DROP TYPE IF EXISTS feedbacktype")
    op.execute("DROP TYPE IF EXISTS extractionstatus")
    op.execute("DROP TYPE IF EXISTS documentstatus")
