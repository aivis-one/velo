// =============================================================================
// VELO Frontend -- usePracticeWindows (NEW-10)
// =============================================================================
//
// Pure helper functions for check-in and feedback time window checks.
// Extracted from UserDashboardView and PracticeDetailView to avoid
// duplicating the same arithmetic in two places.
//
// Both views keep their own reactive `now` ref and computeds --
// these helpers only handle the math.
//
// Constants (CHECKIN_WINDOW_H, FEEDBACK_WINDOW_H) live in utils/constants.ts.
// =============================================================================

import { CHECKIN_WINDOW_H, FEEDBACK_WINDOW_H } from '@/utils/constants'

/**
 * Returns true if `now` is within the check-in window for a practice.
 * Window: [scheduledAt - CHECKIN_WINDOW_H hours, scheduledAt]
 */
export function isInCheckinWindow(
  scheduledAtMs: number,
  nowMs: number,
): boolean {
  const windowStartMs = scheduledAtMs - CHECKIN_WINDOW_H * 60 * 60 * 1000
  return nowMs >= windowStartMs && nowMs <= scheduledAtMs
}

/**
 * Returns true if `now` is within the feedback window for a practice.
 * Window: [scheduledAt + durationMinutes, scheduledAt + durationMinutes + FEEDBACK_WINDOW_H hours]
 */
export function isInFeedbackWindow(
  scheduledAtMs: number,
  durationMinutes: number,
  nowMs: number,
): boolean {
  const practiceEndMs = scheduledAtMs + durationMinutes * 60 * 1000
  const feedbackEndMs = practiceEndMs + FEEDBACK_WINDOW_H * 60 * 60 * 1000
  return nowMs >= practiceEndMs && nowMs <= feedbackEndMs
}
