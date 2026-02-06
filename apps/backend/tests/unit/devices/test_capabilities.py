"""
Tests for device capability detection.
"""

from unittest.mock import MagicMock

import pytest
from bosesoundtouchapi import SoundTouchClient, SoundTouchError
from bosesoundtouchapi.models import Capabilities, Information, SourceList

from opencloudtouch.devices.capabilities import (
    DeviceCapabilities,
    get_device_capabilities,
    get_feature_flags_for_ui,
    safe_api_call,
)


@pytest.fixture
def mock_client_st30():
    """Mock SoundTouchClient for SoundTouch 30."""
    client = MagicMock(spec=SoundTouchClient)
    client.Device.DeviceName = "Living Room"
    client.Device.DeviceId = "AABBCC112233"

    # Mock GetInformation()
    info = MagicMock(spec=Information)
    info.DeviceId = "AABBCC112233"
    info.DeviceType = "SoundTouch 30 Series III"
    client.GetInformation.return_value = info

    # Mock GetCapabilities()
    caps = MagicMock(spec=Capabilities)
    caps.IsProductCECHDMIControlCapable = False  # ST30 has no HDMI
    caps.IsBassCapable = True
    caps.IsAudioProductLevelControlCapable = False

    # Mock supported URLs
    caps.SupportedUrls = [
        MagicMock(Url="/info"),
        MagicMock(Url="/nowPlaying"),
        MagicMock(Url="/volume"),
        MagicMock(Url="/bass"),
        MagicMock(Url="/getZone"),
        MagicMock(Url="/bluetoothInfo"),
    ]
    client.GetCapabilities.return_value = caps

    # Mock GetSourceList()
    sources = MagicMock(spec=SourceList)
    sources.Sources = [
        MagicMock(Source="BLUETOOTH", Status="READY"),
        MagicMock(Source="AUX", Status="READY"),
        MagicMock(Source="INTERNET_RADIO", Status="READY"),
        MagicMock(Source="SPOTIFY", Status="UNAVAILABLE"),  # Not ready
    ]
    client.GetSourceList.return_value = sources

    return client


@pytest.fixture
def mock_client_st300():
    """Mock SoundTouchClient for SoundTouch 300 (soundbar with HDMI)."""
    client = MagicMock(spec=SoundTouchClient)
    client.Device.DeviceName = "TV"
    client.Device.DeviceId = "AABBCC112244"

    # Mock GetInformation()
    info = MagicMock(spec=Information)
    info.DeviceId = "AABBCC112244"
    info.DeviceType = "SoundTouch 300"
    client.GetInformation.return_value = info

    # Mock GetCapabilities()
    caps = MagicMock(spec=Capabilities)
    caps.IsProductCECHDMIControlCapable = True  # ST300 has HDMI
    caps.IsBassCapable = True
    caps.IsAudioProductLevelControlCapable = True
    caps.IsAudioProductToneControlsCapable = True

    # Mock supported URLs (including HDMI endpoints)
    caps.SupportedUrls = [
        MagicMock(Url="/info"),
        MagicMock(Url="/nowPlaying"),
        MagicMock(Url="/volume"),
        MagicMock(Url="/bass"),
        MagicMock(Url="/getZone"),
        MagicMock(Url="/bluetoothInfo"),
        MagicMock(Url="/productcechdmicontrol"),
        MagicMock(Url="/audioproductlevelcontrols"),
    ]
    client.GetCapabilities.return_value = caps

    # Mock GetSourceList()
    sources = MagicMock(spec=SourceList)
    sources.Sources = [
        MagicMock(Source="PRODUCT", SourceAccount="TV", Status="READY"),  # HDMI input
        MagicMock(Source="BLUETOOTH", Status="READY"),
        MagicMock(Source="INTERNET_RADIO", Status="READY"),
    ]
    client.GetSourceList.return_value = sources

    return client


@pytest.mark.asyncio
async def test_get_device_capabilities_st30(mock_client_st30):
    """Test capability detection for SoundTouch 30."""
    capabilities = await get_device_capabilities(mock_client_st30)

    assert capabilities.device_id == "AABBCC112233"
    assert capabilities.device_type == "SoundTouch 30 Series III"

    # ST30 does NOT have HDMI
    assert capabilities.has_hdmi_control is False
    assert capabilities.has_bass_control is True

    # Check endpoint support
    assert capabilities.supports_endpoint("info")
    assert capabilities.supports_endpoint(
        "/volume"
    )  # Should work with or without slash
    assert capabilities.supports_endpoint("productcechdmicontrol") is False

    # Check source support
    assert capabilities.supports_source("BLUETOOTH")
    assert capabilities.supports_source("aux")  # Case-insensitive
    assert capabilities.supports_source("SPOTIFY") is False  # Unavailable

    # Device type checks
    assert capabilities.is_soundbar() is False
    assert capabilities.is_wireless_speaker() is True


@pytest.mark.asyncio
async def test_get_device_capabilities_st300(mock_client_st300):
    """Test capability detection for SoundTouch 300 (soundbar)."""
    capabilities = await get_device_capabilities(mock_client_st300)

    assert capabilities.device_id == "AABBCC112244"
    assert capabilities.device_type == "SoundTouch 300"

    # ST300 HAS HDMI
    assert capabilities.has_hdmi_control is True
    assert capabilities.has_bass_control is True
    assert capabilities.has_audio_product_level_control is True

    # Check ST300-specific endpoints
    assert capabilities.supports_endpoint("productcechdmicontrol")
    assert capabilities.supports_endpoint("audioproductlevelcontrols")

    # Check HDMI source
    assert capabilities.supports_source("PRODUCT")

    # Device type checks
    assert capabilities.is_soundbar() is True
    assert capabilities.is_wireless_speaker() is False


@pytest.mark.asyncio
async def test_safe_api_call_success(mock_client_st30):
    """Test safe_api_call with successful response."""
    from bosesoundtouchapi.uri import SoundTouchNodes

    mock_response = MagicMock()
    mock_client_st30.Get.return_value = mock_response

    result = await safe_api_call(mock_client_st30, SoundTouchNodes.volume)

    assert result == mock_response
    mock_client_st30.Get.assert_called_once_with(SoundTouchNodes.volume)


@pytest.mark.asyncio
async def test_safe_api_call_404_not_found(mock_client_st30):
    """Test safe_api_call with 404 (endpoint not supported)."""
    from bosesoundtouchapi.uri import SoundTouchNodes

    # Create real SoundTouchError instance with ErrorCode
    error = SoundTouchError("Not found", errorCode=404)
    mock_client_st30.Get.side_effect = error

    result = await safe_api_call(
        mock_client_st30, SoundTouchNodes.productcechdmicontrol, "HDMI Control"
    )

    # Should return None instead of raising
    assert result is None


@pytest.mark.asyncio
async def test_safe_api_call_401_unauthorized(mock_client_st30):
    """Test safe_api_call with 401 (authentication required)."""
    from bosesoundtouchapi.uri import SoundTouchNodes

    # Create real SoundTouchError instance with ErrorCode
    error = SoundTouchError("Unauthorized", errorCode=401)
    mock_client_st30.Get.side_effect = error

    result = await safe_api_call(mock_client_st30, SoundTouchNodes.speaker)

    # Should return None instead of raising
    assert result is None


@pytest.mark.asyncio
async def test_safe_api_call_unexpected_error(mock_client_st30):
    """Test safe_api_call re-raises unexpected errors."""
    from bosesoundtouchapi.uri import SoundTouchNodes

    # Create real SoundTouchError instance with ErrorCode
    error = SoundTouchError("Server error", errorCode=500)
    mock_client_st30.Get.side_effect = error

    # Should re-raise unexpected errors
    with pytest.raises(SoundTouchError) as exc_info:
        await safe_api_call(mock_client_st30, SoundTouchNodes.volume)

    assert exc_info.value.ErrorCode == 500


def test_get_feature_flags_for_ui_st30():
    """Test UI feature flags for ST30 (wireless speaker)."""
    capabilities = DeviceCapabilities(
        device_id="AABBCC112233",
        device_type="SoundTouch 30 Series III",
        has_hdmi_control=False,
        has_bass_control=True,
        has_bluetooth=True,
        has_aux_input=True,
        has_zone_support=True,
        supported_sources=["BLUETOOTH", "AUX", "INTERNET_RADIO"],
        supported_endpoints={"info", "volume", "bass", "getZone"},
    )

    flags = get_feature_flags_for_ui(capabilities)

    assert flags["device_id"] == "AABBCC112233"
    assert flags["is_soundbar"] is False

    # Features
    assert flags["features"]["hdmi_control"] is False  # No HDMI on ST30
    assert flags["features"]["bass_control"] is True
    assert flags["features"]["bluetooth"] is True
    assert flags["features"]["aux_input"] is True
    assert flags["features"]["zone_support"] is True

    # Sources
    assert "BLUETOOTH" in flags["sources"]
    assert "AUX" in flags["sources"]


def test_get_feature_flags_for_ui_st300():
    """Test UI feature flags for ST300 (soundbar with HDMI)."""
    capabilities = DeviceCapabilities(
        device_id="AABBCC112244",
        device_type="SoundTouch 300",
        has_hdmi_control=True,
        has_bass_control=True,
        has_audio_product_level_control=True,
        has_bluetooth=True,
        has_aux_input=False,  # ST300 might not have AUX
        has_zone_support=True,
        supported_sources=["PRODUCT", "BLUETOOTH", "INTERNET_RADIO"],
        supported_endpoints={
            "info",
            "volume",
            "bass",
            "getZone",
            "productcechdmicontrol",
        },
    )

    flags = get_feature_flags_for_ui(capabilities)

    assert flags["device_id"] == "AABBCC112244"
    assert flags["is_soundbar"] is True

    # Features
    assert flags["features"]["hdmi_control"] is True  # ST300 has HDMI
    assert flags["features"]["bass_control"] is True
    assert flags["features"]["advanced_audio"] is True
    assert flags["features"]["bluetooth"] is True
    assert flags["features"]["aux_input"] is False

    # Sources
    assert "PRODUCT" in flags["sources"]  # HDMI input


@pytest.mark.parametrize(
    "device_type,expected_is_soundbar",
    [
        ("SoundTouch 30 Series III", False),
        ("SoundTouch 10", False),
        ("SoundTouch 300", True),
        ("SoundTouch 300 Soundbar", True),  # Even with extra text
    ],
)
def test_device_type_detection(device_type, expected_is_soundbar):
    """Test soundbar detection across different device types."""
    capabilities = DeviceCapabilities(
        device_id="TEST",
        device_type=device_type,
    )

    assert capabilities.is_soundbar() == expected_is_soundbar
    assert capabilities.is_wireless_speaker() == (not expected_is_soundbar)


def test_supports_endpoint_with_and_without_slash():
    """Test endpoint support check with/without leading slash."""
    capabilities = DeviceCapabilities(
        device_id="TEST",
        device_type="SoundTouch 30",
        supported_endpoints={"info", "volume", "bass"},
    )

    # Both should work
    assert capabilities.supports_endpoint("info")
    assert capabilities.supports_endpoint("/info")
    assert capabilities.supports_endpoint("/volume")
    assert capabilities.supports_endpoint("bass")

    # Not supported
    assert capabilities.supports_endpoint("productcechdmicontrol") is False
    assert capabilities.supports_endpoint("/productcechdmicontrol") is False
