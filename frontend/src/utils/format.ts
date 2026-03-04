// =============================================================================
// VELO Frontend -- Format Utilities (Phase F3.1, updated F4.2)
// =============================================================================
//
// Pure formatting functions used across practice cards, detail views,
// and any future components that display money, dates, or durations.
//
// All functions are locale-aware where applicable (defaults to 'ru').
//
// F4.2: formatMoney gains allowZero param for balance display.
// =============================================================================

/**
 * Format cents into a currency string using Intl.NumberFormat.
 *
 * By default, 0 cents returns "Бесплатно" (for practice prices).
 * Pass allowZero=true to format 0 as "€0,00" (for balance display).
 *
 * Examples:
 *   formatMoney(1500, 'EUR')              → "15,00 €"  (in ru locale)
 *   formatMoney(0, 'EUR')                 → "Бесплатно"
 *   formatMoney(0, 'EUR', 'ru', true)     → "0,00 €"
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
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(cents / 100)
}

/**
 * Format an ISO datetime string into a human-readable date + time.
 *
 * Examples:
 *   formatDate('2026-02-28T07:00:00Z') → "28 февраля, 10:00" (in Europe/Moscow)
 *   formatDate('2026-02-28T07:00:00Z', 'UTC') → "28 февраля, 07:00"
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
 * Format duration in minutes into a readable string.
 *
 * Examples:
 *   formatDuration(45)  → "45 мин"
 *   formatDuration(90)  → "1 ч 30 мин"
 *   formatDuration(120) → "2 ч"
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
