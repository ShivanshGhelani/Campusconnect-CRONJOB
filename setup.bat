@echo off
echo ==========================================
echo  Render Service Keep-Alive Setup
echo ==========================================

:: Change to the script directory
cd /d "%~dp0"

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found. Continuing setup...

:: Create virtual environment
echo.
echo Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

:: Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install dependencies
echo.
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

:: Create logs directory
echo.
echo Creating logs directory...
if not exist "logs" mkdir logs
if not exist "logs\report_backups" mkdir logs\report_backups

:: Create .env file from example if it doesn't exist
echo.
if not exist ".env" (
    if exist ".env.example" (
        echo Creating .env file from example...
        copy ".env.example" ".env"
        echo.
        echo IMPORTANT: Please edit the .env file with your configuration:
        echo - Set your Render service BASE_URL
        echo - Configure your email settings
        echo.
    ) else (
        echo Warning: .env.example not found. You'll need to create .env manually.
    )
) else (
    echo .env file already exists.
)

echo.
echo ==========================================
echo  Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit the .env file with your service URL and email settings
echo 2. Update config.json if needed
echo 3. Run the service with: run_service.bat
echo.
echo For testing, you can also run:
echo   python main.py --report-now
echo.

pause