import { useState, useEffect } from 'react';
import { MOCK_RADIO_STATIONS } from '../mock/data';

export function useRadioSearch() {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    setLoading(true);

    // Debounce: 300ms delay
    const timeout = setTimeout(() => {
      const filtered = MOCK_RADIO_STATIONS.filter(station =>
        station.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        station.tags.toLowerCase().includes(searchQuery.toLowerCase()) ||
        station.country.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setResults(filtered);
      setLoading(false);
    }, 300);

    return () => clearTimeout(timeout);
  }, [searchQuery]);

  return { searchQuery, setSearchQuery, results, loading };
}
