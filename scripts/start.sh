#!/bin/bash
# Start ArenaWealth Pro - API + Frontend

set -e

echo "Starting ArenaWealth Pro..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if needed
echo "Installing dependencies..."
uv pip install -e ".[dev]" > /dev/null 2>&1

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install > /dev/null 2>&1
cd ..

# Start API in background
echo "Starting API server on http://localhost:8000"
python -m uvicorn arenawealth.api.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

# Wait for API to be ready
sleep 2

# Start frontend
echo "Starting frontend on http://localhost:5173"
cd frontend
npm run dev -- --host 0.0.0.0 &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $API_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup INT TERM

echo ""
echo "ArenaWealth Pro is running."
echo "   API:      http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"

# Wait for processes
wait
