# Backend Setup Guide

## Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL (optional for local dev)

## Installation

1. **Create Virtual Environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Copy `.env.example` to `.env` and configure:
   - `OPENAI_API_KEY`: Required for parsing/optimization
   - `FIREBASE_*`: Required for auth

## Running Locally
```bash
uvicorn app.main:app --reload
```

## Testing
```bash
pytest
```
