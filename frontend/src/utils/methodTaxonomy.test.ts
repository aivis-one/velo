// =============================================================================
// VELO Frontend -- methodTaxonomy.ts Unit Tests
// =============================================================================
// R3/R4 regression (ПРОМТ №391): parseMethods used to DROP any string that
// didn't match the taxonomy (Q3=В); it now SURFACES it as the custom variant
// (Q3=А) so a master's «Свой вариант» entry (e.g. "терапия") shows up in the
// picker instead of silently vanishing after submit / after admin approval.
// =============================================================================

import { describe, it, expect } from 'vitest'
import { flattenMethods, parseMethods } from '@/utils/methodTaxonomy'

describe('parseMethods', () => {
  it('matches a bare direction label', () => {
    const parsed = parseMethods(['Йога'])
    expect(parsed.directions).toEqual(['yoga'])
    expect(parsed.styles).toEqual({})
    expect(parsed.customEnabled).toBe(false)
    expect(parsed.customText).toBe('')
  })

  it('matches a «Направление — Вид» pair', () => {
    const parsed = parseMethods(['Йога — Хатха-йога'])
    expect(parsed.directions).toEqual(['yoga'])
    expect(parsed.styles).toEqual({ yoga: ['hatha'] })
  })

  it('surfaces a single unmatched string as the custom variant (R3/R4)', () => {
    const parsed = parseMethods(['терапия'])
    expect(parsed.directions).toEqual([])
    expect(parsed.customEnabled).toBe(true)
    expect(parsed.customText).toBe('терапия')
  })

  it('surfaces a custom variant ALONGSIDE matched directions', () => {
    const parsed = parseMethods(['Йога', 'терапия'])
    expect(parsed.directions).toEqual(['yoga'])
    expect(parsed.customEnabled).toBe(true)
    expect(parsed.customText).toBe('терапия')
  })

  it('surfaces an unmatched «Направление — Вид»-shaped string verbatim (not silently dropped)', () => {
    const parsed = parseMethods(['Йога — Несуществующий вид'])
    expect(parsed.directions).toEqual([])
    expect(parsed.customEnabled).toBe(true)
    expect(parsed.customText).toBe('Йога — Несуществующий вид')
  })

  it('joins multiple unmatched strings rather than dropping all but one', () => {
    const parsed = parseMethods(['терапия', 'пилатес'])
    expect(parsed.customEnabled).toBe(true)
    expect(parsed.customText).toBe('терапия, пилатес')
  })

  it('ignores blank entries', () => {
    const parsed = parseMethods(['Йога', '', '   '])
    expect(parsed.directions).toEqual(['yoga'])
    expect(parsed.customEnabled).toBe(false)
  })
})

describe('parseMethods -> flattenMethods round-trip', () => {
  it('is lossless for a matched direction+style', () => {
    const original = ['Йога — Хатха-йога']
    expect(flattenMethods(parseMethods(original))).toEqual(original)
  })

  it('is lossless for a single custom string (R3/R4 the common case)', () => {
    const original = ['терапия']
    expect(flattenMethods(parseMethods(original))).toEqual(original)
  })

  it('is lossless for a mix of matched + custom', () => {
    const original = ['Йога', 'терапия']
    expect(flattenMethods(parseMethods(original))).toEqual(original)
  })

  it('is stable (idempotent) on a second round-trip after the multi-unmatched join', () => {
    const first = flattenMethods(parseMethods(['терапия', 'пилатес']))
    expect(first).toEqual(['терапия, пилатес'])
    // Second round-trip must reproduce the exact same result (no further drift).
    const second = flattenMethods(parseMethods(first))
    expect(second).toEqual(first)
  })
})
