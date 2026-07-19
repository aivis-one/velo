# VELO screen-test idiom

Every pattern below was read out of the repo's 23 existing test files, not invented.
Follow it exactly. Where you are extending it (screens are new territory), the extension
is marked and justified.

## §1 Mount: `createApp` + happy-dom. NOT `@vue/test-utils`.

`@vue/test-utils@2.4.11` (`frontend/package.json:31`) and `@pinia/testing@0.1.7` (`:28`) are
installed and have **zero usages** in `src/`. This is deliberate and documented three times:

> `MethodTaxonomyPicker.test.ts:19-20` — "Dependency-free SFC mount (createApp + happy-dom),
> matching VPaginationDots.test.ts -- the repo has no @vue/test-utils usage; plugin-vue
> (vitest.config) compiles the .vue for us."

Do not introduce them. The canonical mount (`CalendarFilterModal.test.ts:33-46`):

```ts
let app: App | null = null
let host: HTMLElement | null = null

function mount(): void {
  host = document.createElement('div')
  document.body.appendChild(host)
  app = createApp(ScreenUnderTest)
  app.mount(host)
}

afterEach(() => {
  app?.unmount()
  host?.remove()
  app = null
  host = null
  vi.clearAllMocks()
})
```

**MANDATORY for any screen that opens a modal or a bottom sheet — reap the overlay.**
`app.unmount()` does NOT remove a CLOSED teleported overlay; it stays parked on
`document.body` and the next test clicks the dead node. Add the purge to `afterEach`
(full mechanism: `screen-antipatterns.md` SC-13):

```ts
afterEach(() => {
  app?.unmount()
  host?.remove()
  app = null
  host = null

  // A closed teleported overlay survives unmount -- the <Transition> leave awaits
  // a transitionend happy-dom never fires. Without this, the first sheet test in
  // the file passes and every later one fails against a DEAD node. SC-13.
  document.body.querySelectorAll('.v-sheet__overlay').forEach((el) => el.remove())
  document.body.querySelectorAll('.v-modal__overlay').forEach((el) => el.remove())

  vi.clearAllMocks()
})
```
Purge the class the component actually teleports: `.v-sheet__overlay` for `VBottomSheet`
(`VBottomSheet.vue:20`), `.v-modal__overlay` for `VModal` (`VModal.vue:22`). Grep the child
rather than trusting this list — a new overlay component will not be in it.

Props and event handlers both go in `createApp`'s second arg; handlers arrive as `onFoo`
props (`MethodTaxonomyPicker.test.ts:41-44`):

```ts
app = createApp(Picker, { modelValue, 'onUpdate:modelValue': () => {} })
```

**Extension for screens (new — no prior precedent).** Screens need Pinia inside the mount.
There is no existing `app.use()` in any test because leaf components needed nothing. Use:

```ts
app = createApp(ScreenUnderTest)
app.use(pinia)          // the SAME instance passed to setActivePinia
app.mount(host)
```

Create it once per test in `beforeEach` and hand the same instance to both, or the component
resolves a different store than the test does — the single most likely way to get a green
test that proves nothing.

## §2 Nothing is stubbed. Children render for real.

`CalendarFilterModal.test.ts` stubs no child components; assertions run against real DOM
(`findChip('Терапия')`, `.click()`). Do the same. If a child is genuinely unmountable,
that is a finding to report, not a reason to reach for `global.stubs`.

## §3 Flush async with repeated `nextTick` — COUNT THE AWAITS, do not copy a number

**Three is not the rule. Three was one screen's answer.** `CalendarFilterModal.test.ts:71-74`
awaits `nextTick()` three times because ITS chain is three deep: the mount, the promise
continuation, the re-render. Screens go deeper. Measured in this repo:

| Screen | Ticks needed |
|---|---|
| `CalendarFilterModal` (leaf, one fetch) | 3 |
| `TopupSuccessView` | **5** (`TopupSuccessView.test.ts:60-62`) |
| `MasterFinanceView` | **6** (`MasterFinanceView.test.ts:119-121`) |

The count is **one tick per `await` in the chain the mount kicks off, plus one for the final
re-render**. A screen whose `onMounted` awaits a store action that awaits an API wrapper that
awaits the client has already spent four before it renders. Derive it: read the chain and
count, or raise the loop until the assertion goes green and then confirm you understand WHY
that number — a tick count you cannot explain is a race that will fail on someone else's
machine.

Use a loop, not a copied stack of calls, so the count is a number a reader can see and change:

```ts
async function flush(): Promise<void> {
  for (let i = 0; i < 5; i++) await nextTick()   // <- count YOUR chain
}
```
An under-count fails loudly (the DOM has not re-rendered). An over-count is harmless. When in
doubt, go higher — but write down what you counted.

## §4 Mock at the seam the code actually imports

Two variants, both live in the repo. Pick by what the module under test imports.

**Client seam** — when the code calls `api.get/post` directly (`stores/auth.test.ts:30-41`,
byte-identical in `api/bookings.test.ts:16-27` and `api/payments.test.ts:18-29`):

```ts
vi.mock('@/api/client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/api/client')>()
  return {
    ...actual,
    api: { get: vi.fn(), post: vi.fn(), patch: vi.fn(), delete: vi.fn() },
  }
})
```
`importOriginal` + spread keeps `ApiResponseError` **real**, so rejection tests assert on the
real class (`payments.test.ts:82-89`). Never re-implement error classes in a mock.

**Wrapper seam** — when the code imports an `@/api/*` wrapper
(`MethodTaxonomyPicker.test.ts:30-33`):

```ts
vi.mock('@/api/taxonomy', async () => {
  const actual = await vi.importActual<typeof import('@/api/taxonomy')>('@/api/taxonomy')
  return { ...actual, getActiveTaxonomy: vi.fn() }
})
```

Bare `vi.mock('@/api/bookings')` (auto-mock) is also used (`stores/bookings.test.ts:32`) when
no real export needs preserving.

## §5 Real Pinia, mocked dependencies

`setActivePinia(createPinia())` in `beforeEach` — every store/guard test does this
(`stores/auth.test.ts:24`, `stores/bookings.test.ts`, `guards.test.ts:74`).
**Real stores, mocked API.** Never `createTestingPinia`.

A store that is a *dependency* (not under test) is mocked wholesale, using a
**mutable module-scope object behind getters** so tests mutate state instead of re-mocking
(`guards.test.ts:42-57`):

```ts
const masterStoreState: { profileMissing: boolean; profile: { status: string } | null } = {
  profileMissing: false,
  profile: null,
}
vi.mock('@/stores/master', () => ({
  useMasterStore: () => ({
    get profileMissing() { return masterStoreState.profileMissing },
    get profile() { return masterStoreState.profile },
    fetchMyProfile,
  }),
}))
```
Same trick for a mutable platform name (`stores/auth.test.ts:30-59`).

**The getter is load-bearing against a TDZ crash, not just a convenience.** `vi.mock` factories are
HOISTED above the test file's `const`s. A factory referencing a spy at its TOP level —
`vi.mock('@/platform', () => ({ platform: { openLink } }))` — throws *"Cannot access 'openLink'
before initialization"* as soon as the mocked module is imported EAGERLY (`stores/auth.ts` imports
`@/platform`, so the factory runs during the `.vue` import, before your consts exist).

The `vue-router` / `useToast` factories survive identically-shaped code only because their spies sit
inside a nested arrow nobody calls until mount. The rule: **a spy referenced at factory top level
needs the getter; one referenced inside a returned function does not.** Found on
`MasterDashboardView.test.ts`.

## §6 Router: mock `vue-router`, never build one

No test builds a router. Guards are called **bare** through a cast helper
(`guards.test.ts:33-40`), justified by "Guards ignore (to, from, next) entirely at runtime":

```ts
type BareGuardResult = { path: string } | { name: string; params?: Record<string, string> } | true
function call(guard: unknown): Promise<BareGuardResult> {
  return (guard as () => Promise<BareGuardResult>)()
}
```

For screens, mock the composable:

```ts
const push = vi.fn()
const back = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push, back }) }))
```
Then assert the *intent*: `expect(push).toHaveBeenCalledWith({ name: 'practice-detail', params: { id: 'p1' } })`.

**Never import `@/router/index.ts` in a test.** It holds a module-level
`let authInitialized = false` (`router/index.ts:547-570`) that leaks across tests.

**Route meta carries no auth data.** All role logic is in `beforeEnter` (`router/index.ts:193-211`).
You cannot assert `route.meta.roles` — it does not exist. Exercise the guard.

## §7 The auth seam

`__setReadyForTest(true)` (`composables/useAuth.ts:107-109`, test-only, zero production callers)
forces `isReady` without running the real bootstrap. Pair with `resetAuthState()`
(`useAuth.ts:93-98`) in `beforeEach` or the module singleton leaks across tests.

`testTimeout` is 5000ms (`vitest.config.ts:31`) but `READY_TIMEOUT_MS` is 10_000
(`useAuth.ts:59`). Anything that transitively awaits `waitUntilReady()` must either set the
seam or use fake timers (`guards.test.ts:117-123`):

```ts
vi.useFakeTimers()
const promise = call(roleRedirect)
await vi.advanceTimersByTimeAsync(10_000)
expect(await promise).toEqual({ path: '/auth-error' })
```
Restore with `afterEach(() => { vi.useRealTimers() })`.

## §8 Free from the harness

`test-setup.ts` runs `resetClientState()` in a global `beforeEach` — API client token, 401
callback, and in-flight GET dedupe map are already clean. Do not re-do it.
`vitest.config.ts`: `include: ['src/**/*.test.ts']` — **`.ts` only**, alias `@` → `src`,
`plugins: [vue()]` compiles the SFC.

## §9 Determinism

Screens that read `Date.now()` / `new Date()` (badges, sorting, "Сегодня"/"Завтра") are
nondeterministic unless time is pinned:

```ts
beforeEach(() => { vi.setSystemTime(new Date('2026-07-20T12:00:00Z')) })
afterEach(() => { vi.useRealTimers() })
```
Build fixtures **relative to that instant**, not to `Date.now()` at write time.

Order-dependent tests are allowed but must be **declared in the banner**
(`CalendarFilterModal.test.ts:13-19` does this for a session-lifetime module cache).
No shuffle is configured; declaration order is execution order.

## §10 Comment like the repo

Every test file opens with a `====` banner explaining WHY it exists, what it proves, which
prompt/stage produced it, and any trap a later reader would trip on. Match that density.
State constraints the code cannot show; do not narrate what the next line does.

## §11 The ru NBSP trap — every money assertion, without exception

`formatMoney` (`utils/format.ts:27-40`) is `Intl.NumberFormat('ru', {style:'currency'})`. The
ru locale groups thousands with **U+00A0 (NBSP)**, not the space on your keyboard — what
looks like `1 234,56 EUR` is really `1` + `U+00A0` + `234,56` + `U+00A0` + `€`. A normally
typed assertion passes on `9,99` and fails on every amount over 999, so the trap hides until a
fixture crosses a thousand — and the failure reads as a wrong VALUE rather than a wrong
space, which sends you hunting the screen instead of the assertion. It bit this skill's first
user twice.

This section deliberately NAMES the codepoint rather than showing it: a literal NBSP is exactly
as invisible in prose as it is in code.

This is not an edge case. **"Touches money" is the ranking's +4 signal (Step 2), so the screens
this skill is aimed at FIRST are precisely the ones that hit it.** Normalise before asserting:

```ts
// Written as ESCAPES, never as literal characters -- a literal NBSP is invisible
// in a diff, and the next editor "tidies" it into a plain space without ever
// seeing what they broke.
function norm(s: string | null | undefined): string {
  return (s ?? '').replace(/[\u00A0\u202F\u2009]/g, ' ')
}

expect(norm(text())).toContain('1 234,56')   // plain space -- norm() made it one
```

Live precedent: `MasterFinanceView.test.ts:123-135`, `AdminRevenueView.test.ts:92`. Both
normalise THREE space variants — NBSP (`\u00A0`), narrow NBSP (`\u202F`), thin space
(`\u2009`) — because the exact codepoint Intl emits varies by Node/ICU build. Pinning a
single one writes a test that breaks on a runtime upgrade for no reason.

### Writing the escapes is harder than knowing the rule — plan for it
Four agents have now typed literal NBSPs into the very `norm()` written to defeat them, each having
just read this section. Knowing the rule does not save you; the characters are invisible.
- **Patch via a SCRIPT FILE, not an inline shell command.** A quoted heredoc or `python -c` collapses
  `\\u00A0` into a real NBSP before your code ever sees it — the fix silently writes the bug back in.
- **The Edit tool cannot reliably match a literal NBSP** in `old_string`, so a file that already has
  them resists the obvious repair. Rewrite the region from a script instead.
- **Verify by CODEPOINT SCAN, never by reading.** Reading the file back shows a space either way:
```python
bad = [n+1 for n,l in enumerate(open(p, encoding='utf-8').read().split(chr(10)))
       if any(c in l for c in (chr(0xA0), chr(0x202F), chr(0x2009)))]
```
- ESLint's `no-irregular-whitespace` also catches it — but only if you run it.
