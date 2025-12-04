"""
Complete 7-Stage ResuMAX Pipeline

STAGE 1: Raw Extraction (code only)
STAGE 2: LLM Structural Parsing (GPT-4o-mini required)
STAGE 3: Semantic Cleanup (code only)
STAGE 4: Canonical JSON Output
STAGE 5: Deterministic Layout Engine (grid-based rendering)
STAGE 6: Structured Field Editor (frontend)
STAGE 7: Optional LLM Optimization (user-triggered)

This module handles stages 1-5.
"""
from pathlib import Path
from typing import Dict, Any
from .stage1_raw_extraction import RawExtractor
from .stage2_llm_parsing import LLMStructuralParser
from .stage3_semantic_cleanup import SemanticCleaner
from app.services.layout import LayoutEngine


class ResumeParsingPipeline:
    """
    Complete parsing pipeline (Stages 1-5)
    """

    def __init__(self, openai_api_key: str, layout_config: Dict[str, Any] = None):
        self.raw_extractor = RawExtractor()
        self.llm_parser = LLMStructuralParser(api_key=openai_api_key)
        self.cleaner = SemanticCleaner()

        # Layout configuration (user-configurable)
        self.layout_config = layout_config or {
            "template_name": "modern_tech",
            "use_two_column_header": True,  # Default: two-column layout
            "date_alignment": "right"  # Default: right-aligned dates
        }
        self.layout_engine = LayoutEngine(
            template_name=self.layout_config.get("template_name", "modern_tech"),
            template_config=self.layout_config
        )

    async def parse_resume(self, file_path: Path) -> Dict[str, Any]:
        """
        Run complete parsing pipeline

        Returns:
        {
            "canonical": {...},  # Canonical resume JSON (Stage 4)
            "metadata": {...}    # Processing metadata
        }
        """

        # STAGE 1: Raw Extraction
        print("[STAGE 1] Extracting raw text and metadata from PDF...")
        raw_doc = self.raw_extractor.extract_from_pdf(file_path)
        print(f"  ✓ Extracted {len(raw_doc.text_spans)} text spans")
        print(f"  ✓ Raw text length: {len(raw_doc.raw_text)} characters")

        # STAGE 2: LLM Structural Parsing (REQUIRED)
        print("[STAGE 2] Using LLM to identify structure...")
        structured_data = await self.llm_parser.parse_structure(
            raw_doc.raw_text,
            raw_doc.text_spans
        )
        print(f"  ✓ Identified {len(structured_data.get('experience', []))} experience entries")
        print(f"  ✓ Identified {len(structured_data.get('projects', []))} project entries")
        print(f"  ✓ Identified {len(structured_data.get('education', []))} education entries")

        # STAGE 3: Semantic Cleanup
        print("[STAGE 3] Cleaning text artifacts...")
        cleaned_data = self.cleaner.clean(structured_data)
        print("  ✓ Text cleanup complete")

        # STAGE 4: Build Canonical JSON
        print("[STAGE 4] Building canonical JSON...")
        canonical = self._build_canonical_json(cleaned_data)
        print(f"  ✓ Canonical JSON complete ({self._count_sections(canonical)} sections)")

        # STAGE 5: Deterministic Layout Engine
        print("[STAGE 5] Rendering layout with grid-based engine...")
        layout_result = self.layout_engine.layout_resume(canonical)
        print(f"  ✓ Layout rendered (compression level: {layout_result['compression_level']}, fits on page: {layout_result['fits_on_page']})")

        return {
            "canonical": canonical,
            "layout": layout_result,
            "metadata": {
                "page_count": raw_doc.page_count,
                "text_spans": len(raw_doc.text_spans),
                "sections_found": self._count_sections(canonical),
                "layout_compression": layout_result["compression_level"]
            }
        }

    def _build_canonical_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build final canonical JSON (Stage 4)
        This is the single source of truth
        """
        return {
            "header": data.get("header", {}),
            "summary": data.get("summary", ""),
            "experience": data.get("experience", []),
            "projects": data.get("projects", []),
            "education": data.get("education", []),
            "skills": data.get("skills", {}),
            "certifications": data.get("certifications", []),
            "awards": data.get("awards", []),
            "unclassified": data.get("unclassified", [])
        }

    def _count_sections(self, canonical: Dict[str, Any]) -> int:
        """Count non-empty sections"""
        count = 0
        if canonical.get("experience"):
            count += 1
        if canonical.get("projects"):
            count += 1
        if canonical.get("education"):
            count += 1
        if canonical.get("skills"):
            count += 1
        if canonical.get("certifications"):
            count += 1
        if canonical.get("awards"):
            count += 1
        return count
