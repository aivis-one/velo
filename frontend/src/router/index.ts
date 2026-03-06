// =============================================================================
// VELO Frontend -- Router (Phase F2.2, updated F6)
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
// =============================================================================

import { createRouter, createWebHistory } from 'vue-router'
import { roleRedirect, roleGuard, masterStatusGuard } from '@/router/guards'

// Shells (layout wrappers) -- small, loaded eagerly
import UserShell from '@/views/shells/UserShell.vue'
import MasterShell from '@/views/shells/MasterShell.vue'
import AdminShell from '@/views/shells/AdminShell.vue'

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
    // MASTER routes (role=master required via MasterShell)
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

export default router
