#!/bin/bash
echo "Starting ResuMAX Backend..."
cd backend
source venv/bin/activate
python -m app.main
