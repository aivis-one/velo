# Mockups — Index

Last updated: 2026-05-19

> Template per VELO-METHODOLOGY.md §12.6. Updated **immediately** after
> any mockup file is added or its status changes (§12.2).

Status legend:
- ✅ approved — operator visually approved, MOCKUP GATE passed (§10.4)
- 🔄 in revision — submitted, awaiting operator review or being revised
- 🔧 work in progress — being actively built/iterated, not yet ready for review
- ⬜ pending — planned, not yet built
- ⛔ blocked — blocked on token gap, API gap, or design decision
- 🗑 superseded — replaced by a newer artifact, kept for reference until next sprint closure

---

## User block

| File | Status | Approved on | Notes |
|---|---|---|---|
| `user/_onboarding-flow.html` | ✅ **MOCKUP GATE passed 2026-05-18** | 2026-05-18 | Combined viewer: 8 columns Onboarding flow (welcome / login / register / oauth / onb-1..4). Все колонки approved оператором. DS canon promoted (typography h1+body tokens, button/input heights, stack gaps, glass canon, halo composition). Real Figma SVG icons (`icon-onb-*.svg`) extracted via Plugin API. |
| `user/_dashboard-flow.html` | 🔧 **work in progress — DS-compliant 2026-05-19** | — | Combined viewer: 9 columns Dashboard block. **Full rebuild + DS compliance pass 2026-05-19.** `_shared/` CSS architecture (AP-M-6). z-index stacking bug fixed globally. All emoji removed (0). 3 new DS icons extracted from Figma. 19/19 icon refs resolved. 70/70 structural checks. Three new shared components in `_shared/components.css`. **Bottom Nav pass 2026-05-19:** `class="bottom-nav"` → `class="bottom-nav bottom-nav--user"` (2 instances, DS-first §7.0). Awaiting operator MOCKUP GATE. |
| `user/_calendar-flow.html` | 🔧 **work in progress — built 2026-05-19** | — | Combined viewer: 11 columns Calendar 11 block (Macro-Phase II Priority 2). 8/11 screens with PNG etalons. 3 TBD overlays: col 03 `23_Calendar 2` (541:1744, no PNG deferred), col 07 `27_Ask Master` (541:2156, no PNG deferred), col 11 `31_Message` widget (541:6514, 350×293 non-standard). 0 emoji, 0 missing icons, div balance 231/231. New components: CalendarWeekStrip, FilterPanel, PracticeDetailCard, FeedbackRating, MasterProfileHero (all ⬜ candidate). **Bottom Nav pass 2026-05-19:** `class="bottom-nav"` → `class="bottom-nav bottom-nav--user"` (2 instances, DS-first §7.0). Awaiting operator MOCKUP GATE. |

Planning target (per ROADMAP §6.1, §7.1): ~20-25 screens.

### Sprint 2 Phase 4 batch — Onboarding (8) + Dashboard (9)

**Onboarding combined viewer**: `user/_onboarding-flow.html` — 8 колонок с парным сравнением. Минимальный тулбар (только device switcher + screen name). Frames 1:1, no phone chrome.

**Per-column HTML status — ALL ✅ approved 2026-05-18:**
1. ✅ `01 — welcome` — operator approved
2. ✅ `02 — login` — operator approved
3. ✅ `03 — register` — operator approved
4. ✅ `04 — oauth` — operator approved
5. ✅ `05 — onboarding-1 (find practice)` — operator approved
6. ✅ `06 — onboarding-2 (diary)` — operator approved
7. ✅ `07 — onboarding-3 (chat with masters)` — operator approved
8. ✅ `08 — onboarding-4 (timezone)` — operator approved

✅ **Onboarding block CLOSED 2026-05-18.** Dashboard 9 viewer rebuilt 2026-05-19 — awaiting MOCKUP GATE.

**Dashboard combined viewer — per-column HTML status (all 🔧 built 2026-05-19, awaiting MOCKUP GATE):**
1. 🔧 `01 — dashboard-1` — greeting + 2 alert-pills + practice-card + action-row + stats-row + AI tabs + blurred ai-card + bottom-nav (home active)
2. 🔧 `02 — dashboard-2` — expanded ai-card + energy-row 😩→😊 + Подробнее link + bottom-nav (home active)
3. 🔧 `03 — check-in` — top-header + practice-info (centered) + mood-widget (3 picks, center active) + mw-slider + v-textarea + primary CTA + skip link
4. 🔧 `04 — checkin-success` — pure white bg + icon-checkin-success.svg (80px) + title + sub + buttons (no mandala bg)
5. 🔧 `05 — practice-live` — video-block + practice-info + v-badge--live + Войти primary + Check-in glass + Покинуть destructive
6. 🔧 `06 — booked-practice` — top-header + practice-info + paid-badge + 2 list-rows + master-card + warning-alert + Check-in primary + Отменить destructive
7. 🔧 `07 — ai-summary` — top-header + info-pill (Саммари недели) + summary-body + energy-row + 2 recommendation-cards
8. 🔧 `08 — my-reservations` — top-header + 3 booking-cards (warning/success/error v-badge variants)
9. 🔧 `09 — booking-detail` — top-header + practice-info + detail-row (Статус + v-badge--success) + master-card + ZOOM section + info-pill + Отменить destructive

**DS components promoted from Onboarding** (codified в variables.css 2026-05-18):
- Layer 2 tokens: `--velo-button-height` (52), `--velo-input-height` (42), `--velo-stack-gap-buttons` (16), `--velo-stack-gap-forms` (10), `--velo-typo-h1-{size,line,spacing,color}` (30/36/1.2/steel-light), `--velo-typo-body-{size,line,color}` (18/24/steel-light), `--velo-glass-fill` (10% blue), `--velo-shadow-button` (drop-on-top composition).
- Text aliases re-aliased to steel-light: `--velo-text-primary/secondary/link`.
- DS-assets (vector from Figma): `velo-logo-mandala.svg` (white hero), `velo-logo-mandala-blue.svg` (Group 1925 compact with VELO), `icon-back-arrow.svg`, `icon-onb-{practice,diary,chat}.svg`. PNG versions deprecated.
- DS-asset (raster): `velo-bg-app.png` (universal background — composite RECTANGLE fill, stays raster).

**Glass-component canon (two-layer pattern):**
- `.v-element { background: transparent; isolation: isolate; box-shadow: var(--velo-shadow-button); }`
- `::before { z-index: -2; border: 1px solid #fff; inset: -1px }` (white outline layer)
- `::after { z-index: -1; background: var(--velo-glass-fill); inset: -1px }` (plashka fill ON TOP of border)
- Applied to: v-button glass/ghost/oauth + velo-back-arrow.

## Master block

| Screen file | Status | Approved on | Notes |
|---|---|---|---|
| (none yet) | — | — | — |

Planning target: ~20-25 screens.

## Admin block

| Screen file | Status | Approved on | Notes |
|---|---|---|---|
| (none yet) | — | — | — |

Planning target: ~15-20 screens.

## Shared block (auth, error, modal templates)

| Screen file | Status | Approved on | Notes |
|---|---|---|---|
| (none yet) | — | — | — |

Note: shared screens live under their primary role folder unless they are
truly cross-role; in that case place them under whichever role is most
natural and reference from elsewhere.

---

## Shared CSS infrastructure

All mockup HTML files link to three shared CSS layers in `_shared/`:

| File | Contents |
|---|---|
| `_shared/tokens.css` | Full `:root {}` mirror of `02_design-system/tokens/variables.css` + `@font-face` (Marmelad) + shell-chrome tokens (`--shell-*`). **Sync rule**: update whenever `variables.css` changes. |
| `_shared/shell.css` | Viewer chrome: `.frame`, `.topbar`, `.workspace`, `.column`, `.row-label`, `.tbd-overlay`, t