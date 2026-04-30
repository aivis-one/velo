// =============================================================================
// VELO Frontend -- Application Entry Point
// =============================================================================
//
// Equivalent of backend/app/main.py.
// Creates the Vue app, attaches plugins (router, pinia), mounts it.
// =============================================================================

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// Global styles (order matters: variables first, then reset/base).
import './styles/variables.css'
import './styles/global.css'

// BACKLOG #49 (S2 P06 C16): fail-fast in PROD if VITE_TELEGRAM_BOT_URL is unset.
// Prevents silent fallback to test bot. Non-PROD tolerates undefined and surfaces
// the issue visually (anchor href becomes string "undefined").
if (import.meta.env.PROD && !import.meta.env.VITE_TELEGRAM_BOT_URL) {
  throw new Error(
    '[velo] VITE_TELEGRAM_BOT_URL must be set in production builds. ' +
      'Refusing to boot to prevent silent fallback to test bot.',
  )
}

const app = createApp(App)

// Pinia = state manager (like a global dict of reactive objects).
app.use(createPinia())

// S2 P07 C25: theme initialization — read localStorage 'velo:theme' OR
// prefers-color-scheme; sets document.documentElement.dataset.theme.
// Must run after Pinia mount but before router (so first navigation already
// has correct data-theme attribute).
import { useUiStore } from '@/stores/ui'
useUiStore().initTheme()

// Router = URL -> component mapping (like FastAPI include_router).
app.use(router)

// Mount into <div id="app"> in index.html.
app.mount('#app')
