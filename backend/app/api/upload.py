import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.dependencies import get_current_user
from app.core.config import get_settings
from app.services.pipeline import ResumeParsingPipeline
from app.schemas.resume import ResumeResponse, Resume
from datetime import datetime
import aiofiles
import os

# Import the in-memory database from resume.py
from app.api.resume import resumes_db

router = APIRouter()


@router.post("/", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """
    Upload and parse resume file

    Accepts PDF, DOCX, or TXT files.
    Returns structured Resume JSON.
    """
    settings = get_settings()

    # Validate file type
    allowed_extensions = {".pdf", ".docx", ".doc", ".txt"}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_path = upload_dir / f"{file_id}{file_ext}"

    # Save uploaded file
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Parse resume using NEW 7-stage pipeline (LLM REQUIRED)
    try:
        print(f"[UPLOAD] Starting 7-stage pipeline for {file.filename}")

        # Initialize pipeline with OpenAI API key (REQUIRED)
        pipeline = ResumeParsingPipeline(openai_api_key=settings.OPENAI_API_KEY)

        # Run Stages 1-4: Raw extraction → LLM parsing → Cleanup → Canonical JSON
        result = await pipeline.parse_resume(file_path)

        # Extract canonical JSON (this is the single source of truth)
        canonical = result["canonical"]
        layout_data = result["layout"]  # Layout engine output from Stage 5
        metadata = result["metadata"]

        print(f"[UPLOAD] Canonical JSON created with {len(canonical.get('experience', []))} experience entries")
        print(f"[UPLOAD] Layout: compression={metadata.get('layout_compression', 0)}, sections={metadata.get('sections_found', 0)}")

        # Convert canonical to Resume schema format (for backward compatibility with frontend)
        resume_data = Resume(
            header=canonical.get("header", {}),
            summary=canonical.get("summary", ""),
            experience=canonical.get("experience", []),
            projects=canonical.get("projects", []),
            skills=canonical.get("skills", {}),
            education=canonical.get("education", []),
            certifications=canonical.get("certifications", []),
            awards=canonical.get("awards", []),
            flexible_sections=[]
        )

        print(f"[UPLOAD] Resume data conversion complete")

    except Exception as e:
        # Clean up file on parse error
        print(f"[UPLOAD ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")
    finally:
        # Clean up temporary file
        if file_path.exists():
            os.remove(file_path)

    # Save to in-memory database
    resume_id = str(uuid.uuid4())
    now = datetime.utcnow()

    resume_response = ResumeResponse(
        resume_id=resume_id,
        user_id=user["uid"],
        name=file.filename,
        data=resume_data,
        layout=layout_data,  # Layout from Stage 5 (grid-based deterministic rendering)
        created_at=now,
        updated_at=now
    )

    # Store in database
    resumes_db[resume_id] = resume_response

    return resume_response
