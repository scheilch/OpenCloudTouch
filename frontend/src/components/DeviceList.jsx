import { useState, useEffect } from 'react'
import './DeviceList.css'

function DeviceList() {
  const [devices, setDevices] = useState([])
  const [loading, setLoading] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const [error, setError] = useState(null)

  const loadDevices = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const res = await fetch('/api/devices')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      
      const data = await res.json()
      setDevices(data.devices || [])
    } catch (err) {
      console.error('Failed to load devices:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const syncDevices = async () => {
    setSyncing(true)
    setError(null)
    
    try {
      const res = await fetch('/api/devices/sync', { method: 'POST' })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      
      const data = await res.json()
      console.log('Sync result:', data)
      
      // Reload device list
      await loadDevices()
    } catch (err) {
      console.error('Failed to sync devices:', err)
      setError(err.message)
    } finally {
      setSyncing(false)
    }
  }

  useEffect(() => {
    loadDevices()
  }, [])

  return (
    <div className="device-list">
      <div className="device-list-header">
        <h2>SoundTouch Devices</h2>
        <div className="device-list-actions">
          <button 
            onClick={loadDevices} 
            disabled={loading}
            className="btn btn-secondary"
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
          <button 
            onClick={syncDevices} 
            disabled={syncing}
            className="btn btn-primary"
          >
            {syncing ? 'Discovering...' : 'Discover Devices'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}

      {devices.length === 0 && !loading && (
        <div className="empty-state">
          <p>No devices found</p>
          <p className="empty-hint">Click "Discover Devices" to search for SoundTouch speakers on your network</p>
        </div>
      )}

      {devices.length > 0 && (
        <div className="device-grid">
          {devices.map(device => (
            <div key={device.device_id} className="device-card">
              <div className="device-icon">🔊</div>
              <div className="device-info">
                <h3 className="device-name">{device.name}</h3>
                <p className="device-model">{device.model}</p>
                <div className="device-details">
                  <span className="device-ip">IP: {device.ip}</span>
                  <span className="device-firmware">FW: {device.firmware_version}</span>
                </div>
                {device.last_seen && (
                  <p className="device-last-seen">
                    Last seen: {new Date(device.last_seen).toLocaleString()}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default DeviceList
