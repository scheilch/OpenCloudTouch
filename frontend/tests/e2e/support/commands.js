/**
 * Custom Cypress Commands with API Interception
 */

/**
 * Setup API mocks for test environment
 * @param {Object} options - Mock configuration
 * @param {number} options.deviceCount - Number of devices to return (0, 1, 3)
 * @param {string[]} options.manualIPs - Manual IPs to return
 * @param {boolean} options.initialEmpty - If true, start with 0 devices, switch to deviceCount after sync
 */
Cypress.Commands.add('setupMocks', (options = {}) => {
  const { deviceCount = 3, manualIPs = [], initialEmpty = false } = options

  // Mock GET /api/devices
  if (initialEmpty) {
    // Two-stage mocking: Start empty, switch to devices after sync
    let syncCalled = false
    
    cy.intercept('GET', '/api/devices', (req) => {
      if (syncCalled) {
        // After sync: Return devices based on deviceCount
        if (deviceCount === 0) {
          req.reply({ fixture: 'devices-empty.json' })
        } else if (deviceCount === 3) {
          req.reply({ fixture: 'devices-3.json' })
        } else {
          req.reply({
            count: deviceCount,
            devices: Array.from({ length: deviceCount }, (_, i) => ({
              id: i + 1,
              device_id: `MOCK_192_168_1_${101 + i}`,
              ip: `192.168.1.${101 + i}`,
              name: `Mock Device ${i + 1}`,
              model: ['ST10', 'ST30', 'ST300'][i % 3],
              mac_address: `AA:BB:CC:DD:EE:${(i + 1).toString().padStart(2, '0')}`,
              firmware_version: '1.0.0-mock'
            }))
          })
        }
      } else {
        // Before sync: Always return empty
        req.reply({ fixture: 'devices-empty.json' })
      }
    }).as('getDevices')
    
    // Hook into sync to flip the flag
    cy.intercept('POST', '/api/devices/sync', (req) => {
      syncCalled = true
      if (deviceCount === 0) {
        req.reply({ fixture: 'sync-no-devices.json' })
      } else {
        req.reply({ fixture: 'sync-success.json' })
      }
    }).as('syncDevices')
  } else {
    // Single-stage mocking: Always return same deviceCount
    if (deviceCount === 0) {
      cy.intercept('GET', '/api/devices', { fixture: 'devices-empty.json' }).as('getDevices')
    } else if (deviceCount === 3) {
      cy.intercept('GET', '/api/devices', { fixture: 'devices-3.json' }).as('getDevices')
    } else {
      // Dynamic device count (generate on-the-fly)
      cy.intercept('GET', '/api/devices', {
        count: deviceCount,
        devices: Array.from({ length: deviceCount }, (_, i) => ({
          id: i + 1,
          device_id: `MOCK_192_168_1_${101 + i}`,
          ip: `192.168.1.${101 + i}`,
          name: `Mock Device ${i + 1}`,
          model: ['ST10', 'ST30', 'ST300'][i % 3],
          mac_address: `AA:BB:CC:DD:EE:${(i + 1).toString().padStart(2, '0')}`,
          firmware_version: '1.0.0-mock'
        }))
      }).as('getDevices')
    }

    // Mock POST /api/devices/sync
    if (deviceCount === 0) {
      cy.intercept('POST', '/api/devices/sync', { fixture: 'sync-no-devices.json' }).as('syncDevices')
    } else {
      cy.intercept('POST', '/api/devices/sync', { fixture: 'sync-success.json' }).as('syncDevices')
    }
  }

  // Mock GET /api/settings/manual-ips
  cy.intercept('GET', '/api/settings/manual-ips', { ips: manualIPs }).as('getManualIPs')

  // Mock POST /api/settings/manual-ips
  cy.intercept('POST', '/api/settings/manual-ips', (req) => {
    req.reply({ message: 'IPs saved successfully', ips: req.body.ips })
  }).as('setManualIPs')

  // Mock DELETE /api/settings/manual-ips/{ip}
  cy.intercept('DELETE', '/api/settings/manual-ips/*', { message: 'IP deleted successfully' }).as('deleteManualIP')
})

/**
 * Get devices (mocked)
 */
Cypress.Commands.add('getDevices', () => {
  return cy.get('@getDevices.all').then(interceptions => {
    const lastInterception = interceptions[interceptions.length - 1]
    return lastInterception?.response?.body?.devices || []
  })
})

/**
 * Get manual IPs (mocked)
 */
Cypress.Commands.add('getManualIPs', () => {
  return cy.get('@getManualIPs.all').then(interceptions => {
    const lastInterception = interceptions[interceptions.length - 1]
    return lastInterception?.response?.body?.ips || []
  })
})

/**
 * Clear manual IPs (mocked)
 */
Cypress.Commands.add('clearManualIPs', () => {
  cy.setupMocks({ deviceCount: 0, manualIPs: [] })
})

/**
 * Set manual IPs (mocked)
 */
Cypress.Commands.add('setManualIPs', (ips) => {
  cy.setupMocks({ deviceCount: ips.length, manualIPs: ips })
})

/**
 * Trigger device sync (mocked)
 */
Cypress.Commands.add('syncDevices', () => {
  return cy.wait('@syncDevices').its('response.body')
})

/**
 * Open manual IP configuration modal
 */
Cypress.Commands.add('openIPConfigModal', () => {
  cy.get('details').then($details => {
    if (!$details.attr('open')) {
      cy.get('details summary').click()
    }
  })
  cy.get('[data-test="manual-add-button"]').should('be.visible').click()
  cy.get('[data-test="modal-content"]').should('be.visible')
})

/**
 * Save IPs in modal
 */
Cypress.Commands.add('saveIPsInModal', (ips) => {
  cy.get('[data-test="ip-textarea"]').clear().type(ips.join(', '))
  cy.get('[data-test="save-button"]').click()
})

/**
 * Wait for modal close
 */
Cypress.Commands.add('waitForModalClose', () => {
  cy.get('[data-test="modal-content"]').should('not.exist')
})

/**
 * Trigger discovery (deprecated - use syncDevices)
 */
Cypress.Commands.add('triggerDiscovery', () => {
  cy.log('⚠️  triggerDiscovery is deprecated - use setupMocks instead')
})
