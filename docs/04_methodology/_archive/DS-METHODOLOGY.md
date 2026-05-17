# Design System Methodology v2.0

> Universal methodology for building a design system and its documentation.
> Source of truth is pixel-truth (PNG / screenshot / frame), not a tool.
> Applies to any stack (Vue / React / Svelte / Web Components / native).
> Compatible with the W3C Design Tokens Community Group format (DTCG v2025.10).
>
> This document is the single source of truth for the process. Not tied to
> Figma, does not require MCPs, plugins, or AI tooling. Can be executed by
> hand in any editor.

---

## 0. Principles

| # | Principle | Why |
|---|---|---|
| 1 | **Pixel-truth is the only authority.** Compare render with source side-by-side, pixel-by-pixel. | Design tools lie (group names, states, layers). Pictures do not. |
| 2 | **Layered token architecture.** Primitives → Semantic → (optional) Component. | Theme-swap, audit, migration, multi-brand — all happen via swapping aliases. |
| 3 | **Single source of truth.** Every constant lives in exactly one place. Everything else references. | One value change = one edit. Otherwise drift. |
| 4 | **Staged build with a verify gate.** After each phase — formal report + approval. | A discrepancy caught at phase N is 10× cheaper than one caught at N+3. |
| 5 | **Discovery, not imagination.** Components emerge from screens, not from "we usually need this". | A DS built upfront becomes fat and unused. |
| 6 | **Reproducible pipeline.** The next person / agent can pick up exactly where the previous one stopped. | Knowledge is not in the head — it is in `docs/`. |
| 7 | **Scale-by-need.** Start at Lean, grow to Standard, reach Enterprise only when product complexity demands it. | A DS sized for the wrong tier wastes effort or breaks under load. |
| 8 | **Accessibility is a contract, not a polish step.** Every component carries an a11y contract from day one. | Retrofitting a11y costs 10–30× more than building it in. |
| 9 | **Interoperability over lock-in.** Token data is exchangeable via an open format (DTCG). | Tools change, tokens shouldn't have to. |

---

## 0.5 Scale Tiers — Lean / Standard / Enterprise

Not every project needs every section of this methodology. Pick the tier that matches the product's complexity and grow into the next when **specific triggers** fire — not on a hunch.

### Tier matrix

| Capability | **LEAN** (MVP / single product / <10 screens) | **STANDARD** (active product / 1–3 themes / 10–50 screens) | **ENTERPRISE** (multi-product / multi-brand / 50+ screens / multiple consuming teams) |
|---|---|---|---|
| Token layers | Primitives + Semantic (2) | Primitives + Semantic (2) | Primitives + Semantic + Component (3) |
| Token format | CSS variables, optional JSON | CSS variables + DTCG JSON | DTCG JSON (canonical) + transformed outputs |
| Themes | Single | Light + Dark | Multi-brand + Light/Dark + density modes |
| Components (Tier 1) | ≥ 10 of 14 (skip Link/Tabs/Avatar if not used in product) | Full Tier 1 (14/14) + Tier 2 as needed | Full Tier 1 + Tier 2 + product-specific extensions |
| Motion tokens | None or 2 durations | Full motion scale + easing | Motion scale + spring + per-component patterns |
| Accessibility | WCAG 2.2 AA contrast + keyboard + focus ring + reduced-motion | + RTL + full a11y contract per component + axe in CI | + manual screen-reader testing + VPAT/ACR |
| Testing | Visual sanity pass | Visual regression (Chromatic/Percy) + axe-core | + interaction tests + cross-theme parity + a11y manual |
| Versioning | Pre-1.0, internal | SemVer per package, changelog | SemVer per component, RFC process, migration guides |
| Governance | One owner | Working group, weekly triage | Cross-functional council, RFC, contribution flow |
| Documentation | INDEX + DECISIONS + ROADMAP | Full §12 set | Full §12 set + CHANGELOG + MIGRATION + RFC archive |
| KB files (min) | 3 | 6 | 10+ |

### Triggers to step up

| From → To | Trigger |
|---|---|
| Lean → Standard | A second theme appears (dark mode requested) OR a second product begins consuming components OR Tier 1 reaches ≥8 components |
| Standard → Enterprise | A second brand appears OR >3 teams consume components OR a breaking change is needed and downstream teams must coordinate OR multi-platform output is required (web + native) |

### Anti-trigger

Do **not** step up because "we might need it later". Step up only when the trigger fires. Premature enterprise-tier DS is the #1 cause of dead-on-arrival design systems.

---

## 1. Pipeline (the map)

```
Source (PNG / screenshot / Figma frame / mockup)
        │
        ▼
EXTRACT — capture every measurable property
   ├─ tokens (colors, typography, spacing, radius, effects, motion)
   ├─ assets (images, icons, illustrations, photo backgrounds)
   └─ reference screens (pixel-truth, frozen)
        │
        ▼
BUILD STAGE 0 — Tokens
   variables.css + tokens.tokens.json + tokens-preview.html → verify gate
        │
        ▼
BUILD STAGE 1 — UI Kit (primitives)
   src/components/ui/*.{vue,jsx,svelte} + components-preview.html → verify gate
        │
        ▼
BUILD STAGE 2 — Layout + Patterns
   src/components/layout/* + screens-mockup.html → verify gate
        │
        ▼
RELEASE
   code ships to product + visual verify on staging + visual-regression baseline
        │
        ▼
SECTION CLOSED → next section (same loop, incremental)
```

**Every ↓ arrow is a verify gate.** Do not move to the next step without an explicit approval.

---

## 2. Token Architecture

### Layered structure

```
LAYER 1 — Primitives  (raw values, no context)
   neutral/100, brand/500, spacing/md, radius/sm, font/size/lg, duration/base
        │
        │  alias
        ▼
LAYER 2 — Semantic Tokens  (roles, intent)
   text/primary  → primitives/neutral-900
   bg/surface    → primitives/neutral-50
   action/primary/default → primitives/brand-500
        │
        │  bound by
        ▼
[LAYER 3 — Component Tokens  (OPTIONAL — Enterprise tier or specific need)]
   button/primary/bg/default → action/primary/default
   button/primary/bg/hover   → action/primary/hover
        │
        │  bound by
        ▼
Components  (use the lowest-defined layer)
   .btn-primary { background: var(--token-button-primary-bg-default); }
   /* or directly: background: var(--token-action-primary-default); */
```

### When the optional Component layer earns its place

The third layer is **opt-in**, not default. Add it only when at least one is true:

| Trigger | Example |
|---|---|
| The component defines ≥3 visual properties that no other component shares | Modal-specific `shadow` + `radius` + `backdrop-opacity` |
| Component states form a chain not covered by semantic states | Button's `default → hover → pressed → loading → disabled` |
| Same semantic token plays different roles in different components | `action/primary` is bg on Button but border on TabActive |
| Sub-brand or product overrides need component-level granularity | One brand wants ChipRadius different from BadgeRadius |

If none of these — stay at two layers. Adding Layer 3 just to "be tidy" is pure overhead.

### Rules

| # | Rule | Violation cost |
|---|---|---|
| T-01 | Components reference the lowest-defined layer (Semantic by default, Component when present). Never Primitives directly. | No theming, painful refactor |
| T-02 | Semantic tokens carry explicit `scopes` (where they may be used) | Accidental color-in-text or text-in-bg |
| T-03 | Primitives are pure values, no semantics in the name | `brand-500` ok; `text-button-primary` no — that is semantic |
| T-04 | Semantic aliases exactly one primitive (or another semantic in alias chains) | When a value changes, primitives change, semantic stays |
| T-05 | Naming: kebab-case + slashes for hierarchy: `text/primary`, `bg/surface-elevated` | CSS variable naming compatibility |
| T-06 | No typos like `text-primery` — naming is a contract | A DS is a language; dialects break understanding |
| T-07 | No circular aliases: `A → B → A` is forbidden | Build pipelines fail, runtime infinite loops |
| T-08 | No orphan tokens: every defined token has ≥1 consumer (or is documented as part of an atomic library) | Dead weight in payload, drift over time |

### Naming

**Primitives** — `{family}/{shade}` or `{family}/{name}`:

| Family | Pattern | Examples |
|---|---|---|
| brand | `brand/{50..900}` | `brand/500` = main |
| neutral | `neutral/{0..1000}` | `neutral/0` = white, `neutral/1000` = black |
| accent | `accent/{50..900}` | secondary brand |
| feedback | `success/{50..900}`, `warning/`, `error/`, `info/` | state colors |
| spacing | `spacing/{xs,sm,md,lg,xl,2xl,3xl}` | 4-/8-pt scale |
| radius | `radius/{none,xs,sm,md,lg,xl,full}` | corner radius |
| typography | `font/family/{sans,mono}`, `font/size/{xs..3xl}`, `font/weight/{regular..bold}` | type system |
| motion | `motion/duration/{instant..slower}`, `motion/easing/{standard,in,out,in-out,emphasized}` | timing primitives |

**Semantic** — `{role}/{name}`:

| Role group | Pattern | Examples |
|---|---|---|
| Background | `bg/{page,surface,elevated,inverse,brand,muted}` | `bg/surface` |
| Text | `text/{primary,secondary,disabled,inverse,brand,success,warning,error}` | `text/primary` |
| Border | `border/{default,subtle,strong,brand,error,focus}` | `border/focus` |
| Icon | `icon/{primary,secondary,disabled,brand}` | `icon/primary` |
| Action | `action/{primary,secondary,destructive}/{default,hover,active,focus,disabled}` | `action/primary/hover` |
| Spacing (semantic) | `space/{component,section,page}/{sm,md,lg}` | `space/component/md` |
| Radius (semantic) | `radius/{control,card,modal,pill}` | `radius/control` |
| Effect | `effect/{elevation-1,elevation-2,elevation-3,focus}` | `effect/focus` (double-ring shadow used for keyboard focus) |
| Motion (semantic) | `motion/{micro,quick,moderate,deliberate}` | `motion/quick` (= duration + easing pair) |

### CSS mapping

Prefix `--{namespace}-`. Slashes become dashes:

- `bg/surface` → `--velo-bg-surface`
- `text/primary` → `--velo-text-primary`
- `action/primary/hover` → `--velo-action-primary-hover`
- `motion/duration/base` → `--velo-motion-duration-base`

### DTCG interchange format (Standard+)

The canonical exchange format is the **W3C Design Tokens Community Group format (v2025.10)**. File extension `.tokens.json`, MIME `application/design-tokens+json`.

Example mapping:

```json
{
  "$schema": "https://www.designtokens.org/schemas/2025.10/format.json",
  "color": {
    "neutral": {
      "0":   { "$value": "#ffffff", "$type": "color" },
      "900": { "$value": "#0a0a0a", "$type": "color" }
    },
    "brand": {
      "500": { "$value": "#3b82f6", "$type": "color" }
    }
  },
  "bg": {
    "surface": {
      "$value": "{color.neutral.0}",
      "$type": "color",
      "$description": "Default surface background",
      "$extensions": { "scopes": ["background"] }
    }
  },
  "motion": {
    "duration": {
      "base": { "$value": "240ms", "$type": "duration" }
    },
    "easing": {
      "standard": { "$value": [0.2, 0, 0, 1], "$type": "cubicBezier" }
    }
  }
}
```

Allowed `$type` values per spec: `color`, `dimension`, `fontFamily`, `fontWeight`, `duration`, `cubicBezier`, `number`, `strokeStyle`, `border`, `transition`, `shadow`, `gradient`, `typography`. Stick to these; custom types break tool interop.

The internal naming (`bg/surface`) and DTCG JSON nesting (`bg.surface`) are isomorphic — slashes become object hierarchy.

### Modes (themes)

Light / Dark / brand / density are all "modes" — multiple sets of alias values over the same primitives (or partly over different primitives). Components know nothing about modes — they always read semantic, which is swapped under them.

To adopt a new mode: add the mode to the Semantic collection and walk each semantic token picking which primitive each one aliases. Components are not touched.

See §16 for multi-brand specifics.

---

## 3. Component System

### Tier 1 — required (14)

Minimum set for any product UI. If any one is missing, the DS is incomplete.

| # | Component | Variant axes | Minimum variants |
|---|---|---|---|
| T1-1 | Button | Variant (primary/secondary/ghost/destructive) × Size (sm/md/lg) × State (default/hover/active/focus/disabled/loading) | 12 |
| T1-2 | Link | Variant (default/inline/standalone) × State (default/hover/visited/focus) | 4 |
| T1-3 | Form Field (wrapper for Input/Select/Textarea — label + control + helper + error) | State (default/focus/error/disabled) × Size | 4–8 |
| T1-4 | Input / Text Field | State (default/focus/error/disabled) × Size × Type (text/email/password/search/number) | 4–8 |
| T1-5 | Checkbox | State (unchecked/checked/indeterminate/disabled) | 4 |
| T1-6 | Radio | State (unselected/selected/disabled) | 3 |
| T1-7 | Toggle / Switch | State (off/on/disabled) | 3 |
| T1-8 | Select / Dropdown | State (closed/open/disabled) × Size | 3–6 |
| T1-9 | Card | Variant (flat/elevated/outlined) × Padding (sm/md/lg) | 3 |
| T1-10 | Badge | Variant (default/info/success/warning/error) × Size (sm/md) | 5 |
| T1-11 | Alert / Banner | Severity (info/success/warning/error) × Dismissible (yes/no) | 4 |
| T1-12 | Modal / Dialog | Size (sm/md/lg/full) | 4 |
| T1-13 | Tabs | Orientation (h/v) × State (default/active/disabled) | 3 |
| T1-14 | Avatar | Size (xs/sm/md/lg/xl) × Type (image/initials/icon) | 5 |

### Tier 2 — recommended (12)

Extension of Tier 1. Absence is acceptable but reduces coverage.

| # | Component | Variant axes |
|---|---|---|
| T2-1 | Tooltip | Position (top/right/bottom/left) |
| T2-2 | Popover | Position, Size |
| T2-3 | Menu / Dropdown menu | State (closed/open) |
| T2-4 | Pagination | Variant (numeric/prev-next-only) |
| T2-5 | Breadcrumb | Length |
| T2-6 | Progress bar | Variant (determinate/indeterminate) × Size |
| T2-7 | Spinner | Size × Color |
| T2-8 | Slider | Variant (single/range) × State |
| T2-9 | Accordion | State (collapsed/expanded) |
| T2-10 | Toast / Snackbar | Severity × Position |
| T2-11 | Skeleton | Shape (text/avatar/card) |
| T2-12 | Divider | Orientation (h/v) |

### Naming

- **Prefix** for components (V-prefix, M-prefix, App-prefix — pick one for the project).
- **PascalCase** for the name: `VButton`, `VInputText`, `VCheckbox`.
- **One file = one component**: `VButton.vue` / `VButton.jsx`.
- **BEM** in CSS classes: `.v-button`, `.v-button__label`, `.v-button--primary`, `.v-button--disabled`.
- **Barrel import only**: `import { VButton } from '@/components/ui'`. Never `import VButton from '@/components/ui/VButton.vue'`.

### Variant axes — canonical

| Axis | Allowed values |
|---|---|
| Variant | primary, secondary, tertiary, ghost, destructive |
| Size | xs, sm, md, lg, xl |
| State | default, hover, active, focus, disabled, loading, error |
| Type | text, email, password, search, number, tel, url |
| Severity | info, success, warning, error |
| Position | top, right, bottom, left, top-left, top-right, bottom-left, bottom-right |
| Density (Enterprise) | compact, comfortable, spacious |

Do not invent new axes for Tier 1. If something does not fit — that is a signal the component is Tier 2 or a new component entirely.

### Component description template

In the component file header (or in the Storybook description):

```
PURPOSE: <one sentence>
USAGE: <when to use, when not to>
VARIANTS: <axis 1: values; axis 2: values>
ACCESSIBILITY:
  - Semantic element: <button | a | input | dialog | …>
  - ARIA: <role(s), states, properties>
  - Keyboard: <Tab order, Enter, Space, Esc, Arrow keys>
  - Focus management: <how focus enters/leaves; trap if modal>
  - Accessible name source: <label | aria-label | aria-labelledby | text content>
  - Touch target: <≥ 44×44 recommended; ≥ 24×24 minimum with documented justification — see §6>
  - RTL: <mirrors / does not mirror>
  - Reduced motion: <fallback behavior>
NOTES: <project-specific caveats>
```

### Deprecation marker

Components that must not be used in new code but cannot yet be deleted:

- Name starts with `[deprecated] `: `[deprecated] VButtonOld`
- Description starts with `DEPRECATED: <reason>. Use <replacement> instead.`
- Excluded from Tier-matrix coverage counts.
- Lifecycle: announce → ship at least one MINOR version with the marker → remove in next MAJOR (see §14).

---

## 4. Source Extraction (mockup mining)

### Asset taxonomy — frequency analysis

| Tier | What | Where | Examples |
|---|---|---|---|
| **S** | reusable mark / motif appears **5+ times** | Foundations / Decorations | logo, brand pattern, sacred-geometry |
| **A** | UI atom repeats **3-5 times** | Components | badge, avatar slot, divider |
| **B** | composition appears **2-3 times** | Patterns | card with hero image, list-row with avatar |
| **C** | unique to one screen | leave in place, do not extract | one-off illustration, screen-specific text |

Thresholds are tunable (record in `docs/DECISIONS.md`).

### Frequency-analysis algorithm

1. Walk every screen in the source, collect every top-level group / frame.
2. Bucket by `(width rounded to 4px, height rounded to 4px)` — the "size signature".
3. Filter buckets with count ≥ 3.
4. For each surviving bucket — check visual cleanliness (see below).
5. For survivors — compute a visual hash.
6. Group hash-identical members into deduplication clusters.
7. Cluster ≥ 3 = Tier S/A; cluster of 2 = Tier B; cluster of 1 = Tier C, leave it.

### Screenshot-before-naming rule

**Never assign a DS name based on the source group name.** Do this instead:

1. Screenshot the candidate.
2. Inspect visually.
3. Name by visual content ("Sacred Geometry", not "Group 1924").
4. Apply the naming convention from §3.

Names in source files lie: "Group 142" may be a carefully crafted brand mark, "Brand Logo" may be an outdated draft.

### Dedup by hash, not by name

Two components with the same name may be different. Two groups with different names may be identical. Content hash is the only reliable signal.

### Cloning recipe

When extracting an asset from the source:

1. **Clone**, do not move (source stays as reference).
2. **Strip transient state**: elements `*_hover`, `*_active`, `*_disabled` — remove.
3. **Scale preserving aspect ratio** if the destination cell is fixed.
4. **Bind to tokens** — no hex / px residue.
5. **Rename** per convention.
6. **Verify hash** against at least one source occurrence.

### Priority — where to look first

When mining a new screen:

1. Repeating logos / marks — almost always Tier S.
2. Backgrounds with clean geometric content — Tier S decorations.
3. Status indicators (badges, dots, pills) — Tier A.
4. List rows with consistent layout — Tier B.
5. Form layouts — last priority (often have screen-specific deviations).

Skip on the first pass: hero illustrations, screen-specific copy, marketing-only one-offs.

---

## 5. Visual Patterns (Foundations docs)

The minimum that should appear in DS documentation (preview HTML / Storybook / etc.).

### Swatch Card

Each color is a vertical stack:

| Element | Size | Source |
|---|---|---|
| Color block | 240×120 | bound to color variable |
| Name | type/sm | display name ("Brand 500") |
| Hex value | type/xs mono | derived from current value |
| Role | type/xs | semantic role |

### Typography section

One row per style:

| Element | Source |
|---|---|
| Sample text | bound to text style ("The quick brown fox…") |
| Style name | e.g. "Display / 2xl" |
| Metrics | `48 / 56` (size / line-height) |

Mobile vs desktop type scales: maintain both, document the divergence.

### Surface variants

4-up grid:

| Surface | Token | Border |
|---|---|---|
| Page | `bg/page` | none |
| Surface | `bg/surface` | `border/subtle` |
| Elevated | `bg/elevated` | none + shadow |
| Inverse | `bg/inverse` | none |

### WCAG Contrast Card

Table of token pairs with actual ratios:

| Pair | Required | Actual | Pass? |
|---|---|---|---|
| `text/primary` on `bg/surface` | ≥ 4.5 (AA body) | derived | ✓/✗ |
| `text/secondary` on `bg/surface` | ≥ 4.5 | derived | ✓/✗ |
| `action/primary` on `bg/page` | ≥ 3.0 (AA UI element) | derived | ✓/✗ |
| `border/focus` on `bg/surface` | ≥ 3.0 (focus indicator) | derived | ✓/✗ |

Run for **every theme** the DS supports (light, dark, each brand). Each pair must pass in each theme.

### Shadow elevation

Three levels:

| Level | Token | y-offset | blur | spread | Color |
|---|---|---|---|---|---|
| 1 (subtle) | `effect/elevation-1` | 1 | 2 | 0 | `neutral/900 @ 5%` |
| 2 (default) | `effect/elevation-2` | 4 | 8 | 0 | `neutral/900 @ 10%` |
| 3 (modal) | `effect/elevation-3` | 12 | 24 | 0 | `neutral/900 @ 15%` |

In dark theme, shadows often vanish — substitute or augment with a 1px subtle border in dark mode.

### Motion scale (full set at Standard+; minimal subset allowed at Lean)

Display all motion tokens with live previews:

| Token | Duration | When to use |
|---|---|---|
| `motion/duration/instant` | 100ms | State color flips, immediate feedback |
| `motion/duration/fast` | 160ms | Hovers, tooltips, small movements |
| `motion/duration/base` | 240ms | Default — most UI transitions |
| `motion/duration/slow` | 360ms | Modals, sheets, larger transitions |
| `motion/duration/slower` | 500ms | Page-level transitions, hero animations |

| Token | Curve | When to use |
|---|---|---|
| `motion/easing/standard` | `cubic-bezier(0.2, 0, 0, 1)` | Default — most motion |
| `motion/easing/out` | `cubic-bezier(0, 0, 0.2, 1)` | Elements entering the screen |
| `motion/easing/in` | `cubic-bezier(0.4, 0, 1, 1)` | Elements leaving the screen |
| `motion/easing/emphasized` | `cubic-bezier(0.2, 0, 0, 1.2)` | Attention-grabbing entrances |

Semantic pairs (optional but recommended):

- `motion/micro` = `duration/instant` + `easing/standard`
- `motion/quick` = `duration/fast` + `easing/out`
- `motion/moderate` = `duration/base` + `easing/standard`
- `motion/deliberate` = `duration/slow` + `easing/emphasized`

**Lean subset:** a Lean-tier DS may ship with only `motion/duration/{fast, base}` and `motion/easing/standard`. The full scale becomes mandatory at Standard tier.

### Cover gradient

Requirement for hero / cover: at least 3 stops with an explicit angle. Single-stop and 2-stop gradients often render flat.

---

## 6. Mobile Patterns

### Frame baselines

| Platform | Width | Height |
|---|---|---|
| iOS (iPhone 14/15) | 390 | 844 |
| iOS Pro Max | 430 | 932 |
| Android (medium) | 360 | 800 |
| Android (large) | 412 | 915 |

Build DS patterns at 1× (logical pixels), export resolution per-asset.

### Safe-area insets

| Platform | Top | Bottom |
|---|---|---|
| iOS notched | 47 | 34 |
| iOS Dynamic Island | 59 | 34 |
| Android | 24 | 16 |

Encode as tokens: `space/safe/top`, `space/safe/bottom` per platform mode.

### Touch target rule

Two bars:

- **Minimum (WCAG 2.2 AA, 2.5.8)**: 24×24 CSS pixels — meets legal baseline.
- **Recommended**: 44×44 (iOS HIG) / 48dp (Android Material) — comfortable for thumbs.

Default to recommended; allow minimum only with justification recorded in `docs/DECISIONS.md`.

If the visible element is smaller (16px icon), wrap it in a 44×44 transparent frame that owns the tap handler.

### Dynamic Type / system font scale

Components must survive system text-scale up to 200% (WCAG 1.4.4). Test:

- Buttons grow vertically, do not clip
- Form fields wrap label and helper
- Tab bars switch to icon-only if labels overflow

### Tab Bar

| Element | Spec |
|---|---|
| Height | 49 (iOS) + safe-bottom; 56 (Android) |
| Item count | 3-5 (more = scroll, fewer = use FAB) |
| Item layout | Icon (24×24, top) + label (xs, bottom) |
| Active | filled icon + `text/brand` |
| Inactive | outline icon + `text/secondary` |

### Top App Bar

| Element | Spec |
|---|---|
| Height | 44 (iOS) + safe-top; 56 (Android) |
| Title | center (iOS) / left (Android), type/lg |
| Leading | back / menu / none |
| Trailing | ≤ 2 actions / overflow menu |

### Bottom Sheet (mobile Modal)

| State | Height | Handle | Backdrop |
|---|---|---|---|
| Mini | content-HUG | optional | none |
| Half | 50% screen | yes | `bg/inverse @ 50%` |
| Full | safe-top → bottom | yes | dimmed |

### FAB

| Variant | Size | Position |
|---|---|---|
| Standard | 56×56 | 16 from bottom + right |
| Mini | 40×40 | same |
| Extended | 56h, HUG width | same |

Elevation 2 or 3. Background `action/primary/default`, icon `text/inverse`.

### Theme parity rule

Every mobile component works in both themes (if dark mode exists). Check:

- zero hardcoded hex
- contrast ≥ 4.5 in both themes
- shadow visible in dark (sometimes needs a different elevation token)

### Status bar treatment

| Background | Status bar style |
|---|---|
| `bg/page` (light theme) | dark content |
| `bg/inverse`, `bg/brand` | light content |
| Image / hero | light content + dim overlay |

### Acknowledged gaps (not in scope)

These are intentionally out of scope for this methodology — document the boundary, do not pretend otherwise:

- Foldables and split-screen
- Watch / TV / Auto form factors
- Native platform-specific patterns (iOS context menus, Android material-you dynamic color)

If the product needs any of these, treat as a project-specific extension.

---

## 6.5 Accessibility (a11y)

Accessibility is a **contract per component**, not a polish step. Every component carries its a11y contract from day one (see §3 template). Target: **WCAG 2.2 Level AA** as the baseline (ISO/IEC 40500:2025).

### Universal contract checklist

Every interactive component must satisfy:

| # | Requirement | How verified |
|---|---|---|
| A-01 | Uses semantic element when one exists (`<button>` not `<div onClick>`) | Code review |
| A-02 | Has accessible name (visible text, `aria-label`, or `aria-labelledby`) | axe-core |
| A-03 | Fully operable by keyboard (Tab to reach, Enter/Space to activate, Esc to dismiss, Arrows for in-component nav) | Manual keyboard test |
| A-04 | Visible focus indicator with contrast ≥ 3:1 against adjacent colors | Manual + visual regression on focused state |
| A-05 | Touch target ≥ 44×44 recommended; ≥ 24×24 minimum (WCAG 2.5.8) only with documented justification per §6 | Layout inspection |
| A-06 | Text contrast ≥ 4.5:1 (body) or ≥ 3:1 (large text 18px+ or 14px+ bold, UI elements) | Automated contrast check |
| A-07 | Color is not the sole carrier of meaning (icon + text alongside) | Manual review |
| A-08 | Respects `prefers-reduced-motion` (durations collapse to 0 or near-0) | Manual test with OS toggle |
| A-09 | RTL: mirrors directional UI (chevrons, progress, slide direction); does not mirror text content | Visual check in RTL locale |
| A-10 | Live regions for dynamic announcements (toast, error, loading state change) where appropriate | Screen reader test |

### Focus ring as a token

Define a single focus indicator used by every focusable component. Two semantic tokens, one CSS implementation.

**Semantic aliases (per theme):**

```
light theme:
  border/focus → brand/600    (contrast ≥ 3:1 vs every surface)
  effect/focus → shadow with border/focus, 2-ring offset

dark theme:
  border/focus → neutral/0    (contrast ≥ 3:1 vs every surface)
  effect/focus → shadow with border/focus, 2-ring offset
```

**CSS implementation (double-ring pattern, visible on any background):**

```css
:root {
  --effect-focus: 0 0 0 2px var(--bg-page),
                  0 0 0 4px var(--border-focus);
}

.focusable:focus-visible {
  outline: none;
  box-shadow: var(--effect-focus);
}
```

Components consume `--effect-focus`; theme swaps `--border-focus` underneath.

### Reduced motion pattern

Use the canonical WAI-recommended pattern: a global override that collapses all transitions and animations under `prefers-reduced-motion: reduce`. No per-component branching, no scalar token to maintain.

```css
/* Default — components reference motion tokens normally */
.transition { transition-duration: var(--motion-duration-base); }

/* Global override — flips every transition/animation to near-instant */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
  }
}
```

This satisfies WCAG 2.3.3 globally with one CSS rule. Components do not need to know reduced-motion exists.

**Alternative (advanced):** if more granular control is needed — e.g., keep some essential motion (loading spinners) but kill decorative motion — introduce a `motion/duration/scalar` primitive (number, default `1`, set to `0` under the media query) and multiply unitless durations: `transition-duration: calc(var(--motion-scalar) * 240ms)`. This requires every motion-bearing rule to opt in via the scalar, and breaks for any rule that forgets. Use only at Enterprise tier when audited.

### Component-specific contracts (examples)

**Modal / Dialog**
- `role="dialog"` + `aria-modal="true"` + `aria-labelledby` referencing the title
- Focus traps inside while open; first focusable element receives focus on open; previously focused element receives focus on close
- Esc closes; backdrop click closes (configurable)
- Background content has `aria-hidden="true"` or `inert`

**Tooltip**
- Appears on hover **and** keyboard focus
- Dismissible with Esc without moving focus
- Content remains visible while hovering the tooltip itself
- Not the sole carrier of essential information (use Popover for that)

**Tabs**
- `role="tablist"` / `role="tab"` / `role="tabpanel"` with `aria-controls`/`aria-labelledby`
- Arrow keys move between tabs; Home/End to jump; Enter or Space to activate
- `tabindex="0"` only on active tab, `-1` on inactive

**Form Field**
- `<label>` associated via `for`/`id` or wrapping
- Error: `aria-invalid="true"` + `aria-describedby` referencing the error text
- Helper text linked via `aria-describedby`

### Automated coverage and its limits

- **axe-core in CI**: catches roughly 30–57% of WCAG violations depending on rule set. Necessary but not sufficient.
- **Visual regression in dark + light + RTL**: catches contrast and layout regressions.
- **Manual keyboard pass**: required on every new component.
- **Manual screen reader pass** (NVDA + VoiceOver): required at Enterprise tier before each MAJOR release.

### Acknowledged limit

A DS provides accessible building blocks. A consuming product can still misuse them (wrong heading order, missing landmarks, broken page flow). Document this boundary in `docs/A11Y.md` so product teams know their own responsibility.

---

## 7. Header Blocks (optional, recommended)

Every numbered DS section gets a Header Block — 6 fields answering "what, who, why, what's broken".

### 6-field structure

| Field | Content | Length |
|---|---|---|
| **PURPOSE** | one sentence "what this section is for" | ≤ 120 chars |
| **USAGE** | when to apply, when not | 1-3 bullets |
| **INVENTORY** | counts: N components, M variants, K patterns | one line |
| **RELATED** | cross-references (B.7 / P-NNN) | 0-5 IDs |
| **OPEN ISSUES** | known problems, deferred fixes, awaiting decisions | 0-5 bullets |
| **ANCHOR** | this section's own anchor ID | 1 ID |

Plus a colored identity-bar (4px wide) on the left edge — a visual signature at zoom-out.

### 3 layout variants

| Layout | When |
|---|---|
| **A — single column** | Narrow section, single-column content |
| **B — 2D grid** | Uniform preview cells of equal width |
| **C — adaptive cards** | Heterogeneous widths, migration scenario |

---

## 8. Workflow Phases (P-1 pre-flight, then P0..P8)

Universal sequence for building a DS section. **Max 2-3 phases per chat session** — more = drift and context loss.

### P-1 — Inventory audit (only when retrofitting an existing product)

Skip if greenfield. Mandatory if a product exists without a DS:

- List every color used across the product (CSS audit, design file scan)
- List every component-like piece (search for repeated DOM patterns)
- Identify near-duplicates (same component with 3 slightly different paddings)
- Output: `docs/INVENTORY.md` — basis for the EXTRACT phase

### P0 — Pre-flight

- Source identified (PNG / Figma / screenshot)
- Target platforms (web / mobile / both)
- Target tier (Lean / Standard / Enterprise) chosen and recorded
- Token namespace chosen (`--velo-*`, `--app-*`, etc.)
- Folders `extract/`, `stage-{0,1,2}-*/`, `docs/` exist
- VALIDATE → 4-field report.

### P1 — Tokens (Primitives)

- Parse source — extract color / spacing / radius / typography / motion values
- Create primitives with explicit scopes
- VALIDATE.

### P2 — Tokens (Semantic)

- Create semantic aliases over primitives
- Apply explicit scopes
- Confirm 0 wildcards
- Verify no circular aliases, no orphans
- VALIDATE.

**[Session boundary recommended after P2.]**

### P3 — Styles (text + effect + motion)

- Create text styles for each size / style
- Create effect styles (elevation 1/2/3)
- Create motion styles (Standard+) — duration × easing pairs
- Letter-spacing: pick one unit (% or px) and stick with it
- VALIDATE.

### P4 — Cover + Foundations

- Cover frame (≥ 3-stop gradient, logo, version/date)
- Foundations: swatches, gradients, type rows, surfaces, WCAG contrast card, motion previews
- If decoration mining is in scope: Tier-S decorations via cloning recipe
- VALIDATE.

### P5 — Icons

- Import icon library (Lucide / Phosphor / Heroicons)
- Categorize
- Single stroke weight per category
- VALIDATE.

**[Session boundary recommended after P5.]**

### P6 — Components (Tier 1)

For each T1-1 .. T1-14:

1. Build base component
2. Build variant components
3. Combine via variant axes
4. Apply tokens (no hardcode)
5. Apply a11y contract (§3 template + §6.5 checklist)
6. Fill component description

VALIDATE after every 3 components.

### P7 — Components (Tier 2) + Patterns

- Tier 2 (T2-1 .. T2-12) — same pattern
- Patterns: numbered P-NNN frames, ONLY component instances (no detached masters)
- If headers are in scope: a Header Block per pattern (§7)
- VALIDATE.

### P8 — Playground + final audit

- Build ≥ 1 screen-level composition in Playground (DS components only)
- Run AUDIT (§§ 10–11) — 0 BREAK before closing
- Run tests (§15) — visual regression baseline captured, axe-core clean
- Update `docs/PROGRESS.md`, `docs/SESSION-LOG.md`, `docs/CHANGELOG.md`
- Final salvage pass over the whole chat (§9)
- VALIDATE.

### GATE-OUT

```
✓ 6 root frames present (Cover / Foundations / Icons / Components / Patterns / Playground)
✓ docs/ updated (INDEX / ROADMAP / PROGRESS / SESSION-LOG / DECISIONS / CHANGELOG)
✓ Quality Gates PASS (§11)
✓ Tier 1 minimum met per tier (Lean: ≥10/14; Standard/Enterprise: 14/14)
✓ A11y contracts filled on every component
✓ Final AUDIT: 0 BREAK
✓ Visual regression baseline captured (Standard+)
```

---

## 9. Validation Protocol

### 4-field VALIDATE report

After **every** phase. Do not skip.

```
=== VALIDATE — Phase {N}: {phase name} ===

PLANNED
- {bullet 1 — verbatim from phase GATE-IN}
- {bullet 2}

GOT
- {artifact 1: path, count, ID}
- {artifact 2}

DISCREPANCIES
- {Planned X not in Got — reason}
- {Got Y not in Planned — reason}
- {Semantic delta on Z — reason}
- (or "none")

DEFERRED
- {item} -> Phase {M}, because {reason}
- (or "none")

NEXT PHASE: {N+1: name} — proceed? (OK / fix / pause)
```

### Field rules

**Planned** — verbatim from GATE-IN. No paraphrasing. If you cannot copy verbatim — that is itself a discrepancy.

**Got** — concrete file paths or node IDs. No "implemented" verbs — only artifacts. Counts derived (`find ... | wc -l`), not estimated.

**Discrepancies** — three classes:

- *Planned-not-in-Got* — the phase failed to deliver what was committed
- *Got-not-in-Planned* — the phase delivered out-of-scope (potential scope creep)
- *Semantic delta* — item in both lists, implementation differs from plan

Each row carries a reason. "Unknown" is allowed but escalates.

**Deferred** — each row points to a target phase. Open-ended "later" is forbidden. Max carry distance: 3 phases.

### Severity scale

| Severity | Meaning | Action |
|---|---|---|
| **BREAK** | critical violation, section / release blocked | fix immediately |
| **GAP** | important but non-blocking | fix before phase close |
| **NIT** | cosmetic / preference | may defer, record under OPEN ISSUES |

### Pre-close salvage pass (before closing a chat session)

Walk these 6 checkpoints over the entire session dialog:

| # | Checkpoint | Signals | Lands in |
|---|---|---|---|
| 1 | Decisions agreed | "let's go with X", "OK fix it", "use approach B" | `docs/DECISIONS.md` |
| 2 | Constraints discovered | "X doesn't work because Y" | `docs/DECISIONS.md` or `docs/METHODOLOGY.md` |
| 3 | Edge cases hit | "what about empty / large / negative / zero / unicode" | `docs/DECISIONS.md` or lessons file |
| 4 | Renames done | "rename A to B" | `docs/INDEX.md` + relevant places |
| 5 | User corrections | "no, actually X", "you got that wrong" | lessons file + reflect in target |
| 6 | Rejected-then-revived | idea dismissed earlier, brought back later | `docs/DECISIONS.md` with "revived from {date}" |

Items not matching any checkpoint → lessons file as "unclassified".

### When the report cannot be skipped

| Skip rationale | Why it is wrong |
|---|---|
| "Phase was small" | Small phases drift faster |
| "Nothing went wrong" | The report verifies that; without it you do not know |
| "User is in a hurry" | Hurry is the worst time; debt compounds |
| "I'll combine with next phase" | Doubles the scan surface, discrepancies hide |

---

## 10. Anti-Patterns

These patterns pass formal validation but make the DS hard to extract and unmaintainable.

### Structural (A1-A8)

| # | Pattern | Detection | Severity | Fix |
|---|---|---|---|---|
| **A1** | Empty wrapper | Container with 0 children | BREAK | delete |
| **A2** | Single-child redundancy | Wrapper with 1 child that is itself a component, wrapper adds no padding/effects | GAP | unwrap |
| **A3** | Zero-atomic frame | Frame under "Components" with no COMPONENT descendants | GAP | move to Patterns (it is a composition) |
| **A4** | Inconsistent showcase prefix | Sibling preview cells with mixed naming (`Card / display`, `Card showcase`, `Card preview`) | NIT | normalize |
| **A5** | Generic default name | `Frame N`, `Rectangle N`, `Group N`, `Vector N` | GAP | rename |
| **A6** | Created-but-not-placed | Component with 0 instances, no documented "atomic library" intent | GAP | place ≥ 1 instance in Playground |
| **A7** | Mixed-domain Set | One component-set holding variants across semantic domains | BREAK | split into two sets |
| **A8** | Vertical sprawl | Section > 10000px tall, single-column | GAP | reorganize as 2D grid OR adaptive cards |

### Token anti-patterns (A9-A11)

| # | Pattern | Detection | Severity | Fix |
|---|---|---|---|---|
| **A9** | Hardcoded value in component | Hex / px / ms / cubic-bezier literal inside a component file | BREAK | replace with token reference |
| **A10** | Orphan token | Token defined, 0 consumers in components or other tokens, not flagged as atomic library | GAP | remove or document |
| **A11** | Circular alias | `A → B → A` in alias chain | BREAK | flatten the chain |

### Duplicates (D1-D5)

Require hash-based detection (names lie).

| # | Pattern | Detection | Fix |
|---|---|---|---|
| **D1** | Triple-form | 3 sibling components with shared stem + suffix {outline, filled, reusable} + hash similarity | merge into one set with `Style` variant |
| **D2** | Composite-vs-atom | Same hash appears in Foundations (preview cell) and Components (master) | keep master, replace Foundations occurrence with an instance |
| **D3** | Cross-frame name | 2 components share a name but live in different root frames | rename the less-canonical one |
| **D4** | Variant-overlap | Generic set holds variants fully covered by a more specific set | move overlapping variants into the specific set |
| **D5** | Wrapper-redundancy | Frame `{X} / display` containing exactly 1 component `{X}` | drop wrapper or rename to `{X} Cell` |

### Detection ordering (important)

Run in this order (some patterns mask others):

1. **A1** (empty) — removes nodes that would falsely trip A2/A5
2. **A5** (generic names) — fix names before A4 normalization runs
3. **A2, D5** (wrapper redundancy) — collapse before duplicate detection
4. **D1-D4** (duplicates) — require post-collapse hash equality
5. **A3, A6** (placement) — semantic check on what remains
6. **A4, A7, A8** (naming consistency, domain mixing, sprawl) — final pass
7. **A9, A10, A11** (token violations) — separate token-layer pass

---

## 11. Quality Gates

Pass/fail checks before release.

### Core gates (Lean+)

| QG | Gate | Provides |
|---|---|---|
| **QG-1** | Every semantic token carries explicit scopes | Protection against cross-domain misuse |
| **QG-2** | Letter-spacing uses a single unit (% or px) consistently | Shipping consistency |
| **QG-3** | Single source of truth for the DS (one file / folder) | Navigation does not suffer |
| **QG-4** | All component masters live in one place (not scattered across mockups) | Findable, no duplicates |
| **QG-5** | All Tier 1 components present + named per the matrix | Full coverage for extraction |
| **QG-6** | Variant property names use canonical axes (Variant / Size / State) for Tier 1 | Predictable API |
| **QG-7** | No instance-level overrides on color / font / size | Overrides expressed as variant changes |
| **QG-8** | No hardcoded values (color / font / spacing / motion) — everything bound to tokens | Theme-swap works |

### Accessibility gates — Lean+ (manual at Enterprise)

| QG | Gate | Provides |
|---|---|---|
| **QG-9** | Every interactive component operable via keyboard | WCAG 2.1.1 |
| **QG-10** | Visible focus indicator on every focusable element, contrast ≥ 3:1 | WCAG 2.4.7, 1.4.11 |
| **QG-11** | Text / UI contrast ≥ WCAG 2.2 AA in every theme | WCAG 1.4.3, 1.4.11 |
| **QG-12** | `prefers-reduced-motion` respected | WCAG 2.3.3 |

### Accessibility gates — Standard+ (when product targets RTL locales)

| QG | Gate | Provides |
|---|---|---|
| **QG-13** | RTL: component mirrors correctly (where applicable) | International support |

### Engineering gates (Standard+)

| QG | Gate | Provides |
|---|---|---|
| **QG-14** | Token JSON validates against DTCG v2025.10 schema | Tool interoperability |
| **QG-15** | Visual regression: 0 unintentional diffs on main | Catch unintended visual changes |
| **QG-16** | axe-core: 0 violations on every Storybook story | Automated a11y baseline |

### Performance gates (Enterprise)

| QG | Gate | Provides |
|---|---|---|
| **QG-17** | Bundle size per component within budget | Stays lean as DS grows |
| **QG-18** | Tree-shakable: importing one component does not pull the rest | Consumer apps stay fast |

### Output format

```
=== QUALITY GATES — tier: STANDARD ===

  QG-1 scopes:        PASS
  QG-2 typography:    PASS
  QG-3 single-source: PASS
  QG-4 masters:       PASS
  QG-5 Tier 1:        BREAK — missing T1-5 Toggle, T1-11 Tabs
  QG-6 variant names: PASS
  QG-7 overrides:     PASS
  QG-8 hardcode:      BREAK — 4 hex values found in VButton (see list)
  QG-9 keyboard:      PASS
  QG-10 focus ring:   PASS
  QG-11 contrast:     PASS (light), BREAK (dark — text/secondary on bg/elevated = 3.8:1)
  QG-12 reduced-motion: PASS
  QG-13 RTL:          PASS
  QG-14 DTCG:         PASS
  QG-15 vis. regression: PASS (12 baselines)
  QG-16 axe-core:     PASS

Verdict: 3 BREAK
```

---

## 12. Knowledge Base Structure

So the next person / agent can pick up exactly where the previous one stopped. Minimum file set in `docs/` scales by tier:

### Lean (3 files minimum)

| File | Content |
|---|---|
| **INDEX.md** | Map of all folders + bootstrap for a new chat |
| **DECISIONS.md** | Chronological log of decisions (D-NNN IDs) |
| **ROADMAP.md** | Roadmap Stage 0 → 1 → 2 → sections |

### Standard (6 files)

Add:

| File | Content |
|---|---|
| **PROGRESS.md** | Task state in real time |
| **SESSION-LOG.md** | Chronology of chat sessions |
| **METHODOLOGY.md** | Rules of work (this document, project-adapted) |
| **CHANGELOG.md** | Keep-a-Changelog format, per-release |

### Enterprise (10+ files)

Add:

| File | Content | Update when |
|---|---|---|
| **A11Y.md** | Accessibility contract for the DS + product responsibilities | new component, a11y issue raised |
| **THEMING.md** | How to add a new theme / brand | new theme/brand added |
| **CONTRIBUTING.md** | Flow for adding components, tokens, patterns | flow changes |
| **MIGRATION-v{N}.md** | One per MAJOR — step-by-step upgrade guide | each MAJOR release |
| **RFCS/** | Folder of open and closed RFC documents | every significant proposal |

Plus: `docs/_raw-extracts/` — raw dumps from sources (for potential rebuilds).

**Principle:** a new chat opens `INDEX.md` and can continue without asking the human anything.

---

## 13. What the methodology does NOT do

| ❌ Does not | ✅ Does |
|---|---|
| Decide colors, fonts, spacing for you — that is art direction | Organize what you already chose |
| Replace visual verification (PNG ↔ preview HTML / rendered component) | Structure the verification process |
| Make original design | Turn existing design into a system |
| Tie you to one tool | Applies to any stack and any source |
| Require an AI agent | You can work by hand with this document and an editor |
| Protect against human error without verify gates | Surfaces drift via the 4-field report |
| Decide your tier for you | Provides criteria and triggers to choose and step up |
| Cover platform-specific edge cases (foldables, watch, TV) | Defines the boundary so extensions are conscious |

---

## 14. Versioning & Governance (Standard+)

### SemVer for design systems

Use Semantic Versioning: `MAJOR.MINOR.PATCH`.

| Bump | Trigger |
|---|---|
| **MAJOR** | Token renamed or removed; component API breaking change (prop removed/renamed); variant axis renamed; theme structure changed in incompatible way; minimum browser/runtime support raised |
| **MINOR** | New component or token added; new variant added; new theme added; deprecation announced (with marker, not yet removed); non-breaking prop additions with sensible defaults |
| **PATCH** | Bug fix not changing API; visual fix within tolerance; internal refactor invisible to consumers; doc-only changes |

### Versioning strategy — pick one, document it

| Strategy | When |
|---|---|
| **Single package** (one version for the whole DS) | Lean / Standard; small surface; one consumer team |
| **Per-component** (each component versioned independently) | Enterprise; many consumers; want surgical updates |
| **Per-domain** (tokens, components, icons as separate packages) | Enterprise multi-platform output (web + native sharing tokens but not components) |

Record the choice in `docs/DECISIONS.md` and `docs/CONTRIBUTING.md`.

### Deprecation lifecycle

1. Mark component / token as deprecated (`[deprecated]` prefix, description starts with reason + replacement)
2. Ship at least one MINOR version with the deprecation marker visible to consumers
3. Provide replacement and migration note in `docs/MIGRATION-v{next-major}.md`
4. Remove in the next MAJOR release
5. Never remove without going through this sequence

### Changelog

Format: [Keep a Changelog](https://keepachangelog.com/). One section per release with subsections:

- **Added** — new features
- **Changed** — changes in existing functionality
- **Deprecated** — soon-to-be removed
- **Removed** — now removed
- **Fixed** — bug fixes
- **Security** — vulnerabilities

Mark BREAKING changes with ⚠️ and link to migration guide.

### Governance — RFC process (Enterprise)

Any change that touches: token semantics, component API, theme architecture, or affects ≥2 consumer teams — goes through RFC:

1. Open RFC document in `docs/RFCS/RFC-NNN-{slug}.md`
2. Sections: Motivation / Proposal / Alternatives Considered / Migration / Open Questions
3. Comment period: 5 working days minimum
4. Decision: Accepted / Rejected / Deferred — recorded in `docs/DECISIONS.md`
5. Accepted RFCs become work items in the roadmap

### Governance — working group (Standard+)

- One DS lead (owner; final call when disagreement persists)
- Cross-functional contributors (design + eng + at least one consumer team rep)
- Weekly or bi-weekly triage of issues and proposals
- Quarterly retrospective: what worked, what didn't, metric review (adoption, time-to-feedback, open issues)

### Adoption metrics (Enterprise)

Track to know if the DS is healthy:

- **Coverage**: % of product UI built from DS components (target: >70%)
- **Drift**: count of hardcoded values found in consumer apps (target: trending down)
- **Time-to-feedback**: hours from a question raised to an answer in DS channel
- **Open issues / age**: shouldn't grow unboundedly

---

## 15. Testing Layers (Standard+)

Verify gates (§9) are process-level. Tests are continuous quality protection after release.

### L1 — Visual regression

Every component, every variant, captured as a baseline image. Re-run on every PR.

- **Tools**: Storybook + Chromatic, or Storybook + Playwright snapshots, or Percy
- **Coverage**: every story; both themes; both LTR and RTL (if supported); at small/medium/large viewport for responsive components
- **Approval flow**: visual diff triggers human review; intended changes are approved and become new baseline; unintended changes block merge

### L2 — Accessibility automated

Every story passes axe-core or equivalent.

- **Tools**: `@storybook/addon-a11y`, `jest-axe`, `axe-playwright`
- **Coverage**: every story; both themes
- **Caveat**: axe-core catches roughly 30–57% of WCAG issues — necessary but not sufficient. Pair with manual checks at Enterprise tier.

### L3 — Interaction tests

Keyboard navigation, focus management, ARIA state updates.

- **Tools**: Storybook play functions; Testing Library; Playwright component tests
- **Coverage**: every interactive component — at minimum a "keyboard happy path" test

### L4 — Cross-theme parity

Same component renders correctly in every supported theme. Differences are intentional (color), not structural (broken layout).

- Run L1 visual regression across all themes
- Visually inspect for shadows disappearing, contrast failing, hardcoded colors leaking

### L5 — Token contract tests

Static analysis on the token files.

- No circular references
- No orphan tokens (defined but unconsumed)
- All semantic tokens reference existing primitives
- DTCG schema validation passes
- No two tokens resolve to the same final value with different intents (warns, doesn't block)

### Manual layer (Enterprise)

- **Screen reader passes** with NVDA (Windows) and VoiceOver (macOS + iOS) before every MAJOR release
- **Keyboard-only user test** — full task flow without a mouse
- **High-contrast mode test** on Windows
- **200% zoom** check — content reflows, nothing clips

---

## 16. Theming Architecture (Standard+)

### Single theme (Lean)

One set of primitives, one set of semantic aliases. Done.

### Light + Dark (Standard)

One set of primitives shared across both themes. Two sets of semantic aliases — each maps to potentially different primitives.

```
primitives (one set)
  neutral/0..1000, brand/50..900, …

semantic (two sets)
  [light theme]
    bg/surface     → neutral/0
    text/primary   → neutral/900
    border/focus   → brand/600
  [dark theme]
    bg/surface     → neutral/900
    text/primary   → neutral/50
    border/focus   → brand/400
```

Components reference semantic only; theme swap = swap of which alias set is active.

### Multi-brand / White-label (Enterprise)

Architecture: **core + brand-theme [+ sub-brand-theme]**.

```
LAYER A — Core primitives (shared across all brands)
  neutral/0..1000 (rarely varies)
  spacing scale, radius scale, motion scale (rarely vary)

LAYER B — Brand-specific primitives (varies per brand)
  brand/50..900 — different hue per brand
  font/family/sans — different brand font
  radius scale (some brands prefer sharper or rounder)

LAYER C — Core semantic aliases (shared logic)
  bg/surface, text/primary, action/primary/default, …
  Mapping logic identical; values differ because Layer B differs

LAYER D — Brand override aliases (optional, per brand)
  Override a specific alias only when the standard mapping does not fit
  e.g. brand X wants action/primary/hover to be a tint, brand Y wants a shade

LAYER E — Sub-brand overrides (optional, per sub-brand)
  Final tweaks; should be minimal
```

Components consume Layer C / D / E aliases only. The same component renders correctly for every brand.

### Density modes (Enterprise, orthogonal axis)

Independent of theme/brand. Mode swaps spacing aliases:

```
[comfortable]
  space/component/md → spacing/md (16px)
[compact]
  space/component/md → spacing/sm (12px)
[spacious]
  space/component/md → spacing/lg (24px)
```

Components don't care which mode is active; semantic spacing tokens carry the abstraction.

### Theme switching at runtime

Recommended: `data-theme` attribute on `<html>` or root container; CSS reads `:root[data-theme="dark"] { … }` to swap variable values. No JavaScript per-component logic needed.

### Theme parity rule

Every component must pass visual regression and a11y checks in every supported theme. If a component looks wrong in one theme — it's the theme that needs an alias adjustment, not the component.

---

## 17. Internationalization & RTL

### Scope

This methodology covers what a DS must do; full i18n (date formats, plural rules, currency) is product-level.

### What DS must provide

- **Logical CSS properties** in components: `padding-inline-start` not `padding-left`; `margin-block-end` not `margin-bottom`. Auto-mirrors in RTL contexts.
- **Direction-aware icons**: arrows, chevrons, progress indicators must flip in RTL. Text-content icons must not flip (e.g., a checkmark stays a checkmark).
- **Font fallback stacks** per script if the product targets non-Latin scripts: separate `font/family/sans` overrides for CJK, Arabic, Hebrew, Cyrillic if needed. Brand font may not cover all scripts.
- **Line-height tuning** for scripts with taller glyphs (Arabic, Devanagari) — a single `line-height: 1.5` may clip ascenders.
- **Number direction**: numbers stay LTR even in RTL text (use `<bdi>` or `unicode-bidi: isolate`).

### Quality Gate

QG-13 (already in §11): RTL renders correctly for every component that ships.

---

## 18. Performance Budget (Enterprise)

### Why

A DS that ships 800 KB of JS for an 8 KB component is broken. Performance budgets keep growth honest.

### Budgets

| Metric | Lean / Standard | Enterprise |
|---|---|---|
| Per-component JS (gzipped) | track only | hard cap, e.g. 5 KB |
| Total DS bundle (full import) | track only | hard cap, e.g. 80 KB |
| CSS variables count | informational | hard cap, e.g. 600 |
| Icon set, total | track only | hard cap; icons should be tree-shaken |

### Enforcement

- CI step that fails the PR if the budget is exceeded
- Visible budget delta in PR description (auto-comment)
- Quarterly budget review — adjust based on real product needs

### Anti-patterns

- Importing the whole icon library when only 12 icons are used
- Components that pull a heavy dependency for one helper (replace with local utility)
- Repeating the same SVG inline instead of `<use>` referencing a sprite

---

## Anchor

```
[*] DS-METHODOLOGY.md v2.0
Universal Design System methodology — tools-agnostic, framework-agnostic.
Tier-aware (Lean / Standard / Enterprise). DTCG v2025.10 compatible.
Derived from v1.0 + 2025 industry research (DTCG, WCAG 2.2, Brad Frost,
Carbon, Material 3, Atlassian, Tetrisly, Photon).
Sections: principles → tiers → pipeline → tokens → components →
extraction → visual patterns → mobile patterns → a11y → header blocks →
workflow → validation → anti-patterns → quality gates → knowledge base →
boundaries → versioning → testing → theming → i18n → performance.
```
