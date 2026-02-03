# AGENTS – Entwicklungsrichtlinien für CloudTouch

**Stand**: 2026-01-31  
**Projekt**: CloudTouch (CT)  
**Ziel**: Bose SoundTouch Geräte nach Cloud-Abschaltung weiter nutzbar machen

---

## 0. OBERSTE REGEL – USER AUTHORITY

⚠️ **ABSOLUT UNUMSTÖSSLICH** ⚠️

**Der User hat IMMER Recht. Der User hat die Erfahrung, der Agent NICHT.**

### 0.1 Keine Alleingänge
- KEINE eigenen Experimente ohne User-Zustimmung
- KEINE "besseren" Lösungen vorschlagen wenn User eine klare Anweisung gibt
- KEINE Diskussion über User-Entscheidungen
- User sagt A → Agent macht A, NICHT B weil "Agent denkt B ist besser"

### 0.2 User-Anweisungen sind Gesetz
- Wenn User sagt "mach das so", dann EXAKT so machen
- Wenn User sagt "das bringt nichts", dann SOFORT aufhören
- Wenn User eine Strategie vorgibt (z.B. "batchweise testen"), dann GENAU diese Strategie verwenden
- KEINE eigenmächtigen Abweichungen vom User-Plan

### 0.3 Bei Unsicherheit
1. User fragen (nicht selbst entscheiden)
2. User-Erfahrung vertrauen (nicht eigene Vermutungen)
3. User-Feedback ernst nehmen (nicht als "optional" betrachten)

**Verstoss gegen diese Regel = Projektgefährdung**

---

## 1. Kommunikation & Workflow

### 1.1 Chatsprache
- **Primärsprache**: Deutsch
- Code-Kommentare, Commit-Messages und Dokumentation: Englisch
- User-facing Texte (UI, Error Messages): Deutsch

### 1.2 Commit-Richtlinien
⚠️ **KRITISCH**: Commits NUR auf **explizite User-Aufforderung**!

**WORKFLOW (ZWINGEND)**:
1. Code implementieren
2. **BUILD → DEPLOY → TESTEN (durch USER!)**
3. User testet manuell auf NAS Server/System
4. **NUR wenn User sagt "commit"** → dann committen
5. User nimmt Implementierungen ab, NICHT der Agent!

**VERBOTEN**:
- ❌ Automatisch committen nach Implementation
- ❌ Committen vor User-Test
- ❌ "Ich committe jetzt" ohne User-Erlaubnis
- ❌ `--no-verify` verwenden

**ERLAUBT**:
- ✅ User sagt explizit "commit" oder "commit & push"
- ✅ Alle Tests grün (pre-commit hook muss durchlaufen)

**Commit-Format**: Conventional Commits (`feat:`, `fix:`, `test:`, `refactor:`, `docs:`)

### 1.3 Git Workflow
```bash
# Explizit auf User-Anweisung warten:
git add -A
git commit -m "feat: Beschreibung"  # NIEMALS --no-verify!
git push

# ODER für Force-Push (bei Rebase):
git push --force-with-lease
```

---

## 2. Test-Driven Development (TDD) – GESETZ

### 2.1 TDD ist nicht verhandelbar
**JEDE** Code-Änderung folgt dem TDD-Zyklus:

```
1. 🔴 RED   → Test schreiben (schlägt fehl)
2. 🟢 GREEN → Code schreiben (Test besteht)
3. 🔵 BLUE  → Refactoring (Test bleibt grün)
```

### 2.2 Test-Anforderungen
- **Mindest-Coverage**: 80%
- Tests vor Implementation schreiben
- Tests müssen deterministisch sein (keine Flaky Tests)
- Mock externe Dependencies (HTTP, DB, Filesystem)

### 2.3 Test-Struktur
```python
"""
Tests for [Modul/Feature]
"""
import pytest
from unittest.mock import AsyncMock, patch

# Arrange
@pytest.mark.asyncio
async def test_feature_success():
    """Test successful feature execution."""
    # Arrange
    mock_dependency = AsyncMock()
    
    # Act
    result = await feature(mock_dependency)
    
    # Assert
    assert result.status == "success"
```

### 2.4 Coverage-Ausnahmen
Nur folgende Code-Bereiche dürfen von Coverage ausgenommen werden:
```python
# In pytest.ini [coverage:report] exclude_lines:
if __name__ == .__main__.:
raise NotImplementedError
if TYPE_CHECKING:
@abstractmethod
pragma: no cover
```

### 2.5 Bug-Fix Tests (PFLICHT)
**Für jeden gefundenen Bug MUSS ein Regression-Test geschrieben werden** - unabhängig davon wie trivial der Bug erscheint!

**Workflow bei Bug-Fixes**:
1. Bug identifizieren und reproduzieren
2. Test schreiben der das Fehlverhalten demonstriert (RED)
3. Bug fixen (GREEN)
4. Test bleibt als Regression-Schutz im Code

**Beispiel**: XML Namespace Bug
```python
def test_xml_namespace_parsing_regression():
    """Regression test for XML namespace handling in SSDP discovery.
    
    Bug: _find_xml_text() failed to parse elements with xmlns namespace.
    Fixed: 2026-01-29 - Implemented namespace-agnostic element search.
    """
    discovery = SSDPDiscovery()
    xml_with_namespace = '''
    <root xmlns="urn:schemas-upnp-org:device-1-0">
        <device>
            <manufacturer>Bose Corporation</manufacturer>
        </device>
    </root>
    '''
    root = ElementTree.fromstring(xml_with_namespace)
    manufacturer = discovery._find_xml_text(root, ".//manufacturer")
    assert manufacturer == "Bose Corporation"
```

---

## 3. Clean Code Prinzipien

### 3.1 SOLID Principles
- **S**ingle Responsibility: Eine Klasse = eine Verantwortung
- **O**pen/Closed: Offen für Erweiterung, geschlossen für Änderung
- **L**iskov Substitution: Subtypen müssen austauschbar sein
- **I**nterface Segregation: Viele kleine Interfaces statt ein großes
- **D**ependency Inversion: Von Abstraktionen abhängen, nicht von Konkretionen

### 3.2 DRY (Don't Repeat Yourself)
- Code-Duplikation vermeiden
- Bei 3. Wiederholung → Abstraktion einführen
- Shared Logic in Utilities auslagern

### 3.3 Code-Qualität
```python
# ✅ GOOD: Sprechende Namen
async def discover_soundtouch_devices(timeout: int) -> List[DiscoveredDevice]:
    """Discover Bose SoundTouch devices via SSDP."""
    
# ❌ BAD: Kryptische Namen
async def disc(t: int) -> List:
    """Do stuff."""
```

**Regeln**:
- Funktionen: max. 20 Zeilen
- Klassen: max. 200 Zeilen
- Parameter: max. 4 pro Funktion
- Keine Magic Numbers (Konstanten verwenden)

### 3.4 Error Handling
```python
# ✅ GOOD: Spezifische Exceptions
try:
    device = await client.get_info()
except DeviceConnectionError as e:
    logger.error(f"Failed to connect to device: {e}")
    raise

# ❌ BAD: Generische Exceptions
try:
    device = await client.get_info()
except Exception:
    pass  # Fehler verschlucken ist verboten!
```

### 3.5 Naming Conventions & Consistency

**ZWINGEND**: Konsistente Namensgebung über ALLE Code-Dateien hinweg!

#### 3.5.1 Python Backend
```python
# ✅ GOOD: PEP 8 Konventionen
class DeviceRepository:           # PascalCase für Klassen
    def get_by_device_id(self):   # snake_case für Funktionen/Methoden
        pass

SSDP_MULTICAST_ADDR = "..."      # UPPER_SNAKE_CASE für Konstanten
device_count = 5                  # snake_case für Variablen
_internal_cache = {}              # Leading underscore für private

# ❌ BAD: Inkonsistent
class deviceRepository:           # Falsch! PascalCase fehlt
    def GetDeviceById(self):      # Falsch! camelCase statt snake_case
        MAX_devices = 10          # Falsch! Inkonsistent
```

#### 3.5.2 TypeScript/JavaScript Frontend
```typescript
// ✅ GOOD: Standard JS/TS Konventionen
class DeviceManager {             // PascalCase für Klassen
  fetchDevices() {}               // camelCase für Methoden
}

const MAX_RETRY_COUNT = 3;        // UPPER_SNAKE_CASE für Konstanten
let deviceList = [];              // camelCase für Variablen
const _privateHelper = () => {};  // Leading underscore für private

// React Components: PascalCase
function DeviceCard({ device }) { return <div>...</div>; }

// ❌ BAD: Inkonsistent
function device_card() {}         // Falsch! Components PascalCase
let DeviceList = [];              // Falsch! Variablen camelCase
const max_retry = 3;              // Falsch! Konstanten UPPER_SNAKE_CASE
```

#### 3.5.3 Dateinamen
```
# ✅ GOOD: Konsistente Konventionen

Backend Python:
  adapter.py                      # snake_case für Module
  device_repository.py            # snake_case mit Unterstrichen
  test_adapter.py                 # test_ Präfix für Tests

Frontend JavaScript/TypeScript:
  DeviceCard.jsx                  # PascalCase für React Components
  deviceService.ts                # camelCase für Services/Utils
  DeviceCard.test.jsx             # .test. für Tests

# ❌ BAD: Inkonsistent
  Device_Repository.py            # Falsch! Keine PascalCase für Python-Module
  device-card.jsx                 # Falsch! Kebab-case vermeiden
  devicecard.jsx                  # Falsch! Keine Trennung erkennbar
```

#### 3.5.4 URL/API Endpoints
```python
# ✅ GOOD: RESTful mit kebab-case
@router.get("/api/devices")                    # Plural für Collections
@router.get("/api/devices/{device_id}")        # snake_case für Parameter
@router.post("/api/settings/manual-ips")       # kebab-case für Multi-Word

# ❌ BAD: Inkonsistent
@router.get("/api/Device")                     # Falsch! Singular + PascalCase
@router.get("/api/devices/{deviceId}")         # Falsch! camelCase in URL
@router.post("/api/settings/manualIPs")        # Falsch! camelCase statt kebab
```

#### 3.5.5 Environment Variables & Config
```bash
# ✅ GOOD: UPPER_SNAKE_CASE mit Namespace-Präfix
CT_DISCOVERY_TIMEOUT=10
CT_MANUAL_DEVICE_IPS=192.168.1.100,192.168.1.101
CT_LOG_LEVEL=DEBUG

# ❌ BAD: Inkonsistent oder ohne Präfix
discoveryTimeout=10               # Falsch! Kein UPPER_SNAKE_CASE
ct-manual-ips=...                 # Falsch! Kebab-case statt Underscore
TIMEOUT=10                        # Falsch! Kein CT_ Präfix (Kollisionsgefahr)
```

#### 3.5.6 Datenbank-Felder
```python
# ✅ GOOD: snake_case konsistent
class Device:
    device_id: str                # snake_case
    ip_address: str
    friendly_name: str
    created_at: datetime

# ❌ BAD: Inkonsistent
class Device:
    deviceId: str                 # Falsch! camelCase in Python
    IPAddress: str                # Falsch! PascalCase
    FriendlyName: str             # Falsch! PascalCase
```

#### 3.5.7 Boolean Variablen/Flags
```python
# ✅ GOOD: is_, has_, should_, can_ Präfixe
is_connected = True
has_error = False
should_retry = True
can_discover = False

# ❌ BAD: Verb oder Substantiv
connected = True                  # Unklar: Status oder Aktion?
error = False                     # Unklar: Boolean oder Error-Objekt?
retry = True                      # Unklar: Boolean oder Retry-Count?
```

#### 3.5.8 Event Handler / Callbacks
```typescript
// ✅ GOOD: on/handle Präfixe
function handleClick(event) {}
function onDeviceSelected(device) {}
function handleRetry() {}

// ❌ BAD: Kein Präfix
function click() {}               // Unklar: Handler oder Aktion?
function deviceSelected() {}      // Unklar: Handler oder Getter?
```

#### 3.5.9 Naming Consistency Checklist
**Vor jedem Commit prüfen**:
- [ ] Python: snake_case (Funktionen/Variablen), PascalCase (Klassen), UPPER_SNAKE_CASE (Konstanten)
- [ ] TypeScript/React: camelCase (Funktionen/Variablen), PascalCase (Klassen/Components), UPPER_SNAKE_CASE (Konstanten)
- [ ] Dateinamen: snake_case (Python), camelCase/PascalCase (JS/TS je nach Typ)
- [ ] API-Endpoints: kebab-case, Plural für Collections
- [ ] Env-Variablen: CT_ Präfix + UPPER_SNAKE_CASE
- [ ] Boolean: is_/has_/should_/can_ Präfixe
- [ ] Event Handler: handle/on Präfixe
- [ ] Private: Leading underscore `_`
- [ ] Keine Abbreviations (außer allgemein bekannt: HTTP, URL, IP, ID)
- [ ] Sprechende Namen statt Kürzel (discovery statt disc, timeout statt to)

#### 3.5.10 Anti-Patterns vermeiden
```python
# ❌ VERBOTEN
temp, tmp, data, info, obj       # Zu generisch
a, b, c, x, y, z                 # Single-letter (außer in Loops/Math)
get_data(), do_stuff()           # Nicht-deskriptiv
myVar, theDevice, aDevice        # Artikel-Präfixe
deviceManager2, device_final     # Nummerierung/Suffixe
```

**Bei Unsicherheit**: Bestehende Code-Patterns nachahmen, nicht neue Stile erfinden!

---

## 4. Clean Architecture

### 4.1 Schichtenmodell
```
┌─────────────────────────────────────┐
│  API Layer (FastAPI Routes)        │  ← HTTP/REST Interface
├─────────────────────────────────────┤
│  Use Cases / Services               │  ← Business Logic
├─────────────────────────────────────┤
│  Domain Models                      │  ← Entities, Value Objects
├─────────────────────────────────────┤
│  Adapters (External Systems)       │  ← SoundTouch, RadioBrowser
├─────────────────────────────────────┤
│  Infrastructure (DB, Config)        │  ← SQLite, Logging
└─────────────────────────────────────┘
```

**Abhängigkeitsregel**: Innere Schichten kennen äußere nicht!

### 4.2 Adapter Pattern
Alle externen Systeme werden gewrappt:
```python
# backend/src/cloudtouch/devices/adapter.py
class BoseSoundTouchDiscoveryAdapter(DeviceDiscovery):
    """Wraps SSDP discovery for SoundTouch devices."""
    
    async def discover(self, timeout: int) -> List[DiscoveredDevice]:
        # Implementation uses SSDPDiscovery internally
```

### 4.3 Repository Pattern
Datenzugriff nur über Repositories:
```python
# backend/src/cloudtouch/devices/repository.py
class DeviceRepository:
    async def upsert(self, device: Device) -> None:
        """Insert or update device."""
    
    async def get_by_device_id(self, device_id: str) -> Optional[Device]:
        """Get device by ID."""
```

### 4.4 Dependency Injection
FastAPI Dependencies verwenden:
```python
@router.post("/api/devices/sync")
async def sync_devices(repo: DeviceRepository = Depends(get_device_repo)):
    """Sync discovered devices to database."""
    devices = await discover()
    for device in devices:
        await repo.upsert(device)
```

---

## 5. Clean UX Prinzipien

### 5.1 Laien-Fokus
CT muss von **technischen Laien** bedienbar sein:
- ✅ Automatische Discovery (keine IP-Konfiguration)
- ✅ Verständliche Fehlermeldungen
- ✅ Progressive Disclosure (Experten-Features versteckt)
- ❌ Rohe XML/JSON Ausgaben im UI
- ❌ Technische Logs im UI

### 5.2 UX-Patterns
**Loading States**:
```tsx
{loading ? <Spinner /> : <DeviceList devices={devices} />}
```

**Error States**:
```tsx
{error ? (
  <ErrorMessage>
    Keine Geräte gefunden. 
    <Link to="/help">Hilfe anzeigen</Link>
  </ErrorMessage>
) : null}
```

**Empty States**:
```tsx
{devices.length === 0 ? (
  <EmptyState>
    Noch keine Geräte gefunden.
    <Button onClick={discover}>Jetzt suchen</Button>
  </EmptyState>
) : null}
```

### 5.3 Accessibility (WCAG 2.1 AA)
- Semantic HTML (`<button>`, `<nav>`, `<main>`)
- ARIA Labels für Screen Reader
- Keyboard Navigation (Tab, Enter, Escape)
- Kontrast-Ratio ≥ 4.5:1

### 5.4 Mobile-First Design
- Responsive Breakpoints: 320px, 768px, 1024px, 1440px
- Touch-Targets: min. 44x44px
- Font-Size: min. 16px (verhindert Auto-Zoom auf iOS)

---

## 6. Code-Review Checkliste

Vor jedem Commit prüfen:

### 6.1 Tests
- [ ] Alle Tests grün (`pytest -v`)
- [ ] Coverage ≥ 80% (`pytest --cov --cov-fail-under=80`)
- [ ] Neue Tests für neue Features
- [ ] TDD-Zyklus befolgt (RED → GREEN → BLUE)

### 6.2 Code-Qualität
- [ ] Keine Code-Duplikation
- [ ] Sprechende Variablen-/Funktionsnamen
- [ ] Docstrings für Public Functions
- [ ] Type Hints (Python 3.11+)
- [ ] Error Handling mit spezifischen Exceptions

### 6.3 Architektur
- [ ] Schichten-Trennung eingehalten
- [ ] Dependencies von außen nach innen
- [ ] Adapter für externe Systeme
- [ ] Repository für DB-Zugriff

### 6.4 UX
- [ ] Loading States implementiert
- [ ] Error States implementiert
- [ ] Empty States implementiert
- [ ] Accessibility geprüft

---

## 7. Technologie-Stack

### 7.1 Backend
- **Python**: 3.11+ (Type Hints, async/await)
- **Framework**: FastAPI 0.100+
- **HTTP**: httpx (async)
- **DB**: SQLite + aiosqlite
- **Tests**: pytest + pytest-asyncio + pytest-cov
- **Logging**: Structured JSON logging

### 7.2 Frontend
- **Framework**: React 18+
- **Build**: Vite 4+
- **Styling**: CSS Modules / TailwindCSS
- **HTTP**: Fetch API / Axios

### 7.3 DevOps
- **Container**: Docker (Multi-stage Build)
- **Deployment**: NAS Server (Podman)
- **CI/CD**: Manuelle Scripts (deploy-to-server.ps1)

---

## 8. Iteration-Workflow

### 8.1 Jede Iteration umfasst:
1. **E2E Demo-Script** (`e2e/demo_iterationN.py`)
   - Funktioniert mit Mock-Daten (CI)
   - Funktioniert mit echten Geräten (optional)
   - Exit Code 0 = Erfolg, 1 = Fehler

2. **Tests schreiben** (TDD RED)
   - Unit Tests für neue Module
   - Integration Tests für API
   - E2E Tests für User-Flows

3. **Implementation** (TDD GREEN)
   - Minimal viable Code
   - Keine Spekulation
   - Keine halluzinierten APIs

4. **Refactoring** (TDD BLUE)
   - Code-Duplikation entfernen
   - Architektur-Muster anwenden
   - Performance optimieren

5. **Dokumentation**
   - README.md aktualisieren
   - API-Dokumentation (OpenAPI)
   - Architektur-Diagramme

6. **Review & Commit** (nur auf User-Anweisung!)
   ```bash
   git add -A
   git commit -m "feat(iteration1): SSDP discovery implemented"
   git push
   ```

### 8.2 Definition of Done
- [ ] Alle Tests grün
- [ ] Coverage ≥ 80%
- [ ] E2E Demo-Script funktioniert
- [ ] Dokumentation aktualisiert
- [ ] Code-Review Checkliste abgehakt
- [ ] User testet manuell (optional)

---

## 9. Verbotene Praktiken

### 9.1 Code
❌ Code ohne Tests schreiben  
❌ Tests ignorieren ("das teste ich später")  
❌ **Bugs fixen ohne Regression-Test**  
❌ Exceptions verschlucken (`except: pass`)  
❌ Magic Numbers (`if x > 42:`)  
❌ Globale Variablen (außer Config)  
❌ God Classes (>300 Zeilen)  
❌ Tight Coupling zwischen Schichten  

### 9.2 Commits
❌ Commits ohne User-Anweisung  
❌ `git push --force` (nur `--force-with-lease`)  
❌ Unvollständige Commits (broken builds)  
❌ Vage Commit-Messages ("fixes", "wip")  

### 9.3 UX
❌ Technische Fehler im UI zeigen  
❌ Keine Feedback bei langsamen Operationen  
❌ Nicht-responsive Design  
❌ Fehlende Accessibility  

### 9.4 Terminal & Background Prozesse
❌ **Neues Command in Console mit laufendem Background-Prozess**  
   - `run_in_terminal` mit `isBackground=true` startet Prozess in Terminal
   - Terminal-ID wird zurückgegeben (z.B. `a6218b85-c436-402d-8c8a`)
   - ⚠️ **NIEMALS** neues Command in gleicher Console ausführen!
   - Nutze `get_terminal_output(id)` um Status zu prüfen
   - Warte auf `idle` oder `completed` Status
   
**Falsches Beispiel** (VERBOTEN):
```powershell
# ❌ FALSCH: Kills Background-Prozess!
run_in_terminal(".\deploy.ps1", isBackground=true)  # → Terminal ID: abc123
run_in_terminal("Start-Sleep -Seconds 120")         # → Killt deploy.ps1!
```

**Richtiges Beispiel**:
```powershell
# ✅ RICHTIG: Separates Polling
id = run_in_terminal(".\deploy.ps1", isBackground=true)  # → Terminal ID: abc123
# Warte 30s ohne neue Commands
# Dann:
output = get_terminal_output(id)  # Prüfe Status ohne zu killen
```

### 9.5 Rate Limit Management (PFLICHT)
❌ **Große Batch-Operationen ohne Pausen**  
   - Bei >10 Files oder >20 Tool-Calls: Rate-Limit-Protokoll aktivieren
   - Ohne Pausen: Risiko von API-Throttling oder Timeout
   
**Rate-Limit-Protokoll**:
```python
# Batch-Größe: Max. 5 Tool-Calls
# Pause: 60 Sekunden nach jedem Batch
# Progress: Status nach jedem Batch ausgeben

# Beispiel:
Batch 1: [Tool Call 1-5]
→ run_in_terminal("Start-Sleep -Seconds 60")
→ "✓ Batch 1/20 done (5 files)"

Batch 2: [Tool Call 6-10]
→ run_in_terminal("Start-Sleep -Seconds 60")
→ "✓ Batch 2/20 done (10 files total)"
```

**Exception**: Read-only Operations (grep_search, read_file) bis zu 10 parallel erlaubt.

**Eskalation bei Erfolg**:
- Start: 5 Calls + 60s Pause
- Nach 3 erfolgreichen Batches: 10 Calls + 30s
- Nach 5 erfolgreichen Batches: 20 Calls + 10s
- Bei Rate-Limit-Error: Zurück zu 5 Calls + 60s

---

## 10. Spezifische Projektregeln

### 10.0 Bose SoundTouch API Dokumentation

**⚠️ PFLICHTLEKTÜRE vor jeder API-Interaktion!**

Die vollständige API-Referenz befindet sich in:
- **API-Dokumentation**: `backend/bose_api/README.md`
- **Schema-Unterschiede**: `backend/bose_api/SCHEMA_DIFFERENCES.md`
- **Schema-Sammlung**: `backend/bose_api/device_*.xml` (153 Files)

**Wichtigste Erkenntnisse**:
1. **109 Endpoints** total (102 gemeinsam, 7 ST300-exklusiv)
2. **Capability Detection** ist PFLICHT (nicht alle Geräte können alles)
3. **bosesoundtouchapi Library** Property-Namen beachten:
   - `info.DeviceName` (NICHT `info.Name`)
   - `client.GetNowPlayingStatus()` (NICHT `GetNowPlaying()`)
   - `info.NetworkInfo[0]` (ist eine Liste!)
4. **ST300 HDMI-Endpoints** geben 404 auf ST30/ST10 → Error Handling!

**Workflow bei neuen Features**:
1. In `backend/bose_api/README.md` nachschlagen welcher Endpoint
2. In `backend/bose_api/device_*.xml` Schema-Beispiele ansehen
3. In `SCHEMA_DIFFERENCES.md` prüfen ob Modell-spezifisch
4. Capability Detection implementieren
5. Tests mit Mock-Schemas schreiben
6. Erst dann Code implementieren

### 10.1 SSDP Discovery
- Namespace-agnostisches XML Parsing (`local-name()`)
- Timeout: 10s (konfigurierbar via `CT_DISCOVERY_TIMEOUT`)
- Filter: Nur Geräte mit `manufacturer=Bose Corporation`
- Fallback: Manuelle IPs via `CT_MANUAL_DEVICE_IPS`

### 10.2 Konfiguration
```python
# Alle Config-Werte über Pydantic BaseSettings
class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CT_")
    
    manual_device_ips: list[str] = Field(default_factory=list)
    
    @field_validator("manual_device_ips", mode="before")
    @classmethod
    def parse_manual_ips(cls, v):
        """Parse comma-separated IPs from env var."""
        if isinstance(v, str):
            return [ip.strip() for ip in v.split(",") if ip.strip()]
        return v if v else []
```

### 10.3 Logging
```python
# Structured JSON Logging für Production
logger.info("Device discovered", extra={
    "device_id": device.device_id,
    "ip": device.ip,
    "name": device.name
})
```

### 10.4 Error Messages (User-facing)
```python
# ✅ GOOD: Verständlich + Actionable
"Keine SoundTouch-Geräte gefunden. Prüfen Sie, ob die Geräte eingeschaltet und im gleichen WLAN sind."

# ❌ BAD: Technisch
"SSDP M-SEARCH timeout after 10s. No UPnP devices responded on 239.255.255.250:1900"
```

---

## 11. Performance-Ziele

### 11.1 Backend (Runtime)
- API Response Time: <100ms (p95), <500ms (p99)
- SSDP Discovery: <10s
- SQLite Queries: <10ms
- Container Startup: <10s

### 11.2 Frontend (Runtime)
- Time to Interactive (TTI): <3s
- First Contentful Paint (FCP): <1.5s
- Bundle Size: <500KB (gzipped)
- Lighthouse Score: >90

### 11.3 Docker (Build)
- Image Size: <500MB
- Build Time: <3min (multi-stage)
- Deployment (NAS Server): <5min
- Layer Cache Hit Rate: >80%

### 11.4 Tests (Execution)
- Backend pytest: <10s
- Frontend vitest: <5s
- E2E Cypress: <60s
- Pre-commit Hook: <2min

### 11.5 Scripts (Deployment)
- deploy-local.ps1: <2min
- deploy-to-server.ps1: <5min
- export-image.ps1: <1min

**Messung**:
```powershell
# Runtime Performance
Measure-Command { Invoke-WebRequest http://localhost:8000/api/devices }

# Build Performance
Measure-Command { docker build -t cloudtouch:test . }

# Test Performance
Measure-Command { cd backend; pytest -v }

# Script Performance
Measure-Command { .\deployment\deploy-local.ps1 }
```

**Bei Unterschreitung (<50% Target)**:
1. Profiling (cProfile, Chrome DevTools)
2. Bottleneck identifizieren
3. Optimierung implementieren
4. Re-measure
5. Dokumentieren in docs/analysis/performance-improvements.md

---

## 12. Debugging & Troubleshooting

### 12.1 Development
```bash
# Backend Tests
pytest -v --cov=backend --cov-report=html

# Backend starten (debug mode)
CT_LOG_LEVEL=DEBUG uvicorn backend.main:app --reload

# Container lokal bauen
docker build -t cloudtouch:latest .

# Container lokal starten
docker run --rm -it --network host -e CT_LOG_LEVEL=DEBUG cloudtouch:latest
```

### 12.2 NAS Server Deployment
```bash
# Deployment-Script ausführen
.\deploy-to-server.ps1

# Container Logs anzeigen
ssh user@targethost "docker logs cloudtouch -f"

# Container Shell
ssh user@targethost "docker exec -it cloudtouch /bin/bash"

# SSDP Discovery testen
ssh user@targethost "docker exec cloudtouch python -m backend.adapters.ssdp_discovery"
```

---

## 13. Zusammenfassung

**3 goldene Regeln**:
1. **TDD ist Gesetz** – Erst Test, dann Code
2. **Kein Auto-Commit** – Nur auf explizite User-Anweisung
3. **Laien-UX** – Technische Details verstecken

**Code-Philosophie**:
- Clean Code > Clever Code
- Explicit > Implicit
- Simple > Complex
- Tested > Optimized

**Bei Unsicherheit**:
1. User fragen (nicht raten)
2. Docs lesen (nicht halluzinieren)
3. Tests schreiben (nicht spekulieren)

---

**Letzte Aktualisierung**: 2026-01-29  
**Nächste Review**: Bei Start Iteration 2
