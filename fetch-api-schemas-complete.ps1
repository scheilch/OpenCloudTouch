# Complete SoundTouch API Schema Fetcher with Reverse Engineering
# Fetches ALL endpoints including POST/PUT methods by analyzing supportedURLs
# and using intelligent payload generation based on known schema patterns

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

# Device configurations
$devices = @(
    @{Name='ST30_Living Room'; IP='192.0.2.78'; ID='78'; Model='SoundTouch 30'},
    @{Name='ST10_Kueche'; IP='192.0.2.79'; ID='79'; Model='SoundTouch 10'},
    @{Name='ST300_TV'; IP='192.0.2.83'; ID='83'; Model='SoundTouch 300'}
)

$outputDir = "backend\bose_api"

# Known payload templates for POST/PUT endpoints (from Bose SoundTouch Web API PDF)
$payloadTemplates = @{
    '/key' = @{
        Method = 'POST'
        Payload = '<key state="press" sender="Gabbo">POWER</key>'
        Description = 'Simulate key press (POWER, PRESET_1-6, VOLUME_UP/DOWN, etc.)'
    }
    '/volume' = @{
        Method = 'POST'
        Payload = '<volume>20</volume>'
        Description = 'Set volume level 0-100'
    }
    '/bass' = @{
        Method = 'POST'
        Payload = '<bass>0</bass>'
        Description = 'Set bass level -9 to +9'
    }
    '/name' = @{
        Method = 'POST'
        Payload = '<name>My SoundTouch</name>'
        Description = 'Set device friendly name'
    }
    '/preset' = @{
        Method = 'POST'
        Payload = '<ContentItem source="INTERNET_RADIO" type="stationurl" location="http://example.com/stream.mp3" sourceAccount=""><itemName>Test Station</itemName></ContentItem>'
        Description = 'Store preset (1-6)'
    }
    '/setZone' = @{
        Method = 'POST'
        Payload = '<zone master="192.168.1.10"><member ipaddress="192.168.1.11">B92C7D383488</member></zone>'
        Description = 'Create multi-room zone'
    }
    '/removeZoneSlave' = @{
        Method = 'POST'
        Payload = '<zone master="192.168.1.10"><member ipaddress="192.168.1.11">B92C7D383488</member></zone>'
        Description = 'Remove device from zone'
    }
    '/addZoneSlave' = @{
        Method = 'POST'
        Payload = '<zone master="192.168.1.10"><member ipaddress="192.168.1.11">B92C7D383488</member></zone>'
        Description = 'Add device to zone'
    }
    '/select' = @{
        Method = 'POST'
        Payload = '<ContentItem source="INTERNET_RADIO" sourceAccount=""></ContentItem>'
        Description = 'Select and play source'
    }
    '/speaker' = @{
        Method = 'POST'
        Payload = '<speaker>TV</speaker>'
        Description = 'Select speaker output (ST300: TV, FRONT_CENTER, STEREO_NORMAL)'
    }
    '/balance' = @{
        Method = 'POST'
        Payload = '<balance>0</balance>'
        Description = 'Set audio balance -9 (left) to +9 (right)'
    }
    '/audiodspcontrols' = @{
        Method = 'POST'
        Payload = '<audiodspcontrols><audiodspcontrol name="videosyncaudio">AUTO</audiodspcontrol></audiodspcontrols>'
        Description = 'ST300: Audio DSP settings'
    }
    '/audioproductlevelcontrols' = @{
        Method = 'POST'
        Payload = '<audioproductlevelcontrols><audioproductlevelcontrol name="centerleveltrim" type="decibel">0</audioproductlevelcontrol></audioproductlevelcontrols>'
        Description = 'ST300: Audio level controls (center, subwoofer trim)'
    }
    '/audioproducttonecontrols' = @{
        Method = 'POST'
        Payload = '<audioproducttonecontrols><audioproducttonecontrol name="bass">0</audioproducttonecontrol></audioproducttonecontrols>'
        Description = 'ST300: Tone controls (bass, treble)'
    }
    '/productcechdmicontrol' = @{
        Method = 'POST'
        Payload = '<productcechdmicontrol><hdmicec>AUTO</hdmicec></productcechdmicontrol>'
        Description = 'ST300: HDMI CEC control (AUTO, ON, OFF)'
    }
    '/producthdmiassignmentcontrols' = @{
        Method = 'POST'
        Payload = '<producthdmiassignmentcontrols><producthdmiassignment name="HDMI_1">TV</producthdmiassignment></producthdmiassignmentcontrols>'
        Description = 'ST300: HDMI input assignments'
    }
    '/systemtimeoutcontrol' = @{
        Method = 'POST'
        Payload = '<systemtimeoutcontrol><timeout>20</timeout></systemtimeoutcontrol>'
        Description = 'ST300: System timeout in minutes'
    }
    '/DSPMonoStereo' = @{
        Method = 'POST'
        Payload = '<DSPMonoStereo>STEREO</DSPMonoStereo>'
        Description = 'Set audio output mode (MONO, STEREO)'
    }
    '/clockTime' = @{
        Method = 'POST'
        Payload = '<clockTime><time utc="1234567890" timezone="Europe/Berlin">12:34</time><clockdisplay>ON</clockdisplay></clockTime>'
        Description = 'Set clock time and display'
    }
    '/language' = @{
        Method = 'POST'
        Payload = '<language>en-us</language>'
        Description = 'Set device language'
    }
    '/powerManagement' = @{
        Method = 'POST'
        Payload = '<powerManagement><autoWakeup>ENABLE</autoWakeup></powerManagement>'
        Description = 'Power management settings'
    }
    '/rebroadcastlatencymode' = @{
        Method = 'POST'
        Payload = '<rebroadcastlatencymode>LOW</rebroadcastlatencymode>'
        Description = 'Multiroom latency mode (LOW, HIGH)'
    }
}

# Endpoints that require special handling (read-only state endpoints)
$stateOnlyEndpoints = @(
    '/nowPlaying',          # Current playback state
    '/status',              # Device status
    '/capabilities',        # Device capabilities
    '/info',                # Device information
    '/networkInfo',         # Network configuration
    '/sources',             # Available sources
    '/presets',             # Stored presets
    '/recents',             # Recent playback history
    '/bluetoothInfo',       # Bluetooth pairing state
    '/bassCapabilities',    # Bass control capabilities
    '/supportedURLs',       # List of supported endpoints
    '/trackInfo',           # Current track metadata
    '/stationInfo',         # Current station metadata
    '/genreStations',       # Genre-based station list
    '/searchStation',       # Station search results (requires query param)
    '/listMediaServers',    # UPnP/DLNA media servers
    '/serviceAvailability', # Service availability status
    '/soundTouchConfigurationStatus',  # Configuration state
    '/sourceDiscoveryStatus',          # Source discovery state
    '/netStats',            # Network statistics
    '/systemtimeout',       # System timeout value (use /systemtimeoutcontrol for POST)
    '/test',                # Test endpoint
    '/notification',        # WebSocket notification endpoint
    '/introspect',          # API introspection
    '/navigate',            # Content navigation (requires POST with location)
    '/search',              # Content search (requires POST with query)
    '/bookmark',            # Content bookmarks
    '/requestToken',        # OAuth token request
    '/getZone',             # Current zone configuration
    '/getGroup',            # Current group configuration (ST10 only)
    '/getActiveWirelessProfile',  # Active WiFi profile
    '/pdo',                 # Product Data Object
    '/marge',               # Unknown (possibly deprecated)
    '/masterMsg',           # Zone master messages
    '/slaveMsg',            # Zone slave messages
    '/nameSource'           # Source name mapping
)

function Get-SupportedEndpoints {
    param([string]$DeviceIP)
    
    try {
        $url = "http://${DeviceIP}:8090/supportedURLs"
        $response = Invoke-RestMethod -Uri $url -Method GET -TimeoutSec 5
        
        # Parse XML to extract URLs
        $urls = $response.supportedURLs.URL | ForEach-Object { $_.location }
        return $urls
    } catch {
        Write-Host "    WARNING: Could not fetch supportedURLs from $DeviceIP" -ForegroundColor Yellow
        return @()
    }
}

function Get-EndpointSchema {
    param(
        [string]$DeviceIP,
        [string]$Endpoint,
        [string]$Method = 'GET',
        [string]$Payload = $null
    )
    
    $url = "http://${DeviceIP}:8090${Endpoint}"
    
    try {
        if ($Method -eq 'GET') {
            $response = Invoke-RestMethod -Uri $url -Method GET -TimeoutSec 5
        } else {
            $headers = @{'Content-Type' = 'application/xml'}
            $response = Invoke-RestMethod -Uri $url -Method $Method -Body $Payload -Headers $headers -TimeoutSec 5
        }
        
        # Convert response to XML string
        if ($response -is [System.Xml.XmlDocument]) {
            return $response.OuterXml
        } elseif ($response -is [string]) {
            return $response
        } else {
            return $response | ConvertTo-Json -Depth 10
        }
    } catch {
        # Check for specific HTTP errors
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
            if ($statusCode -eq 404) {
                return $null  # Endpoint not supported
            } elseif ($statusCode -eq 401) {
                Write-Host " [401-AUTH]" -ForegroundColor Yellow -NoNewline
                return "<!-- 401 Unauthorized: App-Key required -->"
            } elseif ($statusCode -eq 400) {
                Write-Host " [400-BAD]" -ForegroundColor Magenta -NoNewline
                return "<!-- 400 Bad Request: Invalid payload -->"
            }
        }
        return $null
    }
}

function Reverse-EngineerEndpoint {
    param(
        [string]$DeviceIP,
        [string]$Endpoint
    )
    
    # Try GET first
    $schema = Get-EndpointSchema -DeviceIP $DeviceIP -Endpoint $Endpoint -Method 'GET'
    if ($schema) {
        return @{Schema = $schema; Method = 'GET'; Status = 'OK'}
    }
    
    # Check if we have a known POST template
    if ($payloadTemplates.ContainsKey($Endpoint)) {
        $template = $payloadTemplates[$Endpoint]
        $schema = Get-EndpointSchema -DeviceIP $DeviceIP -Endpoint $Endpoint -Method $template.Method -Payload $template.Payload
        
        if ($schema) {
            return @{Schema = $schema; Method = $template.Method; Status = 'OK-POST'; Description = $template.Description}
        }
    }
    
    # Try POST with empty payload (some endpoints accept this)
    $schema = Get-EndpointSchema -DeviceIP $DeviceIP -Endpoint $Endpoint -Method 'POST' -Payload ''
    if ($schema) {
        return @{Schema = $schema; Method = 'POST'; Status = 'OK-EMPTY'}
    }
    
    # Try PUT (rare, but some endpoints use it)
    $schema = Get-EndpointSchema -DeviceIP $DeviceIP -Endpoint $Endpoint -Method 'PUT' -Payload ''
    if ($schema) {
        return @{Schema = $schema; Method = 'PUT'; Status = 'OK-PUT'}
    }
    
    return @{Schema = $null; Method = 'NONE'; Status = 'SKIP'}
}

# Main execution
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  COMPLETE SOUNDTOUCH API SCHEMA FETCHER WITH REVERSE ENGINEERING" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Features:" -ForegroundColor Green
Write-Host "  - Fetches ALL endpoints (GET/POST/PUT)" -ForegroundColor Gray
Write-Host "  - Analyzes supportedURLs.xml from each device" -ForegroundColor Gray
Write-Host "  - Reverse-engineers POST endpoints with payload templates" -ForegroundColor Gray
Write-Host "  - Handles 404/401/400 errors gracefully" -ForegroundColor Gray
Write-Host "  - Generates complete schema documentation" -ForegroundColor Gray
Write-Host ""

$totalFetched = 0
$totalSkipped = 0
$totalErrors = 0
$endpointStats = @{}

foreach ($device in $devices) {
    Write-Host "Device: $($device.Model) - $($device.Name) ($($device.IP))" -ForegroundColor Yellow
    Write-Host ("=" * 70) -ForegroundColor DarkGray
    
    # Get supported endpoints for this device
    Write-Host "  Fetching supportedURLs..." -NoNewline
    $supportedEndpoints = Get-SupportedEndpoints -DeviceIP $device.IP
    Write-Host " [Found: $($supportedEndpoints.Count) endpoints]" -ForegroundColor Green
    Write-Host ""
    
    foreach ($endpoint in $supportedEndpoints) {
        $filename = "device_$($device.ID)$($endpoint.Replace('/', '_')).xml"
        $filePath = Join-Path $outputDir $filename
        
        Write-Host "  $endpoint" -NoNewline -ForegroundColor White
        Write-Host " -> " -NoNewline -ForegroundColor DarkGray
        
        # Skip if already exists (unless force flag is set)
        if ((Test-Path $filePath) -and -not $env:FORCE_REFETCH) {
            Write-Host "[CACHED]" -ForegroundColor DarkCyan
            $totalFetched++
            continue
        }
        
        # Reverse engineer the endpoint
        $result = Reverse-EngineerEndpoint -DeviceIP $device.IP -Endpoint $endpoint
        
        if ($result.Schema) {
            # Add metadata comment
            $metadata = "<!-- Fetched: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | Method: $($result.Method) | Device: $($device.Model) | Status: $($result.Status) -->`n"
            if ($result.Description) {
                $metadata += "<!-- Description: $($result.Description) -->`n"
            }
            $content = $metadata + $result.Schema
            
            $content | Out-File -Encoding UTF8 $filePath
            Write-Host "[$($result.Status)]" -ForegroundColor Green
            $totalFetched++
            
            # Track endpoint statistics
            if (-not $endpointStats.ContainsKey($endpoint)) {
                $endpointStats[$endpoint] = @{Count = 0; Methods = @{}}
            }
            $endpointStats[$endpoint].Count++
            $endpointStats[$endpoint].Methods[$result.Method] = $true
        } else {
            Write-Host "[$($result.Status)]" -ForegroundColor Gray
            $totalSkipped++
        }
    }
    
    Write-Host ""
}

# Generate statistics report
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  FETCH STATISTICS" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total schemas fetched: " -NoNewline
Write-Host $totalFetched -ForegroundColor Green
Write-Host "Total skipped (404):   " -NoNewline
Write-Host $totalSkipped -ForegroundColor Yellow
Write-Host ""
Write-Host "Endpoint Coverage:" -ForegroundColor White
$endpointStats.GetEnumerator() | Sort-Object Name | ForEach-Object {
    $endpoint = $_.Key
    $stats = $_.Value
    $methods = ($stats.Methods.Keys -join ', ')
    $deviceCount = $stats.Count
    
    $color = if ($deviceCount -eq 3) { 'Green' } elseif ($deviceCount -eq 1) { 'Yellow' } else { 'Cyan' }
    Write-Host "  $endpoint" -NoNewline -ForegroundColor White
    Write-Host " ($methods)" -NoNewline -ForegroundColor Gray
    Write-Host " -> $deviceCount devices" -ForegroundColor $color
}
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Run: python backend/bose_api/consolidate_schemas.py" -ForegroundColor Gray
Write-Host "  2. Review: backend/bose_api/device_schemas/*.xml" -ForegroundColor Gray
Write-Host "  3. Update: backend/bose_api/SCHEMA_DIFFERENCES.md" -ForegroundColor Gray
Write-Host ""
Write-Host "Done!" -ForegroundColor Green
Write-Host ""
