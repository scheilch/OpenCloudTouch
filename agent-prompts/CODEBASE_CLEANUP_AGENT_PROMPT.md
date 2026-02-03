# 🧹 CloudTouch Codebase & Documentation Cleanup - Agent Instructions

**Project**: CloudTouch (Bose SoundTouch Bridge)  
**Objective**: Eliminate technical debt, remove workarounds, consolidate documentation, achieve clean architecture  
**Execution**: Sequential phases with quality gates  
**Version**: 2026-02-03

---

## 📋 MISSION OVERVIEW

After extensive refactoring iterations, the codebase contains:
- ❌ Workarounds that treat symptoms instead of root causes
- ❌ Overly complex solutions from incremental problem-solving
- ❌ Deviations from standard practices (React, FastAPI, pytest best practices)
- ❌ Technical debt from rapid prototyping
- ❌ Verbose documentation with outdated information
- ❌ Duplicated or conflicting documentation

**GOAL**: Production-ready codebase with minimal complexity, clean architecture, and concise documentation.

---

## 🎯 PHASE 0: CONTEXT ACQUISITION (30 minutes)

### 0.1 Understand Application Purpose via Cypress E2E Tests

**Action**: Analyze Cypress test scenarios to extract:
- Core user workflows
- Business logic flow
- Feature set (device discovery, playback control, preset management, radio browsing)
- Integration points (Backend API, SoundTouch devices, RadioBrowser)

**Deliverable**: Temporary context document (1 page max):
```markdown
# CloudTouch - Application Context (TEMP)

## Purpose
[1 sentence: What does CloudTouch do?]

## User Workflows (from Cypress tests)
1. Device Discovery: [2-3 sentences]
2. Playback Control: [2-3 sentences]
3. Preset Management: [2-3 sentences]
4. Radio Browsing: [2-3 sentences]

## Technical Stack
- Frontend: [React version, key libraries]
- Backend: [FastAPI version, key dependencies]
- Testing: [Cypress, pytest, vitest versions]

## Architecture (from tests)
- API Endpoints: [list critical endpoints]
- State Management: [Redux/Context/other]
- External Services: [SoundTouch API, RadioBrowser API]
```

**Files to analyze**:
- `frontend/cypress/e2e/**/*.cy.js`
- `frontend/cypress/support/commands.js`
- `backend/tests/e2e/**/*.py`

---

## 🔍 PHASE 1: FRONTEND CODE ANALYSIS (60 minutes)

### 1.1 Static Code Analysis

**Tools to run**:
```powershell
# ESLint (JavaScript/React linting)
cd frontend
npm run lint -- --format json --output-file ../analysis/eslint-report.json

# Prettier (code formatting violations)
npx prettier --check "src/**/*.{js,jsx,css}" --write=false > ../analysis/prettier-violations.txt

# Dependency audit (security vulnerabilities)
npm audit --json > ../analysis/npm-audit.json

# Bundle size analysis
npm run build -- --mode production
npx vite-bundle-visualizer --analyze dist/stats.json > ../analysis/bundle-size.txt

# Dead code detection
npx unimported --init
npx unimported > ../analysis/dead-code.txt

# Cyclomatic complexity (React components)
npx es6-plato -r -d ../analysis/complexity-report src/
```

### 1.2 Manual Code Review Checklist

**Architecture Violations**:
- [ ] Are components doing too much? (>200 lines = suspect)
- [ ] Is state management consistent? (Redux vs. Context vs. local useState)
- [ ] Are side effects properly handled? (useEffect dependencies correct?)
- [ ] Is data fetching centralized? (API layer vs. scattered fetch calls)
- [ ] Are PropTypes/TypeScript used consistently?

**React Best Practices Violations**:
- [ ] Unnecessary re-renders (missing React.memo, useMemo, useCallback)?
- [ ] Keys in lists (using index as key)?
- [ ] Event handler naming (handleClick vs. onClick)?
- [ ] Conditional rendering (ternary hell vs. early returns)?
- [ ] Inline function definitions in JSX (performance issue)?

**Code Smells**:
- [ ] Magic numbers/strings (should be constants)
- [ ] Copy-pasted code (DRY violations)
- [ ] Commented-out code (delete it!)
- [ ] Console.log statements in production code
- [ ] Try-catch without proper error handling
- [ ] Empty catch blocks (error swallowing)

**Workarounds & Hacks**:
- [ ] setTimeout/setInterval for race condition fixes (symptom, not root cause)
- [ ] Multiple useEffect calls doing related things (should be one)
- [ ] Force re-renders (key={Date.now()}) - WHY?
- [ ] Prop drilling >3 levels (use Context/Redux)
- [ ] Duplicate API calls (caching missing?)

**File Structure Issues**:
- [ ] Files in wrong directories (`utils/` containing components?)
- [ ] Inconsistent naming (camelCase vs. PascalCase)
- [ ] Missing index.js for barrel exports
- [ ] Too many files in one directory (>20 = needs subdirectories)

### 1.3 Dependencies Audit

**Check for**:
- Unused dependencies (from `unimported` output)
- Outdated dependencies (run `npm outdated`)
- Duplicate dependencies (multiple versions of same lib)
- Unnecessary polyfills (if targeting modern browsers)
- Heavy libraries for simple tasks (lodash for one function?)

**Document**:
```markdown
| Dependency | Current Version | Latest | Used? | Action |
|------------|-----------------|--------|-------|--------|
| react-router-dom | 6.x | 6.y | ✅ | Keep |
| lodash | 4.17.21 | 4.17.21 | ❌ | REMOVE (only using _.debounce, replace with custom) |
```

### 1.4 Deliverable: Frontend Analysis Report

**Format** (max 3 pages):
```markdown
# Frontend Code Analysis Report

## Executive Summary
- Total Issues Found: [number]
- Critical: [number] (blocking production)
- High: [number] (should fix)
- Medium: [number] (nice to have)
- Low: [number] (cosmetic)

## Critical Issues (MUST FIX)
### Issue 1: [Title]
- **Location**: `src/components/DeviceList.jsx:45-67`
- **Problem**: Using setTimeout to fix race condition in device discovery
- **Root Cause**: Missing dependency in useEffect
- **Fix**: Add `devices` to dependency array, remove setTimeout
- **Files Affected**: 1
- **Estimated Effort**: 15 minutes

## High Priority Issues (SHOULD FIX)
[Same format as Critical]

## Code Cleanup Opportunities
- Remove dead code: [list files]
- Consolidate duplicates: [list patterns]
- Extract components: [list candidates]

## Dependencies
- Remove: [list]
- Update: [list]
- Security fixes: [list from npm audit]

## Metrics
- Lines of Code: [total]
- Cyclomatic Complexity: [average, max]
- Bundle Size: [KB]
- Test Coverage: [%]
```

---

## 🔍 PHASE 2: BACKEND CODE ANALYSIS (60 minutes)

### 2.1 Static Code Analysis

**Tools to run**:
```powershell
cd backend

# Ruff (fast Python linter)
ruff check src/ tests/ --output-format json > ../analysis/ruff-report.json

# Black (code formatting)
black --check --diff src/ tests/ > ../analysis/black-violations.txt

# MyPy (type checking)
mypy src/ --strict --no-error-summary --json-report ../analysis/mypy-report

# Bandit (security issues)
bandit -r src/ -f json -o ../analysis/bandit-security.json

# Radon (cyclomatic complexity)
radon cc src/ -a -s -j > ../analysis/radon-complexity.json

# Vulture (dead code detection)
vulture src/ > ../analysis/dead-code-backend.txt

# Safety (dependency vulnerabilities)
safety check --json > ../analysis/safety-report.json

# Import analysis (circular imports, unused imports)
pylint src/ --disable=all --enable=cyclic-import,unused-import --output-format=json > ../analysis/import-issues.json
```

### 2.2 Manual Code Review Checklist

**Clean Architecture Violations**:
- [ ] Are layers properly separated? (API → Use Cases → Domain → Adapters → Infrastructure)
- [ ] Dependencies flowing inward? (outer layers depend on inner, not vice versa)
- [ ] Domain models free of infrastructure concerns? (no SQLAlchemy in domain)
- [ ] Adapters wrapping external systems? (SoundTouch, RadioBrowser)
- [ ] Repository pattern used consistently for data access?

**FastAPI Best Practices Violations**:
- [ ] Dependency injection used properly? (Depends() for shared resources)
- [ ] Request validation with Pydantic models?
- [ ] Response models defined (not returning raw dicts)?
- [ ] HTTP status codes correct (201 for creation, 204 for deletion)?
- [ ] Error handling with HTTPException?
- [ ] Background tasks for long operations?
- [ ] API versioning strategy (/api/v1/)?

**Python Code Smells**:
- [ ] God classes (>300 lines, doing too much)
- [ ] Long functions (>50 lines)
- [ ] Too many parameters (>4 = use dataclass)
- [ ] Mutable default arguments (`def func(items=[])`)?
- [ ] Bare except clauses (`except:` without exception type)
- [ ] Global variables (except constants)
- [ ] String concatenation in loops (use f-strings or join)
- [ ] Import * (from module import *)

**Async/Await Issues**:
- [ ] Blocking I/O in async functions (requests instead of httpx)
- [ ] Missing await on async calls
- [ ] Unnecessary async (function doesn't do I/O)
- [ ] Mixing sync and async code incorrectly

**Workarounds & Hacks**:
- [ ] Sleep/delay to avoid race conditions (symptom fix)
- [ ] Try-except to hide errors (proper error handling?)
- [ ] Hardcoded timeouts (should be configurable)
- [ ] Duplicate code (extract to utils/shared modules)

**Configuration Issues**:
- [ ] Hardcoded values (should be in config/env vars)
- [ ] Secrets in code (use environment variables)
- [ ] Config scattered across files (centralize in config.py)
- [ ] No validation of config values (Pydantic Settings)

### 2.3 Dependencies Audit

**Check for**:
- Unused dependencies (from vulture output)
- Outdated dependencies (`pip list --outdated`)
- Conflicting versions in requirements.txt vs pyproject.toml
- Missing version pins (should pin all dependencies)
- Development dependencies in production requirements

**Document**:
```markdown
| Dependency | Current | Latest | Used? | Action |
|------------|---------|--------|-------|--------|
| httpx | 0.24.1 | 0.27.0 | ✅ | UPDATE |
| libsoundtouch | local | N/A | ✅ | Keep |
| pytest-mock | 3.11.1 | 3.12.0 | ❌ | REMOVE (not used, using unittest.mock) |
```

### 2.4 Deliverable: Backend Analysis Report

**Format** (max 3 pages, same structure as Frontend report)

---

## 🔍 PHASE 3: TEST SUITE ANALYSIS (60 minutes)

### 3.1 Frontend Tests (Vitest + Cypress)

**Static Analysis**:
```powershell
cd frontend

# Test coverage
npm run test:coverage -- --reporter=json > ../analysis/vitest-coverage.json

# Cypress test results
npx cypress run --reporter json > ../analysis/cypress-results.json

# Test file analysis (unused test files)
npx unimported --init --entry "tests/**/*.test.{js,jsx}"
```

**Manual Review Checklist**:
- [ ] Test coverage >80%? (check htmlcov/ or coverage report)
- [ ] Are tests testing implementation or behavior? (should be behavior)
- [ ] Flaky tests? (intermittent failures)
- [ ] Tests with hardcoded waits (cy.wait(5000) = bad)
- [ ] Tests without assertions (pointless tests)
- [ ] Over-mocking (mocking everything defeats the purpose)
- [ ] Under-mocking (calling real APIs in unit tests = integration test)
- [ ] Duplicate test cases (same thing tested multiple ways)
- [ ] Missing edge cases (null, empty, error scenarios)
- [ ] Test names unclear (should describe what's being tested)

**Test Quality Issues**:
- [ ] AAA pattern followed? (Arrange, Act, Assert)
- [ ] One assertion per test? (or logically grouped assertions)
- [ ] Tests independent? (can run in any order)
- [ ] Tests deterministic? (no random values, no Date.now())
- [ ] Proper cleanup (afterEach hooks for state reset)

### 3.2 Backend Tests (pytest)

**Static Analysis**:
```powershell
cd backend

# Test coverage with branch coverage
pytest --cov=src --cov-report=json --cov-report=html --cov-branch > ../analysis/pytest-coverage.txt

# Test duration analysis (slow tests)
pytest --durations=20 --durations-min=1.0 > ../analysis/slow-tests.txt

# Test collection (find uncollected test files)
pytest --collect-only -q > ../analysis/pytest-collection.txt
```

**Manual Review Checklist**:
- [ ] Test coverage >80%?
- [ ] Async tests properly marked (@pytest.mark.asyncio)?
- [ ] Fixtures reused (not duplicated across files)?
- [ ] Fixtures scope correct (function vs. module vs. session)?
- [ ] Mocking external services (SoundTouch API, RadioBrowser)?
- [ ] Database transactions rolled back (no test pollution)?
- [ ] Proper exception testing (pytest.raises)?
- [ ] Parametrize used for similar test cases?
- [ ] Test docstrings explain intent?

**Test Smells**:
- [ ] Tests longer than code being tested
- [ ] Tests with complex setup (extract to fixtures)
- [ ] Tests skipped without reason (@pytest.mark.skip without reason)
- [ ] Tests marked as xfail (expected to fail = technical debt)
- [ ] Slow tests (>1s for unit test = probably integration test)

### 3.3 Deliverable: Test Analysis Report

**Format** (max 2 pages):
```markdown
# Test Suite Analysis Report

## Coverage Summary
- Frontend Unit Tests: [%]
- Backend Unit Tests: [%]
- E2E Tests (Cypress): [scenarios covered]
- Total Coverage: [%]

## Test Quality Issues
### Critical
[Issues that make tests unreliable]

### High Priority
[Tests missing for critical paths]

## Test Cleanup Tasks
- Remove: [list obsolete tests]
- Refactor: [list tests needing rewrite]
- Add: [list missing test scenarios]

## Performance
- Slowest tests: [list with duration]
- Flaky tests: [list with failure rate]
```

---

## 📚 PHASE 4: DOCUMENTATION CLEANUP (45 minutes)

### 4.1 Documentation Inventory

**Scan all docs**:
```powershell
Get-ChildItem -Path docs,README.md,CONTRIBUTING.md,backend/README.md,frontend/README.md -Recurse -Include *.md | 
  Select-Object FullName, Length, LastWriteTime |
  Export-Csv -Path analysis/docs-inventory.csv
```

**Categorize each document**:

| Document | Category | Status | Action |
|----------|----------|--------|--------|
| README.md | Essential | Current | **CONSOLIDATE** (remove setup duplication) |
| docs/ITERATION_2.5.1_COMPLETE.md | Archive | Completed | **DELETE** (iteration done) |
| docs/MIGRATION_PROMPT.md | Archive | Obsolete | **DELETE** (migration done) |
| backend/bose_api/README.md | Reference | Current | **KEEP** (still needed) |
| docs/TESTING_REQUIREMENTS.md | Process | Current | **CONSOLIDATE** into CONTRIBUTING.md |
| docs/SoundTouchBridge_Projektplan.md | Planning | Obsolete | **DELETE** (historical, not actionable) |

**Categories**:
- **Essential**: README, CONTRIBUTING, API docs (KEEP, consolidate if needed)
- **Reference**: API schemas, architecture diagrams (KEEP if current, DELETE if obsolete)
- **Process**: Testing guides, development workflows (CONSOLIDATE into main docs)
- **Archive**: Iteration logs, migration notes, meeting notes (**DELETE ALL - NO ARCHIVE**)
- **Redundant**: Duplicate information (MERGE into canonical source)

### 4.2 Documentation Quality Criteria

**Each document MUST**:
- ✅ Be <10 minutes reading time (~2000 words max)
- ✅ Have clear purpose (stated in first paragraph)
- ✅ Be current (last update <3 months, or mark as outdated)
- ✅ Have unique information (no duplicates)
- ✅ Use concise language (no fluff, no repetition)
- ✅ Include code examples ONLY where essential (not for illustration)
- ✅ Have actionable content (if it doesn't guide a decision, delete it)

**PROHIBITED**:
- ❌ "Background" or "History" sections (nobody cares, delete)
- ❌ Long code examples (link to real code instead)
- ❌ Verbose explanations ("as we discussed earlier", "it's important to note")
- ❌ Redundant information (if it's in code comments, don't repeat in docs)
- ❌ Future plans (use GitHub Issues instead)
- ❌ Apologetic language ("this might not be perfect but...")

### 4.3 Documentation Cleanup Actions

**For each document, decide**:

1. **DELETE** (no questions asked):
   - Iteration logs (ITERATION_*.md)
   - Migration guides (MIGRATION_*.md)
   - Meeting notes
   - Old architecture docs (if superseded)
   - Draft documents
   - Test coverage reports (data is in htmlcov/)

2. **CONSOLIDATE** (merge into canonical source):
   - Multiple README files → One main README
   - Scattered testing docs → CONTRIBUTING.md
   - Deployment guides → DEPLOYMENT.md (one file)
   - Multiple API docs → backend/API.md

3. **REWRITE** (reduce to essentials):
   - Remove verbose intros
   - Keep only actionable content
   - Replace long examples with links to code
   - Use bullet points, not paragraphs
   - Add table of contents if >1000 words

4. **KEEP AS-IS** (rare):
   - backend/bose_api/README.md (concise reference)
   - LICENSE, NOTICE (legal requirement)

### 4.4 Documentation Structure (Target State)

```
/
├── README.md                    # Project overview, quick start (5 min read)
├── CONTRIBUTING.md              # Dev setup, testing, git workflow (8 min read)
├── DEPLOYMENT.md                # Production deployment (5 min read)
├── LICENSE                      # Keep as-is
├── NOTICE                       # Keep as-is
│
backend/
├── README.md                    # Backend-specific setup (3 min read)
├── API.md                       # API reference (8 min read)
└── bose_api/
    └── README.md                # Bose API docs (keep as-is)

frontend/
└── README.md                    # Frontend-specific setup (3 min read)

docs/
├── ARCHITECTURE.md              # System design (10 min read)
└── TROUBLESHOOTING.md           # Common issues (5 min read)

# EVERYTHING ELSE: DELETE!
```

### 4.5 Deliverable: Documentation Cleanup Plan

**Format**:
```markdown
# Documentation Cleanup Plan

## Files to DELETE (no archive)
- [ ] docs/ITERATION_2.5.1_COMPLETE.md
- [ ] docs/MIGRATION_PROMPT.md
- [ ] docs/MIGRATION_TO_CLEAN_TEST_ARCHITECTURE.md
- [ ] docs/SoundTouchBridge_Projektplan.md
- [ ] docs/archive/* (entire directory)
[... full list ...]

Total: [N] files, [MB] disk space

## Files to CONSOLIDATE

### README.md ← backend/README.md, frontend/README.md
**Action**: Merge backend/frontend setup into main README under "Development" section
**Before**: 3 files, 15 min total read time
**After**: 1 file, 5 min read time

### CONTRIBUTING.md ← docs/TESTING_REQUIREMENTS.md, docs/PRE-COMMIT-HOOK.md
**Action**: Merge testing and git workflow into CONTRIBUTING
**Before**: 3 files, 20 min total read time
**After**: 1 file, 8 min read time

[... more consolidations ...]

## Files to REWRITE (>10 min read time)
- [ ] docs/ARCHITECTURE.md (currently 25 min) → target 10 min
  - Remove: History, Background (3 pages)
  - Condense: Code examples → links to actual code
  - Keep: Architecture diagram, layer descriptions, design decisions

[... more rewrites ...]

## Final Documentation Size
- Before: [N] files, [total words], [estimated read time]
- After: [M] files (<10), [total words], [<60 min total]
- Reduction: [%]
```

---

## 🛠️ PHASE 5: CLEANUP EXECUTION (120 minutes)

### 5.1 Frontend Cleanup Tasks

**Priority Order**:
1. **Critical issues** (blocking production)
2. **Security issues** (npm audit findings)
3. **Architecture violations** (wrong dependencies, state management mess)
4. **Code smells** (magic numbers, duplication)
5. **Dependencies** (remove unused, update outdated)
6. **Dead code** (remove unused files/functions)
7. **Formatting** (run Prettier)

**For each issue**:
```markdown
### Issue: [Title from analysis report]
- **Fix**: [Exact code change]
- **Test**: [How to verify fix works]
- **Commit**: `refactor(frontend): [description]`
```

**Execute**:
```powershell
# Fix linting issues
npm run lint -- --fix

# Format code
npx prettier --write "src/**/*.{js,jsx,css}"

# Remove unused dependencies
npm uninstall [list from analysis]

# Update dependencies (safe updates only)
npm update --save

# Re-run tests
npm run test
npm run test:e2e

# Verify no regressions
npm run build
```

### 5.2 Backend Cleanup Tasks

**Priority Order**:
1. **Security issues** (Bandit, Safety findings)
2. **Critical bugs** (type errors, logic errors)
3. **Architecture violations** (layer mixing, wrong dependencies)
4. **Code smells** (god classes, long functions)
5. **Dependencies** (remove unused, update safe)
6. **Dead code** (remove unused modules)
7. **Formatting** (run Black, isort)

**Execute**:
```powershell
# Fix auto-fixable issues
ruff check src/ tests/ --fix

# Format code
black src/ tests/
isort src/ tests/

# Remove unused dependencies
# (manual: edit pyproject.toml, then:)
pip install -e ".[dev]"

# Re-run tests
pytest --cov=src --cov-fail-under=80

# Type check
mypy src/ --strict

# Security scan
bandit -r src/ -ll
```

### 5.3 Test Cleanup Tasks

**Frontend**:
```powershell
# Remove obsolete test files
Remove-Item [list from analysis]

# Update test dependencies
npm update --save-dev [test libraries]

# Re-run with coverage
npm run test:coverage

# Verify >80% coverage
```

**Backend**:
```powershell
# Remove obsolete test files
Remove-Item [list from analysis]

# Refactor slow tests (mock external calls)
# Refactor flaky tests (remove hardcoded waits)

# Re-run with strict coverage
pytest --cov=src --cov-fail-under=80 --cov-branch

# Check for test leaks
pytest -x --lf
```

### 5.4 Documentation Cleanup Tasks

**Execute**:
```powershell
# DELETE files (NO ARCHIVE!)
Remove-Item docs/ITERATION_*.md
Remove-Item docs/MIGRATION_*.md
Remove-Item -Recurse docs/archive/

# CONSOLIDATE files
# (manual editing per plan)

# REWRITE files
# (manual editing per plan)

# Verify all links work
# (use markdown-link-check or similar)

# Final review: each doc <10 min read
```

---

## ✅ PHASE 6: QUALITY GATES & VALIDATION (30 minutes)

### 6.1 Code Quality Gates

**All must pass**:
```powershell
# Frontend
cd frontend
npm run lint          # 0 errors
npm run test          # 100% pass, >80% coverage
npm run build         # successful build

# Backend
cd backend
ruff check src/ tests/               # 0 errors
black --check src/ tests/            # no formatting issues
mypy src/ --strict                   # 0 type errors
pytest --cov=src --cov-fail-under=80 # >80% coverage
bandit -r src/ -ll                   # 0 high/medium security issues
```

### 6.2 Documentation Quality Gates

**All must pass**:
- [ ] Total docs <10 files
- [ ] Each doc <10 min read time
- [ ] No iteration/migration logs remaining
- [ ] No duplicate information
- [ ] All code examples link to real code (or removed)
- [ ] All links work (no 404s)
- [ ] TOC present for docs >1000 words

### 6.3 Functional Validation

**E2E tests must pass**:
```powershell
# Cypress
cd frontend
npm run test:e2e

# Backend E2E
cd backend
pytest tests/e2e/
```

### 6.4 Git Cleanliness

**Verify**:
```powershell
# No uncommitted changes (except deliberate)
git status

# No ignored files that should be tracked
git ls-files --others --exclude-standard

# No large files accidentally committed
git ls-files | ForEach-Object { Get-Item $_ } | Where-Object { $_.Length -gt 1MB }
```

---

## 📊 PHASE 7: FINAL REPORT (30 minutes)

### 7.1 Cleanup Summary

**Format**:
```markdown
# CloudTouch Codebase Cleanup - Final Report

**Date**: [YYYY-MM-DD]
**Duration**: [total hours]
**Status**: ✅ COMPLETE

## Metrics

### Code
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Frontend LoC | [N] | [M] | -[X]% |
| Backend LoC | [N] | [M] | -[X]% |
| Cyclomatic Complexity (avg) | [N] | [M] | -[X]% |
| Test Coverage | [N]% | [M]% | +[X]% |
| ESLint Errors | [N] | 0 | -100% |
| MyPy Errors | [N] | 0 | -100% |
| Security Issues | [N] | 0 | -100% |

### Dependencies
| | Before | After | Removed |
|-|--------|-------|---------|
| Frontend | [N] | [M] | [X] |
| Backend | [N] | [M] | [X] |

### Documentation
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total Files | [N] | [M] | -[X]% |
| Total Words | [N] | [M] | -[X]% |
| Read Time | [N] min | [M] min | -[X]% |

## Changes Summary

### Frontend
- Fixed [N] critical issues
- Removed [N] unused dependencies
- Deleted [N] dead code files
- Refactored [N] complex components

### Backend
- Fixed [N] architecture violations
- Removed [N] workarounds
- Consolidated [N] duplicate functions
- Updated [N] dependencies

### Tests
- Removed [N] obsolete tests
- Fixed [N] flaky tests
- Added [N] missing test scenarios
- Coverage: [X]% → [Y]%

### Documentation
- Deleted [N] files ([MB] saved)
- Consolidated [N] files
- Rewrote [N] files (reduced by [X]%)

## Technical Debt Eliminated

### Critical (Blockers)
1. [Description] - Fixed in [commit hash]
2. [...]

### High Priority
1. [Description] - Fixed in [commit hash]
2. [...]

## Remaining Known Issues

### Technical Debt (Accepted)
1. [Description] - Reason for keeping: [justification]

### Future Improvements (Backlog)
1. [Description] - Estimated effort: [hours]

## Commits
- Total commits: [N]
- Commit message format: Conventional Commits (feat, fix, refactor, docs, test)
- Branch: `cleanup/[YYYY-MM-DD]`

## Quality Gates Status
- [x] All linters pass
- [x] All tests pass (>80% coverage)
- [x] No security vulnerabilities
- [x] Documentation <10 files, each <10 min read
- [x] E2E tests pass
- [x] Build successful
```

### 7.2 Git Commit Strategy

**Branch**:
```powershell
git checkout -b cleanup/2026-02-03
```

**Commits (atomic, in order)**:
```powershell
# Frontend
git commit -m "refactor(frontend): remove unused dependencies"
git commit -m "fix(frontend): eliminate setTimeout race condition workaround in DeviceList"
git commit -m "refactor(frontend): extract duplicate API calls to centralized service"
git commit -m "style(frontend): apply Prettier formatting"
git commit -m "test(frontend): remove obsolete test files"

# Backend
git commit -m "refactor(backend): fix layer mixing in device repository"
git commit -m "fix(backend): replace hardcoded timeouts with config values"
git commit -m "refactor(backend): consolidate duplicate error handling"
git commit -m "style(backend): apply Black and isort formatting"
git commit -m "test(backend): fix flaky SSDP discovery tests"

# Documentation
git commit -m "docs: delete completed iteration logs and migration guides"
git commit -m "docs: consolidate README files into main README"
git commit -m "docs: rewrite ARCHITECTURE.md to <10 min read time"

# Final
git commit -m "chore: update dependencies to latest secure versions"
git commit -m "ci: add static analysis to pre-commit hook"
```

**Push & Review**:
```powershell
git push origin cleanup/2026-02-03

# USER REVIEWS CHANGES
# USER RUNS MANUAL TESTS
# USER APPROVES

# Then on USER instruction:
git checkout main
git merge --no-ff cleanup/2026-02-03
git push origin main
```

---

## 🚨 EXCEPTION HANDLING

### What if Analysis Reveals MAJOR Architectural Problems?

**Scenario**: Layer violations everywhere, state management chaos, test coverage <50%

**Action**:
1. **STOP cleanup execution**
2. **Document findings** in `CRITICAL_ISSUES.md`
3. **Propose refactoring plan** with estimated effort
4. **Get user approval** before proceeding
5. **Execute in phases** (not one big cleanup)

**Example**:
```markdown
# CRITICAL: Frontend State Management Chaos

## Problem
- Redux used in 3 components
- Context used in 5 components
- Local useState in 15 components
- Prop drilling 5 levels deep in 2 places

## Impact
- Hard to maintain
- Unclear data flow
- Duplicate state
- Race conditions

## Proposed Solution
**Option 1**: Standardize on Redux (2 days effort)
**Option 2**: Standardize on Context (1 day effort)
**Option 3**: Hybrid (Redux for global, Context for features) (1.5 days)

## Recommendation
Option 2 (Context) - simplest, fits project size

## Next Steps
1. USER APPROVAL REQUIRED
2. Create separate refactoring branch
3. Migrate incrementally (one feature at a time)
4. Update tests after each migration
5. Merge when all tests pass
```

### What if Tests Start Failing During Cleanup?

**Root Cause Analysis**:
1. Did cleanup introduce a bug? → **REVERT**, fix properly
2. Was test relying on implementation detail? → **FIX TEST** (test behavior, not implementation)
3. Was test flaky to begin with? → **FIX TEST** (remove race conditions)

**Never**:
- ❌ Skip failing tests
- ❌ Mark as xfail
- ❌ Lower coverage threshold

**Always**:
- ✅ Understand why test failed
- ✅ Fix root cause
- ✅ Add regression test if needed

### What if Dependencies Can't Be Updated?

**Scenario**: Dependency X has breaking changes, major refactor needed

**Action**:
1. **Document** in `DEPENDENCIES.md`:
   ```markdown
   ## Pinned Dependencies
   
   ### httpx==0.24.1 (pinned, not latest 0.27.0)
   **Reason**: Version 0.25+ changed async API, requires refactoring all API calls
   **Impact**: Missing performance improvements, security patches
   **Plan**: Upgrade in Q2 2026 (dedicated refactoring sprint)
   **Tracking**: Issue #123
   ```

2. **Add to backlog**, don't block cleanup

### What if User Wants to Keep "Archive" Docs?

**Push back gently**:
```
"Archive documents create maintenance burden and confusion. 
Historical context belongs in git history, not docs.

If specific information is valuable:
1. Extract essential facts
2. Add to relevant current doc
3. Delete archive

What specific information from [doc] do you need to preserve?"
```

**If user insists**:
- Create `docs/archive/` folder
- Add `README.md` with warning: "Historical docs, may be outdated"
- Never link to archive from main docs

---

## 🎯 SUCCESS CRITERIA

**Cleanup is COMPLETE when**:

### Code
- [x] All static analysis tools report 0 errors
- [x] Test coverage ≥80% (both frontend and backend)
- [x] No workarounds or TODO comments (or tracked in issues)
- [x] Dependencies up-to-date (or explicitly pinned with reason)
- [x] No dead code (verified with unimported/vulture)
- [x] Consistent code style (Prettier/Black applied)

### Tests
- [x] All tests pass
- [x] No flaky tests (5 consecutive runs, all pass)
- [x] No slow unit tests (>1s = integration test, move to separate suite)
- [x] E2E tests cover critical user paths

### Documentation
- [x] ≤10 documentation files total
- [x] Each doc ≤10 min read time (~2000 words)
- [x] No iteration/migration/archive docs
- [x] No duplicate information
- [x] All links work

### Functional
- [x] Application runs locally (npm run dev, uvicorn)
- [x] E2E tests pass
- [x] No errors in browser console
- [x] No errors in backend logs

### Git
- [x] All changes committed (atomic commits)
- [x] Conventional commit messages
- [x] Branch ready for merge
- [x] No merge conflicts with main

---

## 📝 FINAL CHECKLIST FOR AGENT

**Before starting**:
- [ ] Read AGENTS.md (project-specific rules)
- [ ] Read this prompt completely
- [ ] Understand TDD requirements (tests must pass always)
- [ ] Understand USER AUTHORITY (no experiments without approval)

**Phase 0 (Context)**:
- [ ] Analyze Cypress tests
- [ ] Create temporary context doc
- [ ] Get user approval on context understanding

**Phase 1-3 (Analysis)**:
- [ ] Run all static analysis tools
- [ ] Manual code review with checklists
- [ ] Document ALL findings (not just selected ones)
- [ ] Categorize by priority (Critical, High, Medium, Low)
- [ ] Estimate effort for each fix

**Phase 4 (Documentation)**:
- [ ] Inventory all docs with metadata
- [ ] Categorize each (Essential, Reference, Process, Archive, Redundant)
- [ ] Create DELETE list (user approval required!)
- [ ] Create CONSOLIDATE plan
- [ ] Create REWRITE list with word count targets

**Phase 5 (Execution)**:
- [ ] Fix in priority order (Critical → Low)
- [ ] ONE COMMIT PER LOGICAL CHANGE
- [ ] Run tests after EVERY change
- [ ] Never bypass pre-commit hooks
- [ ] Never commit broken code
- [ ] Document any exceptions/trade-offs

**Phase 6 (Validation)**:
- [ ] All quality gates pass
- [ ] Manual smoke test (app works)
- [ ] No regressions in E2E tests

**Phase 7 (Report)**:
- [ ] Create final report with metrics
- [ ] List all commits
- [ ] Document remaining known issues
- [ ] Get user approval for merge

**After merge**:
- [ ] Delete cleanup branch (after successful merge)
- [ ] Close related issues
- [ ] Update project status

---

## 🔗 RELATED DOCUMENTS

- `AGENTS.md` - General agent rules (TDD, Clean Code, etc.)
- `CONTRIBUTING.md` - Development workflow
- `backend/bose_api/README.md` - Bose API reference

---

**REMEMBER**: 
- Code quality > speed
- Tests must pass always
- User approval required for structural changes
- Document trade-offs and exceptions
- No experiments without permission

**START WITH PHASE 0 - CONTEXT ACQUISITION**
