"""
Deterministic Layout Engine

Renders Block/Row/Column/Text primitives to positioned elements.
Implements auto-compression and auto-pagination.
"""
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from .primitives import Block, Row, Column, Text, BulletList
from .templates import TEMPLATES, ModernTechTemplate


@dataclass
class PositionedElement:
    """
    Element with exact position on page
    """
    text: str
    x: float  # inches from left
    y: float  # inches from top
    font_size: float
    is_bold: bool = False
    is_italic: bool = False
    width: float = 0.0  # calculated width
    height: float = 0.0  # calculated height


class LayoutEngine:
    """
    Deterministic layout engine with auto-compression and pagination
    """

    def __init__(self, template_name: str = "modern_tech", template_config: Dict[str, Any] = None):
        self.template_class = TEMPLATES.get(template_name, ModernTechTemplate)
        self.template_config = template_config or {}
        self.template = self.template_class(config=self.template_config)

        # Compression levels
        self.compression_level = 0
        self.max_compression = 5

        # Font metrics (approximate - deterministic)
        self.char_widths = {
            10.0: 0.06,  # 10pt font: ~0.06 inches per char
            11.0: 0.066,
            12.0: 0.072,
            9.0: 0.054
        }

    def layout_resume(self, canonical: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point: convert canonical JSON to positioned elements
        Returns layout with compression level and pagination info
        """
        # Try progressive compression until it fits
        for compression in range(self.max_compression + 1):
            self.compression_level = compression
            self._apply_compression()

            # Recreate template with updated config for each compression attempt
            self.template = self.template_class(config=self.template_config)

            # Render template to primitives
            root_block = self.template.render(canonical)

            # Convert primitives to positioned elements
            elements, total_height = self._render_block(
                root_block,
                x=self.template.margin_left,
                y=self.template.margin_top,
                max_width=self.template.page_width - self.template.margin_left - self.template.margin_right
            )

            # Check if fits on one page
            content_height = total_height + self.template.margin_bottom
            if content_height <= self.template.page_height:
                return {
                    "elements": [self._elem_to_dict(e) for e in elements],
                    "total_height": total_height,
                    "fits_on_page": True,
                    "compression_level": compression,
                    "page_count": 1
                }

        # Still doesn't fit - paginate
        return self._paginate(elements, total_height)

    def _apply_compression(self):
        """
        Apply compression to template settings
        Progressive compression levels:
        0: No compression
        1: Reduce section spacing
        2: Reduce entry spacing
        3: Reduce bullet spacing + line height
        4: Reduce font size
        5: Aggressive compression
        """
        if self.compression_level == 0:
            return

        if self.compression_level >= 1:
            self.template.section_spacing *= 0.85

        if self.compression_level >= 2:
            self.template.entry_spacing *= 0.80

        if self.compression_level >= 3:
            if hasattr(self.template, 'bullet_spacing'):
                self.template.bullet_spacing *= 0.75

        if self.compression_level >= 4:
            # Reduce font sizes across the board
            pass  # Applied during rendering

        if self.compression_level >= 5:
            # Aggressive: tighten everything
            self.template.section_spacing *= 0.70
            self.template.entry_spacing *= 0.70

    def _render_block(self, block: Block, x: float, y: float, max_width: float) -> Tuple[List[PositionedElement], float]:
        """
        Render a Block to positioned elements
        Returns (elements, final_y)
        """
        elements = []
        current_y = y + block.margin_top
        current_x = x + block.indent

        for child in block.children:
            if isinstance(child, Text):
                elem, height = self._render_text(child, current_x, current_y, max_width)
                elements.append(elem)
                current_y += height

            elif isinstance(child, Row):
                row_elements, height = self._render_row(child, current_x, current_y, max_width)
                elements.extend(row_elements)
                current_y += height + child.margin_bottom

            elif isinstance(child, Block):
                nested_elements, final_y = self._render_block(child, current_x, current_y, max_width)
                elements.extend(nested_elements)
                current_y = final_y

            elif isinstance(child, BulletList):
                bullet_elements, height = self._render_bullets(child, current_x, current_y, max_width)
                elements.extend(bullet_elements)
                current_y += height

        current_y += block.margin_bottom
        return elements, current_y

    def _render_text(self, text: Text, x: float, y: float, max_width: float) -> Tuple[PositionedElement, float]:
        """
        Render a Text element
        Returns (element, height)
        """
        font_size = text.font_size
        if self.compression_level >= 4:
            font_size *= 0.95  # Reduce font size

        # Calculate width
        char_width = self.char_widths.get(font_size, 0.06)
        estimated_width = len(text.content) * char_width

        # Line height
        line_height = font_size / 72.0 * 1.2  # Convert pt to inches

        elem = PositionedElement(
            text=text.content,
            x=x,
            y=y,
            font_size=font_size,
            is_bold=text.is_bold,
            is_italic=text.is_italic,
            width=estimated_width,
            height=line_height
        )

        return elem, line_height

    def _render_row(self, row: Row, x: float, y: float, max_width: float) -> Tuple[List[PositionedElement], float]:
        """
        Render a Row (two-column layout)
        Returns (elements, max_height)
        """
        elements = []
        current_x = x
        max_height = 0.0

        for col in row.columns:
            # Calculate column width
            if col.width.endswith("%"):
                percent = float(col.width.rstrip("%")) / 100.0
                col_width = max_width * percent
            else:
                col_width = float(col.width.rstrip("px")) / 72.0  # px to inches

            # Render column contents
            col_x = current_x
            if col.align == "right":
                # Right-align: calculate content width and offset
                col_x = current_x + col_width - 2.0  # Approximate

            col_elements = []
            col_y = y
            for child in col.children:
                if isinstance(child, Text):
                    elem, height = self._render_text(child, col_x, col_y, col_width)
                    col_elements.append(elem)
                    col_y += height
                elif isinstance(child, Block):
                    nested, final_y = self._render_block(child, col_x, col_y, col_width)
                    col_elements.extend(nested)
                    col_y = final_y

            elements.extend(col_elements)
            max_height = max(max_height, col_y - y)
            current_x += col_width + row.spacing

        return elements, max_height

    def _render_bullets(self, bullet_list: BulletList, x: float, y: float, max_width: float) -> Tuple[List[PositionedElement], float]:
        """
        Render bullet list
        Returns (elements, total_height)
        """
        elements = []
        current_y = y
        bullet_x = x + bullet_list.indent

        for bullet in bullet_list.bullets:
            # Render bullet character
            bullet_text = f"{bullet_list.bullet_char} {bullet}"
            elem, height = self._render_text(
                Text(content=bullet_text, font_size=bullet_list.font_size),
                bullet_x,
                current_y,
                max_width - bullet_list.indent
            )
            elements.append(elem)
            current_y += height + bullet_list.spacing

        return elements, current_y - y

    def _paginate(self, elements: List[PositionedElement], total_height: float) -> Dict[str, Any]:
        """
        Split content across multiple pages
        """
        # Simple pagination: split at page boundary
        page_height = self.template.page_height - self.template.margin_top - self.template.margin_bottom
        page_count = int(total_height / page_height) + 1

        return {
            "elements": [self._elem_to_dict(e) for e in elements],
            "total_height": total_height,
            "fits_on_page": False,
            "compression_level": self.compression_level,
            "page_count": page_count
        }

    def _elem_to_dict(self, elem: PositionedElement) -> Dict[str, Any]:
        """Convert PositionedElement to dict"""
        return {
            "text": elem.text,
            "x": elem.x,
            "y": elem.y,
            "font_size": elem.font_size,
            "is_bold": elem.is_bold,
            "is_italic": elem.is_italic,
            "width": elem.width,
            "height": elem.height
        }
