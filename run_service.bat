@echo off
echo ==========================================
echo  Render Service Keep-Alive Monitor
echo ==========================================

:: Change to the script directory
cd /d "%~dp0"

:: Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to set up the environment.
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and configure your settings.
    echo.
    if exist ".env.example" (
        echo Would you like to create .env from .env.example now? (y/n)
        set /p create_env=
        if /i "!create_env!"=="y" (
            copy ".env.example" ".env"
            echo .env file created. Please edit it with your configuration.
            notepad .env
        )
    )
    echo.
    pause
    exit /b 1
)

:: Display configuration info
echo.
echo Starting Render Service Keep-Alive Monitor...
echo Service will:
echo - Ping your Render service every 60 seconds
echo - Monitor uptime/downtime
echo - Send daily reports via email at midnight
echo - Save logs to the 'logs' directory
echo.
echo Press Ctrl+C to stop the service
echo.

:: Run the service
python main.py

echo.
echo Service stopped.
pause