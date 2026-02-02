#!/usr/bin/env pwsh
# Clear the SoundTouch Bridge database on NAS Server

param(
    [string]$serverHost = "remotehost",
    [string]$serverUser = "user",
    [string]$DataPath = "/mnt/Docker/soundtouch-bridge/data",
    [string]$ContainerName = "soundtouch-bridge"
)

Write-Host ""
Write-Host "=== Clear SoundTouch Bridge Database ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "Target: $serverUser@$serverHost" -ForegroundColor White
Write-Host "Database: $DataPath/ct.db" -ForegroundColor White
Write-Host ""

$confirmation = Read-Host "Are you sure you want to delete the database? (yes/no)"

if ($confirmation -ne "yes") {
    Write-Host "Cancelled." -ForegroundColor Gray
    exit 0
}

Write-Host "[>] Clearing database..." -ForegroundColor Cyan

$clearScript = @"
#!/bin/bash
set -e
DataPath="$DataPath"
ContainerName="$ContainerName"

if [ -f "`${DataPath}/ct.db" ]; then
    rm -f "`${DataPath}/ct.db"
    echo "[OK] Database deleted: `${DataPath}/ct.db"
else
    echo "[INFO] Database not found (already empty)"
fi

echo "[>] Restarting container..."
docker restart "`${ContainerName}"
echo "[OK] Container restarted: `${ContainerName}"
"@

$clearScript = $clearScript -replace "`r`n", "`n"
$clearScript | ssh "${serverUser}@${serverHost}" "bash -s"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[OK] Database cleared and container restarted!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access the app at: http://${serverHost}:7777" -ForegroundColor Cyan
    Write-Host "You should now see the empty state with 'Keine Geräte gefunden'" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "[ERROR] Failed to clear database or restart container" -ForegroundColor Red
    exit 1
}
