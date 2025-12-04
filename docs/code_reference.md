# AI Code Reference - ResuMAX

**Last Updated**: December 2024 (Updated with structure preservation, format metadata, and anti-hallucination parsing)

This file serves as a complete map for AI agents and developers. It documents the **current, cleaned-up codebase** with all redundant files removed.

---

## 🏗️ Architecture Overview

**Backend**: FastAPI + Python 3.11  
**Frontend**: React + TypeScript + Vite  
**Database**: In-Memory (PostgreSQL planned)  
**Auth**: Firebase Admin SDK  
**AI**: OpenAI (GPT-4o-mini for analysis, GPT-4 for rewrites)  
**Prompt Framework**: All LLM prompts follow ROAST (Role, Objective, Audience, Style, Tone)

---

## 📁 Backend Structure (`backend/`)

### Models (`app/models/`)
*Currently empty - using Pydantic schemas with in-memory storage*

Planned: SQLModel/SQLAlchemy models for PostgreSQL migration

### Schemas (`app/schemas/`)
All request/response validation using Pydantic.

**Files**:
- `resume.py`: Resume data structures
  - `Resume`: Complete resume object
  - `ResumeCreate`, `ResumeUpdate`: CRUD operations
  - `ResumeResponse`: API response format
  - `ExperienceItem`, `ProjectItem`, `EducationItem`: Sub-schemas
  - **NEW**: `DocumentStructure`: Metadata about original resume structure
    - `section_order`: List of sections in order they appeared
    - `sections_present`: Which sections actually exist
    - `has_summary`, `has_projects`, `has_certifications`, `has_awards`: Boolean flags
  - **NEW**: `FormattingMetadata`: Font, spacing, alignment info (planned for future)

- `export.py`: PDF/DOCX export configurations
  - `ExportRequest`: Export parameters
  - `ExportOptions`: Font, size, theme settings

### Services (`app/services/`)
**Core business logic**. All services are modular and reusable.

#### 1. **LLM Parser** (`llm_parser.py`)
- **Purpose**: Parse resumes using GPT-4 with ROAST framework
- **Features**:
  - PDF/DOCX/TXT extraction (PyMuPDF, pypdf, python-docx)
  - Structured JSON output matching Resume schema
  - Extracts: Header, Summary, Experience, Projects, Skills, Education, Certifications, Awards
  - **NEW**: Structure metadata extraction (section order, which sections exist)
  - **NEW**: Enhanced ROAST prompts to prevent fabrication and preserve exact content
  - Uses ROAST framework prompts for accurate extraction
  - Graceful fallback to regex parser if LLM fails
  - Handles missing dependencies (pypdf, python-docx)
  - **CRITICAL**: ONLY extracts sections that exist in original resume, never invents content
- **Cost**: ~$0.01 per resume (GPT-4 Turbo)
- **ROAST Prompt**: Expert resume parser role, extract ONLY what exists, preserve exact wording

#### 2. **Job Analyzer** (`job_analyzer.py`) ✨ NEW
- **Purpose**: Extract requirements from job descriptions
- **Model**: GPT-4o-mini (100x cheaper than GPT-4)
- **Features**:
  - Extracts required/preferred keywords
  - Identifies role level (Entry/Mid/Senior/Staff)
  - Detects industry
  - Lists key responsibilities
  - **Gap Analysis**: Compares resume vs job requirements
    - Missing keywords
    - Weak bullets (no metrics, vague)
    - Alignment score (0-100)
    - Actionable recommendations
- **Cost**: ~$0.001 per analysis

#### 3. **Diff Engine** (`diff_engine.py`) ✨ NEW
- **Purpose**: Track text changes for visual highlighting
- **Method**: Deterministic (Python's difflib, no LLM)
- **Features**:
  - Word-level change detection
  - Categories: added, removed, unchanged
  - Keyword highlighting for job matching
  - Returns precise positions for UI
- **Use Cases**:
  - Yellow highlights for LLM edits
  - Green highlights for added keywords
  - Accept/reject workflow

#### 4. **One-Page Layout Engine** (`one_page_engine.py`) ✨ NEW
- **Purpose**: Guarantee resume fits exactly one page
- **Method**: Deterministic calculations (no LLM)
- **Compression Strategy** (applied in order):
  1. Reduce section spacing
  2. Reduce line height (min 1.1)
  3. Reduce font size (min 9pt)
  4. Reduce margins (min 0.4in)
- **Intelligence**:
  - Estimates content height in inches
  - Applies minimal compression needed
  - Never sacrifices readability
  - Provides user recommendations
- **Returns**: LayoutMetrics with fit status

#### 5. **PDF Generator** (`pdf_generator.py`)
- **Purpose**: Generate professional PDFs with ReportLab
- **Features**:
  - Customizable fonts (Helvetica, Times, Courier)
  - Adjustable sizes (8-12pt)
  - Multiple themes (Professional, Modern, Minimal)
  - **One-page guarantee** - Integrated with OnePageLayoutEngine
  - Automatic compression (spacing, font size, margins)
  - Supports all resume sections (Summary, Experience, Projects, Skills, Education, Certifications, Awards)
  - **NEW**: Respects original document structure metadata (section order from parsing)
  - **NEW**: Only includes sections that existed in original resume
- **Output**: BytesIO buffer or file

#### 6. **Optimizer** (`optimizer.py`)
- **Purpose**: AI-powered bullet point improvement
- **Model**: GPT-4 (for quality)
- **Features**:
  - Single bullet optimization
  - **Full resume optimization** with job description
  - Optimizes both experience and project bullets
  - Context-aware (job title, company, job description)
  - Action-oriented rewrites with metrics
  - Returns mapping of original -> optimized bullets
  - Uses ROAST framework prompts for consistent quality
- **Cost**: ~$0.005 per bullet, ~$0.05-0.10 per full resume optimization
- **ROAST Prompts**: 
  - Single bullet: Expert resume writer role, ATS-focused optimization
  - Full resume: Senior optimization specialist, job description alignment

### API Routes (`app/api/`)

#### `upload.py`
- **POST** `/api/upload`
- Accepts: PDF, DOCX, TXT
- Calls: LLM Parser
- Returns: Parsed Resume object

#### `resume.py`
- **GET** `/api/resume` - List all resumes
- **GET** `/api/resume/{id}` - Get specific resume
- **PUT** `/api/resume/{id}` - Update resume
- **DELETE** `/api/resume/{id}` - Delete resume
- Storage: In-memory dict (`resumes_db`)

#### `job_analysis.py` ✨ NEW
- **POST** `/api/job/analyze`
- **Input**:
  ```json
  {
    "job_description": "string",
    "resume_id": "optional"
  }
  ```
- **Output**:
  - Job analysis (keywords, level, industry)
  - Gap analysis (if resume_id provided)
- **Cost**: ~$0.001 per call (GPT-4o-mini)

#### `optimize.py`
- **POST** `/api/optimize/bullet`
- Single bullet AI improvement
- Returns: Optimized version

#### `export.py`
- **POST** `/api/export/pdf`
- Generates one-page PDF
- Customizable: font, size, theme

### Configuration (`app/core/`)
- `config.py`: Settings (Pydantic BaseSettings)
- `dependencies.py`: Auth (Firebase `get_current_user`)
- `firebase.py`: Firebase Admin SDK initialization

---

## 📁 Frontend Structure (`frontend/`)

### Pages (`src/pages/`)
- `Dashboard.tsx`: Resume list, upload, delete (with improved error handling)
- `Editor.tsx`: **COMPLETE** resume editor with:
  - Real-time editing for ALL sections (Header, Summary, Experience, Projects, Skills, Education, Certifications, Awards)
  - PDF export options
  - Full resume optimization with job description
  - Diff highlighting for optimized changes (yellow highlights)
  - Accept/reject workflow for optimizations
  - Job description sidebar integration
  - Add/remove experiences, projects, bullets
  - AI optimization (single bullet + full resume)
- `Login.tsx`: Firebase authentication
- `Upload.tsx`: Resume upload interface

### Components (`src/components/`)
- `RichTextEditor.tsx`: TipTap-based rich text editor with placeholder support
- `JobDescriptionSidebar.tsx`: Job description analysis, keyword extraction, gap analysis
- `BulletOptimizer.tsx`: Single bullet optimization with accept/reject
- `DiffHighlight.tsx`: Word-level diff visualization (yellow for changes, red for removed)
- `ResumePreview.tsx`: PDF preview component
- `ProtectedRoute.tsx`: Auth guard for protected routes

### Hooks (`src/hooks/`)
- `useResume.ts`: React Query hooks
  - `useResumes()`: Fetch all resumes
  - `useResume(id)`: Fetch single resume
  - `useUpdateResume()`: Update mutation
  - `useDeleteResume()`: Delete mutation
  - `useUploadResume()`: Upload mutation

- `useOptimize.ts`: AI optimization
  - `useOptimizeBullet()`: Single bullet improvement

### API Client (`src/lib/api.ts` or `src/services/api/`)
- Axios instance with Firebase auth
- Base URL from env (`VITE_API_URL`)

---

## 🔐 Environment Variables

### Backend (`backend/.env`)
```bash
# Required
OPENAI_API_KEY=sk-...           # For LLM parsing & optimization
FIREBASE_PROJECT_ID=...         # Auth
FIREBASE_CREDENTIALS_PATH=...   # Service account key

# Optional
UPLOAD_DIR=./uploads
TEMP_DIR=./temp
```

### Frontend (`frontend/.env`)
```bash
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=...
VITE_FIREBASE_PROJECT_ID=...
```

---

## 🚀 Workflows

### Adding a New Feature

1. **Backend**:
   - Add Pydantic schema in `app/schemas/`
   - Implement service logic in `app/services/`
   - Create API route in `app/api/`
   - Register router in `app/api/__init__.py`

2. **Frontend**:
   - Create React Query hook in `src/hooks/`
   - Build UI component/page
   - Connect via API client

3. **Documentation**:
   - Update `docs/api.md` with new endpoints
   - Update `docs/code_reference.md` (this file)

### Testing a Service

All services have `if __name__ == "__main__"` blocks for standalone testing:

```bash
cd backend
python -m app.services.job_analyzer
python -m app.services.diff_engine
python -m app.services.one_page_engine
```

---

## 🗑️ Removed Files (Cleanup Dec 2)

These were **deleted** as redundant:

### Services
- `parser.py` → Replaced by `llm_parser.py`
- `layout_engine.py` → Replaced by `one_page_engine.py`
- `jd_extractor.py` → Replaced by `job_analyzer.py`
- `renderer.py` → Not used
- `template_loader.py` → Not used
- `docx_exporter.py` → Not used

### API
- `job_description.py` → Replaced by `job_analysis.py`
- `templates.py` → Not needed

### Tests
- `tests/` folder → Will recreate with new structure

---

## 📊 Cost Optimization Strategy

| Operation | Model | Cost/Call | Why |
|-----------|-------|-----------|-----|
| Resume Parsing | GPT-4 Turbo | ~$0.01 | Quality matters, done once |
| Job Analysis | GPT-4o-mini | ~$0.001 | Simple extraction, done often |
| Gap Analysis | GPT-4o-mini | ~$0.001 | Comparison task, fast |
| Bullet Optimization | GPT-4 | ~$0.005 | Quality rewrites |
| Diff Engine | None (deterministic) | $0 | No LLM needed |
| Layout Engine | None (deterministic) | $0 | Pure math |

**Total typical flow**: Upload ($0.01) + Analyze JD ($0.001) + Optimize 5 bullets ($0.025) = **~$0.036 per resume**

---

## 🎯 Next Phase: Rich Text Editor

### Planned Components
1. **Rich Text Editor** (Lexical/TipTap)
2. **Live PDF Preview** (WebSocket)
3. **Diff Highlighting UI** (Yellow/Green highlights)
4. **Accept/Reject Workflow** (Per-bullet controls)
5. **Job Description Sidebar** (Keyword visualization)

### Required Backend Services
1. **WebSocket Handler** for real-time sync
2. **Batch Optimization** (multiple bullets at once)

---

## 📝 Notes for AI Agents & Developers

- **Always check this file first** before making changes
- All services are in `backend/app/services/`
- All API routes are in `backend/app/api/`
- All schemas are in `backend/app/schemas/`
- Use GPT-4o-mini for cheap operations (analysis)
- Reserve GPT-4 for quality rewrites (optimization, parsing)
- **All LLM prompts follow ROAST framework** (Role, Objective, Audience, Style, Tone)
- Update this file when you add/remove code
- Keep `docs/api.md` in sync with API changes
- See `docs/backend/workflow.md` for adding backend features
- See `docs/frontend/workflow.md` for adding frontend features

---

**End of Reference**
