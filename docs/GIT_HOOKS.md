# Git Hooks Setup Guide

## 🎯 Was sind Git Hooks?

Git Hooks sind **automatische Scripts**, die bei bestimmten Git-Events laufen:
- **commit-msg** - Validiert Commit-Nachricht vor dem Commit
- **pre-commit** - Führt Checks aus bevor Code committed wird
- **pre-push** - Führt Tests aus bevor Code gepusht wird

**Vorteil**: Fängt Fehler **lokal** bevor sie zu GitHub pusht werden!

---

## 🚀 Installation (einmalig)

### **Windows (PowerShell):**
```powershell
.\scripts\install-hooks.ps1
```

### **Linux/Mac (Bash):**
```bash
chmod +x scripts/install-hooks.sh
./scripts/install-hooks.sh
```

**Das war's!** Hooks sind jetzt aktiv.

---

## 📋 Konfigurierte Hooks

### **1. commit-msg Hook**
**Wann**: Bei jedem `git commit`  
**Was**: Validiert Conventional Commits Format

```bash
✅ git commit -m "feat(devices): add discovery"
❌ git commit -m "added stuff"  # → BLOCKIERT!
```

### **2. pre-commit Hook**
**Wann**: Bei jedem `git commit`  
**Was**: Automatische Code-Qualität

**Backend (Python):**
- ✅ `black` - Auto-Formatierung
- ✅ `ruff` - Linting (Auto-Fix)
- ✅ `bandit` - Security Scan

**Frontend (JavaScript/TypeScript):**
- ✅ `prettier` - Auto-Formatierung
- ✅ `eslint` - Linting

**Allgemein:**
- ✅ Trailing Whitespace entfernen
- ✅ End-of-File Newline
- ✅ YAML/JSON Syntax-Check
- ✅ Merge-Konflikt Detection
- ✅ Private Key Detection

### **3. pre-push Hook**
**Wann**: Bei `git push`  
**Was**: Schnelle Unit Tests

```bash
git push  # → Führt Backend Unit Tests aus
```

---

## 💡 Verwendung

### **Normaler Workflow:**
```bash
# 1. Code schreiben
vim apps/backend/src/adapter.py

# 2. Commit (Hooks laufen automatisch!)
git commit -m "feat(devices): add SSDP discovery"

# Hooks führen aus:
# ✅ Format Python mit black
# ✅ Lint Python mit ruff
# ✅ Security check mit bandit
# ✅ Validiere Commit-Message

# 3. Push (Tests laufen automatisch!)
git push

# Hook führt aus:
# ✅ Backend Unit Tests
```

### **Hooks haben Fehler gefunden:**

**Beispiel: Formatierung:**
```bash
$ git commit -m "feat: add discovery"

black................................................Failed
- hook id: black
- files were modified by this hook

reformatted apps/backend/src/adapter.py
```

**Lösung:**
```bash
# black hat Files automatisch formatiert
git add apps/backend/src/adapter.py
git commit -m "feat: add discovery"  # Jetzt klappt's ✅
```

**Beispiel: Commit Message:**
```bash
$ git commit -m "added stuff"

commitizen..........................................Failed
- hook id: commitizen

commit validation: failed!
please enter a commit message in the commitizen format.
```

**Lösung:**
```bash
git commit -m "feat(api): add device endpoint"  # ✅
```

---

## 🚨 Hooks überspringen (Notfall!)

**WARNUNG**: Nur in Notfällen verwenden!

```bash
# Alle Hooks überspringen
git commit --no-verify -m "WIP: emergency fix"
git push --no-verify

# Einzelnen Hook überspringen
SKIP=black git commit -m "feat: add feature"
```

**ABER**: GitHub Actions wird es trotzdem prüfen! Besser: Fehler lokal fixen.

---

## 🔧 Hooks aktualisieren

Wenn `.pre-commit-config.yaml` geändert wurde:

```bash
# Hooks neu installieren
pre-commit install --hook-type pre-commit --hook-type commit-msg --hook-type pre-push

# Auf allen Files testen
pre-commit run --all-files
```

---

## 🐛 Troubleshooting

### **Hook schlägt fehl mit "command not found"**

**Problem**: Dependency fehlt

**Lösung**:
```bash
# Windows
.\scripts\install-hooks.ps1

# Linux/Mac
./scripts/install-hooks.sh
```

### **Hooks laufen gar nicht**

**Problem**: Nicht installiert

**Lösung**:
```bash
# Check ob installiert
ls .git/hooks/

# Sollte enthalten:
# - pre-commit
# - commit-msg
# - pre-push

# Falls nicht:
pre-commit install --hook-type pre-commit --hook-type commit-msg --hook-type pre-push
```

### **"pre-commit: command not found"**

**Problem**: pre-commit Package fehlt

**Lösung**:
```bash
pip install pre-commit commitizen
```

### **Hooks sind zu langsam**

**Problem**: Hooks laufen auf allen Files

**Lösung**: Hooks laufen normalerweise nur auf **geänderten Files**. Bei `--all-files` dauert's länger.

**Optimierung**:
```yaml
# In .pre-commit-config.yaml
- id: pytest-quick
  stages: [push]  # Nur bei push, nicht commit
```

---

## 📊 Hook-Performance

Typische Laufzeiten:

| Hook | Laufzeit | Wann |
|------|----------|------|
| commit-msg | <1s | Jeder Commit |
| black | 1-3s | Jeder Commit (nur geänderte Files) |
| ruff | 1-2s | Jeder Commit (nur geänderte Files) |
| prettier | 1-2s | Jeder Commit (nur geänderte Files) |
| pytest-quick | 5-10s | Jeder Push |

**Gesamt**: ~5s bei Commit, ~10s bei Push

---

## 🎓 Best Practices

### **1. Hooks immer laufen lassen**
- ❌ NICHT: `git commit --no-verify` als Standard
- ✅ Fehler lokal fixen, nicht überspringen

### **2. Kleine, fokussierte Commits**
- Hooks laufen schneller auf wenigen Files
- Einfacher zu debuggen

### **3. Auto-Fixes nutzen**
- black/prettier formatieren automatisch
- Einfach `git add` nach Hook-Run

### **4. Bei konflikten mit Team**
- Alle müssen gleiche Hooks haben
- `install-hooks.ps1` im Onboarding

---

## 📚 Konfiguration

### **Hooks anpassen:**

Editiere `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black
        # Anpassen:
        args: [--line-length=100]
        exclude: ^legacy/  # Ignore legacy code
```

### **Neue Hooks hinzufügen:**

```yaml
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        files: ^apps/backend/src/
```

---

## 🔗 Weiterführende Links

- **Pre-commit Framework**: https://pre-commit.com/
- **Commitizen**: https://commitizen-tools.github.io/commitizen/
- **Conventional Commits**: [docs/CONVENTIONAL_COMMITS.md](CONVENTIONAL_COMMITS.md)
- **Supported Hooks**: https://pre-commit.com/hooks.html

---

## ✅ Zusammenfassung

**Git Hooks automatisieren:**
1. ✅ Code-Formatierung (black, prettier)
2. ✅ Linting (ruff, eslint)
3. ✅ Security Checks (bandit)
4. ✅ Commit-Message Validierung (commitizen)
5. ✅ Unit Tests (pytest)

**Vorteil**: Keine kaputten Commits mehr in GitHub! 🎉

---

**Installation**: `.\scripts\install-hooks.ps1` (Windows) oder `./scripts/install-hooks.sh` (Linux/Mac)
