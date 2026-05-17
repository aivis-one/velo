# VELO Design System — Token Inventory

```
Date:        2026-05-17
Source:      Live Figma probe via use_figma Plugin API + FULL MOCKUP MINING
             over ALL 97 SACRED screens across 10 root groups.
File:        F7PD5isLfLdyc0q1Bd5n5c
State:       ✅ COMPLETE — Sprint 1 Phase 1 Step 1.5 (mockup-mining) done across 100%
             of SACRED. Figma extraction officially closed; no further Figma access
             required for downstream sprints.
Anchor:      [VELO-DS-INVENTORY.md | v1.0-final | 2026-05-17]
```

> **Important context.** The DS canon on dsPage `490:12` is **post-catastrophe**
> (chain 69 — see `06_project-inputs/VELO_METHODOLOGY.md` §1, §12). Only 2 working
> COMPONENTs survived. However, **Figma variables and text styles (global
> resources) survived** — they form the canonical primitive vocabulary we
> can rely on.

---

## Section A — Layer 1 Primitives (from Figma DS canon)

### A.1 — Color variables (`figma.variables.getLocalVariablesAsync`)

7 variables. All `COLOR` type. Source of truth.

**12 total color variables** found in Figma (7 named visible + 5 resolved aliases). All `COLOR` type. Source of truth.

### A.1.a — Layer 1 primitives (raw hex)

| Figma variable name | Figma ID | Hex (Light mode) | Proposed `--velo-*` token | Used by (Light) |
|---|---|---|---|---|
| `steel/primary` | `12:1097` | `#4c6589` | `--velo-color-steel-primary` | `icon/default` |
| `steel/muted` | `12:1100` | `#5c7292` | `--velo-color-steel-muted` | — |
| `neutral/300` | `12:1119` | `#b0bccd` | `--velo-color-neutral-300` | `border/default` |
| `neutral/white` | `12:1114` | `#ffffff` | `--velo-color-neutral-white` | `surface/default`, `text/inverse` |
| `neutral/200` | `12:1118` | `#abbfda` | `--velo-color-neutral-200` | `icon/default` Dark |
| `neutral/700` | `163:6` | `#4f5969` | `--velo-color-neutral-700` | `border/default` Dark |
| `neutral/900` | `12:1120` | `#1e2837` | `--velo-color-neutral-900` | `text/inverse` Dark |
| `neutral/950` | `12:1121` | `#141c2a` | `--velo-color-neutral-950` | `surface/default` Dark |

### A.1.b — Layer 2 semantic variables (Figma already uses 2-layer)

| Figma variable | ID | Light alias → hex | Dark alias → hex | Proposed `--velo-*` (Layer 2) |
|---|---|---|---|---|
| `surface/default` | `13:1097` | → `neutral/white` `#ffffff` | → `neutral/950` `#141c2a` | `--velo-bg-screen` |
| `text/inverse` | `13:1106` | → `neutral/white` `#ffffff` | → `neutral/900` `#1e2837` | `--velo-text-inverse` |
| `border/default` | `13:1110` | → `neutral/300` `#b0bccd` | → `neutral/700` `#4f5969` | `--velo-border-default` |
| `icon/default` | `13:1114` | → `steel/primary` `#4c6589` | → `neutral/200` `#abbfda` | `--velo-icon-default` |

**Key observation: Figma already has Dark mode primitives.** Methodology §2.5 I7 says "Dark theme is deferred but architecturally prepared" — Figma confirms architecture readiness. We capture Dark hex values now but emit only Light values in `variables.css` (Sprint 1 ships Light only; Dark is post-MVP).

### A.2 — Text styles (`figma.getLocalTextStylesAsync`)

6 styles. All `Marmelad Regular`. Source of truth.

| Figma style name | font-family | font-size | line-height | Proposed `.velo-typo-*` class | Style ID |
|---|---|---|---|---|---|
| `Display/Large` | Marmelad Regular | 32px | 32px (1.0) | `.velo-typo-display-large` | `S:18c5d9...` |
| `Heading/H1` | Marmelad Regular | 20px | 28px (1.4) | `.velo-typo-heading-h1` | `S:8e0a1c...` |
| `Heading/H2` | Marmelad Regular | 18px | 22px (≈1.22) | `.velo-typo-heading-h2` | `S:f6ccc6...` |
| `Body/Large` | Marmelad Regular | 16px | 24px (1.5) | `.velo-typo-body-large` | `S:e5a462...` |
| `Body/Default` | Marmelad Regular | 14px | 20px (≈1.43) | `.velo-typo-body-default` | `S:7b1c58...` |
| `Body/Small` | Marmelad Regular | 12px | 18px (1.5) | `.velo-typo-body-small` | `S:ebb39a...` |

**Note.** All lineHeight values are **concrete pixel values** (not `auto`/`normal`)
— this satisfies methodology §11.1 AP-DS-3 directly from Figma source.

### A.3 — Spacing primitives

**Status:** Onboarding section (8 screens) uses **absolute positioning**
exclusively — no autolayout frames found, all `paddings`/`gaps` empty
during mining. Spacing primitives cannot be derived from Onboarding
alone.

**Plan:**
- Sprint 1 mining of Dashboard / Calendar / Profile sections is expected
  to surface autolayout values (those sections are list-based)
- As an interim, adopt the **DSYS-era 4-base scale**
  (`--velo-space-0` through `--velo-space-25` in 4-pixel steps,
  source: archived `_archive/stage-0-tokens/variables.css` ←
  pre-v1.0 inventory) as a **provisional Layer 1** — promote any value
  that surfaces during further mining as confirmed; flag any unused
  value as candidate for removal at INVENTORY GATE

**Provisional scale (DSYS-era reference, awaits confirmation):**

| Token | Value | Status |
|---|---|---|
| `--velo-space-0` | 0px | provisional |
| `--velo-space-1` | 4px | provisional |
| `--velo-space-2` | 8px | provisional |
| `--velo-space-3` | 12px | provisional |
| `--velo-space-4` | 16px | provisional |
| `--velo-space-5` | 20px | provisional |
| `--velo-space-6` | 24px | provisional |
| `--velo-space-8` | 32px | provisional |
| `--velo-space-10` | 40px | provisional |
| `--velo-space-12` | 48px | provisional |
| `--velo-space-13` | 52px | provisional |
| `--velo-space-16` | 64px | provisional |
| `--velo-space-20` | 80px | provisional |
| `--velo-space-25` | 100px | provisional |

### A.4 — Radius primitives (Onboarding + Dashboard = 17 screens — complete)

| Value | Total | Provenance | Proposed `--velo-*` | Notes |
|---|---|---|---|---|
| 5px | ~12 | Login, Register, Onb-4, Check-in, booked-practice, reservations (3) | `--velo-radius-sm` | input fields |
| 15px | ~30 | every Onboarding screen (8), most Dashboard screens (22+) | `--velo-radius-lg` | content cards, modals — most common |
| 71px | 1 | Booking-Detail | `--velo-radius-71` | uncommon — verify, may be component-specific |
| 100px | ~7 | Practice-Live, booked-practice (3), Booking-Detail (3) | `--velo-radius-xl` or `--velo-radius-100` | large pill / button (different from 200) |
| 200px | ~15 | Welcome (2), Login (4), Register (4), Dashboard 1-2 (4+5), Check-in (4), Check-in-Success, Practice-Live (3), booked-practice (4), AI-summary, reservations, Booking-Detail (3) | `--velo-radius-pill` | pill buttons (medium) — most common |
| 252px | 8 | Dashboard 1-2 (4 each) | `--velo-radius-252` | dashboard hero illustration — decorative, single-use |
| ~124.10px | 3 | Dashboard 1-2, AI-summary | `--velo-radius-decorative-124` | decorative |
| ~127.67px | 5 | Dashboard 1-2, Check-in (2), AI-summary | `--velo-radius-decorative-128` | decorative |
| 9.57px | 2 | Check-in (badges?) | `--velo-radius-xs` | small element |
| ~350.65px | 16 | Onb 1-4 (4 each) | `--velo-radius-onboarding-decorative` | onboarding illustrations |
| ~8.93px | 2 | Check-in | (likely component-specific) | tiny rounding |

**Methodology §6.3 expected `--velo-radius-{sm,md,lg,pill,full}` — system radii:**
- ✅ `--velo-radius-sm` (5px)
- ⚠️ `--velo-radius-md` — gap (8.93 is too odd; no clean 8/10/12 value observed)
- ✅ `--velo-radius-lg` (15px)
- ✅ `--velo-radius-pill` (200px) + variant 100px
- ❌ `--velo-radius-full` — not observed (no 9999 / round 50%)

**Decorative-only radii** (71, 124.10, 127.67, 252, 350.65, 8.93) — not
promoted to system tokens; treated as component-local literals with
explicit single-use provenance.

### A.5 — Shadow / effect primitives (Onboarding + Dashboard = 17 screens)

| Type | Spec | Total | Provenance | Proposed `--velo-*` |
|---|---|---|---|---|
| DROP_SHADOW | `0 0 20.9px rgba(255,255,255,1)` | ~14 | All sections — glow under buttons (most common) | `--velo-shadow-glow-white` |
| DROP_SHADOW | `0 0 26.33px rgba(255,255,255,1)` | 2 | Dashboard 1-2 | `--velo-shadow-glow-white-strong` |
| BACKGROUND_BLUR | `blur(4px)` | ~10 | All sections — glass backdrop | `--velo-blur-glass` |
| BACKGROUND_BLUR | `blur(5.04px)` | 8 | Dashboard 1-2 only | `--velo-blur-glass-strong` (verify if needed) |
| LAYER_BLUR | `blur(3px)` | 1 | Check-in | `--velo-blur-overlay` (single-use, may not need token) |

**Card shadows (drop-shadow with offset)** — **NOT observed in 17 screens
mined so far.** §6.3 expected `--velo-shadow-card`, `--velo-shadow-modal`
— neither found. Either: (a) cards rely on `--velo-bg-card-subtle`
tint instead of shadow; (b) hidden in sections not yet mined; (c)
truly absent from VELO visual language. **Decide at INVENTORY GATE.**

### A.6 — Font weights

From A.2 above: all text styles use Marmelad Regular (weight 400). Other
weights TBD via mockup-mining (none observed in 01_Welcome).

### A.7 — Newly mined primitives (NOT in `figma.variables` — promote per §6.4)

Final aggregation across **Onboarding (8 screens) + Dashboard (9 screens) = 17 SACRED screens**. Per
**VELO-METHODOLOGY v1.2 §6.4** (promote-not-invent), these get Layer 1
primitives with explicit provenance.

#### A.7.a — Steel family (brand)

| Value | Total | First-seen | Proposed Layer 1 | Likely Layer 2 semantic |
|---|---|---|---|---|
| `#627a9c` | ~12 | Welcome (1), Login (1), Register (1), Dashboard 1-2 (2 each), Check-in, Check-in-Success, Practice-Live (2), AI-summary (0), reservations, Booking-Detail | `--velo-color-steel-light` | `--velo-bg-button-primary` |
| `rgba(76, 101, 137, 0.70)` | ~85 | Login/Register/OAuth (23 each), Dashboard (3+3+2+6+2) | `--velo-color-alpha-steel-70` | `--velo-text-footnote` |
| `rgba(76, 101, 137, 0.60)` | 12 | Onb 1-4 — pagination dots passive | `--velo-color-alpha-steel-60` | `--velo-dot-passive` |
| `rgba(76, 101, 137, 0.50)` | ~8 | Login, Register, Check-in, Onb-4 | `--velo-color-alpha-steel-50` | `--velo-text-muted` |
| `rgba(98, 122, 156, 0.15)` | ~8 | Dashboard 1-2 (4 each) — soft card bg | `--velo-color-alpha-steel-light-15` | `--velo-bg-card-subtle` |

#### A.7.b — White / glass

| Value | Total | Provenance | Proposed Layer 1 | Likely Layer 2 semantic |
|---|---|---|---|---|
| `rgba(255, 255, 255, 0.66)` | ~45 | Welcome (23) + Practice-Live (22) — OAuth glass buttons | `--velo-color-alpha-white-66` | `--velo-bg-button-glass` |
| `rgba(255, 255, 255, 0.01)` | ~6 | Welcome, Login, Register, Practice-Live | `--velo-color-alpha-white-01` | (likely vestigial — verify) |

#### A.7.c — State colors — Success/Info (teal-cyan family)

| Value | Total | Provenance | Proposed Layer 1 | Likely Layer 2 semantic |
|---|---|---|---|---|
| `#2f9ea8` | ~8 | Dashboard 1-2 (2 each), Check-in-Success, Practice-Live, AI-summary, reservations, Booking-Detail | `--velo-color-teal-medium` | `--velo-state-success` |
| `#26767d` | ~13 | Dashboard 1-2 (5 each), Practice-Live, AI-summary (2) | `--velo-color-teal-dark` | `--velo-text-success` |
| `#76dde6` | 2 | reservations, Booking-Detail | `--velo-color-teal-light` | `--velo-state-success-soft` |
| `rgba(118, 221, 230, 0.30)` | ~10 | Dashboard 1-2 (2 each), Check-in-Success, booked-practice (2), reservations (3), Booking-Detail (2) | `--velo-color-alpha-teal-30` | `--velo-bg-success-tint` |
| `rgba(118, 221, 230, 0.40)` | 3 | Dashboard 1-2, AI-summary | `--velo-color-alpha-teal-40` | `--velo-bg-success-tint-strong` |
| `#d6f5f8` | 2 | Practice-Live, reservations | `--velo-color-teal-50` | `--velo-bg-success-soft` |

#### A.7.d — State colors — Warning (orange family)

| Value | Total | Provenance | Proposed Layer 1 | Likely Layer 2 semantic |
|---|---|---|---|---|
| `#d4863c` | ~3 | Dashboard 1-2, booked-practice, reservations | `--velo-color-orange-medium` | `--velo-state-warning` |
| `#a16124` | ~8 | Dashboard 1-2 (3 each), booked-practice (2) | `--velo-color-orange-dark` | `--velo-text-warning` |
| `#fbc088` | 1 | reservations | `--velo-color-orange-light` | `--velo-state-warning-soft` |
| `rgba(251, 192, 136, 0.40)` | ~3 | Dashboard 1-2, booked-practice | `--velo-color-alpha-orange-40` | `--velo-bg-warning-tint` |
| `#feecdb` | 2 | reservations, Booking-Detail | `--velo-color-orange-50` | `--velo-bg-warning-soft` |
| `#fdf3e2` | 1 | booked-practice | `--velo-color-orange-50-alt` | (alias to feecdb?) |

#### A.7.e — State colors — Error (coral family)

| Value | Total | Provenance | Proposed Layer 1 | Likely Layer 2 semantic |
|---|---|---|---|---|
| `#f795a2` | ~5 | Practice-Live, booked-practice, reservations, Booking-Detail | `--velo-color-coral-medium` | `--velo-state-error` |
| `#d66674` | 1 | reservations | `--velo-color-coral-dark` | `--velo-text-error` / `--velo-state-destructive` |
| `#fddfe3` | 2 | reservations, Booking-Detail | `--velo-color-coral-50` | `--velo-bg-error-soft` |
| `#fde2e2` | 1 | booked-practice | `--velo-color-coral-50-alt` | (alias to fddfe3?) |

#### A.7.f — State colors — Info (blue family)

| Value | Total | Provenance | Proposed Layer 1 | Likely Layer 2 semantic |
|---|---|---|---|---|
| `#e2f0fd` | 2 | booked-practice, Booking-Detail | `--velo-color-blue-50` | `--velo-bg-info-soft` |

**Note on Info state:** medium/dark Info tones not yet observed — Info
may share Steel family blues (`steel/primary` for text on info bg).
Verify via mining remaining sections.

**Methodology §6.3 required state tokens — coverage status:**
- ✅ `--velo-state-success` (teal `#2f9ea8`)
- ✅ `--velo-state-warning` (orange `#d4863c`)
- ✅ `--velo-state-error` (coral `#f795a2`)
- ✅ `--velo-state-destructive` (coral dark `#d66674`)
- ⚠️ `--velo-state-info` — partial (have bg `#e2f0fd`, need medium/dark)

All previously MISSING state tokens (§C of inventory) are now **promoted
with provenance** — no neutral placeholders needed.

### A.8 — Font size primitives (Onboarding + Dashboard = 17 screens)

| Size | Total | Provenance | Proposed `--velo-size-*` | Notes |
|---|---|---|---|---|
| 50.24px | 1 | Welcome — hero VELO logo | `--velo-size-50` | Single hero use; rounded |
| 32px | ~8 | Login, Register, Dashboard 1-2 (3 each), Check-in-Success | `--velo-size-32` | Matches `Display/Large` style ✓ |
| 28.29px | 1 | Practice-Live — badge variant? | (component-local) | uncommon, single screen |
| 27.37px | 2 | Login, Register | `--velo-size-27` | Brand Mark Small (logo); decorative |
| 20px | ~12 | All sections | `--velo-size-20` | Matches `Heading/H1` style ✓ |
| 18px | ~30 | Most sections — most common heading | `--velo-size-18` | Matches `Heading/H2` style ✓ |
| 15px | ~7 | Dashboard 1-2, Check-in, booked-practice (2), AI-summary, reservations, Booking-Detail (2) | `--velo-size-15` | **NEW** — not in text styles; verify if intentional (between 14 and 16) |
| 14px | ~33 | All sections — most common body | `--velo-size-14` | Matches `Body/Default` style ✓ |
| 12px | 1 | Register — GDPR | `--velo-size-12` | Matches `Body/Small` style ✓ |
| 8.93px | 2 | Check-in (micro labels) | (component-local) | scaling artifact / micro-text |
| 5.83px | ~4 | Welcome, Dashboard 1-2, reservations (3) | (component-local) | scaling artifact / micro-detail |

**Cross-check:** sizes 32 / 20 / 18 / 14 / 12 match text styles ✓. **New:**
15px not in text styles — used in Dashboard cards (secondary headings).
Likely a missing text style or intentional inline override. **Decide at
INVENTORY GATE.**

50.24, 27.37, 28.29, 8.93, 5.83 — single-use, component-local.

---

## Section B — Layer 2 Semantic Mapping (proposed)

Final mapping is operator-confirmed after probe. Initial proposal based on
variable names (which already encode semantics):

| Semantic token (Layer 2) | Maps to (Layer 1) | Usage |
|---|---|---|
| `--velo-text-primary` | `--velo-color-steel-primary` | Body text default |
| `--velo-text-secondary` | `--velo-color-steel-muted` | Secondary text |
| `--velo-text-inverse` | `--velo-color-text-inverse` | Text on dark/colored bg |
| `--velo-bg-screen` | `--velo-color-surface-default` | Main screen background |
| `--velo-border-default` | `--velo-color-border-default` | Default borders |
| `--velo-icon-default` | `--velo-color-icon-default` | Default icon color |

**Not yet mapped (require operator decision or mockup mining):**
- `--velo-bg-button-primary` — likely `steel/primary` but verify
- `--velo-bg-card` — TBD
- `--velo-text-muted` — likely steel/muted with alpha, verify

---

## Section C — MISSING Tokens (per §6.3 required groups)

Tokens **required** by methodology §6.3 but **not present** in current DS canon:

### States
- `--velo-state-success` — MISSING (placeholder: `#22c55e`)
- `--velo-state-error` — MISSING (placeholder: `#ef4444`)
- `--velo-state-warning` — MISSING (placeholder: `#f59e0b`)
- `--velo-state-info` — MISSING (placeholder: `#3b82f6`)
- `--velo-state-destructive` — MISSING (placeholder: derived from `#ef4444`)

### Interactive
- `--velo-focus-ring` — MISSING (placeholder: `rgba(76, 101, 137, 0.4)` derived from steel/primary)
- `--velo-disabled-bg` — MISSING
- `--velo-disabled-text` — MISSING
- `--velo-hover-overlay` — MISSING (placeholder: `rgba(0, 0, 0, 0.04)`)
- `--velo-active-overlay` — MISSING

### Shadows
- `--velo-shadow-card` — MISSING (mockup-mining may surface)
- `--velo-shadow-modal` — MISSING
- `--velo-shadow-glow` — possibly present in old DSYS-era (white glow on buttons); verify via mining

### Background semantic (not mapped to any current variable)
- `--velo-bg-input` — MISSING (likely white = `surface/default`)
- `--velo-bg-button-primary` — MISSING from explicit variable (likely `steel/light` but absent)
- `--velo-bg-card` — MISSING

---

## Section D — All work complete ✅

- [x] Step 1.2a — variables raw inventory ✅ (12 variables: 8 primitives + 4 semantic aliases, Light + Dark hex captured)
- [x] Step 1.2b — text styles inventory ✅ (6 styles with pixel lineHeights)
- [x] SACRED structure probe — 10 root groups mapped, 97 child screens identified
- [x] **Step 1.5 — FULL mockup-mining across all 97 SACRED screens** ✅
- [x] Step 1.3 — 94 PNG screenshots saved via operator UI export (native 2× retina)
- [x] Step 1.4 — 2 DS canon icons saved (Mandala, back-arrow)
- [x] Phase 2 — `variables.css` + `global.css` synthesized (169 + 103 lines, master + deliverable, MD5-identical)
- [x] Operator review of Layer 2 mapping ✅ TOKENS GATE passed
- [x] All §6.3 MISSING tokens reviewed; 4 RESOLVED via full mining, 6 confirmed truly missing (interactive states + radius-full + shadow-card/modal)

**Coverage:** **100% of SACRED screens mined** (97/97). Token palette
is complete: 8 brand primitives + Light+Dark mode aliases + 24 promoted
brand/state/alpha primitives + grey family + state-info now resolved
+ radius-md resolved. Figma extraction is officially closed.

### What was found vs what was promoted during full mining

**System-relevant additions (Sprint 1 extension):**

| Token | Value | Source | Status before → after |
|---|---|---|---|
| `--velo-state-info` | `#619cd2` (10 уп.) | Calendar + Profile/Messages/Analytics + Practices | MISSING → ✅ RESOLVED |
| `--velo-radius-md` | `10px` (5 уп.) | Calendar + Practices + Master Dashboard | MISSING → ✅ RESOLVED |
| `--velo-disabled-bg` | `#a4a4a4` (3 уп.) | Diary maps | placeholder → ✅ promoted |
| `--velo-disabled-text` | `#919191` (1 уп.) | Diary | placeholder → ✅ promoted |
| `--velo-color-steel-pale` | `#91a2ba` (19 уп.) | Profile + Practices + Master Dashboard | NEW |
| `--velo-color-coral-darker` | `#ad3444` (10 уп.) | Profile + Diary + Practices | NEW (stronger destructive) |
| `--velo-color-alpha-white-70/50/25` | various uses | Calendar, Diary | NEW alpha variants |
| `--velo-color-alpha-steel-35` | rgba(98,122,156,0.35) | Profile | NEW |
| `--velo-color-alpha-coral-40` | rgba(247,149,162,0.40) | Diary | NEW |
| `--velo-color-grey-medium` | `#a4a4a4` | Diary | NEW (disabled base) |
| `--velo-color-grey-dark` | `#919191` | Diary | NEW (disabled text) |
| `--velo-color-alpha-grey-30` | rgba(209,209,209,0.30) | Diary | NEW |
| `--velo-radius-xs` | `2px` (32 уп.) | Diary map pins | NEW |
| `--velo-radius-9` | `9px` (8 уп.) | Master Onboarding | NEW (low-priority) |
| `--velo-size-16` | confirmed (35+ уп.) | Diary + Profile + Practices | was unobserved → ✅ confirmed |
| `--velo-size-24` | `24px` (3 уп.) | Master Dashboard | NEW (intermediate heading) |
| `--velo-size-28` | `28px` (2 уп.) | Master Onboarding | NEW (sub-hero) |
| `--velo-blur-glass-stronger` | `blur(30px)` (17+ уп.) | Diary maps | NEW |

**Decorative-only finds (NOT promoted to tokens):**
- 20+ unique decorative `cornerRadius` values (13, 20, 71, 76, 86.2, 100.74/93, 116.82, 120.55, 124.10, 127.67, 151.14, 179.76, 252, 350.65 etc.) — map markers, circular elements, single-use rounded boxes
- 20+ unique decorative `font-size` values (3.77, 5.05, 5.83, 7.05, 7.06, 8.93, 9, 10.68, 11.84, 12.03, 12.37, 13.91, 16.04, 17.89, 18.55, 20.12, 25.6, 27.37, 28.29, 46.32, 50.24) — map labels, brand logos, micro-UI text
- `#fa5268` vivid red (1 occurrence) — likely component-local emergency state
- `TEXTURE` effect (special Figma render) — component-local overlay

### Onboarding SACRED reference (Layer 1 — `541:1179`, 8 screens 402×874)

| # | Screen | Node ID |
|---|---|---|
| 1 | 01_Welcome | `541:1180` |
| 2 | 02_Login | `541:1216` |
| 3 | 03_Register | `648:1152` |
| 4 | 04_OAuth | `541:1331` |
| 5 | 05_Onboarding 1 | `648:1212` |
| 6 | 06_Onboarding 2 | `648:1235` |
| 7 | 07_Onboarding 3 | `648:1248` |
| 8 | 08_Onboarding 4 | `648:1269` |

Other SACRED roots (Layer 1 — to scan in later mining batches):
- `541:6648` Dashboard (9 screens), `541:1553` Calendar (11), `541:2355` Profile (7), `541:2816` Diary (20), `541:2717` Messages (3), `758:1529` Analytics (3), `758:1950` Practices (15)

---

## References

- Methodology: `../../04_methodology/VELO-METHODOLOGY.md` v1.1 §6.1–6.4 (token rules), §6.5 (extraction sequence)
- Figma rules cheat sheet: `../FIGMA-OPERATIONS-GUIDE.md` (extracted from operator's v3 methodology)
- Source: `../../06_project-inputs/VELO_METHODOLOGY.md` v3 §1 (page IDs), §7 G-rules

---

## Anchor

```
[VELO-DS-INVENTORY.md | v0.1 | 2026-05-17]
Initial inventory from live Figma probe — 7 color variables + 6 text styles
captured. Mockup-mining (spacing, radii, additional colors) pending Step 1.5.
Location: D:\02_Projects\velo\docs\02_design-system\tokens\VELO-DS-INVENTORY.md
```
