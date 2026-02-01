import React from 'react';
import { Link } from 'react-router-dom';
import './EmptyState.css';

/**
 * EmptyState Component
 * 
 * Shown on first app start when no devices are discovered yet.
 * Guides user through initial setup.
 */
export default function EmptyState({ onDiscover }) {
  return (
    <div className="empty-state">
      <div className="empty-state-content">
        <div className="empty-state-icon">
          <svg width="120" height="120" viewBox="0 0 120 120" fill="none">
            <circle cx="60" cy="60" r="50" stroke="currentColor" strokeWidth="2" opacity="0.2"/>
            <path d="M40 60L55 75L80 50" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" opacity="0.3"/>
            <rect x="35" y="45" width="50" height="30" rx="4" stroke="currentColor" strokeWidth="2"/>
            <rect x="45" y="55" width="10" height="10" rx="2" fill="currentColor" opacity="0.5"/>
            <rect x="60" y="55" width="10" height="10" rx="2" fill="currentColor" opacity="0.5"/>
          </svg>
        </div>
        
        <h1 className="empty-state-title">Willkommen bei CloudTouch</h1>
        <p className="empty-state-description">
          Noch keine Bose SoundTouch Geräte gefunden.
        </p>

        <div className="empty-state-steps">
          <div className="setup-step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Geräte einschalten</h3>
              <p>Stelle sicher, dass deine SoundTouch Geräte eingeschaltet und mit dem gleichen Netzwerk verbunden sind.</p>
            </div>
          </div>

          <div className="setup-step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Geräte suchen</h3>
              <p>Klicke auf "Jetzt suchen" um automatisch alle Geräte im Netzwerk zu finden.</p>
            </div>
          </div>

          <div className="setup-step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Presets verwalten</h3>
              <p>Nach erfolgreicher Erkennung kannst du Radiosender auf die Preset-Tasten (1-6) legen.</p>
            </div>
          </div>
        </div>

        <button className="cta-button" onClick={onDiscover}>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M10 3C6.13 3 3 6.13 3 10C3 13.87 6.13 17 10 17C13.87 17 17 13.87 17 10C17 6.13 13.87 3 10 3ZM10 15C7.24 15 5 12.76 5 10C5 7.24 7.24 5 10 5C12.76 5 15 7.24 15 10C15 12.76 12.76 15 10 15Z" fill="currentColor"/>
            <circle cx="10" cy="10" r="3" fill="currentColor"/>
          </svg>
          Jetzt Geräte suchen
        </button>

        <div className="empty-state-help">
          <details>
            <summary>Keine Geräte gefunden?</summary>
            <ul>
              <li>Prüfe ob die Geräte im gleichen WLAN sind wie CloudTouch</li>
              <li>Firewall-Regeln könnten die Geräteerkennung blockieren</li>
              <li>Starte die Geräte und CloudTouch neu</li>
              <li>
                Füge Geräte-IPs manuell in den{' '}
                <Link to="/settings" className="settings-link">
                  <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor" style={{ verticalAlign: 'middle', marginRight: '2px' }}>
                    <path d="M10 2a8 8 0 100 16 8 8 0 000-16zm1 11H9v-2h2v2zm0-4H9V5h2v4z"/>
                  </svg>
                  Einstellungen
                  <svg width="12" height="12" viewBox="0 0 20 20" fill="currentColor" style={{ verticalAlign: 'middle', marginLeft: '2px' }}>
                    <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"/>
                  </svg>
                </Link>
                {' '}hinzu
              </li>
            </ul>
          </details>
        </div>
      </div>
    </div>
  );
}
