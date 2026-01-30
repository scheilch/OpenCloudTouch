#!/usr/bin/env python3
"""
Demo: Radio API - Absolut Relax suchen
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.adapters.radiobrowser_adapter import RadioBrowserAdapter


async def main():
    print("\n" + "="*60)
    print("RADIO API DEMO: Absolut Relax")
    print("="*60 + "\n")
    
    adapter = RadioBrowserAdapter()
    
    print("Suche nach 'absolut relax'...")
    stations = await adapter.search_by_name("absolut relax", limit=3)
    
    print(f"\nGefunden: {len(stations)} Stationen\n")
    
    for i, s in enumerate(stations, 1):
        print(f"[{i}] {s.name}")
        print(f"    Stream-URL: {s.url}")
        print(f"    Land: {s.country}")
        print(f"    Codec: {s.codec} @ {s.bitrate or '?'} kbps")
        print(f"    UUID: {s.uuid}")
        print()
    
    print("="*60)
    print("Radio API funktioniert! ✓")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
