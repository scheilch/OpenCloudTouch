<#
.SYNOPSIS
    Bereitet einen USB-Stick für SoundTouch SSH-Aktivierung vor.

.DESCRIPTION
    - Formatiert USB-Stick als FAT32
    - Erstellt leere 'remote_services' Datei
    - Verifiziert korrekte Erstellung

.PARAMETER DriveLetter
    Laufwerksbuchstabe des USB-Sticks (z.B. E, F, G)

.EXAMPLE
    .\Prepare-SoundTouchUSB.ps1 -DriveLetter E
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidatePattern('^[A-Z]$')]
    [string]$DriveLetter
)

$ErrorActionPreference = "Stop"

Write-Host "=== SoundTouch USB-Stick Vorbereitung ===" -ForegroundColor Cyan
Write-Host ""

# Prüfe ob Laufwerk existiert
$volume = Get-Volume -DriveLetter $DriveLetter -ErrorAction SilentlyContinue
if (-not $volume) {
    Write-Host "FEHLER: Laufwerk ${DriveLetter}: nicht gefunden!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verfügbare Laufwerke:" -ForegroundColor Yellow
    Get-Volume | Where-Object { $_.DriveLetter } | Format-Table DriveLetter, FileSystemLabel, Size, FileSystem
    exit 1
}

Write-Host "Gefunden: ${DriveLetter}: ($($volume.FileSystemLabel)) - $([math]::Round($volume.Size / 1GB, 2)) GB" -ForegroundColor Green
Write-Host ""

# Warnung
Write-Host "WARNUNG: Alle Daten auf ${DriveLetter}: werden GELÖSCHT!" -ForegroundColor Red
$confirm = Read-Host "Fortfahren? (j/n)"
if ($confirm -ne "j") {
    Write-Host "Abgebrochen." -ForegroundColor Yellow
    exit 0
}

Write-Host ""

# 1. Formatieren
Write-Host "[1/3] Formatiere als FAT32..." -ForegroundColor Yellow
Format-Volume -DriveLetter $DriveLetter -FileSystem FAT32 -NewFileSystemLabel "BOSE" -Confirm:$false | Out-Null
Write-Host "      OK" -ForegroundColor Green

# 2. remote_services Datei erstellen
Write-Host "[2/3] Erstelle remote_services Datei..." -ForegroundColor Yellow
$filePath = "${DriveLetter}:\remote_services"
New-Item -Path $filePath -ItemType File -Force | Out-Null
Write-Host "      OK" -ForegroundColor Green

# 3. Verifizieren
Write-Host "[3/3] Verifiziere..." -ForegroundColor Yellow
$files = Get-ChildItem "${DriveLetter}:\" -Force
$remoteServicesFile = $files | Where-Object { $_.Name -eq "remote_services" }

if ($remoteServicesFile) {
    Write-Host "      OK - Datei gefunden: $($remoteServicesFile.Name)" -ForegroundColor Green
} else {
    Write-Host "      FEHLER: remote_services nicht gefunden!" -ForegroundColor Red
    Write-Host "      Gefundene Dateien:" -ForegroundColor Yellow
    $files | ForEach-Object { Write-Host "        - $($_.Name)" }
    exit 1
}

Write-Host ""
Write-Host "=== USB-Stick bereit! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Nächste Schritte:" -ForegroundColor Cyan
Write-Host "1. USB-Stick sicher auswerfen"
Write-Host "2. USB-C Adapter an USB-Stick stecken"
Write-Host "3. SoundTouch AUSSCHALTEN"
Write-Host "4. Micro-USB in SoundTouch 'Setup-B' Port"
Write-Host "5. SoundTouch EINSCHALTEN"
Write-Host "6. 60 Sekunden warten"
Write-Host "7. SSH: ssh root@<SOUNDTOUCH-IP>"
Write-Host ""
