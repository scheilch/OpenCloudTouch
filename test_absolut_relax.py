#!/usr/bin/env python3
"""
Test: Absolut Relax Radio Station finden und Stream testen
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.radio.providers.radiobrowser import RadioBrowserAdapter
import httpx


async def main():
    print("=" * 60)
    print("Suche: Absolut Relax")
    print("=" * 60)
    
    adapter = RadioBrowserAdapter()
    
    # Suche nach "Absolut Relax"
    stations = await adapter.search_by_name("absolut relax", limit=5)
    
    print(f"\nGefunden: {len(stations)} Stationen\n")
    
    for i, station in enumerate(stations, 1):
        print(f"\n[{i}] {station.name}")
        print(f"    Land: {station.country}")
        print(f"    Stream-URL: {station.url}")
        print(f"    Codec: {station.codec} @ {station.bitrate or '?'} kbps")
        print(f"    Tags: {station.tags or 'keine'}")
        print(f"    Homepage: {station.homepage or 'keine'}")
        
        # Teste Stream (erste 1KB abrufen)
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(station.url, headers={
                    "User-Agent": "SoundTouchBridge/0.2.0",
                    "Icy-MetaData": "1"
                })
                content_type = response.headers.get("content-type", "unknown")
                print(f"    Stream-Test: OK (Content-Type: {content_type})")
        except Exception as e:
            print(f"    Stream-Test: FEHLER ({e})")
    
    print("\n" + "=" * 60)
    print("Stream-URLs bereit zum Abspielen!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
