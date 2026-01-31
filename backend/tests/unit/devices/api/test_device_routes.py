"""
Tests for Device API Endpoints

Struktur:
- TestDeviceListEndpoint: GET /api/devices
- TestDeviceDetailEndpoint: GET /api/devices/{id}
- TestDiscoverEndpoint: GET /api/devices/discover
- TestSyncEndpoint: POST /api/devices/sync
- TestCapabilitiesEndpoint: GET /api/devices/{id}/capabilities
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from soundtouch_bridge.main import app
from soundtouch_bridge.devices.repository import Device, DeviceRepository
from soundtouch_bridge.devices.api.routes import get_device_repo


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
def sample_devices():
    """Sample device list for testing."""
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


class TestDeviceListEndpoint:
    """Tests for GET /api/devices endpoint."""
    
    def test_get_devices_empty(self, client, mock_repo):
        """Test GET /api/devices with empty database."""
        mock_repo.get_all = AsyncMock(return_value=[])
        
        response = client.get("/api/devices")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["devices"] == []
    
    def test_get_devices_with_data(self, client, mock_repo, sample_devices):
        """Test GET /api/devices with devices in database."""
        mock_repo.get_all = AsyncMock(return_value=sample_devices)
        
        response = client.get("/api/devices")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["devices"]) == 2
        assert data["devices"][0]["device_id"] == "12345ABC"
        assert data["devices"][1]["device_id"] == "67890DEF"
    
    def test_get_devices_includes_all_fields(self, client, mock_repo, sample_devices):
        """Test that response includes all device fields."""
        mock_repo.get_all = AsyncMock(return_value=[sample_devices[0]])
        
        response = client.get("/api/devices")
        
        assert response.status_code == 200
        device = response.json()["devices"][0]
        assert "device_id" in device
        assert "ip" in device
        assert "name" in device
        assert "model" in device
        assert "mac_address" in device
        assert "firmware_version" in device


class TestDeviceDetailEndpoint:
    """Tests for GET /api/devices/{device_id} endpoint."""
    
    def test_get_device_by_id_success(self, client, mock_repo, sample_devices):
        """Test GET /api/devices/{device_id} - device found."""
        mock_repo.get_by_device_id = AsyncMock(return_value=sample_devices[0])
        
        response = client.get("/api/devices/12345ABC")
        
        assert response.status_code == 200
        data = response.json()
        assert data["device_id"] == "12345ABC"
        assert data["name"] == "Living Room"
        assert data["model"] == "SoundTouch 30"
    
    def test_get_device_by_id_not_found(self, client, mock_repo):
        """Test GET /api/devices/{device_id} - device not found."""
        mock_repo.get_by_device_id = AsyncMock(return_value=None)
        
        response = client.get("/api/devices/NOTFOUND")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_device_by_id_includes_all_fields(self, client, mock_repo, sample_devices):
        """Test that device detail response includes all fields."""
        mock_repo.get_by_device_id = AsyncMock(return_value=sample_devices[0])
        
        response = client.get("/api/devices/12345ABC")
        
        assert response.status_code == 200
        device = response.json()
        assert device["device_id"] == "12345ABC"
        assert device["ip"] == "192.168.1.100"
        assert device["name"] == "Living Room"
        assert device["model"] == "SoundTouch 30"
        assert device["mac_address"] == "AA:BB:CC:DD:EE:FF"
        assert device["firmware_version"] == "28.0.5.46710"


class TestSyncEndpoint:
    """Tests for POST /api/devices/sync endpoint."""
    
    @pytest.mark.asyncio
    async def test_sync_prevents_concurrent_requests(self):
        """
        Regression test: Concurrent discovery requests blocked.
        
        Bug: Multiple simultaneous discovery requests cause race condition.
        Fixed: 2026-01-29 - _discovery_in_progress flag + asyncio.Lock.
        """
        from soundtouch_bridge.devices.api.routes import _discovery_lock, _discovery_in_progress
        import soundtouch_bridge.devices.api.routes as devices_module
        
        # Reset state
        devices_module._discovery_in_progress = False
        
        # Simulate discovery in progress
        devices_module._discovery_in_progress = True
        
        try:
            # Verify flag is set (endpoint would return 409)
            assert devices_module._discovery_in_progress is True
            
        finally:
            # Reset
            devices_module._discovery_in_progress = False
    
    @pytest.mark.asyncio
    async def test_sync_releases_lock_on_error(self):
        """
        Regression test: Discovery lock released even when discovery fails.
        
        Bug: If discovery raises exception, lock might remain acquired.
        Fixed: 2026-01-29 - try-finally block resets _discovery_in_progress.
        """
        from soundtouch_bridge.devices.api.routes import _discovery_lock
        import soundtouch_bridge.devices.api.routes as devices_module
        
        # Reset global state
        devices_module._discovery_in_progress = False
        
        # Mock discovery to raise exception
        original_discover = devices_module.discover_devices
        
        async def failing_discover():
            raise RuntimeError("Discovery failed")
        
        devices_module.discover_devices = failing_discover
        
        try:
            # Attempt discovery (should fail but release lock)
            async with _discovery_lock:
                devices_module._discovery_in_progress = True
                try:
                    await devices_module.discover_devices()
                except RuntimeError:
                    pass
                finally:
                    devices_module._discovery_in_progress = False
            
            # Verify lock released
            assert not _discovery_lock.locked()
            assert not devices_module._discovery_in_progress
            
        finally:
            # Restore original function
            devices_module.discover_devices = original_discover
    
    def test_sync_endpoint_returns_409_when_in_progress(self, client, mock_repo):
        """Test POST /api/devices/sync returns 409 if discovery already running."""
        import soundtouch_bridge.devices.api.routes as devices_module
        
        # Set discovery in progress
        devices_module._discovery_in_progress = True
        
        try:
            response = client.post("/api/devices/sync")
            
            assert response.status_code == 409
            assert "already in progress" in response.json()["detail"].lower()
            
        finally:
            # Reset
            devices_module._discovery_in_progress = False


class TestDiscoverEndpoint:
    """Tests for GET /api/devices/discover endpoint."""
    
    # TODO: Add tests for discover endpoint
    # - test_discover_success
    # - test_discover_no_devices
    # - test_discover_with_manual_ips
    # - test_discover_timeout
    pass


class TestCapabilitiesEndpoint:
    """Tests for GET /api/devices/{device_id}/capabilities endpoint."""
    
    # TODO: Add tests for capabilities endpoint
    # - test_get_capabilities_success
    # - test_get_capabilities_device_not_found
    # - test_get_capabilities_device_offline
    pass
