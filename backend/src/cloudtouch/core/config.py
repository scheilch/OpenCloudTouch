"""
Zentrale Konfiguration für SoundTouchBridge.
Nutzt pydantic-settings für ENV + YAML Validierung.
"""

from pathlib import Path
from typing import Optional

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Application configuration with ENV override and YAML support."""

    model_config = SettingsConfigDict(
        env_prefix="CT_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Server
    host: str = Field(default="0.0.0.0", description="API bind address")
    port: int = Field(default=7777, description="API port")
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="text", description="Log format: 'text' or 'json'")
    log_file: Optional[str] = Field(default=None, description="Optional log file path")

    # Database
    db_path: str = Field(default="/data/ct.db", description="SQLite database path")

    # Discovery
    discovery_enabled: bool = Field(
        default=True, description="Enable SSDP/UPnP discovery"
    )
    discovery_timeout: int = Field(
        default=10, description="Discovery timeout (seconds)"
    )
    manual_device_ips: str = Field(
        default="", description="Comma-separated list of manual device IPs"
    )

    @property
    def manual_device_ips_list(self) -> list[str]:
        """Get manual IPs as list."""
        if not self.manual_device_ips:
            return []
        return [ip.strip() for ip in self.manual_device_ips.split(",") if ip.strip()]

    # SoundTouch
    soundtouch_http_port: int = Field(
        default=8090, description="SoundTouch HTTP API port"
    )
    soundtouch_ws_port: int = Field(
        default=8080, description="SoundTouch WebSocket port"
    )

    # Station Descriptor
    station_descriptor_base_url: str = Field(
        default="http://localhost:7777/stations/preset",
        description="Base URL for station descriptors (used in preset URLs)",
    )

    # Feature Toggles (9.3.6 - NICE TO HAVE)
    enable_hdmi_controls: bool = Field(
        default=True,
        description="Enable HDMI/CEC controls for ST300 (can be disabled if causing issues)",
    )
    enable_advanced_audio: bool = Field(
        default=True,
        description="Enable advanced audio controls (DSP, Tone, Level) for ST300",
    )
    enable_zone_management: bool = Field(
        default=True, description="Enable multi-room zone management"
    )
    enable_group_management: bool = Field(
        default=True, description="Enable group management features"
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate and normalize log level.
        
        Args:
            v: Log level string (case-insensitive).
            
        Returns:
            Uppercase log level string.
            
        Raises:
            ValueError: If log level is not in allowed values.
        """
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}, got {v}")
        return v_upper

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Validate and normalize log format.
        
        Args:
            v: Log format string (case-insensitive).
            
        Returns:
            Lowercase log format string ('text' or 'json').
            
        Raises:
            ValueError: If log format is not in allowed values.
        """
        allowed = {"text", "json"}
        v_lower = v.lower()
        if v_lower not in allowed:
            raise ValueError(f"log_format must be one of {allowed}, got {v}")
        return v_lower

    @classmethod
    def load_from_yaml(cls, yaml_path: Path) -> "AppConfig":
        """Load configuration from YAML file (optional overlay)."""
        if not yaml_path.exists():
            return cls()

        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return cls(**data)


# Globale Config-Instanz
config: Optional[AppConfig] = None


def init_config(yaml_path: Optional[Path] = None) -> AppConfig:
    """Initialize global config instance."""
    global config
    if yaml_path and yaml_path.exists():
        config = AppConfig.load_from_yaml(yaml_path)
    else:
        config = AppConfig()
    return config


def get_config() -> AppConfig:
    """Get current config instance."""
    if config is None:
        raise RuntimeError("Config not initialized. Call init_config() first.")
    return config
