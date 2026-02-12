# 02 Architecture Analysis

**Projekt**: OpenCloudTouch  
**Datum**: 2026-02-11  
**Analyst**: GitHub Copilot (Claude Opus 4.5)

---

## Executive Summary

Die Architektur folgt grundsätzlich Clean Architecture Prinzipien mit klarer Schichtentrennung. Hauptprobleme: Global Singletons statt FastAPI app.state, fehlende Interface-Abstraktion, unvollständiges Repository-Pattern.

**Architectural Health Score**: 68/100

---

## 1. Ist-Architektur

### 1.1 Schichtenmodell (Implemented)

```
┌─────────────────────────────────────────────────────────┐
│  Presentation Layer (FastAPI Routes)                    │
│  - main.py: /health, SPA catch-all                      │
│  - devices/routes.py: /api/devices/*                    │
│  - presets/routes.py: /api/presets/*                    │
│  - settings/routes.py: /api/settings/*                  │
│  - radio/routes.py: /api/radio/*                        │
├─────────────────────────────────────────────────────────┤
│  Business Logic Layer (Services)                        │
│  - devices/service.py: DeviceService                    │
│  - devices/services/sync_service.py: DeviceSyncService  │
│  - presets/service.py: PresetService                    │
│  - settings/service.py: SettingsService                 │
│  - presets/descriptor_service.py: StationDescriptor     │
├─────────────────────────────────────────────────────────┤
│  Domain Layer (Models + Repositories)                   │
│  - devices/repository.py: Device Model + DB Access      │
│  - presets/models.py: Preset Model                      │
│  - presets/repository.py: PresetRepository              │
│  - settings/repository.py: SettingsRepository           │
├─────────────────────────────────────────────────────────┤
│  Adapter Layer (External Systems)                       │
│  - devices/adapter.py: BoseDeviceDiscoveryAdapter       │
│  - devices/client.py: BoseDeviceClient (bosesoundtouch) │
│  - devices/mock_client.py: MockBoseDeviceClient         │
│  - radio/adapter.py: RadioAdapter (→ Providers)         │
│  - radio/providers/radiobrowser.py: RadioBrowserProvider│
├─────────────────────────────────────────────────────────┤
│  Infrastructure Layer (Core Services)                   │
│  - core/config.py: AppConfig (Pydantic)                 │
│  - core/dependencies.py: DI Container (Singletons)      │
│  - core/logging.py: Structured Logging                  │
│  - core/exceptions.py: Custom Exception Hierarchy       │
│  - devices/discovery/: SSDP, Manual, Mock               │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Dependency Flow

```
Routes (Presentation)
    │
    ▼
Services (Business Logic)
    │
    ├── Repositories (Data Access)
    │       │
    │       ▼
    │   SQLite (aiosqlite)
    │
    └── Adapters (External)
            │
            ├── bosesoundtouchapi (Bose Devices)
            └── httpx (RadioBrowser API)
```

**✅ Positiv**: Dependencies fließen von außen nach innen (Clean Architecture Regel)  
**⚠️ Problem**: Keine Abstraktionen (Interfaces/Protocols) zwischen Schichten

---

## 2. Architektur-Findings

### [ARCH-01] Global Singleton DI Pattern
**Severity**: P2 (Refactoring)  
**Location**: [core/dependencies.py](../../apps/backend/src/opencloudtouch/core/dependencies.py#L1-L114)

```python
# IST (Z. 20-30): Module-level Globals
_device_repo_instance: DeviceRepository | None = None
_device_service_instance: DeviceService | None = None
_preset_repo_instance: PresetRepository | None = None
```

**Problem**: 
- Singletons leben außerhalb FastAPI Lifecycle
- Kein Garbage Collection bei Shutdown
- Schwer zu testen ohne globalen State Reset

**SOLL: app.state Pattern**
```python
# In main.py lifespan():
async with lifespan(app):
    app.state.device_repo = DeviceRepository(config.effective_db_path)
    await app.state.device_repo.initialize()
    yield
    await app.state.device_repo.close()

# In dependencies.py:
def get_device_repo(request: Request) -> DeviceRepository:
    return request.app.state.device_repo
```

---

### [ARCH-02] Fehlende Protocol/Interface Abstraktion
**Severity**: P2 (Maintainability)  
**Location**: Alle Module

**Problem**: Konkrete Klassen statt Abstractions

```python
# IST: Concrete dependency
class DeviceService:
    def __init__(
        self,
        repository: DeviceRepository,  # Konkrete Klasse
        sync_service: DeviceSyncService,  # Konkrete Klasse
        discovery_adapter: BoseDeviceDiscoveryAdapter,  # Konkrete Klasse
    ):
```

**SOLL: Protocol-basierte Abstraktion**
```python
# In devices/interfaces.py (NEU)
from typing import Protocol

class IDeviceRepository(Protocol):
    async def get_all(self) -> list[Device]: ...
    async def get_by_id(self, device_id: str) -> Device | None: ...
    async def upsert(self, device: Device) -> None: ...

class IDiscoveryAdapter(Protocol):
    async def discover(self, timeout: int = 10) -> list[DiscoveredDevice]: ...

# In devices/service.py
class DeviceService:
    def __init__(
        self,
        repository: IDeviceRepository,  # Protocol
        discovery_adapter: IDiscoveryAdapter,  # Protocol
    ):
```

---

### [ARCH-03] Incomplete Repository Pattern
**Severity**: P3 (Code Smell)  
**Location**: [devices/repository.py](../../apps/backend/src/opencloudtouch/devices/repository.py)

**Problem**: Model (Device) und Repository in gleicher Datei

```python
# Z. 10-25: Device Model
@dataclass
class Device:
    device_id: str
    ip: str
    # ...

# Z. 40+: Repository
class DeviceRepository:
    # ...
```

**SOLL**: Separate files für Model und Repository
```
devices/
├── models.py       # Device dataclass
├── repository.py   # DeviceRepository
├── service.py      # DeviceService
└── interfaces.py   # Protocols
```

---

### [ARCH-04] Service Constructor Complexity
**Severity**: P3 (Maintainability)  
**Location**: [devices/service.py](../../apps/backend/src/opencloudtouch/devices/service.py#L25-L40)

```python
class DeviceService:
    def __init__(
        self,
        repository: DeviceRepository,
        sync_service: DeviceSyncService,
        discovery_adapter: BoseDeviceDiscoveryAdapter,
        device_client_factory: Callable[[str], BoseDeviceClient] | None = None,
        capabilities_client: DeviceCapabilitiesClient | None = None,
    ):
```

**Problem**: 5 Dependencies im Constructor (Grenzwert: 4)

**SOLL**: DeviceServiceContext oder separate Services
```python
# Option A: Context Object
@dataclass
class DeviceServiceContext:
    repository: IDeviceRepository
    sync_service: ISyncService
    discovery: IDiscoveryAdapter
    client_factory: Callable[[str], IDeviceClient]
    capabilities: ICapabilitiesClient

class DeviceService:
    def __init__(self, ctx: DeviceServiceContext):
        self._ctx = ctx
```

---

### [ARCH-05] Fehlende Domain Events
**Severity**: P3 (Architecture)  
**Location**: Global

**Problem**: Keine Event-basierte Kommunikation zwischen Modulen

**Beispiel**: Wenn ein Gerät entdeckt wird:
1. DeviceService speichert in Repository
2. … aber PresetsModule weiß nichts davon
3. … und SettingsModule auch nicht

**SOLL**: Domain Event Pattern
```python
# core/events.py (NEU)
class DeviceDiscoveredEvent:
    device_id: str
    ip: str
    timestamp: datetime

# In devices/service.py
class DeviceService:
    async def sync_devices(self):
        devices = await self._discovery.discover()
        for device in devices:
            await self._repo.upsert(device)
            await self._event_bus.publish(DeviceDiscoveredEvent(
                device_id=device.device_id,
                ip=device.ip
            ))
```

---

### [ARCH-06] Inconsistent Error Handling Strategy
**Severity**: P2 (Reliability)  
**Location**: Multiple files

**Pattern A (devices/service.py)**: Let exceptions propagate
```python
async def discover_devices(self, timeout: int = 10):
    return await self._discovery_adapter.discover(timeout=timeout)
    # No try/catch - exception bubbles up
```

**Pattern B (presets/service.py)**: Catch and log
```python
try:
    ...
except Exception as e:
    logger.error(f"Error: {e}")
    raise
```

**SOLL**: Einheitliche Error-Handling-Strategie
1. Domain-spezifische Exceptions (core/exceptions.py)
2. Route-Level Exception Handlers (main.py)
3. Structured Logging mit Correlation IDs

---

## 3. Module Dependency Graph

```
                        ┌─────────┐
                        │  main   │
                        └────┬────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
       ┌────▼────┐     ┌─────▼────┐     ┌─────▼────┐
       │ devices │     │ presets  │     │ settings │
       │ router  │     │ router   │     │ router   │
       └────┬────┘     └────┬─────┘     └────┬─────┘
            │               │                │
       ┌────▼────┐     ┌────▼─────┐    ┌─────▼─────┐
       │ Device  │     │ Preset   │    │ Settings  │
       │ Service │     │ Service  │    │ Service   │
       └────┬────┘     └────┬─────┘    └─────┬─────┘
            │               │                │
     ┌──────┼──────┐        │                │
     │      │      │        │                │
┌────▼───┐ ┌▼────┐ ┌▼─────┐ ┌▼─────┐   ┌─────▼─────┐
│ Device │ │Sync │ │Adapt.│ │Preset│   │ Settings  │
│  Repo  │ │Svc  │ │      │ │ Repo │   │   Repo    │
└────────┘ └──┬──┘ └──────┘ └──────┘   └───────────┘
              │
         ┌────▼─────┐
         │ Discovery│
         │ SSDP/Man │
         └──────────┘
```

**✅ Gut**: Keine zyklischen Dependencies  
**✅ Gut**: Module sind cohesive (hohe Kohäsion)  
**⚠️ Problem**: Keine expliziten Module Boundaries (Python Packages ohne __init__.py exports)

---

## 4. Frontend-Backend Coupling

### 4.1 API Contract

| Endpoint | Method | Frontend Component | Backend Route |
|----------|--------|-------------------|---------------|
| `/api/devices/discover` | GET | useDevices | devices/routes.py |
| `/api/devices/sync` | POST | useDevices | devices/routes.py |
| `/api/presets/{device}` | GET/POST | RadioPresets | presets/routes.py |
| `/api/radio/search` | GET | StationSearchModal | radio/routes.py |
| `/api/settings/manual-ips` | GET/POST/DELETE | SettingsView | settings/routes.py |

**⚠️ Problem**: Kein API Schema Sharing (OpenAPI zu TypeScript Types)

**SOLL**: 
```bash
# Generate TypeScript types from OpenAPI
npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts
```

---

## 5. Data Flow Diagrams

### 5.1 Device Discovery Flow

```
User clicks "Discover"
        │
        ▼
Frontend: fetch("/api/devices/discover")
        │
        ▼
Backend: DeviceService.discover_devices()
        │
        ▼
BoseDeviceDiscoveryAdapter.discover()
        │
        ├─► SSDPDiscovery.discover() ──► UDP Multicast (239.255.255.250:1900)
        │
        └─► ManualDiscovery.discover() ──► HTTP /info endpoints
        │
        ▼
Returns: List[DiscoveredDevice]
        │
        ▼
Frontend: setDevices(response.data)
```

### 5.2 Preset Assignment Flow

```
User assigns station to preset
        │
        ▼
Frontend: POST /api/presets
        Body: {device_id, preset_number, station}
        │
        ▼
Backend: PresetService.set_preset()
        │
        ├─► PresetRepository.set_preset() ──► SQLite INSERT/UPDATE
        │
        └─► BoseDeviceClient.select_preset() ──► HTTP PUT /select
        │
        ▼
Device plays station
        │
        ▼
Frontend: Updates UI state
```

---

## 6. Ziel-Architektur (SOLL)

```
┌─────────────────────────────────────────────────────────┐
│  API Layer (FastAPI Routes + OpenAPI)                   │
│  └─ Automatic TypeScript type generation                │
├─────────────────────────────────────────────────────────┤
│  Application Layer (Use Cases / Services)               │
│  └─ Protocol-based dependencies                         │
│  └─ Domain Event publishing                             │
├─────────────────────────────────────────────────────────┤
│  Domain Layer (Entities + Value Objects)                │
│  └─ Separate models.py per module                       │
│  └─ Business rule validation in models                  │
├─────────────────────────────────────────────────────────┤
│  Infrastructure Layer (Repositories + Adapters)         │
│  └─ app.state for lifecycle management                  │
│  └─ Unified error handling strategy                     │
├─────────────────────────────────────────────────────────┤
│  Core Services (Config, Logging, Events)                │
│  └─ Event bus for cross-module communication            │
│  └─ Correlation IDs for request tracing                 │
└─────────────────────────────────────────────────────────┘
```

---

## 7. Recommended Refactoring Order

| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| 1 | Migrate to app.state DI | 4h | High |
| 2 | Extract Device model to models.py | 1h | Medium |
| 3 | Add Protocol interfaces | 4h | High |
| 4 | Unified exception handling | 2h | Medium |
| 5 | OpenAPI to TypeScript codegen | 2h | Medium |
| 6 | Domain events (optional) | 8h | Low |

---

## 8. Compliance Matrix

| Principle | Implemented | Notes |
|-----------|-------------|-------|
| Dependency Rule | ✅ Yes | Inner layers don't know outer |
| Interface Segregation | ⚠️ Partial | No explicit protocols |
| Repository Pattern | ✅ Yes | All DB access via repos |
| Adapter Pattern | ✅ Yes | External systems wrapped |
| DI Container | ⚠️ Partial | Globals instead of app.state |
| Error Boundaries | ⚠️ Partial | Inconsistent strategy |
| Event-Driven | ❌ No | No domain events |

---

**Gesamtbewertung**: Solide Grundstruktur mit klaren Verbesserungsmöglichkeiten. Die wichtigsten Maßnahmen (app.state Migration, Protocol-Einführung) sind low-risk und high-impact.
