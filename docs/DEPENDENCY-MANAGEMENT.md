# Dependency Management - npm Workspaces

## Overview

CloudTouch uses **npm workspaces** for monorepo dependency management.

```
cloudtouch/
├── package.json              # Root workspace (shared deps)
└── apps/
    └── frontend/
        └── package.json      # Frontend workspace (app-specific deps)
```

---

## How It Works

### Installation
```bash
npm install  # Run from root - installs everything
```

This does:
1. Install root dependencies (`concurrently`, `rimraf`)
2. Install all workspace dependencies (`apps/frontend/package.json`)
3. **Hoist shared dependencies** to root `node_modules/`
4. Create symlinks for workspace-specific versions

### Hoisting Rules

**If same version:**
```
root/node_modules/
  react@19.2.4              ← Hoisted (shared)
  react-dom@19.2.4          ← Hoisted (shared)
```

**If different versions:**
```
root/node_modules/
  vite@7.3.1                ← Root version
apps/frontend/node_modules/
  vite@7.3.2                ← Frontend-specific (overrides)
```

**Best practice:** Keep versions aligned to save disk space.

---

## Current Dependencies

### Root (`package.json`)

**devDependencies** (development tools, shared across workspace):
```json
{
  "concurrently": "^9.1.2",    // Run commands in parallel
  "rimraf": "^6.0.1"           // Cross-platform rm -rf
}
```

**Why here?**
- Used by root npm scripts (`npm run dev`, `npm run clean`)
- Shared across all workspaces
- No version conflicts

### Frontend (`apps/frontend/package.json`)

**dependencies** (runtime):
```json
{
  "framer-motion": "^12.31.0",
  "react": "^19.2.4",
  "react-dom": "^19.2.4",
  "react-router-dom": "^7.13.0"
}
```

**devDependencies** (build/test tools):
```json
{
  "@vitejs/plugin-react": "^5.1.3",
  "cypress": "^15.10.0",
  "eslint": "^9.39.2",
  "rimraf": "^6.0.1",          // Also in root - no conflict
  "typescript": "^5.9.3",
  "vite": "^7.3.1",
  "vitest": "^4.0.18"
}
```

**Why here?**
- Frontend-specific (React, Vite, Cypress)
- Not needed in backend
- Isolated from other workspaces

---

## Version Conflicts?

### Same Package, Different Versions

**Example:**
```json
// Root package.json
"rimraf": "^6.0.1"

// apps/frontend/package.json
"rimraf": "^6.0.1"
```

**Result:** npm hoists to root, frontend uses symlink → **No duplicate install** ✅

**If versions differ:**
```json
// Root
"rimraf": "^6.0.1"

// Frontend
"rimraf": "^5.0.0"
```

**Result:** npm keeps both versions → **2 copies on disk** (but isolated) ⚠️

### Resolution

**Option 1:** Align versions (recommended)
```bash
npm install rimraf@latest           # Update root
npm install rimraf@latest -w apps/frontend  # Update workspace
```

**Option 2:** Use `overrides` in root (force version)
```json
// Root package.json
{
  "overrides": {
    "rimraf": "^6.0.1"    // Force this version everywhere
  }
}
```

---

## Adding Dependencies

### To Root (shared tools)

```bash
npm install -D prettier          # Add to root devDependencies
npm install lodash               # Add to root dependencies
```

**Use for:**
- Linting/formatting tools (ESLint, Prettier)
- Build orchestration (concurrently, cross-env)
- Shared utilities used in multiple workspaces

### To Frontend Workspace

```bash
npm install axios -w apps/frontend           # Runtime dependency
npm install -D @types/node -w apps/frontend  # Dev dependency
```

**Use for:**
- App-specific libraries (React, Vite, Cypress)
- Frontend-only tools
- Anything not needed in backend

### To Backend (Python)

```bash
cd apps/backend
pip install fastapi
pip freeze > requirements.txt
```

Backend is **Python-only** - no npm/JavaScript dependencies.

---

## Checking for Duplicates

```bash
# List all dependencies (hierarchical)
npm ls

# Check specific package
npm ls react

# Find duplicates
npm dedupe
```

---

## Updating Dependencies

### Update All (safe)
```bash
npm update             # Updates within semver range (^, ~)
```

### Update to Latest
```bash
npm install react@latest -w apps/frontend
npm install concurrently@latest
```

### Interactive Update (recommended)
```bash
npm install -g npm-check-updates
ncu -i                 # Interactive: choose what to update
ncu -u && npm install  # Auto-update package.json
```

---

## Troubleshooting

### "Module not found"

**Symptom:** `Cannot find module 'react'` even though installed

**Solution:**
```bash
# Delete all node_modules and reinstall
npm run clean
npm install
```

### "Peer dependency warnings"

**Symptom:** `WARN react@19.2.4 requires a peer of react-dom@^19.0.0`

**Solution:** Usually harmless, but can fix with:
```bash
npm install react-dom@^19.0.0 -w apps/frontend
```

### "Version mismatch"

**Symptom:** Frontend expects `vite@7.3.1` but root has `vite@7.0.0`

**Solution:** Align versions or use `overrides`:
```json
{
  "overrides": {
    "vite": "7.3.1"
  }
}
```

---

## Best Practices

1. **Keep versions aligned** - avoid duplicates
2. **Use workspaces** (`-w apps/frontend`) for workspace deps
3. **Commit lock files** - `package-lock.json` ensures reproducibility
4. **Run `npm install` from root** - always from monorepo root
5. **Use `^` for libraries** - allows minor/patch updates
6. **Use exact versions for tools** - `eslint@9.39.2` (no `^`)

---

## CI/CD

```yaml
- name: Install dependencies
  run: npm ci              # Use 'ci' for reproducible builds
  
- name: Test
  run: npm test            # Runs tests in all workspaces
```

**Why `npm ci` instead of `npm install`?**
- Faster (skips package.json resolution)
- Reproducible (uses exact versions from lock file)
- Fails if lock file is out of sync

---

## Resources

- [npm Workspaces Docs](https://docs.npmjs.com/cli/v10/using-npm/workspaces)
- [npm Dependency Resolution](https://docs.npmjs.com/cli/v10/configuring-npm/package-json#dependencies)
- [Semver Explained](https://semver.org/)

---

**Questions?** Check `package.json` comments or ask in team chat!
