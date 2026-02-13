# 09 - Prioritized Roadmap

**Report**: Forensic Audit – OpenCloudTouch  
**Date**: 2026-02-11  
**Auditor**: Claude Opus 4.5 (Automated Code Audit)

---

## Executive Summary

**Audit Scope:** Complete forensic analysis of OpenCloudTouch codebase  
**Files Analyzed:** ~90 source files (40 Python, 25 TypeScript, configs, scripts)  
**Tests Found:** 351 backend tests, ~20 frontend tests  
**Documents Produced:** 9 analysis reports

**Overall Assessment:** 🟢 **Production-Ready with Minor Issues**

The codebase demonstrates professional quality:
- Clean Architecture properly implemented
- Comprehensive test coverage (80%+)
- Modern tech stack (FastAPI, React 19, TypeScript 5)
- Good CI/CD pipeline
- Proper security practices (defusedxml, path traversal protection)

**Critical Bugs Found:** 1 (P1-001 in interfaces.py)  
**Architecture Issues:** 7 (P2 category)  
**Cleanup Items:** 15+ (P3 category)

---

## P1 - Critical Issues (Fix Immediately)

### P1-001: Indentation Bug in interfaces.py

**Report:** [03_BACKEND_CODE_REVIEW.md](03_BACKEND_CODE_REVIEW.md#p1-001)  
**File:** [devices/interfaces.py](../../apps/backend/src/opencloudtouch/devices/interfaces.py#L98)  
**Severity:** 🔴 Critical - Will cause runtime AttributeError  
**Effort:** 5 minutes

**Problem:**
```python
# Line 98 - Method defined OUTSIDE class body
class IDeviceSyncService(Protocol):
    ...

async def sync(self) -> tuple[int, int]:  # WRONG INDENTATION
```

**Fix:**
```python
class IDeviceSyncService(Protocol):
    """Protocol for device synchronization services."""

    async def sync(self) -> tuple[int, int]:  # Properly indented
        """Synchronize devices.
        
        Returns:
            Tuple of (devices_added, devices_updated)
        """
        ...
```

**Verification:**
```bash
cd apps/backend
pytest tests/ -v -k "sync"
```

---

## P2 - Architecture Issues (Fix This Sprint)

### P2-001: CORS Allows All Origins in Production

**Report:** [03_BACKEND_CODE_REVIEW.md](03_BACKEND_CODE_REVIEW.md#p2-001)  
**File:** [main.py](../../apps/backend/src/opencloudtouch/main.py#L86-92)  
**Effort:** 30 minutes

**Current State:**
```python
allow_origins=config.cors_origins or ["*"]
```

**Fix:**
```python
# In core/config.py
cors_origins: list[str] = Field(
    default=["http://localhost:5173", "http://localhost:7777"],
    description="Allowed CORS origins"
)

# In main.py
if config.cors_origins == ["*"]:
    logger.warning("CORS allows all origins - not recommended for production")
```

---

### P2-002: SQLite Index Name Collision

**Report:** [03_BACKEND_CODE_REVIEW.md](03_BACKEND_CODE_REVIEW.md#p2-002)  
**File:** [presets/repository.py](../../apps/backend/src/opencloudtouch/presets/repository.py#L45)  
**Effort:** 15 minutes

**Problem:** Both devices and presets use `idx_device_id`

**Fix:**
```python
# presets/repository.py line 45
CREATE INDEX IF NOT EXISTS idx_presets_device_id ON presets(device_id)

# devices/repository.py - already correct
CREATE INDEX IF NOT EXISTS idx_devices_device_id ON devices(device_id)
```

---

### P2-003: RadioStation Model Duplicated

**Report:** [03_BACKEND_CODE_REVIEW.md](03_BACKEND_CODE_REVIEW.md#p2-003)  
**Files:** 
- `radio/providers/__init__.py`
- `radio/providers/radiobrowser.py`
- `presets/models.py`  
**Effort:** 1 hour

**Fix:** Create single source of truth:
```python
# radio/models.py (NEW FILE)
from pydantic import BaseModel

class RadioStation(BaseModel):
    """Unified radio station model."""
    name: str
    stream_url: str
    logo_url: str | None = None
    country: str | None = None
    genre: str | None = None
    bitrate: int | None = None

# Import everywhere from this single location
from opencloudtouch.radio.models import RadioStation
```

---

### P2-004: Dependency Version Mismatch

**Report:** [08_DEPENDENCY_AUDIT.md](08_DEPENDENCY_AUDIT.md#p1-dep-001)  
**Files:** `pyproject.toml`, `requirements.txt`  
**Effort:** 30 minutes

**Fix:** Sync pyproject.toml with requirements.txt pinned versions:
```toml
dependencies = [
    "fastapi==0.115.0",
    "uvicorn[standard]==0.32.0",
    "httpx==0.27.2",
    # ... match requirements.txt exactly
]
```

---

### P2-005: Move @tanstack/react-query to Frontend

**Report:** [08_DEPENDENCY_AUDIT.md](08_DEPENDENCY_AUDIT.md#p2-dep-001)  
**File:** Root `package.json`  
**Effort:** 10 minutes

```bash
npm uninstall @tanstack/react-query
npm install @tanstack/react-query --workspace=apps/frontend
```

---

### P2-006: Remove Deprecated @types/react-router-dom

**Report:** [08_DEPENDENCY_AUDIT.md](08_DEPENDENCY_AUDIT.md#p2-dep-002)  
**Effort:** 5 minutes

```bash
cd apps/frontend
npm uninstall @types/react-router-dom
```

---

### P2-007: Create Missing Documentation

**Report:** [07_DOCUMENTATION_GAPS.md](07_DOCUMENTATION_GAPS.md)  
**Effort:** 2 hours

**Required:**
1. `docs/API.md` - API reference with endpoints table
2. `docs/TROUBLESHOOTING.md` - Common issues and solutions
3. `SECURITY.md` - Security policy
4. `CHANGELOG.md` - Release history

---

### P2-008: Standardized Error Response Format

**Report:** User feedback (2026-02-13)  
**Files:** All API endpoints, exception handlers  
**Effort:** 3 hours  
**Priority:** High - Improves error handling UX

**Problem:**
- Backend returns inconsistent error formats (500 without response body, HTTP exceptions with different structures)
- Frontend cannot reliably parse and display error messages
- No standard error codes for client-side error categorization
- Radio search returns 500 errors without meaningful error details

**Current Issues:**
1. Device page shows "unknown IP, unknown Model, unknown device" (error handling missing)
2. Radio search modal: Fast/slow typing triggers 500 errors without error response body
3. No consistent error object structure across endpoints

**Solution:**
Create RFC 7807 Problem Details-inspired error response format:

```python
# core/exceptions.py (NEW)
from pydantic import BaseModel
from typing import Any

class ErrorDetail(BaseModel):
    """Standardized error response format."""
    type: str  # Error category: validation_error, not_found, server_error, etc.
    title: str  # Human-readable error title
    status: int  # HTTP status code
    detail: str  # Detailed error message
    instance: str | None = None  # Request path that triggered error
    errors: list[dict[str, Any]] | None = None  # Field-level validation errors

# Example responses:
# 404 Not Found
{
    "type": "not_found",
    "title": "Device Not Found",
    "status": 404,
    "detail": "Device with ID 'abc123' does not exist",
    "instance": "/api/devices/abc123"
}

# 422 Validation Error
{
    "type": "validation_error",
    "title": "Invalid Request Data",
    "status": 422,
    "detail": "Query parameter 'q' is required for search",
    "instance": "/api/radio/search",
    "errors": [
        {"field": "q", "message": "Field required", "type": "missing"}
    ]
}

# 500 Internal Server Error
{
    "type": "server_error",
    "title": "Internal Server Error",
    "status": 500,
    "detail": "Failed to connect to RadioBrowser API",
    "instance": "/api/radio/search"
}
```

**Implementation Steps:**

1. **Create exception handler** (`main.py`):
```python
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorDetail(
            type=_map_status_to_type(exc.status_code),
            title=exc.detail,
            status=exc.status_code,
            detail=exc.detail,
            instance=str(request.url.path)
        ).model_dump()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ErrorDetail(
            type="validation_error",
            title="Invalid Request Data",
            status=422,
            detail="Request validation failed",
            instance=str(request.url.path),
            errors=[
                {"field": ".".join(str(loc) for loc in err["loc"]), 
                 "message": err["msg"], 
                 "type": err["type"]}
                for err in exc.errors()
            ]
        ).model_dump()
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content=ErrorDetail(
            type="server_error",
            title="Internal Server Error",
            status=500,
            detail=str(exc) if config.debug else "An unexpected error occurred",
            instance=str(request.url.path)
        ).model_dump()
    )
```

2. **Update all endpoints** to use HTTPException with meaningful messages
3. **Create TypeScript interface** in frontend:
```typescript
// api/types.ts
export interface ApiError {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance?: string;
  errors?: Array<{
    field: string;
    message: string;
    type: string;
  }>;
}
```

4. **Update API error handling** in frontend:
```typescript
// api/errorHandler.ts
export function handleApiError(error: unknown): string {
  if (axios.isAxiosError(error) && error.response?.data) {
    const apiError = error.response.data as ApiError;
    return apiError.detail || apiError.title;
  }
  return "An unexpected error occurred";
}
```

**Benefits:**
- ✅ Consistent error format across all endpoints
- ✅ Frontend can display meaningful error messages
- ✅ Field-level validation errors for forms
- ✅ Error categorization (type field) for different UI treatments
- ✅ Better debugging with instance path
- ✅ Security: Generic messages in production (via config.debug flag)

**Testing:**
```bash
# Backend
pytest tests/integration/test_error_responses.py -v

# Manual testing
curl http://localhost:8000/api/devices/invalid-id
curl http://localhost:8000/api/radio/search (without query param)
curl http://localhost:8000/api/presets -X POST -d '{"invalid": "data"}'
```

---

## P3 - Cleanup Items (Next Sprint)

### Code Quality

| ID | Issue | File | Effort |
|----|-------|------|--------|
| P3-001 | Hardcoded polling interval | `hooks/usePolling.ts:4` | 10m |
| P3-002 | Magic number 6 for presets | `components/PresetButton.tsx` | 10m |
| P3-003 | Unused DeviceType enum | `devices/models.py` | 5m |
| P3-004 | Extract common API error handling | `api/*.ts` | 30m |
| P3-005 | Type assertions should be stricter | `api/presets.ts:73` | 15m |

### Documentation

| ID | Issue | File | Effort |
|----|-------|------|--------|
| P3-006 | Fix README.md typo (apps/apps/) | `README.md:127` | 2m |
| P3-007 | Fix config.example.yaml (ct.db→oct.db) | `config.example.yaml:9` | 2m |
| P3-008 | Add docs/adr/ directory with ADRs | New files | 1h |

### Dependencies

| ID | Issue | File | Effort |
|----|-------|------|--------|
| P3-009 | Remove duplicate cypress | Root `package.json` | 5m |
| P3-010 | Align prettier versions | Both `package.json` | 5m |
| P3-011 | Add npm audit to CI | `ci-cd.yml` | 10m |

### Tests

| ID | Issue | File | Effort |
|----|-------|------|--------|
| P3-012 | Add E2E device interaction tests | `cypress/e2e/` | 2h |
| P3-013 | Add frontend error boundary tests | `tests/` | 1h |
| P3-014 | Add API error response tests | `tests/integration/` | 1h |

---

## Implementation Tickets

### Sprint 1: Critical & Architecture (2-3 days)

```markdown
## Ticket 1.1: Fix interfaces.py Indentation Bug
**Priority:** P1
**Estimate:** 15 minutes
**Assignee:** Backend Dev

### Steps:
1. Open apps/backend/src/opencloudtouch/devices/interfaces.py
2. Find line 98 (`async def sync`)
3. Indent to be inside IDeviceSyncService class
4. Run: pytest tests/ -v
5. Commit: "fix(devices): correct indentation in IDeviceSyncService protocol"
```

```markdown  
## Ticket 1.2: Fix CORS Configuration
**Priority:** P2
**Estimate:** 30 minutes
**Assignee:** Backend Dev

### Steps:
1. Update core/config.py with explicit CORS origins list
2. Add warning log when CORS is wildcard
3. Update docs/CONFIGURATION.md with security note
4. Test: Verify frontend can still connect
5. Commit: "fix(security): restrict CORS origins in production"
```

```markdown
## Ticket 1.3: Fix SQLite Index Collision
**Priority:** P2
**Estimate:** 15 minutes
**Assignee:** Backend Dev

### Steps:
1. Open apps/backend/src/opencloudtouch/presets/repository.py
2. Line 45: Change idx_device_id → idx_presets_device_id
3. Delete existing database (data-local/oct.db)
4. Restart container to recreate schema
5. Commit: "fix(db): use unique index names per table"
```

```markdown
## Ticket 1.4: Consolidate RadioStation Model
**Priority:** P2
**Estimate:** 1 hour
**Assignee:** Backend Dev

### Steps:
1. Create apps/backend/src/opencloudtouch/radio/models.py
2. Move RadioStation class to new file
3. Update imports in:
   - radio/providers/__init__.py
   - radio/providers/radiobrowser.py
   - presets/models.py
4. Run: pytest tests/unit/radio -v
5. Commit: "refactor(radio): consolidate RadioStation model"
```

---

### Sprint 2: Documentation & Dependencies (2 days)

```markdown
## Ticket 2.1: Create API Documentation
**Priority:** P2
**Estimate:** 1 hour
**Assignee:** Any

### Steps:
1. Create docs/API.md using template from 07_DOCUMENTATION_GAPS.md
2. Export OpenAPI: curl http://localhost:7777/openapi.json > docs/api/openapi.json
3. Add endpoint tables for Devices, Presets, Radio, Settings
4. Commit: "docs(api): add REST API reference"
```

```markdown
## Ticket 2.2: Create Troubleshooting Guide
**Priority:** P2
**Estimate:** 1 hour
**Assignee:** DevOps

### Steps:
1. Create docs/TROUBLESHOOTING.md using template from 07_DOCUMENTATION_GAPS.md
2. Document: SSDP discovery issues, container startup, database errors
3. Include WSL2 multicast workarounds
4. Commit: "docs: add troubleshooting guide"
```

```markdown
## Ticket 2.3: Fix Dependency Issues
**Priority:** P2
**Estimate:** 30 minutes
**Assignee:** Any

### Steps:
1. Remove cypress from root package.json
2. Move @tanstack/react-query to apps/frontend/package.json
3. Remove @types/react-router-dom from frontend
4. Align prettier versions to ^3.8.1
5. Run: npm install
6. Commit: "chore(deps): clean up workspace dependencies"
```

---

### Sprint 3: Cleanup (1-2 days)

```markdown
## Ticket 3.1: Extract Frontend Constants
**Priority:** P3
**Estimate:** 30 minutes
**Assignee:** Frontend Dev

### Steps:
1. Create apps/frontend/src/constants/app.ts
2. Move magic numbers: polling interval, preset count, volume min/max
3. Import constants where used
4. Commit: "refactor(frontend): extract magic numbers to constants"
```

```markdown
## Ticket 3.2: Add Missing Tests
**Priority:** P3
**Estimate:** 4 hours
**Assignee:** QA

### Steps:
1. Add Cypress tests for device discovery flow
2. Add vitest tests for ErrorBoundary component
3. Add pytest tests for API error responses (400, 404, 500)
4. Ensure coverage stays ≥80%
5. Commit: "test: add missing integration and E2E tests"
```

---

## Metrics Dashboard

### Before Audit
| Metric | Value |
|--------|-------|
| Backend Tests | 351 |
| Frontend Tests | ~20 |
| Coverage | 80%+ |
| P1 Bugs | Unknown |
| Documentation | Partial |

### After Applying Fixes (Target)
| Metric | Target |
|--------|--------|
| Backend Tests | 360+ |
| Frontend Tests | 35+ |
| Coverage | 85%+ |
| P1 Bugs | 0 |
| Documentation | 100% |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| P1-001 not fixed causes production crash | High | Critical | Fix first, test immediately |
| CORS wildcard exposes to CSRF | Medium | High | Restrict before public deployment |
| Index collision corrupts data | Low | High | Delete DB, recreate schema |
| Documentation gaps hurt adoption | Medium | Medium | Prioritize API docs |

---

## Audit Completion Checklist

- [x] 01_PROJECT_OVERVIEW.md - File inventory
- [x] 02_ARCHITECTURE_ANALYSIS.md - Layer analysis
- [x] 03_BACKEND_CODE_REVIEW.md - Python code review
- [x] 04_FRONTEND_CODE_REVIEW.md - React/TS code review
- [x] 05_TESTS_ANALYSIS.md - Test coverage analysis
- [x] 06_BUILD_DEPLOY_ANALYSIS.md - CI/CD analysis
- [x] 07_DOCUMENTATION_GAPS.md - Doc coverage
- [x] 08_DEPENDENCY_AUDIT.md - Package analysis
- [x] 09_ROADMAP.md - This document

---

## Agent Execution Instructions

**For an AI agent implementing these fixes:**

1. **Start with P1-001** - This is a critical bug that will cause AttributeError
2. **Run tests after each fix** - `pytest tests/ -v` for backend
3. **Commit atomically** - One fix per commit, conventional format
4. **Do NOT use --no-verify** - Let pre-commit hooks validate
5. **Check terminal completion** - Wait for PS prompt before next command
6. **Silent execution** - Report only at end, max 20 lines

**Command to start:**
```bash
cd c:\DEV\private\soundtouch-bridge
# Fix P1-001 first, then run tests
```

---

**End of Prioritized Roadmap**

**Total Audit Time:** ~4 hours  
**Estimated Fix Time:** ~16 hours (2 sprints)  
**ROI:** High - Prevents production bugs, improves maintainability
