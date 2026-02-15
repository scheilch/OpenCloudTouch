# Internet Research: Bose SoundTouch Custom Preset Solutions

**Datum**: 2026-02-15  
**Problem**: Custom Internet Radio Presets spielen nicht ab (LED: orange→weiß→orange)

---

## Executive Summary

**Kernproblem identifiziert:**
Alle funktionierenden Lösungen erfordern **Gerätekonfiguration via USB-Stick + Root-Zugang**.

Es gibt **KEINE** Lösung die ohne Gerätemodifikation funktioniert, weil:
1. Bose-Geräte haben hardcodierte Server-URLs
2. BMX-Server hat "IsItBose" Check mit API-Key Validierung
3. HTTPS-Streams können nicht direkt abgespielt werden

---

## Geklonte Repositories

Alle Repos befinden sich unter `reference-impl/`:

| Repository | Stars | Sprache | Beschreibung | Git Clone |
|------------|-------|---------|--------------|-----------|
| **soundcork** | 96 | Python | Vollständiger Cloud-Ersatz | `git clone https://github.com/deborahgu/soundcork.git` |
| **ueberboese** | 10 | Java | Alternative Cloud-Ersatz mit Spotify/TuneIn | `git clone https://github.com/julius-d/ueberboese-api.git` |
| **marvoo01** | 10 | HTML | Preset-Editor ohne TuneIn | `git clone https://github.com/Marvoo01/Alternative-Bose-SoundTouch-controller-no-Cloud.git` |
| **colinmacgiolla** | 1 | Docker | Traefik Redirect zu .m3u/.pls | `git clone https://github.com/colinmacgiolla/bose-soundtouch-redirector.git` |
| **bose-soundtouch** | - | Docs | vintx86 API Reference (bereits vorhanden) | - |

---

## Detailanalyse der Projekte

### 1. soundcork (★ EMPFOHLEN - 96 Stars)
**URL**: https://github.com/deborahgu/soundcork

**Was es macht:**
- Vollständiger Ersatz für alle Bose Cloud-Server
- Marge Server (streaming.bose.com) - Account/Presets
- BMX Server (content.api.bose.io) - TuneIn Integration
- FastAPI-basiert, Python 3.12

**Vorteile:**
- Aktive Entwicklung (letzter Commit: 3 Tage)
- 5 Contributors, 70 geschlossene Issues
- Gute Dokumentation
- TuneIn Support funktioniert

**Nachteile:**
- Erfordert USB-Stick + Root-Zugang
- Erfordert Gerätekonfiguration ändern

**Konfigurationsanforderung:**
```xml
<!-- /opt/Bose/etc/SoundTouchSdkPrivateCfg.xml -->
<margeServerUrl>http://soundcork.local:8000/marge</margeServerUrl>
<bmxRegistryUrl>http://soundcork.local:8000/bmx/registry/v1/services</bmxRegistryUrl>
```

---

### 2. ueberboese-api (10 Stars)
**URL**: https://github.com/julius-d/ueberboese-api

**Was es macht:**
- Java/Quarkus-basierter Cloud-Ersatz
- Spotify OAuth Integration
- TuneIn Support
- Docker Compose Deployment

**Vorteile:**
- Docker Container verfügbar: `ghcr.io/julius-d/ueberboese-api`
- Spotify funktioniert (OAuth Token Refresh)
- Gute API-Dokumentation: https://julius-d.github.io/ueberboese-api/

**Alternativer Konfigurationsweg (ohne USB-Stick):**
```bash
# Über Stockholm Port 17000 (nur für Marge-URLs!)
nc 192.168.178.79 17000
envswitch boseurls set http://ueberboese.local https://dummy.local/updates
exit
```
⚠️ **ABER**: BMX-URLs können so NICHT geändert werden!

---

### 3. marvoo01 - Preset Editor (10 Stars)
**URL**: https://github.com/Marvoo01/Alternative-Bose-SoundTouch-controller-no-Cloud

**Was es macht:**
- HTML-basierter Controller für SoundTouch
- Preset-Editor für 6 Presets
- Desktop + Smartphone Versionen

**Interessante Dateien:**
- `De zes presets maken zonder tunein v2.html` - Presets ohne TuneIn
- `De zes presets maken met tunein v3.html` - Presets mit TuneIn

**Preset-Format (TuneIn):**
```xml
<ContentItem source="TUNEIN" type="stationurl" 
             location="/v1/playback/station/s33828" 
             sourceAccount="" isPresetable="true">
    <itemName>Radio Station Name</itemName>
</ContentItem>
```

**Wichtige Warnung aus README:**
> "It's just a shame that the six preset buttons are almost certainly expected 
> to stop working, as the SoundTouch will likely request information from the 
> cloud when you press them."

**Workaround des Autors:**
Nutzt WiiM Mini Streamer für mehr Presets (12 statt 6)

---

### 4. colinmacgiolla - Traefik Redirector (1 Star)
**URL**: https://github.com/colinmacgiolla/bose-soundtouch-redirector

**Was es macht:**
- Traefik als Reverse Proxy
- HTTP 302 Redirects zu Playlist-Files (.m3u, .pls)

**Interessanter Ansatz:**
```yaml
# docker-compose.yml Auszug
- traefik.http.middlewares.redir-station0.redirectregex.replacement=https://www.rte.ie/manifests/radio1.m3u
- traefik.http.middlewares.redir-station3.redirectregex.replacement=http://www.streamingsoundtracks.com/aacPlus-hi.pls
```

**Hypothese:** Bose könnte Playlist-Files (.m3u/.pls) besser verarbeiten als direkte Stream-URLs.

---

## Technische Erkenntnisse

### 1. "IsItBose" Check
Bose hat einen hardcodierten Check in `/usr/lib/libBmxAccountHsm.so`:
```bash
# Zeigt den Check
strings libBmxAccountHsm.so | grep -i bose
# Output: ^https://bose-[a-zA-Z0-9._-$%]+.apigee.net/
```

**Workaround (erfordert Root-Zugang):**
```bash
sed "s#\^https:....bose.\+apigee..net..#http[aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa]*#g" \
    <libBmxAccountHsm.so.orig >libBmxAccountHsm.so.patched
```

### 2. BMX API Key
```
x-bmx-api-key: srI32oFlkcAXvN630s61JEYZ9JJAzk0W
```
(Base64: `eC1ibXgtYXBpLWtleTpzckkzMm9GbGtjQVh2TjYzMHM2MUpFWVo5SkpBemswVwo=`)

### 3. USB-Stick Root-Zugang
```bash
# USB-Stick (FAT32) mit leerer Datei "remote_services"
# Dann: Gerät mit eingestecktem Stick neu starten
telnet 192.168.178.79
# Login: root (kein Passwort)

# Permanenten Zugang ohne USB-Stick aktivieren:
touch /mnt/nv/remote_services
/etc/init.d/sshd start
reboot
```

### 4. Firmware-Update Problem
Issue #112 in soundcork:
> "ST30 MK3 vers 27.0.6: USB-Stick Methode funktioniert nicht mehr"

**Lösung:** Firmware auf 27.0.6.46330.5043500 downgraden (Bluetooth Version)
Download: https://archive.org/download/bose-soundtouch-software-and-firmware/

---

## Bewertung der Optionen

| Option | Aufwand | Erfolgswahrscheinlichkeit | Gerätemodifikation |
|--------|---------|--------------------------|-------------------|
| **soundcork** | Mittel | Hoch (96 Stars, aktiv) | USB-Stick + Root |
| **ueberboese** | Mittel | Hoch (10 Stars, aktiv) | USB-Stick + Root (für BMX) |
| **Playlist-Files** | Niedrig | Unbekannt (nicht getestet) | Keine |
| **DNS Hijacking** | Niedrig | Gering (HTTPS Cert Problem) | Keine |
| **OCT Stream Proxy** | Niedrig | Gering (500 Error) | Keine |

---

## Empfehlung: Nächste Schritte

### Option A: Playlist-File Test (Ohne Gerätemodifikation)
1. Implementiere .m3u Endpoint in OCT
2. Speichere Preset mit Playlist-URL statt direkter Stream-URL
3. Teste ob Bose das Playlist-File parst

**Beispiel:**
```python
# Neuer Endpoint: GET /playlist/{preset_id}.m3u
@router.get("/playlist/{preset_id}.m3u")
async def get_playlist(preset_id: int):
    preset = await get_preset(preset_id)
    return Response(
        content=f"""#EXTM3U
#EXTINF:-1,{preset.name}
{preset.stream_url}
""",
        media_type="audio/x-mpegurl"
    )
```

### Option B: soundcork/ueberboese Integration (Mit Gerätemodifikation)
1. soundcork als Docker Container deployen
2. USB-Stick mit `remote_services` erstellen
3. Gerät konfigurieren
4. OCT als Frontend, soundcork als BMX-Backend

### Option C: WiiM Mini Workaround (Hardware)
wie marvoo01 - WiiM Mini Streamer kaufen, SoundTouch als "Slave" nutzen

---

## Offene Fragen

1. Funktioniert Playlist-File Parsing auf Bose ohne Gerätemodifikation?
2. Welche Firmware-Version hat das Küchen-Gerät (689E194F7D2F)?
3. Ist USB-Stick Root-Zugang auf diesem Gerät möglich?
4. Kann `envswitch boseurls` über Port 17000 ohne Root-Zugang genutzt werden?

---

## Quellen

- soundcork Discussions: https://github.com/deborahgu/soundcork/discussions
- soundcork Issue #62 (IsItBose): https://github.com/deborahgu/soundcork/issues/62
- soundcork Issue #112 (USB removed): https://github.com/deborahgu/soundcork/issues/112
- ueberboese Docs: https://julius-d.github.io/ueberboese-api/
- flarn2006 Blog (Original Hack): https://flarn2006.blogspot.com/2014/09/hacking-bose-soundtouch-and-its-linux.html
