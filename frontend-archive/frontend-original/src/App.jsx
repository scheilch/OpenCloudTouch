import { useState, useEffect } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './App.css'
import TopBar from './components/TopBar'
import DeviceCarousel from './components/DeviceCarousel'
import RadioSearch from './components/RadioSearch'

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

function App() {
  const [devices, setDevices] = useState([])
  const [loading, setLoading] = useState(true)
  const [isDiscovering, setIsDiscovering] = useState(false)
  const [currentView, setCurrentView] = useState('devices') // 'devices' or 'radio'

  useEffect(() => {
    loadDevices()
  }, [])

  const loadDevices = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/devices')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      
      const data = await res.json()
      setDevices(data.devices || [])
    } catch (err) {
      console.error('Failed to load devices:', err)
    } finally {
      setLoading(false)
    }
  }

  const syncDevices = async () => {
    setIsDiscovering(true)
    try {
      const res = await fetch('/api/devices/sync', { method: 'POST' })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      await loadDevices()
    } catch (err) {
      console.error('Failed to sync devices:', err)
    } finally {
      setIsDiscovering(false)
    }
  }

  return (
    <QueryClientProvider client={queryClient}>
      <div className="app">
        <TopBar 
          onDiscover={syncDevices} 
          deviceCount={devices.length}
          isDiscovering={isDiscovering}
        />
        
        {/* Navigation Tabs */}
        <nav className="app-nav">
          <button
            onClick={() => setCurrentView('devices')}
            className={currentView === 'devices' ? 'active' : ''}
          >
            Geräte
          </button>
          <button
            onClick={() => setCurrentView('radio')}
            className={currentView === 'radio' ? 'active' : ''}
          >
            Radio
          </button>
        </nav>
        
        <main className="app-main">
          {currentView === 'devices' ? (
            <DeviceCarousel 
              devices={devices} 
              loading={loading}
              onRefresh={syncDevices}
              isDiscovering={isDiscovering}
            />
          ) : (
            <RadioSearch />
          )}
        </main>
      </div>
    </QueryClientProvider>
  )
}

export default App
