// =============================================================================
// VELO Frontend -- activity-entry vocabulary (B57 / B58, PROMPT No761)
// =============================================================================
//
// The strings and keys the "Новое событие" screen is built from. Kept in one
// place so the screen, the picker and their tests agree, in the same spirit as
// `practiceOptions.ts`.
//
// ⚠ THIS DELIBERATELY DOES NOT REUSE `displayHelpers.MOOD_LABEL`, and the
// reason is worth keeping: that map is the 1..10 check-in SCORE bucketed into
// low/mid/high ("Не очень" / "Нормально" / "Хорошо"). This screen's control is
// a three-way CHOICE with its own words ("Так себе" / "Хорошо" / "Отлично").
// The two overlap on the word "Хорошо" while meaning different things, so
// folding them together would look like deduplication and would silently bind
// two vocabularies that are free to move apart.
//
// ⚠ THE MOOD COLOURS ARE `--velo-rating-*`, NOT `--velo-mood-*`. Measured: the
// three hexes in the owner's asset (#4C6589 / #D66674 / #D4863C) are exactly
// --velo-rating-confused / -good / -fire, which already drive the feedback
// screen (23 live consumers). The tokens literally NAMED --velo-mood-low/mid/
// high are a different palette (pink/peach/teal) with ZERO consumers anywhere.
// A name match is not a finding.

/** The three states of the "Мое состояние" control. */
export type ActivityMood = 'soso' | 'good' | 'great'

export interface ActivityMoodOption {
  key: ActivityMood
  /** Shown to screen readers; the design draws no visible labels (measured). */
  label: string
  /** CSS custom property that carries this state's accent colour. */
  colorVar: string
}

/** Left-to-right, as the owner's `10.svg` lays them out (derived from x, not
 *  document order -- in SVG document order is paint order). */
export const ACTIVITY_MOODS: readonly ActivityMoodOption[] = [
  { key: 'soso', label: 'Так себе', colorVar: 'var(--velo-rating-confused)' },
  { key: 'good', label: 'Хорошо', colorVar: 'var(--velo-rating-good)' },
  { key: 'great', label: 'Отлично', colorVar: 'var(--velo-rating-fire)' },
] as const

/** Seed activities, in the owner's WRITTEN order (`velo_written_beats_mockup`
 *  -- the design file happens to draw them in a different order).
 *
 *  ⚠ A FRONTEND CONSTANT ON PURPOSE, NOT A MISSING TABLE. B58's real
 *  per-user list is gated on the schema question in B64, which is with the
 *  backend teammate. These six are the seed the owner specified; nothing here
 *  invents a storage shape. */
export const SEED_ACTIVITIES: readonly string[] = [
  'Медитация',
  'Массаж',
  'Танцы',
  'Вокал',
  'Йога',
  'Гвоздестояние',
] as const
