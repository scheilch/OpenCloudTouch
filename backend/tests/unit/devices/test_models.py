"""Tests for device models module."""
import pytest


def test_device_models_imports():
    """Test that all device models can be imported from models package."""
    from soundtouch_bridge.devices.models import Device, DeviceInfo, NowPlayingInfo
    
    # Verify classes are importable
    assert Device is not None
    assert DeviceInfo is not None
    assert NowPlayingInfo is not None


def test_device_models_all_exports():
    """Test that __all__ exports are complete."""
    from soundtouch_bridge.devices import models
    
    assert hasattr(models, "__all__")
    assert "Device" in models.__all__
    assert "DeviceInfo" in models.__all__
    assert "NowPlayingInfo" in models.__all__
    assert len(models.__all__) == 3
