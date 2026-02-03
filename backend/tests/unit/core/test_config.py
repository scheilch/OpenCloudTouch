"""
Unit tests for configuration module
"""

import pytest
from pathlib import Path

from cloudtouch.core.config import AppConfig, init_config


def test_config_defaults():
    """Test default configuration values."""
    config = AppConfig()

    assert config.host == "0.0.0.0"
    assert config.port == 7777
    assert config.log_level == "INFO"
    assert config.db_path == ""  # Empty by default
    assert config.effective_db_path == "/data/ct.db"  # Production default
    assert config.discovery_enabled is True
    assert config.discovery_timeout == 10
    assert config.manual_device_ips_list == []
    assert config.soundtouch_http_port == 8090
    assert config.soundtouch_ws_port == 8080

    # Feature toggles (9.3.6)
    assert config.enable_hdmi_controls is True
    assert config.enable_advanced_audio is True
    assert config.enable_zone_management is True
    assert config.enable_group_management is True


def test_config_feature_toggles():
    """Test feature toggle configuration."""
    # Default: all enabled
    config1 = AppConfig()
    assert config1.enable_hdmi_controls is True
    assert config1.enable_advanced_audio is True

    # Disable specific features
    config2 = AppConfig(
        enable_hdmi_controls=False,
        enable_advanced_audio=False,
        enable_zone_management=False,
    )
    assert config2.enable_hdmi_controls is False
    assert config2.enable_advanced_audio is False
    assert config2.enable_zone_management is False
    assert config2.enable_group_management is True  # Still enabled


def test_config_feature_toggles_from_env():
    """Test feature toggles from environment variables."""
    import os

    # Set ENV variables
    os.environ["CT_ENABLE_HDMI_CONTROLS"] = "false"
    os.environ["CT_ENABLE_ADVANCED_AUDIO"] = "false"

    config = AppConfig()

    assert config.enable_hdmi_controls is False
    assert config.enable_advanced_audio is False
    assert config.enable_zone_management is True  # Not set, default True

    # Clean up
    del os.environ["CT_ENABLE_HDMI_CONTROLS"]
    del os.environ["CT_ENABLE_ADVANCED_AUDIO"]


def test_config_log_level_validation():
    """Test log level validation."""
    # Valid log levels
    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        config = AppConfig(log_level=level)
        assert config.log_level == level

    # Case insensitive
    config = AppConfig(log_level="info")
    assert config.log_level == "INFO"

    # Invalid log level
    with pytest.raises(ValueError):
        AppConfig(log_level="INVALID")


def test_config_env_prefix():
    """Test that ENV variables are recognized with CT_ prefix."""
    import os

    # Set ENV variable
    os.environ["CT_PORT"] = "9000"
    os.environ["CT_LOG_LEVEL"] = "DEBUG"

    config = AppConfig()

    assert config.port == 9000
    assert config.log_level == "DEBUG"

    # Clean up
    del os.environ["CT_PORT"]
    del os.environ["CT_LOG_LEVEL"]


def test_config_init():
    """Test init_config function."""
    config = init_config()

    assert config is not None
    assert isinstance(config, AppConfig)


def test_config_yaml_loading():
    """Test loading config from YAML file."""
    import tempfile
    import yaml

    # Create temporary YAML config
    yaml_content = {
        "host": "127.0.0.1",
        "port": 9000,
        "log_level": "DEBUG",
        "db_path": "/tmp/test.db",
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(yaml_content, f)
        yaml_path = Path(f.name)

    try:
        config = AppConfig.load_from_yaml(yaml_path)

        assert config.host == "127.0.0.1"
        assert config.port == 9000
        assert config.log_level == "DEBUG"
        assert config.db_path == "/tmp/test.db"
    finally:
        yaml_path.unlink()


def test_config_yaml_nonexistent():
    """Test loading config from nonexistent YAML file returns defaults."""
    config = AppConfig.load_from_yaml(Path("/nonexistent/file.yaml"))

    # Should return default config
    assert config.host == "0.0.0.0"
    assert config.port == 7777


def test_get_config_not_initialized():
    """Test get_config raises error when not initialized."""
    import cloudtouch.core.config

    # Temporarily set config to None
    original = cloudtouch.core.config.config
    cloudtouch.core.config.config = None

    try:
        with pytest.raises(RuntimeError, match="Config not initialized"):
            cloudtouch.core.config.get_config()
    finally:
        cloudtouch.core.config.config = original


def test_effective_db_path_explicit():
    """Test effective_db_path returns explicit value when set."""
    config = AppConfig(db_path="/custom/path.db")
    assert config.effective_db_path == "/custom/path.db"


def test_effective_db_path_ci_mode(monkeypatch):
    """Test effective_db_path returns :memory: in CI."""
    monkeypatch.setenv("CI", "true")
    config = AppConfig()
    assert config.effective_db_path == ":memory:"


def test_effective_db_path_mock_mode():
    """Test effective_db_path returns test DB in mock mode."""
    config = AppConfig(mock_mode=True)
    assert config.effective_db_path == "data-local/ct-test.db"


def test_effective_db_path_production():
    """Test effective_db_path returns production path by default."""
    config = AppConfig()
    assert config.effective_db_path == "/data/ct.db"

