import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useDevices } from '../hooks/useDevices'
import './Settings.css'

const LANGUAGES = ['Deutsch', 'English', 'Français', 'Italiano', 'Español']
const AUTO_STANDBY_OPTIONS = ['Nie', '15 Minuten', '30 Minuten', '1 Stunde', '2 Stunden']
const STREAMING_PROVIDERS = [
  { id: 'music-assistant', name: 'Music Assistant', icon: '🎵', available: false },
  { id: 'spotify', name: 'Spotify Connect', icon: '🎧', available: false },
  { id: 'apple-music', name: 'Apple Music', icon: '🍎', available: false },
  { id: 'deezer', name: 'Deezer', icon: '🎶', available: false }
]

const FAQ_ITEMS = [
  {
    question: 'Warum werden meine Geräte nicht gefunden?',
    answer: 'Stellen Sie sicher, dass alle Geräte eingeschaltet sind und sich im gleichen WLAN befinden wie SoundTouch Bridge. Die automatische Erkennung nutzt SSDP-Multicast.'
  },
  {
    question: 'Kann ich Geräte manuell hinzufügen?',
    answer: 'Ja, verwenden Sie die "Manuelle IPs" Funktion in den Discovery-Einstellungen. Geben Sie die IP-Adressen getrennt durch Kommas ein.'
  },
  {
    question: 'Was passiert wenn Bose die Cloud abschaltet?',
    answer: 'SoundTouch Bridge übernimmt alle wesentlichen Funktionen lokal: Radio-Streaming, Presets, Multi-Room und Gerätesteuerung funktionieren weiterhin.'
  },
  {
    question: 'Unterstützt STB alle SoundTouch Modelle?',
    answer: 'Ja, STB unterstützt ST10, ST20, ST30, ST300 und alle Wave SoundTouch Modelle. Einige Features (z.B. HDMI) sind modellspezifisch.'
  }
]

export default function Settings() {
  const { devices, loading } = useDevices()
  const [currentDeviceIndex] = useState(0)
  
  // Device Settings
  const [language, setLanguage] = useState('Deutsch')
  const [bass, setBass] = useState(0)
  const [clockDisplay, setClockDisplay] = useState(true)
  const [bluetoothName, setBluetoothName] = useState('ST30')
  const [autoStandby, setAutoStandby] = useState('30 Minuten')
  
  // Discovery Settings
  const [autoDiscovery, setAutoDiscovery] = useState(true)
  const [manualIps, setManualIps] = useState('')
  
  // Streaming Providers
  const [enabledProviders, setEnabledProviders] = useState([])
  
  // FAQ
  const [expandedFaq, setExpandedFaq] = useState(null)

  const currentDevice = devices[currentDeviceIndex]

  const handleBassChange = (e) => {
    setBass(parseInt(e.target.value, 10))
  }

  const handleDiscoverDevices = () => {
    console.log('Scanning for devices...')
  }

  const handleSaveSettings = () => {
    console.log('Saving settings:', {
      language,
      bass,
      clockDisplay,
      bluetoothName,
      autoStandby,
      autoDiscovery,
      manualIps
    })
  }

  const toggleFaq = (index) => {
    setExpandedFaq(expandedFaq === index ? null : index)
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner" />
        <p className="loading-message">Geräte werden geladen...</p>
      </div>
    )
  }

  if (devices.length === 0) {
    return (
      <div className="empty-container">
        <p className="empty-message">Keine Geräte gefunden</p>
      </div>
    )
  }

  return (
    <div className="page settings-page">
      <h1 className="page-title">Einstellungen</h1>

      {/* Device Settings */}
      <motion.section 
        className="settings-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h2 className="section-title">
          <span className="section-icon">🔧</span>
          Geräteeinstellungen - {currentDevice?.name}
        </h2>
        <div className="settings-card">
          {/* Language */}
          <div className="setting-item">
            <label className="setting-label">Sprache</label>
            <select 
              className="setting-select"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              {LANGUAGES.map(lang => (
                <option key={lang} value={lang}>{lang}</option>
              ))}
            </select>
          </div>

          {/* Bass */}
          <div className="setting-item">
            <label className="setting-label">
              Bass: <span className="setting-value">{bass > 0 ? '+' : ''}{bass}</span>
            </label>
            <input
              type="range"
              min="-5"
              max="5"
              value={bass}
              onChange={handleBassChange}
              className="setting-slider"
            />
            <div className="slider-labels">
              <span>-5</span>
              <span>0</span>
              <span>+5</span>
            </div>
          </div>

          {/* Clock Display */}
          <div className="setting-item toggle">
            <label className="setting-label">Uhr anzeigen</label>
            <button 
              className={`toggle-button ${clockDisplay ? 'active' : ''}`}
              onClick={() => setClockDisplay(!clockDisplay)}
            >
              <span className="toggle-slider" />
              <span className="toggle-text">{clockDisplay ? 'AN' : 'AUS'}</span>
            </button>
          </div>

          {/* Bluetooth Name */}
          <div className="setting-item">
            <label className="setting-label">Bluetooth Name</label>
            <input
              type="text"
              className="setting-input"
              value={bluetoothName}
              onChange={(e) => setBluetoothName(e.target.value)}
              maxLength={20}
            />
          </div>

          {/* Auto Standby */}
          <div className="setting-item">
            <label className="setting-label">Automatischer Standby</label>
            <select 
              className="setting-select"
              value={autoStandby}
              onChange={(e) => setAutoStandby(e.target.value)}
            >
              {AUTO_STANDBY_OPTIONS.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>
        </div>
      </motion.section>

      {/* Discovery Settings */}
      <motion.section 
        className="settings-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <h2 className="section-title">
          <span className="section-icon">🔍</span>
          Gerätesuche
        </h2>
        <div className="settings-card">
          {/* Auto Discovery */}
          <div className="setting-item toggle">
            <label className="setting-label">Automatische Erkennung (SSDP)</label>
            <button 
              className={`toggle-button ${autoDiscovery ? 'active' : ''}`}
              onClick={() => setAutoDiscovery(!autoDiscovery)}
            >
              <span className="toggle-slider" />
              <span className="toggle-text">{autoDiscovery ? 'AN' : 'AUS'}</span>
            </button>
          </div>

          {/* Manual IPs */}
          <div className="setting-item">
            <label className="setting-label">Manuelle IP-Adressen</label>
            <textarea
              className="setting-textarea"
              value={manualIps}
              onChange={(e) => setManualIps(e.target.value)}
              placeholder="192.0.2.101, 192.0.2.102, ..."
              rows={3}
            />
            <p className="setting-hint">Komma-getrennte Liste von IP-Adressen</p>
          </div>

          {/* Scan Button */}
          <button className="scan-button" onClick={handleDiscoverDevices}>
            <span className="button-icon">🔍</span>
            <span>Jetzt nach Geräten suchen</span>
          </button>
        </div>
      </motion.section>

      {/* Streaming Providers */}
      <motion.section 
        className="settings-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h2 className="section-title">
          <span className="section-icon">🎵</span>
          Streaming-Anbieter
        </h2>
        <div className="settings-card">
          <div className="providers-grid">
            {STREAMING_PROVIDERS.map((provider) => (
              <div 
                key={provider.id}
                className={`provider-card ${!provider.available ? 'disabled' : ''}`}
              >
                <input
                  type="checkbox"
                  id={provider.id}
                  disabled={!provider.available}
                  checked={enabledProviders.includes(provider.id)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setEnabledProviders([...enabledProviders, provider.id])
                    } else {
                      setEnabledProviders(enabledProviders.filter(id => id !== provider.id))
                    }
                  }}
                />
                <label htmlFor={provider.id} className="provider-label">
                  <span className="provider-icon">{provider.icon}</span>
                  <span className="provider-name">{provider.name}</span>
                  {!provider.available && (
                    <span className="coming-soon-badge">Bald verfügbar</span>
                  )}
                </label>
              </div>
            ))}
          </div>
        </div>
      </motion.section>

      {/* FAQ */}
      <motion.section 
        className="settings-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h2 className="section-title">
          <span className="section-icon">❓</span>
          Häufig gestellte Fragen
        </h2>
        <div className="faq-list">
          {FAQ_ITEMS.map((item, index) => (
            <div key={index} className="faq-item">
              <button 
                className={`faq-question ${expandedFaq === index ? 'expanded' : ''}`}
                onClick={() => toggleFaq(index)}
              >
                <span className="faq-question-text">{item.question}</span>
                <span className="faq-toggle-icon">{expandedFaq === index ? '−' : '+'}</span>
              </button>
              {expandedFaq === index && (
                <motion.div 
                  className="faq-answer"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                >
                  {item.answer}
                </motion.div>
              )}
            </div>
          ))}
        </div>
      </motion.section>

      {/* About */}
      <motion.section 
        className="settings-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <h2 className="section-title">
          <span className="section-icon">ℹ️</span>
          Über CloudTouch
        </h2>
        <div className="about-card">
          <div className="about-logo">🎵</div>
          <h3 className="about-title">CloudTouch</h3>
          <p className="about-version">Version 1.0.0 (Beta)</p>
          <p className="about-description">
            Lokale Steuerung für Bose SoundTouch Geräte nach Cloud-Abschaltung.
            Open Source Projekt unter MIT Lizenz.
          </p>
          <div className="about-links">
            <a 
              href="https://github.com/scheilch/cloudtouch" 
              className="about-link"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
            <Link to="/licenses" className="about-link">
              Open-Source Lizenzen
            </Link>
          </div>
        </div>
      </motion.section>

      {/* Save Button */}
      <motion.div 
        className="save-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <button className="save-button" onClick={handleSaveSettings}>
          <span className="button-icon">💾</span>
          <span>Einstellungen speichern</span>
        </button>
      </motion.div>
    </div>
  )
}
