// =============================================================================
// VELO Frontend -- Vite Configuration
// =============================================================================
//
// Vite is the build tool (like Docker build for frontend).
// It bundles .vue + .ts files into static HTML/JS/CSS for production.
//
// Key settings:
//   - resolve.alias: @/ -> src/ (short imports)
//   - server.proxy: /api requests -> backend during local dev
//   - build.outDir: dist/ (what Nginx serves)
// =============================================================================

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      // Makes `@/stores/auth` resolve to `src/stores/auth`.
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },

  server: {
    // Dev server port (only used if someone runs `npm run dev` locally).
    port: 5173,
    // Proxy API requests to backend during local development.
    // In production, Nginx handles this routing.
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },

  build: {
    // Output directory for `npm run build`.
    // This is what gets copied into the Docker image.
    outDir: 'dist',
    // Generate source maps for easier debugging.
    sourcemap: false,
    // Target modern browsers (Telegram WebApp uses recent Chromium).
    target: 'es2022',
  },
})
