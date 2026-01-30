# E2E Demo & Test Scripts

E2E Tests und Demo-Scripts für SoundTouchBridge.

## Iteration 0: Basic Connectivity

```bash
cd e2e
python demo_iteration0.py
```

Voraussetzung: SoundTouchBridge läuft (docker compose up oder lokal).

## Iteration 1: Discovery + Device Listing ✅

```bash
python e2e/demo_iteration1.py
```

**Features**:
- SSDP Device Discovery
- SoundTouch Client (Info + Now Playing)
- Device Repository (SQLite)
- API Endpoints: `/devices`, `/health`

**Status**: Abgeschlossen (41 Tests, 100% Pass)

## Iteration 2: RadioBrowser API Integration ✅

```bash
# Mock-Modus (CI-friendly, keine Internet-Verbindung)
python e2e/demo_iteration2.py

# Real API-Modus (echte RadioBrowser API Calls)
python e2e/demo_iteration2.py --real
```

**Features**:
- RadioBrowser API Client (Search, Station Detail)
- API Endpoints: `/api/radio/search`, `/api/radio/station/{uuid}`
- Query-Parameter: `q`, `search_type` (name/country/tag), `limit`
- Error Handling (Timeout, Connection, HTTP Errors)

**Status**: Abgeschlossen (150 Tests, 83.29% Coverage)

**API Examples**:
```bash
# Search by name
curl "http://localhost:7777/api/radio/search?q=relax&search_type=name&limit=5"

# Search by country
curl "http://localhost:7777/api/radio/search?q=Germany&search_type=country"

# Search by tag
curl "http://localhost:7777/api/radio/search?q=jazz&search_type=tag"

# Get station detail
curl "http://localhost:7777/api/radio/station/{uuid}"
```

## Kommende Iterationen

- **Iteration 3**: Preset Mapping (Store Preset to Device)
- **Iteration 4**: Playback + Now Playing (vollständiger E2E Test)
- **Iteration 5**: Frontend UI (React Search Component)

Jede Iteration liefert ein Demo-Script, das auf echten Geräten getestet werden kann.
