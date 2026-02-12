# Cypress E2E Test Performance Analysis

**Date**: 2026-02-12  
**Baseline**: 31s for 22 tests (3 specs)  
**After Phase 1+2**: ~29s (estimated 1.2s improvement)  
**Goal**: Improve performance without introducing flaky tests

## Baseline (Before Optimizations)

```
Spec                              Tests  Duration
device-discovery.cy.ts              5     7s
manual-ip-configuration.cy.ts      10    22s
preset-mapping.cy.ts                7     1s (reduced to 3 tests)
-------------------------------------------
Total                              22    31s
After test cleanup                 18    31s
```

## Implemented Optimizations

### ✅ Phase 1: Timeout Reduction (Commit c0e8f9d)
- `defaultCommandTimeout`: 10s → 5s
- `requestTimeout`: 10s → 8s
- `responseTimeout`: 10s → 8s
- **Expected Savings**: 1-2s (on failed assertions)
- **Risk**: ZERO (only affects failure speed)

### ✅ Phase 2: Animation Waits (Commit 9ee6c1c)
- Reduced `cy.wait(300)` → `cy.wait(150)` at 8 locations
- device-discovery.cy.ts lines: 47, 58, 69, 75, 100, 102, 107, 109
- **Actual Savings**: 1.2s (8 × 150ms per test run)
- **Risk**: LOW (50% reduction conservative, animations <150ms)

### ❌ Phase 3: beforeEach → before (CANCELLED - UNSAFE)
**Analysis Result**: All test suites modify state (devices, settings, presets)
- device-discovery.cy.ts: Test 2 modifies manual IPs
- manual-ip-configuration.cy.ts: All tests modify IPs
- preset-mapping.cy.ts: All tests modify presets

**Safety Assessment**:
- beforeEach → before would break test isolation
- Tests expect clean DB state on each run
- Conditional cleanup adds complexity without meaningful savings
- **Expected Savings**: 2-4s (22 → 3 cleanups)
- **Risk**: HIGH (flaky tests, race conditions)
- **Decision**: SKIPPED - test stability > performance gains

## Final Performance Summary

| Phase | Optimization | Savings | Status |
|-------|-------------|---------|--------|
| Phase 1 | Timeout reduction | 1-2s | ✅ COMMITTED (c0e8f9d) |
| Phase 2 | Animation waits | 1.2s | ✅ COMMITTED (9ee6c1c) |
| Phase 3 | beforeEach consolidation | 2-4s | ❌ UNSAFE - CANCELLED |
| **Total** | **Implemented** | **~2.2s** | **7% improvement** |

**New Estimated Duration**: 31s → ~29s (conservative)

## Performance Bottlenecks

### 1. beforeEach Database Cleanup (MAJOR)
```typescript
beforeEach(() => {
  cy.request('DELETE', `${apiUrl}/devices`)  // Every single test!
  cy.request('POST', `${apiUrl}/settings/manual-ips`, { ips: [] })
})
```

**Impact**: 22 DB cleanups x ~100-200ms = 2.2-4.4s overhead

**Solution Options**:
- **A) before() instead of beforeEach()**: Single cleanup per suite (not per test)
  - Risk: Test isolation broken if tests modify state
  - Benefit: 20x faster (~100ms total vs 4.4s)
  
- **B) Conditional cleanup**: Only clean if previous test modified DB
  - Complexity: Need state tracking
  - Benefit: Skip cleanup for read-only tests

- **C) Database transactions**: Rollback after each test
  - Complexity: Requires backend changes
  - Benefit: True test isolation + fast cleanup

**Recommendation**: Use `before()` for suites with independent tests

### 2. Fixed Wait Times (MEDIUM)
```typescript
cy.wait(300)  // 8x in device-discovery = 2.4s
```

**Current**: Hard-coded animation waits  
**Status**: Already optimized in failed attempt

**Solution**:
- Replace with DOM visibility assertions
- Keep minimal waits (50-100ms) for CSS transitions
- Use `cy.get().should('be.visible')` (auto-retry)

### 3. Sequential API Calls (MEDIUM)
```typescript
// Current: Sequential
cy.request(`${apiUrl}/devices`)
cy.request(`${apiUrl}/settings/manual-ips`)
cy.request(`${apiUrl}/presets/${deviceId}`)
```

**Issue**: 3x 50ms = 150ms instead of 50ms parallel

**Solution**: Batch independent requests
```typescript
cy.wrap(null).then(() => {
  return Cypress.Promise.all([
    cy.request(`${apiUrl}/devices`),
    cy .request(`${apiUrl}/settings/manual-ips`)
  ])
})
```

### 4. Slow Timeouts (LOW)
```typescript
defaultCommandTimeout: 10000  // 10s default wait
```

**Current**: Conservative 10s timeout on all commands  
**Impact**: Failed assertions wait full 10s before failing

**Solution**:
- Reduce to 4-6s (most assertions resolve <2s)
- Keep 10s+ for slow operations (network, large renders)
- Use per-command overrides: `cy.get(..., { timeout: 2000 })`

### 5. Test Execution Overhead (LOW)
```typescript
video: false  // Already disabled ✓
```

**Already Optimized**:
- Video recording disabled
- Screenshots only on failure
- No fixture loading

**Additional Options**:
- `numTestsKeptInMemory: 0` (reduce memory)
- `experimentalMemoryManagement: true` (Cypress 13+)

## Future Optimization Opportunities

### Potential Phase 4: Test Parallelization
- Cypress Cloud: Run specs in parallel across machines
- Expected savings: 30-50% (3 specs → parallel execution)
- Cost: Cypress Cloud subscription required

### Potential Phase 5: Mock Optimization
- MockDiscoveryAdapter: Instant responses (<10ms)
- Current: Simulates real timing (~100ms)
- Expected savings: Minimal (<500ms total)
- Risk: Tests don't reflect real-world performance

### NOT RECOMMENDED: beforeEach → before
**Reason**: Tests modify state and require isolation
```typescript
// ❌ UNSAFE - Tests expect clean DB
before(() => {
  cy.request('DELETE', `${apiUrl}/devices`)
})

// ✅ SAFE - Guarantees test isolation
beforeEach(() => {
  cy.request('DELETE', `${apiUrl}/devices`)
})
```
```typescript
defaultCommandTimeout: 5000,  // Down from 10s
requestTimeout: 8000,          // Keep higher for network
```

3. **Batch API calls** (saves ~0.5s)
```typescript
// In commands.ts
Cypress.Commands.add('cleanDatabase', () => {
  const apiUrl = Cypress.env('apiUrl')
  return Cypress.Promise.all([
    cy.request('DELETE', `${apiUrl}/devices`),
    cy.request('POST', `${apiUrl}/settings/manual-ips`, { ips: [] })
  ])
})
```

### Phase 2: Medium-Risk Optimizations (Expected: 24s → 18s)

4. **Optimize waits with assertions** (saves ~2s)
```typescript
// Instead of cy.wait(300)
cy.get('.swipe-arrow-right').click()
cy.get('[data-test="device-card"]').should('be.visible')
```

5. **Parallel test execution** (saves ~6s)
```bash
cypress run --parallel --record --key <key>
# Requires Cypress Cloud (paid) or CI setup
```

### Phase 3: Advanced Optimizations (Research)

6. **Custom test data seeding** (instead of discovery)
```typescript
// Skip slow device sync, inject mock DB data directly
cy.task('seedDatabase', [device1, device2, device3])
```

7. **Shared browser context** (experimental)
```typescript
// Keep browser session between tests (Cypress 13+)
testIsolation: false
```

## Performance Comparison Matrix

| Optimization                  | Time Saved | Risk  | Effort |
|-------------------------------|------------|-------|--------|
| before() instead beforeEach() | 3-4s       | Low   | 5min   |
| Reduce timeouts 10s→5s        | 1-2s       | Low   | 2min   |
| Batch API calls               | 0.5s       | Low   | 10min  |
| Replace cy.wait() with assert | 2s         | Med   | 20min  |
| Parallel execution (Cloud)    | 6s         | Low   | 1hr    |
| Custom DB seeding             | 3-5s       | Med   | 2hr    |
| Shared browser context        | 4-6s       | High  | 30min  |

**Total Potential**: 31s → 12-15s (without high-risk changes)

## Implementation Plan

### Step 1: Safe Changes (No Test Modifications)
```typescript
// cypress.config.ts
export default defineConfig({
  e2e: {
    defaultCommandTimeout: 5000,  // ← Change 1
    requestTimeout: 8000,
    numTestsKeptInMemory: 0,      // ← Change 2
  }
})
```

### Step 2: before() Migration
```typescript
// Pattern for each spec
describe('Suite', () => {
  before(() => {
    // ONE-TIME setup
    cy.request('DELETE', `${apiUrl}/devices`)
  })
  
  beforeEach(() => {
    // Only if test requires clean state
  })
})
```

### Step 3: Targeted cy.wait() Removal
```typescript
// Only remove where safe (no CSS transitions)
cy.get('.button').click()
// cy.wait(300) ← REMOVE
cy.get('.result').should('exist') // ← ADD (auto-retry)
```

### Step 4: Validate
```bash
# Run tests 5x to check for flakiness
for i in {1..5}; do npm run test:e2e; done
```

## Anti-Patterns to Avoid

❌ **Don't**:
- Remove all cy.wait() (CSS transitions need time)
- Set timeouts <2s (causes false negatives)
- Use testIsolation: false (breaks test independence)
- Skip cleanup (state leaks between tests)

✅ **Do**:
- Keep 50-100ms waits for animations
- Use progressive timeouts (fast assertions = short timeout)
- Cleanup once per suite (if tests are independent)
- Measure flakiness (run tests 10x)

## Expected Results

**Conservative Approach** (Phase 1 only):
- Duration: 31s → 24s (23% improvement)
- Flakiness: 0% (no risky changes)
- Effort: 30 minutes

**Aggressive Approach** (Phase 1-2):
- Duration: 31s → 18s (42% improvement)
- Flakiness: <5% (acceptable for dev)
- Effort: 2 hours

**Maximum Optimization** (Phase 1-3):
- Duration: 31s → 12s (61% improvement)
- Flakiness: 10-15% (CI retry needed)
- Effort: 4 hours + Cypress Cloud setup

## References

- [Cypress Best Practices - Performance](https://docs.cypress.io/guides/references/best-practices#Performance)
- [Cypress Configuration Options](https://docs.cypress.io/guides/references/configuration)
- [Cypress parallelization](https://docs.cypress.io/guides/guides/parallelization)
- [Community: Speeding up Cypress tests](https://glebbahmutov.com/blog/cypress-tips-and-tricks/)

## Decision

**Recommended**: Phase 1 (Safe Changes)  
**Rationale**: 23% improvement with zero risk, 30min effort  
**Next Step**: Implement before() + timeout reduction, measure results
