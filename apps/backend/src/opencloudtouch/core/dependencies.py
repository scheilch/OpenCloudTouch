"""Dependency injection for FastAPI routes.

Centralizes dependency management and eliminates global state.
"""

from typing import Optional

from opencloudtouch.devices.repository import DeviceRepository
from opencloudtouch.settings.repository import SettingsRepository

# Private singleton instances (module-level)
_device_repo_instance: Optional[DeviceRepository] = None
_settings_repo_instance: Optional[SettingsRepository] = None


def set_device_repo(repo: DeviceRepository) -> None:
    """Register device repository instance (called from lifespan)."""
    global _device_repo_instance
    _device_repo_instance = repo


def set_settings_repo(repo: SettingsRepository) -> None:
    """Register settings repository instance (called from lifespan)."""
    global _settings_repo_instance
    _settings_repo_instance = repo


async def get_device_repo() -> DeviceRepository:
    """Get device repository instance (FastAPI dependency)."""
    if _device_repo_instance is None:
        raise RuntimeError("DeviceRepository not initialized")
    return _device_repo_instance


async def get_settings_repo() -> SettingsRepository:
    """Get settings repository instance (FastAPI dependency)."""
    if _settings_repo_instance is None:
        raise RuntimeError("SettingsRepository not initialized")
    return _settings_repo_instance


def clear_dependencies() -> None:
    """Clear all dependency instances (for testing)."""
    global _device_repo_instance, _settings_repo_instance
    _device_repo_instance = None
    _settings_repo_instance = None
