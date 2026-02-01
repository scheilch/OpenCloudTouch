import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Navigation from './components/Navigation'
import EmptyState from './components/EmptyState'
import RadioPresets from './pages/RadioPresets'
import LocalControl from './pages/LocalControl'
import MultiRoom from './pages/MultiRoom'
import Firmware from './pages/Firmware'
import Settings from './pages/Settings'
import Licenses from './pages/Licenses'
import './App.css'

function App() {
  const [devices, setDevices] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [hasTriggeredDiscovery, setHasTriggeredDiscovery] = useState(false)

  // Fetch devices from backend
  const fetchDevices = async () => {
    try {
      const response = await fetch('/api/devices')
      if (response.ok) {
        const data = await response.json()
        setDevices(data.devices || [])
      }
    } catch (error) {
      console.error('Failed to fetch devices:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Trigger device discovery
  const triggerDiscovery = async () => {
    setIsLoading(true)
    setHasTriggeredDiscovery(true)
    try {
      const response = await fetch('/api/devices/discover', { method: 'POST' })
      if (response.ok) {
        // Wait a bit for discovery to complete, then fetch devices
        setTimeout(fetchDevices, 2000)
      }
    } catch (error) {
      console.error('Discovery failed:', error)
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchDevices()
  }, [])

  // Show empty state if no devices and discovery hasn't been triggered yet
  if (!isLoading && devices.length === 0 && !hasTriggeredDiscovery) {
    return <EmptyState onDiscover={triggerDiscovery} />
  }

  return (
    <BrowserRouter>
      <div className="app">
        <header className="app-header">
          <Navigation />
        </header>
        <main className="app-main">
          <Routes>
            <Route path="/" element={<RadioPresets devices={devices} />} />
            <Route path="/local" element={<LocalControl devices={devices} />} />
            <Route path="/multiroom" element={<MultiRoom devices={devices} />} />
            <Route path="/firmware" element={<Firmware devices={devices} />} />
            <Route path="/settings" element={<Settings onRefreshDevices={fetchDevices} />} />
            <Route path="/licenses" element={<Licenses />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
