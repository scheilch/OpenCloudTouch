"""
E2E Test for Discovery - reproduces production issue

Bug: SSDP discovery finds devices but cannot parse them.
Root Cause: Bose SoundTouch devices respond to SSDP but don't provide valid XML.
Solution: Use native bosesoundtouchapi Zeroconf discovery OR manual IPs.

This test MUST run against real devices to catch this regression.
"""
import asyncio
import sys
import pytest


@pytest.mark.integration
async def test_ssdp_discovery():
    """Test SSDP Discovery (currently broken)."""
    print("\n=== Test 1: SSDP Discovery ===")
    from soundtouch_bridge.devices.discovery.ssdp import SSDPDiscovery
    
    ssdp = SSDPDiscovery(timeout=10)
    devices = await ssdp.discover()
    
    print(f"SSDP found {len(devices)} Bose devices")
    for mac, info in devices.items():
        print(f"  - {info['name']} @ {info['ip']}")
    
    return len(devices) > 0


@pytest.mark.integration
async def test_adapter_discovery():
    """Test BoseSoundTouchDiscoveryAdapter (our abstraction layer)."""
    print("\n=== Test 2: Adapter Discovery (BoseSoundTouchDiscoveryAdapter) ===")
    from soundtouch_bridge.devices.adapter import BoseSoundTouchDiscoveryAdapter
    
    print("Discovering via SSDP adapter...")
    adapter = BoseSoundTouchDiscoveryAdapter()
    devices = await adapter.discover(timeout=10)
    
    print(f"Adapter found {len(devices)} devices")
    for device in devices:
        print(f"  - {device.name} @ {device.ip}:{device.port}")
    
    # Verify structure
    if devices:
        assert hasattr(devices[0], 'ip')
        assert hasattr(devices[0], 'port')
        assert hasattr(devices[0], 'name')
        print("✓ DiscoveredDevice structure valid")
    
    return len(devices) > 0


@pytest.mark.integration
async def test_manual_discovery():
    """Test Manual IP Discovery (fallback)."""
    print("\n=== Test 3: Manual IP Discovery ===")
    from soundtouch_bridge.devices.discovery.manual import ManualDiscovery
    
    manual_ips = [
        "192.0.2.36",  # ST30
        "192.0.2.32",  # ST10
        "192.0.2.27"   # ST300
    ]
    
    manual = ManualDiscovery(manual_ips)
    devices = await manual.discover()
    
    print(f"Manual discovery found {len(devices)} devices")
    for d in devices:
        print(f"  - {d.name} @ {d.ip}")
    
    return len(devices) > 0


@pytest.mark.integration
async def test_api_sync():
    """Test full /api/devices/sync flow."""
    print("\n=== Test 4: API Sync Flow ===")
    import httpx
    
    async with httpx.AsyncClient() as client:
        # Trigger sync
        print("Calling POST /api/devices/sync...")
        response = await client.post("http://remotehost:7777/api/devices/sync", timeout=30.0)
        response.raise_for_status()
        
        result = response.json()
        print(f"Sync result: {result}")
        
        # Check DB
        response = await client.get("http://remotehost:7777/api/devices")
        response.raise_for_status()
        
        devices = response.json()
        print(f"DB contains {devices['count']} devices")
        
        return devices['count'] > 0


async def main():
    """Run all discovery tests."""
    print("=" * 60)
    print("DISCOVERY E2E TEST - Production Issue Reproduction")
    print("=" * 60)
    
    results = {}
    
    # Test 1: SSDP (currently broken)
    try:
        results['ssdp'] = await test_ssdp_discovery()
    except Exception as e:
        print(f"SSDP Discovery FAILED: {e}")
        results['ssdp'] = False
    
    # Test 2: Zeroconf (native library method)
    try:
        results['zeroconf'] = await test_zeroconf_discovery()
    except Exception as e:
        print(f"Zeroconf Discovery FAILED: {e}")
        results['zeroconf'] = False
    
    # Test 3: Manual IPs (fallback)
    try:
        results['manual'] = await test_manual_discovery()
    except Exception as e:
        print(f"Manual Discovery FAILED: {e}")
        results['manual'] = False
    
    # Test 4: API Sync
    try:
        results['api_sync'] = await test_api_sync()
    except Exception as e:
        print(f"API Sync FAILED: {e}")
        results['api_sync'] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    # Exit code
    if any(results.values()):
        print("\n✅ At least one discovery method works")
        sys.exit(0)
    else:
        print("\n❌ ALL discovery methods failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
