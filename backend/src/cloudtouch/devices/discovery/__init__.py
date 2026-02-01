"""Device discovery implementations"""

from cloudtouch.devices.discovery.ssdp import SSDPDiscovery
from cloudtouch.devices.discovery.manual import ManualDiscovery

__all__ = ["SSDPDiscovery", "ManualDiscovery"]
