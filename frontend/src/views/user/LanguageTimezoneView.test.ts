// =============================================================================
// VELO Frontend -- LanguageTimezoneView Screen Tests (probekit-screen-test)
// =============================================================================
//
// 255 lines, shared user/master settings screen (mounted on BOTH roles' routes,
// role-agnostic; no role-specific behaviour to split on).
//
// PATTERN A (store-backed): the one real seam is authStore.updateProfile
// (auth.ts:142), which calls updateMe (@/api/users, auth.ts:143) then stores the
// result. The REAL useAuthStore is used; @/api/users is mocked. Error branching
// is ApiResponseError from @/api/client (auth.ts import chain, .vue:80).
//
// CHILD SEAM CHECKED, NOT ASSUMED, AND CORRECTED: the real (unstubbed)
// TimezoneCityPicker was suspected of its own fetch seam (EditProfileView's
// MethodTaxonomyPicker precedent, per the operator recon). Read it end to end
// (TimezoneCityPicker.vue) -- it has NONE. Its city list is a static import
// (TIMEZONE_CITIES, @/utils/timezoneCities), no onMounted, no API call. It is
// driven for real throughout below: clicking a city row is what fires
// `@update:modelValue` on the child (TimezoneCityPicker.vue:97), exercising
// the real wiring instead of calling the handler off a fixture.
//
// ============================================================================
// A REAL BUG, FOUND BY THIS FILE AND MUTATION-CONFIRMED -- not fixed here (see
// the report; a separate commit per the operator's "no bundling" rule).
// ============================================================================
// .vue:59 writes BOTH `v-model="selectedTimezone"` AND an explicit
// `@update:modelValue="onTimezoneChange"` on the SAME <TimezoneCityPicker>
// tag. Compiling that template (checked directly via
// @vue/compiler-sfc's compileTemplate) shows Vue merges them into an ARRAY of
// two `onUpdate:modelValue` handlers: the auto-generated v-model setter
// (`selectedTimezone.value = $event`) FIRST, then `onTimezoneChange` SECOND.
// Vue invokes array-valued emit handlers in that order, unconditionally, on
// every single emission of the event -- there is no way for `onTimezoneChange`
// to run before the raw setter has already applied the new value.
//
// Two consequences, both mutation-confirmed live against this component
// (temporarily edited, run, reverted -- not left in the tree):
//   (a) The revert-on-failure logic is DEAD CODE. `const previous =
//       selectedTimezone.value` (.vue:148) runs AFTER the raw setter already
//       moved `selectedTimezone` to the NEW value, so `previous` is never the
//       true previous value -- it equals the new value. `selectedTimezone.value
//       = previous` on the catch path (.vue:156) is therefore a no-op.
//       CONFIRMED: deleting .vue:156 entirely and re-running the failing-save
//       test below produces a BYTE-IDENTICAL failure (same assertion, same
//       line, same false/true) -- the line changes nothing observable.
//   (b) The `saving` reentrancy guard (.vue:147) only blocks a SECOND api call
//       -- it does NOT block the raw setter from applying a second, later
//       click's value to the display while the first save is still in flight.
//       Double-tapping two different cities can leave the UI showing the
//       SECOND city (with the FIRST city's "saved" toast having just fired)
//       while the backend actually persisted the FIRST. CONFIRMED: commenting
//       out .vue:147's guard flips `updateMe` from 1 call to 2 -- the guard
//       itself is real and load-bearing for the API-call count, it just does
//       not protect the displayed value the way the header comment
//       (.vue:155, "Revert the selection so the UI matches the server on
//       failure") claims.
// Both tests below assert the CURRENT, OBSERVED behaviour (bug included), not
// the intended one -- per this repo's changelog-as-red precedent
// (FeedbackView/EditProfileView-delete-stub): the day someone splits the dual
// binding (e.g. drops the explicit @update:modelValue and reads the new value
// off the v-model'd ref inside a watcher, or reorders so onTimezoneChange owns
// the assignment), these are what should go red as the fix.
// ============================================================================
//
// TIMEZONE_CITIES ITSELF DOES DOUBLE DUTY as the isValidIana probe. Its
// `generatedZones()` (timezoneCities.ts:177-192) walks the REAL
// `Intl.supportedValuesOf('timeZone')` and renders one row per zone this Node's
// ICU actually supports, keyed by iana. That is used directly (no Intl mock,
// per the operator recon) to observe .vue:129-142's two branches from the
// OUTSIDE: a valid-but-uncurated zone ('Pacific/Kiritimati', confirmed present
// via `Intl.supportedValuesOf('timeZone').includes(...)` in this repo's node)
// renders its generated row as active; a genuinely invalid string ('Not/AZone',
// confirmed to throw in `Intl.DateTimeFormat` in this repo's node) renders NO
// active row at all, because the FALLBACK_TIMEZONE 'UTC' constant is itself
// absent from TIMEZONE_CITIES (not in CURATED/ALIASES, and 'UTC' is excluded
// from Node's supportedValuesOf('timeZone') list) -- "no row is active" is the
// honest, network-free way to observe a fallback to a value nothing renders.
//
// LANGUAGE BRANCH -- A REAL, DOCUMENTED GAP, not silently skipped (recon
// flagged this; verified true by reading the file, not assumed): LANGUAGE_OPTIONS
// (.vue:96-98) currently renders ONLY 'ru' (English hidden 2026-06-19, available
// stub kept for later). onSelectLanguage's `!opt.available` toast branch
// (.vue:106-110) is therefore DEAD from the template's own perspective -- there
// is no second button to click, and the file has no defineExpose, so the
// handler cannot be invoked directly without changing production source, which
// is out of this task's scope (minimal-scope rule). The first test below in
// that describe block PROVES the branch is unreachable (asserts exactly one
// `.lang-tz__lang` button renders) rather than asserting nothing about it; the
// gap is reported as logic-covered-not-template-reachable, not swept under a
// green suite.
//
// MONEY: none on this screen. Nothing to NBSP-guard.
//
// No modal, no v-show (grepped this file and TimezoneCityPicker.vue -- both
// v-if only), no window.location / clipboard / IntersectionObserver /
// ResizeObserver seam. No order dependence -- every test mounts its own app +
// fresh Pinia.
// =============================================================================

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { createApp, nextTick, type App } from 'vue'
import { setActivePinia, createPinia, type Pinia } from 'pinia'
import LanguageTimezoneView from '@/views/user/LanguageTimezoneView.vue'
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
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ error: toastError, info: toastInfo, success: vi.fn() }),
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
    notifications: {} as UserResponse['notifications'],
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
  app = createApp(LanguageTimezoneView)
  app.use(pinia)
  app.mount(host)
  return host
}

// Mount itself is synchronous (init is off the store, see banner) but the SAVE
// chain is not: onTimezoneChange -> await authStore.updateProfile -> await
// updateMe, each a microtask hop, then the catch/finally re-render. COUNTED,
// not copied (SC-08): 2 awaits deep plus Vue's own scheduler flush -- 8 ticks
// is generous headroom, matching this repo's other Pattern-A screens.
async function flush(): Promise<void> {
  for (let i = 0; i < 8; i++) await nextTick()
}

function cityRow(cityLabel: string): HTMLButtonElement | undefined {
  return Array.from(host?.querySelectorAll<HTMLButtonElement>('.tz-picker__row') ?? []).find(
    (r) => r.querySelector('.tz-picker__city')?.textContent?.trim() === cityLabel,
  )
}
function activeCityRows(): HTMLButtonElement[] {
  return Array.from(
    host?.querySelectorAll<HTMLButtonElement>('.tz-picker__row.tz-picker__row--active') ?? [],
  )
}
function languageButtons(): HTMLButtonElement[] {
  return Array.from(host?.querySelectorAll<HTMLButtonElement>('.lang-tz__lang') ?? [])
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
})

afterEach(() => {
  app?.unmount()
  host?.remove()
  app = null
  host = null
  vi.clearAllMocks()
})

describe('LanguageTimezoneView', () => {
  // ===========================================================================
  describe('timezone: optimistic update with revert on failure', () => {
    it('success: selecting a city calls updateProfile with the new zone and toasts success', async () => {
      mount()
      await flush()

      cityRow('Берлин')?.click()
      await flush()

      expect(usersApi.updateMe).toHaveBeenCalledWith({ timezone: 'Europe/Berlin' })
      expect(toastInfo).toHaveBeenCalledWith('Часовой пояс сохранён')
      expect(cityRow('Берлин')?.classList.contains('tz-picker__row--active')).toBe(true)
    })

    it('BUG (see banner): on failure the error toast still fires, but the selection does NOT revert -- it stays on the failed city', async () => {
      vi.mocked(usersApi.updateMe).mockRejectedValue(new Error('ECONNRESET'))
      mount()
      await flush()

      expect(cityRow('Москва')?.classList.contains('tz-picker__row--active')).toBe(true)

      cityRow('Берлин')?.click()
      await flush()

      expect(toastError).toHaveBeenCalledWith('Не удалось сохранить часовой пояс')
      // Intended behaviour (per .vue:155's own comment) would put Moscow back
      // here. It does not: Berlin -- the value that just failed to save --
      // stays selected. Mutation-confirmed dead code, see banner.
      expect(cityRow('Берлин')?.classList.contains('tz-picker__row--active')).toBe(true)
      expect(cityRow('Москва')?.classList.contains('tz-picker__row--active')).toBe(false)
    })

    it('saving guard: a second selection while the first save is in flight makes no second API call', async () => {
      let resolveUpdate!: (u: UserResponse) => void
      vi.mocked(usersApi.updateMe).mockReset().mockImplementation(
        () =>
          new Promise<UserResponse>((resolve) => {
            resolveUpdate = resolve
          }),
      )
      mount()
      await flush()

      // No await between the two clicks -- `saving` must gate the second call
      // synchronously, in the same frame, not after a tick settles it.
      cityRow('Берлин')?.click()
      cityRow('Лондон')?.click()
      await flush()

      // The GUARD holds for the API call: only Berlin (the first tap) is ever
      // persisted. Mutation-confirmed: commenting out .vue:147's guard makes
      // this go from 1 call to 2 (Лондон's tap also reaching updateMe).
      expect(usersApi.updateMe).toHaveBeenCalledTimes(1)
      expect(usersApi.updateMe).toHaveBeenCalledWith({ timezone: 'Europe/Berlin' })

      resolveUpdate(user({ timezone: 'Europe/Berlin' }))
      await flush()

      // BUG (see banner), consequence (b): the guard does NOT hold for the
      // DISPLAY. London's raw v-model setter ran unconditionally on the
      // second click (before onTimezoneChange's own guard could see it), so
      // London -- not Berlin -- ends up shown as selected, even though the
      // toast that just fired says the save succeeded and Berlin is what was
      // actually persisted to the backend.
      expect(toastInfo).toHaveBeenCalledWith('Часовой пояс сохранён')
      expect(cityRow('Лондон')?.classList.contains('tz-picker__row--active')).toBe(true)
      expect(cityRow('Берлин')?.classList.contains('tz-picker__row--active')).toBe(false)
    })
  })

  // ===========================================================================
  describe('timezone: save error branching (ApiResponseError vs generic)', () => {
    it('ApiResponseError WITH a detail surfaces the real backend message', async () => {
      vi.mocked(usersApi.updateMe).mockRejectedValue(
        new ApiResponseError(422, 'Некорректный часовой пояс', 'validation_error'),
      )
      mount()
      await flush()

      cityRow('Берлин')?.click()
      await flush()

      expect(toastError).toHaveBeenCalledWith('Некорректный часовой пояс')
    })

    it('ApiResponseError with an EMPTY detail falls back to the generic message', async () => {
      vi.mocked(usersApi.updateMe).mockRejectedValue(new ApiResponseError(500, '', 'server_error'))
      mount()
      await flush()

      cityRow('Берлин')?.click()
      await flush()

      expect(toastError).toHaveBeenCalledWith('Не удалось сохранить часовой пояс')
    })

    it('a non-ApiResponseError (network failure) also falls back to the generic message (SC-05)', async () => {
      vi.mocked(usersApi.updateMe).mockRejectedValue(new Error('ECONNRESET'))
      mount()
      await flush()

      cityRow('Берлин')?.click()
      await flush()

      expect(toastError).toHaveBeenCalledWith('Не удалось сохранить часовой пояс')
    })
  })

  // ===========================================================================
  describe('timezone: initial value via isValidIana (real Intl, no mock)', () => {
    it('a valid but uncurated IANA zone is kept as-is, not folded to the fallback', async () => {
      useAuthStore().user = user({ timezone: 'Pacific/Kiritimati' })
      mount()
      await flush()

      const row = cityRow('Kiritimati')
      expect(row).toBeDefined()
      expect(row?.classList.contains('tz-picker__row--active')).toBe(true)
    })

    it('a genuinely invalid zone string falls back to UTC, which renders NO active row', async () => {
      useAuthStore().user = user({ timezone: 'Not/AZone' })
      mount()
      await flush()

      // 'UTC' is absent from TIMEZONE_CITIES (not curated, and excluded from
      // this Node's Intl.supportedValuesOf('timeZone')) -- no row can be
      // active for it. This is the honest observation of the fallback.
      expect(activeCityRows()).toHaveLength(0)
    })
  })

  // ===========================================================================
  describe('language', () => {
    it('only Русский renders -- the unavailable/English branch is unreachable via the template (documented gap, see banner)', async () => {
      mount()
      await flush()

      expect(languageButtons()).toHaveLength(1)
      expect(languageButtons()[0]?.textContent).toContain('Русский')
    })

    it('Русский initialises active from the stored (available) language and stays active on click', async () => {
      useAuthStore().user = user({ language: 'ru' })
      mount()
      await flush()

      const ruBtn = languageButtons()[0]
      expect(ruBtn?.classList.contains('lang-tz__lang--active')).toBe(true)

      ruBtn?.click()
      await flush()

      expect(ruBtn?.classList.contains('lang-tz__lang--active')).toBe(true)
      // Only one real language today -- selecting it persists nothing.
      expect(usersApi.updateMe).not.toHaveBeenCalled()
    })

    it('a stored language with no matching available option still initialises to ru, not a crash', async () => {
      useAuthStore().user = user({ language: 'en' })
      mount()
      await flush()

      expect(languageButtons()[0]?.classList.contains('lang-tz__lang--active')).toBe(true)
    })
  })
})
