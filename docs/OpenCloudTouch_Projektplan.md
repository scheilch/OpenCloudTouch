**OpenCloudTouch (OCT) ÔÇô Projekt- und Arbeitsplan**
> **⚠️ Historical Document**: This is the original project planning document. It contains references to the old project names "SoundTouchBridge (STB)" and "CloudTouch (CT)". The project has been rebranded to **OpenCloudTouch (OCT)**. For current documentation, see [README.md](../README.md).
_Stand: 2026-01-27 | Ziel: Bose SoundTouch Ger├ñte nach Cloud-Abschaltung weiter nutzbar machen (Radio, Presets, Multiroom, Volume) ÔÇô f├╝r Laien einfach, f├╝r Power-User erweiterbar._

# 1\. Kontext und Zielbild (konsolidiert)

Bose stellt Cloud-Funktionen f├╝r SoundTouch ein (u. a. integrierte Dienste wie TuneIn/Spotify in der SoundTouch-App und Cloud-gest├╝tzte Multiroom-Funktionen). Du besitzt SoundTouch 10, SoundTouch 30 sowie eine SoundTouch 300 Soundbar (Acoustimass 300 ist als Sub kein eigenst├ñndiger Player). Ziel ist eine eigenst├ñndige, Open-Source-f├ñhige L├Âsung ohne Home Assistant-Abh├ñngigkeit: ein einzelner Docker-Container (optional sp├ñter als Raspberry-Pi-Image), mit Web-UI ├ñhnlich der alten SoundTouch-App. Kernfunktionen f├╝r die erste Instanz: Preset-Taste am Ger├ñt dr├╝cken ÔåÆ definierter Radiosender startet ÔåÆ Sender/Track-Infos sind im Display und in der Web-UI sichtbar.

## 1.1 Muss-Kriterien (MVP)

*   Einfaches Setup: Ger├ñt ist bereits im WLAN; OCT findet Ger├ñte automatisch (ohne statische IPs) oder per manueller IP-Liste als Fallback.
*   Web-UI Seite 1: Radiosender suchen/ausw├ñhlen und einem Preset (1ÔÇô6) zuordnen.
*   Physische Preset-Taste am Ger├ñt funktioniert wieder ohne Bose-Cloud.
*   Now Playing (Sender/Track/Show) wird in der Web-UI angezeigt; Display-Anzeige auf dem Ger├ñt wird genutzt, soweit vom Stream/Metadaten unterst├╝tzt.
*   E2E Demo/Test: Station finden ÔåÆ Preset setzen ÔåÆ Preset-Taste per API simulieren ÔåÆ echtes Playback auf Ger├ñt verifizieren ÔåÆ /now\_playing verifizieren.

## 1.2 Soll-Kriterien (EPICs, sp├ñter)

*   Web-UI Seite 2: Multiroom ÔÇô Gruppen anzeigen, Ger├ñte zuordnen/abkoppeln (SoundTouch Zones).
*   Web-UI: Lautst├ñrke, Play/Pause, Source, Standby (lokale Steuerung).
*   Weitere Provider/Adapter: Spotify/Apple Music/Deezer oder Music Assistant (MA) als optionales Plugin.
*   Hilfe-Seite (Setup/Fehlerdiagnose, IP/Version remotehostusfinden, WLAN-Einrichtung).
*   Firmware-Seite: Firmware-Versionen anzeigen, Updates/Downgrades unterst├╝tzen (rechtlich sauber).

# 2\. Technische Grundlage und Quellen (nicht spekulativ)

## 2.1 Bose SoundTouch lokale Web API (WAPI)

SoundTouch Ger├ñte bieten eine lokale HTTP-Schnittstelle auf Port 8090 (GET/POST) sowie Notifications ├╝ber WebSocket (typisch Port 8080). Diese APIs sind in der 'SoundTouch Web API' Dokumentation beschrieben.

Wichtige Endpunkte/Mechanismen f├╝r OCT:

*   Presets setzen/lesen (z. B. storePreset) ÔÇô f├╝r das Re-Programmieren der 1ÔÇô6 Presets auf eine lokale URL (stationurl).
*   Key-Events (PRESET\_1 ÔÇª PRESET\_6) per API simulieren (press/release) ÔÇô f├╝r E2E Tests.
*   now\_playing abrufen ÔÇô zur Verifikation von Sender/Track/State und f├╝r UI-Anzeige.
*   WebSocket Notifications ÔÇô f├╝r Live-Updates ohne Polling.

## 2.2 ├ûffentliche Radiosender-Quelle ohne TuneIn-Abh├ñngigkeit: Radio Browser

F├╝r ein laienfreundliches MVP ist RadioBrowser.info eine praktikable, offene Quelle f├╝r Radiosender/Stream-URLs, inklusive Such- und Filterfunktionen, und einer klar dokumentierten ├Âffentlichen API.

## 2.3 Firmware-Repository-Ansatz (rechtlich vorsichtig)

Es gibt Community-Threads (z. B. Reddit), die auf Firmware-Sammlungen/Repos verweisen. F├╝r ein Open-Source-Projekt ist das Risiko hoch, propriet├ñre Firmware direkt im eigenen GitHub-Repo zu spiegeln. Empfehlung: OCT bietet eine Firmware-Seite, die (a) nur Metadaten/Checksums listet und (b) Firmware optional von einer URL herunterl├ñdt, oder (c) Nutzer l├ñdt Firmware-Datei lokal hoch. OCT speichert dann Hashes und f├╝hrt einen gef├╝hrten Update-Prozess aus.

## 2.4 Referenzen (f├╝r dieses Dokument)

Prim├ñre Quellen (Auswahl):

*   Bose SoundTouch Web API (PDF): https://assets.bosecreative.com/m/496577402d128874/original/SoundTouch-Web-API.pdf
*   Music Assistant API-Doku (Hinweis auf /api-docs): https://www.music-assistant.io/api/
*   Radio Browser API: https://api.radio-browser.info/
*   Reddit Firmware-Threads (Beispiele): https://www.reddit.com/r/bose/comments/1lb1uav/solved\_bose\_soundtouch\_firmware\_downgrade\_guide/ und https://www.reddit.com/r/bose/comments/d2zdb1/githubcombosefirmwarecedold/

# 3\. Produktkonzept: OCT als 'Ein Container ÔÇô eine Web-App'

## 3.1 Was sollte (vorerst) NICHT sichtbar sein (Vorschl├ñge)

Damit Laien nicht ├╝berfordert werden, sollten die folgenden Dinge im MVP nicht prominent sein, sondern als 'Erweitert' versteckt oder erst sp├ñter kommen:

*   Provider-/Adapter-Details (OAuth, Tokens, API Keys).
*   Technische Rohdaten (XML der SoundTouch API, Debug-Logs) ÔÇô nur in einem Diagnosebereich.
*   Netzwerkdetails (Ports, Multicast, etc.) ÔÇô nur 'Ger├ñte gefunden / nicht gefunden' mit kurzen Hilfetexten.
*   Firmware 'Downgrade' als 1-Klick ÔÇô erst sp├ñter, mit Warnungen und checksums; im MVP maximal Info + Upload/Download-Assistent.

## 3.2 UI-Seiten (deine Vorgaben, konkretisiert)

### Seite 1: Radio & Presets

*   Suchfeld (Name, Land, Tag/Genre), Ergebnisliste mit Play-Preview (optional), Stream-Qualit├ñt/Codec (soweit bekannt).
*   Preset-Zuordnung 1ÔÇô6 pro Ger├ñt oder 'auf alle Ger├ñte anwenden'.
*   Button: 'Preset schreiben' (persistiert mapping + programmiert storePreset auf Ger├ñt).
*   Now Playing Panel je Ger├ñt (Live-Update via WebSocket + Fallback Polling).

### Seite 2: Multi Room

*   Liste der Ger├ñte und aktueller Zone/Gruppe (Master/Slave).
*   Drag-and-drop oder Buttons: 'Zur Gruppe hinzuf├╝gen' / 'Abkoppeln'.
*   Anzeige, welches Ger├ñt Master ist, und Konflikt-/Fehlerbehandlung.

### Seite 3: Firmware

*   Ger├ñte-Firmware anzeigen (Version, Modell).
*   Optional: Firmware-Katalog (nur Metadaten/Hashes).
*   Gef├╝hrter Ablauf: Datei ausw├ñhlen oder URL angeben ÔåÆ Hash pr├╝fen ÔåÆ Update ansto├ƒen.
*   Explizite Warnung/Disclaimer (Garantie, Brick-Risiko).

# 4\. Technologien/Frameworks (bewusst gew├ñhlt)

## 4.1 Backend

*   Python 3.11+
*   FastAPI (HTTP API, statische Assets, OpenAPI f├╝r OCT selbst)
*   httpx (async HTTP), websockets oder websocket-client (SoundTouch WS)
*   zeroconf + async-upnp-client (Discovery; SSDP/UPnP; mDNS optional)
*   SQLite (Preset-Mappings, Device Registry, Cache)
*   uvicorn (ASGI)

## 4.2 Frontend

*   React (oder Preact) SPA
*   Vite Build
*   Einfaches, robustes UI: Preset-Kacheln, Station-Suche, Ger├ñteleiste

## 4.3 Packaging/Deployment

*   Ein Docker Image (Multi-arch: amd64 + arm64) ÔÇô wichtig f├╝r Raspberry Pi.
*   docker-compose Beispiel f├╝r Laien (mit --network host empfohlen, um Discovery zu vereinfachen).
*   Optional: sp├ñter 'RasPi Image' (Debian Lite + Docker + Autostart + mDNS 'device.local').

## 4.4 Streaming Provider (Adapter-Architektur)

MVP: RadioBrowser Adapter (offen, gut dokumentiert). TuneIn erst sp├ñter, wegen m├Âglicher Lizenz/ToS-Fragen. Music Assistant kann als optionaler Adapter integriert werden, da es einen offiziellen Python Client gibt (music-assistant-client).

# 5\. Architektur-Blueprint (komponentenweise)

## 5.1 High-Level

Browser UI
\-> OCT REST/WS API
\-> Device Layer (SoundTouch HTTP/WS, Discovery)
\-> Provider Layer (RadioBrowser, optional MA)
\-> Station Descriptor Service (/stations/preset/{n}.json)
\-> Stream Proxy (optional: HTTPS upstream -> HTTP local)
\-> Storage (SQLite)

## 5.2 Zentrale technische Idee f├╝r Preset-Tasten

OCT programmiert die SoundTouch Presets so, dass sie auf eine lokale HTTP-URL zeigen (stationurl). Beim Dr├╝cken der physischen Preset-Taste l├ñdt das Ger├ñt diese URL ab und startet das Streaming. Damit wird der Tastendruck wieder nutzbar, ohne dass OCT den Tastendruck selbst abfangen muss.

## 5.3 Contract der OCT HTTP API (intern + f├╝r UI)

*   GET /api/devices -> gefundene Ger├ñte (id, name, model, ip, capabilities)
*   GET /api/radio/search?q=... -> Stationen (Provider abstrahiert)
*   POST /api/presets/apply -> mapping schreiben + storePreset an Ger├ñte
*   GET /stations/preset/{n}.json -> SoundTouch Descriptor (Name + streamUrl)
*   GET /api/nowplaying/{device\_id} -> Aggregation aus /now\_playing
*   WS /api/events -> Live-Updates (NowPlaying, device online/offline)

# 6\. Teststrategie (Unit, Integration, E2E, Demo)

## 6.1 Unit Tests (schnell, deterministisch)

*   XML Rendering f├╝r storePreset und key press/release
*   Station Descriptor JSON Rendering
*   Provider Adapter Parsing (RadioBrowser responses)
*   DB Layer (Mappings, migrations)

## 6.2 Integration Tests (mocked)

*   Mock SoundTouch HTTP server (endpoints: /info, /storePreset, /now\_playing, /key)
*   Mock RadioBrowser API server (Search responses, station detail)
*   Proxy tests (HTTPS upstream -> HTTP passthrough, content-type/stream)

## 6.3 E2E Tests mit echten Ger├ñten (deine Verifikation)

E2E Testfall (auch als Demo nutzbar):

1.  OCT startet und findet SoundTouch Ger├ñte via Discovery.
2.  OCT sucht Station (z. B. 'Absolut Relax') via RadioBrowser API.
3.  OCT setzt Preset 3 auf dem ausgew├ñhlten Ger├ñt (storePreset).
4.  OCT simuliert PRESET\_3 per SoundTouch API (press + release).
5.  OCT wartet auf Playback-Start (WebSocket event oder polling now\_playing).
6.  OCT best├ñtigt: /now\_playing enth├ñlt stationName und state=PLAY\_STATE (oder ├ñquivalent).
7.  Optional: UI zeigt Now Playing; Nutzer schaut auf physisches Display zur Best├ñtigung.

## 6.4 Nicht-Ziele im MVP (damit Tests nicht explodieren)

*   Firmware flashen/downgraden automatisieren ÔÇô nur Info/Upload/Hashcheck im MVP.
*   Spotify/Apple Music/Deezer ÔÇô sp├ñter als Adapter-EPIC.

# 7\. Iterationsplan (agentenfreundlich, kleinteilig)

Prinzip: Jede Iteration liefert ein lauff├ñhiges Inkrement + 1 gezielte Refactoring-Ma├ƒnahme, die Komplexit├ñt reduziert und Open-Source/Laien-Usability st├ñrkt. Kein Overengineering.

## Iteration 0 ÔÇô Repo/Build/Run

*   Repo anlegen: backend/, frontend/, docs/, e2e/
*   Dockerfile multi-stage (Backend + Frontend build)
*   docker-compose.dev.yml (host networking)
*   Healthcheck endpoint /health

Refactoring nach Iteration: Standardisierte Konfig (ENV + config.yaml) + zentrale Validierung (pydantic).

## Iteration 1 ÔÇô SoundTouch Discovery + Device Inventory

*   SSDP Discovery implementieren (UPnP), Fallback manuelle IP-Liste
*   GET /api/devices
*   Device Detail: /info + capabilities cachen

Refactoring: Discovery und SoundTouch-Client strikt trennen (interface + 1 Implementierung).

## Iteration 2 ÔÇô RadioBrowser Adapter + Stationsuche

*   RadioBrowser API Client (Search, Station Detail)
*   GET /api/radio/search?q=...&limit=...
*   UI: Suchfeld + Ergebnisliste

Refactoring: Provider-Adapter-Interface einf├╝hren (search(), resolve\_stream()).

## Iteration 3 ÔÇô Preset Mapping + storePreset

*   SQLite Schema: devices, presets, mappings
*   POST /api/presets/apply (Preset 1ÔÇô6)
*   Endpoint /stations/preset/{n}.json (Descriptor aus Mapping)

Refactoring: Mapping-Logik als Domain-Service (keine DB/HTTP im Core).

## Iteration 4 ÔÇô Playback Demo/E2E (Key press + NowPlaying)

*   SoundTouch /key press+release PRESET\_n
*   NowPlaying Polling + minimaler WS Listener (optional)
*   E2E Script 'demo\_e2e.py' (CLI)

Refactoring: Eventing-Schicht (Polling/WS) hinter gemeinsamer 'NowPlayingFeed' API verstecken.

## Iteration 5 ÔÇô UI Preset-UX (Killerfeature)

*   Preset-Kacheln (1ÔÇô6), Zuweisen per Klick
*   Apply-Button mit Fortschritt und Fehlerhinweisen
*   NowPlaying Panel

Refactoring: UI State Management vereinfachen (ein zentraler API client + typed DTOs).

## Iteration 6 ÔÇô Multiroom Seite (EPIC 1, minimal)

*   Zonen anzeigen (Master/Slaves), simple Zuordnung/Abkoppeln
*   UI: Ger├ñte + Gruppe

Refactoring: SoundTouch-Features als Module (presets, zones, volume) mit klaren Grenzen.

## Iteration 7 ÔÇô Firmware Seite (EPIC 2, minimal & sicher)

*   Firmware-Version anzeigen
*   Firmware Upload + Hashcheck (keine automatische Repo-Spiegelung im MVP)
*   Dokumentation und Warnungen

Refactoring: 'Dangerous operations' isolieren (Firmware) + Feature Flag.
---

# 10. Post-MVP: Short & Long Term Improvements

**Stand**: 2026-02-03 (nach Cleanup Iteration 2.5)

## 10.1 Short-Term (Q1 2026) - Stabilität & Wartbarkeit

**10.1.1 Security: Vite 7.x Upgrade** (Breaking Changes!)
- **Problem**: 5 moderate vulnerabilities in esbuild (dev-only, GHSA-67mh-4wv8-2f99)
- **Fix**: Upgrade zu Vite 7.x (erfordert Breaking Changes in vite.config.js)
- **Impact**: Nur Dev-Server betroffen, nicht Prod-Builds
- **Priority**: MEDIUM (keine kritischen Prod-Risiken)
- **Estimated Effort**: 2-4 Stunden (inkl. Config-Migration + Tests)

**10.1.2 Dependencies: React 19 Migration Planning**
- **Current**: React 18.2.0 (stabil)
- **Goal**: React 19 stable release abwarten, dann Migration planen
- **Impact**: Performance-Verbesserungen, neue Features (Actions, use() hook)
- **Priority**: LOW (React 18.2 ist LTS bis 2025+)
- **Estimated Effort**: 4-6 Stunden (Codebase-Audit + Migration)

**10.1.3 Technical Debt: GitHub Issues aus TODO Comments**
- **Problem**: 5 TODO-Comments in RadioPresets.jsx (Phase 3 TODOs)
  - Backend preset endpoints fehlen noch
  - handleAssignClick, handleStationSelect, handlePlayPreset, handleClearPreset
- **Action**: GitHub Issues erstellen für jeden TODO
- **Priority**: HIGH (Feature ist incomplete)
- **Estimated Effort**: 1-2 Stunden pro TODO (Backend + Frontend)

**10.1.4 Code Quality: EmptyState Component Refactoring**
- **Current**: EmptyState.jsx ist 196 Zeilen (nahe an 200-Zeilen-Limit)
- **Goal**: Extrahiere ManualIPModal in separates Component
- **Impact**: Bessere Wartbarkeit, Testbarkeit
- **Priority**: LOW (optional, nur wenn >200 Zeilen)
- **Estimated Effort**: 30 Minuten

## 10.2 Long-Term (Q2 2026) - Feature EPICs

**10.2.1 React 19 Stable Migration**
- Komplette Codebase-Audit (Hooks, Actions, Suspense)
- Breaking Changes dokumentieren
- Migration durchführen
- E2E Tests validieren
- **Estimated Effort**: 8-12 Stunden

**10.2.2 Vitest 4.x Evaluation**
- Breaking Changes in Config API prüfen
- Specpattern Migration
- Performance-Verbesserungen evaluieren
- **Estimated Effort**: 2-3 Stunden

**10.2.3 Cypress 15.x Upgrade**
- SpecPattern Changes reviewen
- Config Migration
- E2E Tests validieren
- **Estimated Effort**: 2-3 Stunden

**10.2.4 TypeScript Migration (Optional)**
- Bessere Type Safety (aktuell nur JSDoc)
- Vite + React 18/19 volle TS-Unterstützung
- Schrittweise Migration (Datei für Datei)
- **Estimated Effort**: 20-40 Stunden (gesamte Codebase)

## 10.3 Roadmap Integration

**Integration in Iteration 8-10**:

**Iteration 8 - Security & Dependencies Hardening (Q1 2026)**
- Vite 7.x Upgrade (Breaking Changes)
- Dependency Audit & Updates
- Security Scan mit npm audit fix
- Refactoring: Dependency Injection für besser testbare Komponenten

**Iteration 9 - TODO Cleanup & Feature Completion (Q1 2026)**
- Backend Preset Endpoints implementieren (Phase 3)
- Frontend RadioPresets.jsx vervollständigen
- GitHub Issues für verbleibende TODOs
- Refactoring: Extract ManualIPModal aus EmptyState

**Iteration 10 - React 19 Migration (Q2 2026)**
- React 19 stable abwarten
- Breaking Changes evaluieren
- Schrittweise Migration
- E2E Tests + Cypress 15.x Upgrade
- Refactoring: Modernisierung mit React 19 Patterns (Actions, use() Hook)
# 8\. Agent Prompt (Codex/├ñhnlich) ÔÇô vollst├ñndig, reaktiv, end-to-end

Du bist ein Senior-Software-Engineer + QA-Lead + Release-Engineer in einer Person.
Du entwickelst ein Open-Source-Projekt namens 'OpenCloudTouch (OCT)' als EIN dockerisiertes Produkt
(kein Home Assistant erforderlich). Zielgruppe: nicht versierte Nutzer (Raspberry Pi + Docker + Web-UI).
Du arbeitest iterativ, testgetrieben und lieferst nach jeder Iteration ein lauff├ñhiges Inkrement.
Kernziele (MVP):
\- Ger├ñte sind bereits im WLAN.
\- OCT findet Bose SoundTouch Ger├ñte automatisch (SSDP/UPnP), ohne feste IPs, mit manuellem Fallback.
\- Web-UI: Radiosender suchen, ausw├ñhlen, Preset 1ÔÇô6 zuordnen und auf Ger├ñte schreiben.
\- Physische Preset-Taste am Ger├ñt startet Sender (ohne Cloud).
\- Now Playing wird angezeigt (UI + /now\_playing Verifikation).
\- E2E Demo/Test: Station suchen -> Preset setzen -> PRESET\_n via API simulieren -> Playback/now\_playing verifizieren.
Technische Constraints:
\- Backend: Python 3.11+, FastAPI, httpx (async), SQLite.
\- Discovery: SSDP/UPnP (zeroconf optional).
\- SoundTouch: lokale HTTP API (Port 8090) + WebSocket Notifications (Port 8080).
\- Provider MVP: RadioBrowser API (offen). TuneIn/Spotify erst sp├ñter als Adapter-EPICs.
\- Packaging: Ein Docker Image (multi-arch amd64/arm64). Host networking empfohlen.
\- Keine propriet├ñre Firmware im Repo einchecken. Firmware nur via URL/Upload mit Hashes.
Arbeitsweise:
\- Arbeite in kleinen Iterationen (siehe Iterationsplan in docs/OpenCloudTouch_Projektplan.md)
\- Nach jeder Iteration:
1) Alle Tests laufen lassen (unit+integration).
2) Einen E2E Demo-Run beschreiben (und ein Script bereitstellen), der auf echten Ger├ñten funktionieren kann.
3) Eine gezielte Refactoring-Ma├ƒnahme durchf├╝hren, die Komplexit├ñt reduziert und Open-Source/Laien-Usability verbessert.
\- Kein Overengineering: Refactoring nur, wenn es Wartbarkeit/Usability/Erweiterbarkeit messbar verbessert.
Definition of Done pro Iteration:
\- Lauff├ñhig via docker compose up.
\- README aktualisiert mit konkreten Schritten (Copy/Paste) und Troubleshooting.
\- Tests gr├╝n, Coverage sinnvoll (nicht dogmatisch).
\- Logging/Fehlerausgaben nutzerverst├ñndlich (keine Stacktraces im UI).
Reaktivit├ñt:
\- Wenn Anforderungen/Designentscheidungen im Chat ge├ñndert werden, aktualisiere PLAN.md + Architektur und passe die n├ñchsten Iterationen an.
\- Stelle keine R├╝ckfragen, wenn du mit sinnvollen Defaults fortfahren kannst; dokumentiere Annahmen.
Lieferformat:
\- Gib am Ende jeder Iteration die ge├ñnderten Dateien vollst├ñndig aus oder erstelle ein ZIP mit dem kompletten Projekt.

# 9\. Agent-Setup & Mensch-Workflow (verbindlich)

## 9.1 Ziel dieses Abschnitts

Dieser Abschnitt beschreibt verbindlich, wie ein LLM-Agent (empfohlen: Claude Sonnet 4.5) f├╝r die Entwicklung von OpenCloudTouch eingesetzt wird und welche konkreten Schritte du als Mensch durchf├╝hren musst, um mit GitHub und VS Code effizient weiterzuarbeiten.

## 9.2 Rollenverteilung: Mensch vs. Agent

*   Der Mensch trifft strategische Entscheidungen, gibt Freigaben und f├╝hrt reale Verifikationen (E2E auf echten Ger├ñten) durch.
*   Der Agent ├╝bernimmt Architektur-Feinarbeit, Implementierung, Tests, CI/CD, Refactorings und Dokumentation.
*   Der Agent arbeitet iterativ und reagiert auf Feedback, Testergebnisse und ge├ñnderte Anforderungen.

## 9.3 Empfohlenes Modell & Arbeitsmodus

Empfohlenes Prim├ñrmodell: Claude Sonnet 4.5.
Arbeitsmodus: Langer, konsistenter Kontext, iterative Entwicklung, testgetrieben.

## 9.4 Vorbereitung: Was du als Mensch einmalig tun musst

*   GitHub Account bereitstellen (pers├Ânlich oder Organisation).
*   Neues ├Âffentliches Repository anlegen, z. B. 'opencloudtouch'.
*   Lizenz festlegen (empfohlen: Apache-2.0 oder MIT).
*   README.md minimal anlegen (Projektname + Kurzbeschreibung reicht).
*   GitHub Container Registry (ghcr.io) ist automatisch verf├╝gbar ÔÇô kein Extra-Setup n├Âtig.

## 9.5 Lokales Setup (VS Code)

*   VS Code installieren.
*   GitHub Repository lokal klonen.
*   Docker & Docker Compose installieren.
*   VS Code Extensions (empfohlen): Docker, Python, YAML, GitHub Actions.

## 9.6 Arbeitsweise mit dem Agenten (konkret)

Du arbeitest dialogbasiert mit dem Agenten. F├╝r jede Iteration:
1) Du gibst dem Agenten den aktuellen Stand (Repo-Status, letzte Iteration, Feedback).
2) Du gibst frei, welche Iteration umgesetzt werden soll (z. B. 'Iteration 0: Repo + CI/CD').
3) Der Agent liefert Code, Tests, CI/CD und Doku.
4) Du pr├╝fst lokal (docker compose up) und ggf. auf echten Ger├ñten.
5) Du gibst Feedback oder Freigabe.
6) Erst nach Freigabe commitest und pushst du nach GitHub.

## 9.7 Commit- und Review-Regeln

*   Der Agent schreibt Code, aber du f├╝hrst die Commits aus (lokal).
*   Ein Commit pro Iteration oder logisch abgeschlossener Teil.
*   Commit Message Schema: 'Iteration X: <kurze Beschreibung>'.
*   CI muss gr├╝n sein, bevor gemerged oder released wird.

## 9.8 Umgang mit CI/CD

Der Agent erstellt und pflegt GitHub Actions Workflows:
\- Build (Backend + Frontend)
\- Tests (unit/integration)
\- Docker Buildx (amd64 + arm64)
\- Push nach ghcr.io bei Tags oder main
Du als Mensch:
\- Beobachtest die Pipeline-Ausgaben.
\- Meldest dem Agenten konkrete Fehlerlogs, falls Builds fehlschlagen.

## 9.9 Releases & Testing durch den Menschen

*   Lokaler Test: docker compose up ÔåÆ Web-UI aufrufen ÔåÆ Preset setzen.
*   E2E Test: Preset-Taste am Ger├ñt dr├╝cken und Audio/Display pr├╝fen.
*   Bei Erfolg: Git Tag setzen (z. B. v0.1.0) und pushen.
*   CI/CD baut Release-Image und pusht nach ghcr.io.

## 9.10 Goldene Regeln f├╝r die Zusammenarbeit

*   Der Agent implementiert ÔÇô du entscheidest.
*   Keine 'stillen' Architekturwechsel ohne explizite Zustimmung.
*   Refactoring nur nach Iterationsende und mit klarer Begr├╝ndung.
*   Immer im Blick behalten: Laienfreundlichkeit, ein Container, Web-UI, Open Source.
