#!/usr/bin/env python3
"""
Safecrate - Start Script
Runs both the API server and frontend dev server
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path


def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     ███████╗██╗   ██╗ ██████╗ ██████╗ ███╗   ███╗███████╗║
║     ██╔════╝██║   ██║██╔════╝██╔═══██╗████╗ ████║██╔════╝║
║     ███████╗██║   ██║██║     ██║   ██║██╔████╔██║█████╗  ║
║     ╚════██║██║   ██║██║     ██║   ██║██║╚██╔╝██║██╔══╝  ║
║     ███████║╚██████╔╝╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗║
║     ╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝║
║                                                           ║
║     Content Safety Validator for Indian Creators           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)


def check_dependencies():
    """Check if required packages are installed."""
    print("\n[1/4] Checking dependencies...")

    # Check Python packages
    try:
        import fastapi

        print("   ✓ FastAPI")
    except ImportError:
        print("   ✗ FastAPI - Installing...")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "fastapi",
                "uvicorn",
                "httpx",
                "-q",
            ]
        )

    try:
        import safecrate

        print("   ✓ Safecrate")
    except ImportError:
        print("   ! Safecrate module - make sure you're in the correct directory")

    # Check frontend dependencies
    frontend_dir = Path(__file__).parent / "frontend"
    if (frontend_dir / "node_modules").exists():
        print("   ✓ Frontend dependencies")
    else:
        print("   ! Frontend dependencies - Installing...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, shell=True)

    print("   ✓ All dependencies ready!\n")


def start_api_server():
    """Start the FastAPI backend server."""
    print("[2/4] Starting API Server...")
    print("   Server will run at: http://localhost:8000")
    print("   API docs at: http://localhost:8000/docs\n")

    server_process = subprocess.Popen(
        [sys.executable, "server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=Path(__file__).parent,
    )

    # Wait for server to start
    time.sleep(3)
    print("   ✓ API Server started!\n")
    return server_process


def start_frontend():
    """Start the Vite frontend dev server."""
    print("[3/4] Starting Frontend Server...")

    frontend_dir = Path(__file__).parent / "frontend"

    frontend_process = subprocess.Popen(
        ["npm", "run", "dev", "--", "--host", "0.0.0.0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=frontend_dir,
        shell=True,
    )

    # Wait for frontend to start
    time.sleep(5)
    print("   Frontend will run at: http://localhost:5173\n")
    print("   ✓ Frontend started!\n")
    return frontend_process


def main():
    print_banner()

    # Change to script directory
    os.chdir(Path(__file__).parent)

    check_dependencies()

    print("[4/4] Starting services...\n")

    # Start servers
    api_server = start_api_server()
    frontend_server = start_frontend()

    # Open browser
    print("   Opening browser...")
    time.sleep(2)
    webbrowser.open("http://localhost:5173")

    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║  ✓ Safecrate is running!                                ║
║                                                           ║
║  Frontend:  http://localhost:5173                        ║
║  API:       http://localhost:8000                        ║
║  API Docs:  http://localhost:8000/docs                   ║
║                                                           ║
║  Press Ctrl+C to stop all services                       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    try:
        # Wait for keyboard interrupt
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping services...")
        api_server.terminate()
        frontend_server.terminate()
        print("   ✓ Services stopped!")
        sys.exit(0)


if __name__ == "__main__":
    main()
