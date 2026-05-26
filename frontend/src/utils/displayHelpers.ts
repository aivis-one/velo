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
import type { Component } from 'vue'
import { IconMeditation, IconYoga, IconBreathwork, IconDots } from '@/components/icons'

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

/**
 * Accent color per rating ICON on the feedback form (Figma feedback design):
 * confused = brand blue, good = rose, fire = peach/orange. Separate from
 * RATING_COLOR (analytics bar fills) on purpose -- different surfaces,
 * different palettes. Values reference --velo-rating-* tokens (variables.css).
 */
export const RATING_ICON_COLOR: Record<FeedbackRating, string> = {
  confused: 'var(--velo-rating-confused)',
  good:     'var(--velo-rating-good)',
  fire:     'var(--velo-rating-fire)',
}

// ---------------------------------------------------------------------------
// Calendar taxonomy (direction / difficulty) + feed buckets
// ---------------------------------------------------------------------------
//
// Labels for the Calendar filter UI and practice detail. Values MUST match
// the backend allowed lists / filter literals. Single source of truth --
// do not duplicate these strings in components.

export const DIRECTION_LABEL: Record<PracticeDirection, string> = {
  meditation:    'Медитация',
  yoga:          'Йога',
  breathwork:    'Дыхательные практики',
  somatic:       'Соматика',
  tantra:        'Тантра',
  womens_circle: 'Женский круг',
  mens_circle:   'Мужской круг',
  kundalini:     'Кундалини',
}

// Direction -> icon component for the practice hero card.
// Partial (not Record) ON PURPOSE: the backend direction list will grow
// (somatic / womens_circle / tantra / ...), and generated.ts will widen
// PracticeDirection. A full Record would then fail vue-tsc until every new
// value got an icon. With Partial + DIRECTION_ICON_FALLBACK, a new direction
// simply renders the fallback glyph until its own icon is added here.
// IconYoga is a placeholder (TD-CAL-ICON-YOGA), swap when the real asset lands.
export const DIRECTION_ICON: Partial<Record<PracticeDirection, Component>> = {
  meditation: IconMeditation,
  yoga:       IconYoga,
  breathwork: IconBreathwork,
}

/** Neutral placeholder glyph for directions without a dedicated icon yet
 * (somatic / tantra / womens_circle / mens_circle / kundalini). Deliberately
 * NOT IconMeditation: a meditation glyph on a tantra/yoga practice is
 * misleading -- a neutral "..." reads as "icon pending" instead. Swap each new
 * direction into DIRECTION_ICON as its real asset lands. */
export const DIRECTION_ICON_FALLBACK: Component = IconDots

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
// Diary feed (unified timeline)
// ---------------------------------------------------------------------------
//
// Card title per event kind. The feed renders these as the card heading;
// checkin/feedback append the mood/rating label (e.g. "Check-in: Не очень").
// Values match the design (screens 40/41). kind->icon COMPONENT mapping lives
// in DiaryFeedCard.vue, not here -- the utils layer must not import .vue files
// (same rule as MOOD_ICON in CheckinView).

import type { DiaryEventKind } from '@/api/types'

export const FEED_KIND_TITLE: Record<DiaryEventKind, string> = {
  booking_confirmed:            'Вы записались',
  booking_cancelled_by_user:    'Вы отменили запись',
  practice_rescheduled:         'Мастер перенёс практику',
  practice_cancelled_by_master: 'Практика отменена',
  practice_outcome:             '',          // uses practice_title from snapshot
  checkin:                      'Check-in',  // + ": " + mood label
  feedback:                     'Feedback',  // + ": " + rating label
  note:                         'Дневник',
  dream:                        'Сонник',
}

/**
 * Outcome badge label for a practice_outcome card.
 * attended -> "Done" (teal), no_show -> "Не состоялась".
 */
export const OUTCOME_LABEL: Record<string, string> = {
  attended: 'Done',
  no_show:  'Не состоялась',
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
