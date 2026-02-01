"""
Tests for backend/discovery/manual.py

Manual discovery allows users to specify device IPs when SSDP doesn't work.
"""

import pytest

from cloudtouch.devices.discovery.manual import ManualDiscovery
from cloudtouch.discovery import DiscoveredDevice


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


@pytest.mark.asyncio
async def test_manual_discovery_ipv6_address():
    """Test manual discovery with IPv6 address.

    Edge case: User configures IPv6 addresses in manual IP list.
    Expected: IPv6 addresses are accepted and passed through.
    """
    # Arrange - various valid IPv6 formats
    manual_ips = [
        "2001:db8::1",  # Compressed
        "fe80::1",  # Link-local
        "::1",  # Loopback
        "2001:0db8:0000:0000:0000:0000:0000:0001",  # Full format
    ]
    discovery = ManualDiscovery(device_ips=manual_ips)

    # Act
    devices = await discovery.discover()

    # Assert
    assert len(devices) == 4
    assert devices[0].ip == "2001:db8::1"
    assert devices[1].ip == "fe80::1"
    assert devices[2].ip == "::1"
    assert devices[3].ip == "2001:0db8:0000:0000:0000:0000:0000:0001"


@pytest.mark.asyncio
async def test_manual_discovery_mixed_ipv4_ipv6():
    """Test manual discovery with mixed IPv4 and IPv6 addresses.

    Edge case: User has both IPv4 and IPv6 enabled network.
    Expected: Both address types are supported.
    """
    # Arrange
    manual_ips = [
        "192.168.1.100",  # IPv4
        "2001:db8::1",  # IPv6
        "10.0.0.1",  # IPv4
        "fe80::1",  # IPv6 link-local
    ]
    discovery = ManualDiscovery(device_ips=manual_ips)

    # Act
    devices = await discovery.discover()

    # Assert
    assert len(devices) == 4
    ipv4_devices = [d for d in devices if "." in d.ip]
    ipv6_devices = [d for d in devices if ":" in d.ip]
    assert len(ipv4_devices) == 2
    assert len(ipv6_devices) == 2


@pytest.mark.asyncio
async def test_manual_discovery_duplicate_ips():
    """Test manual discovery with duplicate IPs in config.

    Edge case: User accidentally duplicates IPs in config file.
    Expected: All entries are preserved (deduplication happens at higher level).
    """
    # Arrange
    manual_ips = ["192.168.1.100", "192.168.1.100", "192.168.1.101"]
    discovery = ManualDiscovery(device_ips=manual_ips)

    # Act
    devices = await discovery.discover()

    # Assert
    # Manual discovery doesn't deduplicate - that's the adapter's job
    assert len(devices) == 3
    assert devices[0].ip == "192.168.1.100"
    assert devices[1].ip == "192.168.1.100"
    assert devices[2].ip == "192.168.1.101"
