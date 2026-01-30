import { useState, useEffect } from 'react'
import './App.css'
import TopBar from './components/TopBar'
import DeviceCarousel from './components/DeviceCarousel'

function App() {
  const [devices, setDevices] = useState([])
  const [loading, setLoading] = useState(true)
  const [isDiscovering, setIsDiscovering] = useState(false)

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
    <div className="app">
      <TopBar 
        onDiscover={syncDevices} 
        deviceCount={devices.length}
        isDiscovering={isDiscovering}
      />
      
      <main className="app-main">
        <DeviceCarousel 
          devices={devices} 
          loading={loading}
          onRefresh={syncDevices}
          isDiscovering={isDiscovering}
        />
      </main>
    </div>
  )
}

export default App
