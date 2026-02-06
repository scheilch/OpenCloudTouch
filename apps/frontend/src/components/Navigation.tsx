import { NavLink } from "react-router-dom";
import "./Navigation.css";

export default function Navigation() {
  return (
    <nav className="nav">
      <div className="nav-container">
        <NavLink to="/" className="nav-link">
          <span className="nav-icon">📻</span>
          <span className="nav-label">Presets</span>
        </NavLink>
        <NavLink to="/local" className="nav-link">
          <span className="nav-icon">🎵</span>
          <span className="nav-label">Control</span>
        </NavLink>
        <NavLink to="/multiroom" className="nav-link">
          <span className="nav-icon">🔊</span>
          <span className="nav-label">Zones</span>
        </NavLink>
        <NavLink to="/firmware" className="nav-link">
          <span className="nav-icon">⚙️</span>
          <span className="nav-label">Firmware</span>
        </NavLink>
        <NavLink to="/settings" className="nav-link">
          <span className="nav-icon">⚡</span>
          <span className="nav-label">Settings</span>
        </NavLink>
      </div>
    </nav>
  );
}
