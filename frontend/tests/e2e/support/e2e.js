/**
 * Cypress E2E Support File
 * Loads custom commands and global setup
 */

// Import commands
import './commands'

// Global before hook - Setup default mocks
beforeEach(() => {
  // Default: No devices
  cy.setupMocks({ deviceCount: 0, manualIPs: [] })
})
