import { useState } from 'react'
import './TopBar.css'
import BurgerMenu from './BurgerMenu'

function TopBar({ onDiscover, deviceCount = 0, isDiscovering = false }) {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <>
      <header className="topbar">
        {deviceCount > 0 && (
          <button 
            className="topbar-button"
            onClick={() => setMenuOpen(true)}
            aria-label="Menü öffnen"
            disabled={isDiscovering}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" strokeWidth="2">
              <line x1="3" y1="6" x2="21" y2="6" stroke="#000000" />
              <line x1="3" y1="12" x2="21" y2="12" stroke="#000000" />
              <line x1="3" y1="18" x2="21" y2="18" stroke="#000000" />
            </svg>
          </button>
        )}

        <button 
          className="topbar-button"
          onClick={onDiscover}
          aria-label="Geräte suchen"
          title="Geräte suchen"
          disabled={isDiscovering}
        >
          {isDiscovering ? (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" strokeWidth="2" className="spinner">
              <path d="M21 12a9 9 0 1 1-6.219-8.56" stroke="#000000" />
            </svg>
          ) : (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" strokeWidth="2">
              <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2" stroke="#000000" />
            </svg>
          )}
        </button>
      </header>

      <BurgerMenu 
        isOpen={menuOpen} 
        onClose={() => setMenuOpen(false)}
        onDiscover={onDiscover}
        deviceCount={deviceCount}
        isDiscovering={isDiscovering}
      />
    </>
  )
}

export default TopBar
