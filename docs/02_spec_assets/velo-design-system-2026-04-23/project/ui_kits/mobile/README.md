# VELO Mobile UI Kit

Clickable hi-fi mockup of the VELO mobile app (iOS/Android shared).

- `index.html` — the interactive prototype. Navigate between Auth → Dashboard → Loading → Empty → Error → back.
- `components/` — small reusable JSX components used across screens.
- Uses tokens from `../../colors_and_type.css` and brand icons from `../../assets/brand-icons/`.

Screens
- **Auth / Login** — entry screen, mandala backdrop, wordmark, email/password, ghost forgot-password link.
- **Dashboard (Light)** — greeting + stat card + warm check-in nudge + "Ближайшая практика" + practice list + tab bar with glow.
- **Dashboard (Dark)** — same layout, dark tokens; flip via the theme toggle in the top-right.
- **Loading / Empty / Error** — the three canonical state screens, triggered via a floating dev switcher.

Touch targets are all ≥ 44×44; card radius 15; CTA pill radius 200; type is Marmelad Regular only.
