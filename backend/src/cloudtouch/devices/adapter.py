"""
Adapter for bosesoundtouchapi library
Wraps SoundTouchDiscovery and SoundTouchClient with our internal interfaces
"""

import logging
import os
from typing import List

from bosesoundtouchapi import SoundTouchClient as BoseClient
from bosesoundtouchapi import SoundTouchDevice

from cloudtouch.core.exceptions import DeviceConnectionError, DiscoveryError
from cloudtouch.devices.client import (DeviceInfo, NowPlayingInfo,
                                       SoundTouchClient)
from cloudtouch.devices.discovery.ssdp import SSDPDiscovery
from cloudtouch.discovery import DeviceDiscovery, DiscoveredDevice

logger = logging.getLogger(__name__)


class BoseSoundTouchDiscoveryAdapter(DeviceDiscovery):
    """Adapter using SSDP discovery for Bose SoundTouch devices."""

    async def discover(self, timeout: int = 10) -> List[DiscoveredDevice]:
        """
        Discover SoundTouch devices using SSDP.

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
                port = 8090  # Bose SoundTouch default port

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

    def _extract_firmware_version(self, info) -> str:
        """Extract firmware version from Components list."""
        if not hasattr(info, "Components") or not info.Components:
            return ""

        first_component = info.Components[0]
        return (
            first_component.SoftwareVersion
            if hasattr(first_component, "SoftwareVersion")
            else ""
        )

    def _extract_ip_address(self, info) -> str:
        """Extract IP address from NetworkInfo or fallback to self.ip."""
        if not info.NetworkInfo or len(info.NetworkInfo) == 0:
            return self.ip

        network_info = info.NetworkInfo[0]
        return network_info.IpAddress if hasattr(network_info, "IpAddress") else self.ip

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

            firmware_version = self._extract_firmware_version(info)
            ip_address = self._extract_ip_address(info)

            device_info = DeviceInfo(
                device_id=info.DeviceId,
                name=info.DeviceName,
                type=info.DeviceType,
                mac_address=getattr(info, "MacAddress", ""),
                ip_address=ip_address,
                firmware_version=firmware_version,
                module_type=getattr(info, "ModuleType", None),
                variant=getattr(info, "Variant", None),
                variant_mode=getattr(info, "VariantMode", None),
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
            state = now_playing.PlayStatus or "STOP_STATE"
            source = now_playing.Source or "UNKNOWN"

            return NowPlayingInfo(
                source=source,
                state=state,
                station_name=getattr(now_playing, "StationName", None),
                artist=getattr(now_playing, "Artist", None),
                track=getattr(now_playing, "Track", None),
                album=getattr(now_playing, "Album", None),
                artwork_url=getattr(now_playing, "ArtUrl", None),
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


# ==================== FACTORY FUNCTIONS ====================


def get_discovery_adapter(timeout: int = 10) -> DeviceDiscovery:
    """
    Factory function to get discovery adapter based on CT_MOCK_MODE.

    Args:
        timeout: Discovery timeout in seconds

    Returns:
        DeviceDiscovery implementation (Mock or Real)
    """
    mock_mode = os.getenv("CT_MOCK_MODE", "false").lower() == "true"

    if mock_mode:
        logger.info("[MOCK MODE] Using MockDiscoveryAdapter")
        from cloudtouch.devices.discovery.mock import MockDiscoveryAdapter

        return MockDiscoveryAdapter(timeout=timeout)
    else:
        logger.info("[REAL MODE] Using BoseSoundTouchDiscoveryAdapter")
        adapter = BoseSoundTouchDiscoveryAdapter()
        return adapter


def get_soundtouch_client(base_url: str, timeout: float = 5.0) -> SoundTouchClient:
    """
    Factory function to get SoundTouch client based on CT_MOCK_MODE.

    Args:
        base_url: Base URL of device (e.g., http://192.168.1.100:8090)
        timeout: Request timeout in seconds

    Returns:
        SoundTouchClient implementation (Mock or Real)
    """
    mock_mode = os.getenv("CT_MOCK_MODE", "false").lower() == "true"

    if mock_mode:
        # Extract device_id from base_url or use IP as fallback
        from urllib.parse import urlparse

        parsed = urlparse(base_url)
        ip = parsed.hostname or base_url.split("://")[1].split(":")[0]

        # For mock mode, we use MAC as device_id
        # In production, this would come from discovery
        # For testing, try to extract from known mocks
        from cloudtouch.devices.mock_client import MockSoundTouchClient

        # Try to find matching mock device by IP
        device_id = None
        for mac, device_data in MockSoundTouchClient.MOCK_DEVICES.items():
            if device_data["info"].ip_address == ip:
                device_id = mac
                break

        if not device_id:
            # Fallback: Use first mock device
            device_id = list(MockSoundTouchClient.MOCK_DEVICES.keys())[0]
            logger.warning(
                f"[MOCK MODE] No mock device found for IP {ip}, using {device_id}"
            )

        logger.info(f"[MOCK MODE] Using MockSoundTouchClient for {device_id}")
        return MockSoundTouchClient(device_id=device_id, ip_address=ip)
    else:
        logger.info(f"[REAL MODE] Using BoseSoundTouchClientAdapter for {base_url}")
        return BoseSoundTouchClientAdapter(base_url=base_url, timeout=timeout)
