// =============================================================================
// VELO Frontend -- format.ts Unit Tests (updated Phase F4.2)
// =============================================================================

import { describe, it, expect } from 'vitest'
import {
  formatMoney,
  formatDuration,
  formatDateShort,
  formatTime,
  formatParticipants,
  isFull,
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

  it('formats EUR cents into euros', () => {
    const result = formatMoney(1500, 'EUR', 'ru')
    // Intl.NumberFormat output may vary by environment, but should
    // contain "15" and euro sign/code
    expect(result).toContain('15')
    // Should not show "Бесплатно"
    expect(result).not.toBe('Бесплатно')
  })

  it('formats small amounts correctly', () => {
    const result = formatMoney(50, 'EUR', 'ru')
    // 50 cents = 0.50 EUR
    expect(result).toContain('0')
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
    // UTC 07:00 → Europe/Moscow is UTC+3 → 10:00
    const result = formatTime('2026-02-28T07:00:00Z', 'Europe/Moscow')
    expect(result).toBe('10:00')
  })
})

// -----------------------------------------------------------------------
// formatParticipants
// -----------------------------------------------------------------------
describe('formatParticipants', () => {
  it('shows current/max when max is set', () => {
    expect(formatParticipants(5, 20)).toBe('5/20 мест')
  })

  it('shows count + label when max is null (unlimited)', () => {
    expect(formatParticipants(3, null)).toBe('3 участн.')
  })

  it('shows 0/max', () => {
    expect(formatParticipants(0, 10)).toBe('0/10 мест')
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
