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
        env_prefix="STB_",
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
    db_path: str = Field(default="/data/stb.db", description="SQLite database path")

    # Discovery
    discovery_enabled: bool = Field(default=True, description="Enable SSDP/UPnP discovery")
    discovery_timeout: int = Field(default=10, description="Discovery timeout (seconds)")
    manual_device_ips: list[str] = Field(default_factory=list, description="Manual device IPs")

    @field_validator("manual_device_ips", mode="before")
    @classmethod
    def parse_manual_ips(cls, v):
        """Parse manual IPs from string or list."""
        if isinstance(v, str):
            if not v:
                return []
            return [ip.strip() for ip in v.split(",") if ip.strip()]
        return v if v else []

    # SoundTouch
    soundtouch_http_port: int = Field(default=8090, description="SoundTouch HTTP API port")
    soundtouch_ws_port: int = Field(default=8080, description="SoundTouch WebSocket port")

    # Station Descriptor
    station_descriptor_base_url: str = Field(
        default="http://localhost:7777/stations/preset",
        description="Base URL for station descriptors (used in preset URLs)",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}, got {v}")
        return v_upper
    
    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        allowed = {"text", "json"}
        v_lower = v.lower()
        if v_lower not in allowed:
            raise ValueError(f"log_format must be one of {allowed}, got {v}")
        return v_lower
        if v_upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v_upper

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
