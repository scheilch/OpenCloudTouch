/**
 * E2E Tests: Manual IP Configuration
 * Uses Cypress Intercept (NO Backend required!)
 */

describe('Manual IP Configuration', () => {
  describe('EmptyState - Modal Opening', () => {
    it('should display EmptyState welcome screen', () => {
      cy.setupMocks({ deviceCount: 0 })
      cy.visit('/welcome')
      
      cy.get('[data-test="empty-state"]').should('be.visible')
      cy.get('[data-test="welcome-title"]').should('be.visible').and('contain', 'Willkommen')
      cy.get('p').should('contain', 'Noch keine')
    })

    it('should open manual IP configuration modal', () => {
      cy.setupMocks({ deviceCount: 0 })
      cy.visit('/welcome')
      
      cy.openIPConfigModal()
      
      // Verify modal elements exist
      cy.get('[data-test="modal-title"]').should('contain', 'Manuelle IP-Konfiguration')
      cy.get('[data-test="ip-textarea"]').should('be.visible')
      cy.get('[data-test="save-button"]').should('be.visible')
      cy.get('[data-test="cancel-button"]').should('be.visible')
    })
  })

  describe('Single IP Configuration', () => {
    it('should save 1 IP and create 1 device', () => {
      const ips = ['192.168.1.50']
      
      cy.setupMocks({ deviceCount: 0 })
      cy.visit('/welcome')
      
      // Open modal and enter IP
      cy.openIPConfigModal()
      cy.saveIPsInModal(ips)
      cy.wait('@setManualIPs')
      
      // Verify modal closes
      cy.waitForModalClose()
      
      // Trigger discovery
      cy.setupMocks({ deviceCount: ips.length, manualIPs: ips })
      cy.get('[data-test="discover-button"]').click()
      cy.wait('@syncDevices')
      cy.wait('@getDevices')
      
      // Verify redirect to dashboard
      cy.url().should('eq', Cypress.config().baseUrl + '/')
      cy.get('[data-test="device-card"]').should('be.visible')
    })
  })

  describe('Multiple IPs Configuration', () => {
    it('should save 2 IPs and create 2 devices', () => {
      const ips = ['192.168.1.50', '192.168.1.51']
      
      cy.setupMocks({ deviceCount: 0 })
      cy.visit('/welcome')
      
      cy.openIPConfigModal()
      cy.saveIPsInModal(ips)
      cy.wait('@setManualIPs')
      cy.waitForModalClose()
      
      // Trigger discovery
      cy.setupMocks({ deviceCount: ips.length, manualIPs: ips })
      cy.get('[data-test="discover-button"]').click()
      cy.wait('@syncDevices')
      cy.wait('@getDevices')
      
      // Verify devices
      cy.get('@getDevices.all').then(interceptions => {
        const devices = interceptions[interceptions.length - 1].response.body.devices
        expect(devices).to.have.length(2)
      })
    })

    it('should save 3 IPs and create 3 devices', () => {
      const ips = ['192.168.1.50', '192.168.1.51', '192.168.1.52']
      
      cy.setupMocks({ deviceCount: 0 })
      cy.visit('/welcome')
      
      cy.openIPConfigModal()
      cy.saveIPsInModal(ips)
      cy.wait('@setManualIPs')
      cy.waitForModalClose()
      
      cy.setupMocks({ deviceCount: ips.length, manualIPs: ips })
      cy.get('[data-test="discover-button"]').click()
      cy.wait('@syncDevices')
      cy.wait('@getDevices')
      
      // Verify 3 devices
      cy.get('@getDevices.all').then(interceptions => {
        const devices = interceptions[interceptions.length - 1].response.body.devices
        expect(devices).to.have.length(3)
      })
    })
  })

  describe('Cancel Action - No Save', () => {
    it('should not save IPs when cancel is clicked', () => {
      cy.setupMocks({ deviceCount: 0 })
      cy.visit('/welcome')
      
      cy.openIPConfigModal()
      
      // Enter IPs but cancel
      cy.get('[data-test="ip-textarea"]').type('192.168.1.99, 192.168.1.100')
      cy.get('[data-test="cancel-button"]').click()
      
      // Verify modal closed
      cy.get('[data-test="modal-content"]').should('not.exist')
      
      // EmptyState should still be visible
      cy.get('[data-test="welcome-title"]').should('contain', 'Willkommen')
    })
  })

  describe('Complete User Journey', () => {
    it('should complete full flow: EmptyState → Add IPs → Discover → Dashboard', () => {
      const ips = ['192.168.1.50', '192.168.1.51']
      
      // Step 1: EmptyState visible
      cy.setupMocks({ deviceCount: 0 })
      cy.visit('/welcome')
      cy.get('[data-test="welcome-title"]').should('contain', 'Willkommen')
      
      // Step 2: Open modal
      cy.openIPConfigModal()
      
      // Step 3: Enter IPs
      cy.saveIPsInModal(ips)
      cy.wait('@setManualIPs')
      
      // Step 4: Modal closes
      cy.waitForModalClose()
      
      // Step 5: Trigger discovery
      cy.setupMocks({ deviceCount: ips.length, manualIPs: ips })
      cy.get('[data-test="discover-button"]').click()
      cy.wait('@syncDevices')
      cy.wait('@getDevices')
      
      // Step 6: Dashboard appears
      cy.url().should('eq', Cypress.config().baseUrl + '/')
      cy.get('[data-test="device-card"]').should('be.visible')
      cy.get('[data-test="app-header"]').should('be.visible')
    })
  })

  describe('Regression Tests - Bug Fixes', () => {
    it('BUG-FIX: Manual IPs should save via bulk endpoint', () => {
      // Bug: Interceptor didn't handle POST /api/settings/manual-ips (bulk)
      // Fix: Added handler for bulk endpoint alongside /add endpoint
      
      const ips = ['192.168.1.100', '192.168.1.101']
      
      cy.setupMocks({ deviceCount: 0 })
      cy.visit('/welcome')
      
      cy.openIPConfigModal()
      cy.saveIPsInModal(ips)
      
      // Verify the bulk endpoint was called
      cy.wait('@setManualIPs').then((interception) => {
        expect(interception.request.body).to.have.property('ips')
        expect(interception.request.body.ips).to.deep.equal(ips)
        expect(interception.response.statusCode).to.equal(200)
      })
    })

    // Note: "Discovery syncs devices immediately (1 click)" is already covered by:
    // → "should complete full flow: EmptyState → Add IPs → Discover → Dashboard"
    // That test verifies ONE discover click is sufficient (not 2 clicks needed)
    
    // Note: Following bugs are ONLY verifiable with `npm run dev` (VITE_MOCK_MODE=true)
    // They test the dev mock interceptor's localStorage logic, not production code
    
    it.skip('BUG-FIX: State persists across page reloads (manual test only)', () => {
      // Bug: No localStorage persistence → browser refresh lost all data
      // Fix: saveMockState() called after every mutation, loadMockState() on startup
      // 
      // How to verify manually:
      // 1. npm run dev
      // 2. Add manual IPs via modal
      // 3. Click discover
      // 4. Refresh page (F5)
      // 5. Devices should still be visible (not redirected to /welcome)
      //
      // Cypress cannot test this because it uses its own mock system, not the dev interceptor
    })

    it.skip('BUG-FIX: Placeholder images are SVG data URLs (manual test only)', () => {
      // Bug: via.placeholder.com URLs caused ERR_NAME_NOT_RESOLVED (network dependency)
      // Fix: Use SVG data URLs (data:image/svg+xml;base64,...)
      //
      // How to verify manually:
      // 1. npm run dev
      // 2. Open DevTools Console
      // 3. Click discover
      // 4. Check Network tab: NO requests to via.placeholder.com
      // 5. Check Console: NO ERR_NAME_NOT_RESOLVED errors
      //
      // Cypress cannot test this because fixtures don't include image URLs
    })
  })
})
