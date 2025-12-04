"""
ResuMAX Services Package

All business logic lives here.
Services are modular, reusable, and testable.
"""

# Core services (cleaned up Dec 2, 2024)
from app.services.llm_parser import ResumeParserService
from app.services.job_analyzer import JobAnalyzer
from app.services.diff_engine import DiffEngine
from app.services.one_page_engine import OnePageLayoutEngine
from app.services.pdf_generator import ResumePDFGenerator
from app.services.optimizer import OptimizationService

__all__ = [
    "ResumeParserService",      # LLM-based resume parsing
    "JobAnalyzer",              # Job description analysis (GPT-4o-mini)
    "DiffEngine",               # Text comparison & highlighting
    "OnePageLayoutEngine",      # One-page layout compression
    "ResumePDFGenerator",       # PDF generation (ReportLab)
    "OptimizationService",      # Bullet optimization
]
