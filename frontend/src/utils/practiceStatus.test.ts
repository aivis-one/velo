// =============================================================================
// VELO Frontend -- practiceStatus.ts Unit Tests
// =============================================================================

import { describe, it, expect } from 'vitest'
import { masterPracticeBadge, practiceEndMs, practiceHasEnded } from '@/utils/practiceStatus'

describe('masterPracticeBadge', () => {
  it('draft → Черновик / warning', () => {
    expect(masterPracticeBadge('draft')).toEqual({ label: 'Черновик', variant: 'warning' })
  })
  it('completed → Завершена / success', () => {
    expect(masterPracticeBadge('completed')).toEqual({ label: 'Завершена', variant: 'success' })
  })
  it('cancelled → Отменена / error', () => {
    expect(masterPracticeBadge('cancelled')).toEqual({ label: 'Отменена', variant: 'error' })
  })
  it('scheduled / live / deleted → null (active phase has no badge)', () => {
    expect(masterPracticeBadge('scheduled')).toBeNull()
    expect(masterPracticeBadge('live')).toBeNull()
    expect(masterPracticeBadge('deleted')).toBeNull()
  })
})

const NOW = 1_700_000_000_000
function prac(startOffsetMin: number, durationMin: number) {
  return {
    scheduled_at: new Date(NOW + startOffsetMin * 60_000).toISOString(),
    duration_minutes: durationMin,
  }
}

describe('practiceEndMs / practiceHasEnded', () => {
  it('end = start + duration', () => {
    const p = prac(0, 45)
    expect(practiceEndMs(p) - new Date(p.scheduled_at).getTime()).toBe(45 * 60_000)
  })
  it('ended when now >= end', () => {
    expect(practiceHasEnded(prac(-60, 60), NOW)).toBe(true) // ends exactly now
    expect(practiceHasEnded(prac(-10, 60), NOW)).toBe(false) // still running
    expect(practiceHasEnded(prac(30, 60), NOW)).toBe(false) // not started
  })
})
