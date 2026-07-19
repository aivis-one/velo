// =============================================================================
// VELO Frontend -- Vitest Configuration
// =============================================================================
//
// Separate config file so vite.config.ts stays clean.
// Uses happy-dom for lightweight DOM emulation (needed by Vue composables).
// Path alias @/ -> src/ inherited from resolve.alias.
// =============================================================================

import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },

  test: {
    // happy-dom is faster than jsdom and sufficient for unit tests
    environment: 'happy-dom',
    // Test file patterns
    include: ['src/**/*.test.ts'],
    // Runs before every test file -- resets api/client.ts module state (T1 stage 2)
    setupFiles: ['./src/test-setup.ts'],
    // Global timeout per test (ms)
    testTimeout: 5000,
    // Coverage (optional, run with --coverage)
    coverage: {
      provider: 'v8',
      include: ['src/**/*.ts'],
      exclude: ['src/**/*.test.ts', 'src/**/*.d.ts', 'src/main.ts'],
    },
  },
})
