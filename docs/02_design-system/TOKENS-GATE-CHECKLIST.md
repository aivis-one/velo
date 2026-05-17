# TOKENS GATE checklist — Sprint 1 Phase 2

```
Date prepared:  2026-05-17
Gate ref:       VELO-METHODOLOGY.md §10.2
Files to review:
  - 02_design-system/tokens/variables.css     (213 lines, master)
  - 02_design-system/tokens/global.css        (103 lines, master)
  - 01_deliverable/styles/variables.css       (MD5-identical copy)
  - 01_deliverable/styles/global.css          (MD5-identical copy)
Inventory:
  - 02_design-system/tokens/VELO-DS-INVENTORY.md  (Sections A/B/C)
```

> Open the four files side-by-side. The checklist below mirrors the
> formal §10.2 criteria plus 4 operator-decision points specific to this
> draft.

---

## Part 1 — Structural criteria (§10.2)

Check each — all should be ✅ before moving to Part 2:

### `variables.css`

- [ ] File contains ONLY `:root { ... }` blocks
- [ ] No `@import url(...)` (those go to `global.css`)
- [ ] No `* { box-sizing }` or `body { ... }` reset
- [ ] No `.velo-typo-*` utility classes
- [ ] No component-specific dimensions like `--velo-button-height` or `--velo-back-pill-width`
- [ ] No viewport constants like `--velo-screen-width: 402px`
- [ ] Zero occurrences of `var(--velo-…) + Npx` without `calc()` wrapper
- [ ] Every Layer 2 semantic token is defined as `var(--velo-color-...)` alias to Layer 1
- [ ] MISSING tokens explicitly marked with `/* MISSING: ... */` comment
- [ ] Layer 1 ordering: brand → neutral → alphas → states → spacing → radius → effects → font
- [ ] Layer 2 ordering: text → background → button → border → icon → dots → state-* → interactive

### `global.css`

- [ ] File contains: 1 `@import url(...)`, universal reset, 6 `.velo-typo-*` classes — and nothing else
- [ ] No `:root { ... }` block
- [ ] No `--velo-*` variable definitions
- [ ] Zero `line-height: normal` anywhere
- [ ] Zero `line-height: auto` anywhere
- [ ] Every `line-height` is a concrete pixel value (`32px`, `28px`, `22px`, `24px`, `20px`, `18px`)
- [ ] All `font-size`, `color`, `background` reference `var(--velo-*)` from variables.css
- [ ] No component-specific styles
- [ ] No hardcoded hex / px values for colors / sizes / spacing

### Sync

- [ ] `01_deliverable/styles/variables.css` MD5 matches `02_design-system/tokens/variables.css`
      (run `md5sum` if uncertain — checked at draft time 2026-05-17, both = `f1b51af6e9993f70fe9f744cfb2f462c`)
- [ ] `01_deliverable/styles/global.css` MD5 matches master
      (checked = `d3db31d19e3f76c96758e8b7cb0381d0`)

---

## Part 2 — Operator decisions (4 items pending input)

These four points need your call before TOKENS GATE can fully pass.

### D1 — `--velo-size-15` (15px font size)

**Found:** ~7 occurrences in Dashboard cards (Dashboard 1, 2, Check-in,
booked-practice, AI-summary, reservations, Booking-Detail).

**Issue:** 15px is NOT in `figma.getLocalTextStylesAsync()` — only 12,
14, 16, 18, 20, 32 are formal text styles. So 15px is either a missing
text style or an inline override.

**Options:**
- **(a)** Codify as standard size + add new `.velo-typo-body-15` utility
  class to `global.css` (requires Figma update too — add text style)
- **(b)** Treat as inline override; remove `--velo-size-15` from
  variables.css; replace any 15px in mockups with closest standard
  (14 or 16)
- **(c)** Keep `--velo-size-15` token but NO utility class (current
  draft state) — components use `var(--velo-size-15)` ad-hoc when needed

**Default if no input:** option (c).

### D2 — `--velo-shadow-card` / `--velo-shadow-modal` not observed

**Issue:** §6.3 lists shadow-card and shadow-modal as required. Across
17 SACRED screens, **no DROP_SHADOW with `offset.y > 0`** was observed.
The only shadows are `--velo-shadow-glow-white` (centered, no offset)
under buttons.

**Three possibilities:**
- VELO genuinely doesn't use card-elevation shadows (uses
  `--velo-bg-card-subtle` tint instead)
- Cards in not-yet-mined sections (Profile, Practices, etc.) use them
- Design oversight to fix

**Options:**
- **(a)** Skip these tokens for now; resume mining when needed
- **(b)** Add as neutral placeholder shadows
  (`0 2px 8px rgba(76,101,137,0.08)` derived from steel/primary)
- **(c)** Hold gate; mine remaining 6 sections to confirm

**Default if no input:** option (a) — skip, revisit at Sprint 2
styleguide.

### D3 — Interactive states (focus-ring, disabled, hover/active overlay)

**Issue:** Static Figma frames don't show interactive states (focus,
hover, active, disabled). All 5 interactive Layer 2 tokens are currently
**placeholders**:
- `--velo-focus-ring: rgba(76, 101, 137, 0.4)` (derived from
  steel/primary)
- `--velo-disabled-bg: var(--velo-color-neutral-200)`
- `--velo-disabled-text: var(--velo-color-alpha-steel-50)` (alias to
  text-muted)
- `--velo-hover-overlay: rgba(0, 0, 0, 0.04)` (industry-standard)
- `--velo-active-overlay: rgba(0, 0, 0, 0.08)` (industry-standard)

**Options:**
- **(a)** Accept placeholders as-is — refine when first interactive
  component is built in Sprint 2 mockups
- **(b)** Replace with different values now (specify)

**Default if no input:** option (a).

### D4 — Spacing scale verification

**Issue:** Spacing scale `--velo-space-0..25` (14 tokens, 4-base) is
**provisional** — copied from DSYS-era `_archive` (which itself was
mined from earlier extraction). Current Sprint 1 mining over 17 SACRED
screens could NOT verify spacing because all screens use absolute
positioning (no autolayout, `paddings`/`itemSpacing` all empty).

**Options:**
- **(a)** Accept DSYS scale as-is — refine later if a value proves wrong
  during Sprint 2 styleguide / mockup HTML construction
- **(b)** Pause and mine remaining 6 sections looking for any autolayout
  frames

**Default if no input:** option (a) — DSYS scale is well-tested
practical 4-base scale; refinement during HTML construction is cheap.

---

## Part 3 — Gate decision

After Part 1 ✅ and Part 2 decisions captured:

- [ ] TOKENS GATE: ✅ pass — proceed to Sprint 1 Step 1.3 (PNG export)
      then Sprint 2 Phase 3 (Styleguide HTML)
- [ ] TOKENS GATE: ❌ revise — list specific changes required:
      - ...

If revisions: I (Cowork-Chat) apply them in `02_design-system/tokens/`
master, re-sync to `01_deliverable/styles/`, then re-submit for gate.

---

## Anchor

```
[TOKENS-GATE-CHECKLIST.md | v1.0 | 2026-05-17]
Operator review aid for Sprint 1 Phase 2 draft of variables.css + global.css.
Lives in 02_design-system/ next to the artifacts under review.
Discarded after gate passes; recreated for any future Phase 2 iteration.
```
