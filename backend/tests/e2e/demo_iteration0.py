"""
E2E Demo Script für SoundTouchBridge
Iteration 0: Basic connectivity check

Zeigt die Grundfunktionalität des Systems:
- Backend erreichbar
- Health check funktioniert
- Basis für kommende Iterationen (Discovery, Presets, etc.)

Usage:
    python e2e/demo_iteration0.py
"""

import asyncio
import sys

import httpx


async def demo_iteration0():
    """E2E Demo für Iteration 0."""
    print("=" * 60)
    print("SoundTouchBridge E2E Demo - Iteration 0")
    print("=" * 60)
    print()

    base_url = "http://localhost:7777"

    async with httpx.AsyncClient() as client:
        # 1. Health Check
        print("[1/1] Testing /health endpoint...")
        try:
            response = await client.get(f"{base_url}/health", timeout=5.0)
            response.raise_for_status()
            data = response.json()

            print(f"  ✓ Status: {data['status']}")
            print(f"  ✓ Version: {data['version']}")
            print(f"  ✓ Discovery: {data['config']['discovery_enabled']}")
            print(f"  ✓ Database: {data['config']['db_path']}")
            print()

        except httpx.RequestError as e:
            print(f"  ✗ Connection failed: {e}")
            print()
            print("Make sure SoundTouchBridge is running:")
            print("  docker compose up -d")
            print("  or")
            print("  cd backend && python main.py")
            return False

        except httpx.HTTPStatusError as e:
            print(f"  ✗ HTTP error: {e}")
            return False

    print("=" * 60)
    print("Iteration 0 Demo: SUCCESS ✓")
    print("=" * 60)
    print()
    print("Next steps (Iteration 1):")
    print("  - Device discovery (SSDP/UPnP)")
    print("  - GET /api/devices endpoint")
    print("  - Device detail caching")
    print()

    return True


if __name__ == "__main__":
    result = asyncio.run(demo_iteration0())
    sys.exit(0 if result else 1)
