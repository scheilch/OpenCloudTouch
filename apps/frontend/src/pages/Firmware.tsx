import { useState } from "react";
import { motion } from "framer-motion";
import { Device } from "../components/DeviceSwiper";
import "./Firmware.css";

interface FirmwareProps {
  devices?: Device[];
}

export default function Firmware({ devices = [] }: FirmwareProps) {
  const [currentDeviceIndex] = useState(0);

  const currentDevice = devices[currentDeviceIndex];

  if (devices.length === 0 || !currentDevice) {
    return (
      <div className="empty-container">
        <p className="empty-message">Keine Geräte gefunden</p>
      </div>
    );
  }

  const getFirmwareStatus = (firmware?: string): "up-to-date" | "update-available" => {
    // Mock logic: versions ending with .6 are up-to-date
    const version = firmware?.split(".")[2] || "0";
    return parseInt(version) >= 12 ? "up-to-date" : "update-available";
  };

  const parseFirmwareVersion = (firmware?: string): string => {
    if (!firmware) return "Unknown";
    const parts = firmware.split(".");
    return `${parts[0]}.${parts[1]}.${parts[2]}`;
  };

  return (
    <div className="page firmware-page">
      <h1 className="page-title">Firmware Updates</h1>

      {/* Current Device Firmware */}
      <motion.section
        className="current-device-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h2 className="section-title">Aktuelles Gerät</h2>
        <div className="firmware-card current">
          <div className="firmware-card-header">
            <span className="firmware-icon">📱</span>
            <div className="firmware-device-info">
              <h3 className="firmware-device-name">{currentDevice.name}</h3>
              <span className="firmware-device-model">
                {currentDevice.model || "Unknown Model"}
              </span>
            </div>
          </div>

          <div className="firmware-details">
            <div className="firmware-detail-row">
              <span className="detail-label">Aktuelle Version:</span>
              <span className="detail-value">
                {parseFirmwareVersion(currentDevice.firmware)}
              </span>
            </div>
            <div className="firmware-detail-row">
              <span className="detail-label">Status:</span>
              <span
                className={`status-badge ${getFirmwareStatus(currentDevice.firmware)}`}
              >
                {getFirmwareStatus(currentDevice.firmware) === "up-to-date" ? (
                  <>✓ Aktuell</>
                ) : (
                  <>⚠️ Update verfügbar</>
                )}
              </span>
            </div>
          </div>
        </div>
      </motion.section>

      {/* All Devices Overview */}
      <motion.section
        className="all-devices-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <h2 className="section-title">Alle Geräte</h2>
        <div className="firmware-list">
          {devices.map((device, index) => {
            const status = getFirmwareStatus(device.firmware);

            return (
              <motion.div
                key={device.device_id}
                className="firmware-item"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.05 * index }}
              >
                <div className="firmware-item-left">
                  <span className="firmware-item-icon">
                    {device.model?.includes("ST300")
                      ? "📺"
                      : device.model?.includes("ST30")
                        ? "🔊"
                        : "📻"}
                  </span>
                  <div className="firmware-item-info">
                    <span className="firmware-item-name">{device.name}</span>
                    <span className="firmware-item-model">{device.model}</span>
                  </div>
                </div>

                <div className="firmware-item-right">
                  <span className="firmware-version">
                    {parseFirmwareVersion(device.firmware)}
                  </span>
                  <span className={`status-icon ${status}`}>
                    {status === "up-to-date" ? "✓" : "⚠️"}
                  </span>
                </div>
              </motion.div>
            );
          })}
        </div>
      </motion.section>

      {/* Warning Box */}
      <motion.div
        className="warning-box"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="warning-icon">⚠️</div>
        <div className="warning-content">
          <h3 className="warning-title">Experimentelle Funktion</h3>
          <p className="warning-text">
            Firmware-Updates sind experimentell und können Ihr Gerät
            beschädigen. Verwenden Sie nur offizielle Firmware-Dateien von Ihrem
            Gerätehersteller. Der Upload ist derzeit deaktiviert.
          </p>
        </div>
      </motion.div>

      {/* Upload Section (Disabled) */}
      <motion.section
        className="upload-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h2 className="section-title">Firmware hochladen</h2>
        <div className="upload-card disabled">
          <div className="upload-icon">📤</div>
          <p className="upload-text">
            Firmware-Upload ist derzeit nicht verfügbar
          </p>
          <button className="upload-button" disabled>
            <span className="button-icon">📁</span>
            <span>Firmware auswählen</span>
          </button>
          <p className="upload-hint">
            Diese Funktion wird in zukünftigen Versionen aktiviert
          </p>
        </div>
      </motion.section>

      {/* Info Box */}
      <motion.div
        className="info-box"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        <div className="info-icon">ℹ️</div>
        <div className="info-content">
          <h4 className="info-title">Firmware-Hinweise</h4>
          <ul className="info-list">
            <li>
              Firmware-Updates sollten nur bei Problemen durchgeführt werden
            </li>
            <li>
              Während des Updates darf das Gerät nicht ausgeschaltet werden
            </li>
            <li>Der Update-Prozess kann 5-10 Minuten dauern</li>
            <li>Nach dem Update startet das Gerät automatisch neu</li>
          </ul>
        </div>
      </motion.div>
    </div>
  );
}
