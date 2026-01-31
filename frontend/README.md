# SoundTouchBridge Frontend

React + Vite SPA für die SoundTouchBridge Web-UI.

## 📂 Structure

```
frontend/
├── src/               # React source code
│   ├── components/    # UI components
│   ├── hooks/         # Custom React hooks
│   ├── services/      # API services
│   └── App.jsx        # Main app component
├── tests/             # Frontend tests
│   └── test_frontend_empty_state.py  # Regression tests
├── index.html         # Entry HTML
├── package.json       # Dependencies
├── vite.config.js     # Vite configuration
└── vitest.config.js   # Test configuration
```

## 🚀 Installation

```bash
cd frontend
npm install
```

## 🔧 Development

```bash
npm run dev
```

UI läuft auf: http://localhost:3000

API-Calls werden zu http://localhost:8000 proxied (siehe vite.config.js).

## 📦 Build

```bash
npm run build
```

Build-Output: `dist/`

## 🧪 Tests

Frontend tests befinden sich in `tests/`:

```bash
# Python backend integration tests
cd ..
python -m pytest frontend/tests/ -v
```

**Note**: `test_frontend_empty_state.py` ist ein Backend-Integration-Test,
der das Frontend-Verhalten über die API testet.

## 🏗️ Docker Multi-stage Build

Frontend wird im Docker Build kompiliert:

```dockerfile
# Stage 1: Frontend build (siehe ../backend/Dockerfile)
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend + Frontend assets
FROM python:3.11-slim
COPY --from=frontend-builder /app/frontend/dist /app/static
```

## 📚 Related Docs

- [Main README](../README.md)
- [Backend README](../backend/README.md)
- [Deployment README](../deployment/README.md)
