import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './InitialSettings.css'

export default function InitialSettings() {
  const [ipList, setIpList] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const navigate = useNavigate()

  // Load existing IPs on mount
  useEffect(() => {
    fetchManualIPs()
  }, [])

  const fetchManualIPs = async () => {
    try {
      const response = await fetch('/api/settings/manual-ips')
      if (response.ok) {
        const data = await response.json()
        if (data.ips && data.ips.length > 0) {
          setIpList(data.ips.join(', '))
        }
      }
    } catch (err) {
      console.error('Failed to fetch manual IPs:', err)
    }
  }

  const handleSave = async () => {
    setIsSaving(true)
    setError(null)
    setSuccess(false)

    // Parse IPs (comma or newline separated)
    const ips = ipList
      .split(/[,\n]/)
      .map(ip => ip.trim())
      .filter(ip => ip.length > 0)

    // Basic IP validation
    const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/
    const invalidIPs = ips.filter(ip => !ipRegex.test(ip))
    
    if (invalidIPs.length > 0) {
      setError(`Ungültige IP-Adressen: ${invalidIPs.join(', ')}`)
      setIsSaving(false)
      return
    }

    try {
      const response = await fetch('/api/settings/manual-ips', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ips })
      })

      if (!response.ok) {
        throw new Error('Failed to save IPs')
      }

      setSuccess(true)
      
      // Navigate back to home after short delay
      setTimeout(() => {
        navigate('/')
      }, 1500)
    } catch (err) {
      setError('Fehler beim Speichern der IP-Adressen')
      console.error(err)
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="initial-settings">
      <div className="initial-settings-content">
        <button 
          className="back-button"
          onClick={() => navigate('/')}
          aria-label="Zurück"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"/>
          </svg>
          Zurück
        </button>

        <h1>Manuelle IP-Konfiguration</h1>
        <p className="settings-description">
          Wenn die automatische Geräteerkennung nicht funktioniert, können Sie die IP-Adressen 
          Ihrer SoundTouch-Geräte hier manuell eintragen.
        </p>

        <div className="settings-section">
          <label htmlFor="ip-list">
            IP-Adressen (eine pro Zeile oder kommagetrennt)
          </label>
          <textarea
            id="ip-list"
            value={ipList}
            onChange={(e) => setIpList(e.target.value)}
            placeholder="Beispiel:&#10;192.168.1.100&#10;192.168.1.101&#10;192.168.1.102"
            rows={6}
            disabled={isSaving}
          />
          
          <div className="settings-hint">
            <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"/>
            </svg>
            <span>
              Tipp: Die IP-Adresse Ihrer Geräte finden Sie in der Bose SoundTouch App 
              unter Einstellungen → Info oder in Ihrem Router.
            </span>
          </div>
        </div>

        {error && (
          <div className="settings-error">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd"/>
            </svg>
            {error}
          </div>
        )}

        {success && (
          <div className="settings-success">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
            </svg>
            IP-Adressen gespeichert! Kehre zur Startseite zurück...
          </div>
        )}

        <div className="settings-actions">
          <button 
            className="cancel-button"
            onClick={() => navigate('/')}
            disabled={isSaving}
          >
            Abbrechen
          </button>
          <button 
            className="save-button"
            onClick={handleSave}
            disabled={isSaving || ipList.trim().length === 0}
          >
            {isSaving ? 'Speichere...' : 'Speichern & Zurück'}
          </button>
        </div>

        <div className="settings-footer">
          <p>
            Nach dem Speichern kehren Sie zur Startseite zurück und können dort 
            auf "Jetzt Geräte suchen" klicken, um die Discovery zu starten.
          </p>
        </div>
      </div>
    </div>
  )
}
