// =============================================================================
// VELO Frontend -- Display Helpers (S2-S3 speedrun MEGA-1 emoji refactor)
// =============================================================================
//
// Single source of truth for all icon / label / color mappings used in
// practice cards, diary, check-in, feedback, and analytics views.
//
// Per decision #048 (forthcoming S2-S3 close): no-emoji rule. Practice-type
// glyphs migrated from emoji string map to Vue-SVG icon component map.
//
// MOOD and FEEDBACK rating maps still ship emoji + label pairs for views NOT
// yet refactored in MEGA-1 (analytics, AnalyticsView master-side, legacy
// DiaryEntryDetail). MEGA-1 cycles that consume mood/rating (CheckinFormView
// C30, FeedbackFormView C32) reference the SVG assets under
// `frontend/src/assets/mood/` directly OR use IconHeart/IconQuestion/IconFlame.
// Master/admin view emoji cleanup is out of MEGA-1 scope (S4/S5+).
// =============================================================================

import type { Component } from 'vue'
import type { Mood, FeedbackRating } from '@/api/types'
import {
  IconMeditation,
  IconBreathwork,
  IconGroup,
  IconProfile,
} from '@/components/icons'

// ---------------------------------------------------------------------------
// Practice type — Vue-SVG icon map (post-#048 refactor)
// ---------------------------------------------------------------------------

export const PRACTICE_TYPE_ICON: Record<string, Component> = {
  live: IconMeditation,
  series: IconBreathwork,
  one_on_one: IconProfile,
  replay: IconGroup,
}

/**
 * @deprecated Use PRACTICE_TYPE_ICON instead. Retained for legacy components
 * (master views + a few shared components) not yet refactored. Cleanup
 * scheduled at S4 (master views) / MEGA-2 (DiaryList) / S5+ polish cluster.
 */
export const PRACTICE_TYPE_EMOJI: Record<string, string> = {
  live: '',
  series: '',
  one_on_one: '',
  replay: '',
}

/**
 * Russian label for practice_type (used in cards + analytics).
 */
export const PRACTICE_TYPE_LABEL: Record<string, string> = {
  live: 'Live',
  series: 'Серия',
  one_on_one: 'Индивидуально',
  replay: 'Replay',
}

// ---------------------------------------------------------------------------
// Mood (check-in) — kept as emoji map for legacy DiaryCheckinDetail view
// not refactored in MEGA-1; MEGA-1 CheckinFormView uses MOOD_OPTIONS labels +
// the SVG assets under frontend/src/assets/mood/{mood-sad,mood-neutral,mood-calm}.svg
// ---------------------------------------------------------------------------

export const MOOD_OPTIONS: Array<{ value: Mood; label: string }> = [
  { value: 'low', label: 'Не очень' },
  { value: 'mid', label: 'Нормально' },
  { value: 'high', label: 'Хорошо' },
]

export const MOOD_LABEL: Record<string, string> = {
  low: 'Не очень',
  mid: 'Нормально',
  high: 'Хорошо',
}

/**
 * @deprecated Retained for legacy DiaryList / DiaryCheckinDetail not yet
 * refactored. Replace with mood SVG assets at MEGA-2 Diary refresh.
 */
export const MOOD_EMOJI: Record<string, string> = {
  low: '',
  mid: '',
  high: '',
}

// ---------------------------------------------------------------------------
// Feedback rating — kept as label map; MEGA-1 FeedbackFormView uses Icon
// components (IconQuestion / IconHeart / IconFlame placeholders).
// ---------------------------------------------------------------------------

export const RATING_OPTIONS: Array<{ value: FeedbackRating; label: string }> = [
  { value: 'confused', label: 'Есть вопросы' },
  { value: 'good', label: 'Хорошо' },
  { value: 'fire', label: 'Огонь!' },
]

export const RATING_LABEL: Record<string, string> = {
  fire: 'Огонь!',
  good: 'Хорошо',
  confused: 'Есть вопросы',
}

/**
 * @deprecated Retained for legacy DiaryList / DiaryFeedbackDetail not yet
 * refactored. Replace at MEGA-2 Diary refresh.
 */
export const RATING_EMOJI: Record<string, string> = {
  fire: '',
  good: '',
  confused: '',
}

/**
 * CSS variable references for rating progress bar fills (AnalyticsView).
 */
export const RATING_COLOR: Record<string, string> = {
  fire: 'var(--warm-deep)',
  good: 'var(--teal-primary)',
  confused: 'var(--feedback-warning)',
}

// ---------------------------------------------------------------------------
// Date helper
// ---------------------------------------------------------------------------

/**
 * Format ISO datetime to short Russian locale date: "5 янв".
 */
export function formatShortDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
  })
}
