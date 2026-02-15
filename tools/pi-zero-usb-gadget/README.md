# Raspberry Pi Zero 2 W USB Gadget für SoundTouch SSH

Verwandelt den Pi Zero 2 W in einen USB-Stick mit `remote_services` Datei, um SSH auf dem SoundTouch zu aktivieren.

## Materialliste

| Teil | Preis ca. | Link-Beispiel |
|------|-----------|---------------|
| Raspberry Pi Zero 2 W | ~18€ | [BerryBase](https://www.berrybase.de/raspberry-pi-zero-2-w) |
| Micro-SD Karte (≥8GB) | ~5€ | Jede Class 10 |
| Micro-USB Datenkabel | ~3€ | WICHTIG: Muss Daten können! |

**Optional für Setup:**
- Micro-USB OTG Adapter + USB-Tastatur (für Ersteinrichtung ohne WLAN)
- Oder: USB-Ethernet Adapter

## Pi Zero 2 W Ports

```
┌─────────────────────────────────────┐
│  [Mini-HDMI]  [USB-OTG]  [PWR]     │
│                  ↑         ↑       │
│                DATA      POWER     │
└─────────────────────────────────────┘

USB-OTG Port (links) → An SoundTouch anschließen!
PWR Port (rechts)    → Nur für Stromversorgung
```

## Setup

### 1. SD-Karte vorbereiten

```powershell
# Raspberry Pi Imager herunterladen und installieren
# https://www.raspberrypi.com/software/

# Image: Raspberry Pi OS Lite (64-bit)
# Einstellungen (Zahnrad):
#   - Hostname: pizero
#   - SSH aktivieren
#   - WLAN konfigurieren (SSID + Passwort)
#   - Username/Passwort setzen
```

### 2. USB Gadget Mode aktivieren

Nach dem Flashen, SD-Karte wieder einlegen und `boot` Partition öffnen:

**config.txt** - Am Ende hinzufügen:
```
dtoverlay=dwc2
```

**cmdline.txt** - Nach `rootwait` einfügen (EINE Zeile, Leerzeichen!):
```
modules-load=dwc2,g_mass_storage
```

### 3. USB-Stick Image erstellen

Auf dem Pi (nach erstem Boot via WLAN/SSH):

```bash
# SSH verbinden
ssh pi@pizero.local

# 1MB Image für virtuellen USB-Stick erstellen
sudo dd if=/dev/zero of=/home/pi/usbstick.img bs=1M count=1
sudo mkfs.vfat /home/pi/usbstick.img

# Image mounten und remote_services Datei erstellen
sudo mkdir -p /mnt/usb
sudo mount -o loop /home/pi/usbstick.img /mnt/usb
sudo touch /mnt/usb/remote_services
sudo umount /mnt/usb

# Gadget-Script erstellen
cat << 'EOF' | sudo tee /usr/local/bin/start-usb-gadget.sh
#!/bin/bash
modprobe g_mass_storage file=/home/pi/usbstick.img stall=0 removable=1
EOF

sudo chmod +x /usr/local/bin/start-usb-gadget.sh

# Beim Boot ausführen
echo "/usr/local/bin/start-usb-gadget.sh" | sudo tee -a /etc/rc.local
```

### 4. An SoundTouch anschließen

```
1. Pi Zero ausschalten: sudo shutdown -h now
2. Micro-USB Kabel an Pi Zero USB-OTG Port (NICHT PWR!)
3. Anderes Ende an SoundTouch Micro-USB "Setup-B" Port
4. Pi Zero bekommt Strom vom SoundTouch (!)
5. Warten ~30 Sekunden bis Pi gebootet
6. SoundTouch neu starten (Power-Taste lang drücken, wieder ein)
```

### 5. SSH zum SoundTouch

```bash
# Von deinem PC aus (SoundTouch muss im Netzwerk sein)
ssh root@<SOUNDTOUCH-IP>

# Kein Passwort nötig - einfach Enter
```

## Troubleshooting

### Pi startet nicht vom SoundTouch-Strom
- SoundTouch liefert nur ~100mA am Setup-Port
- Alternative: Y-Kabel mit externer Stromversorgung
- Oder: Pi separat mit Strom versorgen, nur Daten zum SoundTouch

### USB-Stick wird nicht erkannt
```bash
# Auf Pi prüfen:
lsmod | grep g_mass_storage
# Sollte g_mass_storage zeigen

# Falls nicht:
sudo modprobe g_mass_storage file=/home/pi/usbstick.img
```

### SSH zum SoundTouch funktioniert nicht
- Prüfe ob SoundTouch nach Pi-Boot neu gestartet wurde
- Prüfe ob remote_services Datei auf dem Image existiert:
  ```bash
  sudo mount -o loop /home/pi/usbstick.img /mnt/usb
  ls -la /mnt/usb/
  ```

## Alternative: Fertiges Image

Anstatt manuell zu konfigurieren, kann ein fertiges Image verwendet werden:

```bash
# TODO: Fertiges Image auf GitHub Releases bereitstellen
# Download: soundtouch-usb-gadget.img.xz
# Mit Raspberry Pi Imager auf SD flashen
# Fertig!
```

## Nach SSH-Zugriff

```bash
# Auf SoundTouch nach Login:

# 1. SSH persistent machen (ohne USB-Stick)
touch /mnt/nv/remote_services
/etc/init.d/sshd start

# 2. Config prüfen
cat /opt/Bose/etc/SoundTouchSdkPrivateCfg.xml | grep bmxRegistry

# 3. Override erstellen (falls nötig)
# Siehe: reference-impl/SOUNDTOUCH_HACKING_REFERENCE.md
```
