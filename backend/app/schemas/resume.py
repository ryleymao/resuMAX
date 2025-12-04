from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ContactInfo(BaseModel):
    """Contact information in resume header"""
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    other: Optional[Dict[str, str]] = None


class ExperienceItem(BaseModel):
    """Work experience entry"""
    company: str
    title: str
    location: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    current: bool = False
    bullets: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    """Project entry"""
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    bullets: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    """Education entry"""
    institution: str
    degree: str
    field: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    honors: List[str] = Field(default_factory=list)
    coursework: List[str] = Field(default_factory=list)


class CertificationItem(BaseModel):
    """Certification or license entry"""
    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None
    expiry: Optional[str] = None
    credential_id: Optional[str] = None
    url: Optional[str] = None


class AwardItem(BaseModel):
    """Award or honor entry"""
    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None


class FormattingMetadata(BaseModel):
    """Formatting information from original document"""
    font_family: Optional[str] = None
    font_size: Optional[int] = None
    is_bold: bool = False
    is_italic: bool = False
    spacing_before: Optional[float] = None
    spacing_after: Optional[float] = None
    alignment: Optional[str] = None  # left, center, right


class FlexibleSection(BaseModel):
    """Generic section that can hold any content type"""
    title: str  # Original section title from resume
    type: str  # Type: experience, education, skills, certifications, awards, volunteer, publications, etc.
    content: Any  # Flexible content - can be list, dict, or string
    formatting: Optional[FormattingMetadata] = None
    order: int = 0  # Display order


class DocumentStructure(BaseModel):
    """Metadata about the original document structure for format preservation"""
    section_order: List[str] = Field(default_factory=list)  # Order sections appear: ["header", "summary", "experience", "education", "skills"]
    sections_present: List[str] = Field(default_factory=list)  # Which sections actually exist in the original
    estimated_font_size: Optional[int] = None  # Best guess at font size
    has_summary: bool = False
    has_projects: bool = False
    has_certifications: bool = False
    has_awards: bool = False


class Resume(BaseModel):
    """Core resume data structure - supports both standard and flexible sections"""
    header: Dict[str, Any] = Field(
        default_factory=lambda: {"name": "", "title": "", "contact": {}}
    )
    summary: str = ""

    # Standard sections (backward compatible)
    experience: List[ExperienceItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    skills: Dict[str, List[str]] = Field(default_factory=dict)
    education: List[EducationItem] = Field(default_factory=list)

    # New standard sections
    certifications: List[CertificationItem] = Field(default_factory=list)
    awards: List[AwardItem] = Field(default_factory=list)

    # Flexible sections for anything else (volunteer, publications, languages, etc.)
    flexible_sections: List[FlexibleSection] = Field(default_factory=list)

    # Overall formatting metadata from original document
    formatting: Optional[FormattingMetadata] = None

    # Document structure for format preservation when generating new resumes
    structure: Optional[DocumentStructure] = None

    # Legacy field for backward compatibility
    extra: Dict[str, Any] = Field(default_factory=dict)


class ResumeCreate(BaseModel):
    """Request to create new resume"""
    data: Resume
    name: Optional[str] = "My Resume"
    target_job_intelligence_id: Optional[str] = None


class ResumeUpdate(BaseModel):
    """Request to update resume"""
    data: Optional[Resume] = None
    name: Optional[str] = None
    target_job_intelligence_id: Optional[str] = None


class SectionReorderRequest(BaseModel):
    """Request to reorder resume sections"""
    section_order: List[str]  # e.g., ["header", "education", "experience", "skills"]


class ResumeResponse(BaseModel):
    """Resume response with metadata"""
    resume_id: str
    user_id: str
    name: str
    data: Resume
    layout: Optional[Dict[str, Any]] = None  # Layout engine output
    target_job_intelligence_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
