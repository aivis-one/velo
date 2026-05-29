# VELO — Фронтовый Кодекс

**Версия:** 1.6
**Дата:** 29 мая 2026
**Статус:** Active 

> **v1.6 (раздел Профиль + аудит-фиксы, 29 мая 2026):** реализован раздел
> «Профиль» (Figma `F7PD5isLfLdyc0q1Bd5n5c`, node `4715-3463`). Новые вью
> `LanguageTimezoneView` (язык-заглушка + переиспользуемый picker таймзоны),
> `EditProfileView` (имя/email-заглушка/телефон/о-себе + модалка удаления),
> `NotificationsView` (4 свича); переработан `UserProfileView` (две стат-карточки
> из `GET /bookings/me/stats`, пункты-переходы). Новый UI-примитив `VSwitch`
> (on/off). Новые роуты `user-language-timezone`, `user-edit-profile`,
> `user-notifications`. Экран G (Поддержка, node 76) — отложен по решению
> заказчика (пункт «Поддержка» = toast-заглушка). Аудит-фиксы: W-2 (честный текст
> модала удаления), S-1 (`bio.trimEnd()`), S-2 (язык-строка неинтерактивна при
> одном языке). Детали — §3.7, §10. i18n в проекте по-прежнему НЕТ (язык — задел).

> **v1.5 (Calendar flow 4-7 + master public, 24 мая 2026):** завершён флоу
> «Календарь» (Figma node `541:1553`, кадры 4-7 + публичный профиль мастера).
> Новые вью `MasterPublicView` (профиль мастера для юзера) и `BookingConfirmedView`
> (кадр 5, экран после брони); аватары мастеров переведены на `VAvatar` (фото или
> инициалы) — закрыт TD-FE-AVATAR; иконка hero практики выбирается по `direction`
> (`DIRECTION_ICON` Partial+fallback); emoji-рейтинг и success-сердце на feedback
> заменены векторными иконками из Figma (`IconRating*`, `IconHeart`) c цветом через
> новые токены `--velo-rating-*`. Урок: `vue-tsc` проверяет передачу пропов в
> дочерние компоненты в ШАБЛОНЕ — см. §FP-10. Все «вопросы мастеру» по приложению —
> заглушки (TD-ASK-MASTER). Детали — §3.5, §10. Аудит итерации: 0 critical /
> 0 warning, 3 suggestion (S-1/S-3 ✅, S-2 осознанно отложен).

> **v1.4 (Calendar iteration, 22 мая 2026):** реализован экран «Календарь» (кадры 1-3
> Figma node `541:1553`): отдельный стор `stores/calendar.ts` (загрузка недели одним
> запросом), компоненты `WeekStrip` / `CalendarPracticeCard` / `CalendarFilterModal`,
> переработан `CalendarView`, добавлен индикатор сложности на `PracticeDetailView`.
> Контракт `PracticeFilters` стал мульти-фасетным (массивы), `buildQuery` поддерживает
> повторяемые ключи. Детали — §3.5, §4, §5.1. Аудит: C-1/W-2 ✅, открыт техдолг по
> «Виду практики» (см. §10).

---

## 1. Архитектура 

### 1.1. Одно SPA — три роли

Единое приложение с ролевым роутингом. Роль определяется из `GET /api/v1/users/me`
после авторизации. Каждая роль имеет свой Shell (layout-обёртку) и Tab Bar.

| Роль | Shell | Tab Bar |
|------|-------|---------|
| `user` | `UserShell` | IconHome Дашборд / IconCalendar Календарь / IconDiary Дневник / IconProfile Я |
| `master` | `MasterShell` | IconHome Дашборд / IconPractices Практики / IconBrain Аналитика / IconProfile Я |
| `admin` | `AdminShell` | IconDashboard Дашборд / IconGroup Мастера / IconModeration Модерация / IconProfile Я |

Мастер и Админ имеют доступ к user-интерфейсу через переключение режима (см. TD-FE-ROLE-SWITCH).

### 1.2. Платформенная абстракция

Приложение работает в двух средах. Различия инкапсулированы в `src/platform/`:

| Файл | Назначение |
|------|------------|
| `platform/types.ts` | Интерфейс `Platform` (общий контракт) |
| `platform/telegram.ts` | Реализация для Telegram WebApp SDK |
| `platform/standalone.ts` | Заглушки для браузера (Phase F10) |
| `platform/index.ts` | Автодетект: `window.Telegram?.WebApp` → telegram, иначе standalone |

Интерфейс `Platform`:

```typescript
interface Platform {
  name: 'telegram' | 'standalone'
  init(): Promise<void>
  getInitData(): string | null
  getTheme(): 'light' | 'dark'
  hapticFeedback(type: string): void
  showBackButton(cb: () => void): void
  hideBackButton(): void
  openLink(url: string): void   // external link: Telegram WebApp.openLink / window.open(noopener)
  close(): void
}
```

MVP работает только в Telegram. Standalone — Phase F10.

`openLink` добавлен для экрана Practice-Live (кнопка "Войти" в Zoom). В Telegram —
`WebApp.openLink(url)`, в standalone — `window.open(url, '_blank', 'noopener')`.

### 1.3. Структура проекта

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts          -- Base fetch обёртка, 401 handler
│   │   ├── generated.ts       -- Auto-generated from backend OpenAPI (DO NOT EDIT)
│   │   ├── types.ts           -- Re-export from generated.ts + frontend-only types
│   │   ├── utils.ts           -- buildQuery() и прочие shared helpers
│   │   ├── auth.ts            -- POST /auth/telegram, logout
│   │   ├── users.ts           -- GET/PATCH /users/me
│   │   ├── practices.ts       -- CRUD практик, finalize, attendance
│   │   ├── bookings.ts        -- Бронирования, purchase, waitlist
│   │   ├── payments.ts        -- Topup
│   │   ├── masters.ts         -- Apply, profile, payout, withdrawals
│   │   ├── diary.ts           -- Check-ins, feedbacks, entries, insights, listDiaryFeed (cursor)
│   │   └── admin.ts           -- Stats, verify, reports, consistency
│   │
│   ├── components/
│   │   ├── ui/                -- Примитивы (V-префикс)
│   │   │   ├── icons/         -- SVG-иконки из Design_prototype (Vue-компоненты)
│   │   │   └── index.ts       -- Barrel export всех UI-компонентов
│   │   ├── layout/            -- Shell-компоненты, VHeader, VTabBar
│   │   └── shared/            -- Доменные: PracticeCard, BookingCard...
│   │
│   ├── composables/
│   │   ├── useAuth.ts         -- Login/logout flow + waitUntilReady()
│   │   ├── usePagination.ts   -- Пагинация + infinite scroll (offset)
│   │   ├── useCursorPagination.ts -- Курсорная пагинация (Diary feed: {items,next_cursor})
│   │   ├── useToast.ts        -- Всплывающие уведомления
│   │   └── useForm.ts         -- Валидация форм
│   │
│   ├── platform/              -- Платформенная абстракция (см. 1.2)
│   │
│   ├── router/
│   │   ├── index.ts           -- Маршруты + beforeEach guard
│   │   ├── guards.ts          -- roleRedirect, roleGuard, masterStatusGuard
│   │   └── tabs.ts            -- USER_TABS, MASTER_TABS, ADMIN_TABS
│   │
│   ├── stores/
│   │   ├── auth.ts            -- user, token, role, isAuthenticated
│   │   ├── practices.ts       -- list, filters, selected
│   │   ├── calendar.ts        -- Calendar screen: week load, selected day, facet filters (Calendar iteration)
│   │   ├── bookings.ts        -- my bookings
│   │   ├── balance.ts         -- balance_cents, operations
│   │   ├── master.ts          -- master profile, practices, finance
│   │   └── diary.ts           -- unified cursor feed (feedItems/filters), submit checkin/feedback, entry CRUD, insights cache
│   │
│   ├── styles/
│   │   ├── variables.css      -- Дизайн-токены (единственный источник цветов)
│   │   └── global.css         -- Reset, typography, Google Fonts
│   │
│   ├── utils/
│   │   ├── format.ts          -- formatMoney, formatDate, formatDateShort
│   │   ├── currency.ts        -- eurStringToCents, centsToEurString
│   │   ├── displayHelpers.ts  -- MOOD_*/RATING_*/PRACTICE_TYPE_* + DIRECTION/DIFFICULTY/DURATION_BUCKET/TIME_OF_DAY (Calendar)
│   │   ├── adminHelpers.ts    -- Хелперы форматирования для admin-вью
│   │   ├── commission.ts      -- COMMISSION_RATE константа
│   │   └── practiceOptions.ts -- DURATION_OPTIONS, TIMEZONE_OPTIONS, DIRECTION_OPTIONS, DIFFICULTY_OPTIONS
│   │
│   └── views/
│       ├── auth/              -- LoadingView, StandaloneStubView, WelcomeView, OnboardingView
│       ├── shells/            -- UserShell, MasterShell, AdminShell
│       ├── user/              -- Dashboard, Calendar, Diary, Profile...
│       ├── master/            -- Dashboard, Practices, Analytics, Profile...
│       └── admin/             -- Dashboard, Masters, Reports, Consistency...
│
├── public/
│   ├── js/telegram-web-app.js -- Локальная копия Telegram SDK (CDN заблокирован ТСПУ)
│   ├── bg/                    -- Фоновое изображение VELΘ (background.png)
│   ├── icons/                 -- PWA иконки + логотипы VELΘ (logo.svg, logo-white.svg)
│   └── manifest.json          -- PWA manifest
├── Dockerfile
└── package.json
```

---

## 2. Роутинг

### 2.1. Все маршруты

```
/                           → roleRedirect (→ /user/dashboard, /master/dashboard, /admin/dashboard)
/loading                    → LoadingView

-- User --
/user/dashboard             → UserDashboardView
/user/calendar              → CalendarView
/user/diary                 → DiaryFeedView             (name: user-diary -- единая лента-нить, экран 40; шелл в fill-режиме)
/user/profile               → UserProfileView
/user/profile/language-timezone → LanguageTimezoneView  (name: user-language-timezone -- Профиль, экран F)
/user/profile/edit          → EditProfileView            (name: user-edit-profile -- Профиль, экраны C+D)
/user/profile/notifications → NotificationsView          (name: user-notifications -- Профиль, экран E)
/user/practices/:id         → PracticeDetailView
/user/practice-live/:practiceId → PracticeLiveView      (name: practice-live -- экран 14, live-сессия + Zoom)
/user/bookings              → MyBookingsView
/user/bookings/:id          → BookingDetailView          (name: booking-detail -- экран 18)
/user/ai-summary            → AiSummaryView              (name: user-ai-summary -- экран 16, заглушка, ждёт AI-бэк юзера)
/user/checkin/:practiceId   → CheckinView
/user/feedback/:practiceId  → FeedbackView
/user/topup                 → TopupView
/user/topup/success         → TopupSuccessView
/user/topup/cancel          → TopupCancelView

-- Master --
/master/dashboard           → MasterDashboardView
/master/practices           → MasterPracticesView
/master/practices/new       → CreatePracticeView
/master/practices/:id       → EditPracticeView
/master/practices/:id/attendance → AttendanceView
/master/analytics           → AnalyticsView
/master/profile             → MasterProfileView
/master/finance             → MasterFinanceView
/master/apply               → MasterApplyView
/master/pending             → MasterPendingView

-- Admin --
/admin/dashboard            → AdminDashboardView
/admin/masters              → AdminMastersView
/admin/masters/:id          → AdminMasterReviewView
/admin/reports              → AdminReportsView
/admin/reports/:id          → AdminReportDetailView
/admin/consistency          → AdminConsistencyView
/admin/profile              → AdminProfileView  ← создать (TD-FE-ROLE-SWITCH)

/404                        → NotFoundView
/:pathMatch(.*)             → redirect /404
```

### 2.2. Guards

| Guard | Логика |
|-------|--------|
| `roleRedirect` | Редирект `/` на dashboard по роли. `async` — ждёт `waitUntilReady()` перед чтением `auth.role` |
| `roleGuard('master')` | Пропускает master + admin, остальных → `/user/dashboard` |
| `roleGuard('admin')` | Пропускает только admin → `/user/dashboard` |
| `masterStatusGuard` | Проверяет верификацию профиля мастера, нет → `/master/pending` |
| `applyGuard` | Верифицированный мастер не может повторно подать заявку |

**`beforeEach` (global guard):**

Сейчас: блокирует только `/user/dashboard` для мастера/админа, все остальные `/user/*` доступны.
После `TD-FE-ROLE-SWITCH`: если `uiStore.uiMode === 'user'` — пропускать `/user/dashboard` без редиректа.

### 2.3. Auth инициализация

`waitUntilReady()` в `composables/useAuth.ts` — `Promise`, который резолвится когда `restoreSession()` завершён (или по таймауту 10s). Используется в `roleRedirect` и `beforeEach` чтобы не читать `auth.role` до готовности сессии.

**Шлюз входа в `App.vue` (welcome + onboarding).** После успешной авторизации
`App.vue` не сразу рендерит `RouterView`, а проходит через локальную машину
состояний `stage: 'welcome' | 'onboarding' | 'app'` (обычный `ref`, вне роутера —
консистентно с тем, как LoadingView/StandaloneStubView гейтят доступ):

```
!isReady                       -> LoadingView
isStandalone || !isAuthenticated -> StandaloneStubView
иначе по stage:
  'welcome'    -> WelcomeView      (показывается всем, при каждом открытии)
  'onboarding' -> OnboardingView   (только новым: onboarding_completed === false)
  'app'        -> RouterView
```

Переходы:
- WelcomeView `@enter` ("Войти"): `onboarding_completed === true` -> `stage='app'`;
  иначе -> `stage='onboarding'`.
- OnboardingView `@done` (завершил или пропустил; флаг уже сохранён в нём самом
  через `authStore.updateProfile({ timezone, onboarding_completed: true })`) -> `stage='app'`.
- WelcomeView `@create-account`: только standalone/браузерная сборка (F10); в Telegram
  кнопка скрыта (`v-if="isStandalone"`).

**Продуктовое решение:** Welcome показывается при каждом открытии приложения, для всех
(перезагрузка = новый запуск = снова Welcome). `stage` живёт в памяти компонента, не в
роутере и не персистится. Онбординг-карусель новый юзер видит один раз — после успешного
финиша флаг `onboarding_completed` остаётся `true` (переживает релогин, см. Бэковый
Кодекс 3.7), и при следующем "Войти" он идёт сразу в `app`.

Файлы: `views/auth/WelcomeView.vue` (экран 01), `views/auth/OnboardingView.vue`
(экраны 05-08: 3 интро + шаг таймзоны), `App.vue` (машина состояний).

---

## 3. Компоненты

### 3.1. UI-примитивы (src/components/ui/)

| Компонент | Ключевые пропсы |
|-----------|----------------|
| `VButton` | `variant` (primary/secondary/ghost/danger), `size` (sm/md), `disabled`, `loading` |
| `VInput` | `label`, `placeholder`, `type` |
| `VTextarea` | `label`, `placeholder`, `rows` |
| `VSelect` | `label`, `options` |
| `VCheckbox` | `label`, `checked` |
| `VCard` | slot, `clickable`, `padding` |
| `VBadge` | `variant` (success/warning/error/info) |
| `VTag` | `variant` (blue/pink/sand) — категориальные pill-лейблы |
| `VNotification` | `variant` (warning/success), `title`, `body` — inline banner |
| `VToggle` | `modelValue`, `options` — segmented control |
| `VAccordion` | `title` — expandable row |
| `VAvatar` | `name`, `url`, `size` |
| `VLoader` | `size` |
| `VDivider` | — |
| `VEmptyState` | `icon`, `title`, `description` |
| `VToast` | composable `useToast()` |
| `VStatCard` | `value`, `label`, `icon` |
| `VProgressBar` | `value`, `max`, `color` |
| `VModal` | `open`, `closeOnOverlay`, `showClose` |
| `VeloLogo` | `size`, `variant` (default/white) — загружается через `<img>` из `public/icons/` |

**Иконки** (`src/components/ui/icons/`): SVG-компоненты из `Design_prototype/assets/icons/`. Все принимают проп `size?: number` (default 24). Используются в `VTabBar` через `TabItem.icon: string | Component`.

**Доменные иконки** (`src/components/icons/`, barrel `index.ts`): отдельный набор Vue-компонентов
для контентных экранов (НЕ путать с табовыми из `ui/icons/`). Все: `fill="currentColor"`,
проп `:size` (default 24). Цветные mood-иконки используют `useId()` для уникальных id градиентов.

| Иконка | Назначение |
|--------|-----------|
| `IconMeditation` / `IconBreathwork` | тип практики (meditation -- круг teal-аватар; breathwork -- эвристика по заголовку, см. ниже) |
| `IconCalendar` / `IconClock` | мета практики (дата / длительность) |
| `IconBrain` | AI-блок / экран AI-саммари |
| `IconCheck` | success-галочка (экран 13), verified-бейдж мастера |
| `IconArrowRight` | "Подробнее" в MasterCard |
| `IconClose` | крестик закрытия (попапы) |
| `IconMoodLow` / `IconMoodMid` / `IconMoodHigh` | цветные mood-лица для check-in (экран 12) |
| `IconHome` / `IconGroup` / `IconWarning` / `IconRuble` / `IconSuccess` / `IconSupport` / `IconFeedback` | прочие контентные |

> **Эвристика типа практики:** в `practice_type` НЕТ значения `breathwork`
> (enum: `live | series | one_on_one | replay`). Иконка дыхания выбирается эвристикой
> по заголовку практики -- это намеренно (см. `BookingCard.typeIcon`).

### 3.2. Layout-компоненты (src/components/layout/)

| Компонент | Описание |
|-----------|----------|
| `VHeader` | Заголовок с кнопкой назад и action-слотом справа |
| `VTabBar` | Нижняя навигация, конфигурируется через `items` пропс. Редизайн по Figma: круглые стеклянные "пузыри" 63x63, без подписей (aria-label сохранён). Активная вкладка — растворённый пузырь + `box-shadow: var(--velo-shadow-glow)` (мягкое свечение), различается ТОЛЬКО свечением, не размером. Иконки 27x27 (`fill="currentColor"`). Поле `badge` в интерфейсе оставлено, но не рендерится |
| `MobileLayout` | Header-слот + `<slot>` + VTabBar (user и master). Проп `fill?` (по умолчанию false): в fill-режиме `main` не скроллится сам, а отдаёт полную высоту дочернему вью (для чат-экранов с фиксированным низом — дневник). Включается в UserShell по роуту `user-diary` |
| `AdminLayout` | Аналогично, отдельный для будущего desktop-варианта |

### 3.3. Shared-компоненты (src/components/shared/)

| Компонент | Описание |
|-----------|----------|
| `PracticeCard` | карточка практики в каталоге |
| `PracticeHeroCard` | hero-шапка практики (иконка teal-круг 46px, title, мета date/duration, проп `participants?`, слот `#badge`). Используется на экранах 15 и 18 |
| `MasterCard` | карточка мастера (аватар `IconMeditation`-плейсхолдер, имя + `IconCheck` verified, теги `VTag` чередованием `[blue,pink,sand][i%3]`, "Подробнее" → toast "скоро"). Пропы `masterName`, `methods`. Используется на 15 и 18 |
| `BookingCard` | dumb-компонент брони. Пропы `{ booking, badge?, clickable? }` — бейдж считается во вью-родителе (`badgeFor`), сам компонент не содержит бизнес-логики. Экспортит `interface BookingBadge { label; variant }`, `variant: 'live' \| 'today' \| 'tomorrow' \| 'done' \| 'cancelled' \| 'no_show'` |
| `FormShell` | общая оболочка форм (header + контент + actions + success-экран). Извлечена из CheckinView/FeedbackView — закрыла WARNING-9 (~200 строк дублей CSS) |
| `BookingPopup` | попап бронирования |
| `CancelBookingPopup` | попап отмены брони. Тип пропа структурный: `interface CancellableBooking { practice: { title; scheduled_at } }` — принимает и `BookingWithPracticeResponse`, и `BookingDetailResponse`. Refund deadline 24h. Используется только в BookingDetailView |
| `WeekStrip` | (Calendar) недельная лента: 7 пилюль ПН-ВС (день+число+точка-маркер), активный день залит `--velo-primary`, стрелки ←→. Dumb: пропы `days/selectedDate/daysWithPractices/localDateKey`, эмиты `select-day/prev-week/next-week`. Пилюли rounded-15 (Figma 44×71), стрелки — inline SVG (в DS нет компонента-стрелки) |
| `CalendarPracticeCard` | (Calendar) карточка практики фида на визуальном языке `BookingCard` (иконка-в-круге 46px, мастер+verified, мета 🗓️/🕐). Бейдж: `is_paid`→«Оплачено» (teal), иначе `is_free`→«Бесплатно» (blue). Проп `practice: PracticeResponse`, эмит `click` |
| `CalendarFilterModal` | (Calendar) модалка фильтра на `VModal` (кадр 2). Группы: Направление/Сложность/Тип (мульти-чипы), Длительность/Время (одиночный выбор, 4 корзины времени), Вид практики (свободный `VInput` — см. техдолг). Работает на draft-копии, применяет по «Применить». Пропы `open/filters`, эмиты `apply/close` |
| `DiaryFeedCard` | (Diary redesign) карточка события ленты, 3 формы по `kind`: **banner** (бирюзовый для `booking_confirmed`, нейтральный для отмен/переносов), **practice** (белая: practice_outcome — мастер+дата+бейдж Done/Не состоялась, без аватара — TD-DIARY-PRACTICE-AVATAR), **standard** (иконка+заголовок+превью+дата для checkin/feedback/note/dream). Читает `snapshot` защитно. `@tap` эмитит `{ item, editable }` (note/dream → editable). kind→иконка-маппинг локально во вью (utils не импортируют `.vue`) |
| `DiaryComposer` | (Diary redesign) нижний композер-pill: поле + mic-стаб (toast) + send. Создаёт note через `diaryStore.createEntry`. Стекло: `--velo-glass-blue-15`, backdrop-blur, glow-тень |
| `DiaryTimeline` | (Diary redesign) нить с альтернированием (экран 40, Уровень 2 упрощённый): центральная ось (CSS), дата-узлы по календарным дням в tz юзера, banner/practice по центру, standard чередуются L/R сквозным счётчиком со **сбросом каждый день**, сторона детерминирована позицией (пагинация не перетасовывает). Коннекторы — CSS-штрихи (не Figma-кривые) |

### 3.4. Флоу ДАШБОРД (экраны 10–18)

Реализован по Figma (node `541:6648`). Карта вью:

| Экран | View | Примечания |
|-------|------|-----------|
| 10/11 Dashboard | `views/user/UserDashboardView.vue` | белые карточки `--velo-bg-card-solid`, алерты, карточка ближайшей практики, AI-блок (тоггл Неделя/Месяц + mood). `nearestIsLive` + `openNearest()`: live → practice-live, иначе practice-detail |
| 12/13 Check-in + Success | `views/user/CheckinView.vue` (+ `shared/FormShell.vue`) | mood-лица `IconMood*`, success `IconCheck`. `onBack()` → `router.back()` (фикс петли 12↔15) |
| 14 Practice-Live | `views/user/PracticeLiveView.vue` | видео-плейсхолдер, бейдж "● В эфире", "Войти" (`platform.openLink`, дизейбл без `https`-zoom), "Check-in", "Покинуть". Достижим из дашборда при live |
| 15 Practice Detail | `views/user/PracticeDetailView.vue` | каталог + booked в одном вью. Hero/master вынесены в `PracticeHeroCard`/`MasterCard` (рефакторинг, God-component закрыт) |
| 16 AI-summary | `views/user/AiSummaryView.vue` | честная заглушка "в разработке" (`IconBrain`). Персонального AI-саммари юзера на бэке НЕТ |
| 17 My reservations | `views/user/MyBookingsView.vue` (+ `shared/BookingCard.vue`) | две секции Предстоящие/Прошедшие. Бейдж "В эфире" приоритетнее today/tomorrow; live-практики сортируются вверх (`upcomingRank`). Даты TZ-aware через `calendarDate(d, tz)` |
| 18 Booking Detail | `views/user/BookingDetailView.vue` | hero, статус + `VBadge`, `MasterCard`, секция Zoom, "Отменить" + `CancelBookingPopup`. Грузит через `bookingsStore.fetchBooking(id)` |

**Бэк-разблокировка:** `PracticeSummary` получил поле `status` (см. Бэковый Кодекс §2)
→ дашборд и список броней показывают бейдж "В эфире" и ведут на `practice-live`
без дополнительного запроса деталей.

---

### 3.5. Флоу КАЛЕНДАРЬ (кадры 1-3, Calendar iteration)

Реализован по Figma (node `541:1553`, кадры 1/2/3). Карта вью:

| Кадр | View / компонент | Примечания |
|------|------------------|-----------|
| 1 Лента «Календарь» | `views/user/CalendarView.vue` | заголовок, `WeekStrip`, контрол «Выбрать практики», секции по дням (`formatDateShort`), `CalendarPracticeCard`, состояния loading/error/empty. Данные из `useCalendarStore` |
| 2 Модалка «Фильтр» | `shared/CalendarFilterModal.vue` | направление/сложность/тип (мульти), длительность/время (одиночный, 4 корзины), вид практики (VInput) |
| 3 «Выбрать практики» раскрыто | часть `CalendarView` | свёрнуто — пилюля + воронка (→ модалка); развёрнуто — чипы активных фильтров (тап снимает фильтр) + кнопка свернуть. **Вариант 1:** модалка — единственный источник редактирования фильтров, inline-чипы лишь отображают/снимают активные |
| — Индикатор сложности | `views/user/PracticeDetailView.vue` | точки ●●○ (`DIFFICULTY_DOTS`) + лейбл (`DIFFICULTY_LABEL`) в body детали; показывается только если `practice.difficulty` задан. `PracticeHeroCard` не тронут |

**Стор `useCalendarStore`** (`stores/calendar.ts`) — намеренно ОТДЕЛЬНЫЙ от `usePracticesStore`,
чтобы навигация по неделям и фасет-фильтры Календаря не задевали общий фид (Дашборд использует
`usePracticesStore`/`useBookingsStore`). Грузит всю видимую неделю одним запросом
(`date_from..date_to` = локальные Пн..Вс **с буфером ±1 день** — фикс W-2 для экстремальных TZ),
маркеры дней и список выбранного дня выводятся клиентом по `calendarDateInTz` (TZ практики).

**Контракт фильтров:** `PracticeFilters` стал мульти-фасетным — `practice_type` теперь
массив, добавлены `direction[]/difficulty[]/style/duration_bucket/time_of_day`. `buildQuery`
(`api/utils.ts`) сериализует массивы повторяемыми ключами, пустой массив/undefined/null —
пропускает. Старый `CalendarView` (до итерации) был единственным потребителем одиночного
`practice_type` и переработан полностью; Дашборд `practice_type` не использует — не затронут.

### 3.6. Флоу КАЛЕНДАРЬ (кадры 4-7 + профиль мастера, Calendar flow)

Завершение флоу по Figma (node `541:1553`). Карта вью:

| Кадр | View / компонент | Примечания |
|------|------------------|-----------|
| 4 + master profile | `views/user/MasterPublicView.vue` | публичный профиль мастера для юзера: hero (`VAvatar xl` + имя + ✓Верифицирован + «N лет опыта» + bio), две стат-карточки (`practices_count`/`reviews_count` с рус. плюрализацией), аккордеон «Методы», «Ближайшие практики» (`getPractices({master_id, status:'scheduled'})`). «Задать вопрос» → toast-заглушка (TD-ASK-MASTER). Роут `user-master-public` (`masters/:id`). Грузит профиль через `getPublicMaster(userId)`; loading/error/not-found через `VEmptyState`; ошибка списка практик не фатальна (отдельный try/catch → `upcoming=[]`) |
| 5 «Практика забронирована!» | `views/user/BookingConfirmedView.vue` | экран после успешной брони: success-карточка (`IconSuccess` celebration в teal-круге + статичный Zoom-текст), блок «запрос мастеру» (textarea + инфо-баннер + «Отправить запрос» = toast-заглушка, TD-ASK-MASTER), «В календарь» → calendar, «На главную» → dashboard. Роут `user-booking-confirmed` (`booking-confirmed/:practiceId`). Самодостаточен: грузит практику по id в `onMounted` (переживает reload/deep-link). `PracticeDetailView.onPurchased` редиректит сюда |
| 6 «Вопрос мастеру» | — отложен | См. TD-ASK-MASTER: вопросы мастеру — отдельная сквозная фича с бэком. Кадр не реализован |
| 7 Feedback (рейтинг) | `views/user/FeedbackView.vue` | emoji-рейтинг (❓👍🔥) заменён векторными иконками из Figma `IconRatingConfused/Good/Fire` (`<component :is>`), цвет каждой через `RATING_ICON_COLOR` (токены `--velo-rating-*`). `RATING_ICON` map — локально во вью (utils не импортируют `.vue`, как `MOOD_ICON` в Checkin) |
| 7 Feedback success | `views/user/FeedbackView.vue` (success-слот) | success-сердце `💚` заменено векторным `IconHeart` (Figma, teal через `--velo-teal-400`) в слоте `#success-icon` FormShell |

**Аватары — `VAvatar` (закрыт TD-FE-AVATAR).** Везде, где раньше был плейсхолдер
`IconMeditation`, теперь `VAvatar` (`ui/VAvatar.vue`): показывает фото по `url` или
инициалы из `name`, размеры sm/md/lg/xl. `MasterCard` — `VAvatar lg`, `MasterPublicView`
hero — `VAvatar xl`. Единый паттерн вызова `:url="avatarUrl ?? ''"` + `:name`. Seed-мастер
без Telegram-фото корректно показывает инициалы (ожидаемо, не баг). Бэк отдаёт
`master_avatar_url` в деталях практики (Бэковый Кодекс §3.9).

**Иконка hero практики — по `direction`, не по типу.** `PracticeHeroCard` выбирает иконку
через `DIRECTION_ICON: Partial<Record<PracticeDirection, Component>>` (meditation/yoga/breathwork)
+ `DIRECTION_ICON_FALLBACK = IconMeditation`. **Partial + fallback намеренно:** бэк будет
расширять список направлений (somatic/womens_circle/mens_circle/tantra/kundalini, TD-CAL-DIRECTIONS-EXPAND) —
новые значения не сломают `vue-tsc` до появления иконки, просто получат fallback.
`IconYoga` сейчас — Claude-плейсхолдер (TD-CAL-ICON-YOGA).

**Иконки из Figma — паттерн извлечения.** Рейтинг/сердце экспортированы из Figma как SVG
(get_design_context → asset URL → curl → реальный SVG, хотя Figma отдаёт `<img>`-обёртку),
причёсаны под контракт DS-иконок: чистый `<svg :width :height viewBox fill="currentColor">`,
проп `size`, оригинальный viewBox. Каждая одноцветная → цвет задаёт родитель через токен.
Новые токены `--velo-rating-confused/good/fire` (good = новый `#d66674`; confused/fire —
ссылки на `--velo-primary-dark`/`--velo-peach-500`); ОТДЕЛЬНО от `RATING_COLOR`
(заливки баров аналитики — не трогать, иначе ломается AnalyticsView).

---

### 3.7. Флоу ПРОФИЛЬ (раздел Профиль, node `4715-3463`)

Реализован раздел «Профиль» по Figma (`F7PD5isLfLdyc0q1Bd5n5c`). Это USER-профиль.
Карта вью:

| Экран (Figma node) | View / роут | Примечания |
|--------------------|-------------|-----------|
| A — главный (70/71) | `UserProfileView.vue` (`user-profile`) | две стат-карточки из `GET /bookings/me/stats` (`getMyStats` в `api/bookings.ts`); векторные иконки (IconEdit/Bookings/Bell/Globe/Share/Logout); пункты-переходы. Балансовая карта и email УБРАНЫ с главного; «Сообщения» УБРАНЫ (модуля нет). «Изменить фото» / share / прочие заглушки — toast |
| F — Язык/Часовой пояс (75) | `LanguageTimezoneView.vue` (`user-language-timezone`) | таймзона = переиспользуемый `VSelect` + `TIMEZONE_OPTIONS` (`practiceOptions.ts`), автосейв `updateProfile({timezone})` + revert-on-error. Язык — заглушка из ОДНОГО пункта «Русский» (i18n НЕТ), рендер через `v-for` по `LANGUAGE_OPTIONS` (расширяемо), неинтерактивна пока язык один (`isLanguageStatic`), НЕ сохраняется. «Изменить город»/radio-список из макета НЕ делаем — выбор пояса через select |
| C — Редактирование (72) | `EditProfileView.vue` (`user-edit-profile`) | Имя=`first_name`; E-mail=disabled-заглушка «появится позже» (не сохраняется); Телефон=`phone`, О себе=`bio` (оба в credentials JSONB, см. Бэк §3.11); «Изменить фото»=toast. Сохранение шлёт только изменённые поля; очистка phone/bio = пустая строка. `VInput` БЕЗ пропа `error` — ошибка телефона рисуется отдельным `<p>`. `bio` сравнивается/шлётся через `.trimEnd()` (S-1) |
| D — Удаление (73) | модалка в `EditProfileView` (`VModal`) | «Удалить аккаунт» -> подтверждение -> `deleteMe()` (`DELETE /users/me`) -> `authStore.logout()`. MVP = сброс онбординга (Бэк §3.11), данные сохраняются. Текст модала ЧЕСТНЫЙ: «вернётся к начальному состоянию… данные сохранятся» (W-2), кнопка осталась «Удалить» |
| E — Уведомления (74) | `NotificationsView.vue` (`user-notifications`) | 4 свича (push / practice_reminders / master_messages / support_messages), все ON по умолчанию; хранение — вложенный `credentials.notifications` (Бэк §3.11); автосейв при флипе ТИХО (без тоста), revert-on-error; шлётся только флипнутый ключ |
| G — Поддержка (76) | — отложен | Не реализован по решению заказчика. Пункт «Поддержка» на экране A — toast-заглушка. Задумано: форма (Тема+Сообщение+Отправить) + тост, без бэка |

**Новый UI-примитив `VSwitch`** (`components/ui/VSwitch.vue`, в barrel рядом с
`VCheckbox`): boolean on/off (pill + ползунок), `v-model`, `disabled`, `aria-label`.
Отличается от `VToggle` (segmented control) и `VCheckbox` (квадратный чек). Цвета —
токены (`--velo-primary` вкл).

**i18n НЕ существует** — язык на экране F это задел: переключатель показан, но
интерфейс не переключает и предпочтение не сохраняется. Полноценная локализация —
отдельная крупная задача, в MVP не входит.

---

## 4. Stores (Pinia)

| Store | Ключевые поля |
|-------|--------------|
| `auth` | `user`, `token` (module-level var в client.ts), `role`, `isAuthenticated`; методы `restoreSession`/`fetchMe` (через `getMe`), `updateProfile(body)` (через `updateMe` + `_setUser`, бросает ошибку наверх — карусель не "проскакивает" при сбое сохранения) |
| `practices` | `practices[]`, `total`, `filters`, `loading` |
| `calendar` | `weekAnchor`, `selectedDate`, `weekPractices[]`, `filters` (facets); computed `days`, `daysWithPractices`, `selectedDayPractices`; actions `loadWeek`, `selectDay`, `prevWeek`, `nextWeek`, `applyFilters`, `init`. Экспортит `CalendarFacetFilters`, `localDateKey` |
| `bookings` | `bookings[]`, `total`, `loading`; `selectedBooking`, `selectedLoading`, `selectedError`; методы `fetchBooking(id)` (через `getBooking` → `BookingDetailResponse`), `joinBooking`/`leaveBooking` (возвращают `{ ok, error }` через `extractApiError`) |
| `balance` | `balance_cents`, `operations[]` |
| `master` | `profile` (MasterProfile), `practices[]`, `withdrawals[]` |
| `diary` | Переписан (Diary redesign). Единая курсорная лента: `feedItems[]`, `feedLoading`, `feedError`, `feedHasMore`, реактивные `feedFilters` (categories/date_from/date_to/search); actions `fetchFeed`/`loadMoreFeed`/`refreshFeed`/`setFeedFilters`/`clearFeedFilters`/`runFeedSearch` (на `useCursorPagination`). Сохранены `submitCheckin`/`submitFeedback` (Checkin/FeedbackView), CRUD записей `createEntry`/`updateEntry`/`deleteEntry` (рефрешат ленту), `selectedEntry`+`fetchEntry`, `insightsCache` (master-facing), `$reset`. Удалены три offset-списка (checkins/feedbacks/entries) и их `fetch*`/`loadMore*` — их роль забрала лента |

**Осознанное решение:** `token` хранится как module-level переменная в `api/client.ts`, не в Pinia — исключает circular dependency `client → store → client`.

---

## 5. Утилиты

### 5.1. displayHelpers.ts — единственный источник маппингов

Все emoji, лейблы и CSS-цвета для mood/rating/type живут только здесь.
Дублировать в компонентах запрещено.

```typescript
// Mood (check-in)
MOOD_OPTIONS: { value, emoji, label }[]
MOOD_EMOJI: Record<string, string>   -- { low: '😔', mid: '😐', high: '😊' }
MOOD_LABEL: Record<string, string>
MOOD_COLOR: Record<string, string>   -- CSS-переменные, не hex

// Rating (feedback)
RATING_OPTIONS: { value, emoji, label }[]
RATING_EMOJI: Record<string, string>  -- { fire: '🔥', good: '👍', confused: '❓' }
RATING_LABEL: Record<string, string>
RATING_COLOR: Record<string, string>  -- CSS-переменные

// Practice type
PRACTICE_TYPE_EMOJI: Record<string, string>
PRACTICE_TYPE_LABEL: Record<string, string>

// Calendar taxonomy + feed buckets (Calendar iteration)
DIRECTION_LABEL: Record<PracticeDirection, string>      -- meditation→Медитация, yoga→Йога, breathwork→Дыхательные практики
DIFFICULTY_LABEL: Record<PracticeDifficulty, string>    -- beginner→Начальная, medium→Средняя, high→Высокая
DIFFICULTY_DOTS: Record<PracticeDifficulty, number>     -- beginner→1, medium→2, high→3 (индикатор ●●○ на детали)
DURATION_BUCKET_LABEL: Record<DurationBucket, string>   -- short→«До 1 часа», long→«1 час и больше»
TIME_OF_DAY_LABEL: Record<TimeOfDay, string>            -- night→Ночь, morning→Утро, day→День, evening→Вечер
```

### 5.2. currency.ts

```typescript
eurStringToCents(str: string): number   -- "14.57" → 1457 (без float-ловушки)
centsToEurString(cents: number): string -- 1457 → "14.57"
```

Прямое `parseFloat(x) * 100` запрещено — IEEE-754 float precision trap.

### 5.3. format.ts

`formatMoney(cents, currency, locale)`, `formatDate(iso)`, `formatDateShort(iso)`.

### 5.4. commission.ts

`COMMISSION_RATE = 0.15` — единственный источник. Используется в `CreatePracticeView` и `EditPracticeView` для подсказки "Вы получите".

---

## 6. Правила разработки

### FP-01: Только CSS-переменные, никаких hex

```css
/* ЗАПРЕЩЕНО: */
color: #334D6E;
background: #FEF2F2;

/* ПРАВИЛЬНО: */
color: var(--velo-primary);
background: var(--velo-error-bg-subtle);
```

Все токены определены в `src/styles/variables.css`. При необходимости нового токена — добавлять туда.

### FP-02: displayHelpers — единственный источник маппингов

```typescript
// ЗАПРЕЩЕНО — локальный дубль:
const MOOD_EMOJI = { low: '😔', mid: '😐', high: '😊' }

// ПРАВИЛЬНО:
import { MOOD_EMOJI } from '@/utils/displayHelpers'
```

### FP-03: Деньги — только через currency.ts

```typescript
// ЗАПРЕЩЕНО:
const cents = parseFloat(input) * 100

// ПРАВИЛЬНО:
const cents = eurStringToCents(input)
```

### FP-04: Double-submit guard — ДО валидации

```typescript
// ПРАВИЛЬНО — guard первым:
if (submitting.value) return
submitting.value = true
try {
  // validate, then submit
} finally {
  submitting.value = false
}
```

### FP-05: Комментарии — только английский

```typescript
// ЗАПРЕЩЕНО:
// Получаем список практик

// ПРАВИЛЬНО:
// Fetch paginated practice list
```

### FP-06: Типизация — никаких `any`

```typescript
// ЗАПРЕЩЕНО:
const data: any = await api.get(...)

// ПРАВИЛЬНО:
const data: PracticeResponse = await getPractice(id)
```

### FP-07: Ошибки API — только через ApiResponseError

```typescript
import { ApiResponseError } from '@/api/client'

try {
  await someApiCall()
} catch (e) {
  if (e instanceof ApiResponseError) {
    toast.error(e.message)
  }
}
```

### FP-08: sessionStorage для token, не localStorage

Telegram WebApp закрывает вкладку — `sessionStorage` очищается автоматически.
`localStorage` оставлял бы протухший токен навсегда.

### FP-09: API-типы генерируются из OpenAPI, не пишутся вручную

```typescript
// ЗАПРЕЩЕНО — ручной интерфейс для бэкенд-схемы:
export interface PracticeResponse { ... }  // в types.ts

// ПРАВИЛЬНО — автогенерация + реэкспорт:
// generated.ts — создаётся скриптом, НЕ ТРОГАТЬ
// types.ts — реэкспорт из generated + frontend-only типы
export type { PracticeResponse } from './generated'
```

Скрипт: `backend/scripts/generate_ts_types.py`. Запускается при `velo update` автоматически.
Frontend-only типы (PracticeFilters, ApiError и т.д.) остаются в `types.ts`.

### FP-10: `vue-tsc` проверяет ШАБЛОН, а не только `<script setup>`

Серверный GATE (`vue-tsc --noEmit` в build) проверяет типы и в шаблоне — в т.ч.
**передачу пропов в дочерние компоненты** и обращения к optional-полям в биндингах.
Скрипт-эмуляция, проверяющая только извлечённый `<script setup>` со стаб-компонентами
(`Component = {}`), эти ошибки НЕ видит — стаб не несёт сигнатуру пропов.

```vue
<!-- FormShell объявляет successIcon: string (REQUIRED). Слот #success-icon
     лишь переопределяет рендер (<slot name="success-icon">{{ successIcon }}</slot>),
     но проп всё равно обязателен по типам. -->

<!-- ❌ vue-tsc TS2345: Property 'successIcon' is missing -->
<FormShell ...>
  <template #success-icon><IconHeart /></template>
</FormShell>

<!-- ✅ передать проп (пустой) + слот: тип удовлетворён, слот рисует иконку -->
<FormShell success-icon="" ...>
  <template #success-icon><IconHeart /></template>
</FormShell>
```

Та же категория ошибки ловила дважды: optional generated-поле (`profile.methods?.length`
в шаблоне) и required-проп дочернего компонента. **Правило проверки перед отдачей:** для
вью, которые передают пропы в дочерние компоненты (FormShell, hero-карточки и т.п.),
гонять НАСТОЯЩИЙ `vue-tsc` с типизированными стабами дочерних компонентов, а не
script-эмуляцию. Контр-тест (убрать фикс → ошибка воспроизводится) подтверждает, что
проверка реальная.

---

## 7. Дизайн-система

Токены в `src/styles/variables.css`. Дизайн-система VELΘ — soft glassmorphism, перенесена из `Design_prototype/` (DS-1 — DS-9, март 2026).

Основные группы:

```css
/* Цвета */
--velo-primary: #627a9c          -- основной синий
--velo-brand-text: #4c6589       -- текст, заголовки
--velo-glass-blue-15/60          -- glass-поверхности
--velo-glass-teal-30/40          -- teal glass (success)
--velo-glass-peach-40            -- peach glass (warning)
--velo-glass-white-01            -- ghost-кнопки
--velo-teal-*, --velo-peach-*, --velo-pink-*, --velo-sand-*  -- примитивная палитра

/* Семантика */
--velo-warning-bg/border/text/text-light
--velo-error-bg/border/text
--velo-success-bg/text
--velo-info-bg/text
--velo-mood-low/mid/high

/* Типографика */
--font-body: 'Marmelad', 'Noto Sans', sans-serif  -- единственный шрифт, weight 400
--font-heading: 'Marmelad', ...                    -- алиас, тот же шрифт

/* Spacing */
--space-1..10, --velo-content-width: 336px, --velo-screen-padding: 33px

/* Радиусы */
--radius-sm/md/lg: 15px     -- карточки
--radius-xl: 100px           -- теги
--radius-full: 9999px        -- pill (кнопки)
--radius-input: 5px          -- инпуты

/* Тени */
--velo-shadow-glow: 0px 0px 20.9px 7px #ffffff  -- glow на всех кнопках
```

Шрифт: Marmelad Regular 400 — единственный вес, единственное начертание. Подключён через `<link>` в `index.html`.

Фон: `body { background: url('/bg/background.png') center / cover no-repeat fixed }` — фото из `Design_prototype`, sacred geometry overlay. Все layout-контейнеры прозрачные.

**Правило FP-01 уточняется:** стекло-эффекты используют `rgba`-значения через переменные (`var(--velo-glass-blue-15)`), не через прямые hex.

---

## 8. Phase F9 ✅

Выполнено. Check-in, Feedback, Дневник, Аналитика мастера реализованы и задеплоены.

---

## 9. Phase F10 (не начата)

| Задача | Описание | Зависимость |
|--------|----------|-------------|
| Standalone-авторизация | `platform/standalone.ts` — полноценная реализация. Новый бэкенд-эндпоинт `POST /api/v1/auth/email` | Новый бэкенд |
| Push-уведомления | Service Worker + Web Push channel в notification formatters | Бэкенд Phase 7 частично готов |
| Skeleton-загрузки | Заменить спиннеры на skeleton placeholders | — |
| Тёмная тема | CSS-переменные позволяют, нужен toggle + сохранение | — |
| Pull-to-refresh | — | — |
| Haptic feedback | На кнопках и успешных действиях | — |
| Offline-заглушка | "Нет подключения" + кнопка "Повторить" | — |

---

## 10. Технический долг

### Обозначения

- **Среда:** 🧪 низкий приоритет / 🚀 перед публичным запуском
- **Статус:** ⬜ Open

### Перед публичным запуском 🚀

| ID | Файл | Описание | Решение |
|----|------|----------|---------|
| **TD-RU-PROXY** | Инфра | Hetzner IP заблокирован ТСПУ. Недоступен из России без VPN (и Telegram WebView, и обычные браузеры) | Российский reverse proxy (Timeweb/Selectel ~300-500₽/мес) или DDoS-Guard CDN |
| **TD-F01** | `platform/telegram.ts`, `composables/useAuth.ts` | Deep links не обрабатываются. `startapp=open_practice__{uuid}` открывает дашборд вместо практики. Бэкенд уже генерирует корректные ссылки через `TelegramFormatter.format_deep_link()` | Парсить `startapp` параметр в `useAuth.ts` при инициализации, редиректить на нужный роут |

### Переключение режима мастер ↔ юзер

| ID | Среда | Описание | Решение |
|----|-------|----------|---------|
| **TD-FE-ROLE-SWITCH** | 🧪 | Мастер и Админ не имеют UI-точки входа в юзерский интерфейс (каталог, бронирования, дневник). `/user/dashboard` редиректит обратно. Маршруты `/user/*` (кроме dashboard) технически доступны, но недосягаемы | **Подробное решение:** |

**Детали TD-FE-ROLE-SWITCH:**

Хранение режима: Pinia (`src/stores/ui.ts`, поле `uiMode: 'default' | 'user'`).
Сброс при старте: `uiMode = 'default'` при каждом открытии приложения (не персистится).
Область: мастер и админ (админ тоже является мастером для тестирования).

Файлы для изменения:

| Файл | Изменение |
|------|-----------|
| `src/stores/ui.ts` | **Создать.** Поле `uiMode: 'default' \| 'user'`, action `setUiMode(mode)` |
| `src/views/master/MasterProfileView.vue` | Кнопка "Перейти в интерфейс юзера" → `uiMode = 'user'` + `router.push('/user/profile')` |
| `src/views/admin/AdminProfileView.vue` | **Создать.** Минимальный профиль администратора с той же кнопкой переключения |
| `src/router/tabs.ts` | Добавить 4-й таб в `ADMIN_TABS`: `{ icon: '👤', label: 'Я', to: '/admin/profile' }` |
| `src/router/index.ts` | Добавить маршрут `/admin/profile`. Адаптировать `beforeEach`: если `uiStore.uiMode === 'user'` — пропускать `/user/dashboard` без редиректа |
| `src/views/user/UserProfileView.vue` | Кнопка "Вернуться в режим мастера/админа", видна только если `role === 'master' \|\| role === 'admin'` → `uiMode = 'default'` + `router.push('/master/dashboard')` или `/admin/dashboard` |

Логика `beforeEach` после изменения:
```
if (role === 'master' || role === 'admin') && to === /user/dashboard:
  if uiMode === 'user' → пропустить (return true)
  else → redirect /master/dashboard или /admin/dashboard
```

### Ревью v2 — критические (март 2026)

| ID | Среда | Файл | Описание | Решение |
|----|-------|------|----------|---------|
| **CRITICAL-2** | 🚀 | `api/client.ts` | `fetch()` без `AbortController` и timeout. При потере сети запрос висит вечно — в Telegram WebApp это обычная ситуация | `AbortController` + 15с timeout, новый класс `ApiTimeoutError` |

### Ревью v2 — открытые находки (март 2026)

| ID | Среда | Файл | Описание | Решение |
|----|-------|------|----------|---------|
| **NEW-1** | 🧪 | `UserDashboardView.vue`, `PracticeDetailView.vue` | `CHECKIN_WINDOW_H=3` и `FEEDBACK_WINDOW_H=72` захардкожены в двух местах — рассинхрон при изменении | Вынести в `utils/constants.ts` |
| **NEW-2** | ✅ | ~~`DiaryView.vue`~~ | Снято Diary redesign: `DiaryView.vue` удалён (заменён `DiaryFeedView`), локальной `formatShortDate` больше нет; дата ленты — `formatFeedDateTime` в `utils/format.ts` |
| **NEW-3** | ✅ | ~~`DiaryView.vue`~~ | Снято Diary redesign: монолит-вкладки удалён целиком вместе с 5 sub-компонентами (DiaryList/DiaryCheckinDetail/DiaryFeedbackDetail/DiaryEntryDetail/DiaryEntryForm). Новая структура — `DiaryFeedView` + `DiaryTimeline` + `DiaryFeedCard` + `DiaryComposer` |
| **NEW-4** | ✅ | ~~`DiaryView.vue`~~ | Снято Diary redesign: старый `onMounted` с `Promise.all` удалён; `DiaryFeedView` грузит ленту через стор с обработкой ошибок (`feedError` + состояние ошибки во вью) |
| **NEW-5** | ✅ | `CheckinView.vue`, `FeedbackView.vue`, `DiaryView.vue` | `background: white` хардкод | Закрыто в DS-7 — заменено на `transparent` / glass-токены |
| **NEW-6** | ✅ | `stores/diary.ts` | Снято Diary redesign: в переписанном сторе у `insightsCache` есть LRU-ограничение (`MAX_INSIGHTS_CACHE=100` + эвикция старейшего ключа при переполнении) |
| **WARNING-1** | ✅ | `stores/*.ts` | Каждый store реализует свой паттерн try/catch — 7+ дублей одинаковой структуры | ЗАКРЫТО: единый `composables/useApiError.ts` (`extractApiError`), применён в bookings-store (join/leave/fetchBooking) и далее по мере касания |
| **WARNING-3** | 🧪 | `composables/useAuth.ts` | `waitUntilReady()` при таймауте резолвится без ошибки — код дальше думает что auth готов | Возвращать `{ ok: boolean, timedOut: boolean }` |
| **WARNING-8** | 🧪 | `CheckinView.vue`, `FeedbackView.vue` | `fetchPractice()` вызывается всегда в `onMounted`, даже если practice уже в store | `if (store.selected?.id !== practiceId)` перед fetch |
| **WARNING-9** | ✅ | `CheckinView.vue`, `FeedbackView.vue` | ~200 строк идентичного CSS (header, textarea, actions, success screen) | ЗАКРЫТО (флоу дашборд): извлечён `shared/FormShell.vue` со слотами, CheckinView переведён на него |
| **WARNING-10** | 🧪 | Стили | Magic numbers: `font-size: 80px`, `56px`, `min-width: 90px` без CSS-токенов | Добавить токены в `variables.css` |
| **WARNING-11** | 🧪 | Компоненты | `platform.hapticFeedback()` без fallback — silent crash если platform не инициализирован | try/catch вокруг вызовов haptic |
| **WARNING-12** | 🧪 | `tests/` | 2 тест-файла при значительной бизнес-логике F9 (DiaryStore, time window, alert banners, guards) | Покрыть: DiaryStore CRUD, `inCheckinWindow`, `inFeedbackWindow`, `checkinAlert`, router guards |
| **WARNING-13** | 🧪 | `api/client.ts`, `composables/useAuth.ts` | Module-level mutable state (`_token`, `isReady`) не сбрасывается между тестами | Явный `reset()` или DI через параметры |

### Фронтенд — открытые

| ID | Среда | Файл | Описание | Решение |
|----|-------|------|----------|---------|
| TD-SDK | 🧪 | `public/js/telegram-web-app.js` | SDK — локальная копия (3331 строка). Ручное обновление при новых версиях | Миграция на `@telegram-apps/sdk` (npm) |
| TD-FE-W4 | 🧪 | `MasterProfileView.vue` | `v-show` на payout-форме — весь DOM всегда присутствует | Заменить на `v-if` если форма не нужна при анимированном переходе |
| TD-FE-W6 | ✅ | `MasterFinanceView.vue` | `MIN_WITHDRAWAL_EUROS=50` и `WITHDRAWAL_FEE_EUROS=2` захардкожены — рассинхрон с `config.py` при изменении | CR-01: бэкенд отдаёт `min_withdrawal_cents` и `withdrawal_fee_cents` в `MasterProfileResponse` |
| TD-FE-A11Y | 🧪 | Admin views (5 файлов) | Clickable `<div>` без `role="button"`, `tabindex="0"`, `@keydown` handlers. Нарушает WCAG 2.1 AA 2.1.1. Затронуто: алертовый баннер, stat cards, action cards, master cards, report cards | Добавить `role="button"`, `tabindex="0"`, `@keydown.enter.stop`, `@keydown.space.prevent` |
| TD-FE-LOGO-SVGO | 🧪 | `public/icons/logo.svg`, `public/icons/logo-white.svg` | SVG-логотипы загружены через `<img>` как есть из Figma-экспорта: `logo.svg` — 228KB, `logo-white.svg` — 434KB. Избыточный размер из-за неоптимизированных path-данных | Прогнать через `svgo` с дефолтными настройками — ожидаемое уменьшение в 5–10× без видимых изменений |
| AUDIT-0520-FE | 🧪 | `src/**` | Нет компонентных тестов фронтенда (отмечено аудитом 2026-05-20). Логика вью покрыта только ручной проверкой | Vitest + Vue Test Utils для ключевых вью (OnboardingView gate-машина, BookingPopup, формы) |
| **TD-FE-AISUM** | 🧪 | `views/user/AiSummaryView.vue` | Экран 16 — честная заглушка "в разработке". Персонального AI-саммари юзера на бэке нет (есть только мастерский per-practice, розетка Phase 9) | Реализовать полноценный экран, когда появится бэк-эндпоинт юзерского AI-саммари |
| **TD-FE-AVATAR** | ✅ | `shared/MasterCard.vue`, `PracticeHeroCard.vue`, `MasterPublicView.vue` | Аватарки мастеров — плейсхолдер `IconMeditation` (нет поля с URL аватара) | ЗАКРЫТО (Calendar flow): бэк отдаёт `master_avatar_url`; фронт перешёл на `VAvatar` (фото по `url` или инициалы по `name`). MasterCard — lg, MasterPublicView hero — xl |
| **TD-FE-ICONSVG** | 🧪 | `src/components/icons/` | В каталоге доменных иконок остались сырые `.svg`-файлы рядом с `.vue`-компонентами (артефакт экспорта) | `git rm` сырых `.svg` (операция в рабочей копии) |
| **S-4** | 🧪 | `shared/MasterCard.vue` | Кнопка "Подробнее" (профиль мастера) кликабельна и показывает toast "скоро", хотя экрана профиля мастера для юзера ещё нет | Осознанно отложено: либо disabled-state, либо реальный экран профиля. Аудит 2026-05-20 предлагал disabled — решено оставить toast-заглушку до появления экрана |
| **TD-CAL-STYLE** | 🧪 | `shared/CalendarFilterModal.vue` | «Вид практики» (style) — свободный `VInput`, в Figma (кадр 2) задуман дропдаун. Справочника стилей пока нет, бэк принимает свободную строку (точное совпадение) | Заменить на дропдаун, когда появится каталог стилей практик |
| **TD-CAL-ARROW** | 🧪 | `shared/WeekStrip.vue`, `CalendarView.vue` | Стрелки недели и шеврон/воронка — inline SVG (в `components/icons` нет `IconChevron`/левой стрелки/воронки) | Завести `IconChevronLeft/Right`, `IconFilter` в DS и заменить inline SVG |
| **TD-ASK-MASTER** | 🧪 | `MasterPublicView.vue`, `BookingConfirmedView.vue`, и везде, где есть «вопрос мастеру» | Вопросы мастеру — сквозная фича: задаются из профиля мастера («в общем», без привязки к практике), ИЛИ до брони, ИЛИ после; улетают в Telegram-бот мастера, мастер отвечает юзеру тоже в бот. Требует серьёзного бэка. Сейчас ВСЕ кнопки/поля «вопрос мастеру» ЕСТЬ визуально, но ведут в toast-заглушку. Кадр 6 флоу отложен | Спроектировать и реализовать бэк (маршрутизация в бота, треды вопрос/ответ), затем подключить все точки входа |
| **TD-CAL-ICON-YOGA** | 🧪 | `components/icons/IconYoga.vue` | `IconYoga` — Claude-сгенерированный плейсхолдер | Заменить на ассет дизайнера (тот же filename/viewBox/`currentColor` → замена без правок кода) |
| **TD-DIARY-PRACTICE-AVATAR** | 🧪 | `shared/DiaryFeedCard.vue` (practice-форма), бэк `diary/projections.py` | В practice-карточке ленты убраны аватар мастера и verified-галочка: бэк не кладёт `master_avatar_url`/`master_verified` в `_practice_snapshot`. Карточка показывает имя мастера | Добавить эти поля в `_practice_snapshot` (бэк), затем вернуть аватар+галочку в карточку (слоты под них уже есть) |
| **TD-DIARY-TAP-VARIANT-B** | 🧪 | `views/user/DiaryFeedView.vue` (`onTap`) | Вариант A: тап по note/dream → toast «Функция временно недоступна», остальное no-op. Редактирования/удаления записи из ленты пока нет | Вариант B: тап по note/dream открывает редактор (bottom-sheet или экран) с правкой/удалением. Меняется только обработчик `onTap` во вью; карточки и нить не трогаются (`@tap` уже эмитит `{ item, editable }`) |
| **TD-DIARY-LIST-VIEW** | 🧪 | дневник | В MVP дневник = только нить (экран 40). Плоский список (экран 41) и переключатель list/map не сделаны | Добавить list-вид (плоский стек карточек, 1:1 с feed) и переключатель, когда понадобится |
| **TD-DIARY-FILTER-SEARCH** | 🧪 | `views/user/DiaryFeedView.vue` («...» меню), стор (`feedFilters`/`runFeedSearch` уже есть) | Фильтр по категориям + поиск + диапазон дат на бэке и в сторе готовы, но UI («...» меню → модалка фильтра/поиск) — заглушка-toast | Реализовать модалку фильтра/поиск на `VModal`, повесить на готовые `setFeedFilters`/`runFeedSearch` |
| **TD-DIARY-ORNAMENT** | 🧪 | `components/icons/IconDateLeaf.vue` | Орнамент дата-узлов нити — лёгкий рисованный (`IconDateLeaf`), не оригинальный Figma-SVG (тот — 2×31KB с масками). Аутентичные сохранены | Вернуть аутентичные орнаменты, если заказчик захочет «точь-в-точь макет» |
| **TD-CAL-DIRECTIONS-EXPAND** | 🧪 | `utils/displayHelpers.ts` (`DIRECTION_ICON`) | Бэк добавит направления (somatic/womens_circle/mens_circle/tantra/kundalini) | Иконки уже Partial+fallback — добавить новые иконки в `DIRECTION_ICON` по мере появления (рост списка код не ломает) |
| **TD-ZOOM-TEXT** | 🧪 | `views/user/BookingConfirmedView.vue` | Текст «Ссылка на Zoom придёт за 10 минут» статичен независимо от типа практики (аудит S-2, осознанно отложено — все практики сейчас через Zoom) | Сделать нейтральным («Детали подключения…») или условным по `practice.zoom_link`, когда появятся не-Zoom практики |
| **TD-PROFILE-SUPPORT** | 🧪 | раздел Профиль, экран G (node 76) | Экран «Поддержка» не реализован (отложен заказчиком). Пункт «Поддержка» на экране A — toast-заглушка. Единственный незакрытый экран раздела | Сверстать форму (Тема+Сообщение+Отправить) + тост; бэка нет (витрина) |
| **TD-PROFILE-LANG-I18N** | 🧪 | `LanguageTimezoneView.vue` | Переключатель языка — заглушка из одного пункта: i18n в проекте нет, выбор не сохраняется и интерфейс не меняется | Реализовать локализацию (vue-i18n), снять `isLanguageStatic`, добавить языки в `LANGUAGE_OPTIONS`, сохранять `user.language` |
| **TD-PROFILE-AVATAR-UPLOAD** | 🧪 | `EditProfileView.vue` | «Изменить фото» — toast-заглушка: инфраструктуры загрузки аватара нет (аватар приходит из Telegram `photo_url`) | Реализовать загрузку при появлении файлового бэка/хранилища |

> **Аудит итерации «Профиль» (2026-05-29):** закрыты W-2 (честный текст модала
> удаления в `EditProfileView` — поведение = сброс онбординга, данные сохраняются),
> S-1 (`bio.trimEnd()` перед сравнением/отправкой), S-2 (язык-строка `:disabled`
> + `cursor:default` при одном языке, авто-снимается при добавлении второго).
> W-1/W-4/S-5 — на бэке (Бэковый Кодекс §9). W-3/S-3 — осознанно не код.

### Осознанные решения (не техдолг)

| Решение | Обоснование |
|---------|-------------|
| API-типы генерируются из OpenAPI (CR-01) | Единый источник правды — Pydantic-схемы бэкенда. `generated.ts` создаётся автоматически при `velo update`. Drift невозможен конструктивно |
| `sessionStorage` для token (не `localStorage`) | Telegram WebApp закрывает вкладку — sessionStorage очищается автоматически |
| Свой CSS вместо Tailwind | Дизайн-система VELΘ готова в мокапах, перенос 1:1 проще |
| Внутренний Nginx в Docker фронтенда | SPA fallback + кеширование без усложнения хост-конфига |
| Telegram SDK через локальную копию (не npm) | CDN Telegram заблокирован ТСПУ; локальная копия гарантирует загрузку |
| `token` в module-level var в `client.ts`, не в Pinia | Исключает circular dependency `client → store → client` |
| `v-show` на payout-форме | Анимированное скрытие; `v-if` ломает CSS-переход |
| Auth guard в `App.vue` (Phase F1), не в router | В F1 один маршрут; guards добавлены в F2.2 |
| Фон через `body { background }` в `global.css`, не через `#app::before` | `#app::before` — статический CSS, Telegram WebApp кеширует и не обновляет. `global.css` импортируется в `main.ts` и попадает в JS-бандл, который обновляется при каждом деплое |
| SVG-логотипы через `<img>` (не inline) | Файлы из Figma-экспорта весят 228KB и 434KB — inline SVG раздует HTML. `<img>` позволяет браузеру кешировать отдельно (TD-FE-LOGO-SVGO покроет оптимизацию) |
| Один `PracticeDetailView` на каталог + booked (экран 15) | Состояния практики (доступна к брони / уже забронирована) различаются в одном вью. God-component-долг смягчён выносом hero/master в `PracticeHeroCard`/`MasterCard` |
| `MasterCard` "Подробнее" → toast вместо disabled (S-4) | ЗАКРЫТО (Calendar flow): экран профиля мастера для юзера реализован (`MasterPublicView`), `onMore()` теперь ведёт на `user-master-public` (с guard `if (!masterId)` → toast). Toast-заглушка убрана |
| Отдельный `useCalendarStore` (не общий `usePracticesStore`) | Навигация по неделям и фасет-фильтры Календаря не должны задевать общий фид. Дашборд использует `usePracticesStore`/`useBookingsStore` — изолирован |
| Календарь грузит неделю одним запросом + буфер ±1 день | Объём недели мал; маркеры/список дня выводятся клиентом по TZ практики. Буфер ±1д закрывает W-2 (практики экстремальных TZ у границы недели) |
| «Выбрать практики»: модалка — единственный источник фильтров (Вариант 1) | Inline-чипы лишь отображают/снимают активные фильтры; редактирование — в `CalendarFilterModal`. Не дублируем UI выбора, нет рассинхрона |

---

**Конец документа**
