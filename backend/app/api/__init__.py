from fastapi import APIRouter
from app.api import upload, resume, job_analysis, optimize, export

api_router = APIRouter()

# Core resume operations
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(resume.router, prefix="/resume", tags=["resume"])

# Job analysis & optimization
api_router.include_router(job_analysis.router, prefix="/job", tags=["job-analysis"])
api_router.include_router(optimize.router, prefix="/optimize", tags=["optimize"])

# Export
api_router.include_router(export.router, prefix="/export", tags=["export"])

__all__ = ["api_router"]
