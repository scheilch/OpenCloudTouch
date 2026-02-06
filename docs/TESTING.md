# OpenCloudTouch Testing Infrastructure

Professional npm-based test orchestration for the OpenCloudTouch monorepo.

## Quick Start

```bash
# Install dependencies (root + all workspaces)
npm install

# Run all tests
npm test

# Run specific test suites
npm run test:backend     # Python pytest
npm run test:frontend    # Vitest unit tests
npm run test:e2e         # Cypress E2E tests
```

## Test Commands

### All Tests

```bash
# Sequential execution (recommended for CI)
npm test
# or
npm run test:all

# Parallel execution (faster, for local dev)
npm run test:all:parallel
```

### Backend Tests (Python)

```bash
npm run test:backend

# Direct pytest (from apps/backend)
cd apps/backend
pytest -v --cov=src
```

### Frontend Unit Tests (Vitest)

```bash
npm run test:frontend

# Watch mode
npm run test:frontend -- --watch

# Coverage
npm run test:frontend -- --coverage
```

### E2E Tests (Cypress)

```bash
# Automated run (headless)
npm run test:e2e

# Interactive mode
cd apps/frontend
npm run test:e2e:open

# Headed mode (see browser but automated)
cd apps/frontend
npm run test:e2e:headed
```

## Development

```bash
# Start both backend and frontend
npm run dev

# Build frontend
npm run build

# Preview production build
npm run preview
```

## Clean Up

```bash
# Clean all build artifacts and dependencies
npm run clean

# Clean frontend only
npm run clean:frontend
```

## Docker

```bash
# Build Docker image
npm run docker:build

# Run Docker container
npm run docker:run
```

## Architecture

### Monorepo Structure

```
opencloudtouch/
├── package.json              # Root workspace orchestration
├── scripts/
│   └── e2e-runner.mjs       # Node.js E2E test runner
├── apps/
│   ├── backend/             # Python FastAPI backend
│   │   ├── pyproject.toml
│   │   ├── pytest.ini
│   │   └── src/opencloudtouch/
│   └── frontend/            # React frontend
│       ├── package.json     # Workspace package
│       ├── vite.config.js
│       ├── vitest.config.js
│       └── cypress.config.js
└── tools/
    └── local-scripts/       # Legacy PowerShell scripts (deprecated)
```

### E2E Test Flow

The `scripts/e2e-runner.mjs` script orchestrates E2E tests:

1. **Cleanup** - Kill processes on ports 7778 (backend) and 4173 (frontend)
2. **Start Backend** - Launch FastAPI on port 7778 with mock mode
3. **Build Frontend** - Production build via Vite
4. **Start Preview** - Vite preview server on port 4173
5. **Run Cypress** - Execute E2E tests
6. **Cleanup** - Stop all processes and free ports

**Why Node.js instead of PowerShell?**
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Better error handling and async control
- ✅ Integrates seamlessly with npm scripts
- ✅ No shell-specific issues (encoding, pipes, exit codes)
- ✅ Professional industry standard

## Migration from PowerShell

### Old Way ❌

```powershell
.\tools\local-scripts\run-all-tests.ps1
.\tools\local-scripts\run-e2e-tests.ps1 -MockMode $true
```

**Problems:**
- Platform-specific (Windows only)
- Encoding issues (UTF-8, emojis)
- Exit code bugs (Cypress -1)
- Complex script orchestration
- Hard to debug hanging processes

### New Way ✅

```bash
npm test                     # All tests
npm run test:e2e            # E2E only
```

**Benefits:**
- Cross-platform
- Industry standard
- Clean exit codes
- Proper async/await
- Better error messages
- Integrated with IDE

## CI/CD Integration

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          npm install
          cd apps/backend && pip install -r requirements.txt
      
      - name: Run tests
        run: npm test
```

### GitLab CI

```yaml
test:
  image: node:20
  before_script:
    - npm install
    - cd apps/backend && pip install -r requirements.txt
  script:
    - npm test
```

## Troubleshooting

### E2E Tests Hang

**Symptom:** Tests never start or hang at "Running Cypress..."

**Solution:**
```bash
# Kill stuck processes
npx kill-port 7778 4173

# Or manually
# Windows
netstat -ano | findstr :7778
taskkill /F /PID <PID>

# Linux/macOS
lsof -ti:7778 | xargs kill -9
```

### Frontend Build Fails

**Symptom:** Vite build errors

**Solution:**
```bash
cd apps/frontend
rm -rf node_modules dist
npm install
npm run build
```

### Backend Tests Fail

**Symptom:** Import errors or module not found

**Solution:**
```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
pytest -v
```

## Best Practices

### Local Development

1. **Always use npm scripts** (not direct CLI commands)
2. **Run tests before commit** (`npm test`)
3. **Use watch mode during development** (`npm run test:frontend -- --watch`)
4. **Open E2E UI for debugging** (`cd apps/frontend && npm run test:e2e:open`)

### CI/CD

1. **Use `npm test`** for sequential execution
2. **Cache dependencies** (`node_modules`, `.venv`)
3. **Fail fast** - stop on first failure
4. **Upload coverage** reports
5. **Archive test artifacts** (screenshots, videos)

## Performance

### Execution Times (Typical)

- Backend Tests: ~8-15s (291 tests, 92% coverage)
- Frontend Tests: ~3-8s (197 tests)
- E2E Tests: ~30-45s (15 tests, 2 specs)
- **Total: ~45-70s**

### Optimization Tips

1. **Parallel execution** for local dev: `npm run test:all:parallel`
2. **Skip E2E in pre-commit** (too slow): only run backend + frontend unit
3. **Use Vite watch mode** during frontend development
4. **Run E2E headed mode** for debugging (see what's happening)

## Future Enhancements

- [ ] Test result caching (Nx, Turborepo)
- [ ] Visual regression testing (Percy, Chromatic)
- [ ] Performance budgets (Lighthouse CI)
- [ ] Contract testing (Pact)
- [ ] Mutation testing (Stryker)
- [ ] Test parallelization (Cypress Cloud)

---

**Questions?** Check the [main README](../README.md) or open an issue.
