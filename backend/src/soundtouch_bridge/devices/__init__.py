"""Devices Domain - All device-related functionality"""
from soundtouch_bridge.devices.adapter import BoseSoundTouchDiscoveryAdapter, BoseSoundTouchClientAdapter
from soundtouch_bridge.devices.repository import Device, DeviceRepository
from soundtouch_bridge.devices.client import SoundTouchClient, DeviceInfo, NowPlayingInfo
from soundtouch_bridge.devices.capabilities import get_device_capabilities, get_feature_flags_for_ui

__all__ = [
    "BoseSoundTouchDiscoveryAdapter",
    "BoseSoundTouchClientAdapter",
    "Device",
    "DeviceRepository",
    "SoundTouchClient",
    "DeviceInfo",
    "NowPlayingInfo",
    "get_device_capabilities",
    "get_feature_flags_for_ui",
]
