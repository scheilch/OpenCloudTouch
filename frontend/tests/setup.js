import { expect, afterEach, beforeAll, vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'

// Mock fetch with base URL for API calls
beforeAll(() => {
  const originalFetch = global.fetch;
  global.fetch = vi.fn((url, options) => {
    const baseUrl = 'http://localhost:8000';
    const fullUrl = typeof url === 'string' && url.startsWith('/') 
      ? baseUrl + url 
      : url;
    
    // Return mock response by default
    return Promise.resolve({
      ok: true,
      status: 200,
      json: async () => ({}),
      text: async () => '',
    });
  });
});

// Cleanup after each test
afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})
