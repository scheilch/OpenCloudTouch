"""
Adapter for bosesoundtouchapi library
Wraps SoundTouchDiscovery and SoundTouchClient with our internal interfaces
"""

import logging
from typing import List

from bosesoundtouchapi import SoundTouchClient as BoseClient, SoundTouchDevice

from backend.discovery import DeviceDiscovery, DiscoveredDevice
from backend.soundtouch import SoundTouchClient, DeviceInfo, NowPlayingInfo
from backend.core.exceptions import DiscoveryError, DeviceConnectionError
from backend.adapters.ssdp_discovery import SSDPDiscovery

logger = logging.getLogger(__name__)


class BoseSoundTouchDiscoveryAdapter(DeviceDiscovery):
    """Adapter using SSDP discovery for compatible streaming devices."""

    async def discover(self, timeout: int = 10) -> List[DiscoveredDevice]:
        """
        Discover compatible streaming devices using SSDP.

        Args:
            timeout: Discovery timeout in seconds

        Returns:
            List of discovered devices (IP + Name only, details loaded lazily)

        Raises:
            DiscoveryError: If discovery fails
        """
        logger.info(f"Starting discovery via SSDP (timeout: {timeout}s)")

        try:
            # Use SSDP discovery instead of mDNS (avoids port 5353 conflicts)
            ssdp = SSDPDiscovery(timeout=timeout)
            devices_dict = await ssdp.discover()

            logger.info(f"Discovery completed: {len(devices_dict)} device(s) found")

            discovered: List[DiscoveredDevice] = []

            for mac, device_info in devices_dict.items():
                ip = device_info.get("ip", "")
                name = device_info.get("name", "Unknown Device")
                port = 8090  # Default HTTP API port

                # Device details (model, mac, firmware) are fetched lazily in /api/devices/sync
                discovered.append(DiscoveredDevice(ip=ip, port=port, name=name))

            logger.info(
                f"Discovered {len(discovered)} device(s): {[d.name for d in discovered]}"
            )
            return discovered

        except Exception as e:
            logger.error(f"Discovery failed: {e}", exc_info=True)
            raise DiscoveryError(f"Failed to discover devices: {e}") from e


class BoseSoundTouchClientAdapter(SoundTouchClient):
    """Adapter wrapping bosesoundtouchapi SoundTouchClient."""

    def __init__(self, base_url: str, timeout: float = 5.0):
        """
        Initialize client adapter.

        Args:
            base_url: Base URL of device (e.g., http://192.168.1.100:8090)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Extract IP and port for BoseClient
        # BoseClient expects SoundTouchDevice object
        from urllib.parse import urlparse

        parsed = urlparse(base_url)
        self.ip = parsed.hostname or base_url.split("://")[1].split(":")[0]
        port = parsed.port or 8090

        # Create SoundTouchDevice with connectTimeout parameter
        # This initializes the device and loads info/capabilities
        device = SoundTouchDevice(host=self.ip, connectTimeout=int(timeout), port=port)

        self._client = BoseClient(device)

    async def get_info(self) -> DeviceInfo:
        """
        Get device info from /info endpoint.

        Returns:
            DeviceInfo parsed from response
        """
        try:
            # BoseClient.GetInformation() returns InfoElement
            # Properties: DeviceName, DeviceId, DeviceType, ModuleType, etc.
            info = self._client.GetInformation()

            # Extract network info for IP/MAC
            # NetworkInfo is a list - take first SCM entry
            network_info = (
                info.NetworkInfo[0]
                if info.NetworkInfo and len(info.NetworkInfo) > 0
                else None
            )

            # Extract firmware version from Components
            firmware_version = ""
            if hasattr(info, "Components") and info.Components:
                # Components is a list - take first component's SoftwareVersion
                firmware_version = (
                    info.Components[0].SoftwareVersion
                    if hasattr(info.Components[0], "SoftwareVersion")
                    else ""
                )

            device_info = DeviceInfo(
                device_id=info.DeviceId,
                name=info.DeviceName,
                type=info.DeviceType,
                mac_address=info.MacAddress if hasattr(info, "MacAddress") else "",
                ip_address=(
                    network_info.IpAddress
                    if network_info and hasattr(network_info, "IpAddress")
                    else self.ip
                ),
                firmware_version=firmware_version,
                module_type=info.ModuleType if hasattr(info, "ModuleType") else None,
                variant=info.Variant if hasattr(info, "Variant") else None,
                variant_mode=info.VariantMode if hasattr(info, "VariantMode") else None,
            )

            # Structured logging with firmware details
            logger.info(
                f"Device {device_info.name} initialized",
                extra={
                    "device_id": device_info.device_id,
                    "device_type": device_info.type,
                    "firmware": firmware_version,
                    "module_type": device_info.module_type,
                    "variant": device_info.variant,
                },
            )

            return device_info

        except Exception as e:
            logger.error(f"Failed to get info from {self.base_url}: {e}", exc_info=True)
            raise DeviceConnectionError(self.ip, str(e)) from e

    async def get_now_playing(self) -> NowPlayingInfo:
        """
        Get now playing info from /now_playing endpoint.

        Returns:
            NowPlayingInfo parsed from response
        """
        try:
            # BoseClient.GetNowPlayingStatus() returns NowPlayingStatus
            # Properties: Source, PlayStatus, StationName, Artist, Track, Album, ArtUrl
            now_playing = self._client.GetNowPlayingStatus()

            # Map PlayStatus to our state format
            # BoseClient uses: PLAY_STATE, PAUSE_STATE, STOP_STATE, BUFFERING_STATE
            state = now_playing.PlayStatus if now_playing.PlayStatus else "STOP_STATE"

            # Extract content info (ContentItem has source info)
            (
                now_playing.ContentItem if hasattr(now_playing, "ContentItem") else None
            )

            return NowPlayingInfo(
                source=now_playing.Source if now_playing.Source else "UNKNOWN",
                state=state,
                station_name=(
                    now_playing.StationName
                    if hasattr(now_playing, "StationName")
                    else None
                ),
                artist=now_playing.Artist if hasattr(now_playing, "Artist") else None,
                track=now_playing.Track if hasattr(now_playing, "Track") else None,
                album=now_playing.Album if hasattr(now_playing, "Album") else None,
                artwork_url=(
                    now_playing.ArtUrl if hasattr(now_playing, "ArtUrl") else None
                ),
            )

        except Exception as e:
            logger.error(
                f"Failed to get now_playing from {self.base_url}: {e}", exc_info=True
            )
            raise DeviceConnectionError(self.ip, str(e)) from e

    async def close(self) -> None:
        """Close client connections (no-op for bosesoundtouchapi)."""
        # BoseClient doesn't require explicit cleanup
        pass
