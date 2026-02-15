#!/bin/bash
# =============================================================================
# SoundTouch Post-SSH Configuration Script
# =============================================================================
# Dieses Script läuft AUF dem SoundTouch nach SSH-Login
# Kopiere es via SCP oder copy-paste in eine Datei
# =============================================================================

set -e

echo "=== SoundTouch Post-SSH Configuration ==="
echo ""

# Farben (falls Terminal unterstützt)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# OCT Server (anpassen!)
OCT_SERVER="192.168.178.11"
OCT_PORT="7777"
BMX_URL="http://${OCT_SERVER}:${OCT_PORT}/bmx/registry/v1/services"

# -----------------------------------------------------------------------------
# 1. System Info sammeln
# -----------------------------------------------------------------------------
echo "[1/6] System-Informationen..."
echo "---"
echo "Hostname: $(hostname)"
echo "Kernel: $(uname -r)"
echo "Uptime: $(uptime)"
if [ -f /opt/Bose/etc/version.txt ]; then
    echo "Bose Version: $(cat /opt/Bose/etc/version.txt)"
fi
echo "---"
echo ""

# -----------------------------------------------------------------------------
# 2. SSH persistent machen
# -----------------------------------------------------------------------------
echo "[2/6] SSH persistent aktivieren..."
if [ -f /mnt/nv/remote_services ]; then
    echo "  -> Bereits aktiviert"
else
    touch /mnt/nv/remote_services
    echo "  -> Erstellt: /mnt/nv/remote_services"
fi
echo ""

# -----------------------------------------------------------------------------
# 3. Backup erstellen
# -----------------------------------------------------------------------------
echo "[3/6] Backup erstellen..."
BACKUP_DIR="/mnt/nv/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Wichtige Config-Dateien sichern
for file in \
    /opt/Bose/etc/SoundTouchSdkPrivateCfg.xml \
    /opt/Bose/etc/SoundTouchCfg.xml \
    /opt/Bose/etc/BoseApp-*.xml \
    /opt/Bose/etc/Shepherd-*.xml
do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/" 2>/dev/null || true
        echo "  -> $(basename $file)"
    fi
done
echo "  Backup in: $BACKUP_DIR"
echo ""

# -----------------------------------------------------------------------------
# 4. Aktuelle BMX URL anzeigen
# -----------------------------------------------------------------------------
echo "[4/6] Aktuelle BMX Konfiguration..."
if [ -f /opt/Bose/etc/SoundTouchSdkPrivateCfg.xml ]; then
    echo "  Datei: /opt/Bose/etc/SoundTouchSdkPrivateCfg.xml"
    grep -i "bmxRegistryUrl" /opt/Bose/etc/SoundTouchSdkPrivateCfg.xml || echo "  bmxRegistryUrl nicht gefunden"
else
    echo "  WARNUNG: SoundTouchSdkPrivateCfg.xml nicht gefunden!"
fi
echo ""

# -----------------------------------------------------------------------------
# 5. Override prüfen
# -----------------------------------------------------------------------------
echo "[5/6] Override-Mechanismus prüfen..."
if [ -d /mnt/nv ]; then
    echo "  /mnt/nv existiert und ist beschreibbar: $(ls -la /mnt/nv | head -1)"
    
    # Prüfe ob bereits Override existiert
    if [ -f /mnt/nv/SoundTouchSdkPrivateCfg.xml ]; then
        echo "  -> Override bereits vorhanden!"
        grep -i "bmxRegistryUrl" /mnt/nv/SoundTouchSdkPrivateCfg.xml || true
    else
        echo "  -> Kein Override vorhanden"
    fi
else
    echo "  WARNUNG: /mnt/nv nicht gefunden!"
fi
echo ""

# -----------------------------------------------------------------------------
# 6. Netzwerk-Test
# -----------------------------------------------------------------------------
echo "[6/6] Netzwerk-Test zu OCT Server..."
if command -v wget &> /dev/null; then
    if wget -q --spider "http://${OCT_SERVER}:${OCT_PORT}/health" 2>/dev/null; then
        echo "  -> OCT Server erreichbar: http://${OCT_SERVER}:${OCT_PORT}"
    else
        echo "  -> OCT Server NICHT erreichbar (http://${OCT_SERVER}:${OCT_PORT})"
    fi
elif command -v curl &> /dev/null; then
    if curl -s --connect-timeout 5 "http://${OCT_SERVER}:${OCT_PORT}/health" > /dev/null 2>&1; then
        echo "  -> OCT Server erreichbar"
    else
        echo "  -> OCT Server NICHT erreichbar"
    fi
else
    echo "  -> Kein wget/curl verfügbar, überspringe"
fi
echo ""

# -----------------------------------------------------------------------------
# Zusammenfassung
# -----------------------------------------------------------------------------
echo "=== Zusammenfassung ==="
echo ""
echo "SSH persistent: $([ -f /mnt/nv/remote_services ] && echo 'JA' || echo 'NEIN')"
echo "Backup erstellt: $BACKUP_DIR"
echo ""
echo "Nächster Schritt: BMX URL ändern"
echo "  Neue URL: $BMX_URL"
echo ""
echo "Befehl zum Ändern (MANUELL ausführen nach Prüfung):"
echo "  # TODO: Override-Mechanismus implementieren"
echo ""
