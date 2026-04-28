# responsive-audit — frontend/src — 2026-04-28

**Skill**: probekit-responsive-audit v1.0.0
**Target**: `frontend/src` + `frontend/index.html`
**Device target**: phone-first (TMA primary surface) with PWA fallback for tablet/desktop browser
**Scope**: 100dvh layouts, safe-area, touch targets, sticky headers, breakpoint usage

---

## Summary

| Probe | Severity | Verdict | Score |
|---|---|---|---|
| P1 — Viewport Meta | CRITICAL | partial | 7/10 |
| P2 — Safe Area | HIGH | partial | 6/10 |
| P3 — Touch Target Size | HIGH | WARN | 5/10 |
| P4 — Flex/Grid Layout | MEDIUM | clean | 9/10 |
| P5 — Sticky vs Fixed | HIGH | 💎 clean | 10/10 |
| P6 — RTL Layout | MEDIUM | n/a — out of scope | n/a |
| P7 — Breakpoint Consistency | MEDIUM | clean (single bp) | 8/10 |
| P8 — `dvh` Units | LOW | 💎 clean | 10/10 |
| **Average** (excl. n/a) | | | **7.86/10** |

**Findings**: 0 🔴 / 3 🟡 / 4 🟢 / 2 💎.

**Headline**: responsive layout is solid (mobile-first architecture matches TMA target; `100dvh` adopted with `100vh` fallback; sticky headers/tabs; safe-area-inset on tab bar). Three improvement areas: touch-target compliance (small buttons below 44px), missing `safe-area-inset-top` on header, viewport meta omits `viewport-fit=cover`.

---

## P1 — Viewport Meta (CRITICAL) — 7/10

`frontend/index.html:5`:
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=3.0, user-scalable=yes" />
```

### Confirms

- `width=device-width` ✓
- `initial-scale=1.0` ✓
- `user-scalable=yes` ✓ (zoom allowed — accessibility-friendly)
- `maximum-scale=3.0` ✓ (does not lock zoom; 3x is permissive)

### 🟡 WARNING — `viewport-fit=cover` missing

Without `viewport-fit=cover`, iOS notched devices (iPhone X+) won't extend content edge-to-edge through the safe area, and `env(safe-area-inset-*)` returns 0 in some Safari rendering paths. The tab bar's `safe-area-inset-bottom` usage at `VTabBar.vue:59` partially mitigates, but the meta tag should be complete.

```diff
- <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=3.0, user-scalable=yes" />
+ <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=3.0, user-scalable=yes, viewport-fit=cover" />
```

Single-line fix.

---

## P2 — Safe Area (HIGH) — 6/10

### Confirms

- `safe-area-inset-bottom` correctly applied at `components/layout/VTabBar.vue:59`:
  ```css
  padding-bottom: calc(var(--space-2) + env(safe-area-inset-bottom, 0px));
  ```
  Bottom tab bar accounts for home-indicator on iPhone X+. ✓

### 🟡 WARNING — `safe-area-inset-top` not applied to VHeader

`components/layout/VHeader.vue:51` uses `position: sticky` with no `padding-top: env(safe-area-inset-top)`. On iPhone notched devices in fullscreen TMA mode (which is the primary surface per #013), the header content can be obscured by the notch.

Fix:
```diff
  .v-header {
    position: sticky;
    top: 0;
    ...
+   padding-top: calc(var(--space-3) + env(safe-area-inset-top, 0px));
  }
```

### 🟢 SUGGESTION — Body-level safe-area not used

`styles/global.css` has no body-level `padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)`. Pure-fullscreen views (LoadingView, WelcomeView, StandaloneStubView) rely on `min-height: 100dvh` but don't account for inset padding. Edge-case: their content (mandala backdrop, central VELΘ wordmark) is centered so it's unlikely to be obscured, but a generic body-level inset would harden against future fullscreen views.

---

## P3 — Touch Target Size (HIGH) — 5/10

### 🟡 WARNING — `size="sm"` button height = 36px (below WCAG 44×44)

`components/ui/VButton.vue:88-92`:
```css
.v-btn--sm {
  padding: 8px 16px;
  font-size: var(--text-xs);
  min-height: 36px;     /* ← below WCAG 2.5.5 minimum of 44px */
}
```

`min-height: 36px` is below WCAG 2.5.5 «Target Size (Enhanced)» 44×44 px requirement.

**Affected sites**: 30 usages across 20 files (`grep size="sm"`):
```
UserProfileView, MasterDashboard, MasterPracticesView, MasterFinanceView,
MasterProfileView, MasterPendingView, MasterApplyView, EditPracticeView,
AttendanceView, AnalyticsView, AdminConsistencyView, BookingPopup,
DiaryEntryForm, DiaryList, MyBookingsView, CalendarView, PracticeDetailView,
TopupSuccessView, UserDashboardView, VEmptyState
```

**Fix options**:
1. Bump `min-height: 36px` → `44px` (compatible — pads spaces tighter where rendered).
2. Keep visual height 36px but expand the **clickable** area via `padding` and `::before` pseudo-element (preserves visual design while meeting touch target).

Option 2 sketch:
```css
.v-btn--sm {
  position: relative;
  padding: 8px 16px;
  min-height: 36px;     /* visual height kept */
}
.v-btn--sm::before {
  content: '';
  position: absolute;
  inset: -4px 0;        /* extends 4px above + below = 36+8 = 44 */
}
```

Recommend option 1 (simpler; visual delta is +8px in vertical direction, usually swallowed by surrounding spacing in mobile contexts).

### 🟢 SUGGESTION — VTabBar item height borderline

`components/layout/VTabBar.vue:63-75` — tab-bar items have no explicit `min-height`. Computed height = icon (20px) + label (~14px) + 2 × `var(--space-1)` (≈8px) = ~42px. Below 44px by a small margin. Cumulative effect with safe-area inset bumps the actual tap zone above 44, but the explicit visual height is below threshold.

Recommended: add `min-height: 48px` to `.v-tabbar__item`.

### 🟢 SUGGESTION — VInput height 40px (below 44 for non-inline use)

`components/ui/VInput.vue:62-72`:
```css
.v-input__field {
  width: 100%;
  height: 40px;        /* below 44 */
  ...
}
```

Same in `VTextarea`, `VSelect`. WCAG 2.5.5 has an «inline» exception for inputs in flowing text, which arguably applies to form inputs in a stacked form layout. Conservative reading recommends 44 for explicit form inputs.

---

## P4 — Flex/Grid Layout (MEDIUM) — 9/10

### Confirms

- Layouts use flex column architecture (`MobileLayout.vue`, `AdminLayout.vue` — `display: flex; flex-direction: column`).
- Content area uses `overflow-y: auto` patterns (verified in shells).
- No fixed-width media that would break <390px viewports.
- Grid usage is sparse (a few cards and stat layouts) — no auto-fit/auto-fill needed at current scale.

No findings.

---

## P5 — Sticky vs Fixed (HIGH) — 10/10 💎

### 💎 DIAMOND — Sticky pattern correctly applied

`components/layout/VHeader.vue:51` — `position: sticky` ✓
`components/layout/VTabBar.vue:52` — `position: sticky` ✓

`position: fixed` usages confirmed only on overlay/floating surfaces (acceptable per probe definition):
- `VModal.vue:95` — overlay
- `VToast.vue:44` — toast container
- `DiaryList.vue:406` — FAB
- `AttendanceView.vue:504`, `EditPracticeView.vue:902` — custom confirm-dialog overlays (note: could reuse VModal, but functionality-correct)
- `global.css:106` — `#app::before` background image layer

No findings — all `position: fixed` usages are on overlay-tier elements.

---

## P6 — RTL Layout (MEDIUM) — n/a

Velo does not yet support RTL. Per BACKLOG #38, i18n infrastructure is deferred until a future sprint. The Russian-only locale (per bundle README) does not require RTL.

When i18n lands and Arabic is added (currently `--velo-mood-*` and other tokens have no RTL-specific treatment), repeat this probe. Today: **n/a**.

---

## P7 — Breakpoint Consistency (MEDIUM) — 8/10

### Confirms

`grep '@media'` in `frontend/src` returns exactly **1** site:

`components/ui/VModal.vue:166`:
```css
@media (min-width: 640px) {
  .v-modal__overlay { align-items: center; }
  ...
}
```

Velo is mobile-first (TMA + PWA fallback per #013); no tablet/desktop-specific layouts beyond this VModal switch from bottom-sheet to centered dialog. Single breakpoint is intentional architecture, not a bug.

### 🟢 SUGGESTION — Document the breakpoint convention

The `640px` threshold isn't formally documented anywhere in `decisions.md` or `ARCHITECTURE.md`. If future sprints introduce more responsive elements, having a documented breakpoint set (`--bp-mobile: 480px`, `--bp-tablet: 1024px`, etc.) prevents drift. Single-cycle doc-touch.

---

## P8 — `dvh` Units (LOW) — 10/10 💎

### 💎 DIAMOND — Correct progressive enhancement pattern

Pattern observed at 14 sites (every full-height view):
```css
min-height: 100vh;     /* fallback for older browsers */
min-height: 100dvh;    /* override on modern browsers */
```

Files using this pattern (sample):
- `MobileLayout.vue:48-49`, `AdminLayout.vue:50-51` (layout shells)
- All `views/auth/*` (LoadingView, WelcomeView, StandaloneStubView, LoadingErrorView)
- `MasterPendingView.vue`, `MasterApplyView.vue`
- All admin views (AdminDashboardView, AdminMasterReviewView, AdminConsistencyView, AdminMastersView, AdminReportDetailView, AdminReportsView)
- `NotFoundView.vue`, `HomeView.vue`

This is the canonical pattern for handling iOS Safari's URL-bar collapse behavior — `100vh` overflows when the URL bar is visible, `100dvh` correctly tracks dynamic viewport height. Velo applies it universally and with the proper fallback ordering. 💎 DIAMOND.

---

## Cross-Reference

- **#007** flat aesthetic (no backdrop-filter) — does not impact responsive behavior.
- **#013** VELO is TMA + PWA — mobile-first design is correct architecture.
- **BACKLOG #13** visual convergence post-glass — adjacent concern.
- **BACKLOG #38** i18n deferred — invalidates P6 RTL probe for now.

---

## Step 3 Classification Suggestions

| Group | Findings | Effort |
|---|---|---|
| A. Viewport meta + safe-area-top | P1 (`viewport-fit=cover`) + P2 (header inset) | 1 cycle, S |
| B. Touch target compliance | P3 (VButton sm 36→44, VTabBar item, VInput 40→44) | 1 cycle, M |
| C. Breakpoint convention doc | P7 (`decisions.md` entry + token in variables.css) | 0.5 cycle, S |

Total: ~2 cycles. Could land as a single «mobile-polish» cycle (S2 hardening).

---

## Anchor

[*] responsive-audit v1.0.0 * report ready
[>] | NEXT: Run 5 (probekit-security-audit)
