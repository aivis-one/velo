import { describe, it, expect } from 'vitest'
import { diaryWriteTarget } from './diaryComposeTarget'
import type { DiaryFeedCategory } from '@/api/types'

describe('diaryWriteTarget (T5 filter-aware compose routing)', () => {
  it('writes to Дневник (note) when no filter is active ("Все" / root)', () => {
    expect(diaryWriteTarget([])).toBe('note')
  })

  it('writes to Дневник (note) when only entries is selected', () => {
    expect(diaryWriteTarget(['entries'])).toBe('note')
  })

  it('writes to Сонник (dream) when only dreams is selected', () => {
    expect(diaryWriteTarget(['dreams'])).toBe('dream')
  })

  it('defaults to Дневник (note) when entries + dreams are both selected', () => {
    expect(diaryWriteTarget(['entries', 'dreams'])).toBe('note')
    expect(diaryWriteTarget(['dreams', 'entries'])).toBe('note')
  })

  it('blocks (null) each read-only category on its own', () => {
    expect(diaryWriteTarget(['practices'])).toBeNull()
    expect(diaryWriteTarget(['checkins'])).toBeNull()
    expect(diaryWriteTarget(['feedbacks'])).toBeNull()
  })

  it('blocks (null) any mix that contains a read-only category (variant в)', () => {
    expect(diaryWriteTarget(['entries', 'feedbacks'])).toBeNull()
    expect(diaryWriteTarget(['dreams', 'checkins'])).toBeNull()
    expect(diaryWriteTarget(['entries', 'dreams', 'practices'])).toBeNull()
  })

  it('covers every single-category selection exhaustively', () => {
    const expected: Record<DiaryFeedCategory, ReturnType<typeof diaryWriteTarget>> = {
      entries: 'note',
      dreams: 'dream',
      practices: null,
      checkins: null,
      feedbacks: null,
    }
    for (const [cat, target] of Object.entries(expected)) {
      expect(diaryWriteTarget([cat as DiaryFeedCategory])).toBe(target)
    }
  })
})
