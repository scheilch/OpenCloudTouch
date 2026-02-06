import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:4173', // Frontend (Vite Preview)
    specPattern: 'tests/e2e/**/*.cy.{js,jsx,ts,tsx}',
    excludeSpecPattern: 'tests/real/**/*.cy.{js,jsx,ts,tsx}', // Exclude real device tests from default runs
    supportFile: 'tests/e2e/support/e2e.js',
    fixturesFolder: false, // No fixtures needed (backend provides mocks)
    screenshotsFolder: 'tests/e2e/screenshots',
    videosFolder: 'tests/e2e/videos',
    
    env: {
      // API URL set via CYPRESS_API_URL env var by run-e2e-tests.ps1
      // Default: http://localhost:7778/api (test port)
      apiUrl: 'http://localhost:7778/api'
    },
    
    setupNodeEvents(on, config) {
      // Future: Code Coverage Plugin
    },
    
    viewportWidth: 1280,
    viewportHeight: 720,
    defaultCommandTimeout: 8000,   // Reduced from 10s (fail faster)
    requestTimeout: 5000,           // API requests should be fast
    responseTimeout: 5000,
    pageLoadTimeout: 30000,         // 30s for page load (includes build assets)
    execTimeout: 60000,
    taskTimeout: 60000,
    video: false,                   // Disable video to speed up tests
    screenshotOnRunFailure: true,   // Capture screenshot on failure
  },
})
