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

