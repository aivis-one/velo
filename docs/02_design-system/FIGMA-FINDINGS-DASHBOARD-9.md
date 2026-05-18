# Figma Audit — Dashboard 9 Block

Date: 2026-05-18
Probe: SACRED root `541:6648`, all 9 frames walked depth-first
Probe code: see Daily log of sprint-02.md (session 4 T2)

> What was probed: for every node in every Dashboard 9 frame — `fills`, `strokes`, `cornerRadius`, `effects` (shadows + blurs), `fontSize`, `fontFamily/style`, `letterSpacing`. Values deduplicated and counted. Total: 9 frames, hundreds of nodes, ~30 unique colors, ~20 unique strokes, ~10 unique radii, 2 shadow patterns, 3 blur patterns, 9 distinct font sizes, **Marmelad/Regular** the only font family.

---

## Frame inventory (sanity check)

All 9 frames present, all 402×876 (one at 402×874 — Practice-Live). Names match our PNG screenshot file names:

| # | Figma frame name | Figma node ID | Our PNG |
|---|---|---|---|
| 01 | `10_Dashboard 1` | `541:6649` | `user-dashboard-01-dashboard-1.png` |
| 02 | `11_Dashboard 2` | `648:1283` | `user-dashboard-02-dashboard-2.png` |
| 03 | `12_Check-in` | `541:6913` | `user-dashboard-03-checkin.png` |
| 04 | `13_Check-in Success` | `541:6987` | `user-dashboard-04-checkin-success.png` |
| 05 | `14_Practice-Live` | `541:6999` | `user-dashboard-05-practice-live.png` |
| 06 | `15_booked practice` | `541:7573` | `user-dashboard-06-booked-practice.png` |
| 07 | `16_AI-summary` | `541:7144` | `user-dashboard-07-ai-summary.png` |
| 08 | `17_My reservations` | `541:7182` | `user-dashboard-08-my-reservations.png` |
| 09 | `18_Booking Detail` | `648:1589` | `user-dashboard-09-booking-detail.png` |

---

## Section A — Token gaps (Figma has it, DS does not)

These need DS-promotion-pass before col 01 plashki can be rebuilt correctly.

### A.1 — Alert-pill colored outlines 🔥 CRITICAL (blocks T3 col 01 rebuild)

Operator-flagged: my `.alert-pill` is wrong (grey card with small icon). Figma reality:

| Stroke value | Count | Visual meaning |
|---|---|---|
| `#76dde6 @ 2px` (teal-light) | 3 | Info / check-in reminder pill outline |
| `#76dde6 @ 3px` (teal-light) | 7 | Stronger info variant outline |
| `#76dde6 @ 1.85px` | 5 | Sub-variant (decorative-fractional) |
| `#fbc088 @ 2px` (orange-light) | 3 | Warning / feedback reminder pill outline |
| `#f795a2 @ 3px` (coral-medium) | 2 | Error variant outline (likely destructive button border) |

**Promotion candidate tokens:**
- `--velo-border-alert-info: 2px solid var(--velo-color-teal-light)` (or 3px sibling)
- `--velo-border-alert-warning: 2px solid var(--velo-color-orange-light)`
- `--velo-border-alert-error: 3px solid var(--velo-color-coral-medium)`

Or, simpler — emit them as 1-line `border` declarations on the `.v-badge--alert` / `.alert-pill` component CSS, no new token needed. **Recommend: no new tokens, just use existing color primitives × 2px stroke directly in the component.** Saves token surface.

### A.2 — Card border (alpha-steel-30, not alpha-steel-15) 🔥

`#4c6589 @ 0.3 alpha @ 1px` — 25 occurrences across all 9 frames. This is **the** canonical card-border in Dashboard.

My bridge has `--velo-color-alpha-steel-15` (= rgba(..., 0.15)) and I used it for all card borders. Figma actually uses `rgba(..., 0.30)` — twice as dark. My cards look "ghostly", Figma cards have a visible edge.

**Action:** promote `--velo-color-alpha-steel-30: rgba(76, 101, 137, 0.30)` to Layer 1 primitives + Layer 2 alias `--velo-border-card: var(--velo-color-alpha-steel-30)`. Replace all `.practice-card / .v-badge / .booking-card / .info-pill / .warning-alert / .master-card / .stat-card / .recommendation-card / .list-row` borders to use the new token.

### A.3 — Soft tint backgrounds — small surface, defer

- `#fdf3e2` — soft cream-sand (1 occurrence)
- `#fde2e2` — soft pink (1 occurrence)

Single occurrence each = decorative, not promotion-worthy. Keep as inline literals if surfaced. **No action.**

### A.4 — Linear gradients (9 occurrences) — surface unclear

`GRADIENT_LINEAR` 9 occurrences across Dashboard. Likely candidates:
- AI-summary preview card (col 02 — already in my skeleton as `linear-gradient(135deg, teal 0.18, steel 0.10)`)
- Welcome / status banners
- Possibly bg-mandala secondary tint

**Action:** need a follow-up probe to capture `gradientStops` per gradient node — current probe only counted occurrences. Defer to T2.5 sub-task.

### A.5 — Radius 4 (1) and Radius 9.57 (2)

- `radius: 4` — between xs (2) and sm (5). Single occurrence. Likely decorative. **No promotion.**
- `radius: 9.57` (twice) — between sm and md. Decorative-fractional. **No promotion.**

---

## Section B — Implementation drift (DS has correct token, I used wrong one)

### B.1 — Glass halo composition diverges from Figma canon 🔥

**This is mine — Sprint 2 Phase 4 Onboarding promotion.** I codified a compound shadow in `variables.css`:

```css
--velo-shadow-button:
  0 6px 14px   rgba(76, 101, 137, 0.20),
  0 0 7px 11px rgba(255, 255, 255, 0.57);
```

**Figma actually uses a single DROP_SHADOW (white, no offset, blur 20.9, spread 7) — 13 occurrences across Dashboard:**

```
DROP_SHADOW { offset: 0,0; radius: 20.9; spread: 7; color: #ffffff (alpha 1) }
```

And one stronger variant (2 occurrences):

```
DROP_SHADOW { offset: 0,0; radius: 26.34; spread: 8.82; color: #ffffff (alpha 1) }
```

**The good news:** these EXACTLY match tokens that already exist in `variables.css`:

```css
--velo-shadow-glow-white:        0 0 20.9px 0 rgba(255, 255, 255, 1);
--velo-shadow-glow-white-strong: 0 0 26.34px 0 rgba(255, 255, 255, 1);
```

These were promoted in Sprint 1 Phase 2 and **I never used them**. I invented the compound version during Onboarding instead. This is the source of the "my glass looks different from Figma" feeling.

**Action options:**
1. **Honest** — revert all glass-button halos to `--velo-shadow-glow-white` (Figma canon). My compound becomes a legacy token, marked superseded. Re-render onboarding-flow.html for verification — if operator approves visual, the compound version is officially retired.
2. **Keep compound** — declare my compound as a Phase 4 evolution of Figma canon (steel drop adds depth), keep both tokens. Risk: two halo "truths" in DS.

**Recommend option 1** (honest revert). The 20% glass-halo softening you asked for last round can be achieved by simply alpha-reducing the white in `--velo-shadow-glow-white` — `rgba(255,255,255,0.80)` for soft variant, `rgba(255,255,255,1.0)` for strong variant. Cleaner DS, matches Figma 1:1.

### B.2 — White stroke weights with fractions

Figma uses `1.26px` (8 occurrences) and `1.27px` (3 + 12 + 1 = 16 occurrences) instead of round 1px. These are scale-derived — Figma exports the actual measured size from some compound transform. **Action: ignore the fractions, use clean 1px in CSS.** Token gap = none.

### B.3 — Letter-spacing 2PERCENT (all 135 text nodes)

Every text node has `letterSpacing: 2%`. My DS has `--velo-typo-h1-spacing: 1.2px` only for h1 — and body text in my bridge has no explicit letter-spacing.

**Action:** promote letter-spacing to body text token. Either:
- `--velo-typo-body-spacing: 0.02em` (relative — matches Figma %)
- Or compute per font-size as px (18px → 0.36px, etc.)

Recommend `0.02em` (relative) so all text scales correctly. Should be applied to body, footnote, label classes globally.

---

## Section C — Confirmed match (DS and Figma agree)

For the record — these are correct as-is, no action needed:

- `#4c6589` steel-primary (162 occurrences) ↔ `--velo-color-steel-primary` ✅
- `#627a9c` steel-light + alpha variants ↔ `--velo-color-steel-light` ✅
- `#5c7292` steel-muted (1) ↔ `--velo-color-steel-muted` ✅
- `#26767d / #2f9ea8 / #76dde6 / #d6f5f8` teal family ↔ teal-dark / -medium / -light / -50 ✅
- `#a16124 / #d4863c / #fbc088 / #feecdb` orange family ↔ orange-dark / -medium / -light / -50 ✅
- `#f795a2 / #d66674 / #fddfe3` coral family ↔ coral-medium / -dark / -50 ✅
- `#e2f0fd` blue-50 ✅
- `#ffffffa8` white 66% ↔ `--velo-color-alpha-white-66` ✅
- `#ffffff03` white 1% — vestigial (DS notes it as not promoted) ✅
- `radius 5 / 15 / 100 / 200` ↔ `--velo-radius-sm / -lg / -xl / -pill` ✅
- `BACKGROUND_BLUR 4 / 5.04` ↔ `--velo-blur-glass / -glass-medium` ✅
- Font: Marmelad Regular only (135 text nodes — single font, single weight) ✅
- Font sizes 14 / 18 / 20 / 15 / 32 — all in DS ✅

---

## Section D — New components / assets needed

### D.1 — Real Figma icons (SVG, via Plugin API exportAsync)

Mockup skeleton uses inline SVG drawn by me. Figma has the real ones. Candidates for extraction:

- **Bottom-nav icons** (4): home / chart / chat / profile (Dashboard 1-2)
- **Practice-type icons** (in alert-pill icon slot, practice-info, reservation rows): clock, message bubble, meditation pose, breath/breathwork
- **Section icons** (some sections have leading icons): check-mark, alert triangle
- **Mood faces** (col 03): 3 emoji-pair faces (Не очень / Нормально / Хорошо)
- **Energy faces** (col 02 / col 07): "from face" / "to face" pair

**Action:** drill down per frame, find GROUP / VECTOR nodes that are icons (have small bbox and live near label text), `exportAsync({format: 'SVG'})` chunked (>20KB needs split-call). Same protocol as `icon-onb-*.svg` from Onboarding.

### D.2 — AI-card gradient stops

A.4 above — need follow-up probe for gradient definitions.

### D.3 — Avatar imagery decision

Figma probably has master photos as IMAGE fills (12 IMG occurrences in probe). DS decision (Sprint 1) was initials-based avatars, no external imagery. **Action: confirm with operator** — keep initials, or extract avatar imageHashes and resolve to URLs / placeholders?

---

## Decision matrix — what to promote, what to leave alone

| Finding | Status | Action | Priority |
|---|---|---|---|
| A.1 alert-pill colored outlines | 🔥 blocks T3 | Add 2px coloured stroke to `.alert-pill` (no new tokens, reuse existing color primitives) | HIGH |
| A.2 card border alpha-steel-30 (not -15) | 🔥 visible drift | Promote `--velo-color-alpha-steel-30` + `--velo-border-card` alias. Mass replace in viewer. | HIGH |
| A.3 soft cream/pink tints | decorative-only | No action | — |
| A.4 linear gradients | needs probe | T2.5 sub-task — capture gradient stops | MEDIUM |
| A.5 radius 4, 9.57 | decorative | No action | — |
| B.1 glass halo diverges | 🔥 design drift | Revert to `--velo-shadow-glow-white` (1.0 / 0.8 alpha variants). Retire compound. | HIGH |
| B.2 fractional stroke weights | source artifact | Use 1px clean | — |
| B.3 letter-spacing 2% missing on body | minor drift | Add `letter-spacing: 0.02em` to body / footnote / label classes | LOW |
| C.* confirmed matches | ✅ ok | — | — |
| D.1 real icons SVG | enhancement | Per-frame drill-down → exportAsync. Bottom-nav icons first. | MEDIUM |
| D.2 AI-card gradient stops | T2.5 sub-task | Defer | MEDIUM |
| D.3 avatar decision | open question | Confirm initials policy stays | LOW |

---

## Proposed next sequence

Before T3 (col 01 rebuild) — DS promotion mini-pass to unblock:

1. **HIGH** Promote `--velo-color-alpha-steel-30` + `--velo-border-card` to `variables.css` master + deliverable, MD5-identical.
2. **HIGH** Revert glass halo to `--velo-shadow-glow-white` (canon, single drop-shadow white, blur 20.9, spread 7). Mark compound `--velo-shadow-button` as superseded → retire later. Apply alpha variants for soft/strong if needed.
3. **HIGH** Apply colored 2px stroke + soft tint bg to `.alert-pill --teal` and `.alert-pill --orange` variants directly (no new tokens).
4. **LOW** Add `letter-spacing: 0.02em` to body / footnote text rules.
5. Mass-replace `--velo-color-alpha-steel-15` → `--velo-border-card` for card borders across viewer (8-10 components).
6. T2.5 — second Figma probe for gradient stops + bottom-nav icon exports (optional, can defer).

After 1-5: col 01 plashki rebuild has correct token foundation, and all 9 frames pick up the corrected borders / halos automatically.

---

## Anchor

```
[FIGMA-FINDINGS-DASHBOARD-9.md | v1.0 | 2026-05-18]
T2 audit of Dashboard 9 SACRED root 541:6648.
Findings drive Sprint 2 Phase 4 DS-promotion-pass before T3 col 01 rebuild.
```
