# PowerShell script to launch both Backend and Frontend locally
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Starting CloudScope Multi-Cloud Platform Locally " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Initialize DB and Demo Data
Write-Host "`n[1/3] Initializing SQLite database and seeding demo estate..." -ForegroundColor Yellow
python scripts/seed_demo_data.py

# 2. Start Backend in separate process or background job
Write-Host "`n[2/3] Starting FastAPI Backend on http://localhost:8000 (OpenAPI: http://localhost:8000/docs)..." -ForegroundColor Yellow
$backendJob = Start-Process -FilePath "python" -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000" -WorkingDirectory "backend" -PassThru

# 3. Start Frontend
Write-Host "`n[3/3] Starting Next.js Frontend on http://localhost:3000..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop both servers.`n" -ForegroundColor Green

Set-Location -Path "frontend"
try {
    pnpm dev
} finally {
    Set-Location -Path ".."
    if ($backendJob -and -not $backendJob.HasExited) {
        Write-Host "Stopping backend server (PID $($backendJob.Id))..." -ForegroundColor Yellow
        Stop-Process -Id $backendJob.Id -Force
    }
}
