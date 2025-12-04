# ResuMAX

**Ultimate Full-Stack AI Resume Optimizer**

ResuMAX is a production-grade, modular, and scalable application designed to help users optimize their resumes using AI. It features intelligent parsing, professional PDF generation, and AI-powered content enhancement.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (Planned), In-Memory (MVP)
- **AI**: OpenAI GPT-4
- **PDF Generation**: ReportLab
- **Auth**: Firebase Admin SDK

### Frontend
- **Framework**: React + Vite
- **Styling**: Tailwind CSS
- **State**: React Query
- **Routing**: React Router

## Quick Start (Docker)

```bash
# 1. Clone repository
git clone https://github.com/ryleymao/resuMAX.git
cd resuMAX

# 2. Setup Environment Variables
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# 3. Start Application
make up
```

## Quick Start (Local)

```bash
./scripts/run.sh
```

## Documentation

- [Backend Guide](backend/setup.md)
- [Frontend Guide](frontend/setup.md)
- [API Reference](api.md)
- [AI Code Reference](code_reference.md)
