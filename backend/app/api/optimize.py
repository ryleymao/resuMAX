"""
Optimization API
Endpoints for AI-powered content improvement.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.core.dependencies import get_current_user
from app.services.optimizer import OptimizationService


router = APIRouter()


class OptimizeBulletRequest(BaseModel):
    """Request to optimize a single bullet"""
    bullet: str
    context: Dict[str, Any] = {}  # job_title, company, etc.


class OptimizeBulletResponse(BaseModel):
    """Response with optimized bullet"""
    optimized: str
    original: str
    suggestions: list = []


@router.post("/bullet", response_model=OptimizeBulletResponse)
async def optimize_bullet(
    request: OptimizeBulletRequest,
    user: dict = Depends(get_current_user)
):
    """
    Optimize a single resume bullet point.
    
    Uses GPT-4 for quality rewrites.
    
    Example:
        Input: "Managed team projects"
        Output: "Led cross-functional team of 5 engineers on 3 high-impact projects, reducing delivery time by 30%"
    
    Cost: ~$0.005 per bullet
    """
    try:
        optimizer = OptimizationService()
        
        # Use the optimizer service
        # Note: OptimizationService.optimize_bullet expects different signature
        # We'll adapt it here
        result = await optimizer.optimize_bullet(
            bullet=request.bullet,
            job_title=request.context.get("job_title", ""),
            company=request.context.get("company", "")
        )
        
        return OptimizeBulletResponse(
            optimized=result,
            original=request.bullet,
            suggestions=[]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Optimization failed: {str(e)}"
        )


class OptimizeResumeRequest(BaseModel):
    """Request to optimize full resume"""
    resume_data: Dict[str, Any]
    job_description: str


@router.post("/resume")
async def optimize_resume(
    request: OptimizeResumeRequest,
    user: dict = Depends(get_current_user)
):
    """
    Optimize entire resume based on job description.
    Returns a map of original -> optimized bullets.
    """
    try:
        optimizer = OptimizationService()
        result = await optimizer.optimize_resume(
            request.resume_data,
            request.job_description
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
