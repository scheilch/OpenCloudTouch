#!/usr/bin/env python3
"""
E2E Demo Script für Iteration 1: Device Discovery & Inventory

Demonstriert:
- Device Discovery (SSDP + Manual Fallback)
- SoundTouch Client (Info + Now Playing)
- Device Repository (Add, List, Get)
- API Endpoints (/devices, /discover, /sync)

Nutzung:
  python e2e/demo_iteration1.py
  
Voraussetzungen:
  - Backend läuft auf http://localhost:7777
  - Optional: SoundTouch Gerät im Netzwerk (für SSDP Discovery)
"""

import asyncio
import sys
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import httpx

from opencloudtouch.devices.client import HttpSoundTouchClient
from opencloudtouch.devices.discovery.manual import ManualDiscovery
from opencloudtouch.devices.repository import Device, DeviceRepository


async def demo_api_endpoints():
    """Demo 1: Test API Endpoints"""
    print("\n" + "=" * 60)
    print("DEMO 1: API Endpoints")
    print("=" * 60)

    base_url = "http://localhost:7777"

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Health Check
        print("\n[1] Testing /health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            response.raise_for_status()
            data = response.json()
            print(f"✓ Health OK: {data['status']} (Version: {data['version']})")
        except Exception as e:
            print(f"✗ Health check failed: {e}")
            return False

        # Get Devices
        print("\n[2] Testing GET /api/devices...")
        try:
            response = await client.get(f"{base_url}/api/devices")
            response.raise_for_status()
            result = response.json()
            devices = result.get("devices", [])
            print(f"✓ Current devices: {len(devices)} found")
            for device in devices:
                print(
                    f"  - {device.get('name', 'Unknown')} @ {device.get('ip', 'Unknown IP')}"
                )
        except Exception as e:
            print(f"✗ Get devices failed: {e}")
            return False

        # Note: Discovery and Sync endpoints don't exist yet in Iteration 1
        print("\n[3] Note: /api/discover endpoint (Iteration 2)")
        print("[4] Note: /api/sync endpoint (Iteration 2)")

    return True


async def demo_manual_discovery():
    """Demo 2: Manual Discovery"""
    print("\n" + "=" * 60)
    print("DEMO 2: Manual Discovery")
    print("=" * 60)

    print("\n[1] Creating ManualDiscovery instance...")
    discovery = ManualDiscovery(["192.168.1.100", "192.168.1.101"])

    print("[2] Starting discovery...")
    await discovery.start()

    print("[3] Running discovery...")
    devices = await discovery.discover(timeout=5)
    print(f"✓ Found {len(devices)} configured device(s)")
    for device in devices:
        print(f"  - {device.base_url}")

    print("[4] Stopping discovery...")
    await discovery.stop()
    print("✓ Discovery stopped")

    return True


async def demo_soundtouch_client():
    """Demo 3: SoundTouch Client (Mock mode, no real device needed)"""
    print("\n" + "=" * 60)
    print("DEMO 3: SoundTouch Client")
    print("=" * 60)

    print("\n[1] Creating HttpSoundTouchClient...")
    client = HttpSoundTouchClient(base_url="http://192.168.1.100:8090")
    print(f"✓ Client created for {client.base_url}")

    print("\n[2] Testing get_info()...")
    print("   Note: This will fail without a real device, which is expected")
    try:
        info = await client.get_info()
        print("✓ Device Info:")
        print(f"  - Name: {info.name}")
        print(f"  - Device ID: {info.device_id}")
        print(f"  - Type: {info.type}")
    except Exception as e:
        print(f"✗ get_info() failed (expected): {type(e).__name__}")

    print("\n[3] Testing get_now_playing()...")
    print("   Note: This will fail without a real device, which is expected")
    try:
        now_playing = await client.get_now_playing()
        print("✓ Now Playing:")
        print(f"  - Source: {now_playing.source}")
        print(f"  - State: {now_playing.play_status}")
    except Exception as e:
        print(f"✗ get_now_playing() failed (expected): {type(e).__name__}")

    await client.close()
    print("\n[4] Client closed")

    return True


async def demo_device_repository():
    """Demo 4: Device Repository"""
    print("\n" + "=" * 60)
    print("DEMO 4: Device Repository")
    print("=" * 60)

    print("\n[1] Creating in-memory repository...")
    repo = DeviceRepository(db_path=":memory:")
    await repo.initialize()
    print("✓ Repository initialized")

    print("\n[2] Adding test devices...")
    device1 = Device(
        device_id="TEST001",
        name="Living Room SoundTouch 30",
        ip="192.168.1.100",
        model="SoundTouch 30",
        mac_address="00:11:22:33:44:55",
        firmware_version="21.0.5.1",
    )
    device2 = Device(
        device_id="TEST002",
        name="Bedroom SoundTouch 10",
        ip="192.168.1.101",
        model="SoundTouch 10",
        mac_address="00:11:22:33:44:66",
        firmware_version="21.0.5.1",
    )
    device1 = await repo.upsert(device1)
    device2 = await repo.upsert(device2)
    print(f"✓ Added {device1.name}")
    print(f"✓ Added {device2.name}")

    print("\n[3] Listing all devices...")
    devices = await repo.get_all()
    print(f"✓ Found {len(devices)} devices:")
    for device in devices:
        print(f"  - {device.name} ({device.device_id}) at {device.ip}")

    print("\n[4] Getting device by ID...")
    device = await repo.get_by_device_id("TEST001")
    if device:
        print(f"✓ Retrieved: {device.name}")
    else:
        print("✗ Device not found")

    print("\n[5] Updating device...")
    device1.name = "Living Room SoundTouch 30 (Updated)"
    updated = await repo.upsert(device1)
    print(f"✓ Updated: {updated.name}")

    await repo.close()
    print("\n[6] Repository closed")

    return True


async def main():
    """Run all demos"""
    print("=" * 60)
    print("OpenCloudTouch - Iteration 1 E2E Demo")
    print("=" * 60)

    demos = [
        ("API Endpoints", demo_api_endpoints),
        ("Manual Discovery", demo_manual_discovery),
        ("SoundTouch Client", demo_soundtouch_client),
        ("Device Repository", demo_device_repository),
    ]

    results = {}
    for name, demo_func in demos:
        try:
            result = await demo_func()
            results[name] = result if result is not None else True
        except Exception as e:
            print(f"\n✗ Demo '{name}' failed with exception: {e}")
            results[name] = False

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")

    all_passed = all(results.values())
    if all_passed:
        print("\n✓ All demos completed successfully!")
        return 0
    else:
        print("\n✗ Some demos failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
