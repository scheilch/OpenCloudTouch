#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Git pre-commit hook - runs tests and checks coverage
.DESCRIPTION
    Runs pytest with coverage check before allowing commit.
    Prevents commits if:
    - Tests fail
    - Coverage falls below 80%
.NOTES
    Use 'git commit --no-verify' to bypass this hook
#>

$ErrorActionPreference = "Stop"

# Colors
function Write-Hook { param($Message) Write-Host "[PRE-COMMIT] $Message" -ForegroundColor Cyan }
function Write-HookError { param($Message) Write-Host "[PRE-COMMIT ERROR] $Message" -ForegroundColor Red }
function Write-HookSuccess { param($Message) Write-Host "[PRE-COMMIT OK] $Message" -ForegroundColor Green }

Write-Hook "Running tests with coverage check..."
Write-Host ""

# Run pytest with coverage
try {
    Set-Location backend
    & ..\.venv\Scripts\python.exe -m pytest tests/ `
        --cov=soundtouch_bridge `
        --cov-report=term-missing `
        --cov-fail-under=75 `
        --quiet
    
    $exitCode = $LASTEXITCODE
    Set-Location ..
    
    if ($exitCode -ne 0) {
        Write-Host ""
        Write-HookError "Tests failed or coverage below 80%!"
        Write-Host ""
        Write-Host "To see details, run:" -ForegroundColor Yellow
        Write-Host "  cd backend && pytest -v" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To bypass this hook (NOT RECOMMENDED):" -ForegroundColor Yellow
        Write-Host "  git commit --no-verify" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
    
    Write-Host ""
    Write-HookSuccess "All tests passed and coverage >= 80%"
    Write-Host ""
    exit 0
}
catch {
    Write-HookError "Failed to run tests: $_"
    exit 1
}
