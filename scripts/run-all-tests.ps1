#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run ALL test suites (Backend, Frontend Unit, E2E) with cleanup

.DESCRIPTION
    Runs all test suites in sequence:
    1. Backend Unit/Integration Tests (pytest)
    2. Frontend Unit Tests (vitest)
    3. E2E Tests (Cypress)

.PARAMETER SkipBackend
    Skip backend tests (default: false)

.PARAMETER SkipFrontend
    Skip frontend unit tests (default: false)

.PARAMETER SkipE2E
    Skip E2E tests (default: false)

.PARAMETER MockMode
    Use mock adapters for E2E tests (default: true)

.EXAMPLE
    .\scripts\run-all-tests.ps1
    .\scripts\run-all-tests.ps1 -SkipBackend $true
    .\scripts\run-all-tests.ps1 -MockMode $false
#>

param(
    [bool]$SkipBackend = $false,
    [bool]$SkipFrontend = $false,
    [bool]$SkipE2E = $false,
    [bool]$MockMode = $true
)

$ErrorActionPreference = "Stop"
$RootDir = Join-Path $PSScriptRoot ".."

# Colors
function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Write-Error($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }
function Write-Section($msg) { 
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host $msg -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""
}

$results = @{
    Backend = $null
    Frontend = $null
    E2E = $null
}

Write-Section "CloudTouch - Full Test Suite Runner"

# 1. Backend Tests
if (-not $SkipBackend) {
    Write-Section "1/3: Backend Unit/Integration Tests (pytest)"
    try {
        & "$PSScriptRoot\run-backend-tests.ps1" -Coverage $true
        if ($LASTEXITCODE -eq 0) {
            $results.Backend = "PASSED"
        }
        else {
            $results.Backend = "FAILED"
        }
    }
    catch {
        Write-Error "Backend tests crashed: $_"
        $results.Backend = "CRASHED"
    }
}
else {
    Write-Info "Skipping backend tests"
    $results.Backend = "SKIPPED"
}

# 2. Frontend Unit Tests
if (-not $SkipFrontend) {
    Write-Section "2/3: Frontend Unit Tests (vitest)"
    try {
        & "$PSScriptRoot\run-frontend-tests.ps1" -Coverage $true
        if ($LASTEXITCODE -eq 0) {
            $results.Frontend = "PASSED"
        }
        else {
            $results.Frontend = "FAILED"
        }
    }
    catch {
        Write-Error "Frontend tests crashed: $_"
        $results.Frontend = "CRASHED"
    }
}
else {
    Write-Info "Skipping frontend unit tests"
    $results.Frontend = "SKIPPED"
}

# 3. E2E Tests
if (-not $SkipE2E) {
    Write-Section "3/3: E2E Tests (Cypress)"
    try {
        Set-Location (Join-Path $RootDir "frontend")
        if ($MockMode) {
            $process = Start-Process -FilePath "npm" -ArgumentList "run", "test:e2e:mock" -Wait -NoNewWindow -PassThru
        }
        else {
            $process = Start-Process -FilePath "npm" -ArgumentList "run", "test:e2e:real" -Wait -NoNewWindow -PassThru
        }
        
        if ($process.ExitCode -eq 0) {
            $results.E2E = "PASSED"
        }
        else {
            $results.E2E = "FAILED"
        }
    }
    catch {
        Write-Error "E2E tests crashed: $_"
        $results.E2E = "CRASHED"
    }
    finally {
        Set-Location $RootDir
    }
}
else {
    Write-Info "Skipping E2E tests"
    $results.E2E = "SKIPPED"
}

# Final Summary
Write-Section "TEST SUMMARY"
Write-Host "Backend Tests:  " -NoNewline
switch ($results.Backend) {
    "PASSED" { Write-Host "✅ PASSED" -ForegroundColor Green }
    "FAILED" { Write-Host "❌ FAILED" -ForegroundColor Red }
    "CRASHED" { Write-Host "💥 CRASHED" -ForegroundColor Red }
    "SKIPPED" { Write-Host "⏭️  SKIPPED" -ForegroundColor Yellow }
}

Write-Host "Frontend Tests: " -NoNewline
switch ($results.Frontend) {
    "PASSED" { Write-Host "✅ PASSED" -ForegroundColor Green }
    "FAILED" { Write-Host "❌ FAILED" -ForegroundColor Red }
    "CRASHED" { Write-Host "💥 CRASHED" -ForegroundColor Red }
    "SKIPPED" { Write-Host "⏭️  SKIPPED" -ForegroundColor Yellow }
}

Write-Host "E2E Tests:      " -NoNewline
switch ($results.E2E) {
    "PASSED" { Write-Host "✅ PASSED" -ForegroundColor Green }
    "FAILED" { Write-Host "❌ FAILED" -ForegroundColor Red }
    "CRASHED" { Write-Host "💥 CRASHED" -ForegroundColor Red }
    "SKIPPED" { Write-Host "⏭️  SKIPPED" -ForegroundColor Yellow }
}

Write-Host ""

# Exit code
$allPassed = ($results.Backend -in @("PASSED", "SKIPPED")) -and 
             ($results.Frontend -in @("PASSED", "SKIPPED")) -and 
             ($results.E2E -in @("PASSED", "SKIPPED"))

if ($allPassed) {
    Write-Success "All test suites passed! 🎉"
    exit 0
}
else {
    Write-Error "Some test suites failed!"
    exit 1
}
