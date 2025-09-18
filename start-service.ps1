# PowerShell script to run the Render Service Keep-Alive & Monitoring
# Usage: .\start-service.ps1

Write-Host "🚀 Starting Render Service Keep-Alive & Monitoring..." -ForegroundColor Green
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Check if virtual environment exists
if (-Not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: .\setup.bat" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# Check if .env exists
if (-Not (Test-Path ".env")) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red  
    Write-Host "Please copy .env.example to .env and configure it" -ForegroundColor Yellow
    exit 1
}

# Display configuration
Write-Host ""
Write-Host "📊 Service Configuration:" -ForegroundColor Cyan
$config = Get-Content "config.json" | ConvertFrom-Json
Write-Host "  Service: $($config.service_name)" -ForegroundColor White
Write-Host "  URL: $($config.base_url)" -ForegroundColor White  
Write-Host "  Endpoints: $($config.endpoints -join ', ')" -ForegroundColor White
Write-Host "  Interval: $($config.interval_seconds) seconds" -ForegroundColor White

Write-Host ""
Write-Host "Starting monitoring service..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Run the service
python main.py