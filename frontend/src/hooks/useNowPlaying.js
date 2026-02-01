import { useState, useEffect } from 'react';
import { MOCK_NOW_PLAYING } from '../mock/data';

export function useNowPlaying(deviceId) {
  const [nowPlaying, setNowPlaying] = useState(null);

  useEffect(() => {
    if (!deviceId) return;

    // Initial load
    setNowPlaying({ ...MOCK_NOW_PLAYING, device_id: deviceId });

    // Simulate WebSocket updates every 5 seconds
    const interval = setInterval(() => {
      setNowPlaying(prev => ({
        ...prev,
        position: prev ? prev.position + 5 : 0
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, [deviceId]);

  return nowPlaying;
}
