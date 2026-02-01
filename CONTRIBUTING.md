# Contributing to CloudTouch

Danke für dein Interesse an **CloudTouch**! 🎉  
Beiträge jeder Art sind willkommen – Code, Tests, Dokumentation, Ideen und Feedback.

---

## 🎯 Projektziele (bitte unbedingt beachten)

CloudTouch ist als **Open-Source-Produkt** für **nicht versierte Nutzer** gedacht.
Bitte richte deinen Beitrag an diesen Prinzipien aus:

- **Laienfreundlichkeit**
  - „Ein Container, eine Web-UI“
  - Keine Pflicht zu Home Assistant, YAML oder komplexen Setups
  - Fehlermeldungen verständlich, nicht nur Stacktraces

- **Erweiterbarkeit**
  - Provider/Streaming über Adapter (kein Hardcoding)
  - Klare Modulgrenzen (Device / Provider / UI / Storage)

- **Testbarkeit**
  - Neue Logik braucht Tests (mind. Unit)
  - Integration für Adapter/Protokoll-Module

- **Open-Source-Tauglichkeit**
  - Keine proprietären Firmware-Dateien im Repository
  - Keine Nutzung von APIs/Quellen, die rechtlich/ToS-technisch unklar sind (ohne vorherige Diskussion)

Beiträge, die diese Ziele verschlechtern (Overengineering, unnötige Komplexität, UI-Regression), können abgelehnt werden.

---

## 🛠️ Entwicklungsworkflow (Standard)

1. Fork das Repository
2. Erstelle einen Feature-Branch (`feat/...`, `fix/...`, `docs/...`)
3. Implementiere die Änderung
4. Starte Tests lokal
5. Erstelle einen Pull Request

**Commit Messages (empfohlen):**
- `Iteration X: <kurze Beschreibung>` (wenn iterativ entwickelt wird)
- oder conventional-ish: `feat: ...`, `fix: ...`, `docs: ...`

---

## 🧪 Tests

Erwartet werden je nach Änderung:

- **Unit Tests** (Pflicht für neue Logik)
- **Integration Tests** (z. B. Provider-Adapter, SoundTouch-Client)
- **E2E/Demo** (optional): ein Script, das Preset setzt und Playback verifiziert

Ziel ist nicht Dogmatismus, sondern stabile Entwicklung mit schnellen Feedback-Loops.

---

## 🧼 Refactoring-Regeln

- Refactoring nur mit **Begründung** und **Scope**
- Kein Overengineering (keine „Frameworkitis“)
- Lesbarkeit > Cleverness
- Jede Refactoring-Änderung muss die Ziele **Laienfreundlichkeit** und **Wartbarkeit** verbessern

---

## 🔐 Lizenz & Rechte

Mit dem Einreichen eines Beitrags erklärst du dich einverstanden, dass dein Beitrag unter der **Apache License 2.0**
veröffentlicht wird.

Du bestätigst außerdem, dass du das Recht hast, den Code beizusteuern, und dass der Beitrag keine Rechte Dritter verletzt.

---

## 💬 Kommunikation

- Nutze GitHub Issues für Bugs/Features/Design-Diskussionen
- Bitte immer:
  - Reproduktionsschritte
  - Logs/Screenshots (wenn möglich)
  - Geräte-Modell + Firmware-Version

Vielen Dank fürs Mitmachen! 🚀
