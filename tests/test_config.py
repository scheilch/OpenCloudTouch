"""
Unit tests for configuration module
"""
import pytest
from pathlib import Path

from backend.config import AppConfig, init_config


def test_config_defaults():
    """Test default configuration values."""
    config = AppConfig()
    
    assert config.host == "0.0.0.0"
    assert config.port == 7777
    assert config.log_level == "INFO"
    assert config.db_path == "/data/stb.db"
    assert config.discovery_enabled is True
    assert config.discovery_timeout == 10
    assert config.manual_device_ips == []
    assert config.soundtouch_http_port == 8090
    assert config.soundtouch_ws_port == 8080


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
    """Test that ENV variables are recognized with STB_ prefix."""
    import os
    
    # Set ENV variable
    os.environ["STB_PORT"] = "9000"
    os.environ["STB_LOG_LEVEL"] = "DEBUG"
    
    config = AppConfig()
    
    assert config.port == 9000
    assert config.log_level == "DEBUG"
    
    # Clean up
    del os.environ["STB_PORT"]
    del os.environ["STB_LOG_LEVEL"]


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
        'host': '127.0.0.1',
        'port': 9000,
        'log_level': 'DEBUG',
        'db_path': '/tmp/test.db',
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(yaml_content, f)
        yaml_path = Path(f.name)
    
    try:
        config = AppConfig.load_from_yaml(yaml_path)
        
        assert config.host == '127.0.0.1'
        assert config.port == 9000
        assert config.log_level == 'DEBUG'
        assert config.db_path == '/tmp/test.db'
    finally:
        yaml_path.unlink()


def test_config_yaml_nonexistent():
    """Test loading config from nonexistent YAML file returns defaults."""
    config = AppConfig.load_from_yaml(Path('/nonexistent/file.yaml'))
    
    # Should return default config
    assert config.host == "0.0.0.0"
    assert config.port == 7777


def test_get_config_not_initialized():
    """Test get_config raises error when not initialized."""
    import backend.config
    
    # Temporarily set config to None
    original = backend.config.config
    backend.config.config = None
    
    try:
        with pytest.raises(RuntimeError, match="Config not initialized"):
            backend.config.get_config()
    finally:
        backend.config.config = original
