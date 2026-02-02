# Cypress E2E Tests - Quick Start Guide

## Aktuelle Änderungen (2026-02-02)

### ✅ Was wurde implementiert:

1. **data-test Attribute** in allen relevanten UI-Komponenten:
   - `[data-test="empty-state"]` - EmptyState Container
   - `[data-test="welcome-title"]` - Willkommens-Titel
   - `[data-test="discover-button"]` - Discovery Button
   - `[data-test="manual-add-button"]` - Manuell hinzufügen Button
   - `[data-test="modal-overlay"]` - Modal Overlay
   - `[data-test="modal-content"]` - Modal Container
   - `[data-test="modal-title"]` - Modal Titel
   - `[data-test="ip-textarea"]` - IP-Eingabefeld
   - `[data-test="save-button"]` - Speichern Button
   - `[data-test="cancel-button"]` - Abbrechen Button
   - `[data-test="device-card"]` - Device Card
   - `[data-test="device-name"]` - Device Name
   - `[data-test="device-model"]` - Device Model
   - `[data-test="app-header"]` - App Header (Navigation)

2. **Custom Cypress Commands** aktualisiert:
   - Alle Commands nutzen jetzt data-test Attribute statt CSS-Klassen
   - Robustere Selektoren

3. **App.jsx Fix**:
   - Discovery Button triggert jetzt `/api/devices/sync` statt `/api/devices/discover`
   - Sync speichert Devices in DB (benötigt für Tests)

4. **Test Scenarios** angepasst:
   - Alle 12 Tests nutzen jetzt data-test Selektoren
   - Element-Existenz-Checks vor Interaktionen

## Wie testen?

### 1. Backend & Frontend starten
```bash
# Container läuft bereits: http://localhost:7777
# DB zurücksetzen:
Invoke-RestMethod -Uri "http://localhost:7777/api/test/reset" -Method POST
```

### 2. Cypress UI öffnen
```bash
cd frontend
npm run test:e2e:open
```

### 3. Tests ausführen
- **Interaktiv**: Klick auf Test-Datei in Cypress UI
- **Headless**: `npm run test:e2e:mock`

### 4. Erwartete Test-Ergebnisse

#### ✅ SOLLTEN GRÜN SEIN:
1. EmptyState - Modal Opening
   - Display EmptyState welcome screen
   - Open manual IP configuration modal

2. Single IP Configuration
   - Should save 1 IP and create 1 device

3. Two IPs Configuration
   - Should save 2 IPs and create 2 devices

4. Three IPs Configuration
   - Should save 3 IPs and create 3 devices

5. Cancel Action - No Save
   - Should not save IPs when cancel is clicked

6. Pre-filled IPs
   - Should display existing IPs when modal is opened again
   - Should allow editing existing IPs and saving changes
   - Should allow clearing all IPs

7. Complete User Journey - First Time User
   - Should complete full flow: EmptyState → Add IPs → Discover → Dashboard

#### ⚠️ MÖGLICHE ISSUES:

1. **Edge Case Tests**:
   - "10+ IPs" - könnte timeout wenn Mock-Discovery zu langsam
   - "Character limit" - hängt von UI-Validierung ab (noch nicht implementiert)

2. **Modal overlay click**:
   - Test erwartet dass Klick außerhalb Modal schließt
   - Aktuell implementiert, sollte funktionieren

3. **Returning User Journey**:
   - Erfordert dass Devices in DB sind UND App beim Start lädt
   - Sollte funktionieren mit neuem sync Endpoint

## Debugging

### Test schlägt fehl?

1. **Check Browser DevTools** (in Cypress UI):
   - Console für Errors
   - Network Tab für API Calls
   - Elements Tab für data-test Attribute

2. **Check Backend**:
   ```bash
   # Logs anzeigen
   podman logs cloudtouch-local -f
   
   # Health Check
   Invoke-RestMethod -Uri "http://localhost:7777/health"
   
   # Manual IPs prüfen
   Invoke-RestMethod -Uri "http://localhost:7777/api/settings/manual-ips"
   
   # Devices prüfen
   Invoke-RestMethod -Uri "http://localhost:7777/api/devices"
   ```

3. **Element nicht gefunden**:
   - Öffne http://localhost:7777 im Browser
   - F12 → Elements → Suche nach `data-test=`
   - Prüfe ob Attribut existiert

4. **DB State Issues**:
   ```bash
   # DB zurücksetzen zwischen Tests
   Invoke-RestMethod -Uri "http://localhost:7777/api/test/reset" -Method POST
   ```

### Bekannte Probleme & Lösungen

| Problem | Ursache | Lösung |
|---------|---------|--------|
| Modal öffnet nicht | Button Selector falsch | Prüfe `data-test="manual-add-button"` existiert |
| Devices werden nicht angezeigt | Sync erstellt keine Devices | Prüfe `/api/devices/sync` Response |
| Test timeout | Network zu langsam | Erhöhe `defaultCommandTimeout` in cypress.config.js |
| DB nicht resettet | Test-Endpoint nicht verfügbar | Prüfe `mock_mode: true` in /health |

## Nächste Schritte

### Nach erfolgreichem Test-Run:

1. **Fehlgeschlagene Tests fixen**:
   - Screenshot ansehen (`tests/e2e/screenshots/`)
   - Video ansehen (`tests/e2e/videos/`)
   - Log-Output prüfen

2. **Edge Cases implementieren**:
   - Character limit validation (z.B. max 10.000 Zeichen)
   - IP Format validation (bereits teilweise implementiert)

3. **Weitere Tests**:
   - Device interaction (Play, Pause, Volume)
   - Radio station selection
   - Multi-room control

4. **CI/CD Integration**:
   - GitHub Actions Workflow
   - Automatische Test-Runs bei Pull Requests

## Test Command Reference

```bash
# Alle Commands aus frontend/
npm run test:e2e            # Headless, default mode (mock)
npm run test:e2e:open       # Interactive UI
npm run test:e2e:mock       # Headless, explicit mock mode
npm run test:e2e:real       # Headless, real devices (requires hardware)
```

## API Endpoints für manuelle Tests

```powershell
# Reset DB
Invoke-RestMethod -Uri "http://localhost:7777/api/test/reset" -Method POST

# Set Manual IPs
Invoke-RestMethod -Uri "http://localhost:7777/api/settings/manual-ips" -Method POST -ContentType "application/json" -Body '{"ips": ["192.168.1.50", "192.168.1.51"]}'

# Get Manual IPs
Invoke-RestMethod -Uri "http://localhost:7777/api/settings/manual-ips"

# Sync Devices
Invoke-RestMethod -Uri "http://localhost:7777/api/devices/sync" -Method POST

# Get Devices
Invoke-RestMethod -Uri "http://localhost:7777/api/devices"
```

## Erfolgs-Kriterien

✅ **Tests sind erfolgreich wenn**:
- Alle Element-Checks grün (data-test Attribute gefunden)
- Modal öffnet/schließt korrekt
- IPs werden in DB gespeichert (API-Check)
- Devices werden erstellt (API-Check)
- UI zeigt korrekte Anzahl Devices (visueller Check)
- Navigation erscheint nach Discovery

❌ **Tests schlagen fehl wenn**:
- Element nicht gefunden (falsche Selektoren)
- API gibt Error (Backend-Problem)
- Timeout (Performance-Problem)
- DB-State inkonsistent (Reset nicht durchgeführt)
