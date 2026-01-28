"""
Device API Routes
Endpoints for device discovery and management
"""
import logging
from typing import List

from fastapi import APIRouter, HTTPException, Depends

from backend.discovery import DiscoveredDevice
from backend.adapters.bosesoundtouch_adapter import BoseSoundTouchDiscoveryAdapter, BoseSoundTouchClientAdapter
from backend.discovery.manual import ManualDiscovery
from backend.db import Device, DeviceRepository
from backend.config import get_config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/devices", tags=["Devices"])


# Dependency injection
async def get_device_repo() -> DeviceRepository:
    """Get device repository instance."""
    from backend.main import device_repo
    return device_repo


@router.get("/discover")
async def discover_devices():
    """
    Trigger device discovery.
    
    Returns:
        List of discovered devices (not yet saved to DB)
    """
    cfg = get_config()
    
    devices: List[DiscoveredDevice] = []
    
    # Try SSDP discovery first
    if cfg.discovery_enabled:
        logger.info("Starting discovery via bosesoundtouchapi...")
        discovery = BoseSoundTouchDiscoveryAdapter()
        try:
            discovered_devices = await discovery.discover(timeout=cfg.discovery_timeout)
            devices.extend(discovered_devices)
        except Exception as e:
            logger.error(f"Discovery failed: {e}")
    
    # Fallback to manual IPs
    manual_ips = cfg.get_manual_ips()
    if manual_ips:
        logger.info(f"Using manual device IPs: {manual_ips}")
        manual = ManualDiscovery(manual_ips)
        manual_devices = await manual.discover()
        devices.extend(manual_devices)
    
    logger.info(f"Discovery complete: {len(devices)} device(s) found")
    
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


@router.post("/sync")
async def sync_devices(repo: DeviceRepository = Depends(get_device_repo)):
    """
    Discover devices and sync to database.
    Queries each device for detailed info (/info endpoint).
    
    Returns:
        Sync summary with success/failure counts
    """
    cfg = get_config()
    
    # Discover devices
    devices: List[DiscoveredDevice] = []
    
    if cfg.discovery_enabled:
        discovery = BoseSoundTouchDiscoveryAdapter()
        try:
            discovered_devices = await discovery.discover(timeout=cfg.discovery_timeout)
            devices.extend(discovered_devices)
        except Exception as e:
            logger.error(f"Discovery failed: {e}")
    
    manual_ips = cfg.get_manual_ips()
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
