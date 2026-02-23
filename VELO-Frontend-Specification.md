# VELO — Техническое задание: Frontend

**Версия:** 1.0
**Дата:** 22 февраля 2026
**Статус:** Draft

---

## 1. Обзор

### 1.1. Цель

Фронтенд VELO — единое SPA-приложение с ролевым роутингом, работающее в двух режимах:

1. **Telegram WebApp** — основной канал MVP. Открывается внутри Telegram, авторизация через initData
2. **Standalone PWA** — будущий режим. Устанавливается на Home Screen, авторизация через email/OAuth

Оба режима используют один и тот же код. Различия инкапсулированы в платформенной абстракции.

### 1.2. Критерии готовности MVP (Frontend)

| Критерий | Описание |
|----------|----------|
| Auth | Telegram WebApp авторизация работает |
| Каталог | Юзер видит практики, может фильтровать |
| Бронирование | Юзер записывается и отменяет запись |
| Баланс | Пополнение через Stripe, отображение баланса |
| Master CRUD | Мастер создаёт, редактирует, финализирует практики |
| Admin | Верификация мастеров, статистика, модерация |
| PWA | Приложение добавляется на Home Screen |

### 1.3. Вне scope MVP (Frontend)

- Standalone-авторизация (email/OAuth) — только Telegram WebApp
- Офлайн-режим (кроме заглушки "Нет подключения")
- Push-уведомления через Service Worker
- Тёмная тема (пока только светлая)
- Локализация (только русский)
- Анимации переходов между экранами

### 1.4. Три роли — одно приложение

Приложение определяет роль из `GET /api/v1/users/me` и показывает соответствующий интерфейс:

| Роль | Tab Bar | Доступ |
|------|---------|--------|
| user | Дашборд, Календарь, Дневник, Профиль | Каталог, бронирования, баланс |
| master | Дашборд, Практики, Аналитика, Профиль | Всё user + управление практиками, финансы мастера |
| admin | Дашборд, Мастера, Модерация | Верификация, статистика, семафоры, жалобы |

Master видит свои user-экраны + мастер-экраны. Переключение через профиль (не отдельное приложение).

---

## 2. Технологический стек

| Компонент | Технология | Версия | Назначение |
|-----------|-----------|--------|------------|
| Фреймворк | Vue 3 | latest | Composition API, SFC |
| Язык | TypeScript | 5.x | Строгая типизация |
| Сборка | Vite | latest | HMR, быстрая сборка |
| Роутинг | Vue Router | 4.x | Role-based guards |
| Стейт | Pinia | latest | Реактивные хранилища |
| HTTP | Fetch (обёртка) | native | Запросы к API |
| PWA | vite-plugin-pwa | latest | Manifest + Service Worker |
| Стили | Свой CSS | — | Дизайн-система из мокапов |
| Линтинг | ESLint + Prettier | latest | Качество кода |
| Платформа | Telegram WebApp SDK | latest | initData, тема, haptic |

### 2.1. Почему Vue 3

- Синтаксис ближе к HTML — интуитивен для бэкенд-разработчиков
- Однофайловые компоненты (.vue) — шаблон, логика, стили в одном файле
- Composition API — композиция логики без class-based паттернов
- Лучшая документация среди SPA-фреймворков
- Достаточная экосистема для MVP и масштабирования

### 2.2. Почему не React / Svelte

- **React:** JSX контринтуитивен для новичков, больше "магии" (хуки, ре-рендеры), для MVP разница несущественна
- **Svelte:** Маленькое коммьюнити, меньше примеров для Telegram WebApp

---

## 3. Архитектура

### 3.1. Структура проекта

```
velo/                              ← GitHub repo root (уже существует)
├── backend/                       ← Бэкенд (существует)
├── frontend/                      ← Фронтенд (новый)
│   ├── src/
│   │   ├── api/                   ← HTTP-клиент + типизированные методы
│   │   │   ├── client.ts          ← Base fetch обёртка, interceptors
│   │   │   ├── types.ts           ← TypeScript-интерфейсы (из OpenAPI)
│   │   │   ├── auth.ts            ← POST /auth/telegram, logout
│   │   │   ├── users.ts           ← GET/PATCH /users/me
│   │   │   ├── practices.ts       ← CRUD практик
│   │   │   ├── bookings.ts        ← Бронирования
│   │   │   ├── payments.ts        ← Topup, purchases, withdrawals
│   │   │   ├── masters.ts         ← Apply, profile, payout
│   │   │   └── admin.ts           ← Stats, verify, reports, consistency
│   │   │
│   │   ├── components/            ← Переиспользуемые UI-компоненты
│   │   │   ├── ui/                ← Примитивы: VButton, VInput, VCard...
│   │   │   ├── layout/            ← VHeader, VTabBar, MobileLayout...
│   │   │   └── shared/            ← PracticeCard, BookingCard, BalanceDisplay...
│   │   │
│   │   ├── views/                 ← Экраны (по ролям)
│   │   │   ├── auth/              ← LoginView, LoadingView
│   │   │   ├── user/              ← Dashboard, Calendar, Practice, Bookings...
│   │   │   ├── master/            ← Dashboard, Practices, Analytics, Apply...
│   │   │   └── admin/             ← Dashboard, Masters, Reports, Consistency...
│   │   │
│   │   ├── stores/                ← Pinia хранилища
│   │   │   ├── auth.ts            ← user, token, role, isAuthenticated
│   │   │   ├── practices.ts       ← list, filters, selected
│   │   │   ├── bookings.ts        ← my bookings
│   │   │   ├── balance.ts         ← balance_cents, operations
│   │   │   └── master.ts          ← master profile, practices, finance
│   │   │
│   │   ├── router/                ← Vue Router
│   │   │   ├── index.ts           ← Маршруты + guards
│   │   │   └── guards.ts          ← Auth guard, role guard
│   │   │
│   │   ├── platform/              ← Абстракция Telegram / Standalone
│   │   │   ├── index.ts           ← Автодетект среды, экспорт
│   │   │   ├── telegram.ts        ← Реальный Telegram WebApp SDK
│   │   │   ├── standalone.ts      ← Заглушки для браузера
│   │   │   └── types.ts           ← Общий интерфейс Platform
│   │   │
│   │   ├── composables/           ← Vue composables (переиспользуемая логика)
│   │   │   ├── useAuth.ts         ← Login/logout flow
│   │   │   ├── usePagination.ts   ← Пагинация + infinite scroll
│   │   │   ├── useToast.ts        ← Всплывающие уведомления
│   │   │   └── useForm.ts         ← Валидация форм
│   │   │
│   │   ├── styles/                ← Глобальные стили
│   │   │   ├── variables.css      ← Дизайн-токены (из мокапов)
│   │   │   ├── components.css     ← Базовые стили компонентов
│   │   │   ├── global.css         ← Reset, typography, utilities
│   │   │   └── telegram.css       ← Telegram-specific overrides
│   │   │
│   │   ├── utils/                 ← Утилиты
│   │   │   ├── format.ts          ← Форматирование дат, валют, чисел
│   │   │   ├── validation.ts      ← Общие валидаторы форм
│   │   │   └── constants.ts       ← Статусы, роли, магические числа
│   │   │
│   │   ├── App.vue                ← Корневой компонент
│   │   └── main.ts                ← Точка входа: createApp, router, pinia
│   │
│   ├── public/
│   │   ├── manifest.json          ← PWA-манифест
│   │   ├── sw.js                  ← Service Worker (через vite-plugin-pwa)
│   │   └── icons/                 ← Иконки приложения (192, 512)
│   │
│   ├── index.html                 ← SPA entry point
│   ├── vite.config.ts             ← Vite + PWA plugin config
│   ├── tsconfig.json              ← TypeScript config
│   ├── eslint.config.js           ← ESLint flat config
│   ├── .prettierrc                ← Prettier config
│   ├── package.json               ← Dependencies
│   ├── .env.example               ← VITE_API_BASE_URL=...
│   ├── .gitignore                 ← node_modules, dist
│   ├── Dockerfile                 ← Multi-stage: node build → nginx
│   └── README.md                  ← Инструкция
│
├── velo-mockups/                  ← UI-прототипы (существуют)
├── VELO-Technical-Specification.md
├── VELO-Frontend-Specification.md ← ЭТОТ ДОКУМЕНТ
└── ...
```

### 3.2. Интеграция с бэкендом

```
Browser / Telegram
      │
      ▼
   Nginx (api.talentir.info)
      │
      ├── /*         → static files → frontend/dist/
      ├── /api/*     → proxy_pass   → Docker (FastAPI :8000)
      └── /health    → proxy_pass   → Docker (FastAPI :8000)
```

Фронтенд и бэкенд на одном домене — CORS не нужен.

При переезде на продакшн-сервер заказчика:
- Новый домен в .env (VITE_API_BASE_URL)
- Nginx: app.domain.com → фронтенд, api.domain.com → бэкенд
- Код не меняется

### 3.3. Платформенная абстракция

```typescript
// src/platform/types.ts
interface Platform {
  name: 'telegram' | 'standalone'
  init(): Promise<void>
  getInitData(): string | null         // Telegram initData или null
  getTheme(): 'light' | 'dark'
  hapticFeedback(type: string): void
  showBackButton(cb: () => void): void
  hideBackButton(): void
  close(): void
}
```

Telegram WebApp обнаруживается по наличию `window.Telegram?.WebApp`. Если нет — standalone-режим.

### 3.4. Соглашения

**Именование файлов:**
- Компоненты: PascalCase (`PracticeCard.vue`, `VButton.vue`)
- Утилиты, stores, api: camelCase (`auth.ts`, `usePagination.ts`)
- Стили: kebab-case (`variables.css`, `global.css`)

**Префикс V для UI-примитивов:**
- `VButton`, `VInput`, `VCard` — собственные компоненты дизайн-системы
- Без префикса — доменные компоненты (`PracticeCard`, `BookingList`)

**Комментарии:** на английском (как в бэкенде).

---

## 4. Фазы разработки

---

## PHASE F0: Инфраструктура

### F0.1: Инициализация проекта

**Цель:** Проект собирается, деплоится на VPS, пустая страница открывается.

**Задачи:**
- [ ] `npm create vue@latest` с TypeScript, Vue Router, Pinia
- [ ] Структура папок (src/api, components, views, stores, router, platform, styles, composables, utils)
- [ ] ESLint flat config + Prettier (единый стиль кода)
- [ ] tsconfig.json — strict mode, path aliases (`@/` → `src/`)
- [ ] vite.config.ts — base path, proxy для dev, env переменные
- [ ] .env.example (`VITE_API_BASE_URL=https://api.talentir.info`)
- [ ] .gitignore (node_modules, dist, .env)
- [ ] README.md (команды: install, dev, build, lint)

**Результат:**
```
frontend/
├── src/
│   ├── App.vue            ← <div>VELO</div>
│   └── main.ts            ← createApp + router + pinia
├── index.html
├── vite.config.ts
├── tsconfig.json
├── eslint.config.js
├── .prettierrc
├── package.json
├── .env.example
├── .gitignore
└── README.md
```

**Критерий готовности:** `npm run build` проходит, `npm run lint` без ошибок.

---

### F0.2: Дизайн-система (перенос из мокапов)

**Цель:** CSS-переменные и базовые стили из мокапов перенесены в проект.

**Задачи:**
- [ ] src/styles/variables.css — дизайн-токены из velo-mockups/css/variables.css
- [ ] src/styles/global.css — reset, typography, базовые утилиты
- [ ] src/styles/components.css — базовые стили (будут постепенно мигрировать в .vue)
- [ ] main.ts — импорт стилей
- [ ] Проверка: элементы выглядят идентично мокапам

**Зависимость от мокапов:** velo-mockups/css/variables.css, velo-mockups/css/components.css

**Критерий готовности:** Страница с примерами компонентов (кнопки, карточки, инпуты) визуально совпадает с мокапами.

---

### F0.3: Docker + деплой на VPS

**Цель:** Фронтенд деплоится через `velo update`, доступен по HTTPS.

**Задачи:**
- [ ] frontend/Dockerfile (multi-stage: node:22 build → nginx:alpine static)
- [ ] docker-compose.yml — новый сервис `frontend` (порт 3000 внутренний)
- [ ] Nginx-конфиг: /* → frontend:3000, /api/* → app:8000
- [ ] SPA fallback: все несуществующие пути → index.html (для Vue Router history mode)
- [ ] `velo update` — git pull + rebuild frontend + rebuild backend + migrate + test + restart
- [ ] HTTPS уже работает (certbot настроен на VPS)

**Dockerfile:**
```dockerfile
# Stage 1: Build
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
```

**Решения:**
- Фронтенд в отдельном контейнере (не в бэкенд-контейнере) — изоляция, независимый rebuild
- Внутренний Nginx в контейнере фронтенда — отдаёт статику + SPA fallback
- Внешний Nginx на хосте — SSL termination + маршрутизация между сервисами

**Критерий готовности:** `curl https://api.talentir.info/` → HTML-страница с "VELO".

---

### F0.4: PWA-заготовка

**Цель:** Приложение можно добавить на Home Screen.

**Задачи:**
- [ ] vite-plugin-pwa в vite.config.ts
- [ ] public/manifest.json (name, short_name, icons, theme_color, display: standalone)
- [ ] Иконки: 192x192, 512x512 (placeholder, заменим на брендинг заказчика)
- [ ] Service Worker: precache статики (только кеширование, без офлайна)
- [ ] meta-теги в index.html (apple-mobile-web-app-capable, viewport)

**Критерий готовности:** iPhone Safari → "Добавить на экран" → приложение открывается в standalone-режиме (без адресной строки).

---

## PHASE F1: Auth + Платформа

### F1.1: Платформенная абстракция

**Цель:** Приложение знает, где запущено, и адаптируется.

**Задачи:**
- [ ] src/platform/types.ts — интерфейс Platform
- [ ] src/platform/telegram.ts — обёртка над `window.Telegram.WebApp`:
  - `init()` — вызов `WebApp.ready()`, expand, задание цвета
  - `getInitData()` — `WebApp.initData`
  - `getTheme()` — `WebApp.colorScheme`
  - `hapticFeedback()` — `WebApp.HapticFeedback.impactOccurred()`
  - `showBackButton() / hideBackButton()` — `WebApp.BackButton`
  - `close()` — `WebApp.close()`
- [ ] src/platform/standalone.ts — заглушки:
  - `getInitData()` → `null`
  - `getTheme()` → `'light'`
  - `hapticFeedback()` → no-op
  - Кнопка назад → Vue Router `router.back()`
- [ ] src/platform/index.ts — автодетект: `window.Telegram?.WebApp` → telegram, иначе → standalone
- [ ] Тип в index.html: подключение Telegram WebApp SDK через `<script src="https://telegram.org/js/telegram-web-app.js">`

**Решение:** SDK подключается через `<script>` в index.html (не через npm — Telegram рекомендует CDN для актуальной версии).

**Критерий готовности:** `platform.name === 'telegram'` в Telegram, `platform.name === 'standalone'` в браузере.

---

### F1.2: API-клиент

**Цель:** Типизированный HTTP-клиент для общения с бэкендом.

**Задачи:**
- [ ] src/api/client.ts:
  - `BASE_URL` из `import.meta.env.VITE_API_BASE_URL`
  - Обёртка над fetch: `get<T>()`, `post<T>()`, `patch<T>()`, `delete()`
  - Авто-подстановка `Authorization: Bearer {token}` из auth store
  - Обработка 401 → разлогин + редирект
  - Обработка 422 → парсинг Pydantic ValidationError
  - Обработка сетевых ошибок → toast "Нет подключения"
- [ ] src/api/types.ts — TypeScript-интерфейсы, соответствующие Pydantic-схемам бэкенда:
  - `UserResponse`, `UserUpdate`
  - `AuthResponse`, `TelegramAuthRequest`
  - `PracticeResponse`, `PaginatedPracticesResponse`
  - `BookingResponse`, `PaginatedBookingsResponse`
  - `PurchaseResponse`
  - и т.д. (заполняется по мере реализации фаз)

**Решение:** Ручная типизация (не автогенерация из OpenAPI). Причина: контроль над типами, проще поддерживать, OpenAPI-генераторы для Vue/TS часто генерируют неидиоматичный код.

**Критерий готовности:** `api.get<UserResponse>('/api/v1/users/me')` возвращает типизированный ответ.

---

### F1.3: Auth flow (Telegram)

**Цель:** Юзер открывает WebApp → автоматически авторизован.

**Задачи:**
- [ ] src/stores/auth.ts (Pinia):
  - `user: UserResponse | null`
  - `token: string | null`
  - `isAuthenticated: boolean` (computed)
  - `role: string` (computed из user.role)
  - `login()` — POST /auth/telegram с initData
  - `logout()` — POST /auth/logout + очистка store
  - `fetchMe()` — GET /users/me (обновление профиля)
  - Персистенция token в `sessionStorage` (для page reload в Telegram)
- [ ] src/composables/useAuth.ts — объединяет platform.getInitData() + auth store:
  - Telegram: автоматический login при mount
  - Standalone: показ заглушки "Откройте через Telegram"
- [ ] src/views/auth/LoadingView.vue — экран загрузки (логотип + спиннер)
- [ ] src/views/auth/StandaloneStubView.vue — "Войдите через Telegram" (заглушка для Phase F10)
- [ ] src/router/guards.ts — `beforeEach`: не авторизован → LoadingView → login → redirect

**Зависимость от бэкенда:** POST /api/v1/auth/telegram (Phase 1.2 ✅).

**Критерий готовности:** Открываем WebApp в Telegram → автоматический логин → видим user в DevTools.

---

## PHASE F2: Компоненты + Layout

### F2.1: UI-компоненты (дизайн-система)

**Цель:** Библиотека переиспользуемых компонентов из мокапов.

**Задачи:**
- [ ] Компоненты из мокапов (1:1 перенос визуала):

**Примитивы (src/components/ui/):**

| Компонент | Пропсы | Описание |
|-----------|--------|----------|
| VButton | variant (primary/secondary/outline/danger), size, disabled, loading | Кнопка с состояниями |
| VInput | label, placeholder, error, type | Текстовое поле |
| VTextarea | label, placeholder, error, rows | Многострочное поле |
| VSelect | label, options, error | Выпадающий список |
| VCheckbox | label, checked | Чекбокс |
| VCard | — (slot) | Карточка-контейнер |
| VBadge | variant (success/warning/error/info), text | Статусный бейдж |
| VAvatar | name, url, size | Аватар (инициалы или фото) |
| VLoader | size | Спиннер загрузки |
| VDivider | — | Горизонтальный разделитель |
| VEmptyState | icon, title, description | Пустое состояние |
| VToast | — (composable) | Всплывающее уведомление |
| VStatCard | value, label, icon | Числовая карточка статистики |
| VProgressBar | value, max, color | Полоска прогресса |

**Layout-компоненты (src/components/layout/):**

| Компонент | Описание |
|-----------|----------|
| VHeader | Заголовок с кнопкой назад и действием справа |
| VTabBar | Нижняя навигация (конфигурируется через пропсы) |
| MobileLayout | Header + `<slot>` + TabBar (для user и master) |
| AdminLayout | Аналогичный, с другим TabBar |

**Критерий готовности:** Страница-каталог компонентов (Storybook не нужен — просто /dev/components route) показывает все элементы.

---

### F2.2: Роутинг + Layout

**Цель:** Навигация между экранами, role-based доступ.

**Задачи:**
- [ ] src/router/index.ts — маршруты:

```
/                          → редирект на /user/dashboard (или /master/ или /admin/)
/loading                   → LoadingView (авторизация в процессе)

/user/dashboard            → UserDashboardView
/user/calendar             → CalendarView
/user/diary                → DiaryView (Phase F9)
/user/profile              → UserProfileView
/user/practices/:id        → PracticeDetailView
/user/bookings             → MyBookingsView
/user/topup                → TopupView
/user/topup/success        → TopupSuccessView
/user/topup/cancel         → TopupCancelView

/master/dashboard          → MasterDashboardView
/master/practices          → MasterPracticesView
/master/practices/new      → CreatePracticeView
/master/practices/:id      → EditPracticeView
/master/practices/:id/attendance → AttendanceView
/master/analytics          → AnalyticsView (Phase F9)
/master/profile            → MasterProfileView
/master/finance            → MasterFinanceView
/master/apply              → MasterApplyView (3 шага)
/master/pending            → MasterPendingView (ожидание верификации)

/admin/dashboard           → AdminDashboardView
/admin/masters             → AdminMastersView
/admin/masters/:id         → AdminMasterReviewView
/admin/reports             → AdminReportsView
/admin/reports/:id         → AdminReportDetailView
/admin/consistency         → AdminConsistencyView

/404                       → NotFoundView
```

- [ ] src/router/guards.ts:
  - `authGuard` — не авторизован → /loading
  - `roleGuard('master')` — role не master/admin → /user/dashboard
  - `roleGuard('admin')` — role не admin → /user/dashboard
  - `masterStatusGuard` — мастер не верифицирован → /master/pending

- [ ] Tab bar конфигурация по ролям:

| Роль | Таб 1 | Таб 2 | Таб 3 | Таб 4 |
|------|-------|-------|-------|-------|
| user | 🏠 Дашборд | 📅 Календарь | 📔 Дневник | 👤 Профиль |
| master | 📊 Дашборд | 📅 Практики | 📈 Аналитика | 👤 Профиль |
| admin | 📊 Дашборд | 👥 Мастера | ⚠️ Модерация | — |

- [ ] Пустые View-заглушки для всех маршрутов (заполняются в следующих фазах)

**Зависимость от бэкенда:** GET /api/v1/users/me (role) — Phase 1.4 ✅.

**Критерий готовности:** После логина юзер видит layout с tab bar. Переходы между пустыми экранами работают. Переключение role через прямое изменение в базе → разный tab bar.

---

## PHASE F3: Каталог практик

### F3.1: Список практик

**Цель:** Юзер видит доступные практики.

**Задачи:**
- [ ] src/stores/practices.ts (Pinia):
  - `practices: PracticeResponse[]`
  - `total: number`
  - `filters: { date_from, date_to, type, sort_by }`
  - `loading: boolean`
  - `fetchPractices()` — GET /api/v1/practices с фильтрами и пагинацией
- [ ] src/api/practices.ts — типизированные методы API
- [ ] src/components/shared/PracticeCard.vue:
  - Карточка практики (из мокапов): иконка типа, название, мастер, дата/время, цена, кол-во мест
  - Бейдж статуса (scheduled, live)
  - Клик → /user/practices/:id
- [ ] src/views/user/DashboardView.vue:
  - Приветствие с именем
  - "Ближайшие практики" — горизонтальный скролл или список
  - "Все практики" → ссылка на календарь
- [ ] src/views/user/CalendarView.vue:
  - Вид по дням (список, не сетка — проще для MVP)
  - Фильтры: тип практики, диапазон дат
  - Бесконечный скролл (или кнопка "Показать ещё")
- [ ] src/composables/usePagination.ts — переиспользуемая пагинация

**Зависимость от бэкенда:** GET /api/v1/practices (Phase 4.3 ✅).

**Критерий готовности:** Юзер видит список практик, фильтрует по типу и дате.

---

### F3.2: Детали практики

**Цель:** Экран конкретной практики с полной информацией.

**Задачи:**
- [ ] src/views/user/PracticeDetailView.vue:
  - Заголовок, описание, мастер (имя, аватар)
  - Дата, время, длительность, timezone
  - Тип практики
  - Цена (или "Бесплатно")
  - Кол-во мест (свободно / всего)
  - Кнопка "Записаться" (или "Вы записаны" / "Мест нет")
  - Ссылка на waitlist, если мест нет (Phase F4)
- [ ] src/api/practices.ts — `getPractice(id)`: GET /api/v1/practices/:id

**Зависимость от бэкенда:** GET /api/v1/practices/:id (Phase 4.3 ✅).

**Критерий готовности:** Клик по карточке → полная информация о практике.

---

## PHASE F4: Бронирование + Баланс

### F4.1: Бронирование

**Цель:** Юзер записывается на практику.

**Задачи:**
- [ ] Кнопка "Записаться" на PracticeDetailView:
  - POST /api/v1/practices/:id/purchase
  - Обработка ошибок: недостаточно средств (→ предложить пополнить), полная, уже записан
  - Success toast: "Вы записаны!"
- [ ] Промокод (опционально):
  - Поле ввода на экране практики
  - POST /api/v1/practices/:id/purchase/preview — показ скидки
  - Применение при бронировании
- [ ] src/stores/bookings.ts (Pinia):
  - `bookings: BookingWithPracticeResponse[]`
  - `total: number`
  - `fetchMyBookings()` — GET /api/v1/bookings/me
- [ ] src/views/user/MyBookingsView.vue:
  - Список бронирований с фильтром по статусу (confirmed, cancelled, attended)
  - BookingCard: практика, статус, дата, кнопка отмены
- [ ] src/components/shared/BookingCard.vue:
  - Карточка бронирования (из мокапов)
  - Бейдж статуса, мини-инфо о практике
- [ ] Отмена бронирования:
  - POST /api/v1/bookings/:id/cancel
  - Подтверждение: "Отменить запись?" (с информацией о refund policy)
  - Обновление списка

**Зависимость от бэкенда:** bookings + purchase (Phase 5+6 ✅).

**Критерий готовности:** Юзер записывается, видит бронирование, может отменить.

---

### F4.2: Отображение баланса

**Цель:** Баланс виден в интерфейсе.

**Задачи:**
- [ ] src/stores/balance.ts (Pinia):
  - `balanceCents: number` (из user.balance_cents)
  - `formattedBalance: string` (computed: "€15.00")
  - `refresh()` — GET /users/me, обновить баланс
- [ ] Отображение баланса:
  - В header или на экране профиля
  - На экране практики (достаточно ли для бронирования)
- [ ] src/utils/format.ts:
  - `formatCents(cents: number, currency?: string): string` → "€15.00"
  - `formatDate(iso: string, timezone?: string): string` → "22 фев, 10:00"
  - `formatDuration(minutes: number): string` → "1ч 30мин"

**Зависимость от бэкенда:** GET /api/v1/users/me (Phase 1.4 ✅).

**Критерий готовности:** Баланс отображается, форматирование корректно.

---

## PHASE F5: Пополнение (Stripe)

### F5.1: Topup flow

**Цель:** Юзер пополняет баланс через Stripe.

**Задачи:**
- [ ] src/views/user/TopupView.vue:
  - Текущий баланс
  - Предустановленные суммы (€5, €10, €20, €50) + произвольная сумма
  - Кнопка "Пополнить" → POST /api/v1/payments/topup → redirect на Stripe Checkout
- [ ] src/views/user/TopupSuccessView.vue:
  - "Баланс пополнен!" + обновление баланса из API
  - Кнопка "Вернуться" → dashboard
- [ ] src/views/user/TopupCancelView.vue:
  - "Оплата отменена" + кнопка "Попробовать снова"
- [ ] .env: VITE_API_BASE_URL (Stripe success/cancel URL-ы указывают на фронтенд-роуты)
- [ ] Бэкенд: убедиться, что STRIPE_SUCCESS_URL и STRIPE_CANCEL_URL указывают на фронтенд-роуты

**Зависимость от бэкенда:** POST /api/v1/payments/topup (Phase 6.3 ✅). Нужно обновить STRIPE_SUCCESS_URL / STRIPE_CANCEL_URL в .env бэкенда.

**Критерий готовности:** Юзер пополняет баланс через Stripe, видит обновлённую сумму.

---

## PHASE F6: Master — Управление практиками

### F6.1: Заявка мастера

**Цель:** Обычный юзер подаёт заявку на мастера.

**Задачи:**
- [ ] src/views/master/MasterApplyView.vue — 3-шаговая форма (из мокапов):
  - Шаг 1: Профиль (имя, email, телефон)
  - Шаг 2: Опыт (направления, стаж, языки)
  - Шаг 3: Документы (placeholder — загрузка не в MVP)
  - Progress bar (3 шага)
  - POST /api/v1/masters/apply
- [ ] src/views/master/MasterPendingView.vue:
  - "Заявка отправлена, ожидайте верификации"
  - Статус из GET /api/v1/masters/me
- [ ] Router guard: если user.role === 'user' и есть pending заявка → /master/pending

**Зависимость от бэкенда:** POST /api/v1/masters/apply, GET /api/v1/masters/me (Phase 2 ✅).

**Критерий готовности:** Юзер подаёт заявку, видит статус ожидания.

---

### F6.2: Список и создание практик

**Цель:** Мастер управляет своими практиками.

**Задачи:**
- [ ] src/stores/master.ts (Pinia):
  - `practices: PracticeResponse[]`
  - `profile: MasterProfileResponse | null`
  - `fetchMyPractices()` — GET /api/v1/masters/me/practices
- [ ] src/views/master/MasterPracticesView.vue:
  - Список практик мастера (upcoming / past)
  - Кнопка "Создать практику"
  - Карточка: название, дата, статус, участники
- [ ] src/views/master/CreatePracticeView.vue:
  - Форма: title, description, type, datetime (date+time picker), duration, timezone, max_participants, price, currency
  - POST /api/v1/practices
  - Валидация: дата в будущем, duration в пределах config
- [ ] src/views/master/EditPracticeView.vue:
  - PATCH /api/v1/practices/:id
  - State machine: показывать доступные переходы (draft→scheduled, scheduled→live, live→completed)
  - Кнопка "Удалить" (только для draft)
  - Кнопка "Опубликовать" (draft → scheduled)

**Зависимость от бэкенда:** practices CRUD (Phase 4 ✅).

**Критерий готовности:** Мастер создаёт практику, публикует, видит в списке.

---

### F6.3: Финализация + посещаемость

**Цель:** Мастер завершает практику и видит посещаемость.

**Задачи:**
- [ ] Кнопка "Завершить практику" на EditPracticeView (live → completed):
  - POST /api/v1/practices/:id/finalize
  - Подтверждение: "Завершить практику? Участники будут отмечены"
- [ ] src/views/master/AttendanceView.vue:
  - GET /api/v1/practices/:id/attendance
  - Список: имя, статус (attended / no_show / pending)
  - Агрегаты: всего, пришли, не пришли

**Зависимость от бэкенда:** finalize + attendance (Phase 5.4 ✅).

**Критерий готовности:** Мастер финализирует практику, видит кто пришёл.

---

## PHASE F7: Master — Финансы

### F7.1: Баланс мастера + выводы

**Цель:** Мастер видит финансы и выводит средства.

**Задачи:**
- [ ] src/views/master/MasterFinanceView.vue:
  - Баланс: available (доступно к выводу) + frozen (заморожено)
  - Кнопка "Вывести средства"
  - История выводов (если есть эндпоинт)
- [ ] Запрос вывода:
  - POST /api/v1/masters/me/withdraw
  - Ввод суммы, подтверждение
  - Обработка ошибок: недостаточно средств, нет payout details
- [ ] Настройки выплат:
  - PATCH /api/v1/masters/me/payout
  - Форма: method (bank_transfer / paypal / revolut), details (IBAN, email, etc.)
- [ ] src/views/master/MasterProfileView.vue:
  - Информация профиля
  - Ссылка на настройки выплат
  - Ссылка на финансы

**Зависимость от бэкенда:** withdrawals + payout (Phase 6.6 ✅).

**Критерий готовности:** Мастер видит баланс, настраивает выплаты, запрашивает вывод.

---

## PHASE F8: Admin

### F8.1: Дашборд + статистика

**Цель:** Админ видит ключевые метрики.

**Задачи:**
- [ ] src/views/admin/AdminDashboardView.vue:
  - GET /api/v1/admin/stats
  - Карточки: users_count, masters_count, practices_count, pending_verifications
  - Алерты (если pending > 0)

**Зависимость от бэкенда:** GET /api/v1/admin/stats (Phase 3.1 ✅).

**Критерий готовности:** Админ видит статистику.

---

### F8.2: Верификация мастеров

**Цель:** Админ верифицирует или отклоняет заявки.

**Задачи:**
- [ ] src/views/admin/AdminMastersView.vue:
  - Список pending заявок — GET /api/v1/admin/masters?status=pending
  - Карточка: имя, направления, стаж, дата заявки
- [ ] src/views/admin/AdminMasterReviewView.vue:
  - Полная информация о заявке
  - Кнопка "Верифицировать" → POST /api/v1/admin/masters/:id/verify
  - Кнопка "Отклонить" → POST /api/v1/admin/masters/:id/reject (с причиной)
  - Toast: "Мастер верифицирован" / "Заявка отклонена"

**Зависимость от бэкенда:** admin masters endpoints (Phase 2.3 ✅).

**Критерий готовности:** Админ верифицирует и отклоняет заявки.

---

### F8.3: Модерация + Семафоры

**Цель:** Обработка жалоб и мониторинг целостности данных.

**Задачи:**
- [ ] src/views/admin/AdminReportsView.vue:
  - Список жалоб — GET /api/v1/admin/reports?status=pending
  - Фильтр по статусу, типу
- [ ] src/views/admin/AdminReportDetailView.vue:
  - Информация о жалобе
  - Кнопки: resolve / dismiss
- [ ] src/views/admin/AdminConsistencyView.vue:
  - GET /api/v1/admin/consistency
  - Список из 21 семафора: имя, статус (OK/ALERT), категория
  - Цветовая индикация: зелёный/красный
  - ok_count / alert_count / total

**Зависимость от бэкенда:** reports + consistency (Phase 3.3 + 6.8 ✅).

**Критерий готовности:** Админ обрабатывает жалобы, видит семафоры.

---

## PHASE F9: Diary / Check-in / Feedback

### F9.1: Check-in + Feedback

**Цель:** Юзер отмечает состояние перед практикой и оставляет отзыв после.

**Задачи:**
- [ ] Check-in экран (перед практикой):
  - Выбор настроения: low / mid / high (emoji-кнопки из мокапов)
  - Опциональный комментарий
  - POST /api/v1/practices/:id/checkin
- [ ] Feedback экран (после практики):
  - Оценка: 🔥 Огонь / 👍 Хорошо / ❓ Есть вопросы
  - Опциональный комментарий
  - POST /api/v1/practices/:id/feedback
- [ ] Интеграция в booking flow:
  - Перед практикой (за N часов): баннер "Как вы себя чувствуете?"
  - После практики: баннер "Как прошла практика?"

**Зависимость от бэкенда:** Phase 8 бэкенда — **НЕ ГОТОВ. БЛОКИРУЮЩАЯ ЗАВИСИМОСТЬ.**

---

### F9.2: Дневник

**Цель:** Личные записи юзера.

**Задачи:**
- [ ] src/views/user/DiaryView.vue:
  - Вкладки: Все / Check-ins / Feedbacks / Записи
  - CRUD записей дневника
  - GET /api/v1/diary

**Зависимость от бэкенда:** Phase 8 бэкенда — **НЕ ГОТОВ. БЛОКИРУЮЩАЯ ЗАВИСИМОСТЬ.**

---

### F9.3: Insights для мастера

**Цель:** Мастер видит агрегированную обратную связь.

**Задачи:**
- [ ] src/views/master/AnalyticsView.vue:
  - GET /api/v1/practices/:id/insights
  - Распределение check-ins (high/mid/low) — прогресс-бары
  - Распределение feedbacks (fire/good/confused) — прогресс-бары
  - Количество комментариев

**Зависимость от бэкенда:** Phase 8.4 бэкенда — **НЕ ГОТОВ. БЛОКИРУЮЩАЯ ЗАВИСИМОСТЬ.**

---

## PHASE F10: PWA + Standalone + Полировка

### F10.1: Standalone-авторизация

**Цель:** Вход без Telegram (для PWA на Home Screen).

**Задачи:**
- [ ] src/views/auth/LoginView.vue:
  - Email + magic link (или email + пароль — решить с заказчиком)
  - Или: "Войти через Telegram" → deep link в Telegram бот
- [ ] Бэкенд: **новый эндпоинт** — POST /api/v1/auth/email (или /auth/magic-link)
- [ ] platform/standalone.ts — полноценная реализация вместо заглушек

**Зависимость от бэкенда:** **НОВЫЙ ЭНДПОИНТ — нужна реализация на бэкенде.**

---

### F10.2: Push-уведомления

**Цель:** Уведомления через Service Worker.

**Задачи:**
- [ ] Service Worker: обработка push events
- [ ] Запрос разрешения на push
- [ ] Регистрация подписки на бэкенде
- [ ] Бэкенд: Web Push channel в notification formatters

**Зависимость от бэкенда:** Phase 7.3 (Telegram-бот, Web Push channel) — **частично готов.**

---

### F10.3: Полировка

**Цель:** UX-улучшения для production-ready состояния.

**Задачи:**
- [ ] Skeleton-загрузки (вместо спиннеров)
- [ ] Анимации переходов (Vue `<Transition>`)
- [ ] Pull-to-refresh
- [ ] Тёмная тема (CSS-переменные уже позволяют, нужен toggle)
- [ ] Haptic feedback в Telegram (на кнопках, на успешных действиях)
- [ ] Error boundary (глобальная обработка ошибок Vue)
- [ ] Offline-заглушка ("Нет подключения" с кнопкой "Повторить")

**Критерий готовности:** Приложение ощущается как нативное на iPhone.

---

## 5. Сводка зависимостей

| Frontend Phase | Backend Phase | Статус бэка | Блокирует? |
|---------------|---------------|-------------|------------|
| F0: Инфра | — | — | Нет |
| F1: Auth | 1.2, 1.4 | ✅ | Нет |
| F2: Компоненты | 1.4 | ✅ | Нет |
| F3: Каталог | 4.3 | ✅ | Нет |
| F4: Бронирование | 5+6 | ✅ | Нет |
| F5: Stripe | 6.3 | ✅ | Нет |
| F6: Master | 2+4+5.4 | ✅ | Нет |
| F7: Финансы | 6.6 | ✅ | Нет |
| F8: Admin | 3+6.8 | ✅ | Нет |
| F9: Diary | **8** | **Нет** | **Да** |
| F10: PWA | 7.3 + новый auth | **Частично** | **Частично** |

---

## 6. Реестр технического долга

### Обозначения

- **Среда:** 🧪 Тест / 🚀 Прод
- **Статус:** ⬜ Open / ✅ Done

### Известные решения (НЕ является долгом)

| Решение | Причина |
|---------|---------|
| Ручная типизация API вместо OpenAPI codegen | Контроль, идиоматичность, проще поддерживать |
| sessionStorage вместо localStorage для token | Telegram WebApp закрывает вкладку — sessionStorage очищается, localStorage нет |
| Свой CSS вместо Tailwind | Дизайн-система уже готова в мокапах, переносить проще 1:1 |
| Внутренний Nginx в Docker фронтенда | SPA fallback + кеширование без усложнения хост-конфига |
| Telegram SDK через CDN script (не npm) | Рекомендация Telegram — всегда актуальная версия |

---

## 7. LLM Code Review Guide (Frontend)

### FP-01: Не хардкодить API URL

```typescript
// ❌ ЗАПРЕЩЕНО:
fetch('https://api.talentir.info/api/v1/users/me')

// ✅ ПРАВИЛЬНО:
const BASE_URL = import.meta.env.VITE_API_BASE_URL
fetch(`${BASE_URL}/api/v1/users/me`)
```

### FP-02: Не мутировать Pinia store напрямую из компонентов

```typescript
// ❌ ЗАПРЕЩЕНО:
authStore.user = response.data

// ✅ ПРАВИЛЬНО — через action:
authStore.setUser(response.data)
```

### FP-03: Не забывать обработку ошибок API

```typescript
// ❌ ЗАПРЕЩЕНО:
const data = await api.get('/practices')
practices.value = data.items

// ✅ ПРАВИЛЬНО:
try {
  const data = await api.get<PaginatedPracticesResponse>('/practices')
  practices.value = data.items
} catch (error) {
  toast.error('Не удалось загрузить практики')
}
```

### FP-04: Не забывать loading-состояния

```typescript
// ❌ Кнопка без блокировки — двойной клик:
async function book() {
  await api.post(`/practices/${id}/purchase`)
}

// ✅ С loading:
const loading = ref(false)
async function book() {
  if (loading.value) return
  loading.value = true
  try {
    await api.post(`/practices/${id}/purchase`)
  } finally {
    loading.value = false
  }
}
```

### FP-05: Не использовать `any`

```typescript
// ❌ ЗАПРЕЩЕНО:
function handleResponse(data: any) { ... }

// ✅ ПРАВИЛЬНО:
function handleResponse(data: PracticeResponse) { ... }
```

### FP-06: Cents → отображение (всегда через format)

```typescript
// ❌ ЗАПРЕЩЕНО:
<span>{{ user.balance_cents / 100 }}€</span>

// ✅ ПРАВИЛЬНО:
<span>{{ formatCents(user.balance_cents) }}</span>
```

### FP-07: Не привязываться к Telegram SDK напрямую

```typescript
// ❌ ЗАПРЕЩЕНО в компонентах:
window.Telegram.WebApp.HapticFeedback.impactOccurred('medium')

// ✅ ПРАВИЛЬНО — через абстракцию:
platform.hapticFeedback('medium')
```

---

**Конец документа**
