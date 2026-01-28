import { useState, useEffect } from 'react'
import './App.css'
import DeviceList from './components/DeviceList'

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
        {health && (
          <p className="version">v{health.version}</p>
        )}
      </header>
      
      <main className="app-main">
        <DeviceList />
      </main>

      <footer className="app-footer">
        <p>Iteration 1 – Device Discovery & Inventory</p>
      </footer>
    </div>
  )
}

export default App
