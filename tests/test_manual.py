"""
Tests for backend/discovery/manual.py

Manual discovery allows users to specify device IPs when SSDP doesn't work.
"""
import pytest

from backend.discovery.manual import ManualDiscovery
from backend.discovery import DiscoveredDevice


@pytest.mark.asyncio
async def test_manual_discovery_single_ip():
    """Test manual discovery with single IP address."""
    # Arrange
    manual_ips = ["192.168.1.100"]
    discovery = ManualDiscovery(device_ips=manual_ips)
    
    # Act
    devices = await discovery.discover()
    
    # Assert
    assert len(devices) == 1
    assert devices[0].ip == "192.168.1.100"
    assert devices[0].port == 8090  # Default SoundTouch port


@pytest.mark.asyncio
async def test_manual_discovery_multiple_ips():
    """Test manual discovery with multiple IP addresses."""
    # Arrange
    manual_ips = ["192.168.1.100", "192.168.1.101", "192.168.1.102"]
    discovery = ManualDiscovery(device_ips=manual_ips)
    
    # Act
    devices = await discovery.discover()
    
    # Assert
    assert len(devices) == 3
    assert devices[0].ip == "192.168.1.100"
    assert devices[1].ip == "192.168.1.101"
    assert devices[2].ip == "192.168.1.102"
    for device in devices:
        assert device.port == 8090
        assert isinstance(device, DiscoveredDevice)


@pytest.mark.asyncio
async def test_manual_discovery_empty_list():
    """Test manual discovery with empty IP list."""
    # Arrange
    manual_ips = []
    discovery = ManualDiscovery(device_ips=manual_ips)
    
    # Act
    devices = await discovery.discover()
    
    # Assert
    assert len(devices) == 0


@pytest.mark.asyncio
async def test_manual_discovery_timeout_ignored():
    """Test that timeout parameter is ignored in manual discovery."""
    # Arrange
    manual_ips = ["192.168.1.100"]
    discovery = ManualDiscovery(device_ips=manual_ips)
    
    # Act
    devices_default = await discovery.discover()
    devices_with_timeout = await discovery.discover(timeout=30)
    
    # Assert
    assert len(devices_default) == 1
    assert len(devices_with_timeout) == 1
    assert devices_default[0].ip == devices_with_timeout[0].ip


@pytest.mark.asyncio
async def test_manual_discovery_preserves_order():
    """Test that manual discovery preserves IP order."""
    # Arrange
    manual_ips = ["10.0.0.1", "192.168.1.50", "172.16.0.100"]
    discovery = ManualDiscovery(device_ips=manual_ips)
    
    # Act
    devices = await discovery.discover()
    
    # Assert
    assert [d.ip for d in devices] == manual_ips
