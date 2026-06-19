// =============================================================================
// VELO Frontend -- Shared Constants (NEW-1, TD-FE-W6)
// =============================================================================
//
// Single source of truth for magic numbers shared across multiple views.
// All values mirror their backend counterparts in config.py -- if a backend
// value changes, update it here too.
// =============================================================================

// ---------------------------------------------------------------------------
// Time window constants (NEW-1)
// Mirror: backend config.py checkin_window_hours / feedback_window_hours.
// If those change, update these too.
// Used by: UserDashboardView, PracticeDetailView
// ---------------------------------------------------------------------------

/**
 * Hours before scheduled_at during which check-in is allowed.
 * Mirrors backend config.py checkin_window_hours (24). Changed 3 -> 24
 * (customer request 2026-06-03). NB: this equals PRACTICE_MAX_DURATION_H by
 * coincidence -- they are different settings (window-open vs finished-ceiling),
 * do not merge them.
 */
export const CHECKIN_WINDOW_H = 24

/** Hours after practice ends during which feedback is allowed. */
export const FEEDBACK_WINDOW_H = 72

/**
 * Hard ceiling (hours after scheduled_at) past which a practice is considered
 * finished even if its master never closed it. Mirrors the backend
 * practice_max_duration_hours (config.py) used by the auto-finalizer. The
 * dashboard uses it to stop showing a booking once the practice has ended.
 */
export const PRACTICE_MAX_DURATION_H = 24

// ---------------------------------------------------------------------------
// Finance constants (TD-FE-W6)
// Mirror: backend config.py min_withdrawal_cents=5000, withdrawal_fee_cents=200
// Used by: MasterFinanceView
// ---------------------------------------------------------------------------

/** Minimum withdrawal amount in euros (backend: min_withdrawal_cents = 5000). */
export const MIN_WITHDRAWAL_EUROS = 50

/** Platform fee deducted per withdrawal in euros (backend: withdrawal_fee_cents = 200). */
export const WITHDRAWAL_FEE_EUROS = 2

// ---------------------------------------------------------------------------
// Master onboarding (WS-1, item 2)
// Used by: MasterApplyView (set), master store $reset (clear), masterPendingGuard (read)
// ---------------------------------------------------------------------------

/**
 * sessionStorage marker set on a successful master-application submit. The
 * `master-pending` route guard uses it to tell an actual applicant (who stays
 * role='user' until the backend promotes them) apart from a plain user who
 * navigated to the pending URL directly. Cleared on logout via master $reset.
 */
export const MASTER_APPLIED_KEY = 'velo:master-applied'
