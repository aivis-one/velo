# VELO Design System

> **VELO** (стилизуется как **VELΘ**) — wellness-платформа: медитация, дыхательные практики, дневник осознанности.
> Mobile-first (iOS + Android), плюс desktop landing. Полноценные Light и Dark темы.
> Целевая аудитория — русскоязычные 25–45, mindfulness-аудитория.

This folder is a self-contained design system you can give to any designer or AI agent to produce on-brand work. It's grounded in the single source of truth we were given: the `VELΘ App.fig` Figma file.

## Sources

- **Figma:** `VELΘ App.fig` (one page · four frames: Foundations, Components, Icons, Patterns). Read directly via the mounted VFS at `/Design-System/*`. Everything below was extracted from that file's pseudocode JSX, not from screenshots.
- **Fonts:** Marmelad Regular (Google Fonts). One family across all 10 text styles.
- **Icons:** 50 Lucide outline icons (24×24, stroke 1.5) + 12 brand wellness PNG sprites (filled silhouette style, one per concept).

## Brand in one paragraph

VELO is **calm, aware, friendly — but never childish**. It's wellness/mindfulness, never medical, never corporate. The voice addresses the reader with a quiet "вы" ("Доброе утро", "Начните свой путь осознанных практик"). Imagery is soft: mandalas, radial gradients, muted steel-blue on warm white. Nothing shouts. Nothing is clinical. The signature visual is the logo — **VELΘ** with the Greek theta, rendered in Marmelad over a pale circular mandala.

## File index

```
README.md                  ← this file
SKILL.md                   ← agent-invocable skill manifest
colors_and_type.css        ← all CSS variables: primitives + semantic (Light + Dark)
fonts/                     ← Marmelad loaded via Google Fonts (see note)
assets/
  brand/mandala.png          ← 400×400 soft mandala, the signature motif
  brand-icons/*.png          ← 12 wellness icons (one style each)
preview/                   ← HTML cards registered to the Design System tab
ui_kits/mobile/            ← iOS/Android app UI kit — components + index.html
```

## High-level architecture

The system is three layers, in this order:

1. **Primitives** — raw palette chips and type sizes. Never used in components directly.
2. **Semantic tokens** — `surface/*`, `text/*`, `border/*`, `icon/*`, `accent/*`, `feedback/*`. Every component binds to these. Swapping `[data-theme="dark"]` on `<html>` rewires the same token names to different primitives — every surface, text, icon, and border flips together.
3. **Components** — 26 top-level components (Button 4×4 variant matrix, Chip 5 states, Input/Select/Toggle, Tab Bar, Avatars, Cards, Modals, Toast). All touch targets ≥ 44×44 px.

> **Localization note:** UI copy is Russian. Token/component names are English. Keep this split.

---

## CONTENT FUNDAMENTALS

**Voice.** Mindful, quiet, encouraging. Second-person formal ("вы"), though implicit — we usually don't pronounce the pronoun at all, we just greet and suggest. Never imperative-barking; always an invitation.

**Tone examples (lifted verbatim from Figma):**
- Greeting: *"Доброе утро, Алина"*
- Card titles: *"Ближайшая практика"*, *"AI-саммари"*, *"Утренняя медитация"*
- Check-in nudge (warm variant): *"Пора на check-in!"* · *"Утренняя медитация через 30 минут"*
- Empty state: *"Пока нет практик"* / *"Запишитесь на ближайшую сессию, и она появится здесь"*
- Error state: *"Что-то пошло не так"* / *"Не удалось загрузить данные. Проверьте соединение и попробуйте снова."*
- Loading: *"Загружаем практики"* / *"Это может занять пару секунд"*
- Auth: *"С возвращением"* / *"Войдите, чтобы продолжить практику"*
- CTA: *"Попробовать бесплатно"*, *"Найти практику"*, *"Попробовать снова"*
- Secondary link: *"Все →"*, *"Забыли пароль?"*, *"Зарегистрироваться"*

**Casing.** Russian sentence case throughout. No Title Case. No ALL-CAPS. Labels like "Неделя" / "Месяц" are always sentence case.

**Pronouns.** "Вы" (formal plural), used implicitly. Never "ты". We speak *to* the user, not about them — "Посетили 3 практики", never "Пользователь посетил".

**Emoji.** Avoid. The Figma file contains zero UI emoji. Warmth comes from colour and the wellness icons, not from 🧘‍♀️.

**Numbers and metrics.** Spelled out where human-friendly ("Пора на check-in!"), numeric where quantitative ("3 практики", "45 мин", "12"). Unit abbreviations are Russian-style with a non-breaking space: `45 мин`, `07:00`, `3 мин`.

**Punctuation.** Russian typographic conventions: `—` (em dash with spaces), `«»` guillemets for quotes when needed, middle-dot `·` as a separator in meta rows ("Alex Mindful · 45 мин").

**Copy length.** Short. Card headings are 1 line. Secondary text rarely exceeds two lines. State-screens have a headline + one supporting sentence + one action.

**Vibe.** Every string should feel like it's being said in a calm voice in a sunlit room.

---

## VISUAL FOUNDATIONS

### Colors

Steel-blue on warm white, accented with teal and peach. Cold-ish but never clinical. Two warm accents (peach, pink) keep it human.

- **Steel primary `#4C6589`** — body text, the brand. Every heading and paragraph is some variant of this blue-grey.
- **Steel button `#627A9C`** — filled primary buttons (slightly lighter than primary text for glow contrast).
- **Teal 500 `#2F9EA8` (light) · Teal primary `#76DDE6` (dark)** — the accent. Active tabs, links, success, accent borders. In dark mode the saturation is kept but the brightness is pushed up; teal-700 `#26767D` is the AA-compliant text-on-light-surface variant.
- **Warm `#FBC088` with bg `rgba(251,192,136,0.4)`** — emotional moments. Used for "check-in" nudges with a 2px warm-primary border and a warm-deep `#A16124` heading. Never used for errors or neutral chrome.
- **Pink `#F795A2`** — soft secondary accent. Gradients and occasional badges.
- **Error `#AD3444`** — the only red. Used sparingly: badge count, error-state icon circle.
- **13-step neutral** from `#FFFFFF` to `#0B111C`. In light mode hierarchy is carried by **shadow over white**; in dark mode by **colour** (950 → 900 → 800 → 700).

WCAG: all `text/*` tokens hit AA normal (≥4.5:1) on `surface/default` in both modes.

### Typography

**One family, one weight: Marmelad Regular (400).** Everything. Display, body, labels, captions. The wordmark too. The variety comes from size and line-height, not weight or family. Marmelad's humanist curves give the system its "friendly-but-adult" feel — this is a deliberate anti-pattern to the Inter/Roboto defaults that make wellness apps look like dashboards.

Scale (10 steps):

| Token | Size | Line height | Use |
|---|---|---|---|
| Display/Large | 32 | 40 | Logo wordmark on-screen, big stats (e.g. "12") |
| Display/Small | 24 | 32 | Screen titles, hero |
| Heading/H1 | 20 | 28 | Section title |
| Heading/H2 | 18 | 24 | Card heading (most common heading) |
| Heading/H3 | 16 | 22 | Sub-heading |
| Body/Large | 16 | 24 | Body copy (desktop) |
| Body/Default | 14 | 20 | Body copy (mobile), secondary card text |
| Body/Small | 12 | 18 | Meta, captions in rows |
| Label | 15 | 20 | Input placeholder, button label (on larger buttons) |
| Caption | 9 | 14 | Tiny tags, legal |

### Spacing

8-step scale: **4 · 8 · 16 · 24 · 32 · 48 · 64 · 96 px**. Gaps between cards are 16. Card inner padding is 16–20. Screen padding is 16 on mobile, 24–32 on desktop sections, 96 on large desktop page gutters.

### Radii

Five steps: **md 8 · lg 15 · xl 24 · full 200**. Card radius is **15** (yes, fifteen — not 16). Buttons and tab-bar pills are `full` (200). Modal is `xl` (24). Inputs are `md` (8).

### Shadows

Six steps, low-profile. In **light mode** shadows carry elevation:

- `shadow/sm` — hairline lift on rows, card-on-card
- `shadow/md` — default card shadow (`0 4px 12px rgba(30,40,55,0.06)`)
- `shadow/lg` — elevated card, sticky header
- `shadow/xl` — dropdown, popover
- `shadow/2xl` — modal, sheet
- `shadow/glow-white` — the signature glow on primary buttons (`0 0 20.9px 7px rgba(255,255,255,1)`) and the Tab Bar. This pillowy halo is the brand's "breath" — it's how we show an element is *the* thing to tap.

In **dark mode** shadows are barely visible; we rely on lighter surface colours instead.

### Backgrounds, imagery, textures

- **Default surface is just white.** No gradients on most screens.
- **The mandala** (`assets/brand/mandala.png`, 400×400) is the one recurring illustration — used behind the logo on auth/splash, and as a faded backdrop on hero sections. It's a circular sacred-geometry pattern in pale blue-pink. Always low-opacity (20–35%).
- **Gradients** are reserved for emotional hero surfaces: `gradient/pink-peach` and `gradient/blue-teal`. Never on body content.
- **No full-bleed photography.** No b&w grain, no hand-drawn illustration. The warmth is in the palette, not in textures.

### Animation

- `motion/fast` 150ms · `motion/normal` 250ms · `motion/slow` 400ms.
- `ease-out` for enters, `ease-in-out` for loops, spring for taps (transform scale 0.98 → 1).
- No bouncy overshoot, no parallax. Breathing pulses (opacity 0.8 ↔ 1 over 4s) are on-brand for meditation surfaces.
- Hovers fade; they don't translate.

### Hover / press states

- **Hover** — `filter: brightness(1.06)` on filled buttons; `background: var(--surface-subtle)` on ghost/outline buttons; underline on links.
- **Focus** — 2px outline in `border-accent` with 2px offset. Never the browser default.
- **Pressed** — `transform: scale(0.98)` + brightness 0.96, 80ms.
- **Disabled** — 40% opacity, no pointer.

### Borders

Usually 1px `border-subtle` (`#E2F0FD` light / `#364150` dark). Strong borders (`#B0BCCD` / `#4F5969`) only on inputs and dividers between regions. Accent borders (2px `#FBC088`) on emotional cards like check-in nudges.

### Transparency & blur

- Ambient card background: occasional `rgba(251,192,136,0.4)` peach wash on emotional cards.
- Teal chip bg: `rgba(118,221,230,0.3)` — "paid" / "success" status pill.
- No `backdrop-filter: blur`. The system relies on flat semi-transparent fills, not glassmorphism.

### Layout rules

- Mobile screens are 390×844 (iPhone 14 logical).
- Outer screen padding: **16px** horizontal.
- Content gap: **20px** between sections, **12px** between rows inside a card.
- Tab bar pinned bottom, 44px tall, pill-shaped, always `shadow/glow-white`.
- Status-bar top padding: 48–56px (safe area).
- Desktop page max-width: 1200px, gutter 60px, section gap 96px.

### Cards

The canonical card: `background: surface/elevated`, `border-radius: 15`, `padding: 16–20`, `shadow/md`. No border in light mode (shadow does the work). In dark mode a 1px `border-subtle` on top of `surface/elevated` for separation.

### Fixed elements

Bottom tab bar, top app header. Both respect safe-area. The tab-bar has its `shadow/glow-white` so it never feels flat against the content behind it.

---

## ICONOGRAPHY

Two coexisting systems:

1. **Lucide** — the utility set. 50 icons, `Size=24`, stroke **1.5**, rounded caps and joins. Wired to `icon/*` semantic tokens, so they re-colour with theme. Covers nav (home, user, settings, bell), actions (plus, download, eye), feedback (info, shield), and controls (chevrons, arrows).

   Load from CDN: `https://unpkg.com/lucide-static@latest` or inline with the Lucide JS runtime. Recommended default usage: 24×24, stroke 1.5, `color: var(--icon-default)`.

2. **Brand Wellness Icons** — 12 custom wellness-themed pictograms, **single filled silhouette style** (outline variants were duplicates in the original Figma and have been removed): **meditation, spa, brain, flame, wind, bolt, heart, high-five, love, quill-pen, quill-pen-story, circle-microphone**. Shipped as PNG sprites in `assets/brand-icons/*.png` with clean names (no `-filled` / `-outline` suffix). Use for practice categories and emotional moments.

Usage priority: reach for Lucide for anything UI-utility; reach for brand wellness icons for practice categories (meditation types, breathing, journaling, etc.). Never mix the two stroke weights in one row — pick one family per surface.

- **Emoji** are **not** used in the UI.
- **Unicode glyphs** appear only in the wordmark (`Θ` / theta as the "O" in VELΘ).
- **No hand-drawn SVGs.** If you need an icon that's not here, substitute the nearest Lucide; flag it in the commit.

**Substitution flag:** the shipped brand-wellness PNGs were exported from Figma's embedded assets. If higher-fidelity source vectors are needed, ask the brand owner for the originals — the included PNGs are 512×512 raster.

---

## FONTS — substitution note

We load **Marmelad Regular** from Google Fonts (it's officially hosted there; no local TTF needed). If you need an offline copy, download from: https://fonts.google.com/specimen/Marmelad

No fallback substitutions were needed.

## Index — where to go next

- `preview/*.html` — one HTML card per design-system concept. These are what the Design System tab renders.
- `ui_kits/mobile/index.html` — the clickable iOS/Android UI kit demo. Start here to see the system in use.
- `ui_kits/mobile/*.jsx` — reusable JSX components (Button, TabBar, PracticeItem, BalanceCard, StatCard, CheckInCard, Input, Avatar, AppHeader, StateScreens).
- `colors_and_type.css` — drop this into any HTML file and you have the full token vocabulary.
- `SKILL.md` — Agent Skills manifest: how an AI agent should invoke this system.
