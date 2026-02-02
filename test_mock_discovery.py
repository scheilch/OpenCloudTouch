"""Quick test script for mock discovery debugging."""

import asyncio
import sys
sys.path.insert(0, "/app/backend/src")

from cloudtouch.devices.discovery.mock import MockDiscovery


async def test():
    print("=== Testing Mock Discovery ===")
    
    # Test 1: No manual IPs
    print("\n1. No manual IPs:")
    mock = MockDiscovery()
    devices = await mock.discover()
    print(f"   Devices: {len(devices)}")
    for d in devices:
        print(f"   - {d.ip}: {d.name} ({d.model})")
    
    # Test 2: With manual IPs
    print("\n2. With 2 manual IPs:")
    manual_ips = ["192.168.1.50", "192.168.1.51"]
    mock = MockDiscovery(manual_ips=manual_ips)
    devices = await mock.discover()
    print(f"   Devices: {len(devices)}")
    for d in devices:
        print(f"   - {d.ip}: {d.name} ({d.model})")
    
    # Test 3: Settings repo
    print("\n3. Testing settings repo:")
    from cloudtouch.main import settings_repo
    if settings_repo:
        manual_ips = await settings_repo.get_manual_ips()
        print(f"   Manual IPs from DB: {manual_ips}")
    else:
        print("   Settings repo not initialized!")


if __name__ == "__main__":
    asyncio.run(test())
