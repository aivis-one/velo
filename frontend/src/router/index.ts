// =============================================================================
// VELO Frontend -- Router (Phase F0.1 skeleton)
// =============================================================================
//
// URL -> Component mapping. Like FastAPI's @app.get("/path") -> handler.
// History mode = clean URLs (requires Nginx SPA fallback).
// Guards (auth, role) added in Phase F1-F2.
// =============================================================================

import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    // Catch-all: unknown routes -> home (404 page added in Phase F2).
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

export default router
