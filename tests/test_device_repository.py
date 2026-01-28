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
