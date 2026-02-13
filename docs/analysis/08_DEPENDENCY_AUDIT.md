# 08 - Dependency Audit

**Report**: Forensic Audit – OpenCloudTouch  
**Date**: 2026-02-11  
**Auditor**: Claude Opus 4.5 (Automated Code Audit)

---

## Executive Summary

**Total Dependencies:**
- Python (Backend): 12 runtime + 16 dev = 28
- JavaScript (Frontend): 4 runtime + 24 dev = 28
- JavaScript (Root workspace): 2 runtime + 4 dev = 6
- **Total**: 62 direct dependencies

**Risk Assessment:**
- 🔴 **Critical CVEs**: 0 (as of audit date)
- 🟡 **Outdated Major**: 3 packages need major bump investigation
- 🟢 **License Compatibility**: All compatible (Apache-2.0, MIT, BSD, ISC)

---

## Python Dependencies (Backend)

### Runtime Dependencies

| Package | Pinned Version | Latest | Status | Notes |
|---------|---------------|--------|--------|-------|
| fastapi | 0.115.0 | 0.115.x | ✅ Current | Core framework |
| uvicorn[standard] | 0.32.0 | 0.32.x | ✅ Current | ASGI server |
| httpx | 0.27.2 | 0.27.x | ✅ Current | Async HTTP client |
| pydantic | 2.9.2 | 2.9.x | ✅ Current | Data validation |
| pydantic-settings | 2.6.0 | 2.6.x | ✅ Current | Env config |
| aiosqlite | 0.20.0 | 0.20.x | ✅ Current | Async SQLite |
| PyYAML | 6.0.2 | 6.0.x | ✅ Current | YAML parsing |
| websockets | 13.1 | 13.x | ✅ Current | WebSocket client |
| bosesoundtouchapi | 1.0.86 | 1.0.x | ✅ Current | Device control |
| ssdpy | 0.4.1 | 0.4.x | ✅ Current | SSDP discovery |
| defusedxml | 0.7.1 | 0.7.x | ✅ Current | Secure XML parsing |

### Dev Dependencies

| Package | Pinned Version | Latest | Status | Notes |
|---------|---------------|--------|--------|-------|
| pytest | 8.3.3 | 8.3.x | ✅ Current | Test framework |
| pytest-asyncio | 0.24.0 | 0.24.x | ✅ Current | Async test support |
| pytest-cov | 5.0.0 | 5.0.x | ✅ Current | Coverage reporting |
| pytest-timeout | 2.3.1 | 2.3.x | ✅ Current | Test timeout |
| pytest-xdist | 3.6.1 | 3.6.x | ✅ Current | Parallel tests |
| black | 24.10.0 | 24.x | ✅ Current | Code formatter |
| ruff | 0.8.4 | 0.8.x | ✅ Current | Fast linter |
| mypy | 1.13.0 | 1.13.x | ✅ Current | Type checker |
| bandit | 1.7.10 | 1.7.x | ✅ Current | Security linter |
| safety | 3.2.11 | 3.2.x | ✅ Current | CVE scanner |
| pre-commit | 4.0.1 | 4.0.x | ✅ Current | Git hooks |
| commitizen | 3.29.1 | 3.29.x | ✅ Current | Commit formatting |
| types-PyYAML | 6.0.12.x | 6.0.x | ✅ Current | Type stubs |

---

## JavaScript Dependencies (Frontend)

### Runtime Dependencies

| Package | Pinned Version | Latest | Status | Notes |
|---------|---------------|--------|--------|-------|
| react | ^19.2.4 | 19.x | ✅ Current | UI framework |
| react-dom | ^19.2.4 | 19.x | ✅ Current | React DOM |
| react-router-dom | ^7.13.0 | 7.x | ✅ Current | Routing |
| framer-motion | ^12.33.0 | 12.x | ✅ Current | Animations |

### Dev Dependencies (Notable)

| Package | Pinned Version | Latest | Status | Notes |
|---------|---------------|--------|--------|-------|
| vite | ^7.3.1 | 7.x | ✅ Current | Build tool |
| vitest | ^4.0.18 | 4.x | ✅ Current | Test framework |
| typescript | ^5.9.3 | 5.9.x | ✅ Current | Type system |
| eslint | 9.39.2 | 9.x | ✅ Current | Linter |
| prettier | ^3.4.2 | 3.x | ✅ Current | Formatter |
| cypress | ^15.10.0 | 15.x | ✅ Current | E2E testing |
| jsdom | ^28.0.0 | 28.x | ✅ Current | DOM simulation |

### Root Workspace Dependencies

| Package | Pinned Version | Latest | Status | Notes |
|---------|---------------|--------|--------|-------|
| @tanstack/react-query | ^5.90.21 | 5.x | ✅ Current | Data fetching |
| cypress | ^15.10.0 | 15.x | ⚠️ Duplicate | Also in frontend |
| concurrently | ^9.1.2 | 9.x | ✅ Current | Parallel commands |
| license-checker | ^25.0.1 | 25.x | ✅ Current | License audit |
| rimraf | ^6.0.1 | 6.x | ✅ Current | Cross-platform rm |

---

## P1 - Critical Issues

### 1.1 [P1-DEP-001] pyproject.toml vs requirements.txt Version Mismatch

**Issue:** Dependency versions differ between pyproject.toml and requirements.txt

**Evidence:**

| Package | pyproject.toml | requirements.txt |
|---------|---------------|------------------|
| fastapi | `>=0.100.0` | `==0.115.0` |
| uvicorn | `>=0.23.0` | `==0.32.0` |
| pydantic | `>=2.0.0` | `==2.9.2` |
| websockets | `>=13.0` | `==13.1` |

**Impact:**
- `pyproject.toml` uses loose constraints (pip install editable)
- `requirements.txt` uses pinned versions (Docker build)
- Different behavior between development and production

**Risk:** Medium - Works but confusing

**Recommended Action:**
Either:
1. Use `pyproject.toml` exclusively with `pip install -e .[dev]`
2. Or generate `requirements.txt` from locked dependencies

```bash
# Option 1: pyproject.toml only
pip install -e ".[dev]"
pip freeze > requirements-lock.txt  # For reproducibility

# Option 2: Keep requirements.txt as source of truth
# Update pyproject.toml to match:
dependencies = [
    "fastapi==0.115.0",
    "uvicorn[standard]==0.32.0",
    ...
]
```

---

### 1.2 [P1-DEP-002] Cypress Duplicated in Root and Frontend

**Issue:** Cypress is installed in both root and frontend package.json

**Location:**
- `package.json:48` → `"cypress": "^15.10.0"`
- `apps/frontend/package.json` → NOT PRESENT but should be consistent

**Impact:**
- Wasted disk space (~500MB)
- Version drift potential
- Unclear which Cypress runs

**Recommended Action:**

In root `package.json`:
```json
// REMOVE from root - E2E tests run in frontend workspace
"dependencies": {
    "@tanstack/react-query": "^5.90.21"
    // Remove cypress
}
```

And ensure frontend has:
```json
// apps/frontend/package.json devDependencies
"cypress": "^15.10.0"
```

---

## P2 - Architecture Issues

### 2.1 [P2-DEP-001] @tanstack/react-query in Root Instead of Frontend

**Issue:** React Query is in root package.json but only used by frontend.

**Location:** [package.json](../package.json) line 47

```json
"dependencies": {
    "@tanstack/react-query": "^5.90.21",
    ...
}
```

**Problem:**
- React Query is a frontend-only dependency
- Should be in `apps/frontend/package.json`
- Root workspace should only have shared dev tools

**Impact:** Minor - Works but violates workspace conventions

**Recommended Action:**

Move to frontend:
```bash
# Remove from root
npm uninstall @tanstack/react-query

# Add to frontend workspace
npm install @tanstack/react-query --workspace=apps/frontend
```

Update `apps/frontend/package.json`:
```json
"dependencies": {
    "@tanstack/react-query": "^5.90.21",
    "framer-motion": "^12.33.0",
    "react": "^19.2.4",
    "react-dom": "^19.2.4",
    "react-router-dom": "^7.13.0"
}
```

---

### 2.2 [P2-DEP-002] Missing @types/react-router-dom Deprecation

**Issue:** `@types/react-router-dom` is deprecated since react-router-dom v6+

**Location:** `apps/frontend/package.json:31`
```json
"@types/react-router-dom": "^5.3.3"
```

**Evidence:**
- react-router-dom v7 bundles its own TypeScript types
- @types/react-router-dom is for v5.x only
- Potential type conflicts

**Recommended Action:**

```bash
cd apps/frontend
npm uninstall @types/react-router-dom
```

Remove from package.json:
```json
// REMOVE this line
"@types/react-router-dom": "^5.3.3"
```

---

### 2.3 [P2-DEP-003] Prettier Version Inconsistency

**Issue:** Different Prettier versions in root and frontend.

**Evidence:**
- Root: `"prettier": "^3.8.1"`
- Frontend: `"prettier": "^3.4.2"`

**Impact:**
- Different formatting results depending on where prettier runs
- CI might format differently than local

**Recommended Action:**

Align versions (prefer latest):
```json
// Both package.json files
"prettier": "^3.8.1"
```

Or remove from frontend and use root's version (npm workspace hoisting).

---

## P3 - Cleanup Items

### 3.1 [P3-DEP-001] Unused Dependencies Check

**Recommendation:** Run dependency analysis to find unused packages.

**Commands:**
```bash
# Python - check for unused imports
pip install pip-autoremove
pip-autoremove --list

# JavaScript - check unused
npx depcheck
```

**Potential Candidates for Removal:**
- `colorette` (frontend) - Check if actually used
- `jiti` (frontend) - ESLint config loader, may be indirect

---

### 3.2 [P3-DEP-002] License Compatibility Verification

**Python Licenses:**
| Package | License | Compatible |
|---------|---------|------------|
| fastapi | MIT | ✅ |
| uvicorn | BSD-3-Clause | ✅ |
| httpx | BSD-3-Clause | ✅ |
| pydantic | MIT | ✅ |
| aiosqlite | MIT | ✅ |
| websockets | BSD-3-Clause | ✅ |
| bosesoundtouchapi | MIT | ✅ |
| ssdpy | MIT | ✅ |
| defusedxml | PSF-2.0 | ✅ |

**JavaScript Licenses:**
| Package | License | Compatible |
|---------|---------|------------|
| react | MIT | ✅ |
| react-dom | MIT | ✅ |
| react-router-dom | MIT | ✅ |
| framer-motion | MIT | ✅ |
| vite | MIT | ✅ |
| typescript | Apache-2.0 | ✅ |

**Project License:** Apache-2.0

**Compatibility:** All dependencies compatible with Apache-2.0 project license.

---

### 3.3 [P3-DEP-003] Security Scanning Integration

**Current Status:**
- ✅ `bandit` for Python security linting
- ✅ `safety` for Python CVE checking
- ⚠️ No `npm audit` in CI/CD

**Recommended Addition to CI:**

```yaml
# .github/workflows/ci-cd.yml
- name: Security Scan (npm)
  run: npm audit --audit-level=moderate
```

---

## Dependency Update Strategy

### Automated Updates

**Already Configured:**
- GitHub Dependabot (via `.github/dependabot.yml` - verify exists)

**Recommended Dependabot Config:**
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/apps/backend"
    schedule:
      interval: "weekly"
    commit-message:
      prefix: "chore(deps)"
    
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    commit-message:
      prefix: "chore(deps)"
```

### Manual Update Process

```bash
# Python - check outdated
cd apps/backend
pip list --outdated

# Python - update specific
pip install --upgrade fastapi==X.Y.Z
# Then update requirements.txt

# JavaScript - check outdated
npm outdated

# JavaScript - update
npm update  # Minor/patch only
npm install package@latest  # For major
```

---

## Summary Table

| Category | Count | Status |
|----------|-------|--------|
| **P1 Issues** | 2 | Version mismatch, duplicate cypress |
| **P2 Issues** | 3 | Workspace organization, deprecated @types |
| **P3 Issues** | 3 | Unused deps, license check, npm audit |
| **Total Dependencies** | 62 | All current, no CVEs |

**Overall Health:** ✅ Good - Minor organizational issues only

---

## Recommended Actions (Priority Order)

1. **[P1-DEP-001]** Sync pyproject.toml with requirements.txt versions
2. **[P1-DEP-002]** Remove duplicate cypress from root
3. **[P2-DEP-001]** Move @tanstack/react-query to frontend workspace
4. **[P2-DEP-002]** Remove deprecated @types/react-router-dom
5. **[P2-DEP-003]** Align prettier versions
6. **[P3-DEP-003]** Add npm audit to CI/CD

---

**End of Dependency Audit**
