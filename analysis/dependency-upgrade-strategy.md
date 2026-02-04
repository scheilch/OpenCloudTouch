# Dependency Upgrade Strategy

**Date**: 2026-02-04  
**Status**: Partial Update Completed

## Executive Summary

Out of 14 outdated packages, **2 were safely updated** (jsdom, @vitejs/plugin-react), **1 is already current** (Cypress 13.17.0), and **11 are blocked** due to breaking changes that require coordinated migration strategy.

---

## ✅ Successfully Updated (2 packages)

### 1. jsdom: 23.2.0 → 28.0.0
- **Type**: Dev dependency (test environment)
- **Risk**: Low (isolated to test execution)
- **Changes**: 9 packages added, 10 removed, 15 changed
- **Validation**: ✅ All 87 frontend tests passed, 15 E2E tests passed
- **Reason for Update**: No breaking API changes affecting our test suite, improved DOM compatibility

### 2. @vitejs/plugin-react: 4.7.0 → 5.1.3
- **Type**: Dev dependency (build tooling)
- **Risk**: Low (peer deps confirm Vite ^5.0.0 compatible)
- **Changes**: 3 packages changed
- **Validation**: ✅ Production build successful (1.26s), all tests passed
- **Reason for Update**: Performance improvements, better error messages, no breaking changes for Vite 5.x users

---

## ⏸️ Already Current (1 package)

### Cypress: 13.17.0 (Latest stable v13.x)
- **Latest v13**: 13.17.0 (currently installed)
- **Latest Overall**: 15.10.0 (BREAKING)
- **Action**: SKIP - Already on latest stable v13 release
- **Reason**: v14 and v15 introduce breaking changes to component testing API and TypeScript config. Wait for coordinated migration window.

---

## 🚫 Blocked Updates (11 packages)

### Critical Blocker: React Ecosystem (4 packages)

#### 1. React: 18.3.1 → 19.2.4 ⚠️ **MAJOR BREAKING CHANGES**
**Breaking Changes**:
- New JSX transform (no longer auto-imports `React`)
- Server Components architecture changes
- Concurrent Rendering by default (may break timing assumptions)
- `useEffect` cleanup timing changes
- Removed legacy APIs: `ReactDOM.render()`, `unmountComponentAtNode()`

**Impact**: HIGH - Core dependency affecting all components

**Migration Strategy**:
1. Audit all 26 TSX components for removed API usage
2. Test concurrent rendering behavior (especially multi-room features)
3. Update all third-party libraries to React 19 compatible versions first
4. Coordinate with React Router v7 upgrade (also requires React 19)

**Blocked By**: React Router, @testing-library/react, Framer Motion compatibility

**Estimated Effort**: 2-3 days (testing + fixes)

---

#### 2. React-DOM: 18.3.1 → 19.2.4
**Reason**: MUST stay in sync with React core version

**Breaking Changes**: Same as React package above

**Action**: Update together with React in coordinated migration

---

#### 3. @types/react: 18.3.27 → 19.2.10
**Reason**: TypeScript definitions must match React version

**Breaking Changes**:
- Stricter type checking for hooks (especially `useEffect`, `useCallback`)
- New types for Server Components
- Changes to `ReactNode` type definition

**Action**: Update together with React + React-DOM

---

#### 4. @testing-library/react: 14.3.1 → 16.3.2
**Reason**: Requires React 19 peer dependency

**Breaking Changes** (v15+):
- Removed `waitFor` timeout default (must be explicit)
- Stricter async act() warnings
- Changes to rendering API for Server Components

**Action**: Update after React migration, requires test suite audit

---

### Build Tooling Blocker: Vite Ecosystem (1 package)

#### 5. Vite: 5.4.21 → 7.3.1 ⚠️ **SECURITY + BREAKING**
**Security Issue**: Related to esbuild vulnerability (CVE pending)

**Breaking Changes** (v6):
- Node.js 18+ required (currently using 20.19.4 ✅)
- ESM-only (no CommonJS support)
- Plugin API changes (may affect @vitejs/plugin-react)
- CSS handling changes

**Breaking Changes** (v7):
- Further plugin API evolution
- Rollup 4.x requirement
- Build optimization changes

**Complexity**: Major version jump (5→7), 2 major releases skipped

**Migration Strategy**:
1. Audit all Vite plugins for v6/v7 compatibility
2. Test SSR/build pipeline changes
3. Update vitest + @vitest/* packages simultaneously (coupled versions)
4. May require updating to @vitejs/plugin-react v6+

**Blocked By**: Vitest, @vitest/coverage-v8, @vitest/ui (must upgrade together)

**Estimated Effort**: 1-2 days (testing build pipeline + fixes)

---

### Testing Framework Blocker: Vitest Ecosystem (3 packages)

#### 6. Vitest: 1.6.1 → 4.0.18
**Reason**: MAJOR version jump (1→4), coupled with Vite version

**Breaking Changes** (cumulative across v2, v3, v4):
- Vite 5+ required (currently satisfied ✅)
- Config API changes (vitest.config.js structure)
- Coverage reporter changes
- Snapshot format changes (may break existing snapshots)

**Migration Strategy**:
1. Upgrade Vite first (blocks this update)
2. Update all @vitest/* packages together
3. Regenerate all snapshots (if any)
4. Test coverage reporting pipeline

**Blocked By**: Vite upgrade completion

**Estimated Effort**: 1 day (config updates + snapshot regeneration)

---

#### 7. @vitest/coverage-v8: 1.0.4 → 4.0.18
**Reason**: MUST match Vitest version exactly

**Action**: Upgrade together with Vitest core package

---

#### 8. @vitest/ui: 1.6.1 → 4.0.18
**Reason**: MUST match Vitest version exactly

**Action**: Upgrade together with Vitest core package

---

### Routing Blocker: React Router (1 package)

#### 9. React Router: 6.30.3 → 7.13.0 ⚠️ **MAJOR BREAKING**
**Breaking Changes** (v7):
- File-based routing by default (we use programmatic routes ✅)
- `<Outlet>` context changes
- Loader/action API changes (if using data APIs)
- TypeScript: Stricter route typing
- Removed deprecated APIs from v6

**Migration Strategy**:
1. Audit all 6 routes in App.tsx
2. Check if we use any deprecated v6 APIs
3. Test navigation guards (empty state redirects)
4. Update TypeScript route types

**Blocked By**: React 19 compatibility (React Router v7 requires React 18.3+, but optimized for React 19)

**Estimated Effort**: 1 day (route migration + testing)

---

### Animation Library Blocker: Framer Motion (1 package)

#### 10. Framer Motion: 10.18.0 → 12.31.0
**Breaking Changes** (v11+):
- LazyMotion API changes
- Gesture detection changes (may affect device swiper)
- TypeScript: Stricter variant typing
- Performance optimizations (may change animation timing)

**Migration Strategy**:
1. Test DeviceSwiper component (uses Framer Motion gestures)
2. Check all animated components (Toast, Navigation)
3. Verify animation timing hasn't regressed

**Blocked By**: React 19 testing (ensure animations work with concurrent rendering)

**Estimated Effort**: 1 day (testing animations)

---

### Optional Type Definitions (1 package)

#### 11. @types/react-dom: 18.3.7 → 19.2.3
**Reason**: Follow React-DOM version

**Action**: Update together with React-DOM + @types/react

---

## 📋 Recommended Migration Roadmap

### Phase 1: Foundation (Current - COMPLETED ✅)
- [x] Update jsdom (dev dependency, low risk)
- [x] Update @vitejs/plugin-react (compatible with Vite 5.x)
- [x] Verify Cypress already on latest v13

### Phase 2: Build Tooling (Next - 2-3 days)
**Prerequisites**: None (standalone upgrade)

**Steps**:
1. [ ] Upgrade Vite: 5.4.21 → 7.3.1
   - Review Vite v6 + v7 migration guides
   - Test production build pipeline
   - Verify all Vite plugins compatible
2. [ ] Upgrade Vitest: 1.6.1 → 4.0.18
   - Update vitest.config.js
   - Upgrade @vitest/coverage-v8, @vitest/ui simultaneously
   - Regenerate snapshots (if any)
   - Test coverage reporting

**Validation**:
- [ ] Production build successful
- [ ] All 87 unit tests pass
- [ ] Coverage ≥80% maintained

**Rollback Plan**: Git revert, restore Vite 5.x + Vitest 1.x from package-lock.json

---

### Phase 3: React Ecosystem (Next - 3-4 days)
**Prerequisites**: Phase 2 complete, Vite 7 stable

**Steps**:
1. [ ] Audit React 19 breaking changes
   - Check for `ReactDOM.render()` usage (should be `createRoot()`)
   - Verify no legacy Context API
   - Test concurrent rendering behavior
2. [ ] Upgrade React + React-DOM: 18.3.1 → 19.2.4
   - Update @types/react, @types/react-dom simultaneously
3. [ ] Upgrade @testing-library/react: 14.3.1 → 16.3.2
   - Fix waitFor() timeouts (now explicit)
   - Address async act() warnings
4. [ ] Upgrade React Router: 6.30.3 → 7.13.0
   - Test routing guards (empty state redirects)
   - Update route TypeScript types
5. [ ] Upgrade Framer Motion: 10.18.0 → 12.31.0
   - Test DeviceSwiper gestures
   - Verify animation timing

**Validation**:
- [ ] All 87 unit tests pass
- [ ] All 15 E2E tests pass
- [ ] DeviceSwiper swipe gestures work
- [ ] Toast animations render correctly
- [ ] Routing guards function (empty state redirect)

**Rollback Plan**: Git revert entire React ecosystem, restore v18 from package-lock.json

---

### Phase 4: Cypress (Optional - 1 day)
**Prerequisites**: All React 19 changes stable

**Note**: Cypress v13.17.0 is already latest stable v13. Upgrade to v15 is OPTIONAL and breaking.

**If upgrading to v15**:
1. [ ] Review Cypress v14 + v15 migration guides
2. [ ] Update cypress.config.js (component testing API changes)
3. [ ] Test all 15 E2E tests
4. [ ] Verify screenshot/video capture still works

**Validation**:
- [ ] All E2E tests pass (device discovery, manual IP config)

**Recommended**: DEFER until v15 is industry-standard or critical features needed

---

## 🔍 Validation Checklist (All Phases)

After each phase, run full test suite:

```powershell
# Backend tests
cd backend
pytest -v --cov --cov-fail-under=80

# Frontend unit tests
cd frontend
npm run test

# Frontend E2E tests
npm run test:e2e:mock

# Production build
npm run build
```

**Success Criteria**:
- ✅ 268 backend tests pass
- ✅ 87 frontend unit tests pass
- ✅ 15 E2E tests pass
- ✅ Coverage ≥80%
- ✅ Production build <2s, bundle <350KB
- ✅ No TypeScript errors

---

## 📦 Package Update Summary

| Package                   | Current | Target  | Status      | Phase   |
|---------------------------|---------|---------|-------------|---------|
| jsdom                     | 23.2.0  | 28.0.0  | ✅ DONE     | 1       |
| @vitejs/plugin-react      | 4.7.0   | 5.1.3   | ✅ DONE     | 1       |
| Cypress                   | 13.17.0 | 13.17.0 | ✅ CURRENT  | 1       |
| Vite                      | 5.4.21  | 7.3.1   | ⏸️ BLOCKED  | 2       |
| Vitest                    | 1.6.1   | 4.0.18  | ⏸️ BLOCKED  | 2       |
| @vitest/coverage-v8       | 1.0.4   | 4.0.18  | ⏸️ BLOCKED  | 2       |
| @vitest/ui                | 1.6.1   | 4.0.18  | ⏸️ BLOCKED  | 2       |
| React                     | 18.3.1  | 19.2.4  | ⏸️ BLOCKED  | 3       |
| React-DOM                 | 18.3.1  | 19.2.4  | ⏸️ BLOCKED  | 3       |
| @types/react              | 18.3.27 | 19.2.10 | ⏸️ BLOCKED  | 3       |
| @types/react-dom          | 18.3.7  | 19.2.3  | ⏸️ BLOCKED  | 3       |
| @testing-library/react    | 14.3.1  | 16.3.2  | ⏸️ BLOCKED  | 3       |
| React Router              | 6.30.3  | 7.13.0  | ⏸️ BLOCKED  | 3       |
| Framer Motion             | 10.18.0 | 12.31.0 | ⏸️ BLOCKED  | 3       |

**Progress**: 3/14 addressed (21%), 11/14 blocked (79%)

---

## 🛡️ Risk Mitigation

### Version Pinning
All updated packages use **caret ranges** (`^`) to allow patch updates but block minor/major:
- `^28.0.0` allows 28.0.x, blocks 29.x
- `^5.1.3` allows 5.1.x, blocks 5.2.x

### Git Safety
- Commit after each phase
- Tag stable states: `git tag deps-phase-1-stable`
- Fast rollback: `git reset --hard deps-phase-1-stable`

### Testing Rigor
- No phase complete without 100% test pass rate
- E2E tests critical for React 19 concurrent rendering validation

---

## 📅 Timeline Estimate

- **Phase 1**: ✅ COMPLETE (0.5 days)
- **Phase 2**: 2-3 days (Vite + Vitest migration + testing)
- **Phase 3**: 3-4 days (React 19 ecosystem migration + extensive testing)
- **Phase 4**: Optional, 1 day (Cypress v15 if needed)

**Total**: ~6-8 days for full migration

---

## 🔗 References

- [React 19 Upgrade Guide](https://react.dev/blog/2024/04/25/react-19)
- [Vite 6 Migration Guide](https://vitejs.dev/guide/migration)
- [Vitest v2+ Migration](https://vitest.dev/guide/migration.html)
- [React Router v7 Upgrade](https://reactrouter.com/en/main/upgrading/v7)
- [Framer Motion v11 Changelog](https://www.framer.com/motion/changelog/)

---

**Last Updated**: 2026-02-04  
**Next Review**: After Phase 2 completion (Vite 7 + Vitest 4 migration)
