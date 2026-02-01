"""Devices Domain - All device-related functionality"""

from cloudtouch.devices.adapter import (
    BoseSoundTouchDiscoveryAdapter,
    BoseSoundTouchClientAdapter,
)
from cloudtouch.devices.repository import Device, DeviceRepository
from cloudtouch.devices.client import SoundTouchClient, DeviceInfo, NowPlayingInfo
from cloudtouch.devices.capabilities import (
    get_device_capabilities,
    get_feature_flags_for_ui,
)

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
