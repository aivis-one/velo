// =============================================================================
// VELO Frontend -- MoodPicker Unit Tests (B57, PROMPT No761)
// =============================================================================
//
// Dependency-free SFC mount (createApp + happy-dom container) -- the repo has no
// @vue/test-utils usage, and plugin-vue (vitest.config) compiles the .vue for us.
//
// WHAT IS WORTH ASSERTING HERE, and it is not "does it render three buttons":
// this control's whole mechanism is that selection swaps TWO CSS custom
// properties and changes WHICH of two different drawings is shown. A test that
// only counted buttons would pass on a control that never visibly reacts.
// =============================================================================

import { describe, it, expect, afterEach } from 'vitest'
import { createApp, type App } from 'vue'
import MoodPicker from '@/components/shared/MoodPicker.vue'
import { ACTIVITY_MOODS, type ActivityMood } from '@/utils/activityEntry'

let app: App | null = null
let host: HTMLElement | null = null

function mount(props: { modelValue?: ActivityMood | null; size?: number } = {}): HTMLElement {
  host = document.createElement('div')
  document.body.appendChild(host)
  app = createApp(MoodPicker, props)
  app.mount(host)
  return host
}

afterEach(() => {
  app?.unmount()
  host?.remove()
  app = null
  host = null
})

const OPT = '.mood-picker__opt'

/** Indexed access under `noUncheckedIndexedAccess` -- fail loudly on a missing
 *  option rather than let a test read `undefined` and pass vacuously. */
function opt(el: ParentNode, i: number): HTMLElement {
  const found = [...el.querySelectorAll(OPT)][i]
  if (!found) throw new Error(`no option at index ${i}`)
  return found as HTMLElement
}

describe('MoodPicker', () => {
  it('renders one option per mood, in the design order', () => {
    const el = mount()
    const labels = [...el.querySelectorAll(OPT)].map((o) => o.getAttribute('aria-label'))
    expect(labels).toEqual(['Так себе', 'Хорошо', 'Отлично'])
  })

  it('is a radiogroup and every option is a radio', () => {
    const el = mount()
    expect(el.querySelector('.mood-picker')?.getAttribute('role')).toBe('radiogroup')
    const roles = [...el.querySelectorAll(OPT)].map((o) => o.getAttribute('role'))
    expect(roles).toEqual(['radio', 'radio', 'radio'])
  })

  it('marks exactly the selected option checked', () => {
    const el = mount({ modelValue: 'good' })
    const checked = [...el.querySelectorAll(OPT)].map((o) => o.getAttribute('aria-checked'))
    expect(checked).toEqual(['false', 'true', 'false'])
  })

  it('nothing is checked when the value is null -- the field is optional', () => {
    const el = mount({ modelValue: null })
    const checked = [...el.querySelectorAll(OPT)].map((o) => o.getAttribute('aria-checked'))
    expect(checked).toEqual(['false', 'false', 'false'])
  })

  it('selecting swaps the two colour variables, not just a class', () => {
    // The mechanism itself: resting = white circle + coloured face; selected =
    // coloured circle + white face. Asserting the class alone would pass on a
    // control whose colours never move.
    const el = mount({ modelValue: 'great' })
    const soso = opt(el, 0)
    const great = opt(el, 2)
    const fire = ACTIVITY_MOODS[2]?.colorVar
    const confused = ACTIVITY_MOODS[0]?.colorVar

    expect(great.style.getPropertyValue('--vam-face')).toBe(fire)
    expect(great.style.getPropertyValue('--vam-ink')).toBe('var(--velo-white)')
    expect(soso.style.getPropertyValue('--vam-face')).toBe('var(--velo-white)')
    expect(soso.style.getPropertyValue('--vam-ink')).toBe(confused)
  })

  it('emits the key on click, and null when the selected one is clicked again', async () => {
    const emitted: (ActivityMood | null)[] = []
    host = document.createElement('div')
    document.body.appendChild(host)
    app = createApp(MoodPicker, {
      modelValue: null,
      'onUpdate:modelValue': (v: ActivityMood | null) => emitted.push(v),
    })
    app.mount(host)

    opt(host, 1).click()
    expect(emitted).toEqual(['good'])

    // Re-mount as if the parent had applied the value, then click the same one.
    app.unmount()
    host.remove()
    host = document.createElement('div')
    document.body.appendChild(host)
    app = createApp(MoodPicker, {
      modelValue: 'good',
      'onUpdate:modelValue': (v: ActivityMood | null) => emitted.push(v),
    })
    app.mount(host)
    opt(host, 1).click()
    expect(emitted).toEqual(['good', null])
  })

  it('draws a different glyph for the selected state, not a recolour', () => {
    // The resting and selected faces are genuinely different artwork (measured
    // with getBBox: 64.4% vs 53.6% of the circle), which shows up as a
    // different viewBox window onto the source sheet.
    const rest = mount({ modelValue: null })
    const restBox = opt(rest, 1).querySelector('svg')?.getAttribute('viewBox')
    app?.unmount()
    host?.remove()

    const sel = mount({ modelValue: 'good' })
    const selBox = opt(sel, 1).querySelector('svg')?.getAttribute('viewBox')

    expect(restBox).toBeTruthy()
    expect(selBox).toBeTruthy()
    expect(selBox).not.toBe(restBox)
  })

  it('carries no hardcoded colour -- every fill routes through a variable', () => {
    const el = mount({ modelValue: 'soso' })
    const svg = el.querySelector('svg')
    const fills = [...(svg?.querySelectorAll('[fill]') ?? [])].map((n) => n.getAttribute('fill'))
    expect(fills.length).toBeGreaterThan(0)
    expect(fills.every((f) => f !== null && f.startsWith('var(--'))).toBe(true)
  })
})
