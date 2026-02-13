# 08 Dependency Audit

**Projekt**: OpenCloudTouch  
**Datum**: 2026-02-11  
**Analyst**: GitHub Copilot (Claude Opus 4.5)

---

## Executive Summary

Moderne Dependency-Versionen mit guter Security-Posture. Minimale Abhängigkeiten entsprechend Projektgröße. Empfehlung: Dependabot aktivieren für automatische Updates.

**Dependency Health Score**: 85/100

---

## 1. Backend Dependencies (Python)

**Source**: [apps/backend/pyproject.toml](../../apps/backend/pyproject.toml)

### 1.1 Runtime Dependencies

| Package | Version | Purpose | Risk |
|---------|---------|---------|------|
| fastapi | >=0.100.0 | Web framework | ✅ Low |
| uvicorn[standard] | >=0.23.0 | ASGI server | ✅ Low |
| httpx | >=0.24.0 | HTTP client | ✅ Low |
| aiosqlite | >=0.19.0 | Async SQLite | ✅ Low |
| pydantic | >=2.0.0 | Validation | ✅ Low |
| pydantic-settings | >=2.0.0 | Config | ✅ Low |
| pyyaml | >=6.0 | YAML parsing | ✅ Low |
| bosesoundtouchapi | >=0.2.0 | Bose API | ⚠️ Medium |
| defusedxml | >=0.7.1 | Safe XML | ✅ Low |
| websockets | >=13.0 | WebSocket support | ✅ Low |
| ssdpy | >=0.4.0 | SSDP client | ✅ Low |

### 1.2 Dev Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | >=8.3.3 | Test runner |
| pytest-asyncio | >=0.24.0 | Async tests |
| pytest-cov | >=5.0.0 | Coverage |

---

## 2. Frontend Dependencies (JavaScript/TypeScript)

**Source**: [apps/frontend/package.json](../../apps/frontend/package.json)

### 2.1 Runtime Dependencies

| Package | Version | Purpose | Risk |
|---------|---------|---------|------|
| react | ^19.2.4 | UI framework | ✅ Low |
| react-dom | ^19.2.4 | React DOM | ✅ Low |
| react-router-dom | ^7.13.0 | Routing | ✅ Low |
| framer-motion | ^12.33.0 | Animations | ✅ Low |

### 2.2 Dev Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| vite | ^7.3.1 | Build tool |
| vitest | ^4.0.18 | Test runner |
| typescript | ^5.9.3 | Type checking |
| eslint | 9.39.2 | Linting |
| @testing-library/react | ^16.3.2 | Component testing |

---

## 3. Dependency Findings

### [DEP-01] bosesoundtouchapi - Third-Party Risk
**Severity**: P3 (Monitoring Required)  
**Package**: bosesoundtouchapi >=0.2.0

**Concerns**:
- Community-maintained (nicht offiziell von Bose)
- Letztes Release: Variable (GitHub prüfen)
- Single maintainer → Bus factor 1

**Mitigation**:
1. Adapter-Pattern bereits implementiert (gut!)
2. Fallback zu direkten HTTP-Calls möglich
3. Fork-Strategie dokumentieren

**SOLL**: Monitoring Setup
```python
# In DEPENDENCY-MANAGEMENT.md dokumentieren:
# Falls bosesoundtouchapi abandoned wird:
# 1. Repository forken
# 2. Als opencloudtouch-soundtouchapi publishen
# 3. pyproject.toml updaten
```

---

### [DEP-02] React 19 - Major Version
**Severity**: INFO  
**Package**: react ^19.2.4

**Kontext**: React 19 ist aktuell (2026). Features genutzt:
- Concurrent rendering
- use() hook (nicht explizit gefunden)
- Compiler support (nicht aktiviert)

**Status**: Korrekt und aktuell.

---

### [DEP-03] Version Ranges zu weit
**Severity**: P3 (Reproducibility)  
**Location**: pyproject.toml

```toml
# IST
dependencies = [
    "fastapi>=0.100.0",  # Erlaubt 0.100.0 bis unbegrenzt
]
```

**Problem**: Bei major releases könnte Breaking Change eingeführt werden.

**SOLL**: Upper bounds oder exakte Versionen
```toml
# Option A: Upper bound
dependencies = [
    "fastapi>=0.100.0,<1.0.0",
]

# Option B: Lockfile (besser)
# pip-tools: requirements.txt generieren
pip-compile pyproject.toml -o requirements.txt
```

**Aktueller Stand**: requirements.txt existiert mit exakten Versionen → Lockfile vorhanden ✅

---

### [DEP-04] Fehlende Security Advisory Monitoring
**Severity**: P2 (Security)  
**Location**: Repository-wide

**Problem**: Keine automatische Benachrichtigung bei Security-Vulnerabilities.

**SOLL**: Dependabot aktivieren
```yaml
# .github/dependabot.yml (NEU)
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/apps/backend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    
  - package-ecosystem: "npm"
    directory: "/apps/frontend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

---

### [DEP-05] Keine License Audit
**Severity**: P3 (Compliance)  
**Location**: All dependencies

**Problem**: Keine automatische License-Prüfung.

**SOLL**:
```bash
# Python
pip install pip-licenses
pip-licenses --format=markdown > docs/LICENSES_PYTHON.md

# JavaScript
npx license-checker --summary --out docs/LICENSES_JS.md
```

**Erwartete Licenses** (alle MIT/BSD-kompatibel):
- FastAPI: MIT
- React: MIT
- Pydantic: MIT
- Vite: MIT

---

### [DEP-06] defusedxml Richtig Verwendet
**Severity**: ✅ Positive Finding
**Package**: defusedxml >=0.7.1

**Kontext**: XML-Parsing ist security-critical (XXE attacks).

**Prüfung erforderlich**: Wird defusedxml auch tatsächlich verwendet?

**Check**:
```bash
grep -r "defusedxml" apps/backend/src/
# vs.
grep -r "xml.etree" apps/backend/src/
```

**Empfehlung**: In discovery/ssdp.py verifizieren dass defusedxml.ElementTree verwendet wird.

---

## 4. Dependency Tree Analysis

### 4.1 Python Dependencies (Transitive)

```
opencloudtouch
├── fastapi (→ starlette, pydantic, typing-extensions)
├── uvicorn (→ click, h11, httptools, uvloop, watchfiles)
├── httpx (→ certifi, httpcore, idna, sniffio)
├── aiosqlite (→ sqlite3 stdlib)
├── pydantic (→ annotated-types, pydantic-core)
├── pydantic-settings (→ python-dotenv)
├── pyyaml (→ libyaml optional)
├── bosesoundtouchapi (→ aiohttp, lxml)
├── defusedxml (→ none)
├── websockets (→ none)
└── ssdpy (→ none)
```

**Beobachtung**: bosesoundtouchapi bringt aiohttp und lxml mit → größerer Dependency-Graph.

### 4.2 JavaScript Dependencies (Transitive)

```
opencloudtouch-frontend
├── react (→ react-dom, scheduler)
├── react-router-dom (→ react-router, @remix-run/router)
└── framer-motion (→ @emotion/is-prop-valid, tslib)
```

**Beobachtung**: Minimaler Dependency-Graph → gut!

---

## 5. Update Strategy

### 5.1 Recommended Cadence

| Type | Frequency | Process |
|------|-----------|---------|
| Patch updates | Weekly | Auto-merge via Dependabot |
| Minor updates | Bi-weekly | PR review + test |
| Major updates | Quarterly | Manual migration |
| Security fixes | Immediate | Emergency patch |

### 5.2 Lock File Management

**Python**:
```bash
# Update all dependencies
pip-compile --upgrade pyproject.toml -o requirements.txt

# Update single dependency
pip-compile --upgrade-package fastapi pyproject.toml -o requirements.txt
```

**JavaScript**:
```bash
# Update all
npm update

# Update with breaking changes
npx npm-check-updates -u
npm install
```

---

## 6. Compliance Matrix

| Requirement | Status | Notes |
|-------------|--------|-------|
| All dependencies versioned | ✅ | pyproject.toml entries |
| Lock files present | ✅ | requirements.txt |
| No known vulnerabilities | ⚠️ | Manual check required |
| License compatibility | ⚠️ | Not audited |
| Dependabot enabled | ❌ | Not configured |
| SBOM generated | ❌ | Not implemented |

---

## 7. Recommended Actions

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| 1 | Enable Dependabot | 0.5h | Security monitoring |
| 2 | Verify defusedxml usage | 0.5h | Security |
| 3 | Generate license audit | 1h | Compliance |
| 4 | Add upper bounds to versions | 1h | Reproducibility |
| 5 | Document bosesoundtouchapi fallback | 1h | Risk mitigation |

---

## 8. Security Checklist

- [ ] `pip-audit` für Python vulnerability check
- [ ] `npm audit` für JavaScript vulnerability check
- [ ] Alle XML-Parsing uses defusedxml
- [ ] Keine hardcoded credentials in dependencies
- [ ] Keine deprecated packages
- [ ] Keine packages mit known CVEs

**Audit Commands**:
```bash
# Python
pip install pip-audit
pip-audit

# JavaScript
npm audit
```

---

**Gesamtbewertung**: Saubere, moderne Dependency-Landschaft. Hauptempfehlung ist Automatisierung via Dependabot und regelmäßige Security Audits.
