@echo off
echo Starting ResuMAX Backend...
cd backend
call venv\Scripts\activate.bat
python -m app.main
