# 09 Roadmap - Priorisierter Aktionsplan

**Projekt**: OpenCloudTouch  
**Datum**: 2026-02-11  
**Analyst**: GitHub Copilot (Claude Opus 4.5)

---

## Executive Summary

Konsolidierter Aktionsplan basierend auf forensischer Code-Analyse. 1 kritisches Security-Issue (P1), 15 wichtige Verbesserungen (P2), diverse Nice-to-haves (P3). Geschätzter Gesamtaufwand: ~60 Stunden.

---

## Findings Summary

| Priority | Count | Category |
|----------|-------|----------|
| P1 (Critical) | 1 | Security |
| P2 (Important) | 15 | Architecture, Tests, Build |
| P3 (Nice-to-have) | 12 | Code Quality, Documentation |

---

## Phase 1: Critical Security (Woche 1)

### Sprint Goal: Eliminate P1 Security Risk

| ID | Finding | Action | Effort | Owner |
|----|---------|--------|--------|-------|
| **BE-01** | Path Traversal in serve_spa() | Implement path validation | 2h | Backend |

**Implementation**:
```python
# main.py serve_spa() - SOFORT FIXEN
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # SECURITY: Validate path
    safe_path = Path(full_path).resolve()
    frontend_root = Path(FRONTEND_DIR).resolve()
    
    if not str(safe_path).startswith(str(frontend_root)):
        raise HTTPException(status_code=404)
    
    # Continue with file serving...
```

**Verification**:
```python
# test_main.py - Security Test hinzufügen
def test_path_traversal_blocked():
    client = TestClient(app)
    response = client.get("/../../../etc/passwd")
    assert response.status_code == 404
```

**Exit Criteria**:
- [ ] Path validation implemented
- [ ] Security test added and green
- [ ] Manual penetration test passed

---

## Phase 2: Foundation Fixes (Woche 2-3)

### Sprint Goal: Stabilize Architecture & Enable CI

| ID | Finding | Action | Effort | Priority |
|----|---------|--------|--------|----------|
| **TEST-07** | conftest.py Import Error | Add pythonpath to pytest.ini | 0.5h | P2 |
| **ARCH-01** | Global Singleton DI | Migrate to app.state | 4h | P2 |
| **BUILD-04** | No CI Pipeline | Add GitHub Actions | 4h | P2 |
| **DEP-04** | No Dependabot | Enable security monitoring | 0.5h | P2 |

**Total Effort**: ~9 hours

### 2.1 Fix Test Import (0.5h)

```toml
# pyproject.toml [tool.pytest.ini_options]
pythonpath = ["src"]
```

### 2.2 Migrate DI to app.state (4h)

**Step 1**: Update lifespan
```python
# main.py
async with lifespan(app):
    app.state.config = config
    app.state.device_repo = DeviceRepository(config.effective_db_path)
    await app.state.device_repo.initialize()
    # ... other repos
    yield
    await app.state.device_repo.close()
```

**Step 2**: Update dependencies.py
```python
def get_device_repo(request: Request) -> DeviceRepository:
    return request.app.state.device_repo
```

**Step 3**: Remove global singletons

### 2.3 Add GitHub Actions (4h)

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: |
          cd apps/backend
          pip install -e .[dev]
          pytest --cov --cov-fail-under=80
```

### 2.4 Enable Dependabot (0.5h)

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/apps/backend"
    schedule:
      interval: "weekly"
  - package-ecosystem: "npm"
    directory: "/apps/frontend"
    schedule:
      interval: "weekly"
```

**Exit Criteria**:
- [ ] Tests run successfully in CI
- [ ] Dependabot PRs appearing
- [ ] No global singletons in dependencies.py

---

## Phase 3: Test Coverage (Woche 4-5)

### Sprint Goal: Achieve 85% Coverage + Integration Tests

| ID | Finding | Action | Effort | Priority |
|----|---------|--------|--------|----------|
| **TEST-08** | No Security Tests | Add path traversal test | 1h | P1 |
| **TEST-01** | No Integration Tests | Add API integration tests | 4h | P2 |
| **TEST-02** | No Frontend Tests | Add React component tests | 8h | P2 |
| **TEST-04** | Missing Error Cases | Add error scenario tests | 4h | P2 |

**Total Effort**: ~17 hours

### 3.1 Critical Security Test (1h)

```python
# tests/unit/test_main.py
def test_spa_rejects_path_traversal():
    """Security: Path traversal must be blocked."""
    client = TestClient(app)
    
    attacks = [
        "/../../../etc/passwd",
        "..%2f..%2f..%2fetc/passwd",
        "....//....//etc/passwd",
    ]
    
    for path in attacks:
        response = client.get(path)
        assert response.status_code == 404, f"Path traversal not blocked: {path}"
```

### 3.2 Integration Tests (4h)

```python
# tests/integration/test_device_flow.py
@pytest.mark.asyncio
async def test_discover_sync_persist_flow():
    """E2E: Device discovery → sync → persistence."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Discover
        r = await client.get("/api/devices/discover")
        assert r.status_code == 200
        
        # 2. Sync
        r = await client.post("/api/devices/sync")
        assert r.status_code == 200
        
        # 3. Verify persisted
        r = await client.get("/api/devices")
        assert r.status_code == 200
```

### 3.3 Frontend Tests (8h)

```typescript
// RadioPresets.test.tsx
describe('RadioPresets', () => {
  it('renders all 6 preset slots', () => {
    render(<RadioPresets device={mockDevice} presets={[]} />);
    expect(screen.getAllByRole('button')).toHaveLength(6);
  });

  it('shows station info when preset assigned', () => {
    const presets = [{ preset_number: 1, station_name: 'Test FM' }];
    render(<RadioPresets device={mockDevice} presets={presets} />);
    expect(screen.getByText('Test FM')).toBeInTheDocument();
  });
});
```

**Exit Criteria**:
- [ ] Coverage ≥85%
- [ ] Integration tests green
- [ ] Frontend has ≥5 component tests
- [ ] All error handlers have tests

---

## Phase 4: Architecture Refinement (Woche 6-7)

### Sprint Goal: Clean Architecture Compliance

| ID | Finding | Action | Effort | Priority |
|----|---------|--------|--------|----------|
| **ARCH-02** | No Protocol Interfaces | Add typing.Protocol abstractions | 4h | P2 |
| **ARCH-03** | Model in Repository File | Separate models.py | 1h | P3 |
| **ARCH-06** | Inconsistent Error Handling | Unified exception strategy | 2h | P2 |
| **BE-07** | No Retry Logic | Add httpx retry for RadioBrowser | 2h | P2 |

**Total Effort**: ~9 hours

### 4.1 Protocol Interfaces (4h)

```python
# devices/interfaces.py (NEU)
from typing import Protocol

class IDeviceRepository(Protocol):
    async def get_all(self) -> list[Device]: ...
    async def get_by_id(self, device_id: str) -> Device | None: ...
    async def upsert(self, device: Device) -> None: ...

class IDiscoveryAdapter(Protocol):
    async def discover(self, timeout: int = 10) -> list[DiscoveredDevice]: ...
```

### 4.2 Unified Exception Handling (2h)

```python
# core/exceptions.py (ERWEITERUNG)
class OCTError(Exception):
    """Base exception for all OCT errors."""
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code

class DeviceNotFoundError(OCTError):
    def __init__(self, device_id: str):
        super().__init__(f"Device {device_id} not found", "DEVICE_NOT_FOUND")

class DiscoveryTimeoutError(OCTError):
    def __init__(self, timeout: int):
        super().__init__(f"Discovery timed out after {timeout}s", "DISCOVERY_TIMEOUT")
```

```python
# main.py (ERWEITERUNG)
@app.exception_handler(OCTError)
async def oct_error_handler(request: Request, exc: OCTError):
    return JSONResponse(
        status_code=400,
        content={"error": exc.code, "message": exc.message}
    )
```

**Exit Criteria**:
- [ ] All services use Protocol types
- [ ] Models in separate files
- [ ] All routes use custom exceptions

---

## Phase 5: Frontend Modernization (Woche 8-9)

### Sprint Goal: Production-Ready Frontend

| ID | Finding | Action | Effort | Priority |
|----|---------|--------|--------|----------|
| **FE-01** | useState for Server Data | Add useSWR/React Query | 4h | P2 |
| **FE-02** | Manual Error Handling | Implement error boundaries | 2h | P2 |
| **FE-04** | Inline Fetch in Handlers | Extract to API service | 2h | P2 |
| **FE-05** | No Loading States | Add loading indicators | 2h | P3 |

**Total Effort**: ~10 hours

### 5.1 React Query Integration (4h)

```bash
npm install @tanstack/react-query
```

```typescript
// hooks/useDevices.ts (NEU)
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiService } from '../services/api';

export function useDevices() {
  return useQuery({
    queryKey: ['devices'],
    queryFn: () => apiService.getDevices(),
    staleTime: 30_000,
  });
}

export function useSyncDevices() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiService.syncDevices(),
    onSuccess: () => queryClient.invalidateQueries(['devices']),
  });
}
```

### 5.2 Error Boundaries (2h)

```typescript
// components/ErrorBoundary.tsx (NEU)
class ErrorBoundary extends Component<Props, State> {
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-fallback">
          <h2>Etwas ist schiefgelaufen</h2>
          <button onClick={() => window.location.reload()}>
            Neu laden
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

**Exit Criteria**:
- [ ] React Query installed and configured
- [ ] All API calls use React Query hooks
- [ ] Error boundaries wrap major sections
- [ ] Loading states visible

---

## Phase 6: Build & Deploy Hardening (Woche 10)

### Sprint Goal: Production-Ready Infrastructure

| ID | Finding | Action | Effort | Priority |
|----|---------|--------|--------|----------|
| **BUILD-02** | No .dockerignore | Create .dockerignore | 0.5h | P3 |
| **BUILD-03** | Unpinned Base Images | Pin with SHA256 | 1h | P2 |
| **BUILD-04** | No Security Scanning | Add Trivy to CI | 1h | P2 |

**Total Effort**: ~2.5 hours

### 6.1 .dockerignore (0.5h)

```
# .dockerignore
.git
.gitignore
*.md
!README.md
docs/
htmlcov/
.pytest_cache/
__pycache__/
*.pyc
node_modules/
.venv/
*.egg-info/
.coverage
```

### 6.2 Trivy Scanning (1h)

```yaml
# .github/workflows/ci.yml (ERWEITERUNG)
- name: Build Docker image
  run: docker build -t opencloudtouch:test .

- name: Scan for vulnerabilities
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'opencloudtouch:test'
    severity: 'HIGH,CRITICAL'
    exit-code: '1'
```

**Exit Criteria**:
- [ ] Build time reduced by ≥20%
- [ ] No HIGH/CRITICAL CVEs
- [ ] Base images pinned

---

## Timeline Visualization

```
Week 1  │ PHASE 1: Critical Security
        │ └── BE-01 Path Traversal Fix
        │
Week 2  │ PHASE 2: Foundation
Week 3  │ └── DI Migration, CI Setup, Dependabot
        │
Week 4  │ PHASE 3: Test Coverage
Week 5  │ └── Integration Tests, Frontend Tests
        │
Week 6  │ PHASE 4: Architecture
Week 7  │ └── Protocols, Exception Handling
        │
Week 8  │ PHASE 5: Frontend
Week 9  │ └── React Query, Error Boundaries
        │
Week 10 │ PHASE 6: Build Hardening
        │ └── Docker optimization, Security scanning
```

---

## Effort Summary

| Phase | Description | Hours | Week |
|-------|-------------|-------|------|
| 1 | Critical Security | 2h | 1 |
| 2 | Foundation Fixes | 9h | 2-3 |
| 3 | Test Coverage | 17h | 4-5 |
| 4 | Architecture | 9h | 6-7 |
| 5 | Frontend | 10h | 8-9 |
| 6 | Build/Deploy | 2.5h | 10 |
| **Total** | | **~50h** | **10 weeks** |

---

## Success Metrics

| Metric | Current | Target | Phase |
|--------|---------|--------|-------|
| Security vulnerabilities | 1 P1 | 0 P1 | 1 |
| Test coverage | ~78% | ≥85% | 3 |
| CI pipeline | None | Green | 2 |
| Frontend tests | 0 | ≥10 | 3 |
| Response time p95 | Unknown | <100ms | 5 |
| Docker build time | ~2min | <1.5min | 6 |

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| bosesoundtouchapi abandoned | High | Adapter pattern allows swap |
| React Query learning curve | Medium | Start with simple hooks |
| Breaking changes in majors | Medium | Pin versions, Dependabot |
| CI build time explosion | Low | Cache layers, minimize deps |

---

## Quick Wins (Can do anytime)

Diese Items erfordern <1h und können jederzeit erledigt werden:

- [ ] Add .dockerignore
- [ ] Enable Dependabot
- [ ] Fix pytest pythonpath
- [ ] Add security test for path traversal
- [ ] Pin Docker base images
- [ ] Generate license audit

---

## Definition of Done

Ein Phase gilt als abgeschlossen wenn:

1. ✅ Alle Tasks der Phase implementiert
2. ✅ Tests für neue Funktionalität grün
3. ✅ Code Review durchgeführt
4. ✅ Dokumentation aktualisiert
5. ✅ CI Pipeline grün
6. ✅ User-Abnahme (bei UI-Änderungen)

---

**Nächster Schritt**: Phase 1 starten - Path Traversal Fix in main.py serve_spa()
