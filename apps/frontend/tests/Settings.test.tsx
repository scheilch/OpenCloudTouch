import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import Settings from '../src/pages/Settings'

// Mock fetch globally
global.fetch = vi.fn()

describe('Settings Page', () => {
  beforeEach(() => {
    fetch.mockClear()
  })

  it('shows loading state initially', () => {
    fetch.mockImplementation(() => new Promise(() => {})) // Never resolves

    render(<Settings />)

    expect(screen.getByText('Einstellungen werden geladen...')).toBeInTheDocument()
  })

  it('fetches manual IPs on mount', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ips: ['192.168.1.10', '192.168.1.20'] })
    })

    render(<Settings />)

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/settings/manual-ips')
    })
  })

  it('displays fetched IPs', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ips: ['192.168.1.10', '192.168.1.20'] })
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByText('192.168.1.10')).toBeInTheDocument()
      expect(screen.getByText('192.168.1.20')).toBeInTheDocument()
    })
  })

  it('shows empty state when no IPs configured', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ips: [] })
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByText('Keine manuellen IPs konfiguriert')).toBeInTheDocument()
    })
  })

  it('shows error message when fetch fails', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'))

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByText(/Fehler beim Laden/i)).toBeInTheDocument()
    })
  })

  it('validates IP format before adding', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ips: [] })
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('192.168.1.10')).toBeInTheDocument()
    })

    const input = screen.getByPlaceholderText('192.168.1.10')
    const form = input.closest('form')

    // Invalid IP: too many octets
    fireEvent.change(input, { target: { value: '192.168.1.1.1' } })
    fireEvent.submit(form)

    await waitFor(() => {
      expect(screen.getByText(/Ungültige IP-Adresse/i)).toBeInTheDocument()
    })

    // fetch should not be called for invalid IP
    expect(fetch).toHaveBeenCalledTimes(1) // Only initial fetch
  })

  it('validates IP octet range', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ips: [] })
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('192.168.1.10')).toBeInTheDocument()
    })

    const input = screen.getByPlaceholderText('192.168.1.10')
    const form = input.closest('form')

    // Invalid IP: octet > 255
    fireEvent.change(input, { target: { value: '192.168.1.300' } })
    fireEvent.submit(form)

    await waitFor(() => {
      expect(screen.getByText(/Ungültige IP-Adresse/i)).toBeInTheDocument()
    })
  })

  it('prevents adding duplicate IPs', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ips: ['192.168.1.10'] })
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByText('192.168.1.10')).toBeInTheDocument()
    })

    const input = screen.getByPlaceholderText('192.168.1.10')
    const addButton = screen.getByText('+ Hinzufügen')

    fireEvent.change(input, { target: { value: '192.168.1.10' } })
    fireEvent.click(addButton)

    await waitFor(() => {
      expect(screen.getByText(/Diese IP-Adresse existiert bereits/i)).toBeInTheDocument()
    })
  })

  it('adds valid IP successfully', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ips: [] })
    })

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({})
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('192.168.1.10')).toBeInTheDocument()
    })

    const input = screen.getByPlaceholderText('192.168.1.10')
    const addButton = screen.getByText('+ Hinzufügen')

    fireEvent.change(input, { target: { value: '192.168.1.30' } })
    fireEvent.click(addButton)

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        '/api/settings/manual-ips',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ip: '192.168.1.30' })
        })
      )
    })

    await waitFor(() => {
      expect(screen.getByText(/IP 192.168.1.30 hinzugefügt/i)).toBeInTheDocument()
    })
  })

  it('clears input after successful add', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ips: [] })
    })

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({})
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('192.168.1.10')).toBeInTheDocument()
    })

    const input = screen.getByPlaceholderText('192.168.1.10')
    const addButton = screen.getByText('+ Hinzufügen')

    fireEvent.change(input, { target: { value: '192.168.1.30' } })
    fireEvent.click(addButton)

    await waitFor(() => {
      expect(input.value).toBe('')
    })
  })

  it('shows error when add fails', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ips: [] })
    })

    fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Server error' })
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('192.168.1.10')).toBeInTheDocument()
    })

    const input = screen.getByPlaceholderText('192.168.1.10')
    const addButton = screen.getByText('+ Hinzufügen')

    fireEvent.change(input, { target: { value: '192.168.1.30' } })
    fireEvent.click(addButton)

    await waitFor(() => {
      expect(screen.getByText(/Fehler/i)).toBeInTheDocument()
    })
  })

  it('deletes IP successfully', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ips: ['192.168.1.10', '192.168.1.20'] })
    })

    fetch.mockResolvedValueOnce({
      ok: true
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByText('192.168.1.10')).toBeInTheDocument()
    })

    const deleteButtons = screen.getAllByTitle('IP entfernen')
    fireEvent.click(deleteButtons[0])

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        '/api/settings/manual-ips/192.168.1.10',
        expect.objectContaining({ method: 'DELETE' })
      )
    })

    await waitFor(() => {
      expect(screen.getByText(/IP 192.168.1.10 entfernt/i)).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.queryByText('192.168.1.10')).not.toBeInTheDocument()
      expect(screen.getByText('192.168.1.20')).toBeInTheDocument()
    })
  })

  it('shows error when delete fails', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ips: ['192.168.1.10'] })
    })

    fetch.mockResolvedValueOnce({
      ok: false
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByText('192.168.1.10')).toBeInTheDocument()
    })

    const deleteButton = screen.getByTitle('IP entfernen')
    fireEvent.click(deleteButton)

    await waitFor(() => {
      expect(screen.getByText(/Fehler beim Löschen/i)).toBeInTheDocument()
    })

    // IP should still be in list
    expect(screen.getByText('192.168.1.10')).toBeInTheDocument()
  })

  it('shows info box', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ips: [] })
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByText(/Nach dem Hinzufügen oder Entfernen/i)).toBeInTheDocument()
    })
  })

  it('rejects empty IP input', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ips: [] })
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('192.168.1.10')).toBeInTheDocument()
    })

    const addButton = screen.getByText('+ Hinzufügen')
    fireEvent.click(addButton)

    await waitFor(() => {
      expect(screen.getByText(/Bitte geben Sie eine IP-Adresse ein/i)).toBeInTheDocument()
    })
  })

  it('trims whitespace from IP input', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ips: [] })
    })

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({})
    })

    render(<Settings />)

    await waitFor(() => {
      expect(screen.getByPlaceholderText('192.168.1.10')).toBeInTheDocument()
    })

    const input = screen.getByPlaceholderText('192.168.1.10')
    const form = input.closest('form')

    fireEvent.change(input, { target: { value: '  192.168.1.30  ' } })
    fireEvent.submit(form)

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        '/api/settings/manual-ips',
        expect.objectContaining({
          body: JSON.stringify({ ip: '192.168.1.30' }) // Trimmed
        })
      )
    })
  })
})
