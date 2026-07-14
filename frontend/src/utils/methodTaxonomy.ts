// =============================================================================
// VELO Frontend -- Method taxonomy seed/parse helper (batch L, FOUNDATION-2)
// =============================================================================
//
// Converts between the STORED flat `methods: string[]` (the «Направление — Вид»
// vocabulary the master apply-wizard emits) and the two-level picker's
// selection state (MethodTaxonomyPicker / MasterApplyView). Single source for
// both the flatten (selection -> string[]) and the seed/parse (string[] ->
// selection) sides, so the create wizard, the edit-profile picker and the
// pending-request display all round-trip through the SAME logic.
//
// DECISION Q3 = А (SURFACE-UNMATCHED, operator-reversed 2026-07-13, ПРОМТ
// №391 — was Q3=В DROP-UNMATCHED, ПРОМТ №349): any stored string that does
// NOT map to a known direction (or direction + style) is now SURFACED as the
// custom variant instead of dropped. The original DROP-UNMATCHED rationale
// ("prod is still test-grade with no real masters, zero real data loss") no
// longer held once the operator started actually using «Свой вариант» —
// submitted custom methods were being saved correctly by the backend but
// silently vanishing from every display (pending-request card AND the live
// «Методы» box after admin approval), which read as data loss even though
// none had actually occurred server-side.
//
// customText carries the surfaced value(s). The picker UI only ever edits
// ONE custom string at a time (a single "Свой вариант" toggle + text input),
// so flattenMethods only ever emits 0 or 1 unmatched entry in normal use —
// but parseMethods defensively handles the (should-not-happen) case of
// multiple unmatched strings by joining them with ", " rather than dropping
// all but one, so no text is ever lost even from unexpected/legacy data.
// Round-trip for MATCHED strings remains lossless (set-preserving; order
// normalises to the taxonomy encounter order); round-trip for the custom
// variant is lossless for the single-string case and text-preserving (not
// structure-preserving) for the multi-string edge case.
//
// The flatten side is byte-identical to the wizard's previous inline
// `allMethods` (same directionLabel map, same STYLE_LABEL, same « — »
// separator = space + U+2014 em dash + space, same custom-variant handling).
// =============================================================================

import type { PracticeDirection } from '@/api/types'
import { DIRECTION_OPTIONS, STYLE_OPTIONS_BY_DIRECTION, STYLE_LABEL } from '@/utils/practiceOptions'

/** The two-level picker's selection state. Mirrors the fields the wizard held
 *  inline (selectedDirections / selectedStyles / otherMethod*). */
export interface MethodSelection {
  directions: PracticeDirection[]
  /** direction value -> chosen style values (only for directions with styles). */
  styles: Record<string, string[]>
  customEnabled: boolean
  customText: string
}

/** « — » = space + U+2014 (em dash) + space. MUST match the wizard's flatten
 *  byte-for-byte so the stored payload is unchanged. */
const SEP = ' — '

// direction value -> Russian label (for the level-2 heading + flat payload).
const DIRECTION_LABEL: Record<string, string> = Object.fromEntries(
  DIRECTION_OPTIONS.map((o) => [o.value, o.label]),
)

// Russian label -> direction value (reverse, for parsing stored strings).
const DIRECTION_VALUE_BY_LABEL: Record<string, PracticeDirection> = Object.fromEntries(
  DIRECTION_OPTIONS.map((o) => [o.label, o.value]),
)

// Per direction: style label -> style value (reverse, scoped per direction so
// an identical style label under a different direction can't cross-match).
const STYLE_VALUE_BY_LABEL: Partial<Record<PracticeDirection, Record<string, string>>> =
  Object.fromEntries(
    Object.entries(STYLE_OPTIONS_BY_DIRECTION).map(([dir, opts]) => [
      dir,
      Object.fromEntries((opts ?? []).map((o) => [o.label, o.value])),
    ]),
  )

/** direction value -> Russian label, falling back to the raw value. */
export function directionLabel(dir: string): string {
  return DIRECTION_LABEL[dir] ?? dir
}

/**
 * Flatten a selection into the stored `methods: string[]`. A direction with
 * chosen styles emits «Направление — Вид» per style; a direction with no chosen
 * style emits «Направление»; the custom variant is emitted verbatim (trimmed).
 * Byte-identical to the wizard's previous inline `allMethods`.
 */
export function flattenMethods(sel: MethodSelection): string[] {
  const result: string[] = []
  for (const dir of sel.directions) {
    const label = directionLabel(dir)
    const styles = sel.styles[dir] ?? []
    if (styles.length > 0) {
      for (const st of styles) result.push(`${label}${SEP}${STYLE_LABEL[st] ?? st}`)
    } else {
      result.push(label)
    }
  }
  if (sel.customEnabled && sel.customText.trim()) {
    result.push(sel.customText.trim())
  }
  return result
}

/**
 * Parse a stored `methods: string[]` back into a selection (SURFACE-UNMATCHED,
 * Q3=А, ПРОМТ №391 — was DROP-UNMATCHED, Q3=В, ПРОМТ №349). An entry with the
 * « — » separator must match BOTH a known direction and a known style under
 * it to be treated as a direction+style pair; a bare entry must match a known
 * direction label. Anything else (including a « — » entry where either half
 * doesn't match) is surfaced verbatim as the custom variant instead of being
 * dropped — see the module header for why, and for how multiple unmatched
 * strings are handled (joined, not truncated to one).
 */
export function parseMethods(methods: string[]): MethodSelection {
  const directions: PracticeDirection[] = []
  const styles: Record<string, string[]> = {}
  const unmatched: string[] = []

  const addDirection = (d: PracticeDirection): void => {
    if (!directions.includes(d)) directions.push(d)
  }

  for (const raw of methods) {
    const s = raw.trim()
    if (!s) continue

    const sepIdx = s.indexOf(SEP)
    if (sepIdx !== -1) {
      // «Направление — Вид»: both halves must map to the taxonomy.
      const dirLabel = s.slice(0, sepIdx)
      const styleLabel = s.slice(sepIdx + SEP.length)
      const dirValue = DIRECTION_VALUE_BY_LABEL[dirLabel]
      const styleValue = dirValue ? STYLE_VALUE_BY_LABEL[dirValue]?.[styleLabel] : undefined
      if (!dirValue || !styleValue) {
        unmatched.push(s)
        continue
      }
      addDirection(dirValue)
      const list = styles[dirValue] ?? (styles[dirValue] = [])
      if (!list.includes(styleValue)) list.push(styleValue)
    } else {
      // Bare «Направление» (no style) -- or, if it doesn't match, custom text.
      const dirValue = DIRECTION_VALUE_BY_LABEL[s]
      if (!dirValue) {
        unmatched.push(s)
        continue
      }
      addDirection(dirValue)
    }
  }

  return {
    directions,
    styles,
    customEnabled: unmatched.length > 0,
    customText: unmatched.join(', '),
  }
}
