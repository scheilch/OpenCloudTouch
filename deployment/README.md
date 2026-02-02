# Deployment Scripts

Alle Deployment-bezogenen Dateien für SoundTouchBridge Container-Deployment.

## 📁 Files

- **docker-compose.yml**: Docker Compose Konfiguration für Development
- **Dockerfile**: siehe `backend/Dockerfile` (wird von Compose referenziert)
- **deploy-to-truenas.ps1**: TrueNAS Scale Deployment-Script (SSH-basiert)
- **export-image.ps1**: Container Image Build & Export (Podman)
- **run-container.ps1**: Lokaler Container Start (Podman)

## 🚀 Usage

### Local Development

```bash
# Docker Compose starten
cd deployment/
docker-compose up --build

# ODER: Podman lokal
.\run-container.ps1 -Port 7777 -ManualIPs "192.168.1.100"
```

### TrueNAS Deployment

```bash
cd deployment/
.\deploy-to-truenas.ps1
```

**Voraussetzungen**:
- PowerShell 7+
- SSH-Zugriff zu TrueNAS Host (siggiaze@hera)
- Podman (für export-image.ps1)
- Docker (für docker-compose)

## 📝 Build Context

Alle Scripts verwenden folgende Pfade (relativ zu `deployment/`):

```
deployment/
├── docker-compose.yml      → context: .., dockerfile: backend/Dockerfile
├── export-image.ps1        → podman build -f ../backend/Dockerfile ..
├── run-container.ps1       → podman build -f ../backend/Dockerfile ..
└── deploy-to-truenas.ps1   → ruft export-image.ps1 auf
```

**Build Context**: `..` (Parent directory = Repository Root)  
**Dockerfile**: `../backend/Dockerfile`

## 🔧 Konfiguration

### Environment Variables

```bash
# SSDP Discovery
CT_DISCOVERY_TIMEOUT=10

# Manual Device IPs (wenn SSDP nicht funktioniert)
CT_MANUAL_DEVICE_IPS="192.168.1.100,192.168.1.101"

# Logging
CT_LOG_LEVEL=INFO

# Database
CT_DB_PATH=/data/ct.db
```

### Ports

- **Backend API**: 7777 (default)
- **Frontend**: Embedded in Backend (bei Multi-stage Build)

### Volumes

- **data/**: SQLite DB, Config, Logs
- **config.yaml**: Optional (überschreibt Env Vars)

## 🧪 Testing

```bash
# Image bauen (ohne starten)
.\export-image.ps1

# Container starten (mit Build)
.\run-container.ps1

# Container starten (ohne Build, existing image)
.\run-container.ps1 -NoBuild
```

## 🛠️ Troubleshooting

### Build Fehler

```bash
# Podman: Build mit --no-cache
.\export-image.ps1 -NoCache

# Docker Compose: Clean rebuild
docker-compose build --no-cache
```

### SSDP Discovery funktioniert nicht

Windows Container können kein SSDP:
```bash
# Manual IPs verwenden
.\run-container.ps1 -ManualIPs "192.168.1.100,192.168.1.101"
```

### TrueNAS SSH Fehler

```bash
# SSH Verbindung testen
ssh siggiaze@hera "docker version"

# Podman Container prüfen
ssh siggiaze@hera "docker ps -a | grep soundtouch"
```

## 📄 Related Docs

- [Main README](../README.md): Projektübersicht
- [Backend README](../backend/README.md): Backend-spezifische Docs
- [TRUENAS-DEPLOY.md](../TRUENAS-DEPLOY.md): TrueNAS Deployment Guide
