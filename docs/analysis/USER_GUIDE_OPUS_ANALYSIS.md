# User Guide: Opus 4.5 Analyse-Session überwachen

## Deine Rolle als Auftraggeber

Du überwachst die Analyse-Session. Opus arbeitet selbstständig, aber braucht manchmal Korrekturen.

---

## 🚨 NOTFALL-PROMPTS (Copy-Paste Ready)

### 1. Bei Abbruch / Timeout / Session-Ende

```
RESUME: Die letzte Session ist abgebrochen.

1. Lies: docs/analysis/00_MASTER_ANALYSIS_PROMPT.md
2. Lies den SESSION-STATE am Ende des letzten Outputs (oder in der Analyse-Datei)
3. Setze EXAKT dort fort wo du warst
4. Keine Wiederholungen, keine Neustart - einfach WEITERMACHEN

Welche Datei war als nächstes dran?
```

### 2. Bei Rate Limit

```
Rate Limit erreicht. Bitte:
1. Speichere JETZT den aktuellen Stand (SESSION-STATE Block)
2. Schreibe den bisherigen Output in die Analyse-Datei
3. Warte 60 Sekunden
4. Dann weitermachen

Nicht vergessen: SESSION-STATE am Ende ausgeben!
```

### 3. Bei Abschweifungen / Philosophieren

```
STOPP. Du schweifst ab.

Lies nochmal den KONTEXT-CHECK Block aus dem Master-Prompt.

Dann:
- KEINE Einleitungen
- KEINE Meta-Reflexionen
- Analysiere die nächste Datei
- Dokumentiere Findings
- WEITER

Nächste Datei: [Name einfügen oder "die nächste auf der Liste"]
```

### 4. Bei zu netten/vagen Findings

```
DISZIPLINAR: Deine Findings sind zu weich.

SCHLECHT (was du geschrieben hast):
"Der Code könnte an einigen Stellen verbessert werden..."

GUT (was ich erwarte):
"BUG Zeile 45: Null-Check fehlt. Crash bei device=None."

Geh zurück zu den letzten 3 Dateien und formuliere die Findings KONKRET um.
Mit: Zeilennummer, Problem, Fix.
```

### 5. Bei "Sieht gut aus" ohne Details

```
UNZULÄSSIG. "Sieht gut aus" ist keine Analyse.

Für die Datei [X] fehlst mir:
- Welche Funktionen hast du geprüft?
- Welche Edge Cases hast du geprüft?
- Hast du recherchiert ob das Pattern aktuell ist?

Analysiere die Datei NOCHMAL. Diesmal richtig.
```

### 6. Bei übersprungenen Dateien

```
Du hast Dateien übersprungen.

Laut list_dir gibt es in [Modul]:
- datei1.py
- datei2.py
- datei3.py

Du hast nur datei1.py analysiert. Wo sind datei2 und datei3?

Analysiere ALLE Dateien. Keine Ausnahmen.
```

### 7. Bei fehlender Recherche

```
Du hast [Pattern/Library] als "okay" bewertet ohne Recherche.

Bitte:
1. Recherchiere: "[Pattern] best practices 2025"
2. Vergleiche mit aktueller FastAPI/React Dokumentation
3. Dokumentiere deine Quellen
4. Dann erst bewerten

"Ich denke das ist Standard" ist KEINE Quelle.
```

### 8. Bei Kontextverlust (wirre Antworten)

```
KONTEXT-RESET.

Du analysierst das Projekt OpenCloudTouch.
Aktuelles Dokument: [Name]
Aktuelle Datei: [Name]

Lies nochmal:
1. docs/analysis/00_MASTER_ANALYSIS_PROMPT.md (Abschnitt "Deine Rolle")
2. Den SESSION-STATE von deinem letzten Output

Dann weitermachen wo du warst.
```

---

## 📊 Überwachungs-Checkliste

### Nach jeder Opus-Antwort prüfen:

| Check | Frage | Wenn NEIN → |
|-------|-------|-------------|
| ✓ Progress | Hat er den Fortschritt gezeigt? | "Zeige den PROGRESS-Stand" |
| ✓ Zeilennummern | Haben Findings Zeilennummern? | Disziplinar #4 |
| ✓ Code-Snippets | Sind Code-Beispiele dabei? | Disziplinar #4 |
| ✓ Keine Dateien fehlen | Hat er alle Dateien aus list_dir? | Disziplinar #6 |
| ✓ Nicht zu nett | Sind Findings direkt formuliert? | Disziplinar #4 |
| ✓ SESSION-STATE | Ist am Ende ein Resume-Block? | "Füge SESSION-STATE hinzu" |

### Warnsignale erkennen:

| Warnsignal | Bedeutung | Aktion |
|------------|-----------|--------|
| Lange Einleitungen | Philosophiert statt arbeitet | Disziplinar #3 |
| "Insgesamt solide" | Zu nett, nicht kritisch | Disziplinar #4 |
| Keine Zeilennummern | Liest nicht wirklich den Code | Disziplinar #5 |
| Plötzlich anderes Thema | Kontextverlust | Disziplinar #8 |
| Keine Findings bei großer Datei | Überfliegt nur | Disziplinar #5 |
| Keine SESSION-STATE | Vergisst Resume-Protokoll | Reminder |

---

## 🕐 Typischer Session-Ablauf

### Phase 1: Setup (5 min)
1. Master-Prompt zeigen
2. Opus listet Dateien auf
3. Opus beginnt mit 01_PROJECT_OVERVIEW.md

### Phase 2: Backend-Analyse (30-60 min)
- ~25 Python-Dateien
- Erwartung: 5-15 Findings pro Modul
- Checkpoints alle 5 Dateien
- **Du:** Alle 10 Dateien kurz prüfen

### Phase 3: Frontend-Analyse (20-40 min)
- ~15 TypeScript-Dateien
- Erwartung: 5-10 Findings
- **Du:** Prüfen ob React Best Practices gecheckt

### Phase 4: Tests + Rest (15-30 min)
- Test-Dateien
- Build/Deploy
- Dokumentation
- **Du:** Prüfen ob Coverage-Lücken genannt

### Phase 5: Roadmap (10-20 min)
- Zusammenfassung
- Priorisierung
- **Du:** Final-Review

---

## 💡 Pro-Tipps

### 1. Nicht zu oft unterbrechen
Opus arbeitet besser wenn er im Flow ist. Nur eingreifen bei echten Problemen.

### 2. SESSION-STATE sichern
Nach jeder großen Antwort: Copy-Paste den SESSION-STATE in ein separates Dokument. Falls Session crasht.

### 3. Zwischenstände committen
Alle 30 Minuten: `git add docs/analysis/ && git commit -m "WIP: Analyse Stand [Zeit]"`

### 4. Bei Zweifeln: Fragen
Wenn ein Finding unklar ist: "Erkläre Finding #X genauer. Was genau ist das Problem?"

### 5. Nicht alles glauben
Opus kann sich irren. Bei kritischen Security-Findings: Selbst verifizieren oder zweite Meinung.

---

## 🔧 Troubleshooting

### Problem: Opus wiederholt sich
```
Du wiederholst dich. Datei [X] hast du bereits analysiert.

Prüfe deinen SESSION-STATE. Welche Datei ist als NÄCHSTES dran?
Dann: Diese Datei analysieren, nicht [X] nochmal.
```

### Problem: Opus macht zu viele kleine Findings
```
Zu viele Micro-Findings. Fasse zusammen:
- Gleiche Probleme in mehreren Dateien → 1 Finding mit allen Stellen
- Triviale Style-Issues → Sammeln als P3

Fokus auf P1 und P2.
```

### Problem: Opus findet "nichts"
```
"Keine Findings" bei einer 200-Zeilen-Datei ist unwahrscheinlich.

Prüfe nochmal:
- Edge Cases in Input-Handling?
- Error Handling vollständig?
- Pattern noch aktuell (recherchieren!)?
- Type Hints vollständig?
- Docstrings vorhanden?

Mindestens 1-2 Kleinigkeiten gibt es IMMER.
```

### Problem: Opus antwortet nicht mehr / Timeout
Warte 30 Sekunden. Dann neuer Chat mit Resume-Prompt (#1).

---

## Cheat Sheet: Schnelle Korrekturen

| Situation | Prompt |
|-----------|--------|
| Zu nett | "Sei kritischer. Konkrete Probleme!" |
| Keine Zeilen | "Zeilennummern fehlen!" |
| Schweift ab | "STOPP. Nächste Datei." |
| Datei fehlt | "Wo ist [datei.py]?" |
| Kontextverlust | "RESET. Lies Master-Prompt." |
| Session Ende | Resume-Prompt #1 |
| Rate Limit | "Speichern und pausieren." |
