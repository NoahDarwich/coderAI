"""
API routes for data export functionality.
"""
import os
import tempfile
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.models.project import Project
from src.schemas.export import ExportConfig, ExportFormat, ExportResponse
from src.services.export_service import ExportService

router = APIRouter(tags=["exports"])


@router.post(
    "/api/v1/projects/{project_id}/export",
    response_model=ExportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_export(
    project_id: UUID,
    export_config: ExportConfig,
    db: AsyncSession = Depends(get_db),
) -> ExportResponse:
    """
    Generate export file for project extractions.

    The export file is generated based on the specified format and configuration.
    The response includes a download URL that can be used to retrieve the file.

    Args:
        project_id: Project UUID
        export_config: Export configuration
        db: Database session

    Returns:
        Export response with download URL

    Raises:
        HTTPException: 404 if project not found
        HTTPException: 400 if no extractions found
    """
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Create export service
    export_service = ExportService(db)

    try:
        # Generate export based on format
        if export_config.format == ExportFormat.CSV_WIDE:
            file_content = await export_service.generate_csv_wide(
                project_id=project_id,
                include_confidence=export_config.include_confidence,
                include_source_text=export_config.include_source_text,
                min_confidence=export_config.min_confidence,
            )
            extension = "csv"

        elif export_config.format == ExportFormat.CSV_LONG:
            file_content = await export_service.generate_csv_long(
                project_id=project_id,
                include_confidence=export_config.include_confidence,
                include_source_text=export_config.include_source_text,
                min_confidence=export_config.min_confidence,
            )
            extension = "csv"

        elif export_config.format == ExportFormat.EXCEL:
            file_content = await export_service.generate_excel(
                project_id=project_id,
                include_confidence=export_config.include_confidence,
                include_source_text=export_config.include_source_text,
                min_confidence=export_config.min_confidence,
            )
            extension = "xlsx"

        elif export_config.format == ExportFormat.JSON:
            file_content = await export_service.generate_json(
                project_id=project_id,
                include_confidence=export_config.include_confidence,
                include_source_text=export_config.include_source_text,
                min_confidence=export_config.min_confidence,
            )
            extension = "json"

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported export format: {export_config.format}",
            )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Generate filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{project.name.replace(' ', '_')}_{timestamp}.{extension}"

    # Save file temporarily
    # In production, this should upload to S3 or similar storage
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)

    with open(file_path, "wb") as f:
        f.write(file_content)

    # Generate download URL
    # In production, this should be a signed URL to S3 or CDN
    download_url = f"/api/v1/exports/download/{filename}"

    return ExportResponse(
        download_url=download_url,
        format=export_config.format,
        filename=filename,
        size_bytes=len(file_content),
    )


@router.get("/api/v1/exports/download/{filename}")
async def download_export(filename: str) -> FileResponse:
    """
    Download an export file.

    Note: This is a simple implementation for MVP. In production, use signed URLs
    to S3 or CDN with expiration and access control.

    Args:
        filename: Export filename

    Returns:
        File response

    Raises:
        HTTPException: 404 if file not found
    """
    # Get file from temporary directory
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Export file {filename} not found",
        )

    # Determine media type based on extension
    if filename.endswith(".csv"):
        media_type = "text/csv"
    elif filename.endswith(".xlsx"):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif filename.endswith(".json"):
        media_type = "application/json"
    else:
        media_type = "application/octet-stream"

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type,
    )
