"""
Tests for Device API Endpoints
"""
import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from backend.main import app
from backend.db.devices import Device, DeviceRepository
from backend.api.devices import get_device_repo


@pytest.fixture
def mock_repo():
    """Mock device repository."""
    repo = AsyncMock(spec=DeviceRepository)
    return repo


@pytest.fixture
def client(mock_repo):
    """FastAPI test client with dependency override."""
    app.dependency_overrides[get_device_repo] = lambda: mock_repo
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def mock_devices():
    """Sample device list."""
    return [
        Device(
            id=1,
            device_id="12345ABC",
            ip="192.168.1.100",
            name="Living Room",
            model="SoundTouch 30",
            mac_address="AA:BB:CC:DD:EE:FF",
            firmware_version="28.0.5.46710",
        ),
        Device(
            id=2,
            device_id="67890DEF",
            ip="192.168.1.101",
            name="Kitchen",
            model="SoundTouch 10",
            mac_address="11:22:33:44:55:66",
            firmware_version="28.0.5.46710",
        ),
    ]


def test_get_devices_empty(client, mock_repo):
    """Test GET /api/devices with empty database."""
    mock_repo.get_all = AsyncMock(return_value=[])
    
    response = client.get("/api/devices")
    
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["devices"] == []


def test_get_devices(client, mock_repo, mock_devices):
    """Test GET /api/devices with devices."""
    mock_repo.get_all = AsyncMock(return_value=mock_devices)
    
    response = client.get("/api/devices")
    
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["devices"]) == 2
    assert data["devices"][0]["device_id"] == "12345ABC"
    assert data["devices"][1]["device_id"] == "67890DEF"


def test_get_device_by_id(client, mock_repo, mock_devices):
    """Test GET /api/devices/{device_id} - device found."""
    mock_repo.get_by_device_id = AsyncMock(return_value=mock_devices[0])
    
    response = client.get("/api/devices/12345ABC")
    
    assert response.status_code == 200
    data = response.json()
    assert data["device_id"] == "12345ABC"
    assert data["name"] == "Living Room"


def test_get_device_by_id_not_found(client, mock_repo):
    """Test GET /api/devices/{device_id} - device not found."""
    mock_repo.get_by_device_id = AsyncMock(return_value=None)
    
    response = client.get("/api/devices/NOTFOUND")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
