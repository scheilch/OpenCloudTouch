#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run Frontend Unit Tests (Vitest) with cleanup

.DESCRIPTION
    Runs vitest unit tests, cleans up any leftover processes/ports

.PARAMETER Coverage
    Generate coverage report (default: true)

.PARAMETER UI
    Open Vitest UI (default: false)

.EXAMPLE
    .\scripts\run-frontend-tests.ps1
    .\scripts\run-frontend-tests.ps1 -Coverage $true -UI $false
#>

param(
    [bool]$Coverage = $true,
    [bool]$UI = $false
)

$ErrorActionPreference = "Stop"

# Configuration
$RootDir = Join-Path $PSScriptRoot ".."
$FrontendDir = Join-Path $RootDir "frontend"
$TestPorts = @(5173, 4173)  # Vite dev/preview ports

# Colors
function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Write-Error($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }

Write-Info "Starting Frontend Test Runner (Vitest)"
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

# Step 2: Run vitest
Write-Info "Running vitest..."
Set-Location $FrontendDir

if ($UI) {
    $npmScript = "test:ui"
}
elseif ($Coverage) {
    $npmScript = "test:coverage"
}
else {
    $npmScript = "test"
}

try {
    $process = Start-Process -FilePath "npm" -ArgumentList "run", $npmScript -Wait -NoNewWindow -PassThru
    $exitCode = $process.ExitCode
}
catch {
    Write-Error "Vitest execution failed: $_"
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
    Write-Success "Frontend Tests PASSED"
    Write-Host "========================================" -ForegroundColor Cyan
    if ($Coverage) {
        Write-Info "Coverage report: $FrontendDir\coverage\index.html"
    }
    exit 0
}
else {
    Write-Error "Frontend Tests FAILED"
    Write-Host "========================================" -ForegroundColor Cyan
    exit $exitCode
}
