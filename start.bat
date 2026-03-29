@echo off
title Safecrate - Content Safety Validator
color 0A

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║     SAFECRATE - Content Safety Validator                 ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo [1/4] Checking dependencies...
pip install fastapi uvicorn httpx -q 2>nul
echo    OK

echo.
echo [2/4] Starting API Server...
start "Safecrate API" cmd /c "python server.py"
timeout /t 3 /nobreak >nul

echo [3/4] Starting Frontend Server...
cd frontend
start "Safecrate Frontend" cmd /c "npm run dev"
cd ..

echo.
echo [4/4] Opening browser...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║  SAFECRATE IS RUNNING!                                 ║
echo  ║                                                           ║
echo  ║  Frontend:  http://localhost:5173                        ║
echo  ║  API:       http://localhost:8000                        ║
echo  ║                                                           ║
echo  ║  Press Ctrl+C in the API window to stop                 ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

pause
