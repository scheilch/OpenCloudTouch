# 04 - Frontend Code Review

**Stand**: 2026-02-12  
**Analyst**: Principal Software Engineer (AI-assisted)

---

## [P2] [ARCHITECTURE] useState für Server Data statt React Query

**Datei:** `apps/frontend/src/App.tsx`  
**Zeilen:** 89-116

**Problem:**
```tsx
function App() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDevices = async (): Promise<Device[]> => {
    try {
      setError(null);
      setIsLoading(true);
      const response = await fetch("/api/devices");
      // ... manual state management
    } catch (err) {
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };
```

**Warum schlecht:**
- 2025 Best Practice für Server-Data: TanStack Query (React Query) oder SWR
- Manuelles state management für loading/error ist fehleranfällig
- Kein automatisches Cache-Invalidation, Refetching, Deduplication
- Kein Optimistic Updates Support

**Recherche:**
- TanStack Query v5: https://tanstack.com/query/latest
- React 19 Best Practices: Server-Data über Query-Libraries
- Bundle Size: @tanstack/react-query ~13KB gzipped (akzeptabel)

**Fix:**
```tsx
// api/hooks.ts (NEU)
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function useDevices() {
  return useQuery({
    queryKey: ['devices'],
    queryFn: async () => {
      const response = await fetch('/api/devices');
      if (!response.ok) throw new Error('Failed to fetch devices');
      const data = await response.json();
      return data.devices as Device[];
    },
    staleTime: 30_000, // 30 seconds
  });
}

// In App.tsx:
function App() {
  const { data: devices = [], isLoading, error, refetch } = useDevices();
  // ... rest
}
```

**Aufwand:** 2h (Query-Library einführen + alle API-Calls umstellen)  
**Hinweis:** Niedrigere Priorität da aktueller Code funktioniert

---

## [P2] [UX] Confirm Dialog mit window.confirm

**Datei:** `apps/frontend/src/pages/RadioPresets.tsx`  
**Zeile:** 105

**Problem:**
```tsx
const handleClearPreset = async (presetNumber: number) => {
  // Confirm deletion
  if (!confirm(`Möchten Sie Preset ${presetNumber} wirklich löschen?`)) {
    return;
  }
  // ...
};
```

**Warum schlecht:**
- `window.confirm()` blockt den UI-Thread
- Ist nicht stylebar (bricht aus dem Design aus)
- Nicht barrierefrei (Screen Reader Support mangelhaft)
- Modern UX: Modal-Dialoge oder Confirmation Toasts

**Fix:**
```tsx
// Variante A: Confirmation Modal Component
const [confirmOpen, setConfirmOpen] = useState(false);
const [presetToDelete, setPresetToDelete] = useState<number | null>(null);

const handleClearPreset = (presetNumber: number) => {
  setPresetToDelete(presetNumber);
  setConfirmOpen(true);
};

const handleConfirmDelete = async () => {
  if (presetToDelete === null) return;
  // ... actual delete logic
  setConfirmOpen(false);
  setPresetToDelete(null);
};

// In render:
<ConfirmDialog
  isOpen={confirmOpen}
  title="Preset löschen"
  message={`Möchten Sie Preset ${presetToDelete} wirklich löschen?`}
  onConfirm={handleConfirmDelete}
  onCancel={() => setConfirmOpen(false)}
/>
```

**Aufwand:** 1h (ConfirmDialog Component erstellen + einbauen)

---

## [P2] [BUG] Settings POST vs PUT mismatch mit Backend

**Datei:** `apps/frontend/src/pages/Settings.tsx`  
**Zeilen:** 63-70

**Problem:**
```tsx
const response = await fetch("/api/settings/manual-ips", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ ip: trimmedIP }),  // ⚠️ Falsches Schema
});
```

**Warum schlecht:**
- Backend erwartet `SetManualIPsRequest` mit `{ ips: string[] }`
- Frontend sendet `{ ip: string }` (einzelne IP)
- Resultat: Validation Error oder unerwartetes Verhalten

**Fix:**
Option A - Frontend anpassen für Replace-Semantik:
```tsx
const handleAddIP = async () => {
  // ... validation
  const newList = [...manualIPs, trimmedIP];
  
  const response = await fetch("/api/settings/manual-ips", {
    method: "POST",  // oder PUT wenn Backend geändert
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ips: newList }),
  });
  // ...
};
```

Option B - Backend anpassen für einzelne IP:
```python
# Backend: Neuer Endpoint für einzelne IP
@router.post("/manual-ips/add", response_model=ManualIPsResponse)
async def add_single_manual_ip(ip: str, ...):
    """Add a single IP to the list."""
```

**Aufwand:** 30min

---

## [P3] [MAINTAINABILITY] API Base URL dupliziert

**Dateien:** 
- `apps/frontend/src/api/presets.ts:7`
- `apps/frontend/src/components/RadioSearch.tsx:20`

**Problem:**
```tsx
// presets.ts:
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:7777";

// RadioSearch.tsx:
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:7777";
```

**Warum schlecht:**
- DRY-Verletzung: Gleiche Konstante an 2+ Stellen
- Änderungen müssen an mehreren Stellen erfolgen

**Fix:**
```tsx
// api/config.ts (NEU)
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

// Für relative URLs in Production (wenn SPA vom gleichen Origin geserved wird):
export function getApiUrl(path: string): string {
  const base = API_BASE_URL || "";  // Leerer String = relativer Pfad
  return `${base}${path}`;
}

// Nutzung:
// presets.ts:
import { getApiUrl } from './config';
const response = await fetch(getApiUrl('/api/presets/set'), ...);
```

**Aufwand:** 30min

---

## [P3] [PERFORMANCE] RadioSearch: Debounce mit setTimeout

**Datei:** `apps/frontend/src/components/RadioSearch.tsx`  
**Zeilen:** 42-68

**Problem:**
```tsx
const debounceRef = useRef<number | null>(null);

const handleSearch = async (searchQuery: string) => {
  // ...
  if (debounceRef.current !== null) {
    window.clearTimeout(debounceRef.current);
  }

  debounceRef.current = window.setTimeout(async () => {
    // search logic
  }, 300);
};
```

**Analyse:**
- Funktioniert, aber custom debounce ist fehleranfällig
- `useDeferredValue` (React 19) oder `lodash.debounce` sind stabiler
- AbortController wird korrekt verwendet ✓

**Optional Fix (wenn Zeit):**
```tsx
import { useDeferredValue, useEffect, useState } from 'react';

export default function RadioSearch({ ... }) {
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);
  const [results, setResults] = useState<RadioStation[]>([]);
  
  useEffect(() => {
    if (!deferredQuery.trim()) {
      setResults([]);
      return;
    }
    
    const controller = new AbortController();
    
    fetch(`/api/radio/search?q=${encodeURIComponent(deferredQuery)}`, {
      signal: controller.signal
    })
      .then(res => res.json())
      .then(data => setResults(data.stations || []))
      .catch(() => {});
    
    return () => controller.abort();
  }, [deferredQuery]);
  
  // ...
}
```

**Aufwand:** 30min  
**Priorität:** Niedrig (aktueller Code funktioniert)

---

## [P3] [ACCESSIBILITY] Fehlende ARIA Labels

**Datei:** `apps/frontend/src/components/RadioSearch.tsx`  
**Zeilen:** 110-119

**Problem:**
```tsx
<input
  type="search"
  className="search-input"
  placeholder="Sender suchen..."
  value={query}
  onChange={(e) => handleSearch(e.target.value)}
  autoFocus
/>
```

**Warum schlecht:**
- Kein `aria-label` oder `<label>` Element
- Screen Reader können Zweck nicht erkennen
- WCAG 2.1 AA Verletzung

**Fix:**
```tsx
<label htmlFor="radio-search-input" className="sr-only">
  Radiosender suchen
</label>
<input
  id="radio-search-input"
  type="search"
  className="search-input"
  placeholder="Sender suchen..."
  value={query}
  onChange={(e) => handleSearch(e.target.value)}
  autoFocus
  aria-describedby="search-results-count"
/>
<span id="search-results-count" className="sr-only">
  {results.length > 0 
    ? `${results.length} Sender gefunden` 
    : query ? "Keine Sender gefunden" : ""}
</span>
```

**Aufwand:** 15min

---

## [P3] [UX] Missing Loading States in DeviceSwiper

**Datei:** `apps/frontend/src/components/DeviceSwiper.tsx`

**Analyse:**
Der DeviceSwiper hat keine Loading-Indikation wenn:
- Zwischen Devices gewechselt wird (schnell, aber merkbar)
- Device-Daten aktualisiert werden

**Current:**
- Smooth animation vorhanden ✓
- Kein Loading-Skeleton für Content

**Optional Enhancement:**
```tsx
// Loading-Skeleton für Device-Details
{isLoading ? (
  <div className="device-card-skeleton">
    <div className="skeleton-line skeleton-name" />
    <div className="skeleton-line skeleton-model" />
  </div>
) : (
  children
)}
```

**Aufwand:** 30min  
**Priorität:** Nice-to-have

---

## [OK] Positive Findings

### DeviceSwiper.tsx | 136 Zeilen | ✓ OK
- Framer Motion korrekt verwendet
- Swipe-Gesten funktionieren
- Keyboard Navigation vorhanden (Pfeiltasten fehlen aber)

### Navigation.tsx | 35 Zeilen | ✓ OK
- NavLink mit active states
- Semantisches `<nav>` Element
- Icons mit Labels (Accessibility)

### NowPlaying.tsx | 47 Zeilen | ✓ OK
- Empty state vorhanden
- Alt-Text für Bilder (leer aber vorhanden)

### ToastContext.tsx | ✓ OK
- Context Pattern korrekt
- Auto-dismiss implementiert

---

## Vollständigkeits-Nachweis

| Bereich | Dateien | Status | Findings |
|---------|---------|--------|----------|
| Root | 3 | ✓ | P2: 1 |
| api/ | 1 | ✓ | P3: 1 |
| components/ | 9 | ✓ | P3: 2 |
| pages/ | 6 | ✓ | P2: 2 |
| contexts/ | 1 | ✓ | OK |
| utils/ | 2 | ✓ | OK |

**Total:** 22 Dateien, ~1800 Zeilen, 6 Findings (P2: 3, P3: 3)

---

## 💾 SESSION-STATE

**Fortschritt:** Frontend komplett analysiert
**Nächste Datei:** Architecture Analysis
