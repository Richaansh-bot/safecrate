#!/bin/bash

# Safecrate - Content Safety Validator
# Start script for Linux/macOS

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     SAFECRATE - Content Safety Validator                 ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "[1/4] Checking dependencies..."
pip install fastapi uvicorn httpx -q
echo "   OK"

echo ""
echo "[2/4] Starting API Server..."
python server.py &
API_PID=$!
sleep 3
echo "   Server running at http://localhost:8000"

echo ""
echo "[3/4] Starting Frontend Server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "[4/4] Opening browser..."
sleep 3
xdg-open http://localhost:5173 2>/dev/null || open http://localhost:5173 2>/dev/null || echo "   Open manually: http://localhost:5173"

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  SAFECRATE IS RUNNING!                                 ║"
echo "║                                                           ║"
echo "║  Frontend:  http://localhost:5173                      ║"
echo "║  API:       http://localhost:8000                       ║"
echo "║                                                           ║"
echo "║  Press Ctrl+C to stop all services                       ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Wait for interrupt
trap "kill $API_PID $FRONTEND_PID 2>/dev/null; echo 'Services stopped!'; exit" INT TERM

wait
