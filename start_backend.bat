@echo off
echo ====================================
echo   PrivacyLens - Starting Backend
echo ====================================

cd /d "%~dp0backend"

if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo [INFO] Installing dependencies...
pip install -r requirements.txt --quiet

if not exist ".env" (
    echo [WARN] .env not found! Copying from .env.example
    copy "..\\.env.example" ".env"
    echo [WARN] Please edit backend\.env with your MySQL password and JWT secret!
)

echo [INFO] Starting FastAPI server on http://localhost:8000
echo [INFO] API docs at http://localhost:8000/docs
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
