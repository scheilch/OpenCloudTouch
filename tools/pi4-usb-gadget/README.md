# Raspberry Pi 4 USB Mass Storage Gadget

Verwandelt den Raspberry Pi 4 in einen USB-Stick, um die SoundTouch-Box zu konfigurieren.

## Voraussetzungen

- Raspberry Pi 4 (USB-C Port unterstützt Gadget-Mode)
- Micro-SD Karte mit Raspberry Pi OS Lite
- USB-C Kabel (Data, nicht nur Charging)
- Optional: USB-C zu USB-A Adapter + USB-A zu Micro-USB Kabel

## Verkabelung

```
Pi 4 USB-C Port ←→ USB-C Kabel ←→ [Adapter wenn nötig] ←→ SoundTouch Micro-USB Port
```

## Setup-Schritte

### 1. Raspberry Pi OS Lite auf SD-Karte flashen

```powershell
# Mit Raspberry Pi Imager
# Wähle: Raspberry Pi OS Lite (64-bit)
# Aktiviere SSH in den Einstellungen
```

### 2. Nach dem Booten: SSH verbinden

```bash
ssh pi@raspberrypi.local
# Standard-Passwort: raspberry
```

### 3. Setup-Script ausführen

```bash
# Script auf Pi kopieren
scp setup-usb-gadget.sh pi@raspberrypi.local:~/

# Auf Pi ausführen
ssh pi@raspberrypi.local
chmod +x setup-usb-gadget.sh
sudo ./setup-usb-gadget.sh

# Pi neu starten
sudo reboot
```

### 4. An SoundTouch anschließen

1. Pi ausschalten
2. USB-C Kabel an Pi 4 USB-C Port (nicht USB-A!)
3. Anderes Ende an SoundTouch Micro-USB Service Port
4. Pi einschalten
5. Warten bis Pi gebootet (ca. 30s)
6. SoundTouch aus- und wieder einstecken (Reboot)

### 5. Nach SoundTouch-Reboot: Telnet

```bash
# Von deinem PC aus
telnet 192.168.178.79

# Login: root (kein Passwort)
```

### 6. SoundTouch konfigurieren

```bash
# Filesystem beschreibbar machen
rw

# Config editieren
vi /opt/Bose/etc/SoundTouchSdkPrivateCfg.xml

# Ändere bmxRegistryUrl zu:
# http://192.168.178.11:7777/bmx/registry/v1/services

# Speichern: ESC, dann :wq

# Neustart
reboot
```

## Troubleshooting

### Pi bootet nicht als USB-Gadget

- Prüfe ob USB-C Kabel Daten unterstützt (nicht nur Laden)
- Prüfe ob config.txt dtoverlay=dwc2 enthält
- Prüfe ob g_mass_storage Modul geladen ist: `lsmod | grep g_mass`

### SoundTouch erkennt USB-Stick nicht

- Pi muss VOR SoundTouch eingeschaltet sein
- SoundTouch muss nach Pi-Boot neu gestartet werden
- Prüfe ob `remote_services` Datei auf dem virtuellen USB-Stick existiert

### Telnet funktioniert nicht

- Nur möglich NACH Boot mit `remote_services` Datei
- IP-Adresse prüfen (evtl. hat sich geändert)
- Port 23 muss im Netzwerk offen sein
