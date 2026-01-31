#!/usr/bin/env python3
"""
Demo Script for Iteration 1.c - Capability Detection System

This script demonstrates Punkt 9.1 (MUST HAVE) from SCHEMA_DIFFERENCES.md:
- Device capability detection via /capabilities endpoint
- Graceful degradation for unsupported endpoints (404/401)
- UI feature flags based on device model
- Cross-model compatibility handling

Usage:
    # Mock mode (for CI/automated testing):
    python e2e/demo_capability_detection.py

    # With real device (optional):
    python e2e/demo_capability_detection.py --device-ip 192.168.1.100

Requirements:
    - pytest (for mock mode)
    - bosesoundtouchapi (for real device mode)
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from soundtouch_bridge.devices.capabilities import (
    DeviceCapabilities,
    get_device_capabilities,
    safe_api_call,
    get_feature_flags_for_ui
)


def print_section(title: str):
    """Print formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print('=' * 70)


def print_capabilities(caps: DeviceCapabilities):
    """Pretty-print device capabilities."""
    print(f"\n📱 Device: {caps.device_type} ({caps.device_id})")
    print(f"\n🎛️  Hardware Capabilities:")
    print(f"  • HDMI Control:        {'✅' if caps.has_hdmi_control else '❌'}")
    print(f"  • Bass Control:        {'✅' if caps.has_bass_control else '❌'}")
    print(f"  • Bluetooth:           {'✅' if caps.has_bluetooth else '❌'}")
    print(f"  • AUX Input:           {'✅' if caps.has_aux_input else '❌'}")
    print(f"  • Multi-Room (Zones):  {'✅' if caps.has_zone_support else '❌'}")
    print(f"  • Audio Level Control: {'✅' if caps.has_audio_product_level_control else '❌'}")
    print(f"  • Tone Controls:       {'✅' if caps.has_audio_product_tone_control else '❌'}")
    
    print(f"\n📻 Available Sources ({len(caps.supported_sources)}):")
    for source in sorted(caps.supported_sources):
        print(f"  • {source}")
    
    print(f"\n🔌 Supported Endpoints ({len(caps.supported_endpoints)}):")
    # Group endpoints by category
    hdmi_endpoints = [e for e in caps.supported_endpoints if 'hdmi' in e.lower() or 'cec' in e.lower()]
    audio_endpoints = [e for e in caps.supported_endpoints if 'bass' in e.lower() or 'audio' in e.lower() or 'tone' in e.lower()]
    network_endpoints = [e for e in caps.supported_endpoints if 'zone' in e.lower() or 'bluetooth' in e.lower()]
    
    if hdmi_endpoints:
        print(f"  HDMI/CEC: {', '.join(sorted(hdmi_endpoints))}")
    if audio_endpoints:
        print(f"  Audio:    {', '.join(sorted(audio_endpoints))}")
    if network_endpoints:
        print(f"  Network:  {', '.join(sorted(network_endpoints))}")


def print_feature_flags(flags: dict):
    """Pretty-print UI feature flags."""
    print(f"\n🎨 Frontend Feature Flags:")
    print(f"  Device Type:      {flags['device_type']}")
    print(f"  Is Soundbar:      {'✅ YES' if flags['is_soundbar'] else '❌ NO'}")
    
    print(f"\n  Features:")
    for feature, enabled in sorted(flags['features'].items()):
        print(f"    • {feature:25s} {'✅' if enabled else '❌'}")
    
    print(f"\n  Available Sources:")
    for source in sorted(flags['sources']):
        print(f"    • {source}")
    
    print(f"\n  Advanced Features:")
    for feature, enabled in sorted(flags['advanced'].items()):
        print(f"    • {feature:25s} {'✅' if enabled else '❌'}")


async def demo_mock_mode():
    """Demonstrate capability detection with mock data."""
    from unittest.mock import MagicMock
    from bosesoundtouchapi import SoundTouchClient
    from bosesoundtouchapi.models import Capabilities, Information, SourceList
    
    print_section("DEMO MODE: Mock Device Testing")
    
    # Test 1: SoundTouch 30 (wireless speaker, no HDMI)
    print("\n🧪 Test 1: SoundTouch 30 Series III (Wireless Speaker)")
    
    client_st30 = MagicMock(spec=SoundTouchClient)
    
    # Mock GetInformation()
    info_st30 = MagicMock(spec=Information)
    info_st30.DeviceId = "AABBCC112233"
    info_st30.DeviceType = "SoundTouch 30 Series III"
    client_st30.GetInformation.return_value = info_st30
    
    # Mock GetCapabilities()
    caps_st30 = MagicMock(spec=Capabilities)
    caps_st30.IsProductCECHDMIControlCapable = False
    caps_st30.IsBassCapable = True
    caps_st30.IsAudioProductLevelControlCapable = False
    caps_st30.IsAudioProductToneControlsCapable = False
    caps_st30.SupportedUrls = [
        MagicMock(Url="/info"),
        MagicMock(Url="/nowPlaying"),
        MagicMock(Url="/volume"),
        MagicMock(Url="/bass"),
        MagicMock(Url="/getZone"),
        MagicMock(Url="/bluetoothInfo"),
    ]
    client_st30.GetCapabilities.return_value = caps_st30
    
    # Mock GetSourceList()
    sources_st30 = MagicMock(spec=SourceList)
    sources_st30.Sources = [
        MagicMock(Source="BLUETOOTH", Status="READY"),
        MagicMock(Source="AUX", Status="READY"),
        MagicMock(Source="INTERNET_RADIO", Status="READY"),
        MagicMock(Source="SPOTIFY", Status="UNAVAILABLE"),
    ]
    client_st30.GetSourceList.return_value = sources_st30
    
    # Get capabilities
    capabilities_st30 = await get_device_capabilities(client_st30)
    print_capabilities(capabilities_st30)
    
    # Get UI feature flags
    flags_st30 = get_feature_flags_for_ui(capabilities_st30)
    print_feature_flags(flags_st30)
    
    # Validate expectations
    assert not capabilities_st30.has_hdmi_control, "ST30 should NOT have HDMI"
    assert capabilities_st30.has_bass_control, "ST30 should have bass control"
    assert "BLUETOOTH" in capabilities_st30.supported_sources
    assert "SPOTIFY" not in capabilities_st30.supported_sources  # Not READY
    print("\n✅ ST30 validation passed!")
    
    # Test 2: SoundTouch 300 (soundbar with HDMI)
    print("\n\n🧪 Test 2: SoundTouch 300 (Soundbar with HDMI)")
    
    client_st300 = MagicMock(spec=SoundTouchClient)
    
    # Mock GetInformation()
    info_st300 = MagicMock(spec=Information)
    info_st300.DeviceId = "AABBCC112244"
    info_st300.DeviceType = "SoundTouch 300"
    client_st300.GetInformation.return_value = info_st300
    
    # Mock GetCapabilities()
    caps_st300 = MagicMock(spec=Capabilities)
    caps_st300.IsProductCECHDMIControlCapable = True
    caps_st300.IsBassCapable = True
    caps_st300.IsAudioProductLevelControlCapable = True
    caps_st300.IsAudioProductToneControlsCapable = True
    caps_st300.SupportedUrls = [
        MagicMock(Url="/info"),
        MagicMock(Url="/nowPlaying"),
        MagicMock(Url="/volume"),
        MagicMock(Url="/bass"),
        MagicMock(Url="/getZone"),
        MagicMock(Url="/bluetoothInfo"),
        MagicMock(Url="/productcechdmicontrol"),
        MagicMock(Url="/audioproductlevelcontrols"),
        MagicMock(Url="/audioproducttonecontrols"),
    ]
    client_st300.GetCapabilities.return_value = caps_st300
    
    # Mock GetSourceList()
    sources_st300 = MagicMock(spec=SourceList)
    sources_st300.Sources = [
        MagicMock(Source="PRODUCT", SourceAccount="TV", Status="READY"),
        MagicMock(Source="BLUETOOTH", Status="READY"),
        MagicMock(Source="INTERNET_RADIO", Status="READY"),
    ]
    client_st300.GetSourceList.return_value = sources_st300
    
    # Get capabilities
    capabilities_st300 = await get_device_capabilities(client_st300)
    print_capabilities(capabilities_st300)
    
    # Get UI feature flags
    flags_st300 = get_feature_flags_for_ui(capabilities_st300)
    print_feature_flags(flags_st300)
    
    # Validate expectations
    assert capabilities_st300.has_hdmi_control, "ST300 should have HDMI"
    assert capabilities_st300.has_audio_product_level_control, "ST300 should have level controls"
    assert "PRODUCT" in capabilities_st300.supported_sources  # HDMI input
    print("\n✅ ST300 validation passed!")
    
    print_section("SUMMARY")
    print("\n✅ All mock tests passed successfully!")
    print("\nDemonstrated features:")
    print("  • Device capability detection via /capabilities")
    print("  • Source filtering (only READY sources)")
    print("  • UI feature flags generation")
    print("  • Model-specific endpoint support (HDMI only on ST300)")
    print("  • Graceful handling of different device types")


async def demo_real_device(device_ip: str):
    """Demonstrate capability detection with real device."""
    from bosesoundtouchapi import SoundTouchClient
    
    print_section(f"REAL DEVICE MODE: {device_ip}")
    
    try:
        # Connect to device
        print(f"\n🔌 Connecting to device at {device_ip}...")
        client = SoundTouchClient(device_ip)
        
        # Get capabilities
        print("📡 Querying device capabilities...")
        capabilities = await get_device_capabilities(client)
        print_capabilities(capabilities)
        
        # Get UI feature flags
        flags = get_feature_flags_for_ui(capabilities)
        print_feature_flags(flags)
        
        # Test safe_api_call with potentially unsupported endpoint
        print("\n\n🧪 Testing graceful degradation (HDMI endpoint)...")
        from bosesoundtouchapi.uri import SoundTouchNodes
        
        hdmi_result = await safe_api_call(
            client, 
            SoundTouchNodes.productcechdmicontrol, 
            "HDMI Control"
        )
        
        if hdmi_result is None:
            print("  ⚠️  HDMI Control endpoint not supported (404/401) - gracefully handled")
        else:
            print(f"  ✅ HDMI Control endpoint supported: {hdmi_result}")
        
        print_section("REAL DEVICE TEST COMPLETE")
        print("\n✅ Successfully tested capability detection with real device!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. Device is powered on")
        print("  2. Device is on the same network")
        print("  3. IP address is correct")
        return 1
    
    return 0


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Demo script for Capability Detection (Iteration 1.c, Punkt 9.1)"
    )
    parser.add_argument(
        "--device-ip",
        type=str,
        help="IP address of real SoundTouch device (optional, uses mock mode if not provided)"
    )
    args = parser.parse_args()
    
    try:
        if args.device_ip:
            return await demo_real_device(args.device_ip)
        else:
            await demo_mock_mode()
            return 0
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
