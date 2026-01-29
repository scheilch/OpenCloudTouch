#!/usr/bin/env python3
"""
Extract and analyze Bose SoundTouch Web API documentation from PDF.
"""

import re
from pathlib import Path
try:
    from PyPDF2 import PdfReader
except ImportError:
    print("ERROR: PyPDF2 not installed. Run: pip install pypdf2")
    exit(1)


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract all text from PDF."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        return text
    except Exception as e:
        print(f"ERROR extracting PDF: {e}")
        return None


def extract_endpoints(text: str) -> list:
    """Extract endpoint definitions from documentation."""
    endpoints = []
    
    # Look for patterns like: GET /info, POST /volume, etc.
    pattern = r'(GET|POST|PUT|DELETE)\s+(/[\w/]+)'
    matches = re.findall(pattern, text)
    
    for method, endpoint in matches:
        endpoints.append({
            'method': method,
            'endpoint': endpoint.strip('/')
        })
    
    return endpoints


def main():
    """Main extraction logic."""
    # Try multiple paths
    script_dir = Path(__file__).parent
    possible_paths = [
        script_dir.parent.parent / "docs" / "2025.12.18 SoundTouch Web API.pdf",
        Path("docs") / "2025.12.18 SoundTouch Web API.pdf",
        Path("../../docs/2025.12.18 SoundTouch Web API.pdf"),
    ]
    
    pdf_path = None
    for path in possible_paths:
        if path.exists():
            pdf_path = path
            break
    
    if not pdf_path:
        print(f"ERROR: PDF not found. Tried:")
        for path in possible_paths:
            print(f"  - {path}")
        return
    
    print("=" * 80)
    print("Bose SoundTouch Web API Documentation Extraction")
    print("=" * 80)
    print(f"\nReading PDF: {pdf_path.name}")
    
    # Extract text
    text = extract_pdf_text(pdf_path)
    
    if not text:
        print("ERROR: Failed to extract text from PDF")
        return
    
    print(f"Extracted {len(text)} characters")
    
    # Save raw text for analysis
    output_dir = Path(__file__).parent / "official"
    output_dir.mkdir(exist_ok=True)
    
    text_file = output_dir / "bose_api_documentation.txt"
    text_file.write_text(text, encoding='utf-8')
    print(f"Saved raw text to: {text_file}")
    
    # Extract endpoints
    endpoints = extract_endpoints(text)
    print(f"\nFound {len(endpoints)} endpoint references:")
    
    endpoint_file = output_dir / "endpoints_from_pdf.txt"
    with endpoint_file.open('w', encoding='utf-8') as f:
        unique_endpoints = {}
        for ep in endpoints:
            key = ep['endpoint']
            if key not in unique_endpoints:
                unique_endpoints[key] = []
            unique_endpoints[key].append(ep['method'])
        
        f.write("Endpoints found in Bose SoundTouch Web API Documentation\n")
        f.write("=" * 80 + "\n\n")
        
        for endpoint, methods in sorted(unique_endpoints.items()):
            f.write(f"{', '.join(methods):20s} /{endpoint}\n")
            print(f"  {', '.join(methods):20s} /{endpoint}")
    
    print(f"\nSaved endpoint list to: {endpoint_file}")
    
    # Look for XML examples
    xml_pattern = r'<[^>]+>.*?</[^>]+>'
    xml_matches = re.findall(xml_pattern, text, re.DOTALL)
    print(f"\nFound {len(xml_matches)} potential XML examples in PDF")
    
    if xml_matches:
        xml_file = output_dir / "xml_examples_from_pdf.txt"
        with xml_file.open('w', encoding='utf-8') as f:
            f.write("XML Examples from Bose SoundTouch Web API Documentation\n")
            f.write("=" * 80 + "\n\n")
            for i, xml in enumerate(xml_matches[:50], 1):  # First 50 examples
                f.write(f"Example {i}:\n{xml}\n\n")
        print(f"Saved XML examples to: {xml_file}")
    
    print("\n" + "=" * 80)
    print("Extraction complete!")
    print("=" * 80)
    print(f"\nNext steps:")
    print(f"1. Review: {text_file}")
    print(f"2. Compare endpoints with our collected schemas")
    print(f"3. Identify missing/additional endpoints")


if __name__ == "__main__":
    main()
