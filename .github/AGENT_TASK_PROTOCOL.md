# Agent Task Protocol - TDD & Silent Execution

## Workflow (MANDATORY)

```
1. IMPLEMENT → 2. TEST ALL → 3. FIX BUGS → 4. REGRESSION TEST → 5. COMMIT
```

### Rule #1: Silent Execution
- NO progress announcements ("I will now...", "Let me...")
- NO tool usage descriptions
- ONLY final 20-line report at end

### Rule #2: Test-First Development
After EVERY code change:
```bash
npm test              # Run ALL tests (backend + frontend + e2e)
```

**NEVER skip tests. NEVER commit without green tests.**

### Rule #3: Bug → Regression Test
When ANY test fails after your change:
1. **STOP** - Do NOT fix without test
2. **CREATE** regression test reproducing bug
3. **VERIFY** test fails (RED)
4. **FIX** bug (GREEN)
5. **COMMIT** fix + test together

### Rule #4: Commit Gate
```bash
git add -A
git commit -m "type(scope): description"  # Triggers pre-commit hook
# Hook runs: black, ruff, prettier, ALL TESTS
# If hook fails: FIX, don't bypass with --no-verify
git push
```

**NO commits without:** ✅ All tests green ✅ Pre-commit hook passed

### Rule #5: Final Report Format
```
✅ Task: [description]

Changes:
- file1.py (lines 10-30)
- file2.ts (new function)

Tests: 359 backend + 260 frontend + 17 e2e = all green ✅
Commit: abc1234
```

---

## Example Task Execution

**Input:** "Fix CORS configuration for E2E tests"

**Agent Workflow:**
1. Edit `config.py` (add port 4173) - SILENT
2. Run `npm test` - SILENT
3. E2E fails → Create `test_cors_configuration.py` - SILENT
4. Run `npm test` → All green - SILENT
5. `git commit -m "fix(cors): add port 4173 for E2E preview"`
6. Output final report (20 lines max)

**NO intermediate outputs. NO "I'm now testing...". NO explanations during work.**

---

## Anti-Patterns (FORBIDDEN)

❌ Committing without running tests
❌ Skipping regression tests for "trivial" bugs  
❌ Using `git commit --no-verify`
❌ Verbose progress updates during execution
❌ Fixing bugs without reproducing them in tests first

---

**TL;DR:** Code → Test ALL → Fix bugs with regression tests → Commit when green → Report
