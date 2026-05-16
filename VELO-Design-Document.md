# VELO -- Дизайн-документ (Конституция)

**Версия:** 3.0
**Дата:** 16 мая 2026
**Статус:** Active

> **Изменение в v3.0:** Frontend откачен на Phase 0 foundation. Все компоненты,
> views, stores и composables удалены. Новые views генерируются через Claude Code
> из Figma по гайду `frontend/ARCHITECTURE.md` и бэклогу `VELO-Frontend-TZ-Final.md`.
> Backend не затронут.

---

## 1. Что такое VELO

### 1.1. Миссия

> **Мастера хотят творить, а не быть бухгалтерами и секретарями. VELO снимает рутину.**

VELO -- платформа для мастеров практик (медитация, йога, breathwork и смежные направления).
Автоматизирует всё, что мешает мастеру заниматься своим делом:

| Рутина | До VELO | После VELO |
|--------|---------|------------|
| Записи на практику | Сообщения в чат "запишите меня" | Автоматические бронирования |
| Очередь ожидания | "Напишу, если место освободится" | Waitlist + авто-уведомления |
| Напоминания участникам | Ручная рассылка | Авто: 24ч, 1ч, 10мин |
| Сбор оплаты | "Переведите на карту" | Stripe, автоматически |
| Учёт посещений | Галочки в блокноте | Attendance tracking |
| Обратная связь | "Напишите как вам" | Check-in / Feedback формы |
| Аналитика | Никакой | Insights по каждой практике |

### 1.2. Аудитория

| Роль | Описание |
|------|----------|
| **User** | Участник практик. Бронирует, платит, оставляет обратную связь |
| **Master** | Ведущий практик. Одновременно может быть участником чужих практик |
| **Admin** | Администратор платформы. Верификация мастеров, модерация, поддержка |

### 1.3. Глоссарий

| Термин | Определение |
|--------|-------------|
| **Практика** | Сессия (медитация, йога, breathwork и т.д.), проводимая мастером |
| **Бронирование** | Резервация места на практике участником |
| **Check-in** | Фиксация состояния участника ДО практики (mood: low/mid/high) |
| **Feedback** | Обратная связь участника ПОСЛЕ практики (rating: fire/good/confused) |
| **Ledger** | Журнал финансовых транзакций (принцип double-entry) |
| **Waitlist** | Очередь ожидания на заполненную практику |
| **Розетка** | Заготовка под будущую функцию: интерфейс определён, логика не реализована |

---

## 2. Технологический стек

### 2.1. Backend

| Компонент | Технология | Версия |
|-----------|------------|--------|
| Язык | Python | 3.12 |
| Фреймворк | FastAPI | latest |
| ORM | SQLAlchemy | 2.0 (async) |
| Валидация | Pydantic | v2 |
| Миграции | Alembic | latest |
| Тестирование | pytest + pytest-asyncio | latest |
| Логирование | structlog | latest |

### 2.2. База данных и кэш

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| Primary DB | PostgreSQL 16 | Все данные |
| Cache / Sessions | Redis 7 | Сессии, очереди задач, кэш |

### 2.3. Frontend

| Компонент | Технология | Версия |
|-----------|------------|--------|
| Фреймворк | Vue 3 | latest |
| Язык | TypeScript | 5.x |
| Сборка | Vite | latest |
| Роутинг | Vue Router | 4.x |
| Стейт | Pinia | latest |
| HTTP | Fetch (обёртка `client.ts`) | native |
| i18n | vue-i18n | latest |
| PWA | vite-plugin-pwa | latest |
| Стили | Свой CSS (дизайн-токены из Figma) | -- |
| Линтинг | ESLint + Prettier | latest |

### 2.4. Внешние сервисы

| Сервис | Назначение |
|--------|------------|
| Stripe | Пополнение баланса юзера, вывод средств мастером |
| Telegram Bot API | Уведомления (aiogram), Telegram WebApp (фронтенд MVP) |

### 2.5. Инфраструктура

| Компонент | Технология |
|-----------|------------|
| Контейнеризация | Docker + Docker Compose |
| Хостинг | VPS (Hetzner, NL) |
| Reverse proxy | Nginx (на хосте) |
| SSL | Let's Encrypt (certbot) |
| Деплой | Ручной: `velo update` (git pull + rebuild + migrate + restart) |

---

## 3. Архитектура

### 3.1. Модульный монолит сейчас -- микросервисы потом

MVP -- один сервис, разбитый на изолированные модули. Каждый модуль
самодостаточен и спроектирован так, чтобы в будущем стать отдельным
микросервисом без переписывания бизнес-логики.

```
backend/app/modules/
├── auth/           -- Telegram auth, сессии (Redis)
├── users/          -- Профили, роли
├── masters/        -- Профили мастеров, верификация, балансы
├── practices/      -- CRUD практик, state machine
├── bookings/       -- Бронирования, waitlist
├── payments/       -- Ledgers (double-entry), Stripe, промокоды, выводы
├── notifications/  -- Telegram-бот, процессор, шаблоны, напоминания
├── diary/          -- Check-ins, feedbacks, diary entries, insights
└── admin/          -- Верификация мастеров, модерация, семафоры
```

### 3.2. Структура модуля

Каждый модуль содержит:

```
module/
├── models.py       -- SQLAlchemy ORM models
├── schemas.py      -- Pydantic request/response schemas
├── service.py      -- Business logic (единственное место для логики)
├── router.py       -- FastAPI endpoints (только маршрутизация)
└── exceptions.py   -- Module-specific exceptions (опционально)
```

### 3.3. Будущий распил на микросервисы

Таблицы БД уже сгруппированы по будущим сервисам:

```
User Service:       users, diary_entries
Master Service:     master_profiles, withdrawals
Practice Service:   practices, practice_pricing
Booking Service:    bookings, waitlist
Payment Service:    user_ledger, master_ledger, company_ledger,
                    payments, purchases, promos
State Service:      checkins, feedbacks
Notification Service: notifications, notification_deliveries
Admin Service:      reports, audit_log
```

### 3.4. Frontend: три роли, одно приложение

Одно SPA с ролевым роутингом. Роль определяется из `GET /api/v1/users/me`.

| Роль | Shell | Tab Bar |
|------|-------|---------|
| user | UserShell | Дашборд / Календарь / Дневник / Профиль |
| master | MasterShell | Дашборд / Практики / Аналитика / Профиль |
| admin | AdminShell | Дашборд / Мастера / Модерация |

Мастер и Админ имеют доступ к интерфейсу нижестоящих ролей через viewMode
(переключение режима без смены роли в БД). `viewMode` хранится в Pinia +
sessionStorage, сбрасывается при logout. Admin-only API-действия игнорируют
viewMode и проверяют реальную `user.role`.

**Детали:** `frontend/ARCHITECTURE.md` (конституция фронта для Claude Code) +
`VELO-Frontend-TZ-Final.md` (бэклог экранов и спринт-план).

### 3.5. Платёжная архитектура (Double-Entry)

**Принцип:** каждая операция -- две записи в журналах. Сумма всех записей = 0.

Три журнала:

| Журнал | Владелец | Назначение |
|--------|----------|------------|
| `user_ledger` | Каждый юзер | Баланс кошелька |
| `master_ledger` | Каждый мастер | Заработок (frozen + available) |
| `company_ledger` | Платформа | Комиссии, маркетинг, возвраты |

**Ключевые правила:**
- Юзер платит мастеру 100% при бронировании (деньги идут в `frozen`)
- Мастер платит платформе 15% комиссии после завершения практики
- Комиссия только с живых денег: бесплатная практика = нулевые записи
- Вывод средств мастером -- только из `available`, только вручную (админ подтверждает)
- Юзер не может выводить деньги из системы

---

## 4. Принципы и запреты

### 4.1. Архитектурные принципы

| Принцип | Описание |
|---------|----------|
| **ORM only** | Никакого raw SQL. Только SQLAlchemy ORM |
| **Service layer** | Вся бизнес-логика -- в `service.py`. Роутеры только маршрутизируют |
| **No commit in routers** | `get_db_session()` делает commit сам. В роутерах -- только `flush()` + `refresh()` |
| **JSONBMixin** | Все мутации JSONB-колонок -- только через `set_jsonb()`. Прямое присвоение dict не детектится SQLAlchemy |
| **State machine** | Переходы статусов -- только через явные функции в service.py. `setattr(obj, "status", x)` без валидации -- запрещено |
| **Double-entry** | Прямое изменение балансов запрещено. Только через ledger-записи + listeners |
| **Async I/O** | Все I/O операции -- async/await. Синхронные вызовы блокируют event loop |

### 4.2. Запреты (бэкенд)

```python
# ЗАПРЕЩЕНО:
await session.commit()          # в роутерах -- двойной коммит
raw_sql = text("SELECT ...")    # только ORM
profile.data["key"] = value     # JSONB мутация без set_jsonb()
user.balance_cents += amount    # прямое изменение баланса
practice.status = "completed"   # статус без валидации перехода
import logging                  # только structlog
```

### 4.3. Запреты (фронтенд)

Принципиальные запреты. Полный список и примеры -- в `frontend/ARCHITECTURE.md §8`.

```css
/* ЗАПРЕЩЕНО -- хардкод цветов/отступов/радиусов: */
color: #4c6589;
padding: 16px;
border-radius: 15px;

/* ПРАВИЛЬНО -- только дизайн-токены из variables.css: */
color: var(--velo-text-primary);
padding: var(--space-4);
border-radius: var(--radius-md);
```

```typescript
// ЗАПРЕЩЕНО -- raw fetch и хардкод URL:
const res = await fetch('https://api.vel-app.com/api/v1/users/me')

// ПРАВИЛЬНО -- типизированные обёртки из src/api/:
import { getMe } from '@/api/users'
const user = await getMe()
```

```typescript
// ЗАПРЕЩЕНО -- any и ручная типизация бэкенд-схем:
function handle(data: any) { ... }

// ПРАВИЛЬНО -- типы из api/types.ts (re-export из generated.ts):
import type { PracticeResponse } from '@/api/types'
```

```typescript
// ЗАПРЕЩЕНО -- прямое обращение к Telegram SDK:
window.Telegram.WebApp.HapticFeedback.impactOccurred('medium')

// ПРАВИЛЬНО -- через platform-абстракцию:
import { platform } from '@/platform'
platform.hapticFeedback('medium')
```

```vue
<!-- ЗАПРЕЩЕНО -- русские литералы в шаблонах: -->
<button>Записаться на практику</button>

<!-- ПРАВИЛЬНО -- ключи i18n сразу, с первого экрана: -->
<button>{{ t('practice.book') }}</button>
```

### 4.4. Соглашения по коду

| Правило | Значение |
|---------|---------|
| Комментарии в коде | Только английский |
| Общение / документация | Русский |
| Символ `→` в коде | Заменять на `->` (ASCII) |
| Символ `—` в коде | Заменять на `--` (двойной дефис) |
| Unicode-символы | Допустимы только в документации вне кода |
| Backend formatter | ruff (black удалён в Phase 0.6) |
| Backend type checker | mypy (strict) |
| Frontend formatter | Prettier |
| Frontend linter | ESLint (flat config) |

---

## 5. Структура репозитория

```
velo/                              -- GitHub repo root
├── backend/
│   ├── app/
│   │   ├── main.py                -- FastAPI app + lifespan
│   │   ├── core/                  -- DB, Redis, config, exceptions, mixins
│   │   └── modules/               -- Бизнес-модули (см. раздел 3.1)
│   ├── migrations/                -- Alembic migrations
│   ├── tests/                     -- pytest
│   ├── scripts/                   -- seed.py, generate_ts_types.py
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api/                   -- HTTP-клиент + generated types + API-методы
│   │   ├── components/            -- ui/, layout/, shared/ (генерируется CC)
│   │   ├── composables/           -- useAuth, useToast, usePagination (генерируется CC)
│   │   ├── platform/              -- Telegram / Standalone абстракция (стабильно, не трогать)
│   │   ├── router/                -- Vue Router + guards
│   │   ├── stores/                -- Pinia stores (генерируется CC)
│   │   ├── styles/                -- variables.css (Figma tokens), global.css
│   │   ├── utils/                 -- format, currency, constants
│   │   └── views/                 -- shells/, auth/, user/, master/, admin/ (генерируется CC)
│   ├── public/                    -- manifest.json, иконки, telegram-web-app.js
│   ├── ARCHITECTURE.md            -- Фронт-конституция для Claude Code
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml             -- Весь стек: app + frontend + postgres + redis
├── scripts/
│   └── install_velo.sh            -- Первоначальная установка на VPS
├── VELO-Design-Document.md        -- Этот файл (конституция)
├── VELO-Backend.md                -- Бэковый Кодекс (детали бэка)
└── VELO-Frontend-TZ-Final.md      -- Фронт-бэклог: экраны, спринты, endpoint-mapping
```

**Источники правды:**
- Схема БД: `backend/app/modules/*/models.py`
- API-контракт: автогенерируется в `frontend/src/api/generated.ts` из OpenAPI бэкенда
- Дизайн UI: Figma (единственный источник для визуала и токенов)

---

## 6. Дорожная карта за MVP

### 6.1. Standalone PWA (F10)

Сейчас приложение работает только через Telegram WebApp. После MVP:

- Standalone-авторизация (email + magic link или email + пароль)
- Полноценная реализация `platform/standalone.ts` (сейчас -- заглушки)
- Push-уведомления через Service Worker
- Новый бэкенд-эндпоинт: `POST /api/v1/auth/email`

Платформенная абстракция (`src/platform/`) уже готова к этому: Telegram и Standalone реализуют единый интерфейс `Platform`.

### 6.2. Мультиязычность (i18n)

`vue-i18n` подключается с первого экрана генерации фронта. Все строки в
`.vue` и `.ts` -- через `t('key')`, никаких русских литералов в шаблонах.

Локали: `ru` (основной) + `en`. Файлы локалей: `frontend/src/locales/`.

Отдельный план миграции не требуется: старого фронта с накопленными
литералами больше нет, новые views создаются сразу i18n-ready.

### 6.3. Микросервисы

Таблицы БД уже сгруппированы по будущим сервисам (см. раздел 3.3).
`trace_id` пробрасывается в каждом запросе -- готова основа для distributed tracing.
Распил не требует переписывания бизнес-логики, только разделения транспорта.

### 6.4. Российская аудитория (TD-RU-PROXY)

Hetzner IP (`api.talentir.info`) заблокирован ТСПУ. До публичного запуска
в России нужен российский VPS-reverse-proxy (Timeweb/Selectel, ~300-500₽/мес)
или DDoS-Guard CDN. Бэкенд и фронтенд остаются на Hetzner.

---

## 7. Розетки

Заготовки, которые намеренно не реализованы в MVP.
Интерфейсы определены, чтобы будущая реализация не ломала архитектуру.

### 7.1. AI-саммари

Интерфейс в `backend/app/modules/ai/interface.py` (Protocol):

```python
class AIService(Protocol):
    async def generate_summary(
        self,
        practice_id: UUID,
        checkins: list[Checkin],
        feedbacks: list[Feedback],
    ) -> str: ...
```

Эндпоинт `GET /api/v1/practices/{id}/ai-summary` возвращает placeholder.

### 7.2. Library (Записи практик)

Будущие таблицы: `recordings` (метаданные) + S3 для файлов.
В коде -- TODO-комментарии в нужных местах.

### 7.3. Подписки

Таблица `subscriptions` спроектирована, логика не реализована:

```python
class Subscription:
    plan: Enum          # monthly | yearly
    status: Enum        # active | cancelled | expired
    stripe_subscription_id: str
```

### 7.4. OAuth (Google, Apple)

`User.credentials` -- JSONB, структура поддерживает несколько провайдеров:

```json
{
  "telegram": {"id": 123456789},
  "google":   {"id": "...", "email": "..."},
  "apple":    {"id": "..."}
}
```

При необходимости -- миграция в отдельную таблицу `user_auths`.

### 7.5. Standalone-авторизация

`src/platform/standalone.ts` -- safe no-op заглушки (живые, в фундаменте).
UI-экраны для standalone-режима (LoginView через email/OAuth, StandaloneStubView)
будут созданы в Phase F10. MVP работает только через Telegram WebApp.

---

## 8. Артефакты

| Артефакт | Путь | Статус |
|----------|------|--------|
| Дизайн-документ (конституция) | `VELO-Design-Document.md` | Актуален (этот файл) |
| Бэковый Кодекс | `VELO-Backend.md` | Актуален |
| Фронт-конституция (для Claude Code) | `frontend/ARCHITECTURE.md` | Актуален, CC стартует отсюда |
| Фронт-бэклог (экраны и спринты) | `VELO-Frontend-TZ-Final.md` | Живой документ, обновляется после каждого спринта |
| Схема БД (источник правды) | `backend/app/modules/*/models.py` | Актуальна |
| API-типы для фронта | `frontend/src/api/generated.ts` | Автогенерация из OpenAPI при `velo update` |
| Дизайн UI (источник правды) | Figma | Единственный источник для визуала и токенов |

---

**Конец документа**
