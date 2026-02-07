#!/usr/bin/env pwsh
# Install Git Hooks for OpenCloudTouch
# This script configures pre-commit hooks for local development

Write-Host "Installing Git Hooks for OpenCloudTouch..." -ForegroundColor Cyan
Write-Host ""

# Check if in git repository
if (-not (Test-Path ".git")) {
    Write-Host "ERROR: Not in a git repository root!" -ForegroundColor Red
    Write-Host "Run this script from the project root directory." -ForegroundColor Yellow
    exit 1
}

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  OK: Found $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found! Install Python 3.11+ first." -ForegroundColor Red
    exit 1
}

# Install pre-commit package
Write-Host ""
Write-Host "Installing pre-commit framework..." -ForegroundColor Yellow
pip install pre-commit

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Failed to install pre-commit!" -ForegroundColor Red
    exit 1
}

# Install commitizen for commit message validation
Write-Host ""
Write-Host "Installing commitizen..." -ForegroundColor Yellow
pip install commitizen

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Failed to install commitizen!" -ForegroundColor Red
    exit 1
}

# Install backend dev dependencies
Write-Host ""
Write-Host "Installing backend dev dependencies..." -ForegroundColor Yellow
pip install -r apps/backend/requirements-dev.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "  WARNING: Could not install backend dependencies" -ForegroundColor Yellow
}

# Check Node.js installation
Write-Host ""
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  OK: Found $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Node.js not found! Install Node.js 20+ first." -ForegroundColor Red
    exit 1
}

# Install frontend dependencies
Write-Host ""
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Push-Location apps/frontend
npm ci --prefer-offline
if ($LASTEXITCODE -ne 0) {
    Pop-Location
    Write-Host "  ERROR: Failed to install frontend dependencies!" -ForegroundColor Red
    exit 1
}
Pop-Location

# Install pre-commit hooks
Write-Host ""
Write-Host "Installing pre-commit hooks..." -ForegroundColor Yellow
pre-commit install --hook-type pre-commit --hook-type commit-msg --hook-type pre-push

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Failed to install hooks!" -ForegroundColor Red
    exit 1
}

# Run pre-commit on all files (optional, for initial setup)
Write-Host ""
Write-Host "Testing hooks on existing files..." -ForegroundColor Yellow
Write-Host "(This may take a few minutes on first run)" -ForegroundColor Gray
pre-commit run --all-files

# Summary
Write-Host ""
Write-Host "=== Git Hooks installed successfully! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Configured Hooks:" -ForegroundColor Cyan
Write-Host "  - commit-msg   : Validates Conventional Commits format" -ForegroundColor White
Write-Host "  - pre-commit   : Runs linters and formatters" -ForegroundColor White
Write-Host "  - pre-push     : Runs fast unit tests" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Make a commit: git commit -m 'feat: test hooks'" -ForegroundColor White
Write-Host "  2. Hooks will run automatically" -ForegroundColor White
Write-Host "  3. Fix any issues they report" -ForegroundColor White
Write-Host ""
Write-Host "To skip hooks (emergency only):" -ForegroundColor Yellow
Write-Host "  git commit --no-verify -m '...'" -ForegroundColor Gray
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  docs/CONVENTIONAL_COMMITS.md" -ForegroundColor White
Write-Host "  .pre-commit-config.yaml" -ForegroundColor White
Write-Host ""
