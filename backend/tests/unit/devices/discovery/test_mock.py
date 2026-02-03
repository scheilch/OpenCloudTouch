"""
Tests for MockDiscoveryAdapter.
"""

import pytest

from cloudtouch.devices.discovery.mock import MockDiscoveryAdapter
from cloudtouch.discovery import DiscoveredDevice


class TestMockDiscoveryAdapter:
    """Tests for mock discovery adapter."""

    @pytest.mark.asyncio
    async def test_returns_predefined_devices(self):
        """Test that mock adapter returns 3 predefined devices."""
        adapter = MockDiscoveryAdapter()
        
        devices = await adapter.discover()
        
        assert len(devices) == 3
        assert isinstance(devices, list)
        assert all(isinstance(d, DiscoveredDevice) for d in devices)
        
        # Check that all 3 MAC addresses are present
        mac_addresses = {d.mac_address for d in devices}
        assert mac_addresses == {"AABBCC112233", "DDEEFF445566", "112233445566"}

    @pytest.mark.asyncio
    async def test_device_structure(self):
        """Test that devices have correct structure."""
        adapter = MockDiscoveryAdapter()
        
        devices = await adapter.discover()
        
        # Find Living Room device
        living_room = next(d for d in devices if d.mac_address == "AABBCC112233")
        
        assert living_room.ip == "192.168.1.100"
        assert living_room.port == 8090
        assert living_room.mac_address == "AABBCC112233"
        assert living_room.name == "Living Room"
        assert living_room.model == "SoundTouch 20"
        assert living_room.firmware_version == "28.0.12.46499"
        assert living_room.base_url == "http://192.168.1.100:8090"

    @pytest.mark.asyncio
    async def test_all_devices_have_required_fields(self):
        """Test that all mock devices have required fields."""
        adapter = MockDiscoveryAdapter()
        
        devices = await adapter.discover()
        
        for device in devices:
            assert device.ip is not None
            assert device.port == 8090
            assert device.mac_address is not None
            assert device.name is not None
            assert device.model is not None
            assert device.firmware_version is not None

    @pytest.mark.asyncio
    async def test_timeout_parameter_accepted(self):
        """Test that timeout parameter is accepted (for interface compatibility)."""
        adapter = MockDiscoveryAdapter(timeout=5)
        
        devices = await adapter.discover()
        assert len(devices) == 3  # Should work regardless of timeout
