// =============================================================================
// VELO Frontend -- Router (Phase F2.2, updated F9, TD-FE-ROLE-SWITCH, WARNING-3)
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
import type { ReadyResult } from '@/composables/useAuth'

// -- Shell layouts --
import UserShell from '@/views/shells/UserShell.vue'
import MasterShell from '@/views/shells/MasterShell.vue'
import AdminShell from '@/views/shells/AdminShell.vue'

// =============================================================================
// applyGuard: verified masters don't need to visit the apply form.
// A master who is already verified has no reason to visit the apply form.
// =============================================================================
const applyGuard = async () => {
  const { timedOut }: ReadyResult = await waitUntilReady()
  const auth = useAuthStore()

  // WARNING-3: if auth stalled, send to error screen.
  if (timedOut && auth.role === null) {
    return { path: '/auth-error' }
  }

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
        // S2 P08 booking flow + S2 P09 profile sub-routes (speedrun MEGA-1)
        {
          path: 'practices/:id/booking-success',
          name: 'user-booking-success',
          component: () => import('@/views/user/BookingSuccessView.vue'),
        },
        {
          path: 'practices/:id/booked',
          name: 'user-booked-practice',
          component: () => import('@/views/user/BookedPracticeView.vue'),
        },
        {
          path: 'booking/:id',
          name: 'user-booking-detail',
          component: () => import('@/views/user/BookingDetailView.vue'),
        },
        {
          path: 'practices/:practiceId/checkin/success',
          name: 'user-checkin-success',
          component: () => import('@/views/user/CheckinSuccessView.vue'),
        },
        {
          path: 'practices/:practiceId/live',
          name: 'user-practice-live',
          component: () => import('@/views/user/PracticeLiveView.vue'),
        },
        {
          path: 'practices/:practiceId/feedback/success',
          name: 'user-feedback-success',
          component: () => import('@/views/user/FeedbackSuccessView.vue'),
        },
        {
          path: 'profile/edit',
          name: 'user-profile-edit',
          component: () => import('@/views/user/EditProfileView.vue'),
        },
        // S2-S3 SPEEDRUN MEGA-2 routes (C39, C42, C45, C46-C52)
        {
          path: 'diary/checkins',
          name: 'user-diary-checkins',
          component: () => import('@/views/user/CheckinsCategoryView.vue'),
        },
        {
          path: 'diary/feedbacks',
          name: 'user-diary-feedbacks',
          component: () => import('@/views/user/FeedbacksCategoryView.vue'),
        },
        {
          path: 'diary/entries',
          name: 'user-diary-entries',
          component: () => import('@/views/user/EntriesCategoryView.vue'),
        },
        {
          path: 'diary/entry/:id',
          name: 'user-diary-entry',
          component: () => import('@/views/user/DiaryEntryView.vue'),
        },
        {
          path: 'diary/entry/:id/relationships',
          name: 'user-diary-relationships',
          component: () => import('@/views/user/RelationshipsView.vue'),
        },
        {
          path: 'profile/notifications',
          name: 'user-profile-notifications',
          component: () => import('@/views/user/NotificationsView.vue'),
        },
        {
          path: 'profile/language',
          name: 'user-profile-language',
          component: () => import('@/views/user/LanguageTimezoneView.vue'),
        },
        {
          path: 'profile/support',
          name: 'user-profile-support',
          component: () => import('@/views/user/SupportFormView.vue'),
        },
        {
          path: 'messages',
          name: 'user-messages',
          component: () => import('@/views/user/MessagesListView.vue'),
        },
        {
          path: 'messages/:conversationId',
          name: 'user-messages-thread',
          component: () => import('@/views/user/ThreadView.vue'),
        },
        {
          path: 'ai-summary',
          name: 'user-ai-summary',
          component: () => import('@/views/user/AISummaryView.vue'),
        },
        {
          path: 'master/:id',
          name: 'user-master-public',
          component: () => import('@/views/user/MasterProfilePublicView.vue'),
        },
        {
          path: 'reservations',
          name: 'user-reservations',
          component: () => import('@/views/user/MyReservationsView.vue'),
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
    // Welcome -- hybrid auth splash (S2-P06 C16; TMA-splash + PWA-standalone
    // branches per decision #036).
    // =========================================================================
    {
      path: '/welcome',
      name: 'welcome',
      component: () => import('@/views/auth/WelcomeView.vue'),
    },

    // =========================================================================
    // PWA-standalone auth surface (S2-P06 C17/C18/C19) -- mock until
    // BACKEND-COORDINATION § A.1 + § A.2 land.
    // =========================================================================
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue'),
    },
    {
      path: '/oauth/callback',
      name: 'oauth-callback',
      component: () => import('@/views/auth/OAuthLoadingView.vue'),
    },
    {
      path: '/onboarding/intro',
      name: 'onboarding-intro',
      component: () => import('@/views/auth/OnboardingCarouselView.vue'),
    },
    {
      path: '/onboarding/timezone',
      name: 'onboarding-timezone',
      component: () => import('@/views/auth/OnboardingTimezoneView.vue'),
    },

    // =========================================================================
    // Auth error -- shown when waitUntilReady() times out with null role.
    // =========================================================================
    {
      path: '/auth-error',
      name: 'auth-error',
      component: () => import('@/views/auth/LoadingErrorView.vue'),
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
    const { timedOut }: ReadyResult = await waitUntilReady()
    authInitialized = true
    if (timedOut) {
      console.warn('[router] auth initialization timed out on first navigation')
    }
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
