// =============================================================================
// VELO Frontend -- Vite Configuration (Phase F0.4: PWA)
// =============================================================================
//
// PWA is currently DISABLED -- F0 has empty views and no static assets in
// public/, so workbox-build can't find anything matching globPatterns and
// errors out. Re-enable (disable: false) once Sprint 2 produces real assets
// (icons, fonts, build output > 16 modules).
// =============================================================================

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      disable: true, // F0: nothing to precache yet
      registerType: 'autoUpdate',
      manifest: false, // Using public/manifest.json directly
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        navigateFallback: 'index.html',
        navigateFallbackDenylist: [/^\/api\//],
      },
    }),
  ],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },

  server: {
    port: 5173,
    host: true,
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
    outDir: 'dist',
    sourcemap: false,
    target: 'es2022',
  },
})
