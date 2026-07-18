// =============================================================================
// VELO Frontend -- AdminMasterInviteView Screen Tests (probekit-screen-test)
// =============================================================================
//
// 151 lines. A single mutating action (inviteMaster) + a clipboard-copy
// button. No store, no ladder in the generic list/detail sense -- just a
// form-card that always renders, plus a result-card gated on `inviteLink`.
//
// CORRECTION TO RECON -- READ, NOT ASSUMED, ARGUING BACK: `onCreate` (.vue:
// 66-78) is described in the prompt as "guarded by `creating`". Reading the
// function body, there is NO `if (creating.value) return` at all --
// `creating.value = true` is set UNCONDITIONALLY at the top, with no
// re-entrancy check before it:
//   async function onCreate(): Promise<void> {
//     creating.value = true
//     try { ... } finally { creating.value = false }
//   }
// The ONLY thing standing between a double-click and a double `inviteMaster`
// call is VButton's OWN `:disabled="disabled || loading"` binding
// (VButton.vue:27) reacting to `:loading="creating"` (.vue:35) -- a template
// binding, not a handler guard, and Vue's reactive DOM update is
// microtask-batched, not synchronous. A SAME-TICK double click (no `await`
// between the two `.click()` calls) reaches `onCreate` twice before that
// `disabled` attribute has painted -- proven below, not assumed. This is
// THE SAME SHAPE this whole admin zone has repeatedly found (AdminReportDetail
// View pre-№481, 2 of AdminMasterReviewView's 3 guards pre-№483) -- except
// here there is no handler-level check to even partially rely on. REPORTED
// as a real finding, NOT fixed here (owner's call, per protocol). Contrast
// tests below cover both: the realistic with-a-tick interaction (genuinely
// blocked, because the real DOM button really is disabled once painted) AND
// the same-tick programmatic gap (reaches the handler twice).
//
// THE LINK ONLY APPEARS AFTER A SUCCESSFUL CREATE: `<VCard v-if="inviteLink">`
// (.vue:43) -- `inviteLink` starts `''` (falsy) and is only ever assigned
// inside the try block's success path (.vue:70), never touched in catch.
// Asserted directly: absent before create, absent after a FAILED create,
// present only after success.
//
// THE CLIPBOARD TRAP (operator-flagged, confirmed real): `onCopy` (.vue:
// 81-88) calls `navigator.clipboard.writeText`, which happy-dom does not
// implement by default -- calling it unstubbed throws
// "navigator.clipboard is undefined", which would make the REJECTION branch
// impossible to reach honestly (a thrown-because-missing-API error is not
// the same test as a genuine write failure). Stubbed via
// `Object.defineProperty(navigator, 'clipboard', {configurable: true,
// writable: true, value: {writeText}})` in `beforeEach` (same technique as
// this repo's existing MasterPromocodesView.test.ts precedent), with
// `writeText` a fresh `vi.fn()` per test so both the resolve AND reject
// paths are independently controllable -- and explicitly deleted in
// `afterEach` to restore happy-dom's undefined-clipboard baseline for any
// test file that runs after this one.
//
// Cyrillic fixtures/expected strings below were typed via the Write tool,
// never a shell heredoc.
// =============================================================================

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { createApp, nextTick, type App } from 'vue'
import AdminMasterInviteView from '@/views/admin/AdminMasterInviteView.vue'
import * as adminApi from '@/api/admin'
import { ApiResponseError } from '@/api/client'
import type { InviteMasterResponse } from '@/api/types'

vi.mock('@/api/admin')

const back = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ back, push: vi.fn() }),
}))

const toastError = vi.fn()
const toastSuccess = vi.fn()
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ error: toastError, success: toastSuccess, info: vi.fn() }),
}))

// -----------------------------------------------------------------------------
// Fixtures
// -----------------------------------------------------------------------------

function inviteResponse(overrides: Partial<InviteMasterResponse> = {}): InviteMasterResponse {
  return {
    invite_link: 'https://t.me/velo_bot?start=invite_abc123',
    issued_at: '2026-07-01T00:00:00Z',
    ...overrides,
  }
}

// -----------------------------------------------------------------------------
// Mount
// -----------------------------------------------------------------------------

let app: App | null = null
let host: HTMLElement | null = null
let writeText: ReturnType<typeof vi.fn>

function mount(): HTMLElement {
  host = document.createElement('div')
  document.body.appendChild(host)
  app = createApp(AdminMasterInviteView)
  app.mount(host)
  return host
}

async function flush(): Promise<void> {
  for (let i = 0; i < 6; i++) await nextTick()
}

function buttonByText(t: string): HTMLButtonElement | undefined {
  return Array.from(host?.querySelectorAll<HTMLButtonElement>('.v-btn') ?? []).find(
    (b) => b.textContent?.trim() === t,
  )
}
function createBtn(): HTMLButtonElement {
  const b = buttonByText('Создать ссылку')
  if (!b) throw new Error('«Создать ссылку» did not render')
  return b
}
function copyBtn(): HTMLButtonElement | undefined {
  return buttonByText('Скопировать')
}
function linkText(): string {
  return host?.querySelector('.invite__link')?.textContent?.trim() ?? ''
}

// -----------------------------------------------------------------------------

beforeEach(() => {
  vi.mocked(adminApi.inviteMaster).mockReset().mockResolvedValue(inviteResponse())

  back.mockReset()
  toastError.mockReset()
  toastSuccess.mockReset()

  writeText = vi.fn().mockResolvedValue(undefined)
  Object.defineProperty(navigator, 'clipboard', {
    configurable: true,
    writable: true,
    value: { writeText },
  })
})

afterEach(() => {
  app?.unmount()
  host?.remove()
  app = null
  host = null
  delete (navigator as unknown as { clipboard?: unknown }).clipboard
  vi.clearAllMocks()
})

describe('AdminMasterInviteView', () => {
  // ===========================================================================
  describe('onCreate (.vue:66-78) -- the link only appears after success', () => {
    it('no result card before any create', async () => {
      mount()
      await flush()

      expect(host?.querySelector('.invite__link')).toBeNull()
    })

    it('success: fills inviteLink, result card renders with the exact link', async () => {
      mount()
      await flush()

      createBtn().click()
      await flush()

      expect(linkText()).toBe('https://t.me/velo_bot?start=invite_abc123')
    })

    it('failure (generic Error): toasts the fallback, NO result card', async () => {
      vi.mocked(adminApi.inviteMaster).mockRejectedValue(new Error('ECONNRESET'))
      mount()
      await flush()

      createBtn().click()
      await flush()

      expect(toastError).toHaveBeenCalledWith('Не удалось создать ссылку')
      expect(host?.querySelector('.invite__link')).toBeNull()
    })

    it('failure (ApiResponseError, e.g. bot_url_not_configured): toasts the real backend detail', async () => {
      vi.mocked(adminApi.inviteMaster).mockRejectedValue(
        new ApiResponseError(503, 'Бот не настроен', 'bot_url_not_configured'),
      )
      mount()
      await flush()

      createBtn().click()
      await flush()

      expect(toastError).toHaveBeenCalledWith('Бот не настроен')
    })

    it('re-generating replaces the result card in place with a NEW link', async () => {
      mount()
      await flush()
      createBtn().click()
      await flush()
      expect(linkText()).toBe('https://t.me/velo_bot?start=invite_abc123')

      vi.mocked(adminApi.inviteMaster).mockResolvedValueOnce(
        inviteResponse({ invite_link: 'https://t.me/velo_bot?start=invite_xyz789' }),
      )
      createBtn().click()
      await flush()

      expect(linkText()).toBe('https://t.me/velo_bot?start=invite_xyz789')
    })

    it('while creating, VButton shows its own :loading state (spinner + real disabled attribute)', async () => {
      let resolveCreate!: (v: InviteMasterResponse) => void
      vi.mocked(adminApi.inviteMaster).mockImplementation(
        () =>
          new Promise((resolve) => {
            resolveCreate = resolve
          }),
      )
      mount()
      await flush()

      createBtn().click()
      await flush() // let :loading="creating" paint

      expect(createBtn().disabled).toBe(true)
      expect(createBtn().classList.contains('v-btn--loading')).toBe(true)

      resolveCreate(inviteResponse())
      await flush()
      expect(createBtn().disabled).toBe(false)
    })

    it('REALISTIC interaction: once :disabled has painted, a second click on the real <button> is a no-op', async () => {
      let resolveCreate!: (v: InviteMasterResponse) => void
      vi.mocked(adminApi.inviteMaster).mockImplementation(
        () =>
          new Promise((resolve) => {
            resolveCreate = resolve
          }),
      )
      mount()
      await flush()

      createBtn().click()
      await flush() // disabled attribute paints
      createBtn().click() // a real click on a disabled <button> does not fire

      expect(adminApi.inviteMaster).toHaveBeenCalledTimes(1)
      resolveCreate(inviteResponse())
      await flush()
    })

    it('REAL FINDING: a same-tick double click reaches onCreate TWICE -- no handler-level guard exists (see banner)', async () => {
      let resolveCreate!: (v: InviteMasterResponse) => void
      vi.mocked(adminApi.inviteMaster).mockImplementation(
        () =>
          new Promise((resolve) => {
            resolveCreate = resolve
          }),
      )
      mount()
      await flush()

      const btn = createBtn()
      btn.click()
      btn.click() // no await -- the disabled attribute has not painted yet
      await flush()

      expect(adminApi.inviteMaster).toHaveBeenCalledTimes(2)
      resolveCreate(inviteResponse())
      await flush()
    })
  })

  // ===========================================================================
  describe('onCopy (.vue:81-88) -- the clipboard trap, both branches (see banner)', () => {
    it('success: writes the exact inviteLink, toasts success', async () => {
      mount()
      await flush()
      createBtn().click()
      await flush()

      copyBtn()?.click()
      await flush()

      expect(writeText).toHaveBeenCalledWith('https://t.me/velo_bot?start=invite_abc123')
      expect(toastSuccess).toHaveBeenCalledWith('Ссылка скопирована')
    })

    it('a clipboard rejection surfaces as an error, not a false success', async () => {
      writeText.mockRejectedValue(new Error('denied'))
      mount()
      await flush()
      createBtn().click()
      await flush()

      copyBtn()?.click()
      await flush()

      expect(toastError).toHaveBeenCalledWith('Не удалось скопировать')
      expect(toastSuccess).not.toHaveBeenCalled()
    })
  })
})
