# Real Device Tests

⚠️ **REQUIRES ACTUAL BOSE SOUNDTOUCH HARDWARE**

These tests are **NOT** run in CI/CD or pre-commit hooks. They must be run **manually** when hardware is available.

## Purpose

Real device tests validate that:
- Discovery works against actual hardware
- API endpoints behave correctly with real devices
- Device capabilities are detected properly
- Network communication is stable
- Hardware-specific quirks are handled

## Prerequisites

Before running these tests, ensure:

1. ✅ **At least 1 Bose SoundTouch device** is available
2. ✅ Device(s) are **powered ON**
3. ✅ Device(s) are **connected to network**
4. ✅ Test machine has **network connectivity** to devices
5. ✅ **Update device IPs** in `test_discovery_real.py` if using manual discovery

## Running Real Device Tests

### All Real Tests (Recommended)
```bash
# From project root
.\scripts\run-real-tests.ps1
```

### Backend Real Tests Only
```bash
# Option 1: pytest directly
cd backend
pytest tests/real -v -m real_devices

# Option 2: via script
.\scripts\run-real-tests.ps1 -SkipFrontend $true -SkipE2E $true
```

### Frontend Real Tests Only
```bash
# Option 1: npm directly
cd frontend
npm run test:real

# Option 2: via script
.\scripts\run-real-tests.ps1 -SkipBackend $true -SkipE2E $true
```

### E2E Real Tests Only
```bash
# Option 1: Cypress headless
cd frontend
npm run test:e2e:real

# Option 2: Cypress GUI (for debugging)
npm run test:e2e:real:debug

# Option 3: via script
.\scripts\run-real-tests.ps1 -SkipBackend $true -SkipFrontend $true
```

## Test Configuration

### Backend (`pytest`)
- **Marker**: `@pytest.mark.real_devices`
- **Location**: `backend/tests/real/`
- **Excluded from**: `pytest` (default), `run-backend-tests.ps1`, `run-all-tests.ps1`
- **Included in**: `run-real-tests.ps1`

### Frontend (`vitest`)
- **Environment**: `CT_HAS_DEVICES=true`
- **Location**: `frontend/tests/real/`
- **Excluded from**: `vitest` (default), `run-frontend-tests.ps1`, `run-all-tests.ps1`
- **Included in**: `run-real-tests.ps1`, `npm run test:real`

### E2E (`Cypress`)
- **Environment**: `CT_MOCK_MODE=false`
- **Location**: `frontend/tests/real/`
- **Excluded from**: `cypress run` (default), `run-e2e-tests.ps1`
- **Included in**: `run-real-tests.ps1`, `npm run test:e2e:real`

## Updating Device IPs

If using manual discovery tests, update IPs in `test_discovery_real.py`:

```python
manual_ips = [
    "192.0.2.36",  # ST30 - UPDATE THIS!
    "192.0.2.32",  # ST10 - UPDATE THIS!
    "192.0.2.27",  # ST300 - UPDATE THIS!
]
```

## Expected Results

When hardware is available:
- ✅ Discovery finds at least 1 device
- ✅ Device info queries return valid data
- ✅ Device IPs are valid (not mock IPs like 192.168.1.100-102)
- ✅ Device IDs are real (not AABBCC112233, etc.)
- ✅ Capabilities match actual hardware

When hardware is NOT available:
- ❌ Tests will FAIL with "No devices found" errors
- ⚠️ This is **expected** - these tests require hardware!

## Troubleshooting

### No devices found
1. Check device power (device LED should be lit)
2. Check network connection (device WiFi indicator)
3. Verify test machine is on same network
4. Try manual ping: `ping <device-ip>`
5. Check firewall rules (allow UDP 1900 for SSDP)

### Discovery timeout
- SSDP can take 10-15 seconds
- Tests wait up to 15 seconds
- If still timing out, check network switches/routers

### Connection refused
- Device might be in standby mode
- Try waking device via Bose app first
- Check device /info endpoint manually: `curl http://<device-ip>:8090/info`

## CI/CD Exclusion

These tests are **excluded** from:
- ✅ `run-backend-tests.ps1` (via `-m "not real_devices"`)
- ✅ `run-frontend-tests.ps1` (via vitest exclude pattern)
- ✅ `run-e2e-tests.ps1` (via Cypress excludeSpecPattern)
- ✅ `run-all-tests.ps1` (calls above scripts)
- ✅ Pre-commit hooks (would use run-all-tests.ps1)
- ✅ GitHub Actions (would use run-all-tests.ps1)

Only `run-real-tests.ps1` explicitly includes these tests.
