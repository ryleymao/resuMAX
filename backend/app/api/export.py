from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from app.core.dependencies import get_current_user
from app.schemas.export import ExportRequest
from app.services.pdf_generator import ResumePDFGenerator
from app.api.resume import resumes_db


router = APIRouter()


@router.post("/pdf")
async def export_pdf(
    request: ExportRequest,
    user: dict = Depends(get_current_user)
):
    """
    Export resume to professional one-page PDF
    
    Uses ReportLab for precise layout control.
    Automatically fits content to one page.
    """
    # Get resume
    if request.resume_id not in resumes_db:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume_obj = resumes_db[request.resume_id]

    # Verify ownership
    if resume_obj.user_id != user["uid"]:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get options from request
    options = request.options.model_dump() if request.options else {}
    font_family = options.get("font_family", "Helvetica")
    font_size = options.get("font_size", 10)
    theme = options.get("theme", "professional")

    # Generate PDF
    try:
        pdf_buffer = ResumePDFGenerator.generate(
            resume=resume_obj.data,
            font_family=font_family,
            font_size=font_size,
            theme=theme
        )
        pdf_bytes = pdf_buffer.getvalue()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )

    # Return PDF file
    filename = resume_obj.name.replace('.pdf', '') + '_optimized.pdf'
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
