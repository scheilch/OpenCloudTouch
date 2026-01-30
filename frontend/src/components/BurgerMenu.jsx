import { useEffect } from 'react'
import './BurgerMenu.css'

function BurgerMenu({ isOpen, onClose, onDiscover, deviceCount = 0, isDiscovering = false }) {
  useEffect(() => {
    if (isOpen) {
      document.body.classList.add('no-scroll')
    } else {
      document.body.classList.remove('no-scroll')
    }
    
    return () => document.body.classList.remove('no-scroll')
  }, [isOpen])

  const handleDiscover = () => {
    onDiscover()
    // Menu bleibt offen - User kann manuell schließen
  }

  const getDiscoverLabel = () => {
    return deviceCount > 0 ? "Weitere Geräte suchen" : "Geräte suchen"
  }

  const menuItems = [
    { id: 'spotify', label: 'Spotify', disabled: true },
    { id: 'amazon', label: 'Amazon Music', disabled: true },
    { id: 'radio', label: 'Internet Radio', disabled: true },
    { id: 'mymusic', label: 'My Music', disabled: true },
    { id: 'add', label: 'Service hinzufügen', disabled: true },
    { id: 'settings', label: 'Einstellungen', disabled: true },
    { id: 'help', label: 'Hilfe', disabled: true },
    { id: 'divider', isDivider: true },
    { id: 'discover', label: getDiscoverLabel(), disabled: isDiscovering, onClick: handleDiscover, isDiscovering },
  ]

  return (
    <>
      <div 
        className={`burger-overlay ${isOpen ? 'burger-overlay--open' : ''}`}
        onClick={onClose}
        aria-hidden={!isOpen}
      />
      
      <nav 
        className={`burger-menu ${isOpen ? 'burger-menu--open' : ''}`}
        aria-label="Hauptnavigation"
      >
        <div className="burger-header">
          <button 
            className="burger-close"
            onClick={onClose}
            aria-label="Menü schließen"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <ul className="burger-list">
          {menuItems.map(item => {
            if (item.isDivider) {
              return <li key={item.id} className="burger-divider" />
            }
            
            return (
              <li key={item.id}>
                <button 
                  className="burger-item"
                  disabled={item.disabled}
                  onClick={item.onClick}
                >
                  <div>{item.label}</div>
                  {item.isDiscovering && (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="spinner">
                      <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                    </svg>
                  )}
                  {item.disabled && !item.isDiscovering && <span className="badge-coming-soon">Demnächst</span>}
                </button>
              </li>
            )
          })}
        </ul>
      </nav>
    </>
  )
}

export default BurgerMenu
