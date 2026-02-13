# Agent Prompt Template

**Anleitung:** Task-Datei öffnen, dann Prompt unten komplett kopieren (mit Maus markieren oder Strg+A) und in neuen Chat einfügen.

---

Arbeite die Tasks aus [TASK-DATEI] komplett autonom ab.

**Regeln:**
- Komplett silent (keine "Ich mache jetzt...", "Lass mich..." Ankündigungen)
- Keine Abkürzungen (ALLE Tasks abarbeiten)
- Kein Nachfragen (außer kritische Fehler)
- Kein Überspringen von Tasks
- Kein "Darf ich jetzt?" oder "Soll ich?"

**Workflow pro Task:**
1. Task implementieren (silent)
2. `npm test` ausführen (ALLE Tests: Backend + Frontend + E2E)
3. Falls Test fehlschlägt: Erst Regression-Test schreiben, dann fixen
4. `git commit -m "..."` nur wenn ALLE Tests grün
5. Nächster Task

**Nach ALLEN Tasks - Finaler Report (maximal 20 Zeilen):**
```
✅ Alle Tasks abgeschlossen

Geänderte Dateien:
- apps/backend/src/config.py (Zeile 36: Port 4173 hinzugefügt)
- apps/backend/tests/integration/test_cors.py (NEU: 4 Regression-Tests)

Commits:
- abc1234 fix(e2e): resolve 'Failed to fetch' error

Tests: 359 Backend + 260 Frontend + 17 E2E = ALLE grün ✅
```

**Verboten:**
- Tool-Usage beschreiben ("Ich nutze jetzt grep_search...")
- Fortschritt kommentieren ("Task 1 von 5 erledigt...")
- Commits ohne grüne Tests
- Bug-Fixes ohne Regression-Test
- `git commit --no-verify` verwenden
