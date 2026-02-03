"""
Tests for BoseSoundTouch Adapter
"""

from unittest.mock import AsyncMock, patch

import pytest

from cloudtouch.core.exceptions import DiscoveryError
from cloudtouch.devices.adapter import BoseSoundTouchDiscoveryAdapter
from cloudtouch.discovery import DiscoveredDevice


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
            "name": "Living Room",
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
        assert devices[0].name == "Living Room"

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


# ==================== CLIENT ADAPTER TESTS ====================


@pytest.mark.asyncio
async def test_client_extract_firmware_version_missing_components():
    """Test firmware extraction when Components list is empty."""
    from cloudtouch.devices.adapter import BoseSoundTouchClientAdapter
    from unittest.mock import MagicMock

    # Mock info object without Components
    mock_info = MagicMock()
    mock_info.Components = []  # Empty list

    with patch("cloudtouch.devices.adapter.SoundTouchDevice"):
        with patch("cloudtouch.devices.adapter.BoseClient"):
            client = BoseSoundTouchClientAdapter("http://192.168.1.100:8090")
            version = client._extract_firmware_version(mock_info)

            assert version == ""


@pytest.mark.asyncio
async def test_client_extract_firmware_version_no_software_version():
    """Test firmware extraction when SoftwareVersion attribute is missing."""
    from cloudtouch.devices.adapter import BoseSoundTouchClientAdapter
    from unittest.mock import MagicMock

    # Mock info with Components but no SoftwareVersion
    mock_info = MagicMock()
    mock_component = MagicMock(spec=[])  # Component without SoftwareVersion
    del mock_component.SoftwareVersion
    mock_info.Components = [mock_component]

    with patch("cloudtouch.devices.adapter.SoundTouchDevice"):
        with patch("cloudtouch.devices.adapter.BoseClient"):
            client = BoseSoundTouchClientAdapter("http://192.168.1.100:8090")
            version = client._extract_firmware_version(mock_info)

            assert version == ""


@pytest.mark.asyncio
async def test_client_extract_ip_address_no_network_info():
    """Test IP extraction when NetworkInfo is empty."""
    from cloudtouch.devices.adapter import BoseSoundTouchClientAdapter
    from unittest.mock import MagicMock

    # Mock info without NetworkInfo
    mock_info = MagicMock()
    mock_info.NetworkInfo = []

    with patch("cloudtouch.devices.adapter.SoundTouchDevice"):
        with patch("cloudtouch.devices.adapter.BoseClient"):
            client = BoseSoundTouchClientAdapter("http://192.168.1.100:8090")
            ip = client._extract_ip_address(mock_info)

            # Should fallback to self.ip
            assert ip == "192.168.1.100"


@pytest.mark.asyncio
async def test_client_extract_ip_address_no_ip_address_attribute():
    """Test IP extraction when IpAddress attribute is missing."""
    from cloudtouch.devices.adapter import BoseSoundTouchClientAdapter
    from unittest.mock import MagicMock

    # Mock info with NetworkInfo but no IpAddress
    mock_info = MagicMock()
    mock_network = MagicMock(spec=[])  # Network without IpAddress
    del mock_network.IpAddress
    mock_info.NetworkInfo = [mock_network]

    with patch("cloudtouch.devices.adapter.SoundTouchDevice"):
        with patch("cloudtouch.devices.adapter.BoseClient"):
            client = BoseSoundTouchClientAdapter("http://192.168.1.100:8090")
            ip = client._extract_ip_address(mock_info)

            # Should fallback to self.ip
            assert ip == "192.168.1.100"


@pytest.mark.asyncio
async def test_client_get_now_playing_success():
    """Test successful get_now_playing call."""
    from cloudtouch.devices.adapter import BoseSoundTouchClientAdapter
    from unittest.mock import MagicMock

    # Mock now playing status
    mock_status = MagicMock()
    mock_status.PlayStatus = "PLAY_STATE"
    mock_status.Source = "SPOTIFY"
    mock_status.StationName = "Chill Hits"
    mock_status.Artist = "Artist Name"
    mock_status.Track = "Track Title"
    mock_status.Album = "Album Name"
    mock_status.ArtUrl = "http://example.com/art.jpg"

    with patch("cloudtouch.devices.adapter.SoundTouchDevice"):
        with patch("cloudtouch.devices.adapter.BoseClient") as mock_bose_client:
            mock_bose_client.return_value.GetNowPlayingStatus.return_value = mock_status

            client = BoseSoundTouchClientAdapter("http://192.168.1.100:8090")
            info = await client.get_now_playing()

            assert info.source == "SPOTIFY"
            assert info.state == "PLAY_STATE"
            assert info.station_name == "Chill Hits"
            assert info.artist == "Artist Name"
            assert info.track == "Track Title"
            assert info.album == "Album Name"
            assert info.artwork_url == "http://example.com/art.jpg"


@pytest.mark.asyncio
async def test_client_get_now_playing_minimal():
    """Test get_now_playing with minimal data (no optional fields)."""
    from cloudtouch.devices.adapter import BoseSoundTouchClientAdapter
    from unittest.mock import MagicMock

    # Mock now playing with only required fields
    mock_status = MagicMock(spec=["PlayStatus", "Source"])
    mock_status.PlayStatus = "STOP_STATE"
    mock_status.Source = "STANDBY"

    with patch("cloudtouch.devices.adapter.SoundTouchDevice"):
        with patch("cloudtouch.devices.adapter.BoseClient") as mock_bose_client:
            mock_bose_client.return_value.GetNowPlayingStatus.return_value = mock_status

            client = BoseSoundTouchClientAdapter("http://192.168.1.100:8090")
            info = await client.get_now_playing()

            assert info.source == "STANDBY"
            assert info.state == "STOP_STATE"
            assert info.station_name is None
            assert info.artist is None
            assert info.track is None
            assert info.album is None
            assert info.artwork_url is None


@pytest.mark.asyncio
async def test_client_get_now_playing_error():
    """Test get_now_playing when an error occurs."""
    from cloudtouch.devices.adapter import BoseSoundTouchClientAdapter
    from cloudtouch.core.exceptions import DeviceConnectionError

    with patch("cloudtouch.devices.adapter.SoundTouchDevice"):
        with patch("cloudtouch.devices.adapter.BoseClient") as mock_bose_client:
            mock_bose_client.return_value.GetNowPlayingStatus.side_effect = Exception(
                "Connection timeout"
            )

            client = BoseSoundTouchClientAdapter("http://192.168.1.100:8090")

            with pytest.raises(DeviceConnectionError) as exc_info:
                await client.get_now_playing()

            assert "Connection timeout" in str(exc_info.value)


# ==================== FACTORY FUNCTION TESTS ====================


def test_get_discovery_adapter_real_mode():
    """Test factory returns real adapter in normal mode."""
    from cloudtouch.devices.adapter import get_discovery_adapter

    with patch.dict("os.environ", {"CT_MOCK_MODE": "false"}, clear=False):
        adapter = get_discovery_adapter(timeout=15)

        from cloudtouch.devices.adapter import BoseSoundTouchDiscoveryAdapter

        assert isinstance(adapter, BoseSoundTouchDiscoveryAdapter)


def test_get_discovery_adapter_mock_mode():
    """Test factory returns mock adapter in mock mode."""
    from cloudtouch.devices.adapter import get_discovery_adapter

    with patch.dict("os.environ", {"CT_MOCK_MODE": "true"}, clear=False):
        adapter = get_discovery_adapter(timeout=15)

        from cloudtouch.devices.discovery.mock import MockDiscoveryAdapter

        assert isinstance(adapter, MockDiscoveryAdapter)


def test_get_soundtouch_client_real_mode():
    """Test factory returns real client in normal mode."""
    from cloudtouch.devices.adapter import get_soundtouch_client

    with patch.dict("os.environ", {"CT_MOCK_MODE": "false"}, clear=False):
        with patch("cloudtouch.devices.adapter.SoundTouchDevice"):
            with patch("cloudtouch.devices.adapter.BoseClient"):
                client = get_soundtouch_client("http://192.168.1.100:8090")

                from cloudtouch.devices.adapter import BoseSoundTouchClientAdapter

                assert isinstance(client, BoseSoundTouchClientAdapter)


def test_get_soundtouch_client_mock_mode():
    """Test factory returns mock client in mock mode."""
    from cloudtouch.devices.adapter import get_soundtouch_client

    with patch.dict("os.environ", {"CT_MOCK_MODE": "true"}, clear=False):
        client = get_soundtouch_client("http://192.168.1.100:8090")

        from cloudtouch.devices.mock_client import MockSoundTouchClient

        assert isinstance(client, MockSoundTouchClient)


def test_get_soundtouch_client_mock_mode_ip_matching():
    """Test mock client factory matches IP to mock device."""
    from cloudtouch.devices.adapter import get_soundtouch_client
    from cloudtouch.devices.mock_client import MockSoundTouchClient

    # Mock devices should have known IP addresses
    with patch.dict("os.environ", {"CT_MOCK_MODE": "true"}, clear=False):
        # Use IP from first mock device
        first_mac = list(MockSoundTouchClient.MOCK_DEVICES.keys())[0]
        mock_ip = MockSoundTouchClient.MOCK_DEVICES[first_mac]["info"].ip_address

        client = get_soundtouch_client(f"http://{mock_ip}:8090")

        assert isinstance(client, MockSoundTouchClient)
        assert client.ip_address == mock_ip


def test_get_soundtouch_client_mock_mode_unknown_ip():
    """Test mock client factory fallback for unknown IP."""
    from cloudtouch.devices.adapter import get_soundtouch_client
    from cloudtouch.devices.mock_client import MockSoundTouchClient

    with patch.dict("os.environ", {"CT_MOCK_MODE": "true"}, clear=False):
        # Use unknown IP
        client = get_soundtouch_client("http://10.0.0.1:8090")

        # Should fallback to first mock device but keep provided IP
        assert isinstance(client, MockSoundTouchClient)
        assert client.ip_address == "10.0.0.1"  # IP from base_url preserved

