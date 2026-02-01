import { useState, useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import styles from './RadioSearch.module.css'

/**
 * RadioSearch Component
 * 
 * Allows users to search for radio stations using RadioBrowser API.
 * Features: Debouncing, Loading/Error/Empty States, Accessibility
 */
function RadioSearch() {
  const [searchTerm, setSearchTerm] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const debounceTimeoutRef = useRef(null)

  // Debounce search input (300ms)
  useEffect(() => {
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current)
    }

    debounceTimeoutRef.current = setTimeout(() => {
      setDebouncedSearch(searchTerm)
    }, 300)

    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current)
      }
    }
  }, [searchTerm])

  // Fetch radio stations with React Query
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['radioSearch', debouncedSearch],
    queryFn: async () => {
      if (!debouncedSearch) return { stations: [], total: 0 }

      const response = await fetch(
        `/api/radio/search?q=${encodeURIComponent(debouncedSearch)}&limit=20`
      )
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      
      return response.json()
    },
    enabled: debouncedSearch.length > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes cache
  })

  const handleInputChange = (e) => {
    setSearchTerm(e.target.value)
  }

  const handleRetry = () => {
    refetch()
  }

  const stations = data?.stations || []
  const total = data?.total || 0

  return (
    <div className={styles.container} role="search">
      <div className={styles.searchBox}>
        <label htmlFor="radio-search-input" className={styles.visuallyHidden}>
          Radio Suchen
        </label>
        <input
          id="radio-search-input"
          type="text"
          value={searchTerm}
          onChange={handleInputChange}
          placeholder="Sender nach Name suchen..."
          aria-label="Radio Suchen"
          className={styles.searchInput}
        />
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className={styles.loadingContainer} role="status" aria-live="polite">
          <p className={styles.loadingText}>Lade Sender...</p>
          <div className={styles.skeletonList}>
            {[1, 2, 3].map((i) => (
              <div key={i} className={styles.skeletonCard} role="status" aria-label="Laden">
                <div className={styles.skeletonTitle}></div>
                <div className={styles.skeletonText}></div>
                <div className={styles.skeletonText}></div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <div className={styles.errorContainer} role="alert">
          <p className={styles.errorMessage}>
            Fehler beim Laden der Sender. Bitte überprüfen Sie Ihre Netzwerkverbindung.
          </p>
          <button onClick={handleRetry} className={styles.retryButton}>
            Erneut versuchen
          </button>
        </div>
      )}

      {/* Empty State - No search term */}
      {!searchTerm && !isLoading && !error && (
        <div className={styles.emptyState}>
          <p className={styles.emptyMessage}>
            Geben Sie einen Suchbegriff ein, um Radiosender zu finden.
          </p>
        </div>
      )}

      {/* Empty State - No results */}
      {debouncedSearch && !isLoading && !error && stations.length === 0 && (
        <div className={styles.emptyState}>
          <p className={styles.emptyMessage}>
            Keine Sender gefunden für "{debouncedSearch}"
          </p>
        </div>
      )}

      {/* Results */}
      {!isLoading && !error && stations.length > 0 && (
        <div className={styles.resultsContainer}>
          <p className={styles.resultCount}>
            {total} Sender gefunden
          </p>
          <div className={styles.stationList}>
            {stations.map((station) => (
              <div key={station.stationuuid} className={styles.stationCard}>
                <h3 className={styles.stationName}>{station.name}</h3>
                <div className={styles.stationDetails}>
                  <span className={styles.stationCountry}>{station.country}</span>
                  <span className={styles.stationCodec}>{station.codec}</span>
                </div>
                <a
                  href={station.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.stationUrl}
                >
                  Stream-URL
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default RadioSearch
