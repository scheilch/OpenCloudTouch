"""API routes for Settings management."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from cloudtouch.settings.repository import SettingsRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])


# Dependency to get settings repository
async def get_settings_repo() -> SettingsRepository:
    """Get settings repository instance."""
    from cloudtouch.main import settings_repo

    return settings_repo


class AddIPRequest(BaseModel):
    """Request model for adding manual IP."""

    ip: str = Field(..., description="IP address to add", examples=["192.168.1.10"])


class SetManualIPsRequest(BaseModel):
    """Request model for setting all manual IPs at once."""

    ips: list[str] = Field(..., description="List of IP addresses to set")


class ManualIPsResponse(BaseModel):
    """Response model for manual IPs list."""

    ips: list[str] = Field(..., description="List of manual IP addresses")


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    ip: str


@router.get("/manual-ips", response_model=ManualIPsResponse)
async def get_manual_ips(
    repo: Annotated[SettingsRepository, Depends(get_settings_repo)],
) -> ManualIPsResponse:
    """
    Get all manual device IP addresses.

    Returns:
        List of manually configured IP addresses
    """
    ips = await repo.get_manual_ips()
    return ManualIPsResponse(ips=ips)


@router.post(
    "/manual-ips",
    response_model=ManualIPsResponse,
    status_code=status.HTTP_200_OK,
)
async def set_manual_ips(
    request: SetManualIPsRequest,
    repo: Annotated[SettingsRepository, Depends(get_settings_repo)],
) -> ManualIPsResponse:
    """
    Replace all manual device IP addresses with new list.

    Args:
        request: Request containing list of IP addresses

    Returns:
        Updated list of manual IP addresses
    """
    # Clear existing IPs
    existing_ips = await repo.get_manual_ips()
    for ip in existing_ips:
        await repo.remove_manual_ip(ip)
    
    # Add new IPs
    for ip in request.ips:
        try:
            await repo.add_manual_ip(ip)
        except ValueError as e:
            # If one IP fails, rollback by clearing all
            for added_ip in request.ips:
                try:
                    await repo.remove_manual_ip(added_ip)
                except Exception:
                    pass
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid IP address: {ip}"
            ) from e
    
    return ManualIPsResponse(ips=request.ips)


@router.post(
    "/manual-ips/add",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_manual_ip(
    request: AddIPRequest,
    repo: Annotated[SettingsRepository, Depends(get_settings_repo)],
) -> MessageResponse:
    """
    Add a manual device IP address.

    Args:
        request: Request containing IP address to add

    Raises:
        HTTPException 400: If IP is invalid or already exists

    Returns:
        Success message with added IP
    """
    try:
        await repo.add_manual_ip(request.ip)
        return MessageResponse(message="IP added successfully", ip=request.ip)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.delete("/manual-ips/{ip}", response_model=MessageResponse)
async def delete_manual_ip(
    ip: str,
    repo: Annotated[SettingsRepository, Depends(get_settings_repo)],
) -> MessageResponse:
    """
    Remove a manual device IP address.

    Args:
        ip: IP address to remove

    Returns:
        Success message with removed IP
    """
    await repo.remove_manual_ip(ip)
    return MessageResponse(message="IP removed successfully", ip=ip)
