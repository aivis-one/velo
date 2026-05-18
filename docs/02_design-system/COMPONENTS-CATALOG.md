# VELO Design System — Components Catalog

Last updated: 2026-05-18
Version: 1.1
Status: Sprint 2 Calendar 11 DS harvest — Calendar 11 candidates added (6 new), total components: 30+

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
**When to use:** detail / nested views (check-in, booked-practice, booking-detail, reservations, AI-summary, practice-live).
**Tokens consumed:**
- `--velo-shadow-button-glass`, `--velo-glass-fill`, `--velo-radius-pill` (back button)
- typography h2-style for title
**Status:** ⬜ candidate (Dashboard 9, 2026-05-18)

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

### BottomNav

**Class:** `.bottom-nav`
**Anatomy:**
- Container: `.bottom-nav` flex-row, no background — buttons sit directly on screen bg
- 4 items: `button.v-button.v-button--glass.v-button--round-icon` (52×52 glass circle)
- Active item gets `.active` modifier → `color: steel-primary`, `::after fill: glass-fill-hover`
- Tab icons rendered as `<img>` inside each button: `icon-nav-home.svg` (active, 40px render) · `icon-nav-diary.svg` (27×27) · `icon-nav-reservations.svg` (27×27) · `icon-nav-profile.svg` (21×27)
**States:** one button has `.active` class at all times.
**Layout:** fixed bottom bar, full-width, 4-equal-column grid. Home is always center-left (tab 2 of 4) per SACRED.
**When to use:** every Dashboard-block screen — the persistent bottom navigation.
**Anti-patterns:**
- ❌ Don't add a 5th tab — SACRED is strictly 4. Overflow = sprint 7+ admin concern.
- ❌ Don't apply `--velo-shadow-button-glass` to inactive tabs — only active home.
**Tokens consumed:**
- `.bn-tab--active` → `--velo-shadow-button-glass`, `--velo-glass-fill`, `--velo-blur-glass-medium` (5.04px on glass circle), `--velo-color-neutral-white` (border)
- icons baked in SVG with `--velo-color-steel-primary` fill (#4C6589)
- `--velo-text-muted` (inactive labels), `--velo-text-primary` (active label)
**Icons (Figma exportAsync 2026-05-18):**
- `02_design-system/assets/icons/icon-nav-home.svg` — Group 1984 `541:6756` (active, 134×134 with glass circle + glow filter)
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
- `--duration`      → `assets/icons/icon-cal-duration.svg` — Group 1976 `648:1768` (15×15)
- `--datetime`      → `assets/icons/icon-cal-datetime.svg` — Group 1975 `648:1774` (15×15)
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