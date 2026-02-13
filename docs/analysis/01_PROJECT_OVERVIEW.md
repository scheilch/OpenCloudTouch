# Project Overview: OpenCloudTouch (OCT)

**Analyse-Datum:** 2026-02-13
**Version:** 0.2.0
**Analyst:** Claude Opus 4.5

---

## 1. Projekt-Zusammenfassung

**OpenCloudTouch (OCT)** ist eine Open-Source-Lösung zur lokalen Steuerung von Bose® SoundTouch® Geräten nach Cloud-Abschaltung.

### Zielbild
- Ein Docker-Container (Backend + Frontend)
- Web-UI für Radio-Presets, Now Playing, Multiroom
- Physische Preset-Tasten am Gerät funktionieren wieder
- Laien-freundliche Bedienung

### Aktueller Implementierungsstand

| Feature | Status | Anmerkungen |
|---------|--------|-------------|
| Device Discovery (SSDP) | ✅ Implementiert | Mock + Real Mode |
| Device Sync | ✅ Implementiert | Speichert in SQLite |
| Preset Management | ✅ Implementiert | CRUD für Presets 1-6 |
| Radio Station Search | ✅ Implementiert | RadioBrowser API |
| Station Descriptors | ✅ Implementiert | XML für SoundTouch |
| Settings (Manual IPs) | ✅ Implementiert | Persistiert |
| Web-UI (React) | ✅ Implementiert | Mobile-First |
| Now Playing | ⚠️ UI vorhanden, Backend TODO | Kein Polling |
| Playback Control | ❌ Nicht implementiert | Phase 4 geplant |
| Multiroom Zones | ⚠️ Capabilities erkannt | Steuerung fehlt |
| Volume Control | ⚠️ UI vorhanden | Backend TODO |

---

## 2. Datei-Inventar

### 2.1 Backend Python Dateien (`apps/backend/src/opencloudtouch/`)

| Pfad | Datei | Zeilen | Status |
|------|-------|--------|--------|
| `/` | `__init__.py` | ~5 | ☐ |
| `/` | `__main__.py` | ~10 | ☐ |
| `/` | `main.py` | 304 | ☐ |
| `/core/` | `__init__.py` | ~5 | ☐ |
| `/core/` | `config.py` | ~170 | ☐ |
| `/core/` | `dependencies.py` | ~50 | ☐ |
| `/core/` | `exceptions.py` | ~40 | ☐ |
| `/core/` | `logging.py` | ~115 | ☐ |
| `/core/` | `repository.py` | ~70 | ☐ |
| `/devices/` | `__init__.py` | ~5 | ☐ |
| `/devices/` | `adapter.py` | 271 | ☐ |
| `/devices/` | `capabilities.py` | 244 | ☐ |
| `/devices/` | `client.py` | ~65 | ☐ |
| `/devices/` | `interfaces.py` | ~50 | ☐ |
| `/devices/` | `mock_client.py` | ~250 | ☐ |
| `/devices/` | `models.py` | ~50 | ☐ |
| `/devices/` | `repository.py` | ~250 | ☐ |
| `/devices/` | `service.py` | 178 | ☐ |
| `/devices/discovery/` | `__init__.py` | ~5 | ☐ |
| `/devices/discovery/` | `manual.py` | ~50 | ☐ |
| `/devices/discovery/` | `mock.py` | ~80 | ☐ |
| `/devices/discovery/` | `ssdp.py` | 295 | ☐ |
| `/devices/services/` | `__init__.py` | ~5 | ☐ |
| `/devices/services/` | `sync_service.py` | ~150 | ☐ |
| `/devices/api/` | `__init__.py` | ~5 | ☐ |
| `/devices/api/` | `routes.py` | 198 | ☐ |
| `/discovery/` | `__init__.py` | ~30 | ☐ |
| `/presets/` | `__init__.py` | ~5 | ☐ |
| `/presets/` | `models.py` | ~60 | ☐ |
| `/presets/` | `repository.py` | 251 | ☐ |
| `/presets/` | `service.py` | ~130 | ☐ |
| `/presets/api/` | `__init__.py` | ~5 | ☐ |
| `/presets/api/` | `descriptor_service.py` | ~100 | ☐ |
| `/presets/api/` | `routes.py` | ~150 | ☐ |
| `/presets/api/` | `station_routes.py` | ~80 | ☐ |
| `/radio/` | `__init__.py` | ~5 | ☐ |
| `/radio/` | `adapter.py` | ~50 | ☐ |
| `/radio/` | `provider.py` | ~130 | ☐ |
| `/radio/api/` | `__init__.py` | ~5 | ☐ |
| `/radio/api/` | `routes.py` | ~100 | ☐ |
| `/radio/providers/` | `__init__.py` | ~5 | ☐ |
| `/radio/providers/` | `mock.py` | ~80 | ☐ |
| `/radio/providers/` | `radiobrowser.py` | ~150 | ☐ |
| `/settings/` | `__init__.py` | ~5 | ☐ |
| `/settings/` | `repository.py` | ~100 | ☐ |
| `/settings/` | `routes.py` | ~80 | ☐ |
| `/settings/` | `service.py` | ~60 | ☐ |
| `/db/` | `__init__.py` | ~10 | ☐ |
| `/api/` | `__init__.py` | ~10 | ☐ |

**Total Backend:** ~48 Python Dateien, ~4000+ Zeilen

---

### 2.2 Frontend TypeScript/React Dateien (`apps/frontend/src/`)

| Pfad | Datei | Zeilen (est.) | Status |
|------|-------|---------------|--------|
| `/` | `App.tsx` | 112 | ☐ |
| `/` | `main.tsx` | 26 | ☐ |
| `/` | `App.css` | ~100 | ☐ |
| `/` | `index.css` | ~50 | ☐ |
| `/` | `vite-env.d.ts` | ~5 | ☐ |
| `/api/` | `devices.ts` | ~80 | ☐ |
| `/api/` | `presets.ts` | ~100 | ☐ |
| `/api/` | `settings.ts` | ~50 | ☐ |
| `/components/` | `DeviceImage.tsx` | ~50 | ☐ |
| `/components/` | `DeviceImage.test.tsx` | ~30 | ☐ |
| `/components/` | `DeviceSwiper.tsx` | ~100 | ☐ |
| `/components/` | `DeviceSwiper.css` | ~80 | ☐ |
| `/components/` | `EmptyState.tsx` | ~50 | ☐ |
| `/components/` | `EmptyState.css` | ~30 | ☐ |
| `/components/` | `ErrorBoundary.tsx` | ~80 | ☐ |
| `/components/` | `ErrorBoundary.css` | ~20 | ☐ |
| `/components/` | `LoadingSkeleton.tsx` | ~30 | ☐ |
| `/components/` | `LoadingSkeleton.css` | ~20 | ☐ |
| `/components/` | `Navigation.tsx` | ~80 | ☐ |
| `/components/` | `Navigation.css` | ~100 | ☐ |
| `/components/` | `NowPlaying.tsx` | ~60 | ☐ |
| `/components/` | `NowPlaying.css` | ~50 | ☐ |
| `/components/` | `PresetButton.tsx` | ~100 | ☐ |
| `/components/` | `PresetButton.css` | ~80 | ☐ |
| `/components/` | `RadioSearch.tsx` | ~200 | ☐ |
| `/components/` | `RadioSearch.css` | ~100 | ☐ |
| `/components/` | `Toast.tsx` | ~60 | ☐ |
| `/components/` | `Toast.css` | ~40 | ☐ |
| `/components/` | `VolumeSlider.tsx` | ~80 | ☐ |
| `/components/` | `VolumeSlider.css` | ~50 | ☐ |
| `/pages/` | `RadioPresets.tsx` | 220 | ☐ |
| `/pages/` | `RadioPresets.css` | ~100 | ☐ |
| `/pages/` | `LocalControl.tsx` | ~150 | ☐ |
| `/pages/` | `LocalControl.css` | ~50 | ☐ |
| `/pages/` | `MultiRoom.tsx` | ~100 | ☐ |
| `/pages/` | `MultiRoom.css` | ~50 | ☐ |
| `/pages/` | `Firmware.tsx` | ~100 | ☐ |
| `/pages/` | `Firmware.css` | ~30 | ☐ |
| `/pages/` | `Settings.tsx` | ~150 | ☐ |
| `/pages/` | `Settings.css` | ~50 | ☐ |
| `/pages/` | `Licenses.tsx` | ~80 | ☐ |
| `/pages/` | `Licenses.css` | ~30 | ☐ |
| `/contexts/` | `ToastContext.tsx` | ~80 | ☐ |
| `/hooks/` | `useDevices.ts` | ~45 | ☐ |
| `/hooks/` | `useSettings.ts` | ~60 | ☐ |
| `/utils/` | `deviceImages.ts` | ~50 | ☐ |
| `/utils/` | `deviceImages.test.ts` | ~30 | ☐ |

**Total Frontend:** ~46 Dateien, ~3200+ Zeilen

---

### 2.3 Backend Test-Dateien (`apps/backend/tests/`)

| Pfad | Datei | Status |
|------|-------|--------|
| `/` | `conftest.py` | ☐ |
| `/` | `__init__.py` | ☐ |
| `/unit/` | `test_main.py` | ☐ |
| `/unit/core/` | `test_config.py` | ☐ |
| `/unit/core/` | `test_logging.py` | ☐ |
| `/unit/devices/` | `test_adapter.py` | ☐ |
| `/unit/devices/` | `test_capabilities.py` | ☐ |
| `/unit/devices/` | `test_client.py` | ☐ |
| `/unit/devices/` | `test_device_service.py` | ☐ |
| `/unit/devices/` | `test_mock_client.py` | ☐ |
| `/unit/devices/` | `test_repository.py` | ☐ |
| `/unit/devices/` | `test_sync_service.py` | ☐ |
| `/unit/devices/api/` | `test_device_routes.py` | ☐ |
| `/unit/devices/discovery/` | `test_discovery.py` | ☐ |
| `/unit/devices/discovery/` | `test_manual.py` | ☐ |
| `/unit/devices/discovery/` | `test_mock.py` | ☐ |
| `/unit/devices/discovery/` | `test_ssdp.py` | ☐ |
| `/unit/presets/` | `test_models.py` | ☐ |
| `/unit/presets/` | `test_repository.py` | ☐ |
| `/unit/presets/api/` | `test_descriptor_service.py` | ☐ |
| `/unit/radio/` | `test_provider.py` | ☐ |
| `/unit/radio/api/` | `test_radio_routes.py` | ☐ |
| `/unit/radio/providers/` | `test_radiobrowser.py` | ☐ |
| `/unit/settings/` | `test_repository.py` | ☐ |
| `/unit/settings/` | `test_settings_service.py` | ☐ |
| `/integration/` | `test_api_integration.py` | ☐ |
| `/integration/` | `test_cross_model_compatibility.py` | ☐ |
| `/integration/` | `test_device_flow.py` | ☐ |
| `/integration/` | `test_main.py` | ☐ |
| `/integration/` | `test_real_api_stack.py` | ☐ |
| `/integration/presets/` | `test_preset_routes.py` | ☐ |
| `/integration/settings/` | `test_routes.py` | ☐ |
| `/real/` | `test_discovery_real.py` | ☐ |
| `/e2e/` | `demo_iteration0.py` | ☐ |
| `/e2e/` | `demo_iteration1.py` | ☐ |
| `/e2e/` | `demo_iteration2.py` | ☐ |
| `/e2e/` | `demo_iteration3.py` | ☐ |
| `/e2e/` | `demo_capability_detection.py` | ☐ |

**Total Tests:** ~38 Test-Dateien

---

## 3. Architektur-Überblick

### 3.1 Backend (Python/FastAPI)

```
┌──────────────────────────────────────────────────────────────┐
│                      FastAPI App (main.py)                   │
├──────────────────────────────────────────────────────────────┤
│  API Layer                                                   │
│  ├── devices/api/routes.py    (Device CRUD, Discovery)       │
│  ├── presets/api/routes.py    (Preset CRUD)                  │
│  ├── presets/api/station_routes.py (Station Descriptors)     │
│  ├── radio/api/routes.py      (Station Search)               │
│  └── settings/routes.py       (User Settings)                │
├──────────────────────────────────────────────────────────────┤
│  Service Layer                                               │
│  ├── devices/service.py       (DeviceService)                │
│  ├── devices/services/sync_service.py (DeviceSyncService)    │
│  ├── presets/service.py       (PresetService)                │
│  └── settings/service.py      (SettingsService)              │
├──────────────────────────────────────────────────────────────┤
│  Repository Layer (aiosqlite)                                │
│  ├── core/repository.py       (BaseRepository)               │
│  ├── devices/repository.py    (DeviceRepository)             │
│  ├── presets/repository.py    (PresetRepository)             │
│  └── settings/repository.py   (SettingsRepository)           │
├──────────────────────────────────────────────────────────────┤
│  Adapter Layer                                               │
│  ├── devices/adapter.py       (BoseDeviceClientAdapter)      │
│  ├── devices/discovery/ssdp.py (SSDPDiscovery)               │
│  ├── radio/providers/radiobrowser.py (RadioBrowserAdapter)   │
│  └── devices/mock_client.py   (MockDeviceClient)             │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 Frontend (React/TypeScript)

```
┌──────────────────────────────────────────────────────────────┐
│                         App.tsx                              │
├──────────────────────────────────────────────────────────────┤
│  Pages                                                       │
│  ├── RadioPresets.tsx   (Main: Device selection + Presets)   │
│  ├── LocalControl.tsx   (Playback controls - TODO)           │
│  ├── MultiRoom.tsx      (Zone management - TODO)             │
│  ├── Firmware.tsx       (Firmware info)                      │
│  ├── Settings.tsx       (Manual IPs, Config)                 │
│  └── Licenses.tsx       (OSS Licenses)                       │
├──────────────────────────────────────────────────────────────┤
│  Components                                                  │
│  ├── DeviceSwiper.tsx   (Swipeable device cards)             │
│  ├── NowPlaying.tsx     (Now Playing display)                │
│  ├── PresetButton.tsx   (Preset 1-6 buttons)                 │
│  ├── RadioSearch.tsx    (Station search modal)               │
│  ├── VolumeSlider.tsx   (Volume control)                     │
│  └── Navigation.tsx     (Bottom navigation)                  │
├──────────────────────────────────────────────────────────────┤
│  Hooks & API                                                 │
│  ├── hooks/useDevices.ts (TanStack Query)                    │
│  ├── api/devices.ts      (Device API)                        │
│  ├── api/presets.ts      (Preset API)                        │
│  └── api/settings.ts     (Settings API)                      │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Kritische Beobachtungen (Erste Einschätzung)

### 4.1 Positive Aspekte

1. **Saubere Schichtentrennung:** API → Service → Repository Pattern konsistent umgesetzt
2. **Mock Mode:** Vollständiger Mock-Stack für Tests ohne echte Geräte
3. **DI via app.state:** Modern (kürzlich migriert von Global Singletons)
4. **Test Coverage:** 348 Backend Tests, Coverage >80%
5. **TypeScript Frontend:** Typisierung vorhanden
6. **TanStack Query:** Moderne Data Fetching Lösung

### 4.2 Potenzielle Probleme (zu verifizieren)

1. **Now Playing nicht implementiert:** UI-Skeleton vorhanden, Backend fehlt
2. **Playback Control fehlt:** "TODO Phase 4" in RadioPresets.tsx
3. **Volume Control fehlt:** VolumeSlider hat kein Backend
4. **Multiroom Steuerung fehlt:** Nur Capabilities-Erkennung
5. **Error Handling:** Zu prüfen ob vollständig
6. **Path Traversal:** main.py hat bereits Fix (zu verifizieren)

### 4.3 Fehlende Features für MVP

| Feature | Priorität | Aufwand (Schätzung) |
|---------|-----------|---------------------|
| Now Playing Polling | P1 | 4h |
| Volume Control Backend | P1 | 2h |
| Play Preset Backend | P1 | 4h |
| Multiroom Zone Control | P2 | 8h |
| WebSocket Live Updates | P3 | 8h |

---

## 5. Nächste Schritte

1. **03_BACKEND_CODE_REVIEW.md** - Zeile-für-Zeile Analyse aller Backend-Dateien
2. **04_FRONTEND_CODE_REVIEW.md** - Zeile-für-Zeile Analyse aller Frontend-Dateien
3. **05_TESTS_ANALYSIS.md** - Testabdeckung und Testqualität
4. **09_ROADMAP.md** - Priorisierter Aktionsplan

---

## 💾 SESSION-STATE (für Resume)

**Letzter Stand:** 2026-02-13 
**Aktuelles Dokument:** 01_PROJECT_OVERVIEW.md ✅
**Fortschritt:** 1/9 Dokumente erstellt

### Abgeschlossen:
- [x] 01_PROJECT_OVERVIEW.md

### Noch offen:
- [ ] 03_BACKEND_CODE_REVIEW.md
- [ ] 04_FRONTEND_CODE_REVIEW.md
- [ ] 05_TESTS_ANALYSIS.md
- [ ] 02_ARCHITECTURE_ANALYSIS.md
- [ ] 06_BUILD_DEPLOY_ANALYSIS.md
- [ ] 07_DOCUMENTATION_GAPS.md
- [ ] 08_DEPENDENCY_AUDIT.md
- [ ] 09_ROADMAP.md

**Nächster Schritt:** Starte Backend Code Review mit core/config.py
