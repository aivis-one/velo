---
name: velo-design
description: Use this skill to generate well-branded interfaces and assets for VELO, a Russian-language wellness/meditation mobile app, either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, mandala assets, and UI kit components for prototyping.
user-invocable: true
---

Read the README.md file within this skill, and explore the other available files.

Key files:
- `README.md` — full brand voice, visual foundations, iconography, and caveats
- `colors_and_type.css` — drop-in CSS with the brand palette, Marmelad webfont, type scale, and reusable atoms (`.velo-pill-button`, `.velo-input`, `.velo-card`, `.velo-page-bg`)
- `fonts/Marmelad-Regular.ttf` — the only typeface; covers Cyrillic + Latin
- `assets/brand/` — mandala motif SVGs (already colored brand-ink at 100% — wrap in 12% opacity at use site)
- `ui_kits/velo-app/` — full interactive iPhone-frame UI kit; copy `App.jsx`, `Welcome.jsx`, `Login.jsx`, `Home.jsx`, `Calendar.jsx`, `Profile.jsx`, `components.jsx` for ready-made screens
- `slides/` — none provided

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view. Always link `colors_and_type.css` and use `font-family: "Marmelad"` so Cyrillic renders correctly.

If working on production code, you can copy assets and read the rules in README.md to become an expert in designing with this brand.

If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts _or_ production code, depending on the need.

**Critical brand rules:**
- One typeface (Marmelad Regular), one dominant color (`#4C6589`), one accent (mint `#76DDE6` for "paid/verified" only)
- Russian copy in second-person informal; no emoji; sentence case
- 15px radius for cards, full pill (200px) for buttons/inputs
- White cards on sky-tint background, no shadows, no gradients
- The mandala motif at 12% opacity is the signature atmosphere — use it on hero/auth/onboarding screens, never as a focal element
