"""
ARQ worker for async export job processing.
"""
import logging
import os
import tempfile
from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from src.models.project import Project
from src.services.export_service import ExportService

logger = logging.getLogger(__name__)


async def process_export_job(
    ctx: dict,
    project_id: str,
    format: str,
    include_confidence: bool = False,
    include_source_text: bool = False,
    min_confidence: float | None = None,
) -> dict:
    """
    ARQ task: generate an export file asynchronously.

    Returns dict with filename and path for download.
    """
    session_factory = ctx["session_factory"]

    async with session_factory() as db:
        try:
            result = await db.execute(
                select(Project).where(Project.id == UUID(project_id))
            )
            project = result.scalar_one_or_none()
            if not project:
                return {"status": "error", "message": "Project not found"}

            export_service = ExportService(db)
            pid = UUID(project_id)

            if format == "CSV_WIDE":
                content = await export_service.generate_csv_wide(
                    pid, include_confidence, include_source_text, min_confidence
                )
                ext = "csv"
            elif format == "CSV_LONG":
                content = await export_service.generate_csv_long(
                    pid, include_confidence, include_source_text, min_confidence
                )
                ext = "csv"
            elif format == "EXCEL":
                content = await export_service.generate_excel(
                    pid, include_confidence, include_source_text, min_confidence
                )
                ext = "xlsx"
            elif format == "JSON":
                content = await export_service.generate_json(
                    pid, include_confidence, include_source_text, min_confidence
                )
                ext = "json"
            else:
                return {"status": "error", "message": f"Unsupported format: {format}"}

            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{project.name.replace(' ', '_')}_{timestamp}.{ext}"

            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, filename)

            with open(file_path, "wb") as f:
                f.write(content)

            logger.info(f"Export completed: {filename} ({len(content)} bytes)")
            return {
                "status": "completed",
                "filename": filename,
                "download_url": f"/api/v1/exports/download/{filename}",
                "size_bytes": len(content),
            }

        except Exception as e:
            logger.exception(f"Export job failed: {e}")
            return {"status": "error", "message": str(e)}
