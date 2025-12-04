#!/bin/bash

# Quick start script for local development (non-Docker)

# Colors
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting ResuMAX in local development mode...${NC}"

# Check for .env
if [ ! -f backend/.env ]; then
    echo "Error: backend/.env not found. Please copy backend/.env.example to backend/.env"
    exit 1
fi

# Start Backend
echo -e "${GREEN}Starting Backend...${NC}"
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Warning: No virtual environment found. Using system python."
fi

# Install dependencies if needed
# pip install -r requirements.txt

# Run in background
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..
    
# Start Frontend
echo -e "${GREEN}Starting Frontend...${NC}"
cd frontend
# npm install
npm run dev &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}ResuMAX is running!${NC}"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Press CTRL+C to stop."

# Handle cleanup
cleanup() {
    echo -e "${GREEN}Stopping services...${NC}"
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit
}

trap cleanup SIGINT

wait
