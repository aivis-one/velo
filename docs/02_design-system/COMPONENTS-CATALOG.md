# VELO Design System — Components Catalog

Last updated: 2026-05-18
Version: 1.0
Status: bootstrap (Sprint 2 Phase 4 mid-pass — populated from current DS canon + Onboarding 8 promotions + Dashboard 9 candidates)

> **Single MD master for every component in VELO DS.** Each entry has Class+Variants+States, When-to-use+Anti-patterns, Tokens consumed+Related, Provenance+Status. Tokens themselves live in `tokens/variables.css` + `tokens/VELO-DS-INVENTORY.md` — this file is the **component layer** on top.

---

## Before-naming check (rule for every session)

**Before inventing a new CSS class name** for anything in a mockup:

1. Open this file. `Grep` for the visual function ("badge", "card", "alert", "input", "button").
2. If a canonical entry exists → **use that class name and variants as-is**. Override behaviour via DS tokens, not by writing a new ruleset.
3. If no canonical entry exists → add a new `## NEW` candidate at the bottom of this file in the same edit pass. Status: `⬜ candidate`. After operator approval at MOCKUP GATE, the next DS-promotion-pass moves it into its tier section and updates status to `✅ canon`.

**Why this matters.** Without this check sessions silently plodят дубли — `.status-badge` instead of `.v-badge`, `.reservation-row` instead of `.booking-card`, `.mood-selector` instead of `.mood-widget`. Two months later nobody knows which class is the truth.

---

## Status legend

- ✅ **canon** — visualised in `styleguide/velo-design-system.html`, frozen, used in production mockups
- 🔧 **awaiting promotion** — surfaced in a mockup, operator-approved at MOCKUP GATE, awaiting next DS-promotion-pass into styleguide
- ⬜ **candidate** — surfaced in a mockup skeleton, not yet operator-approved
- 🗑 **superseded** — replaced by a newer canonical entry (kept for reference)

---

## TOC

- [Tier 1 — atomic components](#tier-1--atomic-components)
- [Tier 2 — domain components](#tier-2--domain-components)
- [Patterns — multi-component compositions](#patterns--multi-component-compositions)
- [NEW — promotion candidates (Dashboard 9 mining)](#new--promotion-candidates-dashboard-9-mining)
- [Promotion history](#promotion-history)

---

## Tier 1 — atomic components

### VButton

**Class:** `.v-button` + modifier
**Variants:** `--primary` · `--glass` · `--oauth` · `--destructive` · `--round-icon` (Dashboard 9 candidate)
**States:** default · `:hover` · `:active` · `.is-disabled` (planned) · `.active` (round-icon menu item)
**When to use:**
- `--primary` — main CTA on a screen (Войти, Создать аккаунт, Check-in)
- `--glass` — secondary action of equal weight to primary (Zoom рядом с Check-in)
- `--oauth` — third-party sign-in (Google / Apple) with embedded provider icon
- `--destructive` — irreversible / negative action (Покинуть практику, Отменить бронирование)
- `--round-icon` — icon-only round button (bottom-nav items)
**Anti-patterns:**
- ❌ Never use `--primary` for a destructive action — operator-rule, primary is reserved for forward-motion.
- ❌ Never nest two `--primary` buttons in one stack — there is only one CTA per screen.
- ❌ Do not override `box-shadow` per-button — use the glass / primary halo tokens.
**Tokens consumed:**
- `--velo-button-height` (52px)
- `--velo-radius-pill`
- `--velo-bg-button-primary` / `--velo-bg-button-glass`
- `--velo-glass-fill` / `--velo-glass-fill-hover`
- `--velo-shadow-button` (primary), `--velo-shadow-button-glass` (glass + destructive, softer halo)
- `--velo-text-inverse` (primary text), `--velo-color-steel-light` (glass text)
- `--velo-color-coral-medium` / `--velo-color-coral-dark` (destructive bg + hover)
**Related:** stacks via `--velo-stack-gap-buttons` (16px). Halo total extent ≤ stack-gap (no overlap).
**Provenance:**
- `--primary` / `--glass` / `--oauth` — Onboarding 1-4 + Welcome, promoted 2026-05-18
- `--destructive` — Tier 1 in DS INDEX since Sprint 2 Phase 3 styleguide; surfaced in Dashboard 9 col 05/06/09 skeletons
- `--round-icon` — Dashboard 9 bottom-nav (col 01/02), 2026-05-18 candidate
**Status:** ✅ canon (primary/glass/oauth) · 🔧 awaiting promotion (destructive concrete CSS) · ⬜ candidate (--round-icon)

---

### VInput

**Class:** `.v-input`
**Variants:** `--pill` (rounded-pill with backdrop-blur) · `--textarea` (multi-line, currently `.v-textarea`)
**States:** default · `:focus` · `:disabled` · `.is-error`
**When to use:**
- Single-line text entry (e-mail, password, name, timezone)
- `--textarea` for free-text comment (check-in comment)
**Anti-patterns:**
- ❌ Don't combine `--pill` with `box-shadow` — visual conflict with glass-button halo.
- ❌ No placeholder-only — always have visible label or icon if context is non-obvious.
**Tokens consumed:**
- `--velo-input-height` (42px = 80% of button height)
- `--velo-radius-sm` (5px) — flat variant, or `--velo-radius-pill` for `--pill` variant
- `--velo-border-input`, `--velo-bg-input`
- `--velo-text-primary` (entered text), `--velo-text-muted` (placeholder)
**Related:** stacks via `--velo-stack-gap-forms` (10px — tighter than buttons).
**Provenance:** Login/Register screens, promoted 2026-05-18.
**Status:** ✅ canon · 🔧 textarea variant awaiting promotion

---

### VBadge

**Class:** `.v-badge` + variant
**Variants:** `--success` · `--warning` · `--error` · `--info` · `--neutral` · `--live` (Dashboard 9 candidate)
**States:** static (no interactivity — badges are display-only)
**When to use:**
- Status of a record — `Оплачено` (success), `Завтра` (warning), `Отменена` (error), `Подтверждена` (success), `В эфире` (live)
**Anti-patterns:**
- ❌ Don't use a badge as a tappable element — wrap the entire row in a tap target instead.
- ❌ Don't combine more than one badge in a single visual cluster — pick the most informative.
**Tokens consumed:**
- `--velo-color-teal-50` / `--velo-color-teal-dark` (success)
- `--velo-color-orange-50` / `--velo-color-orange-dark` (warning)
- `--velo-color-coral-50` / `--velo-color-coral-dark` (error)
- `--velo-color-blue-50` / `--velo-color-blue-medium` (info, live with dot)
- `--velo-radius-pill`
**Related:** sits inside BookingCard, PracticeCard, MasterCard.
**Provenance:** Tier 1 in DS INDEX since Sprint 2 Phase 3 styleguide; `--live` variant surfaced in Dashboard 9 col 05.
**Status:** ✅ canon (success/warning/error/info/neutral) · ⬜ candidate (--live with pulse dot)

---

### VAvatar

**Class:** `.v-avatar` + size
**Variants:** `--sm` (32px) · `--md` (38px) · `--lg` (48px) · with-image / initials-only
**States:** static
**When to use:** representing a user/master in a card. Defaults to initials-based (Sprint 1 decision — no external avatar URLs).
**Anti-patterns:**
- ❌ Don't add tap behaviour to the avatar alone — tap the whole card.
**Tokens consumed:**
- `--velo-color-alpha-steel-15` (initials bg)
- `--velo-color-steel-primary` (initials text)
- `--velo-radius-pill` (full circle)
**Related:** lives in PracticeCard, BookingCard, MasterCard.
**Provenance:** Tier 1 in DS INDEX. Live in Dashboard 9 practice-card / master-card / reservation-row.
**Status:** ✅ canon

---

### VLink

**Class:** `.v-link` (inline) · `.v-link-block` (full-width centered)
**Variants:** inline (in text), block (centered, e.g. "Пропустить", "На главную")
**States:** default · `:hover` (underline) · `:active`
**When to use:** secondary tap target with no halo / no fill — visual lightweight option vs button.
**Anti-patterns:**
- ❌ Don't use for primary destructive action — use `--destructive` button.
- ❌ Don't put halo on `.v-link` — it's intentionally lightweight.
**Tokens consumed:**
- `--velo-text-link` (= steel-light)
- font: inherited from body / Marmelad
**Related:** —
**Provenance:** Login (Забыли пароль?), Register (Создать), Check-in (Пропустить), Success (На главную).
**Status:** ✅ canon

---

### VDivider

**Class:** `.v-divider`
**Variants:** with text label («или») · pure horizontal line
**When to use:** separating sign-in methods («Войти» vs OAuth row).
**Anti-patterns:**
- ❌ Don't use as decorative space — use stack-gap instead.
**Tokens consumed:**
- `--velo-border-default`
- `--velo-text-muted` (label color)
**Status:** ✅ canon (promoted Onboarding 2026-05-18)

---

### VDots (pagination)

**Class:** `.v-dots`
**Variants:** big-active (14×14 круг steel-light) + small-passive (8×8 alpha-steel-60)
**When to use:** carousel pagination indicator (Onboarding 1-4 carousel).
**Tokens consumed:**
- `--velo-dot-active`, `--velo-dot-passive`
**Status:** ✅ canon

---

### VToast

**Class:** `.v-toast` (currently rendered as `.toast` in mockups — alias scheduled)
**Variants:** `--success` · `--warning` · `--error` · `--info`
**When to use:** transient feedback for every interactive element per VELO-METHODOLOGY §7.5 — toast emitted on click in mockup `showToast()`.
**Tokens consumed:**
- shell-surface bg + shell-border (mockup) / state colors (production)
**Status:** ✅ canon · 🔧 alias `.toast` → `.v-toast` planned

---

## Tier 2 — domain components

### PracticeCard

**Class:** `.practice-card`
**Variants:** compact (dashboard list) · detail (with avatar + meta row + badges)
**Anatomy:**
- `.pc-head` (avatar + title + master + verified badge)
- `.pc-meta` (date, duration, payment status badge)
**States:** default · `:hover` · pressable (entire card)
**When to use:** representing a single practice in dashboard / list views. **Not** for booking detail — that's a different card.
**Anti-patterns:**
- ❌ Don't put primary CTA inside the card — primary lives outside, card opens detail.
- ❌ Don't omit verified badge for verified masters.
**Tokens consumed:**
- `--velo-bg-card`, `--velo-color-alpha-steel-15` (border), `--velo-shadow-card`
- `--velo-radius-lg`
- `--velo-color-teal-medium` (verified ✓)
**Related:** VAvatar (initials), VBadge (Оплачено / Завершена / Отменена), MasterCard (different — for master profile, not practice).
**Provenance:** Tier 2 in DS INDEX since Sprint 2 Phase 3. Live in Dashboard 9 col 01/02.
**Status:** ✅ canon

---

### BookingCard

**Class:** `.booking-card` (formerly `.reservation-row` — rename pending)
**Variants:** upcoming (with warning badge "Завтра") · past (with success/error badge)
**Anatomy:**
- `.bc-icon` (practice type icon, circle)
- `.bc-body` (title + master + meta row)
- `.bc-status` (VBadge variant)
**When to use:** in "Мои бронирования" list — each row is one booking. Tap to open booking detail.
**Anti-patterns:**
- ❌ Don't combine upcoming and past in one section — group with `.group-title`.
**Tokens consumed:** same as PracticeCard + VBadge variant.
**Related:** VBadge, VAvatar (not used here — icon instead).
**Provenance:** Dashboard 9 col 08 (`.reservation-row` skeleton 2026-05-18) — rename to `.booking-card` scheduled in this DS-naming-pass.
**Status:** 🔧 awaiting promotion + rename

---

### MoodWidget

**Class:** `.mood-widget` (formerly `.mood-selector` — rename pending)
**Variants:** 3-option (Plохо / Нормально / Хорошо) · 5-option (planned)
**Anatomy:**
- 3 `.mood-pick` buttons (face emoji + label)
- Central is `.is-active` — face circle larger + raised + halo
- `.mood-slider` horizontal strip below
**States:** active mood pick = is-active; others muted.
**When to use:** check-in flow before practice — user picks current state.
**Anti-patterns:**
- ❌ Don't use as a generic rating — for ratings use a 5-star pattern (TBD).
**Tokens consumed:**
- `--velo-color-alpha-steel-15` (inactive face bg)
- `--velo-color-alpha-white-70` (active face bg → white when raised)
- `--velo-shadow-button` (active raised face)
- `--velo-color-steel-light` (active label)
**Related:** lives in check-in screen alongside `.v-textarea`.
**Provenance:** Tier 2 in DS INDEX since Sprint 2 Phase 3. Live in Dashboard 9 col 03.
**Status:** 🔧 awaiting promotion + rename

---

### MasterStatusBadge

**Class:** `.master-status-badge` (planned — currently inline via VBadge)
**Status:** ✅ canon in DS INDEX, not yet used in Dashboard 9 (will surface in Master screens Sprint 5)

---

### FeedbackWidget

**Class:** `.feedback-widget`
**Status:** ✅ canon in DS INDEX, not yet surfaced in mockups (Sprint 3+)

---

### WaitlistCard / PriceDisplay / BalanceChip

**Status:** ✅ canon in DS INDEX, awaiting first mockup usage.

---

## Patterns — multi-component compositions

### velo-bg-mandala

**Class:** `.velo-bg-mandala`
**Anatomy:** absolutely-positioned background layer with `velo-bg-app.png` (804×1748, universal app bg).
**When to use:** every user screen except SuccessScreen (which is pure white).
**Tokens consumed:** —
**Status:** ✅ canon (promoted Onboarding 2026-05-18)

### velo-header-compact

**Class:** `.velo-header-compact`
**Anatomy:** centered mini-mandala (`velo-logo-mandala-blue.svg`, 154×154) with padding 37px top.
**When to use:** login / register / oauth — branded header without full hero.
**Status:** ✅ canon

### top-header

**Class:** `.top-header`
**Anatomy:** `.header-back` (glass round 36×36 back-arrow, absolute left) + `.header-title` (centered title).
**When to use:** detail / nested views (check-in, booked-practice, booking-detail, reservations, AI-summary, practice-live).
**Tokens consumed:**
- `--velo-shadow-button-glass`, `--velo-glass-fill`, `--velo-radius-pill` (back button)
- typography h2-style for title
**Status:** ⬜ candidate (Dashboard 9, 2026-05-18)

### bottom-nav

**Class:** `.bottom-nav` container + N×`.v-button.v-button--glass.v-button--round-icon`
**Anatomy:** 4 round-icon glass buttons in flex-row, no container background — buttons lie directly on screen bg. Active item = `.active` modifier (color = steel-primary, fill = glass-fill-hover).
**When to use:** root dashboard screens (col 01/02). Hidden in detail views.
**Tokens consumed:**
- inherited from `.v-button--glass.v-button--round-icon`
**Status:** ⬜ candidate (Dashboard 9, 2026-05-18) — DS-promotion priority HIGH (used across many user screens)

### velo-back-arrow

**Class:** `.velo-back-arrow`
**Anatomy:** standalone absolute-positioned glass round 36×36 (in Onboarding flows where there's no top-header bar).
**Status:** ✅ canon (Onboarding promoted 2026-05-18) — superseded by `.top-header .header-back` in detail views from Dashboard 9 onwards.

### velo-skip

**Class:** `.velo-skip`
**Anatomy:** top-right `.v-link` ("Пропустить") on Onboarding 1-3.
**Status:** ✅ canon

---

## NEW — promotion candidates (Dashboard 9 mining)

These surfaced during Dashboard 9 skeleton pass (2026-05-18, session 4). All ⬜ candidate, awaiting operator MOCKUP GATE pass per screen, then promotion to Tier section.

### MasterCard

**Class:** `.master-card`
**Anatomy:** `.mc-head` (avatar + name + verified + tags row) + `.mc-foot` ("Подробнее →" chevron).
**When to use:** showing a master profile inside booking detail / booked practice.
**Tokens:** card-shadow + alpha-steel-15 border + radius-lg.
**Status:** ⬜ candidate

### InfoPill

**Class:** `.info-pill`
**Anatomy:** leading `.ip-icon` circle (blue) + body title+sub.
**When to use:** info notice with leading symbol — "Саммари недели 16-22 января", "ZOOM — ссылка будет отправлена…".
**Tokens:** blue-50 bg + alpha border + blue-medium icon bg.
**Status:** ⬜ candidate — possible alias for **InfoCard** if pattern repeats.

### WarningAlert

**Class:** `.warning-alert`
**Anatomy:** leading triangle icon (orange-medium) + body title (uppercase) + body text.
**When to use:** disclaimer / contraindication — "ПРОТИВОПОКАЗАНИЯ Беременность, эпилепсия".
**Tokens:** orange-50 tint bg + alpha-orange border + orange-dark title.
**Status:** ⬜ candidate

### ListRow

**Class:** `.list-row`
**Anatomy:** label + trailing `.lr-chevron` (⌄).
**When to use:** collapsible disclosure row — "О практике ⌄", "Что подготовить ⌄".
**Tokens:** card bg + alpha-steel-15 border + shadow-card.
**Status:** ⬜ candidate

### VideoBlock

**Class:** `.video-block`
**Anatomy:** dark steel-primary square placeholder with "video" label.
**When to use:** in-session practice view, video stream area.
**Tokens:** steel-primary bg + alpha-white-70 text.
**Status:** ⬜ candidate — production version will be `<video>` element, mockup-only for now.

### EnergyPair

**Class:** `.energy-pair`
**Anatomy:** inline row "с [face] до [face]" — emoji circles flanking text labels.
**When to use:** AI-summary energy trend visualisation.
**Tokens:** alpha-white-85 face bg + steel-light text.
**Status:** ⬜ candidate

### StatCard

**Class:** `.stat-card`
**Anatomy:** large `.stat-value` (28px) + `.stat-label` (12px muted).
**When to use:** dashboard progress stats (12 практик / 9,5 часов).
**Tokens:** card bg + shadow-card + radius-lg + steel-primary value text.
**Status:** ⬜ candidate

### AICard

**Class:** `.ai-card`
**Anatomy:** rounded card with linear-gradient bg (teal 0.18 → steel 0.10), text + optional energy-pair + link "Подробнее →".
**Tokens:** custom gradient (candidate token `--velo-bg-ai-tint`), alpha-steel-15 border.
**Status:** ⬜ candidate — color tokens for the gradient need Figma sample.

### RecommendationCard

**Class:** `.recommendation-card`
**Anatomy:** plain white card, text inside.
**When to use:** AI summary recommendations list.
**Tokens:** card bg + shadow-card + radius-lg.
**Status:** ⬜ candidate — может быть просто `.v-card` базовый.

### SectionTitle / GroupTitle

**Classes:** `.section-title` (compact, dashboard sections) · `.group-title` (slightly tighter, in detail views)
**Anatomy:** h2 with letter-spacing.
**When to use:** "Ближайшая практика", "Ваш прогресс", "Мастер", "Статус", "Предстоящие", "Прошедшие".
**Tokens:** steel-primary color, font-size 15-16px (candidate `--velo-typo-h2-*` token group).
**Status:** ⬜ candidate — DS gap: there's no h2 token group yet (only h1 + body promoted Phase 4).

### SuccessScreen layout

**Class:** `.scr-success`
**Anatomy:** pure white bg (no velo-bg-mandala), centered teal check circle (132×132) + h1 + sub + action stack.
**When to use:** terminal positive states — "Check-in отправлен!", future success screens.
**Tokens:** teal-50 bg + teal-light icon + h1 typography.
**Status:** ⬜ candidate

### AlertPill

**Class:** `.alert-pill` + variant
**Variants:** `--warning` (orange-themed) · `--info` (teal-themed) · `--error` (coral-themed, reserved)
**Anatomy:**
- `.pill-icon` (22×22 leading icon — colored per variant)
- `.pill-body` (`.pill-title` + `.pill-sub` stack)
- Outer container: tinted background + 2-3px colored outline + radius-lg
**States:** default · `:active` (scale 0.99) · pressable (whole row tappable)
**When to use:** dashboard notification row — call-to-action or status update with semantic urgency.
**Variant semantics:**
- `--warning` — time-sensitive action user must take ("Пора на check-in!", "Оплата истекает через 2 дня")
- `--info` — gentle invitation to engage ("Оставьте feedback!", "Новая практика доступна")
- `--error` — destructive / failed state notification (reserved)
**Anti-patterns:**
- ❌ Don't nest more than 2 alert-pills in one cluster — they compete for attention.
- ❌ Don't use plain text in `.pill-sub` for action — pill itself is the tap target.
- ❌ Don't swap colors per personal preference — variant choice is **semantic**, not stylistic.
**Tokens consumed:**
- `--warning` → `--velo-bg-alert-warning` (orange-light @ 40% alpha) + `--velo-color-orange-light` (border 2px) + `--velo-text-warning` (title = orange-dark) + `backdrop-filter: blur(4px)` (Figma BACKGROUND_BLUR(4))
- `--info` → `--velo-bg-alert-info` (teal-light @ 40% alpha) + `--velo-color-teal-light` (border 2px) + `--velo-text-success` (title = teal-dark) — **no backdrop blur on this variant**
- `--error` → `--velo-bg-alert-error` (coral-medium @ 40% alpha) + `--velo-color-coral-medium` (border 3px) + `--velo-text-error` (title = coral-dark)
- `--velo-text-muted` (sub text), `--velo-radius-lg`
**Icons (real Figma extracts via use_figma exportAsync):**
- `--warning` → `02_design-system/assets/icons/icon-alert-clock.svg` (21×21, fill `#A16124` baked in)
- `--info` → `02_design-system/assets/icons/icon-alert-feedback.svg` (21×21, fill `#26767D` baked in, bubble + pen + 2 dialog dots)
**Visual canon (Figma Dashboard 9 audit 2026-05-18, round 2):**
- Background uses **same hue as outline** with alpha 0.4 — NOT a different tint family. This is single-color-with-alpha approach.
- `--warning` ALSO has `BACKGROUND_BLUR(4)` — info variant does NOT (Figma asymmetry, preserved).
- Title text is **dark variant of outline color**, NOT steel-primary.
- Icon color is **baked into SVG** (Figma exports with hard-coded fills) — no CSS color override.
- Sub text stays muted-steel for hierarchy.
**Related:** —
**Provenance:** Dashboard 9 audit 2026-05-18. Border weights and tints captured from Figma probe (`#76dde6@2-3`, `#fbc088@2`, `#f795a2@3` strokes). Variants `--warning` and `--info` live in col 01 + col 02.
**Status:** ⬜ candidate — awaiting MOCKUP GATE approval, then promotion to Tier 2.

### --round-icon button modifier

Already documented under **VButton** above. Belongs in DS-promotion-pass with bottom-nav promotion.

---

## Promotion history

| Date | Action | Source |
|---|---|---|
| 2026-05-17 | Sprint 1 — initial Tier 1/2 catalog populated in `INDEX.md` Component Status | Figma probe + DSYS-era reference |
| 2026-05-17 | Sprint 2 Phase 3 — 15 components visualised in `velo-design-system.html`, STYLEGUIDE GATE passed | Operator visual review |
| 2026-05-18 | Sprint 2 Phase 4 — Onboarding 8 closed. Promoted: glass-button canon (white outline + halo + 5% blue), back-arrow, v-link, v-divider, v-dots, oauth, header-compact, bg-mandala, skip-link. Typography h1+body, button heights, stack gaps, glass-fill tokens added to `variables.css` | Onboarding flow pixel-measured |
| 2026-05-18 | Sprint 2 Phase 4 — Dashboard 9 skeleton pass. Surfaced ~14 candidates (above NEW section). `--velo-shadow-button-glass` token added (operator request −20% white alpha vs primary). `--round-icon` button modifier added | Dashboard skeleton iteration 1 |
| 2026-05-18 | **COMPONENTS-CATALOG.md created** — single MD master, before-naming check rule active from this date | — |

---

## References

- DS Index (canonical Component Status table source): `INDEX.md`
- DS Tokens master: `tokens/variables.css`
- DS Tokens inventory: `tokens/VELO-DS-INVENTORY.md`
- Visual catalog (browseable): `styleguide/velo-design-system.html`
- Methodology — Tier definitions §6.6, Mockup Layer §7, Mockup gate §10.4, Anti-patterns §11.2: `../04_methodology/VELO-METHODOLOGY.md`
- Figma operations (when re-probing): `FIGMA-OPERATIONS-GUIDE.md`

---

## Anchor

```
[COMPONENTS-CATALOG.md | v1.0 | 2026-05-18]
Single MD master for VELO DS components.
Before-naming check is mandatory in every session.
Location: D:\02_Projects\velo\docs\02_design-system\COMPONENTS-CATALOG.md
```
