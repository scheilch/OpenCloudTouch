#!/usr/bin/env python3
"""
Compare three sources of SoundTouch API knowledge:
1. Official Bose Web API Documentation (PDF)
2. Collected XML Schemas from devices
3. bosesoundtouchapi Python Library
"""

import re
from pathlib import Path
from typing import Dict, Set, List


SCRIPT_DIR = Path(__file__).parent


def parse_official_docs() -> Dict[str, Dict]:
    """Parse endpoints from official Bose documentation."""
    docs_file = SCRIPT_DIR / "official" / "bose_api_documentation.txt"
    
    if not docs_file.exists():
        print(f"ERROR: {docs_file} not found")
        return {}
    
    text = docs_file.read_text(encoding='utf-8')
    
    endpoints = {}
    
    # Parse table of contents for endpoint list
    # Pattern: 6.X /endpoint_name
    toc_pattern = r'\d+\.\d+\s+/(\w+)'
    for match in re.finditer(toc_pattern, text):
        endpoint = match.group(1)
        endpoints[endpoint] = {
            'source': 'official_docs',
            'methods': [],
            'description': ''
        }
    
    # Try to find GET/POST info for each endpoint
    for endpoint in list(endpoints.keys()):
        # Look for section describing this endpoint
        section_pattern = rf'/({endpoint})\s*\n.*?Description:(.*?)(?:GET:|POST:)'
        section_match = re.search(section_pattern, text, re.DOTALL | re.IGNORECASE)
        
        if section_match:
            description = section_match.group(2).strip()
            endpoints[endpoint]['description'] = ' '.join(description.split()[:50])
        
        # Check for GET
        if re.search(rf'/({endpoint}).*?GET:\s*\n(?!N/A)', text, re.DOTALL):
            endpoints[endpoint]['methods'].append('GET')
        
        # Check for POST
        if re.search(rf'/({endpoint}).*?POST:\s*\n(?!N/A)', text, re.DOTALL):
            endpoints[endpoint]['methods'].append('POST')
    
    return endpoints


def parse_collected_schemas() -> Dict[str, Dict]:
    """Parse endpoints from our collected device schemas."""
    consolidated_dir = SCRIPT_DIR / "consolidated"
    
    if not consolidated_dir.exists():
        print(f"ERROR: {consolidated_dir} not found")
        return {}
    
    endpoints = {}
    
    for xml_file in consolidated_dir.glob("*.xml"):
        endpoint = xml_file.stem
        
        # Read file to check if device-specific
        content = xml_file.read_text(encoding='utf-8')
        
        is_device_specific = "DEVICE-SPECIFIC ENDPOINT" in content
        available_on = []
        missing_on = []
        
        if is_device_specific:
            # Extract which models support it
            if "SoundTouch 300" in content and "Available on" in content:
                available_on.append("ST300")
            if "SoundTouch 30" in content and "Available on" in content:
                available_on.append("ST30")
            if "SoundTouch 10" in content and "Available on" in content:
                available_on.append("ST10")
        else:
            available_on = ["ST30", "ST10", "ST300"]
        
        endpoints[endpoint] = {
            'source': 'collected_schemas',
            'device_specific': is_device_specific,
            'available_on': available_on,
            'file': xml_file.name
        }
    
    return endpoints


def parse_library_endpoints() -> Dict[str, Dict]:
    """Parse endpoints from bosesoundtouchapi library source."""
    # We already documented this from GitHub search
    # These are the SoundTouchNodes from the library
    
    library_endpoints = [
        'addMusicServiceAccount', 'addStereoPair', 'addWirelessProfile', 'addZoneSlave',
        'artistAndPlaylistInfo', 'audiodspcontrols', 'audioproductlevelcontrols',
        'audioproducttonecontrols', 'audiospeakerattributeandsetting',
        'balance', 'bass', 'bassCapabilities', 'bluetoothInfo',
        'capabilities', 'clearBluetoothPaired', 'clockConfig', 'clockDisplay', 'clockTime',
        'createZone', 'DSPMonoStereo',
        'enterBluetoothPairing', 'getActiveWirelessProfile', 'getBCOReset', 'getGroup', 'getZone',
        'info', 'introspect', 'key', 'language', 'listMediaServers',
        'name', 'navigate', 'netStats', 'networkInfo', 'nowPlaying',
        'powerManagement', 'powersaving', 'presets', 'productcechdmicontrol',
        'producthdmiassignmentcontrols',
        'rebroadcastlatencymode', 'recents', 'removeGroup', 'removeMusicServiceAccount',
        'removePreset', 'removeStation', 'removeStereoPair', 'removeZoneSlave',
        'requestToken', 'search', 'searchStation', 'select', 'serviceAvailability',
        'setMargeAccount', 'setZone', 'simpleSetup', 'soundTouchConfigurationStatus',
        'sources', 'speaker', 'supportedURLs', 'swUpdateAbort', 'swUpdateCheck',
        'swUpdateQuery', 'swUpdateStart', 'systemtimeout', 'systemtimeoutcontrol',
        'test', 'trackInfo', 'userActivity', 'userRating', 'userTrackControl',
        'volume', 'volumeUpdated', 'wirelessProfile'
    ]
    
    endpoints = {}
    for endpoint in library_endpoints:
        endpoints[endpoint] = {
            'source': 'library',
            'in_soundtouchnodes': True
        }
    
    return endpoints


def compare_sources() -> Dict:
    """Compare all three sources and identify gaps."""
    print("=" * 80)
    print("SoundTouch API Sources Comparison")
    print("=" * 80)
    
    print("\n1. Parsing official Bose documentation...")
    official = parse_official_docs()
    print(f"   Found {len(official)} endpoints")
    
    print("\n2. Parsing collected device schemas...")
    schemas = parse_collected_schemas()
    print(f"   Found {len(schemas)} endpoints")
    
    print("\n3. Parsing bosesoundtouchapi library...")
    library = parse_library_endpoints()
    print(f"   Found {len(library)} endpoints")
    
    # Create comprehensive comparison
    all_endpoints = set(official.keys()) | set(schemas.keys()) | set(library.keys())
    print(f"\n   Total unique endpoints: {len(all_endpoints)}")
    
    comparison = {}
    for endpoint in sorted(all_endpoints):
        comparison[endpoint] = {
            'in_official': endpoint in official,
            'in_schemas': endpoint in schemas,
            'in_library': endpoint in library,
            'official_info': official.get(endpoint, {}),
            'schema_info': schemas.get(endpoint, {}),
            'library_info': library.get(endpoint, {})
        }
    
    return comparison


def generate_report(comparison: Dict):
    """Generate detailed comparison report."""
    output_file = SCRIPT_DIR / "official" / "API_COMPARISON.md"
    
    with output_file.open('w', encoding='utf-8') as f:
        f.write("# SoundTouch API 3-Way Comparison\n\n")
        f.write("**Date**: 2026-01-29\n\n")
        f.write("**Sources**:\n")
        f.write("1. **Official Bose Docs**: `2025.12.18 SoundTouch Web API.pdf`\n")
        f.write("2. **Collected Schemas**: 37 endpoints from 3 devices (ST30, ST10, ST300)\n")
        f.write("3. **Python Library**: bosesoundtouchapi 1.0.86 (SoundTouchNodes)\n\n")
        f.write("---\n\n")
        
        # Summary statistics
        only_official = [e for e, d in comparison.items() if d['in_official'] and not d['in_schemas'] and not d['in_library']]
        only_schemas = [e for e, d in comparison.items() if not d['in_official'] and d['in_schemas'] and not d['in_library']]
        only_library = [e for e, d in comparison.items() if not d['in_official'] and not d['in_schemas'] and d['in_library']]
        in_all_three = [e for e, d in comparison.items() if d['in_official'] and d['in_schemas'] and d['in_library']]
        missing_from_official = [e for e, d in comparison.items() if not d['in_official']]
        
        f.write("## Summary\n\n")
        f.write(f"| Category | Count |\n")
        f.write(f"|----------|-------|\n")
        f.write(f"| **Total Unique Endpoints** | {len(comparison)} |\n")
        f.write(f"| In all 3 sources | {len(in_all_three)} |\n")
        f.write(f"| Only in Official Docs | {len(only_official)} |\n")
        f.write(f"| Only in Collected Schemas | {len(only_schemas)} |\n")
        f.write(f"| Only in Python Library | {len(only_library)} |\n")
        f.write(f"| Missing from Official Docs | {len(missing_from_official)} |\n\n")
        
        # Detailed comparison table
        f.write("## Detailed Endpoint Comparison\n\n")
        f.write("| Endpoint | Official | Schemas | Library | Notes |\n")
        f.write("|----------|----------|---------|---------|-------|\n")
        
        for endpoint in sorted(comparison.keys()):
            data = comparison[endpoint]
            official_mark = "✅" if data['in_official'] else "❌"
            schemas_mark = "✅" if data['in_schemas'] else "❌"
            library_mark = "✅" if data['in_library'] else "❌"
            
            # Notes
            notes = []
            if data.get('schema_info', {}).get('device_specific'):
                available = data['schema_info'].get('available_on', [])
                notes.append(f"Device-specific: {', '.join(available)}")
            
            if not data['in_official']:
                notes.append("Missing from official docs")
            
            notes_str = "; ".join(notes) if notes else ""
            
            f.write(f"| `/{endpoint}` | {official_mark} | {schemas_mark} | {library_mark} | {notes_str} |\n")
        
        # Gaps and Issues
        f.write("\n## Gaps and Potential Issues\n\n")
        
        f.write("### 1. Endpoints Missing from Official Documentation\n\n")
        if missing_from_official:
            f.write(f"**{len(missing_from_official)} endpoints** found in schemas/library but not in official docs:\n\n")
            for endpoint in sorted(missing_from_official):
                in_schemas = "✅ Schemas" if comparison[endpoint]['in_schemas'] else ""
                in_library = "✅ Library" if comparison[endpoint]['in_library'] else ""
                sources = " + ".join(filter(None, [in_schemas, in_library]))
                f.write(f"- `/{endpoint}` - Found in: {sources}\n")
        else:
            f.write("✅ All endpoints are documented in official docs!\n")
        
        f.write("\n### 2. Endpoints Only in Official Documentation\n\n")
        if only_official:
            f.write(f"**{len(only_official)} endpoints** documented but not found in practice:\n\n")
            for endpoint in sorted(only_official):
                desc = comparison[endpoint]['official_info'].get('description', '')
                f.write(f"- `/{endpoint}` - {desc[:100]}...\n")
        else:
            f.write("✅ All documented endpoints are implemented!\n")
        
        f.write("\n### 3. Device-Specific Endpoints\n\n")
        device_specific = [e for e, d in comparison.items() if d.get('schema_info', {}).get('device_specific')]
        if device_specific:
            f.write(f"**{len(device_specific)} endpoints** only available on specific models:\n\n")
            for endpoint in sorted(device_specific):
                available = comparison[endpoint]['schema_info'].get('available_on', [])
                f.write(f"- `/{endpoint}` - Only on: {', '.join(available)}\n")
        
    print(f"\n✅ Report generated: {output_file}")
    return output_file


def main():
    """Main comparison logic."""
    comparison = compare_sources()
    report_file = generate_report(comparison)
    
    print("\n" + "=" * 80)
    print("Next Steps:")
    print("=" * 80)
    print(f"1. Review report: {report_file}")
    print("2. Identify critical gaps")
    print("3. Create mitigation plan")
    print("=" * 80)


if __name__ == "__main__":
    main()
