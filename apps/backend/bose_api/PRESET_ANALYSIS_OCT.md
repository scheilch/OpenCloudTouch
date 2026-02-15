# Bose SoundTouch Preset Analysis - OCT Integration

**Date**: 2026-02-14  
**Device**: Küche (689E194F7D2F) - Bose SoundTouch ST30  
**Firmware**: (see device info)

---

## Problem Statement

**Issue**: Preset 1 saved with `INTERNET_RADIO` + direct stream URL does NOT play  
- Bose Now Playing shows: `source="INVALID_SOURCE"`
- Preset IS stored on device (verified via `/presets` endpoint)
- URL is valid (tested with curl, returns HTTP 200 + audio stream)

---

## Preset Comparison

### ✅ WORKING: TUNEIN Presets (2-6)

**Example: Preset 2 (Charivari 98.6)**
```xml
<ContentItem 
  source="TUNEIN" 
  type="stationurl" 
  location="/v1/playback/station/s3115"   ← RELATIVE PATH!
  sourceAccount="" 
  isPresetable="true">
  <itemName>Charivari 98.6</itemName>
  <containerArt>http://cdn-radiotime-logos.tunein.com/s3115q.png</containerArt>
</ContentItem>
```

**Key Characteristics:**
- ✅ `source="TUNEIN"` - Bose has TuneIn integration
- ✅ `location="/v1/playback/station/s3115"` - **RELATIVE PATH** (not full URL!)
- ✅ Bose internally resolves TuneIn API endpoint
- ✅ `containerArt` provides station logo

---

### ❌ NOT WORKING: INTERNET_RADIO Preset (1)

**Example: Preset 1 (Absolut Relax - Direct Stream)**
```xml
<ContentItem 
  source="INTERNET_RADIO" 
  type="stationurl" 
  location="https://edge71.live-sm.absolutradio.de/absolut-relax/stream/mp3"   ← FULL URL!
  isPresetable="true">
  <itemName>Absolut Relax (Direct)</itemName>
</ContentItem>
```

**Key Characteristics:**
- ❌ `source="INTERNET_RADIO"` - Generic internet radio
- ❌ `location="https://..."` - **ABSOLUTE URL** (direct stream)
- ❌ No `containerArt` (no logo)
- ❌ Bose shows `INVALID_SOURCE` when trying to play

---

## Root Cause Analysis

### Hypothesis 1: Codec/Format Issue
- Stream URL returns: `audio/mpeg` (MP3 stream)
- Bose supports MP3 (verified: TuneIn stations play)
- **UNLIKELY** to be codec issue

### Hypothesis 2: HTTPS Certificate Validation
- Direct URL uses HTTPS with redirect (302 Found)
- Bose firmware might not handle:
  - Self-signed certs
  - Certificate chain validation
  - SNI (Server Name Indication)
- **POSSIBLE** - older firmware might have SSL issues

### Hypothesis 3: Missing Stream Metadata
TuneIn stations have:
- `containerArt` (album art URL)
- TuneIn ecosystem integration
- Metadata endpoints for track info

Direct INTERNET_RADIO:
- No artwork
- No metadata
- Just raw stream URL
- **LIKELY** - Bose might require additional metadata

### Hypothesis 4: Bose Expects LOCAL Endpoint (CORRECT!)
From OpenCloudTouch Project Plan (Iteration 3):
```markdown
* Endpoint /stations/preset/{n}.json (Descriptor aus Mapping)
```

**Original Design Intent:**
1. Save RadioBrowser station to OCT database ✅ (DONE)
2. Program Bose device with **OCT Backend URL**: 
   ```
   location="http://192.168.178.108:7777/stations/preset/1"
   ```
   ❌ (NOT IMPLEMENTED)
3. When PRESET_1 pressed:
   - Bose requests: `GET http://192.168.178.108:7777/stations/preset/1`
   - OCT Backend responds with:
     - **Option A**: Stream Descriptor (XML/JSON with stream URL + metadata)
     - **Option B**: HTTP 302 Redirect to RadioBrowser stream
     - **Option C**: Direct stream proxy (OCT fetches RadioBrowser, pipes to Bose)
4. Bose plays stream

**Why This Would Work:**
- ✅ Local network endpoint (no HTTPS issues)
- ✅ OCT controls response format (can add metadata, artwork, etc.)
- ✅ OCT can handle redirects internally
- ✅ Consistent with TuneIn model (relative path, Bose resolves)
- ✅ OCT becomes "RadioBrowser integration" like TuneIn

---

## Recommended Solution

### Implement `/stations/preset/{n}` Endpoint

**Backend Route:**
```python
# apps/backend/src/opencloudtouch/presets/api/routes.py

@router.get("/stations/preset/{preset_id}")
async def get_preset_station(
    preset_id: int = Path(..., ge=1, le=6),
    device_id: str = Query(...),  # or from session/cookie
    preset_service: PresetService = Depends(get_preset_service),
):
    """
    Return stream descriptor for a preset.
    
    Bose device will call this when PRESET_X button is pressed.
    """
    preset = await preset_service.get_preset(device_id, preset_id)
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not configured")
    
    # Option A: Return XML descriptor (like TuneIn response)
    return Response(
        content=f"""<?xml version="1.0" encoding="UTF-8"?>
<ContentItem source="INTERNET_RADIO" type="stationurl" 
             location="{preset.station_url}" 
             isPresetable="true">
  <itemName>{preset.station_name}</itemName>
  <containerArt>{preset.station_favicon or ''}</containerArt>
</ContentItem>""",
        media_type="application/xml"
    )
    
    # Option B: HTTP 302 Redirect to stream
    # return Response(status_code=302, headers={"Location": preset.station_url})
```

**Update `store_preset()` to use OCT Backend URL:**
```python
# apps/backend/src/opencloudtouch/devices/adapter.py

async def store_preset(
    self,
    preset_number: int,
    station_url: str,
    station_name: str,
    oct_backend_url: str,  # NEW: OCT backend base URL
) -> None:
    """Store preset on Bose device pointing to OCT backend."""
    from bosesoundtouchapi.models.preset import Preset
    
    # Use OCT backend as proxy instead of direct stream URL
    proxy_url = f"{oct_backend_url}/stations/preset/{preset_number}?device_id={self.device_id}"
    
    preset = Preset(
        presetId=preset_number,
        source="INTERNET_RADIO",
        typeValue="stationurl",
        location=proxy_url,  # ← Point to OCT backend!
        name=station_name,
        isPresetable=True,
    )
    
    self._client.StorePreset(preset)
```

**Expected Preset on Bose Device:**
```xml
<preset id="1">
  <ContentItem 
    source="INTERNET_RADIO" 
    type="stationurl" 
    location="http://192.168.178.108:7777/stations/preset/1?device_id=689E194F7D2F"
    isPresetable="true">
    <itemName>Absolut Relax</itemName>
  </ContentItem>
</preset>
```

---

## Benefits of OCT Backend Proxy Approach

1. **No HTTPS Issues**: Local HTTP endpoint (no certificate validation)
2. **Metadata Control**: OCT can inject artwork, track info from RadioBrowser API
3. **Redirect Handling**: OCT resolves RadioBrowser redirects internally
4. **Fallback Logic**: OCT can try alternative stream URLs if one fails
5. **Analytics**: OCT can log which presets are played, how often
6. **Dynamic Updates**: Change stream URL in DB without reprogramming Bose device
7. **Multi-Device Support**: Same preset number on different devices can map to different stations

---

## Test Plan

1. Implement `/stations/preset/{n}` endpoint
2. Update `store_preset()` to use OCT backend URL
3. Save Preset 1 again (will overwrite current one)
4. Check Bose `/presets` - should show `location="http://192.168.178.108:7777/..."`
5. Press PRESET_1 button
6. Bose should request OCT backend
7. OCT logs should show: `GET /stations/preset/1?device_id=689E194F7D2F`
8. OCT returns stream descriptor or redirect
9. Bose plays station ✅

---

## Alternative: Test Direct HTTP (No HTTPS)

If we want to test without implementing proxy first:

1. Find HTTP (not HTTPS) stream URL from RadioBrowser
2. Use HTTP stream in preset
3. See if `INVALID_SOURCE` still occurs

**Test Stream:**
```bash
# Find HTTP streams
curl -X POST "http://all.api.radio-browser.info/json/stations/search" \
  -H "Content-Type: application/json" \
  -d '{"name":"Absolut Relax","limit":5}' | jq '.[] | select(.url | startswith("http://"))'
```

---

## Status

- ✅ Preset storage to OCT database: WORKING
- ✅ Bose `/storePreset` API call: WORKING
- ✅ Preset visible in Bose device preset list: VERIFIED
- ❌ Playback of INTERNET_RADIO preset: **FAILS** (`INVALID_SOURCE`)
- ⏸️ OCT Backend proxy endpoint: **NOT IMPLEMENTED** (original plan)

**Next Step**: Implement `/stations/preset/{n}` endpoint (Iteration 3 completion)
