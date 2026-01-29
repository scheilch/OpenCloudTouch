"""
Tests for SSDP Discovery
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import socket

from backend.adapters.ssdp_discovery import SSDPDiscovery


@pytest.mark.asyncio
async def test_ssdp_discovery_success():
    """Test successful SSDP discovery."""
    discovery = SSDPDiscovery(timeout=5)
    
    # Mock the device description response
    mock_device_info = {
        'AA:BB:CC:11:22:33': {
            'ip': '192.168.1.100',
            'mac': 'AA:BB:CC:11:22:33',
            'name': 'Living Room',
            'model': 'SoundTouch 10'
        }
    }
    
    with patch.object(discovery, '_ssdp_msearch', return_value=['http://192.168.1.100:8090/info']):
        with patch.object(discovery, '_fetch_device_descriptions', return_value=mock_device_info):
            devices = await discovery.discover()
            
            assert len(devices) == 1
            assert 'AA:BB:CC:11:22:33' in devices
            assert devices['AA:BB:CC:11:22:33']['ip'] == '192.168.1.100'
            assert devices['AA:BB:CC:11:22:33']['name'] == 'Living Room'


@pytest.mark.asyncio
async def test_ssdp_discovery_no_devices():
    """Test SSDP discovery when no devices are found."""
    discovery = SSDPDiscovery(timeout=5)
    
    with patch.object(discovery, '_ssdp_msearch', return_value=[]):
        with patch.object(discovery, '_fetch_device_descriptions', return_value={}):
            devices = await discovery.discover()
            
            assert devices == {}


@pytest.mark.asyncio
async def test_ssdp_discovery_error():
    """Test SSDP discovery when an error occurs."""
    discovery = SSDPDiscovery(timeout=5)
    
    with patch.object(discovery, '_ssdp_msearch', side_effect=Exception("Network error")):
        devices = await discovery.discover()
        
        # Should return empty dict on error, not raise
        assert devices == {}


def test_parse_location():
    """Test parsing LOCATION header from SSDP response."""
    discovery = SSDPDiscovery()
    
    response = (
        "HTTP/1.1 200 OK\r\n"
        "CACHE-CONTROL: max-age=1800\r\n"
        "LOCATION: http://192.168.1.100:8090/info\r\n"
        "SERVER: Linux UPnP/1.0 Bose SoundTouch\r\n"
        "\r\n"
    )
    
    location = discovery._parse_location(response)
    assert location == "http://192.168.1.100:8090/info"


def test_parse_location_no_header():
    """Test parsing LOCATION when header is missing."""
    discovery = SSDPDiscovery()
    
    response = (
        "HTTP/1.1 200 OK\r\n"
        "CACHE-CONTROL: max-age=1800\r\n"
        "\r\n"
    )
    
    location = discovery._parse_location(response)
    assert location is None


@pytest.mark.asyncio
async def test_fetch_device_descriptions_filters_non_bose():
    """Test that non-Bose devices are filtered out."""
    discovery = SSDPDiscovery()
    
    # Mock httpx to return non-Bose device
    mock_response = MagicMock()
    mock_response.text = """<?xml version="1.0"?>
    <root xmlns="urn:schemas-upnp-org:device-1-0">
        <device>
            <manufacturer>NotBose</manufacturer>
            <friendlyName>Other Device</friendlyName>
        </device>
    </root>"""
    mock_response.raise_for_status = MagicMock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client.return_value = mock_client_instance
        
        devices = await discovery._fetch_device_descriptions(['http://192.168.1.100:8090/info'])
        
        # Non-Bose device should be filtered out
        assert devices == {}
