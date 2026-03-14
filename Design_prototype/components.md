# Components — VELΘ App

> Each component has defined states. Implement only documented states.
> All measurements are in px. All radii from tokens.md.

---

## Button

### States

| State | Description | Visual Change |
|-------|-------------|---------------|
| default | Resting | See variants below |
| hover | Mouse over | Slight opacity shift (web); tap highlight (mobile) |
| active | Pressed | Scale down slightly (0.97) |
| disabled | Not interactive | Opacity 40%, pointer-events none |
| loading | Async | Spinner in place of label |

### Variants

| Variant | Background | Text Color | Border | Shadow |
|---------|-----------|------------|--------|--------|
| primary | color-action-cta-default (#627a9c) | white | 1px white | shadow-glow |
| secondary | color-glass-blue-60 (rgba 171,191,218,0.60) | color-text-primary | 1px white | shadow-glow |
| ghost | color-glass-white-01 (rgba 255,255,255,0.01) | color-text-primary | 1px white | shadow-glow |
| danger | color-action-danger-bg (#f795a2) | white | 1px white | shadow-glow |

### Anatomy

| Property | Value |
|----------|-------|
| Height | 50px |
| Width | 336px (full content column) |
| Border-radius | radius-full (200px) |
| Font | font-button (20px, 400, tracking 0.4px) |
| Backdrop-filter | blur(2px) |

---

## Card

White panel used for practice details, progress stats, master info, etc.

### States

| State | Description | Visual Change |
|-------|-------------|---------------|
| default | Resting | White bg, radius-sm |
| hover | Mouse over | No visual change on mobile |

### Variants

| Variant | Height | Notes |
|---------|--------|-------|
| standard | 104px | Progress stats, practice listing |
| compact | 35–48px | Single-row info (Status, Стоимость, accordion rows) |
| tall | 142px | Practice/booking header card |
| content | variable | AI summary, descriptions |

### Anatomy

| Property | Value |
|----------|-------|
| Background | color-surface-card (#ffffff) |
| Border-radius | radius-sm (15px) |
| Width | spacing-content (336px) |
| Shadow | none (cards have no shadow — page bg provides depth) |

---

## Input

### States

| State | Description | Visual Change |
|-------|-------------|---------------|
| default | Resting | White bg, no visible border |
| focus | Active / selected | 2px border color-border-input-focus (#abbfda) |
| filled | Has value | Same as default |
| placeholder | Empty | Text at color-text-placeholder (rgba 76,101,137,0.50) |
| error | Invalid | Not defined in current design — use warning banner |
| disabled | Not editable | Opacity 40% |

### Anatomy

| Property | Value |
|----------|-------|
| Height | 40px |
| Width | 336px |
| Background | color-surface-input (#ffffff) |
| Border-radius | radius-xs (5px) |
| Border default | none |
| Border focus | 2px solid #abbfda |
| Font | font-body (18px, 400, tracking 0.36px) |
| Placeholder color | rgba(76,101,137,0.50) |

---

## Notification Banner

Contextual inline banners — warning (peach) or success/info (teal).

### Variants

| Variant | Background | Border | Title Color | Body Color |
|---------|-----------|--------|------------|-----------|
| warning | rgba(251,192,136,0.4) | 2px solid #fbc088 | #a16124 | #d4863c |
| success/info | rgba(118,221,230,0.4) | 2px solid #76dde6 | #26767d | #2f9ea8 |

### Anatomy

| Property | Value |
|----------|-------|
| Height | 66px |
| Width | 336px |
| Border-radius | radius-sm (15px) |
| Backdrop-filter | blur(2px) |
| Title font | font-heading (18px, tracking 0.36px) |
| Body font | font-caption (14px, tracking 0.28px) |
| Icon | 20–23px, left-aligned at 46–48px from screen left |

---

## Tag / Chip

Colored pill labels for categories (Медитация, Mindfulness, MBSR, etc.)

### Anatomy

| Property | Value |
|----------|-------|
| Height | 19px |
| Border-radius | radius-pill (100px) |
| Font | font-caption (14px, tracking 0.28px) |
| Text color | color-tag-text (#4c6589) |

### Variants

| Variant | Background | Example |
|---------|-----------|---------|
| pink | #fde2e2 | Mindfulness |
| blue | #e2f0fd | Медитация |
| sand | #fdf3e2 | MBSR |

---

## Status Badge

Pill-shaped status indicator (confirmed, paid).

### Anatomy

| Property | Value |
|----------|-------|
| Height | 23px |
| Border-radius | 71px |
| Background | color-status-confirmed-bg (rgba 118,221,230,0.30) |
| Text color | color-status-confirmed-text (#2f9ea8) |
| Font | font-caption (14px, tracking 0.28px) |
| Icon | checkmark, 11–14px, left-padded |

---

## Nav Bar (Bottom Navigation)

Fixed bottom navigation with 4 items.

### Items

| Item | Icon | Active State |
|------|------|-------------|
| Home (Главная) | home icon | Active |
| Calendar (Календарь) | calendar icon | Inactive |
| Bookings (Бронирования) | list/booking icon | Inactive |
| Profile (Профиль) | person icon | Inactive |

### Anatomy

| Property | Value |
|----------|-------|
| Item size | 63×63px |
| Active item bg | color-nav-active-bg (#627a9c), solid fill |
| Inactive item bg | color-nav-inactive-bg (rgba 98,122,156,0.15) |
| Border-radius | radius-full (252px — full circle) |
| Border | 1.26px white |
| Backdrop-filter | blur(2.52px) (inactive items only) |
| Total nav width | ~364px (4 items + gaps from x=37 to x=364) |

---

## Back Button

Pill-shaped navigation control, appears top-left on detail screens.

### Anatomy

| Property | Value |
|----------|-------|
| Size | 64×36px |
| Border-radius | radius-full |
| Background | glass / backdrop |
| Icon | left arrow |

---

## Toggle / Segmented Control

Used in AI-саммари (Неделя / Месяц).

### Anatomy

| Property | Value |
|----------|-------|
| Container height | 30px |
| Container bg | color-glass-blue-15 |
| Container radius | radius-full (200px) |
| Active segment bg | color-brand-primary (#627a9c) |
| Active segment radius | radius-full (200px) |
| Active text | white, 14px, tracking 0.28px |
| Inactive text | color-text-primary, 14px, tracking 0.28px |

---

## Master Card

Composite card showing master profile within practice/booking screens.

### Anatomy

| Property | Value |
|----------|-------|
| Container bg | color-surface-card (#ffffff) |
| Container radius | radius-sm (15px) |
| Height | 104px |
| Avatar size | 74×74px, masked to circle |
| Name font | font-heading (18px, tracking 0.36px) |
| Verified badge | 26×26px icon |
| Tags | Tag chips below name |
| Arrow button | 64×36px, rotated, bottom-right |

---

## Accordion Row

Expandable list item used in Practice Detail (О практике, Что подготовить, Стоимость).

### States

| State | Visual |
|-------|--------|
| collapsed | Chevron pointing down/right, white bg |
| expanded | Content revealed below (not shown in current designs) |

### Anatomy

| Property | Value |
|----------|-------|
| Height | 48px (collapsed), variable (expanded) |
| Background | color-surface-card (#ffffff) |
| Border-radius | radius-sm (15px) |
| Label font | font-heading (18px) |
| Value font | font-heading (18px, right-aligned) |
| Chevron | 15.5×8px, right-aligned |
