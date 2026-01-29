# SoundTouch API 3-Way Comparison

**Date**: 2026-01-29

**Sources**:
1. **Official Bose Docs**: `2025.12.18 SoundTouch Web API.pdf`
2. **Collected Schemas**: 37 endpoints from 3 devices (ST30, ST10, ST300)
3. **Python Library**: bosesoundtouchapi 1.0.86 (SoundTouchNodes)

---

## Summary

| Category | Count |
|----------|-------|
| **Total Unique Endpoints** | 78 |
| In all 3 sources | 12 |
| Only in Official Docs | 2 |
| Only in Collected Schemas | 2 |
| Only in Python Library | 33 |
| Missing from Official Docs | 58 |

## Detailed Endpoint Comparison

| Endpoint | Official | Schemas | Library | Notes |
|----------|----------|---------|---------|-------|
| `/DSPMonoStereo` | ❌ | ✅ | ✅ | Missing from official docs |
| `/addMusicServiceAccount` | ❌ | ❌ | ✅ | Missing from official docs |
| `/addStereoPair` | ❌ | ❌ | ✅ | Missing from official docs |
| `/addWirelessProfile` | ❌ | ❌ | ✅ | Missing from official docs |
| `/addZoneSlave` | ✅ | ❌ | ✅ |  |
| `/artistAndPlaylistInfo` | ❌ | ❌ | ✅ | Missing from official docs |
| `/audiodspcontrol` | ✅ | ❌ | ❌ |  |
| `/audiodspcontrols` | ✅ | ✅ | ✅ | Device-specific: ST300, ST30, ST10 |
| `/audioproductlevelcontrols` | ✅ | ✅ | ✅ | Device-specific: ST300, ST30, ST10 |
| `/audioproducttonecontrols` | ✅ | ✅ | ✅ | Device-specific: ST300, ST30, ST10 |
| `/audiospeakerattributeandsetting` | ❌ | ❌ | ✅ | Missing from official docs |
| `/balance` | ❌ | ✅ | ✅ | Missing from official docs |
| `/bass` | ✅ | ✅ | ✅ |  |
| `/bassCapabilities` | ✅ | ✅ | ✅ |  |
| `/bluetoothInfo` | ❌ | ✅ | ✅ | Missing from official docs |
| `/capabilities` | ✅ | ✅ | ✅ |  |
| `/clearBluetoothPaired` | ❌ | ❌ | ✅ | Missing from official docs |
| `/clockConfig` | ❌ | ❌ | ✅ | Missing from official docs |
| `/clockDisplay` | ❌ | ❌ | ✅ | Missing from official docs |
| `/clockTime` | ❌ | ✅ | ✅ | Missing from official docs |
| `/createZone` | ❌ | ❌ | ✅ | Missing from official docs |
| `/enterBluetoothPairing` | ❌ | ❌ | ✅ | Missing from official docs |
| `/getActiveWirelessProfile` | ❌ | ✅ | ✅ | Missing from official docs |
| `/getBCOReset` | ❌ | ❌ | ✅ | Missing from official docs |
| `/getGroup` | ❌ | ✅ | ✅ | Device-specific: ST300, ST30, ST10; Missing from official docs |
| `/getZone` | ✅ | ✅ | ✅ |  |
| `/info` | ✅ | ✅ | ✅ |  |
| `/introspect` | ❌ | ❌ | ✅ | Missing from official docs |
| `/key` | ✅ | ✅ | ✅ |  |
| `/language` | ❌ | ✅ | ✅ | Missing from official docs |
| `/listMediaServers` | ❌ | ✅ | ✅ | Missing from official docs |
| `/marge` | ❌ | ✅ | ❌ | Missing from official docs |
| `/name` | ✅ | ✅ | ✅ |  |
| `/navigate` | ❌ | ❌ | ✅ | Missing from official docs |
| `/netStats` | ❌ | ✅ | ✅ | Missing from official docs |
| `/networkInfo` | ❌ | ✅ | ✅ | Missing from official docs |
| `/now` | ✅ | ❌ | ❌ |  |
| `/nowPlaying` | ❌ | ❌ | ✅ | Missing from official docs |
| `/now_playing` | ❌ | ✅ | ❌ | Missing from official docs |
| `/powerManagement` | ❌ | ✅ | ✅ | Missing from official docs |
| `/powersaving` | ❌ | ✅ | ✅ | Missing from official docs |
| `/presets` | ✅ | ❌ | ✅ |  |
| `/productcechdmicontrol` | ❌ | ✅ | ✅ | Device-specific: ST300, ST30, ST10; Missing from official docs |
| `/producthdmiassignmentcontrols` | ❌ | ✅ | ✅ | Device-specific: ST300, ST30, ST10; Missing from official docs |
| `/rebroadcastlatencymode` | ❌ | ✅ | ✅ | Missing from official docs |
| `/recents` | ❌ | ✅ | ✅ | Missing from official docs |
| `/removeGroup` | ❌ | ❌ | ✅ | Missing from official docs |
| `/removeMusicServiceAccount` | ❌ | ❌ | ✅ | Missing from official docs |
| `/removePreset` | ❌ | ❌ | ✅ | Missing from official docs |
| `/removeStation` | ❌ | ❌ | ✅ | Missing from official docs |
| `/removeStereoPair` | ❌ | ❌ | ✅ | Missing from official docs |
| `/removeZoneSlave` | ✅ | ❌ | ✅ |  |
| `/requestToken` | ❌ | ✅ | ✅ | Missing from official docs |
| `/search` | ❌ | ❌ | ✅ | Missing from official docs |
| `/searchStation` | ❌ | ❌ | ✅ | Missing from official docs |
| `/select` | ✅ | ❌ | ✅ |  |
| `/serviceAvailability` | ❌ | ✅ | ✅ | Missing from official docs |
| `/setMargeAccount` | ❌ | ❌ | ✅ | Missing from official docs |
| `/setZone` | ✅ | ❌ | ✅ |  |
| `/simpleSetup` | ❌ | ❌ | ✅ | Missing from official docs |
| `/soundTouchConfigurationStatus` | ❌ | ✅ | ✅ | Missing from official docs |
| `/sources` | ✅ | ✅ | ✅ |  |
| `/speaker` | ❌ | ✅ | ✅ | Missing from official docs |
| `/supportedURLs` | ❌ | ✅ | ✅ | Missing from official docs |
| `/swUpdateAbort` | ❌ | ❌ | ✅ | Missing from official docs |
| `/swUpdateCheck` | ❌ | ❌ | ✅ | Missing from official docs |
| `/swUpdateQuery` | ❌ | ❌ | ✅ | Missing from official docs |
| `/swUpdateStart` | ❌ | ❌ | ✅ | Missing from official docs |
| `/systemtimeout` | ❌ | ✅ | ✅ | Missing from official docs |
| `/systemtimeoutcontrol` | ❌ | ✅ | ✅ | Device-specific: ST300, ST30, ST10; Missing from official docs |
| `/test` | ❌ | ❌ | ✅ | Missing from official docs |
| `/trackInfo` | ✅ | ❌ | ✅ |  |
| `/userActivity` | ❌ | ❌ | ✅ | Missing from official docs |
| `/userRating` | ❌ | ❌ | ✅ | Missing from official docs |
| `/userTrackControl` | ❌ | ❌ | ✅ | Missing from official docs |
| `/volume` | ✅ | ✅ | ✅ | Device-specific: ST300, ST30, ST10 |
| `/volumeUpdated` | ❌ | ❌ | ✅ | Missing from official docs |
| `/wirelessProfile` | ❌ | ❌ | ✅ | Missing from official docs |

## Gaps and Potential Issues

### 1. Endpoints Missing from Official Documentation

**58 endpoints** found in schemas/library but not in official docs:

- `/DSPMonoStereo` - Found in: ✅ Schemas + ✅ Library
- `/addMusicServiceAccount` - Found in: ✅ Library
- `/addStereoPair` - Found in: ✅ Library
- `/addWirelessProfile` - Found in: ✅ Library
- `/artistAndPlaylistInfo` - Found in: ✅ Library
- `/audiospeakerattributeandsetting` - Found in: ✅ Library
- `/balance` - Found in: ✅ Schemas + ✅ Library
- `/bluetoothInfo` - Found in: ✅ Schemas + ✅ Library
- `/clearBluetoothPaired` - Found in: ✅ Library
- `/clockConfig` - Found in: ✅ Library
- `/clockDisplay` - Found in: ✅ Library
- `/clockTime` - Found in: ✅ Schemas + ✅ Library
- `/createZone` - Found in: ✅ Library
- `/enterBluetoothPairing` - Found in: ✅ Library
- `/getActiveWirelessProfile` - Found in: ✅ Schemas + ✅ Library
- `/getBCOReset` - Found in: ✅ Library
- `/getGroup` - Found in: ✅ Schemas + ✅ Library
- `/introspect` - Found in: ✅ Library
- `/language` - Found in: ✅ Schemas + ✅ Library
- `/listMediaServers` - Found in: ✅ Schemas + ✅ Library
- `/marge` - Found in: ✅ Schemas
- `/navigate` - Found in: ✅ Library
- `/netStats` - Found in: ✅ Schemas + ✅ Library
- `/networkInfo` - Found in: ✅ Schemas + ✅ Library
- `/nowPlaying` - Found in: ✅ Library
- `/now_playing` - Found in: ✅ Schemas
- `/powerManagement` - Found in: ✅ Schemas + ✅ Library
- `/powersaving` - Found in: ✅ Schemas + ✅ Library
- `/productcechdmicontrol` - Found in: ✅ Schemas + ✅ Library
- `/producthdmiassignmentcontrols` - Found in: ✅ Schemas + ✅ Library
- `/rebroadcastlatencymode` - Found in: ✅ Schemas + ✅ Library
- `/recents` - Found in: ✅ Schemas + ✅ Library
- `/removeGroup` - Found in: ✅ Library
- `/removeMusicServiceAccount` - Found in: ✅ Library
- `/removePreset` - Found in: ✅ Library
- `/removeStation` - Found in: ✅ Library
- `/removeStereoPair` - Found in: ✅ Library
- `/requestToken` - Found in: ✅ Schemas + ✅ Library
- `/search` - Found in: ✅ Library
- `/searchStation` - Found in: ✅ Library
- `/serviceAvailability` - Found in: ✅ Schemas + ✅ Library
- `/setMargeAccount` - Found in: ✅ Library
- `/simpleSetup` - Found in: ✅ Library
- `/soundTouchConfigurationStatus` - Found in: ✅ Schemas + ✅ Library
- `/speaker` - Found in: ✅ Schemas + ✅ Library
- `/supportedURLs` - Found in: ✅ Schemas + ✅ Library
- `/swUpdateAbort` - Found in: ✅ Library
- `/swUpdateCheck` - Found in: ✅ Library
- `/swUpdateQuery` - Found in: ✅ Library
- `/swUpdateStart` - Found in: ✅ Library
- `/systemtimeout` - Found in: ✅ Schemas + ✅ Library
- `/systemtimeoutcontrol` - Found in: ✅ Schemas + ✅ Library
- `/test` - Found in: ✅ Library
- `/userActivity` - Found in: ✅ Library
- `/userRating` - Found in: ✅ Library
- `/userTrackControl` - Found in: ✅ Library
- `/volumeUpdated` - Found in: ✅ Library
- `/wirelessProfile` - Found in: ✅ Library

### 2. Endpoints Only in Official Documentation

**2 endpoints** documented but not found in practice:

- `/audiodspcontrol` - ...
- `/now` - ...

### 3. Device-Specific Endpoints

**8 endpoints** only available on specific models:

- `/audiodspcontrols` - Only on: ST300, ST30, ST10
- `/audioproductlevelcontrols` - Only on: ST300, ST30, ST10
- `/audioproducttonecontrols` - Only on: ST300, ST30, ST10
- `/getGroup` - Only on: ST300, ST30, ST10
- `/productcechdmicontrol` - Only on: ST300, ST30, ST10
- `/producthdmiassignmentcontrols` - Only on: ST300, ST30, ST10
- `/systemtimeoutcontrol` - Only on: ST300, ST30, ST10
- `/volume` - Only on: ST300, ST30, ST10
