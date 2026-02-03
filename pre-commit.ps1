#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Git pre-commit hook - runs tests and checks coverage
.DESCRIPTION
    Runs backend + frontend tests before allowing commit.
    Prevents commits if:
    - Backend tests fail
    - Backend coverage falls below 80%
    - Frontend Cypress E2E tests fail
.NOTES
    Use 'git commit --no-verify' to bypass this hook
    Warning: Cypress tests take ~15-30 seconds!
#>

$ErrorActionPreference = "Stop"

# Colors
function Write-Hook { param($Message) Write-Host "[PRE-COMMIT] $Message" -ForegroundColor Cyan }
function Write-HookError { param($Message) Write-Host "[PRE-COMMIT ERROR] $Message" -ForegroundColor Red }
function Write-HookSuccess { param($Message) Write-Host "[PRE-COMMIT OK] $Message" -ForegroundColor Green }

Write-Hook "Running backend + frontend tests..."
Write-Host ""

# Step 1: Backend tests with coverage
Write-Hook "Step 1/2: Backend tests (pytest + coverage)..."
try {
    Set-Location backend
    & ..\.venv\Scripts\python.exe -m pytest tests/ `
        --cov=src `
        --cov-report=term-missing `
        --cov-fail-under=80 `
        --quiet
    
    $exitCode = $LASTEXITCODE
    Set-Location ..
    
    if ($exitCode -ne 0) {
        Write-Host ""
        Write-HookError "Backend tests failed or coverage below 80%!"
        Write-Host ""
        Write-Host "To see details, run:" -ForegroundColor Yellow
        Write-Host "  cd backend && pytest -v" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
    
    Write-HookSuccess "Backend tests passed (coverage >= 80%)"
    Write-Host ""
}
catch {
    Write-HookError "Failed to run backend tests: $_"
    exit 1
}

# Step 2: Frontend Cypress E2E tests
Write-Hook "Step 2/2: Frontend E2E tests (Cypress)..."
Write-Hook "Warning: This may take ~15-30 seconds..."
try {
    Set-Location frontend
    
    # Run E2E tests with managed backend (MockMode)
    # Script handles: backend start, tests, backend stop, cleanup
    $process = Start-Process -FilePath "npm" -ArgumentList "run", "test:e2e:mock" -Wait -NoNewWindow -PassThru
    $exitCode = $process.ExitCode
    
    Set-Location ..
    
    if ($exitCode -ne 0) {
        Write-Host ""
        Write-HookError "Frontend E2E tests failed!"
        Write-Host ""
        Write-Host "To debug, run:" -ForegroundColor Yellow
        Write-Host "  cd frontend && npm run test:e2e:debug" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
    
    Write-HookSuccess "Frontend E2E tests passed"
    Write-Host ""
}
catch {
    Set-Location ..
    Write-HookError "Failed to run frontend tests: $_"
    exit 1
}

Write-Host ""
Write-HookSuccess "All checks passed! Proceeding with commit..."
Write-Host ""
exit 0
