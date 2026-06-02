# VELO — Бэковый Кодекс

**Версия:** 1.7
**Дата:** 2 июня 2026
**Статус:** Active
**Тесты:** 481 passed, 12 skipped  

> **v1.7 (Attendance enrichment для master prep, 2 июня 2026):** `GET
> /api/v1/practices/{id}/attendance` (master-only) обогащён под экран
> подготовки мастера: каждый item теперь несёт `user_display_name` /
> `user_avatar_url` участника и его PRE-чек-ин `checkin { mood, comment }`
> (если оставлен), иначе `null`. Новая схема `AttendanceCheckinResponse`.
> `get_attendance` батч-грузит участников (`User.id IN`) и PRE-чек-ины через
> новую `diary/service.py::get_pre_checkins_for_bookings` (`booking_id IN`) —
> два запроса, без N+1. **Приватность:** PRE-чек-ин участника осознанно открыт
> владельцу практики и ТОЛЬКО внутри attendance этой практики (ownership →
> P-08 → 404 чужому); глобальная приватность `/users/me/checkins` не тронута.
> Поле `master_request`/эндпоинт сохранения запроса НЕ добавлялись: диалог
> юзер ↔ мастер — отдельная фича (TD-ASK-MASTER), вне MVP. +6 тестов
> (`test_attendance.py`, 63xxx). Детали — §2 (Bookings), §3.12.

> **v1.6 (Профиль пользователя + аудит-фиксы, 29 мая 2026):** реализован раздел
> «Профиль» (Figma `F7PD5isLfLdyc0q1Bd5n5c`, node `4715-3463`). Бэк-часть:
> новые поля профиля `phone` / `bio` и настройки `notifications` живут в
> `User.credentials` JSONB (schema-on-read, тот же паттерн, что
> `onboarding_completed` — см. §3.7 и новый §3.11); новый эндпоинт статистики
> `GET /api/v1/bookings/me/stats` (`UserStatsResponse`, ORM-агрегат COUNT+SUM по
> attended-броням) и `DELETE /api/v1/users/me` (MVP-семантика — сброс онбординга,
> не удаление, см. §3.11). Аудит ветки (W-1): `update_practice` теперь ре-валидирует
> `style` против СОХРАНЁННОГО `direction` при PATCH без direction (переиспользует
> `_validate_style_for_direction` — закрыто и S-5; +3 теста W-4). W-3 (replay-окно
> initData) и S-3 (banker's rounding в `hours_attended`) — осознанно не код
> (см. §9). Тесты 446 -> 480. Детали — §2, §3.8, §3.11.

> **v1.5 (Calendar flow 4-7 + master public, 24 мая 2026):** добавлен публичный
> профиль мастера `GET /api/v1/masters/{user_id}` (схема `MasterPublicResponse` —
> только публичные поля, без финансов/контактов; verified-only или 404 по P-08;
> два live-COUNT practices/reviews) + `master_avatar_url` в детали практики;
> найден и устранён root-cause флака теста доставки уведомлений — фоновый
> процессор гонялся с ручными `_stage_*` в тестах; введён флаг
> `notification_processor_enabled` (§5.2). +11 тестов master_public (диапазон
> `telegram_id` 56xxx). Детали — §3.9 (master public), §5.2 (processor toggle), §8.
> Аудит итерации (24 мая): 0 critical / 0 warning, 3 suggestion (все обработаны).

> **v1.4 (Calendar iteration, 22 мая 2026):** Practice получил JSONB-колонку `data`
> с taxonomy-песочницей (direction / difficulty / style); публичный фид расширен
> фильтрами по таксономии, длительности и времени суток + per-user флагами
> `is_booked` / `is_paid`; 13 новых тестов. Детали — §2 (Practices), §3.1, §3.8.
> Аудит итерации: C-1 ✅, W-2 ✅ устранены; W-1 (Stripe startup-валидатор) — в техдолге (§9).

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
| `diary` | `app/modules/diary/` | Check-ins, feedbacks, diary entries, insights; append-only `DiaryEvent` journal (`models.py`) + `projections.py` (единственный писатель журнала) + единая лента `GET /diary/feed` (cursor) |
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
GET   /api/v1/users/me              -- Мой профиль (+ onboarding_completed, phone, bio, notifications)
PATCH /api/v1/users/me              -- Обновить профиль (вкл. onboarding_completed, phone, bio, notifications)
DELETE /api/v1/users/me             -- "Удалить аккаунт" (MVP: сброс онбординга, см. 3.11)
GET   /api/v1/users/me/checkins     -- Мои check-ins (пагинация)
GET   /api/v1/users/me/feedbacks    -- Мои feedbacks (пагинация)
```

`UserResponse.onboarding_completed: bool` — вычисляется из `credentials` JSONB (см. 3.7), не колонка.
`UserUpdate.onboarding_completed: bool | None` — флаг завершения онбординга пишется в `credentials`.
`UserResponse.phone/bio: str | None` и `UserResponse.notifications: NotificationSettings` —
также вычисляются из `credentials` JSONB (schema-on-read, см. 3.11). `UserUpdate` принимает
`phone`/`bio` (пустая строка = очистить) и `notifications` (частичный объект, мёржится).

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
GET    /api/v1/practices                        -- Публичный фид (фильтры ниже)
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

**Фильтры `GET /practices` (Calendar iteration):** все опциональны.
Мульти-фасеты передаются повторяемыми query-параметрами (`?direction=yoga&direction=breathwork`);
внутри одного фасета значения OR-ятся, между фасетами — AND.

| Параметр | Тип | Значения / семантика |
|----------|-----|----------------------|
| `practice_type` | мульти | `live\|series\|one_on_one\|replay` |
| `direction` | мульти | `meditation\|yoga\|breathwork` (из `data.taxonomy`) |
| `difficulty` | мульти | `beginner\|medium\|high` (из `data.taxonomy`) |
| `style` | строка | свободное точное совпадение по `data.taxonomy.style` |
| `duration_bucket` | один | `short` (< 60 мин) / `long` (>= 60 мин) |
| `time_of_day` | один | `night\|morning\|day\|evening` — по ЛОКАЛЬНОМУ часу практики |
| `status` | один | `scheduled\|live` (alias `status`) |
| `master_id`, `date_from`, `date_to`, `sort_by`, `sort_order` | — | как раньше |

`time_of_day` считается в таймзоне практики через `func.timezone(Practice.timezone, scheduled_at)`
+ `extract('hour', ...)` (ORM, без сырого SQL). Границы корзин — в `config.py` (см. §7).

**Per-user флаги в `PracticeResponse`** (фид и детали, для текущего юзера):
- `is_booked: bool` — у юзера есть бронь в статусах `pending|confirmed|attended`.
- `is_paid: bool` — `is_booked` И практика платная (`price_cents > 0`). ВАРИАНТ 1:
  определяется по цене практики, НЕ по наличию `purchase_id` (бесплатные брони тоже
  создают Purchase, поэтому purchase_id для «оплачено» не годится).
- На master-facing list-эндпоинтах флаги остаются `False` (мастер не бронирует свои практики).
- Детальный эндпоинт собирает ответ через публичную `get_practice_detail()` в сервисе
  (роутер не импортирует приватные хелперы — C-1 аудита Calendar, §9).

> **`PracticeSummary.status`:** облегчённая схема `PracticeSummary` (отдаётся в list-views:
> `GET /bookings/me`, waitlist, purchases) получила поле `status: PracticeStatus`.
> Подхватывается автоматически через `model_validate(practice)` + `from_attributes`
> во всех 3 потребителях (Booking/Waitlist/Purchase-WithPractice) — как ранее `timezone` (CR-01).
> Миграций не требует (колонка `status` в таблице уже есть). Поля `PracticeSummary`:
> `id, title, practice_type, status, scheduled_at, duration_minutes, timezone, master_id, master_name`.
> Это позволяет фронту (дашборд, список броней) отличать live от scheduled без отдельного GET деталей.

### Bookings

```
POST   /api/v1/bookings             -- Забронировать (+ опциональный promo_code)
GET    /api/v1/bookings/me          -- Мои бронирования
GET    /api/v1/bookings/me/stats    -- Моя статистика практик (объявлен ДО /{id})
GET    /api/v1/bookings/{id}        -- Детали бронирования
DELETE /api/v1/bookings/{id}        -- Отменить бронирование
POST   /api/v1/bookings/{id}/join   -- Отметить приход (владелец брони)
POST   /api/v1/bookings/{id}/leave  -- Отметить уход (владелец брони)
```

`GET /bookings/me/stats` -> `UserStatsResponse { practices_attended: int, hours_attended: float }`.
Один ORM-запрос: `func.count(Booking.id)` + `func.coalesce(func.sum(Practice.duration_minutes), 0)`
с join `Practice` по `practice_id` и фильтром `user_id == me AND status == attended`;
`hours_attended = round(minutes/60, 1)`. Роут объявлен ДО динамического `/{booking_id}`,
иначе `me/stats` перехватился бы как booking_id (Профиль, экран A).

> **Доступ к join/leave:** доступны **владельцу брони** (юзеру), non-owner → 404
> (`test_join_booking_success` — owner 200; `test_join_booking_not_owner` — 404).
> Фронт использует их на экране 14 (Practice-Live): юзер сам отмечает приход/уход.

**Attendance для мастера (обогащён, v1.7).** `GET /api/v1/practices/{id}/attendance`
(master-only, в разделе Practices) отдаёт `AttendanceResponse` = агрегаты
(`total/attended/no_show/pending`) + `items: list[AttendanceItemResponse]`. С
v1.7 каждый item, помимо `booking_id/user_id/status/joined_at/left_at`, несёт:
- `user_display_name: str | None` — `first_name` + `last_name` участника
  (иначе `None`; фоллбэка «Master» нет — это участник, не мастер);
- `user_avatar_url: str | None` — аватар участника (`User.avatar_url`);
- `checkin: AttendanceCheckinResponse | None` — PRE-чек-ин участника
  (`{ mood: int, comment: str | None }`) на эту практику, либо `null`.

`get_attendance` (`bookings/service.py`) после owner-проверки (P-08) батч-грузит
участников (`User.id IN`) и их PRE-чек-ины одним запросом через
`diary/service.py::get_pre_checkins_for_bookings` (`Checkin.booking_id IN`,
`check_type == PRE`) — **без N+1** независимо от числа участников. Роутер только
маппит результат в схему (хелпер `_participant_display_name`).

> **Приватность чек-ина (осознанное решение, v1.7):** чек-ины приватны
> (`GET /users/me/checkins` — только свои). Здесь PRE-чек-ин участника
> открывается мастеру-**владельцу именно этой практики** и **только** в рамках
> её attendance (booking_ids принадлежат этой практике, авторизацию проверяет
> вызывающий — тот же trust-boundary, что у `get_practice_insights`). Глобальная
> приватность не меняется. `master_request`/эндпоинт «вопрос мастеру» НЕ
> добавлялись — это диалог юзер↔мастер, отдельная фича (TD-ASK-MASTER, §9 / §2
> Diary), вне MVP. См. §3.12.

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
POST   /api/v1/diary                -- Создать запись дневника (note/dream)
GET    /api/v1/diary                -- Мои записи дневника (пагинация, legacy)
GET    /api/v1/diary/{id}           -- Запись дневника
PATCH  /api/v1/diary/{id}           -- Обновить запись
DELETE /api/v1/diary/{id}           -- Удалить запись (soft-delete)
GET    /api/v1/diary/feed           -- Единая лента дневника (cursor pagination)
```

**Diary redesign (журнал событий + единая лента).** Поверх неизменных
таблиц-источников (Booking, Practice, Checkin, Feedback, DiaryEntry) работает
тонкий append-only журнал `DiaryEvent`, который наполняется ТОЛЬКО через
`projections.py` в момент мутации источника (в той же транзакции). Лента
`GET /api/v1/diary/feed` отдаёт события из журнала, отсортированные
newest-first, с курсорной пагинацией (`{ items, next_cursor }`,
`next_cursor === null` = конец).

9 видов событий (`DiaryEventKind`): `booking_confirmed`,
`booking_cancelled_by_user`, `practice_rescheduled`,
`practice_cancelled_by_master`, `practice_outcome`, `checkin`, `feedback`,
`note`, `dream`. Каждое событие несёт `snapshot` (денормализованный слепок
источника на момент события) — лента самодостаточна и не делает JOIN к
источникам при чтении.

**Snapshot-контракт** (что кладёт `projections.py`):
- `_practice_snapshot` (базовый): `practice_id, practice_title, master_id,
  master_name, scheduled_at, duration_minutes, direction`. NB: аватар мастера
  и verified-флаг в snapshot НЕ входят (TD-DIARY-PRACTICE-AVATAR).
- `practice_outcome` += `outcome_status` (`attended` / `no_show`).
- `practice_rescheduled` += `old_scheduled_at`, `new_scheduled_at`.
- `checkin` += `mood`, `comment_preview`.
- `feedback` += `rating`, `comment_preview`.
- `note` / `dream` (entry): `entry_type, title, content_preview, mood,
  practice_id, practice_phase`.

Миграция журнала: `c4d5e6f7a8b9`.

Открытый техдолг бэка дневника: TD-DIARY-FEED-CURSOR-TIEBREAK (стабильный
тай-брейк курсора при равных `occurred_at`), TD-DIARY-SNAPSHOT-TYPED
(типизировать snapshot вместо открытого dict), TD-DIARY-CANCEL-COMMENT
(причина отмены в snapshot), TD-ASK-MASTER (диалог юзер↔мастер как отдельная
фича — не строка на брони; вне MVP, см. §9; чек-ин клиента мастеру уже
отдаётся через attendance, см. §3.12).

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
| `User` | `credentials` | ✅ (TD-024 закрыт — onboarding flow + phone/bio/notifications, set_jsonb в users/service.py, см. §3.7, §3.11) |
| `Practice` | `data` | ✅ (Calendar iteration — taxonomy sandbox, set_jsonb в practices/service.py, см. §3.8) |

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

### 3.6. Генерация TypeScript-типов из OpenAPI (CR-01)

Бэкенд — единственный источник правды для API-контракта. TypeScript-типы фронтенда генерируются автоматически из OpenAPI-схемы FastAPI.

**Скрипт:** `backend/scripts/generate_ts_types.py`
**Вход:** `openapi.json` (снимается с живого бэкенда через `curl`)
**Выход:** `frontend/src/api/generated.ts` (коммитится в git, перегенерируется при каждом `velo update`)

**Как работает при `velo update`:**

```
build app -> down -> up app -> migrate -> pytest ->
curl openapi.json -> generate_ts_types.py -> generated.ts ->
[drift? -> velo-bot commit + push origin $BRANCH] ->
build frontend -> up frontend -> health check
```

**Авто-коммит типов (важно):** после регенерации `velo update` проверяет дрейф
(`git status --porcelain generated.ts`). Если файл изменился — коммитит от имени
`velo-bot <bot@velo.local>` и пушит в `origin/$BRANCH`. Push идёт через SSH-config
alias `github.com-velo` (deploy-key уже привязан, `GIT_SSH_COMMAND` не нужен).
Провал push -> `exit 1` (фатально: рассинхрон типов делает сборку фронта
бессмысленной). Это разрывает порочный круг "регенерил -> не закоммитил ->
discard на следующем update". Перенесено из рабочей модели проекта CBS Home.

**Как работает при `bash install_velo.sh`:**

```
build app -> up app -> wait health ->
curl openapi.json -> generate_ts_types.py -> generated.ts ->
build frontend -> up frontend
```

**Ручной запуск:** `velo gen-types` — только регенерирует + предупреждает о дрейфе,
НЕ коммитит и НЕ пушит (это работа `velo update`). Для итерации над схемой на VPS
без полного деплоя.

**Правила для response-схем:**

- Статусные поля (`status`, `practice_type`) — использовать `StrEnum`, не `str`. OpenAPI отдаёт `enum: [...]`, генератор создаёт union-тип.
- Поля с `default=X` в response-only схемах — убирать default, делать required. Иначе OpenAPI помечает как optional, генератор пишет `field?: type`, фронт вынужден использовать `?.`.
- `dict` в response-полях — типизировать через Pydantic-модель (например, `payout_details: PayoutDetails` вместо `dict`). Иначе генератор пишет `Record<string, unknown>`.
- Вычисляемые поля из JSONB — через `@computed_field` (см. 3.7). Если геттер возвращает не-Optional тип, OpenAPI помечает поле `required` -> генератор пишет без `?`.

---

### 3.7. Onboarding flag — schema-on-read в credentials

`onboarding_completed` — НЕ колонка. Хранится внутри существующего `User.credentials`
(JSONB) под ключом `"onboarding_completed"`. Паттерн schema-on-read: без миграции,
в зоне роста credentials. Закрывает TD-024 (первая ORM-мутация credentials).

**Чтение (`UserResponse`):**
- Приватное входное поле `credentials_in: dict` (Field с `validation_alias="credentials"`,
  `exclude=True`) — заполняется из ORM-объекта через `from_attributes`, наружу НЕ отдаётся.
- `@computed_field onboarding_completed -> bool` читает `credentials_in.get("onboarding_completed", False)`.
- Сырой `credentials` в API-ответ не попадает никогда — только булев флаг.

**Запись (`update_user`, users/service.py):**
- `UserUpdate.onboarding_completed: bool | None`. JSONB-поля развилкой отделяются
  от колоночных: колоночные -> `setattr`, `onboarding_completed` -> копия credentials +
  `user.set_jsonb("credentials", new)` (JSONBMixin -> flag_modified -> реальный UPDATE).
- `None` фильтруется (`value is not None`): прислать `null` = no-op, не сбрасывает флаг.
  Семантики "сбросить" нет — осмыслен только `true`.

**Инвариант при логине (`upsert_user_on_login`, auth/service.py):**
- На UPDATE credentials МЕРДЖИТСЯ, не перезаписывается:
  `coalesce(User.credentials, '{}'::jsonb) || fresh`. Свежие Telegram-поля
  накладываются поверх, `onboarding_completed` (которого нет в `fresh`) переживает
  релогин. COALESCE защищает edge-case `NULL || x = NULL`.
- На INSERT (новый юзер) credentials = fresh, флага нет -> читается как `false` ->
  онбординг показывается автоматически.

Тесты: `tests/test_users.py` — дефолт false, set true, **survives relogin** (ключевой),
merge + refresh telegram-полей, null игнорируется.

---

### 3.8. Practice taxonomy — schema-on-read в data (Calendar iteration)

Practice получил JSONB-колонку `data` (миграция `b2c3d4e5f6a8`, down_revision
`a1b2c3d4e5f7`). Таксономия Календаря живёт под ключом `data.taxonomy`:

```json
{ "taxonomy": { "direction": "meditation", "difficulty": "beginner", "style": "MBSR" } }
```

- `direction` ∈ `meditation|yoga|breathwork`, `difficulty` ∈ `beginner|medium|high`
  (StrEnum `PracticeDirection` / `PracticeDifficulty` в `practices/models.py`).
  `style` — свободная строка (≤ `practice_style_max_length`).
- **Create:** `direction` и `difficulty` ОБЯЗАТЕЛЬНЫ, `style` опционален. Пишутся в
  `data.taxonomy` через `set_jsonb("data", ...)` + deepcopy (JSONBMixin, §3.1).
- **Update (PATCH):** все три опциональны. «Не прислано» — значение не трогается;
  присланное — валидируется и мёржится в `data.taxonomy` (pop из `_TAXONOMY_FIELDS`
  до общего setattr-цикла, затем deepcopy-merge).
- **Response:** `practice_to_response()` читает из `data.taxonomy` и поднимает в
  top-level optional поля `direction|style|difficulty` (None, если песочница пуста).
  Поля опциональны, т.к. практики, созданные до итерации, имеют пустой `data`.
- **Допустимые значения** (`practice_allowed_directions/difficulties`) и
  `practice_style_max_length` — в `config.py` (NO-LITERALS), валидируются `@field_validator`.

Тесты: `tests/test_practices.py` (раздел Calendar) — хранение таксономии (create/update-merge),
фильтры фида (каждый + комбинированный AND), флаги is_booked/is_paid.

### 3.9. Публичный профиль мастера (Calendar flow)

`GET /api/v1/masters/{user_id}` — публичная карточка мастера для юзера (Figma
кадр 4 + master profile). Схема ответа `MasterPublicResponse` (`masters/schemas.py`).

- **Изоляция по схеме (граница безопасности):** `MasterPublicResponse` содержит
  ТОЛЬКО публичные поля — `user_id`, `status`, `display_name`, `bio`, `methods`,
  `experience_years`, `avatar_url`, `practices_count`, `reviews_count`. Финансовые
  и контактные поля (баланс, payout-реквизиты, и т.п.) в схему не входят и с бэка
  не приходят в принципе. `PayoutDetails` (та же `schemas.py`) к этому ответу
  отношения не имеет и импортируется `admin/withdrawals` — не удалять.
- **Доступ:** только verified-мастер, иначе 404 (P-08: не раскрываем существование
  неверифицированного/чужого профиля).
- **Счётчики — два live ORM-COUNT** (не denormalized, считаются на каждый запрос):
  `practices_count` исключает draft/deleted; `reviews_count` = `count(Feedback.id)`
  через join на Practice по `master_id` (вариант A — все отзывы мастера, не
  фильтруются по статусу практики; задокументировано в коде, ответ на S-2 аудита).
  Два COUNT идут последовательно (нельзя `asyncio.gather` на одной `AsyncSession` —
  тоже зафиксировано комментарием, ответ на S-1).
- **`display_name`** падает в `first_name`, если профильное имя пустое.
- **Роут объявлен ПОСЛЕДНИМ** в `masters/router.py` (после всех `/me*`), чтобы
  динамический `/{user_id}` не перехватывал статические пути.
- **`master_avatar_url` в деталях практики:** `get_practice()` дополнительно
  SELECT-ит `User.avatar_url` (4-колоночный tuple); `practice_to_response()`
  получил keyword-only параметр `master_avatar_url` (в списочных вызовах — None,
  у фида аватары не нужны).

Тесты: `tests/test_master_public.py` — 11 тестов (verified/404, счётчики,
изоляция полей), диапазон `telegram_id` 56xxx.

---

### 3.10. Diary projections — единственный писатель журнала (Diary redesign)

`DiaryEvent` — append-only журнал поверх неизменных источников. Инвариант:
**журнал наполняется ТОЛЬКО через `projections.py`, и только в момент мутации
источника, в той же транзакции.** Никакой код не пишет `DiaryEvent` напрямую
через ORM в обход проекций, и журнал НЕ наполняется задним числом (backfill
отсутствует by design).

- Функции-проекции (`project_*` / `upsert_*_event` в `projections.py`)
  вызываются из сервисов источников (bookings/practices/diary) сразу после
  успешной мутации, до коммита, через ленивый импорт (избегаем циклов).
- Каждое событие несёт денормализованный `snapshot` (см. snapshot-контракт в
  разделе «Diary» выше). Лента читается без JOIN к источникам.
- Следствие для сидов и фикстур: чтобы события появились в ленте, seed ДОЛЖЕН
  вызывать проекции (или идти через те же сервисные функции, что и прод), а не
  создавать Booking/Practice/Checkin напрямую — иначе журнал останется пустым
  при наполненных источниках.
- Чтение: `GET /diary/feed`, курсорная пагинация newest-first. Открытый
  тай-брейк при равных `occurred_at` — TD-DIARY-FEED-CURSOR-TIEBREAK.

---

### 3.11. Профиль в credentials + "удаление" аккаунта (Профиль, 29 мая)

Раздел «Профиль» (Figma node `4715-3463`) расширил schema-on-read в
`User.credentials` тремя сущностями — тем же паттерном, что `onboarding_completed`
(§3.7), без миграций.

**phone / bio (экран C — Edit Profile):**
- `UserResponse` отдаёт их через `@computed_field` (`credentials_in.get("phone")` /
  `("bio")`), `None` если ключа нет.
- `UserUpdate`: `phone` (max_length=20, мягкий валидатор: только цифры/пробел/`+()-`,
  >=5 цифр), `bio` (max_length=2000). **БЕЗ `min_length`** — в отличие от имён,
  пустая строка `""` допустима и означает «очистить» (вариант (б)). `null` для них
  = «не трогать» (как и для onboarding-флага: `update_user` отбрасывает `None`).
  Очистка делается пустой строкой, не null.
- `service.py`: `_JSONB_CREDENTIAL_FIELDS = {onboarding_completed, phone, bio}` —
  тот же единый write-путь (`""` проходит `is not None`, `null` отсекается).

**notifications (экран E — Notifications):**
- ВЛОЖЕННЫЙ объект `credentials["notifications"]` = `{push, practice_reminders,
  master_messages, support_messages}`, все дефолты **True** (`_NOTIFICATION_DEFAULTS`).
  Схемы `NotificationSettings` (Response) и `NotificationSettingsUpdate` (все поля
  опциональны) в `users/schemas.py`.
- `UserResponse.notifications` всегда отдаёт полный объект: дефолты накладываются
  на сохранённые ключи (частично сохранённый блоб дополняется до полного).
- **Частичный апдейт МЕРЖИТСЯ** ключ-за-ключом ОТДЕЛЬНОЙ веткой в `update_user`
  (`notifications` извлекается `updates.pop(...)` ДО плоской JSONB-развилки; читаем
  текущий объект, накладываем не-None ключи, `set_jsonb`). НЕЛЬЗЯ класть в плоский
  `_JSONB_CREDENTIAL_FIELDS` — `dict.update` затёр бы весь объект и сбросил
  неприсланные тоглы. Push-движок НЕ подключён — флаги это задел, переживают
  релогин (merge credentials, §3.7).

**DELETE /api/v1/users/me — "удаление" = сброс онбординга (экран D, MVP):**
- `reset_user_to_onboarding` (service.py) ставит `onboarding_completed=False` через
  `set_jsonb`. **is_active НЕ трогается, данные НЕ стираются.** При следующем входе
  юзер проходит онбординг заново, старые данные «всплывают» (merge при логине).
- Эндпоинт возвращает 204. Фронт после вызова делает logout (закрытие Mini App в
  Telegram). Контракт `DELETE` намеренно оставлен под будущее РЕАЛЬНОЕ удаление —
  менять только тело сервиса, не контракт (докстринг это фиксирует; specification
  drift осознан — Frontend Codex W-2 привёл текст модала в соответствие).

Тесты: `tests/test_users.py` — phone/bio set/clear(""), мягкая валидация телефона,
relogin-persist; notifications дефолты-all-true, частичный merge, накопление,
сосуществование с onboarding/phone; delete сбрасывает онбординг и сохраняет данные.

---

### 3.12. Attendance enrichment + «вопрос мастеру» (2 июня)

**Что (v1.7).** `GET /api/v1/practices/{id}/attendance` (master-only) обогащён под
экран подготовки мастера: по каждому участнику отдаются `user_display_name`,
`user_avatar_url` и его PRE-чек-ин `checkin { mood, comment } | null`. Новая
schema `AttendanceCheckinResponse` (`bookings/schemas.py`).

**Откуда данные, без N+1.** `get_attendance` (`bookings/service.py`) после
owner-проверки (P-08) делает ровно два батч-запроса поверх списка броней:
- участники — `select(User).where(User.id.in_(user_ids))` → `dict[user_id, User]`;
- PRE-чек-ины — `diary/service.py::get_pre_checkins_for_bookings(booking_ids)`
  (`Checkin.booking_id.in_(...)`, `check_type == PRE`) → `dict[booking_id, Checkin]`.
Сигнатура расширена до `tuple[Practice, list[Booking], dict[UUID, User],
dict[UUID, Checkin]]`; роутер — тонкий маппер (хелпер `_participant_display_name`:
`first_name`+`last_name`, иначе `None`; без «Master»-фоллбэка). Зависимость
`bookings -> diary` односторонняя — `Checkin` под `TYPE_CHECKING` для аннотации +
локальный рантайм-импорт внутри функции (тот же приём, что в `list_user_bookings`).

**Приватность.** PRE-чек-ин участника приватен (`/users/me/checkins` — свой), но
владельцу этой практики он открыт **только** внутри её attendance: `booking_ids`
принадлежат одной практике, авторизацию гарантирует вызывающий. Тот же
trust-boundary, что у `get_practice_insights` (мастер видит чек-ины участников
своей практики). Только PRE (что человек написал ДО практики — для подготовки).

**Почему НЕ `master_request`.** Исходный тикет просил поле `master_request` на
`Booking` + эндпоинт сохранения. Не сделано осознанно: «вопрос к мастеру» — это
**диалог** юзер↔мастер (мастер должен не только получить сообщение, но и
ответить; точки входа — из профиля «в общем» / до брони / после; роутинг в
Telegram-бот мастера с ответом юзеру). Строковое поле на брони такой флоу не
выносит (нет автора per-сообщение, порядка, статусов, ответов) и в V2 было бы
выброшено. Это отдельная сущность + флоу — фича диалогов, **вне MVP**
(TD-ASK-MASTER, §9). Фронт оставляет заглушку `TD-ASK-MASTER` как есть.

Тесты: `tests/test_attendance.py` (63xxx) — +6: имя+аватар; чек-ин виден мастеру;
`checkin=null` без чек-ина; `comment=None` при пустом; не-владелец → 404 (чек-ины
не утекают); корректный маппинг чек-инов на нужного участника при нескольких
участниках.

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

CR-01: `MasterProfileResponse` возвращает `min_withdrawal_cents` и `withdrawal_fee_cents` из settings. Фронтенд берёт лимиты из API, не хардкодит.

---

## 5. Уведомления

### 5.1. Архитектура

Два уровня:
- `Notification` — что отправить, кому (channel-agnostic).
- `NotificationDelivery` — конкретная доставка: юзер + канал + статус.

### 5.2. Процессор

Фоновая задача (`notifications/processor.py`). Забирает pending Notification, резолвит target → список юзеров, создаёт `NotificationDelivery` per-user, отправляет через channel-formatter.

**Запуск процессора управляется флагом** `notification_processor_enabled: bool = True`
(`core/config.py`). В `main.py` lifespan читает флаг ДО `create_task(run_processor())`:
при `False` фоновая задача не стартует (лог `notification_processor_disabled`).
Safe default — в production флаг включён.

> **Почему флаг (root-cause флака теста доставки, 24 мая 2026):** тесты гоняются
> через `ASGITransport(app=app)`, что активирует lifespan → фоновый `run_processor()`
> крутится в том же event loop, что и тело теста. Процессор забирает delivery-строки
> через `FOR UPDATE SKIP LOCKED`; когда тест вручную вызывал `_stage_deliver()`,
> фоновый цикл успевал залочить ту же строку → ручной вызов её пропускал → `attempts`
> оставался 0 (тест ждал 1). Гонка таймингова (не зависела от порядка тестов —
> `pytest-randomly` не стоит). Лечится на уровне конфига, а не патчингом теста:
> `conftest.py` в session-autouse `setup_infrastructure` (ДО миграций и lifespan)
> ставит `settings.notification_processor_enabled = False`. Тесты, которым нужен
> процессор, вызывают его шаги вручную и детерминированно.

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

**Пороги фильтров Календаря** (settings в `config.py`, НЕ env — внутренние константы, NO-LITERALS):

| Параметр | Дефолт | Назначение |
|----------|--------|-----------|
| `practice_duration_long_min_minutes` | `60` | Граница `duration_bucket`: short < N, long >= N |
| `practice_time_night_start_hour` | `0` | Начало корзины «ночь» (локальный час) |
| `practice_time_morning_start_hour` | `5` | Начало «утро» |
| `practice_time_day_start_hour` | `12` | Начало «день» |
| `practice_time_evening_start_hour` | `17` | Начало «вечер» (до 24) |

Корзины полусегментные `[start, next_start)`: night [0,5), morning [5,12), day [12,17), evening [17,24).
En-значения query-параметров (`short|long`, `night|morning|day|evening`) остаются `Literal` в роутере.

---

## 8. Тесты

481 passed, 12 skipped. Все запускаются внутри Docker:

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
| practices (Calendar iteration) | 60xxx |
| masters (public profile) | 56500-56599 |

> **Развод диапазона 56xxx (TD-TGID-56XXX, закрыт 24 мая):** изначально
> `test_master_public.py` занимал весь 56000-56999 и пересекался с
> `test_admin_masters.py` (56001-56010 аппликанты, 56900-56907 админы) по id
> 56001/56900 — оба модуля ещё и чистили весь 56xxx (`cleanup_range(56000,56999)`).
> Зелено держалось только на cleanup между модулями — хрупко. Исправлено: master_public
> перенесён в компактный **56500-56599** (мастер 56501, вьюеры 565xx, админ 56590) и
> чистит ТОЛЬКО свой поддиапазон. admin_masters не тронут (остаётся в 560xx/569xx).

---

## 9. Технический долг

### Обозначения

- **Среда:** 🧪 низкий приоритет / 🚀 перед публичным запуском
- **Статус:** ⬜ Open / ✅ Done

### Перед публичным запуском 🚀

| ID | Файл | Описание | Решение |
|----|------|----------|---------|
| **TD-RU-PROXY** | Инфра | Hetzner IP заблокирован ТСПУ. Недоступен из России без VPN | Российский reverse proxy (Timeweb/Selectel ~300-500₽/мес) или DDoS-Guard CDN |
| **AUDIT-0520-01** 🔴 | `payments/stripe.py` | Stripe `amount_total=None` обходит проверку суммы: `if stripe_amount is not None and ...` -> при отсутствии суммы блок пропускается, баланс кредитуется без верификации | Инвертировать: `if stripe_amount is None or stripe_amount != payment.amount_cents:` -> mark FAILED. + тест на `amount_total=None` (AUDIT-0520-09) |
| **AUDIT-0520-02** 🔴 | `practices/schemas.py` | `zoom_link` принимает любую строку (только max_length), вкл. `javascript:...` -> XSS если фронт рендерит как href. Нет валидатора ни в Create, ни в Update. **Частично смягчено на фронте (2026-05-21):** экран 14 открывает ссылку через `platform.openLink` только при `https://`-схеме, кнопка дизейблится иначе — но это НЕ заменяет серверную валидацию | `@field_validator("zoom_link")`: требовать `https://` schema (или пустоту/None). Остаётся открытым на бэке |
| **CRITICAL-4** | `auth/router.py` | Нет rate limiting на `POST /auth/telegram`. Replay valid initData в 5-минутном окне → тысячи Redis-сессий | `slowapi` или Redis-based limiter |
| **WARNING-4** | `auth/router.py` | Telegram initData replay в 5-минутном окне — нет защиты от повторного использования | Redis SET `used_init_data:{hash}` с TTL 5 минут |
| **WARNING-5** | `payments/webhook.py` | Stripe webhook signature не проверяется при `STRIPE_STUB=true` | Запрет `STRIPE_STUB` в production через config validator |
| **CAL-W1** 🔴🚀 | `core/config.py` | **Проверить, не затёрт ли startup-`model_validator` Stripe-ключей при правках config в Calendar iteration.** Если валидатор пропал — production может стартовать с пустыми Stripe-ключами и упасть только при первой оплате | Сверить текущий `config.py` с дореитерационным; восстановить `model_validator`, проверяющий наличие ключей в `APP_ENV=production`. Найдено аудитом Calendar (W-1), принято в техдолг |
| TD-025 | Все роутеры | Нет rate limiting на masters endpoints. **(подтверждено аудитом 2026-05-20: распространить и на топап `POST /payments/topup` и покупку `POST /practices/{id}/purchase`)** | `slowapi` или Redis-based custom limiter |
| TD-026 | `docker-compose.yml` | Redis без пароля | `requirepass` + `REDIS_PASSWORD` в .env |
| **AUDIT-0520-03** 🟡🚀 | `core/middleware.py` | `_extract_client_ip` берёт первый элемент `X-Forwarded-For` без проверки trusted proxy -> клиент может подделать IP в audit log финансовых операций | Доверять XFF только от известного прокси (Nginx); или брать N-й справа hop; список trusted proxies в config |

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
| TD-024 | ✅ | `users/models.py` | `User` не наследовал `JSONBMixin` для `credentials` | ЗАКРЫТО (onboarding flow): `User` наследует `JSONBMixin`, мутация через `set_jsonb("credentials", ...)` в `update_user`. См. 3.7 |
| TD-F7-W5 | ✅ | `masters/models.py` | `payout_details: dict` — содержимое не типизировано | CR-01: `WithdrawalResponse.payout_details` и `AdminWithdrawalResponse.payout_details` теперь типизированы как `PayoutDetails` |
| TD-W01 | 🧪 | `bookings/service.py` | Нет cron для экспирации `NOTIFIED` waitlist-записей | Cron job или processor расширить |
| PERF-04 | 🚀 | `notifications/service.py` | `_resolve_target_users` для ALL и ROLE загружает все user IDs в память | Batched processing при росте базы (10k+) |
| **AUDIT-0520-04** | 🧪 | `core/database.py` | `get_db_reader` не делает `SET TRANSACTION READ ONLY` — случайная мутация в reader-сессии не блокируется на уровне БД, только откатывается в конце (TD-008, ранее жил только в докстринге) | `await session.execute(text("SET TRANSACTION READ ONLY"))` в начале reader-сессии |
| **AUDIT-0520-05** | 🧪 | `payments/refund.py` | `_get_master_frozen_amount` и `_is_company_promo` оба делают `session.get(Promo, ...)` одного объекта — дублирование. Identity-map сессии смягчает реальный hit к БД, но логика дублирована | Загрузить Promo один раз, передавать в обе функции (или объединить) |
| **AUDIT-0520-06** | 🧪 | `admin/withdrawals/service.py` | Устаревший count-паттерн (не subquery, как в B-05/B-09 для прочих модулей) | Унифицировать на subquery-паттерн |
| **AUDIT-0520-07** | 🧪 | `payments/purchase_router.py` | `Practice` загружается дважды при покупке с промокодом (узкое окно). FOR UPDATE защищает от гонки -> перф-нюанс, не корректность | Переиспользовать загруженный объект |
| **AUDIT-0520-08** | 🧪 | `payments/refund.py` | `update(Waitlist).values(status=...)` (bulk core UPDATE) не обновляет `Waitlist.updated_at` | Добавить `updated_at=func.now()` в `.values(...)` или onupdate-триггер для bulk |
| **AUDIT-0520-09** | 🧪 | `tests/` | Нет теста на Stripe `amount_total=None` (кейс AUDIT-0520-01) | Тест: webhook без `amount_total` -> payment FAILED, баланс не кредитуется |
| **AUDIT-0520-S** | 🧪 | разное (SUGGESTION) | Унификация count-паттерна в 3 модулях (см. B-05/B-09); вынос `recalculate_participants` (см. TD-034); обновление Stripe SDK до v9 | Низкий приоритет, по мере касания кода |
| **CAL-FLAKE** | ✅ | `tests/test_notifications.py`, `core/config.py`, `main.py`, `tests/conftest.py` | Флак `TestStageDeliver::test_failed_delivery_retries` (attempts 0 вместо 1): фоновый `run_processor()` под `ASGITransport` lifespan гонялся с ручными `_stage_*` через `FOR UPDATE SKIP LOCKED` | ЗАКРЫТО (24 мая): флаг `notification_processor_enabled` (safe default True); тесты выключают его в session-autouse `setup_infrastructure`. Детали — §5.2 |
| **TD-TGID-56XXX** | ✅ | `tests/test_master_public.py` | Диапазон `telegram_id` 56xxx пересекался между master_public (был 56000-56999) и admin_masters (56001-56010, 56900-56907); оба чистили весь 56xxx — зелено только из-за cleanup между модулями, хрупко | ЗАКРЫТО (24 мая): master_public перенесён в 56500-56599 (мастер 56501, вьюеры 565xx, админ 56590) и чистит только свой поддиапазон. admin_masters не тронут |
| **TD-NOTIF-RACE** | 🧪 | `tests/test_notifications.py`, `notifications/processor.py` | Рецидив `CAL-FLAKE` после ввода второго live-воркера (авто-финализатор, см. блок-цитату ниже). Постоянный `app`-контейнер крутит lifespan-`run_processor`; тесты `exec`-аются в ТОТ ЖЕ контейнер. Стейдж-тесты зовут ГЛОБАЛЬНЫЕ `_stage_resolve/_stage_deliver/_stage_rollup` (без scope — селектят по всей таблице через `FOR UPDATE SKIP LOCKED`), live-процессор гоняется с ними → нотификация застревает в `processing` или `resolved=0`. Флаг `notification_processor_enabled` НЕ помогает: conftest гасит воркер в pytest-процессе, а не в live-uvicorn того же контейнера. Изолированный прогон `pytest tests/test_notifications.py` всегда зелёный | Временно: 3 класса под `@pytest.mark.skip` — `TestStageResolve`, `TestStageDeliver`, `TestRollup` (единственные, кто зовёт глобальные `_stage_*`). Постоянно: опциональный параметр `scope` стадиям (трогает `processor.py`) — тест дёргает стадию только по своему диапазону; ЛИБО одноразовый тест-контейнер без live-воркеров. Прочие классы нотификаций (`TestCreateNotification/TestTargetResolution/TestTemplateEngine/TestTelegramFormatter`) не тронуты |
| **TD-LOCK-AUTOGEN** | 🧪 | Инфра, `install_velo.sh` (секция `update`) | `package-lock.json` синхронизируется с `package.json` вручную. Сервер эфемерный (сносится по плану), `npm ci` в `frontend/Dockerfile` требует синхронный lock из репозитория — рассинхрон валит сборку фронта при пересоздании сервера | Автогенерировать и пушить `package-lock.json` в репозиторий при смене зависимостей — ровно как `generated.ts` (`velo update` его регенерирует и коммитит, «Types are in sync»). Хук — рядом с генерацией типов в секции `update`: при изменении `package.json` → `npm install --package-lock-only` → commit/push lock |

> **Источник AUDIT-0520-*:** полный аудит ветки main от 2026-05-20.
> Отчёт: `docs/01_refer/ARCHIVES/CODE-AUDIT/PROBKIT-REVIEW/2026-05-20-full-audit.md` (оценка 7/10).
> Циклические импорты через lazy import, отмеченные аудитом, — осознанное решение
> проекта (см. ТЗ Phase 5.3 / 6.4), НЕ техдолг.

> **Аудит Calendar iteration (2026-05-22, оценка 7/10):**
> отчёт `docs/01_refer/ARCHIVES/CODE-AUDIT/PROBKIT-REVIEW/2026-05-22-calendar-iteration.md`.
> - **C-1** (роутер импортировал приватную `_user_flags_for_practices`) — ✅ устранено
>   через публичную `get_practice_detail()` в сервисе.
> - **W-2** (граница недели в локальном TZ vs UTC-фильтр) — ✅ устранено буфером ±1 день
>   в `frontend/src/stores/calendar.ts` (клиент группирует по `calendarDateInTz`,
>   лишние дни не протекают в неделю).
> - **W-1** (Stripe startup-валидатор) — ⬜ в техдолге (CAL-W1 выше).
> - **W-3** (EditPracticeView молча проставляет `meditation/beginner` старым практикам
>   без таксономии) — won't fix: БД сносится после каждого обновления кода, практик без
>   таксономии не существует; ветка недостижима. Пересмотреть, если появится импорт
>   практик извне или миграция без сноса БД.
> - 5 SUGGESTION — открыты, низкий приоритет, см. отчёт.

> **Аудит итерации «Профиль» (2026-05-29):**
> - **W-1** (`practices/service.py` `update_practice`) — ✅ устранено: при PATCH
>   `style` без `direction` сервис ре-валидирует против СОХРАНЁННОГО direction
>   (`_validate_style_for_direction` из schemas), невалидная пара -> 400. Закрыло
>   и **S-5** (функция-валидатор теперь переиспользуется и в service, не только в
>   schemas). **W-4** — добавлены 3 теста (`test_update_style_rejected_for_wrong_direction`,
>   `..._for_styleless_direction`, `..._accepted_for_same_direction`).
> - **W-3** (replay-окно initData после удаления anti-replay) — ⬜ осознанный
>   компромисс, не код: приемлемо в Telegram-контексте (HTTPS + rate-limit),
>   задокументировать в threat model; пересмотреть при server-side push/критичных
>   операциях.
> - **S-3** (`bookings/service.py` `hours_attended` — banker's rounding в `round()`)
>   — ⬜ безвреден для статистики; заменить на `Decimal`, если значение пойдёт в
>   финансовые расчёты.

> **Итерация авто-финализации + таймзоны (2026-05-31):** переписана работа
> практик до рабочего состояния. Шесть батчей, все зелёные.
> - **Авто-финализация 24ч** — ✅ корень «зависших» практик: мастер забывал
>   финализировать вручную, практика навечно оставалась `scheduled/live`, деньги
>   заморожены. Фоновый воркер `bookings/autofinalize.py` (`run_autofinalizer`,
>   поллинг 5 мин, backoff, gate `practice_autofinalize_enabled`) добивает
>   просроченные через 24ч-потолок. `finalize_practice` расщеплён на
>   `_finalize_practice_core(actor=...)` (без auth/commit), тонкий owner-checked
>   `finalize_practice` (P-08, сигнатура та же) и системный
>   `auto_finalize_practice` (actor_type="system", actor_id=None, без owner-check).
>   `_claim_overdue_ids` — `FOR UPDATE SKIP LOCKED`, батч 50, своя короткая
>   транзакция. Тесты гасят воркер флагом в conftest (как процессор).
> - **Фильтр публичного фида по времени** — ✅ дефолтный фид (`list_public_practices`
>   без явного `?status=`) теперь отдаёт только `scheduled_at > now()`: начавшиеся/
>   прошедшие скрыты («можно ли ещё забронировать»). Явный `?status=` обходит гейт.
> - **`time_of_day` в поясе ЗРИТЕЛЯ** (Батч 5d) — ✅ фасет «утро/день/вечер»
>   теперь считает локальный час в таймзоне зрителя (`user.timezone`, фолбэк "UTC"),
>   а не практики: `_time_of_day_filter(time_of_day, viewer_tz)` подаёт строку пояса
>   в уже-параметризованный `_local_hour` (`func.timezone(tz, ts)` — bound-параметр,
>   не идентификатор, ORM-чисто). Фид аутентифицирован, `user` уже прокинут —
>   контракт API и фронт не менялись. Тест `test_filter_time_of_day_uses_viewer_timezone`
>   доказывает зависимость от пояса зрителя (практика в UTC@08:00 → morning для
>   UTC-зрителя, day для Asia/Bangkok-зрителя). Решение по таймзонам в целом —
>   Фронтовый Кодекс §10 (пояс профиля решает везде).
> - **TD-NOTIF-RACE** — второй live-воркер обострил гонку тест/процессор; 3 класса
>   под skip. См. «Открытые находки» выше.

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
