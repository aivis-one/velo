// =============================================================================
// VELO Frontend -- bookingStatus.ts Unit Tests
// =============================================================================

import { describe, it, expect } from 'vitest'
import {
  isLiveNow,
  hasEnded,
  isFree,
  practiceStartMs,
  practiceEndMs,
} from '@/utils/bookingStatus'
import type { BookingWithPracticeResponse } from '@/api/types'

const NOW = 1_700_000_000_000 // fixed epoch ms

/** Minimal booking: only the fields the helpers read. */
function makeBooking(opts: {
  startOffsetMin: number
  durationMin: number
  free?: boolean
}): BookingWithPracticeResponse {
  return {
    practice: {
      scheduled_at: new Date(NOW + opts.startOffsetMin * 60_000).toISOString(),
      duration_minutes: opts.durationMin,
      is_free: opts.free ?? false,
    },
  } as unknown as BookingWithPracticeResponse
}

describe('isLiveNow', () => {
  it('true when started and not yet ended', () => {
    expect(isLiveNow(makeBooking({ startOffsetMin: -10, durationMin: 60 }), NOW)).toBe(true)
  })
  it('false before start', () => {
    expect(isLiveNow(makeBooking({ startOffsetMin: 5, durationMin: 60 }), NOW)).toBe(false)
  })
  it('false after end', () => {
    expect(isLiveNow(makeBooking({ startOffsetMin: -120, durationMin: 60 }), NOW)).toBe(false)
  })
  it('false exactly at end (end is exclusive)', () => {
    expect(isLiveNow(makeBooking({ startOffsetMin: -60, durationMin: 60 }), NOW)).toBe(false)
  })
})

describe('hasEnded', () => {
  it('true at and after end', () => {
    expect(hasEnded(makeBooking({ startOffsetMin: -60, durationMin: 60 }), NOW)).toBe(true)
  })
  it('false while live', () => {
    expect(hasEnded(makeBooking({ startOffsetMin: -10, durationMin: 60 }), NOW)).toBe(false)
  })
  it('false before start', () => {
    expect(hasEnded(makeBooking({ startOffsetMin: 30, durationMin: 60 }), NOW)).toBe(false)
  })
})

describe('isFree', () => {
  it('reflects practice.is_free', () => {
    expect(isFree(makeBooking({ startOffsetMin: 0, durationMin: 60, free: true }))).toBe(true)
    expect(isFree(makeBooking({ startOffsetMin: 0, durationMin: 60, free: false }))).toBe(false)
  })
})

describe('practiceStartMs / practiceEndMs', () => {
  it('end = start + duration', () => {
    const b = makeBooking({ startOffsetMin: 0, durationMin: 45 })
    expect(practiceEndMs(b) - practiceStartMs(b)).toBe(45 * 60_000)
  })
})
