// =============================================================================
// VELO Frontend -- Master onboarding gate (Phase D, slice-1)
// =============================================================================
//
// Pure helpers for the post-approval master onboarding carousel
// (MasterOnboardingView), shown ONCE to a freshly-verified master as a
// full-screen overlay on first master-dashboard entry. Kept framework-free so
// the gate is unit-testable.
//
// The gating flag `master_onboarding_completed` is NOT yet on the generated
// UserResponse type (Zod task E15). It is read DEFENSIVELY here (absent /
// undefined -> not completed -> show once); generated.ts stays untouched.
// =============================================================================

import type { UserRole } from '@/api/types'

/**
 * Defensive read of the not-yet-typed `master_onboarding_completed` flag.
 *
 * Mirrors the role_switch cast precedent in stores/auth.ts: the field lives in
 * the backend credentials JSONB but is not surfaced on the autogen UserResponse
 * until Zod ships E15. Absent / undefined / null -> false (not completed).
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
