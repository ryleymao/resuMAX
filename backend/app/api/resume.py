import uuid
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from app.core.dependencies import get_current_user
from app.schemas.resume import ResumeCreate, ResumeUpdate, ResumeResponse, SectionReorderRequest, DocumentStructure


router = APIRouter()

# In-memory storage for MVP
# In production, replace with database calls
resumes_db = {}


@router.post("/", response_model=ResumeResponse)
async def create_resume(
    resume: ResumeCreate,
    user: dict = Depends(get_current_user)
):
    """Create new resume"""
    resume_id = str(uuid.uuid4())
    now = datetime.utcnow()

    resume_data = ResumeResponse(
        resume_id=resume_id,
        user_id=user["uid"],
        name=resume.name,
        data=resume.data,
        target_job_intelligence_id=resume.target_job_intelligence_id,
        created_at=now,
        updated_at=now
    )

    resumes_db[resume_id] = resume_data

    return resume_data


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    user: dict = Depends(get_current_user)
):
    """Get resume by ID"""
    if resume_id not in resumes_db:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume = resumes_db[resume_id]

    # Verify ownership
    if resume.user_id != user["uid"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return resume


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: str,
    update: ResumeUpdate,
    user: dict = Depends(get_current_user)
):
    """Update resume"""
    if resume_id not in resumes_db:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume = resumes_db[resume_id]

    # Verify ownership
    if resume.user_id != user["uid"]:
        raise HTTPException(status_code=403, detail="Access denied")

    # Update fields
    if update.data is not None:
        resume.data = update.data

    if update.name is not None:
        resume.name = update.name

    if update.target_job_intelligence_id is not None:
        resume.target_job_intelligence_id = update.target_job_intelligence_id

    resume.updated_at = datetime.utcnow()

    return resume


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete resume"""
    if resume_id not in resumes_db:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume = resumes_db[resume_id]

    # Verify ownership
    if resume.user_id != user["uid"]:
        raise HTTPException(status_code=403, detail="Access denied")

    del resumes_db[resume_id]

    return {"message": "Resume deleted successfully"}


@router.get("/", response_model=List[ResumeResponse])
async def list_resumes(
    user: dict = Depends(get_current_user)
):
    """List all user's resumes"""
    user_resumes = [
        resume for resume in resumes_db.values()
        if resume.user_id == user["uid"]
    ]

    return sorted(user_resumes, key=lambda x: x.updated_at, reverse=True)


@router.post("/{resume_id}/reorder-sections", response_model=ResumeResponse)
async def reorder_sections(
    resume_id: str,
    reorder: SectionReorderRequest,
    user: dict = Depends(get_current_user)
):
    """
    Reorder resume sections

    This endpoint allows users to drag and drop sections to change their order
    in the final PDF export. The order is stored in the resume's structure metadata.
    """
    if resume_id not in resumes_db:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume = resumes_db[resume_id]

    # Verify ownership
    if resume.user_id != user["uid"]:
        raise HTTPException(status_code=403, detail="Access denied")

    # Ensure structure exists
    if resume.data.structure is None:
        resume.data.structure = DocumentStructure()

    # Update section order
    resume.data.structure.section_order = reorder.section_order
    resume.data.structure.sections_present = reorder.section_order  # sections_present mirrors section_order

    resume.updated_at = datetime.utcnow()

    return resume
