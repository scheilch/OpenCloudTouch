import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import App from '../src/App'

// Mock fetch globally
global.fetch = vi.fn()

describe('App Component', () => {
  beforeEach(() => {
    fetch.mockClear()
  })

  it('shows empty state when no devices found', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ devices: [] })
    })

    render(<App />)

    await waitFor(() => {
      expect(screen.getByText(/Willkommen bei OpenCloudTouch/i)).toBeInTheDocument()
    })
  })

  it('fetches devices on mount', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ devices: [{ id: '1', device_id: '1', name: 'Test Device' }] })
    })

    render(<App />)

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/devices')
    })
  })

  it('renders navigation when devices exist', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ devices: [{ id: '1', device_id: '1', name: 'Test Device' }] })
    })

    render(<App />)

    await waitFor(() => {
      // Navigation should be visible
      const nav = screen.getByRole('navigation')
      expect(nav).toBeInTheDocument()
    })
  })
})
