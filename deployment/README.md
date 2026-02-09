# Deployment Scripts

Alle Deployment-bezogenen Dateien für OpenCloudTouch Container-Deployment.

> **Trademark Notice**: OpenCloudTouch (OCT) is not affiliated with Bose Corporation. Bose® and SoundTouch® are registered trademarks of Bose Corporation. See [TRADEMARK.md](../TRADEMARK.md) for details.

## 📁 Files

- **docker-compose.yml**: Docker Compose Konfiguration für Development
- **Dockerfile**: Root-Dockerfile (`../Dockerfile`) wird von Compose genutzt


> Hinweis: PowerShell-Deploy-Skripte liegen jetzt unter `tools/local-scripts/`.

## 🚀 Usage

### Local Development

```bash
# Docker Compose starten
cd deployment/
docker-compose up --build

# ODER: Podman lokal
siehe `tools/local-scripts/` (z. B. `run-container.ps1`)iner.ps1 -Port 7777 -ManualIPs "192.168.1.100"
```

### NAS/Server Deployment

```bash
cd deployment/
.\deploy-to-server.ps1
```

**Voraussetzungen**:
- PowerShell 7+
- SSH-Zugriff zu Target Server (user@targethost)
- Podman (für export-image.ps1)
- Docker (für docker-compose)

## 📝 Build Context

Alle Scripts verwenden folgende Pfade (relativ zu `deployment/`):

```
deployment/
├── docker-compose.yml      → context: .., dockerfile: Dockerfile
├── export-image.ps1        → podman build -t opencloudtouch:latest ..
├── run-container.ps1       → podman build -f ../Dockerfile ..
└── deploy-to-server.ps1    → ruft export-image.ps1 auf
```

**Build Context**: `..` (Parent directory = Repository Root)  
**Dockerfile**: `../Dockerfile`

## 🔧 Konfiguration

### Environment Variables

```bash
# SSDP Discovery
OCT_DISCOVERY_TIMEOUT=10

# Manual Device IPs (wenn SSDP nicht funktioniert)
OCT_MANUAL_DEVICE_IPS="192.168.1.100,192.168.1.101"

# Logging
OCT_LOG_LEVEL=INFO

# Database
OCT_DB_PATH=/data/oct.db
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
siehe `tools/local-scripts/` (z. B. `run-container.ps1`)iner.ps1

# Container starten (ohne Build, existing image)
siehe `tools/local-scripts/` (z. B. `run-container.ps1`)iner.ps1 -NoBuild
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
siehe `tools/local-scripts/` (z. B. `run-container.ps1`)iner.ps1 -ManualIPs "192.168.1.100,192.168.1.101"
```

### Server SSH Fehler

```bash
# SSH Verbindung testen
ssh user@targethost "docker version"

# Podman Container prüfen
ssh user@targethost "docker ps -a | grep opencloudtouch"
```

## 📄 Related Docs

- [Main README](../README.md): Projektübersicht
- [Backend README](../apps/backend/README.md): Backend-spezifische Docs
- [SERVER-DEPLOYMENT.md](../SERVER-DEPLOYMENT.md): Server Deployment Guide
