"""
Custom exceptions for SoundTouch Bridge
Provides a unified exception hierarchy for better error handling
"""


class SoundTouchBridgeError(Exception):
    """Base exception for all SoundTouch Bridge errors."""

    pass


class DiscoveryError(SoundTouchBridgeError):
    """Raised when device discovery fails."""

    pass


class DeviceConnectionError(SoundTouchBridgeError):
    """Raised when connection to a SoundTouch device fails."""

    def __init__(self, device_ip: str, message: str = "Device unreachable"):
        self.device_ip = device_ip
        super().__init__(f"{message}: {device_ip}")


class DeviceNotFoundError(SoundTouchBridgeError):
    """Raised when a requested device is not found in the database."""

    def __init__(self, device_id: str):
        self.device_id = device_id
        super().__init__(f"Device not found: {device_id}")


class ConfigurationError(SoundTouchBridgeError):
    """Raised when configuration is invalid."""

    pass
