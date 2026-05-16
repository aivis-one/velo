// =============================================================================
// VELO Frontend -- Router (Phase 0 foundation)
//
// Minimal shell structure for CC generation.
// No guards, no store dependencies, no auth logic.
// Guards and auth flow will be added after views are generated.
// =============================================================================

import { createRouter, createWebHistory } from 'vue-router'

// -- Shell layouts --
import UserShell from '@/views/shells/UserShell.vue'
import MasterShell from '@/views/shells/MasterShell.vue'
import AdminShell from '@/views/shells/AdminShell.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // -- Root placeholder --
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },

    // =========================================================================
    // USER routes
    // =========================================================================
    {
      path: '/user',
      component: UserShell,
      children: [
        { path: '', redirect: { name: 'user-dashboard' } },
        { path: 'dashboard',         name: 'user-dashboard',       component: () => import('@/views/user/UserDashboardView.vue') },
        { path: 'calendar',          name: 'user-calendar',        component: () => import('@/views/user/CalendarView.vue') },
        { path: 'diary',             name: 'user-diary',           component: () => import('@/views/user/DiaryView.vue') },
        { path: 'profile',           name: 'user-profile',         component: () => import('@/views/user/UserProfileView.vue') },
        { path: 'practices/:id',     name: 'practice-detail',      component: () => import('@/views/user/PracticeDetailView.vue') },
        { path: 'bookings',          name: 'user-bookings',        component: () => import('@/views/user/MyBookingsView.vue') },
        { path: 'topup',             name: 'user-topup',           component: () => import('@/views/user/TopupView.vue') },
      ],
    },

    // =========================================================================
    // MASTER routes
    // =========================================================================
    {
      path: '/master',
      component: MasterShell,
      children: [
        { path: '', redirect: { name: 'master-dashboard' } },
        { path: 'dashboard',              name: 'master-dashboard',     component: () => import('@/views/master/MasterDashboardView.vue') },
        { path: 'practices',              name: 'master-practices',     component: () => import('@/views/master/MasterPracticesView.vue') },
        { path: 'practices/new',          name: 'master-practice-new',  component: () => import('@/views/master/CreatePracticeView.vue') },
        { path: 'practices/:id',          name: 'master-practice-edit', component: () => import('@/views/master/EditPracticeView.vue') },
        { path: 'practices/:id/attendance', name: 'master-attendance',  component: () => import('@/views/master/AttendanceView.vue') },
        { path: 'profile',                name: 'master-profile',       component: () => import('@/views/master/MasterProfileView.vue') },
        { path: 'finance',                name: 'master-finance',       component: () => import('@/views/master/MasterFinanceView.vue') },
      ],
    },

    // -- Master standalone (no shell) --
    { path: '/master/apply',   name: 'master-apply',   component: () => import('@/views/master/MasterApplyView.vue') },
    { path: '/master/pending', name: 'master-pending', component: () => import('@/views/master/MasterPendingView.vue') },

    // =========================================================================
    // ADMIN routes
    // =========================================================================
    {
      path: '/admin',
      component: AdminShell,
      children: [
        { path: '', redirect: { name: 'admin-dashboard' } },
        { path: 'dashboard',    name: 'admin-dashboard',      component: () => import('@/views/admin/AdminDashboardView.vue') },
        { path: 'masters',      name: 'admin-masters',        component: () => import('@/views/admin/AdminMastersView.vue') },
        { path: 'masters/:id',  name: 'admin-master-review',  component: () => import('@/views/admin/AdminMasterReviewView.vue') },
        { path: 'reports',      name: 'admin-reports',        component: () => import('@/views/admin/AdminReportsView.vue') },
        { path: 'consistency',  name: 'admin-consistency',    component: () => import('@/views/admin/AdminConsistencyView.vue') },
      ],
    },

    // =========================================================================
    // Catch-all
    // =========================================================================
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

export default router