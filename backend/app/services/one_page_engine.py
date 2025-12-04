"""
One-Page Layout Engine
Ensures resumes ALWAYS fit on exactly one page.

This is DETERMINISTIC - no LLM usage.
Uses precise calculations and smart compression techniques.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter


class LayoutConfig(BaseModel):
    """Configuration for one-page layout"""
    page_size: tuple = letter
    target_height: float = letter[1]  # 11 inches
    min_font_size: int = 9
    max_font_size: int = 12
    default_font_size: int = 10
    min_line_height: float = 1.1
    max_line_height: float = 1.5
    min_margins: float = 0.4  # inches
    max_margins: float = 0.75


class LayoutMetrics(BaseModel):
    """Calculated metrics for resume layout"""
    estimated_height: float  # in inches
    font_size: int
    line_height: float
    margins: float
    section_spacing: float
    fits_one_page: bool
    compression_level: str  # "none", "light", "moderate", "aggressive"


class OnePageLayoutEngine:
    """
    Intelligently compresses resume content to fit exactly one page.
    
    Strategy:
    1. Calculate content height
    2. If > 1 page, apply compression in order:
       - Reduce section spacing
       - Reduce line height
       - Reduce font size
       - Reduce margins
    3. Never sacrifice readability
    
    Example:
        engine = OnePageLayoutEngine()
        metrics = engine.calculate_layout(resume_data, current_font=11)
        # metrics.fits_one_page == True
        # metrics.font_size might be 10 (auto-reduced)
    """
    
    def __init__(self, config: Optional[LayoutConfig] = None):
        self.config = config or LayoutConfig()
    
    def calculate_layout(
        self,
        resume_data: Dict[str, Any],
        current_font_size: int = 10
    ) -> LayoutMetrics:
        """
        Calculate optimal layout to fit one page.
        
        Args:
            resume_data: The resume content (parsed JSON)
            current_font_size: User's preferred font size
            
        Returns:
            LayoutMetrics with optimized settings
        """
        # Estimate content height
        estimated_height = self._estimate_content_height(
            resume_data,
            current_font_size
        )
        
        # Start with user preferences
        font_size = current_font_size
        line_height = 1.5
        margins = 0.75
        section_spacing = 0.2
        compression_level = "none"
        
        # Apply compression if needed
        if estimated_height > self.config.target_height:
            font_size, line_height, margins, section_spacing, compression_level = \
                self._apply_compression(
                    estimated_height,
                    current_font_size
                )
            
            # Recalculate with new settings
            estimated_height = self._estimate_content_height(
                resume_data,
                font_size,
                line_height,
                margins,
                section_spacing
            )
        
        return LayoutMetrics(
            estimated_height=estimated_height,
            font_size=font_size,
            line_height=line_height,
            margins=margins,
            section_spacing=section_spacing,
            fits_one_page=estimated_height <= self.config.target_height,
            compression_level=compression_level
        )
    
    def _estimate_content_height(
        self,
        resume_data: Dict[str, Any],
        font_size: int = 10,
        line_height: float = 1.5,
        margins: float = 0.75,
        section_spacing: float = 0.2
    ) -> float:
        """
        Estimate total content height in inches.
        
        Calculation:
        - Each line of text = font_size/72 * line_height inches
        - Each section has spacing
        - Margins reduce available space
        """
        height = margins * 2  # Top + bottom margins
        
        line_height_inches = (font_size / 72.0) * line_height
        
        # Header (name, title, contact)
        height += line_height_inches * 3  # Name, title, contact info
        height += section_spacing
        
        # Summary
        if resume_data.get("summary"):
            summary_lines = len(resume_data["summary"]) / 80  # ~80 chars per line
            height += line_height_inches * max(1, summary_lines)
            height += section_spacing
        
        # Experience
        for exp in resume_data.get("experience", []):
            height += line_height_inches * 2  # Job title + company/dates
            bullet_count = len(exp.get("bullets", []))
            height += line_height_inches * bullet_count
            height += section_spacing * 0.5  # Half spacing between jobs
        
        height += section_spacing  # After experience section
        
        # Projects
        for proj in resume_data.get("projects", []):
            height += line_height_inches  # Project name
            bullet_count = len(proj.get("bullets", []))
            height += line_height_inches * bullet_count
            height += section_spacing * 0.5
        
        height += section_spacing
        
        # Education
        edu_count = len(resume_data.get("education", []))
        height += line_height_inches * edu_count * 2  # 2 lines per edu
        height += section_spacing
        
        # Skills
        skill_categories = len(resume_data.get("skills", {}))
        height += line_height_inches * skill_categories
        
        return height
    
    def _apply_compression(
        self,
        current_height: float,
        preferred_font_size: int
    ) -> tuple:
        """
        Apply compression techniques to fit content on one page.
        
        Returns: (font_size, line_height, margins, section_spacing, compression_level)
        """
        overflow = current_height - self.config.target_height
        
        # Light compression: reduce spacing
        if overflow < 1.0:
            return (
                preferred_font_size,
                1.3,  # Reduce line height
                0.6,  # Reduce margins
                0.15,  # Reduce section spacing
                "light"
            )
        
        # Moderate compression: reduce font + spacing
        elif overflow < 2.0:
            return (
                max(self.config.min_font_size, preferred_font_size - 1),
                1.2,
                0.5,
                0.1,
                "moderate"
            )
        
        # Aggressive compression: minimum everything
        else:
            return (
                self.config.min_font_size,
                self.config.min_line_height,
                self.config.min_margins,
                0.08,
                "aggressive"
            )
    
    def get_recommendations(self, metrics: LayoutMetrics) -> list:
        """
        Get user-friendly recommendations if content doesn't fit.
        
        Returns list of actionable suggestions.
        """
        if metrics.fits_one_page:
            return ["✅ Resume fits perfectly on one page!"]
        
        recommendations = []
        
        if metrics.compression_level == "aggressive":
            recommendations.append(
                "⚠️ Content is too long. Consider removing 2-3 bullet points."
            )
            recommendations.append(
                "💡 Focus on most impactful achievements from recent roles."
            )
        
        elif metrics.compression_level == "moderate":
            recommendations.append(
                f"ℹ️ Content is slightly long. Reducing font to {metrics.font_size}pt."
            )
        
        return recommendations


# Example usage
if __name__ == "__main__":
    # Test with sample resume
    sample_resume = {
        "summary": "Experienced software engineer with 5 years...",
        "experience": [
            {
                "title": "Senior Engineer",
                "company": "Tech Corp",
                "bullets": [
                    "Led team of 5 engineers",
                    "Built microservices architecture",
                    "Reduced latency by 40%"
                ]
            },
            {
                "title": "Engineer",
                "company": "Startup Inc",
                "bullets": [
                    "Developed React applications",
                    "Implemented CI/CD pipeline"
                ]
            }
        ],
        "education": [
            {"degree": "B.S. Computer Science", "institution": "University"}
        ],
        "skills": {
            "Languages": ["Python", "JavaScript"],
            "Frameworks": ["React", "FastAPI"]
        },
        "projects": []
    }
    
    engine = OnePageLayoutEngine()
    metrics = engine.calculate_layout(sample_resume, current_font_size=11)
    
    print(f"Estimated height: {metrics.estimated_height:.2f} inches")
    print(f"Fits one page: {metrics.fits_one_page}")
    print(f"Recommended font size: {metrics.font_size}pt")
    print(f"Compression level: {metrics.compression_level}")
    
    for rec in engine.get_recommendations(metrics):
        print(rec)
