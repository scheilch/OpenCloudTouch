"""Device discovery implementations"""

from cloudtouch.devices.discovery.manual import ManualDiscovery
from cloudtouch.devices.discovery.ssdp import SSDPDiscovery

__all__ = ["SSDPDiscovery", "ManualDiscovery"]
