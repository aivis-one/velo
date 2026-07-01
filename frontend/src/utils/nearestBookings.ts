// =============================================================================
// VELO Frontend -- nearest-bookings selection (user dashboard, TASK-2)
// =============================================================================
//
// Pure, timezone-independent selection for the dashboard «Ближайшие практики»
// section. Extracted from UserDashboardView so it can be unit-tested directly.
// =============================================================================

import type { BookingWithPracticeResponse } from '@/api/types'

/** Default number of upcoming bookings shown alongside a live session. */
export const DEFAULT_MAX_UPCOMING = 2

const startMs = (b: BookingWithPracticeResponse): number =>
  new Date(b.practice.scheduled_at).getTime()

/**
 * Live-aware nearest-bookings selection (operator Г).
 *
 * Candidate rule: a confirmed booking whose practice is not completed/cancelled
 * and has NOT ended yet (now < start + duration_minutes) -- the same filter the
 * single-card version used.
 *
 * Selection: pin the ACTIVE session first (the single latest-started in-progress
 * booking -- start <= now), then the `maxUpcoming` soonest NOT-yet-started
 * bookings (start > now). Result is capped at 1 + maxUpcoming cards; when nothing
 * is live it is just the soonest upcoming ones. A genuinely-imminent booking is
 * therefore never hidden behind a live session.
 *
 * All comparisons are absolute epoch ms -> timezone-independent (TASK-2 proved
 * the reported dropout is not a tz bug).
 */
export function selectNearestBookings(
  bookings: readonly BookingWithPracticeResponse[],
  nowMs: number,
  maxUpcoming: number = DEFAULT_MAX_UPCOMING,
): BookingWithPracticeResponse[] {
  const candidates = bookings.filter((b) => {
    if (b.status !== 'confirmed') return false
    if (b.practice.status === 'completed' || b.practice.status === 'cancelled') {
      return false
    }
    const endMs = startMs(b) + b.practice.duration_minutes * 60 * 1000
    return nowMs < endMs
  })

  // Active session: already started, not past the ceiling. Keep only the single
  // latest-started one (matches the old "live wins" pick).
  const live = candidates
    .filter((b) => startMs(b) <= nowMs)
    .sort((a, b) => startMs(b) - startMs(a))[0]

  // Upcoming: not yet started; the `maxUpcoming` soonest.
  const upcoming = candidates
    .filter((b) => startMs(b) > nowMs)
    .sort((a, b) => startMs(a) - startMs(b))
    .slice(0, maxUpcoming)

  return [live, ...upcoming].filter((b): b is BookingWithPracticeResponse => b != null)
}
