# VELΘ App Design KB — README

## Project

| Field | Value |
|-------|-------|
| Project | VELΘ App (meditation / wellness mobile app) |
| Platform | Mobile only (iOS/Android) |
| Figma file | VEL Θ App--Copy- (tYLv1wfOERQxsyZKPVkTQA) |
| Generated | 2026-03-11 |

---

## Built

| File | Layer | Status |
|------|-------|--------|
| CLAUDE.md | L0 | ✓ generated |
| tokens.md | L0 | ✓ generated — colors, typography, spacing, shadows, radii |
| components.md | L1 | ✓ generated — Button, Card, Input, Notification, Tag, Badge, Nav, Accordion, Master Card |
| screens.md | L1 | ✓ generated — 21 screens, mobile-only breakpoint |
| behavior.md | L1 | ✓ generated — durations, easing, interaction rules |

---

## Skipped

| File | Reason |
|------|--------|
| accessibility.md | Accessibility zone not collected (not defined in Figma) |
| patterns.md | Patterns zone not collected |
| assets/manifest.md | Assets zone not collected (icons are SVG groups in Figma, not exported assets) |

---

## Source Screens Analyzed

| Screen | Node ID | Used For |
|--------|---------|----------|
| Dashboard 1 | 134:432 | Colors, spacing, cards, nav, notification banners, typography |
| Login | 134:92 | Input states, button variants, auth layout |
| 2 Practice Detail | 176:2074 | Accordion, master card, tags, CTA, back button |
| Welcome | 134:53 | Logo treatment, hero text, glass ghost button |
| Booking Detail | 165:268 | Danger button, status badge, ZOOM section |

---

## Load Instruction

To use this KB in Claude Code:
1. Place the `design-kb-velo/` folder in your project root
2. At session start, include: @design-kb-velo/CLAUDE.md
3. Claude will load full KB context for this project

---

## Key Design Fingerprints

- **Font**: Marmelad, Regular 400 only — no other weights
- **Colors**: Everything derives from #4c6589 (blue-slate) + teal #76dde6 + peach #fbc088 + pink #f795a2
- **Glass**: Every interactive surface uses backdrop-blur(2px) + semi-transparent bg + 1px white border
- **Radius**: 15px cards / 200px pills / 5px inputs / 100px tags
- **Shadow**: All buttons share `0 0 20.9px 7px white` glow — always on, not hover-only
- **Background**: Full-bleed decorative photo layer (493px wide) with sacred geometry overlay on every screen
