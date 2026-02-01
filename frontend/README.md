# CloudTouch Frontend

Modern React SPA für die lokale Steuerung von Bose SoundTouch Geräten.

## Features

- **Swipeable Device Cards**: Intuitive Geräteauswahl mit Wischgesten
- **Empty State**: Benutzerführung beim ersten App-Start
- **Radio Presets**: Radiosender auf Preset-Tasten (1-6) verwalten
- **Local Control**: Lautstärke, Quellen, Playback-Steuerung
- **MultiRoom**: Zonen-Management für synchrone Wiedergabe
- **Firmware**: Geräte-Informationen und Firmware-Status
- **Settings**: Gerätekonfiguration und Discovery-Einstellungen
- **Licenses**: Open-Source Lizenzen aller verwendeten Bibliotheken

## Tech Stack

- **React** 18.2.0 - UI Framework
- **React Router** 6.20.0 - Client-side Routing
- **Framer Motion** 10.16.16 - Animations
- **Vite** 5.0.8 - Build Tool
- **Vitest** 1.0.4 - Testing Framework

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm test

# Run tests with UI
npm run test:ui

# Generate coverage report
npm run test:coverage
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable components
│   │   ├── EmptyState.jsx
│   │   ├── DeviceSwiper.jsx
│   │   └── Navigation.jsx
│   ├── pages/            # Page components
│   │   ├── RadioPresets.jsx
│   │   ├── LocalControl.jsx
│   │   ├── MultiRoom.jsx
│   │   ├── Firmware.jsx
│   │   ├── Settings.jsx
│   │   └── Licenses.jsx
│   ├── hooks/            # Custom React hooks
│   │   └── useDevices.js
│   ├── App.jsx           # Main app component
│   └── main.jsx          # Entry point
├── tests/                # Test files
│   ├── setup.js
│   ├── App.test.jsx
│   ├── EmptyState.test.jsx
│   └── Licenses.test.jsx
└── public/               # Static assets
```

## API Integration

Das Frontend kommuniziert mit dem CloudTouch Backend über folgende Endpoints:

- `GET /api/devices` - Liste aller Geräte
- `POST /api/devices/discover` - Gerätesuche triggern
- `GET /api/devices/{id}` - Gerätedetails
- `GET /api/devices/{id}/presets` - Presets eines Geräts
- `PUT /api/devices/{id}/presets/{num}` - Preset setzen
- `GET /api/radio/search` - Radiosender suchen

## Migration von Original-Frontend

Das Original-Frontend wurde nach `frontend-archive/frontend-original/` verschoben.
Die Swipe-Variante aus `prototypes/soundtouch-spa-swipe/` ist jetzt das produktive Frontend.

### Wichtigste Änderungen:

1. **Empty State** beim ersten Start (keine Geräte gefunden)
2. **API-Integration** mit Backend
3. **Licenses-Seite** für Open-Source Compliance
4. **Device Prop Passing** für konsistente Datenhaltung
5. **Test-Setup** mit Vitest und Testing Library

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## License

MIT License - siehe [Licenses](/licenses) Page in der App

---

**CloudTouch** - Lokale Steuerung für Bose SoundTouch
