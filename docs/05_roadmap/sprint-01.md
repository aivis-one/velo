# Sprint 1 — Figma Extraction + Token Synthesis

```
Dates:    TBD → TBD (planned 1 week)
Status:   planned
Owner:    Cowork (executor), Operator (validator)
Goal ref: ROADMAP.md §4
Phase:    Phase 1 (Figma Extraction) + Phase 2 (Token Synthesis)
```

---

## Goal

Complete Phase 1 (Figma extraction) and Phase 2 (token synthesis) per
methodology. Establish the design-system foundation.

> **Carry-over context from v1.0 adoption (2026-05-17):** the DSYS-era
> `variables.css` (now deleted from the workspace, lives only in git
> history) violated §11.1 anti-patterns AP-DS-1 through AP-DS-5 and was
> missing most §6.3 required token groups. Sprint 1 must produce a
> clean rebuild from Figma per §6.5, **not** restore from git history.
> The pre-v1.0 reconnaissance report `06_project-inputs/CC-REPORT.txt`
> (and Q2 in `06_project-inputs/CC-REPORT-2.txt` once it lands) records
> what colors/font primitives were verified earlier — useful as
> cross-checks during inventory, not as starting points.

---

## Scope

Five tasks across Phase 1 and Phase 2.

| # | Task | Owner | Phase |
|---|---|---|---|
| T1.1 | Phase 1 execution (Figma extraction) | Cowork | 1 |
| T1.2 | INVENTORY GATE validation | Operator | 1 |
| T1.3 | Phase 2 execution (token synthesis) | Cowork | 2 |
| T1.4 | TOKENS GATE validation | Operator | 2 |
| T1.5 | Sync to frontend (initial) | Claude Code | — |

---

## Task checklist

### T1.1 — Phase 1: Figma Extraction

Ref: VELO-METHODOLOGY.md §6.5 + Prompt template §9.2.
Owner: Cowork.

Steps per §6.5:

- [ ] Step 1.1 — Locate the Design System frame on the Figma "Design
      System" page via `get_design_context`
- [ ] Step 1.1 — If DS frame present: record as primary source; if
      absent: log fact in `VELO-DS-INVENTORY.md`
- [ ] Step 1.2 — Inventory existing variables via `get_variable_defs`
- [ ] Step 1.2 — Record line-heights as concrete numbers (no `auto`/`normal`)
- [ ] Step 1.3 — Extract every top-level screen frame on "Mockups" page
      as PNG to `02_design-system/assets/screenshots/{role}-{name}.png`
- [ ] Step 1.4 — Extract every icon as PNG (2× scale) + SVG where
      supported, to `02_design-system/assets/icons/icon-{name}.png`
- [ ] Step 1.5 — Mockup-mining: aggregate unique fill colors, radii,
      gap/padding, text node props, dropShadow effects across all screens
- [ ] Step 1.6 — Cross-reference DS frame vs mockup-mining
- [ ] Step 1.7 — Produce `02_design-system/tokens/VELO-DS-INVENTORY.md`
      with Sections A, B, C
- [ ] Update `02_design-system/assets/ASSETS-INDEX.md` with every
      screenshot and icon (source node ID + target path)
- [ ] Update `02_design-system/INDEX.md` → Token Status, Asset Index,
      Iteration Log

### T1.2 — INVENTORY GATE validation

Ref: VELO-METHODOLOGY.md §10.1.
Owner: Operator.

Criteria:

- [ ] `02_design-system/tokens/VELO-DS-INVENTORY.md` exists
- [ ] All three sections (A primitives, B semantic mapping, C MISSING) present
- [ ] Section A: every row has name, value, source, occurrences (no empty cells)
- [ ] Section B: every required §6.3 Layer 2 token has a mapping
- [ ] Section C: explicitly lists MISSING tokens or states "no MISSING tokens"
- [ ] `02_design-system/assets/screenshots/` contains a PNG per top-level
      Figma screen frame
- [ ] `02_design-system/assets/icons/` contains every icon used in any
      screen
- [ ] `ASSETS-INDEX.md` lists every asset with source node ID
- [ ] `02_design-system/INDEX.md` updated
- [ ] Spot-check: 3–5 screenshots match Figma at full size
- [ ] Spot-check: 3–5 icons match Figma at intended use
- [ ] Operator approves or requests revision (per §10.7 protocol if fail)

### T1.3 — Phase 2: Token Synthesis

Ref: VELO-METHODOLOGY.md §6.1, §6.2, §6.4 + Prompt §9.3.
Owner: Cowork.

`variables.css` requirements (§6.2):

- [ ] File at `02_design-system/tokens/variables.css` exists
- [ ] Contains only `:root { … }` block(s) with `--velo-*` definitions
- [ ] Layer 1 (primitives) block first, commented
- [ ] Layer 2 (semantic) block second, every alias defined as `var(--velo-color-*)` reference to Layer 1
- [ ] No `@import` statements (those go to global.css)
- [ ] No universal selectors (`* { box-sizing }`)
- [ ] No body/html resets
- [ ] No `.velo-typo-*` or any utility classes
- [ ] No component-specific dimensions (no `--velo-button-height`, etc.)
- [ ] No single-screen viewport constants (no `--velo-screen-width`, etc.)
- [ ] MISSING tokens present with `/* MISSING: not found in Figma — placeholder */` comments
- [ ] All §6.3 required token groups present (with MISSING placeholders if needed)

`global.css` requirements (§6.2):

- [ ] File at `02_design-system/tokens/global.css` exists
- [ ] `@import url(...)` for Google Fonts (or `@font-face` if self-hosted)
- [ ] Universal reset block: `* { box-sizing: border-box; }` + body reset
- [ ] Typography utility classes: `.velo-typo-{name}` per text style
- [ ] All `line-height` values are concrete decimals (never `normal`, never `auto`)
- [ ] No `:root` variable definitions
- [ ] No component-specific styles

Strict prohibitions (§11.1) — must verify zero of each:

- [ ] Zero `var(--velo-…) + Npx` constructs without `calc()` wrapper (AP-DS-2)
- [ ] Zero `line-height: normal` anywhere (AP-DS-3)
- [ ] Zero component dimensions in `variables.css` (AP-DS-4)
- [ ] Zero single-screen viewport constants in `variables.css` (AP-DS-5)
- [ ] Zero citations of non-existent ARCHITECTURE.md sections in file headers (AP-DS-6)

Sync to deliverable:

- [ ] Copy `02_design-system/tokens/variables.css` → `01_deliverable/styles/variables.css`
- [ ] Copy `02_design-system/tokens/global.css` → `01_deliverable/styles/global.css`
- [ ] Diff between master and copy is empty (byte-equal)

### T1.4 — TOKENS GATE validation

Ref: VELO-METHODOLOGY.md §10.2.
Owner: Operator.

Criteria:

- [ ] `02_design-system/tokens/variables.css` exists and contains ONLY `:root { … }` block(s)
- [ ] `02_design-system/tokens/global.css` exists with imports, reset, typography classes only
- [ ] Zero `line-height: normal` in either file
- [ ] Zero `var(--velo-…) + Npx` without `calc()` wrapper
- [ ] Zero `@import` in `variables.css`
- [ ] Zero `:root` variable definitions in `global.css`
- [ ] Zero component-specific tokens in `variables.css`
- [ ] All §6.3 required tokens present (with MISSING placeholders if needed)
- [ ] Both files copied to `01_deliverable/styles/`
- [ ] Spot-check 5–10 token values against the inventory
- [ ] Approve or revise

### T1.5 — Sync to frontend (initial)

Ref: ROADMAP.md §4.1 T1.5.
Owner: Claude Code, instructed by Operator after T1.4 passes.

- [ ] Ensure `frontend/src/styles/` directory exists (create if absent)
- [ ] Copy `01_deliverable/styles/variables.css` → `frontend/src/styles/variables.css`
- [ ] Copy `01_deliverable/styles/global.css` → `frontend/src/styles/global.css`
- [ ] Import order verified in `main.ts`: `global.css` (or `variables.css`) imported before any component CSS
- [ ] `npm run build` passes
- [ ] `npm run typecheck` (`vue-tsc --noEmit`) passes
- [ ] Commit + push

---

## Sprint 1 Gate

Ref: ROADMAP.md §4.2.

- [ ] INVENTORY GATE passed (T1.2)
- [ ] TOKENS GATE passed (T1.4)
- [ ] `frontend/src/styles/` contains valid tokens
- [ ] `02_design-system/INDEX.md` shows Token Status table filled
- [ ] Sprint 1 file (this one) marked `closed`

---

## Risks

| ID | Risk | Mitigation |
|---|---|---|
| 1.A | Figma "Design System" page is empty/absent — mockup-mining is the only source. | §6.5 step 1.1 covers this path; Cowork logs and proceeds. Inventory Section A marks source as "mining only". |
| 1.B | Required token groups have many MISSING entries (states, hover, focus). | §6.4 placeholder protocol; TODO logged in `02_design-system/INDEX.md`. |
| 1.C | Cowork repeats earlier anti-patterns (mixed `variables.css`/`global.css`, `line-height: normal`, etc.). | §11.1 explicit prohibitions; T1.4 gate checks each violation explicitly. |
| 1.D | Cowork tries to restore the DSYS-era `variables.css` from git history as a shortcut, dragging in §11.1 anti-patterns. | Operator enforces "rebuild from Figma per §6.5" rule. The pre-v1.0 reconnaissance reports (`CC-REPORT.txt` + `CC-REPORT-2.txt`) are reference only — never source of truth for tokens. |

---

## Daily log

- 2026-MM-DD: …

---

## Closure

- INVENTORY GATE: ☐ passed / ☐ failed (reason: __________)
- TOKENS GATE: ☐ passed / ☐ failed (reason: __________)
- Deferred to Sprint 2: ☐
- Methodology amendments proposed: ☐
- Operator signoff (date): ☐

---

## References

- Roadmap: `ROADMAP.md` §4
- Methodology: §6 (Design System Layer), §10.1–10.2 (gates), §11.1 (anti-patterns), §9.2–9.3 (prompts)
- Prior context: `../06_project-inputs/CC-REPORT.txt` (pre-v1.0 token inventory observations) and `../06_project-inputs/CC-REPORT-2.txt` (if present) for what was extracted earlier
- Inputs read during this sprint: `../06_project-inputs/ARCHITECTURE.md` (for rule cross-references)
