// =============================================================================
// VELO Frontend -- Router (Phase F2.2, updated F9, TD-FE-ROLE-SWITCH)
// =============================================================================
//
// F9: Added two new user routes:
//   /user/checkin/:practiceId  → CheckinView  (full-screen check-in form)
//   /user/feedback/:practiceId → FeedbackView (full-screen feedback form)
//
// Both are accessible to users AND masters (no roleGuard) because masters
// are also users and may participate in practices.
//
// TD-FE-ROLE-SWITCH: Added /admin/profile route.
// beforeEach updated: if uiMode === 'user', master/admin can reach /user/dashboard.
// =============================================================================

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { useMasterStore } from '@/stores/master'
import { roleRedirect, roleGuard, masterStatusGuard } from '@/router/guards'
import { waitUntilReady } from '@/composables/useAuth'

// -- Shell layouts --
import UserShell from '@/views/shells/UserShell.vue'
import MasterShell from '@/views/shells/MasterShell.vue'
import AdminShell from '@/views/shells/AdminShell.vue'

// =============================================================================
// applyGuard: verified masters don't need to visit the apply form.
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
        // F9: check-in and feedback -- full-screen flows
        {
          path: 'checkin/:practiceId',
          name: 'user-checkin',
          component: () => import('@/views/user/CheckinView.vue'),
        },
        {
          path: 'feedback/:practiceId',
          name: 'user-feedback',
          component: () => import('@/views/user/FeedbackView.vue'),
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
        // TD-FE-ROLE-SWITCH: admin profile with user-mode switch button.
        {
          path: 'profile',
          name: 'admin-profile',
          component: () => import('@/views/admin/AdminProfileView.vue'),
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
// TD-FE-ROLE-SWITCH: if uiMode === 'user', let master/admin through to
// /user/dashboard without redirect.
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

  if (auth.role === 'master' || auth.role === 'admin') {
    // TD-FE-ROLE-SWITCH: allow through if user explicitly switched to user mode.
    const uiStore = useUiStore()
    if (uiStore.uiMode === 'user') return true

    return auth.role === 'admin'
      ? { path: '/admin/dashboard' }
      : { path: '/master/dashboard' }
  }

  return true
})

export default router
