# PowerShell script to execute complete test suite
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " CloudScope Multi-Cloud Automated Tests   " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$env:PYTHONPATH = "backend"
pytest backend/tests -v --tb=short

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ All backend tests passed successfully!" -ForegroundColor Green
} else {
    Write-Host "`n✗ Some tests failed. Check output above." -ForegroundColor Red
    exit 1
}

Write-Host "`nValidating frontend production build (pnpm build)..." -ForegroundColor Cyan
Set-Location -Path "frontend"
pnpm build
Set-Location -Path ".."

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ Frontend build passed with zero errors!" -ForegroundColor Green
} else {
    Write-Host "`n✗ Frontend build failed." -ForegroundColor Red
    exit 1
}
