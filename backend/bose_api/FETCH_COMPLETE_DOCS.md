# Complete API Schema Fetcher - Documentation

## Overview

`fetch-api-schemas-complete.ps1` is an advanced PowerShell script that performs **complete reverse engineering** of all SoundTouch API endpoints across all device models.

## Features

### 1. Intelligent Endpoint Discovery
- Fetches `/supportedURLs` from each device to get the complete endpoint list
- Automatically discovers model-specific endpoints (ST300 HDMI/Audio features)
- Cross-references all 3 devices to identify common vs. exclusive endpoints

### 2. Multi-Method Support
- **GET requests**: Standard read-only endpoints (`/info`, `/volume`, `/nowPlaying`, etc.)
- **POST requests**: Control endpoints with payload templates (`/key`, `/volume`, `/preset`, etc.)
- **PUT requests**: Rare update endpoints
- **Empty POST**: Some endpoints accept POST without payload

### 3. Payload Template Library
Built-in templates for 20+ POST/PUT endpoints:
- Key simulation (`/key` - POWER, PRESET_1-6, VOLUME_UP/DOWN)
- Volume control (`/volume` - 0-100)
- Bass/balance (`/bass`, `/balance` - -9 to +9)
- Preset management (`/preset` - store radio stations)
- Multi-room zones (`/setZone`, `/addZoneSlave`, `/removeZoneSlave`)
- ST300 HDMI controls (`/productcechdmicontrol`, `/producthdmiassignmentcontrols`)
- ST300 audio DSP (`/audiodspcontrols`, `/audioproductlevelcontrols`)

### 4. Error Handling
- **404 Not Found**: Endpoint not supported on this model → [SKIP]
- **401 Unauthorized**: App-Key required → [401-AUTH] with comment in XML
- **400 Bad Request**: Invalid payload → [400-BAD] with comment in XML
- **Timeouts**: 5 second timeout per request
- **Caching**: Skips already-fetched files (use `$env:FORCE_REFETCH=1` to override)

### 5. Comprehensive Metadata
Each fetched XML includes:
```xml
<!-- Fetched: 2026-01-29 14:23:45 | Method: POST | Device: SoundTouch 300 | Status: OK-POST -->
<!-- Description: Set volume level 0-100 -->
<volume>20</volume>
```

## Usage

### Basic Execution
```powershell
.\fetch-api-schemas-complete.ps1
```

### Force Re-fetch (ignore cache)
```powershell
$env:FORCE_REFETCH = 1
.\fetch-api-schemas-complete.ps1
```

### Expected Output
```
=====================================================================
  COMPLETE SOUNDTOUCH API SCHEMA FETCHER WITH REVERSE ENGINEERING
=====================================================================

Features:
  - Fetches ALL endpoints (GET/POST/PUT)
  - Analyzes supportedURLs.xml from each device
  - Reverse-engineers POST endpoints with payload templates
  - Handles 404/401/400 errors gracefully
  - Generates complete schema documentation

Device: SoundTouch 30 - ST30_Wohnzimmer (192.0.2.78)
======================================================================
  Fetching supportedURLs... [Found: 102 endpoints]

  /info -> [OK]
  /volume -> [OK-POST]
  /nowPlaying -> [OK]
  /key -> [OK-POST]
  /productcechdmicontrol -> [SKIP]  # Not supported on ST30
  /bass -> [OK-POST]
  ...

Device: SoundTouch 300 - ST300_TV (192.0.2.83)
======================================================================
  Fetching supportedURLs... [Found: 109 endpoints]

  /info -> [OK]
  /productcechdmicontrol -> [OK-POST]  # ST300 exclusive
  /audiodspcontrols -> [OK-POST]       # ST300 exclusive
  ...

=====================================================================
  FETCH STATISTICS
=====================================================================

Total schemas fetched: 296
Total skipped (404):   18

Endpoint Coverage:
  /info (GET) -> 3 devices
  /volume (POST) -> 3 devices
  /productcechdmicontrol (POST) -> 1 device
  /audiodspcontrols (POST) -> 1 device
  ...

Next steps:
  1. Run: python backend/bose_api/consolidate_schemas.py
  2. Review: backend/bose_api/device_schemas/*.xml
  3. Update: backend/bose_api/SCHEMA_DIFFERENCES.md
```

## Output Structure

### File Naming
```
backend/bose_api/
├── device_78_info.xml              # ST30: GET /info
├── device_78_volume.xml            # ST30: POST /volume
├── device_79_info.xml              # ST10: GET /info
├── device_83_info.xml              # ST300: GET /info
├── device_83_productcechdmicontrol.xml  # ST300 only
└── ...
```

### Status Codes
- `[OK]`: GET request successful
- `[OK-POST]`: POST request with template payload successful
- `[OK-EMPTY]`: POST request with empty payload successful
- `[OK-PUT]`: PUT request successful
- `[SKIP]`: 404 Not Found (endpoint not supported)
- `[401-AUTH]`: Unauthorized (App-Key required)
- `[400-BAD]`: Bad Request (invalid payload)
- `[CACHED]`: File already exists

## Reverse Engineering Algorithm

```
FOR each endpoint:
  1. TRY GET request
     IF successful → SAVE as [OK]
     
  2. ELSE IF endpoint in payloadTemplates:
     TRY POST with template payload
     IF successful → SAVE as [OK-POST]
     
  3. ELSE TRY POST with empty payload
     IF successful → SAVE as [OK-EMPTY]
     
  4. ELSE TRY PUT with empty payload
     IF successful → SAVE as [OK-PUT]
     
  5. ELSE → SKIP (404/401/400/timeout)
```

## Known Limitations

1. **App-Key Protected Endpoints**: Endpoints requiring authentication (e.g., `/requestToken`) return 401
2. **Stateful Endpoints**: Some endpoints require specific device state (e.g., `/nowPlaying` returns empty if nothing is playing)
3. **Parametrized Endpoints**: Endpoints requiring URL parameters (e.g., `/searchStation?name=...`) are fetched without parameters
4. **Navigation/Search**: POST-only endpoints (`/navigate`, `/search`) require specific content item payloads

## Integration with Workflow

### Step 1: Fetch Schemas
```powershell
.\fetch-api-schemas-complete.ps1
```

### Step 2: Consolidate
```powershell
python backend/bose_api/consolidate_schemas.py
```
This merges `device_78_volume.xml`, `device_79_volume.xml`, `device_83_volume.xml` → `device_schemas/volume.xml`

### Step 3: Analyze Differences
```powershell
python backend/bose_api/analyze_api.py
```
Generates model-specific endpoint lists and identifies schema variations

### Step 4: Document
Update `backend/bose_api/SCHEMA_DIFFERENCES.md` with findings

## Extending Payload Templates

To add a new endpoint:

```powershell
$payloadTemplates['/myEndpoint'] = @{
    Method = 'POST'
    Payload = '<myEndpoint><param>value</param></myEndpoint>'
    Description = 'What this endpoint does'
}
```

## Advanced Use Cases

### Fetch only ST300 exclusive endpoints
```powershell
$devices = @(@{Name='ST300_TV'; IP='192.0.2.83'; ID='83'; Model='SoundTouch 300'})
.\fetch-api-schemas-complete.ps1
```

### Debug specific endpoint
```powershell
# Add verbose output for specific endpoint
$VerbosePreference = 'Continue'
.\fetch-api-schemas-complete.ps1
```

## Comparison to Original Script

| Feature | `fetch-api-schemas.ps1` | `fetch-api-schemas-complete.ps1` |
|---------|-------------------------|----------------------------------|
| Endpoint Discovery | Hardcoded list (54 endpoints) | Dynamic via `/supportedURLs` (109 endpoints) |
| HTTP Methods | GET only | GET, POST, PUT |
| Payload Support | None | 20+ built-in templates |
| Error Handling | Silent fail | 404/401/400 detection + logging |
| Metadata | None | Fetch time, method, device, description |
| Caching | No | Yes (skip existing files) |
| Statistics | No | Endpoint coverage report |
| Model Detection | Manual IP list | Automatic via `/supportedURLs` |

## Troubleshooting

### "Could not fetch supportedURLs"
- Check device is online: `ping 192.0.2.78`
- Verify port 8090 is open: `Test-NetConnection -ComputerName 192.0.2.78 -Port 8090`
- Check firewall settings on NAS Server/host

### Many [SKIP] entries
- Normal behavior - devices don't support all endpoints
- ST30/ST10 will skip 7 HDMI/Audio endpoints (ST300 exclusive)
- Some endpoints are deprecated or require special state

### [401-AUTH] errors
- These endpoints require App-Key authentication
- Document in SCHEMA_DIFFERENCES.md as "auth required"
- Not a script error

### [400-BAD] errors
- Payload template may be incorrect
- Update `$payloadTemplates` with correct XML structure
- Check Bose SoundTouch Web API PDF for correct format

## Future Enhancements

1. **Interactive Mode**: Ask user which endpoints to re-fetch
2. **Diff Mode**: Compare new schemas with existing files
3. **JSON Export**: Convert XML schemas to JSON for easier parsing
4. **Parallel Fetching**: Use PowerShell jobs to fetch from multiple devices simultaneously
5. **Payload Generation**: Auto-generate payloads from GET responses (e.g., GET /volume → POST with current value)

## References

- Bose SoundTouch Web API PDF: https://assets.bosecreative.com/m/496577402d128874/original/SoundTouch-Web-API.pdf
- SCHEMA_DIFFERENCES.md: Complete analysis of all 109 endpoints
- README.md: API overview and endpoint reference
