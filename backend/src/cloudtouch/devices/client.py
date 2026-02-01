"""
SoundTouch HTTP Client Interface
Abstrakte Basis für SoundTouch Device Communication
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class DeviceInfo:
    """SoundTouch device information from /info endpoint."""

    device_id: str
    name: str
    type: str  # SoundTouch 10, 20, 30, 300, etc.
    mac_address: str
    ip_address: str
    firmware_version: str
    module_type: Optional[str] = None
    variant: Optional[str] = None
    variant_mode: Optional[str] = None


@dataclass
class NowPlayingInfo:
    """Information about currently playing content."""

    source: str  # e.g., "INTERNET_RADIO", "BLUETOOTH", "AUX"
    state: str  # "PLAY_STATE", "PAUSE_STATE", "STOP_STATE"
    station_name: Optional[str] = None
    artist: Optional[str] = None
    track: Optional[str] = None
    album: Optional[str] = None
    artwork_url: Optional[str] = None


class SoundTouchClient(ABC):
    """Abstract client for SoundTouch device HTTP API."""

    @abstractmethod
    async def get_info(self) -> DeviceInfo:
        """
        Get device information from /info endpoint.

        Returns:
            DeviceInfo object with device details

        Raises:
            ConnectionError: If device is unreachable
            ValueError: If response cannot be parsed
        """
        pass

    @abstractmethod
    async def get_now_playing(self) -> NowPlayingInfo:
        """
        Get current playback status from /now_playing endpoint.

        Returns:
            NowPlayingInfo object with playback details

        Raises:
            ConnectionError: If device is unreachable
            ValueError: If response cannot be parsed
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close client connections."""
        pass
