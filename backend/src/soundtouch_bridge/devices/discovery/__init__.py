"""Device discovery implementations"""
from soundtouch_bridge.devices.discovery.ssdp import SSDPDiscovery
from soundtouch_bridge.devices.discovery.manual import ManualDiscovery

__all__ = ["SSDPDiscovery", "ManualDiscovery"]
