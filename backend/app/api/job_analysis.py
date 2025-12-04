"""
Job Description Analysis API
Endpoints for analyzing job descriptions and comparing with resumes.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.core.dependencies import get_current_user
from app.services.job_analyzer import JobAnalyzer, JobAnalysisResult, ResumeGapAnalysis
from app.api.resume import resumes_db


router = APIRouter()


class AnalyzeJobRequest(BaseModel):
    """Request to analyze a job description"""
    job_description: str
    resume_id: Optional[str] = None  # If provided, also run gap analysis


class AnalyzeJobResponse(BaseModel):
    """Response from job analysis"""
    job_analysis: JobAnalysisResult
    gap_analysis: Optional[ResumeGapAnalysis] = None


@router.post("/analyze", response_model=AnalyzeJobResponse)
async def analyze_job_description(
    request: AnalyzeJobRequest,
    user: dict = Depends(get_current_user)
):
    """
    Analyze a job description to extract requirements.
    
    If resume_id is provided, also performs gap analysis.
    
    Uses GPT-4o-mini for cost optimization.
    """
    analyzer = JobAnalyzer()
    
    # Analyze job description
    job_analysis = await analyzer.analyze_job_description(request.job_description)
    
    gap_analysis = None
    
    # Optional: Compare with resume
    if request.resume_id:
        if request.resume_id not in resumes_db:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        resume_obj = resumes_db[request.resume_id]
        
        # Verify ownership
        if resume_obj.user_id != user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Convert resume to text for analysis
        resume_text = _resume_to_text(resume_obj.data)
        
        # Perform gap analysis
        gap_analysis = await analyzer.analyze_resume_gaps(resume_text, job_analysis)
    
    return AnalyzeJobResponse(
        job_analysis=job_analysis,
        gap_analysis=gap_analysis
    )


def _resume_to_text(resume_data) -> str:
    """Convert resume object to plain text for analysis"""
    parts = []
    
    # Header
    if resume_data.header:
        parts.append(resume_data.header.get("name", ""))
        parts.append(resume_data.header.get("title", ""))
    
    # Summary
    if resume_data.summary:
        parts.append(resume_data.summary)
    
    # Experience
    for exp in resume_data.experience:
        parts.append(f"{exp.title} at {exp.company}")
        parts.extend(exp.bullets)
    
    # Projects
    for proj in resume_data.projects:
        parts.append(proj.name)
        parts.extend(proj.bullets)
    
    # Skills
    for category, skills in resume_data.skills.items():
        parts.append(f"{category}: {', '.join(skills)}")
    
    # Education
    for edu in resume_data.education:
        parts.append(f"{edu.degree} from {edu.institution}")
    
    return "\n".join(parts)
