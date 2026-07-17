// =============================================================================
// VELO Frontend -- BookingConfirmedView Screen Tests (probekit-screen-test v1.9)
// =============================================================================
//
// 190 lines, no test. PATTERN A, ONE real store (usePracticesStore) -- same
// single-store detail shape as CheckinView/FeedbackView (real Pinia, mock the
// api/practices seam: `getPractice`). No second store, no diary, no bookings
// here -- this screen only confirms a practice EXISTS, it does not read the
// user's booking at all.
//
// PROVEN ABSENT (grepped the whole template before writing a single test):
//  - NO practice-specific data is ever rendered. `practice` (.vue:91) gates
//    the ladder but its title/master_name/scheduled_at/price are NEVER
//    interpolated anywhere in the content block (.vue:41-73) -- the success
//    card is 100% static copy ("Практика забронирована!", a fixed 10-minute
//    Zoom line). This directly contradicts the assumed shape ("cover that the
//    right data renders") -- there is no per-practice data to cover; two
//    different fixtures produce byte-identical visible text (proven below).
//  - NO money anywhere -- no formatMoney, no price. No NBSP trap, no norm().
//  - NO wall clock -- no Date.now()/new Date() read by this screen at all
//    (the "10 minutes before" line is a hardcoded string, not computed).
//  - NO route-level guard (checked router/index.ts -- same as CalendarView/
//    PracticeLiveView, covered only by the root roleRedirect already tested
//    in guards.test.ts). Not duplicated here.
//
// ⭐ THE ACTUAL PRIZE -- the combined error/missing rung (.vue:32,
// `store.selectedError || !practice`), asked to be examined for the exact bug
// class just fixed on CalendarView (a guard reading "is there ANY data" where
// it should read "is there the RIGHT data for what's on screen"). Two DISTINCT
// findings below, of different severity:
//
//  (a) STRUCTURAL, NOT USER-VISIBLE: the guard's own literal DEFAULTS
//      (selectedLoading=false, selected=null, selectedError=null -- the
//      state before onMounted has run at all) satisfy `!practice` and fail
//      the loading guard (needs loading=true) -- so on the FIRST synchronous
//      render, before onMounted's fetchPractice() call has had a chance to
//      flip `loading` to true, the DOM technically matches the error rung.
//      Reproduced in test (querying the DOM with ZERO awaits after mount()).
//      BUT: fetchPractice's `loading.value = true` write happens SYNCHRONOUSLY
//      inside onMounted, which Vue calls synchronously as part of the SAME
//      app.mount() call that produced the first render -- the resulting
//      re-render is only QUEUED (Vue's scheduler flushes via a Promise
//      microtask), and browsers drain the microtask queue before the next
//      paint. There is no real async boundary (no network delay) between the
//      "wrong" state and the flip to loading=true -- unlike CalendarView's bug,
//      which spanned an actual pending HTTP request a user waits through. A
//      real browser would very likely never paint this frame. Documented as a
//      structural note, not asserted as a user-facing bug.
//  (b) REAL AND BOUNDED: `practice` (.vue:91) is just `store.selected` with NO
//      check that it belongs to THIS screen's route practiceId. usePracticesStore
//      is a session-lifetime singleton; if the user reaches this URL (a
//      supported entry per the header comment -- "works on direct navigation /
//      deep link") while `store.selected` still holds a DIFFERENT practice
//      from an earlier screen, THAT stale-but-non-null value satisfies
//      `!practice` = false for the ENTIRE duration of the real fetch for the
//      new id -- so the loading guard is skipped and the (harmless, since
//      static) success card renders while the actual confirmation is still in
//      flight. If that fetch then fails, the screen shows "Практика
//      забронирована!" BEFORE flipping to "Практика не найдена" for a
//      practice that was never confirmed. Bounded by (a) no data ever states
//      the WRONG practice's details, since none render, and (b) it requires a
//      stale singleton-store value from a different id, not the primary
//      "reached from a payment redirect" path -- but it is real, reproduced
//      with an actual pending/rejecting fetch (real async boundary, unlike
//      finding (a)), and worth the navigator's read.
//
// TICKS: fetchPractice's own chain is one `await getPractice(id)` (not
// awaited by onMounted itself, fire-and-forget) + a final re-render -- flush()
// uses 4, generous per velo-idiom §3 (an over-count is harmless).
// =============================================================================

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { createApp, nextTick, type App } from 'vue'
import { setActivePinia, createPinia, type Pinia } from 'pinia'
import BookingConfirmedView from '@/views/user/BookingConfirmedView.vue'
import { usePracticesStore } from '@/stores/practices'
import { getPractice } from '@/api/practices'
import { ApiResponseError } from '@/api/client'
import type { PracticeResponse } from '@/api/types'

vi.mock('@/api/practices', async () => {
  const actual = await vi.importActual<typeof import('@/api/practices')>('@/api/practices')
  return { ...actual, getPractice: vi.fn() }
})
const getPracticeMock = vi.mocked(getPractice)

const push = vi.fn()
const routeParams: { practiceId: string } = { practiceId: 'p1' }
vi.mock('vue-router', () => ({
  useRouter: () => ({ push, back: vi.fn(), replace: vi.fn() }),
  useRoute: () => ({ params: routeParams }),
}))

const toastInfo = vi.fn()
vi.mock('@/composables/useToast', () => ({
  useToast: () => ({ error: vi.fn(), success: vi.fn(), info: toastInfo }),
}))

function practice(overrides: Partial<PracticeResponse> = {}): PracticeResponse {
  return {
    id: 'p1',
    master_id: 'master_1',
    master_name: 'Мастер',
    practice_type: 'live',
    status: 'scheduled',
    title: 'Утренняя медитация',
    description: null,
    scheduled_at: '2026-07-20T10:00:00Z',
    duration_minutes: 60,
    timezone: 'UTC',
    max_participants: 20,
    current_participants: 5,
    zoom_link: null,
    parent_practice_id: null,
    is_free: true,
    price_cents: 0,
    currency: 'EUR',
    direction: null,
    created_at: '2026-07-01T00:00:00Z',
    updated_at: null,
    ...overrides,
  }
}

let app: App | null = null
let host: HTMLElement | null = null
let pinia: Pinia

function mount(): HTMLElement {
  host = document.createElement('div')
  document.body.appendChild(host)
  app = createApp(BookingConfirmedView)
  app.use(pinia)
  app.mount(host)
  return host
}

async function flush(): Promise<void> {
  for (let i = 0; i < 4; i++) await nextTick()
}

function loader(): HTMLElement | null {
  return host?.querySelector('.booking-confirmed__loader') ?? null
}
function content(): HTMLElement | null {
  return host?.querySelector('.booking-confirmed__content') ?? null
}
function emptyState(): HTMLElement | null {
  return host?.querySelector('.v-empty') ?? null
}
function emptyTitle(): string {
  return (emptyState()?.querySelector('.v-empty__title')?.textContent ?? '').trim()
}
function emptyDesc(): string {
  return (emptyState()?.querySelector('.v-empty__desc')?.textContent ?? '').trim()
}
function homeBtn(): HTMLButtonElement | null {
  return emptyState()?.querySelector<HTMLButtonElement>('button') ?? null
}
function textarea(): HTMLTextAreaElement | null {
  return host?.querySelector<HTMLTextAreaElement>('.v-textarea__field') ?? null
}
function sendBtn(): HTMLButtonElement | null {
  return host?.querySelector<HTMLButtonElement>('.booking-confirmed__ask .v-btn') ?? null
}

beforeEach(() => {
  pinia = createPinia()
  setActivePinia(pinia)
  getPracticeMock.mockReset()
  toastInfo.mockReset()
  push.mockReset()
  routeParams.practiceId = 'p1'
})

afterEach(() => {
  app?.unmount()
  host?.remove()
  app = null
  host = null
  vi.clearAllMocks()
})

describe('BookingConfirmedView', () => {
  // ===========================================================================
  describe('the ladder', () => {
    it('loading: once the reactivity flush lands, the loader shows and neither the error/missing rung nor content does', async () => {
      getPracticeMock.mockReturnValue(new Promise(() => {}))
      mount()
      await nextTick() // one tick is enough for loading=true to flush (SC finding (a))

      expect(loader()).not.toBeNull()
      expect(emptyState()).toBeNull()
      expect(content()).toBeNull()
    })

    it('(finding a, structural) the FIRST synchronous frame -- zero ticks after mount() -- already matches the error/missing rung, because the guard\'s own literal defaults (loading=false, practice=null, error=null) satisfy `!practice` before onMounted\'s fetchPractice() write has been flushed by Vue\'s scheduler', () => {
      getPracticeMock.mockReturnValue(new Promise(() => {}))
      mount() // NO await at all -- inspecting the pre-flush DOM on purpose

      expect(emptyState()).not.toBeNull()
      expect(emptyTitle()).toBe('Практика не найдена')
      expect(loader()).toBeNull()
    })

    it('error: the real backend message renders in the combined rung', async () => {
      getPracticeMock.mockRejectedValue(new ApiResponseError(404, 'Практика не существует', 'not_found'))
      mount()
      await flush()

      expect(emptyTitle()).toBe('Практика не найдена')
      expect(emptyDesc()).toBe('Практика не существует')
      expect(loader()).toBeNull()
      expect(content()).toBeNull()
    })

    it('error fallback: a non-ApiResponseError shows the hardcoded fallback, not a raw exception message', async () => {
      getPracticeMock.mockRejectedValue(new Error('ECONNRESET'))
      mount()
      await flush()

      expect(emptyDesc()).toBe('Не удалось загрузить практику')
    })

    it('content: a successful fetch renders the static success card', async () => {
      getPracticeMock.mockResolvedValue(practice())
      mount()
      await flush()

      expect(loader()).toBeNull()
      expect(emptyState()).toBeNull()
      expect(content()).not.toBeNull()
      expect(content()?.textContent).toContain('Практика забронирована!')
      expect(content()?.textContent).toContain('Ссылка на Zoom появится за 10 минут до начала.')
    })

    it('proves absence: content shows the SAME static text regardless of which practice was fetched -- no title/master/time is ever rendered', async () => {
      getPracticeMock.mockResolvedValue(
        practice({ id: 'p1', title: 'Утренняя медитация', master_name: 'Аня' }),
      )
      mount()
      await flush()
      const textA = content()?.textContent

      app?.unmount()
      host?.remove()
      getPracticeMock.mockResolvedValue(
        practice({ id: 'p2', title: 'Совершенно другая практика', master_name: 'Борис' }),
      )
      routeParams.practiceId = 'p2'
      mount()
      await flush()
      const textB = content()?.textContent

      expect(textA).toBe(textB)
      expect(textA).not.toContain('Утренняя медитация')
      expect(textA).not.toContain('Аня')
    })

    it('goToDashboard: "На главную" from the error/missing rung navigates to the dashboard', async () => {
      getPracticeMock.mockRejectedValue(new Error('boom'))
      mount()
      await flush()

      homeBtn()?.click()

      expect(push).toHaveBeenCalledWith({ name: 'user-dashboard' })
    })
  })

  // ===========================================================================
  describe('mount', () => {
    it('fetches the practice by the route practiceId', () => {
      getPracticeMock.mockReturnValue(new Promise(() => {}))
      routeParams.practiceId = 'p_specific'
      mount()

      expect(getPracticeMock).toHaveBeenCalledWith('p_specific')
    })
  })

  // ===========================================================================
  describe('⭐ finding (b): cross-practice staleness of the shared singleton store', () => {
    it('a stale DIFFERENT practice already in store.selected fools the loading guard: content (harmless -- static) renders while the real fetch for THIS practice is still in flight', async () => {
      // Populate store.selected with a DIFFERENT practice first, exactly as a
      // real session would after viewing/purchasing it on another screen.
      const store = usePracticesStore()
      getPracticeMock.mockResolvedValue(practice({ id: 'p_other' }))
      await store.fetchPractice('p_other')
      expect(store.selected?.id).toBe('p_other')

      // Now mount THIS screen for a DIFFERENT id, with its fetch left pending.
      routeParams.practiceId = 'p_new'
      getPracticeMock.mockReset()
      getPracticeMock.mockReturnValue(new Promise(() => {}))
      mount()
      await nextTick() // let loading=true flush -- same one tick as the plain loading test

      // The guard reads `!practice`, and practice is still the STALE p_other --
      // truthy -- so despite loading being true, content renders, not the loader.
      expect(loader()).toBeNull()
      expect(content()).not.toBeNull()
    })

    it('...and if that in-flight fetch then fails, the screen shows the success card BEFORE flipping to "not found" for a practice that was never actually confirmed', async () => {
      const store = usePracticesStore()
      getPracticeMock.mockResolvedValue(practice({ id: 'p_other' }))
      await store.fetchPractice('p_other')

      routeParams.practiceId = 'p_new'
      let reject!: (e: unknown) => void
      getPracticeMock.mockReset()
      getPracticeMock.mockReturnValue(new Promise((_, rej) => (reject = rej)))
      mount()
      await nextTick()

      // Confirmed above: content shows, not the loader, while genuinely pending.
      expect(content()).not.toBeNull()
      expect(emptyState()).toBeNull()

      reject(new ApiResponseError(404, 'Практика не существует', 'not_found'))
      await flush()

      // Only NOW does the screen catch up to reality.
      expect(emptyTitle()).toBe('Практика не найдена')
      expect(content()).toBeNull()
    })
  })

  // ===========================================================================
  describe('ask-master (TD-ASK-MASTER, honest stub)', () => {
    it('the request textarea and the send button are both genuinely disabled -- not just visually', async () => {
      getPracticeMock.mockResolvedValue(practice())
      mount()
      await flush()

      expect(textarea()?.disabled).toBe(true)
      expect(sendBtn()?.disabled).toBe(true)
    })

    it('clicking the disabled send button never fires the stub toast (a disabled <button> dispatches no click)', async () => {
      getPracticeMock.mockResolvedValue(practice())
      mount()
      await flush()

      sendBtn()?.click()

      expect(toastInfo).not.toHaveBeenCalled()
    })
  })
})
