#!/usr/bin/env pwsh
# Export container image for deployment to NAS Server
# Creates a portable .tar file that can be imported on any Docker/Podman host

# Configuration
$Tag = "soundtouch-bridge:latest"
$OutputFile = "soundtouch-bridge-image.tar"
$SkipBuild = $false
$NoCache = $true  # Force rebuild

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
        Write-ErrorMsg "Podman not found!"
        exit 1
    }
    Write-Success "Podman found: $podmanVersion"

    # Build image
    if (-not $SkipBuild) {
        Write-Step "Building container image..."
        $buildCmd = "podman build -f ../backend/Dockerfile -t $Tag"
        if ($NoCache) {
            $buildCmd += " --no-cache"
        }
        $buildCmd += " .."
        Invoke-Expression $buildCmd
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
