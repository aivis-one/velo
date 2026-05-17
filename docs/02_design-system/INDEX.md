# VELO Design System — Index

Last updated: 2026-05-17
Iteration: 3 (Sprint 1 closed + Sprint 2 Phase 3 closed + Phase 4 in progress)
Status: **TOKENS GATE ✅ passed · INVENTORY GATE ✅ passed · STYLEGUIDE GATE ✅ passed**

> Template per VELO-METHODOLOGY.md §12.4. This file is the local catalog
> of the design system. It is updated **immediately** after any DS change
> per §12.2.

---

## Token Status

| Group | Tokens defined | Source | Missing |
|---|---|---|---|
| Colors / Primitives | 36 | 12 figma.variables + 24 promoted from 17-screen mining | — |
| Text semantic | 5 | mapping to steel/neutral primitives | — |
| Background semantic | 4 (screen, input, card, card-subtle) | mapping to white + alpha-steel-light-15 | — |
| Buttons (bg) | 2 (primary, glass) | mapping to steel-light + alpha-white-66 | — |
| Borders | 3 (default, input, button) | mapping to neutral-300 + white | — |
| Icons | 1 (default) | mapping to steel-primary | — |
| Dots | 2 (active, passive) | mapping to steel-primary + alpha-steel-60 | — |
| States — Success | 4 (state, text, bg-soft, bg-tint) | teal family from Dashboard mining | — |
| States — Warning | 4 (state, text, bg-soft, bg-tint) | orange family | — |
| States — Error/Destructive | 4 (state, destructive, text, bg-soft) | coral family | — |
| States — Info | 2 (bg-soft + state) | blue-50 + state-info `#619cd2` (resolved via full mining) | — |
| Interactive | 5 placeholders | neutral defaults | placeholders (no hover/active observed in SACRED) |
| Spacing | 14 (0..25) | DSYS-era 4-base scale (provisional) | — |
| Radius | 5 (xs, sm, md, lg, pill) | promoted from full mining | radius-full (not observed) |
| Shadows | 2 glow + 2 blur + card + modal | card/modal added Sprint 2 Phase 3 cleanup with neutral defaults | — |
| Font family | 1 (Marmelad Regular) | figma.textStyles | — |
| Font sizes | 7 (12/14/15/16/18/20/32) | text styles + new 15px from Dashboard | — |
| Weights | 1 (regular 400) | only one observed | — |
| Text styles (utility classes) | 6 (.velo-typo-*) | 1:1 from figma.textStyles with pixel lineHeights | — |

---

## Component Status

Components visualised in `styleguide/velo-design-system.html` (Sprint 2 Phase 3 ✅).

| Component | Tier | Status in styleguide | Vue file (Sprint 3+) |
|---|---|---|---|
| VButton (primary / glass / oauth / destructive) | 1 | ✅ visualised | ⬜ |
| VInput | 1 | ✅ visualised | ⬜ |
| VCheckbox | 1 | ✅ visualised | ⬜ |
| VBadge (success/warning/error/info/neutral) | 1 | ✅ visualised | ⬜ |
| VAvatar (sm/md/lg, initials-based) | 1 | ✅ visualised | ⬜ |
| VLoader | 1 | ✅ visualised | ⬜ |
| VToast (success/warning/error/info) | 1 | ✅ visualised | ⬜ |
| PracticeCard | 2 | ✅ visualised | ⬜ |
| BookingCard | 2 | ✅ visualised | ⬜ |
| WaitlistCard | 2 | ✅ visualised | ⬜ |
| PriceDisplay | 2 | ✅ visualised | ⬜ |
| BalanceChip | 2 | ✅ visualised | ⬜ |
| MasterStatusBadge | 2 | ✅ visualised | ⬜ |
| FeedbackWidget | 2 | ✅ visualised | ⬜ |
| MoodWidget | 2 | ✅ visualised | ⬜ |

**New components surfaced during Phase 4 (Onboarding mining)** — awaiting promotion to styleguide after Onboarding block MOCKUP GATE:
`v-input` (pill-shape with blur), `v-back-arrow`, `v-link`, `v-divider` («или» line), `v-dots` (carousel pagination), `v-button--oauth` (Google/Apple), `v-button--glass` (new canon: white outline + halo + 5% blue bg), `velo-header-compact` (mini-mandala + wordmark), `velo-bg-mandala` (full-screen watermark), `velo-skip` (top-right link), illustration slot.

---

## Asset Index

See `assets/ASSETS-INDEX.md` for the full asset list with source node IDs.

- Icons: 2 PNG (`icon-back-arrow.png`, `icon-mandala.png`) + 1 SVG (`velo-logo-mandala.svg` — Group 1944)
- Backgrounds: 1 PNG (`velo-bg-app.png` — universal app background, from Figma 01_Welcome)
- Fonts: 1 TTF (`Marmelad-Regular.ttf` — self-hosted, OFL)
- Screenshots: 94 of 97 SACRED PNG (user 55 + master 39) + 1 admin legacy HTML reference

---

## Open TODOs

- [x] Sprint 1 Phase 1 — 97 of 97 SACRED screens mined (full extension complete 2026-05-17).
- [x] Sprint 1 Phase 2 — `variables.css` + `global.css` (master + deliverable, MD5-identical).
- [x] **TOKENS GATE (§10.2)** — passed by operator via `tokens-preview.html` visual validation.
- [x] **INVENTORY GATE (§10.1)** — passed. 94 PNG + 2 DS icons + 1 legacy admin HTML in place.
- [x] Operator decision on `--velo-shadow-card` / `--velo-shadow-modal` — added with real values during Sprint 2 Phase 3 cleanup.
- [x] Sprint 2 Phase 3 Styleguide HTML — closed. STYLEGUIDE GATE ✅ passed.
- [ ] Operator decision on 15px font size — still open; emitted as inline `font-size: var(--velo-size-15)` for now.
- [ ] **Sprint 2 Phase 4 (in progress)** — promotion of new Onboarding-mining components (`v-button--glass`, `v-input` pill+blur, `v-back-arrow`, `v-link`, `v-divider`, `v-dots`, `velo-header-compact`, etc.) into `styleguide/velo-design-system.html` + `tokens/variables.css`. Trigger: after Onboarding block MOCKUP GATE passes.
- [ ] Dark theme — deferred per VELO-METHODOLOGY §2.5 I7. Figma already has Dark mode primitives.

### Architectural finding for Sprint 7
- Admin role has **no Figma SACRED**. Visual design built from scratch using DS tokens + logic from `assets/screenshots/admin/admin-legacy-reference-v2.5.html`.

---

## Iteration Log

| Iteration | Date | What was done |
|---|---|---|
| 0 | 2026-05-17 | Folder structure created per VELO-METHODOLOGY §3. No extraction yet. |
| 1 | 2026-05-17 | Sprint 1 Phase 1 + Phase 2 draft. Live Figma probe via use_figma Plugin API → 12 figma.variables (8 primitives Light+Dark + 4 semantic aliases) + 6 figma.textStyles. Mockup-mining over 17 SACRED screens (Onboarding 8 + Dashboard 9) → 24 promoted primitives. `variables.css` 213 lines + `global.css` 103 lines drafted in master + sync'd to deliverable. Inventory `VELO-DS-INVENTORY.md` with Section A/B/C complete + provenance. |
| 2 | 2026-05-17 | Sprint 1 closure. TOKENS GATE ✅ + INVENTORY GATE ✅ passed. Full mining extension over remaining 80 SACRED screens (97 of 97 complete). New promoted primitives: state-info, radius-md, disabled-bg/text resolved, steel-pale, coral-darker, alpha-white-70/50/25, radius-xs, blur-glass-stronger. variables.css condensed to 169 lines. 94 PNG screenshots saved (operator UI export, role-organized). |
| 3 | 2026-05-17 | Sprint 2 Phase 3 closed — single production styleguide `velo-design-system.html` (Marmelad self-host via base64, 32 SVG icons in 5 categories, real card/modal shadow tokens added, glass shadows + pattern grid fix). STYLEGUIDE GATE ✅ passed. Sprint 2 Phase 4 started — Onboarding flow viewer with 8 columns (welcome at 80%, 5 pending fixes). 2 new DS assets: `velo-bg-app.png` (universal app background) + `velo-logo-mandala.svg` (Group 1944 brand logo). |

---

## References

- Methodology: `../04_methodology/VELO-METHODOLOGY.md`
- Roadmap: `../05_roadmap/ROADMAP.md`
- Top-level: `../INDEX.md`
