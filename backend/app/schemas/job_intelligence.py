from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class JobIntelligence(BaseModel):
    """
    Structured intelligence extracted from job description.
    This is the ONLY context used for resume optimization.
    """
    role: str
    seniority: str = Field(
        description="Entry, Mid, Senior, Staff, Principal, or Executive"
    )
    top_skills_required: List[str] = Field(
        default_factory=list,
        description="Top 5-10 technical skills required"
    )
    must_have_keywords: List[str] = Field(
        default_factory=list,
        description="Critical keywords that should appear in resume"
    )
    nice_to_haves: List[str] = Field(
        default_factory=list,
        description="Preferred skills and technologies"
    )
    core_responsibilities: List[str] = Field(
        default_factory=list,
        description="Main job responsibilities"
    )
    attributes_recruiters_care_about: List[str] = Field(
        default_factory=list,
        description="Soft skills and personal qualities valued"
    )


class JobIntelligenceCreate(BaseModel):
    """Request to extract job intelligence from description"""
    job_description: str = Field(min_length=50)
    source_url: Optional[str] = None
    company_name: Optional[str] = None


class JobIntelligenceResponse(BaseModel):
    """Job intelligence response with metadata"""
    job_intelligence_id: str
    user_id: str
    data: JobIntelligence
    source_url: Optional[str] = None
    company_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
