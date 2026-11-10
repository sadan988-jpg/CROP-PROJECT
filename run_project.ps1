# ==============================================================================
# PMFBY Crop Analytics - Single Click Run Script
# ==============================================================================
Write-Host "Starting PMFBY Crop Analytics System..." -ForegroundColor Green

# 1. Move to backend directory
Set-Location -Path "$PSScriptRoot\backend"

# 2. Activate virtual environment if it exists
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "Activating Virtual Environment..." -ForegroundColor Cyan
    & ".\.venv\Scripts\Activate.ps1"
}

# 3. Start the unified server (serves both API & Frontend on http://127.0.0.1:8000)
Write-Host "`nServer is running! Access the web portal at:" -ForegroundColor Yellow
Write-Host "👉  http://127.0.0.1:8000/UI.html" -ForegroundColor Cyan
Write-Host "👉  http://127.0.0.1:8000/docs (Interactive Swagger API)`n" -ForegroundColor Cyan

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

