"""
Stage 1: Raw Extraction
Extracts text with ALL formatting metadata preserved.
NO cleaning, NO merging, NO LLM.
"""
from pathlib import Path
from typing import List, Dict, Any
import fitz  # PyMuPDF
from dataclasses import dataclass


@dataclass
class TextBlock:
    """Represents a single block of text with position and formatting"""
    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    font_name: str = ""
    font_size: float = 0
    is_bold: bool = False
    is_italic: bool = False
    line_number: int = 0


@dataclass
class RawDocument:
    """Complete raw document with all metadata"""
    blocks: List[TextBlock]
    page_width: float
    page_height: float
    raw_text: str


class RawExtractor:
    """
    Stage 1: Extract raw text with position metadata
    Preserves:
    - Exact text
    - Line breaks
    - Spatial positioning (x, y coordinates)
    - Font information
    - Formatting (bold, italic)
    """

    def extract_from_pdf(self, file_path: Path) -> RawDocument:
        """
        Extract raw text blocks from PDF with position data
        """
        doc = fitz.open(file_path)
        all_blocks = []
        raw_text_parts = []

        # Process first page only (resume should be 1 page)
        page = doc[0]
        page_width = page.rect.width
        page_height = page.rect.height

        # Get text with detailed position information
        blocks = page.get_text("dict")["blocks"]

        line_num = 0
        for block in blocks:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                line_text = ""
                x0 = min(span["bbox"][0] for span in line["spans"]) if line["spans"] else 0
                y0 = min(span["bbox"][1] for span in line["spans"]) if line["spans"] else 0
                x1 = max(span["bbox"][2] for span in line["spans"]) if line["spans"] else 0
                y1 = max(span["bbox"][3] for span in line["spans"]) if line["spans"] else 0

                # Aggregate spans into line text
                for span in line["spans"]:
                    line_text += span["text"]

                if line_text.strip():
                    # Get font info from first span
                    font_info = line["spans"][0] if line["spans"] else {}
                    font_name = font_info.get("font", "")
                    font_size = font_info.get("size", 0)

                    # Detect bold/italic from font name
                    is_bold = "Bold" in font_name or "bold" in font_name
                    is_italic = "Italic" in font_name or "italic" in font_name

                    text_block = TextBlock(
                        text=line_text,
                        x0=x0,
                        y0=y0,
                        x1=x1,
                        y1=y1,
                        font_name=font_name,
                        font_size=font_size,
                        is_bold=is_bold,
                        is_italic=is_italic,
                        line_number=line_num
                    )
                    all_blocks.append(text_block)
                    raw_text_parts.append(line_text)
                    line_num += 1

        doc.close()

        return RawDocument(
            blocks=all_blocks,
            page_width=page_width,
            page_height=page_height,
            raw_text="\n".join(raw_text_parts)
        )

    def detect_two_column_layout(self, blocks: List[TextBlock], page_width: float) -> List[TextBlock]:
        """
        Detect if blocks are in two-column layout and merge them properly
        For resume headers with "COMPANY          Location" style
        """
        result = []
        i = 0

        while i < len(blocks):
            current = blocks[i]

            # Check if there's text on the right side of the same line
            if i + 1 < len(blocks):
                next_block = blocks[i + 1]

                # Same line if y coordinates overlap
                y_overlap = abs(current.y0 - next_block.y0) < 5

                # Check if there's significant horizontal gap (two-column indicator)
                horizontal_gap = next_block.x0 - current.x1
                is_two_column = horizontal_gap > 50  # More than 50 points apart

                if y_overlap and is_two_column:
                    # Merge with spacing preserved
                    spacing = " " * int(horizontal_gap / 5)  # Approximate spaces
                    merged_text = current.text + spacing + next_block.text

                    merged_block = TextBlock(
                        text=merged_text,
                        x0=current.x0,
                        y0=current.y0,
                        x1=next_block.x1,
                        y1=max(current.y1, next_block.y1),
                        font_name=current.font_name,
                        font_size=current.font_size,
                        is_bold=current.is_bold,
                        is_italic=current.is_italic,
                        line_number=current.line_number
                    )
                    result.append(merged_block)
                    i += 2  # Skip both blocks
                    continue

            result.append(current)
            i += 1

        return result
