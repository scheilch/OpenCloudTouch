/**
 * E2E Tests: Device Discovery
 * Uses Cypress Intercept (NO Backend required!)
 */
describe('Device Discovery', () => {
  describe('Happy Path - Successful Discovery', () => {
    it('should discover devices and redirect to dashboard (3 default devices)', () => {
      // Setup: Start with 0 devices, switch to 3 after sync
      cy.setupMocks({ deviceCount: 3, initialEmpty: true })
      
      // Visit welcome page
      cy.visit('/welcome')
      cy.url().should('include', '/welcome')
      
      // Click discover
      cy.get('[data-test="discover-button"]').should('be.visible').click()
      
      // Wait for API call
      cy.wait('@syncDevices')
      
      // Wait for devices API call
      cy.wait('@getDevices')
      
      // Should redirect to dashboard
      cy.url().should('eq', Cypress.config().baseUrl + '/')
      
      // Verify devices visible
      cy.get('[data-test="app-header"]').should('be.visible')
      cy.get('[data-test="device-card"]').should('have.length.at.least', 1)
    })

    it('should show correct number of devices based on manual IPs', () => {
      const ips = ['192.168.1.50', '192.168.1.51', '192.168.1.52']
      
      // Setup: Start empty, switch to 3 devices after sync
      cy.setupMocks({ deviceCount: ips.length, manualIPs: ips, initialEmpty: true })
      
      cy.visit('/welcome')
      cy.get('[data-test="discover-button"]').click()
      
      cy.wait('@syncDevices')
      cy.wait('@getDevices')
      
      cy.url().should('eq', Cypress.config().baseUrl + '/')
      
      // Verify API returns correct count (check LAST interception, not first)
      cy.get('@getDevices.all').then(interceptions => {
        const lastInterception = interceptions[interceptions.length - 1]
        const devices = lastInterception.response.body.devices
        expect(devices).to.have.length(ips.length)
      })
    })
  })

  describe('Unhappy Path - No Devices Found', () => {
    it('should show toast when no devices found', () => {
      cy.setupMocks({ deviceCount: 0 })
      
      cy.visit('/welcome')
      cy.get('[data-test="discover-button"]').click()
      
      cy.wait('@syncDevices')
      
      // Should stay on welcome page
      cy.url().should('include', '/welcome')
      
      // Toast should appear
      cy.get('[data-test="toast-notification"]', { timeout: 10000 }).should('be.visible')
      cy.get('[data-test="toast-message"]').should('contain', 'Keine Geräte')
    })
  })

  describe('Routing Guards', () => {
    it('should redirect to /welcome when no devices and visiting root', () => {
      cy.setupMocks({ deviceCount: 0 })
      
      cy.visit('/')
      cy.url().should('include', '/welcome')
    })

    it('should redirect to / when devices exist and visiting /welcome', () => {
      // Setup: Start empty, discover 3 devices
      cy.setupMocks({ deviceCount: 3, initialEmpty: true })
      
      // First trigger discovery
      cy.visit('/welcome')
      cy.get('[data-test="discover-button"]').click()
      cy.wait('@syncDevices')
      cy.wait('@getDevices')
      
      // Now try to visit /welcome again
      cy.visit('/welcome')
      
      // Should redirect to dashboard
      cy.url().should('eq', Cypress.config().baseUrl + '/')
    })
  })
})
