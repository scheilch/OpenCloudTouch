#!/usr/bin/env python3
"""
Consolidate XML schemas from multiple devices into single files per endpoint.

This script merges device_78_*.xml, device_79_*.xml, device_83_*.xml into
consolidated *.xml files with differences marked as XML comments.
"""

import re
from pathlib import Path
from typing import Dict
from xml.etree import ElementTree as ET
from xml.dom import minidom

DEVICES = {
    "78": {"name": "living_room", "model": "SoundTouch 30 Series III"},
    "79": {"name": "kitchen", "model": "SoundTouch 10"},
    "83": {"name": "tv", "model": "SoundTouch 300"},
}

SCRIPT_DIR = Path(__file__).parent


def get_schema_files() -> Dict[str, Dict[str, Path]]:
    """Get all device_XX_endpoint.xml files grouped by endpoint."""
    schemas_by_endpoint: Dict[str, Dict[str, Path]] = {}

    for file in SCRIPT_DIR.glob("device_*_*.xml"):
        match = re.match(r"device_(\d+)_(.+)\.xml", file.name)
        if not match:
            continue

        device_id, endpoint = match.groups()
        if device_id not in DEVICES:
            continue

        if endpoint not in schemas_by_endpoint:
            schemas_by_endpoint[endpoint] = {}

        schemas_by_endpoint[endpoint][device_id] = file

    return schemas_by_endpoint


def prettify_xml(elem: ET.Element) -> str:
    """Return a pretty-printed XML string."""
    rough_string = ET.tostring(elem, encoding="unicode")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text for comparison."""
    if not text:
        return ""
    return " ".join(text.split())


def elements_equal(elem1: ET.Element, elem2: ET.Element) -> bool:
    """Check if two XML elements are structurally equal."""
    if elem1.tag != elem2.tag:
        return False

    if normalize_whitespace(elem1.text or "") != normalize_whitespace(elem2.text or ""):
        return False

    if elem1.attrib != elem2.attrib:
        return False

    if len(elem1) != len(elem2):
        return False

    for child1, child2 in zip(elem1, elem2):
        if not elements_equal(child1, child2):
            return False

    return True


def xml_to_string_without_declaration(elem: ET.Element) -> str:
    """Convert Element to XML string without <?xml?> declaration."""
    xml_str = ET.tostring(elem, encoding="unicode")
    # Remove XML declaration if present
    xml_str = re.sub(r"<\?xml[^>]+\?>\s*", "", xml_str)
    return xml_str


def consolidate_endpoint(endpoint: str, device_files: Dict[str, Path]) -> str:
    """Consolidate schemas for one endpoint across all devices."""
    print(f"\n  Processing endpoint: {endpoint}")

    # Parse all schemas
    trees = {}
    roots = {}
    for device_id, file_path in device_files.items():
        try:
            # Read file and skip metadata comments
            content = file_path.read_text(encoding="utf-8")

            # Find the actual XML start (after <!-- comments -->)
            xml_start = content.find("<?xml")
            if xml_start == -1:
                # No XML declaration, find first < that's not a comment
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped and not stripped.startswith("<!--"):
                        content = "\n".join(lines[i:])
                        break
            else:
                content = content[xml_start:]

            # Parse cleaned XML
            tree = ET.ElementTree(ET.fromstring(content))
            trees[device_id] = tree
            roots[device_id] = tree.getroot()
        except ET.ParseError as e:
            print(f"    ⚠️  Parse error in {file_path.name}: {e}")
            return None

    # Check if all schemas are identical
    root_list = list(roots.values())
    all_equal = all(elements_equal(root_list[0], root) for root in root_list[1:])

    if all_equal:
        # All schemas identical - use first device's schema
        first_device = min(device_files.keys())
        print(f"    ✅ Schemas identical - using {DEVICES[first_device]['name']}")

        # Add comment at top
        xml_content = xml_to_string_without_declaration(roots[first_device])
        header = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- AGENT: Consolidated schema from all 3 devices - schemas are identical -->
<!-- Source: {DEVICES[first_device]['name']} ({DEVICES[first_device]['model']}) -->
<!-- Verified: ST30 (.78), ST10 (.79), ST300 (.83) all return same structure -->

"""
        return header + xml_content

    # Schemas differ - need to annotate differences
    print("    ⚠️  Schemas differ - creating annotated version")

    # Start with first device's schema as base
    base_device = min(device_files.keys())
    base_content = xml_to_string_without_declaration(roots[base_device])

    # Create header with model differences
    header_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<!-- AGENT: Consolidated schema with model differences -->",
        "<!-- Base schema: {} ({}) -->".format(
            DEVICES[base_device]["name"], DEVICES[base_device]["model"]
        ),
        "<!-- Differences: -->",
    ]

    # Try to identify specific differences
    for device_id in sorted(device_files.keys()):
        if device_id == base_device:
            continue

        device_content = xml_to_string_without_declaration(roots[device_id])
        if device_content != base_content:
            header_lines.append(
                f'<!--   {DEVICES[device_id]["name"]} ({DEVICES[device_id]["model"]}): Schema differs -->'
            )

    header_lines.append(
        "<!-- Note: Detailed diff analysis needed for this endpoint -->"
    )
    header_lines.append("")

    return "\n".join(header_lines) + "\n" + base_content


def main():
    """Main consolidation logic."""
    print("=" * 80)
    print("XML Schema Consolidation")
    print("=" * 80)

    # Get all schemas grouped by endpoint
    schemas = get_schema_files()
    print(f"\nFound {len(schemas)} unique endpoints across devices:")

    # Statistics
    identical_count = 0
    different_count = 0
    device_specific_count = 0

    # Create consolidated directory
    consolidated_dir = SCRIPT_DIR / "consolidated"
    consolidated_dir.mkdir(exist_ok=True)

    print(f"\nConsolidating schemas into: {consolidated_dir}")

    for endpoint, device_files in sorted(schemas.items()):
        # Check if endpoint exists on all devices
        devices_with_endpoint = set(device_files.keys())
        all_devices = set(DEVICES.keys())

        if devices_with_endpoint != all_devices:
            # Device-specific endpoint
            device_specific_count += 1
            missing_devices = all_devices - devices_with_endpoint

            print(f"\n  Processing endpoint: {endpoint}")
            print("    ⚠️  Device-specific endpoint!")
            print(
                f"    Available on: {', '.join(DEVICES[d]['name'] for d in sorted(devices_with_endpoint))}"
            )
            print(
                f"    Missing on: {', '.join(DEVICES[d]['name'] for d in sorted(missing_devices))}"
            )

            # Use first available device's schema
            first_device = min(devices_with_endpoint)
            tree = ET.parse(device_files[first_device])
            xml_content = xml_to_string_without_declaration(tree.getroot())

            # Create header for device-specific endpoint
            header = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- AGENT: DEVICE-SPECIFIC ENDPOINT -->
<!-- Available on: {', '.join(DEVICES[d]['model'] for d in sorted(devices_with_endpoint))} -->
<!-- Missing on: {', '.join(DEVICES[d]['model'] for d in sorted(missing_devices))} -->
<!-- Source: {DEVICES[first_device]['name']} ({DEVICES[first_device]['model']}) -->

"""
            consolidated_content = header + xml_content
        else:
            # All devices have this endpoint - consolidate
            consolidated_content = consolidate_endpoint(endpoint, device_files)

            if not consolidated_content:
                print("    ❌ Failed to consolidate - skipping")
                continue

            # Track statistics
            if "schemas are identical" in consolidated_content:
                identical_count += 1
            else:
                different_count += 1

        # Write consolidated file
        output_file = consolidated_dir / f"{endpoint}.xml"
        output_file.write_text(consolidated_content, encoding="utf-8")
        print(f"    ✅ Written to: {output_file.name}")

    # Summary
    print("\n" + "=" * 80)
    print("Consolidation Summary")
    print("=" * 80)
    print(f"Total endpoints:       {len(schemas)}")
    print(f"  Identical schemas:   {identical_count}")
    print(f"  Different schemas:   {different_count}")
    print(f"  Device-specific:     {device_specific_count}")
    print(f"\nConsolidated files saved in: {consolidated_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
