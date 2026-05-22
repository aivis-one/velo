// =============================================================================
// VELO Frontend -- Display Helpers (Phase F9 review, extended Calendar)
// =============================================================================
//
// Single source of truth for all emoji / label / color mappings used in
// practice cards, diary, check-in, feedback, and analytics views.
//
// Previously duplicated across 8+ files (W-2, S-3 fixes).
// =============================================================================

import type {
  PracticeType,
  Mood,
  FeedbackRating,
  PracticeDirection,
  PracticeDifficulty,
  DurationBucket,
  TimeOfDay,
} from '@/api/types'

// ---------------------------------------------------------------------------
// Practice type
// ---------------------------------------------------------------------------

export const PRACTICE_TYPE_EMOJI: Record<PracticeType, string> = {
  live:       '🧘',
  series:     '🔄',
  one_on_one: '👤',
  replay:     '📹',
}

// ---------------------------------------------------------------------------
// Mood (check-in)
// ---------------------------------------------------------------------------

/** Ordered array -- use for rendering mood buttons in CheckinView. */
export const MOOD_OPTIONS: Array<{ value: Mood; emoji: string; label: string }> = [
  { value: 'low',  emoji: '😔', label: 'Не очень' },
  { value: 'mid',  emoji: '😐', label: 'Нормально' },
  { value: 'high', emoji: '😊', label: 'Хорошо' },
]

/** Map form -- use for lookups in DiaryView / DiaryStore. */
export const MOOD_EMOJI: Record<string, string> = {
  low:  '😔',
  mid:  '😐',
  high: '😊',
}

export const MOOD_LABEL: Record<string, string> = {
  low:  'Не очень',
  mid:  'Нормально',
  high: 'Хорошо',
}

// ---------------------------------------------------------------------------
// Feedback rating
// ---------------------------------------------------------------------------

/** Ordered array -- use for rendering rating buttons in FeedbackView. */
export const RATING_OPTIONS: Array<{ value: FeedbackRating; emoji: string; label: string }> = [
  { value: 'confused', emoji: '❓', label: 'Есть вопросы' },
  { value: 'good',     emoji: '👍', label: 'Хорошо' },
  { value: 'fire',     emoji: '🔥', label: 'Огонь!' },
]

/** Map form -- use for lookups in DiaryView / AnalyticsView. */
export const RATING_EMOJI: Record<string, string> = {
  fire:     '🔥',
  good:     '👍',
  confused: '❓',
}

export const RATING_LABEL: Record<string, string> = {
  fire:     'Огонь!',
  good:     'Хорошо',
  confused: 'Есть вопросы',
}

/**
 * CSS variable references for rating progress bar fills (AnalyticsView).
 * Values reference tokens from variables.css -- no hardcoded hex.
 */
export const RATING_COLOR: Record<string, string> = {
  fire:     'var(--velo-error-text)',  // #DC2626
  good:     'var(--velo-success)',     // #22C55E
  confused: 'var(--velo-warning)',     // #F59E0B
}

// ---------------------------------------------------------------------------
// Calendar taxonomy (direction / difficulty) + feed buckets
// ---------------------------------------------------------------------------
//
// Labels for the Calendar filter UI and practice detail. Values MUST match
// the backend allowed lists / filter literals. Single source of truth --
// do not duplicate these strings in components.

export const DIRECTION_LABEL: Record<PracticeDirection, string> = {
  meditation: 'Медитация',
  yoga:       'Йога',
  breathwork: 'Дыхательные практики',
}

export const DIFFICULTY_LABEL: Record<PracticeDifficulty, string> = {
  beginner: 'Начальная',
  medium:   'Средняя',
  high:     'Высокая',
}

/**
 * Filled-dot count for the difficulty indicator (PracticeDetailView):
 * beginner ●○○ / medium ●●○ / high ●●●.
 */
export const DIFFICULTY_DOTS: Record<PracticeDifficulty, number> = {
  beginner: 1,
  medium:   2,
  high:     3,
}

export const DURATION_BUCKET_LABEL: Record<DurationBucket, string> = {
  short: 'До 1 часа',
  long:  '1 час и больше',
}

export const TIME_OF_DAY_LABEL: Record<TimeOfDay, string> = {
  night:   'Ночь',
  morning: 'Утро',
  day:     'День',
  evening: 'Вечер',
}

// ---------------------------------------------------------------------------
// Date helper
// ---------------------------------------------------------------------------

/**
 * Format ISO datetime to short Russian locale date: "5 янв".
 * No year -- used for recent items in diary / analytics lists.
 */
export function formatShortDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU', {
    day:   'numeric',
    month: 'short',
  })
}
