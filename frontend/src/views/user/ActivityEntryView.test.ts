// =============================================================================
// VELO Frontend -- ActivityEntryView Screen Tests (B57, PROMPT No761)
// =============================================================================
//
// WHY: pure local-form screen -- no store, no network, `Сохранить` is a
// deliberate honest stub (the storage contract is with the backend teammate,
// B64). Coverage focuses on the form's OWN logic, which is where an
// adversarial verify pass on the build found two real bugs before this file
// existed:
//   1. The activity chip that visually lights up could disagree with which
//      activity `form.seedActivity` actually held, whenever a typed custom
//      value exactly matched a seed name (the binding read the DERIVED
//      `chosenActivity`, not the selection state itself). Fixed: the chip now
//      binds to `form.seedActivity` directly.
//   2. Fixing only the TIME field left a stale "event is in the future"
//      message stuck on the DATE field, because the message is set on
//      `errors.date` but nothing cleared it when only time changed. Fixed:
//      `onTime` now clears it too (and only that specific message, never the
//      "date is required" one).
// This file pins both fixes as regression coverage.
//
// SHEET DRIVING: DatePickerSheet/TimePickerSheet are the REAL, teleported
// components -- same technique as CreatePracticeView.test.ts, which built and
// proved this exact recipe. VWheel (the time wheel) only emits on a real
// `scroll` event happy-dom never fires, so TimePickerSheet's own no-model
// default (12:00) is the only time reachable through the real sheet, and it
// IS the real sheet: the tap, the save button and update:model-value -> form
// wiring are genuinely exercised, not stubbed.
//
// CLOCK: `isFuture()` compares against `DateTime.now()`, pinned via
// vi.useFakeTimers(). The viewer timezone is forced to UTC by seeding a real
// auth-store user -- useViewerTimezone.ts reads authStore.user.timezone with
// NO fallback, so an unseeded user would silently take the runner's local
// zone, which is exactly the risk verification flagged.
//
// ROUTER: a full vue-router module mock (not importOriginal) is safe here --
// unlike DiaryFeedView, nothing in this screen's import chain transitively
// touches the real @/router singleton (checked: neither sheet imports it).
// =============================================================================

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { createApp, nextTick, type App } from 'vue'
import { createPinia, setActivePinia, type Pinia } from 'pinia'
import ActivityEntryView from './ActivityEntryView.vue'
import { useAuthStore } from '@/stores/auth'
import type { UserResponse } from '@/api/types'

const push = vi.fn()
const back = vi.fn()
const replace = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push, back, replace }),
}))

const toastInfo = vi.fn()
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ error: vi.fn(), success: vi.fn(), info: toastInfo }),
}))

// A day well inside the fake-timer month, with headroom on both sides so a
// "future" pick and a "past" pick are both reachable without month navigation.
const NOW = new Date('2026-08-15T10:00:00Z')

function user(overrides: Partial<UserResponse> = {}): UserResponse {
  return {
    id: 'user_1',
    telegram_id: 1,
    role: 'user',
    first_name: 'Аня',
    last_name: null,
    avatar_url: null,
    timezone: 'UTC',
    language: 'ru',
    is_active: true,
    balance_cents: 0,
    created_at: '2026-01-01T00:00:00Z',
    last_login_at: null,
    onboarding_completed: true,
    master_onboarding_completed: false,
    phone: null,
    bio: null,
    email: null,
    role_switch: null,
    ...overrides,
  }
}

let app: App | null = null
let host: HTMLElement | null = null
let pinia: Pinia

function mount(): HTMLElement {
  host = document.createElement('div')
  document.body.appendChild(host)
  app = createApp(ActivityEntryView)
  app.use(pinia)
  app.mount(host)
  return host
}

async function flush(ticks = 3): Promise<void> {
  for (let i = 0; i < ticks; i++) await nextTick()
}

beforeEach(() => {
  vi.useFakeTimers()
  vi.setSystemTime(NOW)
  push.mockReset()
  back.mockReset()
  replace.mockReset()
  toastInfo.mockReset()
  pinia = createPinia()
  setActivePinia(pinia)
  useAuthStore().user = user()
})

afterEach(() => {
  app?.unmount()
  host?.remove()
  app = null
  host = null
  // Purge any teleported sheet corpse before the next test's liveSheet() query
  // (same discipline CreatePracticeView.test.ts documents -- a closed sheet
  // sits on document.body mid-leave-transition in happy-dom).
  document.body.innerHTML = ''
  vi.useRealTimers()
})

// -- Query helpers, mirroring the component's own BEM classes ---------------

function pickerTriggers(): HTMLButtonElement[] {
  return Array.from(host?.querySelectorAll<HTMLButtonElement>('.activity-entry__picker') ?? [])
}

function liveSheet(): Element | null {
  return document.body.querySelector('.v-sheet__overlay:not(.v-sheet-leave-active)')
}

function sheetSave(): HTMLButtonElement | null {
  return liveSheet()?.querySelector<HTMLButtonElement>('.v-sheet__save') ?? null
}

function dayCell(n: number): HTMLButtonElement | undefined {
  return Array.from(liveSheet()?.querySelectorAll<HTMLButtonElement>('.dps__day') ?? []).find(
    (b) => !b.classList.contains('dps__day--dim') && b.textContent?.trim() === String(n),
  )
}

/** Drive the real teleported DatePickerSheet behind «Дата». */
async function pickDate(day: number): Promise<void> {
  pickerTriggers()[0]?.click()
  await flush()
  const cell = dayCell(day)
  if (!cell) throw new Error(`day ${day} not in the open month`)
  cell.click()
  await flush()
  sheetSave()?.click()
  await flush()
}

/** Drive the real teleported TimePickerSheet, taking its no-model default
 *  (12:00) -- see the file banner for why the wheel itself is unreachable. */
async function pickDefaultTime(): Promise<void> {
  pickerTriggers()[1]?.click()
  await flush()
  sheetSave()?.click()
  await flush()
}

function chip(label: string): HTMLElement | undefined {
  return [...(host?.querySelectorAll<HTMLElement>('.v-chip') ?? [])].find(
    (c) => c.textContent?.trim() === label,
  )
}

function customInput(): HTMLInputElement | null {
  // VInput has `inheritAttrs: false` and forwards `$attrs` (class included)
  // straight onto the native <input>, not onto its `.v-input` wrapper -- so
  // the class lands ON the input, not on an ancestor of it.
  return host?.querySelector<HTMLInputElement>('input.activity-entry__own') ?? null
}

function saveButton(el: HTMLElement): HTMLButtonElement {
  const btn = [...el.querySelectorAll('button')].find((b) => b.textContent?.trim() === 'Сохранить')
  if (!btn) throw new Error('Сохранить button not found')
  return btn as HTMLButtonElement
}

function dateError(el: HTMLElement): string | null {
  return (
    el.querySelector('.activity-entry__field:nth-of-type(1) .activity-entry__field-error')
      ?.textContent ?? null
  )
}

describe('ActivityEntryView', () => {
  it('renders the title and all six seed activities, in the owner’s written order', async () => {
    const el = mount()
    await flush()

    expect(el.querySelector('h1')?.textContent).toBe('Новое событие')
    const labels = [...el.querySelectorAll('.v-chip')].map((c) => c.textContent?.trim())
    expect(labels).toEqual(['Медитация', 'Массаж', 'Танцы', 'Вокал', 'Йога', 'Гвоздестояние'])
  })

  it('blocks submit and shows required errors when nothing is filled', async () => {
    const el = mount()
    await flush()

    saveButton(el).click()
    await flush()

    expect(toastInfo).not.toHaveBeenCalled()
    const errors = [...el.querySelectorAll('.activity-entry__field-error')].map((e) =>
      e.textContent?.trim(),
    )
    expect(errors).toEqual(['Укажите дату', 'Укажите время', 'Выберите активность'])
  })

  it('picking a seed chip highlights exactly that chip', async () => {
    const el = mount()
    await flush()

    chip('Танцы')?.click()
    await flush()

    const active = [...el.querySelectorAll('.v-chip--active')]
    expect(active.map((c) => c.textContent?.trim())).toEqual(['Танцы'])
  })

  it('REGRESSION: typing a value that matches a seed name does not falsely light up its chip', async () => {
    // The bug: :active was bound to `chosenActivity` (customActivity.trim() ||
    // seedActivity), so typing "Йога" made the "Йога" chip glow even though
    // seedActivity was still '' and the user never tapped it.
    const el = mount()
    await flush()

    const input = customInput()
    expect(input).toBeTruthy()
    if (input) {
      input.value = 'Йога'
      input.dispatchEvent(new Event('input'))
    }
    await flush()

    expect(el.querySelector('.v-chip--active')).toBeNull()
  })

  it('picking a chip clears a half-typed custom value, and typing clears a picked chip', async () => {
    const el = mount()
    await flush()

    const input = customInput()
    if (input) {
      input.value = 'Плавание'
      input.dispatchEvent(new Event('input'))
    }
    await flush()
    chip('Массаж')?.click()
    await flush()
    expect(customInput()?.value).toBe('')
    expect(el.querySelector('.v-chip--active')?.textContent?.trim()).toBe('Массаж')

    if (input) {
      input.value = 'Плавание'
      input.dispatchEvent(new Event('input'))
    }
    await flush()
    expect(el.querySelector('.v-chip--active')).toBeNull()
  })

  it('rejects a future date+time on submit and blocks the honest-stub toast', async () => {
    const el = mount()
    await flush()

    chip('Йога')?.click()
    await pickDate(28) // 2026-08-28, after the pinned NOW (2026-08-15)
    await pickDefaultTime() // 12:00, still same-day future relative to 10:00 NOW baseline moot -- date alone is future

    saveButton(el).click()
    await flush()

    expect(toastInfo).not.toHaveBeenCalled()
    expect(dateError(el)).toBe('Можно записать только прошедшее событие')
  })

  it('accepts a past date+time and fires the honest-stub toast', async () => {
    const el = mount()
    await flush()

    chip('Йога')?.click()
    await pickDate(10) // 2026-08-10, before the pinned NOW
    await pickDefaultTime()

    saveButton(el).click()
    await flush()

    expect(el.querySelectorAll('.activity-entry__field-error').length).toBe(0)
    expect(toastInfo).toHaveBeenCalledWith('Функциональность пока недоступна')
  })

  it('REGRESSION: touching only the time clears a stale future-date message off the date field', async () => {
    const el = mount()
    await flush()

    chip('Йога')?.click()
    await pickDate(28) // future
    await pickDefaultTime()
    saveButton(el).click()
    await flush()
    expect(dateError(el)).toBe('Можно записать только прошедшее событие')

    // Touch time again (re-opening and re-saving the same 12:00 default is
    // enough to fire onTime -- the fix does not require the VALUE to change,
    // only that the user acted on the time field).
    await pickDefaultTime()

    expect(dateError(el)).toBeNull()
  })

  it('onDate never clears the "date is required" message via the future-check path', async () => {
    // Boundary the fix must respect: onTime only clears FUTURE_MESSAGE, never
    // "Укажите дату". Submit with time filled but date empty, then touch time
    // again -- the required-date error must survive.
    const el = mount()
    await flush()

    chip('Массаж')?.click()
    await pickDefaultTime()
    saveButton(el).click()
    await flush()
    expect(dateError(el)).toBe('Укажите дату')

    await pickDefaultTime()
    expect(dateError(el)).toBe('Укажите дату')
  })

  it('mood and reflection stay optional -- a full submit with neither still saves', async () => {
    const el = mount()
    await flush()

    chip('Вокал')?.click()
    await pickDate(10)
    await pickDefaultTime()
    saveButton(el).click()
    await flush()

    expect(toastInfo).toHaveBeenCalledTimes(1)
  })

  it('the mood control and custom-activity input carry accessible names', async () => {
    const el = mount()
    await flush()

    expect(el.querySelector('.mood-picker')?.getAttribute('aria-label')).toBe('Мое состояние')
    // hide-label keeps a real <label> in the DOM, visually hidden only.
    expect(el.textContent).toContain('Свой вариант активности')
  })

  it('the back button calls router.back()', async () => {
    const el = mount()
    await flush()

    el.querySelector<HTMLElement>('[aria-label="Назад"]')?.click()
    expect(back).toHaveBeenCalledTimes(1)
  })
})
