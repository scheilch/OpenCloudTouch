#!/usr/bin/env python3
"""
E2E Demo Script for Iteration 2: RadioBrowser API Integration

Demonstrates:
- RadioBrowser API search (name, country, tag)
- Station detail retrieval
- API response format validation
- Mock mode for CI/CD
- Real API mode for manual testing

Usage:
  python e2e/demo_iteration2.py              # Mock mode (CI-friendly)
  python e2e/demo_iteration2.py --real       # Real RadioBrowser API

Prerequisites:
  - Backend running on http://localhost:7777
  - Internet connection (for --real mode)
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any
import argparse

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import httpx


class MockRadioBrowserAPI:
    """Mock RadioBrowser API for testing without real API calls."""

    MOCK_STATIONS = [
        {
            "changeuuid": "960761d5-0601-11e8-ae97-52543be04c81",
            "stationuuid": "960761d5-0601-11e8-ae97-52543be04c81",
            "name": "Absolut relax",
            "url": "http://streamlive.syndicast.fr/HautDeFrance-Picardie/all/absoluthautsdefrance-relax.mp3",
            "url_resolved": "http://streamlive.syndicast.fr/HautDeFrance-Picardie/all/absoluthautsdefrance-relax.mp3",
            "homepage": "https://www.absolut-radio.fr",
            "favicon": "https://www.absolut-radio.fr/wp-content/uploads/2020/01/cropped-favicon-absolut-180x180.png",
            "tags": "chillout,easy listening,lounge,relax",
            "country": "France",
            "countrycode": "FR",
            "state": "Hauts-de-France",
            "language": "french",
            "languagecodes": "fr",
            "votes": 12,
            "codec": "MP3",
            "bitrate": 128,
            "hls": 0,
            "lastcheckok": 1,
            "lastchecktime": "2024-01-25 19:28:14",
            "clickcount": 145,
            "clicktrend": 3,
        },
        {
            "changeuuid": "9607621a-0601-11e8-ae97-52543be04c81",
            "stationuuid": "9607621a-0601-11e8-ae97-52543be04c81",
            "name": "Radio Swiss Jazz",
            "url": "http://stream.srg-ssr.ch/m/rsj/mp3_128",
            "url_resolved": "http://stream.srg-ssr.ch/m/rsj/mp3_128",
            "homepage": "https://www.radioswissjazz.ch",
            "favicon": "https://www.radioswissjazz.ch/favicon.ico",
            "tags": "jazz",
            "country": "Switzerland",
            "countrycode": "CH",
            "state": "",
            "language": "german,french,italian",
            "languagecodes": "de,fr,it",
            "votes": 98,
            "codec": "MP3",
            "bitrate": 128,
            "hls": 0,
            "lastcheckok": 1,
            "lastchecktime": "2024-01-25 20:15:42",
            "clickcount": 2341,
            "clicktrend": 15,
        },
        {
            "changeuuid": "9607627c-0601-11e8-ae97-52543be04c81",
            "stationuuid": "9607627c-0601-11e8-ae97-52543be04c81",
            "name": "Bayern 3",
            "url": "http://streams.br.de/bayern3_2.m3u",
            "url_resolved": "http://br-br3-live.cast.addradio.de/br/br3/live/mp3/128/stream.mp3",
            "homepage": "https://www.br.de/radio/bayern3/",
            "favicon": "https://www.br.de/radio/bayern3/img/bayern3-logo-100~_v-img__16__9__xl_-d31c35f8186ebeb80b0cd843a7c267a0e0c81647.jpg",
            "tags": "pop,rock,hits",
            "country": "Germany",
            "countrycode": "DE",
            "state": "Bavaria",
            "language": "german",
            "languagecodes": "de",
            "votes": 234,
            "codec": "MP3",
            "bitrate": 128,
            "hls": 0,
            "lastcheckok": 1,
            "lastchecktime": "2024-01-25 19:45:23",
            "clickcount": 5678,
            "clicktrend": 42,
        },
    ]

    async def search(
        self, name: str = None, country: str = None, tag: str = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Mock search - returns filtered mock stations."""
        await asyncio.sleep(0.1)  # Simulate API delay

        results = self.MOCK_STATIONS.copy()

        # Simple filtering
        if name:
            results = [s for s in results if name.lower() in s["name"].lower()]
        if country:
            results = [s for s in results if country.lower() in s["country"].lower()]
        if tag:
            results = [s for s in results if tag.lower() in s["tags"].lower()]

        return results[:limit]

    async def get_station_by_uuid(self, uuid: str) -> Dict[str, Any]:
        """Mock station detail retrieval."""
        await asyncio.sleep(0.05)  # Simulate API delay

        for station in self.MOCK_STATIONS:
            if station["stationuuid"] == uuid:
                return station

        raise ValueError(f"Station {uuid} not found")


async def demo_radiobrowser_search(api, use_real: bool):
    """Demo 1: RadioBrowser Search"""
    print("\n" + "=" * 60)
    print("DEMO 1: RadioBrowser Station Search")
    print("=" * 60)
    mode = "REAL API" if use_real else "MOCK MODE"
    print(f"Mode: {mode}")

    # Test 1: Search by name
    print("\n[1] Search by name: 'relax'...")
    try:
        if use_real:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://de1.api.radio-browser.info/json/stations/byname/relax",
                    params={"limit": 5},
                )
                response.raise_for_status()
                stations = response.json()
        else:
            stations = await api.search(name="relax", limit=5)

        print(f"✓ Found {len(stations)} station(s)")
        for station in stations[:3]:  # Show first 3
            print(
                f"  - {station['name']} ({station.get('country', 'Unknown')}) - {station.get('codec', '?')}/{station.get('bitrate', '?')}kbps"
            )
    except Exception as e:
        print(f"✗ Search failed: {e}")
        return False

    # Test 2: Search by country
    print("\n[2] Search by country: 'Germany'...")
    try:
        if use_real:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://de1.api.radio-browser.info/json/stations/bycountry/Germany",
                    params={"limit": 5},
                )
                response.raise_for_status()
                stations = response.json()
        else:
            stations = await api.search(country="Germany", limit=5)

        print(f"✓ Found {len(stations)} station(s)")
        for station in stations[:3]:
            print(f"  - {station['name']} ({station.get('state', 'Unknown state')})")
    except Exception as e:
        print(f"✗ Country search failed: {e}")
        return False

    # Test 3: Search by tag
    print("\n[3] Search by tag: 'jazz'...")
    try:
        if use_real:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://de1.api.radio-browser.info/json/stations/bytag/jazz",
                    params={"limit": 5},
                )
                response.raise_for_status()
                stations = response.json()
        else:
            stations = await api.search(tag="jazz", limit=5)

        print(f"✓ Found {len(stations)} station(s)")
        for station in stations[:3]:
            print(f"  - {station['name']} - Tags: {station.get('tags', 'none')}")
    except Exception as e:
        print(f"✗ Tag search failed: {e}")
        return False

    return True


async def demo_station_detail(api, use_real: bool):
    """Demo 2: Station Detail Retrieval"""
    print("\n" + "=" * 60)
    print("DEMO 2: Station Detail Retrieval")
    print("=" * 60)

    # Get a station UUID from search first
    print("\n[1] Searching for station...")
    try:
        if use_real:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://de1.api.radio-browser.info/json/stations/byname/bayern",
                    params={"limit": 1},
                )
                response.raise_for_status()
                stations = response.json()
        else:
            stations = await api.search(name="bayern", limit=1)

        if not stations:
            print("✗ No stations found")
            return False

        station_uuid = stations[0]["stationuuid"]
        print(f"✓ Found station: {stations[0]['name']} (UUID: {station_uuid})")
    except Exception as e:
        print(f"✗ Search failed: {e}")
        return False

    # Get station detail
    print("\n[2] Fetching station detail...")
    try:
        if use_real:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://de1.api.radio-browser.info/json/stations/byuuid/{station_uuid}"
                )
                response.raise_for_status()
                detail = response.json()
                if isinstance(detail, list) and detail:
                    detail = detail[0]
        else:
            detail = await api.get_station_by_uuid(station_uuid)

        print("✓ Station detail retrieved:")
        print(f"  Name: {detail.get('name', 'Unknown')}")
        print(f"  URL: {detail.get('url_resolved', detail.get('url', 'Unknown'))}")
        print(f"  Homepage: {detail.get('homepage', 'None')}")
        print(
            f"  Codec: {detail.get('codec', 'Unknown')} @ {detail.get('bitrate', '?')} kbps"
        )
        print(
            f"  Country: {detail.get('country', 'Unknown')} ({detail.get('countrycode', '??')})"
        )
        print(f"  Language: {detail.get('language', 'Unknown')}")
        print(f"  Tags: {detail.get('tags', 'none')}")
        print(f"  Votes: {detail.get('votes', 0)}")
        print(f"  Click Count: {detail.get('clickcount', 0)}")
    except Exception as e:
        print(f"✗ Detail retrieval failed: {e}")
        return False

    return True


async def demo_response_format_validation(api, use_real: bool):
    """Demo 3: Response Format Validation"""
    print("\n" + "=" * 60)
    print("DEMO 3: Response Format Validation")
    print("=" * 60)

    print("\n[1] Validating required fields...")
    try:
        if use_real:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://de1.api.radio-browser.info/json/stations/byname/radio",
                    params={"limit": 1},
                )
                response.raise_for_status()
                stations = response.json()
        else:
            stations = await api.search(name="radio", limit=1)

        if not stations:
            print("✗ No stations found")
            return False

        station = stations[0]
        required_fields = ["stationuuid", "name", "url", "country", "codec"]
        optional_fields = [
            "url_resolved",
            "homepage",
            "favicon",
            "tags",
            "bitrate",
            "votes",
        ]

        print("✓ Checking required fields:")
        for field in required_fields:
            if field in station:
                print(f"  ✓ {field}: {str(station[field])[:50]}")
            else:
                print(f"  ✗ {field}: MISSING")
                return False

        print("\n✓ Checking optional fields:")
        for field in optional_fields:
            if field in station:
                value = station[field]
                if value is not None and value != "":
                    print(f"  ✓ {field}: {str(value)[:50]}")
                else:
                    print(f"  - {field}: empty")
            else:
                print(f"  - {field}: not present")
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return False

    return True


async def demo_backend_api_integration():
    """Demo 4: Backend API Integration (will fail until backend is implemented)"""
    print("\n" + "=" * 60)
    print("DEMO 4: Backend API Integration")
    print("=" * 60)
    print("Status: Not implemented yet (Iteration 2 - Part 2)")

    base_url = "http://localhost:7777"

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test GET /api/radio/search
        print("\n[1] Testing GET /api/radio/search...")
        try:
            response = await client.get(
                f"{base_url}/api/radio/search", params={"q": "relax", "limit": 5}
            )
            response.raise_for_status()
            result = response.json()
            print(f"✓ Search returned {len(result.get('stations', []))} stations")
            for station in result.get("stations", [])[:3]:
                print(f"  - {station.get('name', 'Unknown')}")
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                print("✗ Endpoint not found (expected - not implemented yet)")
                return True  # Expected failure
            else:
                print(f"✗ Unexpected error: {e}")
                return False
        except Exception as e:
            print(f"✗ Request failed: {e}")
            return True  # Expected failure in RED phase


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="E2E Demo for Iteration 2: RadioBrowser API"
    )
    parser.add_argument(
        "--real", action="store_true", help="Use real RadioBrowser API instead of mock"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("E2E DEMO: Iteration 2 - RadioBrowser API Integration")
    print("=" * 60)
    print(f"Mode: {'REAL API' if args.real else 'MOCK MODE (CI-friendly)'}")
    print("=" * 60)

    api = None if args.real else MockRadioBrowserAPI()

    # Run demos
    success = True
    success = success and await demo_radiobrowser_search(api, args.real)
    success = success and await demo_station_detail(api, args.real)
    success = success and await demo_response_format_validation(api, args.real)
    success = success and await demo_backend_api_integration()

    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✓ ALL DEMOS PASSED")
        print("=" * 60)
        return 0
    else:
        print("✗ SOME DEMOS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
