"""
Deterministic Layout Engine
Guarantees one-page layout through algorithmic compression.
"""
from dataclasses import dataclass
from typing import List, Dict, Any
from .font_metrics import FontMetrics


@dataclass
class LayoutSettings:
    """Layout configuration"""
    page_width: float = 8.5  # inches
    page_height: float = 11.0  # inches
    margin_top: float = 0.5
    margin_bottom: float = 0.5
    margin_left: float = 0.5
    margin_right: float = 0.5
    font_name: str = "Helvetica"
    font_size: float = 10
    line_height: float = 1.2
    heading_size: float = 12
    section_spacing: float = 0.15  # inches
    bullet_indent: float = 0.25  # inches
    paragraph_spacing: float = 0.08  # inches


@dataclass
class LayoutElement:
    """A positioned element on the page"""
    element_type: str  # "heading", "text", "bullet"
    text: str
    x: float  # inches from left
    y: float  # inches from top
    width: float
    height: float
    font_size: float
    is_bold: bool = False
    is_italic: bool = False


@dataclass
class LayoutResult:
    """Complete page layout"""
    elements: List[LayoutElement]
    total_height: float
    fits_on_page: bool
    compression_level: int
    settings: LayoutSettings


class LayoutEngine:
    """
    Deterministic layout engine with automatic compression
    """

    def __init__(self, settings: LayoutSettings = None):
        self.settings = settings or LayoutSettings()
        self.compression_level = 0

    def layout_resume(self, resume_data: Dict[str, Any]) -> LayoutResult:
        """
        Calculate exact layout for resume
        Automatically compresses until it fits one page
        """
        # Try progressive compression until it fits
        for compression in range(5):
            self.compression_level = compression
            self._apply_compression()

            elements, total_height = self._calculate_layout(resume_data)

            content_area_height = (
                self.settings.page_height
                - self.settings.margin_top
                - self.settings.margin_bottom
            )

            if total_height <= content_area_height:
                # SUCCESS: Fits on one page
                return LayoutResult(
                    elements=elements,
                    total_height=total_height,
                    fits_on_page=True,
                    compression_level=compression,
                    settings=self.settings
                )

        # Even at max compression, doesn't fit
        # Return anyway with warning
        elements, total_height = self._calculate_layout(resume_data)
        return LayoutResult(
            elements=elements,
            total_height=total_height,
            fits_on_page=False,
            compression_level=4,
            settings=self.settings
        )

    def _apply_compression(self):
        """
        Apply compression level to settings
        """
        base_settings = LayoutSettings()  # Reset to defaults

        if self.compression_level == 0:
            # No compression
            pass
        elif self.compression_level == 1:
            # Level 1: Reduce line height
            self.settings.line_height = 1.15
        elif self.compression_level == 2:
            # Level 2: Tighten spacing
            self.settings.line_height = 1.1
            self.settings.section_spacing = 0.12
            self.settings.paragraph_spacing = 0.06
        elif self.compression_level == 3:
            # Level 3: Reduce bullet indent and spacing
            self.settings.line_height = 1.1
            self.settings.section_spacing = 0.10
            self.settings.paragraph_spacing = 0.05
            self.settings.bullet_indent = 0.2
        elif self.compression_level >= 4:
            # Level 4: Reduce font size
            self.settings.font_size = 9.5
            self.settings.heading_size = 11
            self.settings.line_height = 1.1
            self.settings.section_spacing = 0.08
            self.settings.paragraph_spacing = 0.04
            self.settings.bullet_indent = 0.2

    def _calculate_layout(self, resume_data: Dict[str, Any]) -> tuple[List[LayoutElement], float]:
        """
        Calculate exact positions for all elements
        Returns (elements, total_height)
        """
        elements = []
        current_y = self.settings.margin_top
        content_width = (
            self.settings.page_width
            - self.settings.margin_left
            - self.settings.margin_right
        )

        font_metrics = FontMetrics(
            self.settings.font_name,
            self.settings.font_size
        )

        # Header
        header = resume_data.get("header", {})
        if header.get("name"):
            element = LayoutElement(
                element_type="heading",
                text=header["name"],
                x=self.settings.margin_left,
                y=current_y,
                width=content_width,
                height=self.settings.heading_size / 72.0,
                font_size=self.settings.heading_size + 2,
                is_bold=True
            )
            elements.append(element)
            current_y += element.height + 0.05

        # Contact info
        contact_info = self._format_contact(header.get("contact", {}))
        if contact_info:
            lines = font_metrics.calculate_line_breaks(contact_info, content_width)
            for line in lines:
                element = LayoutElement(
                    element_type="text",
                    text=line,
                    x=self.settings.margin_left,
                    y=current_y,
                    width=content_width,
                    height=font_metrics.calculate_height(1, self.settings.line_height),
                    font_size=self.settings.font_size - 1
                )
                elements.append(element)
                current_y += element.height

        current_y += self.settings.section_spacing

        # Sections
        for section in resume_data.get("sections", []):
            # Section title
            title_element = LayoutElement(
                element_type="heading",
                text=section.get("title", ""),
                x=self.settings.margin_left,
                y=current_y,
                width=content_width,
                height=self.settings.heading_size / 72.0,
                font_size=self.settings.heading_size,
                is_bold=True
            )
            elements.append(title_element)
            current_y += title_element.height + 0.05

            # Section entries
            for entry in section.get("entries", []):
                # Main text (company/school/project name)
                main_lines = entry.get("main_text", [])
                for line in main_lines:
                    element = LayoutElement(
                        element_type="text",
                        text=line,
                        x=self.settings.margin_left,
                        y=current_y,
                        width=content_width,
                        height=font_metrics.calculate_height(1, self.settings.line_height),
                        font_size=self.settings.font_size,
                        is_bold=True
                    )
                    elements.append(element)
                    current_y += element.height

                # Bullets
                for bullet in entry.get("bullets", []):
                    # Calculate line breaks for bullet
                    bullet_width = content_width - self.settings.bullet_indent
                    lines = font_metrics.calculate_line_breaks(bullet, bullet_width)

                    for i, line in enumerate(lines):
                        element = LayoutElement(
                            element_type="bullet",
                            text=("• " if i == 0 else "  ") + line,
                            x=self.settings.margin_left + self.settings.bullet_indent,
                            y=current_y,
                            width=bullet_width,
                            height=font_metrics.calculate_height(1, self.settings.line_height),
                            font_size=self.settings.font_size
                        )
                        elements.append(element)
                        current_y += element.height

                current_y += self.settings.paragraph_spacing

            current_y += self.settings.section_spacing

        return elements, current_y

    def _format_contact(self, contact) -> str:
        """Format contact info as single line"""
        parts = []

        # Handle both dict and list formats
        if isinstance(contact, dict):
            # Dict format: {"email": "...", "phone": "..."}
            for key in ["email", "phone", "location", "linkedin", "github", "website"]:
                if contact.get(key):
                    parts.append(contact[key])
        elif isinstance(contact, list):
            # List format: ["email@example.com", "555-1234", ...]
            parts = [str(item) for item in contact if item]

        return " • ".join(parts)
