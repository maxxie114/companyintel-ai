@echo off
REM CompanyIntel Backend Startup Script for Windows

echo 🚀 Starting CompanyIntel Backend...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  Warning: .env file not found. Copying from .env.example...
    copy .env.example .env
    echo Please edit .env with your API keys before running the server.
    exit /b 1
)

REM Start server
echo ✅ Starting FastAPI server on http://localhost:8000
echo 📚 API docs available at http://localhost:8000/docs
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
