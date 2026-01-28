"""Tests for structured logging configuration."""
import logging
import json
import sys
from io import StringIO
from pathlib import Path

import pytest

from backend.logging_config import (
    StructuredFormatter,
    ContextFormatter,
    setup_logging,
    get_logger
)


def test_structured_formatter_basic():
    """Test JSON formatter with basic log record."""
    formatter = StructuredFormatter()
    record = logging.LogRecord(
        name="test.module",
        level=logging.INFO,
        pathname="/path/to/file.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    output = formatter.format(record)
    data = json.loads(output)
    
    assert data["message"] == "Test message"
    assert data["level"] == "INFO"
    assert data["logger"] == "test.module"
    assert "timestamp" in data


def test_structured_formatter_with_exception():
    """Test JSON formatter with exception info."""
    formatter = StructuredFormatter()
    
    try:
        raise ValueError("Test error")
    except ValueError:
        exc_info = sys.exc_info()
    
    record = logging.LogRecord(
        name="test.module",
        level=logging.ERROR,
        pathname="/path/to/file.py",
        lineno=100,
        msg="Error occurred",
        args=(),
        exc_info=exc_info
    )
    
    output = formatter.format(record)
    data = json.loads(output)
    
    assert data["message"] == "Error occurred"
    assert "exception" in data
    assert "ValueError: Test error" in data["exception"]


def test_context_formatter_basic():
    """Test colored text formatter."""
    formatter = ContextFormatter()
    record = logging.LogRecord(
        name="test.module",
        level=logging.INFO,
        pathname="/path/to/file.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    output = formatter.format(record)
    assert "Test message" in output
    assert "test.module" in output
    assert "INFO" in output


def test_context_formatter_with_exception():
    """Test colored formatter with exception."""
    formatter = ContextFormatter()
    
    try:
        raise RuntimeError("Test runtime error")
    except RuntimeError:
        exc_info = sys.exc_info()
    
    record = logging.LogRecord(
        name="backend.api",
        level=logging.ERROR,
        pathname="/path/to/api.py",
        lineno=200,
        msg="Error occurred",
        args=(),
        exc_info=exc_info
    )
    
    output = formatter.format(record)
    assert "Error occurred" in output
    assert "RuntimeError: Test runtime error" in output


def test_setup_logging_default(monkeypatch, tmp_path):
    """Test logging setup with default config."""
    # Mock config
    from backend.config import AppConfig
    mock_config = AppConfig(
        log_level="INFO",
        log_format="text",
        log_file=None
    )
    monkeypatch.setattr("backend.logging_config.get_config", lambda: mock_config)
    
    # Setup logging
    setup_logging()
    
    # Verify root logger
    root_logger = logging.getLogger()
    assert root_logger.level == logging.INFO
    assert len(root_logger.handlers) >= 1


def test_setup_logging_json_format(monkeypatch):
    """Test logging setup with JSON format."""
    from backend.config import AppConfig
    mock_config = AppConfig(
        log_level="DEBUG",
        log_format="json",
        log_file=None
    )
    monkeypatch.setattr("backend.logging_config.get_config", lambda: mock_config)
    
    setup_logging()
    
    root_logger = logging.getLogger()
    console_handler = root_logger.handlers[0]
    assert isinstance(console_handler.formatter, StructuredFormatter)


def test_setup_logging_with_file(monkeypatch, tmp_path):
    """Test logging setup with file logging."""
    log_file = tmp_path / "test.log"
    
    from backend.config import AppConfig
    mock_config = AppConfig(
        log_level="WARNING",
        log_format="text",
        log_file=str(log_file)
    )
    monkeypatch.setattr("backend.logging_config.get_config", lambda: mock_config)
    
    setup_logging()
    
    # Write a log message
    test_logger = logging.getLogger("test.file")
    test_logger.warning("Test warning message")
    
    # Verify file was created and contains message
    assert log_file.exists()
    content = log_file.read_text()
    assert "Test warning message" in content


def test_setup_logging_silences_third_party_loggers(monkeypatch):
    """Test that noisy third-party loggers are silenced."""
    from backend.config import AppConfig
    mock_config = AppConfig(
        log_level="DEBUG",
        log_format="text",
        log_file=None
    )
    monkeypatch.setattr("backend.logging_config.get_config", lambda: mock_config)
    
    setup_logging()
    
    # Check that third-party loggers are set to WARNING
    assert logging.getLogger("urllib3").level == logging.WARNING
    assert logging.getLogger("httpx").level == logging.WARNING
    assert logging.getLogger("httpcore").level == logging.WARNING


def test_get_logger():
    """Test get_logger utility function."""
    logger = get_logger("test.logger")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test.logger"
