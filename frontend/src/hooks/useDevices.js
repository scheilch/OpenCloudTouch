import { useState, useEffect } from 'react';
import { MOCK_DEVICES } from '../mock/data';

export function useDevices() {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Simulate API call with 300ms delay
    const timeout = setTimeout(() => {
      setDevices(MOCK_DEVICES);
      setLoading(false);
    }, 300);

    return () => clearTimeout(timeout);
  }, []);

  const retry = () => {
    setLoading(true);
    setError(null);
    setTimeout(() => {
      setDevices(MOCK_DEVICES);
      setLoading(false);
    }, 300);
  };

  return { devices, loading, error, retry };
}
