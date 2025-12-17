"""
Pydantic schemas for export functionality.
"""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    """Export format enumeration."""
    CSV_WIDE = "CSV_WIDE"
    CSV_LONG = "CSV_LONG"
    EXCEL = "EXCEL"
    JSON = "JSON"


class ExportConfig(BaseModel):
    """
    Configuration for export generation.
    """
    format: ExportFormat = Field(..., description="Export format (CSV_WIDE, CSV_LONG, EXCEL, JSON)")
    include_confidence: bool = Field(default=False, description="Include confidence scores in export")
    include_source_text: bool = Field(default=False, description="Include source text excerpts in export")
    min_confidence: Optional[int] = Field(default=None, ge=0, le=100, description="Minimum confidence threshold (0-100)")


class ExportResponse(BaseModel):
    """
    Response for export generation.
    """
    download_url: str = Field(..., description="URL to download the export file")
    format: ExportFormat = Field(..., description="Export format")
    filename: str = Field(..., description="Generated filename")
    size_bytes: int = Field(..., description="File size in bytes")
