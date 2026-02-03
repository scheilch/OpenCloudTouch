/**
 * Device Image Utilities
 * Maps SoundTouch device models to their corresponding product images
 */

// Model name mapping (case-insensitive, flexible matching)
// NOTE: ST300 must be checked BEFORE ST30 to avoid false matches
const MODEL_PATTERNS = {
  st300: /soundtouch\s*300|st\s*300/i,  // Check ST300 first!
  st10: /soundtouch\s*10|st\s*10/i,
  st20: /soundtouch\s*20|st\s*20/i,
  st30: /soundtouch\s*30|st\s*30/i,
};

/**
 * Get device image path based on device type/model
 * @param {string} deviceType - Device type string (e.g., "SoundTouch 10", "ST30")
 * @returns {string} Path to device image SVG
 */
export function getDeviceImage(deviceType) {
  if (!deviceType) {
    return '/images/devices/default.svg';
  }

  const normalizedType = deviceType.trim();

  // Check each pattern
  for (const [model, pattern] of Object.entries(MODEL_PATTERNS)) {
    if (pattern.test(normalizedType)) {
      return `/images/devices/${model}.svg`;
    }
  }

  // Default fallback for unknown models
  return '/images/devices/default.svg';
}

/**
 * Get all available device images
 * @returns {Object} Map of model names to image paths
 */
export function getAllDeviceImages() {
  return {
    st10: '/images/devices/st10.svg',
    st20: '/images/devices/st20.svg',
    st30: '/images/devices/st30.svg',
    st300: '/images/devices/st300.svg',
    default: '/images/devices/default.svg',
  };
}

/**
 * Preload device images for better performance
 * Call this on app initialization to cache device images
 */
export function preloadDeviceImages() {
  const images = getAllDeviceImages();
  Object.values(images).forEach((path) => {
    const img = new Image();
    img.src = path;
  });
}

/**
 * Get device model display name from type string
 * @param {string} deviceType - Raw device type string
 * @returns {string} Formatted display name
 */
export function getDeviceDisplayName(deviceType) {
  if (!deviceType) return 'Unknown Device';

  // Extract model number if present
  for (const [model, pattern] of Object.entries(MODEL_PATTERNS)) {
    if (pattern.test(deviceType)) {
      const modelNumber = model.toUpperCase().replace('ST', '');
      return `SoundTouch ${modelNumber}`;
    }
  }

  return deviceType;
}

/**
 * Get device aspect ratio class for responsive layouts
 * @param {string} deviceType - Device type string
 * @returns {string} CSS class name for aspect ratio
 */
export function getDeviceAspectRatio(deviceType) {
  const normalizedType = deviceType?.trim() || '';

  // NOTE: Check ST300 BEFORE ST30 to avoid false matches
  if (MODEL_PATTERNS.st300.test(normalizedType)) return 'aspect-[4/1]'; // 4:1
  if (MODEL_PATTERNS.st10.test(normalizedType)) return 'aspect-square'; // 1:1
  if (MODEL_PATTERNS.st20.test(normalizedType)) return 'aspect-[3/2]'; // 3:2
  if (MODEL_PATTERNS.st30.test(normalizedType)) return 'aspect-[14/9]'; // 14:9

  return 'aspect-square'; // Default
}

export default {
  getDeviceImage,
  getAllDeviceImages,
  preloadDeviceImages,
  getDeviceDisplayName,
  getDeviceAspectRatio,
};
