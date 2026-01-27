import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/health')
      .then(res => res.json())
      .then(data => {
        setHealth(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to fetch health:', err)
        setLoading(false)
      })
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <h1>SoundTouchBridge</h1>
        <p className="subtitle">Open-Source Replacement for Bose SoundTouch Cloud</p>
      </header>
      
      <main className="app-main">
        <div className="status-card">
          <h2>System Status</h2>
          {loading ? (
            <p>Loading...</p>
          ) : health ? (
            <div className="health-info">
              <p className="status-ok">✓ Status: {health.status}</p>
              <p>Version: {health.version}</p>
              <p>Discovery: {health.config?.discovery_enabled ? 'Enabled' : 'Disabled'}</p>
            </div>
          ) : (
            <p className="status-error">✗ Backend not reachable</p>
          )}
        </div>

        <div className="info-card">
          <h3>Iteration 0: MVP Setup</h3>
          <ul>
            <li>✓ Backend API (FastAPI)</li>
            <li>✓ Frontend UI (React + Vite)</li>
            <li>✓ Docker Build ready</li>
            <li>⏳ Discovery (next iteration)</li>
            <li>⏳ Radio Search (next iteration)</li>
            <li>⏳ Presets (next iteration)</li>
          </ul>
        </div>
      </main>

      <footer className="app-footer">
        <p>Iteration 0 – Repo/Build/Run Complete</p>
      </footer>
    </div>
  )
}

export default App
