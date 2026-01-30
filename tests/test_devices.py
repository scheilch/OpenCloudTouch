"""
Tests for Device Repository
"""
import pytest
import tempfile
from pathlib import Path

from backend.db import Device, DeviceRepository


@pytest.fixture
async def repo():
    """Create temporary test database."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    repository = DeviceRepository(db_path)
    await repository.initialize()
    
    yield repository
    
    await repository.close()
    Path(db_path).unlink()


@pytest.mark.asyncio
async def test_device_repository_initialize(repo):
    """Test database initialization."""
    # Should not raise
    assert repo._db is not None


@pytest.mark.asyncio
async def test_device_upsert_insert(repo):
    """Test inserting a new device."""
    device = Device(
        device_id="TEST123",
        ip="192.168.1.100",
        name="Test Device",
        model="SoundTouch 10",
        mac_address="AA:BB:CC:DD:EE:FF",
        firmware_version="1.0.0",
    )
    
    result = await repo.upsert(device)
    
    assert result.id is not None
    assert result.device_id == "TEST123"


@pytest.mark.asyncio
async def test_device_upsert_update(repo):
    """Test updating an existing device."""
    device = Device(
        device_id="TEST123",
        ip="192.168.1.100",
        name="Test Device",
        model="SoundTouch 10",
        mac_address="AA:BB:CC:DD:EE:FF",
        firmware_version="1.0.0",
    )
    
    await repo.upsert(device)
    
    # Update with new IP
    device.ip = "192.168.1.101"
    device.firmware_version = "2.0.0"
    
    updated = await repo.upsert(device)
    
    assert updated.ip == "192.168.1.101"
    assert updated.firmware_version == "2.0.0"
    
    # Verify only one record exists
    all_devices = await repo.get_all()
    assert len(all_devices) == 1


@pytest.mark.asyncio
async def test_device_get_all_empty(repo):
    """Test get_all with empty database."""
    devices = await repo.get_all()
    
    assert devices == []


@pytest.mark.asyncio
async def test_firmware_version_with_release_suffix_storage(repo):
    """Regression test: Firmware version with release suffix stored correctly.
    
    Bug: Frontend trimmt Firmware bei 'epdbuild', aber Backend muss volle Version speichern.
    Fixed: 2026-01-29 - Backend speichert rohe Version, Frontend trimmt bei Anzeige.
    """
    device = Device(
        device_id="FW_TEST",
        ip="192.168.1.50",
        name="Firmware Test Device",
        model="SoundTouch 30",
        mac_address="11:22:33:44:55:66",
        firmware_version="27.0.6.46330.5043500-release+hepdswbld04.2022",
    )
    
    # Insert
    result = await repo.upsert(device)
    assert result.firmware_version == "27.0.6.46330.5043500-release+hepdswbld04.2022"
    
    # Retrieve by device_id
    retrieved = await repo.get_by_device_id("FW_TEST")
    assert retrieved is not None
    assert retrieved.firmware_version == "27.0.6.46330.5043500-release+hepdswbld04.2022"
    
    # Retrieve via get_all
    all_devices = await repo.get_all()
    fw_device = next(d for d in all_devices if d.device_id == "FW_TEST")
    assert fw_device.firmware_version == "27.0.6.46330.5043500-release+hepdswbld04.2022"


@pytest.mark.asyncio
async def test_firmware_version_minimal_format(repo):
    """Test firmware version with only major.minor.patch format."""
    device = Device(
        device_id="FW_SIMPLE",
        ip="192.168.1.51",
        name="Simple FW Device",
        model="SoundTouch 10",
        mac_address="AA:AA:AA:AA:AA:AA",
        firmware_version="1.0.0",
    )
    
    result = await repo.upsert(device)
    assert result.firmware_version == "1.0.0"
    
    retrieved = await repo.get_by_device_id("FW_SIMPLE")
    assert retrieved.firmware_version == "1.0.0"


@pytest.mark.asyncio
async def test_device_get_all(repo):
    """Test get_all with multiple devices."""
    device1 = Device(
        device_id="DEV1",
        ip="192.168.1.100",
        name="Device 1",
        model="SoundTouch 10",
        mac_address="AA:BB:CC:DD:EE:FF",
        firmware_version="1.0.0",
    )
    
    device2 = Device(
        device_id="DEV2",
        ip="192.168.1.101",
        name="Device 2",
        model="SoundTouch 30",
        mac_address="11:22:33:44:55:66",
        firmware_version="2.0.0",
    )
    
    await repo.upsert(device1)
    await repo.upsert(device2)
    
    devices = await repo.get_all()
    
    assert len(devices) == 2
    assert all(isinstance(d, Device) for d in devices)


@pytest.mark.asyncio
async def test_device_get_by_device_id(repo):
    """Test get_by_device_id."""
    device = Device(
        device_id="TEST123",
        ip="192.168.1.100",
        name="Test Device",
        model="SoundTouch 10",
        mac_address="AA:BB:CC:DD:EE:FF",
        firmware_version="1.0.0",
    )
    
    await repo.upsert(device)
    
    found = await repo.get_by_device_id("TEST123")
    
    assert found is not None
    assert found.device_id == "TEST123"
    assert found.name == "Test Device"


@pytest.mark.asyncio
async def test_device_get_by_device_id_not_found(repo):
    """Test get_by_device_id with non-existent device."""
    found = await repo.get_by_device_id("NONEXISTENT")
    
    assert found is None


def test_device_to_dict():
    """Test Device.to_dict()."""
    device = Device(
        device_id="TEST123",
        ip="192.168.1.100",
        name="Test Device",
        model="SoundTouch 10",
        mac_address="AA:BB:CC:DD:EE:FF",
        firmware_version="1.0.0",
    )
    
    d = device.to_dict()
    
    assert d["device_id"] == "TEST123"
    assert d["ip"] == "192.168.1.100"
    assert d["name"] == "Test Device"
    assert d["model"] == "SoundTouch 10"


def test_device_schema_version_extraction():
    """Test schema version extraction from firmware version."""
    # Full firmware version
    device1 = Device(
        device_id="TEST1",
        ip="192.168.1.1",
        name="Test",
        model="SoundTouch 30",
        mac_address="AA:BB:CC:DD:EE:FF",
        firmware_version="28.0.3.46454 epdbuild.trunk.hepdswbld02.2023-07-27T14:58:40"
    )
    assert device1.schema_version == "28.0.3"
    
    # Short firmware version
    device2 = Device(
        device_id="TEST2",
        ip="192.168.1.2",
        name="Test",
        model="SoundTouch 10",
        mac_address="AA:BB:CC:DD:EE:FF",
        firmware_version="28.0.3"
    )
    assert device2.schema_version == "28.0.3"
    
    # Empty firmware
    device3 = Device(
        device_id="TEST3",
        ip="192.168.1.3",
        name="Test",
        model="SoundTouch 300",
        mac_address="AA:BB:CC:DD:EE:FF",
        firmware_version=""
    )
    assert device3.schema_version == "unknown"
    
    # Manual override
    device4 = Device(
        device_id="TEST4",
        ip="192.168.1.4",
        name="Test",
        model="SoundTouch 30",
        mac_address="AA:BB:CC:DD:EE:FF",
        firmware_version="28.0.3.46454",
        schema_version="custom.1.0"
    )
    assert device4.schema_version == "custom.1.0"


@pytest.mark.asyncio
async def test_device_schema_version_persisted(repo):
    """Test that schema_version is persisted in database."""
    device = Device(
        device_id="TEST_SCHEMA",
        ip="192.168.1.100",
        name="Test Device",
        model="SoundTouch 30",
        mac_address="AA:BB:CC:DD:EE:FF",
        firmware_version="28.0.3.46454 epdbuild.trunk"
    )
    
    # Should auto-extract schema version
    assert device.schema_version == "28.0.3"
    
    # Persist
    await repo.upsert(device)
    
    # Retrieve
    found = await repo.get_by_device_id("TEST_SCHEMA")
    assert found is not None
    assert found.schema_version == "28.0.3"
    assert found.firmware_version == "28.0.3.46454 epdbuild.trunk"
