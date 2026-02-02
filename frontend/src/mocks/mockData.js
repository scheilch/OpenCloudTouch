/**
 * Mock Data for Development Mode
 * Same data structure as backend API responses
 */

// Simple SVG data URL for device placeholder images
const createDevicePlaceholder = (color, text) => {
  const svg = `<svg width="500" height="500" xmlns="http://www.w3.org/2000/svg">
    <rect width="500" height="500" fill="${color}"/>
    <text x="50%" y="50%" font-family="Arial,sans-serif" font-size="24" fill="white" text-anchor="middle" dominant-baseline="middle">${text}</text>
  </svg>`;
  return `data:image/svg+xml;base64,${btoa(svg)}`;
};

export const mockDevices = [
  {
    id: 1,
    device_id: "MOCK_AABBCC112233",
    name: "Living Room (Mock ST10)",
    type: "SoundTouch 10",
    mac_address: "AA:BB:CC:11:22:33",
    ip_address: "192.168.1.101",
    firmware_version: "1.0.0-mock",
    image_url: createDevicePlaceholder("#0066CC", "ST10"),
  },
  {
    id: 2,
    device_id: "MOCK_DDEEFF445566",
    name: "Schlafzimmer (Mock ST30)",
    type: "SoundTouch 30 Series III",
    mac_address: "DD:EE:FF:44:55:66",
    ip_address: "192.168.1.102",
    firmware_version: "1.0.0-mock",
    image_url: createDevicePlaceholder("#00AA66", "ST30"),
  },
  {
    id: 3,
    device_id: "MOCK_112233445566",
    name: "Küche (Mock ST300)",
    type: "SoundTouch 300",
    mac_address: "11:22:33:44:55:66",
    ip_address: "192.168.1.103",
    firmware_version: "1.0.0-mock",
    image_url: createDevicePlaceholder("#CC6600", "ST300"),
  },
];

export const mockManualIps = [];

export const mockSyncSuccess = {
  message: "Devices synchronized successfully",
  discovered: 3,
  synced: 3,
  failed: 0,
};

export const mockSyncNoDevices = {
  message: "No devices found",
  discovered: 0,
  synced: 0,
  failed: 0,
};

export const mockHealth = {
  status: "ok",
  version: "1.0.0-mock",
  mode: "development-mock",
};
