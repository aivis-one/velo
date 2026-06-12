// =============================================================================
// VELO Frontend -- Router (Phase F2.2, updated F9, TD-FE-ROLE-SWITCH, WARNING-3)
// =============================================================================
//
// Diary redesign: /user/diary now points at DiaryFeedView (the unified feed +
// thread). The old DiaryView and its tab sub-components are removed.
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
// =============================================================================
const applyGuard = async () => {
  const { timedOut }: ReadyResult = await waitUntilReady()
  const auth = useAuthStore()

  if (timedOut && auth.role === null) {
    return { path: '/auth-error' }
  }

  if (auth.role !== 'master') return true

  const masterStore = useMasterStore()
  await masterStore.fetchMyProfile()
  if (masterStore.profile?.status === 'verified') {
    return { path: '/master/dashboard' }
  }
  return true
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'root',
      beforeEnter: roleRedirect,
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
          component: () => import('@/views/user/DiaryFeedView.vue'),
        },
        {
          path: 'diary/entry/:id',
          name: 'user-diary-entry',
          component: () => import('@/views/user/EntryView.vue'),
        },
        {
          path: 'diary/:type(checkin|feedback)/:id',
          name: 'user-diary-detail',
          component: () => import('@/views/user/DetailView.vue'),
        },
        {
          path: 'profile',
          name: 'user-profile',
          component: () => import('@/views/user/UserProfileView.vue'),
        },
        {
          path: 'profile/language-timezone',
          name: 'user-language-timezone',
          component: () => import('@/views/user/LanguageTimezoneView.vue'),
        },
        {
          path: 'profile/edit',
          name: 'user-edit-profile',
          component: () => import('@/views/user/EditProfileView.vue'),
        },
        {
          path: 'profile/notifications',
          name: 'user-notifications',
          component: () => import('@/views/user/NotificationsView.vue'),
        },
        {
          path: 'practices/:id',
          name: 'practice-detail',
          component: () => import('@/views/user/PracticeDetailView.vue'),
        },
        {
          path: 'masters/:id',
          name: 'user-master-public',
          component: () => import('@/views/user/MasterPublicView.vue'),
        },
        {
          path: 'booking-confirmed/:practiceId',
          name: 'user-booking-confirmed',
          component: () => import('@/views/user/BookingConfirmedView.vue'),
          // Post-booking screen has no own tab; light up Calendar in the bar.
          meta: { activeTab: '/user/calendar' },
        },
        {
          path: 'bookings',
          name: 'user-bookings',
          component: () => import('@/views/user/MyBookingsView.vue'),
        },
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
          path: 'practice-live/:practiceId',
          name: 'practice-live',
          component: () => import('@/views/user/PracticeLiveView.vue'),
        },
        {
          path: 'ai-summary',
          name: 'user-ai-summary',
          component: () => import('@/views/user/AiSummaryView.vue'),
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
        {
          path: '',
          redirect: { name: 'user-dashboard' },
        },
      ],
    },

    // =========================================================================
    // MASTER routes
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
          path: 'practices/:id/detail',
          name: 'master-practice-detail',
          beforeEnter: masterStatusGuard,
          meta: { hideTabBar: true },
          component: () => import('@/views/master/MasterPracticeDetailView.vue'),
        },
        {
          path: 'practices/:id/roster',
          name: 'master-attendance-roster',
          beforeEnter: masterStatusGuard,
          meta: { hideTabBar: true },
          component: () => import('@/views/master/AttendanceRosterView.vue'),
        },
        {
          path: 'analytics',
          name: 'master-analytics',
          component: () => import('@/views/master/AnalyticsView.vue'),
        },
        {
          path: 'analytics/practice/:id',
          name: 'master-practice-reviews',
          beforeEnter: masterStatusGuard,
          component: () => import('@/views/master/PracticeReviewsView.vue'),
        },
        {
          path: 'profile',
          name: 'master-profile',
          component: () => import('@/views/master/MasterProfileView.vue'),
        },
        // Master profile sub-screens reuse the role-agnostic user settings views
        // (they edit the current user's own profile/settings). Reachable from the
        // master profile hub; back-nav uses router.back() so it returns here.
        {
          path: 'profile/edit',
          name: 'master-edit-profile',
          component: () => import('@/views/user/EditProfileView.vue'),
        },
        {
          path: 'profile/notifications',
          name: 'master-notifications',
          component: () => import('@/views/user/NotificationsView.vue'),
        },
        {
          path: 'profile/language-timezone',
          name: 'master-language-timezone',
          component: () => import('@/views/user/LanguageTimezoneView.vue'),
        },
        {
          path: 'messages',
          name: 'master-messages',
          component: () => import('@/views/master/MasterMessagesView.vue'),
        },
        {
          path: 'messages/:id',
          name: 'master-chat',
          meta: { hideTabBar: true },
          component: () => import('@/views/master/MasterChatView.vue'),
        },
        {
          path: 'promocodes',
          name: 'master-promocodes',
          component: () => import('@/views/master/MasterPromocodesView.vue'),
        },
        {
          path: 'promocodes/new',
          name: 'master-promocode-new',
          meta: { hideTabBar: true },
          component: () => import('@/views/master/MasterNewPromocodeView.vue'),
        },
        {
          path: 'finance',
          name: 'master-finance',
          beforeEnter: masterStatusGuard,
          component: () => import('@/views/master/MasterFinanceView.vue'),
        },
        {
          path: 'students',
          name: 'master-students',
          beforeEnter: masterStatusGuard,
          component: () => import('@/views/master/MasterStudentsView.vue'),
        },
        {
          path: 'students/:id',
          name: 'master-student-profile',
          beforeEnter: masterStatusGuard,
          component: () => import('@/views/master/MasterStudentProfileView.vue'),
        },
        {
          path: 'summary',
          name: 'master-summary',
          beforeEnter: masterStatusGuard,
          component: () => import('@/views/master/MasterSummaryView.vue'),
        },
        {
          path: '',
          redirect: { name: 'master-dashboard' },
        },
      ],
    },

    {
      path: '/master/apply',
      name: 'master-apply',
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
        {
          path: 'profile',
          name: 'admin-profile',
          component: () => import('@/views/admin/AdminProfileView.vue'),
        },
        {
          path: '',
          redirect: { name: 'admin-dashboard' },
        },
      ],
    },

    {
      path: '/auth-error',
      name: 'auth-error',
      component: () => import('@/views/auth/LoadingErrorView.vue'),
    },

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
// Global guard (P-1): redirect master/admin away from /user/dashboard only.
// =============================================================================
let authInitialized = false

router.beforeEach(async (to) => {
  if (!authInitialized) {
    const { timedOut }: ReadyResult = await waitUntilReady()
    authInitialized = true
    if (timedOut) {
      console.warn('[router] auth initialization timed out on first navigation')
    }
  }

  if (to.name !== 'user-dashboard' && to.path !== '/user' && to.path !== '/user/') {
    return true
  }

  const auth = useAuthStore()

  if (auth.role === 'master' || auth.role === 'admin') {
    const uiStore = useUiStore()
    if (uiStore.uiMode === 'user') return true

    return auth.role === 'admin'
      ? { path: '/admin/dashboard' }
      : { path: '/master/dashboard' }
  }

  return true
})

export default router
