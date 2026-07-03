// =============================================================================
// VELO Frontend -- Router Guards (Phase F2.2, updated F6, BUG-role-redirect, TD-F01)
// =============================================================================
//
// Navigation guards for role-based access control.
//
// Auth gate (authenticated yes/no) lives in App.vue (Phase F1.3).
// These guards handle ROLE-BASED routing for authenticated users:
//   - roleRedirect:      redirect / to role-specific dashboard
//   - roleGuard:         require a minimum role to access a route group
//   - masterStatusGuard: require verified master profile
//
// F6 update: masterStatusGuard is now fully implemented.
//   - Calls useMasterStore().fetchMyProfile() lazily (skips if loaded)
//   - Redirects to /master/pending if profile missing or not verified
//   - Guards are applied per-route in router/index.ts via beforeEnter
//
// BUG-role-redirect fix: roleRedirect is now async and awaits waitUntilReady()
// before reading auth.role. Without this, the guard fires during the first
// navigation (before App.vue mounts), sees role=null, and redirects every
// user to /user/dashboard regardless of their real role.
//
// WARNING-3: if waitUntilReady() timed out and role is still null, redirect
// to /auth-error so the user sees a recoverable error screen instead of
// landing on /user/dashboard with broken state.
//
// TD-F01: roleRedirect consumes pendingDeepLink after auth completes.
// If a startapp=open_practice__{uuid} deep link was parsed during initAuth(),
// the user is redirected to the practice detail page instead of the dashboard.
// pendingDeepLink is cleared after first use to prevent stale redirects.
// =============================================================================

import type { NavigationGuardWithThis } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMasterStore } from '@/stores/master'
import { useUiStore } from '@/stores/ui'
import { waitUntilReady, pendingDeepLink } from '@/composables/useAuth'
import type { ReadyResult } from '@/composables/useAuth'
import type { UserRole } from '@/api/types'
import { MASTER_APPLIED_KEY } from '@/utils/constants'

/**
 * Redirect `/` to the correct dashboard based on user role.
 * Falls back to /user/dashboard for unknown roles.
 *
 * Async: awaits auth initialization so role is guaranteed to be set
 * before the switch. Without the await, role is always null on first load.
 *
 * TD-F01: if pendingDeepLink is set, redirect there instead of the dashboard
 * and clear the pending link so subsequent navigations go normally.
 */
export const roleRedirect: NavigationGuardWithThis<undefined> = async () => {
  // Wait for initAuth() to complete so auth.role reflects the real session.
  const { timedOut }: ReadyResult = await waitUntilReady()

  const auth = useAuthStore()

  // WARNING-3: timeout + no role means auth stalled (network/SDK freeze).
  // Redirect to error screen instead of routing with null role.
  if (timedOut && auth.role === null) {
    return { path: '/auth-error' }
  }

  // TD-F01: consume pending deep link from startapp parameter.
  if (pendingDeepLink.value) {
    const target = pendingDeepLink.value
    pendingDeepLink.value = null
    return target
  }

  switch (auth.role) {
    case 'admin':
      return { path: '/admin/dashboard' }
    case 'master':
      return { path: '/master/dashboard' }
    default:
      return { path: '/user/dashboard' }
  }
}

/**
 * Factory: require a minimum role to access a route group.
 *
 * roleGuard('master') -- allows master + admin
 * roleGuard('admin')  -- allows admin only
 */
export function roleGuard(
  required: Extract<UserRole, 'master' | 'admin'>,
): NavigationGuardWithThis<undefined> {
  return () => {
    const auth = useAuthStore()
    const role = auth.role

    if (required === 'admin' && role !== 'admin') {
      return { path: '/user/dashboard' }
    }

    if (required === 'master' && role !== 'master' && role !== 'admin') {
      return { path: '/user/dashboard' }
    }

    return true
  }
}

/**
 * Shared no-application check (№257 honest entry, operator Q4=А).
 *
 * A role=master account with NO master profile at all (confirmed by the
 * backend's 403 code=master_profile_not_found -- e.g. an admin who switched
 * into master, or a CLI-promoted account without a profile) is LED to the
 * application wizard instead of a mute degraded dashboard / a false
 * "заявка отправлена" screen. Distinct from pending/rejected applications,
 * which keep their existing /master/pending verdict flow.
 *
 * Admins browsing /master/* keep today's path (pending -> admin bounce), and
 * a transient fetch error never triggers the redirect (profileMissing is
 * keyed on the machine code, not on profile===null).
 */
async function noProfileMasterRedirect(): Promise<{ path: string } | null> {
  const auth = useAuthStore()
  if (auth.role !== 'master') return null

  const masterStore = useMasterStore()
  // Lazy-fetch profile (skips network if already loaded this session).
  await masterStore.fetchMyProfile()

  return masterStore.profileMissing ? { path: '/master/apply' } : null
}

/**
 * Lead a no-application master to the apply wizard on dashboard entry.
 *
 * Applied to: /master/dashboard (which has no status guard -- pending /
 * rejected masters may sit on it, byte-identical to before №257).
 */
export const masterNoProfileGuard: NavigationGuardWithThis<undefined> = async () =>
  (await noProfileMasterRedirect()) ?? true

/**
 * Require verified master profile before accessing protected master routes.
 *
 * Applied to: practices/*, finance (routes that require active master status).
 * Not applied to: /master/profile, /master/apply, /master/pending.
 * №257: a confirmed no-application master goes to /master/apply (honest
 * entry); everything else non-verified keeps the /master/pending redirect.
 */
export const masterStatusGuard: NavigationGuardWithThis<undefined> = async () => {
  const redirect = await noProfileMasterRedirect()
  if (redirect) return redirect

  const masterStore = useMasterStore()

  // Lazy-fetch profile (skips network if already loaded this session).
  await masterStore.fetchMyProfile()

  if (!masterStore.profile || masterStore.profile.status !== 'verified') {
    return { path: '/master/pending' }
  }

  return true
}

/**
 * Gate the standalone `master-pending` route.
 *
 * The route lives OUTSIDE the /master shell group, so it has no role guard of
 * its own — without this, a plain user who opens /master/pending directly sees
 * a false "Заявка отправлена!" screen. Access rules:
 *   - admin            -> redirect to /admin/dashboard (admins never apply)
 *   - master           -> allow (masterStatusGuard sends non-verified masters
 *                         here; a verified master is redirected to the dashboard
 *                         by the view's own onMounted check)
 *   - user + marker     -> allow (an actual applicant — still role='user' until
 *                         the backend promotes them; MASTER_APPLIED_KEY is set
 *                         on a successful application submit)
 *   - user, no marker   -> redirect to /user/dashboard (never applied)
 */
export const masterPendingGuard: NavigationGuardWithThis<undefined> = async () => {
  const { timedOut }: ReadyResult = await waitUntilReady()
  const auth = useAuthStore()

  if (timedOut && auth.role === null) {
    return { path: '/auth-error' }
  }

  // TEST-only apply-flow preview: admit the preview to the "sent" screen without
  // a real applicant marker. Fires only while previewApplyFlow is set, which is
  // prod-unreachable (see stores/ui.ts).
  if (useUiStore().previewApplyFlow) return true

  if (auth.role === 'admin') return { path: '/admin/dashboard' }
  if (auth.role === 'master') return true

  if (sessionStorage.getItem(MASTER_APPLIED_KEY) === '1') return true

  return { path: '/user/dashboard' }
}
