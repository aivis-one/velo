# VELO Design System — Components Catalog

Last updated: 2026-05-19
Version: 1.8
Status: Sprint 2 Master Onboarding 13 DS harvest — Master Onboarding 13 candidates added (6 new), total components: 65+

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
- [NEW — promotion candidates (Calendar 11 mining)](#new--promotion-candidates-calendar-11-mining)
- [NEW — promotion candidates (Profile 7 mining)](#new--promotion-candidates-profile-7-mining)
- [NEW — promotion candidates (Diary 20 mining)](#new--promotion-candidates-diary-20-mining)
- [NEW — promotion candidates (Messages 3 mining)](#new--promotion-candidates-messages-3-mining)
- [NEW — promotion candidates (Analytics 3 mining)](#new--promotion-candidates-analytics-3-mining)
- [NEW — promotion candidates (Practices 15 mining)](#new--promotion-candidates-practices-15-mining)
- [NEW — promotion candidates (Master Dashboard 8 mining)](#new--promotion-candidates-master-dashboard-8-mining)
- [NEW — promotion candidates (Master Onboarding 13 mining)](#new--promotion-candidates-master-onboarding-13-mining)
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
**Status:** ⬜ promotion candidate — rename to `.booking-card` pending.

---

### MoodWidget

**Class:** `.mood-widget` (formerly `.mood-selector` — renamed 2026-05-18)
**Variants:** 3-option (Plохо / Нормально / Хорошо) · 5-option (planned)
**Anatomy:**
- 3 `.mw-pick` buttons (face emoji + label)
- Central is `.is-active` — face circle larger + raised + halo
- `.mw-slider` horizontal strip below
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
**Status:** ✅ all 3 icons present (mood-bad / mood-neutral / mood-good). Rename complete 2026-05-18.

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
**When to use:** ALL detail / nested views (check-in, booked-practice, booking-detail, reservations, AI-summary, practice-live, calendar detail). This is the ONE canonical header for all app screens. **Do not use `.velo-back-arrow` in app screens** — that pattern is onboarding-only.
**Tokens consumed:**
- `--velo-shadow-button-glass`, `--velo-glass-fill`, `--velo-radius-pill` (back button)
- typography h2-style for title
**Usage count:** 12 screens (Dashboard 03–09 + Calendar 08–11)
**Status:** ✅ canon (promoted 2026-05-20, operator session 17)

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

**Class:** `.energy-row` (renamed from `.energy-pair` — 2026-05-19 DS compliance pass)
**Anatomy:** flex row "с [face-img] [arrow-img] до [face-img]" using DS SVG icons:
- "from" face → `icon-mood-neutral.svg` (40×40, gradient circle + flat-line mouth) — same icon as MoodWidget neutral pick
- "to" face → `icon-mood-good.svg` (40×40, pink gradient circle + smile arc) — same icon as MoodWidget good pick
- arrow → `icon-arrow-forward.svg` (25×15, horizontal → arrow, fill #4C6589) — Figma node `648:1595` mirrored
**When to use:** AI-summary energy trend visualisation (screens 02, 07).
**Tokens:** mood icon gradients baked in SVG (matching Figma Vector 61/62 exactly). Arrow fill: steel-primary.
**Anti-patterns:** ❌ Never use emoji characters (😩/😊) — they were removed 2026-05-19. DS icons are mandatory.
**Status:** ✅ live in Dashboard 9 cols 02, 07. DS-compliant 2026-05-19.

### StatCard

**Class:** `.stat-card`
**Anatomy:** large `.stat-value` (28px) + `.stat-label` (12px muted).
**When to use:** dashboard progress stats (12 практик / 9,5 часов).
**Tokens:** card bg + shadow-card + radius-lg + steel-primary value text.
**Status:** ⬜ candidate

### AICard

**Class:** `.ai-card`
**Anatomy:** rounded card with linear-gradient bg (teal 0.18 → steel 0.10), text + optional `.energy-row` + link "Подробнее" with `icon-arrow-forward.svg` (18×11, inline after text).
**Tokens:** custom gradient (candidate token `--velo-bg-ai-tint`), alpha-steel-15 border.
**Icons:** "Подробнее →" link uses `icon-arrow-forward.svg` (25×15, Figma `648:1595` rotated) — never text `→` char.
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

### BottomNav

**Class:** `.bottom-nav` · Variants: `.bottom-nav--user` (user role nav) · `.bottom-nav--master` (master role nav)
**Anatomy:**
- Container: `.bottom-nav` flex-row, no background — buttons sit directly on screen bg
- 4 items: `button.v-button.v-button--glass.v-button--round-icon` (52×52 glass circle)
- Active item gets `.active` modifier → `color: steel-primary`, `::after fill: glass-fill-hover`
- Tab icons rendered as `<img>` inside each button
- **User icon mapping:** home=`icon-nav-home-active-composite.svg` · reservations=`icon-nav-reservations.svg` · diary=`icon-nav-diary.svg` · profile=`icon-nav-profile.svg`
- **Master icon mapping:** home=`icon-master-nav-home.svg` · schedule=`icon-master-nav-schedule.svg` · students=`icon-master-nav-students.svg` · profile=`icon-master-nav-profile.svg`
**States:** one button has `.active` class at all times.
**Layout:** fixed bottom bar, full-width, 4-equal-column grid.
**When to use:** every screen that has role-appropriate bottom navigation.
**Anti-patterns:**
- ❌ Don't add a 5th tab — SACRED is strictly 4.
- ❌ Don't apply `--velo-shadow-button-glass` to inactive tabs — only active home.
- ❌ Don't swap user/master icons — `.bottom-nav--user` uses user icons, `.bottom-nav--master` uses master icons.
**Tokens consumed:**
- `.bn-tab--active` → `--velo-shadow-button-glass`, `--velo-glass-fill`, `--velo-blur-glass-medium` (5.04px on glass circle), `--velo-color-neutral-white` (border)
- icons baked in SVG with `--velo-color-steel-primary` fill (#4C6589)
- `--velo-text-muted` (inactive labels), `--velo-text-primary` (active label)
**Icons (Figma exportAsync 2026-05-18):**
- `02_design-system/assets/icons/icon-nav-home-active-composite.svg` — Group 1984 `541:6756` (active state composite, 134×134 — glass circle + house path + glow filter; ⚠️ this is a rendered component state, not a bare icon — TODO: replace with CSS active state in Macro-Phase II rebuild)
- `02_design-system/assets/icons/icon-nav-diary.svg` — Group 1961 `541:6761`
- `02_design-system/assets/icons/icon-nav-reservations.svg` — Group 1962 `541:6772`
- `02_design-system/assets/icons/icon-nav-profile.svg` — Group 1959 `541:6767`
**Related:** VButton `--round-icon`
**Provenance:** Dashboard 9 SACRED frames `541:6649` (col 01), `541:7182` (col 08), `648:1589` (col 09). All 9 frames share identical bottom nav.
**Status:** ⬜ candidate — awaiting MOCKUP GATE approval in Dashboard 9 viewer.

---

### PaidBadge

**Class:** `.paid-badge`
**Anatomy:** small pill — leading teal check icon (`icon-check-sm.svg`) + text "Оплачено" (or "Paid").
**Variants:** none — single semantic variant.
**When to use:** inside PracticeCard / BookingCard meta row to indicate payment confirmed.
**Anti-patterns:**
- ❌ Don't use for unpaid state — use VBadge `--warning` for pending payment.
- ❌ Don't show alongside other status badges — one status at a time.
**Tokens consumed:**
- `--velo-color-teal-50` (bg) + `--velo-color-teal-light` (border + icon color) + `--velo-text-success` (text)
- `--velo-radius-pill`, font-size `--velo-size-12`
**Icons:** `02_design-system/assets/icons/icon-check-sm.svg` — Group 1970 `541:6718` (15×12 teal tick)
**Related:** VBadge (generic badge, no icon), BookingCard, PracticeCard
**Provenance:** Dashboard 9 frames `541:7573` (booked-practice col 06), `541:7182` (reservations col 08). Group 1970 `541:6718`.
**Status:** ⬜ candidate — awaiting MOCKUP GATE.

---

### MasterTagChip

**Class:** `.master-tag-chip`
**Anatomy:** small pill, text only — master specialisation label (e.g. "MBSR", "yoga", "yin").
**Variants:** none.
**When to use:** master profile area within BookingCard / booked-practice view to show master's practice tags.
**Anti-patterns:**
- ❌ Don't use for booking status — that's VBadge.
- ❌ Don't truncate tag text — keep tags ≤ 12 chars or use abbreviated form.
**Tokens consumed:**
- `--velo-color-amber-50` (bg `#fdf3e2`) + `--velo-color-orange-dark` (text `#a16124`) + `--velo-border-default` (optional 1px border)
- `--velo-radius-pill`, font-size `--velo-size-12`
**Related:** shown in cluster inside master profile card area alongside `icon-verified-master.svg`
**Provenance:** Dashboard 9 frame `541:7573` (booked-practice). New token `--velo-color-amber-50` promoted during this harvest 2026-05-18.
**Status:** ⬜ candidate — awaiting MOCKUP GATE.

---

## NEW — promotion candidates (Calendar 11 mining)

These surfaced during Calendar 11 DS harvest (2026-05-18, Phase B). All ⬜ candidate. Figma root `541:1553`. Awaiting operator MOCKUP GATE pass when Calendar 11 viewer is built in Sprint 3.

---

### CalendarGrid

**Class:** `.calendar-grid`
**Anatomy:**
- `.cg-header` — month/week label row with prev/next navigation arrows
- `.cg-weekdays` — short day-of-week row (Mon–Sun, 7 columns)
- `.cg-days` — 7-column grid of `.cg-day` cells
- Each `.cg-day` — day number + optional status indicator dot/chip (`.cg-day--booked`, `.cg-day--done`, `.cg-day--today`)
**States:** default cell · today (bold/highlighted) · booked (`.cg-day--booked`) · attended-done (`.cg-day--done`) · empty/disabled (faded)
**When to use:** primary calendar view screen (Calendar 1 / 22_Calendar screen `648:1673`). Full-month grid with booking status indicators.
**Anti-patterns:**
- ❌ Don't embed the grid inside a card — it fills the screen section directly.
- ❌ Don't use for date-pickers in forms — that's a different pattern (TBD).
**Tokens consumed:**
- `--velo-color-steel-primary` (day numbers, header text)
- `--velo-color-teal-medium` (`.cg-day--done` indicator)
- `--velo-color-steel-primary` (`.cg-day--booked` indicator bg)
- `--velo-radius-pill` (circle indicators)
**Icons (Figma exportAsync 2026-05-18):**
- `.cg-day--done` → `02_design-system/assets/icons/icon-cal-day-done.svg` — Group 1972 `648:1756` (16×16 teal circle + stroke check)
- `.cg-day--booked` → `02_design-system/assets/icons/icon-cal-day-booked.svg` — Group 1973 `648:1759` (16×16 dark steel circle + white "pic" text)
**Provenance:** Calendar 11 SACRED frames `648:1673` (22_Calendar 1), `541:1744` (23_Calendar 2 — deferred). Figma `541:1553` root.
**Status:** ⬜ candidate — Sprint 3 Calendar viewer.

---

### CalendarDayCell

**Class:** `.cg-day` (child of `.calendar-grid`)
**Anatomy:** single grid cell — day number centered + optional status icon (16×16 overlay or underline dot).
**Variants:** `--today` · `--booked` · `--done` · `--empty`
**When to use:** only within `.calendar-grid` — never standalone.
**Anti-patterns:**
- ❌ Don't inline status with CSS `content:` trick — use the real SVG icon for pixel-precision.
**Status:** ⬜ candidate — lives as sub-component of CalendarGrid.

---

### PracticeMetaRow

**Class:** `.practice-meta-row`
**Anatomy:**
- `.pmr-icon` — SVG icon (15×15 for duration/datetime/capacity; 27×27 for practice-type)
- `.pmr-label` — single-line text label (body-sm weight)
- Rows stack vertically inside PracticeDetailCard / BookingCard
**Variants:** `--practice-type` · `--duration` · `--datetime` · `--capacity`
**When to use:** inside practice detail cards or booking cards wherever practice metadata rows (type / time / duration / capacity) are displayed.
**Anti-patterns:**
- ❌ Don't use for booking status — use VBadge instead.
- ❌ Don't mix icon sizes in the same card — keep 15×15 for scalar metadata, 27×27 only for practice-type.
**Tokens consumed:**
- `--velo-color-steel-primary` (icon fill + label text)
- `--velo-font-body-sm` (label)
- spacing via `--velo-space-8` gap between icon and label
**Icons (Figma exportAsync 2026-05-18):**
- `--practice-type` → `assets/icons/icon-cal-practice.svg` — Group 1968 `648:1764` (27×27)
- `--duration`      → `assets/icons/icon-time.svg` — Group 1976 (canonical clock icon; `icon-cal-duration.svg` was a floating-point export duplicate, deleted 2026-05-19)
- `--datetime`      → `assets/icons/icon-calendar.svg` — Group 1975 (canonical calendar icon; `icon-cal-datetime.svg` was a byte-identical duplicate, deleted 2026-05-19)
- `--capacity`      → `assets/icons/icon-cal-capacity.svg` — Group 2238 `648:2030` (15×15)
**Provenance:** Calendar 11 SACRED frames `648:1934` (24_Practice Detail), `541:2065` (25_Master Profile). Figma root `541:1553`.
**Status:** ⬜ candidate — Sprint 3 Calendar viewer.

---

### FilterChip

**Class:** `.filter-chip`
**Anatomy:** pill button — label text only (no icon). Selected state fills the pill.
**Variants:** default (inactive) · `--active` (selected)
**States:** default · active · disabled (future)
**When to use:** inside `.filter-sheet-group` rows to select/deselect filter options (practice type, master, time slot). Not for navigation.
**Anti-patterns:**
- ❌ Don't use FilterChip outside a FilterSheet — standalone pill filters should use VBadge instead.
- ❌ Don't add icons inside the chip — text only per Figma spec.
**Tokens consumed:**
- `--velo-radius-pill` (cornerRadius 100)
- `--velo-color-steel-light` (`#627A9C`) — stroke 1.5px in inactive state
- `--velo-color-steel-primary` — fill + white text in active state
- `--velo-font-body-sm`
**Provenance:** Calendar 11 SACRED frame `648:1859` (23_Calendar Filter sheet). Figma root `541:1553`.
**Status:** ⬜ candidate — Sprint 3 Calendar filter.

---

### FilterSheet

**Class:** `.filter-sheet`
**Anatomy:**
- `.filter-sheet-overlay` — full-screen semi-transparent backdrop
- `.filter-sheet-panel` — bottom-anchored panel (rounded top corners)
  - `.filter-sheet-header` — title ("Фильтры") + `.filter-sheet-close` button (`icon-cal-close.svg`)
  - `.filter-sheet-body` — scrollable list of `.filter-sheet-group` sections
    - `.filter-sheet-group` — section label + horizontal-scroll row of `FilterChip`s
  - `.filter-sheet-footer` — "Сбросить" (ghost) + "Применить" (primary) action buttons
**Variants:** none (single pattern; group count varies by content).
**When to use:** triggered by the filter button on the Calendar 1 screen. Bottom sheet slides up over content.
**Anti-patterns:**
- ❌ Don't use a full-screen modal for filters — this is always a bottom sheet.
- ❌ Don't put FilterSheet groups in a vertical scroll without a sticky header+footer.
**Tokens consumed:**
- `--velo-color-white` (panel bg)
- `--velo-radius-16` (panel top corners)
- `--velo-shadow-card` or `--velo-shadow-modal` (panel elevation)
- `--velo-color-steel-primary` (header title, group labels)
- `--velo-color-steel-light` (close icon fill via `icon-cal-close.svg`)
**Icons:** `.filter-sheet-close` → `assets/icons/icon-cal-close.svg` — BOOLEAN_OPERATION `648:1872` (24×24, #627A9C)
**Provenance:** Calendar 11 SACRED frame `648:1859` (23_Calendar Filter). Figma root `541:1553`.
**Status:** ⬜ candidate — Sprint 3 Calendar filter.

---

### FeedbackRating

**Class:** `.feedback-rating`
**Anatomy:**
- `.feedback-rating-title` — prompt text (e.g. "Как прошла практика?")
- `.feedback-rating-options` — horizontal row of 3 `.feedback-option` buttons
  - `.feedback-option` — icon (52×52 or 48×52) + label text below
    - `.feedback-option--questions` ("Есть вопросы") — `icon-feedback-questions.svg`
    - `.feedback-option--good` ("Хорошо") — `icon-feedback-good.svg`
    - `.feedback-option--fire` ("Огонь!") — `icon-feedback-fire.svg`
- Selected option gets a highlight ring or scale transform (per Figma active state)
**Variants:** `--questions` · `--good` · `--fire`
**States:** unselected · selected (`--active`) · submitted
**When to use:** post-practice feedback collection screen (Calendar 11: screen 29 `541:2286`). Shown after check-in success.
**Anti-patterns:**
- ❌ Don't use for mood tracking — that's MoodWidget (different icon set, different context).
- ❌ Don't reduce to fewer than 3 options or change the order — Figma spec is fixed.
**Tokens consumed:**
- `--velo-color-steel-primary` (#4C6589) — "Есть вопросы" icon fill
- `--velo-color-coral-dark` (#D66674) — "Хорошо" icon fill
- Amber #D4863C — "Огонь!" icon fill (no named token yet; promote to `--velo-color-amber-fire` when component is built)
- `--velo-font-body-sm` (option labels)
**Icons (Figma exportAsync 2026-05-18 audit):**
- `--questions` → `assets/icons/icon-feedback-questions.svg` — Group 2336 `541:2326` (52×52)
- `--good`      → `assets/icons/icon-feedback-good.svg` — Group 2335 `541:2334` (52×52)
- `--fire`      → `assets/icons/icon-feedback-fire.svg` — Vector `541:2341` (48×52)
**Provenance:** Calendar 11 SACRED frame `541:2286` (29_Feedback screen). Figma root `541:1553`.
**Status:** ⬜ candidate — Sprint 4 post-practice flow.

---

## NEW — promotion candidates (Profile 7 mining)

These surfaced during Profile 7 DS harvest (2026-05-19, Phase B). All ⬜ candidate. Figma root `541:2355` (7 frames: 70_Profile through 76_Support). Awaiting operator MOCKUP GATE pass when Profile 7 viewer is built in Sprint 3.

**Token audit result: zero new tokens.** All fills, radii, typography, and blur values in Profile 7 map to existing DS tokens. No variables.css changes needed for this block.

**Destructive icon pattern (Profile 7-specific):** Icons for irreversible account actions (Выйти, Удалить аккаунт) use fill `#AD3444` (`--velo-color-coral-darker`) rather than the default steel-light `#627A9C`. This is already a DS token — no new color needed. Apply `.is-destructive` modifier to any row using these icons.

---

### ProfileSettingsRow

**Class:** `.profile-settings-row`
**Anatomy:**
- `.psr-icon` — 20×20 SVG icon (left-aligned, 40×40 circle bg: `--velo-color-alpha-steel-15`)
- `.psr-label` — text label (body weight, steel-primary)
- `.psr-chevron` — trailing `›` or `>` symbol (steel-light)
- Outer row: full-width tappable surface, divider between rows
**Variants:** `--default` (steel-light icon) · `--destructive` (coral-darker icon + label)
**States:** default · `:active` (scale 0.98 / bg tint) · `.is-destructive`
**When to use:** every tappable row in the Profile settings list — navigation to sub-pages (notifications, language, edit profile) and destructive actions (logout, delete account). One row = one action.
**Anti-patterns:**
- ❌ Don't embed complex secondary content in a settings row — for detail content use a sub-page.
- ❌ Don't use `--destructive` for navigation rows — only for irreversible state-change actions.
- ❌ Don't put both Logout and Delete Account in the same visual cluster without a separator — they must be visually separated from navigation rows.
**Tokens consumed:**
- `--velo-color-alpha-steel-15` (icon circle bg)
- `--velo-color-steel-light` (`#627A9C`) — default icon fill + chevron
- `--velo-color-coral-darker` (`#AD3444`) — destructive icon fill + label
- `--velo-color-steel-primary` (`#4C6589`) — default label text
- `--velo-radius-pill` (icon circle, full round)
- `--velo-border-default` (row dividers)
**Icons (Figma exportAsync 2026-05-19):**
- "Редактировать профиль" → `assets/icons/icon-profile-edit.svg` — Vector `541:2419` (20×20)
- "Мои бронирования"     → `assets/icons/icon-profile-bookings.svg` — Group 2616 `541:2424` (20×20)
- "Сообщения"            → `assets/icons/icon-profile-messages.svg` — Group 2525 `541:2433` (20×20)
- "Поддержка"            → `assets/icons/icon-profile-support.svg` — Vector `541:2448` (17×20)
- "Уведомления"          → `assets/icons/icon-profile-notifications.svg` — Group 2637 `541:2361` (20×21)
- "Язык/Часовой пояс"    → `assets/icons/icon-profile-language.svg` — Vector `541:2369` (20×20)
- "Выйти" (destructive)  → `assets/icons/icon-profile-logout.svg` — Group 2645 `541:2572` (20×20) — fill `#AD3444`
- "Удалить аккаунт" (destructive) → `assets/icons/icon-profile-delete.svg` — Group 2645 `541:2609` (20×24) — fill `#AD3444`
- "Часовой пояс" (sub-row) → `assets/icons/icon-profile-timezone.svg` — Group 2673 `541:2674` (20×20) — fill `#ffffff` (for steel-primary bg context)
> ⚠️ "Поделиться" icon (`541:2454`) — export failed (no visible layers). Row exists in Figma but icon asset is unavailable; use placeholder or omit icon in mockup.
**Provenance:** Profile 7 SACRED frames `541:2356` (70_Profile), `541:2460` (71_Profile 2), `541:2577` (72_Edit Profile). Figma root `541:2355`.
**Status:** ⬜ candidate — Sprint 3 Profile viewer.

---

### ToggleSwitch

**Class:** `.toggle-switch`
**Anatomy:**
- Outer track: 42×25 rounded-pill shape (`--velo-radius-pill`)
- Inner thumb: ~21×21 circle (`--velo-radius-pill`), transitions left→right
- Two states: ON (thumb right, track filled with accent) · OFF (thumb left, track muted)
**Variants:** `--on` · `--off`
**States:** ON · OFF · disabled (future)
**When to use:** binary on/off settings in the notifications screen (70_Notifications `541:2627`). Each notification category has one toggle.
**Anti-patterns:**
- ❌ Don't use toggles for multi-choice settings — use FilterChip or radio buttons.
- ❌ Don't substitute a checkbox for a toggle in an inline settings row — toggles are the VELO pattern for yes/no settings.
**Tokens consumed:**
- ON track → `--velo-color-teal-medium` or `--velo-color-steel-primary` (Figma: steel-light `#627A9C` approximate)
- OFF track → `--velo-color-alpha-steel-15` or `--velo-color-steel-light` at low opacity
- Thumb → `--velo-color-neutral-white` + `--velo-shadow-button` (subtle drop shadow)
- `--velo-radius-pill` (track + thumb)
> Note: Figma exports Group 2672 (ON) and Group 2669 (OFF) as 42×25 RECTANGLE+ELLIPSE compositions. Exact token mapping for track color to be confirmed during component build against SACRED screenshots `541:2627` and `541:2655`.
**Provenance:** Profile 7 SACRED frames `541:2627` (75_Notifications), `541:2655` (76_Language-Timezone). Figma root `541:2355`. Nodes: Group 2672 (ON state) `~541:xxxx`, Group 2669 (OFF state).
**Status:** ⬜ candidate — Sprint 4 Profile settings screens.

---

### ConfirmationDialog

**Class:** `.confirmation-dialog`
**Anatomy:**
- Modal overlay (semi-transparent backdrop)
- `.cd-panel` — centered card, 350×310 (approx), radius 20px (component-local, single-occurrence — not promoted to token)
- `.cd-title` — bold warning title (e.g. "Удалить аккаунт?")
- `.cd-body` — explanatory text (muted, body weight)
- `.cd-actions` — two-button row: `--destructive` (confirm) + `--glass` or text link (cancel)
**Variants:** `--destructive` (for account delete / logout) · `--confirm` (for neutral confirmations — future)
**When to use:** two-step confirmation before irreversible account actions (delete account `541:2616`). Always triggered from a `--destructive` ProfileSettingsRow action, never from navigation.
**Anti-patterns:**
- ❌ Don't use for reversible actions — use `.v-toast` feedback instead.
- ❌ Don't put more than 2 action buttons in the dialog.
- ❌ Don't reuse 20px radius as a global token — it appears only here; keep as inline literal.
**Tokens consumed:**
- `--velo-bg-card` (panel bg)
- `--velo-shadow-modal` (panel elevation)
- `--velo-color-coral-darker` (`#AD3444`) — destructive action button bg
- `--velo-text-primary` (title), `--velo-text-muted` (body)
- `--velo-radius-xl` (16px) — closest DS token; actual Figma radius is 20px (use inline override)
**Provenance:** Profile 7 SACRED frame `541:2616` (74_Confirmation, 350×310 small modal). Figma root `541:2355`.
**Status:** ⬜ candidate — Sprint 3 Profile delete account flow.

---

### ProfileHeader

**Class:** `.profile-header`
**Anatomy:**
- `.ph-avatar` — large avatar circle (80-96px), initials or photo
- `.ph-name` — user display name (h1 weight)
- `.ph-email` — email address (body, muted)
- Optional `.ph-edit-btn` — small glass edit button or icon-only tap target
**Variants:** `--view` (main profile) · `--edit` (edit profile mode with editable fields)
**When to use:** top section of the Profile main screen (`541:2356`) and Edit Profile screen (`541:2577`). Not for inline cards.
**Anti-patterns:**
- ❌ Don't use ProfileHeader inside a scroll container — it should remain top-fixed (sticky) or above the scroll content.
**Tokens consumed:**
- `--velo-color-alpha-steel-15` (avatar bg)
- `--velo-color-steel-primary` (name text)
- `--velo-text-muted` (email text)
- `--velo-radius-pill` (avatar circle)
- `--velo-glass-fill` (edit button bg if glass)
**Provenance:** Profile 7 SACRED frames `541:2356` (70_Profile) and `541:2577` (72_Edit Profile). Figma root `541:2355`.
**Status:** ⬜ candidate — Sprint 3 Profile screen.

---

## NEW — promotion candidates (Diary 20 mining)

These surfaced during Diary 20 DS harvest (2026-05-19, Phase B). All ⬜ candidate. Figma root `541:2816` (20 frames: 37_Diary All Map → 52_Edit Entry). Awaiting operator MOCKUP GATE pass when Diary 20 viewer is built in Sprint 3.

**Token audit result: zero new tokens.** All fills, radii, typography, and blur values in Diary 20 map to existing DS tokens. `#627A9C` = `--velo-color-steel-light` (filter chips, tab icon), `#4C6589` = `--velo-color-steel-primary` (map pins, edit icon context). No variables.css changes needed.

**Skipped exports note:** 4 icon nodes could not be exported (stroke-only / no-renderable-layers errors): `541:2930` (location marker), `541:2963`/`541:2960` (view toggles), `541:3258`/`541:3261` (round header buttons). These are geometric composites that must be built from DS primitives in HTML.

---

### DiaryMapView

**Class:** `.diary-map-view`
**Anatomy:**
- Full-screen map canvas (native OS map or placeholder `<div class="dv-map-canvas">`)
- `.dv-pin` — map pin marker(s) overlaid on canvas, each using `icon-diary-pin.svg` or `icon-diary-pin-alt.svg`
- `.dv-tab-bar` — floating filter tab bar (below map, above bottom-nav): horizontal-scroll row of `DiaryFilterTab` items
- `.dv-top-actions` — top-right floating action cluster (search icon + filter icon, round glass buttons)
**Variants:** `--all` (all diary entries) · `--checkins` · `--feedbacks` · `--entries` (each filters which pins appear)
**States:** pins in default / selected / cluster state (single pin vs group count bubble)
**When to use:** primary diary "map" view — screens 37_Diary All Map (`541:2817`), 38_Diary Checkins Map (`541:3446`), 40_Diary Feedbacks Map (`541:3926`), 42_Diary Entries Map (`541:4362`), 43_Diary Entries Map 2 (`541:4556`).
**Anti-patterns:**
- ❌ Don't use DiaryMapView as a static image — the map must be zoomable/pannable.
- ❌ Don't put more than one active tab in `.dv-tab-bar`.
**Tokens consumed:**
- `--velo-color-steel-primary` (`#4C6589`) — pin fill color (baked into SVG)
- `--velo-color-steel-light` (`#627A9C`) — tab bar icons + chip strokes
- `--velo-shadow-card` (floating tab bar elevation)
- `--velo-radius-pill` (round action buttons)
**Icons (Figma exportAsync 2026-05-19):**
- Default pin → `assets/icons/icon-diary-pin.svg` — Group 2354 `541:2950` (28x34, ~31KB complex mask paths)
- Alt pin → `assets/icons/icon-diary-pin-alt.svg` — Group 2355 `541:2953` (28x34, ~31KB mirrored variant)
**Provenance:** Diary 20 SACRED frames `541:2817`, `541:3446`, `541:3926`, `541:4362`, `541:4556`. Figma root `541:2816`.
**Status:** ⬜ candidate — Sprint 3 Diary map viewer.

---

### DiaryFilterBar

**Class:** `.diary-filter-bar`
**Anatomy:**
- Horizontal-scroll container of `.dfb-tab` buttons
- Each `.dfb-tab` — icon (40x40 SVG) or text label (for named category tabs)
- Active tab has filled/highlighted state; inactive tabs are muted
- "All" tab (leftmost) uses `icon-diary-tab-all.svg` (steel-light filled circle with white funnel)
**Variants:** `--map` (floating over map canvas) · `--list` (docked above list scroll area)
**States:** one tab always `.is-active`, rest `.is-inactive`
**When to use:** top-level category selector across all Diary views (map + list modes). Categories: "All", "Checkins", "Feedbacks", "Entries".
**Anti-patterns:**
- ❌ Don't add more than 5 tabs — Figma spec shows 4.
- ❌ Don't make tabs vertical — this is always a horizontal scroll strip.
**Tokens consumed:**
- `--velo-color-steel-light` (`#627A9C`) — active tab icon fill + inactive stroke
- `--velo-color-alpha-steel-light-15` — inactive tab circle bg
- `--velo-radius-pill` (tab circles, 40x40)
**Icons (Figma exportAsync 2026-05-19):**
- "All" tab → `assets/icons/icon-diary-tab-all.svg` — Group 2474 `541:3255` (40x40, steel-light filled circle + white funnel)
**Provenance:** Diary 20 SACRED frames `541:2817` (37_Diary All Map), `541:3076` (38_Diary All List). Figma root `541:2816`.
**Status:** ⬜ candidate — Sprint 3 Diary viewer.

---

### DiaryRatingSelector

**Class:** `.diary-rating-selector`
**Anatomy:**
- Horizontal-scroll row of `.drs-chip` numbered buttons (5 through 11)
- Each `.drs-chip` wraps one of the numeral SVG icons: `icon-diary-filter-n5.svg` through `icon-diary-filter-n11.svg`
- Inactive chip: steel-light circle outline + steel-light digit fill (baked in SVG)
- Active chip: filled steel-primary circle + white digit (active state managed via CSS filter or background override)
**Variants:** single variant; active state via `.is-active` modifier.
**States:** default (inactive) · `.is-active` (selected rating)
**When to use:** Diary filter modal for selecting a rating range (5-11 scale). Shown in filter overlay screens `541:3251` (41_Diary Filter) and `541:3284` (42_Diary Filter 2).
**Anti-patterns:**
- ❌ Don't use this for 1-5 star ratings — that is a different pattern. This is a custom 5-11 scale specific to VELO diary entry ratings.
- ❌ Don't render as text inputs — always use the numeral SVG chips for visual consistency.
**Tokens consumed:**
- `--velo-color-steel-light` (`#627A9C`) — chip outline + digit fill (inactive, baked in SVG)
- `--velo-color-steel-primary` (`#4C6589`) — active chip bg (CSS override on wrapper)
- `--velo-radius-pill` (chip circle, 38x38)
**Icons (Figma exportAsync 2026-05-19):**
- `icon-diary-filter-n5.svg` — Group 2475 `541:3315` (38x38)
- `icon-diary-filter-n6.svg` — Group 2476 `541:3318` (38x38)
- `icon-diary-filter-n7.svg` — Group 2477 `541:3321` (38x38)
- `icon-diary-filter-n8.svg` — Group 2478 `541:3324` (38x38)
- `icon-diary-filter-n9.svg` — Group 2479 `541:3327` (38x38)
- `icon-diary-filter-n10.svg` — Group 2480 `541:3330` (38x38)
- `icon-diary-filter-n11.svg` — Group 2481 `541:3333` (38x38)
**Provenance:** Diary 20 SACRED frames `541:3251` (41_Filter), `541:3284` (42_Filter 2). Figma root `541:2816`.
**Status:** ⬜ candidate — Sprint 3 Diary filter modal.

---

### DiaryFilterModal

**Class:** `.diary-filter-modal`
**Anatomy:**
- Full-screen or bottom-sheet overlay
- `.dfm-header` — title ("Filtry") + close/dismiss button
- `.dfm-body` — scrollable filter groups: Category group, Date range group, Rating group (DiaryRatingSelector chips 5-11)
- `.dfm-footer` — "Sbrosit" (ghost) + "Primenit" (primary CTA) button pair
**Variants:** none — single modal pattern.
**States:** open (overlay visible) · closed · loading (while results refresh).
**When to use:** triggered from the filter icon in the diary header action cluster. Covers the full screen or anchors as a bottom sheet.
**Anti-patterns:**
- ❌ Don't use a separate page navigation for filters — always modal/sheet pattern.
- ❌ Don't embed DiaryFilterModal inside the map canvas — it always overlays on top.
**Tokens consumed:**
- `--velo-bg-card` (modal panel bg)
- `--velo-shadow-modal` (panel elevation)
- `--velo-color-steel-primary` (header title, group labels)
- `--velo-radius-xl` (panel top corners if bottom-sheet)
- VButton `--primary` (Primenit) + VButton `--glass` (Sbrosit)
**Related:** DiaryRatingSelector (embedded), DiaryFilterBar (category row), FilterSheet (same pattern as Calendar — may unify at Sprint 3)
**Provenance:** Diary 20 SACRED frames `541:3251` (41_Diary Filter), `541:3284` (42_Diary Filter 2). Figma root `541:2816`.
**Status:** ⬜ candidate — Sprint 3 Diary filter. Consider merging with CalendarFilterSheet under a unified `FilterSheet` component.

---

### DiaryEntryCard

**Class:** `.diary-entry-card`
**Anatomy:**
- `.dec-header` — entry date + category badge (Chekin / Fidbek / Zapis)
- `.dec-body` — entry text excerpt (1-3 lines, body weight)
- `.dec-meta` — practice name + rating chip (if applicable)
- `.dec-thumb` — optional image thumbnail (right-aligned or below)
- Entire card is tappable — opens DiaryEntryView
**Variants:** `--checkin` · `--feedback` · `--entry` (diary note)
**States:** default · `:active` (scale 0.98 press)
**When to use:** diary list views — screens 38_All List (`541:3076`), 39_Checkins List (`541:3708`), 41_Feedbacks List (`541:4177`), 44_Entries List (`541:4775`). One card per diary record.
**Anti-patterns:**
- ❌ Don't put interactive sub-elements (buttons) inside the card — whole card is the tap target.
- ❌ Don't render as a table row — always a card with full border-radius per DS.
**Tokens consumed:**
- `--velo-bg-card`, `--velo-shadow-card`, `--velo-radius-lg`
- `--velo-color-alpha-steel-30` (card border)
- `--velo-color-steel-primary` (entry text)
- `--velo-text-muted` (meta text)
- VBadge (category label)
**Provenance:** Diary 20 SACRED frames `541:3076` (38_All List), `541:3708` (39_Checkins List), `541:4177` (41_Feedbacks List), `541:4775` (44_Entries List). Figma root `541:2816`.
**Status:** ⬜ candidate — Sprint 3 Diary list viewer.

---

### DiaryEntryView

**Class:** `.diary-entry-view`
**Anatomy:**
- `.dev-header` — top-bar with back arrow + entry title/date + action row (edit button with `icon-diary-edit.svg`)
- `.dev-body` — full entry text content (scrollable)
- `.dev-meta` — practice metadata if linked (practice name, date, rating)
- `.dev-actions` — bottom action strip (delete confirm via ConfirmationDialog)
**Variants:** `--readonly` (view mode) · `--edit` (inline edit mode, triggered by edit button)
**States:** readonly · editing · delete-confirm (ConfirmationDialog overlay)
**When to use:** single diary entry detail view — screens 45_View Entry (`541:4925`), 49_View Entry Diary (`541:5662`), 50_View Entry Diary 2 (`541:5816`), 51_View Entry Delete (`541:5925`), 52_Edit Entry (`541:6042`).
**Anti-patterns:**
- ❌ Don't show the delete confirmation inline — always use ConfirmationDialog overlay.
- ❌ Don't skip the edit icon — `icon-diary-edit.svg` is the canonical edit affordance for this view.
**Tokens consumed:**
- `--velo-color-steel-light` (action icon bg context)
- `--velo-text-primary` (entry text)
- `--velo-text-muted` (meta text)
- VButton `--destructive` (delete action)
**Icons (Figma exportAsync 2026-05-19):**
**Icons (Figma exportAsync 2026-05-19):**
- Edit action → `assets/icons/icon-diary-edit.svg` — Group 2499 `541:5921` (17x20, white fill on steel-primary bg)
**Related:** ConfirmationDialog (for delete-confirm step)
**Provenance:** Diary 20 SACRED frames `541:4925` (45_View Entry) through `541:6042` (52_Edit Entry). Figma root `541:2816`.
**Status:** ⬜ candidate — Sprint 3 Diary entry detail.

---

## NEW — promotion candidates (Messages 3 mining)

These surfaced during Messages 3 DS harvest (2026-05-19, Phase B). All ⬜ candidate. Figma root `541:2717` (3 frames: 80_Messages, 81_Thread, 82_Thread Support). Awaiting operator MOCKUP GATE pass when Messages 3 viewer is built in Sprint 3.

**Token audit result: zero new tokens.** All fills, radii, typography, and blur values in Messages 3 map to existing DS tokens. Notably: the glass message input bar reuses the same glass canon (`--velo-color-alpha-steel-light-15` fill + `--velo-shadow-glow-white-strong` + `--velo-blur-glass-stronger`) already established in Onboarding + Dashboard. No variables.css changes needed for this block.

---

### MessageConversationRow

**Class:** `.message-conversation-row`
**Anatomy:**
- `.mcr-avatar` — 48–56px avatar circle (photo or initials fallback, `--velo-radius-pill`)
- `.mcr-content` — flex column: `.mcr-name` (contact name) + `.mcr-preview` (last message excerpt)
- `.mcr-meta` — right-aligned: `.mcr-time` (timestamp) + optional `.mcr-badge` (unread count badge)
- Entire row is tappable — navigates to MessageThread
- Row divider between items (1px, `--velo-border-default`)
**Variants:** `--unread` (bold name, unread badge visible) · `--read` (normal weight, no badge)
**States:** default · `:active` (scale 0.98 / tint) · `.has-unread`
**Typography (Figma-sampled):**
- Contact name: 18px Marmelad, `--velo-color-steel-primary` (#4C6589), full opacity
- Preview text: 14px Marmelad, `--velo-color-alpha-steel-70` (steel-primary @70%)
- Timestamp: 12px Marmelad, `--velo-color-alpha-steel-70` (steel-primary @70%)
**When to use:** every row in the Messages list screen (80_Messages). One row = one conversation thread.
**Anti-patterns:**
- ❌ Don't render the preview text at full opacity — Figma spec is 70% (alpha-steel-70) for both preview and timestamp.
- ❌ Don't hide the unread badge with `display:none` — use `.has-unread` class toggle on the row.
**Tokens consumed:**
- `--velo-color-steel-primary` (name text)
- `--velo-color-alpha-steel-70` (preview + timestamp)
- `--velo-size-18` / `--velo-size-14` / `--velo-size-12`
- `--velo-radius-pill` (avatar)
- `--velo-border-default` (row divider)
- `--velo-color-coral-medium` (`#f795a2`) — unread badge background
- `--velo-color-teal-light` (`#76dde6`) — unread badge count text color
**Provenance:** 80_Messages SACRED frame `541:2718`. Groups 2326, 2663, 2662. Figma root `541:2717`.
**Status:** ⬜ candidate — Sprint 3 Messages list viewer.

---

### MessageBubble

**Class:** `.message-bubble`
**Anatomy:**
- `.mb-text` — message body text (14px Marmelad)
- `.mb-time` — timestamp (12px Marmelad, 70% opacity)
- **Outbound** (user's own message): `--velo-color-steel-light` (#627A9C) fill, white text, right-aligned
- **Inbound** (master/support reply): white fill, `--velo-color-steel-primary` text, left-aligned
**Variants:** `--outbound` · `--inbound`
**States:** default · sending (opacity 0.6)
**When to use:** every message in a chat thread (81_Thread, 82_Thread Support).
**Anti-patterns:**
- ❌ Don't use the same fill color for both outbound and inbound — direction must be visually distinguishable.
- ❌ Don't render timestamps at full opacity — Figma spec is 70% for both variants.
**Tokens consumed:**
- `--velo-color-steel-light` (#627A9C) — outbound bubble fill
- `--velo-color-neutral-white` — inbound bubble fill + outbound text
- `--velo-color-steel-primary` — inbound text
- `--velo-color-alpha-steel-70` — inbound timestamp
- `--velo-size-14` / `--velo-size-12`
- `--velo-radius-lg` (15px) — bubble corners
**Provenance:** 81_Thread (`541:2775`); 82_Thread Support (`541:2796`). Figma root `541:2717`.
**Status:** ⬜ candidate — Sprint 3 Messages thread viewer.

---

### MessageInputBar

**Class:** `.message-input-bar`
**Anatomy:**
- `.mib-input` — glass pill input field (placeholder "Написать сообщение...", 16px)
- `.mib-send` — circular send button (40×40), `icon-messages-send.svg`
- Glass treatment: `--velo-color-alpha-steel-light-15` fill + white stroke 1.26px + `--velo-shadow-glow-white-strong` + `--velo-blur-glass-stronger` (blur 30)
- CornerRadius on input: 252px (decorative single-component literal — not promoted)
**Variants:** none
**States:** empty · has-text · sending
**When to use:** bottom of every chat thread screen (81_Thread, 82_Thread Support).
**Anti-patterns:**
- ❌ Don't remove the glass treatment — the backdrop-blur is part of the Figma spec.
- ❌ Don't promote radius 252 to a global token — single-component decorative value.
**Tokens consumed:**
- `--velo-color-alpha-steel-light-15` (input fill)
- `--velo-color-neutral-white` (input stroke)
- `--velo-shadow-glow-white-strong` (input halo)
- `--velo-blur-glass-stronger` (`blur(30px)`) — input backdrop blur
- `--velo-color-steel-primary` (placeholder text color base)
- `--velo-size-16`
**Icons (Figma exportAsync 2026-05-19):**
- Send button → `assets/icons/icon-messages-send.svg` — Group 2356 `541:2785` (40×40)
**Provenance:** 81_Thread (`541:2775`) Group 2504; 82_Thread Support (`541:2796`). Figma root `541:2717`.
**Status:** ⬜ candidate — Sprint 3 Messages thread viewer.

---

## NEW — promotion candidates (Analytics 3 mining)

These surfaced during Analytics 3 DS harvest (2026-05-19, Phase B). All ⬜ candidate. Figma root `758:1529` (3 frames: 01_Reviews `758:1530`, 02_Reviews 2 `758:1743`, 03_Payments `758:1891`). Awaiting operator MOCKUP GATE pass when Analytics 3 viewer is built in Sprint 3/5.

**Token audit result: zero new tokens.** All fills, radii, typography, and blur values in Analytics 3 map to existing DS tokens. Fills: `#4C6589` → `--velo-color-steel-primary`; `#91A2BA` → `--velo-color-steel-pale`; `#D66674` → `--velo-color-coral-dark`; `#2F9EA8` → `--velo-color-teal-medium`; `#619CD2` → `--velo-color-blue-medium`; `#D4863C` → `--velo-color-orange-medium`; glass card fill `rgba(98,122,156,0.15)` → `--velo-color-alpha-steel-light-15`. Blur effects: `--velo-blur-glass-medium` / `--velo-blur-glass`. Glow: `--velo-shadow-glow-white-strong`. No `variables.css` changes needed.

---

### AnalyticsTabBar

**Class:** `.analytics-tab-bar`
**Anatomy:**
- Horizontal row of 4 tab buttons, Group 2648 (327×63), present on all 3 Analytics frames
- Each tab slot: 63×63, `.atb-slot` — background rect (radius ~15px) + 27×27 or 21×27 icon centered
- Active slot: filled with `--velo-color-alpha-steel-light-15` + white stroke + `--velo-blur-glass-medium`
- Inactive slots: transparent background, icon at reduced opacity (~50%)
- Tab icons (left→right): `icon-master-nav-home.svg` (tab 1 — home/dashboard), `icon-master-nav-students.svg` (tab 2 — list/clipboard), `icon-analytics-tab-trophy.svg` (tab 3 — trophy), `icon-analytics-tab-chart.svg` (tab 4 — chart)
- ⚠️ Dedup note (2026-05-19): tabs 1+2 reuse MasterNavBar canonical icons. `icon-analytics-tab-profile.svg` was byte-identical to `icon-master-nav-home.svg` (mislabeled as "profile/person" — it is actually a house icon). `icon-analytics-tab-list.svg` was byte-identical to `icon-master-nav-students.svg`. Both duplicates deleted.
**Variants:** none (single 4-slot layout; active state driven by `.is-active` class on slot)
**States:** `.is-active` on one slot at a time
**When to use:** top filter/navigation bar on all Analytics 3 screens.
**Anti-patterns:**
- ❌ Don't reuse this component for the bottom-nav — AnalyticsTabBar is a content-mode switcher.
- ❌ Don't add text labels to the tab slots — icon-only per Figma spec.
**Tokens consumed:**
- `--velo-color-alpha-steel-light-15` (active slot glass fill)
- `--velo-color-neutral-white` (active slot glass stroke, 1px)
- `--velo-blur-glass-medium` (`blur(5.04px)`) — active slot backdrop-filter
- `--velo-color-steel-primary` (icon fill, baked into SVGs)
- `--velo-radius-md` (15px approx — slot background radius)
**Icons (Figma exportAsync 2026-05-19):**
- Tab 1 → `assets/icons/icon-master-nav-home.svg` — `758:3384` (27×27, house — canonical from MasterNavBar)
- Tab 2 → `assets/icons/icon-master-nav-schedule.svg` — `758:1759` (27×27, calendar/schedule — ✅ NEW 2026-05-19, correct master nav slot 2)
- Tab 3 → `assets/icons/icon-analytics-tab-trophy.svg` — Group 1959 `758:1672` (21×27, unique)
- Tab 4 → `assets/icons/icon-analytics-tab-chart.svg` — Group 1962 `758:1677` (27×27, unique)
**Provenance:** All 3 Analytics 3 SACRED frames `758:1530`, `758:1743`, `758:1891`. Figma root `758:1529`.
**Status:** ⬜ candidate — Sprint 3/5 Analytics 3 viewer.

---

### AnalyticsStatCard

**Class:** `.analytics-stat-card`
**Anatomy:**
- 105×104 card with glass fill (`--velo-color-alpha-steel-light-15`) + white stroke + `--velo-blur-glass-medium`
- `.asc-value` — large metric number (approx 28–32px, `--velo-color-steel-primary`, bold Marmelad)
- `.asc-label` — caption below number (12–14px, `--velo-color-steel-light`, normal Marmelad)
- Multiple instances in a 2×N grid layout on Reviews screen
**Variants:** none (single layout; value + label)
**States:** static (display-only)
**When to use:** KPI summary grid at the top of the Analytics reviews/stats screen. One card = one metric.
**Anti-patterns:**
- ❌ Don't add tap handlers to StatCards — display-only.
- ❌ Don't use a different card size — 105×104 is the Figma spec.
**Tokens consumed:**
- `--velo-color-alpha-steel-light-15` (card fill)
- `--velo-color-neutral-white` (card stroke)
- `--velo-blur-glass-medium` (backdrop-filter)
- `--velo-color-steel-primary` (value text)
- `--velo-color-steel-light` (label text)
- `--velo-radius-md` (card corners, ~15px)
**Provenance:** Analytics 3 SACRED frame `758:1743` (02_Reviews 2). Frames 2631, 2632, 2633. Figma root `758:1529`.
**Status:** ⬜ candidate — Sprint 3/5 Analytics 3 viewer.

---

### AnalyticsReviewCard

**Class:** `.analytics-review-card`
**Anatomy:**
- Full-width list item card (glass fill)
- `.arc-avatar` — 41×41 user avatar (`icon-analytics-user-circle.svg` as fallback placeholder)
- `.arc-header` — reviewer name + star rating row
- `.arc-body` — review text excerpt (body weight, `--velo-color-steel-primary`)
- `.arc-meta` — date + practice name (12px, `--velo-color-steel-light`)
**Variants:** none
**States:** default · possibly `.expanded` for long reviews
**When to use:** each row in the reviews list on the Analytics Reviews tab.
**Anti-patterns:**
- ❌ Don't use VAvatar for the reviewer icon — use `icon-analytics-user-circle.svg` placeholder.
- ❌ Don't display the full review inline — truncate to 2-3 lines.
**Tokens consumed:**
- `--velo-color-alpha-steel-light-15` (card fill)
- `--velo-color-neutral-white` (card stroke)
- `--velo-blur-glass-medium` (backdrop-filter)
- `--velo-color-steel-primary` (reviewer name + body text)
- `--velo-color-steel-light` (meta text)
- `--velo-color-coral-dark` / `--velo-color-teal-medium` (star rating indicator fills)
- `--velo-radius-md` (card corners)
**Icons (Figma exportAsync 2026-05-19):**
- Reviewer avatar → `assets/icons/icon-analytics-user-circle.svg` — Group 2629 `758:1875` (41×41)
**Provenance:** Analytics 3 SACRED frame `758:1530` (01_Reviews). Figma root `758:1529`.
**Status:** ⬜ candidate — Sprint 3/5 Analytics 3 viewer.

---

### AnalyticsPeriodChip

**Class:** `.analytics-period-chip`
**Anatomy:**
- 161×30 pill-shaped filter chip, Group 2549 from `758:1891` (03_Payments)
- Glass fill + pill border-radius + label text centered
- Active chip: filled (`--velo-color-alpha-steel-light-15` + white stroke 1px + blur)
- Inactive chip: transparent or muted background
**Variants:** `--active` · `--inactive`
**States:** default · `.is-active` (currently selected period)
**When to use:** period filter selector on the Payments/Finance analytics tab.
**Anti-patterns:**
- ❌ Don't reuse DiaryFilterTab for this — AnalyticsPeriodChip is wider (161px) with different semantics.
- ❌ Don't stack chips vertically — horizontal scroll row.
**Tokens consumed:**
- `--velo-color-alpha-steel-light-15` (active fill)
- `--velo-color-neutral-white` (active stroke)
- `--velo-blur-glass` (`blur(4px)`)
- `--velo-color-steel-primary` (text)
- `--velo-radius-pill`
**Provenance:** Analytics 3 SACRED frame `758:1891` (03_Payments). Group 2549. Figma root `758:1529`.
**Status:** ⬜ candidate — Sprint 3/5 Analytics 3 viewer.

---

### TransactionRow

**Class:** `.transaction-row`
**Anatomy:**
- 336×142 list item, Group 3048 from `758:1891` (03_Payments)
- `.tr-practice-name` — practice/session title (bold, `--velo-color-steel-primary`)
- `.tr-date` — transaction date (12–14px, `--velo-color-steel-light`)
- `.tr-amount` — monetary amount (teal for income, coral for refund/expense)
- `.tr-status` — optional status badge (VBadge `--success`/`--warning`)
**Variants:** `--income` (teal amount) · `--expense` / `--refund` (coral amount)
**States:** default · `:active` (tap to see transaction detail — future)
**When to use:** every row in the Payments/Finance tab transaction list.
**Anti-patterns:**
- ❌ Don't use the same amount color for both income and refund — teal vs coral is a semantic signal.
- ❌ Don't omit the date — timestamp is required for financial records.
**Tokens consumed:**
- `--velo-color-steel-primary` (practice name text)
- `--velo-color-steel-light` (date, secondary meta)
- `--velo-color-teal-medium` (income amount)
- `--velo-color-coral-dark` (refund/expense amount)
- `--velo-color-orange-medium` (pending/partial state amount)
- `--velo-border-default` (row divider)
- `--velo-radius-md` (row card background)
**Provenance:** Analytics 3 SACRED frame `758:1891` (03_Payments). Group 3048. Figma root `758:1529`.
**Status:** ⬜ candidate — Sprint 3/5 Analytics 3 viewer (Payments tab).

---

## NEW — promotion candidates (Practices 15 mining)

These surfaced during Practices 15 DS harvest (2026-05-19, Phase B). All ⬜ candidate. Figma root `758:1950` (15 frames: `241_Practices upcoming` through `255_Attendance 2`). Awaiting operator MOCKUP GATE pass when Practices 15 viewer is built in Sprint 5.

**Token audit result: zero new tokens.** All fills, radii, typography, and blur values in all 15 frames map to existing DS tokens. Fills: `#4C6589` → `--velo-color-steel-primary`; `#FBC088` → `--velo-color-orange-light`; `#FFF3EA` → `--velo-color-orange-50`; `#76DDE6` → `--velo-color-teal-light`; `#D66674` → `--velo-color-coral-dark`. Card glass surface: `--velo-color-alpha-steel-light-15`. All corner radii (16, 20, 252) and shadows already promoted. No `variables.css` changes needed.

---

### MasterPracticeCard

**Class:** `.master-practice-card`
**Anatomy:**
- `.mpc-head` — practice title (h2 weight) + `.mpc-badges` row (status VBadge: "Предстоящая", "Прошедшая", "В эфире")
- `.mpc-meta-row` — 3-slot horizontal meta strip, each slot: icon (15×15) + label text
  - Slot 1 (attendees) — `icon-practices-attendees.svg` + "N/M" count text
  - Slot 2 (recurrence) — `icon-practices-repeat.svg` + day abbreviation (e.g. "Сб")
  - Slot 3 (reviews) — `icon-practices-review-face.svg` + "N/M" review count
- `.mpc-datetime` — date+time row
- Entire card is tappable — opens practice detail view
**Variants:** `--upcoming` (active / editable) · `--past` (archived, read-only)
**States:** default · `.is-live` (practice in progress) · `:active` (scale 0.98)
**When to use:** master's own practices list (241_Practices upcoming, 242_Practices past). Distinct from user-facing `PracticeCard` — this card shows the master's operational meta (attendees capacity, recurrence schedule, review tally).
**Anti-patterns:**
- ❌ Don't reuse user-facing `PracticeCard` for master practice management — different meta row icons and anatomy.
- ❌ Don't show "Оплачено" badge here — payment status is not surfaced in master practice cards.
- ❌ Don't use 27×27 practice-type icon in the meta row — master practice meta uses 15×15 icons only.
**Tokens consumed:**
- `--velo-bg-card`, `--velo-color-alpha-steel-light-15` (border), `--velo-shadow-card`
- `--velo-radius-lg` (card)
- `--velo-color-steel-primary` (meta icon fill, baked in SVG + label text)
- `--velo-font-body-sm` (meta label text)
- `--velo-space-8` (gap between icon and label)
**Icons (Figma exportAsync 2026-05-19):**
- Attendees slot → `assets/icons/icon-practices-attendees.svg` — Group 2689 `758:2010` (16×15)
- Recurrence slot → `assets/icons/icon-practices-repeat.svg` — Group 2820 `758:2019` (15×15)
- Reviews slot → `assets/icons/icon-practices-review-face.svg` — Group 2940 `758:2024` (15×15)
**Related:** VBadge (status chip), PracticeCard (user-facing counterpart — different component)
**Provenance:** Practices 15 SACRED frames `758:1951` (241_Practices upcoming), `758:2111` (242_Practices past), `758:2912` (253_Past alt), `758:3003` (254_Past 3). Figma root `758:1950`.
**Status:** ⬜ candidate — Sprint 5 master-practices viewer.

---

### PracticesFAB

**Class:** `.practices-fab`
**Anatomy:**
- Single circular button, 52×52 (matches `--velo-button-height`)
- Background: `--velo-bg-button-primary` (teal gradient per VButton `--primary`)
- Icon: `icon-practices-add.svg` (20×20 white "+" cross path) centered
- Positioned absolute bottom-right above BottomNav
- No text label — icon-only affordance
**Variants:** none (single CTA per screen)
**States:** default · `:active` (scale 0.95, opacity 0.9)
**When to use:** "Новая практика" add-practice CTA — bottom-right FAB on `241_Practices upcoming` (`758:1951`). Visible only on the upcoming practices list.
**Anti-patterns:**
- ❌ Don't show PracticesFAB on any screen other than the upcoming practices list.
- ❌ Don't use a text button for this action in the master context — FAB is the Figma spec.
- ❌ Don't style as `--glass` — the FAB uses the primary gradient fill.
**Tokens consumed:**
- `--velo-bg-button-primary` (teal gradient)
- `--velo-shadow-button` (halo)
- `--velo-radius-pill` (full circle)
- `--velo-button-height` (52px size)
**Icons (Figma exportAsync 2026-05-19):**
- "+" icon → `assets/icons/icon-practices-add.svg` — BOOLEAN_OPERATION (Union) `758:1979` (20×20, white fill)
**Related:** VButton `--primary` (inherits the same token set), VButton `--round-icon`
**Provenance:** Practices 15 SACRED frame `758:1951` (241_Practices upcoming). Figma root `758:1950`.
**Status:** ⬜ candidate — Sprint 5 master-practices list screen.

---

### PracticeWarningPanel

**Class:** `.practice-warning-panel`
**Anatomy:**
- Full-width panel block inside a modal overlay
- `.pwp-body` — horizontal row: leading `icon-practices-warning.svg` (29×26) + text content column
  - `.pwp-title` — uppercase label (e.g. "ОТМЕНИТЬ ПРАКТИКУ?", "ВАЖНО!")
  - `.pwp-text` — explanatory body text (body weight, steel-primary)
- Background: `--velo-color-orange-50` (`#FFF3EA`)
- Border: 1px `--velo-color-orange-light` (`#FBC088`)
- CornerRadius: `--velo-radius-lg` (16px)
**Variants:** none
**States:** static (display-only inside a modal)
**When to use:** warning/consequence notice inside destructive practice-management modals — `248_Cancel reservation` (`758:2732`) and `249_Abolish practice` (`758:2771`).
**Anti-patterns:**
- ❌ Don't use PracticeWarningPanel outside a modal context — inline warnings use WarningAlert.
- ❌ Don't substitute `icon-warning.svg` (fill `#A16124`) — the Practices modals use `icon-practices-warning.svg` (fill `#FBC088`) on the orange-50 panel background.
- ❌ Don't make PracticeWarningPanel tappable — it is a static informational block.
**Tokens consumed:**
- `--velo-color-orange-50` (`#FFF3EA`) — panel background
- `--velo-color-orange-light` (`#FBC088`) — panel border + warning icon fill (baked in SVG)
- `--velo-color-steel-primary` (`.pwp-text` body)
- `--velo-color-orange-dark` (`.pwp-title` uppercase label)
- `--velo-radius-lg` (panel corners)
**Icons (Figma exportAsync 2026-05-19):**
- Warning icon → `assets/icons/icon-practices-warning.svg` — Group 2069 `758:2755` (29×26, fill #FBC088)
**Related:** WarningAlert (similar anatomy — candidate for unification at Sprint 5 review)
**Provenance:** Practices 15 SACRED frames `758:2732` (248_Cancel reservation, 350×365), `758:2771` (249_Abolish practice, 350×466). Figma root `758:1950`.
**Status:** ⬜ candidate — Sprint 5 practices cancel/abolish modals.

---

### CreatePracticeWizard

**Class:** `.create-practice-wizard`
**Anatomy:**
- 3-step wizard spanning frames `758:2249` (step 1) → `758:2349` (step 2) → `758:2459` (step 3)
- `.cpw-progress` — step indicator at top (dots or numbered chips: 1 / 2 / 3)
- `.cpw-body` — form fields specific to each step:
  - Step 1: practice name, type selector, category, description textarea
  - Step 2: date + time picker, duration selector, recurrence controls (day chips)
  - Step 3: capacity input, price field, location / zoom link
- `.cpw-footer` — "Далее →" primary button (steps 1–2) / "Создать" primary button (step 3) + "Назад" ghost link
**Variants:** none (3-step linear flow)
**States:** step 1 · step 2 · step 3 · submitting
**When to use:** new practice creation initiated from PracticesFAB tap. Full-screen 3-step form. Do not condense into a single long-scroll form.
**Anti-patterns:**
- ❌ Don't skip the progress indicator — step context is required for a 3-screen wizard.
- ❌ Don't allow "Создать" on step 3 if required fields in steps 1-2 are empty.
- ❌ Don't reuse this for practice editing — Edit uses a flat form, not a wizard.
**Tokens consumed:**
- VInput `--pill` (form fields throughout)
- VButton `--primary` ("Далее" / "Создать"), VButton `--glass` or VLink ("Назад")
- `--velo-dot-active` / `--velo-dot-passive` (VDots progress indicator)
- `--velo-bg-card` (step panel bg), `--velo-shadow-card`
**Related:** VInput, VButton, VDots (progress), PracticesFAB (entry point)
**Provenance:** Practices 15 SACRED frames `758:2249` (243_New practice step 1, 804×1748), `758:2349` (244_New practice step 2, 804×1748), `758:2459` (245_New practice step 3, 804\u00d71748). Figma root `758:1950`.
**Status:** ⛹️ candidate — Sprint 5 master-practice-create flow.

---

## NEW — promotion candidates (Master Dashboard 8 mining)

> Source: SACRED root `758:3245` (”ДАШБОРД“), 8 screens. DS iteration 10, 2026-05-19.

---

### MasterHeaderBar

**Class:** `.master-header-bar`
**Anatomy:**
- Full-width top bar, 342x45
- `.mhb-avatar` — circular avatar 36x36, `--velo-radius-pill` — left slot
- `.mhb-title` — screen title text, centered — center slot
- `.mhb-notif` — circular icon button 36x36, `--velo-color-steel-primary` fill — right slot; uses `icon-master-header-notif.svg` (white bell 20x21)
- Background: `--velo-bg-screen` (transparent, app bg shows through)
**Variants:** none observed
**States:** default - notif-active (badge dot over bell, reserved)
**When to use:** top bar on all Master Dashboard 8 screens. Avatar identity + notification shortcut.
**Anti-patterns:**
- No back arrow — top-level master dashboard header.
- Do not use `icon-master-header-notif.svg` on non-steel backgrounds without color inversion.
**Tokens consumed:**
- `--velo-color-steel-primary` (notif button fill)
- `--velo-radius-pill` (avatar + notif button)
- `--velo-bg-screen`
**Icons (Figma exportAsync 2026-05-19):**
- Bell → `assets/icons/icon-master-header-notif.svg` — node `758:3677` (20x21, white fill)
**Related:** VAvatar (avatar slot), MasterNavBar (paired bottom nav)
**Provenance:** Master Dashboard 8 SACRED frame `758:3245`. Figma root `758:3245`.
**Status:** candidate — Sprint 6 master-dashboard screens.

---

### MasterStatCard

**Class:** `.master-stat-card`
**Anatomy:**
- Card 336x140-185 (height varies), `--velo-radius-lg`, `--velo-bg-card`, `--velo-shadow-card`
- `.msc-header` — stat label + period tab group ("Нед / Мес / Год")
- `.msc-value` — large numeric value (32px `--velo-typo-h1-size`) + unit or delta
- `.msc-chart` — bar chart; inactive bars use `rgba(171,191,218,0.15)` (component-local literal); active bar `--velo-color-steel-primary`
- `.msc-footer` — optional footnote / legend
**Variants:** `--attendance` - `--revenue` - `--students`
**States:** default - period-tab-active
**When to use:** top-level metric summary cards on the master dashboard overview.
**Anti-patterns:**
- Do not promote `rgba(171,191,218,0.15)` to a token — single-use bar chart fill, keep component-local.
**Tokens consumed:**
- `--velo-bg-card`, `--velo-shadow-card`, `--velo-radius-lg`
- `--velo-typo-h1-size` (32px value)
- `--velo-color-steel-primary` (active bar + active tab)
- `--velo-color-steel-pale` (inactive tab text)
**Related:** MasterStudentProfile (detail card), AnalyticsStatCard (analytics block analogue)
**Provenance:** Master Dashboard 8 SACRED frames under root `758:3245`. Figma root `758:3245`.
**Status:** candidate — Sprint 6 master-dashboard overview.

---

### MasterStudentRow

**Class:** `.master-student-row`
**Anatomy:**
- List row 336x50, `--velo-radius-md`, `--velo-bg-card`
- `.msr-avatar` — circular avatar 36x36, `--velo-radius-pill` — left
- `.msr-name` — student name, body weight — center top
- `.msr-meta` — secondary info (tier, last seen), footnote — center bottom
- `.msr-badge` — optional MasterStatusBadge / VBadge — right slot
- Separator: 1px `--velo-border-default` between rows (not on last)
**Variants:** `--with-badge` - `--without-badge`
**States:** default - pressed (opacity 0.85)
**When to use:** student list rows on the master dashboard students screen.
**Anti-patterns:**
- Do not use BookingCard for student list items — different content model.
**Tokens consumed:**
- `--velo-bg-card`, `--velo-radius-md`
- `--velo-color-steel-primary` (name), `--velo-color-steel-light` (meta)
- `--velo-border-default` (row separator), `--velo-radius-pill` (avatar)
**Related:** VAvatar, MasterStatusBadge, MasterStudentProfile (tap target)
**Provenance:** Master Dashboard 8 SACRED frame `758:3948` (Student Profile screen). Figma root `758:3245`.
**Status:** candidate — Sprint 6 master-students list.

---

### MoodProgressBar

**Class:** `.mood-progress-bar`
**Anatomy:**
- Full-width bar 336x59, `--velo-radius-lg` container
- `.mpb-track` — horizontal CSS gradient: `--velo-color-steel-wash` → `--velo-color-teal-wash` → `--velo-color-coral-wash` → `--velo-color-peach-wash`
- `.mpb-thumb` — circular indicator along track at current mood value
- `.mpb-labels` — 4 mood label strings beneath track
- `.mpb-value` — optional numeric/emoji value above thumb
**Variants:** full-width (default) - compact (~100px embedded in CheckInRow)
**States:** static (display-only in SACRED) - interactive (reserved for future check-in input)
**When to use:** mood score visualisation on student profile cards and check-in list rows in master dashboard.
**Anti-patterns:**
- Do not substitute a solid fill bar — the 4-stop gradient is the Figma spec.
- Do not hardcode hex values — always reference the 4 wash tokens.
**Tokens consumed:**
- `--velo-color-steel-wash` (#dce6f3) — gradient stop 1 (cool end)
- `--velo-color-teal-wash` (#bdecf1) — gradient stop 2 (teal mid)
- `--velo-color-coral-wash` (#f9cbd1) — gradient stop 3 (warm-mid)
- `--velo-color-peach-wash` (#fddfc4) — gradient stop 4 (warm end)
- `--velo-radius-lg` (track container)
- `--velo-color-steel-primary` (thumb border / active label)
**Related:** CheckInRow (contains MoodProgressBar), MasterStudentProfile (contains MoodProgressBar)
**Provenance:** Master Dashboard 8 SACRED frames `758:3948` (Student Profile) + `758:4068` (Check-ins). 27 total occurrences. Figma root `758:3245`.
**Status:** candidate — Sprint 6 master-dashboard student profile + check-ins.

---

### MasterStudentProfile

**Class:** `.master-student-profile`
**Anatomy:**
- Card 336x271, `--velo-radius-lg`, `--velo-bg-card`, `--velo-shadow-card`
- `.msp-header` — row: VAvatar 48x48 + name + subtitle (subscription/role)
- `.msp-rating` — row of `icon-master-rating-star.svg` (18x17) x N + numeric value
- `.msp-mood` — MoodProgressBar (full width)
- `.msp-stats` — 2-3 column stat grid (practices attended, streak, score)
- `.msp-actions` — row of ghost/glass action buttons
**Variants:** none
**States:** default - loading (skeleton shimmer)
**When to use:** expanded student detail card on the master dashboard student profile screen.
**Anti-patterns:**
- Do not show MasterStudentProfile inline in a list — use MasterStudentRow for list view.
**Tokens consumed:**
- `--velo-bg-card`, `--velo-shadow-card`, `--velo-radius-lg`
- MoodProgressBar tokens (see above)
- `--velo-color-coral-medium` (rating star fill, baked in SVG #D66674)
- VAvatar, VButton tokens
**Icons (Figma exportAsync 2026-05-19):**
- Rating star → `assets/icons/icon-master-rating-star.svg` — node `758:3967` (18x17, fill #D66674)
**Related:** MasterStudentRow (list view), MoodProgressBar (embedded), VAvatar
**Provenance:** Master Dashboard 8 SACRED frame `758:3948` (336x271). Figma root `758:3245`.
**Status:** candidate — Sprint 6 master-dashboard student profile screen.

---

### CheckInRow

**Class:** `.checkin-row`
**Anatomy:**
- List row 336x59, `--velo-radius-md`, `--velo-bg-card`
- `.cr-alert-icon` — left: `icon-master-checkin-alert.svg` (37x40 flame, #D4863C) — visible when urgent
- `.cr-info` — center: student name (top) + check-in timestamp/status (bottom)
- `.cr-mood` — right: MoodProgressBar compact variant (~100px)
- Separator: 1px `--velo-border-default` between rows
**Variants:** `--urgent` (alert icon visible) - `--completed` (muted palette)
**States:** default - pressed (opacity 0.85)
**When to use:** check-in list rows on the master dashboard check-ins screen.
**Anti-patterns:**
- Do not hide the alert icon on urgent rows — it is the primary urgency signal.
- Do not substitute VBadge as the alert indicator — the flame SVG is the Figma spec.
**Tokens consumed:**
- `--velo-bg-card`, `--velo-radius-md`
- `--velo-color-orange-medium` (alert icon fill, baked in SVG #D4863C)
- `--velo-border-default` (separator)
- MoodProgressBar tokens (compact embedded)
**Icons (Figma exportAsync 2026-05-19):**
- Alert flame → `assets/icons/icon-master-checkin-alert.svg` — node `758:4057` (37x40, fill #D4863C)
**Related:** MoodProgressBar (embedded), MasterStudentProfile (tap target)
**Provenance:** Master Dashboard 8 SACRED frame `758:4068` (Check-ins screen). Figma root `758:3245`.
**Status:** candidate — Sprint 6 master-dashboard check-ins screen.

---

### MasterNavBar

**Class:** `.bottom-nav.bottom-nav--master`
**Anatomy:**
- Container: `.bottom-nav.bottom-nav--master` flex-row — inherits all `.bottom-nav` layout
- Figma spec: 327×63px container, 4 children each 63×63px, padding 0 8px 22px
- 4 items: `button.v-button.v-button--glass.v-button--round-icon`
- Button background: `rgba(98, 122, 156, 0.15)` = `--velo-color-alpha-steel-light-15` (both active and inactive)
- Icon fill: `#4C6589` = `--velo-color-steel-primary`
- Icon size: 24×24px displayed (icons are 27×27 viewBox, displayed smaller)
**Variants:** semantic modifier `.bottom-nav--master` distinguishes from user nav.
**Slot mapping (left to right):**
1. Home → `icon-master-nav-home.svg` (`758:3384`, firstM=M17.1121)
2. Schedule → `icon-master-nav-schedule.svg` (`758:1759`, firstM=M7.48828) ✅ NEW 2026-05-19
3. Students → `icon-master-nav-students.svg` (`758:1765`, firstM=M9.28125, 21×27) ✅ FIXED 2026-05-19
4. Master Profile → `icon-master-nav-profile.svg` (`758:1770`, firstM=M26.9945) ✅ NEW 2026-05-19
**States:** one button has `.active` class at all times.
**When to use:** all master-role screens that have bottom navigation.
**Anti-patterns:**
- ❌ Don't reuse user nav icons — master nav has distinct icons (slot 4 profile is different shape).
- ❌ Don't add background tint on active button — same glass fill as inactive.
**Tokens consumed:**
- `--velo-color-alpha-steel-light-15` (button bg, both states)
- `--velo-color-steel-primary` (icon fill, baked in SVG)
- `.bottom-nav` base layout tokens (see BottomNav above)
**Icons (Figma exportAsync 2026-05-19, from Group 2648 in АНАЛИТИКА screen `758:1748`):**
- Home → `assets/icons/icon-master-nav-home.svg` — `758:3384` (27×27)
- Schedule → `assets/icons/icon-master-nav-schedule.svg` — `758:1759` (27×27)
- Students → `assets/icons/icon-master-nav-students.svg` — `758:1765` (21×27)
- Master Profile → `assets/icons/icon-master-nav-profile.svg` — `758:1770` (27×27)
**Related:** BottomNav (user variant), VButton `--round-icon`, VButton `--glass`
**Provenance:** Master АНАЛИТИКА screen `758:1748` (Group 2648 — distinct master nav). ⚠️ ДАШБОРД frames share Group 1988 with user nav — master-specific nav only in АНАЛИТИКА screens.
**Status:** ✅ PROMOTED — DS-first §7.0. Components in `_shared/components.css`. Visualized in `velo-design-system.html` Bottom Navigation section.

---

## NEW — promotion candidates (Calendar 11 mining)

Surfaced during Calendar 11 rebuild pass (2026-05-19). All ⬜ candidate, pending MOCKUP GATE.

### CalendarWeekStrip

**Class:** `.cal-week-strip`
**Anatomy:** `.cal-week-cells` row of 7 `.cal-day-cell` + `.cal-week-nav-row` below. Cell parts: `.cdc-label` (day abbreviation) + `.cdc-num` (date number) + `.cdc-dot` / `.cdc-dot-empty` (event indicator).
**States:** `.active` on current/selected day.
**When to use:** Calendar screens — weekly date picker.
**Status:** ⬜ candidate.

---

### CalFilterButton

**Class:** `.cal-filter-btn`
**Anatomy:** dark steel pill — `.cal-filter-btn-icon` (funnel SVG) + `.cal-filter-btn-label` + `.cal-filter-caret`.
**When to use:** Calendar header — opens filter overlay.
**Status:** ⬜ candidate.

---

### FilterPanel

**Class:** `.filter-panel`
**Anatomy:** bottom sheet — `.filter-panel-header` + `.filter-body` with `.filter-group` / `.filter-chips` / `.filter-chip` rows.
**States:** `.filter-chip--select` / `.filter-chip.active` for selected chips.
**Status:** ⬜ candidate.

---

### PracticeDetailCard

**Class:** `.practice-detail-card`
**Anatomy:** white card — `.pdc-icon` + `.pdc-name` + `.pdc-meta-row` (`.pdc-meta-item` rows) + `.complexity-row` (`.cplx-dots`).
**When to use:** Practice detail screens (Calendar col 03, 07).
**Status:** ⬜ candidate.

---

### MasterProfileHero

**Class:** `.mpr-hero`
**Anatomy:** centered column — `.mpr-avatar` (80×80) + `.mpr-name` + `.mpr-badges` + `.mpr-bio` + `.mpr-stats-row` (`.mpr-stat-card` grid).
**When to use:** Master public profile (Calendar col 05).
**Status:** ⬜ candidate.

---

### FeedbackRating

**Class:** `.fbk-card`
**Anatomy:** white card — `.fbk-heading` + `.fbk-sub` + `.feedback-rating` row of `.fr-option` (`.fr-icon` + `.fr-label`).
**Icons:** icon-feedback-questions.svg · icon-feedback-good.svg · icon-feedback-fire.svg
**When to use:** Post-practice feedback (Calendar col 09).
**Status:** ⬜ candidate.

---

### MessageWidget

**Class:** `.msg-widget`
**Anatomy:** white card — `.msg-master-card` (`.msg-master-avatar` + `.msg-master-info`) + `.msg-body` (textarea) + `.msg-actions`.
**When to use:** Ask Master / Message thread (Calendar col 07, 11).
**Status:** ⬜ candidate.

---

### AskMasterMiniCard

**Class:** `.ask-master-mini-card`
**Anatomy:** row card — `.ask-master-avatar` (44×44) + `.ask-master-info` (`.ask-master-name` + `.ask-master-sub`).
**When to use:** Ask Master flow (Calendar col 06, 07).
**Status:** ⬜ candidate.

---

### CalSuccessBody

**Class:** `.cal-success-body`
**Anatomy:** centered column — `.cal-success-icon` (SVG illustration) + `.cal-success-title` + `.cal-success-sub`.
**When to use:** Check-in success / Booking confirmed screens (Calendar col 10).
**Status:** ⬜ candidate.

---