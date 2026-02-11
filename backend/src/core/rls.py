"""
Row-Level Security (RLS) support for PostgreSQL multi-tenancy.

Provides:
1. SQL statements to enable RLS on tenant-scoped tables
2. Session event listener to set the current user context
3. Utility to generate Alembic migration operations
"""
import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Tables that should have RLS enabled
# Format: (table_name, user_id_path)
# user_id_path is the column path to the owning user:
#   - "user_id" for direct ownership
#   - "project_id->projects.user_id" for indirect via join
RLS_TABLES = [
    ("projects", "user_id"),
    ("documents", "project_id"),
    ("variables", "project_id"),
    ("prompts", "variable_id"),
    ("processing_jobs", "project_id"),
    ("extractions", "job_id"),
    ("extraction_feedback", "extraction_id"),
    ("processing_logs", "job_id"),
    ("document_chunks", "document_id"),
]


def generate_rls_sql() -> list[str]:
    """
    Generate SQL statements to enable RLS on all tenant-scoped tables.

    These should be run in an Alembic migration.
    Direct tables (with user_id column) get simple policies.
    Indirect tables get policies that join through parent tables.

    Returns:
        List of SQL statements
    """
    statements = []

    for table_name, fk_col in RLS_TABLES:
        # Enable RLS
        statements.append(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;")

        if table_name == "projects":
            # Direct: projects.user_id = current_setting
            statements.append(
                f"CREATE POLICY {table_name}_tenant_policy ON {table_name} "
                f"USING (user_id = current_setting('app.current_user_id')::uuid);"
            )
        elif table_name == "documents":
            statements.append(
                f"CREATE POLICY {table_name}_tenant_policy ON {table_name} "
                f"USING (project_id IN ("
                f"  SELECT id FROM projects WHERE user_id = current_setting('app.current_user_id')::uuid"
                f"));"
            )
        elif table_name == "variables":
            statements.append(
                f"CREATE POLICY {table_name}_tenant_policy ON {table_name} "
                f"USING (project_id IN ("
                f"  SELECT id FROM projects WHERE user_id = current_setting('app.current_user_id')::uuid"
                f"));"
            )
        elif table_name == "prompts":
            statements.append(
                f"CREATE POLICY {table_name}_tenant_policy ON {table_name} "
                f"USING (variable_id IN ("
                f"  SELECT v.id FROM variables v "
                f"  JOIN projects p ON v.project_id = p.id "
                f"  WHERE p.user_id = current_setting('app.current_user_id')::uuid"
                f"));"
            )
        elif table_name == "processing_jobs":
            statements.append(
                f"CREATE POLICY {table_name}_tenant_policy ON {table_name} "
                f"USING (project_id IN ("
                f"  SELECT id FROM projects WHERE user_id = current_setting('app.current_user_id')::uuid"
                f"));"
            )
        elif table_name == "extractions":
            statements.append(
                f"CREATE POLICY {table_name}_tenant_policy ON {table_name} "
                f"USING (job_id IN ("
                f"  SELECT j.id FROM processing_jobs j "
                f"  JOIN projects p ON j.project_id = p.id "
                f"  WHERE p.user_id = current_setting('app.current_user_id')::uuid"
                f"));"
            )
        elif table_name == "extraction_feedback":
            statements.append(
                f"CREATE POLICY {table_name}_tenant_policy ON {table_name} "
                f"USING (extraction_id IN ("
                f"  SELECT e.id FROM extractions e "
                f"  JOIN processing_jobs j ON e.job_id = j.id "
                f"  JOIN projects p ON j.project_id = p.id "
                f"  WHERE p.user_id = current_setting('app.current_user_id')::uuid"
                f"));"
            )
        elif table_name == "processing_logs":
            statements.append(
                f"CREATE POLICY {table_name}_tenant_policy ON {table_name} "
                f"USING (job_id IN ("
                f"  SELECT j.id FROM processing_jobs j "
                f"  JOIN projects p ON j.project_id = p.id "
                f"  WHERE p.user_id = current_setting('app.current_user_id')::uuid"
                f"));"
            )
        elif table_name == "document_chunks":
            statements.append(
                f"CREATE POLICY {table_name}_tenant_policy ON {table_name} "
                f"USING (document_id IN ("
                f"  SELECT d.id FROM documents d "
                f"  JOIN projects p ON d.project_id = p.id "
                f"  WHERE p.user_id = current_setting('app.current_user_id')::uuid"
                f"));"
            )

    # Force RLS for table owner too (important for superuser)
    for table_name, _ in RLS_TABLES:
        statements.append(
            f"ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;"
        )

    return statements


async def set_rls_context(session: AsyncSession, user_id: UUID) -> None:
    """
    Set the RLS context for a database session.

    Must be called at the beginning of each request with the authenticated user's ID.

    Args:
        session: Active database session
        user_id: Authenticated user's UUID
    """
    await session.execute(
        text("SET LOCAL app.current_user_id = :user_id"),
        {"user_id": str(user_id)},
    )


async def clear_rls_context(session: AsyncSession) -> None:
    """Clear the RLS context (for worker/superuser bypass)."""
    await session.execute(text("RESET app.current_user_id"))
