"""
Device API Routes
Endpoints for device discovery and management
"""

import logging
import asyncio
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, Depends

from cloudtouch.discovery import DiscoveredDevice
from cloudtouch.devices.adapter import (
    BoseSoundTouchDiscoveryAdapter,
    BoseSoundTouchClientAdapter,
)
from cloudtouch.devices.discovery.manual import ManualDiscovery
from cloudtouch.devices.repository import Device, DeviceRepository
from cloudtouch.core.config import get_config, AppConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/devices", tags=["Devices"])

# Discovery lock to prevent concurrent discovery requests
_discovery_lock = asyncio.Lock()
_discovery_in_progress = False


# Dependency injection
async def get_device_repo() -> DeviceRepository:
    """Get device repository instance."""
    from cloudtouch.main import device_repo

    return device_repo


# Helper functions for discover_devices (keep functions < 20 lines)
async def _discover_via_ssdp(cfg: AppConfig) -> List[DiscoveredDevice]:
    """Discover devices via SSDP (UPnP)."""
    if not cfg.discovery_enabled:
        return []

    logger.info("Starting discovery via SSDP...")
    discovery = BoseSoundTouchDiscoveryAdapter()
    try:
        devices = await discovery.discover(timeout=cfg.discovery_timeout)
        logger.info(f"SSDP discovery found {len(devices)} device(s)")
        return devices
    except Exception as e:
        logger.error(f"SSDP discovery failed: {e}")
        return []


async def _discover_via_manual_ips(cfg: AppConfig) -> List[DiscoveredDevice]:
    """
    Discover devices via manually configured IP addresses.
    
    Merges IPs from:
    - Database (manual_device_ips table)
    - Environment variable (CT_MANUAL_DEVICE_IPS)
    """
    # Get IPs from database
    from cloudtouch.main import settings_repo
    
    db_ips = []
    if settings_repo:
        try:
            db_ips = await settings_repo.get_manual_ips()
        except Exception as e:
            logger.error(f"Failed to get manual IPs from database: {e}")
    
    # Get IPs from environment variable
    env_ips = cfg.manual_device_ips_list or []
    
    # Merge and deduplicate
    all_ips = list(set(db_ips + env_ips))
    
    if not all_ips:
        return []

    logger.info(f"Using manual device IPs: {all_ips} (DB: {len(db_ips)}, ENV: {len(env_ips)})")
    manual = ManualDiscovery(all_ips)
    try:
        devices = await manual.discover()
        logger.info(f"Manual discovery found {len(devices)} device(s)")
        return devices
    except Exception as e:
        logger.error(f"Manual discovery failed: {e}")
        return []


def _format_discovery_response(devices: List[DiscoveredDevice]) -> Dict[str, Any]:
    """Format discovery results as API response."""
    return {
        "count": len(devices),
        "devices": [
            {
                "ip": d.ip,
                "port": d.port,
                "name": d.name,
                "model": d.model,
            }
            for d in devices
        ],
    }


@router.get("/discover")
async def discover_devices() -> Dict[str, Any]:
    """
    Trigger device discovery.

    Returns:
        List of discovered devices (not yet saved to DB)
    """
    cfg = get_config()

    # Discover via SSDP and manual IPs
    ssdp_devices = await _discover_via_ssdp(cfg)
    manual_devices = await _discover_via_manual_ips(cfg)

    all_devices = ssdp_devices + manual_devices
    logger.info(f"Discovery complete: {len(all_devices)} device(s) found")

    return _format_discovery_response(all_devices)


@router.post("/sync")
async def sync_devices(repo: DeviceRepository = Depends(get_device_repo)):
    """
    Discover devices and sync to database.
    Queries each device for detailed info (/info endpoint).

    Returns:
        Sync summary with success/failure counts
    """
    global _discovery_in_progress

    # Check if discovery already in progress
    if _discovery_in_progress:
        logger.warning("Discovery already in progress, rejecting concurrent request")
        raise HTTPException(status_code=409, detail="Discovery already in progress")

    async with _discovery_lock:
        _discovery_in_progress = True
        try:
            cfg = get_config()

            # Discover devices
            devices: List[DiscoveredDevice] = []

            if cfg.discovery_enabled:
                discovery = BoseSoundTouchDiscoveryAdapter()
                try:
                    discovered_devices = await discovery.discover(
                        timeout=cfg.discovery_timeout
                    )
                    devices.extend(discovered_devices)
                except Exception as e:
                    logger.error(f"Discovery failed: {e}")

            manual_ips = cfg.manual_device_ips_list
            if manual_ips:
                manual = ManualDiscovery(manual_ips)
                manual_devices = await manual.discover()
                devices.extend(manual_devices)

            # Query each device for detailed info and save to DB
            synced = 0
            failed = 0

            for discovered in devices:
                try:
                    client = BoseSoundTouchClientAdapter(discovered.base_url)
                    info = await client.get_info()

                    device = Device(
                        device_id=info.device_id,
                        ip=discovered.ip,
                        name=info.name,
                        model=info.type,
                        mac_address=info.mac_address,
                        firmware_version=info.firmware_version,
                    )

                    await repo.upsert(device)
                    synced += 1
                    logger.info(f"Synced device: {info.name} ({info.device_id})")

                except Exception as e:
                    failed += 1
                    logger.error(f"Failed to sync device {discovered.ip}: {e}")

            return {
                "discovered": len(devices),
                "synced": synced,
                "failed": failed,
            }
        finally:
            _discovery_in_progress = False


@router.get("")
async def get_devices(repo: DeviceRepository = Depends(get_device_repo)):
    """
    Get all devices from database.

    Returns:
        List of devices with details
    """
    devices = await repo.get_all()

    return {
        "count": len(devices),
        "devices": [d.to_dict() for d in devices],
    }


@router.get("/{device_id}")
async def get_device(device_id: str, repo: DeviceRepository = Depends(get_device_repo)):
    """
    Get single device by device_id.

    Args:
        device_id: SoundTouch device ID

    Returns:
        Device details
    """
    device = await repo.get_by_device_id(device_id)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return device.to_dict()


@router.get("/{device_id}/capabilities")
async def get_device_capabilities_endpoint(
    device_id: str, repo: DeviceRepository = Depends(get_device_repo)
):
    """
    Get device capabilities for UI feature detection.

    Returns which features this specific device supports:
    - HDMI control (ST300 only)
    - Bass/balance controls
    - Available input sources
    - Zone/group support
    - All supported endpoints

    Args:
        device_id: SoundTouch device ID

    Returns:
        Feature flags and capabilities for UI rendering

    Example Response:
        {
            "device_id": "AABBCC112233",
            "device_type": "SoundTouch 30 Series III",
            "is_soundbar": false,
            "features": {
                "hdmi_control": false,
                "bass_control": true,
                "bluetooth": true,
                ...
            },
            "sources": ["BLUETOOTH", "AUX", "INTERNET_RADIO"],
            "advanced": {...}
        }
    """
    from cloudtouch.devices.capabilities import (
        get_device_capabilities,
        get_feature_flags_for_ui,
    )
    from bosesoundtouchapi import SoundTouchDevice, SoundTouchClient

    # Get device from DB
    device = await repo.get_by_device_id(device_id)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    try:
        # Create SoundTouch client
        st_device = SoundTouchDevice(device.ip)
        client = SoundTouchClient(st_device)

        # Get capabilities
        capabilities = await get_device_capabilities(client)

        # Convert to UI-friendly format
        feature_flags = get_feature_flags_for_ui(capabilities)

        return feature_flags

    except Exception as e:
        logger.error(f"Failed to get capabilities for device {device_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to query device capabilities: {str(e)}"
        )
