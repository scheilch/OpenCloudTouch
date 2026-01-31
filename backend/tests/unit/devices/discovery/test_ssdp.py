"""
Tests for SSDP Discovery
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import socket
from xml.etree import ElementTree

from soundtouch_bridge.devices.discovery.ssdp import SSDPDiscovery


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


@pytest.mark.asyncio
async def test_fetch_device_descriptions_bose_device():
    """Test that Bose devices are correctly parsed with namespace."""
    discovery = SSDPDiscovery()
    
    # Real Bose SoundTouch XML with namespace
    mock_response = MagicMock()
    mock_response.text = """<?xml version="1.0"?>
    <root xmlns="urn:schemas-upnp-org:device-1-0">
        <device>
            <deviceType>urn:schemas-upnp-org:device:MediaRenderer:1</deviceType>
            <friendlyName>Living Room</friendlyName>
            <manufacturer>Bose Corporation</manufacturer>
            <modelName>SoundTouch 30</modelName>
            <serialNumber>B92C7D383488</serialNumber>
        </device>
    </root>"""
    mock_response.raise_for_status = MagicMock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client.return_value = mock_client_instance
        
        devices = await discovery._fetch_device_descriptions(['http://192.168.1.100:8091/XD/BO5EBO5E-F00D-F00D-FEED-B92C7D383488.xml'])
        
        # Bose device should be parsed correctly
        assert len(devices) == 1
        # MAC should be extracted from serial number (last 12 chars formatted as MAC)
        mac_key = list(devices.keys())[0]
        device = devices[mac_key]
        assert device['name'] == 'Living Room'
        assert device['model'] == 'SoundTouch 30'
        assert device['ip'] == '192.168.1.100'


def test_xml_namespace_parsing_regression():
    """Regression test for XML namespace handling in SSDP discovery.
    
    Bug: _find_xml_text() failed to parse elements with xmlns namespace.
    Fixed: 2026-01-29 - Implemented namespace-agnostic element search.
    
    Root cause: ElementTree.find() requires namespace mapping for namespaced XML.
    Solution: Iterate through elements and match by tag suffix (local name).
    """
    discovery = SSDPDiscovery()
    
    # XML with UPnP namespace (real Bose device format)
    xml_with_namespace = '''<?xml version="1.0"?>
    <root xmlns="urn:schemas-upnp-org:device-1-0">
        <device>
            <manufacturer>Bose Corporation</manufacturer>
            <friendlyName>Living Room</friendlyName>
            <modelName>SoundTouch 10</modelName>
        </device>
    </root>'''
    
    root = ElementTree.fromstring(xml_with_namespace)
    
    # These should all work with namespace-agnostic parsing
    manufacturer = discovery._find_xml_text(root, ".//manufacturer")
    assert manufacturer == "Bose Corporation"
    
    friendly_name = discovery._find_xml_text(root, ".//friendlyName")
    assert friendly_name == "Living Room"
    
    model_name = discovery._find_xml_text(root, ".//modelName")
    assert model_name == "SoundTouch 10"


def test_xml_without_namespace_still_works():
    """Ensure namespace-agnostic parsing doesn't break non-namespaced XML."""
    discovery = SSDPDiscovery()
    
    # XML without namespace
    xml_without_namespace = '''<?xml version="1.0"?>
    <root>
        <device>
            <manufacturer>Bose Corporation</manufacturer>
        </device>
    </root>'''
    
    root = ElementTree.fromstring(xml_without_namespace)
    manufacturer = discovery._find_xml_text(root, ".//manufacturer")
    assert manufacturer == "Bose Corporation"
