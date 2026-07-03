// =============================================================================
// VELO Frontend -- Master onboarding gate (Phase D, slice-1)
// =============================================================================
//
// Pure helpers for the post-approval master onboarding carousel
// (MasterOnboardingView), shown ONCE to a freshly-verified master as a
// full-screen overlay on first master-dashboard entry. Kept framework-free so
// the gate is unit-testable.
//
// E15 SHIPPED (ПРОМТ №256/257): `master_onboarding_completed` is persisted by
// the backend and typed on UserResponse. The reader below stays null-tolerant
// (absent / undefined / null -> false) so it accepts a not-yet-loaded user.
// =============================================================================

import type { UserRole } from '@/api/types'

/**
 * Null-tolerant read of the `master_onboarding_completed` flag (E15).
 *
 * The field is now on the typed UserResponse; the loose parameter keeps the
 * helper usable with a still-null auth user and framework-free in unit tests.
 */
export function isMasterOnboardingCompleted(user: unknown): boolean {
  return (
    (user as { master_onboarding_completed?: boolean } | null | undefined)
      ?.master_onboarding_completed ?? false
  )
}

export interface MasterOnboardingGateInput {
  /** Current account role (null while auth is still resolving). */
  role: UserRole | null
  /** Master profile verification status ('verified' once the admin approves). */
  profileStatus: string | null | undefined
  /** Defensive server-flag read (isMasterOnboardingCompleted). */
  completed: boolean
  /** Per-session suppression (set on done/skip; cleared on logout). */
  shownThisSession: boolean
  /**
   * TEST-only force (role-switch replay): bypasses `completed` +
   * `shownThisSession` so a tester can re-watch the carousel. Still requires a
   * verified master — you cannot onboard a non-verified one. Default false.
   */
  forced?: boolean
}

/**
 * Show the post-approval carousel exactly once: only to a VERIFIED master who
 * has neither completed it (server flag) nor dismissed it this session.
 *
 * The session guard is what makes the honest-stub interim safe: until E15 ships
 * the server flag never persists, so without it the overlay would re-trigger on
 * every dashboard re-entry within a session. With it, the carousel re-shows only
 * on a fresh session (next app open) -- the expected interim, not a loop.
 */
export function shouldShowMasterOnboarding(input: MasterOnboardingGateInput): boolean {
  return (
    input.role === 'master' &&
    input.profileStatus === 'verified' &&
    (input.forced === true || (!input.completed && !input.shownThisSession))
  )
}
