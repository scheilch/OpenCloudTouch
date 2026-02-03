import "./VolumeSlider.css";

export default function VolumeSlider({
  volume,
  onVolumeChange,
  muted,
  onMuteToggle,
}) {
  return (
    <div className="volume-slider">
      <button
        className={`volume-mute ${muted ? "muted" : ""}`}
        onClick={onMuteToggle}
        aria-label={muted ? "Unmute" : "Mute"}
      >
        {muted ? "🔇" : volume > 50 ? "🔊" : volume > 0 ? "🔉" : "🔈"}
      </button>
      <input
        type="range"
        className="volume-input"
        min="0"
        max="100"
        value={volume}
        onChange={(e) => onVolumeChange(parseInt(e.target.value))}
        disabled={muted}
        aria-label="Volume"
      />
      <span className="volume-value">{volume}%</span>
    </div>
  );
}
