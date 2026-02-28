// =============================================================================
// VELO Frontend -- Router Guards (Phase F2.2)
// =============================================================================
//
// Navigation guards for role-based access control.
//
// Auth gate (authenticated yes/no) lives in App.vue (Phase F1.3).
// These guards handle ROLE-BASED routing for authenticated users:
//   - roleGuard: checks user role matches required role
//   - masterStatusGuard: checks master verification status (stub for F6)
//
// Guards are applied per-route in router/index.ts via beforeEnter.
// =============================================================================

import type { NavigationGuardWithThis } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { UserRole } from '@/api/types'

/**
 * Redirect `/` to the correct dashboard based on user role.
 * Falls back to /user/dashboard for unknown roles.
 */
export const roleRedirect: NavigationGuardWithThis<undefined> = () => {
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
 * roleGuard('master') — allows master + admin
 * roleGuard('admin')  — allows admin only
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
 * Check master verification status before allowing access.
 *
 * STUB: always passes in F2.2. Real implementation in F6.1 will
 * check master profile status and redirect to /master/pending
 * if not verified.
 */
export const masterStatusGuard: NavigationGuardWithThis<undefined> = () => {
  // TODO (F6.1): check master store verification status
  // const masterStore = useMasterStore()
  // if (masterStore.status !== 'verified') return { path: '/master/pending' }
  return true
}
