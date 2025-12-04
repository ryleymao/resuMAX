"""
Complete parsing pipeline orchestrator
Runs all 5 stages and returns canonical resume JSON + layout
"""
from pathlib import Path
from typing import Dict, Any, Optional
from .stage1_raw_extraction import RawExtractor
from .stage2_structural_segmentation import StructuralSegmenter
from .stage3_semantic_cleanup import SemanticCleaner
from ..layout_engine.engine import LayoutEngine, LayoutSettings


class ResumePipeline:
    """
    Complete pipeline: Raw → Structured → Cleaned → Layout
    """

    def __init__(self, llm_client=None):
        self.raw_extractor = RawExtractor()
        self.segmenter = StructuralSegmenter(llm_client)
        self.cleaner = SemanticCleaner()
        self.layout_engine = LayoutEngine()

    async def process_resume(self, file_path: Path) -> Dict[str, Any]:
        """
        Process resume through complete pipeline
        Returns: {
            "canonical": {...},  # Canonical resume JSON
            "layout": {...},     # Layout with positioned elements
            "metadata": {...}    # Processing metadata
        }
        """
        # Stage 1: Raw Extraction
        raw_doc = self.raw_extractor.extract_from_pdf(file_path)

        # Detect and merge two-column layouts
        merged_blocks = self.raw_extractor.detect_two_column_layout(
            raw_doc.blocks,
            raw_doc.page_width
        )

        # Update raw text from merged blocks
        raw_text = "\n".join(block.text for block in merged_blocks)

        # Stage 2: Structural Segmentation
        structured = await self.segmenter.segment(raw_text, merged_blocks)

        # Stage 3: Semantic Cleanup
        cleaned = self.cleaner.clean(structured)

        # Stage 4 & 5: Build canonical JSON and calculate layout
        canonical = self._build_canonical(cleaned)

        # Layout Engine: Calculate exact positions
        layout_result = self.layout_engine.layout_resume(canonical)

        return {
            "canonical": canonical,
            "layout": {
                "elements": [
                    {
                        "type": elem.element_type,
                        "text": elem.text,
                        "x": elem.x,
                        "y": elem.y,
                        "width": elem.width,
                        "height": elem.height,
                        "font_size": elem.font_size,
                        "is_bold": elem.is_bold,
                        "is_italic": elem.is_italic
                    }
                    for elem in layout_result.elements
                ],
                "total_height": layout_result.total_height,
                "fits_on_page": layout_result.fits_on_page,
                "compression_level": layout_result.compression_level,
                "page_width": layout_result.settings.page_width,
                "page_height": layout_result.settings.page_height
            },
            "metadata": {
                "page_count": 1,
                "blocks_extracted": len(merged_blocks),
                "sections_found": len(cleaned.get("sections", [])),
                "compression_applied": layout_result.compression_level
            }
        }

    def _build_canonical(self, cleaned_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build final canonical resume JSON from cleaned data
        """
        return {
            "header": {
                "name": cleaned_data.get("header", {}).get("name", ""),
                "contact": cleaned_data.get("header", {}).get("contact", {})
            },
            "sections": cleaned_data.get("sections", [])
        }
