@echo off
REM Windows setup script for ResuMAX

echo ========================================
echo ResuMAX Setup (Windows)
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.11+
    exit /b 1
)

REM Check Node
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js 18+
    exit /b 1
)

echo [1/5] Setting up backend...
cd backend

REM Create virtual environment
if not exist venv (
    python -m venv venv
)

REM Activate and install dependencies
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements-minimal.txt

REM Install Playwright
playwright install chromium

cd ..

echo.
echo [2/5] Setting up frontend...
cd frontend
call npm install
cd ..

echo.
echo [3/5] Creating environment files...
if not exist backend\.env (
    copy backend\.env.example backend\.env
    echo Created backend\.env
)
if not exist frontend\.env (
    copy frontend\.env.example frontend\.env
    echo Created frontend\.env
)

echo.
echo [4/5] Creating required directories...
if not exist backend\uploads mkdir backend\uploads
if not exist backend\temp mkdir backend\temp

echo.
echo [5/5] Setup complete!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo 1. Edit backend\.env with your credentials
echo 2. Edit frontend\.env with your Firebase config
echo 3. See CREDENTIALS_NEEDED.md for details
echo.
echo To run the application:
echo   Terminal 1: run-backend.bat
echo   Terminal 2: run-frontend.bat
echo.
echo Or use Docker:
echo   docker-compose up --build
echo ========================================

pause
