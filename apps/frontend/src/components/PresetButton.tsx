import "./PresetButton.css";

export interface Preset {
  station_name: string;
  // Add other preset fields as needed
}

interface PresetButtonProps {
  number: number;
  preset?: Preset | null;
  onAssign: () => void;
  onClear: () => void;
  onPlay: () => void;
}

export default function PresetButton({
  number,
  preset,
  onAssign,
  onClear,
  onPlay,
}: PresetButtonProps) {
  return (
    <div className="preset-button">
      {preset ? (
        <>
          <button className="preset-play" onClick={onPlay}>
            <span className="preset-number">{number}</span>
            <span className="preset-name">{preset.station_name}</span>
          </button>
          <button className="preset-clear" onClick={onClear} aria-label="Clear preset">
            ✕
          </button>
        </>
      ) : (
        <button className="preset-empty" onClick={onAssign}>
          <span className="preset-number">{number}</span>
          <span className="preset-placeholder">Preset zuweisen</span>
        </button>
      )}
    </div>
  );
}
