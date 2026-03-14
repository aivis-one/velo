# Screens — VELΘ App

---

## Breakpoints

| Token | px | Use For |
|-------|-----|---------|
| screen-mobile | 402px | Primary / only breakpoint — mobile app |

> VELΘ is a mobile-only app. No tablet or desktop layouts present in the design.
> All content is 336px wide (402px − 33px left margin − 33px right margin).

---

## Grid System

| Property | Value |
|----------|-------|
| Screen width | 402px |
| Screen height | 874–876px |
| Screen corner radius | 15px |
| Horizontal margin | 33px (both sides) |
| Content width | 336px |
| Vertical rhythm | 8px base unit |

---

## Screen Inventory

| Screen | Node ID | Route | Layout | Width × Height |
|--------|---------|-------|--------|----------------|
| Welcome | 134:53 | / | Single column, centered | 402×874 |
| Login | 134:92 | /login | Single column, centered | 402×874 |
| Register | 134:152 | /register | Single column, centered | 402×874 |
| OAuth | 134:222 | /oauth | Single column | 402×874 |
| Onboarding 1 | 134:334 | /onboarding/1 | Single column | 402×874 |
| Onboarding 2 | 134:316 | /onboarding/2 | Single column | 402×874 |
| Onboarding 3 | 134:349 | /onboarding/3 | Single column | 402×874 |
| Dashboard 1 | 134:432 | /home | Feed + cards + bottom nav | 402×876 |
| Dashboard 2 | 134:553 | /home (alt) | Feed + cards + bottom nav | 402×876 |
| 1 Calendar | 175:738 | /calendar | Calendar view + bottom nav | 402×876 |
| 2 Practice Detail | 176:2074 | /practice/:id | Detail + accordion + CTA | 402×876 |
| 3 Master Profile | 183:2507 | /master/:id | Profile + practices | 402×876 |
| Check-in | 138:930 | /checkin/:id | Single action | 402×876 |
| Check-in Success | 138:1398 | /checkin/success | Confirmation | 402×876 |
| Практика (Live) | 138:1521 | /practice/live | Active session | 402×874 |
| Забронированная практика | 134:805 | /booking/:id/session | Session detail | 402×876 |
| 7 Мои бронирования | 165:171 | /bookings | List view + bottom nav | 402×876 |
| 8 Booking Detail | 165:268 | /booking/:id | Detail + cancel CTA | 402×876 |
| Booking Success | 183:2795 | /booking/success | Confirmation | 402×876 |
| 6 AI-саммари | 161:3 | /ai-summary | Summary + toggle | 402×876 |
| 5 Забронированная практика | 134:692 | /booking/:id/detail | Practice session detail | 402×876 |

---

## Common Screen Anatomy

### Screens with Bottom Navigation (main app screens)

```
┌──────────────────────────────────────────┐ y=0
│  Background photo (493px wide, centered) │
│  + sacred geometry overlay               │
├──────────────────────────────────────────┤ y≈34
│  [← Back]  Screen Title                 │ Top nav row (detail screens)
├──────────────────────────────────────────┤ y≈90
│  ← 33px margin →  Content  ← 33px →    │
│  Card / Section 1                        │
│  ...                                     │
│  Card / Section N                        │
├──────────────────────────────────────────┤ y≈770
│  Bottom Navigation (4 icons)             │
└──────────────────────────────────────────┘ y=876
```

### Auth screens (Welcome, Login, Register)

```
┌──────────────────────────────────────────┐ y=0
│  Background photo + ornamental overlay   │
├──────────────────────────────────────────┤ y≈51
│  Logo (VELΘ mark + wordmark)             │
├──────────────────────────────────────────┤ y≈200
│  Headline (32px)                         │
│  Subheadline (18px)                      │
├──────────────────────────────────────────┤ y≈300
│  Input fields (Login only)               │
├──────────────────────────────────────────┤ y≈440
│  Primary button (Войти)                  │
│  Divider (или)                           │
│  Secondary buttons (Google, Apple)       │
└──────────────────────────────────────────┘ y=874
```

---

## Page Background

All screens share the same background:
- A decorative photo image (`image 40`) sized 493×876px, centered on screen
- The image creates the characteristic light blue-grey gradient tint
- Sacred geometry / mandala pattern overlaid at low opacity (white lines)
- This is NOT a CSS background — it is a full-bleed photo layer underneath all UI
