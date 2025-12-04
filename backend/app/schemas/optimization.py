from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class OptimizationContext(BaseModel):
    """Context for optimization requests"""
    job_title: Optional[str] = None
    company: Optional[str] = None
    job_intelligence_id: Optional[str] = None
    target_role: Optional[str] = None


class BulletOptimizationRequest(BaseModel):
    """Request to optimize a single bullet point"""
    bullet: str = Field(min_length=1)
    context: OptimizationContext


class BulletOptimizationResponse(BaseModel):
    """Response from bullet optimization"""
    original: str
    optimized: str
    reasoning: Optional[str] = None
    keywords_matched: List[str] = Field(default_factory=list)


class SectionOptimizationRequest(BaseModel):
    """Request to optimize an entire section"""
    section: str = Field(
        description="Section name: summary, experience, skills, etc."
    )
    content: str = Field(min_length=1)
    context: OptimizationContext


class SectionOptimizationResponse(BaseModel):
    """Response from section optimization"""
    section: str
    original: str
    optimized: str
    keywords_matched: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
