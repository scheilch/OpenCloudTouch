# Build & Deployment Analysis: OpenCloudTouch

**Analyse-Datum:** 2026-02-13
**Version:** 0.2.0
**Analyst:** Claude Opus 4.5

---

## Build-System Übersicht

### Frontend Build
| Tool | Version | Konfiguration |
|------|---------|---------------|
| Vite | 7.3.1 | `apps/frontend/vite.config.ts` |
| Node.js | 20.11 | Als Docker Base Image |
| TypeScript | 5.9.3 | `tsconfig.json` |

### Backend Build
| Tool | Version | Konfiguration |
|------|---------|---------------|
| Python | 3.11.8 | Docker slim-bookworm |
| setuptools | ≥68.0 | `pyproject.toml` |
| pip | Latest | requirements.txt |

### Container Build
| Tool | Version | Datei |
|------|---------|-------|
| Docker | Multi-stage | `Dockerfile` |
| Podman | Compatible | Local deployment |

---

## Deployment-Targets

### 1. Lokale Entwicklung
```
deployment/local/deploy-local.ps1
├── Podman + WSL2
├── network_mode: host
└── Mock oder Real Devices
```

### 2. TrueNAS Scale
```
deployment/local/deploy-to-server.ps1
├── SSH + SCP Transfer
├── Docker/Podman
└── SSDP Discovery
```

### 3. GitHub Container Registry
```
.github/workflows/ci-cd.yml
├── ghcr.io/user/opencloudtouch
├── Multi-arch: amd64 + arm64
└── Semantic Versioning
```

---

## FINDINGS SUMMARY

| Priorität | Kategorie | Count |
|-----------|-----------|-------|
| P1 | SECURITY | 1 |
| P2 | BUILD | 2 |
| P2 | DEPLOYMENT | 2 |
| P3 | MAINTAINABILITY | 3 |

**TOTAL:** 8 Findings

---

## [P1] [SECURITY] Docker Image SHA256 Digests könnten veraltet sein

**Datei:** `Dockerfile`
**Zeilen:** 18, 50

**Problem:**
```dockerfile
FROM node:20.11-alpine3.19@sha256:aa96f8d22277ea3c16c6892cb89b2dcbe5c3c26b31fcd6a4e23bddf7f81c84b7
# ...
FROM python:3.11.8-slim-bookworm@sha256:8c9da8f3069be48e38bb88c0f5936dfe1bf0e14e0b1ca3e4e1e0b7f7a4a6aa6f
```

**Warum wichtig:**
- Pinned digests veralten wenn Base Images Sicherheitsupdates bekommen
- SHA-Mismatch bei Pull führt zu Build-Fehler
- Keine automatische Aktualisierung

**Fix:**
1. Dependabot bereits konfiguriert für Docker:
```yaml
# .github/dependabot.yml
- package-ecosystem: "docker"
  directory: "/"
  schedule:
    interval: "weekly"
```

2. Alternativ: Renovate Bot mit automerge für Patches

3. Monatliche manuelle Prüfung:
```powershell
# scripts/check-base-images.ps1
docker pull node:20.11-alpine3.19
docker inspect --format='{{index .RepoDigests 0}}' node:20.11-alpine3.19
```

**Aufwand:** 15min (Script erstellen)

---

## [P2] [BUILD] Frontend Bundle nicht optimiert

**Datei:** `apps/frontend/package.json`

**Problem:**
Fehlende Build-Optimierungen:
- Kein Bundle-Analyse-Tool
- Keine Chunk-Splitting Konfiguration
- Keine Dead-Code-Elimination Prüfung

**Fix:**
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    react(),
    visualizer({
      filename: 'dist/stats.html',
      gzipSize: true,
    }),
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          motion: ['framer-motion'],
        },
      },
    },
    sourcemap: process.env.NODE_ENV !== 'production',
    minify: 'esbuild',
    target: 'es2020',
  },
})
```

```json
// package.json
{
  "devDependencies": {
    "rollup-plugin-visualizer": "^5.12.0"
  },
  "scripts": {
    "build:analyze": "vite build && open dist/stats.html"
  }
}
```

**Aufwand:** 30min

---

## [P2] [BUILD] Python .pyc Compilation entfernt .py Source Files

**Datei:** `Dockerfile`
**Zeilen:** 71-74

**Problem:**
```dockerfile
RUN python -m compileall -b opencloudtouch/ && \
    find opencloudtouch/ -name "*.py" ! -name "__main__.py" -delete && \
    find opencloudtouch/ -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
```

**Warum problematisch:**
- Debugging in Production erschwert
- Tracebacks zeigen keine Source Lines
- `inspect.getsource()` schlägt fehl

**Aber:** Dies ist eine bewusste Entscheidung für kleinere Image-Size.

**Empfehlung:**
```dockerfile
# Optional: Keep source in debug builds
ARG DEBUG_BUILD=false
RUN python -m compileall -b opencloudtouch/ && \
    if [ "$DEBUG_BUILD" != "true" ]; then \
        find opencloudtouch/ -name "*.py" ! -name "__main__.py" -delete; \
    fi
```

**Aufwand:** 10min

---

## [P2] [DEPLOYMENT] Hardcoded TrueNAS Credentials

**Datei:** `deployment/local/deploy-to-server.ps1`
**Zeilen:** 14-17

**Problem:**
```powershell
$TrueNasHost = "targethost"
$TrueNasUser = "user"
```

**Warum schlecht:**
- Hardcoded Credentials in Version Control
- Nicht portabel für andere Nutzer
- Keine Sicherheit (obwohl Username-only)

**Fix:**
```powershell
# deployment/local/deploy-to-server.ps1
param(
    [string]$Server = $env:OCT_DEPLOY_HOST,
    [string]$User = $env:OCT_DEPLOY_USER,
    # ...
)

# Validate required params
if (-not $Server -or -not $User) {
    Write-Host "Usage: .\deploy-to-server.ps1 -Server <host> -User <user>"
    Write-Host "Or set environment variables: OCT_DEPLOY_HOST, OCT_DEPLOY_USER"
    exit 1
}
```

```powershell
# Personal config (gitignored):
# deployment/local/.env.local
$env:OCT_DEPLOY_HOST = "targethost"
$env:OCT_DEPLOY_USER = "user"
```

**Aufwand:** 15min

---

## [P2] [DEPLOYMENT] Fehlende Health-Check Retry im CI/CD

**Datei:** `.github/workflows/ci-cd.yml`

**Problem:**
Docker Compose Health Check hat Retries, aber CI/CD Pipeline wartet nicht aktiv:

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "...urlopen..."]
  interval: 30s
  timeout: 10s
  retries: 3
```

CI/CD hat kein explizites "wait for healthy" nach Container-Start.

**Fix:**
```yaml
# In deployment job
- name: Wait for container to be healthy
  run: |
    for i in $(seq 1 30); do
      if docker inspect --format='{{.State.Health.Status}}' opencloudtouch | grep -q "healthy"; then
        echo "Container is healthy!"
        exit 0
      fi
      echo "Waiting for container... ($i/30)"
      sleep 5
    done
    echo "Container did not become healthy in time"
    docker logs opencloudtouch
    exit 1
```

**Aufwand:** 15min

---

## [P3] [MAINTAINABILITY] Keine .env.example für lokale Entwicklung

**Problem:**
Keine Beispiel-Environment-Datei für lokale Entwicklung.

**Fix:**
```bash
# deployment/local/.env.example
# OpenCloudTouch Local Development Configuration
# Copy to .env and adjust values

# Backend
OCT_HOST=0.0.0.0
OCT_PORT=7777
OCT_LOG_LEVEL=DEBUG
OCT_MOCK_MODE=true
OCT_DISCOVERY_ENABLED=true
OCT_DISCOVERY_TIMEOUT=10
# OCT_MANUAL_DEVICE_IPS=192.168.1.100,192.168.1.101

# Frontend (Vite)
VITE_API_BASE_URL=http://localhost:7777

# Deployment
OCT_DEPLOY_HOST=your-server.local
OCT_DEPLOY_USER=your-username
```

```gitignore
# .gitignore
deployment/local/.env
deployment/local/.env.local
```

**Aufwand:** 10min

---

## [P3] [MAINTAINABILITY] Inkonsistente ENV-Variable Prefixes

**Problem:**
```bash
# Backend verwendet:
OCT_HOST, OCT_PORT, OCT_LOG_LEVEL

# Aber auch:
CT_MANUAL_DEVICE_IPS  # ← CT_ statt OCT_!
CT_LOG_LEVEL          # ← CT_ in deploy-to-server.ps1
```

**Fix:**
Alle auf `OCT_` vereinheitlichen:

```python
# core/config.py
class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OCT_")  # Nur OCT_
```

Migration:
- `CT_MANUAL_DEVICE_IPS` → `OCT_MANUAL_DEVICE_IPS`
- `CT_LOG_LEVEL` → `OCT_LOG_LEVEL`
- `CT_DISCOVERY_*` → `OCT_DISCOVERY_*`

**Aufwand:** 30min (inkl. Deployment-Scripts)

---

## [P3] [MAINTAINABILITY] Fehlende Build-Versionierung im Frontend

**Datei:** `apps/frontend/src/`

**Problem:**
Frontend zeigt keine Build-Version/Commit an.

**Fix:**
```typescript
// vite.config.ts
export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    __GIT_COMMIT__: JSON.stringify(process.env.GIT_COMMIT || 'dev'),
  },
})

// src/version.ts
export const VERSION = __APP_VERSION__ || '0.0.0';
export const BUILD_TIME = __BUILD_TIME__ || 'unknown';
export const GIT_COMMIT = __GIT_COMMIT__ || 'unknown';

// Licenses.tsx oder Settings.tsx:
import { VERSION, BUILD_TIME, GIT_COMMIT } from '../version';
// ...
<p>Version {VERSION} ({GIT_COMMIT.slice(0, 7)})</p>
```

```yaml
# CI/CD
env:
  GIT_COMMIT: ${{ github.sha }}
```

**Aufwand:** 20min

---

## POSITIVE BUILD-ASPEKTE

### 1. Multi-Stage Docker Build ✓
```dockerfile
FROM node:20.11-alpine AS frontend-builder
FROM python:3.11-slim AS python-deps
FROM python:3.11-slim AS backend  # Final minimal image
```

### 2. Pinned Image Digests ✓
```dockerfile
FROM node:20.11-alpine@sha256:aa96f8d22...
```

### 3. Multi-Arch Support ✓
```dockerfile
ARG TARGETARCH
RUN if [ "$TARGETARCH" = "arm64" ]; then ...
```

### 4. Non-Root User ✓
```dockerfile
RUN useradd -m -u 1000 oct
USER oct
```

### 5. Health Check ✓
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s \
  CMD /entrypoint.sh health || exit 1
```

### 6. Comprehensive CI/CD Pipeline ✓
```yaml
jobs:
  security:     # Bandit, Safety, npm audit
  format:       # Black, Prettier
  lint:         # Ruff, ESLint
  backend-tests:
  frontend-tests:
  build-docker:
  deploy:
```

### 7. Codecov Integration ✓
```yaml
# codecov.yml
coverage:
  status:
    project:
      default:
        target: 80%
```

---

## CI/CD Pipeline Struktur

```
┌───────────────┐     ┌───────────────┐
│   security    │     │    format     │
│ (bandit,npm)  │     │(black,prettier)│
└───────┬───────┘     └───────┬───────┘
        │                     │
        ├─────────────────────┤
        ▼                     ▼
┌───────────────┐     ┌───────────────┐
│     lint      │     │ backend-tests │
│ (ruff,eslint) │     │   (pytest)    │
└───────┬───────┘     └───────┬───────┘
        │                     │
        ├─────────────────────┤
        ▼                     ▼
┌───────────────┐     ┌───────────────┐
│ frontend-tests│     │ build-docker  │
│   (vitest)    │     │ (multi-arch)  │
└───────────────┘     └───────┬───────┘
                              │
                              ▼
                      ┌───────────────┐
                      │    deploy     │
                      │  (ghcr.io)    │
                      └───────────────┘
```

---

## Deployment Scripts Bewertung

| Script | Zweck | Qualität |
|--------|-------|----------|
| deploy-local.ps1 | Lokales Podman | ✓ Gut |
| deploy-to-server.ps1 | TrueNAS SSH | ⚠️ Hardcoded creds |
| export-image.ps1 | TAR Export | ✓ Gut |
| clear-database.ps1 | DB Reset | ✓ Gut |
| run-real-tests.ps1 | Live Device Tests | ✓ Gut |

---

## 💾 SESSION-STATE (für Resume)

**Letzter Stand:** 2026-02-13
**Aktuelles Dokument:** 06_BUILD_DEPLOY_ANALYSIS.md ✅
**Fortschritt:** 6/9 Dokumente erstellt

### Kumulative Findings:
- P1: 3
- P2: 38
- P3: 27

### Abgeschlossen:
- [x] 01_PROJECT_OVERVIEW.md
- [x] 02_ARCHITECTURE_ANALYSIS.md
- [x] 03_BACKEND_CODE_REVIEW.md
- [x] 04_FRONTEND_CODE_REVIEW.md
- [x] 05_TESTS_ANALYSIS.md
- [x] 06_BUILD_DEPLOY_ANALYSIS.md

### Noch offen:
- [ ] 07_DOCUMENTATION_GAPS.md
- [ ] 08_DEPENDENCY_AUDIT.md
- [ ] 09_ROADMAP.md

**Nächster Schritt:** Documentation Gaps Analysis
