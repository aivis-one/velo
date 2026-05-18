// =============================================================================
// VELO Frontend -- Router (Phase F0 foundation)
//
// Minimal router for F0. Only the home placeholder and a catch-all.
// Real routes are added as CC generates views per VELO-Frontend-TZ-Final.md
// (one route per screen, named to match TZ-Final slugs).
//
// No shells, no guards, no store dependencies at this stage.
// =============================================================================

import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },

    // Catch-all -- redirect any unknown URL to home until real routes exist.
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

export default router
