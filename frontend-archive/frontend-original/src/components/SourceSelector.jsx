import { useState } from 'react'
import './SourceSelector.css'

function SourceSelector() {
  const [activeSource, setActiveSource] = useState('wifi')

  const sources = [
    { 
      id: 'wifi', 
      label: 'Wi-Fi',
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M5 12.55a11 11 0 0 1 14.08 0M1.42 9a16 16 0 0 1 21.16 0M8.53 16.11a6 6 0 0 1 6.95 0M12 20h.01" />
        </svg>
      )
    },
    { 
      id: 'bluetooth', 
      label: 'Bluetooth',
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="m7 7 10 10-5 5V2l5 5L7 17" />
        </svg>
      )
    },
    { 
      id: 'aux', 
      label: 'AUX',
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" />
          <path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01" />
        </svg>
      )
    }
  ]

  return (
    <div className="source-selector">
      <label className="source-label">Quelle</label>
      <div className="source-buttons">
        {sources.map(source => (
          <button
            key={source.id}
            className={`source-button ${activeSource === source.id ? 'source-button--active' : ''}`}
            onClick={() => setActiveSource(source.id)}
            aria-label={source.label}
            title={source.label}
          >
            {source.icon}
            <span className="source-name">{source.label}</span>
          </button>
        ))}
      </div>
    </div>
  )
}

export default SourceSelector
