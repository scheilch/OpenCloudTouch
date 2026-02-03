#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run Backend Unit/Integration Tests with cleanup

.DESCRIPTION
    Runs pytest with coverage, cleans up any leftover processes/ports

.PARAMETER Coverage
    Generate coverage report (default: true)

.PARAMETER Verbose
    Verbose test output (default: false)

.EXAMPLE
    .\scripts\run-backend-tests.ps1
    .\scripts\run-backend-tests.ps1 -Coverage $false -Verbose $true
#>

param(
    [bool]$Coverage = $true,
    [bool]$Verbose = $false
)

$ErrorActionPreference = "Stop"

# Configuration
$RootDir = Join-Path $PSScriptRoot ".."
$BackendDir = Join-Path $RootDir "backend"
$VenvPython = Join-Path (Join-Path $RootDir ".venv") "Scripts\python.exe"
$TestPorts = @(7778, 4173, 8000)  # Ports that might be used in tests

# Colors
function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Write-Error($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }

Write-Info "Starting Backend Test Runner"
Write-Host ""

# Step 1: Cleanup ports before tests
Write-Info "Cleaning up test ports..."
foreach ($port in $TestPorts) {
    try {
        $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($connections) {
            $processIds = $connections | Select-Object -ExpandProperty OwningProcess -Unique
            foreach ($procId in $processIds) {
                Write-Host "  Killing process $procId on port $port" -ForegroundColor Yellow
                Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
            }
        }
    }
    catch {
        # Port already free
    }
}
Start-Sleep -Milliseconds 500
Write-Success "Ports cleaned up"
Write-Host ""

# Step 2: Run pytest
Write-Info "Running pytest..."
Set-Location $BackendDir

$pytestArgs = @()
if ($Verbose) {
    $pytestArgs += "-v"
}
else {
    $pytestArgs += "-q"
}

# Exclude real device tests from default runs
$pytestArgs += "-m"
$pytestArgs += "not real_devices"

if ($Coverage) {
    $pytestArgs += "--cov=src/cloudtouch"
    $pytestArgs += "--cov-report=term-missing"
    $pytestArgs += "--cov-report=html"
}

try {
    & $VenvPython -m pytest @pytestArgs
    $exitCode = $LASTEXITCODE
}
catch {
    Write-Error "Pytest execution failed: $_"
    $exitCode = 1
}

Set-Location $RootDir
Write-Host ""

# Step 3: Cleanup ports after tests
Write-Info "Cleaning up ports after tests..."
foreach ($port in $TestPorts) {
    try {
        $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($connections) {
            $processIds = $connections | Select-Object -ExpandProperty OwningProcess -Unique
            foreach ($procId in $processIds) {
                Write-Host "  Killing leftover process $procId on port $port" -ForegroundColor Yellow
                Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
            }
        }
    }
    catch {
        # Port already free
    }
}
Start-Sleep -Milliseconds 500
Write-Success "Cleanup complete"
Write-Host ""

# Step 4: Report results
Write-Host "========================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Success "Backend Tests PASSED"
    Write-Host "========================================" -ForegroundColor Cyan
    if ($Coverage) {
        Write-Info "Coverage report: $BackendDir\htmlcov\index.html"
    }
    exit 0
}
else {
    Write-Error "Backend Tests FAILED"
    Write-Host "========================================" -ForegroundColor Cyan
    exit $exitCode
}
