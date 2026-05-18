# Mockups — Index

Last updated: 2026-05-18

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
| `user/_dashboard-flow.html` | 🗑 **superseded 2026-05-18** | — | Combined viewer: 9 columns Dashboard block. Built in Sprint 2 Phase 4 via PNG reverse-engineering — incurred 3× rework on alert pills + glass halo + bottom-nav. Per Sprint 2.5 plan, **the viewer is rebuilt ground-up after Dashboard 9 DS-complete state** (Track A T2.5.1 → T2.5.2). File kept until that pass completes for reference; do not use as canon. Custom-named classes (info-pill, warning-alert, master-card, list-row, video-block, energy-pair, recommendation-card) — будут validated против harvested Figma values во время T2.5.1. |

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

✅ **Onboarding block CLOSED 2026-05-18.** Next: **Dashboard 9** (separate viewer).

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

## Summary

- Mockup files: 1 (combined viewer — superseded welcome.html cleaned up 2026-05-18)
- **Approved (MOCKUP GATE passed): 8 columns** — full Onboarding flow ✅ 2026-05-18
- Combined viewer columns pending: 0 (Onboarding complete)
- Dashboard block (9 columns / separate viewer): **next focus** — Sprint 2 Phase 4 continuation. DS canon ready, можно сразу строить на готовых tokens.

---

## References

- Methodology: `../04_methodology/VELO-METHODOLOGY.md` §7 (Mockup Layer) + §10.4 (MOCKUP GATE)
- Prompt template: §9.5
- Anti-patterns: §11.2
- Token bridge for mockups: §11.3
