"""
Tests for BoseSoundTouch Adapter
"""

import pytest
from unittest.mock import AsyncMock, patch

from cloudtouch.devices.adapter import BoseSoundTouchDiscoveryAdapter
from cloudtouch.discovery import DiscoveredDevice
from cloudtouch.core.exceptions import DiscoveryError


@pytest.mark.asyncio
async def test_discovery_success():
    """Test successful device discovery."""
    discovery = BoseSoundTouchDiscoveryAdapter()

    # Mock SSDP discovery result
    mock_devices = {
        "AA:BB:CC:11:22:33": {
            "ip": "192.168.1.100",
            "mac": "AA:BB:CC:11:22:33",
            "name": "Living Room",
        },
        "AA:BB:CC:11:22:44": {
            "ip": "192.168.1.101",
            "mac": "AA:BB:CC:11:22:44",
            "name": "Kitchen",
        },
    }

    with patch("cloudtouch.devices.adapter.SSDPDiscovery") as mock_ssdp_class:
        mock_ssdp_instance = AsyncMock()
        mock_ssdp_instance.discover.return_value = mock_devices
        mock_ssdp_class.return_value = mock_ssdp_instance

        devices = await discovery.discover(timeout=5)

        assert len(devices) == 2
        assert all(isinstance(d, DiscoveredDevice) for d in devices)
        assert devices[0].ip == "192.168.1.100"
        assert devices[0].port == 8090
        assert devices[0].name == "Living Room"
        assert devices[1].ip == "192.168.1.101"
        assert devices[1].name == "Kitchen"

        # Verify timeout was passed
        mock_ssdp_class.assert_called_once_with(timeout=5)


@pytest.mark.asyncio
async def test_discovery_no_devices():
    """Test discovery when no devices are found."""
    discovery = BoseSoundTouchDiscoveryAdapter()

    with patch("cloudtouch.devices.adapter.SSDPDiscovery") as mock_ssdp_class:
        mock_ssdp_instance = AsyncMock()
        mock_ssdp_instance.discover.return_value = {}
        mock_ssdp_class.return_value = mock_ssdp_instance

        devices = await discovery.discover()

        assert len(devices) == 0
        assert devices == []


@pytest.mark.asyncio
async def test_discovery_error():
    """Test discovery when an error occurs."""
    discovery = BoseSoundTouchDiscoveryAdapter()

    with patch("cloudtouch.devices.adapter.SSDPDiscovery") as mock_ssdp_class:
        mock_ssdp_instance = AsyncMock()
        mock_ssdp_instance.discover.side_effect = Exception("Network error")
        mock_ssdp_class.return_value = mock_ssdp_instance

        with pytest.raises(DiscoveryError) as exc_info:
            await discovery.discover()

        assert "Failed to discover devices" in str(exc_info.value)
        assert "Network error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_discovery_address_parsing():
    """Test parsing of various address formats."""
    discovery = BoseSoundTouchDiscoveryAdapter()

    # Test MAC-based device dictionary (new SSDP format)
    mock_devices = {"AA:BB:CC:11:22:33": {"ip": "192.168.1.100", "name": "Test Device"}}

    with patch("cloudtouch.devices.adapter.SSDPDiscovery") as mock_ssdp_class:
        mock_ssdp_instance = AsyncMock()
        mock_ssdp_instance.discover.return_value = mock_devices
        mock_ssdp_class.return_value = mock_ssdp_instance

        devices = await discovery.discover()

        assert len(devices) == 1
        assert devices[0].ip == "192.168.1.100"
        assert devices[0].port == 8090
        assert devices[0].name == "Test Device"


@pytest.mark.asyncio
async def test_discovery_lazy_loading():
    """Test that discovery doesn't fetch device details (lazy loading)."""
    discovery = BoseSoundTouchDiscoveryAdapter()

    mock_devices = {"AA:BB:CC:11:22:33": {"ip": "192.168.1.100", "name": "Test Device"}}

    with patch("cloudtouch.devices.adapter.SSDPDiscovery") as mock_ssdp_class:
        mock_ssdp_instance = AsyncMock()
        mock_ssdp_instance.discover.return_value = mock_devices
        mock_ssdp_class.return_value = mock_ssdp_instance

        devices = await discovery.discover()

        # Device details should NOT be fetched during discovery (lazy loading)
        assert devices[0].model is None
        assert devices[0].mac_address is None
        assert devices[0].firmware_version is None
        # Only IP and name should be set
        assert devices[0].ip == "192.168.1.100"
        assert devices[0].name == "Test Device"


@pytest.mark.asyncio
async def test_discovery_duplicate_detection_same_device_different_sources():
    """Test duplicate detection when device found via both SSDP and Manual IPs.

    Edge case: Device discovered via SSDP and also listed in manual IPs.
    Expected: Deduplication happens at Repository level, not Discovery.

    This test documents current behavior: Discovery layer doesn't deduplicate,
    that's the responsibility of DeviceRepository.upsert() using device_id as key.
    """
    discovery = BoseSoundTouchDiscoveryAdapter()

    # Device found via SSDP
    mock_ssdp_devices = {
        "B92C7D383488": {  # MAC from serial number
            "ip": "192.0.2.78",
            "mac": "B92C7D383488",
            "name": "Wohnzimmer",
            "model": "SoundTouch 30",
        }
    }

    with patch("cloudtouch.devices.adapter.SSDPDiscovery") as mock_ssdp_class:
        mock_ssdp_instance = AsyncMock()
        mock_ssdp_instance.discover.return_value = mock_ssdp_devices
        mock_ssdp_class.return_value = mock_ssdp_instance

        devices = await discovery.discover()

        # Discovery returns raw results without deduplication
        assert len(devices) == 1
        assert devices[0].ip == "192.0.2.78"
        assert devices[0].name == "Wohnzimmer"

        # Note: If same device also in manual IPs, it will appear twice
        # Deduplication happens in sync_devices() using device_id


@pytest.mark.asyncio
async def test_discovery_ipv6_addresses_in_ssdp_response():
    """Test that IPv6 addresses from SSDP discovery are handled correctly.

    Edge case: Network has IPv6 enabled, devices announce with IPv6.
    Expected: IPv6 addresses are preserved and passed through.
    """
    discovery = BoseSoundTouchDiscoveryAdapter()

    # SSDP can return IPv6 addresses
    mock_devices = {
        "AA:BB:CC:11:22:33": {
            "ip": "2001:db8::1",  # IPv6
            "name": "IPv6 Device",
            "model": "SoundTouch 10",
        },
        "AA:BB:CC:11:22:44": {
            "ip": "192.168.1.100",  # IPv4
            "name": "IPv4 Device",
            "model": "SoundTouch 20",
        },
    }

    with patch("cloudtouch.devices.adapter.SSDPDiscovery") as mock_ssdp_class:
        mock_ssdp_instance = AsyncMock()
        mock_ssdp_instance.discover.return_value = mock_devices
        mock_ssdp_class.return_value = mock_ssdp_instance

        devices = await discovery.discover()

        assert len(devices) == 2
        # Find IPv6 device
        ipv6_device = next(d for d in devices if ":" in d.ip)
        assert ipv6_device.ip == "2001:db8::1"
        assert ipv6_device.name == "IPv6 Device"

        # Find IPv4 device
        ipv4_device = next(d for d in devices if "." in d.ip)
        assert ipv4_device.ip == "192.168.1.100"
        assert ipv4_device.name == "IPv4 Device"
