import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// Development Mock Mode: Intercept API calls when VITE_MOCK_MODE=true
if (import.meta.env.VITE_MOCK_MODE === 'true') {
  const { setupMockInterceptor } = await import('./mocks/interceptor.js');
  setupMockInterceptor();
  console.log('%c🎭 MOCK MODE ACTIVE', 'background: #ff9800; color: white; padding: 4px 8px; border-radius: 3px; font-weight: bold');
  console.log('%c📡 All /api/* calls will return mock data', 'color: #ff9800; font-weight: bold');
  console.log('%c💾 State persists in localStorage (key: ct-mock-state)', 'color: #999');
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
