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

## §3 Flush async with repeated `nextTick`

`CalendarFilterModal.test.ts:71-74` awaits `nextTick()` **three times**, commented
"Flush the onMounted async catalog fetch + its .then continuation." An `onMounted` that
awaits an API call needs more than one tick: one for the mount, one for the promise
continuation, one for the re-render. Prefer an explicit helper:

```ts
async function flush(): Promise<void> {
  await nextTick()
  await nextTick()
  await nextTick()
}
```

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
