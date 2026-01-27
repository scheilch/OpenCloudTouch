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
  - Optional später als Raspberry-Pi-Image („Appliance“) mit mDNS (`device.local`)

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

## 🛠️ Lokale Entwicklung

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements-dev.txt
python main.py
```

Backend läuft auf: http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend läuft auf: http://localhost:3000 (proxied zu Backend auf Port 8000)

### Tests

```bash
# Im Projekt-Root
pytest

# Mit Coverage
pytest --cov=backend --cov-report=html
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
- Manuellen Fallback nutzen: ENV Variable `STB_MANUAL_DEVICE_IPS=192.168.1.100,192.168.1.101` setzen

### Port 8000 bereits belegt

Ändern Sie den Port in [docker-compose.yml](docker-compose.yml) oder via ENV:

```bash
STB_PORT=8080 docker compose up -d
```

---

## ⚙️ Konfiguration

Konfiguration erfolgt via:
1. **ENV Variablen** (Prefix: `STB_`)
2. **Config-Datei** (optional): `config.yaml` im Container unter `/app/config.yaml` mounten

Siehe [.env.example](.env.example) und [config.example.yaml](config.example.yaml) für alle Optionen.

### Wichtige ENV Variablen

| Variable | Default | Beschreibung |
|----------|---------|--------------|
| `STB_HOST` | `0.0.0.0` | API Bind-Adresse |
| `STB_PORT` | `8000` | API Port |
| `STB_LOG_LEVEL` | `INFO` | Log-Level (DEBUG, INFO, WARNING, ERROR) |
| `STB_DB_PATH` | `/data/stb.db` | SQLite Datenbankpfad |
| `STB_DISCOVERY_ENABLED` | `true` | SSDP/UPnP Discovery aktivieren |
| `STB_MANUAL_DEVICE_IPS` | `[]` | Manuelle Geräte-IPs (Komma-separiert) |

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
- Tests (pytest)
- Health Check Endpoint

### 🔜 Iteration 1: Discovery + Device Inventory
- SSDP/UPnP Discovery
- Manuelle IP-Liste als Fallback
- GET `/api/devices` Endpoint
- Device Detail Caching

### 🔜 Iteration 2: RadioBrowser Adapter
- RadioBrowser API Client
- GET `/api/radio/search` Endpoint
- UI: Stationssuche

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

## 🧪 Tests

- Unit Tests: XML/JSON Rendering, Mapping-Logik, Provider-Parsing
- Integration Tests: gemockte SoundTouch-Endpunkte + Provider-API
- E2E Tests: optional mit echten Geräten (Demo-fähig)

---

## 🤝 Mitmachen

Beiträge sind willkommen!  
Bitte lies vorab [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## 📄 Lizenz

Apache License 2.0  
Siehe [`LICENSE`](LICENSE) und [`NOTICE`](NOTICE).
