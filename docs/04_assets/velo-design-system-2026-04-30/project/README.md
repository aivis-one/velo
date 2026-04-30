# VELO Design System

VELO (stylized **VELΘ**) is a wellness / mindfulness mobile app — a "space for practice and inner growth" (*Пространство для практики и внутреннего развития*). The product is designed primarily in Russian for the RU/CIS market and centers on guided meditation, breath practice, and instructor-led sessions.

The brand voice is **calm, soft-spoken, and grounded** — closer to a yoga teacher than a SaaS app. Visuals lean on a single dusk-blue ink color, sparse white space, and a recurring **mandala** motif rendered at low opacity as page atmosphere.

---

## Sources

- **Figma file:** mounted as `VELO.fig` (1 page, 5 frames: Decorations, Components, Mockup-mined, Approved Patterns, Icons). All design tokens, components and screen patterns were reconstructed from this file via the figma VFS.
- **Font:** `uploads/Marmelad-Regular.ttf` provided by the user — copied into `fonts/`.
- **No production codebase** was provided. Component implementations in `ui_kits/` are clean re-creations of the Figma mockups, not lifts from a real repo.

---

## Index

- `colors_and_type.css` — root CSS: brand palette, font face, type scale, spacing, radii, shadow, reusable atoms (`.velo-pill-button`, `.velo-input`, `.velo-card`, `.velo-page-bg`).
- `fonts/Marmelad-Regular.ttf` — the only typeface; covers Cyrillic + Latin.
- `assets/brand/` — mandala SVGs (re-colored to brand ink), supporting photos.
- `preview/` — design-system tab cards (foundations, type, components).
- `ui_kits/velo-app/` — interactive iPhone-frame UI kit covering Welcome → Login → Home → Calendar → Profile.
- `SKILL.md` — Agent-Skill manifest so this folder works as a Claude Code skill.

---

## Content fundamentals

**Language.** Primary copy is **Russian**. Latin is reserved for the wordmark (`VELΘ`) and a handful of technical labels (`E-mail`). When localizing, keep the Russian as the canonical surface and treat English as fallback.

**Tone.** Warm, second-person *informal* (`Войдите, чтобы продолжить практику` — "Sign in to continue your practice"). Verbs are gentle and inviting — *войти, продолжить, создать* — never imperative ("submit", "go"). Avoid corporate / SaaS phrasings.

**Casing.**
- Section labels in the design file are **ALL-CAPS** (`AUTH`, `ONBOARDING`, `DASHBOARD`) — that's an internal organizing convention, not user-facing.
- User-facing UI uses **sentence case** in Russian: `Утренняя медитация`, `Забыли пароль?`, `Создать аккаунт`.
- Numbers and units sit on the same baseline: `45 мин`, `156 Практик`, `Завтра, 07:00`.

**Person.** Speak *to* the user (`войдите`, `продолжите`) — never "we" or "the app". The brand isn't a personality; it's a quiet space.

**Emoji.** Not used. The brand is intentionally minimal-iconographic — a single mandala silhouette is the only ornament.

**Specific phrasings observed:**
- Welcome: *"Пространство для практики и внутреннего развития"*
- Login: *"С возвращением!"* / *"Войдите, чтобы продолжить практику"*
- Booking meta: *"Завтра, 07:00 · 45 мин"* — comma + middle-dot separator
- Status chips: *"Оплачено"* (Paid), *"Mindfulness"*, *"MBSR"* — the only place tags use Latin script
- Stats labels: *"Практик"* / *"Отзывов"* (lowercase noun, no period)

---

## Visual foundations

**Single dominant color.** Everything visible — text, icons, primary button, mandala — is the same dusk-blue ink **`#4C6589`** (`rgb(76, 101, 137)`). Variants:
- `#627A9C` — primary button fill (one shade lighter)
- `#8293AC` — secondary text and hints
- 70% / 15% / 18% alpha for timestamps, glass chips, hairlines

**One accent.** A pale mint **`#76DDE6`** at 30% opacity, paired with deeper teal text `#2F9EA8`. Used *only* for "paid / verified / success" status chips. Never for primary CTAs.

**Backgrounds.** Soft sky tints (`#E8F0FF` / `#E2F0FD`), never pure white. Pure white (`#FFFFFF`) is reserved for cards and the tab-bar glass border. No gradients on backgrounds — atmosphere comes from the mandala overlay.

**Mandala motif.** The signature decorative element. A 23-vector circular pattern positioned absolutely in the upper third of every onboarding/auth screen, sized ~491px on a 402px-wide phone (so it bleeds off both sides), rendered at **12% opacity** in the brand ink. Never animated, never the focal element — pure atmosphere. Available as `assets/brand/mandala-mask.svg`.

**Type.**
- Single typeface: **Marmelad** (a soft humanist sans with full Cyrillic support). One weight only — Regular 400.
- Line-height is always **100%** (tight) in the source file. Letter-spacing 2% on small/meta text.
- Scale: 48 / 32 / 28 / 18 / 16 / 14. No 12pt — the smallest type in the app is 14px.

**Spacing.** 4-point grid. The most common gaps are **8 / 16 / 24 / 32**. Card padding is uniformly **24px**. Page padding (left/right) is **33px** on a 402px artboard (roughly 8% of width).

**Borders.** Hairlines at `rgba(76,101,137,0.18)`. Buttons get a **1px solid white** border on top of the colored fill — gives them a subtle "frosted" feel. Inputs get a 1px ink border.

**Corner radii.**
- **15px** — every card, every calendar cell, every booking row. This is the system's signature radius, not 12 or 16.
- **200px** (full pill) — every button, input, avatar, chip, glass tab.
- **5px** — small status chips inside cards (the "Оплачено" badge).
- **252px** — tab-bar glass circles (also a full pill — 63px circles).

**Shadow.** Almost none. Cards sit flush. The one shadow in the system is the **white "halo"** behind the active tab-bar glass circle: `0 0 26px 8px rgba(255,255,255, 0.85)` — it gives the active tab a soft blooming glow against the sky.

**Glassmorphism.** Specific to the tab bar: `rgba(98,122,156,0.15)` background + `1.26px solid white` border + `backdrop-filter: blur(5px)`. The active item adds the white halo above. This pattern is reserved for the tab bar — don't generalize it to other surfaces.

**Hover / press.** Not specified in the source file (it's a mobile design). For web prototypes the system uses:
- Hover → opacity 0.9
- Press → `transform: scale(0.98)`
- No color shifts on hover.

**Animation.** Not specified in static mockups. The brand vibe suggests **slow, breath-paced** motion: 400–600ms eased fades, gentle scale-ins. Never bounces, never spring. Treat motion the way the visuals treat shadow — a touch, not a feature.

**Layout rules.**
- Phone artboard is **402 × 876** (a 9:19.6 ratio — modern iPhone safe area).
- Page side padding **33px** (~8% of width). Top safe-area starts ~80px below the bezel.
- Tab bar floats **24px above the home indicator**, centered, **327×63**.
- Stack rhythm in cards: 4–8px between same-group lines, 16–24px between groups.

**Imagery.** Photographic content (instructor avatars, hero photos) skews **cool / desaturated** to match the ink palette. No grain, no duotone — just slightly muted color. Photos appear in **circles** (avatars, master cards) inside an ink hairline border, never as squares.

**Transparency.** Used as a system, not a flourish:
- Text alpha (`0.7`, `0.18`) for hierarchy without introducing new colors
- 12% mandala overlay
- 15% ink for glass chip fills
- 30% mint for the paid chip background

**Cards.** White fill, 15px radius, 24px padding, no border, no shadow. Variation comes from contents (photo + name + tags, day-cell number + dot, two-up stats), not from the card chrome itself.

---

## Iconography

**Approach: minimal, custom-drawn line/fill SVGs** — not a third-party icon set. Every icon in the Figma file is hand-drawn at 27×27 inside a 63px circular glass tab, or smaller (15×15) for inline meta icons next to text. All icons render in `--velo-ink` `#4C6589`.

**Icon families observed in the file:**
- **Tab bar (4):** home, calendar, list, profile — circular outlines + simple glyphs.
- **Booking meta (small):** clock, calendar mini, check.
- **Decoration / illustration (large):** "Hands Decor" (large hands cradling a swirl), "Sun Mark", "Quill Pen", small mandala rosettes. These are *illustrations*, not utility icons — used once, large, on onboarding hero screens.

**No icon font** is used (no Material/Fontawesome references in the file).

**No emoji.** No unicode pictographs.

**For the UI kit I substituted** the line glyphs with [Lucide](https://lucide.dev/) (CDN-loaded) where pixel-exact matches weren't worth re-drawing — `Home`, `CalendarDays`, `ListChecks`, `User`, `Clock`, `CalendarDays`, `Check`. Lucide's stroke weight (~1.5px) is close enough to the source. **Flagged to user** below.

**Decorative SVGs copied in:**
- `assets/brand/mandala-mask.svg` — the 491×491 mandala at brand ink (12% opacity in use)
- `assets/brand/mandala-large-mask.svg` — same artwork, alternate scale

For full-fidelity production, the original decorations (Hands, Sun, Quill) should be re-exported from Figma — they were not flat SVGs in the source (composed of 23+ sub-vectors each) and are not reproduced here.

---

## Caveats / asks

> **⚠️ Font substitution at risk.** Marmelad-Regular was provided. If a Marmelad **Bold** or **Light** is needed for hierarchy, please supply — I am intentionally using one weight only, which mirrors the source file but is restrictive.
>
> **⚠️ Icons substituted with Lucide.** The Figma file's tab and meta icons are custom-drawn. I used Lucide for the UI kit because re-drawing each from 23+ sub-vectors would be lossy. If you want the original line work, please export the icon symbols as flat SVGs from Figma and drop them in `assets/icons/`.
>
> **⚠️ No real codebase.** Components in `ui_kits/velo-app/` are *visual* recreations from Figma pseudocode, not implementation reference.
>
> **⚠️ "Hands", "Sun Mark", "Quill" decorations were not extracted** — they're composed of dozens of sub-vectors in the source. Placeholder SVGs / omission used in the kit.
