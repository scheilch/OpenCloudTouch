# Architecture Analysis: OpenCloudTouch

**Analyse-Datum:** 2026-02-13
**Version:** 0.2.0
**Analyst:** Claude Opus 4.5

---

## Architektur-Übersicht

### High-Level Struktur

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend (React 19)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │
│  │   Pages     │  │ Components  │  │   Hooks     │  │    API    │  │
│  │ Radio,Local │  │ DeviceSwiper│  │ useDevices  │  │ Client    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                │ HTTP/REST
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Backend (FastAPI)                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    API Layer (Routes)                       │   │
│  │  /api/devices  /api/presets  /api/radio  /api/settings     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                │                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                 Service Layer (Business Logic)              │   │
│  │  DeviceService  PresetService  SettingsService              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                │                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                 Repository Layer (Persistence)              │   │
│  │  DeviceRepo    PresetRepo    SettingsRepo                   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                │                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                 Adapter Layer (External APIs)               │   │
│  │  SSDP Discovery  Bose API Client  RadioBrowser API          │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         ▼                      ▼                      ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐
│   SQLite DB     │  │ Bose® Devices   │  │ RadioBrowser.info API   │
│   (Persistence) │  │ (Local Network) │  │ (External Service)      │
└─────────────────┘  └─────────────────┘  └─────────────────────────┘
```

---

## Layer-Analyse

### 1. API Layer (Routes)
**Pfad:** `apps/backend/src/opencloudtouch/*/api/routes.py`

| Modul | Endpoints | Status |
|-------|-----------|--------|
| devices | 5 | ✓ RESTful |
| presets | 5 | ✓ RESTful |
| radio | 2 | ✓ RESTful |
| settings | 3 | ✓ RESTful |

**Pattern:** FastAPI Router mit Dependency Injection

```python
@router.get("/api/devices")
async def get_devices(service: DeviceService = Depends(get_device_service)):
    return await service.get_all_devices()
```

**Bewertung:** ✓ Sauber implementiert

### 2. Service Layer (Business Logic)
**Pfad:** `apps/backend/src/opencloudtouch/*/service.py`

| Service | Verantwortlichkeit |
|---------|-------------------|
| DeviceService | Device CRUD, Discovery orchestration |
| PresetService | Preset CRUD |
| SettingsService | Manual IP management |
| DeviceSyncService | Discovery → Query → Persist |

**Bewertung:** ✓ Gute Trennung, aber DeviceSyncService sollte in services/ liegen

### 3. Repository Layer (Persistence)
**Pfad:** `apps/backend/src/opencloudtouch/*/repository.py`

| Repository | Tabelle | Pattern |
|------------|---------|---------|
| DeviceRepository | devices | BaseRepository + Upsert |
| PresetRepository | presets | BaseRepository + Upsert |
| SettingsRepository | manual_device_ips | BaseRepository |

**Pattern:** BaseRepository Template

```python
class DeviceRepository(BaseRepository):
    async def upsert(self, device: Device) -> Device:
        # INSERT OR REPLACE pattern
```

**Bewertung:** ✓ Konsistentes Pattern

### 4. Adapter Layer (External Systems)
**Pfad:** `apps/backend/src/opencloudtouch/*/adapter.py`

| Adapter | External System |
|---------|-----------------|
| BoseDeviceDiscoveryAdapter | SSDP/UPnP |
| BoseDeviceClientAdapter | Bose SoundTouch API (bosesoundtouchapi) |
| RadioBrowserAdapter | RadioBrowser.info REST API |
| MockRadioAdapter | Mock Data |

**Bewertung:** ✓ Adapter Pattern korrekt angewendet

---

## FINDINGS SUMMARY

| Priorität | Kategorie | Count |
|-----------|-----------|-------|
| P1 | ARCHITECTURE | 0 |
| P2 | ARCHITECTURE | 4 |
| P2 | COUPLING | 2 |
| P3 | CONSISTENCY | 3 |

**TOTAL:** 9 Findings

---

## [P2] [ARCHITECTURE] `interfaces.py` Bug: Method außerhalb Protocol-Klasse

**Datei:** `apps/backend/src/opencloudtouch/devices/interfaces.py`
**Zeilen:** 91-99

**Problem:**
```python
class IDeviceSyncService(Protocol):
    """Protocol for device synchronization operations."""


async def sync(self) -> SyncResult:  # ⚠️ FALSCHE INDENTATION!
    """Synchronize devices to database."""
    ...
```

**Warum kritisch:**
- `sync()` ist NICHT Teil der Protocol-Klasse
- Steht als freie Funktion im Modul-Scope
- Protocol IDeviceSyncService hat KEINE Methoden!

**Fix:**
```python
class IDeviceSyncService(Protocol):
    """Protocol for device synchronization operations."""

    async def sync(self) -> SyncResult:  # ← Korrekte Indentation
        """Synchronize devices to database."""
        ...
```

**Aufwand:** 5min

---

## [P2] [ARCHITECTURE] Inkonsistente Service-Platzierung

**Problem:**
```
devices/
├── service.py          # DeviceService
├── services/           # ← Subfolder für andere Services
│   └── sync_service.py # DeviceSyncService
```

**Warum schlecht:**
- Nicht klar warum sync_service in Subfolder
- Inkonsistent mit anderen Modulen (presets/service.py direkt)

**Fix Option 1:** Flatten
```
devices/
├── device_service.py
├── sync_service.py
```

**Fix Option 2:** Alle Services in services/
```
devices/
├── services/
│   ├── device_service.py
│   └── sync_service.py
```

**Aufwand:** 30min

---

## [P2] [ARCHITECTURE] Factory Functions statt Dependency Injection

**Datei:** `apps/backend/src/opencloudtouch/devices/services/sync_service.py`
**Zeilen:** 88-90, 142

**Problem:**
```python
from opencloudtouch.devices.adapter import get_discovery_adapter, get_device_client

async def _discover_via_ssdp(self) -> List[DiscoveredDevice]:
    discovery = get_discovery_adapter(timeout=self.discovery_timeout)  # Factory!
```

**Warum schlecht:**
- Schwer zu testen (Factory in Service aufgerufen)
- Verletzt Dependency Injection Prinzip
- Factory-Aufruf statt injizierter Dependency

**Fix:**
```python
class DeviceSyncService:
    def __init__(
        self,
        repository: IDeviceRepository,
        discovery_adapter: IDiscoveryAdapter,  # ← Injected
        device_client_factory: Callable[[str], DeviceClient],  # ← Factory injected
        # ...
    ):
        self._discovery = discovery_adapter
        self._client_factory = device_client_factory

    async def _discover_via_ssdp(self) -> List[DiscoveredDevice]:
        return await self._discovery.discover(timeout=self.discovery_timeout)
```

In `main.py`:
```python
sync_service = DeviceSyncService(
    repository=device_repo,
    discovery_adapter=get_discovery_adapter(),  # ← Factory hier aufrufen
    device_client_factory=get_device_client,
    # ...
)
```

**Aufwand:** 45min

---

## [P2] [ARCHITECTURE] Fehlende Radio-Dependency in dependencies.py

**Datei:** `apps/backend/src/opencloudtouch/core/dependencies.py`

**Problem:**
Radio-Modul verwendet Factory direkt in Routes:

```python
# radio/api/routes.py
from opencloudtouch.radio.adapter import get_radio_provider

@router.get("/search")
async def search_stations(...):
    provider = get_radio_provider()  # ← Factory, nicht DI!
```

Vergleich mit anderen Modulen:
```python
# devices/api/routes.py
@router.get("/")
async def get_devices(service: DeviceService = Depends(get_device_service)):
```

**Fix:**
```python
# core/dependencies.py
from opencloudtouch.radio.provider import RadioProvider
from opencloudtouch.radio.adapter import get_radio_provider

async def get_radio_service(request: Request) -> RadioProvider:
    """Get radio provider from app.state."""
    return request.app.state.radio_provider
```

```python
# main.py lifespan
radio_provider = get_radio_provider()
app.state.radio_provider = radio_provider
```

```python
# radio/api/routes.py
@router.get("/search")
async def search_stations(
    provider: RadioProvider = Depends(get_radio_service),
    # ...
):
```

**Aufwand:** 30min

---

## [P2] [COUPLING] Frontend-Backend Type Synchronization

**Problem:**
Types werden separat in Frontend und Backend definiert:

**Frontend:**
```typescript
// components/RadioSearch.tsx
export interface RadioStation {
  stationuuid: string;  // ← "stationuuid"
  name: string;
```

**Backend:**
```python
# radio/provider.py
@dataclass
class RadioStation:
    uuid: str  # ← "uuid"
    name: str
```

**Warum schlecht:**
- Type-Mismatch zwischen Frontend/Backend
- Manuelles Mapping in RadioSearch.tsx
- Änderungen müssen an 2 Stellen gemacht werden

**Fix-Optionen:**

1. **OpenAPI Type Generation:**
```bash
npx openapi-typescript http://localhost:7777/openapi.json -o src/types/api.ts
```

2. **Shared Schema:**
```yaml
# shared/schemas/radio-station.schema.json
{
  "type": "object",
  "properties": {
    "uuid": { "type": "string" },  # Konsistent
    "name": { "type": "string" }
  }
}
```

3. **Backend Response anpassen:**
```python
# radio/api/routes.py
class RadioStationResponse(BaseModel):
    uuid: str = Field(..., alias="stationuuid")  # Oder umgekehrt
```

**Aufwand:** 2-3 Stunden

---

## [P2] [COUPLING] Tight Coupling zu bosesoundtouchapi Library

**Datei:** `apps/backend/src/opencloudtouch/devices/adapter.py`

**Problem:**
Library-spezifische Details leaken durch Adapter:

```python
async def get_device_info(self) -> Device:
    # bosesoundtouchapi specific property names
    return Device(
        device_id=info.DeviceID,      # Library property
        name=info.DeviceName,         # Library property
        model=info.DeviceType,        # Library property
        mac_address=network.MACAddress,
        firmware_version=version.FirmwareVersion,
    )
```

**Warum problematisch:**
- Library-Änderungen brechen Adapter
- Property-Namen sind undokumentiert
- Schwer andere Libraries einzubinden

**Fix:**
```python
class BoseDeviceClientAdapter:
    """Adapter wrapping bosesoundtouchapi library.
    
    Property Mappings (bosesoundtouchapi → Domain):
    - info.DeviceID → device_id
    - info.DeviceName → name
    - info.DeviceType → model
    - network.MACAddress → mac_address
    - version.FirmwareVersion → firmware_version
    """
    
    LIBRARY_MAPPINGS = {
        'device_id': lambda info: info.DeviceID,
        'name': lambda info: info.DeviceName,
        'model': lambda info: info.DeviceType,
        # ...
    }
    
    async def get_device_info(self) -> Device:
        info = await self._client.get_info()
        return Device(
            **{k: mapper(info) for k, mapper in self.LIBRARY_MAPPINGS.items()}
        )
```

**Aufwand:** 45min

---

## [P3] [CONSISTENCY] Modul-Namespace Inkonsistenz

**Problem:**
```
opencloudtouch/
├── devices/          # Plural
├── presets/          # Plural
├── settings/         # Plural
├── radio/            # Singular ⚠️
├── discovery/        # Singular ⚠️
├── db/               # Abbreviation ⚠️
└── api/              # Abbreviation
```

**Fix:**
Alle Plural ODER alle Singular. Empfehlung: Plural für Entities:
- `radios/` oder `radio_providers/`
- `discoveries/` oder `device_discovery/`

**Aufwand:** 30min (nur Refactoring, keine Code-Änderungen)

---

## [P3] [CONSISTENCY] Exception Hierarchy unvollständig

**Datei:** `apps/backend/src/opencloudtouch/core/exceptions.py`

**Problem:**
```python
class OpenCloudTouchError(Exception):
    pass

class DeviceNotFoundError(OpenCloudTouchError):
    pass

class DeviceConnectionError(OpenCloudTouchError):
    pass

class DiscoveryError(OpenCloudTouchError):
    pass

# FEHLT:
# - RadioProviderError
# - PresetError
# - SettingsError
```

Radio-Modul definiert eigene Exceptions:
```python
# radio/providers/radiobrowser.py
class RadioBrowserError(Exception):  # ⚠️ Nicht von OpenCloudTouchError!
```

**Fix:**
```python
# core/exceptions.py
class OpenCloudTouchError(Exception):
    """Base exception for all OpenCloudTouch errors."""
    pass

# Device exceptions
class DeviceError(OpenCloudTouchError): pass
class DeviceNotFoundError(DeviceError): pass
class DeviceConnectionError(DeviceError): pass
class DiscoveryError(DeviceError): pass

# Radio exceptions  
class RadioError(OpenCloudTouchError): pass
class RadioProviderError(RadioError): pass
class RadioStationNotFoundError(RadioError): pass

# Preset exceptions
class PresetError(OpenCloudTouchError): pass
class PresetNotFoundError(PresetError): pass

# Settings exceptions
class SettingsError(OpenCloudTouchError): pass
class InvalidIPError(SettingsError): pass
```

**Aufwand:** 30min

---

## [P3] [CONSISTENCY] Pydantic Model vs Dataclass Inkonsistenz

**Problem:**
Einige Domänen-Modelle sind Dataclasses, andere Pydantic:

```python
# devices/models.py - Dataclass
@dataclass
class SyncResult:
    discovered: int
    synced: int
    failed: int

# presets/models.py - Pydantic
class Preset(BaseModel):
    device_id: str
    preset_number: int
```

**Warum problematisch:**
- Unterschiedliche Serialization
- Unterschiedliche Validierung
- Inkonsistente API

**Fix:**
Alle auf Pydantic umstellen (FastAPI-native):

```python
# devices/models.py
from pydantic import BaseModel

class SyncResult(BaseModel):
    discovered: int
    synced: int
    failed: int
```

**Aufwand:** 15min

---

## POSITIVE ARCHITEKTUR-ASPEKTE

### 1. Saubere Layer-Trennung ✓
```
Routes → Services → Repositories → Adapters
```

### 2. Protocol-basierte Interfaces ✓
```python
class IDeviceRepository(Protocol):
    async def get_all(self) -> List[Device]: ...
```

### 3. FastAPI Dependency Injection ✓
```python
async def get_device_service(request: Request) -> DeviceService:
    return request.app.state.device_service
```

### 4. Lifespan-basierte Initialization ✓
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize all services
    yield
    # Cleanup
```

### 5. Centralized Exception Handling ✓
```python
@app.exception_handler(DeviceNotFoundError)
async def device_not_found_handler(request, exc):
    return JSONResponse(status_code=404, ...)
```

### 6. Configuration via Pydantic Settings ✓
```python
class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OCT_")
```

---

## ARCHITEKTUR-DIAGRAMME

### Dependency Flow
```
┌─────────────┐
│   Routes    │
│  (FastAPI)  │
└──────┬──────┘
       │ Depends()
       ▼
┌─────────────┐
│  Services   │
│  (Business) │
└──────┬──────┘
       │ Constructor Injection
       ▼
┌─────────────┐      ┌─────────────┐
│ Repositories│      │  Adapters   │
│  (SQLite)   │      │ (External)  │
└─────────────┘      └─────────────┘
```

### Module Dependencies
```
core/
 ├── config.py (settings)
 ├── dependencies.py (DI)
 ├── exceptions.py (errors)
 └── logging.py

devices/ [depends: core, discovery]
 ├── service.py
 ├── repository.py
 └── adapter.py

presets/ [depends: core]
 ├── service.py
 └── repository.py

radio/ [depends: core]
 ├── provider.py (interface)
 └── providers/radiobrowser.py (impl)

settings/ [depends: core]
 ├── service.py
 └── repository.py
```

---

## 💾 SESSION-STATE (für Resume)

**Letzter Stand:** 2026-02-13
**Aktuelles Dokument:** 02_ARCHITECTURE_ANALYSIS.md ✅
**Fortschritt:** 5/9 Dokumente erstellt

### Kumulative Findings:
- P1: 2
- P2: 32
- P3: 21

### Abgeschlossen:
- [x] 01_PROJECT_OVERVIEW.md
- [x] 02_ARCHITECTURE_ANALYSIS.md
- [x] 03_BACKEND_CODE_REVIEW.md
- [x] 04_FRONTEND_CODE_REVIEW.md
- [x] 05_TESTS_ANALYSIS.md

### Noch offen:
- [ ] 06_BUILD_DEPLOY_ANALYSIS.md
- [ ] 07_DOCUMENTATION_GAPS.md
- [ ] 08_DEPENDENCY_AUDIT.md
- [ ] 09_ROADMAP.md

**Nächster Schritt:** Build & Deployment Analysis
