# Bose SoundTouch Hacking Reference

**Stand:** 2026-02-11  
**Zweck:** Kompakte Referenz für Root/SSH-Zugriff und System-Modifikation

---

## 1. SSH/Telnet Aktivierung

### Method A: USB-Stick (EMPFOHLEN - funktioniert auf allen Firmware-Versionen)

```bash
# 1. USB-Stick FAT32 oder EXT2 formatieren
# 2. Leere Datei erstellen (KEINE Extension!):
touch remote_services

# 3. USB-Stick in Setup-B Port stecken (Micro-USB)
# 4. SoundTouch neu starten
# 5. SSH verbinden:
ssh root@<DEVICE_IP>  # Kein Passwort!
```

**Bestätigt funktionierend:** Firmware 9.0.41, 13.0.9, 15.x, 26.x, 27.x  
**Quelle:** Flarn2006 Blog Kommentare (2020-2024)

### Method B: Serial Console (3.5mm Service Port)

```
Hardware: USB-TTL Konverter (PL2303, CH340, CP2102)
Pinout (3.5mm TRS):
  - Tip:    TX (an USB-TTL RX)
  - Ring:   RX (an USB-TTL TX)  
  - Sleeve: GND

Settings: 115200 8N1
Login: root (kein Passwort)
```

**Anleitung kaufen:** https://shop.in-circuit.de/product_info.php?cPath=38&products_id=78

### Method C: Telnet Port 17000 (NUR alte Firmware)

```bash
telnet <DEVICE_IP> 17000
# Am "->" Prompt:
remote_services on
# FUNKTIONIERT NICHT auf Firmware 7.2.21+
```

---

## 2. Persistence (SSH dauerhaft aktivieren)

```bash
# Nach SSH-Login:
touch /mnt/nv/remote_services
/etc/init.d/sshd start

# Persistiert über Neustarts!
# USB-Stick kann danach entfernt werden
```

---

## 3. Device Codenames

| Codename | Gerät |
|----------|-------|
| Lisa | SoundTouch Adapter (SA-4/SA-5) |
| Rhino | SoundTouch 10 |
| Spotty | SoundTouch 20 |
| Mojo | SoundTouch 30 |
| Taigan | SoundTouch Portable |
| Lovejoy | Wave Pedestal |
| Burns | SA-x Amps |

---

## 4. Wichtige Pfade

```bash
# Systemkonfiguration (Read-Only)
/opt/Bose/etc/SoundTouchSdkPrivateCfg.xml
/opt/Bose/etc/Shepherd-spotty.xml

# Beschreibbare Konfiguration
/mnt/nv/BoseApp-Persistence/1/  # XML Configs
/mnt/nv/shepherd/                # Shepherd Override
/mnt/nv/remote_services          # SSH Persistence Flag

# BMX Registry URL (ZU ÄNDERN!)
/opt/Bose/etc/SoundTouchSdkPrivateCfg.xml
  → <bmxRegistryUrl>https://content.api.bose.io/bmx/registry/v1/services</bmxRegistryUrl>
```

---

## 5. "Installing Update 0%" Fix

```bash
# 1. SSH aktivieren (Method A)
# 2. Shepherd-Config kopieren:
mkdir /mnt/nv/shepherd
cp -a /opt/Bose/etc/Shepherd-spotty.xml /mnt/nv/shepherd
cp -a /opt/Bose/etc/Shepherd-noncore.xml /mnt/nv/shepherd

# 3. SoftwareUpdate auskommentieren in /mnt/nv/shepherd/Shepherd-spotty.xml:
<!-- <daemon name="SoftwareUpdate" recovery="ignore"/> -->

# 4. Reboot (WICHTIG für Flash-Persistence!)
reboot
```

**Alternative (temporär):**
```bash
# Via Telnet Port 17000:
demo enter       # 2x eingeben!
demo enter
sys timeout inactivity disable  # 2x eingeben!
sys timeout inactivity disable
```

---

## 6. Telnet Commands (Port 17000)

**Vollständige Liste:** https://pastebin.com/EwPKS26G

### Wichtige Commands

```bash
# System
sys ver                      # Firmware Version
sys reboot                   # Neustart
sys factorydefault           # Factory Reset
sys volume                   # Volume get/set
sys timeout inactivity disable  # Standby deaktivieren

# Presets/Keys
key preset_1                 # Preset 1-6 abspielen
key power                    # Power Toggle
key aux                      # AUX auswählen

# Network
network wi-fi profiles add <SSID> wpa_or_wpa2 <PASSWORD>

# SCM (Service Control Manager)
scm list                     # Prozesse anzeigen
scm restart <process>        # Prozess neustarten

# Demo Mode (für gebrickte Geräte)
demo enter
demo exit

# PDO (Persistent Data Objects)
getpdo CurrentSystemConfiguration
```

---

## 7. USB Direct Connection

```
USB Setup Port (Micro-USB) → Windows Network Interface
IP: 203.0.113.1
Web UI: http://203.0.113.1:17008/update.html  (Firmware Upload!)
Telnet: Port 17000
```

---

## 8. Firmware Ressourcen

### Archive.org (36GB komplett)
```bash
wget --recursive --no-parent --no-host-directories --cut-dirs=1 \
  --content-disposition \
  --accept "*.zip" -e robots=off \
  "https://archive.org/download/bose-soundtouch-software-and-firmware/Firmware/"
```

**WICHTIG:** `--content-disposition` verhindert leere Ordner!

### Downgrade Guide
https://bose.fandom.com/wiki/SoundTouch_Firmware_Downgrade_Guide

### Service Manuals
- ST20: https://manualzz.com/download/6441622
- ST10: https://images-eu.ssl-images-amazon.com/images/I/D1WMdRovblS.pdf
- ST30: https://elektrotanya.com/bose_soundtouch_30_series_i_ii.pdf/download.html

---

## 9. Links

| Resource | URL |
|----------|-----|
| Originaler Blog (2014) | https://flarn2006.blogspot.com/2014/09/hacking-bose-soundtouch-and-its-linux.html |
| Telnet Commands Pastebin | https://pastebin.com/EwPKS26G |
| SCM List Pastebin | https://pastebin.com/zRhdn0Tf |
| Archive.org Firmware | https://archive.org/download/bose-soundtouch-software-and-firmware/ |
| Bose Wiki | https://bose.fandom.com/wiki/ |

---

## 10. System Info

```bash
# Linux Kernel
uname -a
# Linux lisa 3.14.43+ armv7l GNU/Linux

# BusyBox
busybox
# BusyBox v1.19.4

# SoC
# AM335x (BeagleBone Black kompatibel)
/boot/am335x-boneblack.dtb
```

---

## 11. OpenCloudTouch Integration

Nach SSH-Zugriff:
```bash
# BMX Registry URL ändern
vi /opt/Bose/etc/SoundTouchSdkPrivateCfg.xml

# Oder Override erstellen:
cp /opt/Bose/etc/SoundTouchSdkPrivateCfg.xml /mnt/nv/
# Editieren: bmxRegistryUrl → http://YOUR_SERVER:7777/bmx/registry/v1/services
```

**Problem:** Root-FS ist Read-Only. Lösung: Override in /mnt/nv/ oder Firmware-Mod.
