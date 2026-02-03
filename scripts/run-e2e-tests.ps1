#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Run Cypress E2E tests with backend (mock or real mode)

.DESCRIPTION
    Starts backend on test port (7778), runs Cypress tests, stops backend.
    Supports both mock mode (CT_MOCK_MODE=true) and real device mode.

.PARAMETER MockMode
    Use mock adapters (true) or real devices (false). Default: true

.PARAMETER HeadlessMode
    Run Cypress headless (true) or with GUI (false). Default: true

.EXAMPLE
    .\scripts\run-e2e-tests.ps1 -MockMode $true
    .\scripts\run-e2e-tests.ps1 -MockMode $false -HeadlessMode $false
#>

param(
    [bool]$MockMode = $true,
    [bool]$HeadlessMode = $true
)

$ErrorActionPreference = "Stop"

# Configuration
$TestPort = 7778
$FrontendPort = 4173
$RootDir = Join-Path $PSScriptRoot ".."
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"
$VenvPython = Join-Path (Join-Path $RootDir ".venv") "Scripts\python.exe"

# Colors
function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Write-Error($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }
function Write-Warning($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }

Write-Info "Starting E2E Test Runner"
Write-Info "Mode: $(if ($MockMode) { 'MOCK' } else { 'REAL DEVICES' })"
Write-Info "Headless: $HeadlessMode"
Write-Info "Backend Port: $TestPort"
Write-Info "Frontend Port: $FrontendPort"
Write-Host ""

# Step 1: Check if ports are already in use
try {
    $backendConnection = Test-NetConnection -ComputerName localhost -Port $TestPort -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($backendConnection) {
        Write-Error "Backend port $TestPort is already in use!"
        Write-Info "Kill the process or use a different port."
        exit 1
    }
    
    $frontendConnection = Test-NetConnection -ComputerName localhost -Port $FrontendPort -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($frontendConnection) {
        Write-Error "Frontend port $FrontendPort is already in use!"
        Write-Info "Kill the process: Get-NetTCPConnection -LocalPort $FrontendPort | Select OwningProcess"
        exit 1
    }
}
catch {
    # Test-NetConnection might not be available - continue
}

# Step 2: Start Backend
Write-Info "Starting backend on port $TestPort..."

# Build environment variables for backend process
$backendEnv = @{
    CT_MOCK_MODE = if ($MockMode) { "true" } else { "false" }
    CT_LOG_LEVEL = "INFO"  # INFO logs for debugging
    CT_DB_PATH = "data-local/ct-e2e-test.db"  # Separate test DB
    CT_ALLOW_DANGEROUS_OPERATIONS = "true"  # Allow DELETE endpoint in E2E tests
    PYTHONPATH = Join-Path $BackendDir "src"
}

# Convert to environment block for Start-Process
$envString = ($backendEnv.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join "`n"

# Create a wrapper script to set env vars and start uvicorn
$wrapperScript = @"
`$env:CT_MOCK_MODE = '$($backendEnv.CT_MOCK_MODE)'
`$env:CT_LOG_LEVEL = '$($backendEnv.CT_LOG_LEVEL)'
`$env:CT_DB_PATH = '$($backendEnv.CT_DB_PATH)'
`$env:CT_ALLOW_DANGEROUS_OPERATIONS = '$($backendEnv.CT_ALLOW_DANGEROUS_OPERATIONS)'
`$env:PYTHONPATH = '$($backendEnv.PYTHONPATH)'
Set-Location '$BackendDir'
& '$VenvPython' -m uvicorn cloudtouch.main:app --host localhost --port $TestPort
"@

$wrapperPath = Join-Path $env:TEMP "ct-backend-wrapper.ps1"
$wrapperScript | Out-File -FilePath $wrapperPath -Encoding UTF8

$backendProcess = Start-Process -FilePath "powershell.exe" `
    -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$wrapperPath`"" `
    -WindowStyle Hidden `
    -PassThru `
    -RedirectStandardOutput (Join-Path $env:TEMP "ct-backend-stdout.log") `
    -RedirectStandardError (Join-Path $env:TEMP "ct-backend-stderr.log")

Write-Info "Backend PID: $($backendProcess.Id)"
Write-Info "Waiting for backend to start..."

# Wait for backend health check (max 10 seconds)
$maxAttempts = 20
$attempt = 0
$backendReady = $false

while ($attempt -lt $maxAttempts) {
    Start-Sleep -Milliseconds 500
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$TestPort/health" -Method GET -TimeoutSec 1 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            break
        }
    }
    catch {
        # Backend not ready yet
    }
    $attempt++
}

if (-not $backendReady) {
    Write-Error "Backend failed to start within 10 seconds!"
    Write-Info "Check logs:"
    Write-Host "  stdout: $env:TEMP\ct-backend-stdout.log" -ForegroundColor Yellow
    Write-Host "  stderr: $env:TEMP\ct-backend-stderr.log" -ForegroundColor Yellow
    
    # Kill backend process
    if ($backendProcess -and !$backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id -Force
    }
    exit 1
}

Write-Success "Backend started successfully"
Write-Host ""

# Step 3: Build Frontend
Write-Info "Building frontend (production build)..."
try {
    Set-Location $FrontendDir
    
    $buildProcess = Start-Process -FilePath "npm" -ArgumentList "run", "build" -Wait -NoNewWindow -PassThru
    if ($buildProcess.ExitCode -ne 0) {
        throw "Frontend build failed"
    }
    
    Write-Success "Frontend built successfully"
}
catch {
    Write-Error "Failed to build frontend: $_"
    Set-Location $RootDir
    
    # Cleanup: Stop backend
    if ($backendProcess -and !$backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id -Force
    }
    exit 1
}
Write-Host ""

# Step 4: Start Frontend Preview Server
Write-Info "Starting frontend preview server on port $FrontendPort..."
$frontendProcess = Start-Process -FilePath "npm" -ArgumentList "run", "preview" `
    -WorkingDirectory $FrontendDir `
    -WindowStyle Hidden `
    -PassThru `
    -RedirectStandardOutput (Join-Path $env:TEMP "ct-frontend-stdout.log") `
    -RedirectStandardError (Join-Path $env:TEMP "ct-frontend-stderr.log")

Write-Info "Frontend PID: $($frontendProcess.Id)"
Write-Info "Waiting for frontend to start..."

# Wait for frontend (max 10 seconds)
$attempt = 0
$frontendReady = $false

while ($attempt -lt 20) {
    Start-Sleep -Milliseconds 500
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$FrontendPort" -Method GET -TimeoutSec 1 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            $frontendReady = $true
            break
        }
    }
    catch {
        # Frontend not ready yet
    }
    $attempt++
}

if (-not $frontendReady) {
    Write-Error "Frontend failed to start within 10 seconds!"
    Write-Info "Check logs:"
    Write-Host "  stdout: $env:TEMP\ct-frontend-stdout.log" -ForegroundColor Yellow
    Write-Host "  stderr: $env:TEMP\ct-frontend-stderr.log" -ForegroundColor Yellow
    
    # Cleanup
    if ($frontendProcess -and !$frontendProcess.HasExited) {
        Stop-Process -Id $frontendProcess.Id -Force
    }
    if ($backendProcess -and !$backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id -Force
    }
    exit 1
}

Write-Success "Frontend started successfully"
Write-Host ""

# Step 5: Run Cypress Tests
Write-Info "Running Cypress E2E tests..."
$cypressExitCode = 0

try {
    Set-Location $FrontendDir
    
    # Set Cypress env var for API URL
    $env:CYPRESS_API_URL = "http://localhost:$TestPort/api"
    
    if ($HeadlessMode) {
        $process = Start-Process -FilePath "npm" -ArgumentList "run", "cypress:run" -Wait -NoNewWindow -PassThru
    }
    else {
        $process = Start-Process -FilePath "npm" -ArgumentList "run", "cypress:open" -Wait -NoNewWindow -PassThru
    }
    
    $cypressExitCode = $process.ExitCode
}
catch {
    Write-Error "Failed to run Cypress tests: $_"
    $cypressExitCode = 1
}
finally {
    Set-Location $PSScriptRoot\..
}

Write-Host ""

# Step 6: Stop Backend and Frontend
Write-Info "Stopping backend (PID: $($backendProcess.Id))..."
if ($backendProcess -and !$backendProcess.HasExited) {
    Stop-Process -Id $backendProcess.Id -Force
}

Write-Info "Stopping frontend (PID: $($frontendProcess.Id))..."
if ($frontendProcess -and !$frontendProcess.HasExited) {
    Stop-Process -Id $frontendProcess.Id -Force
}

Start-Sleep -Milliseconds 500
Write-Success "Backend and Frontend stopped"
Write-Host ""

# Step 6.5: Cleanup Ports (ensure nothing is left running)
Write-Info "Cleaning up ports $TestPort and $FrontendPort..."
$portsToClean = @($TestPort, $FrontendPort)
foreach ($port in $portsToClean) {
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
Write-Success "Ports cleaned up"
Write-Host ""

# Step 7: Clean up test DB and wrapper script
if ($MockMode) {
    $testDb = Join-Path (Join-Path $RootDir "data-local") "ct-e2e-test.db"
    if (Test-Path $testDb) {
        Remove-Item $testDb -Force
        Write-Info "Cleaned up test database"
    }
}

# Clean up backend wrapper script
$wrapperPath = Join-Path $env:TEMP "ct-backend-wrapper.ps1"
if (Test-Path $wrapperPath) {
    Remove-Item $wrapperPath -Force -ErrorAction SilentlyContinue
}

# Step 8: Report Results
Write-Host "========================================" -ForegroundColor Cyan
if ($cypressExitCode -eq 0) {
    Write-Success "E2E Tests PASSED"
    Write-Host "========================================" -ForegroundColor Cyan
    exit 0
}
else {
    Write-Error "E2E Tests FAILED"
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Info "Run with -HeadlessMode `$false to debug interactively"
    exit $cypressExitCode
}
