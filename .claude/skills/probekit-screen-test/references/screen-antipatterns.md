# Screen-test anti-patterns

What makes a generated screen test worthless. Check every generated file against this list
before reporting it as done.

## SC-01 — Mount smoke test
`expect(host.textContent).toBeTruthy()` after mounting. Proves the component is not a syntax
error and nothing else. If the only assertion is "it rendered", the test is a placeholder.
**Instead:** assert a value that came from the mocked store/API and could only appear if the
screen read it correctly.

## SC-02 — Asserting the mock instead of the screen
```ts
expect(getStudents).toHaveBeenCalled()   // <- tests onMounted, not the screen
```
That the fetch fired is one line of setup, not the behaviour. **Instead:** assert what the
screen *did* with the result — the rendered name, the sorted order, the badge.

## SC-03 — Two pinia instances
`setActivePinia(createPinia())` in the test, and a *different* `createPinia()` passed to
`app.use()`. The test mutates one store; the component renders another. Everything passes;
nothing is proven. **Instead:** one instance, both places.

## SC-04 — Wall-clock fixtures
A fixture built as `new Date(Date.now() + 86400000)` for a "Завтра" badge. Passes at 10:00,
fails at 23:30 near a timezone boundary, and fails differently in CI. **Instead:**
`vi.setSystemTime()` a fixed instant and build fixtures as literals relative to it.

## SC-05 — Hardcoded error string asserted as if it came from the backend
`MasterStudentsView.vue:135-137` does `catch { error.value = 'Попробуйте ещё раз' }` — the
backend message is swallowed. Asserting that literal proves the screen's own constant, not
error propagation. Assert it, but do not *claim* it proves the backend message surfaces.
Contrast `MyBookingsView.vue:31`, which binds `:description="store.error"` — there the real
message does surface, and asserting it is meaningful. Know which pattern you are in.

## SC-06 — Ignoring the initial-load guard
`MyBookingsView.vue:22,28` gate loading/error on `&& store.bookings.length === 0` — they only
show on the *initial* load, so a failed load-more keeps content visible. A test that sets
`error` with a non-empty list and expects the error state will fail, and the screen is right.
Read the guard before asserting the rung.

## SC-07 — Teleported content queried from the mount root
Modals `Teleport to="body"`. `host.querySelector` finds nothing; the test concludes "not
rendered". Query `document.body` (`CalendarFilterModal.test.ts:48-52`).

## SC-08 — One tick
A single `await nextTick()` after mounting a screen whose `onMounted` awaits an API call.
The DOM has not re-rendered yet. Needs the mount tick, the promise continuation, and the
re-render (§3 of velo-idiom.md).

## SC-09 — Testing an inert stub as if it were live
`views/auth/*` are dormant, unlinked stubs (`router/index.ts:496-502`); every handler is a
toast. A test asserting "clicking Войти logs the user in" is fiction. Test what the stub
actually does — that it renders and that the inert handler fires the toast — and label it as
a stub in the banner.

## SC-10 — Weakening to green
Deleting an assertion, loosening `toEqual` to `toBeTruthy`, or wrapping in try/catch to make
a red test pass. A red generated test is either a generation bug or a real find. Both get
reported. Neither gets hidden.

## SC-11 — Guard tested one-directional
Asserting the right role passes but never that the wrong role is redirected. The redirect IS
the guard's job; the pass-through is the trivial half. Always assert both, plus the negative
space (`guards.test.ts:241-245` — the guard must not touch stores it has no business touching).

## SC-12 — Stubbing children to make a mount work
Reaching for stubs because a child component throws. The repo stubs nothing. A child that
cannot mount is a finding worth reporting — it may be a real defect in that child.
