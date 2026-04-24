---
name: velo-design
description: Use this skill to generate well-branded interfaces and assets for VELO (VELΘ), a Russian-language wellness/mindfulness platform (meditation, breathing, journaling), for production or for throwaway prototypes/mocks. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the README.md file within this skill, and explore the other available files.

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view. If working on production code, you can copy assets and read the rules here to become an expert in designing with this brand.

If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts _or_ production code, depending on the need.

Key entry points:
- `colors_and_type.css` — all tokens, Light + Dark via `[data-theme="dark"]`
- `assets/brand/mandala.png` — the signature backdrop motif
- `assets/brand-icons/*.png` — 19 wellness PNG icons (filled + outline)
- `ui_kits/mobile/` — React/JSX UI kit for the mobile app
- Russian copy, English token names. Marmelad Regular for all text. Pill-shaped CTAs with `shadow-glow-white`. Card radius 15.
