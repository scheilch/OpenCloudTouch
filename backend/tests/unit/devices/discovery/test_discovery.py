"""
Tests for Device Discovery
"""
import pytest

from soundtouch_bridge.discovery import DiscoveredDevice
from soundtouch_bridge.devices.discovery.manual import ManualDiscovery


@pytest.mark.asyncio
async def test_manual_discovery():
    """Test manual discovery with configured IPs."""
    ips = ["192.168.1.100", "192.168.1.101"]
    discovery = ManualDiscovery(ips)
    
    devices = await discovery.discover()
    
    assert len(devices) == 2
    assert all(isinstance(d, DiscoveredDevice) for d in devices)
    assert devices[0].ip == "192.168.1.100"
    assert devices[1].ip == "192.168.1.101"
    assert all(d.port == 8090 for d in devices)


@pytest.mark.asyncio
async def test_manual_discovery_empty():
    """Test manual discovery with empty IP list."""
    discovery = ManualDiscovery([])
    
    devices = await discovery.discover()
    
    assert len(devices) == 0


def test_discovered_device_base_url():
    """Test DiscoveredDevice base_url property."""
    device = DiscoveredDevice(ip="192.168.1.100", port=8090)
    
    assert device.base_url == "http://192.168.1.100:8090"


def test_discovered_device_custom_port():
    """Test DiscoveredDevice with custom port."""
    device = DiscoveredDevice(ip="192.168.1.100", port=9000)
    
    assert device.base_url == "http://192.168.1.100:9000"
