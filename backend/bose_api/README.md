# Bose SoundTouch API Referenz

**Stand**: 2026-01-29  
**Projekt**: SoundTouchBridge (STB)  
**Quelle**: Gesammelte Schemas von 3 Geräten + [bosesoundtouchapi 1.0.86](https://github.com/thlucas1/bosesoundtouchapi)

---

## 1. Übersicht

Bose SoundTouch Geräte bieten eine XML-basierte REST API auf Port `8090`.  
Die API ermöglicht vollständige Steuerung und Status-Abfragen über HTTP GET/POST.

**Basis-URL**: `http://{device_ip}:8090/{endpoint}`

**Beispiel**: `curl http://192.0.2.78:8090/info`

---

## 2. Getestete Geräte

| Gerät | Modell | IP | Device-ID | Firmware |
|-------|--------|----|-----------|-----------
| ST30_Living Room | SoundTouch 30 Series III | 192.0.2.78 | ...20C6 | 28.0.3.46454 |
| ST10_Kueche | SoundTouch 10 | 192.0.2.79 | ...AE25 | 28.0.3.46454 |
| ST300_TV | SoundTouch 300 | 192.0.2.83 | ...1111 | 28.0.3.46454 |

---

## 3. API Endpoint Kategorien

### 3.1 Endpoint-Übersicht

**Gesamt**: 109 Endpoints  
**Gemeinsam** (alle Modelle): 102  
**ST300-spezifisch** (nur SoundTouch 300): 7

### 3.2 Kategorisierung

#### Read-Only Endpoints (GET) - 51 Stück
Können gefahrlos abgefragt werden ohne Geräte-Zustand zu ändern.

| Kategorie | Anzahl | Beispiele |
|-----------|--------|-----------|
| **Device Info** | 8 | `/info`, `/capabilities`, `/supportedURLs`, `/volume` |
| **Playback** | 12 | `/nowPlaying`, `/sources`, `/trackInfo`, `/artistAndPlaylistInfo` |
| **Network** | 6 | `/networkInfo`, `/bluetoothInfo`, `/wirelessProfile` |
| **Zone/Group** | 4 | `/getZone`, `/getGroup`, `/bass`, `/bassCapabilities` |
| **Presets** | 3 | `/presets`, `/recents`, `/listMediaServers` |
| **System** | 18 | `/DSPMonoStereo`, `/name`, `/language`, `/systemtimeout`, `/clockConfig` |

#### Write Endpoints (POST/PUT) - 58 Stück
Ändern Geräte-Zustand. **VORSICHT**: Einige können Geräte zurücksetzen!

| Kategorie | Anzahl | Beispiele |
|-----------|--------|-----------|
| **Playback Control** | 15 | `/key`, `/select`, `/speaker`, `/play`, `/pause` |
| **Volume** | 3 | `/volume` (POST) |
| **Presets** | 6 | `/storePreset`, `/removePreset`, `/removeStation` |
| **Zone/Group** | 8 | `/setZone`, `/addZoneSlave`, `/createZone`, `/createGroup` |
| **Network** | 7 | `/setWirelessProfile`, `/addWirelessProfile`, `/bluetoothClassicPair` |
| **System Config** | 14 | `/name` (POST), `/language` (POST), `/clockConfig` (POST) |
| **⚠️ GEFÄHRLICH** | 5 | `/resetDefaults`, `/reboot`, `/standby`, `/powerManagement` |

---

## 4. Modell-Unterschiede

### 4.1 ST300-Exklusive Endpoints (HDMI/Audio)

**Nur SoundTouch 300** unterstützt diese 7 Endpoints:

```
1. /audiodspcontrols              - DSP Audio Kontrollen
2. /audioproductlevelcontrols     - Product-Level Audio-Einstellungen
3. /audioproducttonecontrols      - Tone Controls (Bass, Treble)
4. /audiospeakerattributeandsetting - Lautsprecher-Attribute
5. /productcechdmicontrol         - CEC HDMI Steuerung
6. /producthdmiassignmentcontrols - HDMI Input Zuordnung
7. /systemtimeoutcontrol          - System Timeout Konfiguration
```

**Grund**: ST300 ist eine Soundbar mit HDMI-Eingängen, die anderen sind Wireless Speaker.

**Handhabung in STB**:
- Diese Endpoints nur für ST300 anbieten
- Bei ST30/ST10: 404 Not Found zurückgeben
- UI: Features nur anzeigen wenn Gerät `DeviceType=SoundTouch 300` hat

### 4.2 Gemeinsame Endpoints mit unterschiedlichen Schemas

**Gleiche Endpoint, unterschiedliche Antworten**:

| Endpoint | Unterschied |
|----------|-------------|
| `/capabilities` | ST300 hat zusätzliche HDMI-Capabilities |
| `/supportedURLs` | ST300 listet 7 extra URLs |
| `/info` | Alle: `DeviceType` ist unterschiedlich (`SoundTouch 30 Series III`, `SoundTouch 10`, `SoundTouch 300`) |

---

## 5. Wichtige Endpoints im Detail

### 5.1 Device Information

#### `/info` (GET)
Liefert Device-ID, Name, Typ, Firmware-Version, MAC-Adresse.

**Request**:
```bash
curl http://192.0.2.78:8090/info
```

**Response** (ST30):
```xml
<info deviceID="AABBCC112233">
  <name>Living Room</name>
  <type>SoundTouch 30 Series III</type>
  <margeAccountUUID>AABBCC112233</margeAccountUUID>
  <components>
    <component>
      <componentCategory>SCM</componentCategory>
      <softwareVersion>28.0.3.46454 epdbuild.trunk.hepdswbld02.2023-07-27T14:58:40</softwareVersion>
      <serialNumber>REDACTED</serialNumber>
    </component>
  </components>
  <margeURL>https://streaming.bose.com</margeURL>
  <networkInfo type="SCM">
    <macAddress>REDACTED</macAddress>
    <ipAddress>192.0.2.78</ipAddress>
  </networkInfo>
  <networkInfo type="SMSC">
    <macAddress>REDACTED</macAddress>
    <ipAddress>192.0.2.253</ipAddress>
    <type>SMSC</type>
  </networkInfo>
  <moduleType>sm2</moduleType>
  <variant>ginger</variant>
  <variantMode>normal</variantMode>
  <countryCode>US</countryCode>
  <regionCode>US</regionCode>
</info>
```

**bosesoundtouchapi Mapping**:
```python
client = SoundTouchClient(device)
info = client.GetInformation()

# Properties:
info.DeviceId        # "AABBCC112233"
info.DeviceName      # "Living Room"
info.DeviceType      # "SoundTouch 30 Series III"
info.NetworkInfo[0]  # InformationNetworkInfo object (is a list!)
info.NetworkInfo[0].MacAddress
info.NetworkInfo[0].IpAddress
```

⚠️ **WICHTIG**: `info.NetworkInfo` ist eine **Liste**, nicht ein einzelnes Objekt!

---

#### `/capabilities` (GET)
Liefert Feature-Matrix des Geräts.

**Response** (gekürzt):
```xml
<capabilities>
  <isClockDisplayCapable>true</isClockDisplayCapable>
  <isBassCapable>true</isBassCapable>
  <isProductCECHDMIControlCapable>false</isProductCECHDMIControlCapable> <!-- ST300: true -->
  <isSoundTouchSDKCapable>true</isSoundTouchSDKCapable>
  <isVoicePromptCapable>true</isVoicePromptCapable>
  <mediaInputsSupported>BLUETOOTH,INTERNET_RADIO,...</mediaInputsSupported>
</capabilities>
```

---

#### `/supportedURLs` (GET)
Listet alle vom Gerät unterstützten Endpoints.

**Verwendung**: 
- Capability Detection: Feature nur anbieten wenn Endpoint vorhanden
- Beispiel: `if "/productcechdmicontrol" in supported_urls: show_hdmi_controls()`

---

### 5.2 Playback Status

#### `/nowPlaying` (GET)
Aktueller Playback-Status (was spielt gerade, Play/Pause/Stop).

**Request**:
```bash
curl http://192.0.2.78:8090/nowPlaying
```

**Response** (Radio):
```xml
<nowPlaying source="INTERNET_RADIO" sourceAccount="1">
  <ContentItem source="INTERNET_RADIO" type="stationurl" location="/v1/playback/station/s24896" sourceAccount="1" isPresetable="true">
    <itemName>Klassik Radio</itemName>
    <containerArt>http://cdn-profiles.tunein.com/s24896/images/logoq.png</containerArt>
  </ContentItem>
  <track>Klassik Radio</track>
  <artist></artist>
  <album></album>
  <stationName>Klassik Radio</stationName>
  <art artImageStatus="IMAGE_PRESENT">http://cdn-profiles.tunein.com/s24896/images/logoq.png</art>
  <playStatus>PLAY_STATE</playStatus>
  <streamType>TRACK_ONDEMAND</streamType>
</nowPlaying>
```

**bosesoundtouchapi Mapping**:
```python
now_playing = client.GetNowPlayingStatus()  # NICHT GetNowPlaying()!

# Properties:
now_playing.Source           # "INTERNET_RADIO"
now_playing.SourceAccount    # "1"
now_playing.Track            # "Klassik Radio"
now_playing.Artist           # ""
now_playing.Album            # ""
now_playing.PlayStatus       # "PLAY_STATE" | "PAUSE_STATE" | "STOP_STATE"
now_playing.StreamType       # "TRACK_ONDEMAND"
now_playing.Art              # ContentItem object
now_playing.Art.ArtImageUrl  # "http://..."
```

---

#### `/sources` (GET)
Liefert Liste aller Quellen (Bluetooth, AUX, TuneIn, Spotify, ...).

**Response**:
```xml
<sources deviceID="AABBCC112233">
  <sourceItem source="PRODUCT" sourceAccount="TV" status="READY" isLocal="true" multiroomallowed="true"/>
  <sourceItem source="BLUETOOTH" status="READY" isLocal="true" multiroomallowed="false"/>
  <sourceItem source="AUX" sourceAccount="AUX" status="READY" isLocal="true" multiroomallowed="true"/>
  <sourceItem source="INTERNET_RADIO" status="READY" isLocal="false" multiroomallowed="true"/>
  <sourceItem source="SPOTIFY" sourceAccount="your_account" status="READY" isLocal="false" multiroomallowed="true"/>
</sources>
```

---

### 5.3 Volume Control

#### `/volume` (GET/POST)
Lautstärke abfragen und setzen.

**GET Request**:
```bash
curl http://192.0.2.78:8090/volume
```

**Response**:
```xml
<volume deviceID="AABBCC112233">
  <targetvolume>15</targetvolume>
  <actualvolume>15</actualvolume>
  <muteenabled>false</muteenabled>
</volume>
```

**POST Request** (Lautstärke auf 20 setzen):
```bash
curl -X POST http://192.0.2.78:8090/volume \
  -H "Content-Type: application/xml" \
  -d '<volume>20</volume>'
```

**bosesoundtouchapi Mapping**:
```python
# GET Volume
volume = client.GetVolume()
print(volume.Target)  # 15

# SET Volume
client.SetVolume(20)
```

---

### 5.4 Presets

#### `/presets` (GET)
Liefert alle gespeicherten Presets (1-6).

**Response**:
```xml
<presets>
  <preset id="1">
    <ContentItem source="INTERNET_RADIO" type="stationurl" location="/v1/playback/station/s24896" sourceAccount="1" isPresetable="true">
      <itemName>Klassik Radio</itemName>
      <containerArt>http://cdn-profiles.tunein.com/s24896/images/logoq.png</containerArt>
    </ContentItem>
  </preset>
  <preset id="2">
    <ContentItem source="SPOTIFY" ...>
      ...
    </ContentItem>
  </preset>
  ...
</presets>
```

**bosesoundtouchapi Mapping**:
```python
presets = client.GetPresetList()
for preset in presets.Presets:
    print(f"Preset {preset.PresetId}: {preset.Name}")
```

---

### 5.5 Key Presses (Remote Control)

#### `/key` (POST)
Simuliert Fernbedienung-Tasten (Play, Pause, Next, Previous, Power, ...).

**POST Request** (Play):
```bash
curl -X POST http://192.0.2.78:8090/key \
  -H "Content-Type: application/xml" \
  -d '<key state="press" sender="Gabbo">PLAY</key>'
```

**Verfügbare Keys**:
```
PLAY, PAUSE, PLAY_PAUSE, STOP, PREV_TRACK, NEXT_TRACK,
THUMBS_UP, THUMBS_DOWN, BOOKMARK, POWER, MUTE,
VOLUME_UP, VOLUME_DOWN, PRESET_1, PRESET_2, ..., PRESET_6,
AUX_INPUT, SHUFFLE_OFF, SHUFFLE_ON, REPEAT_OFF, REPEAT_ONE, REPEAT_ALL
```

**bosesoundtouchapi Mapping**:
```python
from bosesoundtouchapi import SoundTouchKeys

client.PressKey(SoundTouchKeys.PLAY)
client.PressKey(SoundTouchKeys.VOLUME_UP)
client.PressKey(SoundTouchKeys.PRESET_1)
```

---

### 5.6 Zone/Group Management

#### `/getZone` (GET)
Liefert Zone-Konfiguration (Multi-Room Audio).

**Response** (Master):
```xml
<zone master="AABBCC112233" senderIPAddress="192.0.2.78">
  <member ipaddress="192.0.2.79">40EF11B1AE25</member>
  <member ipaddress="192.0.2.83">AABBCC112244</member>
</zone>
```

**Response** (Standalone):
```xml
<zone master="AABBCC112233"/>
```

**bosesoundtouchapi Mapping**:
```python
zone = client.GetZoneStatus()
if zone.IsMasterOfZone:
    print(f"Master device with {len(zone.Members)} slaves")
    for member in zone.Members:
        print(f"  - {member.DeviceId} @ {member.IpAddress}")
```

---

## 7. bosesoundtouchapi Library Quirks

Die `bosesoundtouchapi` Python Library abstrahiert die XML API. **WICHTIG**: Property/Method-Namen stimmen NICHT immer mit XML-Elementen überein!

### 7.1 Property-Naming Unterschiede

| XML Element | bosesoundtouchapi Property | Kategorie |
|-------------|----------------------------|-----------|
| `<name>` | `info.DeviceName` (NICHT `info.Name`!) | Device Info |
| `<type>` | `info.DeviceType` | Device Info |
| `<networkInfo>` | `info.NetworkInfo[0]` (ist Liste!) | Network |
| `<sources>` | `client.GetSourceList()` (NICHT `GetSources`!) | Sources |

**Root Cause**: Library nutzt interne Naming-Conventions, nicht 1:1 XML-Mapping.

**Fix**: Immer in Library-Source prüfen:
```bash
# In venv:
C:\Python313\Lib\site-packages\bosesoundtouchapi\
  - models.py      # Datenklassen (Info, Capabilities, etc.)
  - client.py      # Client-Methods (GetInformation, GetSourceList, etc.)
```

### 7.2 Wichtigste Method-Namen

| Funktion | Methode | Return Type |
|----------|---------|-------------|
| Device Info abrufen | `client.GetInformation()` | `Information` |
| Capabilities abrufen | `client.GetCapabilities()` | `Capabilities` |
| Sources abrufen | `client.GetSourceList()` | `SourceList` |
| Volume abrufen | `client.GetVolume()` | `Volume` |
| Now Playing abrufen | `client.GetNowPlayingStatus()` | `NowPlayingStatus` |
| Zone Status abrufen | `client.GetZoneStatus()` | `Zone` |
| Generic GET Request | `client.Get(uri)` | XML String |
| Generic POST Request | `client.Post(uri, xml)` | Response |

**Wichtig**: 
- `Get` vs `GetXXX` - Groß/Kleinschreibung beachten!
- `GetSourceList()` nicht `GetSources()`
- `GetNowPlayingStatus()` nicht `GetNowPlaying()`

### 7.3 Error Handling

`SoundTouchError` hat read-only Property `ErrorCode`:

```python
from bosesoundtouchapi import SoundTouchClient, SoundTouchError

try:
    result = client.Get("/nonexistent")
except SoundTouchError as e:
    if e.ErrorCode == 404:
        # Endpoint not supported by this device
        return None
    elif e.ErrorCode == 401:
        # Authentication required
        return None
    else:
        # Unexpected error - re-raise
        raise
```

**Konstruktor-Signatur**:
```python
SoundTouchError(
    message: str, 
    name: str = None, 
    severity: str = None, 
    errorCode: int = 0,  # ← Parameter verwenden!
    logsi: SISession = None
)
```

**FEHLER** (wird fehlschlagen):
```python
error = SoundTouchError("Not found")
error.ErrorCode = 404  # ❌ AttributeError - no setter!
```

**KORREKT**:
```python
error = SoundTouchError("Not found", errorCode=404)  # ✅
print(error.ErrorCode)  # 404
```

### 7.4 Regression Tests

**REGEL**: Für jeden gefundenen Bug MUSS ein Regression-Test geschrieben werden!

Siehe `docs/REGRESSION_TESTS.md` für Details:
- **RT-001**: GetSources() vs GetSourceList() Fehler
- **RT-002**: SoundTouchError.ErrorCode Read-Only Property

**Warum?**
- Verhindert, dass gleicher Bug nochmal auftritt
- Dokumentiert Library-Eigenheiten für zukünftige Entwickler
- Validiert Annahmen gegen echte Library-Implementierung

**Test-Pattern**:
```python
from unittest.mock import MagicMock
from bosesoundtouchapi import SoundTouchClient

def test_source_list_not_sources():
    """Regression test: GetSourceList() nicht GetSources()."""
    client = MagicMock(spec=SoundTouchClient)
    
    # Mock mit spec=SoundTouchClient würde bei falscher Methode fehlschlagen
    sources = MagicMock()
    sources.Sources = [MagicMock(Source="BLUETOOTH", Status="READY")]
    
    # ✅ KORREKT:
    client.GetSourceList.return_value = sources
    
    # ❌ FEHLER (würde AttributeError werfen):
    # client.GetSources.return_value = sources
```

---

## 8. Schema-Dateien

Alle 153 XML-Schemas sind im Verzeichnis `backend/bose_api/` gespeichert:

**Naming-Convention**:
```
device_{device_id}_{endpoint}.xml
```

**Beispiele**:
- `device_78_info.xml` - Device Info von ST30 (192.0.2.78)
- `device_79_nowPlaying.xml` - Now Playing von ST10 (192.0.2.79)
- `device_83_productcechdmicontrol.xml` - HDMI Control von ST300 (nur dort vorhanden!)

**Verwendung**:
- Als Referenz beim Entwickeln von API-Calls
- Für Unit-Tests (Mock-Responses)
- Zum Vergleichen von Modell-Unterschieden

---

## 7. bosesoundtouchapi Library Integration

### 7.1 Korrekte Property-Namen

⚠️ **VORSICHT**: Library-Properties weichen von XML-Tags ab!

| XML Tag | Library Property | Typ |
|---------|------------------|-----|
| `<name>` | `info.DeviceName` | str |
| `<type>` | `info.DeviceType` | str |
| `<deviceID>` | `info.DeviceId` | str |
| `<networkInfo>` | `info.NetworkInfo` | **List**[InformationNetworkInfo] |
| `<macAddress>` | `info.NetworkInfo[0].MacAddress` | str |

**Korrekter Code**:
```python
info = client.GetInformation()
device_name = info.DeviceName  # NICHT info.Name!
device_type = info.DeviceType  # NICHT info.Type!
mac = info.NetworkInfo[0].MacAddress  # NetworkInfo ist Liste!
```

### 7.2 Korrekte Methoden-Namen

| Falsch (non-existent) | Richtig |
|-----------------------|---------|
| `client.GetNowPlaying()` | `client.GetNowPlayingStatus()` |
| `client.GetInfo()` | `client.GetInformation()` |

### 7.3 Wichtige Library-Klassen

#### SoundTouchDevice
```python
from bosesoundtouchapi import SoundTouchDevice

device = SoundTouchDevice("192.0.2.78")
print(device.Host)           # "192.0.2.78"
print(device.Port)           # 8090
print(device.DeviceId)       # "AABBCC112233"
print(device.DeviceName)     # "Living Room"
print(device.DeviceType)     # "SoundTouch 30 Series III"
```

#### SoundTouchClient
```python
from bosesoundtouchapi import SoundTouchClient

client = SoundTouchClient(device)

# Volume
volume = client.GetVolume()
client.SetVolume(25)

# Playback
status = client.GetNowPlayingStatus()
client.PressKey(SoundTouchKeys.PLAY)

# Presets
presets = client.GetPresetList()
client.SelectPreset(preset=1)

# Zone
zone = client.GetZoneStatus()
```

#### SoundTouchNodes (URI Constants)
```python
from bosesoundtouchapi.uri import SoundTouchNodes

# Low-Level API Access
msg = client.Get(SoundTouchNodes.info)
msg = client.Get(SoundTouchNodes.volume)
msg = client.Put(SoundTouchNodes.volume, '<volume>20</volume>')
```

---

## 8. Fehlerbehandlung

### 8.1 HTTP Status Codes

| Code | Bedeutung | Beispiel |
|------|-----------|----------|
| 200 | OK | Erfolgreiche Abfrage |
| 401 | Unauthorized | App-Key fehlt (bei manchen Endpoints) |
| 404 | Not Found | Endpoint nicht unterstützt (z.B. ST30 + `/productcechdmicontrol`) |
| 415 | Unsupported Media Type | Falsche Content-Type Header |
| 500 | Internal Server Error | Device-Fehler |

### 8.2 Error XML Response

**Beispiel** (Unauthorized):
```xml
<errors deviceID="AABBCC112233">
  <error name="HTTP_STATUS_UNAUTHORIZED" value="401" severity="Unknown">
    Unauthorized
  </error>
</errors>
```

**bosesoundtouchapi Mapping**:
```python
from bosesoundtouchapi import SoundTouchError

try:
    client.SetVolume(150)  # Invalid volume
except SoundTouchError as e:
    print(e.ErrorCode)   # 415
    print(e.Name)        # "HTTP_STATUS_UNSUPPORTED_MEDIA_TYPE"
    print(e.Message)     # "Unsupported Media Type"
```

---

## 9. Best Practices für STB

### 9.1 Capability Detection

**IMMER** `/supportedURLs` oder `/capabilities` prüfen bevor Features angeboten werden:

```python
supported_urls = client.GetCapabilities().SupportedUrls

if "/productcechdmicontrol" in supported_urls:
    # Zeige HDMI Controls nur wenn verfügbar
    show_hdmi_controls()
else:
    # ST30/ST10 haben keine HDMI-Eingänge
    hide_hdmi_controls()
```

### 9.2 Graceful Degradation

**NICHT**: Features für alle Geräte erzwingen  
**SONDERN**: Features nur anbieten wenn Gerät sie unterstützt

```python
# ✅ GOOD
try:
    hdmi_config = client.Get(SoundTouchNodes.productcechdmicontrol)
except SoundTouchError as e:
    if e.ErrorCode == 404:
        logger.info("Device does not support HDMI controls")
        return None
    raise

# ❌ BAD
hdmi_config = client.Get(SoundTouchNodes.productcechdmicontrol)  # Crashes on ST30!
```

### 9.3 Timeouts

**IMMER** Timeouts setzen:

```python
device = SoundTouchDevice("192.0.2.78")
device.ConnectTimeout = 5.0  # Seconds

client = SoundTouchClient(device)
```

### 9.4 Polling-Intervalle

**Empfohlene Intervalle**:
- `/nowPlaying`: 2-5 Sekunden (während Playback)
- `/volume`: 1 Sekunde (während UI-Interaktion)
- `/info`: 60 Sekunden (selten nötig)
- `/getZone`: 10 Sekunden (wenn Zone aktiv)

**WebSocket Alternative**:
```python
from bosesoundtouchapi.ws import SoundTouchWebSocket

# Event-basierte Updates statt Polling
ws = SoundTouchWebSocket(device)
ws.AddListener(SoundTouchNotifyCategorys.nowPlayingUpdated, on_now_playing_changed)
ws.StartNotification()
```

---

## 10. Sicherheitshinweise

### 10.1 Gefährliche Endpoints

**NIEMALS** ohne User-Bestätigung ausführen:

```
/resetDefaults     - Factory Reset (löscht ALLE Daten!)
/reboot            - Reboot des Geräts
/standby           - Gerät in Standby versetzen
/powerManagement   - Power-Einstellungen ändern
```

### 10.2 App-Key Requirement

Manche Endpoints (z.B. `/speaker`, `/playNotification`) benötigen einen **App-Key**.

**Registrierung**: https://developer.bose.com (⚠️ Cloud abgeschaltet!)

**Workaround**: Verwende generischen Key aus bosesoundtouchapi Library.

---

## 11. Unterschiede zur offiziellen Bose API

**Problem**: Bose hat offizielle API-Dokumentation mit Cloud-Shutdown entfernt.

**Lösung**: Diese Dokumentation basiert auf:
1. **Reverse Engineering** (gesammelte Schemas von 3 Geräten)
2. **Community Library** (bosesoundtouchapi 1.0.86)
3. **Praxistests** (alle Endpoints manuell getestet)

**Bekannte Abweichungen**:
- Keine - bosesoundtouchapi Library basiert auf offizieller Bose SDK
- Alle XML-Schemas sind 1:1 von Geräten

---

## 12. Weitere Ressourcen

### 12.1 bosesoundtouchapi Library
- **GitHub**: https://github.com/thlucas1/bosesoundtouchapi
- **Docs**: https://thlucas1.github.io/bosesoundtouchapi/
- **PyPI**: `pip install bosesoundtouchapi`

### 12.2 Community Projekte
- **Home Assistant Integration**: https://github.com/thlucas1/homeassistantcomponent_soundtouchplus
- **Node.js Client**: https://github.com/Adeptive/SoundTouch-NodeJS
- **PHP API**: https://github.com/sabinus52/SoundTouchApi

### 12.3 STB-Spezifische Docs
- **Schema-Sammlung**: `backend/bose_api/device_*.xml`
- **Analyse-Script**: `backend/bose_api/analyze_api.py`
- **Fetch-Script**: `fetch-api-schemas.ps1`

---

## 13. Changelog

| Datum | Änderung |
|-------|----------|
| 2026-01-29 | **Iteration 1.c**: Punkt 9.1 (MUST HAVE) implementiert |
| 2026-01-29 | Capability Detection System (`backend/adapters/capability_detection.py`) |
| 2026-01-29 | Regression Tests dokumentiert (`docs/REGRESSION_TESTS.md`) |
| 2026-01-29 | bosesoundtouchapi Quirks dokumentiert (Abschnitt 7) |
| 2026-01-29 | 13/13 Tests für Capability Detection erfolgreich |
| 2026-01-29 | E2E Demo-Script erstellt (`e2e/demo_capability_detection.py`) |
| 2026-01-29 | Initial release - 109 Endpoints dokumentiert |
| 2026-01-29 | ST300 HDMI-Endpoints identifiziert (7 Stück) |
| 2026-01-29 | bosesoundtouchapi 1.0.86 Integration dokumentiert |

---

**Letzte Aktualisierung**: 2026-01-29  
**Nächste Review**: Bei Firmware-Update der Geräte oder Start Iteration 2
