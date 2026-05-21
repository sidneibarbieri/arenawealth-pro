#!/usr/bin/env bash
# Start the local API and browser app.

set -euo pipefail

echo "Starting ArenaWealth Pro..."

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3.11 -m venv .venv
fi

echo "Installing dependencies..."
.venv/bin/pip install -e ".[dev]" > /dev/null 2>&1

echo "Installing frontend dependencies..."
cd frontend
npm install > /dev/null 2>&1
cd ..

echo "Starting API server on http://localhost:8000"
.venv/bin/uvicorn arenawealth.api.main:app --host 127.0.0.1 --port 8000 --reload &
API_PID=$!

sleep 2

echo "Starting frontend on http://localhost:5173"
cd frontend
npm run dev -- --host 127.0.0.1 &
FRONTEND_PID=$!

cleanup() {
    echo ""
    echo "Shutting down..."
    kill "$API_PID" 2>/dev/null || true
    kill "$FRONTEND_PID" 2>/dev/null || true
    exit 0
}

trap cleanup INT TERM

echo ""
echo "ArenaWealth Pro is running."
echo "   API:      http://127.0.0.1:8000"
echo "   Frontend: http://127.0.0.1:5173"
echo "   API Docs: http://127.0.0.1:8000/docs"
echo ""
echo "Press Ctrl+C to stop"

wait
