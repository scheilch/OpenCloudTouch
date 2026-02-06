"""
Custom exceptions for OpenCloudTouch
Provides a unified exception hierarchy for better error handling
"""


class OpenCloudTouchError(Exception):
    """Base exception for all OpenCloudTouch errors."""

    pass


class DiscoveryError(OpenCloudTouchError):
    """Raised when device discovery fails."""

    pass


class DeviceConnectionError(OpenCloudTouchError):
    """Raised when connection to a streaming device fails."""

    def __init__(self, device_ip: str, message: str = "Device unreachable"):
        self.device_ip = device_ip
        super().__init__(f"{message}: {device_ip}")


class DeviceNotFoundError(OpenCloudTouchError):
    """Raised when a requested device is not found in the database."""

    def __init__(self, device_id: str):
        self.device_id = device_id
        super().__init__(f"Device not found: {device_id}")


class ConfigurationError(OpenCloudTouchError):
    """Raised when configuration is invalid."""

    pass
