"""
ResuMAX 7-Stage Pipeline

STAGE 1: Raw Extraction (code only)
STAGE 2: LLM Structural Parsing (GPT-4o-mini required)
STAGE 3: Semantic Cleanup (code only)
STAGE 4: Canonical JSON Output
STAGE 5: Deterministic Layout Engine
STAGE 6: Structured Field Editor (frontend)
STAGE 7: Optional LLM Optimization (user-triggered)
"""
from .pipeline import ResumeParsingPipeline

__all__ = ["ResumeParsingPipeline"]
