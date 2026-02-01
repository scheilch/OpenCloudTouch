import { useState } from 'react';
import { MOCK_PRESET_MAPPING } from '../mock/data';

export function usePresets(deviceId) {
  const [presets, setPresets] = useState(MOCK_PRESET_MAPPING[deviceId] || {});
  const [selectedPreset, setSelectedPreset] = useState(null);

  const assignPreset = (presetNumber, station) => {
    setPresets(prev => ({
      ...prev,
      [presetNumber]: {
        station_uuid: station.stationuuid,
        station_name: station.name,
        station_url: station.url
      }
    }));
  };

  const clearPreset = (presetNumber) => {
    setPresets(prev => ({
      ...prev,
      [presetNumber]: null
    }));
  };

  return {
    presets,
    selectedPreset,
    setSelectedPreset,
    assignPreset,
    clearPreset
  };
}
