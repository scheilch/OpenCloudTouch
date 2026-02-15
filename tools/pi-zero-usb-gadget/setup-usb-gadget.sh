#!/bin/bash
# Setup-Script für Pi Zero 2 W USB Gadget
# Macht den Pi zu einem USB-Stick mit remote_services Datei

set -e

echo "=== Pi Zero USB Gadget Setup ==="

# 1. USB-Stick Image erstellen (1MB FAT32)
echo "[1/4] Erstelle USB-Stick Image..."
dd if=/dev/zero of=/home/pi/usbstick.img bs=1M count=1
mkfs.vfat /home/pi/usbstick.img

# 2. remote_services Datei erstellen
echo "[2/4] Erstelle remote_services Datei..."
mkdir -p /mnt/usb
mount -o loop /home/pi/usbstick.img /mnt/usb
touch /mnt/usb/remote_services
umount /mnt/usb

# 3. Gadget-Script erstellen
echo "[3/4] Erstelle Gadget-Script..."
cat << 'EOF' > /usr/local/bin/start-usb-gadget.sh
#!/bin/bash
# Warte bis System bereit
sleep 5
# Lade USB Mass Storage Gadget
modprobe g_mass_storage file=/home/pi/usbstick.img stall=0 removable=1 ro=0
EOF

chmod +x /usr/local/bin/start-usb-gadget.sh

# 4. Autostart konfigurieren
echo "[4/4] Konfiguriere Autostart..."
if ! grep -q "start-usb-gadget.sh" /etc/rc.local 2>/dev/null; then
    # rc.local existiert möglicherweise nicht in neueren Versionen
    cat << 'EOF' > /etc/systemd/system/usb-gadget.service
[Unit]
Description=USB Gadget Mass Storage
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/start-usb-gadget.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    systemctl enable usb-gadget.service
fi

echo ""
echo "=== Setup abgeschlossen ==="
echo ""
echo "Nächste Schritte:"
echo "1. Pi ausschalten: sudo shutdown -h now"
echo "2. Micro-USB Kabel an USB-OTG Port (NICHT PWR!)"
echo "3. Anderes Ende an SoundTouch Setup-B Port"
echo "4. Warten bis Pi gebootet (~30s)"
echo "5. SoundTouch neu starten"
echo "6. SSH verbinden: ssh root@<SOUNDTOUCH-IP>"
echo ""
