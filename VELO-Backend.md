# VELO — Бэковый Кодекс

**Версия:** 1.1
**Дата:** 12 марта 2026
**Статус:** Active
**Тесты:** 417 passed, 3 skipped

---

## 1. Модули

### 1.1. Карта модулей  

| Модуль | Путь | Назначение |
|--------|------|------------|
| `auth` | `app/modules/auth/` | Telegram WebApp auth, сессии Redis |
| `users` | `app/modules/users/` | Профили юзеров, роли |
| `masters` | `app/modules/masters/` | Профили мастеров, верификация, балансы, выводы |
| `practices` | `app/modules/practices/` | CRUD практик, state machine |
| `bookings` | `app/modules/bookings/` | Бронирования, посещаемость |
| `waitlist` | `app/modules/waitlist/` | Очередь ожидания |
| `payments` | `app/modules/payments/` | Stripe, пополнение баланса |
| `promos` | `app/modules/promos/` | Промокоды (Company + Master) |
| `withdrawals` | `app/modules/withdrawals/` | Запросы на вывод средств |
| `reports` | `app/modules/reports/` | Жалобы пользователей |
| `notifications` | `app/modules/notifications/` | Telegram-бот, процессор, шаблоны, напоминания |
| `diary` | `app/modules/diary/` | Check-ins, feedbacks, diary entries, insights |
| `admin` | `app/modules/admin/` | Верификация мастеров, модерация, семафоры |
| `ai` | `app/modules/ai/` | Розетка AI-саммари (Phase 9) |

### 1.2. Core

| Файл | Содержимое |
|------|------------|
| `app/core/config.py` | `Settings` (pydantic-settings, `.env`) |
| `app/core/database.py` | `get_db_session()`, `get_db_reader()`, `get_session_factory()` |
| `app/core/exceptions.py` | `VeloError` → `NotFoundError`, `ForbiddenError`, `ConflictError`, `BadRequestError`, `UnauthorizedError` |
| `app/core/mixins.py` | `UUIDMixin`, `TimestampMixin`, `JSONBMixin` |
| `app/core/logging.py` | structlog setup (`setup_logging()`) |
| `app/core/audit.py` | `record_audit()`, `AuditLog` model |

---

## 2. API Endpoints

### Auth

```
POST /api/v1/auth/telegram          -- Вход через Telegram initData
POST /api/v1/auth/logout            -- Выход (текущая сессия)
POST /api/v1/auth/logout-all        -- Выход со всех устройств
```

### Users

```
GET   /api/v1/users/me              -- Мой профиль
PATCH /api/v1/users/me              -- Обновить профиль
GET   /api/v1/users/me/checkins     -- Мои check-ins (пагинация)
GET   /api/v1/users/me/feedbacks    -- Мои feedbacks (пагинация)
```

### Masters

```
POST  /api/v1/masters/apply                         -- Подать заявку на мастера
GET   /api/v1/masters/me                            -- Мой профиль мастера
PATCH /api/v1/masters/me/payout                     -- Обновить реквизиты для выплат
GET   /api/v1/masters/me/practices                  -- Мои практики (пагинация)
POST  /api/v1/masters/me/promos                     -- Создать мастерский промокод
GET   /api/v1/masters/me/promos                     -- Мои промокоды (пагинация)
PATCH /api/v1/masters/me/promos/{id}/deactivate     -- Деактивировать промокод
POST  /api/v1/masters/me/withdraw                   -- Запрос на вывод средств
GET   /api/v1/masters/me/withdrawals                -- История выводов (пагинация)
```

### Practices

```
GET    /api/v1/practices                        -- Публичный фид (фильтры: type, status, date, master)
POST   /api/v1/practices                        -- Создать практику (мастер)
GET    /api/v1/practices/{id}                   -- Детали практики
PATCH  /api/v1/practices/{id}                   -- Обновить практику (владелец)
DELETE /api/v1/practices/{id}                   -- Удалить черновик (владелец)
POST   /api/v1/practices/{id}/cancel            -- Отменить практику + возврат всем
POST   /api/v1/practices/{id}/finalize          -- Завершить практику (мастер)
GET    /api/v1/practices/{id}/attendance        -- Список посещаемости (мастер)
POST   /api/v1/practices/{id}/checkin           -- Создать/обновить check-in (юзер)
POST   /api/v1/practices/{id}/feedback          -- Создать/обновить feedback (юзер)
GET    /api/v1/practices/{id}/insights          -- Агрегированные insights (мастер)
GET    /api/v1/practices/{id}/ai-summary        -- AI-саммари (розетка, Phase 9)
```

### Bookings

```
POST   /api/v1/bookings             -- Забронировать (+ опциональный promo_code)
GET    /api/v1/bookings/me          -- Мои бронирования
GET    /api/v1/bookings/{id}        -- Детали бронирования
DELETE /api/v1/bookings/{id}        -- Отменить бронирование
POST   /api/v1/bookings/{id}/join   -- Отметить приход (мастер)
POST   /api/v1/bookings/{id}/leave  -- Отметить уход (мастер)
```

### Waitlist

```
POST   /api/v1/practices/{id}/waitlist      -- Встать в очередь
DELETE /api/v1/practices/{id}/waitlist      -- Выйти из очереди
GET    /api/v1/practices/{id}/waitlist      -- Список очереди (мастер)
```

### Payments

```
POST /api/v1/payments/topup                 -- Создать сессию пополнения (Stripe Checkout)
GET  /api/v1/payments/topup/success         -- Страница успеха (redirect)
GET  /api/v1/payments/topup/cancel          -- Страница отмены (redirect)
POST /webhooks/stripe                       -- Stripe webhook (checkout.session.completed / expired)
```

### Reports

```
POST  /api/v1/reports               -- Создать жалобу (или получить существующую — 200 если дубль)
PATCH /api/v1/reports/{id}          -- Редактировать свою pending-жалобу
GET   /api/v1/reports/me            -- Мои жалобы (пагинация)
```

### Diary

```
POST   /api/v1/diary                -- Создать запись дневника
GET    /api/v1/diary                -- Мои записи дневника (пагинация)
GET    /api/v1/diary/{id}           -- Запись дневника
PATCH  /api/v1/diary/{id}           -- Обновить запись
DELETE /api/v1/diary/{id}           -- Удалить запись
```

### Admin

```
GET  /api/v1/admin/stats                            -- Метрики платформы

GET  /api/v1/admin/users                            -- Все юзеры (фильтры: role, is_active)
GET  /api/v1/admin/masters/pending                  -- Мастера на верификации
GET  /api/v1/admin/masters/list                     -- Все мастера (фильтр: status)
GET  /api/v1/admin/masters/{id}                     -- Профиль мастера для ревью
POST /api/v1/admin/masters/{id}/verify              -- Верифицировать мастера
POST /api/v1/admin/masters/{id}/reject              -- Отклонить заявку

GET  /api/v1/admin/reports                          -- Список жалоб (фильтры: status, target_type)
GET  /api/v1/admin/reports/{id}                     -- Детали жалобы
POST /api/v1/admin/reports/{id}/resolve             -- Обработать жалобу
POST /api/v1/admin/reports/{id}/dismiss             -- Отклонить жалобу

GET  /api/v1/admin/withdrawals                      -- Список выводов (фильтр: status)
POST /api/v1/admin/withdrawals/{id}/approve         -- Одобрить вывод
POST /api/v1/admin/withdrawals/{id}/reject          -- Отклонить вывод

POST /api/v1/admin/promos                           -- Создать company-промокод
GET  /api/v1/admin/promos                           -- Список company-промокодов
PATCH /api/v1/admin/promos/{id}/deactivate          -- Деактивировать промокод

GET  /api/v1/admin/consistency                      -- Data consistency семафоры

POST /api/v1/admin/templates/reload                 -- Перезагрузить шаблоны уведомлений
```

### System

```
GET /           -- {"name": "VELO API", "version": "..."}
GET /health     -- {"status": "ok", "db": "ok", "redis": "ok"} (всегда 200)
GET /ready      -- То же, но 503 при деградации
```

---

## 3. Архитектурные правила

### 3.1. JSONBMixin — мутации JSONB

SQLAlchemy не детектит изменения JSONB при прямом присвоении dict.
Это silent bug: данные не сохраняются в БД.

```python
# ЗАПРЕЩЕНО:
profile.data = new_dict
profile.data["account"]["status"] = "verified"

# ПРАВИЛЬНО:
profile.set_jsonb("data", new_dict)
```

`JSONBMixin` в `app/core/mixins.py` выполняет `setattr()` + `flag_modified()`.
Все модели с JSONB-колонками обязаны наследовать `JSONBMixin`.

Текущие JSONB-колонки:

| Модель | Колонка | JSONBMixin |
|--------|---------|------------|
| `MasterProfile` | `data` | ✅ |
| `User` | `credentials` | ⬜ TD-024 — добавить при первой ORM-мутации |

### 3.2. Session Commit Rule

`get_db_session()` делает `commit()` автоматически после `yield`.
Явный `commit()` в роутере = двойной коммит = `InvalidRequestError`.

```python
# ЗАПРЕЩЕНО в роутерах:
await session.commit()

# ПРАВИЛЬНО — flush для DB-generated значений:
await session.flush()
await session.refresh(obj)
# get_db_session() сделает единственный commit сам
```

Два вида сессий:

| Зависимость | Поведение | Когда использовать |
|-------------|-----------|-------------------|
| `get_db_session()` | auto-commit после yield, rollback при исключении | Write-операции |
| `get_db_reader()` | всегда rollback | Read-only запросы |

В service-слое допустим `session.rollback()` только внутри `try/except IntegrityError`.

### 3.3. State Machine — практики

Переходы статусов практики — только через явные функции в `practices/service.py`.
Прямой `setattr(practice, "status", x)` без валидации запрещён.

Допустимые переходы:

```
draft      -> scheduled   (мастер публикует)
scheduled  -> live        (практика началась)
scheduled  -> cancelled   (отмена)
live       -> completed   (finalize)
live       -> cancelled   (отмена)
completed  -> (финал, нет переходов)
cancelled  -> (финал, нет переходов)
```

### 3.4. Pydantic PATCH — NOT NULL поля

Для каждого NOT NULL поля в Update-схеме нужен валидатор, отклоняющий `null`:

```python
@field_validator("title", "timezone", mode="before")
@classmethod
def _reject_null(cls, v):
    if v is None:
        raise ValueError("This field cannot be set to null")
    return v
```

Без валидатора `{"timezone": null}` проходит Pydantic, но падает с 500 IntegrityError.

### 3.5. Логирование

Только `structlog`. `import logging` запрещён.

```python
import structlog
logger = structlog.get_logger()

# В сервисах:
logger.info("booking.created", booking_id=str(booking.id), user_id=str(user.id))
```

Уровни: DEBUG (разработка) / INFO (бизнес-события) / WARNING (потенциальные проблемы) / ERROR (recoverable) / CRITICAL (система сломана).

---

## 4. Платёжная архитектура

### 4.1. Double-Entry принцип

Каждая операция — две записи. Сумма всех записей в системе = 0 всегда.

Три журнала:

| Журнал | Таблица | Содержимое |
|--------|---------|------------|
| User Ledger | `user_ledger` | Пополнения, списания, возвраты юзера |
| Master Ledger | `master_ledger` | Продажи (frozen -> available), комиссии, выводы |
| Company Ledger | `company_ledger` | Комиссии, маркетинг, возвраты |

В `master_ledger` есть флаг `is_frozen`: деньги locked до завершения практики.
В `MasterProfile` — кэшированные поля `frozen_cents` и `available_cents`, обновляемые listeners при каждой записи в ledger.

**Прямое изменение балансов запрещено.** Только через ledger-записи + listeners.

### 4.2. Stripe интеграция

Топап-флоу: `POST /payments/topup` → Stripe Checkout Session → webhook `checkout.session.completed` → `UserLedger(+N)` + `CompanyLedger(-N)`.

Stub-режим (`STRIPE_SECRET_KEY="TEST"`): обходит Stripe, мгновенно подтверждает оплату. Только для разработки.

### 4.3. Вывод средств

Флоу: `POST /masters/me/withdraw` (freeze) → admin approve/reject → `MasterLedger(-N frozen)` + `CompanyLedger(+fee)` + `Payment(OUT)`.
Минимальная сумма: `MIN_WITHDRAWAL_CENTS` (дефолт 5000 = €50).
Комиссия за вывод: `WITHDRAWAL_FEE_CENTS` (дефолт 200 = €2).

---

## 5. Уведомления

### 5.1. Архитектура

Два уровня:
- `Notification` — что отправить, кому (channel-agnostic).
- `NotificationDelivery` — конкретная доставка: юзер + канал + статус.

### 5.2. Процессор

Фоновая задача (`notifications/processor.py`). Забирает pending Notification, резолвит target → список юзеров, создаёт `NotificationDelivery` per-user, отправляет через channel-formatter.

### 5.3. Шаблоны

Языки: `ru`, `en`, `de`, `es`. Файлы: `notifications/templates/{lang}.yaml`.
Язык выбирается по `User.language`. По умолчанию: `en`.
Перезагрузка без рестарта: `POST /api/v1/admin/templates/reload`.

### 5.4. Напоминания

Создаются с `scheduled_at = practice.scheduled_at - N` при бронировании.
Отменяются при отмене бронирования или практики.
Пересоздаются при изменении времени практики.
5-минутный буфер: напоминания за < 5 минут не создаются.

---

## 6. Data Consistency Семафоры

Набор проверок для обнаружения рассинхрона данных. Запускаются через `GET /api/v1/admin/consistency`.

Категории:

| Категория | Пример |
|-----------|--------|
| **COUNT = COUNT** | bookings ↔ purchases, users(role=master+admin) ↔ master_profiles |
| **SUM = 0** | Σ(user_ledger + master_ledger + company_ledger) = 0 |
| **Computed = Actual** | `User.balance_cents` = SUM(user_ledger), `MasterProfile.available_cents` = SUM(master_ledger WHERE NOT frozen) |
| **Orphan Detection** | booking без practice = 0, notification_delivery без user = 0 |
| **Invariants** | Отрицательный баланс = 0, frozen у завершённой практики = 0 |

Правило: при добавлении новой таблицы или кэшированного поля — добавить соответствующий семафор.
Полная документация: `VELO-Data-Consistency-Semaphores.md`.

---

## 7. Конфигурация

Все параметры в `app/core/config.py`, загружаются из `.env`.
Ключевые:

| Переменная | Дефолт | Описание |
|-----------|--------|---------|
| `APP_ENV` | `development` | Среда (`development` / `production`) |
| `SECRET_KEY` | — | Обязателен в production |
| `DATABASE_URL` | — | Обязателен в production |
| `TELEGRAM_BOT_TOKEN` | `""` | Токен бота |
| `TELEGRAM_BOT_URL` | `""` | URL бота для deep links |
| `STRIPE_SECRET_KEY` | `""` | Stripe API key (`"TEST"` = stub mode) |
| `STRIPE_WEBHOOK_SECRET` | `""` | Stripe webhook signature |
| `COMMISSION_PERCENT` | `15` | Комиссия платформы (%) |
| `MIN_WITHDRAWAL_CENTS` | `5000` | Минимальный вывод (€50.00) |
| `WITHDRAWAL_FEE_CENTS` | `200` | Комиссия за вывод (€2.00) |
| `CANCELLATION_DEADLINE_HOURS` | `24` | Дедлайн бесплатной отмены |
| `CHECKIN_WINDOW_HOURS` | `3` | За сколько часов до открывается check-in |
| `FEEDBACK_WINDOW_HOURS` | `72` | Сколько часов после практики открыт feedback |
| `SESSION_TTL_DAYS` | `30` | Срок жизни сессии Redis |
| `LOG_LEVEL` | `INFO` | Уровень логирования |

---

## 8. Тесты

417 passed, 3 skipped. Все запускаются внутри Docker:

```bash
velo test          # все тесты
velo lint          # ruff check
```

Диапазоны `telegram_id` в тестах (без конфликтов):

| Модуль | Диапазон |
|--------|---------|
| auth | 77xxx, 99xxx |
| users | 88xxx |
| masters | 80xxx |
| practices | 81xxx |
| bookings | 82xxx |
| payments | 85xxx |
| notifications | 83xxx |
| reminders | 84xxx |
| diary | 86xxx |
| admin | 87xxx |
| cancellation | 76xxx |
| withdrawals | 75xxx |

---

## 9. Технический долг

### Обозначения

- **Среда:** 🧪 низкий приоритет / 🚀 перед публичным запуском
- **Статус:** ⬜ Open / ✅ Done

### Перед публичным запуском 🚀

| ID | Файл | Описание | Решение |
|----|------|----------|---------|
| **TD-RU-PROXY** | Инфра | Hetzner IP заблокирован ТСПУ. Недоступен из России без VPN | Российский reverse proxy (Timeweb/Selectel ~300-500₽/мес) или DDoS-Guard CDN |
| **CRITICAL-4** | `auth/router.py` | Нет rate limiting на `POST /auth/telegram`. Replay valid initData в 5-минутном окне → тысячи Redis-сессий | `slowapi` или Redis-based limiter |
| **WARNING-4** | `auth/router.py` | Telegram initData replay в 5-минутном окне — нет защиты от повторного использования | Redis SET `used_init_data:{hash}` с TTL 5 минут |
| **WARNING-5** | `payments/webhook.py` | Stripe webhook signature не проверяется при `STRIPE_STUB=true` | Запрет `STRIPE_STUB` в production через config validator |
| TD-025 | Все роутеры | Нет rate limiting на masters endpoints | `slowapi` или Redis-based custom limiter |
| TD-026 | `docker-compose.yml` | Redis без пароля | `requirepass` + `REDIS_PASSWORD` в .env |

### Открытые находки

| ID | Среда | Файл | Описание | Решение |
|----|-------|------|----------|---------|
| **CRITICAL-3** | 🚀 | `payments/service.py` | `record_master_ledger` при отсутствующем `MasterProfile` создаёт ledger entry но не обновляет кэшированный баланс → расхождение | Бросать `BadRequestError` вместо silent continue |
| **WARNING-2** | 🧪 | `main.py` | Глобальный 500-обработчик без `request.method` и `trace_id` в логах | Добавить контекст запроса в exception handler |
| **WARNING-14** | 🧪 | `*/service.py` | Сервисы импортируют `settings` напрямую — затрудняет unit-тестирование | Инъекция через параметры или DI |
| TD-013 | 🧪 | `migrations/env.py` | Engine не dispose если `connect()` упадёт | `try/finally` вокруг async with |
| TD-014 | 🧪 | Несколько файлов | Версия `0.1.0` захардкожена в трёх местах | Единый источник в `config.py` или `__version__` |
| TD-015 | 🧪 | `config.py` | `postgres_password` дефолт `"velo"` без проверки в проде | Validator аналогично `SECRET_KEY` |
| TD-017 | 🧪 | `alembic.ini` | Placeholder URL в `sqlalchemy.url` | Убрать или заменить на комментарий |
| TD-022 | 🧪 | `auth/schemas.py` | `balance_cents` в `AuthResponse` — всегда 0 до платежей | Убрать или оставить осознанно |
| TD-024 | 🧪 | `users/models.py` | `User` не наследует `JSONBMixin` для `credentials` | Добавить при первой ORM-мутации `credentials` |
| TD-F7-W5 | 🧪 | `masters/models.py` | `payout_details: dict` — содержимое не типизировано | Создать `PayoutDetailsDict` TypedDict |
| TD-W01 | 🧪 | `bookings/service.py` | Нет cron для экспирации `NOTIFIED` waitlist-записей | Cron job или processor расширить |
| PERF-04 | 🚀 | `notifications/service.py` | `_resolve_target_users` для ALL и ROLE загружает все user IDs в память | Batched processing при росте базы (10k+) |

---

## 10. Phase 9 (не начата)

| Задача | Статус | Описание |
|--------|--------|----------|
| AI-розетка | ✅ Заготовка | `app/modules/ai/interface.py` (Protocol) + `mock.py`, эндпоинт `GET /practices/{id}/ai-summary` возвращает placeholder |
| Library-розетка | ✅ Заготовка | Модель `Recording` (закомментирована) + TODO в коде |
| E2E-тестирование | ❌ | Основные flow: auth → practice → booking → payment → checkin → feedback → withdrawal |
| Load testing | ❌ | — |
| Security audit | ❌ | — |

---

## 11. Розетки

Заготовки, намеренно не реализованные в MVP. Интерфейсы определены, чтобы будущая реализация не ломала архитектуру.

### 11.1. AI-саммари

```python
# app/modules/ai/interface.py
class AIService(Protocol):
    async def generate_summary(
        self,
        practice_id: UUID,
        checkins: list[Checkin],
        feedbacks: list[Feedback],
    ) -> str: ...
```

### 11.2. Library (Записи практик)

Будущие таблицы: `recordings` (метаданные) + S3 для файлов. В коде — TODO-комментарии.

### 11.3. Подписки

Таблица `subscriptions` спроектирована, логика не реализована:

```python
class Subscription:
    plan: Enum          # monthly | yearly
    status: Enum        # active | cancelled | expired
    stripe_subscription_id: str
```

### 11.4. OAuth (Google, Apple)

`User.credentials` — JSONB, структура поддерживает несколько провайдеров:

```json
{
  "telegram": {"id": 123456789},
  "google":   {"id": "...", "email": "..."},
  "apple":    {"id": "..."}
}
```

---

**Конец документа**
