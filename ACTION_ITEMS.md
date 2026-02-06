# 🎯 Cleanup Action Items

**Stand:** 2026-02-06  
**Ziel:** Professionelle npm-basierte Infrastruktur, keine lokalen Artifacts in Git

---

## ✅ Bereits Erledigt

1. **Root package.json erstellt** - Monorepo-Orchestrierung
2. **Frontend package.json aufgeräumt** - Obsolete Scripts entfernt
3. **Node.js E2E Runner** - `scripts/e2e-runner.mjs` (plattformunabhängig)
4. **npm Scripts** - `npm test`, `npm run test:e2e`, etc.
5. **.gitignore aktualisiert** - Lokale Artifacts ausgeschlossen
6. **Dokumentation** - TESTING.md, DEPENDENCY-MANAGEMENT.md, MIGRATION.md
7. **deployment/local/** - Verzeichnis für persönliche Scripts erstellt

---

## 📋 Nächste Schritte (Deine Entscheidung)

### Phase 1: Scripts Aufräumen

**Löschen (obsolete PowerShell Scripts):**
```powershell
Remove-Item tools\local-scripts\run-all-tests.ps1
Remove-Item tools\local-scripts\run-backend-tests.ps1
Remove-Item tools\local-scripts\run-frontend-tests.ps1
Remove-Item tools\local-scripts\run-e2e-tests.ps1
```

**Verschieben (persönliche Deployment Scripts):**
```powershell
Move-Item tools\local-scripts\deploy-*.ps1 deployment\local\
Move-Item tools\local-scripts\export-image.ps1 deployment\local\
Move-Item tools\local-scripts\clear-database.ps1 deployment\local\
Move-Item tools\local-scripts\run-e2e-tests-on-truenas.ps1 deployment\local\
```

**Behalten (für andere Entwickler nützlich):**
```
tools/local-scripts/pre-commit.ps1          → TODO: npm script
tools/local-scripts/fetch-api-schemas-complete.ps1  → TODO: backend utility
tools/local-scripts/run-real-tests.ps1      → Optional: Hardware tests
```

---

### Phase 2: Agent-Dokumente Lokalisieren

**Option A:** Aus Git entfernen (empfohlen)
```bash
# AGENTS.md und agent-prompts/ sind bereits in .gitignore
git rm --cached AGENTS.md
git rm --cached -r docs/agent-prompts/
git commit -m "chore: remove personal agent docs from version control"
```

**Option B:** Behalten (wenn für Team relevant)
- Wenn andere Entwickler auch AI-Agents nutzen
- Umbenennen in `CONTRIBUTING_AI.md` (generischer)
- Agent-Prompts als Templates anbieten

**Deine Entscheidung:** A oder B?

---

### Phase 3: Git History Cleanup (Optional)

Wenn bereits committed (und Du History säubern willst):

```bash
# Alle Commits durchsuchen und sensible Daten entfernen
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch deployment/local/*' \
  --prune-empty --tag-name-filter cat -- --all

# Alternative: BFG Repo-Cleaner (schneller)
bfg --delete-files deployment/local/*
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

**⚠️ Achtung:** Nur wenn noch kein Public Repo! Sonst History bleibt.

---

## 🚀 Neue Workflows

### Entwickeln
```bash
npm run dev              # Backend + Frontend starten
npm test                 # Alle Tests
```

### Testen
```bash
npm run test:backend     # Python pytest
npm run test:frontend    # Vitest
npm run test:e2e         # Cypress (Node.js)
```

### Deployment (persönlich)
```powershell
# Deine Scripts in deployment/local/
.\deployment\local\deploy-to-truenas.ps1
```

### CI/CD
```yaml
- run: npm install
- run: npm test
```

---

## 📁 Neue Struktur (Nach Cleanup)

```
cloudtouch/
├── package.json                  # Root orchestration
├── MIGRATION.md                  # ✅ Migration guide
├── .gitignore                    # ✅ Updated
├── scripts/
│   └── e2e-runner.mjs           # ✅ Node.js E2E runner
├── apps/
│   ├── backend/                  # Python FastAPI
│   └── frontend/                 # React + Vite
│       └── package.json          # ✅ Cleaned up
├── deployment/
│   ├── docker-compose.yml        # Shared config
│   └── local/                    # ✅ Gitignored personal scripts
│       ├── README.md             # ✅ Examples for devs
│       ├── deploy-to-truenas.ps1 # Deine Scripts (nicht committed)
│       └── .env                  # Deine Credentials (gitignored)
├── docs/
│   ├── TESTING.md                # ✅ Test infrastructure
│   └── DEPENDENCY-MANAGEMENT.md  # ✅ npm workspaces guide
└── tools/
    └── local-scripts/            # ⚠️ Gitignored (optional: löschen)
        ├── pre-commit.ps1        # TODO: npm script
        ├── fetch-api-schemas-complete.ps1  # TODO: backend util
        └── run-real-tests.ps1    # Optional: Hardware tests
```

---

## ❓ Deine Entscheidungen

### 1. Agent-Dokumente
- [ ] **Option A:** Aus Git entfernen (AGENTS.md, docs/agent-prompts/) → empfohlen
- [ ] **Option B:** Behalten und umbennen (CONTRIBUTING_AI.md)

### 2. tools/local-scripts/
- [ ] **Option A:** Komplett löschen (alles obsolet oder nach deployment/local/ verschoben)
- [ ] **Option B:** Behalten aber gitignoren (Du nutzt es noch)
- [ ] **Option C:** Nur spezifische Scripts behalten (welche?)

### 3. pre-commit.ps1
- [ ] **Option A:** Konvertieren zu npm script + Husky (Git Hooks)
- [ ] **Option B:** Behalten als PowerShell (falls Du das bevorzugst)
- [ ] **Option C:** Löschen (manuell `npm test` vor commit)

### 4. Git History
- [ ] **Option A:** Lassen wie es ist (History bleibt)
- [ ] **Option B:** filter-branch (entfernt sensible Daten aus History)
- [ ] **Option C:** Neues Repo starten (Clean slate)

---

## 🎓 Was Du Gelernt Hast

1. **npm workspaces** - Dependency Hoisting, Monorepo-Struktur
2. **Cross-platform Scripts** - Node.js statt PowerShell
3. **Gitignore Best Practices** - Lokale Artifacts ausschließen
4. **Professional Workflows** - Industry Standards (npm, Docker, CI/CD)
5. **Documentation First** - TESTING.md, DEPENDENCY-MANAGEMENT.md

---

## 📝 Nächster Schritt

**Was möchtest Du JETZT tun?**

A) Scripts aufräumen (löschen/verschieben) - ich helfe Dir dabei  
B) Agent-Dokumente aus Git entfernen - ich mache das  
C) pre-commit zu npm Script konvertieren - ich setze Husky auf  
D) Alles so lassen, erstmal testen - Du probierst `npm test` aus  

**Deine Wahl?** 🎯
