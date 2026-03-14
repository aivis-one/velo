# Behavior + Animation — VELΘ App

> Use these values for all motion in the UI. Do not use arbitrary durations.
> Animation is not explicitly defined in the Figma file — values below are
> inferred from the soft/calm aesthetic of the design and standard mobile patterns.

---

## Durations

| Token | Value | Use For |
|-------|-------|---------|
| duration-instant | 0ms | Toggles, show/hide without motion |
| duration-fast | 150ms | Micro-interactions (button press, focus ring) |
| duration-normal | 250ms | Component transitions (accordion expand, tab switch) |
| duration-slow | 400ms | Page transitions, modals |
| duration-deliberate | 600ms | Onboarding steps, success animations |

---

## Easing

| Token | Value | Use For |
|-------|-------|---------|
| easing-linear | linear | Progress bars |
| easing-ease-out | cubic-bezier(0, 0, 0.2, 1) | Elements entering screen |
| easing-ease-in | cubic-bezier(0.4, 0, 1, 1) | Elements leaving screen |
| easing-ease-in-out | cubic-bezier(0.4, 0, 0.2, 1) | Repositioning, accordion |
| easing-spring | cubic-bezier(0.34, 1.56, 0.64, 1) | Success states, check-in confirmation |

---

## Interaction Rules

| Interaction | Duration | Easing | Notes |
|-------------|----------|--------|-------|
| Button press | duration-fast | easing-ease-out | Scale 0.97 |
| Input focus | duration-fast | easing-ease-out | Border color transition |
| Accordion open | duration-normal | easing-ease-in-out | Height expand |
| Accordion close | duration-fast | easing-ease-in | Height collapse |
| Page push (forward) | duration-slow | easing-ease-out | Slide from right |
| Page pop (back) | duration-normal | easing-ease-in | Slide to right |
| Bottom sheet open | duration-normal | easing-ease-out | Slide from bottom |
| Success screen | duration-deliberate | easing-spring | Checkmark / celebration |
| Segmented control | duration-fast | easing-ease-in-out | Active indicator slides |
| Notification banner | duration-normal | easing-ease-out | Fade + slide in |

---

## Glass Effect

All glass elements use the same frosted-glass treatment:

| Property | Value |
|----------|-------|
| backdrop-filter | blur(2px) |
| background | semi-transparent (see tokens.md color-glass-*) |
| border | 1px solid rgba(255,255,255,1.0) |
| transition | none (static glass effect, no animation on blur) |

Nav bar inactive items use slightly stronger blur (2.52px) and 1.26px border.

---

## Button Glow

All buttons (primary, secondary, ghost, danger) share this shadow:

```
box-shadow: 0px 0px 20.9px 7px #ffffff
```

The glow is always white and always present — it is part of the resting state,
not an interactive state change.
