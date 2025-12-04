from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class ExportFormat(str, Enum):
    """Supported export formats"""
    PDF = "pdf"
    DOCX = "docx"


class ExportOptions(BaseModel):
    """Customization options for export"""
    font_family: str = Field(default="Helvetica", description="Font family: Helvetica, Times, Courier")
    font_size: int = Field(default=10, ge=8, le=12, description="Base font size in points")
    theme: str = Field(default="professional", description="Color theme: professional, modern, minimal")
    page_margins: float = Field(default=0.5, ge=0.3, le=1.0, description="Margin size in inches")


class ExportRequest(BaseModel):
    """Request to export resume"""
    resume_id: str
    format: ExportFormat
    template: str = "modern"
    options: Optional[ExportOptions] = None


class TemplateInfo(BaseModel):
    """Information about a resume template"""
    id: str
    name: str
    description: str
    preview_url: Optional[str] = None
    supports_columns: bool = False
    available_fonts: List[str] = Field(default_factory=list)
    color_schemes: List[str] = Field(default_factory=list)


class TemplateListResponse(BaseModel):
    """List of available templates"""
    templates: List[TemplateInfo]
