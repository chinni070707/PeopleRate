# PowerShell script to run automated tests
Write-Host "🚀 PeopleRate Automated Test Runner" -ForegroundColor Cyan
Write-Host "====================================`n" -ForegroundColor Cyan

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Activating virtual environment..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
}

# Install Playwright if not installed
Write-Host "📦 Checking Playwright installation..." -ForegroundColor Yellow
$playwrightCheck = python -c "import playwright" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "📥 Installing Playwright..." -ForegroundColor Yellow
    pip install playwright pytest-playwright
    Write-Host "🌐 Installing browser binaries..." -ForegroundColor Yellow
    python -m playwright install chromium
}

# Check if server is running
Write-Host "`n🔍 Checking if server is running..." -ForegroundColor Yellow
$serverCheck = Invoke-WebRequest -Uri "http://localhost:8000" -Method Head -TimeoutSec 2 -ErrorAction SilentlyContinue

if (-not $serverCheck) {
    Write-Host "⚠️  Server not running. Starting server..." -ForegroundColor Yellow
    Write-Host "Please start the server manually: uvicorn main:app --reload" -ForegroundColor Red
    Write-Host "Then run this script again.`n" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Server is running on http://localhost:8000`n" -ForegroundColor Green

# Run tests
Write-Host "🧪 Running automated tests...`n" -ForegroundColor Cyan
python tests\test_ui.py

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Some tests failed. Check output above." -ForegroundColor Red
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
