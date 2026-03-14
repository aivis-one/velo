# VELΘ Design Migration Plan
# Переезд с тестового дизайна на рабочий

> **Источник правды по дизайну:** `Design_prototype/` в БЗ  
> **Правило:** В каждом новом чате загружать этот файл + соответствующий раздел `Design_prototype/`  
> **Статус обновлять здесь** по мере выполнения задач

---

## Контекст

| Параметр | Было (тестовый) | Станет (VELΘ) |
|----------|-----------------|---------------|
| Шрифты | Inter + Playfair Display | Marmelad Regular 400 (один шрифт, один вес) |
| Цвета | `#334D6E`, нейтральный серо-синий | `#4c6589` / `#627a9c` + teal + peach + pink |
| Стиль | Flat, стандартные тени | Soft glassmorphism (backdrop-blur + semi-transparent + 1px white border) |
| Фон | CSS gradient | Full-bleed фото + sacred geometry overlay (каждый экран) |
| Радиусы | 6/10/14/20/9999px | 15px карточки / 200px кнопки / 5px инпуты / 100px теги |
| Тени кнопок | `box-shadow` при hover | `0 0 20.9px 7px #fff` всегда (не интерактивная) |
| Экран | Responsive | 402px fixed, контент 336px, padding 33px |

### Что НЕ меняется
- Вся бизнес-логика, сторы, API-слой
- Роутер (структура маршрутов)
- TypeScript-типы
- Правила FP-01 — FP-09 из VELO-Frontend.md (только переменные меняются)
- Admin-раздел — он вне скоупа VELΘ-дизайна, получает минимальный рескин

---

## Фазы

```
DS-1  Design Tokens          variables.css → VELΘ токены
DS-2  Global Styles          шрифт, фон, reset
DS-3  Base Components        Button, Input, Card, Badge, Tag, Notification
DS-4  Layout Components      MobileLayout, VTabBar, VHeader, Shells
DS-5  Icons                  SVG-иконки из Design_prototype/assets/icons/
DS-6  Auth Views             Welcome, Login, Register, OAuth, Onboarding
DS-7  User Views             Dashboard, Calendar, PracticeDetail, Bookings, Checkin, Feedback, Diary, Profile
DS-8  Master Views           Dashboard, Practices, Analytics, Profile, Finance
DS-9  Admin Views            Минимальный рескин (только токены)
```

---

## DS-1: Design Tokens

**Файл:** `frontend/src/styles/variables.css`  
**Действие:** Полная замена содержимого

**Что меняется:**

| Группа | Было | Станет |
|--------|------|--------|
| Primary | `--velo-primary: #334D6E` | `--velo-primary: #627a9c` (brand-primary) |
| Text | `--velo-text-primary: #1E293B` | `--velo-text-primary: #4c6589` |
| Fonts | Inter / Playfair Display | Marmelad |
| Font sizes | 11/13/15/17/20/24/28px | 14/15/18/20/32/50px |
| Spacing | 4/8/12/16/20/24/32/40px | 8/14/16/24/33/48px (+ content: 336px) |
| Radii | 6/10/14/20/9999px | 5px input / 15px card / 100px tag / 200px pill |
| Shadows | стандартные drop shadows | `0 0 20.9px 7px #fff` для кнопок |

**Новые переменные (добавляются):**

```
--velo-glass-blue-15    rgba(98,122,156,0.15)
--velo-glass-blue-60    rgba(171,191,218,0.60)
--velo-glass-teal-30    rgba(118,221,230,0.30)
--velo-glass-teal-40    rgba(118,221,230,0.40)
--velo-glass-peach-40   rgba(251,192,136,0.40)
--velo-glass-white-01   rgba(255,255,255,0.01)
--velo-teal-400         #76dde6
--velo-teal-600         #2f9ea8
--velo-teal-700         #26767d
--velo-peach-300        #fbc088
--velo-peach-500        #d4863c
--velo-peach-700        #a16124
--velo-pink-300         #f795a2
--velo-pink-100         #fde2e2
--velo-blue-100         #e2f0fd
--velo-blue-200         #abbfda
--velo-sand-100         #fdf3e2
--velo-shadow-glow      0px 0px 20.9px 7px #ffffff
--velo-backdrop-blur    blur(2px)
--velo-screen-width     402px
--velo-content-width    336px
--velo-screen-padding   33px
```

**Удаляются:**
- `--font-heading: 'Playfair Display'`
- `--velo-bg-start / --velo-bg-end` (CSS gradient заменяется на фото-фон)
- Старые shadow-sm/md/lg/xl

**Сохраняются (переименовать значения, не ключи):**
- Все семантические `--velo-warning-*`, `--velo-error-*`, `--velo-success-*`, `--velo-info-*` — значения обновить под VELΘ палитру
- `--velo-mood-*`, `--velo-z-*`, `--transition-*` — обновить значения

**Статус:** ☐

---

## DS-2: Global Styles

**Файлы:**
- `frontend/src/styles/global.css`
- `frontend/index.html` (ссылка на Marmelad в Google Fonts)

**Действия:**

1. **index.html** — заменить Google Fonts ссылку:
   ```html
   <!-- Убрать Inter + Playfair Display, добавить: -->
   <link href="https://fonts.googleapis.com/css2?family=Marmelad&display=swap" rel="stylesheet">
   ```

2. **global.css** — обновить базовую типографику:
   ```css
   body {
     font-family: 'Marmelad', 'Noto Sans', sans-serif;
     font-weight: 400;
     letter-spacing: 0.02em;
   }
   ```

3. **Фоновый ассет** — скопировать из `Design_prototype/assets/` в `frontend/public/`:
   - Фоновая фотография → `public/bg/background.jpg` (или .webp)
   - Sacred geometry overlay → `public/bg/overlay.svg` (если отдельный файл)

4. **AppBackground компонент** (новый) или глобальный CSS-класс:
   ```
   position: fixed, z-index: 0
   фото 493px × 876px, centered
   overlay поверх
   все остальное — z-index: 1+
   ```

**Статус:** ☐

---

## DS-3: Base UI Components

Все файлы в `frontend/src/components/ui/`

### VButton.vue
**Изменения:**
- Variants: `primary | secondary | ghost | danger` (убрать `outline`)
- Height: 50px, Width: 336px (content column)
- Radius: 200px (pill)
- Font: Marmelad 20px, tracking 0.4px
- backdrop-filter: blur(2px)
- box-shadow: `var(--velo-shadow-glow)` — всегда, не только hover
- Backgrounds по дизайну:
  - primary: `#627a9c`, border: 1px white, text: white
  - secondary: `rgba(171,191,218,0.60)`, border: 1px white, text: `#4c6589`
  - ghost: `rgba(255,255,255,0.01)`, border: 1px white, text: `#4c6589`
  - danger: `#f795a2`, border: 1px white, text: white
- States: disabled (opacity 40%), loading (spinner), active (scale 0.97)

**Статус:** ☐

### VInput.vue
**Изменения:**
- Height: 40px, Width: 336px
- Radius: 5px
- Font: Marmelad 18px, tracking 0.36px
- Border default: none
- Border focus: 2px solid `#abbfda`
- Placeholder: `rgba(76,101,137,0.50)`
- Error state: не border — показывать VNotification banner (warning variant)

**Статус:** ☐

### VCard.vue
**Изменения:**
- Background: white
- Radius: 15px
- Width: 336px
- Shadow: none (глубину даёт фото-фон)
- Variants по высоте: standard (104px), compact (35–48px), tall (142px), content (variable)

**Статус:** ☐

### VBadge.vue → переименовать логику под VELΘ
**Изменения:**
- `success` → teal glass: bg `rgba(118,221,230,0.30)`, text `#2f9ea8`, radius 71px
- `warning` → peach: оставить под предупреждения
- `error` / `danger` → pink: `#f795a2`
- Высота: 23px, font: 14px tracking 0.28px

**Статус:** ☐

### VTag.vue (НОВЫЙ компонент)
**Описание:** Цветные pill-лейблы категорий (Медитация, Mindfulness, MBSR)
- Height: 19px, radius: 100px
- Font: 14px tracking 0.28px, color: `#4c6589`
- Variants: pink (`#fde2e2`), blue (`#e2f0fd`), sand (`#fdf3e2`)

**Статус:** ☐

### VNotification.vue (НОВЫЙ компонент)
**Описание:** Inline notification banner (warning / success)
- Height: 66px, Width: 336px, radius: 15px
- backdrop-filter: blur(2px)
- warning: bg `rgba(251,192,136,0.4)`, border 2px `#fbc088`, title `#a16124`, body `#d4863c`
- success: bg `rgba(118,221,230,0.4)`, border 2px `#76dde6`, title `#26767d`, body `#2f9ea8`
- Slot: icon + title + body

**Статус:** ☐

### VToggle.vue (НОВЫЙ — segmented control)
**Описание:** Переключатель Неделя/Месяц для AI-саммари
- Container: height 30px, bg glass-blue-15, radius 200px
- Active segment: `#627a9c`, radius 200px, text white 14px
- Inactive: text `#4c6589`, 14px

**Статус:** ☐

### VAvatar.vue
**Изменения:** Circle mask, 74×74px default — остальное без изменений

**Статус:** ☐

### VLoader.vue, VDivider.vue, VEmptyState.vue, VProgressBar.vue, VModal.vue
**Изменения:** Только цвета через обновлённые переменные. Структура не меняется.

**Статус:** ☐

---

## DS-4: Layout Components

### VTabBar.vue (нижняя навигация)
**Файл:** `frontend/src/components/layout/VTabBar.vue`  
**Изменения:**
- Item size: 63×63px, круг (radius 252px)
- Active bg: `#627a9c` solid
- Inactive bg: `rgba(98,122,156,0.15)` + backdrop-blur(2.52px)
- Border: 1.26px white на всех items
- Иконки: заменить на SVG из `Design_prototype/assets/icons/`
- Total nav width: ~364px (центрировать в 402px экране)

**Статус:** ☐

### VHeader.vue
**Файл:** `frontend/src/components/layout/VHeader.vue`  
**Изменения:**
- Back button: 64×36px, radius-full, glass bg
- Title font: Marmelad 18px tracking 0.36px
- Прозрачный фон (на фото-слое)

**Статус:** ☐

### MobileLayout.vue
**Файл:** `frontend/src/components/layout/MobileLayout.vue`  
**Изменения:**
- Убрать CSS gradient background
- Добавить слот или встроенный фото-фон (через AppBackground или фиксированный псевдоэлемент)
- max-width: 402px, centered
- Padding: 33px horizontal

**Статус:** ☐

### UserShell.vue / MasterShell.vue
**Файл:** `frontend/src/views/shells/`  
**Изменения:** Передать правильные иконки в VTabBar, обновить цветовую схему tabs

**Статус:** ☐

### AdminShell.vue
**Изменения:** Минимальные — только обновлённые CSS-переменные (см. DS-9)

**Статус:** ☐

---

## DS-5: Icons

**Источник:** `Design_prototype/assets/icons/`  
**Цель:** `frontend/src/components/ui/icons/` (Vue-компоненты) или `frontend/public/icons/`

**Доступные иконки:**
- `icon-calendar.svg` → VTabBar (Календарь)
- `icon-clock.svg` → практики (время)
- `icon-diary.svg` → VTabBar (Дневник / Дневник)
- `icon-feedback.svg` → feedback-экраны
- `icon-group.svg` → групповые практики
- `icon-brain.svg` → AI-саммари / аналитика

**Нужно добавить (отсутствуют в БЗ, делаем простые SVG):**
- home icon → VTabBar (Главная)
- person icon → VTabBar (Профиль)
- bookings/list icon → VTabBar (Бронирования)
- checkmark icon → VBadge status

**Подход:** Обернуть каждый SVG в Vue-компонент с пропсом `size` и `color: currentColor`

**Статус:** ☐

---

## DS-6: Auth Views

**Файлы:** `frontend/src/views/auth/`

### WelcomeView / LoginView
**Экраны по дизайну:** Welcome (134:53), Login (134:92), Register (134:152)

**Изменения:**
- Фон: фото-слой (уже через MobileLayout)
- Логотип: VeloLogo.vue — обновить под VELΘ (VELΘ wordmark + mark)
- Hero text: Marmelad 32px (font-heading-xl)
- Sub text: 18px
- Inputs: VInput (обновлённый)
- Кнопки: VButton primary / secondary (Google) / ghost (Apple)
- Разделитель «или»: простой divider с текстом
- Расположение: single column, centered, padding 33px

**Статус:** ☐

### OnboardingView (1-3)
**Экраны:** 134:334, 134:316, 134:349  
**Изменения:** Единый стиль с auth, обновить кнопки и типографику

**Статус:** ☐

---

## DS-7: User Views

### UserDashboardView.vue
**Экраны по дизайну:** Dashboard 1 (134:432), Dashboard 2 (134:553)

**Изменения:**
- Notification banners → VNotification (warning/success)
- Practice cards → VCard (tall variant, 142px)
- Tags на карточках → VTag
- Typography → Marmelad, все размеры по токенам
- Spacing → 33px padding, 336px content

**Статус:** ☐

### CalendarView.vue
**Экран:** 1 Calendar (175:738)  
**Изменения:** Цвета calendar → VELΘ палитра, карточки → VCard, типографика

**Статус:** ☐

### PracticeDetailView.vue
**Экран:** 2 Practice Detail (176:2074)

**Изменения:**
- Back button → VHeader glass
- Master card → новый VMasterCard компонент (74px avatar, теги, arrow button)
- Accordion (О практике / Что подготовить / Стоимость) → новый VAccordion компонент
- Tags → VTag
- CTA button → VButton primary
- Status badge → VBadge

**Новые компоненты:**
- `VMasterCard.vue` — 104px, белый, radius 15px, avatar + name + verified + tags + arrow
- `VAccordion.vue` — expandable row, анимация 250ms ease-in-out

**Статус:** ☐

### MyBookingsView.vue
**Экран:** 7 Мои бронирования (165:171)  
**Изменения:** Cards → VCard, badges → VBadge (teal для confirmed), typography

**Статус:** ☐

### BookingDetailView.vue / BookingSuccessView.vue
**Экраны:** 8 Booking Detail (165:268), Booking Success (183:2795)

**Изменения:**
- Danger button (Отменить) → VButton danger
- Status badge → VBadge teal
- Zoom section → стиль по дизайну

**Статус:** ☐

### CheckinView.vue / FeedbackView.vue
**Экраны:** Check-in (138:930), Check-in Success (138:1398)  
**Изменения:** Mood/rating buttons → обновить под glassmorphism стиль, typography

**Статус:** ☐

### DiaryView.vue
**Изменения:** Только цвета + типографика. Структура не меняется (tabs, list, detail, form)

**Статус:** ☐

### UserProfileView.vue
**Изменения:** Cards, typography, кнопки — под VELΘ

**Статус:** ☐

---

## DS-8: Master Views

### MasterDashboardView.vue
**Изменения:** VStatCard → обновить цвета, VCard → 15px radius, typography

**Статус:** ☐

### CreatePracticeView.vue / EditPracticeView.vue
**Изменения:** VInput, VSelect, VButton — обновлённые компоненты, форма 336px

**Статус:** ☐

### AttendanceView.vue
**Изменения:** Списки, аватары, статусы → VELΘ цвета

**Статус:** ☐

### AnalyticsView.vue
**Экран:** 6 AI-саммари (161:3)

**Изменения:**
- VToggle (Неделя/Месяц) → новый компонент VToggle
- Progress bars → обновить цвета
- Typography → Marmelad

**Статус:** ☐

### MasterProfileView.vue / MasterFinanceView.vue
**Изменения:** Typography, cards, кнопки

**Статус:** ☐

### MasterApplyView.vue / MasterPendingView.vue
**Изменения:** VInput, VButton, typography

**Статус:** ☐

---

## DS-9: Admin Views (минимальный рескин)

Admin — вне скоупа VELΘ-дизайна. Задача: убрать визуальный разрыв с основным приложением за счёт обновлённых токенов. Структура и компоненты не переделываются.

**Файлы:**
- `frontend/src/views/admin/AdminDashboardView.vue`
- `frontend/src/views/admin/AdminMastersView.vue`
- `frontend/src/views/admin/AdminMasterReviewView.vue`
- `frontend/src/views/admin/AdminReportsView.vue`
- `frontend/src/views/admin/AdminReportDetailView.vue`
- `frontend/src/views/admin/AdminConsistencyView.vue`

**Изменения:** После DS-1 (замена переменных) проверить каждый view на визуальные сломы. Починить только сломанное (hardcoded hex, сломанные контрасты). Новый дизайн не придумывать.

**Статус:** ☐

---

## Порядок выполнения

```
DS-1 → DS-2 → DS-5 → DS-3 → DS-4 → DS-6 → DS-7 → DS-8 → DS-9
```

**Почему такой порядок:**
- DS-1 (токены) разблокирует всё остальное
- DS-2 (шрифт + фон) меняет глобальное ощущение сразу
- DS-5 (иконки) нужны DS-3 и DS-4
- DS-3 (компоненты) нужны всем views
- DS-4 (layout) нужен всем views
- DS-6–DS-8 можно делать параллельно после DS-4
- DS-9 последним — просто проверка сломов

---

## Правила для каждого чата

1. Загрузить этот файл в начале сессии
2. Загрузить `Design_prototype/CLAUDE.md` + нужный раздел (`tokens.md`, `components.md`, `screens.md`)
3. Взять одну задачу из плана, выполнить полностью
4. Отметить статус: ☐ → ✅
5. Если задача большая — разбить на подзадачи внутри чата

---

## Глоссарий токенов (старый → новый)

| Старая переменная | Новая переменная | Значение |
|-------------------|-----------------|----------|
| `--velo-primary` | `--velo-primary` | `#627a9c` |
| `--velo-primary-dark` | `--velo-brand-text` | `#4c6589` |
| `--velo-text-primary` | `--velo-text-primary` | `#4c6589` |
| `--velo-text-secondary` | `--velo-text-secondary` | `rgba(76,101,137,0.70)` |
| `--velo-bg-card` | `--velo-surface-card` | `#ffffff` |
| `--velo-border` | `--velo-border-input-focus` | `#abbfda` |
| `--radius-sm` | `--radius-card` | `15px` |
| `--radius-full` | `--radius-pill` | `200px` |
| `--font-body` | `--font-family` | `'Marmelad', 'Noto Sans', sans-serif` |
| `--font-heading` | *(удалена)* | — |
| `--text-xs` | `--text-xs` | `14px` |
| `--text-sm` | `--text-sm` | `15px` |
| `--text-base` | `--text-md` | `18px` |
| `--text-lg` | `--text-lg` | `20px` |
| `--text-xl` | `--text-xl` | `32px` |
| `--text-2xl` | `--text-2xl` | `50px` |
| `--space-4` | `--space-md` | `16px` |
| `--space-6` | `--space-lg` | `24px` |
| `--shadow-md` | `--shadow-glow` | `0px 0px 20.9px 7px #ffffff` |

---

*Последнее обновление: 2026-03-15*
