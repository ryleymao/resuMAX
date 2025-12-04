# ResuMAX

Production-grade resume optimization platform with AI-powered content improvement.

## Features

- Upload resumes (PDF, DOCX, TXT)
- Parse into structured JSON
- Extract intelligence from job descriptions
- Optimize content with GPT-4
- Export to PDF/DOCX with perfect formatting
- Template-based rendering

## Tech Stack

**Backend**: FastAPI, OpenAI API, Playwright, Firebase Auth
**Frontend**: React, TypeScript, Tailwind, Vite

## Quick Start

### Setup

**Mac/Linux**:
```bash
./setup.sh
```

**Windows**:
```cmd
setup.bat
```

**Or using Make**:
```bash
make setup
```

### Configure

Edit `.env` files with your credentials:

**backend/.env**:
```
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json
OPENAI_API_KEY=sk-your-key
```

**frontend/.env**:
```
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_PROJECT_ID=your-project-id
# ... other Firebase config
```

### Run

**Option 1 - Scripts**:
```bash
# Terminal 1
./run-backend.sh    # or run-backend.bat on Windows

# Terminal 2
./run-frontend.sh   # or run-frontend.bat on Windows
```

**Option 2 - Make**:
```bash
make run-backend    # Terminal 1
make run-frontend   # Terminal 2
```

**Option 3 - Docker**:
```bash
docker-compose up --build
```

### Access

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Required Credentials

1. **Firebase Project**
   - Create at https://console.firebase.google.com
   - Enable Email/Password auth
   - Download service account JSON → `backend/serviceAccountKey.json`
   - Get web config → `frontend/.env`

2. **OpenAI API Key**
   - Get at https://platform.openai.com
   - Add to `backend/.env`

## Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel --prod
```

### Backend (Google Cloud Run)
```bash
cd backend
gcloud run deploy resumax-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

## Project Structure

```
backend/
  app/
    api/          # Route handlers
    core/         # Config & auth
    schemas/      # Pydantic models
    services/     # Business logic
    templates/    # Resume templates

frontend/
  src/
    components/   # React components
    hooks/        # Custom hooks
    pages/        # Pages
    lib/          # Utilities
```

## API Endpoints

- `POST /api/upload` - Upload resume
- `GET /api/resume` - List all resumes
- `GET /api/resume/{id}` - Get specific resume
- `PUT /api/resume/{id}` - Update resume
- `DELETE /api/resume/{id}` - Delete resume
- `POST /api/job/analyze` - Analyze job description and perform gap analysis
- `POST /api/optimize/bullet` - Optimize single bullet point
- `POST /api/optimize/resume` - Optimize entire resume with job description
- `POST /api/export/pdf` - Generate one-page PDF

Full docs at http://localhost:8000/docs

## Make Commands

```bash
make install         # Install all dependencies
make setup           # Complete first-time setup
make run-backend     # Run backend
make run-frontend    # Run frontend
make test            # Run tests
make clean           # Clean build artifacts
make docker-up       # Start with Docker
make docker-down     # Stop Docker
```

## License

MIT
