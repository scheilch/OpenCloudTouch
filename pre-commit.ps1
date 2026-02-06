#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Git pre-commit hook - runs backend and frontend unit tests with coverage checks
.DESCRIPTION
    Runs backend + frontend UNIT tests before allowing commit.
    E2E tests are skipped (run in CI/CD pipeline instead).
    
    Prevents commits if:
    - Backend tests fail (unit + integration)
    - Backend coverage falls below 80%
    - Frontend unit tests fail
    - Frontend coverage falls below 80%
.NOTES
    Coverage thresholds: Backend 80%, Frontend 80% (defined in .ci-config.json)
    E2E tests: Run manually with 'npm run test:e2e:mock' or in CI/CD
#>

$ErrorActionPreference = "Stop"

# Colors
function Write-Hook { param($Message) Write-Host "[PRE-COMMIT] $Message" -ForegroundColor Cyan }
function Write-HookError { param($Message) Write-Host "[PRE-COMMIT ERROR] $Message" -ForegroundColor Red }
function Write-HookSuccess { param($Message) Write-Host "[PRE-COMMIT OK] $Message" -ForegroundColor Green }

Write-Hook "Running unit tests (backend + frontend)..."
Write-Host ""

# Step 1: Backend tests with coverage
Write-Hook "Step 1/2: Backend tests (pytest + coverage >= 80%)..."
try {
    Set-Location backend
    & pytest --cov=cloudtouch --cov-report=term-missing --cov-fail-under=80 --quiet
    
    $exitCode = $LASTEXITCODE
    Set-Location ..
    
    if ($exitCode -ne 0) {
        Write-Host ""
        Write-HookError "Backend tests failed or coverage below 80%!"
        Write-Host ""
        Write-Host "To see details, run:" -ForegroundColor Yellow
        Write-Host "  cd backend && pytest -v --cov=cloudtouch --cov-report=term-missing" -ForegroundColor Yellow
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

# Step 2: Frontend unit tests with coverage
Write-Hook "Step 2/2: Frontend unit tests (vitest + coverage >= 80%)..."
try {
    Set-Location frontend
    
    $process = Start-Process -FilePath "npm" -ArgumentList "run", "test:coverage" -Wait -NoNewWindow -PassThru
    $exitCode = $process.ExitCode
    
    Set-Location ..
    
    if ($exitCode -ne 0) {
        Write-Host ""
        Write-HookError "Frontend unit tests failed or coverage below 80%!"
        Write-Host ""
        Write-Host "To see details, run:" -ForegroundColor Yellow
        Write-Host "  cd frontend && npm run test:coverage" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
    
    Write-HookSuccess "Frontend unit tests passed (coverage >= 80%)"
    Write-Host ""
}
catch {
    Set-Location ..
    Write-HookError "Failed to run frontend unit tests: $_"
    exit 1
}

# Step 3: E2E tests skipped in pre-commit (run in CI/CD instead)
# Reason: E2E tests are non-deterministic and can hang (violates AGENTS.md 1.4)
# Run manually with: npm run test:e2e:mock
Write-Hook "Step 3/3: E2E tests skipped (run in CI/CD)"
Write-Host ""

Write-Host ""
Write-HookSuccess "All checks passed! Proceeding with commit..."
Write-Host ""
exit 0
