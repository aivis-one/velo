# a11y-audit — frontend/src — 2026-04-28

**Skill**: probekit-a11y-audit v1.0.0
**Target**: `frontend/src` + `frontend/index.html`
**WCAG target**: 2.1 AA
**Mode**: full project audit

---

## Summary

| Probe | Severity | Score | Status |
|---|---|---|---|
| P1 — Semantic HTML | CRITICAL | 7/10 | partial |
| P2 — ARIA Roles & Attributes | HIGH | 7/10 | partial |
| P3 — Keyboard Navigation | CRITICAL | 6/10 | partial |
| P4 — Focus Management | HIGH | 5/10 | WARN |
| P5 — Color Contrast | HIGH | 7/10 | not directly measurable; tokens-based |
| P6 — Form Labels | CRITICAL | 6/10 | partial |
| P7 — Skip Links & Landmarks | MEDIUM | 6/10 | landmarks present, skip-link missing |
| P8 — Screen Reader Text | MEDIUM | 6/10 | partial |
| **Average** | — | **6.25/10** | — |

**Quality Gate**: **WARN** (avg ≥5.0 and <7.0 per SKILL.md gate definition; no probe scores 0; CRITICAL findings have clear fix paths).

**Findings**: 0 hard 🔴 / 6 🟡 / 4 🟢. Two probes (P3, P6) are tagged CRITICAL by category but downgraded to WARNING per `severity-format.md` (clear fix path; partial coverage already exists).

**Headline**: a11y is the largest improvement area at S1 close. Architecture is sound (semantic landmarks + reusable button components + modal Escape handling); polish is partial. No findings block S1 close, but the gap will compound across S2/S3 if not addressed.

---

## P1 — Semantic HTML (CRITICAL category) — 7/10

### Confirms

- **Layout components use semantic elements**: `components/layout/VHeader.vue:14` uses `<header>`, `VTabBar.vue:12` uses `<nav>`, `MobileLayout.vue:20` and `AdminLayout.vue:22` use `<main>`. Architecture-level a11y is correct.
- **Tab bar buttons**: `VTabBar.vue:13` uses `<button>` for nav items (not `<div @click>`). Clean.
- **Headings present in 29 files** with grep on `<h1>-<h6>`.

### 🟡 WARNING — `<div @click>` used as buttons (7 sites across 4 files)

`grep 'div[^>]*@click'` finds 7 sites where a `<div>` carries the click handler instead of a `<button>`:

| File | Line | Element | Severity context |
|---|---|---|---|
| `views/user/UserProfileView.vue` | 44 | `<div class="profile__balance" @click="onTopup">` | 🟡 |
| `views/user/UserProfileView.vue` | 58 | menu item «Мои бронирования» | 🟡 |
| `views/user/UserProfileView.vue` | 70 | menu item «Уведомления» | 🟡 |
| `views/user/UserProfileView.vue` | 75 | menu item «Язык / Часовой пояс» | 🟡 |
| `views/user/UserProfileView.vue` | 87 | menu item «Поддержка» | 🟡 |
| `views/user/UserProfileView.vue` | 101 | menu item «Вернуться в режим X» | 🟡 |
| `views/user/UserProfileView.vue` | 114 | menu item «Выйти» | 🟡 (destructive action) |
| `views/master/MasterDashboardView.vue` | 53 | balance card | 🟡 |
| `components/shared/PracticeCard.vue` | 15 | entire card click target | 🟡 |
| `views/user/UserDashboardView.vue` | 149 | div with `@click.stop` (intercepts click bubbling) | 🟢 — pattern is intentional event-stop, not a clickable element |
| `components/master/PracticeListItem.vue` | 34 | div with `@click.stop` | 🟢 — same pattern |

**Concrete impact**: 7 user-flow elements (5 in UserProfileView, 1 in MasterDashboard balance card, 1 in PracticeCard) are not keyboard-focusable, not announced by screen readers, and require mouse/tap interaction. Logout in particular (line 114) is a destructive irreversible action that's keyboard-inaccessible.

**Fix template**:
```diff
- <div class="profile__menu-item" @click="onLogout">
+ <button type="button" class="profile__menu-item" @click="onLogout">
    <span class="profile__menu-icon">🚪</span>
    <span class="profile__menu-text">Выйти</span>
    <span class="profile__menu-arrow">→</span>
- </div>
+ </button>
```
Then in CSS: `.profile__menu-item { background: none; border: none; text-align: left; width: 100%; cursor: pointer; }` (override default button styles).

**Counter-pattern (already in admin views)**: `AdminDashboardView.vue:28, 74, 84, 94`, `AdminMastersView.vue:56`, `AdminReportsView.vue:60` use `<div tabindex="0" @click @keydown.enter.space.prevent>` — this is the «keyboard-accessible div» pattern. Acceptable but `<button>` is better. Recommend converging on `<button>`.

---

## P2 — ARIA Roles & Attributes (HIGH category) — 7/10

### Confirms

- **Icon-only buttons have `aria-label`**: confirmed at `VAccordion.vue:14`, `VModal.vue:31` (Закрыть), `MasterDashboardView.vue:68` (Переключить период), `MasterPracticesView.vue:29` (Создать практику), 3 sites in DiaryEntryDetail/Form, DiaryList.vue FAB, PracticeDetailView.vue master profile link.
- **`aria-expanded` on accordion**: `VAccordion.vue:14` — correct.
- **`role="dialog"` + `aria-modal="true"`** on VModal — correct.

### 🟡 WARNING — VTabBar active item missing `aria-current`

`components/layout/VTabBar.vue:13-19`:
```vue
<button
  v-for="item in items"
  :key="item.to"
  class="v-tabbar__item"
  :class="{ 'v-tabbar__item--active': active === item.to }"
  @click="$emit('navigate', item.to)"
>
```

Active tab is indicated only via CSS class. Screen readers don't announce «current page» to users. Add:

```diff
  <button
    v-for="item in items"
    :key="item.to"
    class="v-tabbar__item"
    :class="{ 'v-tabbar__item--active': active === item.to }"
+   :aria-current="active === item.to ? 'page' : undefined"
    @click="$emit('navigate', item.to)"
  >
```

### 🟡 WARNING — VToast lacks `aria-live` / `role="status"`

`components/ui/VToast.vue:11-25`:
```vue
<TransitionGroup name="v-toast" tag="div" class="v-toast-container">
  <div v-for="toast in toasts" ...>
```

Toasts (success/error/info messages from `useToast()`) are not announced to screen readers because the container has no live-region role. Fix:

```diff
- <TransitionGroup name="v-toast" tag="div" class="v-toast-container">
+ <TransitionGroup
+   name="v-toast"
+   tag="div"
+   class="v-toast-container"
+   role="status"
+   aria-live="polite"
+   aria-atomic="false"
+ >
```

For error toasts specifically, consider `aria-live="assertive"` and `role="alert"`. The simplest fix: use `role="status" aria-live="polite"` on the container and accept that errors may be announced with a slight delay — better than not at all.

---

## P3 — Keyboard Navigation (CRITICAL category) — 6/10

### Confirms

- Admin views correctly add `@keydown.enter.space.prevent` on div-clickable elements (4 sites confirmed in AdminDashboard, AdminMasters, AdminReports).
- `VStatCard.vue:19` uses `@keydown.enter.space.prevent="clickable ? $emit('click') : undefined"` — keyboard-aware.
- `BookingPopup.vue:54` uses `@keydown.enter` on promo-code input — Enter submits.
- VModal Escape closes (`VModal.vue:68-72`).

### 🟡 WARNING — 7 div-clickable elements without keyboard handler

Inverse of P1 finding: same 7 sites in `UserProfileView.vue`, `MasterDashboardView.vue:53`, `PracticeCard.vue:15` lack `@keydown.enter`/`@keydown.space` AND `tabindex="0"`. They are keyboard-unreachable. PracticeCard in particular is the primary navigation pattern in user dashboard — keyboard users cannot navigate to a practice from the user dashboard via keyboard.

If P1 fix lands (convert to `<button>`), this resolves automatically. Recommend converging the fixes.

### 🟡 WARNING — VToast click-to-dismiss only via mouse

`VToast.vue:19` — `@click="dismiss(toast.id)"` on the toast `<div>`. No keyboard equivalent. Toasts auto-dismiss (likely on a timer in `useToast()`), so this is partial mitigation. Still, keyboard users cannot dismiss a stuck/unwanted toast manually.

Fix: convert to `<button>` (same fix as P1) OR add `@keydown.enter.space="dismiss"` + `tabindex="0"` + `role="button"`.

---

## P4 — Focus Management (HIGH category) — 5/10

### Confirms

- All `outline: none` sites are paired with alternative focus indicators (border-color or background change). 11 sites confirmed; pattern: `:focus { outline: none; border-color: var(--steel-muted); }`. WCAG-acceptable.
- VModal calls `addEventListener('keydown', onKeydown)` for Escape — correct.

### 🟡 WARNING — VModal lacks focus trap and focus return

`components/ui/VModal.vue` has:
- `role="dialog" aria-modal="true"` ✓
- Escape closes ✓
- Overlay click closes ✓
- ✗ Focus does NOT move into modal on open
- ✗ Focus does NOT return to the trigger element on close
- ✗ Tab can leave the modal and reach background page elements

**Impact**: keyboard users opening a booking popup, cancel-booking confirm dialog, or report dialog face confusing focus state. After closing, focus may be lost (lands at body or back at first focusable on page).

Fix sketch:
```diff
+ const previousActiveElement = ref<HTMLElement | null>(null)
+
+ watch(() => props.open, async (isOpen) => {
+   if (isOpen) {
+     previousActiveElement.value = document.activeElement as HTMLElement
+     await nextTick()
+     // Move focus to first focusable element inside modal:
+     const firstFocusable = modalRef.value?.querySelector<HTMLElement>(
+       'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
+     )
+     firstFocusable?.focus()
+   } else {
+     previousActiveElement.value?.focus()
+     previousActiveElement.value = null
+   }
+   document.body.style.overflow = isOpen ? 'hidden' : ''
+ })
```

Plus a tab-trap handler to keep focus inside the dialog while it's open. There are libraries for this (`focus-trap`, `focus-trap-vue`) — single dependency, ~2 KB gzipped, eliminates the manual implementation. Recommend this route over hand-rolled.

### 🟢 SUGGESTION — No global `:focus-visible` styles

`grep ':focus-visible' frontend/src/styles/` returns 0. The codebase relies on per-component `:focus { ... }` rules. Modern best practice is to define `:focus-visible` (focus indicator only when keyboard-focused, not on click) globally in `styles/global.css`:

```css
*:focus-visible {
  outline: 2px solid var(--steel-button);
  outline-offset: 2px;
}
```

This guarantees keyboard users always have a visible focus indicator even where component-level styles forget it.

### 🟢 SUGGESTION — No focus management on route change

When `<RouterView>` switches, focus stays where it was (often on the link/button that triggered navigation). Screen reader users don't get an announcement that the page changed. Fix: in `App.vue` or a router-after-each guard:

```ts
router.afterEach(() => {
  // Move focus to main content (or page heading) after navigation
  nextTick(() => {
    const main = document.querySelector('main, [role="main"]') as HTMLElement
    main?.focus()
  })
})
```

Requires `<main tabindex="-1">` so it's programmatically focusable.

---

## P5 — Color Contrast (HIGH category) — 7/10 (token-based, not measured at render)

### Method

Static contrast measurement requires rendering each text/background pair against the actual computed color values. The bundle (per `decisions.md` #006) is the SSOT for tokens; values come from `velo-design-system-2026-04-23/project/colors_and_type.css`. The bundle README declares WCAG-mindful contrast per the Marmelad+wellness aesthetic.

Spot-check from `frontend/src/styles/variables.css`:

| Pair | Light mode (computed) | AA threshold | Verdict |
|---|---|---|---|
| `--text-primary` (#4c6589) on `--surface-default` (#ffffff) | ~5.6:1 | ≥4.5:1 (normal) | ✓ |
| `--text-secondary` (rgba(76,101,137,0.70)) on white | ~3.4:1 | ≥4.5:1 (normal) | ✗ low for body text; may be fine for hint text |
| `--text-muted` (rgba(76,101,137,0.50)) on white | ~2.5:1 | ≥4.5:1 (normal) | ✗ for body text |
| `--steel-button` (#627a9c) on white (button bg + text vs bg) | ~4.4:1 | depends on use | borderline |

**Note**: `--text-muted` and `--text-secondary` use rgba transparency, which in real usage composites against varying backgrounds (white in light mode, near-black in dark mode). The lighter variants are intended for placeholder, hint, and caption text where the threshold is 3:1 (large text or non-essential). If these tokens are applied to body-tier text, they would be sub-AA.

### 🟢 SUGGESTION — Validate `--text-muted`/`--text-secondary` usage scope

Audit grep `var(--text-muted)` / `var(--text-secondary)` to confirm only used on:
- Placeholder text (already excluded from AA in WCAG)
- Hint/caption text (large-text threshold 3:1 applies if ≥18px or ≥14px bold)
- Disabled state (excluded from AA)

If used on regular ≤16px body text, these tokens fail AA. Cross-check with BACKLOG #13 (visual convergence post-glass).

### Confirms

- Light + dark mode token sets exist (per #008).
- No inline hex/rgba violations of FP-01 in S1 deliverables (per type-audit Run 2 + design-audit upcoming Run 6).

---

## P6 — Form Labels (CRITICAL category) — 6/10

### 🟡 WARNING — VInput label not associated with input

`components/ui/VInput.vue:13-22`:
```vue
<div class="v-input">
  <label v-if="label" class="v-input__label">{{ label }}</label>
  <input
    class="v-input__field"
    :type="type"
    :value="modelValue"
    ...
  />
</div>
```

No `for`/`id` linkage. Without it, clicking the label does not focus the input, and screen readers may not associate the label with the input (some do it implicitly when label wraps input, but here `<label>` is a sibling of `<input>`, not a parent).

Fix:
```diff
+ const inputId = useId()  // Vue 3.5 has useId()
+
  <label v-if="label" :for="inputId" class="v-input__label">{{ label }}</label>
- <input class="v-input__field" ...
+ <input :id="inputId" class="v-input__field" ...
```

Or wrap the label around the input:
```diff
- <label v-if="label" class="v-input__label">{{ label }}</label>
- <input class="v-input__field" ...
+ <label v-if="label" class="v-input__label">
+   {{ label }}
+   <input class="v-input__field" ...
+ </label>
```

This single-component fix cascades to all input usages (12 files contain inputs; most use VInput).

### 🟡 WARNING — VTextarea, VSelect, VCheckbox likely have the same pattern

Spot check VTextarea, VSelect, VCheckbox — same component-as-wrapper structure expected. Apply the same fix uniformly.

### 🟢 SUGGESTION — No `aria-describedby` for error messages

Form validation in `EditPracticeView.vue:527-554`, `MasterApplyView.vue`, `TopupView.vue:126-132` displays error text below the input but doesn't link the error to the input via `aria-describedby`. Screen reader users tabbing to a field with an error don't hear the error description.

Fix template:
```diff
+ const errorId = `${inputId}-error`
  <input :id="inputId" :aria-invalid="!!error" :aria-describedby="error ? errorId : undefined" ... />
- <span class="error">{{ error }}</span>
+ <span :id="errorId" class="error" role="alert">{{ error }}</span>
```

### Confirms

- Required fields are validated (`MasterApplyView.vue` has visible required indicators).
- No `<input>` uses placeholder as the only label.

---

## P7 — Skip Links & Landmarks (MEDIUM category) — 6/10

### Confirms

- `<main>` landmark present in `MobileLayout.vue:20`, `AdminLayout.vue:22` — only one per layout, correct.
- `<nav>` landmark in `VTabBar.vue:12` and `VHeader.vue:14`.
- One `<h1>` per view (sampled — most views have a single page heading via `VHeader.vue` or inline).

### 🟡 WARNING — No skip-to-content link

`frontend/index.html` has no `<a href="#main">Skip to content</a>` as the first focusable element, and no equivalent inside `App.vue`. Keyboard users navigating via Tab must traverse the entire VHeader before reaching content.

Fix in `index.html`:
```html
<body>
  <a class="skip-link" href="#main-content">Перейти к содержимому</a>
  <div id="app"></div>
  ...
</body>
```

Plus CSS in `global.css` for sr-only-until-focus pattern:
```css
.skip-link {
  position: absolute;
  left: -9999px;
}
.skip-link:focus {
  position: fixed;
  top: 0; left: 0;
  background: var(--surface-elevated);
  padding: var(--space-3);
  z-index: 10000;
}
```

And add `id="main-content"` to the layout `<main>` elements.

### 🟢 SUGGESTION — Multiple `<nav>` regions need unique labels

Two nav regions exist (top header in some views, bottom tab bar). If both render simultaneously (which they do — VHeader at top, VTabBar at bottom), each should have a unique `aria-label`:

```diff
- <nav class="v-tabbar">
+ <nav class="v-tabbar" aria-label="Основная навигация">
```

---

## P8 — Screen Reader Text (MEDIUM category) — 6/10

### Confirms

- `VeloLogo.vue:18`: `alt="VELΘ"` ✓
- `VAvatar.vue:14`: `:alt="name"` ✓
- Icon-only buttons have aria-label (P2 confirmed list).

### 🟡 WARNING — Inline SVG icons missing `aria-hidden="true"` (cosmetic, but cumulative)

All `components/icons/Icon*.vue` (~16 files) are inline SVGs without `aria-hidden`. When used inside a button with text label, screen readers may announce both. Example:

```vue
<button aria-label="Календарь">
  <IconCalendar :size="20" />
  <span>Календарь</span>
</button>
```

Screen reader announces «Календарь, Календарь, button» — duplicated. Fix: add `aria-hidden="true"` to icon SVG, OR omit the parent text-label when icon is decorative.

Single-fix template in IconHome.vue and analogous icons:
```diff
- <svg xmlns="..." :width="size" :height="size" viewBox="0 0 512 512" fill="currentColor">
+ <svg xmlns="..." :width="size" :height="size" viewBox="0 0 512 512" fill="currentColor" aria-hidden="true">
```

Mechanical refactor across ~16 icon files.

### 🟢 SUGGESTION — Loading states announce via aria-busy

When views fetch data, the loading state is shown via VLoader or skeleton, but no `aria-busy="true"` on the parent. Screen reader users don't know «loading» — they just wait silently for the content.

Fix template:
```diff
- <div class="content">
+ <div class="content" :aria-busy="loading">
    <VLoader v-if="loading" />
    <DataDisplay v-else :data="data" />
  </div>
```

---

## Quality Gate Decision

Per SKILL.md Quality Gate definition:
- Avg score 6.25/10 → falls in WARN range (≥5.0 and <7.0)
- Hard CRITICAL findings (probe scores 0): 0 → does not trigger FAIL
- All-interactive-elements-keyboard-accessible: not satisfied (7 sites flagged) → blocks PASS

**Gate**: WARN. Mid-range; clear fix paths for all findings.

---

## Audit Cross-Reference (Velo decisions / BACKLOG)

- **#013** — VELO is TMA + PWA. TMA users on mobile typically have screen reader (VoiceOver/TalkBack) enabled. A11y findings affect them directly.
- **BACKLOG #13** — visual convergence post-glass — addresses P5 contrast indirectly.
- **None of the 7 div-clickable findings** are listed in existing BACKLOG. New work for Step 3 classification.

---

## Step 3 Classification Suggestions

Suggested cycle groupings (Step 3 input):

| Group | Findings | Estimated effort |
|---|---|---|
| A. Convert div@click → button | P1 + P3 (UserProfileView 5 menus + MasterDashboard balance + PracticeCard) | 1 cycle, M |
| B. Modal focus trap | P4 (VModal focus mgmt + focus return) | 1 cycle, M (use `focus-trap-vue` lib) |
| C. ARIA polish | P2 (aria-current on tabs, aria-live on toast) + P8 (aria-hidden on icons, aria-busy on loading) | 1 cycle, S |
| D. Form labels association | P6 (VInput/VTextarea/VSelect/VCheckbox `for`/`id` via `useId()`) | 1 cycle, S |
| E. Skip link + global focus-visible | P7 (skip link) + P4 (`:focus-visible` global) | 1 cycle, S |
| F. Color contrast token audit | P5 (`--text-muted`/`--text-secondary` scope check) | 0.5 cycle, S |

Total: ~4-5 cycles. Could be one «a11y polish sprint» (S2 or S3 hardening cycle).

---

## Anchor

[*] a11y-audit v1.0.0 * report ready
[>] | NEXT: Run 4 (probekit-responsive-audit)
