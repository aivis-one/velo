// =============================================================================
// VELO Frontend -- NotificationsView Screen Tests (probekit-screen-test)
// =============================================================================
//
// 132 lines. Four on/off rows (push / practice_reminders / master_messages /
// support_messages), each auto-saving on flip, silently on success (the switch
// is its own feedback -- .vue:7-11) and reverting + toasting on failure.
//
// PATTERN A (store-backed), sibling of LanguageTimezoneView -- confirmed by
// reading every import. Real seam: authStore.updateProfile (auth.ts:142) ->
// updateMe (@/api/users, auth.ts:143). Real useAuthStore, @/api/users mocked.
// Error branching is ApiResponseError from @/api/client.
//
// THE DUAL-BINDING TRAP THAT BIT LanguageTimezoneView IS ABSENT HERE, VERIFIED
// NOT ASSUMED: VSwitch is bound ONE-WAY -- `:model-value="settings[row.key]"`
// + `@update:model-value="(value) => onToggle(row.key, value)"` (.vue:29-32).
// No v-model, so no auto-generated setter races ahead of the handler.
// `onToggle`'s own `settings[key] = value` (.vue:84) is the ONLY writer, so
// `previous` (.vue:83) is genuinely the prior value and the catch-path revert
// (.vue:91) is live code, not dead like LanguageTimezoneView's was pre-fix.
// The revert test below proves this goes RED on the FIRST mutation attempt
// (contrast: LanguageTimezoneView's needed the :model-value fix first).
//
// VSwitch ITSELF (components/ui/VSwitch.vue) has its own click guard --
// `toggle()` (VSwitch.vue:47) does `if (props.disabled) return` before ever
// emitting. Combined with `:disabled="savingKey === row.key"` (.vue:30), this
// means clicking the CURRENTLY-saving row a second time never even reaches
// `onToggle` -- the emit never fires. The per-key guard at .vue:82
// (`if (savingKey.value) return`) is therefore proven by toggling a
// DIFFERENT, un-disabled row while the first is in flight (recon's framing,
// confirmed correct by reading VSwitch.vue) -- that IS reachable at the
// child, and it's the view's own guard, not the child's, that must stop it.
//
// MONEY: none. No NBSP dance. Cyrillic fixtures/labels below were still typed
// directly via the Write tool (not a shell heredoc), per house habit.
//
// No modal, no v-show, no fetch ladder (init is synchronous off the store).
// No order dependence -- every test mounts its own app + fresh Pinia.
// =============================================================================

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { createApp, nextTick, type App } from 'vue'
import { setActivePinia, createPinia, type Pinia } from 'pinia'
import NotificationsView from '@/views/user/NotificationsView.vue'
import * as usersApi from '@/api/users'
import { useAuthStore } from '@/stores/auth'
import { ApiResponseError } from '@/api/client'
import type { UserResponse } from '@/api/types'

vi.mock('@/api/users')

const back = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ back }),
}))

const toastError = vi.fn()
const toastInfo = vi.fn()
const toastSuccess = vi.fn()
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ error: toastError, info: toastInfo, success: toastSuccess }),
}))

// -----------------------------------------------------------------------------
// Fixtures
// -----------------------------------------------------------------------------

function user(overrides: Partial<UserResponse> = {}): UserResponse {
  return {
    id: 'user_1',
    telegram_id: 1,
    role: 'user',
    first_name: 'Аня',
    last_name: 'Иванова',
    avatar_url: null,
    timezone: 'Europe/Moscow',
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
    notifications: {
      push: true,
      practice_reminders: true,
      master_messages: true,
      support_messages: true,
    },
    master_notifications: null,
    role_switch: null,
    ...overrides,
  }
}

// -----------------------------------------------------------------------------
// Mount
// -----------------------------------------------------------------------------

let app: App | null = null
let host: HTMLElement | null = null
let pinia: Pinia

function mount(): HTMLElement {
  host = document.createElement('div')
  document.body.appendChild(host)
  app = createApp(NotificationsView)
  app.use(pinia)
  app.mount(host)
  return host
}

// Save chain: onToggle -> await authStore.updateProfile -> await updateMe,
// each a microtask hop, then the catch/finally re-render. Same generous
// headroom as LanguageTimezoneView's (SC-08).
async function flush(): Promise<void> {
  for (let i = 0; i < 8; i++) await nextTick()
}

const LABEL = {
  push: 'Push-уведомления',
  practice_reminders: 'Напоминания о практиках',
  master_messages: 'Сообщения от мастеров',
  support_messages: 'Сообщения от поддержки',
} as const

function switchByLabel(label: string): HTMLButtonElement {
  const row = Array.from(host?.querySelectorAll<HTMLElement>('.notifications__row') ?? []).find(
    (r) => r.querySelector('.notifications__label')?.textContent?.trim() === label,
  )
  const btn = row?.querySelector<HTMLButtonElement>('.v-switch')
  if (!btn) throw new Error(`no VSwitch row labelled «${label}»`)
  return btn
}
function isOn(label: string): boolean {
  return switchByLabel(label).getAttribute('aria-checked') === 'true'
}
function isDisabled(label: string): boolean {
  return switchByLabel(label).disabled
}

// -----------------------------------------------------------------------------

beforeEach(() => {
  pinia = createPinia()
  setActivePinia(pinia)

  vi.mocked(usersApi.updateMe)
    .mockReset()
    .mockImplementation(async (body) => user(body as Partial<UserResponse>))

  useAuthStore().user = user()

  back.mockReset()
  toastError.mockReset()
  toastInfo.mockReset()
  toastSuccess.mockReset()
})

afterEach(() => {
  app?.unmount()
  host?.remove()
  app = null
  host = null
  vi.clearAllMocks()
})

describe('NotificationsView', () => {
  // ===========================================================================
  describe('init from the store', () => {
    it('reflects a mix of true/false from authStore.user.notifications', async () => {
      useAuthStore().user = user({
        notifications: {
          push: false,
          practice_reminders: true,
          master_messages: false,
          support_messages: true,
        },
      })
      mount()
      await flush()

      expect(isOn(LABEL.push)).toBe(false)
      expect(isOn(LABEL.practice_reminders)).toBe(true)
      expect(isOn(LABEL.master_messages)).toBe(false)
      expect(isOn(LABEL.support_messages)).toBe(true)
    })

    it('a MISSING field defaults to true (?? true), only the present field is honoured', async () => {
      useAuthStore().user = user({ notifications: { push: false } })
      mount()
      await flush()

      expect(isOn(LABEL.push)).toBe(false)
      expect(isOn(LABEL.practice_reminders)).toBe(true)
      expect(isOn(LABEL.master_messages)).toBe(true)
      expect(isOn(LABEL.support_messages)).toBe(true)
    })
  })

  // ===========================================================================
  describe('toggle: success is SILENT (no toast -- the switch is its own feedback)', () => {
    it('flips the switch, sends the flipped key only, and fires no toast at all', async () => {
      mount()
      await flush()

      switchByLabel(LABEL.practice_reminders).click()
      await flush()

      expect(usersApi.updateMe).toHaveBeenCalledWith({
        notifications: { practice_reminders: false },
      })
      expect(isOn(LABEL.practice_reminders)).toBe(false)
      expect(toastInfo).not.toHaveBeenCalled()
      expect(toastSuccess).not.toHaveBeenCalled()
      expect(toastError).not.toHaveBeenCalled()
    })

    it('the payload carries ONLY the flipped key -- not the other three settings', async () => {
      mount()
      await flush()

      switchByLabel(LABEL.support_messages).click()
      await flush()

      const body = vi.mocked(usersApi.updateMe).mock.calls[0]?.[0]
      expect(body).toEqual({ notifications: { support_messages: false } })
      expect(Object.keys(body?.notifications ?? {})).toEqual(['support_messages'])
    })
  })

  // ===========================================================================
  describe('toggle: revert-on-failure (crown jewel -- LIVE here, unlike LanguageTimezoneView pre-fix)', () => {
    it('reverts the switch to its previous state and toasts the error', async () => {
      vi.mocked(usersApi.updateMe).mockRejectedValue(new Error('ECONNRESET'))
      mount()
      await flush()

      expect(isOn(LABEL.master_messages)).toBe(true)

      switchByLabel(LABEL.master_messages).click()
      await flush()

      expect(isOn(LABEL.master_messages)).toBe(true) // reverted, not left off
      expect(toastError).toHaveBeenCalledWith('Не удалось сохранить настройку')
    })
  })

  // ===========================================================================
  describe('toggle: save error branching (ApiResponseError vs generic, SC-05)', () => {
    it('ApiResponseError WITH a detail surfaces the real backend message', async () => {
      vi.mocked(usersApi.updateMe).mockRejectedValue(
        new ApiResponseError(422, 'Некорректная настройка', 'validation_error'),
      )
      mount()
      await flush()

      switchByLabel(LABEL.push).click()
      await flush()

      expect(toastError).toHaveBeenCalledWith('Некорректная настройка')
    })

    it('ApiResponseError with an EMPTY detail falls back to the generic message', async () => {
      vi.mocked(usersApi.updateMe).mockRejectedValue(new ApiResponseError(500, '', 'server_error'))
      mount()
      await flush()

      switchByLabel(LABEL.push).click()
      await flush()

      expect(toastError).toHaveBeenCalledWith('Не удалось сохранить настройку')
    })

    it('a non-ApiResponseError also falls back to the generic message', async () => {
      vi.mocked(usersApi.updateMe).mockRejectedValue(new Error('ECONNRESET'))
      mount()
      await flush()

      switchByLabel(LABEL.push).click()
      await flush()

      expect(toastError).toHaveBeenCalledWith('Не удалось сохранить настройку')
    })
  })

  // ===========================================================================
  describe('toggle: per-key saving guard', () => {
    it('the in-flight row is disabled; a tap on a DIFFERENT row makes no second API call and does not change its own display', async () => {
      let resolveUpdate!: (u: UserResponse) => void
      vi.mocked(usersApi.updateMe).mockReset().mockImplementation(
        () =>
          new Promise<UserResponse>((resolve) => {
            resolveUpdate = resolve
          }),
      )
      mount()
      await flush()

      switchByLabel(LABEL.push).click()
      await flush()

      // .vue:30's :disabled binding -- the saving row itself is disabled.
      expect(isDisabled(LABEL.push)).toBe(true)

      // A DIFFERENT row is NOT disabled at the child, so this click DOES
      // reach onToggle -- it's the view's own guard (.vue:82) that must stop
      // it, not VSwitch's.
      expect(isDisabled(LABEL.practice_reminders)).toBe(false)
      switchByLabel(LABEL.practice_reminders).click()
      await flush()

      expect(usersApi.updateMe).toHaveBeenCalledTimes(1)
      expect(usersApi.updateMe).toHaveBeenCalledWith({ notifications: { push: false } })
      // Guarded out before .vue:84 ever ran -- practice_reminders' own
      // display is untouched by the ignored click.
      expect(isOn(LABEL.practice_reminders)).toBe(true)

      resolveUpdate(user({ notifications: { push: false } }))
      await flush()

      expect(isOn(LABEL.push)).toBe(false)
      expect(isDisabled(LABEL.push)).toBe(false)
    })
  })
})
