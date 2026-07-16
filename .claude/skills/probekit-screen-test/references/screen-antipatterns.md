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

**SC-07 is about READING teleported content. Reaping it is a separate obligation — SC-13.
Doing SC-07 correctly does not save you from SC-13.**

## SC-08 — Too few ticks, or a tick count copied rather than counted
A single `await nextTick()` after mounting a screen whose `onMounted` awaits an API call: the
DOM has not re-rendered yet.

But the sharper version of this bug is **copying "three"** out of §3 because a leaf component
needed three. Three is not the rule — it was one screen's answer. `TopupSuccessView` needs
**5**, `MasterFinanceView` needs **6**. The count is one tick per `await` in the chain the
mount kicks off, plus one for the final re-render; a store action awaiting an API wrapper
awaiting the client has already spent four before it paints.

**Instead:** count YOUR chain (velo-idiom §3). A tick count you cannot explain is a race that
passes here and fails on a colleague's machine. Under-counting fails loudly; over-counting is
harmless — when unsure, go higher and write down what you counted.

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

## SC-13 — Teleported overlay left un-reaped after unmount *(the expensive one)*
A **closed** teleported overlay survives `app.unmount()`. `VBottomSheet` and `VModal` wrap the
overlay in a `<Transition>` (`VBottomSheet.vue:19-20`, `VModal.vue:21-22`); when `open` flips to
`false`, Vue holds the leaving element pending a `transitionend` that **happy-dom never fires**,
and `unmount()` does not reap it. It stays parked directly on `document.body`, outliving the app
that created it.

The next test then finds the **DEAD** overlay first in document order, clicks it, and nothing
happens — the handler belongs to an unmounted app. Every downstream assertion fails while the
screen under test is perfectly healthy.

**Signature — learn this one, it is unmistakable:** *the first sheet/modal test in a file passes
and every later one fails.* If you see that shape, do not debug the screen. You are clicking a
corpse. Confirmed on `MasterNewPromocodeView` and `AdminWithdrawalDetailView`.

**Instead:** purge in `afterEach`, unconditionally, in every file whose screen can open an
overlay — cheap, idempotent, and invisible when unnecessary:
```ts
document.body.querySelectorAll('.v-sheet__overlay').forEach((el) => el.remove())
document.body.querySelectorAll('.v-modal__overlay').forEach((el) => el.remove())
```
Purge the class the child actually teleports — grep it rather than trusting this pair; a new
overlay component will not be listed here. Precedent: `MasterNewPromocodeView.test.ts:159-173`,
`AdminPromosView.test.ts:132-142`, `AdminWithdrawalDetailView.test.ts:164-176`.

*(Three separate test files independently rediscovered this and hand-rolled the same purge before
it was ever written down. That is the cost of leaving a finding in an orc's head.)*

### SC-13b — the same mechanism, from the other side: asserting the overlay is GONE
The corollary, and it bites even when you HAVE the purge. To prove a dialog closes, the obvious
assertion is:
```ts
expect(document.body.querySelector('.v-modal__overlay')).toBeNull()   // <- never true
```
It never passes. The overlay is not removed — it is parked at `v-modal-leave-active` awaiting the
`transitionend` happy-dom will not fire. **The product is correct; the assertion is wrong.** The
danger is that this failure looks exactly like "the dismiss handler is broken", so the reflex is to
go debug a healthy screen, and the second reflex — after the screen turns out fine — is to delete
the assertion, which is SC-10.

**Instead**, assert the leave *started*, and pin the negative case so it cannot always-pass:
```ts
function dialogDismissed(): boolean {
  return !!document.body.querySelector('.v-modal-leave-active')
}
expect(dialogDismissed()).toBe(false)   // while open -- guards against a vacuous test
// ... dismiss ...
expect(dialogDismissed()).toBe(true)
```
Or sidestep it: assert that the *action* did not fire (`expect(cancelPractice).not.toHaveBeenCalled()`)
rather than that the DOM vanished. Both are live in the repo — `MasterPracticeDetailView.test.ts`
takes the first, `EditPracticeView.test.ts` the second.

*(Two agents hit this independently on the same evening, both with SC-13 already in front of them —
which is why it is written out here rather than left as an inference from the mechanism.)*

### SC-13c — the corpse that parks MID-test, where `afterEach` cannot reach
The `afterEach` purge (SC-13) handles corpses BETWEEN tests. It does nothing for a screen that opens
**two or three overlays inside a single test** — a date sheet, then a time sheet, then a series
end-date sheet. Each close parks a corpse on `document.body` immediately, so
`document.body.querySelector('.v-sheet__save')` finds the DEAD one first, in document order, while
the live sheet sits behind it.

**Instead**, scope every body query to exclude the leaving element:
```ts
function liveSheet(): HTMLElement | null {
  return document.body.querySelector('.v-sheet__overlay:not(.v-sheet-leave-active)')
}
```
This is robust in both worlds: if the leave ever does resolve (a real browser, or a future happy-dom),
the selector still finds the live overlay. Live precedent: `CreatePracticeView.test.ts`, which opens
three sheets in one test.

## SC-14 — Whole-host assertions on a `v-show` screen (a test that cannot fail)
`v-if` removes; **`v-show` only sets `display:none`**. Both panes stay in the DOM forever, so
`host.textContent` spans BOTH tabs at once and a class like `.analytics__loader` matches either one.
```ts
expect(host.textContent).toContain('Платежи')   // <- true before you even switch tabs
```
The test passes whatever the screen does. It is SC-01's cousin: not a weak assertion, an *impossible*
one. Worse than a smoke test, because it looks specific.

**Instead:** scope every query to the pane under test.
```ts
function reviewsPane(): HTMLElement { return host.querySelector('.analytics__body')! }
```
Live case: `AnalyticsView.vue:54,175` — currently the only `v-show` tabs in `views/`, so grep
`v-show` before assuming a screen is safe. Precedent: `AnalyticsView.test.ts`.

**The tab STRIP is a second, subtler instance.** Even on a `v-if` screen the tab buttons are always
mounted, so `expect(text()).toContain('Прошедшие')` is unfailable — it matches the button, not the
pane. Read the active tab off `aria-selected` or the rendered list. Live: `MasterPracticesView.test.ts`
(a `v-if` screen where SC-14 does *not* bite the panes but *does* bite the strip).

## SC-15 — Negative-space assertion over a possibly-empty list
The natural way to prove a filter excludes something:
```ts
expect(titles()).not.toContain('Отменённая')   // <- also passes if NOTHING rendered
```
A `not.toContain` is satisfied by a mount that rendered nothing at all — a broken fixture, a failed
flush, a wrong tab. The test then guards a filter that may not even run. This is the natural failure
mode of **any screen whose behaviour IS a filter**, which is most list screens.

**Instead:** pin the positive set FIRST, then the exclusion is real:
```ts
expect(titles()).toEqual(['Завтрашняя', 'Через неделю'])   // proves the list rendered AND excluded
```
Precedent: `MasterPracticesView.test.ts`.

## SC-16 — A fixture longer than the screen's own preview cap
A screen that caps its list (`slice(0, 5)`, "показать ещё") will silently drop the tail of your
fixture. Build a 4-case boundary fixture on a 3-row cap and the case you actually care about — the
last one — never mounts. The test passes, having proven nothing about it.

**Instead:** assert the row COUNT first, or expand before asserting per-row derivations. `toEqual` on
the full set catches it; `toContain` passes vacuously. Live: `MasterStudentProfileView.test.ts`, where
a 4-rating boundary fixture rendered 3 rows and the `8 → Огонь!` case never existed.
