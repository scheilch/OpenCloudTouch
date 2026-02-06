# Script Migration Guide

**Status:** Tools modernization completed ✅

## What Changed?

We migrated from PowerShell scripts to professional npm-based workflow.

---

## DEPRECATED Scripts (REPLACED by npm)

These PowerShell scripts are **NO longer needed** - use npm commands instead:

### ❌ DELETE THESE:

```
tools/local-scripts/run-all-tests.ps1          → npm test
tools/local-scripts/run-backend-tests.ps1       → npm run test:backend
tools/local-scripts/run-frontend-tests.ps1      → npm run test:frontend
tools/local-scripts/run-e2e-tests.ps1           → npm run test:e2e
```

**Why?**
- Cross-platform (Windows, macOS, Linux)
- Industry standard
- Better error handling
- No encoding issues
- Integrated with CI/CD

---

## Local Deployment Scripts (NOT COMMITTED)

Your **personal** deployment scripts belong in `deployment/local/` (gitignored):

### 📦 Move These to `deployment/local/`:

```bash
tools/local-scripts/clear-database.ps1
tools/local-scripts/deploy-local.ps1
tools/local-scripts/deploy-to-truenas.ps1
tools/local-scripts/export-image.ps1
tools/local-scripts/run-e2e-tests-on-truenas.ps1
```

**Why not commit?**
- Personal environment (your TrueNAS, your IPs, your paths)
- Other developers have different setups
- Security (credentials, hostnames)

**Alternative:**
Create `deployment/local/README.md` with **examples** for other devs:
```md
# Example: Deploy to TrueNAS
ssh user@nas "podman load < opencloudtouch.tar"
ssh user@nas "podman run -d -p 7777:7777 opencloudtouch:latest"
```

---

## Keep for Project (USEFUL for all devs)

These scripts provide value for the whole team:

### ✅ Convert to npm scripts:

**pre-commit.ps1** → Add to package.json:
```json
"scripts": {
  "pre-commit": "npm run test:backend && npm run test:frontend",
  "prepare": "husky install"  // Git hooks automation
}
```

**fetch-api-schemas-complete.ps1** → Backend utility:
- Move to `apps/backend/scripts/fetch-schemas.py`
- Add npm script: `npm run backend:fetch-schemas`

**run-real-tests.ps1** → Optional hardware tests:
- Rename to `run-hardware-tests.ps1`
- Document in README: "Run with real Bose devices"

---

## Migration Checklist

### Phase 1: Test new npm workflow ✅
- [x] `npm test` works
- [x] `npm run test:backend` works
- [x] `npm run test:frontend` works
- [x] `npm run test:e2e` works (Node.js runner)

### Phase 2: Move personal scripts
- [ ] Create `deployment/local/README.md` with examples
- [ ] Move deployment scripts to `deployment/local/`
- [ ] Update `.gitignore` (already done ✅)

### Phase 3: Clean up obsolete scripts
- [ ] Delete `run-all-tests.ps1`
- [ ] Delete `run-backend-tests.ps1`
- [ ] Delete `run-frontend-tests.ps1`
- [ ] Delete `run-e2e-tests.ps1`

### Phase 4: Convert remaining utilities
- [ ] Convert `pre-commit.ps1` to npm script + Husky
- [ ] Move `fetch-api-schemas-complete.ps1` to backend/scripts/
- [ ] Document `run-real-tests.ps1` for hardware testing

---

## New Workflow (After Migration)

### Development
```bash
npm run dev              # Start backend + frontend
npm test                 # Run all tests
```

### Testing
```bash
npm run test:backend     # Backend pytest
npm run test:frontend    # Frontend vitest
npm run test:e2e         # E2E Cypress
```

### Building & Deployment
```bash
npm run build            # Build frontend
npm run docker:build     # Build Docker image
npm run docker:run       # Run container

# Personal deployment (your scripts in deployment/local/)
pwsh deployment/local/deploy-to-truenas.ps1
```

### CI/CD
```yaml
- name: Run tests
  run: npm test
```

---

## Benefits

**Before (PowerShell):**
- ❌ Windows-only
- ❌ Encoding issues (UTF-8, emojis)
- ❌ Exit code bugs (Cypress -1)
- ❌ Complex orchestration
- ❌ Hard to debug

**After (npm):**
- ✅ Cross-platform
- ✅ Industry standard
- ✅ Clean exit codes
- ✅ Proper async/await
- ✅ Better error messages
- ✅ Integrated with IDE/CI

---

## Questions?

See [docs/TESTING.md](../docs/TESTING.md) for full documentation.
