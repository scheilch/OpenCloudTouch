# Codecov Setup - Anleitung

## Was ist Codecov?

Codecov trackt deine **Test-Coverage über Zeit** und zeigt in Pull Requests:
- ✅ Welche neuen Zeilen getestet sind
- ❌ Welche neuen Zeilen NICHT getestet sind  
- 📈 Coverage-Trend (steigt/fällt?)

**Kosten**: 100% GRATIS für Public Repos!

---

## 🚀 Aktivierung (5 Minuten)

### Schritt 1: Codecov Account erstellen

1. Gehe zu: https://about.codecov.io/
2. Klicke **"Sign Up"**
3. Wähle **"Sign in with GitHub"**
4. Autorisiere Codecov

✅ **Fertig!** Codecov erkennt automatisch dass dein Repo public ist.

---

### Schritt 2: Repository aktivieren

1. Nach Login: Du siehst eine Liste deiner GitHub Repos
2. Finde `user/soundtouch-bridge`
3. Klicke **"Setup repo"** oder Toggle auf **ON**

📸 Screenshot: Codecov zeigt Dir jetzt ein Upload-Token an.

---

### Schritt 3: Token zu GitHub Secrets hinzufügen

1. **Kopiere** das Codecov Upload Token (sieht aus wie: `a1b2c3d4-e5f6-...`)

2. Gehe zu deinem GitHub Repo:
   ```
   https://github.com/user/soundtouch-bridge/settings/secrets/actions
   ```

3. Klicke **"New repository secret"**

4. Füge hinzu:
   - **Name**: `CODECOV_TOKEN`
   - **Value**: *(das kopierte Token)*

5. Klicke **"Add secret"**

✅ **Fertig!** GitHub Actions kann jetzt Coverage hochladen.

---

### Schritt 4: Workflow testen

1. Committe & pushe irgendeine Änderung (z.B. README edit)
2. Warte bis GitHub Actions durchgelaufen ist (~5min)
3. Gehe zu **Actions** Tab → Klicke auf den Run
4. Suche Job **"Backend Tests"** → Prüfe Step **"Upload coverage to Codecov"**

✅ Sollte grün sein mit:
```
Uploading coverage to Codecov...
✓ Coverage uploaded successfully
```

---

### Schritt 5: Codecov Dashboard checken

1. Gehe zu: https://app.codecov.io/gh/user/soundtouch-bridge
2. Du siehst jetzt:
   - 📊 Gesamt-Coverage (z.B. 82%)
   - 📈 Coverage-Trend Graph
   - 📁 File-Browser (welche Files gut getestet sind)
   - 🔴 Red/Green Coverage-Ansicht

---

## 🎯 PR Integration (Bonus)

Sobald Codecov aktiv ist, bekommst du **automatisch** in jedem Pull Request:

### GitHub PR Comment (automatisch):
```markdown
## Codecov Report
Coverage: 82.5% (+0.3%) 📈

Files Changed:
| File | Coverage | Δ |
|------|----------|---|
| adapter.py | 95.2% | +2.1% ✅ |
| routes.py | 78.4% | -1.2% ⚠️ |

Missing coverage on:
- Line 42-45: Error handling not tested
- Line 78: Edge case missing
```

### GitHub Status Check:
- ✅ Grün: Coverage hat sich nicht verschlechtert
- ❌ Rot: Coverage ist gefallen (blockiert Merge wenn aktiviert)

---

## ⚙️ Konfiguration (Optional)

Erstelle `codecov.yml` im Root:
```yaml
coverage:
  status:
    project:
      default:
        target: 80%        # Minimale Coverage
        threshold: 1%      # Max. 1% Rückgang erlaubt
    patch:
      default:
        target: 80%        # Neue Code muss 80% Coverage haben

comment:
  layout: "header, diff, files"
  behavior: default

ignore:
  - "apps/frontend/tests/**"
  - "apps/backend/tests/**" 
  - "**/node_modules/**"
```

---

## 🔧 Troubleshooting

### Error: "Missing repository upload token"
➡️ GitHub Secret `CODECOV_TOKEN` fehlt oder falsch geschrieben (siehe Schritt 3)

### Error: "HTTP 401 Unauthorized"
➡️ Token ist abgelaufen oder falsch → Neues Token bei Codecov holen

### Coverage wird nicht angezeigt
➡️ Check ob `coverage.xml` (Backend) und `coverage-summary.json` (Frontend) erzeugt werden:
```bash
# Lokal testen:
cd apps/backend
pytest --cov=opencloudtouch --cov-report=xml
ls coverage.xml  # Muss existieren!

cd apps/frontend  
npm run test:coverage
ls coverage/coverage-summary.json  # Muss existieren!
```

---

## 📊 Was du jetzt hast

✅ Coverage uploaden bei jedem Push/PR  
✅ Coverage-Trend Tracking über Zeit  
✅ Automatische PR Comments mit Diff  
✅ File-Level Coverage Browser  
✅ Branch Coverage Comparison  
✅ Codecov Badge für README (optional):

```markdown
[![codecov](https://codecov.io/gh/user/soundtouch-bridge/branch/main/graph/badge.svg)](https://codecov.io/gh/user/soundtouch-bridge)
```

---

## ❓ FAQ

**Q: Kostet das etwas?**  
A: NEIN! Komplett gratis für Public Repos.

**Q: Kann ich es später deaktivieren?**  
A: Ja, einfach GitHub Secret `CODECOV_TOKEN` löschen.

**Q: Funktioniert es mit Private Repos?**  
A: Ja, aber dann zahlungspflichtig nach 250 Commits/Monat.

**Q: Brauche ich Codecov?**  
A: Nein, pytest-cov + vitest zeigen dir auch Coverage lokal. Aber Codecov hilft **massiv** bei PRs und zeigt Trends.

---

**Viel Erfolg!** 🎉

Bei Fragen: https://docs.codecov.com/
