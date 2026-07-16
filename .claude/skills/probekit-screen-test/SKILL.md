---
name: probekit-screen-test
description: "Generate and audit Vitest tests for Vue 3 screens (views) and route-transition logic. Mounts real SFCs in happy-dom, asserts the loading/error/empty/content ladder, and exercises route guards bare. No browser, no server, no network. Use when: writing tests for a view/screen, covering an untested view, auditing screen tests, testing route guards or role transitions. Triggers on: 'test this screen', 'screen tests', 'view tests', 'покрой экран тестами', 'тесты экрана', '/probekit-screen-test', 'пробкит экран'."
---

# screen-test v1.0.0

Generates working Vitest tests for VELO's screens (`frontend/src/views/**`) and its
route-transition logic (`frontend/src/router/guards.ts`). Produces real, passing tests —
not templates. Runs them and iterates until green.

Scope boundary vs the rest of the family:
- `probekit-unit-test` — pure modules (utils, stores, composables). Already covers those.
- `probekit-integration-test` — API/DB/service seams.
- **`probekit-screen-test` (this)** — the SFC render layer and the guard layer. The gap:
  76 screens, 0 tests.

## Configuration

<!-- VELO-tuned at birth (ПРОМТ №431). Written against the idiom actually in the
     repo, verified by reading all 23 existing test files -- NOT against the
     probekit family defaults, which assume a separate tests/ tree and
     @vue/test-utils. Both are wrong here. See references/velo-idiom.md. -->
test_output_dir: colocated -- `Foo.vue` -> `Foo.test.ts` in the SAME directory. Not a separate tree.
source_dir: frontend/src/views
guards_file: frontend/src/router/guards.ts
report_dir: .tmp/probekit-review
test_command: `cd frontend && npm run test`

## Hard constraints (do not negotiate these)

- **No browser.** No Playwright/Cypress/puppeteer. happy-dom only (`vitest.config.ts:25`).
- **No server, no network, no Telegram, no secrets.** Every boundary is mocked at its seam.
- **No new dependencies.** The harness is `vitest` + `happy-dom` + `vue`, all installed.
  `@vue/test-utils` and `@pinia/testing` are in `package.json` but **deliberately unused** —
  do not introduce them (see references/velo-idiom.md §1).
- **Never touch product code.** If a screen cannot be mounted without a product change,
  STOP and report it. Do not add a seam, do not refactor the screen, do not weaken the test.
- **Never weaken a test to make it pass.** A generated test that fails is either a bug in
  the generation or a real find. Decide which, and say which.

## Execution Steps

**Step 1 — Identify input and mode**

- A `.vue` path under `views/` → generate a screen test.
- `guards.ts` or "transition"/"guard"/"role" in the request → generate a guard test.
- A directory → enumerate, then rank by Step 2 and ask which to take.
- `--audit` → audit existing screen tests against references/screen-antipatterns.md; skip generation.
- No input → run Step 2 and propose the top-ranked untested screens.

**Step 2 — Rank (which screens are worth testing first)**

76 screens are not equal. Score each untested screen; take the highest first.

| Signal | Weight | How to detect |
|---|---|---|
| Touches money | +4 | imports `@/api/payments`, `@/stores/payments`, balance/topup/promo/withdrawal in path or imports |
| Has a real state ladder | +3 | template has `v-if` on `loading` AND (`error` OR empty) |
| Store- or API-backed | +2 | imports `@/stores/*` or `@/api/*` |
| Behind a role guard | +2 | its route has `beforeEnter` in `router/index.ts` |
| Branching computed logic | +2 | `computed(` count >= 3 in `<script setup>` |
| Reads wall-clock time | +1 | `Date.now()` / `new Date()` — nondeterministic, so a test earns its keep |
| Inert stub | -5 | every handler is a toast; no store/API/onMounted (e.g. `views/auth/*`) |
| Pure presentation | -3 | no store, no API, no onMounted, no computed |

Report the ranking to the operator before generating in bulk. Never silently pick.

**Step 3 — Classify the screen's pattern** *(this decides the whole test's shape)*

Read the `<script setup>` block. VELO has exactly two screen patterns — identify which:

- **Pattern A — store-backed.** State lives in a Pinia store (`store.loading`, `store.error`,
  `store.items`). Example: `views/user/MyBookingsView.vue`.
  → Use a REAL Pinia store (`setActivePinia(createPinia())`), mock the **API seam the store
  imports**, drive the ladder by setting store state directly.
- **Pattern B — local-ref.** State lives in the component (`const loading = ref(true)`), fed by
  a direct `@/api/*` call in `onMounted`. Example: `views/master/MasterStudentsView.vue`.
  → No pinia needed. Mock the `@/api/*` module the screen imports. Drive the ladder by
  controlling the mock's resolve/reject.

Getting this wrong produces a test that mocks the wrong layer and asserts nothing.

**Step 4 — Inventory the mount requirements**

Before writing, grep the screen for each and plan a seam:

| Found | Do this |
|---|---|
| `useRouter` / `useRoute` | mock `vue-router` → `{ push: vi.fn(), back: vi.fn(), replace: vi.fn() }`. Never build a real router. |
| `useToast` | mock `@/composables/useToast` and assert the call |
| `Date.now()` / `new Date()` | `vi.setSystemTime(new Date('...'))` — a FIXED instant, or badges/sorting are nondeterministic |
| `Intl.DateTimeFormat` with `timeZone` | pin the timezone in fixtures; assert on a fixed tz |
| a `Teleport to="body"` child (modals) | query `document.body`, not the mount root (`CalendarFilterModal.test.ts:49`) |
| `getComputedStyle` / `visualViewport` | happy-dom returns empty strings / undefined. Only matters if read during mount — check. |
| `waitUntilReady()` transitively | `__setReadyForTest(true)` — testTimeout is 5s, READY_TIMEOUT_MS is 10s |

**Step 5 — Generate** (read references/velo-idiom.md and follow it exactly)

Write the file colocated, `Foo.test.ts`. Open with the repo's `====` banner comment block
stating WHY this test exists and any order/time dependence. Then:

Screens — assert the ladder, one `it()` per rung:
1. **loading** — renders the loader on initial load
2. **error** — renders the error state AND surfaces the real message (not a hardcoded string)
3. **empty** — renders the empty state when the fetch returns nothing
4. **content** — renders what the store/API actually said (assert on real values, not counts alone)
5. **behaviour** — the screen's own logic: sorting, badges, filtering, the preview cap
6. **navigation** — a click pushes the RIGHT route with the RIGHT params

Guards — assert both directions, per `guards.test.ts`:
1. right role passes (`toBe(true)`)
2. wrong role is redirected (`toEqual({ path: '...' })`)
3. negative space — the guard does NOT touch stores it shouldn't (`expect(fn).not.toHaveBeenCalled()`)

**Step 6 — Run and iterate**

`cd frontend && npm run test`. The suite must be green overall — a red suite blocks deploys
(`frontend/Dockerfile:33`, gate restored in `fda4b9e`). If a generated test fails:
- generation bug → fix the test
- real find → STOP, report it, do not fix product code
- untestable without a product change → STOP, report it

**Step 7 — Report**

Write to `.tmp/probekit-review/`. State: screens covered, ladder rungs asserted per screen,
any real finds, any screens rejected as untestable and why.

## References

- `references/velo-idiom.md` — the mount/mock idiom, verbatim from the repo. Read before generating.
- `references/screen-antipatterns.md` — what makes a screen test worthless.
- `references/severity-format.md` — family format (probekit-core).

## Anchor

[*] screen-test v1.0.0 * ready
[>] | NEXT: user command
