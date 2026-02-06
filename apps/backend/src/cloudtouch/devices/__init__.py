"""Devices Domain - All device-related functionality"""

from cloudtouch.devices.adapter import (
    BoseSoundTouchClientAdapter,
    BoseSoundTouchDiscoveryAdapter,
)
from cloudtouch.devices.capabilities import (
    get_device_capabilities,
    get_feature_flags_for_ui,
)
from cloudtouch.devices.client import DeviceInfo, NowPlayingInfo, SoundTouchClient
from cloudtouch.devices.repository import Device, DeviceRepository

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
