// =============================================================================
// VELO Frontend -- Router (Phase F2.2, updated F6, BUG-role-redirect)
// =============================================================================
//
// URL -> Component mapping with role-based access.
//
// Architecture:
//   /          -> redirect to role-specific dashboard
//   /user/*    -> UserShell (MobileLayout + tab bar) -> child views
//   /master/*  -> MasterShell (MobileLayout + tab bar) -> child views
//   /admin/*   -> AdminShell (AdminLayout + tab bar) -> child views
//   /404       -> NotFoundView
//
// Auth gate (authenticated/not) is in App.vue (Phase F1.3).
// Guards here handle role-based routing only.
//
// F6 update: /master/apply and /master/pending moved OUT of MasterShell.
//   They are now standalone routes (no parent shell, no roleGuard).
//   This allows role='user' to access /master/apply to submit an
//   application without being blocked by roleGuard('master').
//   Both views render directly in App.vue's <RouterView />.
//
// BUG-role-redirect fixes:
//   1. roleRedirect (guards.ts) is now async -- awaits waitUntilReady()
//      before reading auth.role. Fixes race condition on first load.
//
//   2. Global beforeEach (below) redirects master/admin away from the
//      /user/dashboard entry point. Only the dashboard is blocked --
//      masters are also users and need access to /user/practices/:id,
//      /user/bookings, /user/topup etc. (P-1 fix).
//
//   3. /master/apply has a beforeEnter guard that redirects already-
//      verified masters to /master/dashboard (S-6 fix).
// =============================================================================

import { createRouter, createWebHistory } from 'vue-router'
import { roleRedirect, roleGuard, masterStatusGuard } from '@/router/guards'
import { waitUntilReady } from '@/composables/useAuth'
import { useAuthStore } from '@/stores/auth'
import { useMasterStore } from '@/stores/master'

// Shells (layout wrappers) -- small, loaded eagerly
import UserShell from '@/views/shells/UserShell.vue'
import MasterShell from '@/views/shells/MasterShell.vue'
import AdminShell from '@/views/shells/AdminShell.vue'

// =============================================================================
// S-6: guard for /master/apply -- redirect verified masters to their dashboard.
// A master who is already verified has no reason to visit the apply form.
// =============================================================================
const applyGuard = async () => {
  await waitUntilReady()
  const auth = useAuthStore()
  if (auth.role !== 'master') return true

  const masterStore = useMasterStore()
  // Lazy-fetch profile (skips network if already loaded this session).
  await masterStore.fetchMyProfile()
  if (masterStore.profile?.status === 'verified') {
    return { path: '/master/dashboard' }
  }
  return true
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // -- Root: redirect to role dashboard --
    {
      path: '/',
      name: 'root',
      beforeEnter: roleRedirect,
      // Component required by Vue Router but never renders (guard always redirects)
      component: { template: '' },
    },

    // =========================================================================
    // USER routes
    // =========================================================================
    {
      path: '/user',
      component: UserShell,
      children: [
        {
          path: 'dashboard',
          name: 'user-dashboard',
          component: () => import('@/views/user/UserDashboardView.vue'),
        },
        {
          path: 'calendar',
          name: 'user-calendar',
          component: () => import('@/views/user/CalendarView.vue'),
        },
        {
          path: 'diary',
          name: 'user-diary',
          component: () => import('@/views/user/DiaryView.vue'),
        },
        {
          path: 'profile',
          name: 'user-profile',
          component: () => import('@/views/user/UserProfileView.vue'),
        },
        {
          path: 'practices/:id',
          name: 'practice-detail',
          component: () => import('@/views/user/PracticeDetailView.vue'),
        },
        {
          path: 'bookings',
          name: 'user-bookings',
          component: () => import('@/views/user/MyBookingsView.vue'),
        },
        {
          path: 'topup',
          name: 'user-topup',
          component: () => import('@/views/user/TopupView.vue'),
        },
        {
          path: 'topup/success',
          name: 'user-topup-success',
          component: () => import('@/views/user/TopupSuccessView.vue'),
        },
        {
          path: 'topup/cancel',
          name: 'user-topup-cancel',
          component: () => import('@/views/user/TopupCancelView.vue'),
        },
        // Default: /user -> /user/dashboard
        {
          path: '',
          redirect: { name: 'user-dashboard' },
        },
      ],
    },

    // =========================================================================
    // MASTER routes (role=master required via roleGuard)
    // =========================================================================
    {
      path: '/master',
      component: MasterShell,
      beforeEnter: roleGuard('master'),
      children: [
        {
          path: 'dashboard',
          name: 'master-dashboard',
          component: () => import('@/views/master/MasterDashboardView.vue'),
        },
        {
          path: 'practices',
          name: 'master-practices',
          beforeEnter: masterStatusGuard,
          component: () => import('@/views/master/MasterPracticesView.vue'),
        },
        {
          path: 'practices/new',
          name: 'master-practice-new',
          beforeEnter: masterStatusGuard,
          component: () => import('@/views/master/CreatePracticeView.vue'),
        },
        {
          path: 'practices/:id',
          name: 'master-practice-edit',
          beforeEnter: masterStatusGuard,
          component: () => import('@/views/master/EditPracticeView.vue'),
        },
        {
          path: 'practices/:id/attendance',
          name: 'master-attendance',
          beforeEnter: masterStatusGuard,
          component: () => import('@/views/master/AttendanceView.vue'),
        },
        {
          path: 'analytics',
          name: 'master-analytics',
          component: () => import('@/views/master/AnalyticsView.vue'),
        },
        {
          path: 'profile',
          name: 'master-profile',
          component: () => import('@/views/master/MasterProfileView.vue'),
        },
        {
          path: 'finance',
          name: 'master-finance',
          beforeEnter: masterStatusGuard,
          component: () => import('@/views/master/MasterFinanceView.vue'),
        },
        // Default: /master -> /master/dashboard
        {
          path: '',
          redirect: { name: 'master-dashboard' },
        },
      ],
    },

    // =========================================================================
    // MASTER apply / pending -- standalone (no MasterShell, no roleGuard)
    //
    // Accessible to:
    //   - role='user'   visiting /master/apply to submit application
    //   - role='master' visiting /master/pending while awaiting verification
    //
    // Auth is still enforced by App.vue (unauthenticated users never reach here).
    // These views render their own header without MasterShell tab bar.
    // =========================================================================
    {
      path: '/master/apply',
      name: 'master-apply',
      // S-6: verified masters have nothing to do on the apply form.
      beforeEnter: applyGuard,
      component: () => import('@/views/master/MasterApplyView.vue'),
    },
    {
      path: '/master/pending',
      name: 'master-pending',
      component: () => import('@/views/master/MasterPendingView.vue'),
    },

    // =========================================================================
    // ADMIN routes
    // =========================================================================
    {
      path: '/admin',
      component: AdminShell,
      beforeEnter: roleGuard('admin'),
      children: [
        {
          path: 'dashboard',
          name: 'admin-dashboard',
          component: () => import('@/views/admin/AdminDashboardView.vue'),
        },
        {
          path: 'masters',
          name: 'admin-masters',
          component: () => import('@/views/admin/AdminMastersView.vue'),
        },
        {
          path: 'masters/:id',
          name: 'admin-master-review',
          component: () => import('@/views/admin/AdminMasterReviewView.vue'),
        },
        {
          path: 'reports',
          name: 'admin-reports',
          component: () => import('@/views/admin/AdminReportsView.vue'),
        },
        {
          path: 'reports/:id',
          name: 'admin-report-detail',
          component: () => import('@/views/admin/AdminReportDetailView.vue'),
        },
        {
          path: 'consistency',
          name: 'admin-consistency',
          component: () => import('@/views/admin/AdminConsistencyView.vue'),
        },
        // Default: /admin -> /admin/dashboard
        {
          path: '',
          redirect: { name: 'admin-dashboard' },
        },
      ],
    },

    // =========================================================================
    // Catch-all
    // =========================================================================
    {
      path: '/404',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/404',
    },
  ],
})

// =============================================================================
// Global guard: redirect master/admin away from /user/dashboard only (P-1 fix).
//
// Problem: /user/* has no roleGuard. A master can land on /user/dashboard via:
//   - saved URL in browser history (after role upgrade user -> master)
//   - restoreSession() which skips / -> roleRedirect entirely
//
// P-1 fix: only block /user/dashboard (and /user bare path).
// All other /user/* routes (/user/practices/:id, /user/bookings, /user/topup
// etc.) remain accessible -- masters are also users and need them.
//
// waitUntilReady() is called only on the first navigation (authInitialized
// flag) -- subsequent navigations resolve immediately with no overhead.
// =============================================================================
let authInitialized = false

router.beforeEach(async (to) => {
  // Wait for auth on first navigation only.
  if (!authInitialized) {
    await waitUntilReady()
    authInitialized = true
  }

  // Only intercept the dashboard entry point, not all of /user/*.
  // Masters need /user/practices/:id, /user/bookings, /user/topup etc.
  if (to.name !== 'user-dashboard' && to.path !== '/user' && to.path !== '/user/') {
    return true
  }

  const auth = useAuthStore()

  if (auth.role === 'master') {
    return { path: '/master/dashboard' }
  }

  if (auth.role === 'admin') {
    return { path: '/admin/dashboard' }
  }

  return true
})

export default router
