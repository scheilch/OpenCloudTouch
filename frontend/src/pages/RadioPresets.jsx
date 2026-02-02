import { useState, useEffect } from 'react'
import { useDevices } from '../hooks/useDevices'
import { useNowPlaying } from '../hooks/useNowPlaying'
import { usePresets } from '../hooks/usePresets'
import DeviceSwiper from '../components/DeviceSwiper'
import NowPlaying from '../components/NowPlaying'
import PresetButton from '../components/PresetButton'
import RadioSearch from '../components/RadioSearch'
import VolumeSlider from '../components/VolumeSlider'
import './RadioPresets.css'

export default function RadioPresets() {
  const { devices, loading, error } = useDevices()
  const [currentDeviceIndex, setCurrentDeviceIndex] = useState(0)
  const [searchOpen, setSearchOpen] = useState(false)
  const [assigningPreset, setAssigningPreset] = useState(null)
  const [volume, setVolume] = useState(45)
  const [muted, setMuted] = useState(false)

  const currentDevice = devices[currentDeviceIndex]
  const nowPlaying = useNowPlaying(currentDevice?.device_id)
  const { presets, assignPreset, clearPreset } = usePresets(currentDevice?.device_id)

  // Update presets when device changes
  useEffect(() => {
    if (currentDevice) {
      // Presets hook automatically updates via device_id dependency
    }
  }, [currentDevice])

  const handleAssignClick = (presetNumber) => {
    setAssigningPreset(presetNumber)
    setSearchOpen(true)
  }

  const handleStationSelect = (station) => {
    if (assigningPreset) {
      assignPreset(assigningPreset, station)
      setAssigningPreset(null)
    }
  }

  const handlePlayPreset = (presetNumber) => {
    console.log('Play preset', presetNumber, presets[presetNumber])
    // Mock: Would trigger API call
  }

  const handleClearPreset = (presetNumber) => {
    clearPreset(presetNumber)
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner" />
        <p className="loading-message">Geräte werden geladen...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-container">
        <p className="error-message">{error}</p>
        <button className="retry-button">Erneut versuchen</button>
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
    <div className="page radio-presets-page">
      <h1 className="page-title">Radio Presets</h1>

      {/* Swipeable Device Cards */}
      <DeviceSwiper
        devices={devices}
        currentIndex={currentDeviceIndex}
        onIndexChange={setCurrentDeviceIndex}
      >
        <div className="device-card" data-test="device-card">
          <div className="device-card-header">
            <h2 className="device-name" data-test="device-name">{currentDevice.name}</h2>
            <span className="device-model" data-test="device-model">{currentDevice.model}</span>
          </div>
          
          <NowPlaying nowPlaying={nowPlaying} />
          
          <VolumeSlider
            volume={volume}
            onVolumeChange={setVolume}
            muted={muted}
            onMuteToggle={() => setMuted(!muted)}
          />
        </div>
      </DeviceSwiper>

      {/* Presets for Current Device */}
      <div className="presets-section">
        <h3 className="section-title">Gespeicherte Sender</h3>
        <div className="presets-grid">
          {[1, 2, 3, 4, 5, 6].map(num => (
            <PresetButton
              key={num}
              number={num}
              preset={presets[num]}
              onAssign={() => handleAssignClick(num)}
              onClear={() => handleClearPreset(num)}
              onPlay={() => handlePlayPreset(num)}
            />
          ))}
        </div>
      </div>

      {/* Radio Search Modal */}
      <RadioSearch
        isOpen={searchOpen}
        onClose={() => {
          setSearchOpen(false)
          setAssigningPreset(null)
        }}
        onStationSelect={handleStationSelect}
      />
    </div>
  )
}
