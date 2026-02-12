# 03 - Backend Code Review

**Stand**: 2026-02-12  
**Analyst**: Principal Software Engineer (AI-assisted)

---

## [P1] [SECURITY] Path Traversal in SPA Catch-All Route

**Datei:** `apps/backend/src/opencloudtouch/main.py`  
**Zeilen:** 181-189

**Problem:**
```python
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve index.html for all non-API routes (SPA support)."""
    # If requesting a static file that exists, serve it
    file_path = static_dir / full_path
    if file_path.is_file():
        return FileResponse(file_path)  # ⚠️ UNSICHER!

    # Otherwise serve index.html (React Router handles the rest)
    return FileResponse(static_dir / "index.html")
```

**Warum schlecht:**
Kein Check ob `full_path` Directory Traversal enthält. Angreifer kann mit `GET /../../../etc/passwd` beliebige Dateien lesen.

**Recherche:**
- OWASP Path Traversal: https://owasp.org/www-community/attacks/Path_Traversal
- FastAPI Security Best Practices empfehlen `resolve()` + `relative_to()` Check
- Ähnliche Vulnerabilities dokumentiert in CVE-2021-21241 (aiohttp)

**Fix:**
```python
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve index.html for all non-API routes (SPA support)."""
    # Sanitize path - prevent directory traversal
    try:
        safe_path = (static_dir / full_path).resolve()
        # Ensure path stays within static_dir
        safe_path.relative_to(static_dir.resolve())
    except ValueError:
        # Path traversal attempt - serve index instead
        return FileResponse(static_dir / "index.html")
    
    # Don't serve hidden files
    if safe_path.name.startswith('.'):
        return FileResponse(static_dir / "index.html")
    
    if safe_path.is_file():
        return FileResponse(safe_path)
    
    return FileResponse(static_dir / "index.html")
```

**Aufwand:** 15min  
**Verifizierung:** Unit-Test mit `../../etc/passwd` hinzufügen

---

## [P2] [SECURITY] CORS Allow All Origins

**Datei:** `apps/backend/src/opencloudtouch/main.py`  
**Zeilen:** 125-132

**Problem:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: configure properly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Warum schlecht:**
`allow_origins=["*"]` kombiniert mit `allow_credentials=True` ermöglicht CSRF-artige Angriffe. Ein Angreifer kann über eine böswillige Website API-Requests mit den Cookies des Users senden.

**Recherche:**
- CORS Best Practices: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
- FastAPI Docs: Empfehlen explizite Origin-Liste in Production

**Fix:**
```python
from opencloudtouch.core.config import get_config

cfg = get_config()

# In production: Only allow same-origin (single container serves both)
# In development: Allow localhost variants
allowed_origins = [
    f"http://localhost:{cfg.port}",
    f"http://127.0.0.1:{cfg.port}",
]

if cfg.mock_mode:  # Development
    allowed_origins.extend([
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

**Aufwand:** 30min  
**Hinweis:** Da Single-Container-Deployment: SPA wird vom gleichen Origin geserved, CORS kann restriktiver sein.

---

## [P2] [ARCHITECTURE] Global Singleton DI Pattern

**Datei:** `apps/backend/src/opencloudtouch/core/dependencies.py`  
**Zeilen:** 15-22

**Problem:**
```python
# Private singleton instances (module-level)
_device_repo_instance: Optional[DeviceRepository] = None
_device_service_instance: Optional[DeviceService] = None
_preset_repo_instance: Optional[PresetRepository] = None
_preset_service_instance: Optional[PresetService] = None
_settings_repo_instance: Optional[SettingsRepository] = None
_settings_service_instance: Optional[SettingsService] = None
```

**Warum schlecht:**
- Global state erschwert Testing und Parallelisierung
- FastAPI 2024+ Best Practice: `app.state` oder `Depends()` mit Closures
- Module-level globals sind in Python 3.11+ für async contexts problematisch

**Recherche:**
- FastAPI Docs 2025: https://fastapi.tiangolo.com/advanced/events/#lifespan
- Starlette Pattern: `app.state` für Application-scoped dependencies
- Alternative: `lru_cache` mit Dependency Injection

**Aktueller Stand (veraltet):**
```python
_device_repo_instance: Optional[DeviceRepository] = None

def set_device_repo(repo: DeviceRepository) -> None:
    global _device_repo_instance
    _device_repo_instance = repo
```

**State-of-the-Art Lösung:**
```python
# In main.py lifespan:
async def lifespan(app: FastAPI):
    # Startup
    device_repo = DeviceRepository(cfg.effective_db_path)
    await device_repo.initialize()
    app.state.device_repo = device_repo
    
    yield
    
    # Shutdown
    await app.state.device_repo.close()

# Als Dependency:
async def get_device_repo(request: Request) -> DeviceRepository:
    return request.app.state.device_repo
```

**Aufwand:** 2h (alle 6 Dependencies umstellen)  
**Hinweis:** Bestehende Tests müssen angepasst werden (`clear_dependencies()` entfällt)

---

## [P2] [BUG] Settings Route POST/PUT Semantik

**Datei:** `apps/backend/src/opencloudtouch/settings/routes.py`  
**Zeilen:** 50-66

**Problem:**
```python
@router.post(
    "/manual-ips",
    response_model=ManualIPsResponse,
    status_code=status.HTTP_200_OK,  # ⚠️ POST sollte 201 zurückgeben
)
async def set_manual_ips(
    request: SetManualIPsRequest,
    ...
) -> ManualIPsResponse:
    """Replace all manual device IP addresses with new list."""
```

**Warum schlecht:**
- `POST` mit "Replace all" Semantik ist ein `PUT` nach REST-Standards
- `POST` sollte `201 Created` zurückgeben, nicht `200 OK`
- Frontend erwartet möglicherweise falsches Verhalten

**Recherche:**
- REST API Design: POST=Create, PUT=Replace, PATCH=Partial Update
- HTTP Status Codes: 201 für Create, 200/204 für Update

**Fix:**
```python
@router.put(
    "/manual-ips",
    response_model=ManualIPsResponse,
    status_code=status.HTTP_200_OK,  # PUT Replace = 200 OK
)
async def set_manual_ips(...):
    """Replace all manual device IP addresses with new list."""

# Zusätzlich: POST für einzelne IP hinzufügen
@router.post(
    "/manual-ips",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_manual_ip(ip: str, ...):
    """Add a single manual IP address."""
```

**Aufwand:** 30min  
**Hinweis:** Frontend-Call muss angepasst werden (POST → PUT)

---

## [P2] [BUG] Doppelte IP-Validierung (redundant + inkonsistent)

**Datei:** `apps/backend/src/opencloudtouch/settings/repository.py`  
**Zeilen:** 38-50

**Problem:**
```python
async def add_manual_ip(self, ip: str) -> None:
    # Basic IP validation
    parts = ip.split(".")
    if len(parts) != 4:
        raise ValueError(f"Invalid IP address format: {ip}")

    try:
        for part in parts:
            if not 0 <= int(part) <= 255:
                raise ValueError(f"Invalid IP address: {ip}")
    except ValueError:
        raise ValueError(f"Invalid IP address: {ip}")
```

**Warum schlecht:**
- IP-Validierung dupliziert: Service UND Repository validieren
- Repository sollte nur Persistenz machen (Single Responsibility)
- Validierung im Service (`settings/service.py:16-25`) ist bereits vorhanden

**Fix:**
Repository-Validierung entfernen, nur Service validiert:
```python
# settings/repository.py
async def add_manual_ip(self, ip: str) -> None:
    """Add manual IP (already validated by service)."""
    db = self._ensure_initialized()
    
    try:
        await db.execute(
            "INSERT INTO manual_device_ips (ip_address, created_at) VALUES (?, ?)",
            (ip, datetime.now(UTC).isoformat()),
        )
        await db.commit()
    except aiosqlite.IntegrityError as e:
        raise ValueError(f"IP address already exists: {ip}") from e
```

**Aufwand:** 15min

---

## [P2] [ARCHITECTURE] Dupliziertes RadioStation Model

**Dateien:** 
- `apps/backend/src/opencloudtouch/radio/provider.py:14-28`
- `apps/backend/src/opencloudtouch/radio/providers/radiobrowser.py:42-67`

**Problem:**
```python
# In provider.py:
@dataclass
class RadioStation:
    station_id: str
    name: str
    url: str
    ...

# In radiobrowser.py:
@dataclass
class RadioStation:
    station_uuid: str  # ⚠️ Anderer Name!
    name: str
    url: str
    ...
```

**Warum schlecht:**
- Zwei verschiedene `RadioStation` Klassen mit unterschiedlichen Feldern
- `station_id` vs `station_uuid` führt zu Verwirrung
- Type Checking schlägt fehl bei Import-Confusion
- API Response Model nutzt `radiobrowser.RadioStation`, nicht `provider.RadioStation`

**Fix:**
Ein einziges Model, das alle Provider unterstützt:
```python
# radio/models.py (NEU)
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class RadioStation:
    """Unified radio station model."""
    station_uuid: str
    name: str
    url: str
    url_resolved: Optional[str] = None
    homepage: Optional[str] = None
    favicon: Optional[str] = None
    tags: Optional[str] = None
    country: str = ""
    countrycode: Optional[str] = None
    codec: str = ""
    bitrate: Optional[int] = None
    provider: str = "unknown"  # e.g. "radiobrowser"
```

**Aufwand:** 1h (Refactoring + alle Imports anpassen)

---

## [P2] [BUG] SSDP Socket Binding kann fehlschlagen

**Datei:** `apps/backend/src/opencloudtouch/devices/discovery/ssdp.py`  
**Zeilen:** 86-95

**Problem:**
```python
def _ssdp_msearch(self) -> list[str]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # ...
    
    # Bind to SSDP port to receive responses
    sock.bind(("", self.SSDP_PORT))  # ⚠️ Port 1900 oft belegt
```

**Warum schlecht:**
- Port 1900 kann von anderen Anwendungen belegt sein
- Kein Fallback wenn Binding fehlschlägt
- Error Handling gibt leere Liste zurück, aber User sieht keine Warnung

**Fix:**
```python
def _ssdp_msearch(self) -> list[str]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind(("", self.SSDP_PORT))
    except OSError as e:
        if e.errno == 98:  # Address already in use
            logger.warning(
                "SSDP port 1900 already in use, trying random port"
            )
            # Fallback: Use random port (can still send, may miss some responses)
            sock.bind(("", 0))
        else:
            logger.error(f"Failed to bind SSDP socket: {e}")
            sock.close()
            return []
    
    # ... rest of method
```

**Aufwand:** 15min

---

## [P3] [MAINTAINABILITY] Magic Numbers in Device Repository

**Datei:** `apps/backend/src/opencloudtouch/devices/repository.py`  
**Zeilen:** 43-48

**Problem:**
```python
@staticmethod
def _extract_schema_version(firmware_version: str) -> str:
    # ...
    parts = firmware_version.split()[0].split(".")
    if len(parts) >= 3:  # ⚠️ Magic number
        return ".".join(parts[:3])  # ⚠️ Magic number
```

**Fix:**
```python
SCHEMA_VERSION_PARTS = 3  # major.minor.patch

@staticmethod
def _extract_schema_version(firmware_version: str) -> str:
    if not firmware_version:
        return "unknown"
    
    parts = firmware_version.split()[0].split(".")
    if len(parts) >= SCHEMA_VERSION_PARTS:
        return ".".join(parts[:SCHEMA_VERSION_PARTS])
    return firmware_version.split()[0] if firmware_version else "unknown"
```

**Aufwand:** 5min

---

## [P3] [DEAD_CODE] Ungenutzte Provider ABC

**Datei:** `apps/backend/src/opencloudtouch/radio/provider.py`

**Problem:**
Die abstrakte `RadioProvider` Klasse wird von `RadioBrowserAdapter` nicht korrekt implementiert:
- `provider_name` Property fehlt in `RadioBrowserAdapter`
- ABC-Methoden sind definiert aber Adapter erbt nicht davon

**Recherche:**
Grep zeigt: `RadioBrowserAdapter` erbt nicht von `RadioProvider`:
```python
# radiobrowser.py:
class RadioBrowserAdapter:  # ⚠️ Fehlt: (RadioProvider)
```

**Fix:**
```python
# radiobrowser.py
from opencloudtouch.radio.provider import RadioProvider

class RadioBrowserAdapter(RadioProvider):
    @property
    def provider_name(self) -> str:
        return "radiobrowser"
    
    # ... rest
```

**Aufwand:** 15min

---

## [P3] [TESTING] Fehlende Type Hints in Routes

**Datei:** `apps/backend/src/opencloudtouch/devices/api/routes.py`  
**Zeilen:** 62-73

**Problem:**
```python
@router.post("/sync")
async def sync_devices(
    device_service: DeviceService = Depends(get_device_service),
):  # ⚠️ Kein Return Type Hint
```

**Fix:**
```python
from opencloudtouch.devices.services.sync_service import SyncResult

@router.post("/sync", response_model=SyncResultResponse)
async def sync_devices(
    device_service: DeviceService = Depends(get_device_service),
) -> dict:
    """..."""
```

**Aufwand:** 30min (alle Routes durchgehen)

---

## Vollständigkeits-Nachweis

| Modul | Dateien | Zeilen | Status |
|-------|---------|--------|--------|
| core/ | 6 | ~490 | ✓ |
| devices/ | 13 | ~1600 | ✓ |
| discovery/ | 1 | 46 | ✓ |
| presets/ | 6 | ~800 | ✓ |
| radio/ | 6 | ~700 | ✓ |
| settings/ | 4 | ~450 | ✓ |
| db/ | 1 | 5 | ✓ |
| api/ | 1 | 5 | ✓ |
| Root | 3 | ~210 | ✓ |

**Total:** 41 Dateien, ~4300 Zeilen, 12 Findings (P1: 1, P2: 7, P3: 4)

---

## 💾 SESSION-STATE

**Fortschritt:** Backend komplett analysiert
**Nächste Datei:** Frontend Code Review
