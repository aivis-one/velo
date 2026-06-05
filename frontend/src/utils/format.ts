// =============================================================================
// VELO Frontend -- Format Utilities (Phase F3.1, updated F4.2, fixed F5 review)
// =============================================================================
//
// Pure formatting functions used across practice cards, detail views,
// and any future components that display money, dates, or durations.
//
// All functions are locale-aware where applicable (defaults to 'ru').
//
// F4.2: formatMoney gains allowZero param for balance display.
// F5 review: S-24 -- minimumFractionDigits: 2 for consistent money format.
// =============================================================================

/**
 * Format cents into a currency string using Intl.NumberFormat.
 *
 * By default, 0 cents returns "Бесплатно" (for practice prices).
 * Pass allowZero=true to format 0 as "0,00 €" (for balance display).
 *
 * S-24: Always uses 2 decimal places for consistency in payment context.
 *
 * Examples:
 *   formatMoney(1500, 'EUR')              -> "15,00 €"  (in ru locale)
 *   formatMoney(0, 'EUR')                 -> "Бесплатно"
 *   formatMoney(0, 'EUR', 'ru', true)     -> "0,00 €"
 */
export function formatMoney(
  cents: number,
  currency: string,
  locale = 'ru',
  allowZero = false,
): string {
  if (cents === 0 && !allowZero) return 'Бесплатно'
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(cents / 100)
}

/**
 * Format an ISO datetime string into a human-readable date + time.
 *
 * Examples:
 *   formatDate('2026-02-28T07:00:00Z') -> "28 февраля, 10:00" (in Europe/Moscow)
 *   formatDate('2026-02-28T07:00:00Z', 'UTC') -> "28 февраля, 07:00"
 */
export function formatDate(
  isoString: string,
  timezone = 'UTC',
  locale = 'ru',
): string {
  const date = new Date(isoString)
  return new Intl.DateTimeFormat(locale, {
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: timezone,
  }).format(date)
}

/**
 * Format an ISO datetime string into a short date for section headers.
 *
 * Returns relative labels for today/tomorrow, otherwise "28 февраля".
 */
export function formatDateShort(
  isoString: string,
  timezone = 'UTC',
  locale = 'ru',
): string {
  const date = new Date(isoString)
  const now = new Date()

  // Compare calendar dates in the target timezone
  const fmt = (d: Date) =>
    new Intl.DateTimeFormat('en-CA', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      timeZone: timezone,
    }).format(d)

  const dateStr = fmt(date)
  const todayStr = fmt(now)
  const tomorrow = new Date(now)
  tomorrow.setDate(tomorrow.getDate() + 1)
  const tomorrowStr = fmt(tomorrow)

  if (dateStr === todayStr) return 'Сегодня'
  if (dateStr === tomorrowStr) return 'Завтра'

  return new Intl.DateTimeFormat(locale, {
    day: 'numeric',
    month: 'long',
    timeZone: timezone,
  }).format(date)
}

/**
 * Format an ISO datetime into a compact card date: "9 июня" / "12 сент.".
 *
 * Months follow the agreed VELO short-date table: a month whose genitive form
 * is <= 4 letters is written in full with NO period (мая / июня / июля); longer
 * ones are abbreviated to <= 4 letters + a period (янв. / февр. / мар. / апр. /
 * авг. / сент. / окт. / нояб. / дек.). Day + month only (no year, no time).
 * Timezone-safe (Intl with timeZone, no Date mutation).
 */
const VELO_SHORT_MONTHS = [
  'янв.', 'февр.', 'мар.', 'апр.', 'мая', 'июня',
  'июля', 'авг.', 'сент.', 'окт.', 'нояб.', 'дек.',
] as const

export function formatShortDate(isoString: string, timezone = 'UTC'): string {
  const date = new Date(isoString)
  const parts = new Intl.DateTimeFormat('en-CA', {
    day: 'numeric',
    month: 'numeric',
    timeZone: timezone,
  }).formatToParts(date)
  const day = parts.find((p) => p.type === 'day')?.value ?? ''
  const monthNum = Number(parts.find((p) => p.type === 'month')?.value ?? '1')
  const month = VELO_SHORT_MONTHS[monthNum - 1] ?? ''
  return `${day} ${month}`.trim()
}

/**
 * Format an ISO datetime string into time only: "07:00".
 */
export function formatTime(
  isoString: string,
  timezone = 'UTC',
  locale = 'ru',
): string {
  const date = new Date(isoString)
  return new Intl.DateTimeFormat(locale, {
    hour: '2-digit',
    minute: '2-digit',
    timeZone: timezone,
  }).format(date)
}

/**
 * Format an ISO datetime into the diary feed card date line:
 *   "23 января • Пятница • 14:35"
 * (day + month, weekday, time -- separated by bullets, matching the design).
 * Used by DiaryFeedCard. Defaults to the user's timezone (the diary is a
 * personal timeline -- "when it happened in my time").
 */
export function formatFeedDateTime(
  isoString: string,
  timezone = 'UTC',
  locale = 'ru',
): string {
  const date = new Date(isoString)
  const dayMonth = new Intl.DateTimeFormat(locale, {
    day: 'numeric',
    month: 'long',
    timeZone: timezone,
  }).format(date)
  const weekday = new Intl.DateTimeFormat(locale, {
    weekday: 'long',
    timeZone: timezone,
  }).format(date)
  const time = new Intl.DateTimeFormat(locale, {
    hour: '2-digit',
    minute: '2-digit',
    timeZone: timezone,
  }).format(date)
  // Capitalize the weekday (Intl returns lowercase in ru: "пятница").
  const weekdayCap = weekday.charAt(0).toUpperCase() + weekday.slice(1)
  return `${dayMonth} • ${weekdayCap} • ${time}`
}

/**
 * Format duration in minutes into a readable string.
 *
 * Examples:
 *   formatDuration(45)  -> "45 мин"
 *   formatDuration(90)  -> "1 ч 30 мин"
 *   formatDuration(120) -> "2 ч"
 */
export function formatDuration(minutes: number): string {
  if (minutes < 60) return `${minutes} мин`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (m === 0) return `${h} ч`
  return `${h} ч ${m} мин`
}

/**
 * Format participants count: "5/20 мест" or "∞" when unlimited.
 */
export function formatParticipants(
  current: number,
  max: number | null,
): string {
  if (max === null) return `${current} участн.`
  return `${current}/${max} мест`
}

/**
 * Check if a practice is full (has max_participants and no spots left).
 */
export function isFull(current: number, max: number | null): boolean {
  if (max === null) return false
  return current >= max
}

/**
 * Strip a trailing " (эфир)" marker from a practice title.
 *
 * Some seeded / manually created practices append "(эфир)" to the title (see
 * seed.py). Live practices already show a "В эфире" badge, so the suffix is
 * redundant noise in the title itself. Single source of truth for cleaning it
 * (FormShell check-in/feedback header; dashboard nearest-practice card).
 */
export function cleanPracticeTitle(title: string): string {
  return title.replace(/\s*\(эфир\)\s*$/i, '')
}
