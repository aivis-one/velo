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
// Mirror: hardcoded in backend finalize/checkin logic (no config key).
// Used by: UserDashboardView, PracticeDetailView
// ---------------------------------------------------------------------------

/** Hours before scheduled_at during which check-in is allowed. */
export const CHECKIN_WINDOW_H = 3

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
