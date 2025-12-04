#!/bin/bash
# Unix/Mac setup script for ResuMAX

set -e

echo "========================================"
echo "ResuMAX Setup (Unix/Mac)"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found. Please install Node.js 18+"
    exit 1
fi

echo "[1/5] Setting up backend..."
cd backend

# Create virtual environment (try python3.11 first, fall back to python3)
if command -v python3.11 &> /dev/null; then
    python3.11 -m venv venv
else
    python3 -m venv venv
fi

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-minimal.txt

# Install Playwright
playwright install chromium || true

cd ..

echo ""
echo "[2/5] Setting up frontend..."
cd frontend
npm install
cd ..

echo ""
echo "[3/5] Creating environment files..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "Created backend/.env"
fi

if [ ! -f frontend/.env ]; then
    cp frontend/.env.example frontend/.env
    echo "Created frontend/.env"
fi

echo ""
echo "[4/5] Creating required directories..."
mkdir -p backend/uploads backend/temp

echo ""
echo "[5/5] Setup complete!"
echo ""
echo "========================================"
echo "Next Steps:"
echo "========================================"
echo "1. Edit backend/.env with your credentials"
echo "2. Edit frontend/.env with your Firebase config"
echo "3. See CREDENTIALS_NEEDED.md for details"
echo ""
echo "To run the application:"
echo "  Terminal 1: ./run-backend.sh"
echo "  Terminal 2: ./run-frontend.sh"
echo ""
echo "Or use Make:"
echo "  make run-backend (Terminal 1)"
echo "  make run-frontend (Terminal 2)"
echo ""
echo "Or use Docker:"
echo "  make docker-up"
echo "========================================"
