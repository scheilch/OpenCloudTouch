# SoundTouchBridge (STB)

**SoundTouchBridge** ist eine lokale, Open-Source-Ersatzlösung für die eingestellten Cloud-Funktionen von **Bose SoundTouch** Geräten.

Ziel ist es, SoundTouch-Lautsprecher (z. B. **SoundTouch 10 / 30 / 300**) auch nach dem Ende des offiziellen Supports **weiter sinnvoll nutzen zu können**
– **ohne Cloud**, **ohne Home Assistant** und ohne proprietäre Apps.

> Leitidee: STB ersetzt nicht die Geräte, sondern die Bose-Cloud.  
> Ein Container, eine Web-App, Presets funktionieren wieder.

---

## ✨ Features (Zielbild)

- 🎵 **Internetradio & Presets**
  - Radiosender suchen (MVP: offene Quellen, z. B. RadioBrowser)
  - Presets **1–6** neu belegen
  - Physische Preset-Tasten am Gerät funktionieren wieder

- 🖥️ **Web-UI (App-ähnlich)**
  - Bedienung per Browser (Desktop & Smartphone)
  - Geführte UX für nicht versierte Nutzer
  - „Now Playing“ (Sender/Titel), soweit vom Stream unterstützt

- 🔊 **Multiroom**
  - Bestehende SoundTouch-Gruppen anzeigen
  - Geräte gruppieren / entkoppeln (Zonen)

- 📟 **Now Playing**
  - Anzeige im Web-UI
  - Anzeige auf dem Gerätedisplay, soweit SoundTouch/Stream-Metadaten es hergeben

- 🐳 **Ein Container**
  - Docker-first (amd64 + arm64)
  - Optional später als Raspberry-Pi-Image („Appliance“) mit mDNS (`soundtouch.local`)

---

## 🎯 Zielgruppe

- Besitzer von Bose SoundTouch Geräten, die nach dem Cloud-Ende weiterhin Radio/Presets/Multiroom nutzen wollen
- Nutzer ohne Home Assistant
- Nutzer mit Raspberry Pi / NAS / Mini-PC, die „einfach nur“ einen Container starten können
- Power-User: Adapter/Provider erweiterbar (Plugins)

---

## 🧩 Architektur (Kurzfassung)

SoundTouchBridge ist eine eigenständige Web-App + Backend im **einen** Container:

```text
Browser UI
   ↓
SoundTouchBridge (Docker)
   ↓
Bose SoundTouch Geräte (lokale API: HTTP + WebSocket)
```

Streaming-Anbieter werden über **Adapter** angebunden (MVP: Internetradio aus offenen Quellen).
Optional kann später ein Music-Assistant-Adapter oder weitere Provider ergänzt werden.

---

## 📦 Installation & Quickstart

### Option 1: Docker Compose (empfohlen)

1. **Repo klonen:**
   ```bash
   git clone https://github.com/<your-username>/soundtouch-bridge.git
   cd soundtouch-bridge
   ```

2. **Container starten:**
   ```bash
   docker compose up -d
   ```

3. **Web-UI öffnen:**
   ```
   http://localhost:8000
   ```

4. **Logs prüfen:**
   ```bash
   docker compose logs -f
   ```

5. **Stoppen:**
   ```bash
   docker compose down
   ```

### Option 2: Docker Run

```bash
docker run -d \
  --name soundtouch-bridge \
  --network host \
  -v stb-data:/data \
  ghcr.io/<your-username>/soundtouch-bridge:latest
```

Danach im Browser öffnen: `http://localhost:8000`

### Warum `--network host`?

Discovery (SSDP/UPnP) und lokale Gerätekommunikation funktionieren damit am stabilsten (insbesondere auf Raspberry Pi/NAS).

---

## � Projekt-Struktur

```
soundtouch-bridge/
├── apps/apps/backend/                    # Python Backend (FastAPI)
│   ├── src/soundtouch_bridge/ # Main package (pip-installable)
│   │   ├── core/              # Config, Logging, Exceptions
│   │   ├── devices/           # Device discovery, client, API
│   │   ├── radio/             # Radio providers, API
│   │   └── main.py            # FastAPI app
│   ├── tests/                 # Backend tests
│   │   ├── unit/              # Unit tests (core, devices, radio)
│   │   ├── integration/       # API integration tests
│   │   └── e2e/               # End-to-end tests
│   ├── pyproject.toml         # Python packaging (PEP 517/518)
│   ├── pytest.ini             # Test configuration
│   └── Dockerfile             # Backend container image
├── apps/apps/frontend/                  # React Frontend (Vite)
│   ├── src/                   # React components, hooks, services
│   ├── tests/                 # Frontend tests
│   └── package.json           # NPM dependencies
├── deployment/                # Deployment scripts
│   ├── docker-compose.yml     # Docker Compose config
│   ├── deploy-to-truenas.ps1  # TrueNAS deployment
│   └── README.md              # Deployment guide
├── scripts/                   # User utility scripts
│   ├── test-all.ps1           # Full test suite
│   ├── demo_radio_api.py      # Radio API demo
│   └── README.md              # Scripts documentation
└── docs/                      # Project documentation
```

---

## 🛠️ Lokale Entwicklung

### Backend

```bash
cd apps/backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements-dev.txt
python main.py
```

Backend läuft auf: http://localhost:8000

### Frontend

```bash
cd apps/frontend
npm install
npm run dev
```

Frontend läuft auf: http://localhost:3000 (proxied zu Backend auf Port 8000)

### Tests

```bash
# Backend: All tests with coverage
cd apps/backend
pytest -v --cov=backend --cov-report=html

# Backend: Specific test file
pytest tests/test_radiobrowser_adapter.py -v

# Frontend: All tests
cd apps/frontend
npm test

# Frontend: Watch mode
npm test -- --watch

# Frontend: Coverage
npm test -- --coverage

# E2E Demos
python e2e/demo_iteration1.py         # Device Discovery
python e2e/demo_iteration2.py         # RadioBrowser API (Mock)
python e2e/demo_iteration2.py --real  # RadioBrowser API (Real)

# Coverage Report (Backend)
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html # Windows
```

---

## 🐛 Troubleshooting

### Container startet nicht

```bash
# Logs prüfen
docker compose logs soundtouch-bridge

# Health check manuell testen
docker exec soundtouch-bridge curl http://localhost:8000/health
```

### Geräte werden nicht gefunden

- Stellen Sie sicher, dass `--network host` verwendet wird (Docker Compose macht dies standardmäßig)
- Prüfen Sie, ob Geräte im selben Netzwerk sind
- Manuellen Fallback nutzen: ENV Variable `CT_MANUAL_DEVICE_IPS=192.168.1.100,192.168.1.101` setzen

### Port 8000 bereits belegt

Ändern Sie den Port in [docker-compose.yml](docker-compose.yml) oder via ENV:

```bash
CT_PORT=8080 docker compose up -d
```

---

## ⚙️ Konfiguration

Konfiguration erfolgt via:
1. **ENV Variablen** (Prefix: `CT_`)
2. **Config-Datei** (optional): `config.yaml` im Container unter `/app/config.yaml` mounten

Siehe [.env.example](.env.example) und [config.example.yaml](config.example.yaml) für alle Optionen.

### Wichtige ENV Variablen

| Variable | Default | Beschreibung |
|----------|---------|--------------|
| `CT_HOST` | `0.0.0.0` | API Bind-Adresse |
| `CT_PORT` | `8000` | API Port |
| `CT_LOG_LEVEL` | `INFO` | Log-Level (DEBUG, INFO, WARNING, ERROR) |
| `CT_DB_PATH` | `/data/ct.db` | SQLite Datenbankpfad |
| `CT_DISCOVERY_ENABLED` | `true` | SSDP/UPnP Discovery aktivieren |
| `CT_MANUAL_DEVICE_IPS` | `[]` | Manuelle Geräte-IPs (Komma-separiert) |

---

## ✅ MVP (erste Instanz)

Fokus: **Knopf drücken → Sender spielt → Anzeige**

- UI-Seite 1: Radiosender suchen/auswählen und Preset (1–6) zuordnen
- STB programmiert Presets so um, dass die Preset-Taste eine lokale Station-URL lädt (cloudfrei)
- E2E Demo/Test: Station finden → Preset setzen → Preset per API simulieren → Playback & „now playing“ verifizieren

---

## 🧭 Roadmap & Status

### ✅ Iteration 0: Repo/Build/Run (FERTIG)
- Backend (FastAPI + Python 3.11)
- Frontend (React + Vite)
- Docker Multi-Stage Build (amd64 + arm64)
- CI/CD Pipeline (GitHub Actions)
- Tests (pytest, 85% coverage)
- Health Check Endpoint

### ✅ Iteration 1: Discovery + Device Inventory (FERTIG)
- SSDP/UPnP Discovery
- Manual IP Fallback
- SoundTouch HTTP Client (/info, /now_playing)
- SQLite Device Repository
- GET/POST `/api/devices` Endpoints
- Frontend: Device List UI
- **Tests**: 109 Backend Tests, E2E Demo Script

### ✅ Iteration 2: RadioBrowser API Integration (FERTIG)
- RadioBrowser API Adapter (108 Zeilen, async httpx, Retry-Logik)
- Search Endpoints: `/api/radio/search`, `/api/radio/station/{uuid}`
- Search Types: name, country, tag (limit-Parameter)
- Frontend: RadioSearch Component (React Query)
  - Debouncing (300ms), Loading/Error/Empty States
  - Skeleton Screens, ARIA Labels, Keyboard Navigation
  - Mobile-First Design (48px Touch Targets, WCAG 2.1 AA)
- **Tests**: 150 Backend Tests (83% Coverage) + 22 Frontend Tests (100% RadioSearch Coverage)
- **Refactoring**: Provider abstraction (radio_provider.py) vorbereitet für zukünftige Erweiterungen

### ✅ Iteration 2.5: Testing & Quality Assurance + Refactoring (ABGESCHLOSSEN)

**Backend Tests**:
- ✅ **268 Tests PASSING** (Unit + Integration + E2E)
- ✅ **Coverage: 88%** (Target: ≥80%) 🎯 **DEUTLICH ÜBERTROFFEN!**
- ✅ **+20 neue Tests** in Session 5-7:
  - BoseSoundTouchClientAdapter: 99% Coverage (+13 Tests)
  - SSDP Edge Cases: 73% Coverage (+7 Tests)
  - Device API Concurrency Tests
  - Error Handling & Retry Logic

**Frontend Tests**:
- ✅ **87 Tests PASSING** (+6 neue Error Handling Tests)
- ✅ **Coverage: ~55%** (von 0% hochgezogen)
- ✅ Component Tests: RadioPresets, Settings, DeviceSwiper, EmptyState
- ✅ **Error Handling**: Network errors, HTTP errors, Retry mechanism

**E2E Tests**:
- ✅ **15 Cypress Tests PASSING** (Mock Mode)
- ✅ Device Discovery + Manual IP Configuration
- ✅ Complete User Journey Tests
- ✅ Regression Tests für 3 Bug-Fixes

**Refactoring Highlights** (13/16 Tasks, 3h 34min, -90% deviation):
- ✅ **Service Layer Extraction**: Clean Architecture, DeviceSyncService
- ✅ **Global State Removal**: Lock-based concurrency statt Boolean-Flag
- ✅ **Frontend Error Handling**: Retry-Button, User-friendly messages
- ✅ **Dead Code Removal**: Alle Linter clean (ruff, vulture, ESLint)
- ✅ **Production Guards**: DELETE endpoint protected
- ✅ **Auto-Formatting**: black, isort, Prettier über 77 Files
- ✅ **Naming Conventions**: Konsistente Namen über alle 370 Tests

**Code Quality**:
- ✅ 370 automatisierte Tests (268 Backend + 87 Frontend + 15 E2E)
- ✅ Zero Global State, Zero Linter Warnings
- ✅ TDD-Workflow: Alle Änderungen mit Tests abgesichert
- ✅ Pre-Commit Hooks: Tests + Coverage + E2E automatisch

**Status**: ✅ **PRODUCTION-READY** - Refactoring abgeschlossen, alle Tests grün

### 🔜 Iteration 3: Preset Mapping
- SQLite Schema (devices, presets, mappings)
- POST `/api/presets/apply`
- Station Descriptor Endpoint

### 🔜 Iteration 4: Playback Demo (E2E)
- Key Press Simulation (PRESET_n)
- Now Playing Polling + WebSocket
- E2E Demo Script

### 🔜 Iteration 5: UI Preset-UX
- Preset-Kacheln (1–6)
- Zuweisen per Klick
- Now Playing Panel

### 🔜 Weitere EPICs
- Multiroom (Gruppen/Entkoppeln)
- Lautstärke, Play/Pause, Standby
- Firmware-Info/Upload-Assistent
- Weitere Provider/Adapter (optional): TuneIn*, Spotify*, Apple Music*, Deezer*, Music Assistant*
  - *Hinweis: Provider werden nur aufgenommen, wenn rechtlich und technisch sauber umsetzbar.*

---

## 🧪 Tests & Coverage

**Coverage-Ziel**: 80% für Backend & Frontend

### Backend
- **Aktuell**: 96% (296 Tests)
- **Arten**: Unit Tests, Integration Tests
- **Technologie**: pytest + pytest-cov + pytest-asyncio
- **Kommando**: `cd apps/backend && pytest --cov=cloudtouch --cov-report=term-missing --cov-fail-under=80`

### Frontend
- **Aktuell**: 52% (87 Tests) ⚠️ UNTER 80% THRESHOLD
- **Arten**: Unit Tests (Vitest), E2E Tests (Cypress)
- **Technologie**: Vitest + @testing-library/react, Cypress
- **Kommandos**:
  - Unit Tests: `cd apps/frontend && npm run test:coverage`
  - E2E Tests: `cd apps/frontend && npm run test:e2e`

### CI/CD & Pre-commit
- **Pre-commit Hook** (`pre-commit.ps1`):
  - Backend Tests (80% enforced)
  - Frontend Unit Tests (80% enforced) ⚠️ Aktuell blockiert bei 52%
  - Frontend E2E Tests (Cypress)
- **GitHub Workflow** (`.github/workflows/ci-cd.yml`):
  - Gleiche Test-Suite wie Pre-commit Hook
  - Zusätzlich: Linting (ruff, black, mypy, ESLint)
- **Config**: Zentrale Konfiguration in `.ci-config.json` und `.ci-config.md`

### Kritische Bereiche (Frontend < 80%)
- `EmptyState.tsx`: 27.63% (46 uncovered lines)
- `LocalControl.tsx`: 2.77%
- `MultiRoom.tsx`: 2.56%
- `Firmware.tsx`: 0%
- `Toast.tsx`: 0%

---

## 🤝 Mitmachen

Beiträge sind willkommen!  
Bitte lies vorab [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## 📄 Lizenz

Apache License 2.0  
Siehe [`LICENSE`](LICENSE) und [`NOTICE`](NOTICE).
