// =============================================================================
// VELO Frontend -- zoomLink.ts Unit Tests
// =============================================================================

import { describe, it, expect } from 'vitest'
import { resolveZoomLink } from '@/utils/zoomLink'

describe('resolveZoomLink', () => {
  it('prefers the personal link when present and https', () => {
    expect(resolveZoomLink('https://zoom.us/w/personal?tk=abc', 'https://zoom.us/j/manual')).toEqual({
      kind: 'personal',
      url: 'https://zoom.us/w/personal?tk=abc',
    })
  })

  it('falls back to the manual link, marked distinctly, when there is no personal link', () => {
    expect(resolveZoomLink(null, 'https://zoom.us/j/manual')).toEqual({
      kind: 'manual',
      url: 'https://zoom.us/j/manual',
    })
  })

  it('falls back to manual when the personal link is undefined (fixture without the field)', () => {
    expect(resolveZoomLink(undefined, 'https://zoom.us/j/manual')).toEqual({
      kind: 'manual',
      url: 'https://zoom.us/j/manual',
    })
  })

  it('reports pending when neither link exists', () => {
    expect(resolveZoomLink(null, null)).toEqual({ kind: 'pending', url: null })
  })

  it('reports pending when both links are empty strings', () => {
    expect(resolveZoomLink('', '')).toEqual({ kind: 'pending', url: null })
  })

  it('never returns a non-https personal link -- falls through to manual instead', () => {
    expect(resolveZoomLink('http://zoom.us/insecure', 'https://zoom.us/j/manual')).toEqual({
      kind: 'manual',
      url: 'https://zoom.us/j/manual',
    })
  })

  it('never returns a non-https manual link -- reports pending instead', () => {
    expect(resolveZoomLink(null, 'http://zoom.us/insecure')).toEqual({
      kind: 'pending',
      url: null,
    })
  })

  it('never silently reports personal when only manual is valid', () => {
    const result = resolveZoomLink(null, 'https://zoom.us/j/manual')
    expect(result.kind).not.toBe('personal')
  })
})
