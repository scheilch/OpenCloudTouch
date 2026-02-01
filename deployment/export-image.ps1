#!/usr/bin/env pwsh
# Export container image for deployment to NAS Server
# Creates a portable .tar file that can be imported on any Docker/Podman host

param(
    [switch]$SkipBuild,
    [switch]$NoCache,
    [switch]$Verbose
)

# Configuration
$Tag = "cloudtouch:latest"
$OutputFile = "cloudtouch-image.tar"

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

try {
    Write-Host ""
    Write-Host "=== SoundTouch Bridge - Image Export ===" -ForegroundColor Yellow
    Write-Host ""

    # Check podman
    Write-Step "Checking Podman installation..."
    $podmanVersion = podman --version 2>$null
    if (-not $podmanVersion) {
        Write-ErrorMsg "Podman not found! Install from https://podman.io"
        exit 1
    }
    Write-Success "Podman found: $podmanVersion"
    
    # Check if Podman Machine is running (Windows/macOS)
    Write-Step "Checking Podman Machine status..."
    $machineStatus = podman machine inspect --format='{{.State}}' 2>$null
    if ($LASTEXITCODE -eq 0) {
        # Machine exists
        if ($machineStatus -ne "running") {
            Write-Host "    Podman Machine is stopped, starting..." -ForegroundColor Yellow
            podman machine start
            if ($LASTEXITCODE -ne 0) {
                Write-ErrorMsg "Failed to start Podman Machine!"
                exit 1
            }
            Write-Success "Podman Machine started"
        } else {
            Write-Success "Podman Machine is running"
        }
    } else {
        Write-Host "    Podman Machine not found (using native Podman)" -ForegroundColor Gray
    }

    # Build image
    if (-not $SkipBuild) {
        Write-Step "Building container image..."
        
        # Ensure we're in project root
        $projectRoot = Split-Path $PSScriptRoot -Parent
        Push-Location $projectRoot
        
        $buildCmd = "podman build -f ./Dockerfile -t $Tag"
        if ($NoCache) {
            $buildCmd += " --no-cache"
            Write-Host "    Using --no-cache (full rebuild)" -ForegroundColor Gray
        }
        if ($Verbose) {
            $buildCmd += " --progress=plain"
            Write-Host "    Verbose build output enabled" -ForegroundColor Gray
        }
        $buildCmd += " ."
        Write-Host "    Working directory: $projectRoot" -ForegroundColor Gray
        Write-Host "    Command: $buildCmd" -ForegroundColor Gray
        Invoke-Expression $buildCmd
        
        Pop-Location
        
        if ($LASTEXITCODE -ne 0) {
            Write-ErrorMsg "Build failed!"
            exit 1
        }
        Write-Success "Image built: $Tag"
    } else {
        Write-Step "Skipping build (using existing image)"
    }

    # Export image
    Write-Step "Exporting image to $OutputFile..."
    podman save -o $OutputFile $Tag
    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Export failed!"
        exit 1
    }

    $fileSize = (Get-Item $OutputFile).Length / 1MB
    Write-Success "Image exported: $OutputFile ($([math]::Round($fileSize, 2)) MB)"

    Write-Host ""
    Write-Host "=== Next Steps ===" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Transfer the image to NAS Server:" -ForegroundColor White
    Write-Host "   scp $OutputFile user@server:/mnt/pool/docker-images/" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. On NAS Server, import and run:" -ForegroundColor White
    Write-Host "   docker load -i /mnt/pool/docker-images/$OutputFile" -ForegroundColor Gray
    Write-Host "   docker run -d --name soundtouch-bridge --network host -v /mnt/pool/stb-data:/data $Tag" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Or use the deploy-to-server.ps1 script for automation" -ForegroundColor White
    Write-Host ""

} catch {
    Write-ErrorMsg "An error occurred: $_"
    exit 1
}
