import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import "./Settings.css";

export default function Settings() {
  const [manualIPs, setManualIPs] = useState([]);
  const [newIP, setNewIP] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Fetch manual IPs from backend
  useEffect(() => {
    fetchManualIPs();
  }, []);

  const fetchManualIPs = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/settings/manual-ips");
      if (!response.ok) throw new Error("Failed to fetch IPs");
      const data = await response.json();
      setManualIPs(data.ips || []);
      setError("");
    } catch (err) {
      setError(`Fehler beim Laden: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const validateIP = (ip) => {
    const parts = ip.split(".");
    if (parts.length !== 4) return false;
    return parts.every((part) => {
      const num = parseInt(part, 10);
      return num >= 0 && num <= 255 && part === num.toString();
    });
  };

  const handleAddIP = async (e) => {
    e.preventDefault();
    const trimmedIP = newIP.trim();

    if (!trimmedIP) {
      setError("Bitte geben Sie eine IP-Adresse ein");
      return;
    }

    if (!validateIP(trimmedIP)) {
      setError("Ungültige IP-Adresse (Format: 192.168.1.10)");
      return;
    }

    if (manualIPs.includes(trimmedIP)) {
      setError("Diese IP-Adresse existiert bereits");
      return;
    }

    try {
      const response = await fetch("/api/settings/manual-ips", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ip: trimmedIP }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to add IP");
      }

      setManualIPs([...manualIPs, trimmedIP]);
      setNewIP("");
      setSuccess(`IP ${trimmedIP} hinzugefügt`);
      setError("");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(`Fehler: ${err.message}`);
    }
  };

  const handleDeleteIP = async (ipToDelete) => {
    try {
      const response = await fetch(`/api/settings/manual-ips/${ipToDelete}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete IP");
      }

      setManualIPs(manualIPs.filter((ip) => ip !== ipToDelete));
      setSuccess(`IP ${ipToDelete} entfernt`);
      setError("");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(`Fehler beim Löschen: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner" />
        <p className="loading-message">Einstellungen werden geladen...</p>
      </div>
    );
  }

  return (
    <div className="page settings-page">
      <h1 className="page-title">Einstellungen</h1>

      {/* Manual IPs Section */}
      <motion.section
        className="settings-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h2 className="section-title">
          <span className="section-icon">🌐</span>
          Manuelle Geräte-IPs
        </h2>

        <div className="settings-card">
          <p className="section-description">
            Fügen Sie IP-Adressen von SoundTouch-Geräten manuell hinzu, falls
            die automatische Erkennung nicht funktioniert.
          </p>

          {/* Add IP Form */}
          <form onSubmit={handleAddIP} className="ip-add-form">
            <input
              type="text"
              value={newIP}
              onChange={(e) => setNewIP(e.target.value)}
              placeholder="192.168.1.10"
              className="ip-input"
              pattern="^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
            />
            <button type="submit" className="btn btn-primary">
              + Hinzufügen
            </button>
          </form>

          {/* Error/Success Messages */}
          {error && <div className="alert alert-error">{error}</div>}
          {success && <div className="alert alert-success">{success}</div>}

          {/* IP List */}
          <div className="ip-list">
            {manualIPs.length === 0 ? (
              <p className="empty-message">Keine manuellen IPs konfiguriert</p>
            ) : (
              <ul className="ip-items">
                {manualIPs.map((ip) => (
                  <motion.li
                    key={ip}
                    className="ip-item"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                  >
                    <span className="ip-address">{ip}</span>
                    <button
                      onClick={() => handleDeleteIP(ip)}
                      className="btn btn-delete"
                      title="IP entfernen"
                    >
                      ×
                    </button>
                  </motion.li>
                ))}
              </ul>
            )}
          </div>

          {/* Info Box */}
          <div className="info-box">
            <strong>ℹ️ Hinweis:</strong>
            <p>
              Nach dem Hinzufügen oder Entfernen von IPs wird die
              Geräteerkennung automatisch neu gestartet. Die Geräte erscheinen
              dann auf der Startseite.
            </p>
          </div>
        </div>
      </motion.section>
    </div>
  );
}
