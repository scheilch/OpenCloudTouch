# 01 - OpenCloudTouch Project Overview

**Stand**: 2026-02-12  
**Analyst**: Principal Software Engineer (AI-assisted)

---

## Projekt-Zusammenfassung

**OpenCloudTouch (OCT)** ist eine lokale Open-Source-Ersatzlösung für eingestellte Cloud-Funktionen von Bose® SoundTouch®-Geräten.

**Zielbild:**
- Ein Docker-Container mit Backend + Frontend
- Web-UI für Radio-Presets, Now Playing, Multiroom
- Physische Preset-Tasten am Gerät funktionieren wieder
- Laien-freundliche Bedienung

**Aktueller Stand:** Funktionsfähiger MVP mit Grundfunktionen, aber technische Schulden und unvollständige Features.

---

## Datei-Inventar

### Backend – `apps/backend/src/opencloudtouch/`

| Datei | Zeilen | Status | Findings |
|-------|--------|--------|----------|
| `__init__.py` | 4 | ✓ | OK |
| `__main__.py` | 9 | ✓ | OK |
| `main.py` | 196 | ✓ | P1: 1, P2: 2 |
| **core/** | | | |
| `__init__.py` | 1 | ✓ | OK (leer) |
| `config.py` | 168 | ✓ | P2: 1 |
| `dependencies.py` | 112 | ✓ | P2: 1 |
| `exceptions.py` | 33 | ✓ | OK |
| `logging.py` | 107 | ✓ | OK |
| `repository.py` | 70 | ✓ | OK |
| **devices/** | | | |
| `__init__.py` | ~10 | ✓ | OK |
| `adapter.py` | 271 | ✓ | P2: 1 |
| `capabilities.py` | 244 | ✓ | P3: 1 |
| `client.py` | 65 | ✓ | OK |
| `mock_client.py` | 127 | ✓ | OK |
| `repository.py` | 233 | ✓ | P3: 1 |
| `service.py` | 169 | ✓ | OK |
| **devices/api/** | | | |
| `__init__.py` | ~5 | ✓ | OK |
| `routes.py` | 191 | ✓ | P3: 1 |
| **devices/discovery/** | | | |
| `__init__.py` | 7 | ✓ | OK |
| `ssdp.py` | 295 | ✓ | P2: 1 |
| `manual.py` | 44 | ✓ | OK |
| `mock.py` | 84 | ✓ | OK |
| **devices/services/** | | | |
| `__init__.py` | ~5 | ✓ | OK |
| `sync_service.py` | 187 | ✓ | OK |
| **presets/** | | | |
| `__init__.py` | ~5 | ✓ | OK |
| `models.py` | 75 | ✓ | OK |
| `repository.py` | 251 | ✓ | P3: 1 |
| `service.py` | 122 | ✓ | OK |
| **presets/api/** | | | |
| `__init__.py` | ~5 | ✓ | OK |
| `descriptor_service.py` | 73 | ✓ | OK |
| `routes.py` | 203 | ✓ | OK |
| `station_routes.py` | 75 | ✓ | OK |
| **radio/** | | | |
| `__init__.py` | ~5 | ✓ | OK |
| `adapter.py` | 47 | ✓ | OK |
| `provider.py` | 125 | ✓ | OK |
| **radio/api/** | | | |
| `__init__.py` | ~5 | ✓ | OK |
| `routes.py` | 178 | ✓ | P2: 1 |
| **radio/providers/** | | | |
| `__init__.py` | ~5 | ✓ | OK |
| `radiobrowser.py` | 274 | ✓ | OK |
| `mock.py` | ~80 | ✓ | OK |
| **settings/** | | | |
| `__init__.py` | ~5 | ✓ | OK |
| `repository.py` | 113 | ✓ | P2: 1 |
| `routes.py` | 100 | ✓ | P2: 1 |
| `service.py` | 121 | ✓ | OK |
| **discovery/** | | | |
| `__init__.py` | 46 | ✓ | OK |
| **db/** | | | |
| `__init__.py` | 5 | ✓ | OK |
| **api/** | | | |
| `__init__.py` | 5 | ✓ | OK |

**Backend Total:** ~45 Python Dateien, ~3500 Zeilen

### Frontend – `apps/frontend/src/`

| Datei | Zeilen | Status | Findings |
|-------|--------|--------|----------|
| `main.tsx` | 14 | ✓ | OK |
| `App.tsx` | 128 | ✓ | P2: 1 |
| `vite-env.d.ts` | 1 | ✓ | OK |
| **api/** | | | |
| `presets.ts` | 121 | ✓ | P3: 1 |
| **components/** | | | |
| `DeviceSwiper.tsx` | 136 | ✓ | OK |
| `DeviceImage.tsx` | ~50 | ✓ | OK |
| `EmptyState.tsx` | ~60 | ✓ | OK |
| `Navigation.tsx` | 35 | ✓ | OK |
| `NowPlaying.tsx` | 47 | ✓ | OK |
| `PresetButton.tsx` | ~80 | ✓ | OK |
| `RadioSearch.tsx` | 144 | ✓ | P3: 1 |
| `Toast.tsx` | ~40 | ✓ | OK |
| `VolumeSlider.tsx` | ~70 | ✓ | OK |
| **pages/** | | | |
| `RadioPresets.tsx` | 207 | ✓ | P2: 1 |
| `LocalControl.tsx` | ~100 | - | Stub |
| `MultiRoom.tsx` | ~100 | - | Stub |
| `Firmware.tsx` | ~80 | - | Stub |
| `Settings.tsx` | 196 | ✓ | P2: 1 |
| `Licenses.tsx` | ~60 | ✓ | OK |
| **contexts/** | | | |
| `ToastContext.tsx` | ~80 | ✓ | OK |
| **utils/** | | | |
| `deviceImages.ts` | ~30 | ✓ | OK |

**Frontend Total:** ~23 TypeScript/TSX Dateien, ~1800 Zeilen

---

## Feature-Vollständigkeit

| Feature | Status | Kommentar |
|---------|--------|-----------|
| SSDP Discovery | ✅ Fertig | Funktioniert mit WSL2 Mirror Mode |
| Manual IP Fallback | ✅ Fertig | Settings-Seite implementiert |
| Radio Search | ✅ Fertig | RadioBrowser API Integration |
| Preset Management | ✅ Fertig | Set, Get, Clear funktioniert |
| Now Playing | ⚠️ Partial | Backend existiert, Frontend-Integration fehlt |
| Volume Control | ⚠️ UI only | Backend-API fehlt |
| Multiroom/Zones | ❌ Stub | Nur Placeholder-Seite |
| Device Grouping | ❌ Stub | Nur Placeholder-Seite |
| Firmware Info | ⚠️ UI only | Backend liefert Daten, UI zeigt wenig |
| Device Capabilities | ✅ Fertig | Backend existiert mit Capability Detection |
| Station Descriptors | ✅ Fertig | URL-Endpunkte für physische Preset-Tasten |

---

## Was funktioniert

1. **Device Discovery** – SSDP findet Bose-Geräte im Netzwerk
2. **Device Sync** – Geräte werden in SQLite gespeichert
3. **Radio Search** – RadioBrowser API funktioniert
4. **Preset Assignment** – Presets 1-6 können belegt werden
5. **Mock Mode** – Vollständiger Mock für Testing ohne Hardware

## Was fehlt für MVP

1. **Now Playing Integration** – Frontend zeigt statische Daten
2. **Volume Control** – Backend-Endpunkt fehlt
3. **Playback Control** – Kein Play/Pause/Skip
4. **Multiroom** – Komplett unimplementiert
5. **Error Recovery** – Keine automatische Reconnect-Logik

## Kritische Issues

| # | Priorität | Typ | Beschreibung |
|---|-----------|-----|--------------|
| 1 | P1 | SECURITY | Path Traversal in SPA Catch-All Route (`main.py:181-186`) |
| 2 | P2 | ARCHITECTURE | Global Singleton DI Pattern (veraltet) |
| 3 | P2 | SECURITY | CORS `allow_origins=["*"]` in Production |
| 4 | P2 | BUG | Settings-Route POST vs PUT Semantik falsch |

---

## Technische Schulden

1. **Veraltetes DI Pattern** – Module-level Singletons statt `app.state`
2. **Duplizierter Code** – RadioStation Model in 2 Dateien definiert
3. **Fehlende Type Exports** – TypeScript Interfaces nicht zentral
4. **Inconsistent Error Handling** – Teils HTTPException, teils rohe Exceptions
5. **Kein Request Validation** – Einige Endpoints ohne Pydantic Models

---

## 💾 SESSION-STATE (für Resume)

**Letzter Stand:** 2026-02-12
**Aktuelles Dokument:** 01_PROJECT_OVERVIEW.md
**Fortschritt:** Datei-Inventar erstellt, Übersicht dokumentiert

### Nächste Schritte:
1. `03_BACKEND_CODE_REVIEW.md` – Detaillierte Findings pro Datei
2. `04_FRONTEND_CODE_REVIEW.md` – Frontend Findings
3. `09_ROADMAP.md` – Priorisierter Aktionsplan

---
