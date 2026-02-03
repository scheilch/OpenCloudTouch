"""
Real Device Discovery Tests
Requires actual Bose SoundTouch devices on network.

Run with: pytest tests/real/test_discovery_real.py -v
Or: scripts/run-real-tests.ps1
"""

import asyncio
import sys
import pytest

pytestmark = pytest.mark.real_devices


@pytest.mark.asyncio
async def test_ssdp_discovery_real():
    """Test SSDP Discovery against real devices."""
    print("\n=== Real Device Test: SSDP Discovery ===")
    from cloudtouch.devices.discovery.ssdp import SSDPDiscovery

    ssdp = SSDPDiscovery(timeout=10)
    devices = await ssdp.discover()

    print(f"SSDP found {len(devices)} Bose devices")
    for mac, info in devices.items():
        print(f"  - {info['name']} @ {info['ip']}")

    assert len(devices) > 0, "No devices found - check network connectivity"
    
    # Verify structure
    for mac, info in devices.items():
        assert "name" in info
        assert "ip" in info
        assert "model" in info


@pytest.mark.asyncio
async def test_adapter_discovery_real():
    """Test BoseSoundTouchDiscoveryAdapter against real devices."""
    print("\n=== Real Device Test: Adapter Discovery ===")
    from cloudtouch.devices.adapter import BoseSoundTouchDiscoveryAdapter

    print("Discovering via SSDP adapter...")
    adapter = BoseSoundTouchDiscoveryAdapter()
    devices = await adapter.discover(timeout=10)

    print(f"Adapter found {len(devices)} devices")
    for device in devices:
        print(f"  - {device.name} @ {device.ip}:{device.port}")

    assert len(devices) > 0, "No devices found - check network connectivity"
    
    # Verify structure
    device = devices[0]
    assert hasattr(device, "ip")
    assert hasattr(device, "port")
    assert hasattr(device, "name")
    assert hasattr(device, "model")
    print("✓ DiscoveredDevice structure valid")


@pytest.mark.asyncio
async def test_manual_discovery_real():
    """
    Test Manual IP Discovery against real devices.
    
    NOTE: Update IPs to match your actual devices!
    """
    print("\n=== Real Device Test: Manual IP Discovery ===")
    from cloudtouch.devices.discovery.manual import ManualDiscovery

    # TODO: Update these IPs to match your actual devices
    manual_ips = [
        "192.0.2.36",  # ST30
        "192.0.2.32",  # ST10
        "192.0.2.27",  # ST300
    ]

    manual = ManualDiscovery(manual_ips)
    devices = await manual.discover()

    print(f"Manual discovery found {len(devices)} devices")
    for d in devices:
        print(f"  - {d.name} @ {d.ip}")

    assert len(devices) > 0, "No devices found - check IPs and connectivity"
    
    # Verify device details
    for device in devices:
        assert device.ip is not None
        assert device.name is not None
        assert device.model is not None


@pytest.mark.asyncio
async def test_device_info_query_real():
    """Test querying /info endpoint from real devices."""
    print("\n=== Real Device Test: Device Info Query ===")
    from cloudtouch.devices.adapter import BoseSoundTouchDiscoveryAdapter
    from cloudtouch.devices.client import BoseSoundTouchClient

    # Discover devices
    adapter = BoseSoundTouchDiscoveryAdapter()
    devices = await adapter.discover(timeout=10)
    
    assert len(devices) > 0, "No devices found"
    
    # Query first device
    device = devices[0]
    print(f"Querying device: {device.name} @ {device.base_url}")
    
    client = BoseSoundTouchClient(device.base_url)
    info = await client.get_info()
    
    print(f"Device ID: {info.device_id}")
    print(f"Name: {info.name}")
    print(f"Type: {info.type}")
    print(f"Firmware: {info.components.get('FIRMWARE', 'unknown')}")
    
    # Verify info structure
    assert info.device_id is not None
    assert info.name is not None
    assert info.type is not None
    assert len(info.components) > 0
    
    await client.close()
    print("✓ Device info query successful")


@pytest.mark.asyncio
async def test_now_playing_query_real():
    """Test querying /nowPlaying endpoint from real devices."""
    print("\n=== Real Device Test: Now Playing Query ===")
    from cloudtouch.devices.adapter import BoseSoundTouchDiscoveryAdapter
    from cloudtouch.devices.client import BoseSoundTouchClient

    # Discover devices
    adapter = BoseSoundTouchDiscoveryAdapter()
    devices = await adapter.discover(timeout=10)
    
    assert len(devices) > 0, "No devices found"
    
    # Query first device
    device = devices[0]
    print(f"Querying now playing: {device.name} @ {device.base_url}")
    
    client = BoseSoundTouchClient(device.base_url)
    now_playing = await client.get_now_playing()
    
    print(f"Source: {now_playing.source}")
    print(f"Play Status: {now_playing.play_status}")
    if now_playing.track:
        print(f"Track: {now_playing.track}")
    if now_playing.artist:
        print(f"Artist: {now_playing.artist}")
    
    # Verify now_playing structure
    assert now_playing.source is not None
    assert now_playing.play_status is not None
    
    await client.close()
    print("✓ Now playing query successful")


if __name__ == "__main__":
    """
    Run all real device discovery tests.
    
    NOTE: Requires actual SoundTouch devices on network!
    """
    print("=" * 60)
    print("REAL DEVICE TESTS - Requires Hardware")
    print("=" * 60)
    print()
    print("⚠️  WARNING: These tests require actual Bose SoundTouch devices!")
    print("Make sure devices are powered on and connected to network.")
    print()
    
    # Run tests
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    sys.exit(exit_code)
