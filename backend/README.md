# CloudTouch Backend

FastAPI-basierter REST-API-Server für Bose SoundTouch Geräte.

## Installation

```bash
cd backend
pip install -e .[dev]
```

## Ausführen

```bash
# Als Modul
python -m cloudtouch

# Mit Uvicorn direkt
uvicorn cloudtouch.main:app --reload
```

## Tests

```bash
cd backend
pytest
pytest --cov=cloudtouch --cov-report=html
```

## Struktur

- `src/cloudtouch/` - Hauptpaket
  - `core/` - Shared Infrastructure (Config, Logging, Exceptions)
  - `devices/` - Device Management & Discovery
  - `radio/` - Radio Station Search
- `tests/` - Test Suite
  - `unit/` - Unit Tests
  - `integration/` - Integration Tests
  - `e2e/` - End-to-End Tests
