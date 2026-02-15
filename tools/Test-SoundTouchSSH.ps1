<#
.SYNOPSIS
    Testet SSH-Verbindung zum SoundTouch.

.PARAMETER IP
    IP-Adresse des SoundTouch (Standard: 192.168.178.79)

.EXAMPLE
    .\Test-SoundTouchSSH.ps1 -IP 192.168.178.79
#>

param(
    [string]$IP = "192.168.178.79"
)

Write-Host "=== SoundTouch SSH Test ===" -ForegroundColor Cyan
Write-Host ""

# 1. Ping Test
Write-Host "[1/3] Ping Test..." -ForegroundColor Yellow
$ping = Test-Connection -ComputerName $IP -Count 1 -Quiet
if ($ping) {
    Write-Host "      OK - Host erreichbar" -ForegroundColor Green
} else {
    Write-Host "      FEHLER - Host nicht erreichbar!" -ForegroundColor Red
    Write-Host "      Prüfe:" -ForegroundColor Yellow
    Write-Host "        - SoundTouch eingeschaltet?"
    Write-Host "        - Im gleichen Netzwerk?"
    Write-Host "        - Richtige IP? (Prüfe in SoundTouch App oder Router)"
    exit 1
}

# 2. Port 22 Test
Write-Host "[2/3] SSH Port Test (22)..." -ForegroundColor Yellow
try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $tcp.Connect($IP, 22)
    $tcp.Close()
    Write-Host "      OK - Port 22 offen" -ForegroundColor Green
} catch {
    Write-Host "      FEHLER - Port 22 nicht erreichbar!" -ForegroundColor Red
    Write-Host "      SSH ist nicht aktiviert. Prüfe:" -ForegroundColor Yellow
    Write-Host "        - USB-Stick mit 'remote_services' Datei eingesteckt?"
    Write-Host "        - SoundTouch nach USB-Stick neu gestartet?"
    Write-Host "        - Setup-B Port verwendet (nicht USB-A)?"
    exit 1
}

# 3. Port 17000 Test (Telnet)
Write-Host "[3/3] Telnet Port Test (17000)..." -ForegroundColor Yellow
try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $tcp.Connect($IP, 17000)
    $tcp.Close()
    Write-Host "      OK - Port 17000 offen (Telnet)" -ForegroundColor Green
} catch {
    Write-Host "      INFO - Port 17000 nicht offen (optional)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== Alle Tests bestanden! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Jetzt SSH verbinden:" -ForegroundColor Cyan
Write-Host "  ssh root@$IP" -ForegroundColor White
Write-Host ""
Write-Host "Oder mit PowerShell:" -ForegroundColor Cyan
Write-Host "  ssh root@$IP 'uname -a'" -ForegroundColor White
Write-Host ""
