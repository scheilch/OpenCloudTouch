#!/usr/bin/env pwsh
# Build and run SoundTouch Bridge in Podman container
# Usage: .\run-container.ps1 [-Port 7777] [-Tag soundtouch-bridge:latest] [-ManualIPs "192.168.1.100,192.168.1.101"] [-NoBuild]
#
# IMPORTANT: On Windows, SSDP/mDNS discovery doesn't work in containers due to VM network isolation.
#            Use -ManualIPs to specify your Bose device IPs directly.

param(
    [string]$Tag = "soundtouch-bridge:latest",
    [int]$Port = 7777,
    [string]$DataDir = ".\data",
    [string]$ManualIPs = "",
    [switch]$NoBuild
)

function Write-Step {
    param([string]$Message)
    Write-Host "[>] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "    $Message" -ForegroundColor Gray
}

$script:ContainerName = "soundtouch-bridge-dev"
$script:CleanupDone = $false

function Cleanup {
    if ($script:CleanupDone) {
        return
    }
    $script:CleanupDone = $true
    
    Write-Host ""
    Write-Step "Cleaning up..."
    
    $running = podman ps -q -f name=$script:ContainerName 2>$null
    if ($running) {
        Write-Info "Stopping container..."
        podman stop $script:ContainerName 2>&1 | Out-Null
    }
    
    $exists = podman ps -aq -f name=$script:ContainerName 2>$null
    if ($exists) {
        Write-Info "Removing container..."
        podman rm $script:ContainerName 2>&1 | Out-Null
    }
    
    Write-Success "Cleanup complete"
}

# Main execution
try {
    Write-Host ""
    Write-Host "=== SoundTouch Bridge - Container Deployment ===" -ForegroundColor Yellow
    Write-Host ""

    Write-Step "Checking Podman installation..."
    $podmanVersion = podman --version 2>$null
    if (-not $podmanVersion) {
        Write-ErrorMsg "Podman is not installed or not in PATH"
        Write-Info "Please install Podman from: https://podman.io/"
        exit 1
    }
    Write-Success "Podman found: $podmanVersion"

    Write-Step "Preparing data directory..."
    $DataDir = Resolve-Path -Path $DataDir -ErrorAction SilentlyContinue
    if (-not $DataDir) {
        $DataDir = Join-Path $PSScriptRoot "data"
        New-Item -ItemType Directory -Path $DataDir -Force | Out-Null
    }
    Write-Success "Data directory: $DataDir"

    if (-not $NoBuild) {
        Write-Step "Building container image..."
        Write-Info "Tag: $Tag"
        
        $buildOutput = podman build -f ../backend/Dockerfile -t $Tag .. 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-ErrorMsg "Build failed!"
            Write-Host $buildOutput
            exit 1
        }
        Write-Success "Image built successfully"
    } else {
        Write-Info "Skipping build (using existing image: $Tag)"
    }

    Cleanup

    Write-Step "Starting container..."
    Write-Info "Container name: $script:ContainerName"
    Write-Info "Port: http://localhost:${Port}"
    Write-Info "Data volume: ${DataDir}:/data"
    if ($ManualIPs) {
        Write-Info "Manual device IPs: $ManualIPs"
        Write-Host ""
        Write-Host "NOTE: Container network isolation on Windows prevents SSDP/mDNS discovery." -ForegroundColor Yellow
        Write-Host "      Using manual IPs instead." -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "WARNING: SSDP/mDNS discovery may not work in container on Windows!" -ForegroundColor Yellow
        Write-Host "         Consider using -ManualIPs parameter (e.g., '192.168.1.100,192.168.1.101')" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the container" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor Gray
    Write-Host ""

    # Build podman command
    $podmanArgs = @(
        "run"
        "--name", $script:ContainerName
        "--rm"
        "-p", "${Port}:7777"
        "-v", "${DataDir}:/data"
        "-e", "CT_LOG_LEVEL=INFO"
        "-e", "CT_LOG_FORMAT=text"
    )
    
    if ($ManualIPs) {
        $podmanArgs += "-e"
        $podmanArgs += "CT_MANUAL_DEVICE_IPS=$ManualIPs"
        $podmanArgs += "-e"
        $podmanArgs += "CT_DISCOVERY_ENABLED=false"
    }
    
    $podmanArgs += $Tag

    # Run container in foreground - Ctrl+C will stop it
    try {
        & podman $podmanArgs
    } catch {
        # Ignore errors on Ctrl+C
    }

    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Gray
    
} catch {
    Write-ErrorMsg "An error occurred: $_"
    exit 1
} finally {
    Cleanup
}

Write-Host ""
Write-Host "=== Container stopped ===" -ForegroundColor Yellow
Write-Host ""
