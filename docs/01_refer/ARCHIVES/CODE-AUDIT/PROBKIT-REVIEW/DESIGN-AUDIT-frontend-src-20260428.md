# Design Audit Report — Velo (VELΘ)

Date: 2026-04-28
Target: `frontend/src` (140 source files; 87 .vue + 42 .ts + 11 SVG/CSS)
Token file: `frontend/src/styles/variables.css` (291 lines, 130 tokens)
Brand reference: `docs/02_spec_assets/velo-design-system-2026-04-23/project/README.md` (bundle SSOT per #006)

---

## Summary

| Probe | Status | Findings |
|-------|--------|----------|
| P1 Hardcoded Colors | WARN | 8 rgba + 30 named-color sites |
| P2 Font Compliance | PASS | 0 |
| P3 Spacing Tokens | WARN | ~15 hardcoded px values |
| P4 Radius Tokens | WARN | ~21 hardcoded px values (12 × `5px` + 8 × `100px` + 1 × `20px`) |
| P5 Shadow Tokens | WARN | 1 (VToast) |
| P6 Dark Mode | PASS | 32-token override block at variables.css:250-291 ✓ |
| P7 Logo Icon Color | n/a | CBS-HOME-specific; Velo uses VELΘ wordmark from `/icons/logo*.svg` (no inline color) |
| P8 Token Sync (vs bundle) | PASS | 130 vs 101 tokens; +29 documented Velo extensions per #020/#021 |

**Findings**: 0 🔴 / 5 🟡 / 0 🟢 / 1 💎 (P6/P8 clean = combined into «sound architecture»).

**Verdict**: design-token discipline is good at the architecture level — bundle SSOT (#006) intact, dark-mode complete (#008), project-extension pattern formalized (#021), admin-deferred markers in place (#020). The gap is in **inline value density** within view styles: ~75 sites use hardcoded px values where tokens exist. Mechanical refactor opportunity.

**Step 3 PR shape**: 1-2 «design-token compliance» cycles in S2.

---

## P1 — Hardcoded Colors (CRITICAL)

### 🟡 WARNING — `rgba()` outside variables.css (8 sites)

| File | Line | Value | Suggested fix |
|---|---|---|---|
| `views/user/UserProfileView.vue` | 313 | `rgba(255, 255, 255, 0.3)` | use a `--surface-overlay-*` token (or add new) |
| `views/user/UserProfileView.vue` | 317 | `rgba(255, 255, 255, 0.1)` | same |
| `views/master/MasterPracticesView.vue` | 244 | `rgba(255, 255, 255, 0.3)` | same |
| `components/layout/VTabBar.vue` | 57 | `rgba(255, 255, 255, 0.85)` | consider `--surface-elevated` or new `--surface-tabbar-bg` |
| `components/ui/VModal.vue` | 101 | `rgba(0, 0, 0, 0.5)` | could be `--surface-overlay-50` token |
| `views/master/AttendanceView.vue` | 506 | `rgba(0, 0, 0, 0.5)` | same — re-use VModal instead (DRY) |
| `views/master/EditPracticeView.vue` | 904 | `rgba(0, 0, 0, 0.5)` | same |
| `components/ui/VToast.vue` | 68 | `rgba(0, 0, 0, 0.3)` (in box-shadow) | use `--shadow-md` (P5 below) |

The two `views/master/*` overlay rgba sites duplicate VModal's overlay — refactor to reuse VModal would eliminate both (also a code-quality finding from code-audit Run 2 Section 6).

### 🟡 WARNING — CSS named color `white` (30 sites across 21 files)

`grep 'color:\s*white\|background:\s*white\|border-color:\s*white'` returns 30 matches. The probe lists `white` (CSS named color) as forbidden — must use `var(--neutral-white)` or `#ffffff`.

Note: the probe's allowed-list explicitly includes `#fff/#ffffff`; using bare `white` is the inconsistent point. Velo defines `--neutral-white: #ffffff` in `variables.css:26`. Mechanical replace:

```diff
- color: white;
+ color: var(--neutral-white);
```

Or, since `--neutral-white === #ffffff`, leaving as `#ffffff` is equally compliant per the probe definition.

Affected files (sample of high-impact):
- `components/layout/VTabBar.vue:79, 104` (active tab text)
- `components/layout/VHeader.vue:105` (header text)
- `components/ui/VButton.vue:103, 121` (primary/danger button text)
- `components/ui/VToggle.vue:54`, `VCheckbox.vue:83`, `VToast.vue:73,78,83`
- 22 view-level sites across master/, user/, admin/, auth/

**Severity**: 🟡 WARNING (style discipline; visually identical output; system-consistency cost).

### Confirms

- **No non-white/black hex** in `.vue` style blocks (other than `#ffffff`). `grep '#[0-9a-fA-F]{6}'` excluding `#ffffff`/`#000000` returns 0 real violations (2 false-positives are `#012`/`#013` decision references in comments — known regex limitation per BACKLOG #34).
- **No `rgb()`** outside variables.css — only `rgba()` cases above.
- **No `hsl()`/`hsla()`** anywhere in source — clean.
- **No CSS named colors** other than `white` (verified — `red|blue|green|gray|orange|...` returned 0 in style values, only in comments and component variant prop names like `<VTag color="blue">` which then map to tokens internally).

---

## P2 — Font Compliance (HIGH) — PASS

✓ All `font-family` declarations use `var(--font-body)`, `var(--font-heading)`, `var(--font-mono, monospace)`, `inherit`, or `monospace` (acceptable per probe definition for code blocks).

`@font-face { font-family: 'Marmelad' }` is in `variables.css` itself (allowed per probe — token-definition source).

2 `font-family: monospace` sites:
- `views/admin/AdminReportDetailView.vue:323` — likely report-ID code block
- `views/master/MasterProfileView.vue:594` — likely user-ID slug

Both acceptable per probe («monospace for code blocks»).

No findings.

---

## P3 — Spacing Tokens (MEDIUM)

### 🟡 WARNING — Hardcoded px values where tokens exist (~12 sites)

Token map (from `variables.css:142-201`):
- `--space-xs: 4px` / `--space-1: 4px`
- `--space-sm: 8px` / `--space-2: 8px`
- `--space-3: 14px`
- `--space-md: 16px` / `--space-4: 16px`
- `--space-lg: 24px` / `--space-5: 24px` / `--space-6: 24px`
- `--space-xl: 32px`

Hardcoded sites that should use tokens:

| File | Line | Hardcoded | Token |
|---|---|---|---|
| `components/layout/VHeader.vue` | 108 | `padding: 2px 8px` | partial: 2px allowed (border), 8px → `--space-sm`/`--space-2` |
| `components/ui/VBadge.vue` | 34-35 | `gap: 4px; padding: 4px 10px` | `gap: var(--space-xs); padding: var(--space-xs) ?` (10px has no token — keep or add) |
| `components/ui/VButton.vue` | 89, 95 | `padding: 8px 16px` (sm) / `12px 24px` (md) | `var(--space-sm) var(--space-md)` / `12px → no token; var(--space-lg)` |
| `components/ui/VTag.vue` | 34 | `padding: 4px 12px` | `--space-xs` / 12px no exact token |
| `components/ui/VToast.vue` | 60 | `padding: 12px 24px` | 12px / `--space-lg` |
| `components/ui/VToggle.vue` | 40, 44 | `padding: 2px;` `padding: 6px 16px` | 2px allowed; 6px no exact token; 16px → `--space-md` |
| `views/admin/AdminConsistencyView.vue` | 303 | `gap: 2px` | allowed (≤2px) |
| `views/master/AnalyticsView.vue` | 747 | `gap: 2px` | allowed |
| `views/master/MasterPracticesView.vue` | 248 | `padding: 1px 6px` | 1px allowed; 6px no token |
| `views/user/UserDashboardView.vue` | 696, 699 | `gap: 2px; padding: 2px` | allowed |

Allowed-by-probe (≤2px borders/gaps): 5 sites. Real violations: ~10. Most are `4/8/16/24px` which map directly to tokens.

`12px` and `6px` appear several times without exact-match tokens. Decision: either accept as project-magic-numbers OR introduce `--space-3xs: 6px` and `--space-2xs: 12px`. Recommend the latter as a token-set extension.

---

## P4 — Radius Tokens (MEDIUM)

### 🟡 WARNING — Hardcoded radius values where tokens exist (~21 sites)

Token map (from `variables.css:152-156`):
- `--radius-sm: 4px`
- `--radius-md: 8px`
- `--radius-lg: 15px` (canonical card radius)
- `--radius-xl: 24px`
- `--radius-full: 200px`

Violations:

| Pattern | Count | Files | Suggested token |
|---|---|---|---|
| `border-radius: 5px` | 12 | VInput, VSelect, VTextarea, VCheckbox, FormShell, BookingPopup, DiaryEntryForm, TopupView, EditPracticeView (×2), CreatePracticeView, MasterApplyView, MasterFinanceView | likely intended as `--radius-sm` (4px); 1px delta is visually negligible. **Bulk find/replace**. |
| `border-radius: 100px` | 8 | DiaryList, AnalyticsView, MasterDashboardView, MasterFinanceView, MasterPracticesView (×2), MasterProfileView, CalendarView, MyBookingsView | use `--radius-full` per #016 (200px renders identically below 64px elements). **Bulk fix**. |
| `border-radius: 20px 20px 0 0` / `20px` | 2 (VModal) | bottom-sheet rounding | use `--radius-xl` (24px) — visually identical below typical modal sizes |

**Severity**: 🟡 WARNING — token-system discipline. All 21 sites are mechanical fixes.

#### Confirms

- `border-radius: 50%` (3 sites in icons/avatars) — acceptable per probe (circular shapes).

---

## P5 — Shadow Tokens (MEDIUM)

### 🟡 WARNING — 1 hardcoded shadow

`components/ui/VToast.vue:68`:
```css
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
```

Velo defines `--shadow-md: 0 4px 12px rgba(0, 0, 0, 0.30);` (verified in `variables.css` dark-mode block; light-mode equivalent is in the main token set). This is a 1:1 match. Fix:

```diff
- box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
+ box-shadow: var(--shadow-md);
```

Also satisfies P1 (rgba) for this site. Single-line bulk fix.

---

## P6 — Dark Mode Completeness (HIGH) — PASS

### 💎 DIAMOND — Full dark-mode token override block

`variables.css:250-291` defines a complete `[data-theme="dark"]` override:
- 6 surface tokens (`--surface-{default,subtle,muted,elevated,overlay,inverse}`)
- 8 text tokens (including `--text-on-accent`, `--text-on-inverse`)
- 4 border tokens
- 4 icon tokens
- 3 accent tokens
- 6 shadow tokens
- `color-scheme: dark` declaration

Per `decisions.md` #008 the dark-mode UI toggle lands in C19 (S2) but tokens are deployed at S1 close so dark-theme is runtime-ready. ✓

#### Spot-check on usage

Components consistently use semantic tokens (`var(--text-primary)`, `var(--surface-default)`, `var(--border-strong)`) rather than primitive (`var(--neutral-900)`, `var(--steel-primary)`). Switching themes via `[data-theme="dark"]` propagates automatically. ✓

---

## P7 — Logo Icon Color (CRITICAL — adapted) — n/a

The original CBS-HOME P7 probe verifies `--o-primary` (#cc3203) on logo icon. This concept doesn't map to Velo:

- Velo brand identity is the **VELΘ wordmark in Marmelad font** + the **mandala backdrop**.
- `components/ui/VeloLogo.vue` uses `<img :src="logoSrc" alt="VELΘ">` where `logoSrc` is `/icons/logo.svg` or `/icons/logo-white.svg`. No inline color.
- Color of the logo SVG file itself is fixed inside the SVG asset (per `decisions.md` #024 — Vue-SVG baseline + bundle PNG decorative supplement).

Velo-equivalent of P7 would be: «verify VELΘ wordmark uses bundle Marmelad font and renders against `--surface-default` background». Both are satisfied by the bundle SSOT setup (#006).

**Verdict**: probe **not applicable** to Velo's brand layer; satisfied by architecture-level decisions.

---

## P8 — Token Sync (HIGH) — PASS

### Method

Compared `frontend/src/styles/variables.css` (130 tokens) against bundle `docs/02_spec_assets/velo-design-system-2026-04-23/project/colors_and_type.css` (101 tokens).

### Result

**Bundle ⊆ Velo**: every bundle token present in Velo. Velo extends with 29 documented additions:

| Extension category | Tokens | Authority |
|---|---|---|
| Font references | `--font-body`, `--font-heading` | application-level (bundle is pure tokens, not font-stack) |
| Project extensions (#021 alpha-surfaces) | `--nav-inactive-bg`, `--surface-{steel,teal,warm}-alpha-*` (5) | decision #021 explicit |
| Legacy spacing scale | `--space-1`..`--space-10` (8) | bundle uses `--space-{xs..4xl}`; Velo retains both for migration cleanliness |
| Legacy text scale | `--text-{xs,sm,base,lg,xl,2xl,3xl}` | parallel to bundle's letter scale |
| Layout sizes | `--size-option-btn-min`, `--size-practice-emoji`, `--size-success-icon` | view-specific component dimensions |
| Transitions | `--transition-{base,fast,slow}` | Velo extension |
| z-index scale | `--z-{background,content,dropdown,modal,popup,sticky,toast}` (7) | Velo extension |
| Admin-deferred (#020) | `--velo-{success,warning,error}-bg/border/text-light/etc.` (8) | decision #020 — Legacy section with marker comment block at lines 230-241 |

All 29 additions are intentional and documented. Either:
- Required by Velo's app-level architecture (font, transitions, z-index)
- Explicit decisions (#020 admin-deferred, #021 project-extension)
- Migration scaffolding (legacy spacing/text scales kept alongside bundle scale)

### 💎 DIAMOND — Token sync is healthy

Bundle SSOT (#006) is intact: zero bundle tokens missing or modified, and Velo's extensions are formally tracked. This is the cleanest token-sync state achievable for an MVP that has migrated from a pre-bundle namespace.

---

## False-positive avoidance — confirmed not flagged

Per Step 1+ guidance + decisions.md:

- **#017 Shadows permitted** — `box-shadow` with bundle `--shadow-*` tokens is allowed; only `backdrop-filter`/glassmorphism are forbidden. P5 only flagged the 1 hardcoded inline-rgba shadow in VToast, NOT box-shadow usage with tokens.
- **#019 CSS imports** — variables.css imported via `main.ts` line 16 (not via `@import` in CSS). Not relevant to design-token compliance per se; auditor did not flag.
- **#020 Admin-deferred legacy tokens** — `--velo-*` tokens at variables.css:234-241 are Velo extensions, not bundle violations. P8 confirms.
- **#021 Project-extension tokens** — `--nav-inactive-bg`, `--surface-{steel,teal,warm}-alpha-*` at variables.css:47-57 are documented extensions. P8 confirms.

---

## Step 3 Classification Suggestions

| Group | Findings | Effort |
|---|---|---|
| A. P4 radius bulk fix | 21 sites: 12 × `5px → --radius-sm`, 8 × `100px → --radius-full`, 1 × VModal `20px → --radius-xl` | 1 cycle, S |
| B. P3 spacing bulk fix + token additions | ~12 sites; consider adding `--space-2xs: 6px` and `--space-3xs: 12px` (or rename to fill gap) | 1 cycle, M |
| C. P1 named-color → token | 30 × `white → var(--neutral-white)` | 1 cycle, S (or skip if `white` is accepted as universal-constant equivalent of `#ffffff`) |
| D. P5 + P1 overlay tokens | VToast shadow → `--shadow-md`; VModal/AttendanceView/EditPracticeView overlay rgba → new `--surface-overlay-50` token | 1 cycle, S |
| E. P1 white-alpha tokens | UserProfile + MasterPractices + VTabBar `rgba(255,255,255, X)` → new `--surface-white-alpha-*` set | 1 cycle, S |

Combined: ~3-4 cycles. Could be a single «design-token bulk-tighten» cycle in S2 P05.

---

## Anchor

[*] design-audit v1.0.0 * report ready
[>] | NEXT: Run 7 (backender-review pass)
