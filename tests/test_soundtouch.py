"""
Tests for SoundTouch Client Adapter
"""
import pytest
from unittest.mock import MagicMock, patch

from backend.adapters.bosesoundtouch_adapter import BoseSoundTouchClientAdapter
from backend.soundtouch import DeviceInfo, NowPlayingInfo


@pytest.mark.asyncio
async def test_get_info_success():
    """Test successful /info request."""
    # Mock SoundTouchDevice constructor to avoid actual network calls
    with patch('backend.adapters.bosesoundtouch_adapter.SoundTouchDevice') as mock_device_class:
        mock_device = MagicMock()
        mock_device_class.return_value = mock_device
        
        client = BoseSoundTouchClientAdapter("http://192.168.1.100:8090")
        
        # Mock BoseClient.GetInformation()
        mock_info = MagicMock()
        mock_info.DeviceId = "12345ABC"
        mock_info.Name = "Living Room"
        mock_info.Type = "SoundTouch 30"
        mock_info.FirmwareVersion = "28.0.5.46710"
        
        mock_network = MagicMock()
        mock_network.MacAddress = "AA:BB:CC:DD:EE:FF"
        mock_network.IpAddress = "192.168.1.100"
        mock_info.NetworkInfo = mock_network
        
        client._client.GetInformation = MagicMock(return_value=mock_info)
        
        info = await client.get_info()
        
        assert isinstance(info, DeviceInfo)
        assert info.device_id == "12345ABC"
        assert info.name == "Living Room"
        assert info.type == "SoundTouch 30"
        assert info.mac_address == "AA:BB:CC:DD:EE:FF"
        assert info.ip_address == "192.168.1.100"
        assert info.firmware_version == "28.0.5.46710"


@pytest.mark.asyncio
async def test_get_now_playing_success():
    """Test successful /now_playing request."""
    with patch('backend.adapters.bosesoundtouch_adapter.SoundTouchDevice') as mock_device_class:
        mock_device = MagicMock()
        mock_device_class.return_value = mock_device
        
        client = BoseSoundTouchClientAdapter("http://192.168.1.100:8090")
        
        # Mock BoseClient.GetNowPlaying()
        mock_now_playing = MagicMock()
        mock_now_playing.Source = "INTERNET_RADIO"
        mock_now_playing.PlayStatus = "PLAY_STATE"
        mock_now_playing.Art = "http://example.com/art.jpg"
        
        mock_content = MagicMock()
        mock_content.ItemName = "Radio Station Name"
        mock_now_playing.ContentItem = mock_content
        
        client._client.GetNowPlaying = MagicMock(return_value=mock_now_playing)
        
        now_playing = await client.get_now_playing()
        
        assert isinstance(now_playing, NowPlayingInfo)
        assert now_playing.source == "INTERNET_RADIO"
        assert now_playing.state == "PLAY_STATE"
        assert now_playing.station_name == "Radio Station Name"
        assert now_playing.artwork_url == "http://example.com/art.jpg"


@pytest.mark.asyncio
async def test_get_info_connection_error():
    """Test /info request with connection error."""
    from backend.exceptions import DeviceConnectionError
    
    with patch('backend.adapters.bosesoundtouch_adapter.SoundTouchDevice') as mock_device_class:
        mock_device = MagicMock()
        mock_device_class.return_value = mock_device
        
        client = BoseSoundTouchClientAdapter("http://192.168.1.100:8090")
        client._client.GetInformation = MagicMock(side_effect=Exception("Connection refused"))
        
        with pytest.raises(DeviceConnectionError):
            await client.get_info()


@pytest.mark.asyncio
async def test_parse_invalid_xml():
    """Test XML parsing with invalid response (library handles internally)."""
    from backend.exceptions import DeviceConnectionError
    
    with patch('backend.adapters.bosesoundtouch_adapter.SoundTouchDevice') as mock_device_class:
        mock_device = MagicMock()
        mock_device_class.return_value = mock_device
        
        client = BoseSoundTouchClientAdapter("http://192.168.1.100:8090")
        
        # bosesoundtouchapi handles XML parsing internally
        # We test error propagation instead
        client._client.GetInformation = MagicMock(side_effect=Exception("Invalid XML"))
        
        with pytest.raises(DeviceConnectionError):
            await client.get_info()


def test_client_base_url_trailing_slash():
    """Test that trailing slash is removed from base_url."""
    with patch('backend.adapters.bosesoundtouch_adapter.SoundTouchDevice') as mock_device_class:
        mock_device = MagicMock()
        mock_device_class.return_value = mock_device
        
        client = BoseSoundTouchClientAdapter("http://192.168.1.100:8090/")
        
        assert client.base_url == "http://192.168.1.100:8090"
