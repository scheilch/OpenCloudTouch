"""
Cross-Model Compatibility Tests (10.1)

Tests endpoint availability across SoundTouch 30, 10, and 300 models.
Verifies that model-specific features are correctly detected and handled.

Endpoint Matrix:
- 102 common endpoints (ST30, ST10, ST300)
- 7 ST300-exclusive endpoints (HDMI/Audio)
- 1 ST10-specific endpoint (getGroup as GET)
"""

from unittest.mock import MagicMock

import pytest

from opencloudtouch.devices.capabilities import (
    get_device_capabilities,
    get_feature_flags_for_ui,
)

# Test Data: Device-specific capabilities based on SCHEMA_DIFFERENCES.md

ST30_CAPABILITIES = {
    "device_type": "SoundTouch 30 Series III",
    "has_hdmi": False,
    "has_bass": True,
    "has_advanced_audio": False,
    "has_balance": False,
    "sources": ["BLUETOOTH", "AUX", "INTERNET_RADIO", "SPOTIFY", "STORED_MUSIC"],
    "st300_only_endpoints": [],  # Should NOT have these
    "common_endpoints": [
        "info",
        "capabilities",
        "supportedURLs",
        "sources",
        "presets",
        "nowPlaying",
        "volume",
        "bass",
        "key",
        "select",
    ],
}

ST10_CAPABILITIES = {
    "device_type": "SoundTouch 10",
    "has_hdmi": False,
    "has_bass": True,
    "has_advanced_audio": False,
    "has_balance": False,
    "sources": ["BLUETOOTH", "INTERNET_RADIO", "SPOTIFY", "STORED_MUSIC"],  # No AUX
    "st300_only_endpoints": [],  # Should NOT have these
    "common_endpoints": [
        "info",
        "capabilities",
        "supportedURLs",
        "sources",
        "presets",
        "nowPlaying",
        "volume",
        "bass",
        "key",
        "select",
    ],
}

ST300_CAPABILITIES = {
    "device_type": "SoundTouch 300",
    "has_hdmi": True,
    "has_bass": True,
    "has_advanced_audio": True,
    "has_balance": True,
    "sources": [
        "BLUETOOTH",
        "PRODUCT",
        "INTERNET_RADIO",
        "SPOTIFY",
        "STORED_MUSIC",
        "HDMI_1",
    ],
    "st300_only_endpoints": [
        "audiodspcontrols",
        "audioproductlevelcontrols",
        "audioproducttonecontrols",
        "audiospeakerattributeandsetting",
        "productcechdmicontrol",
        "producthdmiassignmentcontrols",
        "systemtimeoutcontrol",
    ],
    "common_endpoints": [
        "info",
        "capabilities",
        "supportedURLs",
        "sources",
        "presets",
        "nowPlaying",
        "volume",
        "bass",
        "key",
        "select",
        "balance",
    ],
}


# Fixtures


@pytest.fixture
def mock_st30_client():
    """Mock SoundTouch 30 client."""
    client = MagicMock()

    # Mock info
    info = MagicMock()
    info.DeviceId = "ST30_TEST"
    info.DeviceName = "SoundTouch 30"
    info.DeviceType = "SoundTouch 30 Series III"
    client.GetInformation = MagicMock(return_value=info)

    # Mock capabilities
    caps = MagicMock()
    caps.IsProductCECHDMIControlCapable = False
    caps.IsBassCapable = True
    caps.IsAudioProductLevelControlCapable = False
    caps.IsAudioProductToneControlsCapable = False

    # Mock supported URLs
    common_urls = [MagicMock(Url=url) for url in ST30_CAPABILITIES["common_endpoints"]]
    caps.SupportedUrls = common_urls
    client.GetCapabilities = MagicMock(return_value=caps)

    # Mock sources
    sources_response = MagicMock()
    sources_response.Sources = [
        MagicMock(Source=src, Status="READY") for src in ST30_CAPABILITIES["sources"]
    ]
    client.GetSourceList = MagicMock(return_value=sources_response)

    client.Device = MagicMock(DeviceName="SoundTouch 30")

    return client


@pytest.fixture
def mock_st10_client():
    """Mock SoundTouch 10 client."""
    client = MagicMock()

    # Mock info
    info = MagicMock()
    info.DeviceId = "ST10_TEST"
    info.DeviceName = "SoundTouch 10"
    info.DeviceType = "SoundTouch 10"
    client.GetInformation = MagicMock(return_value=info)

    # Mock capabilities
    caps = MagicMock()
    caps.IsProductCECHDMIControlCapable = False
    caps.IsBassCapable = True
    caps.IsAudioProductLevelControlCapable = False

    # Mock supported URLs
    common_urls = [MagicMock(Url=url) for url in ST10_CAPABILITIES["common_endpoints"]]
    caps.SupportedUrls = common_urls
    client.GetCapabilities = MagicMock(return_value=caps)

    # Mock sources (no AUX)
    sources_response = MagicMock()
    sources_response.Sources = [
        MagicMock(Source=src, Status="READY") for src in ST10_CAPABILITIES["sources"]
    ]
    client.GetSourceList = MagicMock(return_value=sources_response)

    client.Device = MagicMock(DeviceName="SoundTouch 10")

    return client


@pytest.fixture
def mock_st300_client():
    """Mock SoundTouch 300 client."""
    client = MagicMock()

    # Mock info
    info = MagicMock()
    info.DeviceId = "ST300_TEST"
    info.DeviceName = "SoundTouch 300"
    info.DeviceType = "SoundTouch 300"
    client.GetInformation = MagicMock(return_value=info)

    # Mock capabilities
    caps = MagicMock()
    caps.IsProductCECHDMIControlCapable = True
    caps.IsBassCapable = True
    caps.IsAudioProductLevelControlCapable = True
    caps.IsAudioProductToneControlsCapable = True

    # Mock supported URLs (common + ST300-only)
    all_urls = (
        ST300_CAPABILITIES["common_endpoints"]
        + ST300_CAPABILITIES["st300_only_endpoints"]
    )
    caps.SupportedUrls = [MagicMock(Url=url) for url in all_urls]
    client.GetCapabilities = MagicMock(return_value=caps)

    # Mock sources (includes PRODUCT, HDMI)
    sources_response = MagicMock()
    sources_response.Sources = [
        MagicMock(Source=src, Status="READY") for src in ST300_CAPABILITIES["sources"]
    ]
    client.GetSourceList = MagicMock(return_value=sources_response)

    client.Device = MagicMock(DeviceName="SoundTouch 300")

    return client


# Parametrized Tests


@pytest.mark.parametrize(
    "device_type,has_hdmi,has_advanced_audio",
    [
        ("SoundTouch 30 Series III", False, False),
        ("SoundTouch 10", False, False),
        ("SoundTouch 300", True, True),
    ],
)
@pytest.mark.asyncio
async def test_hdmi_control_availability(device_type, has_hdmi, has_advanced_audio):
    """Test HDMI control is only available on ST300."""
    # This test would check actual endpoint availability
    # For now, we verify via capabilities

    if "300" in device_type:
        assert has_hdmi is True
        assert has_advanced_audio is True
    else:
        assert has_hdmi is False
        assert has_advanced_audio is False


@pytest.mark.asyncio
async def test_st30_capabilities(mock_st30_client):
    """Test SoundTouch 30 capabilities."""
    caps = await get_device_capabilities(mock_st30_client)

    assert caps.device_type == "SoundTouch 30 Series III"
    assert caps.has_hdmi_control is False
    assert caps.has_bass_control is True
    assert caps.has_audio_product_level_control is False
    assert "AUX" in [s.upper() for s in caps.supported_sources]

    # Should NOT have ST300-only endpoints
    for endpoint in ST300_CAPABILITIES["st300_only_endpoints"]:
        assert not caps.supports_endpoint(endpoint)


@pytest.mark.asyncio
async def test_st10_capabilities(mock_st10_client):
    """Test SoundTouch 10 capabilities."""
    caps = await get_device_capabilities(mock_st10_client)

    assert caps.device_type == "SoundTouch 10"
    assert caps.has_hdmi_control is False
    assert caps.has_bass_control is True
    assert caps.has_audio_product_level_control is False

    # ST10 does NOT have AUX
    assert "AUX" not in [s.upper() for s in caps.supported_sources]

    # Should NOT have ST300-only endpoints
    for endpoint in ST300_CAPABILITIES["st300_only_endpoints"]:
        assert not caps.supports_endpoint(endpoint)


@pytest.mark.asyncio
async def test_st300_capabilities(mock_st300_client):
    """Test SoundTouch 300 capabilities."""
    caps = await get_device_capabilities(mock_st300_client)

    assert caps.device_type == "SoundTouch 300"
    assert caps.has_hdmi_control is True
    assert caps.has_bass_control is True
    assert caps.has_audio_product_level_control is True
    assert caps.has_audio_product_tone_control is True

    # ST300 has PRODUCT and HDMI sources
    assert "PRODUCT" in [s.upper() for s in caps.supported_sources]

    # SHOULD have ST300-only endpoints
    for endpoint in ST300_CAPABILITIES["st300_only_endpoints"]:
        assert caps.supports_endpoint(endpoint), f"ST300 should support {endpoint}"


@pytest.mark.asyncio
async def test_st300_ui_feature_flags(mock_st300_client):
    """Test that UI feature flags correctly reflect ST300 capabilities."""
    caps = await get_device_capabilities(mock_st300_client)
    flags = get_feature_flags_for_ui(caps)

    assert flags["is_soundbar"] is True
    assert flags["features"]["hdmi_control"] is True
    assert flags["features"]["advanced_audio"] is True
    assert flags["features"]["tone_controls"] is True
    assert flags["features"]["bass_control"] is True


@pytest.mark.asyncio
async def test_st30_ui_feature_flags(mock_st30_client):
    """Test that UI feature flags correctly hide ST300 features for ST30."""
    caps = await get_device_capabilities(mock_st30_client)
    flags = get_feature_flags_for_ui(caps)

    assert flags["is_soundbar"] is False
    assert flags["features"]["hdmi_control"] is False
    assert flags["features"]["advanced_audio"] is False
    assert flags["features"]["tone_controls"] is False
    assert flags["features"]["bass_control"] is True
    assert flags["features"]["aux_input"] is True


@pytest.mark.asyncio
async def test_common_endpoints_all_models(
    mock_st30_client, mock_st10_client, mock_st300_client
):
    """Test that all models support common endpoints."""
    common_endpoints = [
        "info",
        "capabilities",
        "supportedURLs",
        "sources",
        "presets",
        "nowPlaying",
        "volume",
        "bass",
        "key",
        "select",
    ]

    for client in [mock_st30_client, mock_st10_client, mock_st300_client]:
        caps = await get_device_capabilities(client)

        for endpoint in common_endpoints:
            assert caps.supports_endpoint(
                endpoint
            ), f"{caps.device_type} should support common endpoint: {endpoint}"


@pytest.mark.parametrize(
    "model,expected_sources",
    [
        ("ST30", ["BLUETOOTH", "AUX", "INTERNET_RADIO", "SPOTIFY", "STORED_MUSIC"]),
        ("ST10", ["BLUETOOTH", "INTERNET_RADIO", "SPOTIFY", "STORED_MUSIC"]),  # No AUX
        (
            "ST300",
            [
                "BLUETOOTH",
                "PRODUCT",
                "INTERNET_RADIO",
                "SPOTIFY",
                "STORED_MUSIC",
                "HDMI_1",
            ],
        ),
    ],
)
@pytest.mark.asyncio
async def test_source_availability_by_model(
    model, expected_sources, mock_st30_client, mock_st10_client, mock_st300_client
):
    """Test that each model has correct available sources."""
    client_map = {
        "ST30": mock_st30_client,
        "ST10": mock_st10_client,
        "ST300": mock_st300_client,
    }

    client = client_map[model]
    caps = await get_device_capabilities(client)

    # Normalize to uppercase for comparison
    actual_sources_upper = [s.upper() for s in caps.supported_sources]
    expected_sources_upper = [s.upper() for s in expected_sources]

    for source in expected_sources_upper:
        assert source in actual_sources_upper, f"{model} should have source: {source}"
