// =============================================================================
// VELO Frontend -- SupportView Screen Tests (probekit-screen-test)
// =============================================================================
//
// 313 lines. PATTERN B (local-ref form) -- confirmed by reading every import:
// no store, no API seam, no fetch ladder. All state is local refs (topic /
// otherText / message / submitted, .vue:121-133). The only "ladder" is the
// FORM -> TERMINAL transition driven by `submitted`.
//
// External boundaries: vue-router (router.back / router.push) and
// useKeyboardFieldScroll (@/composables, .vue:96,101), mocked so happy-dom
// doesn't choke on its viewport-focus logic -- the `onFieldFocus` spy is
// enough, it is never asserted on (this screen has no keyboard-viewport
// behaviour of its own to test, that composable owns it). No toast anywhere
// on this screen -- grepped, confirmed.
//
// HONEST STUB (.vue:9-15,135-150): onSubmit builds a payload, `console.info`s
// it, and flips `submitted = true`. No backend, no network call, no router
// push on submit. Every submit test below asserts exactly that -- the day
// Zod wires a real ticket-intake POST, these go red as the changelog (same
// discipline as EditProfileView's delete-stub tests).
//
// DRIVEN THROUGH THE DOM THROUGHOUT -- click the radio, type into the
// textarea/input, click the button -- never by reaching into topic/otherText/
// message refs directly (the local-form empty-green trap the skill warns
// about: poking refs would assert this file's own fixture, not the screen).
//
// MONEY: none. Cyrillic fixtures/expected strings below were still typed via
// the Write tool, not a shell heredoc, per house habit.
//
// No modal, no v-show (grepped -- v-if throughout), no order dependence --
// every test mounts its own app.
// =============================================================================

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { createApp, nextTick, type App } from 'vue'
import SupportView from '@/views/user/SupportView.vue'

const back = vi.fn()
const push = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ back, push }),
}))

const onFieldFocus = vi.fn()
vi.mock('@/composables/useKeyboardFieldScroll', () => ({
  useKeyboardFieldScroll: () => ({ onFieldFocus }),
}))

// -----------------------------------------------------------------------------
// Mount
// -----------------------------------------------------------------------------

let app: App | null = null
let host: HTMLElement | null = null

function mount(): HTMLElement {
  host = document.createElement('div')
  document.body.appendChild(host)
  app = createApp(SupportView)
  app.mount(host)
  return host
}

async function flush(): Promise<void> {
  for (let i = 0; i < 3; i++) await nextTick()
}

const TOPIC_LABEL = {
  payment: 'Проблема с оплатой / транзакцией',
  complaint_master: 'Жалоба на мастера',
  practice: 'Проблема с практикой',
  technical: 'Технический вопрос',
  other: 'Другое',
} as const

function radioByLabel(label: string): HTMLButtonElement {
  const btn = Array.from(host?.querySelectorAll<HTMLButtonElement>('.v-radio') ?? []).find(
    (b) => b.querySelector('.v-radio__label')?.textContent?.trim() === label,
  )
  if (!btn) throw new Error(`no radio labelled «${label}»`)
  return btn
}
function messageField(): HTMLTextAreaElement {
  const el = host?.querySelector<HTMLTextAreaElement>('.v-textarea__field')
  if (!el) throw new Error('message textarea did not render')
  return el
}
function otherInput(): HTMLInputElement | null {
  return host?.querySelector<HTMLInputElement>('.support__other-input') ?? null
}
function submitBtn(): HTMLButtonElement {
  const el = host?.querySelector<HTMLButtonElement>('.support__submit')
  if (!el) throw new Error('submit button did not render')
  return el
}
function homeBtn(): HTMLButtonElement | null {
  return host?.querySelector<HTMLButtonElement>('.support__ok-cta') ?? null
}
function isTerminal(): boolean {
  return !!host?.querySelector('.support__done')
}
function setValue(el: HTMLInputElement | HTMLTextAreaElement, value: string): void {
  el.value = value
  el.dispatchEvent(new Event('input'))
}

// -----------------------------------------------------------------------------

beforeEach(() => {
  back.mockReset()
  push.mockReset()
  onFieldFocus.mockReset()
  // Every submit logs via console.info (.vue:148) -- silence it here so
  // tests that don't care about the payload stay quiet; tests that DO care
  // re-spy locally (vi.spyOn on top of this still captures every call).
  vi.spyOn(console, 'info').mockImplementation(() => {})
})

afterEach(() => {
  app?.unmount()
  host?.remove()
  app = null
  host = null
  vi.restoreAllMocks()
})

describe('SupportView', () => {
  // ===========================================================================
  describe('canSubmit truth table (.vue:127-131), asserted via the submit button)', () => {
    it('empty message: disabled (default topic is NOT "other")', async () => {
      mount()
      await flush()

      expect(submitBtn().disabled).toBe(true)
    })

    it('message present, topic != "other": ENABLED', async () => {
      mount()
      await flush()

      setValue(messageField(), 'У меня вопрос')
      await flush()

      expect(submitBtn().disabled).toBe(false)
    })

    it('topic == "other" with an EMPTY otherText: disabled even with a message', async () => {
      mount()
      await flush()

      radioByLabel(TOPIC_LABEL.other).click()
      await flush()
      setValue(messageField(), 'У меня вопрос')
      await flush()

      expect(submitBtn().disabled).toBe(true)
    })

    it('topic == "other" with otherText filled + message: ENABLED', async () => {
      mount()
      await flush()

      radioByLabel(TOPIC_LABEL.other).click()
      await flush()
      setValue(otherInput()!, 'Другой вопрос')
      setValue(messageField(), 'У меня вопрос')
      await flush()

      expect(submitBtn().disabled).toBe(false)
    })
  })

  // ===========================================================================
  describe('"other" branch reveal (.vue:52)', () => {
    it('selecting «Другое» renders the otherText input; switching away hides it', async () => {
      mount()
      await flush()

      expect(otherInput()).toBeNull()

      radioByLabel(TOPIC_LABEL.other).click()
      await flush()
      expect(otherInput()).not.toBeNull()

      radioByLabel(TOPIC_LABEL.technical).click()
      await flush()
      expect(otherInput()).toBeNull()
    })
  })

  // ===========================================================================
  describe('submit -> terminal transition', () => {
    it('a valid submit flips to the terminal screen; the form is gone', async () => {
      mount()
      await flush()

      setValue(messageField(), 'У меня вопрос')
      await flush()
      submitBtn().click()
      await flush()

      expect(isTerminal()).toBe(true)
      expect(host?.textContent).toContain('Спасибо за обращение')
      expect(host?.querySelector('.support__content')).toBeNull()
      expect(host?.querySelector('.v-header')).toBeNull()
    })

    it('a click while canSubmit is false does nothing (real disabled button, no submit)', async () => {
      mount()
      await flush()

      // Message stays empty -> button is a genuinely disabled <button>; a real
      // browser (and happy-dom) refuses to dispatch click on it.
      submitBtn().click()
      await flush()

      expect(isTerminal()).toBe(false)
    })
  })

  // ===========================================================================
  describe('payload shape + priority mapping (.vue:137-147), console.info spied', () => {
    it.each([
      ['payment', 'P1'],
      ['complaint_master', 'P0'],
      ['practice', 'P1'],
      ['technical', 'P2'],
    ] as const)('topic "%s" logs priority %s, custom_topic null', async (topicValue, priority) => {
      const infoSpy = vi.spyOn(console, 'info').mockImplementation(() => {})
      mount()
      await flush()

      radioByLabel(TOPIC_LABEL[topicValue]).click()
      await flush()
      setValue(messageField(), 'Текст обращения')
      await flush()
      submitBtn().click()
      await flush()

      expect(infoSpy).toHaveBeenCalledWith(
        '[support] stub — no backend yet; future ticket payload:',
        {
          topic: topicValue,
          priority,
          custom_topic: null,
          message: 'Текст обращения',
        },
      )
    })

    it('topic "other": custom_topic is the TRIMMED otherText, priority P2', async () => {
      const infoSpy = vi.spyOn(console, 'info').mockImplementation(() => {})
      mount()
      await flush()

      radioByLabel(TOPIC_LABEL.other).click()
      await flush()
      setValue(otherInput()!, '  Свой вариант  ')
      setValue(messageField(), 'Текст обращения')
      await flush()
      submitBtn().click()
      await flush()

      expect(infoSpy).toHaveBeenCalledWith(
        '[support] stub — no backend yet; future ticket payload:',
        {
          topic: 'other',
          priority: 'P2',
          custom_topic: 'Свой вариант',
          message: 'Текст обращения',
        },
      )
    })

    it('message is trimmed before it enters the payload', async () => {
      const infoSpy = vi.spyOn(console, 'info').mockImplementation(() => {})
      mount()
      await flush()

      setValue(messageField(), '  Текст с пробелами  ')
      await flush()
      submitBtn().click()
      await flush()

      const payload = infoSpy.mock.calls[0]?.[1] as { message?: string }
      expect(payload?.message).toBe('Текст с пробелами')
    })
  })

  // ===========================================================================
  describe('goHome (.vue:152-154)', () => {
    it('«На главную» on the terminal screen pushes { name: \'user-dashboard\' }', async () => {
      mount()
      await flush()

      setValue(messageField(), 'У меня вопрос')
      await flush()
      submitBtn().click()
      await flush()

      homeBtn()?.click()
      await flush()

      expect(push).toHaveBeenCalledWith({ name: 'user-dashboard' })
    })
  })
})
