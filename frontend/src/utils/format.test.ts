// =============================================================================
// VELO Frontend -- format.ts Unit Tests (updated F5 review)
// =============================================================================

import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest'
import {
  formatMoney,
  formatDuration,
  formatDateShort,
  formatTime,
  formatParticipants,
  isFull,
  localSortKey,
} from '@/utils/format'

// -----------------------------------------------------------------------
// formatMoney
// -----------------------------------------------------------------------
describe('formatMoney', () => {
  it('returns "Бесплатно" for 0 cents by default', () => {
    expect(formatMoney(0, 'EUR')).toBe('Бесплатно')
  })

  it('formats 0 cents as currency when allowZero is true', () => {
    const result = formatMoney(0, 'EUR', 'ru', true)
    // Should contain "0" and NOT be "Бесплатно"
    expect(result).toContain('0')
    expect(result).not.toBe('Бесплатно')
  })

  it('formats EUR cents into euros with 2 decimal places', () => {
    const result = formatMoney(1500, 'EUR', 'ru')
    // S-24: always 2 decimals -> should contain "15" and ",00" or ".00"
    expect(result).toContain('15')
    expect(result).not.toBe('Бесплатно')
  })

  it('formats small amounts with 2 decimal places', () => {
    const result = formatMoney(50, 'EUR', 'ru')
    // 50 cents = 0.50 EUR -> should show "0,50" not "0,5"
    expect(result).toContain('0')
    expect(result).toMatch(/0[,.]50/)
  })

  it('formats large amounts', () => {
    const result = formatMoney(999900, 'EUR', 'ru')
    // 999900 cents = 9999 EUR
    expect(result).toContain('9')
    expect(result).not.toBe('Бесплатно')
  })

  it('allowZero does not affect non-zero amounts', () => {
    const withFlag = formatMoney(1500, 'EUR', 'ru', true)
    const withoutFlag = formatMoney(1500, 'EUR', 'ru', false)
    expect(withFlag).toBe(withoutFlag)
  })

  it('whole euro amounts still show decimals (S-24)', () => {
    const result = formatMoney(500, 'EUR', 'ru')
    // 500 cents = 5.00 EUR -> must show "5,00" not just "5"
    expect(result).toMatch(/5[,.]00/)
  })
})

// -----------------------------------------------------------------------
// formatDuration
// -----------------------------------------------------------------------
describe('formatDuration', () => {
  it('formats minutes under 60', () => {
    expect(formatDuration(45)).toBe('45 мин')
  })

  it('formats exact hours', () => {
    expect(formatDuration(60)).toBe('1 ч')
    expect(formatDuration(120)).toBe('2 ч')
  })

  it('formats hours and minutes', () => {
    expect(formatDuration(90)).toBe('1 ч 30 мин')
    expect(formatDuration(150)).toBe('2 ч 30 мин')
  })

  it('handles single minute', () => {
    expect(formatDuration(1)).toBe('1 мин')
  })
})

// -----------------------------------------------------------------------
// formatDateShort
// -----------------------------------------------------------------------
describe('formatDateShort', () => {
  // Clock-stable: the «Сегодня»/«Завтра» cases compare against `new Date()`, which
  // is flaky near local midnight (local-tomorrow can resolve to a UTC date +2 days).
  // Pin "now" to a mid-day, mid-month instant so they're deterministic.
  // formatDateShort itself is unchanged. The flake was a test-construction
  // artifact (dates built in the local runtime tz, then formatted as UTC), not
  // a formatDateShort bug.
  beforeAll(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-06-15T12:00:00Z'))
  })
  afterAll(() => {
    vi.useRealTimers()
  })

  it('returns "Сегодня" for today', () => {
    const now = new Date()
    const result = formatDateShort(now.toISOString(), 'UTC')
    expect(result).toBe('Сегодня')
  })

  it('returns "Завтра" for tomorrow', () => {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    // Set to noon to avoid timezone boundary issues
    tomorrow.setHours(12, 0, 0, 0)
    const result = formatDateShort(tomorrow.toISOString(), 'UTC')
    expect(result).toBe('Завтра')
  })

  it('returns a date string for other dates', () => {
    // A date far in the future
    const result = formatDateShort('2030-06-15T12:00:00Z', 'UTC', 'ru')
    // Should contain "15" and some month representation
    expect(result).toContain('15')
    expect(result).not.toBe('Сегодня')
    expect(result).not.toBe('Завтра')
  })
})

// -----------------------------------------------------------------------
// formatTime
// -----------------------------------------------------------------------
describe('formatTime', () => {
  it('formats UTC time', () => {
    const result = formatTime('2026-02-28T07:30:00Z', 'UTC')
    expect(result).toBe('07:30')
  })

  it('respects timezone offset', () => {
    // UTC 07:00 -> Europe/Moscow is UTC+3 -> 10:00
    const result = formatTime('2026-02-28T07:00:00Z', 'Europe/Moscow')
    expect(result).toBe('10:00')
  })
})

// -----------------------------------------------------------------------
// localSortKey (CR-1: list order must match the displayed local time)
// -----------------------------------------------------------------------
describe('localSortKey', () => {
  it('encodes the timezone-local wall-clock as YYYYMMDDHHmmss', () => {
    // 07:00 UTC in Europe/Moscow (UTC+3) reads 10:00 local.
    expect(localSortKey('2026-07-01T07:00:00Z', 'Europe/Moscow')).toBe(20260701100000)
  })

  it('orders by LOCAL time even when the absolute UTC order is reversed', () => {
    // A: 10:00 local in a UTC+0 zone  -> instant 10:00 UTC
    // B: 12:00 local in a UTC+5 zone  -> instant 07:00 UTC
    // Absolute epoch would put B (07:00 UTC) before A (10:00 UTC) — i.e. a 12:00
    // card above a 10:00 card. localSortKey must keep A (10:00) before B (12:00).
    const a = { at: '2026-07-01T10:00:00Z', tz: 'Atlantic/Reykjavik' } // UTC+0, no DST
    const b = { at: '2026-07-01T07:00:00Z', tz: 'Asia/Yekaterinburg' } // UTC+5, no DST

    // Sanity: the naive absolute-epoch order really is reversed vs the local order.
    expect(new Date(b.at).getTime()).toBeLessThan(new Date(a.at).getTime())

    // localSortKey restores the visible order: 10:00 (A) sorts before 12:00 (B).
    expect(localSortKey(a.at, a.tz)).toBeLessThan(localSortKey(b.at, b.tz))
    expect(localSortKey(a.at, a.tz)).toBe(20260701100000)
    expect(localSortKey(b.at, b.tz)).toBe(20260701120000)
  })
})

// -----------------------------------------------------------------------
// formatParticipants
// -----------------------------------------------------------------------
describe('formatParticipants', () => {
  it('shows current/max when max is set', () => {
    expect(formatParticipants(5, 20)).toBe('5/20')
  })

  it('shows count + label when max is null (unlimited)', () => {
    expect(formatParticipants(3, null)).toBe('3 участн.')
  })

  it('shows 0/max', () => {
    expect(formatParticipants(0, 10)).toBe('0/10')
  })
})

// -----------------------------------------------------------------------
// isFull
// -----------------------------------------------------------------------
describe('isFull', () => {
  it('returns false when unlimited (null max)', () => {
    expect(isFull(100, null)).toBe(false)
  })

  it('returns false when spots available', () => {
    expect(isFull(5, 20)).toBe(false)
  })

  it('returns true when current equals max', () => {
    expect(isFull(20, 20)).toBe(true)
  })

  it('returns true when current exceeds max', () => {
    expect(isFull(21, 20)).toBe(true)
  })
})
