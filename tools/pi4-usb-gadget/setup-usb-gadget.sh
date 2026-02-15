#!/bin/bash
# =============================================================================
# Raspberry Pi 4 USB Mass Storage Gadget Setup
# =============================================================================
# This script configures a Raspberry Pi 4 to act as a USB mass storage device
# presenting a virtual "USB stick" with an empty 'remote_services' file.
# This allows enabling telnet on Bose SoundTouch devices.
#
# Usage: sudo ./setup-usb-gadget.sh
# =============================================================================

set -e

echo "=========================================="
echo "Pi 4 USB Mass Storage Gadget Setup"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Please run as root (sudo ./setup-usb-gadget.sh)"
    exit 1
fi

# Check if this is a Pi 4
if ! grep -q "Raspberry Pi 4" /proc/device-tree/model 2>/dev/null; then
    echo "WARNING: This doesn't appear to be a Raspberry Pi 4"
    echo "USB Gadget mode only works on Pi 4 (USB-C) or Pi Zero (Micro-USB)"
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "[1/5] Enabling dwc2 overlay in config.txt..."
if ! grep -q "dtoverlay=dwc2" /boot/firmware/config.txt 2>/dev/null; then
    echo "dtoverlay=dwc2" >> /boot/firmware/config.txt
    echo "  Added: dtoverlay=dwc2"
else
    echo "  Already configured"
fi

# Also check old location
if [ -f /boot/config.txt ] && ! grep -q "dtoverlay=dwc2" /boot/config.txt; then
    echo "dtoverlay=dwc2" >> /boot/config.txt
fi

echo ""
echo "[2/5] Adding dwc2 and g_mass_storage to modules..."
if ! grep -q "^dwc2" /etc/modules; then
    echo "dwc2" >> /etc/modules
    echo "  Added: dwc2"
else
    echo "  dwc2 already in modules"
fi

if ! grep -q "^g_mass_storage" /etc/modules; then
    echo "g_mass_storage" >> /etc/modules
    echo "  Added: g_mass_storage"
else
    echo "  g_mass_storage already in modules"
fi

echo ""
echo "[3/5] Creating virtual USB disk image..."
DISK_IMAGE="/home/pi/usb_disk.img"
MOUNT_POINT="/mnt/usb_gadget"

# Create 16MB disk image (minimum size, we only need one empty file)
if [ ! -f "$DISK_IMAGE" ]; then
    dd if=/dev/zero of="$DISK_IMAGE" bs=1M count=16
    echo "  Created 16MB disk image"
    
    # Format as FAT32
    mkfs.vfat -F 16 "$DISK_IMAGE"
    echo "  Formatted as FAT"
else
    echo "  Disk image already exists"
fi

echo ""
echo "[4/5] Creating remote_services file on virtual disk..."
mkdir -p "$MOUNT_POINT"
mount -o loop "$DISK_IMAGE" "$MOUNT_POINT"

# Create empty remote_services file (this enables telnet on SoundTouch)
touch "$MOUNT_POINT/remote_services"
echo "  Created empty 'remote_services' file"

# Verify
ls -la "$MOUNT_POINT/"

# Unmount
umount "$MOUNT_POINT"
echo "  Unmounted virtual disk"

echo ""
echo "[5/5] Creating systemd service for USB gadget..."
cat > /etc/systemd/system/usb-gadget.service << 'EOF'
[Unit]
Description=USB Mass Storage Gadget
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/sbin/modprobe g_mass_storage file=/home/pi/usb_disk.img stall=0 removable=1
ExecStop=/sbin/modprobe -r g_mass_storage

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable usb-gadget.service
echo "  Created and enabled usb-gadget.service"

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. sudo reboot"
echo "2. Connect Pi 4 USB-C port to SoundTouch Micro-USB port"
echo "3. Power on Pi, wait 30s, then power cycle SoundTouch"
echo "4. telnet 192.168.178.79 (login: root, no password)"
echo "5. Run: rw"
echo "6. Edit: vi /opt/Bose/etc/SoundTouchSdkPrivateCfg.xml"
echo "7. Change bmxRegistryUrl to: http://192.168.178.11:7777/bmx/registry/v1/services"
echo "8. Run: reboot"
echo ""
