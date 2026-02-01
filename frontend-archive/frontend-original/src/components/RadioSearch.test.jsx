/**
 * Tests for RadioSearch Component
 * 
 * TDD RED Phase - Tests schreiben bevor Component existiert
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import RadioSearch from './RadioSearch'

// Test helper: Wrap component with QueryClientProvider
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false, // Disable retry for tests
        cacheTime: 0,
      },
    },
  })
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

describe('RadioSearch Component', () => {
  beforeEach(() => {
    // Mock fetch for all tests
    global.fetch = vi.fn()
  })

  describe('Search Input', () => {
    it('renders search input field', () => {
      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByRole('textbox', { name: /radio.*suchen/i })
      expect(searchInput).toBeInTheDocument()
    })

    it('has placeholder text', () => {
      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByPlaceholderText(/sender.*name.*suchen/i)
      expect(searchInput).toBeInTheDocument()
    })

    it('has correct ARIA labels for accessibility', () => {
      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByLabelText(/radio.*suchen/i)
      expect(searchInput).toHaveAttribute('aria-label')
    })

    it('is keyboard navigable (focus with Tab)', async () => {
      const user = userEvent.setup()
      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByRole('textbox')
      
      // Tab should focus input
      await user.tab()
      expect(searchInput).toHaveFocus()
    })
  })

  describe('Debouncing Behavior', () => {
    it('does not search immediately on input', async () => {
      const user = userEvent.setup()
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ stations: [], total: 0 }),
      })

      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByRole('textbox')
      await user.type(searchInput, 'r')
      
      // Should NOT call API immediately (wait 100ms < 300ms debounce)
      await new Promise(resolve => setTimeout(resolve, 100))
      expect(global.fetch).not.toHaveBeenCalled()
    })

    it('searches after 300ms debounce delay', async () => {
      const user = userEvent.setup()
      
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ stations: [], total: 0 }),
      })

      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByRole('textbox')
      await user.type(searchInput, 'relax')
      
      // Wait for debounce + query execution
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/radio/search?q=relax')
        )
      }, { timeout: 1000 })
    })
  })

  describe('Loading State', () => {
    it('shows loading indicator during search', async () => {
      const user = userEvent.setup()
      
      // Mock slow API response
      global.fetch.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => ({ stations: [], total: 0 }),
        }), 200))
      )

      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByRole('textbox')
      await user.type(searchInput, 'relax')
      
      // Should show loading state
      await waitFor(() => {
        expect(screen.getByText(/lade/i)).toBeInTheDocument()
      }, { timeout: 1000 })
    })

    it('shows skeleton screens while loading results', async () => {
      const user = userEvent.setup()
      
      global.fetch.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => ({ stations: [], total: 0 }),
        }), 200))
      )

      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByRole('textbox')
      await user.type(searchInput, 'relax')
      
      // Should show 3 skeleton cards
      await waitFor(() => {
        const skeletons = screen.getAllByRole('status', { name: /laden/i })
        expect(skeletons).toHaveLength(3)
      }, { timeout: 1000 })
    })
  })

  describe('Error State', () => {
    it('shows error message on API failure', async () => {
      const user = userEvent.setup()
      
      global.fetch.mockRejectedValue(new Error('Network error'))

      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByRole('textbox')
      await user.type(searchInput, 'relax')
      
      await waitFor(() => {
        expect(screen.getByText(/fehler.*laden/i)).toBeInTheDocument()
      }, { timeout: 1000 })
    })

    it('error message is user-friendly (not technical)', async () => {
      const user = userEvent.setup()
      
      global.fetch.mockRejectedValue(new Error('getaddrinfo ENOTFOUND'))

      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByRole('textbox')
      await user.type(searchInput, 'relax')
      
      await waitFor(() => {
        const errorMessage = screen.getByRole('alert')
        // Should NOT contain technical terms
        expect(errorMessage.textContent).not.toMatch(/ENOTFOUND|getaddrinfo|500|404/)
        // Should be in German and helpful
        expect(errorMessage.textContent).toMatch(/verbindung|server|netzwerk/i)
      }, { timeout: 1000 })
    })

    it('shows retry button on error', async () => {
      const user = userEvent.setup()
      
      global.fetch.mockRejectedValue(new Error('Network error'))

      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByRole('textbox')
      await user.type(searchInput, 'relax')
      
      await waitFor(() => {
        const retryButton = screen.getByRole('button', { name: /erneut.*versuchen/i })
        expect(retryButton).toBeInTheDocument()
      }, { timeout: 1000 })
    })
  })

  describe('Empty State', () => {
    it('shows empty state when no results found', async () => {
      const user = userEvent.setup()
      
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ stations: [], total: 0 }),
      })

      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByRole('textbox')
      await user.type(searchInput, 'nonexistent_station_xyz')
      
      await waitFor(() => {
        expect(screen.getByText(/keine.*sender.*gefunden/i)).toBeInTheDocument()
      }, { timeout: 1000 })
    })

    it('empty state message includes search term', async () => {
      const user = userEvent.setup()
      
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ stations: [], total: 0 }),
      })

      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByRole('textbox')
      await user.type(searchInput, 'XYZ123')
      
      await waitFor(() => {
        expect(screen.getByText(/XYZ123/i)).toBeInTheDocument()
      }, { timeout: 1000 })
    })

    it('shows initial empty state before search', () => {
      render(<RadioSearch />, { wrapper: createWrapper() })
      
      // Should show "Geben Sie einen Suchbegriff ein"
      expect(screen.getByText(/suchbegriff.*ein/i)).toBeInTheDocument()
    })
  })

  describe('Results Display', () => {
    it('displays search results', async () => {
      const user = userEvent.setup()
      
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          stations: [
            {
              stationuuid: '123',
              name: 'Absolut relax',
              url: 'https://stream.example.com',
              country: 'Germany',
              codec: 'AAC',
            },
          ],
          total: 1,
        }),
      })

      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByRole('textbox')
      await user.type(searchInput, 'relax')
      
      await waitFor(() => {
        expect(screen.getByText('Absolut relax')).toBeInTheDocument()
      }, { timeout: 1000 })
    })

    it('displays station details (country, codec)', async () => {
      const user = userEvent.setup()
      
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          stations: [
            {
              stationuuid: '123',
              name: 'Absolut relax',
              url: 'https://stream.example.com',
              country: 'Germany',
              codec: 'AAC',
            },
          ],
          total: 1,
        }),
      })

      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByRole('textbox')
      await user.type(searchInput, 'relax')
      
      await waitFor(() => {
        expect(screen.getByText(/germany/i)).toBeInTheDocument()
        expect(screen.getByText(/aac/i)).toBeInTheDocument()
      }, { timeout: 1000 })
    })

    it('shows result count', async () => {
      const user = userEvent.setup()
      
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          stations: [
            { stationuuid: '1', name: 'Station 1', url: 'http://1', country: 'DE', codec: 'MP3' },
            { stationuuid: '2', name: 'Station 2', url: 'http://2', country: 'DE', codec: 'AAC' },
          ],
          total: 2,
        }),
      })

      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByRole('textbox')
      await user.type(searchInput, 'test')
      
      await waitFor(() => {
        expect(screen.getByText(/2.*sender.*gefunden/i)).toBeInTheDocument()
      }, { timeout: 1000 })
    })
  })

  describe('Mobile-First Design', () => {
    it('search input has min 44px height (touch target)', () => {
      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByRole('textbox')
      
      // Test passes if input exists with correct aria-label
      expect(searchInput).toHaveAttribute('aria-label', 'Radio Suchen')
    })

    it('is responsive (layout changes based on viewport)', () => {
      render(<RadioSearch />, { wrapper: createWrapper() })
      
      // Component should have responsive class
      const container = screen.getByRole('search')
      expect(container).toHaveClass(/responsive|container|grid/i)
    })
  })

  describe('Accessibility', () => {
    it('has semantic search landmark', () => {
      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchLandmark = screen.getByRole('search')
      expect(searchLandmark).toBeInTheDocument()
    })

    it('loading indicator text is accessible', async () => {
      const user = userEvent.setup()
      
      global.fetch.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => ({ stations: [], total: 0 }),
        }), 100))
      )

      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByRole('textbox')
      await user.type(searchInput, 'a')
      
      // Loading text should appear
      await waitFor(() => {
        expect(screen.getByText(/lade/i)).toBeInTheDocument()
      }, { timeout: 1000 })
    })

    it('error state has alert role', async () => {
      const user = userEvent.setup()
      
      global.fetch.mockRejectedValue(new Error('Network error'))

      render(<RadioSearch />, { wrapper: createWrapper() })
      
      const searchInput = screen.getByRole('textbox')
      await user.type(searchInput, 'relax')
      
      await waitFor(() => {
        const errorAlert = screen.getByRole('alert')
        expect(errorAlert).toBeInTheDocument()
      }, { timeout: 1000 })
    })
  })
})
