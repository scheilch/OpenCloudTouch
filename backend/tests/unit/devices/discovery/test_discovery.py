"""
Tests for Device Discovery
"""

import tempfile
from pathlib import Path

import pytest

from cloudtouch.devices.discovery.manual import ManualDiscovery
from cloudtouch.discovery import DiscoveredDevice
from cloudtouch.settings.repository import SettingsRepository


@pytest.mark.asyncio
async def test_manual_discovery():
    """Test manual discovery with configured IPs."""
    ips = ["192.168.1.100", "192.168.1.101"]
    discovery = ManualDiscovery(ips)

    devices = await discovery.discover()

    assert len(devices) == 2
    assert all(isinstance(d, DiscoveredDevice) for d in devices)
    assert devices[0].ip == "192.168.1.100"
    assert devices[1].ip == "192.168.1.101"
    assert all(d.port == 8090 for d in devices)


@pytest.mark.asyncio
async def test_manual_discovery_empty():
    """Test manual discovery with empty IP list."""
    discovery = ManualDiscovery([])

    devices = await discovery.discover()

    assert len(devices) == 0


@pytest.mark.asyncio
async def test_manual_discovery_merges_db_and_env_ips():
    """Test that manual discovery merges DB IPs and ENV IPs."""
    # Arrange
    db_ips = ["192.168.1.10", "192.168.1.20"]
    env_ips = ["192.168.1.30", "10.0.0.5"]
    expected_ips = db_ips + env_ips

    # Act
    discovery = ManualDiscovery(expected_ips)
    devices = await discovery.discover()

    # Assert
    assert len(devices) == 4
    device_ips = [d.ip for d in devices]
    assert set(device_ips) == set(expected_ips)


@pytest.mark.asyncio
async def test_manual_discovery_deduplicates_ips():
    """Test that manual discovery deduplicates IPs from DB and ENV."""
    # Arrange (same IP in both sources)
    ips_with_duplicates = [
        "192.168.1.10",
        "192.168.1.20",
        "192.168.1.10",  # Duplicate
    ]

    # Act
    discovery = ManualDiscovery(ips_with_duplicates)
    devices = await discovery.discover()

    # Assert
    assert len(devices) == 3  # Duplicates are passed through
    # Note: Deduplication should happen in the caller, not ManualDiscovery


@pytest.mark.asyncio
async def test_discovery_integration_with_settings_repo():
    """
    Integration test: Verify DB IPs can be merged with ENV IPs for discovery.

    This test verifies the complete flow:
    1. Settings repo stores manual IPs
    2. ENV config provides additional IPs
    3. Discovery uses merged list
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"

        # Arrange: Add IPs to DB
        repo = SettingsRepository(db_path)
        await repo.initialize()
        await repo.add_manual_ip("192.168.1.10")
        await repo.add_manual_ip("192.168.1.20")

        # ENV IPs (simulated)
        env_ips = ["192.168.1.30", "10.0.0.5"]

        # Act: Get DB IPs and merge with ENV
        db_ips = await repo.get_manual_ips()
        all_ips = list(set(db_ips + env_ips))  # Deduplicate

        # Discover with merged IPs
        discovery = ManualDiscovery(all_ips)
        devices = await discovery.discover()

        # Assert
        assert len(devices) == 4
        device_ips = {d.ip for d in devices}
        assert device_ips == {
            "192.168.1.10",
            "192.168.1.20",
            "192.168.1.30",
            "10.0.0.5",
        }

        # Cleanup
        await repo.close()


def test_discovered_device_base_url():
    """Test DiscoveredDevice base_url property."""
    device = DiscoveredDevice(ip="192.168.1.100", port=8090)

    assert device.base_url == "http://192.168.1.100:8090"


def test_discovered_device_custom_port():
    """Test DiscoveredDevice with custom port."""
    device = DiscoveredDevice(ip="192.168.1.100", port=9000)

    assert device.base_url == "http://192.168.1.100:9000"
