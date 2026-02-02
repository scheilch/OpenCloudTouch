import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { ToastProvider } from './contexts/ToastContext'
import Navigation from './components/Navigation'
import EmptyState from './components/EmptyState'
import RadioPresets from './pages/RadioPresets'
import LocalControl from './pages/LocalControl'
import MultiRoom from './pages/MultiRoom'
import Firmware from './pages/Firmware'
import Settings from './pages/Settings'
import Licenses from './pages/Licenses'
import './App.css'

/**
 * AppRouter - Handles routing logic with device-based guards
 */
function AppRouter({ devices, isLoading, onRefreshDevices }) {
  if (isLoading) {
    return (
      <div className="app">
        <div className="loading-container">
          <div className="spinner" />
          <p className="loading-message">CloudTouch wird geladen...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <Routes>
        {/* Welcome Screen - shown when no devices */}
        <Route 
          path="/welcome" 
          element={
            devices.length === 0 ? (
              <EmptyState onRefreshDevices={onRefreshDevices} />
            ) : (
              <Navigate to="/" replace />
            )
          } 
        />

        {/* Main App Routes - require devices */}
        <Route
          path="/*"
          element={
            devices.length > 0 ? (
              <>
                <header className="app-header" data-test="app-header">
                  <Navigation />
                </header>
                <main className="app-main">
                  <Routes>
                    <Route path="/" element={<RadioPresets devices={devices} />} />
                    <Route path="/local" element={<LocalControl devices={devices} />} />
                    <Route path="/multiroom" element={<MultiRoom devices={devices} />} />
                    <Route path="/firmware" element={<Firmware devices={devices} />} />
                    <Route path="/settings" element={<Settings onRefreshDevices={onRefreshDevices} />} />
                    <Route path="/licenses" element={<Licenses />} />
                  </Routes>
                </main>
              </>
            ) : (
              <Navigate to="/welcome" replace />
            )
          }
        />
      </Routes>
    </div>
  )
}

function App() {
  const [devices, setDevices] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  // Fetch devices from backend
  const fetchDevices = async () => {
    try {
      const response = await fetch('/api/devices')
      if (response.ok) {
        const data = await response.json()
        const devicesList = data.devices || []
        setDevices(devicesList)
        return devicesList
      }
      return []
    } catch (error) {
      console.error('Failed to fetch devices:', error)
      return []
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchDevices()
  }, [])

  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <ToastProvider>
        <AppRouter 
          devices={devices} 
          isLoading={isLoading}
          onRefreshDevices={fetchDevices}
        />
      </ToastProvider>
    </BrowserRouter>
  )
}

export default App
