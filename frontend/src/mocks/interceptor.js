/**
 * Development Mode API Interceptor
 * Mocks backend API calls when VITE_MOCK_MODE=true
 * 
 * Usage in development:
 * - Set VITE_MOCK_MODE=true in .env.local
 * - Run `npm run dev`
 * - All API calls will be intercepted with mock data
 */

import { mockDevices, mockManualIps, mockSyncSuccess, mockHealth } from './mockData';

// In-memory state for development mode (with localStorage persistence)
let devMockState = loadMockState();

/**
 * Setup fetch interceptor for development mode
 * Intercepts all /api/* calls and returns mock responses
 */
export function setupMockInterceptor() {
  const originalFetch = window.fetch;

  window.fetch = async function (url, options = {}) {
    const urlStr = url.toString();
    const method = options.method || 'GET';

    // Only intercept /api/* calls
    if (!urlStr.includes('/api/')) {
      return originalFetch(url, options);
    }

    console.log(`[MOCK] ${method} ${urlStr}`, options.body ? JSON.parse(options.body) : '');

    // Simulate network delay (50-150ms)
    await new Promise((resolve) => setTimeout(resolve, 50 + Math.random() * 100));

    // Health endpoint
    if (urlStr.includes('/health')) {
      return createMockResponse(mockHealth);
    }

    // GET /api/devices
    if (method === 'GET' && urlStr.includes('/api/devices') && !urlStr.includes('discover')) {
      return createMockResponse({
        count: devMockState.devices.length,
        devices: devMockState.devices,
      });
    }

    // GET /api/devices/discover
    if (method === 'GET' && urlStr.includes('/api/devices/discover')) {
      // Return mock devices + manual IPs
      const allDevices = [
        ...mockDevices,
        ...devMockState.manualIps.map((ip, idx) => ({
          id: 100 + idx,
          device_id: `MANUAL_${ip.replace(/\./g, '_')}`,
          name: `Manual Device (${ip})`,
          type: 'SoundTouch 10',
          mac_address: `00:00:00:00:00:${idx.toString().padStart(2, '0')}`,
          ip_address: ip,
          firmware_version: '1.0.0-manual',
          image_url: `data:image/svg+xml;base64,${btoa(`<svg width="500" height="500" xmlns="http://www.w3.org/2000/svg"><rect width="500" height="500" fill="#999"/><text x="50%" y="50%" font-family="Arial,sans-serif" font-size="20" fill="white" text-anchor="middle" dominant-baseline="middle">${ip}</text></svg>`)}`,
        })),
      ];

      return createMockResponse({
        count: allDevices.length,
        devices: allDevices,
      });
    }

    // POST /api/devices/sync
    if (method === 'POST' && urlStr.includes('/api/devices/sync')) {
      if (devMockState.discoveryInProgress) {
        return createMockResponse(
          { detail: 'Discovery already in progress' },
          409
        );
      }

      // Simulate discovery - but add devices IMMEDIATELY to state
      const allDevices = [
        ...mockDevices,
        ...devMockState.manualIps.map((ip, idx) => ({
          id: 100 + idx,
          device_id: `MANUAL_${ip.replace(/\./g, '_')}`,
          name: `Manual Device (${ip})`,
          type: 'SoundTouch 10',
          mac_address: `00:00:00:00:00:${idx.toString().padStart(2, '0')}`,
          ip_address: ip,
          firmware_version: '1.0.0-manual',
          image_url: `data:image/svg+xml;base64,${btoa(`<svg width="500" height="500" xmlns="http://www.w3.org/2000/svg"><rect width="500" height="500" fill="#999"/><text x="50%" y="50%" font-family="Arial,sans-serif" font-size="20" fill="white" text-anchor="middle" dominant-baseline="middle">${ip}</text></svg>`)}`,
        })),
      ];

      // IMPORTANT: Set devices BEFORE returning response!
      devMockState.devices = allDevices;
      saveMockState();

      return createMockResponse({
        ...mockSyncSuccess,
        discovered: allDevices.length,
        synced: allDevices.length,
      });
    }

    // GET /api/settings/manual-ips
    if (method === 'GET' && urlStr.includes('/api/settings/manual-ips')) {
      return createMockResponse({
        ips: devMockState.manualIps,
      });
    }

    // POST /api/settings/manual-ips/add
    if (method === 'POST' && urlStr.includes('/api/settings/manual-ips/add')) {
      const body = JSON.parse(options.body || '{}');
      const { ip } = body;

      if (!ip) {
        return createMockResponse({ detail: 'IP address required' }, 400);
      }

      if (devMockState.manualIps.includes(ip)) {
        return createMockResponse({ detail: 'IP already exists' }, 409);
      }

      devMockState.manualIps.push(ip);
      saveMockState();
      return createMockResponse({ message: 'IP added', ip });
    }

    // POST /api/settings/manual-ips (bulk add - expects {ips: [...]})
    if (method === 'POST' && urlStr.endsWith('/api/settings/manual-ips')) {
      const body = JSON.parse(options.body || '{}');
      const { ips } = body;

      if (!ips || !Array.isArray(ips)) {
        return createMockResponse({ detail: 'IPs array required' }, 400);
      }

      // Add all new IPs
      const newIps = ips.filter(ip => !devMockState.manualIps.includes(ip));
      devMockState.manualIps.push(...newIps);
      saveMockState();
      
      return createMockResponse({ 
        message: `${newIps.length} IPs added`, 
        ips: devMockState.manualIps 
      });
    }

    // DELETE /api/settings/manual-ips/:ip
    if (method === 'DELETE' && urlStr.includes('/api/settings/manual-ips/')) {
      const ip = urlStr.split('/').pop();
      const index = devMockState.manualIps.indexOf(ip);

      if (index === -1) {
        return createMockResponse({ detail: 'IP not found' }, 404);
      }

      devMockState.manualIps.splice(index, 1);
      saveMockState();
      return createMockResponse({ message: 'IP removed', ip });
    }

    // Fallback: Return 404 for unknown endpoints
    console.warn(`[MOCK] Unhandled endpoint: ${method} ${urlStr}`);
    return createMockResponse({ detail: 'Endpoint not mocked' }, 404);
  };

  console.log('%c🎭 Mock Interceptor Ready', 'background: #4CAF50; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold');
  console.log('%c📡 Intercepting: /api/*', 'color: #4CAF50');
  console.log('%c💡 Tip: Use localStorage.removeItem("ct-mock-state") to reset', 'color: #999');
  console.log('%c🔍 Debug: JSON.parse(localStorage.getItem("ct-mock-state"))', 'color: #999');
}

/**
 * Helper to create mock Response objects
 */
function createMockResponse(data, status = 200) {
  return Promise.resolve(
    new Response(JSON.stringify(data), {
      status,
      statusText: status === 200 ? 'OK' : 'Error',
      headers: {
        'Content-Type': 'application/json',
      },
    })
  );
}

/**
 * Reset mock state (useful for testing)
 */
export function resetMockState() {
  devMockState = {
    devices: [],
    manualIps: [],
    discoveryInProgress: false,
  };
  saveMockState();
}

/**
 * Load mock state from localStorage
 */
function loadMockState() {
  try {
    const saved = localStorage.getItem('ct-mock-state');
    if (saved) {
      const state = JSON.parse(saved);
      console.log('%c💾 Loaded state from localStorage', 'color: #2196F3', state);
      return state;
    }
  } catch (e) {
    console.warn('[MOCK] Failed to load state from localStorage', e);
  }

  // Default state
  return {
    devices: [],
    manualIps: [],
    discoveryInProgress: false,
  };
}

/**
 * Save mock state to localStorage
 */
function saveMockState() {
  try {
    localStorage.setItem('ct-mock-state', JSON.stringify(devMockState));
  } catch (e) {
    console.warn('[MOCK] Failed to save state to localStorage', e);
  }
}
