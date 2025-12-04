"""
STAGE 1 — RAW EXTRACTION (CODE ONLY)

Extract from PDF:
- text blocks
- x/y coordinates
- font size
- bold/italic flags
- reading order
- keep line breaks
- keep spacing

DO NOT:
- merge lines
- clean text
- infer structure

Output: full raw_text + list of text_spans
"""
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
import fitz  # PyMuPDF


@dataclass
class TextSpan:
    """A single text span with position and formatting metadata"""
    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    font_name: str
    font_size: float
    is_bold: bool
    is_italic: bool
    page_number: int
    line_number: int


@dataclass
class RawDocument:
    """Raw extracted document with all metadata preserved"""
    raw_text: str  # Full text with line breaks preserved
    text_spans: List[TextSpan]  # All text spans with coordinates
    page_width: float
    page_height: float
    page_count: int


class RawExtractor:
    """
    Stage 1: Extract raw text and metadata from PDF
    NO interpretation, NO cleaning, NO merging
    """

    def extract_from_pdf(self, file_path: Path) -> RawDocument:
        """
        Extract raw text with full metadata from PDF
        """
        doc = fitz.open(file_path)

        if not doc or doc.page_count == 0:
            raise ValueError("Empty or invalid PDF")

        all_spans = []
        all_text_lines = []
        page_width = 0
        page_height = 0
        line_counter = 0

        for page_num, page in enumerate(doc):
            page_width = page.rect.width
            page_height = page.rect.height

            # Extract with dict mode to get position + font metadata
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if block.get("type") != 0:  # Skip non-text blocks
                    continue

                for line in block.get("lines", []):
                    line_text = ""

                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        if not text:
                            continue

                        # Detect bold/italic from font name
                        font_name = span.get("font", "")
                        is_bold = "bold" in font_name.lower()
                        is_italic = "italic" in font_name.lower() or "oblique" in font_name.lower()

                        # Create TextSpan with all metadata
                        text_span = TextSpan(
                            text=text,
                            x0=span.get("bbox", [0, 0, 0, 0])[0],
                            y0=span.get("bbox", [0, 0, 0, 0])[1],
                            x1=span.get("bbox", [0, 0, 0, 0])[2],
                            y1=span.get("bbox", [0, 0, 0, 0])[3],
                            font_name=font_name,
                            font_size=span.get("size", 10),
                            is_bold=is_bold,
                            is_italic=is_italic,
                            page_number=page_num,
                            line_number=line_counter
                        )
                        all_spans.append(text_span)
                        line_text += text

                    # Add line to full text (preserving line breaks)
                    if line_text.strip():
                        all_text_lines.append(line_text)
                        line_counter += 1

        # Build full raw text with line breaks preserved
        raw_text = "\n".join(all_text_lines)

        return RawDocument(
            raw_text=raw_text,
            text_spans=all_spans,
            page_width=page_width,
            page_height=page_height,
            page_count=doc.page_count
        )
