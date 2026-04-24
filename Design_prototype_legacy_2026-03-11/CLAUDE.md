# VELΘ App Design KB

## Project Context

| Field | Value |
|-------|-------|
| Project | VELΘ App |
| Platform | Mobile (iOS/Android) |
| Style | Soft glassmorphism · light blue-grey tints · blurred translucent panels · Marmelad typeface · meditation/wellness |
| Generated | 2026-03-11 |

## How to Use This KB

Load at session start with: @design-kb-velo/CLAUDE.md

Files in this KB:
- tokens.md: All design tokens (colors, typography, spacing, shadows, radii)
- components.md: Component library with states and variants
- behavior.md: Animation and interaction rules
- screens.md: Screen inventory with breakpoints

## Key Rules for AI Coder

1. Always use semantic tokens, not primitive values
   - Use: color-brand-primary
   - Not: #627a9c

2. Single font, single weight — no exceptions
   - Font: Marmelad, Regular only (no bold, no semibold in design)
   - Tracking is always ~0.02em of font-size

3. Spacing must follow the scale
   - Screen horizontal padding: 33px (fixed)
   - Content width: 336px (fixed — 402px screen − 33px × 2)
   - Use scale values from tokens.md; do not use arbitrary px values

4. Radii are strict by element type
   - Cards/panels: 15px
   - Pill buttons: 200px
   - Input fields: 5px
   - Tags/chips: 100px

5. Glass effect anatomy
   - All glass elements use: backdrop-blur(2px) + semi-transparent bg + 1px white border
   - Never use opaque backgrounds for nav items or secondary buttons

6. Ask before deviating from this KB
   - If a UI pattern is not covered, ask before inventing
