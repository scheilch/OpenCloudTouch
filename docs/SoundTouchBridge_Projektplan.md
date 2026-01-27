**SoundTouchBridge (STB) – Projekt- und Arbeitsplan**

_Stand: 2026-01-27 | Ziel: Bose SoundTouch Geräte nach Cloud-Abschaltung weiter nutzbar machen (Radio, Presets, Multiroom, Volume) – für Laien einfach, für Power-User erweiterbar._

# 1\. Kontext und Zielbild (konsolidiert)

Bose stellt Cloud-Funktionen für SoundTouch ein (u. a. integrierte Dienste wie TuneIn/Spotify in der SoundTouch-App und Cloud-gestützte Multiroom-Funktionen). Du besitzt SoundTouch 10, SoundTouch 30 sowie eine SoundTouch 300 Soundbar (Acoustimass 300 ist als Sub kein eigenständiger Player). Ziel ist eine eigenständige, Open-Source-fähige Lösung ohne Home Assistant-Abhängigkeit: ein einzelner Docker-Container (optional später als Raspberry-Pi-Image), mit Web-UI ähnlich der alten SoundTouch-App. Kernfunktionen für die erste Instanz: Preset-Taste am Gerät drücken → definierter Radiosender startet → Sender/Track-Infos sind im Display und in der Web-UI sichtbar.

## 1.1 Muss-Kriterien (MVP)

*   Einfaches Setup: Gerät ist bereits im WLAN; STB findet Geräte automatisch (ohne statische IPs) oder per manueller IP-Liste als Fallback.
*   Web-UI Seite 1: Radiosender suchen/auswählen und einem Preset (1–6) zuordnen.
*   Physische Preset-Taste am Gerät funktioniert wieder ohne Bose-Cloud.
*   Now Playing (Sender/Track/Show) wird in der Web-UI angezeigt; Display-Anzeige auf dem Gerät wird genutzt, soweit vom Stream/Metadaten unterstützt.
*   E2E Demo/Test: Station finden → Preset setzen → Preset-Taste per API simulieren → echtes Playback auf Gerät verifizieren → /now\_playing verifizieren.

## 1.2 Soll-Kriterien (EPICs, später)

*   Web-UI Seite 2: Multiroom – Gruppen anzeigen, Geräte zuordnen/abkoppeln (SoundTouch Zones).
*   Web-UI: Lautstärke, Play/Pause, Source, Standby (lokale Steuerung).
*   Weitere Provider/Adapter: Spotify/Apple Music/Deezer oder Music Assistant (MA) als optionales Plugin.
*   Hilfe-Seite (Setup/Fehlerdiagnose, IP/Version remotehostusfinden, WLAN-Einrichtung).
*   Firmware-Seite: Firmware-Versionen anzeigen, Updates/Downgrades unterstützen (rechtlich sauber).

# 2\. Technische Grundlage und Quellen (nicht spekulativ)

## 2.1 Bose SoundTouch lokale Web API (WAPI)

SoundTouch Geräte bieten eine lokale HTTP-Schnittstelle auf Port 8090 (GET/POST) sowie Notifications über WebSocket (typisch Port 8080). Diese APIs sind in der 'SoundTouch Web API' Dokumentation beschrieben.

Wichtige Endpunkte/Mechanismen für STB:

*   Presets setzen/lesen (z. B. storePreset) – für das Re-Programmieren der 1–6 Presets auf eine lokale URL (stationurl).
*   Key-Events (PRESET\_1 … PRESET\_6) per API simulieren (press/release) – für E2E Tests.
*   now\_playing abrufen – zur Verifikation von Sender/Track/State und für UI-Anzeige.
*   WebSocket Notifications – für Live-Updates ohne Polling.

## 2.2 Öffentliche Radiosender-Quelle ohne TuneIn-Abhängigkeit: Radio Browser

Für ein laienfreundliches MVP ist RadioBrowser.info eine praktikable, offene Quelle für Radiosender/Stream-URLs, inklusive Such- und Filterfunktionen, und einer klar dokumentierten öffentlichen API.

## 2.3 Firmware-Repository-Ansatz (rechtlich vorsichtig)

Es gibt Community-Threads (z. B. Reddit), die auf Firmware-Sammlungen/Repos verweisen. Für ein Open-Source-Projekt ist das Risiko hoch, proprietäre Firmware direkt im eigenen GitHub-Repo zu spiegeln. Empfehlung: STB bietet eine Firmware-Seite, die (a) nur Metadaten/Checksums listet und (b) Firmware optional von einer URL herunterlädt, oder (c) Nutzer lädt Firmware-Datei lokal hoch. STB speichert dann Hashes und führt einen geführten Update-Prozess aus.

## 2.4 Referenzen (für dieses Dokument)

Primäre Quellen (Auswahl):

*   Bose SoundTouch Web API (PDF): https://assets.bosecreative.com/m/496577402d128874/original/SoundTouch-Web-API.pdf
*   Music Assistant API-Doku (Hinweis auf /api-docs): https://www.music-assistant.io/api/
*   Radio Browser API: https://api.radio-browser.info/
*   Reddit Firmware-Threads (Beispiele): https://www.reddit.com/r/bose/comments/1lb1uav/solved\_bose\_soundtouch\_firmware\_downgrade\_guide/ und https://www.reddit.com/r/bose/comments/d2zdb1/githubcombosefirmwarecedold/

# 3\. Produktkonzept: STB als 'Ein Container – eine Web-App'

## 3.1 Was sollte (vorerst) NICHT sichtbar sein (Vorschläge)

Damit Laien nicht überfordert werden, sollten die folgenden Dinge im MVP nicht prominent sein, sondern als 'Erweitert' versteckt oder erst später kommen:

*   Provider-/Adapter-Details (OAuth, Tokens, API Keys).
*   Technische Rohdaten (XML der SoundTouch API, Debug-Logs) – nur in einem Diagnosebereich.
*   Netzwerkdetails (Ports, Multicast, etc.) – nur 'Geräte gefunden / nicht gefunden' mit kurzen Hilfetexten.
*   Firmware 'Downgrade' als 1-Klick – erst später, mit Warnungen und checksums; im MVP maximal Info + Upload/Download-Assistent.

## 3.2 UI-Seiten (deine Vorgaben, konkretisiert)

### Seite 1: Radio & Presets

*   Suchfeld (Name, Land, Tag/Genre), Ergebnisliste mit Play-Preview (optional), Stream-Qualität/Codec (soweit bekannt).
*   Preset-Zuordnung 1–6 pro Gerät oder 'auf alle Geräte anwenden'.
*   Button: 'Preset schreiben' (persistiert mapping + programmiert storePreset auf Gerät).
*   Now Playing Panel je Gerät (Live-Update via WebSocket + Fallback Polling).

### Seite 2: Multi Room

*   Liste der Geräte und aktueller Zone/Gruppe (Master/Slave).
*   Drag-and-drop oder Buttons: 'Zur Gruppe hinzufügen' / 'Abkoppeln'.
*   Anzeige, welches Gerät Master ist, und Konflikt-/Fehlerbehandlung.

### Seite 3: Firmware

*   Geräte-Firmware anzeigen (Version, Modell).
*   Optional: Firmware-Katalog (nur Metadaten/Hashes).
*   Geführter Ablauf: Datei auswählen oder URL angeben → Hash prüfen → Update anstoßen.
*   Explizite Warnung/Disclaimer (Garantie, Brick-Risiko).

# 4\. Technologien/Frameworks (bewusst gewählt)

## 4.1 Backend

*   Python 3.11+
*   FastAPI (HTTP API, statische Assets, OpenAPI für STB selbst)
*   httpx (async HTTP), websockets oder websocket-client (SoundTouch WS)
*   zeroconf + async-upnp-client (Discovery; SSDP/UPnP; mDNS optional)
*   SQLite (Preset-Mappings, Device Registry, Cache)
*   uvicorn (ASGI)

## 4.2 Frontend

*   React (oder Preact) SPA
*   Vite Build
*   Einfaches, robustes UI: Preset-Kacheln, Station-Suche, Geräteleiste

## 4.3 Packaging/Deployment

*   Ein Docker Image (Multi-arch: amd64 + arm64) – wichtig für Raspberry Pi.
*   docker-compose Beispiel für Laien (mit --network host empfohlen, um Discovery zu vereinfachen).
*   Optional: später 'RasPi Image' (Debian Lite + Docker + Autostart + mDNS 'device.local').

## 4.4 Streaming Provider (Adapter-Architektur)

MVP: RadioBrowser Adapter (offen, gut dokumentiert). TuneIn erst später, wegen möglicher Lizenz/ToS-Fragen. Music Assistant kann als optionaler Adapter integriert werden, da es einen offiziellen Python Client gibt (music-assistant-client).

# 5\. Architektur-Blueprint (komponentenweise)

## 5.1 High-Level

Browser UI
\-> STB REST/WS API
\-> Device Layer (SoundTouch HTTP/WS, Discovery)
\-> Provider Layer (RadioBrowser, optional MA)
\-> Station Descriptor Service (/stations/preset/{n}.json)
\-> Stream Proxy (optional: HTTPS upstream -> HTTP local)
\-> Storage (SQLite)

## 5.2 Zentrale technische Idee für Preset-Tasten

STB programmiert die SoundTouch Presets so, dass sie auf eine lokale HTTP-URL zeigen (stationurl). Beim Drücken der physischen Preset-Taste lädt das Gerät diese URL ab und startet das Streaming. Damit wird der Tastendruck wieder nutzbar, ohne dass STB den Tastendruck selbst abfangen muss.

## 5.3 Contract der STB HTTP API (intern + für UI)

*   GET /api/devices -> gefundene Geräte (id, name, model, ip, capabilities)
*   GET /api/radio/search?q=... -> Stationen (Provider abstrahiert)
*   POST /api/presets/apply -> mapping schreiben + storePreset an Geräte
*   GET /stations/preset/{n}.json -> SoundTouch Descriptor (Name + streamUrl)
*   GET /api/nowplaying/{device\_id} -> Aggregation aus /now\_playing
*   WS /api/events -> Live-Updates (NowPlaying, device online/offline)

# 6\. Teststrategie (Unit, Integration, E2E, Demo)

## 6.1 Unit Tests (schnell, deterministisch)

*   XML Rendering für storePreset und key press/release
*   Station Descriptor JSON Rendering
*   Provider Adapter Parsing (RadioBrowser responses)
*   DB Layer (Mappings, migrations)

## 6.2 Integration Tests (mocked)

*   Mock SoundTouch HTTP server (endpoints: /info, /storePreset, /now\_playing, /key)
*   Mock RadioBrowser API server (Search responses, station detail)
*   Proxy tests (HTTPS upstream -> HTTP passthrough, content-type/stream)

## 6.3 E2E Tests mit echten Geräten (deine Verifikation)

E2E Testfall (auch als Demo nutzbar):

1.  STB startet und findet SoundTouch Geräte via Discovery.
2.  STB sucht Station (z. B. 'Absolut Relax') via RadioBrowser API.
3.  STB setzt Preset 3 auf dem ausgewählten Gerät (storePreset).
4.  STB simuliert PRESET\_3 per SoundTouch API (press + release).
5.  STB wartet auf Playback-Start (WebSocket event oder polling now\_playing).
6.  STB bestätigt: /now\_playing enthält stationName und state=PLAY\_STATE (oder äquivalent).
7.  Optional: UI zeigt Now Playing; Nutzer schaut auf physisches Display zur Bestätigung.

## 6.4 Nicht-Ziele im MVP (damit Tests nicht explodieren)

*   Firmware flashen/downgraden automatisieren – nur Info/Upload/Hashcheck im MVP.
*   Spotify/Apple Music/Deezer – später als Adapter-EPIC.

# 7\. Iterationsplan (agentenfreundlich, kleinteilig)

Prinzip: Jede Iteration liefert ein lauffähiges Inkrement + 1 gezielte Refactoring-Maßnahme, die Komplexität reduziert und Open-Source/Laien-Usability stärkt. Kein Overengineering.

## Iteration 0 – Repo/Build/Run

*   Repo anlegen: backend/, frontend/, docs/, e2e/
*   Dockerfile multi-stage (Backend + Frontend build)
*   docker-compose.dev.yml (host networking)
*   Healthcheck endpoint /health

Refactoring nach Iteration: Standardisierte Konfig (ENV + config.yaml) + zentrale Validierung (pydantic).

## Iteration 1 – SoundTouch Discovery + Device Inventory

*   SSDP Discovery implementieren (UPnP), Fallback manuelle IP-Liste
*   GET /api/devices
*   Device Detail: /info + capabilities cachen

Refactoring: Discovery und SoundTouch-Client strikt trennen (interface + 1 Implementierung).

## Iteration 2 – RadioBrowser Adapter + Stationsuche

*   RadioBrowser API Client (Search, Station Detail)
*   GET /api/radio/search?q=...&limit=...
*   UI: Suchfeld + Ergebnisliste

Refactoring: Provider-Adapter-Interface einführen (search(), resolve\_stream()).

## Iteration 3 – Preset Mapping + storePreset

*   SQLite Schema: devices, presets, mappings
*   POST /api/presets/apply (Preset 1–6)
*   Endpoint /stations/preset/{n}.json (Descriptor aus Mapping)

Refactoring: Mapping-Logik als Domain-Service (keine DB/HTTP im Core).

## Iteration 4 – Playback Demo/E2E (Key press + NowPlaying)

*   SoundTouch /key press+release PRESET\_n
*   NowPlaying Polling + minimaler WS Listener (optional)
*   E2E Script 'demo\_e2e.py' (CLI)

Refactoring: Eventing-Schicht (Polling/WS) hinter gemeinsamer 'NowPlayingFeed' API verstecken.

## Iteration 5 – UI Preset-UX (Killerfeature)

*   Preset-Kacheln (1–6), Zuweisen per Klick
*   Apply-Button mit Fortschritt und Fehlerhinweisen
*   NowPlaying Panel

Refactoring: UI State Management vereinfachen (ein zentraler API client + typed DTOs).

## Iteration 6 – Multiroom Seite (EPIC 1, minimal)

*   Zonen anzeigen (Master/Slaves), simple Zuordnung/Abkoppeln
*   UI: Geräte + Gruppe

Refactoring: SoundTouch-Features als Module (presets, zones, volume) mit klaren Grenzen.

## Iteration 7 – Firmware Seite (EPIC 2, minimal & sicher)

*   Firmware-Version anzeigen
*   Firmware Upload + Hashcheck (keine automatische Repo-Spiegelung im MVP)
*   Dokumentation und Warnungen

Refactoring: 'Dangerous operations' isolieren (Firmware) + Feature Flag.

# 8\. Agent Prompt (Codex/ähnlich) – vollständig, reaktiv, end-to-end

Du bist ein Senior-Software-Engineer + QA-Lead + Release-Engineer in einer Person.
Du entwickelst ein Open-Source-Projekt namens 'SoundTouchBridge (STB)' als EIN dockerisiertes Produkt
(kein Home Assistant erforderlich). Zielgruppe: nicht versierte Nutzer (Raspberry Pi + Docker + Web-UI).
Du arbeitest iterativ, testgetrieben und lieferst nach jeder Iteration ein lauffähiges Inkrement.
Kernziele (MVP):
\- Geräte sind bereits im WLAN.
\- STB findet Bose SoundTouch Geräte automatisch (SSDP/UPnP), ohne feste IPs, mit manuellem Fallback.
\- Web-UI: Radiosender suchen, auswählen, Preset 1–6 zuordnen und auf Geräte schreiben.
\- Physische Preset-Taste am Gerät startet Sender (ohne Cloud).
\- Now Playing wird angezeigt (UI + /now\_playing Verifikation).
\- E2E Demo/Test: Station suchen -> Preset setzen -> PRESET\_n via API simulieren -> Playback/now\_playing verifizieren.
Technische Constraints:
\- Backend: Python 3.11+, FastAPI, httpx (async), SQLite.
\- Discovery: SSDP/UPnP (zeroconf optional).
\- SoundTouch: lokale HTTP API (Port 8090) + WebSocket Notifications (Port 8080).
\- Provider MVP: RadioBrowser API (offen). TuneIn/Spotify erst später als Adapter-EPICs.
\- Packaging: Ein Docker Image (multi-arch amd64/arm64). Host networking empfohlen.
\- Keine proprietäre Firmware im Repo einchecken. Firmware nur via URL/Upload mit Hashes.
Arbeitsweise:
\- Arbeite in kleinen Iterationen (siehe Iterationsplan in docs/SoundTouchBridge_Projektplan.md)
\- Nach jeder Iteration:
1) Alle Tests laufen lassen (unit+integration).
2) Einen E2E Demo-Run beschreiben (und ein Script bereitstellen), der auf echten Geräten funktionieren kann.
3) Eine gezielte Refactoring-Maßnahme durchführen, die Komplexität reduziert und Open-Source/Laien-Usability verbessert.
\- Kein Overengineering: Refactoring nur, wenn es Wartbarkeit/Usability/Erweiterbarkeit messbar verbessert.
Definition of Done pro Iteration:
\- Lauffähig via docker compose up.
\- README aktualisiert mit konkreten Schritten (Copy/Paste) und Troubleshooting.
\- Tests grün, Coverage sinnvoll (nicht dogmatisch).
\- Logging/Fehlerausgaben nutzerverständlich (keine Stacktraces im UI).
Reaktivität:
\- Wenn Anforderungen/Designentscheidungen im Chat geändert werden, aktualisiere PLAN.md + Architektur und passe die nächsten Iterationen an.
\- Stelle keine Rückfragen, wenn du mit sinnvollen Defaults fortfahren kannst; dokumentiere Annahmen.
Lieferformat:
\- Gib am Ende jeder Iteration die geänderten Dateien vollständig aus oder erstelle ein ZIP mit dem kompletten Projekt.

# 9\. Agent-Setup & Mensch-Workflow (verbindlich)

## 9.1 Ziel dieses Abschnitts

Dieser Abschnitt beschreibt verbindlich, wie ein LLM-Agent (empfohlen: Claude Sonnet 4.5) für die Entwicklung von SoundTouchBridge eingesetzt wird und welche konkreten Schritte du als Mensch durchführen musst, um mit GitHub und VS Code effizient weiterzuarbeiten.

## 9.2 Rollenverteilung: Mensch vs. Agent

*   Der Mensch trifft strategische Entscheidungen, gibt Freigaben und führt reale Verifikationen (E2E auf echten Geräten) durch.
*   Der Agent übernimmt Architektur-Feinarbeit, Implementierung, Tests, CI/CD, Refactorings und Dokumentation.
*   Der Agent arbeitet iterativ und reagiert auf Feedback, Testergebnisse und geänderte Anforderungen.

## 9.3 Empfohlenes Modell & Arbeitsmodus

Empfohlenes Primärmodell: Claude Sonnet 4.5.
Arbeitsmodus: Langer, konsistenter Kontext, iterative Entwicklung, testgetrieben.

## 9.4 Vorbereitung: Was du als Mensch einmalig tun musst

*   GitHub Account bereitstellen (persönlich oder Organisation).
*   Neues öffentliches Repository anlegen, z. B. 'soundtouch-bridge'.
*   Lizenz festlegen (empfohlen: Apache-2.0 oder MIT).
*   README.md minimal anlegen (Projektname + Kurzbeschreibung reicht).
*   GitHub Container Registry (ghcr.io) ist automatisch verfügbar – kein Extra-Setup nötig.

## 9.5 Lokales Setup (VS Code)

*   VS Code installieren.
*   GitHub Repository lokal klonen.
*   Docker & Docker Compose installieren.
*   VS Code Extensions (empfohlen): Docker, Python, YAML, GitHub Actions.

## 9.6 Arbeitsweise mit dem Agenten (konkret)

Du arbeitest dialogbasiert mit dem Agenten. Für jede Iteration:
1) Du gibst dem Agenten den aktuellen Stand (Repo-Status, letzte Iteration, Feedback).
2) Du gibst frei, welche Iteration umgesetzt werden soll (z. B. 'Iteration 0: Repo + CI/CD').
3) Der Agent liefert Code, Tests, CI/CD und Doku.
4) Du prüfst lokal (docker compose up) und ggf. auf echten Geräten.
5) Du gibst Feedback oder Freigabe.
6) Erst nach Freigabe commitest und pushst du nach GitHub.

## 9.7 Commit- und Review-Regeln

*   Der Agent schreibt Code, aber du führst die Commits aus (lokal).
*   Ein Commit pro Iteration oder logisch abgeschlossener Teil.
*   Commit Message Schema: 'Iteration X: <kurze Beschreibung>'.
*   CI muss grün sein, bevor gemerged oder released wird.

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

*   Lokaler Test: docker compose up → Web-UI aufrufen → Preset setzen.
*   E2E Test: Preset-Taste am Gerät drücken und Audio/Display prüfen.
*   Bei Erfolg: Git Tag setzen (z. B. v0.1.0) und pushen.
*   CI/CD baut Release-Image und pusht nach ghcr.io.

## 9.10 Goldene Regeln für die Zusammenarbeit

*   Der Agent implementiert – du entscheidest.
*   Keine 'stillen' Architekturwechsel ohne explizite Zustimmung.
*   Refactoring nur nach Iterationsende und mit klarer Begründung.
*   Immer im Blick behalten: Laienfreundlichkeit, ein Container, Web-UI, Open Source.