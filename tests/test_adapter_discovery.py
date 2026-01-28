"""
Tests for BoseSoundTouch Adapter
"""
import pytest
from unittest.mock import MagicMock, patch

from backend.adapters.bosesoundtouch_adapter import BoseSoundTouchDiscoveryAdapter
from backend.discovery import DiscoveredDevice
from backend.exceptions import DiscoveryError


@pytest.mark.asyncio
async def test_discovery_success():
    """Test successful device discovery."""
    discovery = BoseSoundTouchDiscoveryAdapter()
    
    # Mock SoundTouchDiscovery.DiscoverDevices
    mock_devices = {
        '192.168.1.100:8090': 'Living Room',
        '192.168.1.101:8090': 'Kitchen',
    }
    
    with patch('backend.adapters.bosesoundtouch_adapter.SoundTouchDiscovery') as mock_discovery_class:
        mock_discovery_class.DiscoverDevices.return_value = mock_devices
        
        devices = await discovery.discover(timeout=5)
        
        assert len(devices) == 2
        assert all(isinstance(d, DiscoveredDevice) for d in devices)
        assert devices[0].ip == '192.168.1.100'
        assert devices[0].port == 8090
        assert devices[0].name == 'Living Room'
        assert devices[1].ip == '192.168.1.101'
        assert devices[1].name == 'Kitchen'
        
        # Verify timeout was passed
        mock_discovery_class.DiscoverDevices.assert_called_once_with(timeout=5)


@pytest.mark.asyncio
async def test_discovery_no_devices():
    """Test discovery when no devices are found."""
    discovery = BoseSoundTouchDiscoveryAdapter()
    
    with patch('backend.adapters.bosesoundtouch_adapter.SoundTouchDiscovery') as mock_discovery_class:
        mock_discovery_class.DiscoverDevices.return_value = {}
        
        devices = await discovery.discover()
        
        assert len(devices) == 0
        assert devices == []


@pytest.mark.asyncio
async def test_discovery_error():
    """Test discovery when an error occurs."""
    discovery = BoseSoundTouchDiscoveryAdapter()
    
    with patch('backend.adapters.bosesoundtouch_adapter.SoundTouchDiscovery') as mock_discovery_class:
        mock_discovery_class.DiscoverDevices.side_effect = Exception("Network error")
        
        with pytest.raises(DiscoveryError) as exc_info:
            await discovery.discover()
        
        assert "Failed to discover devices" in str(exc_info.value)
        assert "Network error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_discovery_address_parsing():
    """Test parsing of various address formats."""
    discovery = BoseSoundTouchDiscoveryAdapter()
    
    test_cases = [
        ('192.168.1.100:8090', '192.168.1.100', 8090),
        ('10.0.0.5:9000', '10.0.0.5', 9000),
        ('192.168.1.200', '192.168.1.200', 8090),  # No port -> default 8090
    ]
    
    for address, expected_ip, expected_port in test_cases:
        mock_devices = {address: 'Test Device'}
        
        with patch('backend.adapters.bosesoundtouch_adapter.SoundTouchDiscovery') as mock_discovery_class:
            mock_discovery_class.DiscoverDevices.return_value = mock_devices
            
            devices = await discovery.discover()
            
            assert len(devices) == 1
            assert devices[0].ip == expected_ip
            assert devices[0].port == expected_port


@pytest.mark.asyncio
async def test_discovery_lazy_loading():
    """Test that discovery doesn't fetch device details (lazy loading)."""
    discovery = BoseSoundTouchDiscoveryAdapter()
    
    mock_devices = {'192.168.1.100:8090': 'Test Device'}
    
    with patch('backend.adapters.bosesoundtouch_adapter.SoundTouchDiscovery') as mock_discovery_class:
        mock_discovery_class.DiscoverDevices.return_value = mock_devices
        
        devices = await discovery.discover()
        
        # Device details should NOT be fetched during discovery (lazy loading)
        assert devices[0].model is None
        assert devices[0].mac_address is None
        assert devices[0].firmware_version is None
        # Only IP and name should be set
        assert devices[0].ip == '192.168.1.100'
        assert devices[0].name == 'Test Device'
