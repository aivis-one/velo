// =============================================================================
// VELO Frontend -- MasterNotificationsView Screen Tests (probekit-screen-test)
// =============================================================================
//
// 309 lines. PATTERN = pure local-reactive-state screen -- NO api import, NO
// store import at all, confirmed by reading every import (.vue:79-83: vue,
// vue-router, @/components/layout, @/components/ui, @/components/shared/
// TimePickerSheet.vue -- nothing else). No seam to mock, no vi.mock('@/api/...')
// needed anywhere in this file.
//
// ⚠ THE CROWN CHECK -- THE PERSISTENCE ANSWER, MEASURED END TO END, NOT
// ASSUMED: onToggle (.vue:186-189) and onScheduleDays (.vue:190-193) and
// onTimePicked (.vue:176-180) each mutate ONLY the local `toggles`/`schedule`
// reactive objects -- `toggles[key] = value`, `schedule.days = days`,
// `schedule[edge] = value` -- and NOTHING ELSE. No api call, no store write,
// no localStorage/sessionStorage touch anywhere in this script.
//
// THIS IS CASE (a): A DOCUMENTED, HONEST STUB -- NOT AN UNDOCUMENTED GAP.
// Evidence, file:line:
//   - The file's own header comment (.vue:13-20): "BACKEND (stub → Zod): the
//     typed contract NotificationSettings carries only the four USER keys
//     ... NONE of the master keys, and no schedule. So this screen holds its
//     state LOCALLY and does NOT persist yet (we don't fake a save). Zod
//     task: extend NotificationSettings(+Update) with the master keys + a
//     schedule{from,to,days} object ... then wire persistence (a one-line
//     updateProfile in each handler below)."
//   - onToggle's own comment (.vue:183-185): "Local-only until the backend
//     contract is extended ... We do NOT call updateProfile with master
//     keys: they are not in NotificationSettingsUpdate and would be a
//     contract violation."
//   - Every handler ends with an explicit `// TODO(Zod): persist ...` line
//     (.vue:188,192,179).
// This is the SAME shape as SupportView's honest-submit stub, and a sharp
// contrast with the USER-side equivalent (UserNotificationsView, №469),
// which DOES persist -- optimistic toggle + authStore.updateProfile + revert
// + error toast on failure. The master zone's contract genuinely doesn't
// carry these keys yet (documented), so the gap is conscious, not an
// oversight -- but the CONSEQUENCE for a real master is exactly what the
// operator named: a changed preference is lost the moment they navigate
// away, because nothing anywhere holds it past this component instance.
//
// Asserted below as the REAL, current, honest-stub behaviour -- not a
// wishful "it saves" assertion: a toggle/schedule change updates the local
// UI immediately (looks optimistic), and a fresh remount (nothing to read
// state back from -- no api, no store, no storage was ever written) returns
// to the hardcoded defaults. This test is DELIBERATELY written to go RED the
// day Zod wires real persistence (SC-10 changelog-as-red), which is the
// correct outcome -- it should force an update to this file at that point,
// not silently keep passing against stale expectations.
//
// TimePickerSheet (.vue:68-74) wraps VBottomSheet, teleported to
// document.body, `v-if="open"` -- absent from the DOM entirely when closed,
// not just hidden. Its wheel (VWheel) only emits `update:modelValue` on a
// real `scroll` event debounced 140ms, which happy-dom does not fire in
// response to `el.scrollTo()` -- so a SPECIFIC non-default time cannot be
// dialled in through this DOM-only harness (same documented limitation as
// CreatePracticeView.test.ts's own TimePickerSheet coverage). Covered
// instead: opening the sheet for a given edge shows/commits THAT edge's
// current value via Save (proving `timePickerEdge` routes to the right
// field, not just that both fields exist), and the sheet closes afterward.
//
// Cyrillic fixtures/expected strings below were typed via the Write tool,
// never a shell heredoc.
// =============================================================================

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { createApp, nextTick, type App } from 'vue'
import MasterNotificationsView from '@/views/master/MasterNotificationsView.vue'

const back = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ back, push: vi.fn() }),
}))

// -----------------------------------------------------------------------------
// Mount
// -----------------------------------------------------------------------------

let app: App | null = null
let host: HTMLElement | null = null

function mount(): HTMLElement {
  host = document.createElement('div')
  document.body.appendChild(host)
  app = createApp(MasterNotificationsView)
  app.mount(host)
  return host
}

function unmountOnly(): void {
  app?.unmount()
  host?.remove()
  app = null
  host = null
}

async function flush(): Promise<void> {
  for (let i = 0; i < 6; i++) await nextTick()
}

function switchByRow(label: string): HTMLButtonElement {
  const row = Array.from(host?.querySelectorAll<HTMLElement>('.mn-card') ?? []).find(
    (r) => r.querySelector('.mn-card__title')?.textContent?.trim() === label,
  )
  const btn = row?.querySelector<HTMLButtonElement>('.v-switch')
  if (!btn) throw new Error(`no switch row labelled «${label}»`)
  return btn
}
function isOn(label: string): boolean {
  return switchByRow(label).getAttribute('aria-checked') === 'true'
}

function dayBtn(label: string): HTMLButtonElement {
  const btn = Array.from(host?.querySelectorAll<HTMLButtonElement>('.v-day-picker__day') ?? []).find(
    (b) => b.textContent?.trim() === label,
  )
  if (!btn) throw new Error(`no day button labelled «${label}»`)
  return btn
}
function dayOn(label: string): boolean {
  return dayBtn(label).getAttribute('aria-pressed') === 'true'
}

function timeFields(): HTMLButtonElement[] {
  return Array.from(host?.querySelectorAll<HTMLButtonElement>('.mn-sched__field') ?? [])
}
function fromField(): HTMLButtonElement {
  const b = timeFields()[0]
  if (!b) throw new Error('«from» time field did not render')
  return b
}
function toField(): HTMLButtonElement {
  const b = timeFields()[1]
  if (!b) throw new Error('«to» time field did not render')
  return b
}

/** The live (not mid-leave-transition) teleported sheet overlay. */
function liveSheet(): Element | null {
  return document.body.querySelector('.v-sheet__overlay:not(.v-sheet-leave-active)')
}
function sheetSaveBtn(): HTMLButtonElement | null {
  return liveSheet()?.querySelector<HTMLButtonElement>('.v-sheet__save') ?? null
}

// -----------------------------------------------------------------------------

beforeEach(() => {
  back.mockReset()
})

afterEach(() => {
  unmountOnly()
  document.body.querySelectorAll('.v-sheet__overlay').forEach((el) => el.remove())
  vi.clearAllMocks()
})

describe('MasterNotificationsView', () => {
  // ===========================================================================
  describe('THE PERSISTENCE ANSWER -- a documented honest stub, see banner', () => {
    it('toggling updates the LOCAL state immediately (looks optimistic)', async () => {
      mount()
      await flush()

      expect(isOn('Новое бронирование')).toBe(true) // default
      switchByRow('Новое бронирование').click()
      await flush()

      expect(isOn('Новое бронирование')).toBe(false)
    })

    it('a changed toggle is LOST on remount -- nothing anywhere holds it past this component instance', async () => {
      mount()
      await flush()
      switchByRow('Новое бронирование').click()
      await flush()
      expect(isOn('Новое бронирование')).toBe(false)

      unmountOnly()
      mount() // fresh instance -- no api, no store, no storage to read back from
      await flush()

      expect(isOn('Новое бронирование')).toBe(true) // back to the hardcoded default
    })

    it('a changed schedule day is ALSO lost on remount, same as the toggles', async () => {
      mount()
      await flush()
      expect(dayOn('ПН')).toBe(true) // default includes Monday
      dayBtn('ПН').click()
      await flush()
      expect(dayOn('ПН')).toBe(false)

      unmountOnly()
      mount()
      await flush()

      expect(dayOn('ПН')).toBe(true) // back to the default
    })
  })

  // ===========================================================================
  describe('toggles (.vue:111-158) -- representative rows, both directions', () => {
    it('"Новое бронирование" (Практики, default ON) toggles off', async () => {
      mount()
      await flush()

      switchByRow('Новое бронирование').click()
      await flush()

      expect(isOn('Новое бронирование')).toBe(false)
    })

    it('"Ежемесячный отчет" (Аналитика, the ONE default-OFF row) toggles on', async () => {
      mount()
      await flush()

      expect(isOn('Ежемесячный отчет')).toBe(false) // default
      switchByRow('Ежемесячный отчет').click()
      await flush()

      expect(isOn('Ежемесячный отчет')).toBe(true)
    })

    it('toggling one row does not affect a sibling row (each key is independent)', async () => {
      mount()
      await flush()

      switchByRow('От участников').click() // msg_participants
      await flush()

      expect(isOn('От участников')).toBe(false)
      expect(isOn('От поддержки')).toBe(true) // msg_support, untouched
      expect(isOn('Новое бронирование')).toBe(true) // unrelated group, untouched
    })
  })

  // ===========================================================================
  describe('schedule days (.vue:190-193, VDayPicker)', () => {
    it('default: Mon-Fri on, Sat/Sun off', async () => {
      mount()
      await flush()

      expect(dayOn('ПН')).toBe(true)
      expect(dayOn('ПТ')).toBe(true)
      expect(dayOn('СБ')).toBe(false)
      expect(dayOn('ВС')).toBe(false)
    })

    it('removing a default day and adding a non-default day both work', async () => {
      mount()
      await flush()

      dayBtn('ПН').click() // remove Monday
      await flush()
      dayBtn('СБ').click() // add Saturday
      await flush()

      expect(dayOn('ПН')).toBe(false)
      expect(dayOn('СБ')).toBe(true)
      expect(dayOn('ВТ')).toBe(true) // the rest of the default set is untouched
    })
  })

  // ===========================================================================
  describe('time picker (.vue:172-180, TimePickerSheet -- see banner for the wheel limitation)', () => {
    it('the fields show the current schedule.from/to by default', async () => {
      mount()
      await flush()

      expect(fromField().textContent?.trim()).toBe('08:00')
      expect(toField().textContent?.trim()).toBe('22:00')
    })

    it('opening the "from" field opens the REAL teleported sheet; Save commits back to "from" and closes it', async () => {
      mount()
      await flush()

      expect(liveSheet()).toBeNull()
      fromField().click()
      await flush()

      expect(liveSheet()).not.toBeNull()
      sheetSaveBtn()?.click()
      await flush()

      expect(liveSheet()).toBeNull() // closed
      expect(fromField().textContent?.trim()).toBe('08:00') // committed back to its OWN edge
      expect(toField().textContent?.trim()).toBe('22:00') // "to" untouched
    })

    it('opening the "to" field routes Save to "to", NOT "from" -- proves timePickerEdge, not just that both fields exist', async () => {
      mount()
      await flush()

      toField().click()
      await flush()
      sheetSaveBtn()?.click()
      await flush()

      expect(toField().textContent?.trim()).toBe('22:00') // its own edge, committed
      expect(fromField().textContent?.trim()).toBe('08:00') // NOT overwritten by the "to" commit
    })
  })
})
