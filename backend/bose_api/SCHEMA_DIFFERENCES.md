# Schema-Unterschiede zwischen SoundTouch Modellen

**Stand**: 2026-01-29  
**Analysierte Geräte**: ST30 (.78), ST10 (.79), ST300 (.83)

---

## 1. Executive Summary

**Gesamt-Bewertung**: ✅ **KEIN kritisches Problem**

- **7 ST300-exklusive Endpoints** identifiziert → Erwartetes Verhalten (Soundbar vs Speaker)
- **102 gemeinsame Endpoints** haben identische oder kompatible Schemas
- **Keine Breaking Changes** zwischen Modellen für Standard-Funktionen

**Empfehlung**: 
- Capability Detection implementieren (`/supportedURLs` prüfen)
- UI-Features modell-abhängig anzeigen
- Keine separate API-Abstraktion pro Modell nötig

---

## 2. Modell-spezifische Endpoints

### 2.1 ST300-Exklusive Features (HDMI/Audio)

**Problem**: Diese Endpoints existieren NUR auf ST300:

```
1. /audiodspcontrols
2. /audioproductlevelcontrols
3. /audioproducttonecontrols
4. /audiospeakerattributeandsetting
5. /productcechdmicontrol
6. /producthdmiassignmentcontrols
7. /systemtimeoutcontrol
```

**Test-Ergebnisse**:

| Endpoint | ST30 (.78) | ST10 (.79) | ST300 (.83) |
|----------|------------|------------|-------------|
| `/productcechdmicontrol` | ❌ 404 | ❌ 404 | ✅ 200 |
| `/audioproducttonecontrols` | ❌ 404 | ❌ 404 | ✅ 200 |

**Root Cause**: 
- ST300 ist eine **Soundbar mit HDMI-Eingängen**
- ST30/ST10 sind **Wireless Speaker ohne Video-Fähigkeiten**

**Impact auf STB**: 
- ⚠️ **Mittel** - Features müssen modell-abhängig angeboten werden
- UI darf HDMI-Controls nicht für ST30/ST10 zeigen
- Backend muss 404-Fehler graceful handhaben

**Lösung**:
```python
# Capability Detection
async def supports_hdmi_control(device_id: str) -> bool:
    device = await get_device(device_id)
    return "SoundTouch 300" in device.device_type

# UI Logic
if await supports_hdmi_control(device_id):
    show_hdmi_controls()
else:
    hide_hdmi_controls()

# Backend Error Handling
try:
    hdmi_status = await client.Get(SoundTouchNodes.productcechdmicontrol)
except SoundTouchError as e:
    if e.ErrorCode == 404:
        logger.info(f"Device {device_id} does not support HDMI controls")
        return None
    raise
```

---

### 2.2 Gemeinsame Endpoints mit unterschiedlichen Schemas

#### 2.2.1 `/info` - DeviceType-Unterschied

**Schema-Vergleich**:

**ST30** (.78):
```xml
<type>SoundTouch 30 Series III</type>
<moduleType>sm2</moduleType>
<variant>ginger</variant>
```

**ST10** (.79):
```xml
<type>SoundTouch 10</type>
<moduleType>sm2</moduleType>
<variant>spotty</variant>
```

**ST300** (.83):
```xml
<type>SoundTouch 300</type>
<moduleType>sm2</moduleType>
<variant>ginger-black</variant>
```

**Impact**: ✅ **KEIN Problem**
- Alle haben gleiche XML-Struktur
- Nur Werte unterscheiden sich
- bosesoundtouchapi Library parst alle korrekt

**Verwendung**:
```python
info = client.GetInformation()
device_type = info.DeviceType  # "SoundTouch 30 Series III" | "SoundTouch 10" | "SoundTouch 300"

# Model Detection
is_soundbar = "300" in device_type
is_wireless_speaker = "30" in device_type or "10" in device_type
```

---

#### 2.2.2 `/capabilities` - Feature-Matrix

**ST30** (.78) - Auszug:
```xml
<isProductCECHDMIControlCapable>false</isProductCECHDMIControlCapable>
<isBassCapable>true</isBassCapable>
<isAudioProductLevelControlCapable>false</isAudioProductLevelControlCapable>
```

**ST300** (.83) - Auszug:
```xml
<isProductCECHDMIControlCapable>true</isProductCECHDMIControlCapable>
<isBassCapable>true</isBassCapable>
<isAudioProductLevelControlCapable>true</isAudioProductLevelControlCapable>
```

**Impact**: ✅ **KEIN Problem** - Explizit dafür designed!
- `/capabilities` ist genau für diese Unterschiede da
- Jedes Capability ist boolean-Flag
- UI/Backend können Capabilities direkt abfragen

**Best Practice**:
```python
caps = client.GetCapabilities()

if caps.IsProductCECHDMIControlCapable:
    # Zeige HDMI CEC Controls
    enable_hdmi_cec_toggle()

if caps.IsAudioProductLevelControlCapable:
    # Zeige erweiterte Audio-Einstellungen
    show_advanced_audio_controls()

if caps.IsBassCapable:
    # Zeige Bass-Regler
    show_bass_control()
```

---

#### 2.2.3 `/supportedURLs` - Endpoint-Liste

**Unterschied**:
- **ST30/ST10**: 102 URLs
- **ST300**: 109 URLs (102 gemeinsame + 7 HDMI/Audio)

**Impact**: ✅ **KEIN Problem**
- Jedes Gerät listet nur seine tatsächlich unterstützten URLs
- Perfekt für Capability Detection

**Verwendung**:
```python
supported_urls = client.GetCapabilities().SupportedUrls

def is_endpoint_supported(endpoint: str) -> bool:
    return endpoint in supported_urls

# Vor jedem API-Call:
if is_endpoint_supported("/productcechdmicontrol"):
    hdmi_config = client.Get(SoundTouchNodes.productcechdmicontrol)
```

---

#### 2.2.4 `/nowPlaying` - Source-Abhängige Schemas

**Observation**: Schema variiert je nach **aktiver Quelle**, nicht nach Modell!

**INTERNET_RADIO**:
```xml
<nowPlaying source="INTERNET_RADIO">
  <ContentItem source="INTERNET_RADIO" type="stationurl" ...>
    <itemName>Klassik Radio</itemName>
  </ContentItem>
  <track>Klassik Radio</track>
  <stationName>Klassik Radio</stationName>
  <art artImageStatus="IMAGE_PRESENT">http://...</art>
</nowPlaying>
```

**SPOTIFY**:
```xml
<nowPlaying source="SPOTIFY">
  <ContentItem source="SPOTIFY" type="uri" ...>
    <itemName>Song Title</itemName>
  </ContentItem>
  <track>Song Title</track>
  <artist>Artist Name</artist>
  <album>Album Name</album>
  <art artImageStatus="IMAGE_PRESENT">https://i.scdn.co/...</art>
</nowPlaying>
```

**STANDBY** (nichts spielt):
```xml
<nowPlaying source="STANDBY">
  <ContentItem source="STANDBY" sourceAccount=""></ContentItem>
</nowPlaying>
```

**Impact**: ✅ **KEIN Problem** - bosesoundtouchapi Library handled dies
- Library hat `NowPlayingStatus` Klasse mit optionalen Properties
- Fehlende Felder sind `None`

**Handling**:
```python
status = client.GetNowPlayingStatus()

# Safe Access
track = status.Track or "Unknown"
artist = status.Artist or ""
album = status.Album or ""

# Source Detection
if status.Source == SoundTouchSources.INTERNET_RADIO:
    station_name = status.StationName
elif status.Source == SoundTouchSources.SPOTIFY:
    # Spotify hat Artist/Album
    pass
elif status.Source == SoundTouchSources.STANDBY:
    # Nichts spielt
    show_idle_state()
```

---

## 3. Firmware-Version Analyse

**Observation**: Alle 3 Geräte haben identische Firmware:

```
ST30:  28.0.3.46454 epdbuild.trunk.hepdswbld02.2023-07-27T14:58:40
ST10:  28.0.3.46454 epdbuild.trunk.hepdswbld02.2023-07-27T14:58:40
ST300: 28.0.3.46454 epdbuild.trunk.hepdswbld02.2023-07-27T14:58:40
```

**Impact**: ✅ **SEHR GUT**
- Gleiche API-Version auf allen Geräten
- Keine Firmware-bedingte Schema-Unterschiede
- Updates werden synchron sein (Bose Cloud-Shutdown = keine Updates mehr)

**Risiko**: 
- Falls User unterschiedliche Firmware-Versionen haben könnten Schemas abweichen
- **Mitigation**: STB sollte Firmware-Version loggen für Debugging

---

## 4. Netzwerk-Konfiguration Unterschiede

### 4.1 NetworkInfo - Multiple Interfaces

**ST30** (.78) hat **2 NetworkInfo-Objekte**:
```xml
<networkInfo type="SCM">
  <macAddress>AA:BB:CC:11:22:33</macAddress>
  <ipAddress>192.0.2.78</ipAddress>
</networkInfo>
<networkInfo type="SMSC">
  <macAddress>AA:BB:CC:DD:EE:01</macAddress>
  <ipAddress>192.0.2.253</ipAddress>
  <type>SMSC</type>
</networkInfo>
```

**ST10** (.79) hat **1 NetworkInfo-Objekt**:
```xml
<networkInfo type="SCM">
  <macAddress>AA:BB:CC:11:22:44</macAddress>
  <ipAddress>192.0.2.79</ipAddress>
</networkInfo>
```

**Root Cause**:
- **SCM** = SoundTouch Control Module (WiFi)
- **SMSC** = SoundTouch Media Server Connection (optional Ethernet?)

**Impact**: ⚠️ **MITTEL** - Potenzieller Bug!

**Problem**:
```python
# ❌ BAD - Assumes single NetworkInfo
mac = info.NetworkInfo.MacAddress  # Crashes! NetworkInfo is List!

# ✅ GOOD - Handle as List
mac = info.NetworkInfo[0].MacAddress  # Always use first
```

**Bereits gefixt in STB** (Iteration 1a):
```python
# backend/adapters/bosesoundtouch_adapter.py
network_info = info.NetworkInfo[0]  # First interface
return DiscoveredDevice(
    device_id=info.DeviceId,
    name=info.DeviceName,
    ip=network_info.IpAddress,
    mac=network_info.MacAddress,
    ...
)
```

**Test-Coverage**: ✅ Regression-Test vorhanden
```python
# tests/test_soundtouch.py
def test_get_device_info_with_multiple_network_interfaces():
    """Regression test: NetworkInfo is a list."""
    mock_info.NetworkInfo = [
        InformationNetworkInfo(...),
        InformationNetworkInfo(...)  # 2nd interface
    ]
    result = await adapter.get_device_info(device)
    assert result.mac == "AA:BB:CC:DD:EE:FF"  # First interface
```

---

## 5. XML Namespace Handling

**Problem**: Einige XML-Responses haben Namespaces, andere nicht.

**Mit Namespace** (UPnP Discovery):
```xml
<root xmlns="urn:schemas-upnp-org:device-1-0">
  <device>
    <manufacturer>Bose Corporation</manufacturer>
  </device>
</root>
```

**Ohne Namespace** (REST API):
```xml
<info deviceID="AABBCC112233">
  <name>Living Room</name>
</info>
```

**Impact**: ✅ **Bereits gefixt** (Iteration 1a)

**Lösung**: Namespace-agnostisches XPath:
```python
# backend/adapters/ssdp_discovery.py
def _find_xml_text(self, root: Element, path: str) -> str | None:
    """Find element text using namespace-agnostic XPath."""
    # Convert path to local-name() syntax
    parts = path.lstrip("./").split("/")
    local_name_path = "".join(f"/*[local-name()='{part}']" for part in parts)
    element = root.find(local_name_path)
    return element.text if element is not None else None
```

**Test-Coverage**: ✅ Regression-Test vorhanden
```python
def test_xml_namespace_parsing_regression():
    """Regression test for XML namespace handling."""
    xml_with_namespace = '''
    <root xmlns="urn:schemas-upnp-org:device-1-0">
        <device><manufacturer>Bose Corporation</manufacturer></device>
    </root>
    '''
    manufacturer = discovery._find_xml_text(root, ".//manufacturer")
    assert manufacturer == "Bose Corporation"
```

---

## 6. Content-Type Headers

**Observation**: Alle Endpoints akzeptieren `application/xml`:

**POST `/volume`** - Funktioniert:
```bash
curl -X POST http://192.0.2.78:8090/volume \
  -H "Content-Type: application/xml" \
  -d '<volume>20</volume>'
```

**Impact**: ✅ **bosesoundtouchapi Library setzt korrekte Headers automatisch**

---

## 7. Konsolidierte Schemas

**Speicherort**: `backend/bose_api/device_schemas/`

**36 Endpoint-Schemas** konsolidiert aus 96 device-spezifischen XMLs:
- **Identische Schemas** (8): `getActiveWirelessProfile.xml`, `getZone.xml`, `key.xml`, etc.
- **Unterschiedliche Schemas** (21): Markiert mit `<!-- AGENT: ST30 vs ST300 -->` Kommentaren
- **Device-spezifische Endpoints** (7): Markiert mit `<!-- AGENT: ST300 only -->`

**Verwendung**:
```python
# Als Referenz für API-Entwicklung
with open("backend/bose_api/device_schemas/info.xml") as f:
    schema = f.read()  # Beispiel-Response für /info Endpoint

# Für Mock-Tests
@pytest.fixture
def mock_info_response():
    return Path("backend/bose_api/device_schemas/info.xml").read_text()
```

---

## 8. Zusammenfassung - Potenzielle Probleme

### 8.1 Kritische Probleme

**KEINE** identifiziert! 🎉

### 8.2 Mittel-Risiko Issues

| Problem | Impact | Status | Mitigation |
|---------|--------|--------|------------|
| ST300 HDMI-Endpoints geben 404 auf ST30/ST10 | UI-Features | ⚠️ **MUST FIX** | Capability Detection + Error Handling |
| NetworkInfo ist List, nicht Object | MAC-Adress-Zugriff | ✅ **FIXED** (Iteration 1a) | `info.NetworkInfo[0]` |

### 8.3 Niedrig-Risiko Issues

| Problem | Impact | Status | Mitigation |
|---------|--------|--------|------------|
| `/nowPlaying` Schema variiert per Source | Parsing-Logic | ✅ **Library handled** | bosesoundtouchapi macht Safe Access |
| XML Namespaces | SSDP Discovery | ✅ **FIXED** (Iteration 1a) | Namespace-agnostic XPath |
| Content-Type Header | POST Requests | ✅ **Library handled** | bosesoundtouchapi setzt korrekte Headers |

---

## 9. Empfehlungen für STB

### 9.1 MUST HAVE

✅ **1. Capability Detection implementieren**
```python
async def get_device_capabilities(device_id: str) -> DeviceCapabilities:
    """Get device capabilities to enable/disable features."""
    client = await get_client(device_id)
    caps = client.GetCapabilities()
    
    return DeviceCapabilities(
        has_hdmi_control=caps.IsProductCECHDMIControlCapable,
        has_bass_control=caps.IsBassCapable,
        has_advanced_audio=caps.IsAudioProductLevelControlCapable,
        supported_sources=caps.MediaInputsSupported.split(",")
    )
```

✅ **2. Graceful Error Handling**
```python
try:
    result = await client.Get(endpoint)
except SoundTouchError as e:
    if e.ErrorCode == 404:
        logger.info(f"Endpoint {endpoint} not supported on {device.name}")
        return None
    elif e.ErrorCode == 401:
        logger.warning("App-Key required for this endpoint")
        return None
    raise  # Andere Fehler weiterwerfen
```

✅ **3. UI Features modell-abhängig**
```python
# Frontend API Response
{
  "device_id": "AABBCC112233",
  "name": "Living Room",
  "type": "SoundTouch 30 Series III",
  "capabilities": {
    "hdmi_control": false,      # Hide HDMI UI
    "bass_control": true,        # Show Bass slider
    "advanced_audio": false,     # Hide Audio DSP
    "sources": ["BLUETOOTH", "AUX", "INTERNET_RADIO", "SPOTIFY"]
  }
}
```

### 9.2 SHOULD HAVE

⚠️ **4. Firmware-Version Logging**
```python
logger.info(
    f"Device {device.name} initialized",
    extra={
        "device_id": info.DeviceId,
        "device_type": info.DeviceType,
        "firmware": info.Components[0].SoftwareVersion,
        "module_type": info.ModuleType,
        "variant": info.Variant
    }
)
```

⚠️ **5. Schema-Version Tracking**
```python
# In DB: device_schema_version
# Bei API-Änderungen können wir Migrations schreiben
device.schema_version = "28.0.3"  # Aus Firmware-Version
```

### 9.3 NICE TO HAVE

💡 **6. Feature-Toggle System**
```python
# backend/config.py
class FeatureFlags(BaseModel):
    enable_hdmi_controls: bool = True
    enable_advanced_audio: bool = True
    enable_zone_management: bool = True
    
# Manuell Features deaktivieren falls Probleme
```

---

## 10. Test-Matrix

### 10.1 Cross-Model Compatibility Tests

**Status**: ⚠️ **Noch zu implementieren**

```python
# tests/test_cross_model_compatibility.py

@pytest.mark.parametrize("device_type,has_hdmi", [
    ("SoundTouch 30 Series III", False),
    ("SoundTouch 10", False),
    ("SoundTouch 300", True),
])
async def test_hdmi_control_availability(device_type, has_hdmi):
    """Test HDMI control is only available on ST300."""
    mock_device.DeviceType = device_type
    
    if has_hdmi:
        result = await adapter.get_hdmi_config(mock_device)
        assert result is not None
    else:
        with pytest.raises(SoundTouchError) as exc:
            await adapter.get_hdmi_config(mock_device)
        assert exc.value.ErrorCode == 404
```

### 10.2 Regression Tests für gefixte Bugs

**Status**: ✅ **Implementiert**

```python
# tests/test_soundtouch.py
def test_network_info_is_list_regression():
    """Regression: NetworkInfo ist Liste."""
    # ... existing test ...

def test_xml_namespace_parsing_regression():
    """Regression: XML Namespace Handling."""
    # ... existing test ...
```

---

## 11. Migration Guide (falls Schema sich ändert)

**Aktuell**: Keine Migration nötig, alle Schemas sind kompatibel.

**Falls Bose ein Firmware-Update veröffentlichen würde** (unwahrscheinlich):

1. **Neue Schemas sammeln**:
   ```bash
   .\fetch-api-schemas.ps1
   ```

2. **Schemas vergleichen**:
   ```bash
   python backend/bose_api/compare_schemas.py
   ```

3. **Diff analysieren** → Entscheiden ob Breaking Change

4. **bosesoundtouchapi Library aktualisieren**:
   ```bash
   pip install --upgrade bosesoundtouchapi
   ```

5. **STB Adapter anpassen** (falls nötig):
   - Neue Properties in `DiscoveredDevice` Klasse
   - Neue API-Methoden in `BoseSoundTouchClientAdapter`

---

## 12. Changelog

| Datum | Änderung |
|-------|----------|
| 2026-01-29 | **Schema-Konsolidierung abgeschlossen**: 96 device_XX.xml → 36 endpoint.xml in device_schemas/ |
| 2026-01-29 | **Punkt 9.1 DONE**: Capability Detection vollständig implementiert (13/13 Tests ✅) |
| 2026-01-29 | **Punkt 9.2 geplant**: Firmware Tracking & Schema Versioning ausgearbeitet |
| 2026-01-29 | **Punkt 10.1 geplant**: Cross-Model Compatibility Tests detailliert spezifiziert |
| 2026-01-29 | **Punkt 10.2 geplant**: Regression Test Strategy & Templates definiert |
| 2026-01-29 | Regression-Tests dokumentiert: RT-001 (GetSourceList), RT-002 (ErrorCode readonly) |
| 2026-01-29 | bosesoundtouchapi Quirks dokumentiert in README.md Abschnitt 7 |
| 2026-01-29 | 7 ST300-exklusive Endpoints identifiziert |
| 2026-01-29 | NetworkInfo List-Bug dokumentiert (bereits gefixt) |
| 2026-01-29 | XML Namespace-Bug dokumentiert (bereits gefixt) |

---

**Letzte Aktualisierung**: 2026-01-29  
**Nächste Review**: Nach Implementierung von Iteration 1.c (9.2, 10.1, 10.2)
