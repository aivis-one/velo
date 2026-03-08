# VELO — Фронтовый Кодекс

**Версия:** 1.0
**Дата:** 8 марта 2026
**Статус:** Active

---

## 1. Архитектура

### 1.1. Одно SPA — три роли

Единое приложение с ролевым роутингом. Роль определяется из `GET /api/v1/users/me`
после авторизации. Каждая роль имеет свой Shell (layout-обёртку) и Tab Bar.

| Роль | Shell | Tab Bar |
|------|-------|---------|
| `user` | `UserShell` | 🏠 Дашборд / 📅 Календарь / 📔 Дневник / 👤 Я |
| `master` | `MasterShell` | 📊 Дашборд / 📅 Практики / 📈 Аналитика / 👤 Я |
| `admin` | `AdminShell` | 📊 Дашборд / 👥 Мастера / ⚠️ Модерация / 👤 Я |

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
  close(): void
}
```

MVP работает только в Telegram. Standalone — Phase F10.

### 1.3. Структура проекта

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts          -- Base fetch обёртка, 401 handler
│   │   ├── types.ts           -- TypeScript-интерфейсы (все типы API)
│   │   ├── utils.ts           -- buildQuery() и прочие shared helpers
│   │   ├── auth.ts            -- POST /auth/telegram, logout
│   │   ├── users.ts           -- GET/PATCH /users/me
│   │   ├── practices.ts       -- CRUD практик, finalize, attendance
│   │   ├── bookings.ts        -- Бронирования, purchase, waitlist
│   │   ├── payments.ts        -- Topup
│   │   ├── masters.ts         -- Apply, profile, payout, withdrawals
│   │   ├── diary.ts           -- Check-ins, feedbacks, entries, insights
│   │   └── admin.ts           -- Stats, verify, reports, consistency
│   │
│   ├── components/
│   │   ├── ui/                -- Примитивы (V-префикс)
│   │   ├── layout/            -- Shell-компоненты, VHeader, VTabBar
│   │   └── shared/            -- Доменные: PracticeCard, BookingCard...
│   │
│   ├── composables/
│   │   ├── useAuth.ts         -- Login/logout flow + waitUntilReady()
│   │   ├── usePagination.ts   -- Пагинация + infinite scroll
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
│   │   ├── bookings.ts        -- my bookings
│   │   ├── balance.ts         -- balance_cents, operations
│   │   ├── master.ts          -- master profile, practices, finance
│   │   └── diary.ts           -- checkins, feedbacks, entries, insights cache
│   │
│   ├── styles/
│   │   ├── variables.css      -- Дизайн-токены (единственный источник цветов)
│   │   └── global.css         -- Reset, typography, Google Fonts
│   │
│   ├── utils/
│   │   ├── format.ts          -- formatMoney, formatDate, formatDateShort
│   │   ├── currency.ts        -- eurStringToCents, centsToEurString
│   │   ├── displayHelpers.ts  -- MOOD_*/RATING_*/PRACTICE_TYPE_* маппинги
│   │   ├── adminHelpers.ts    -- Хелперы форматирования для admin-вью
│   │   ├── commission.ts      -- COMMISSION_RATE константа
│   │   └── practiceOptions.ts -- DURATION_OPTIONS, TIMEZONE_OPTIONS
│   │
│   └── views/
│       ├── auth/              -- LoginView, LoadingView, StandaloneStubView
│       ├── shells/            -- UserShell, MasterShell, AdminShell
│       ├── user/              -- Dashboard, Calendar, Diary, Profile...
│       ├── master/            -- Dashboard, Practices, Analytics, Profile...
│       └── admin/             -- Dashboard, Masters, Reports, Consistency...
│
├── public/
│   ├── js/telegram-web-app.js -- Локальная копия Telegram SDK (CDN заблокирован ТСПУ)
│   ├── icons/                 -- PWA иконки
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
/user/diary                 → DiaryView
/user/profile               → UserProfileView
/user/practices/:id         → PracticeDetailView
/user/bookings              → MyBookingsView
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

---

## 3. Компоненты

### 3.1. UI-примитивы (src/components/ui/)

| Компонент | Ключевые пропсы |
|-----------|----------------|
| `VButton` | `variant` (primary/secondary/outline/danger), `size`, `disabled`, `loading`, `block` |
| `VInput` | `label`, `placeholder`, `error`, `type` |
| `VTextarea` | `label`, `placeholder`, `error`, `rows` |
| `VSelect` | `label`, `options`, `error` |
| `VCheckbox` | `label`, `checked` |
| `VCard` | slot |
| `VBadge` | `variant` (success/warning/error/info), `text` |
| `VAvatar` | `name`, `url`, `size` |
| `VLoader` | `size` |
| `VDivider` | — |
| `VEmptyState` | `icon`, `title`, `description` |
| `VToast` | composable `useToast()` |
| `VStatCard` | `value`, `label`, `icon` |
| `VProgressBar` | `value`, `max`, `color` |
| `VModal` | `open`, `closeOnOverlay`, `showClose` |
| `VeloLogo` | SVG-логотип (единственный источник) |

### 3.2. Layout-компоненты (src/components/layout/)

| Компонент | Описание |
|-----------|----------|
| `VHeader` | Заголовок с кнопкой назад и action-слотом справа |
| `VTabBar` | Нижняя навигация, конфигурируется через `items` пропс |
| `MobileLayout` | Header-слот + `<slot>` + VTabBar (user и master) |
| `AdminLayout` | Аналогично, отдельный для будущего desktop-варианта |

### 3.3. Shared-компоненты (src/components/shared/)

`PracticeCard`, `BookingCard`, `BookingPopup`, `CancelBookingPopup` и прочие доменные компоненты.

---

## 4. Stores (Pinia)

| Store | Ключевые поля |
|-------|--------------|
| `auth` | `user`, `token` (module-level var в client.ts), `role`, `isAuthenticated` |
| `practices` | `practices[]`, `total`, `filters`, `loading` |
| `bookings` | `bookings[]`, `total`, `loading` |
| `balance` | `balance_cents`, `operations[]` |
| `master` | `profile` (MasterProfile), `practices[]`, `withdrawals[]` |
| `diary` | `checkins[]`, `feedbacks[]`, `entries[]`, `insightsCache` |

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

### FP-09: Ручная типизация API, не OpenAPI codegen

Контроль, идиоматичность, проще поддерживать при изменении бэкенда.

---

## 7. Дизайн-система

Токены в `src/styles/variables.css`. Перенесены 1:1 из `velo-mockups/css/variables.css`.

Основные группы:

```css
--velo-primary, --velo-primary-light, --velo-primary-dark
--velo-bg-start, --velo-bg-end, --velo-bg-card, --velo-bg-subtle
--velo-text-primary, --velo-text-secondary, --velo-text-muted
--velo-border, --velo-border-light
--velo-success, --velo-warning, --velo-error, --velo-info
--velo-success-bg-subtle, --velo-warning-bg-subtle,
--velo-error-bg-subtle, --velo-info-bg-subtle   (семантические tints для admin-баннеров)
--velo-error-text, --velo-warning-text, ...
```

Шрифты: Inter (body) + Playfair Display (heading) — Google Fonts через `<link>` в `index.html` (не `@import` — устраняет FOIT).

---

## 8. Phase F9 (не начата — разблокирована)

Бэкенд Phase 8 завершён. F9 можно начинать.

### F9.1: Check-in + Feedback

**Файлы для создания/изменения:**
- `src/views/user/CheckinView.vue` — экран check-in: mood (low/mid/high), опциональный комментарий, `POST /api/v1/practices/:id/checkin`
- `src/views/user/FeedbackView.vue` — экран feedback: rating (fire/good/confused), опциональный комментарий, `POST /api/v1/practices/:id/feedback`
- `src/views/user/UserDashboardView.vue` — баннеры: "Как вы себя чувствуете?" (за N часов до) и "Как прошла практика?" (после)
- `src/router/index.ts` — маршруты `/user/checkin/:practiceId`, `/user/feedback/:practiceId` (уже добавлены)
- `src/stores/diary.ts` — стор (уже создан в F9)
- `src/api/diary.ts` — методы API (уже создан)

### F9.2: Дневник

**Файлы:**
- `src/views/user/DiaryView.vue` — 4 таба: Все / Check-ins / Feedbacks / Записи
- CRUD записей через `GET/POST/PATCH/DELETE /api/v1/diary`

### F9.3: Аналитика мастера

**Файлы:**
- `src/views/master/AnalyticsView.vue` — `GET /api/v1/practices/:id/insights`
- Прогресс-бары: распределение mood (high/mid/low) и rating (fire/good/confused)
- Цвета через `MOOD_COLOR` и `RATING_COLOR` из `displayHelpers.ts`

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
| **NEW-2** | 🧪 | `DiaryView.vue` | Локальная `formatShortDate` (month: `'long'`) конфликтует с одноимённой из `displayHelpers.ts` (month: `'short'`) | Переименовать локальную в `formatLongDate` |
| **NEW-3** | 🧪 | `DiaryView.vue` | Монолит ~1000 строк с 6 internal views через ручной state machine. Невозможно тестировать sub-view изолированно | Декомпозиция: `DiaryList.vue`, `DiaryEntryForm.vue`, `DiaryCheckinDetail.vue`, `DiaryFeedbackDetail.vue` |
| **NEW-4** | 🧪 | `DiaryView.vue` | `onMounted` запускает `Promise.all` без `.catch()` — ошибки уходят в unhandled rejection | `onMounted(async () => { try { await Promise.all([...]) } catch(e) { toast.error(...) } })` |
| **NEW-5** | 🧪 | `CheckinView.vue`, `FeedbackView.vue`, `DiaryView.vue` | `background: white` хардкод — сломается при добавлении dark mode | Заменить на `var(--velo-bg-card)` |
| **NEW-6** | 🧪 | `stores/diary.ts` | `insightsCache` (Map) растёт бесконечно — утечка памяти при большом числе практик | LRU-ограничение (50-100 записей) |
| **WARNING-1** | 🧪 | `stores/*.ts` | Каждый store реализует свой паттерн try/catch — 7+ дублей одинаковой структуры | Единый composable `useApiError.ts` |
| **WARNING-3** | 🧪 | `composables/useAuth.ts` | `waitUntilReady()` при таймауте резолвится без ошибки — код дальше думает что auth готов | Возвращать `{ ok: boolean, timedOut: boolean }` |
| **WARNING-8** | 🧪 | `CheckinView.vue`, `FeedbackView.vue` | `fetchPractice()` вызывается всегда в `onMounted`, даже если practice уже в store | `if (store.selected?.id !== practiceId)` перед fetch |
| **WARNING-9** | 🧪 | `CheckinView.vue`, `FeedbackView.vue` | ~200 строк идентичного CSS (header, textarea, actions, success screen) | Извлечь `FormShell.vue` с слотами |
| **WARNING-10** | 🧪 | Стили | Magic numbers: `font-size: 80px`, `56px`, `min-width: 90px` без CSS-токенов | Добавить токены в `variables.css` |
| **WARNING-11** | 🧪 | Компоненты | `platform.hapticFeedback()` без fallback — silent crash если platform не инициализирован | try/catch вокруг вызовов haptic |
| **WARNING-12** | 🧪 | `tests/` | 2 тест-файла при значительной бизнес-логике F9 (DiaryStore, time window, alert banners, guards) | Покрыть: DiaryStore CRUD, `inCheckinWindow`, `inFeedbackWindow`, `checkinAlert`, router guards |
| **WARNING-13** | 🧪 | `api/client.ts`, `composables/useAuth.ts` | Module-level mutable state (`_token`, `isReady`) не сбрасывается между тестами | Явный `reset()` или DI через параметры |

### Фронтенд — открытые

| ID | Среда | Файл | Описание | Решение |
|----|-------|------|----------|---------|
| TD-SDK | 🧪 | `public/js/telegram-web-app.js` | SDK — локальная копия (3331 строка). Ручное обновление при новых версиях | Миграция на `@telegram-apps/sdk` (npm) |
| TD-FE-W4 | 🧪 | `MasterProfileView.vue` | `v-show` на payout-форме — весь DOM всегда присутствует | Заменить на `v-if` если форма не нужна при анимированном переходе |
| TD-FE-W6 | 🧪 | `MasterFinanceView.vue` | `MIN_WITHDRAWAL_EUROS=50` и `WITHDRAWAL_FEE_EUROS=2` захардкожены — рассинхрон с `config.py` при изменении | `GET /api/v1/config` эндпоинт или явный комментарий с источником |
| TD-FE-A11Y | 🧪 | Admin views (5 файлов) | Clickable `<div>` без `role="button"`, `tabindex="0"`, `@keydown` handlers. Нарушает WCAG 2.1 AA 2.1.1. Затронуто: алертовый баннер, stat cards, action cards, master cards, report cards | Добавить `role="button"`, `tabindex="0"`, `@keydown.enter.stop`, `@keydown.space.prevent` |

### Осознанные решения (не техдолг)

| Решение | Обоснование |
|---------|-------------|
| Ручная типизация API вместо OpenAPI codegen | Контроль, идиоматичность, проще при изменении бэкенда |
| `sessionStorage` для token (не `localStorage`) | Telegram WebApp закрывает вкладку — sessionStorage очищается автоматически |
| Свой CSS вместо Tailwind | Дизайн-система готова в мокапах, перенос 1:1 проще |
| Внутренний Nginx в Docker фронтенда | SPA fallback + кеширование без усложнения хост-конфига |
| Telegram SDK через локальную копию (не npm) | CDN Telegram заблокирован ТСПУ; локальная копия гарантирует загрузку |
| `token` в module-level var в `client.ts`, не в Pinia | Исключает circular dependency `client → store → client` |
| `v-show` на payout-форме | Анимированное скрытие; `v-if` ломает CSS-переход |
| Auth guard в `App.vue` (Phase F1), не в router | В F1 один маршрут; guards добавлены в F2.2 |

---

**Конец документа**
