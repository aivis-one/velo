// =============================================================================
// VELO Frontend -- Router Guards (Phase F2.2, updated F6, BUG-role-redirect)
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
// =============================================================================

import type { NavigationGuardWithThis } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMasterStore } from '@/stores/master'
import { waitUntilReady } from '@/composables/useAuth'
import type { UserRole } from '@/api/types'

/**
 * Redirect `/` to the correct dashboard based on user role.
 * Falls back to /user/dashboard for unknown roles.
 *
 * Async: awaits auth initialization so role is guaranteed to be set
 * before the switch. Without the await, role is always null on first load.
 */
export const roleRedirect: NavigationGuardWithThis<undefined> = async () => {
  // Wait for initAuth() to complete so auth.role reflects the real session.
  await waitUntilReady()

  const auth = useAuthStore()
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
 * Require verified master profile before accessing protected master routes.
 *
 * Applied to: practices/*, finance (routes that require active master status).
 * NOT applied to: dashboard, profile, apply, pending.
 *
 * Flow:
 *   1. Lazy-fetch master profile (skipped if already loaded in this session)
 *   2. If fetch fails or profile is null -> redirect to /master/pending
 *   3. If profile.status !== 'verified' -> redirect to /master/pending
 *   4. Otherwise -> allow navigation
 *
 * Note: role=master and status=verified are kept in sync by the backend
 * (admin verify sets both atomically). This guard adds a second layer
 * of safety for edge cases.
 */
export const masterStatusGuard: NavigationGuardWithThis<undefined> = async () => {
  const masterStore = useMasterStore()

  // Lazy-load: skip network call if already fetched this session.
  await masterStore.fetchMyProfile()

  if (!masterStore.profile || masterStore.profile.status !== 'verified') {
    return { path: '/master/pending' }
  }

  return true
}
