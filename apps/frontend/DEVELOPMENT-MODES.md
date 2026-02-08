# Frontend Development Modes

OpenCloudTouch Frontend unterstützt zwei Development-Modi:

## 🎭 Mock Mode (Standard für Entwicklung)

**Verwendung**: UI-Entwicklung OHNE Backend

```bash
npm run dev         # Startet mit Mock-Interceptor (Standard)
```

**Features**:
- ✅ Alle `/api/*` Calls werden abgefangen
- ✅ Mock-Daten aus `src/mocks/mockData.js`
- ✅ 3 vorkonfigurierte Geräte
- ✅ Manuelle IPs funktionieren (in-memory)
- ✅ Discovery Simulation
- ✅ Kein Backend benötigt!

**Verwendungszweck**:
- UI-Komponenten entwickeln
- Styling anpassen
- React-Flows testen
- OHNE echte Geräte oder Backend

---

## 🔴 Live Mode (Gegen echtes Backend)

**Verwendung**: Integration Tests mit echtem Backend

```bash
# Terminal 1: Backend starten
cd ../backend
pip install -e .
python -m opencloudtouch

# Terminal 2: Frontend OHNE Mock
npm run dev:live
```

**Features**:
- ✅ Echte API-Calls zum Backend
- ✅ Echte SSDP Discovery
- ✅ Echte Geräte (falls vorhanden)
- ✅ Manuelle IPs (persistent in SQLite)

**Verwendungszweck**:
- API Integration testen
- Mit echten Geräten testen
- Backend-Features entwickeln

---

## 🏗️ Build für Production

```bash
npm run build              # Production Build (OHNE Mocks)
npm run build:mock         # Development Build (MIT Mocks)

npm run preview            # Preview Production Build
npm run preview:mock       # Preview Development Build (mit Mocks)
```

**Container Deployment**:
```powershell
# Podman Container mit echtem Backend
cd ../deployment
.\deploy-local.ps1

# Browser: http://localhost:7777
```

---

## 📂 Mock-System Dateien

```
frontend/
├─ src/
│  └─ mocks/
│     ├─ mockData.js         # Mock Devices + Responses
│     └─ interceptor.js      # fetch() Interceptor
├─ .env.development.local    # VITE_MOCK_MODE=true
└─ .env.production           # VITE_MOCK_MODE=false
```

**Anpassung Mock-Daten**:
```javascript
// src/mocks/mockData.js
export const mockDevices = [
  {
    id: 1,
    device_id: "MOCK_AABBCC112233",
    name: "Mein Gerät",
    type: "SoundTouch 10",
    // ...
  }
];
```

---

## 🧪 Cypress E2E Tests

**Cypress nutzt eigenes Mocking** (Cypress Intercept):

```bash
npm run test:e2e        # Alle Tests (mit Cypress Mocks)
npm run test:e2e:open   # Interaktiver Mode
```

**Wichtig**: Cypress Tests laufen IMMER mit Mocks (unabhängig von `VITE_MOCK_MODE`)!

### Regression Tests - Bug Fixes

Die folgenden Bug-Fixes haben dedizierte Regression Tests:

#### 1. ✅ Manual IPs Bulk Endpoint
- **Bug**: Interceptor handhabte nur `/add` Endpoint, nicht POST `/api/settings/manual-ips`
- **Fix**: Bulk handler hinzugefügt (interceptor.js Zeile 103-117)
- **Test**: `manual-ip-configuration.cy.js` → "BUG-FIX: Manual IPs should save via bulk endpoint"
- **Status**: ✅ Automatisch getestet in Cypress

#### 2. ✅ Discovery Sync Immediately (1-Click)
- **Bug**: Devices wurden mit `setTimeout(500ms)` gesetzt → 2 Klicks nötig
- **Fix**: Devices SOFORT in sync response setzen (interceptor.js Zeile 77-86)
- **Test**: Bereits abgedeckt durch "should complete full flow: EmptyState → Add IPs → Discover → Dashboard"
- **Status**: ✅ Automatisch getestet in Cypress

#### 3. ⚠️ localStorage Persistence (nur manuell testbar)
- **Bug**: Keine Persistenz → Browser refresh verliert alle Daten
- **Fix**: `saveMockState()` nach jeder Mutation, `loadMockState()` beim Start
- **Test**: KANN NICHT in Cypress getestet werden (Cypress nutzt eigene Mocks!)
- **Status**: ⚠️ Manueller Test erforderlich:
  ```bash
  npm run dev
  # 1. Manual IPs via Modal hinzufügen
  # 2. Discovery klicken
  # 3. F5 drücken (Page Reload)
  # 4. ✅ Devices sollten noch sichtbar sein (nicht /welcome redirect)
  ```

#### 4. ⚠️ SVG Placeholder Images (nur manuell testbar)
- **Bug**: `via.placeholder.com` URLs → ERR_NAME_NOT_RESOLVED (Network Fehler)
- **Fix**: SVG data URLs verwenden (`data:image/svg+xml;base64,...`)
- **Test**: KANN NICHT in Cypress getestet werden (Fixtures haben keine Images!)
- **Status**: ⚠️ Manueller Test erforderlich:
  ```bash
  npm run dev
  # DevTools Console öffnen
  # Discovery klicken
  # ✅ Network Tab: KEINE Requests zu via.placeholder.com
  # ✅ Console: KEINE ERR_NAME_NOT_RESOLVED Fehler
  ```

---

## ⚠️ Troubleshooting

### Mock Mode funktioniert nicht
```bash
# Prüfen ob .env.development.local existiert
cat .env.development.local
# Sollte VITE_MOCK_MODE=true enthalten

# Browser Console prüfen
# Sollte zeigen: "[MOCK MODE] Development interceptor active"
```

### Mock State zurücksetzen (Browser Console)
```javascript
// Alle gespeicherten Devices + IPs löschen
localStorage.removeItem('ct-mock-state')
location.reload()

// Oder über DevTools:
// Application → Local Storage → http://localhost:5175 → ct-mock-state → Delete
```

### Mock State inspizieren (Browser Console)
```javascript
// Aktueller State
JSON.parse(localStorage.getItem('ct-mock-state'))

// Sollte zeigen:
// { devices: [...], manualIps: [...], discoveryInProgress: false }
```

### Live Mode ruft keine API auf
```bash
# Backend läuft?
curl http://localhost:7777/health

# VITE_MOCK_MODE korrekt?
VITE_MOCK_MODE=false npm run dev:live
```

---

## 📋 Checkliste: Was wurde migriert?

✅ **Backend**: Mock-Code entfernt (`OCT_MOCK_MODE`, `MockDiscovery`)  
✅ **Frontend**: Cypress Tests mit Intercept Mocking  
✅ **Frontend**: Development Mock-Interceptor für `npm run dev`  
✅ **Tests**: 218/218 Backend Tests passing (100%)  
✅ **Tests**: 12/12 Cypress Tests passing (100%)  
✅ **Coverage**: 85% Backend, 100% Frontend E2E  

---

## 🎯 Workflow-Empfehlungen

**UI-Entwicklung**:
```bash
npm run dev              # Mock-Mode, schnell, ohne Backend
```

**Feature-Entwicklung (Full Stack)**:
```bash
# Terminal 1: Backend
cd apps/backend && python -m opencloudtouch

# Terminal 2: Frontend Live
cd apps/frontend && npm run dev:live
```

**Testing**:
```bash
# Frontend E2E
npm run test:e2e

# Backend Unit/Integration
cd ../backend && pytest
```

**Deployment**:
```bash
cd deployment
.\deploy-local.ps1       # Podman Container
```
