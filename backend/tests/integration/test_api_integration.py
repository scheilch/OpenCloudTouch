"""Integration tests for device API endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from cloudtouch.db import Device, DeviceRepository
from cloudtouch.devices.api.routes import get_device_repo
from cloudtouch.devices.client import DeviceInfo
from cloudtouch.discovery import DiscoveredDevice
from cloudtouch.main import app
from cloudtouch.settings.repository import SettingsRepository


@pytest.fixture
def mock_config():
    """Mock configuration."""
    with patch("cloudtouch.devices.api.routes.get_config") as mock:
        mock_cfg = AsyncMock()
        mock_cfg.discovery_enabled = True
        mock_cfg.discovery_timeout = 5
        mock_cfg.manual_device_ips_list = []
        mock.return_value = mock_cfg
        yield mock_cfg


@pytest.mark.asyncio
async def test_discover_endpoint_success(mock_config):
    """Test /api/devices/discover endpoint with successful discovery."""
    discovered = [
        DiscoveredDevice(ip="192.168.1.100", port=8090, name="Living Room"),
        DiscoveredDevice(ip="192.168.1.101", port=8090, name="Kitchen"),
    ]

    with patch(
        "cloudtouch.devices.api.routes.BoseSoundTouchDiscoveryAdapter"
    ) as mock_adapter:
        mock_instance = AsyncMock()
        mock_instance.discover.return_value = discovered
        mock_adapter.return_value = mock_instance

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/devices/discover")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["devices"]) == 2
        assert data["devices"][0]["ip"] == "192.168.1.100"


@pytest.mark.asyncio
async def test_discover_endpoint_with_manual_ips(mock_config):
    """Test discovery with manual IPs configured."""
    mock_config.discovery_enabled = False
    mock_config.manual_device_ips_list = ["192.168.1.200"]

    manual_discovered = [
        DiscoveredDevice(ip="192.168.1.200", port=8090, name="Manual Device")
    ]

    with patch("cloudtouch.devices.api.routes.ManualDiscovery") as mock_manual:
        mock_instance = AsyncMock()
        mock_instance.discover.return_value = manual_discovered
        mock_manual.return_value = mock_instance

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/devices/discover")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["devices"][0]["ip"] == "192.168.1.200"


@pytest.mark.asyncio
async def test_discover_endpoint_no_devices(mock_config):
    """Test discovery when no devices are found."""
    with patch(
        "cloudtouch.devices.api.routes.BoseSoundTouchDiscoveryAdapter"
    ) as mock_adapter:
        mock_instance = AsyncMock()
        mock_instance.discover.return_value = []
        mock_adapter.return_value = mock_instance

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/devices/discover")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["devices"] == []


@pytest.mark.asyncio
async def test_discover_endpoint_discovery_error(mock_config):
    """Test discovery endpoint when discovery fails."""
    with patch(
        "cloudtouch.devices.api.routes.BoseSoundTouchDiscoveryAdapter"
    ) as mock_adapter:
        mock_instance = AsyncMock()
        mock_instance.discover.side_effect = Exception("Network error")
        mock_adapter.return_value = mock_instance

        # Discovery errors are caught and logged, returns empty list
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/devices/discover")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0


@pytest.mark.asyncio
async def test_sync_devices_success(mock_config):
    """Test /api/devices/sync endpoint with successful sync."""
    discovered = [DiscoveredDevice(ip="192.168.1.100", port=8090, name="Living Room")]

    device_info = DeviceInfo(
        device_id="AABBCC112233",
        name="Living Room",
        type="SoundTouch 10",
        mac_address="AA:BB:CC:11:22:33",
        ip_address="192.168.1.100",
        firmware_version="1.0.0",
    )

    # Mock repository
    mock_repo = AsyncMock(spec=DeviceRepository)
    mock_repo.upsert = AsyncMock()

    # Mock settings repository
    mock_settings = AsyncMock(spec=SettingsRepository)
    mock_settings.get_manual_ips = AsyncMock(return_value=[])

    async def get_mock_repo():
        return mock_repo

    async def get_mock_settings():
        return mock_settings

    # Inject mock directly into main module
    import cloudtouch.main as main_module

    original_settings = main_module.settings_repo
    main_module.settings_repo = mock_settings

    try:
        with patch(
            "cloudtouch.devices.services.sync_service.get_discovery_adapter"
        ) as mock_get_disco, patch(
            "cloudtouch.devices.services.sync_service.get_soundtouch_client"
        ) as mock_get_client:

            # Mock discovery factory
            mock_disco_instance = AsyncMock()
            mock_disco_instance.discover.return_value = discovered
            mock_get_disco.return_value = mock_disco_instance

            # Mock client factory
            mock_client_instance = AsyncMock()
            mock_client_instance.get_info.return_value = device_info
            mock_get_client.return_value = mock_client_instance

            # Override dependency
            app.dependency_overrides[get_device_repo] = get_mock_repo

            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.post("/api/devices/sync")

            assert response.status_code == 200
            data = response.json()
            assert data["discovered"] == 1
            assert data["synced"] == 1
            assert data["failed"] == 0
    finally:
        # Restore original
        main_module.settings_repo = original_settings
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_sync_devices_partial_failure(mock_config):
    """Test sync with one device failing to connect."""
    discovered = [
        DiscoveredDevice(ip="192.168.1.100", port=8090, name="Working"),
        DiscoveredDevice(ip="192.168.1.101", port=8090, name="Broken"),
    ]

    device_info = DeviceInfo(
        device_id="AABBCC112233",
        name="Working",
        type="SoundTouch 10",
        mac_address="AA:BB:CC:11:22:33",
        ip_address="192.168.1.100",
        firmware_version="1.0.0",
    )

    mock_repo = AsyncMock(spec=DeviceRepository)
    mock_repo.upsert = AsyncMock()

    # Mock settings repository
    mock_settings = AsyncMock(spec=SettingsRepository)
    mock_settings.get_manual_ips = AsyncMock(return_value=[])

    async def get_mock_repo():
        return mock_repo

    # Inject mock directly into main module
    import cloudtouch.main as main_module

    original_settings = main_module.settings_repo
    main_module.settings_repo = mock_settings

    try:
        with patch(
            "cloudtouch.devices.services.sync_service.get_discovery_adapter"
        ) as mock_get_disco, patch(
            "cloudtouch.devices.services.sync_service.get_soundtouch_client"
        ) as mock_get_client:

            mock_disco_instance = AsyncMock()
            mock_disco_instance.discover.return_value = discovered
            mock_get_disco.return_value = mock_disco_instance

            # First device succeeds, second fails
            mock_client_instance = AsyncMock()
            mock_client_instance.get_info.side_effect = [
                device_info,
                Exception("Connection timeout"),
            ]
            mock_get_client.return_value = mock_client_instance

            app.dependency_overrides[get_device_repo] = get_mock_repo

            transport = ASGITransport(app=app)
            async with AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                response = await client.post("/api/devices/sync")

            assert response.status_code == 200
            data = response.json()
            assert data["discovered"] == 2
            assert data["synced"] == 1
            assert data["failed"] == 1
    finally:
        # Restore original
        main_module.settings_repo = original_settings
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_devices_empty():
    """Test GET /api/devices with no devices in DB."""
    mock_repo = AsyncMock(spec=DeviceRepository)
    mock_repo.get_all.return_value = []

    async def get_mock_repo():
        return mock_repo

    app.dependency_overrides[get_device_repo] = get_mock_repo

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/devices")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["devices"] == []
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_devices_with_data():
    """Test GET /api/devices with devices in DB."""
    devices = [
        Device(
            device_id="DEVICE1",
            ip="192.168.1.100",
            name="Living Room",
            model="SoundTouch 10",
            mac_address="AA:BB:CC:11:22:33",
            firmware_version="1.0.0",
        ),
        Device(
            device_id="DEVICE2",
            ip="192.168.1.101",
            name="Kitchen",
            model="SoundTouch 20",
            mac_address="DD:EE:FF:44:55:66",
            firmware_version="1.0.1",
        ),
    ]

    mock_repo = AsyncMock(spec=DeviceRepository)
    mock_repo.get_all.return_value = devices

    async def get_mock_repo():
        return mock_repo

    app.dependency_overrides[get_device_repo] = get_mock_repo

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/devices")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["devices"]) == 2
        assert data["devices"][0]["device_id"] == "DEVICE1"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_device_by_id_success():
    """Test GET /api/devices/{device_id} with existing device."""
    device = Device(
        device_id="DEVICE1",
        ip="192.168.1.100",
        name="Living Room",
        model="SoundTouch 10",
        mac_address="AA:BB:CC:11:22:33",
        firmware_version="1.0.0",
    )

    mock_repo = AsyncMock(spec=DeviceRepository)
    mock_repo.get_by_device_id.return_value = device

    async def get_mock_repo():
        return mock_repo

    app.dependency_overrides[get_device_repo] = get_mock_repo

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/devices/DEVICE1")

        assert response.status_code == 200
        data = response.json()
        assert data["device_id"] == "DEVICE1"
        assert data["name"] == "Living Room"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_device_by_id_not_found():
    """Test GET /api/devices/{device_id} with non-existent device."""
    mock_repo = AsyncMock(spec=DeviceRepository)
    mock_repo.get_by_device_id.return_value = None

    async def get_mock_repo():
        return mock_repo

    app.dependency_overrides[get_device_repo] = get_mock_repo

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/devices/NONEXISTENT")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    finally:
        app.dependency_overrides.clear()
