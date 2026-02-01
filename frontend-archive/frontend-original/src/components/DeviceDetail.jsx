import './DeviceDetail.css'
import SourceSelector from './SourceSelector'
import VolumeControl from './VolumeControl'

function DeviceDetail({ device }) {
  return (
    <div className="device-detail">
      {/* Device Icon */}
      <div className="device-icon-container">
        <svg 
          className="device-icon" 
          width="60" 
          height="60" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="1"
        >
          <path d="M9 18V5l12-2v13M9 18c0 1.657-1.343 3-3 3s-3-1.343-3-3 1.343-3 3-3 3 1.343 3 3zm12-3c0 1.657-1.343 3-3 3s-3-1.343-3-3 1.343-3 3-3 3 1.343 3 3z" />
        </svg>
      </div>

      {/* Device Name */}
      <h2 className="device-name">{device.name}</h2>
      
      {/* Device Model */}
      <p className="device-model">{device.model}</p>

      {/* Source Selector */}
      <SourceSelector />

      {/* Volume Control */}
      <VolumeControl />

      {/* Device Info */}
      <div className="device-info">
        <div className="device-info-item">
          <span className="info-label">IP-Adresse</span>
          <span className="info-value">{device.ip}</span>
        </div>
        <div className="device-info-item">
          <span className="info-label">Firmware</span>
          <span className="info-value">
            {(() => {
              const fw = device.firmware_version || '';
              // Trim bei 'epdbuild', 'hepdswbld' oder '-'
              const match = fw.match(/^([\d.]+)/);
              return match ? match[1] : fw;
            })()}
          </span>
        </div>
      </div>
    </div>
  )
}

export default DeviceDetail
