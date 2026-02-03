"""
Unit tests for SoundTouchBridge main application
"""

import pytest
from fastapi.testclient import TestClient

from cloudtouch.core.config import init_config
from cloudtouch.main import app


@pytest.fixture(scope="module")
def client():
    """Test client fixture."""
    init_config()
    return TestClient(app)


def test_health_endpoint(client):
    """Test /health endpoint returns 200 and expected structure."""
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "version" in data
    assert data["version"] == "0.2.0"
    assert "config" in data
    assert "discovery_enabled" in data["config"]
    assert "db_path" in data["config"]


def test_health_endpoint_structure(client):
    """Test /health endpoint returns proper JSON structure."""
    response = client.get("/health")
    data = response.json()

    # Validate types
    assert isinstance(data["status"], str)
    assert isinstance(data["version"], str)
    assert isinstance(data["config"], dict)
    assert isinstance(data["config"]["discovery_enabled"], bool)
    assert isinstance(data["config"]["db_path"], str)
