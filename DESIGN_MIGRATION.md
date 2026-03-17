# VELΘ Design Migration Plan v2
# Переезд с тестового дизайна на рабочий

> **Источник правды по дизайну:** `Design_prototype/` в репо
> **Главное правило:** Меняем только VALUES переменных, никогда не NAMES
> **Ветка:** `design/veltheta` → merge в `main` когда всё готово
> **Деплой тестов:** VPS переключить на `design/veltheta`, `velo update`

---

## Ключевые уроки v1 (что пошло не так)

1. DS-1 переименовал переменные (`--radius-sm` → `--radius-card`) — все views сломались разом
2. Новые компоненты (VButton, VInput) создавались в чате и некуда было их коммитить
3. Все задания Claude Code должны идти напрямую в ветку, не через чат

---

## Принципы v2

1. **Только значения** — `--velo-primary: #627a9c` вместо `--velo-primary: #334D6E`. Имя не меняется.
2. **Новые переменные добавляются в конец** `variables.css` — не заменяют старые.
3. **Все задания — Claude Code в ветку** — чат только для обсуждения и формулировки заданий.
4. **Каждая DS-фаза = один PR** в `design/veltheta` → проверка на VPS → следующая фаза.

---

## Фазы

```
DS-1  variables.css    Только значения: цвета, шрифт, spacing, radii + новые glass-переменные в конец
DS-2  global.css       Шрифт Marmelad, фото-фон (уже сделано — проверить z-index)
DS-3  Base components  VButton, VInput, VCard, VBadge + новые VTag, VNotification, VToggle, VAccordion
DS-4  Layout           MobileLayout, VTabBar, VHeader, Shells
DS-5  Icons            SVG → Vue-компоненты (уже сделано — проверить)
DS-6  Auth views       Welcome, Login, Register, Onboarding
DS-7  User views       Dashboard, Calendar, PracticeDetail, Bookings, Checkin, Feedback, Diary, Profile
DS-8  Master views     Dashboard, Practices, Analytics, Profile, Finance
DS-9  Admin views      Только проверка сломов после DS-1, минимальные правки
```

---

## DS-1: variables.css

**Файл:** `frontend/src/styles/variables.css`
**Правило:** Менять только значения справа от `:`. Имена слева — не трогать.

### Что менять (существующие переменные)

| Переменная | Было | Станет |
|------------|------|--------|
| `--velo-primary` | `#334D6E` | `#627a9c` |
| `--velo-primary-light` | `#4A6B8A` | `#627a9c` |
| `--velo-primary-dark` | `#1E3A5F` | `#4c6589` |
| `--velo-bg-start` | `#F8FAFC` | `#ffffff` |
| `--velo-bg-end` | `#EEF2F6` | `#ffffff` |
| `--velo-bg-subtle` | `#F1F5F9` | `rgba(98,122,156,0.06)` |
| `--velo-bg-card` | `#FFFFFF` | `#ffffff` |
| `--velo-text-primary` | `#1E293B` | `#4c6589` |
| `--velo-text-secondary` | `#475569` | `rgba(76,101,137,0.70)` |
| `--velo-text-muted` | `#94A3B8` | `rgba(76,101,137,0.50)` |
| `--velo-border` | `#E2E8F0` | `#abbfda` |
| `--velo-border-light` | `#F1F5F9` | `rgba(171,191,218,0.30)` |
| `--velo-success` | `#22C55E` | `#76dde6` |
| `--velo-warning` | `#F59E0B` | `#fbc088` |
| `--velo-error` | `#EF4444` | `#f795a2` |
| `--velo-info` | `#3B82F6` | `#76dde6` |
| `--velo-warning-bg` | `#FEF3C7` | `rgba(251,192,136,0.40)` |
| `--velo-warning-border` | `#F59E0B` | `#fbc088` |
| `--velo-warning-text` | `#92400E` | `#a16124` |
| `--velo-error-bg` | `#FEE2E2` | `rgba(253,226,226,0.40)` |
| `--velo-error-border` | `#FCA5A5` | `#f795a2` |
| `--velo-error-text` | `#DC2626` | `#a16124` |
| `--velo-success-bg` | `#DCFCE7` | `rgba(118,221,230,0.40)` |
| `--velo-success-text` | `#166534` | `#26767d` |
| `--velo-info-bg` | `#DBEAFE` | `rgba(118,221,230,0.40)` |
| `--velo-info-text` | `#1E40AF` | `#2f9ea8` |
| `--velo-mood-low` | `#EF4444` | `#f795a2` |
| `--velo-mood-mid` | `#F59E0B` | `#fbc088` |
| `--velo-mood-high` | `#22C55E` | `#76dde6` |
| `--font-body` | `'Inter', ...` | `'Marmelad', 'Noto Sans', sans-serif` |
| `--font-heading` | `'Playfair Display', ...` | `'Marmelad', 'Noto Sans', sans-serif` |
| `--text-xs` | `11px` | `14px` |
| `--text-sm` | `13px` | `15px` |
| `--text-base` | `15px` | `18px` |
| `--text-lg` | `17px` | `20px` |
| `--text-xl` | `20px` | `32px` |
| `--text-2xl` | `24px` | `50px` |
| `--text-3xl` | `28px` | `32px` |
| `--space-1` | `4px` | `4px` |
| `--space-2` | `8px` | `8px` |
| `--space-3` | `12px` | `14px` |
| `--space-4` | `16px` | `16px` |
| `--space-5` | `20px` | `24px` |
| `--space-6` | `24px` | `24px` |
| `--space-8` | `32px` | `33px` |
| `--space-10` | `40px` | `48px` |
| `--radius-sm` | `6px` | `15px` |
| `--radius-md` | `10px` | `15px` |
| `--radius-lg` | `14px` | `15px` |
| `--radius-xl` | `20px` | `100px` |
| `--radius-full` | `9999px` | `9999px` (не трогать — используется везде) |
| `--shadow-sm` | `0 1px 2px ...` | `none` |
| `--shadow-md` | `0 4px 12px ...` | `none` |
| `--shadow-lg` | `0 8px 24px ...` | `none` |
| `--shadow-xl` | `0 12px 40px ...` | `none` |

### Что добавить в конец (новые переменные — только добавление)

```css
/* === VELΘ: Glass colors === */
--velo-glass-blue-15: rgba(98, 122, 156, 0.15);
--velo-glass-blue-60: rgba(171, 191, 218, 0.60);
--velo-glass-teal-30: rgba(118, 221, 230, 0.30);
--velo-glass-teal-40: rgba(118, 221, 230, 0.40);
--velo-glass-peach-40: rgba(251, 192, 136, 0.40);
--velo-glass-white-01: rgba(255, 255, 255, 0.01);

/* === VELΘ: Primitive palette (новые цвета) === */
--velo-teal-400: #76dde6;
--velo-teal-600: #2f9ea8;
--velo-teal-700: #26767d;
--velo-peach-300: #fbc088;
--velo-peach-500: #d4863c;
--velo-peach-700: #a16124;
--velo-pink-300: #f795a2;
--velo-pink-100: #fde2e2;
--velo-blue-100: #e2f0fd;
--velo-blue-200: #abbfda;
--velo-sand-100: #fdf3e2;

/* === VELΘ: Glow shadow === */
--velo-shadow-glow: 0px 0px 20.9px 7px #ffffff;

/* === VELΘ: Layout === */
--velo-content-width: 336px;
--velo-screen-width: 402px;
--velo-screen-padding: 33px;

/* === VELΘ: Navigation === */
--velo-nav-active-bg: #627a9c;
--velo-nav-inactive-bg: rgba(98, 122, 156, 0.15);

/* === VELΘ: Border === */
--velo-border-input-focus: #abbfda;

/* === VELΘ: Z-index === */
--z-background: -1;
--z-content: 1;
```

---

## DS-2: global.css + index.html

Скорее всего уже сделано в старой ветке. Перенести только эти изменения:

**index.html:** заменить Google Fonts на Marmelad:
```html
<link href="https://fonts.googleapis.com/css2?family=Marmelad&display=swap" rel="stylesheet">
```

**global.css:** фото-фон:
```css
#app::before {
  content: '';
  position: fixed;
  inset: 0;
  z-index: var(--z-background); /* = -1 */
  background: url('/bg/background.jpg') center / cover no-repeat;
  pointer-events: none;
}
```

Файл `background.jpg` скопировать в `frontend/public/bg/`.

---

## DS-3: Base components

**Принцип:** Менять стили компонентов используя существующие имена переменных.
Новые переменные (`--velo-glass-blue-60`, `--velo-shadow-glow` и т.д.) — использовать,
они уже добавлены в DS-1.

### VButton
- `border-radius`: `var(--radius-full)` (9999px — pill)
- `border`: `1px solid #ffffff`
- `backdrop-filter`: `blur(2px)`
- `box-shadow`: `var(--velo-shadow-glow)` — всегда
- `font-family`: `var(--font-body)`
- `font-weight`: `400`
- Высота md: `50px`, sm: `36px`
- Убрать `variant="outline"`, `size="lg"`
- primary: `var(--velo-primary)` / white
- secondary: `var(--velo-glass-blue-60)` / `var(--velo-text-primary)`
- ghost: `var(--velo-glass-white-01)` / `var(--velo-text-primary)`
- danger: `var(--velo-pink-300)` / white

### VInput
- `height`: `40px`
- `border`: none в покое
- `border-radius`: `5px` (использовать `var(--radius-sm)` = 5px после DS-1... нет, `--radius-sm` = 15px после DS-1)
- Использовать хардкод `5px` или добавить `--velo-radius-input: 5px` в DS-1
- focus: `2px solid var(--velo-border-input-focus)`
- placeholder: `var(--velo-text-muted)`
- Убрать error state — использовать VNotification

### VCard
- `border-radius`: `var(--radius-md)` (15px)
- `box-shadow`: none

### VBadge
- success: `var(--velo-glass-teal-30)` / `var(--velo-teal-600)`
- warning: `var(--velo-glass-peach-40)` / `var(--velo-peach-700)`
- error: `var(--velo-pink-100)` / `var(--velo-pink-300)`

### Новые компоненты
- `VTag.vue` — pill категорий (blue/pink/sand)
- `VNotification.vue` — inline banner (warning/success)
- `VToggle.vue` — segmented control
- `VAccordion.vue` — expandable row

---

## DS-4 — DS-9

Без изменений по содержанию — только учитывать что имена переменных не менялись.

---

## Порядок работы

1. Пересоздать ветку `design/veltheta` от актуального `main`
2. Claude Code делает DS-1
3. Мерж в `design/veltheta`, VPS деплоит, проверяем
4. Claude Code делает DS-2
5. И так далее по фазам

---

*v2 — 2026-03-17*
