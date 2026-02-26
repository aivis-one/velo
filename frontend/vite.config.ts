// =============================================================================
// VELO Frontend -- Vite Configuration (updated Phase F0.4: PWA)
// =============================================================================
//
// Vite is the build tool (like Docker build for frontend).
// It bundles .vue + .ts files into static HTML/JS/CSS for production.
//
// Key settings:
//   - resolve.alias: @/ -> src/ (short imports)
//   - server.proxy: /api requests -> backend during local dev
//   - build.outDir: dist/ (what Nginx serves)
//   - VitePWA: generates service worker for precaching static assets
// =============================================================================

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      // Generate SW automatically from build output.
      strategies: 'generateSW',
      // Auto-register the service worker (no manual code needed).
      registerType: 'autoUpdate',
      // Include these file types in precache.
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        // Don't precache source maps.
        globIgnores: ['**/*.map'],
      },
      // Manifest is served from public/manifest.json (not inlined).
      manifest: false,
    }),
  ],

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
