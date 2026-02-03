import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.js',
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/tests/real/**', // Exclude real device tests from default runs
      '**/tests/e2e/**', // Exclude Cypress E2E tests
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.test.{js,jsx}',
        'vite.config.js',
        'vitest.config.js',
      ],
    },
  },
})
