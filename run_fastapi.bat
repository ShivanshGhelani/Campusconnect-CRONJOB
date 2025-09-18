@echo off
echo.
echo ===============================================
echo   Campus Connect Monitoring - FastAPI Server
echo ===============================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing FastAPI dependencies...
pip install fastapi uvicorn python-multipart -q

REM Check if config exists
if not exist ".env" (
    echo.
    echo WARNING: No .env file found!
    echo Please copy .env.example to .env and configure your settings.
    echo.
    pause
)

REM Start FastAPI development server
echo.
echo Starting FastAPI development server...
echo Access the monitoring dashboard at: http://localhost:8000
echo API documentation available at: http://localhost:8000/docs
echo.

cd api
uvicorn index:app --reload --host 0.0.0.0 --port 8000