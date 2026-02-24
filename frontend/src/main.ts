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

const app = createApp(App)

// Pinia = state manager (like a global dict of reactive objects).
app.use(createPinia())

// Router = URL -> component mapping (like FastAPI include_router).
app.use(router)

// Mount into <div id="app"> in index.html.
app.mount('#app')
