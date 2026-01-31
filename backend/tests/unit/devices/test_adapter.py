"""
Tests for BoseSoundTouch Adapter
"""
import pytest
from unittest.mock import AsyncMock, patch

from soundtouch_bridge.devices.adapter import BoseSoundTouchDiscoveryAdapter
from soundtouch_bridge.discovery import DiscoveredDevice
from soundtouch_bridge.core.exceptions import DiscoveryError


@pytest.mark.asyncio
async def test_discovery_success():
    """Test successful device discovery."""
    discovery = BoseSoundTouchDiscoveryAdapter()
    
    # Mock SSDP discovery result
    mock_devices = {
        'AA:BB:CC:11:22:33': {'ip': '192.168.1.100', 'mac': 'AA:BB:CC:11:22:33', 'name': 'Living Room'},
        'AA:BB:CC:11:22:44': {'ip': '192.168.1.101', 'mac': 'AA:BB:CC:11:22:44', 'name': 'Kitchen'},
    }
    
    with patch('soundtouch_bridge.devices.adapter.SSDPDiscovery') as mock_ssdp_class:
        mock_ssdp_instance = AsyncMock()
        mock_ssdp_instance.discover.return_value = mock_devices
        mock_ssdp_class.return_value = mock_ssdp_instance
        
        devices = await discovery.discover(timeout=5)
        
        assert len(devices) == 2
        assert all(isinstance(d, DiscoveredDevice) for d in devices)
        assert devices[0].ip == '192.168.1.100'
        assert devices[0].port == 8090
        assert devices[0].name == 'Living Room'
        assert devices[1].ip == '192.168.1.101'
        assert devices[1].name == 'Kitchen'
        
        # Verify timeout was passed
        mock_ssdp_class.assert_called_once_with(timeout=5)


@pytest.mark.asyncio
async def test_discovery_no_devices():
    """Test discovery when no devices are found."""
    discovery = BoseSoundTouchDiscoveryAdapter()
    
    with patch('soundtouch_bridge.devices.adapter.SSDPDiscovery') as mock_ssdp_class:
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
    
    with patch('soundtouch_bridge.devices.adapter.SSDPDiscovery') as mock_ssdp_class:
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
    mock_devices = {
        'AA:BB:CC:11:22:33': {'ip': '192.168.1.100', 'name': 'Test Device'}
    }
    
    with patch('soundtouch_bridge.devices.adapter.SSDPDiscovery') as mock_ssdp_class:
        mock_ssdp_instance = AsyncMock()
        mock_ssdp_instance.discover.return_value = mock_devices
        mock_ssdp_class.return_value = mock_ssdp_instance
        
        devices = await discovery.discover()
        
        assert len(devices) == 1
        assert devices[0].ip == '192.168.1.100'
        assert devices[0].port == 8090
        assert devices[0].name == 'Test Device'


@pytest.mark.asyncio
async def test_discovery_lazy_loading():
    """Test that discovery doesn't fetch device details (lazy loading)."""
    discovery = BoseSoundTouchDiscoveryAdapter()
    
    mock_devices = {
        'AA:BB:CC:11:22:33': {'ip': '192.168.1.100', 'name': 'Test Device'}
    }
    
    with patch('soundtouch_bridge.devices.adapter.SSDPDiscovery') as mock_ssdp_class:
        mock_ssdp_instance = AsyncMock()
        mock_ssdp_instance.discover.return_value = mock_devices
        mock_ssdp_class.return_value = mock_ssdp_instance
        
        devices = await discovery.discover()
        
        # Device details should NOT be fetched during discovery (lazy loading)
        assert devices[0].model is None
        assert devices[0].mac_address is None
        assert devices[0].firmware_version is None
        # Only IP and name should be set
        assert devices[0].ip == '192.168.1.100'
        assert devices[0].name == 'Test Device'
