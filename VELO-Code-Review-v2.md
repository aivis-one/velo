# VELO Platform — Comprehensive Code Review

**Дата:** 2026-02-26
**Ревьюер:** Senior Software Engineer (12+ лет опыта)
**Scope:** Full-stack review — backend (Python/FastAPI) + frontend (Vue 3/TypeScript)
**Commit:** весь текущий код в `main`

---

## 1. Общий обзор

### Что делает код

VELO — платформа для бронирования wellness-практик (йога, медитации, breathwork). Модульный монолит с:

- **Backend:** FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL + Redis + Stripe
- **Frontend:** Vue 3 + TypeScript + Pinia + Vite (Telegram WebApp + PWA)
- **Домены:** Auth (Telegram), Users, Masters, Practices, Bookings, Waitlist, Payments (double-entry ledger), Withdrawals, Promos, Notifications, Admin

### Архитектура и подход

Модульный монолит с чётким layering: `models.py → schemas.py → service.py → router.py` в каждом модуле. Double-entry бухгалтерия (`user_ledger`, `master_ledger`, `company_ledger`) с инвариантом SUM=0. Аутентификация через Telegram WebApp HMAC-SHA256 + Redis sessions. Background notification processor в FastAPI lifespan.

### Общая оценка качества: 7.5/10

Это хорошо спроектированный проект с продуманной архитектурой. Double-entry ledger, FOR UPDATE блокировки, consistency semaphores — показывает зрелое понимание финансовых систем. Документация в комментариях отличная. Но есть несколько critical багов и ряд проблем, которые нужно исправить до прода.

---

## 2. Критические проблемы и баги

### 🔴 CRITICAL — 2.1: `confirm_waitlist()` — полный rollback вместо savepoint

**Файл:** `backend/app/modules/waitlist/service.py:368-374`

При `IntegrityError` (дублирующий booking) вызывается `session.rollback()`, откатывая **всю** транзакцию. Все предыдущие изменения в сессии теряются. В остальной кодовой базе (promos, masters) используется `begin_nested()` для savepoint-based обработки IntegrityError.

```python
# ❌ Было:
try:
    await session.flush()
except IntegrityError:
    await session.rollback()
    raise ConflictError(
        "Already booked for this practice"
    ) from None

# ✅ Стало:
try:
    async with session.begin_nested():
        await session.flush()
except IntegrityError:
    raise ConflictError(
        "Already booked for this practice"
    ) from None
```

**Воздействие:** Если два пользователя одновременно confirm'ят waitlist для одной practice, и возникает IntegrityError у одного из них — весь rollback может оставить waitlist entry в неконсистентном состоянии (FOR UPDATE lock уже был взят, но изменения потеряны).

---

### 🔴 CRITICAL — 2.2: `upsert_user_on_login()` перезаписывает вручную выбранный язык

**Файл:** `backend/app/modules/auth/service.py:187-195`

При каждом логине `ON CONFLICT DO UPDATE` перезаписывает `language` значением из Telegram `language_code`. Если пользователь вручную сменил язык через PATCH /users/me (например, с `en` на `de`), следующий логин вернёт его обратно.

```python
# ❌ Было:
.on_conflict_do_update(
    index_elements=["telegram_id"],
    set_={
        "first_name": telegram_user.get("first_name"),
        "last_name": telegram_user.get("last_name"),
        "avatar_url": telegram_user.get("photo_url"),
        "language": normalized_lang,         # <-- перезаписывает
        "credentials": credentials,
        "last_login_at": now,
    },
)

# ✅ Стало:
# Не перезаписывать language при update — только при INSERT (новый пользователь)
.on_conflict_do_update(
    index_elements=["telegram_id"],
    set_={
        "first_name": telegram_user.get("first_name"),
        "last_name": telegram_user.get("last_name"),
        "avatar_url": telegram_user.get("photo_url"),
        # "language" убран из set_ — сохраняем пользовательский выбор
        "credentials": credentials,
        "last_login_at": now,
    },
)
```

**Воздействие:** Потеря пользовательских настроек языка после каждого входа. Фрустрация пользователей в мультиязычном приложении.

---

### 🔴 CRITICAL — 2.3: Session index в Redis растёт бесконтрольно (memory leak)

**Файл:** `backend/app/modules/auth/service.py:244-247`

При каждом `create_session()` токен добавляется в SET `user_sessions:{user_id}`. Когда сессии истекают по TTL, токены остаются в SET. TTL SET'а обновляется при каждом логине (строка 247: `await redis.expire(index_key, ttl)`), поэтому для активных пользователей SET никогда не истекает и бесконтрольно растёт.

```python
# ❌ Было:
# create_session() добавляет в SET, но ничего не чистит

# ✅ Стало:
async def create_session(user: User) -> str:
    token = secrets.token_urlsafe(48)
    redis = get_redis()
    ttl = _get_session_ttl()

    session_data = json.dumps({
        "user_id": str(user.id),
        "telegram_id": user.telegram_id,
        "created_at": datetime.now(UTC).isoformat(),
    })

    await redis.set(f"{_SESSION_PREFIX}{token}", session_data, ex=ttl)

    # W-06: Add token and garbage-collect expired ones.
    index_key = f"{_USER_SESSIONS_PREFIX}{user.id}"

    # Garbage collect: remove tokens that no longer exist in Redis
    existing_tokens = await redis.smembers(index_key)
    if existing_tokens:
        session_keys = [f"{_SESSION_PREFIX}{t}" for t in existing_tokens]
        alive = await redis.exists(*session_keys)
        if alive < len(existing_tokens):
            # Some tokens expired — clean up the SET
            for t in existing_tokens:
                exists = await redis.exists(f"{_SESSION_PREFIX}{t}")
                if not exists:
                    await redis.srem(index_key, t)

    await redis.sadd(index_key, token)
    await redis.expire(index_key, ttl)

    logger.info("session_created", user_id=str(user.id))
    return token
```

**Альтернатива (проще):** Использовать Redis Sorted Set с timestamp как score, и при каждом создании сессии удалять записи со score < текущее время.

**Воздействие:** Медленный рост потребления памяти Redis. Для пользователя, логинящегося 10 раз в день за 6 месяцев = ~1800 мёртвых токенов в SET. `delete_all_sessions()` пытается удалить все 1800 несуществующих ключей.

---

## 3. Обработка ошибок

### 🟡 WARNING — 3.1: `process_waitlist()` — stub-уведомление вместо реального

**Файл:** `backend/app/modules/waitlist/service.py:442-450`

```python
# Stub notification -- real implementation in Phase 7.
logger.info(
    "waitlist_notification_stub",
    ...
    message="TODO: Send Telegram notification to user",
)
```

Notification system (Phase 7) уже реализован и работает. Но `process_waitlist()` до сих пор использует stub. Пользователь, получивший место из waitlist, **никак не узнает** об этом — у него 30 минут на подтверждение, а уведомления нет.

```python
# ❌ Было:
logger.info("waitlist_notification_stub", ...)

# ✅ Стало:
from app.modules.notifications.service import create_notification
from app.modules.notifications.models import TargetType

await create_notification(
    type="waitlist_spot_available",
    title="Spot available",
    body="",
    target_type=TargetType.USER.value,
    target_value=str(entry.user_id),
    session=session,
    action_data={
        "action": "confirm_waitlist",
        "params": {"waitlist_id": str(entry.id)},
        "practice_id": str(practice_id),
    },
    priority=1,  # Urgent — 30min window
    expiry_at=entry.expires_at,
)
```

**Воздействие:** Waitlist бесполезен без нотификации. Пользователи пропускают 30-минутное окно и никогда не получают место.

---

### 🟢 SUGGESTION — 3.2: Общая обработка ошибок — хорошо сделана

Проблем не обнаружено в остальной обработке ошибок. Отмечу хорошие решения:

- `VeloError` иерархия с HTTP status codes — чисто и расширяемо
- `BadRequestError` / `NotFoundError` / `ConflictError` — семантически точные
- P-08 паттерн (404 вместо 403 для non-owner) — правильно скрывает существование ресурсов
- structlog с context variables — отличная диагностика
- Webhook router возвращает 500 на transient errors для Stripe retry — правильная стратегия (M-03)
- Notification processor ловит все exceptions в main loop и продолжает — robust

---

## 4. Безопасность и уязвимости

### 🟡 WARNING — 4.1: Отсутствие rate limiting на auth endpoints

**Файл:** `backend/app/modules/auth/router.py`

`POST /auth/telegram` не имеет rate limiting. Хотя initData expires через 5 минут (строка 123 auth service), атакующий может:

1. Получить валидный initData
2. Делать тысячи запросов в течение 5-минутного окна
3. Создать тысячи сессий в Redis (каждый вызов create_session создаёт новый токен)

**Вектор атаки:** DoS через заполнение Redis → OOM
**Воздействие:** Redis out of memory, все существующие сессии теряются
**Как исправить:** Добавить rate limiter (slowapi или кастомный middleware), лимит 5 req/min на telegram_id.

---

### 🟡 WARNING — 4.2: `delete_all_sessions()` — race condition с `create_session()`

**Файл:** `backend/app/modules/auth/service.py:272-299`

```python
tokens = await redis.smembers(index_key)     # (1) Читаем все токены
# ... между (1) и (2) create_session() может добавить новый токен ...
deleted = await redis.delete(*session_keys, index_key)  # (2) Удаляем SET + ключи
```

Между `smembers` и `delete`, параллельный `create_session()` может добавить новый токен в SET и создать новую session key. `delete` удалит SET (включая новый токен), но НЕ удалит новую session key. Результат: сессия-сирота, живая после "logout all".

**Как исправить:** Обернуть в Redis MULTI/EXEC transaction или использовать Lua-скрипт.

---

### 🟢 SUGGESTION — 4.3: Хорошие security-решения

Проблем не обнаружено в:

- HMAC-SHA256 validation с `hmac.compare_digest()` (constant-time) — защита от timing attacks
- initData expiry 5 минут — защита от replay attacks
- `secrets.token_urlsafe(48)` — криптографически стойкие токены
- Production validator: все secrets обязательны (DATABASE_URL, SECRET_KEY, TELEGRAM_BOT_TOKEN, STRIPE_*)
- CORS wildcard запрещён в production
- P-08: 404 not 403 — не раскрывает существование ресурсов
- `_parse_user_id()` — защита от corrupted Redis → SQL injection
- Stripe webhook signature verification — правильная реализация
- Input validation через Pydantic schemas — XSS и injection prevention

---

## 5. Производительность

### 🟡 WARNING — 5.1: Notification rollup — N+1 запросы

**Файл:** `backend/app/modules/notifications/processor.py:416-425`

Для каждой notification в `processing` статусе выполняется отдельный `SELECT COUNT(*)`:

```python
# ❌ Было:
for notification in notifications:
    sent_stmt = (
        select(func.count(NotificationDelivery.id))
        .where(
            NotificationDelivery.notification_id == notification.id,
            NotificationDelivery.status == DeliveryStatus.SENT.value,
        )
    )
    sent_count = (await session.execute(sent_stmt)).scalar_one()
```

```python
# ✅ Стало: Один запрос с GROUP BY
if not notifications:
    return

notification_ids = [n.id for n in notifications]
sent_counts_stmt = (
    select(
        NotificationDelivery.notification_id,
        func.count(NotificationDelivery.id),
    )
    .where(
        NotificationDelivery.notification_id.in_(notification_ids),
        NotificationDelivery.status == DeliveryStatus.SENT.value,
    )
    .group_by(NotificationDelivery.notification_id)
)
result = await session.execute(sent_counts_stmt)
sent_map = dict(result.all())

for notification in notifications:
    sent_count = sent_map.get(notification.id, 0)
    if sent_count > 0:
        notification.status = NotificationStatus.SENT.value
    else:
        notification.status = NotificationStatus.FAILED.value
```

**Воздействие:** При 50 notifications в batch = 50 дополнительных DB roundtrips. На нагруженной системе это может быть заметно.

---

### 🟡 WARNING — 5.2: `reschedule_reminders_for_practice()` — N+1 на пользователей

**Файл:** `backend/app/modules/notifications/reminders.py:413-419`

```python
# ❌ Было:
for booking in bookings:
    user = await session.get(User, booking.user_id)  # N запросов
    if not user:
        continue
    reminders = await schedule_reminders(booking, practice, user, session)
```

```python
# ✅ Стало: Загрузить всех пользователей одним запросом
user_ids = [b.user_id for b in bookings]
users_stmt = select(User).where(User.id.in_(user_ids))
users_result = await session.execute(users_stmt)
users_map = {u.id: u for u in users_result.scalars().all()}

for booking in bookings:
    user = users_map.get(booking.user_id)
    if not user:
        continue
    reminders = await schedule_reminders(booking, practice, user, session)
```

**Воздействие:** На практике с 100 участниками = 100 SQL запросов вместо 1.

---

### 🟡 WARNING — 5.3: `list_public_practices()` — дублирование фильтров

**Файл:** `backend/app/modules/practices/service.py:469-507`

Каждый фильтр применяется дважды — к `query` и к `count_query`. Это нарушает DRY и увеличивает риск рассинхронизации.

```python
# ❌ Было:
if master_id is not None:
    query = query.where(Practice.master_id == master_id)
    count_query = count_query.where(Practice.master_id == master_id)

# ✅ Стало: Построить фильтры один раз
filters = [base_filter]
if master_id is not None:
    filters.append(Practice.master_id == master_id)
if practice_type is not None:
    filters.append(Practice.practice_type == practice_type)
if date_from is not None:
    filters.append(Practice.scheduled_at >= date_from)
if date_to is not None:
    filters.append(Practice.scheduled_at <= date_to)

query = select(Practice).where(*filters)
count_query = select(func.count(Practice.id)).where(*filters)
```

---

### 🟢 SUGGESTION — 5.4: `run_all_semaphores()` — параллельное выполнение

**Файл:** `backend/app/modules/admin/consistency/service.py:734-748`

Пять категорий проверок выполняются последовательно, но они независимы.

```python
# ❌ Было:
all_results.extend(await _check_count_count(session))
all_results.extend(await _check_sum_zero(session))
all_results.extend(await _check_computed_actual(session))
all_results.extend(await _check_orphans(session))
all_results.extend(await _check_invariants(session))
```

Нельзя использовать `asyncio.gather()` здесь, потому что все функции используют одну `session`, а SQLAlchemy AsyncSession не thread-safe и не допускает параллельных запросов в одной сессии. Текущий последовательный подход — единственно правильный. **Проблем не обнаружено.**

---

## 6. Чистота кода и лучшие практики

### 🟡 WARNING — 6.1: Redundant import в `purchase_router.py`

**Файл:** `backend/app/modules/payments/purchase_router.py:122`

```python
# ❌ Было (строка 122, внутри функции):
from app.core.exceptions import NotFoundError
raise NotFoundError("Practice not found")

# ✅ Стало: Убрать внутренний import, использовать уже импортированный на строке 29
raise NotFoundError("Practice not found")
```

`NotFoundError` уже импортирован на уровне модуля (строка 29).

---

### 🟡 WARNING — 6.2: Misleading comment на `current_participants`

**Файл:** `backend/app/modules/practices/models.py:104-110`

```python
# ❌ Было:
# NOT USED -- capacity is checked via COUNT(bookings) (TD-034).
# Column retained for potential future denormalization.
current_participants: Mapped[int] = mapped_column(...)

# ✅ Стало:
# Denormalized counter for frontend display (A-03).
# Source of truth is COUNT(bookings WHERE confirmed/attended).
# Updated via recalculate_participants() in booking/waitlist flows.
current_participants: Mapped[int] = mapped_column(...)
```

Комментарий говорит "NOT USED", но `recalculate_participants()` активно обновляет это поле, и consistency check 3.4 проверяет его корректность.

---

### 🟢 SUGGESTION — 6.3: Отличные практики в кодовой базе

- Каждый файл начинается с comprehensive header comment — превосходно для onboarding
- Phase markers (P-01, P-07, TD-034, W-06) — отличная трассировка решений
- `exclude_unset=True` для partial updates — правильный Pydantic паттерн
- `IntegrityError` catch через `begin_nested()` savepoints — правильно (кроме waitlist)
- Иерархия `VeloError` с HTTP кодами — чистая exception strategy
- `with_for_update(skip_locked=True)` в notification processor — правильный подход для background workers
- Atomic promo increment с `WHERE used_count < max_uses` — отличная защита от race conditions

---

## 7. Тестируемость

### 🟡 WARNING — 7.1: Тесты не изолированы — нет cleanup между тестами

**Файл:** `backend/tests/conftest.py`

Fixture `db_session` создаёт сессию, но не оборачивает тест в transaction с rollback. Данные одного теста остаются для следующего.

```python
# ❌ Было:
@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        await session.close()

# ✅ Стало:
@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    session = factory()
    # Begin a transaction that we'll roll back after the test.
    await session.begin()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()
```

**Альтернатива (надёжнее):** Использовать SAVEPOINT-based подход:
1. `session.begin()` в fixture
2. `session.begin_nested()` для каждого теста
3. Rollback nested transaction после теста
4. Rollback outer transaction в cleanup

**Воздействие:** Тесты могут давать false positives/negatives из-за данных от предыдущих тестов. Порядок запуска тестов влияет на результат.

---

### 🟢 SUGGESTION — 7.2: Хорошая тестируемость архитектуры

- Service functions принимают `session` как dependency — легко мокать
- `P-01: No session.commit() in services` — отделяет бизнес-логику от persistence
- Read-only sessions (`get_db_reader`) — защита от случайных mutations в тестах
- `is_stripe_stub` property — позволяет тестировать без Stripe
- Lazy engine initialization — совместимо с pytest event loop

---

## 8. Рекомендации по рефакторингу

### 🟢 SUGGESTION — 8.1: Унифицировать pagination pattern

Паттерн "count query + items query" дублируется в ~10 местах. Можно создать generic helper:

```python
# app/core/pagination.py
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

async def paginate(
    session: AsyncSession,
    query: Select,
    *,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list, int]:
    """Execute a paginated query, returning (items, total_count)."""
    # Count.
    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar_one()

    # Items.
    items_query = query.limit(limit).offset(offset)
    result = await session.execute(items_query)
    items = list(result.scalars().all())

    return items, total
```

---

### 🟢 SUGGESTION — 8.2: Использовать Enum.value consistently

В некоторых местах сравнение через `.value`:
```python
if promo.type == PromoType.MASTER.value:
```

В других — через Enum напрямую (e.g., `UserRole.ADMIN` в consistency checks). Стоит унифицировать подход. Поскольку модели хранят строки, `.value` необходим, но можно рассмотреть использование `native_enum=True` или `TypeDecorator` для автоматической конвертации.

---

## 9. Мелкие улучшения и polish

### 🟢 SUGGESTION — 9.1: Frontend `window.location.href = '/'` в API client

**Файл:** `frontend/src/api/client.ts:119`

```typescript
// ❌ Было:
if (response.status === 401) {
    _token = null
    sessionStorage.removeItem('velo_token')
    window.location.href = '/'
    throw new ApiResponseError(401, 'Session expired')
}
```

Side effect (redirect) внутри generic HTTP client — антипаттерн. Это мешает обработке 401 на уровне вызывающего кода (например, silent retry, показать модалку).

```typescript
// ✅ Стало:
if (response.status === 401) {
    _token = null
    sessionStorage.removeItem('velo_token')
    // Redirect logic should be in the auth store or interceptor,
    // not in the generic HTTP client.
    throw new ApiResponseError(401, 'Session expired')
}
```

---

### 🟢 SUGGESTION — 9.2: `practice_type` не валидируется против `PracticeType` enum

**Файл:** `backend/app/modules/practices/models.py:81`

```python
practice_type: Mapped[str] = mapped_column(String(20))
```

Нет CHECK constraint или validation что значение входит в `PracticeType` enum. Любая строка до 20 символов будет принята на уровне DB. Валидация в Pydantic schema помогает, но лучше добавить DB-level constraint.

---

### 🟢 SUGGESTION — 9.3: `_build_action_data()` в reminders — `participants_count` как строка

**Файл:** `backend/app/modules/notifications/reminders.py:136`

```python
if participants_count is not None:
    data["participants_count"] = str(participants_count)  # str, не int
```

Все остальные числовые значения в templates используются как строки через `format_map`, так что это работает. Но семантически было бы чище хранить как int и конвертировать при рендеринге.

---

---

## 10. Frontend — Выделенный обзор проблем

Фронтенд на ранней стадии (Phase F1 — только auth flow и skeleton), ~14 TS-файлов + 4 Vue-компонента. Тем не менее, есть проблемы, которые нужно исправить до того, как кодовая база начнёт расти.

---

### 🔴 CRITICAL — 10.1: `telegram.ts` — crash при недоступности Telegram CDN

**Файл:** `frontend/src/platform/telegram.ts:15`

```typescript
// ❌ Было:
const webApp = window.Telegram!.WebApp   // <-- module-level, всегда выполняется
```

Это module-level код. Даже несмотря на то, что `index.ts` использует optional chaining (`window.Telegram?.WebApp?.initData`) для определения платформы, **статический** import `telegram.ts` вызывает выполнение строки 15 при загрузке модуля — **до** проверки платформы.

**Цепочка:**
1. `index.ts` импортирует `telegram.ts` (static import, строка 20)
2. `telegram.ts` строка 15 выполняется: `window.Telegram!.WebApp`
3. Если CDN `telegram.org/js/telegram-web-app.js` не загрузился → `window.Telegram` = `undefined`
4. `undefined.WebApp` → **TypeError: Cannot read properties of undefined**
5. Приложение полностью мертво — ни standalone, ни Telegram mode

**Когда это произойдёт:**
- Telegram CDN заблокирован (корпоративный прокси, Китай, VPN)
- CDN временно недоступен (downtime)
- Content Security Policy блокирует внешние скрипты
- Медленное соединение + script timeout

```typescript
// ✅ Стало: Ленивая инициализация вместо module-level
import type { Platform } from './types'

function getWebApp(): TelegramWebApp {
  const tg = window.Telegram?.WebApp
  if (!tg) {
    throw new Error('Telegram WebApp SDK not available')
  }
  return tg
}

export const telegramPlatform: Platform = {
  name: 'telegram',

  async init(): Promise<void> {
    const webApp = getWebApp()
    webApp.ready()
    webApp.expand()
    webApp.setHeaderColor('#334D6E')
    webApp.setBackgroundColor('#F8FAFC')
  },

  getInitData(): string | null {
    return getWebApp().initData || null
  },

  // ... остальные методы аналогично
}
```

**Воздействие:** 100% crash rate при любом сбое CDN. Приложение не может даже показать StandaloneStub.

---

### 🟡 WARNING — 10.2: 401 handler в API client обходит auth store

**Файл:** `frontend/src/api/client.ts:116-121`

```typescript
// ❌ Было:
if (response.status === 401) {
    _token = null                              // (1) напрямую мутирует _token
    sessionStorage.removeItem('velo_token')    // (2) напрямую чистит storage
    window.location.href = '/'                 // (3) hard redirect
    throw new ApiResponseError(401, 'Session expired')
}
```

Три проблемы:
1. **Двойное управление состоянием:** Auth store имеет `_setToken(null)` который синхронизирует `token.value`, `_token`, и `sessionStorage`. Но 401 handler обходит store и мутирует `_token` и `sessionStorage` напрямую. `token.value` в Pinia остаётся не-null → `isAuthenticated` computed = true, хотя сессия уже мертва.
2. **Side effect в HTTP client:** `window.location.href = '/'` — жёсткий redirect внутри generic HTTP клиента. Вызывающий код не может обработать 401 по-своему (показать модалку, silent retry, redirect на другую страницу).
3. **Race condition:** При нескольких параллельных запросах (fetch user + fetch practices + fetch bookings), если все получат 401, все три вызовут `window.location.href = '/'` одновременно.

```typescript
// ✅ Стало:
if (response.status === 401) {
    // Очистить только _token в клиенте, чтобы не слать
    // невалидный токен в следующих запросах.
    _token = null
    // Не трогать sessionStorage и не делать redirect —
    // пусть вызывающий код (auth store) решает что делать.
    throw new ApiResponseError(401, 'Session expired')
}
```

**Воздействие:** Рассинхронизация между Pinia state и реальным состоянием auth. Потенциальный infinite loop при redirect.

---

### 🟡 WARNING — 10.3: Hardcoded bot URL в StandaloneStubView

**Файл:** `frontend/src/views/auth/StandaloneStubView.vue:46`

```typescript
// ❌ Было:
const botUrl = 'https://t.me/velo_testbot'
```

URL тестового бота захардкожен в компоненте. При деплое в production нужно менять исходный код. На бэкенде есть `settings.telegram_bot_url`, но фронтенд его не использует.

```typescript
// ✅ Стало:
const botUrl = import.meta.env.VITE_BOT_URL || 'https://t.me/velo_testbot'
```

И добавить `VITE_BOT_URL` в `env.d.ts`:
```typescript
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_BOT_URL: string
}
```

**Воздействие:** При смене бота нужно менять исходный код и пересобирать. Невозможно использовать разные боты для staging/production.

---

### 🟡 WARNING — 10.4: `useAuth` — singleton state вне composable

**Файл:** `frontend/src/composables/useAuth.ts:21-24`

```typescript
// ❌ Было:
// Module-level refs — глобальные синглтоны
const isReady = ref(false)
const isStandalone = ref(false)

export function useAuth() {
  // ...
  return { isReady, isStandalone, ... }
}
```

`isReady` и `isStandalone` объявлены на уровне модуля, а не внутри composable. Это означает:
1. **Тесты:** Состояние течёт между тестами. `isReady.value = true` в тесте A → тест B получает `isReady = true` без вызова `initAuth()`.
2. **HMR (Hot Module Replacement):** При hot reload модуль переимпортируется, `isReady` сбрасывается в `false`, но `initAuth()` не вызывается повторно → белый экран.
3. **Семантика:** Нарушает контракт Vue composable — каждый вызов `useAuth()` должен возвращать новый reactive scope или явно документировать shared state.

```typescript
// ✅ Стало (вариант A — explicit singleton через Pinia):
// Перенести isReady и isStandalone в authStore

// ✅ Стало (вариант B — composable с reset):
let isReady = ref(false)
let isStandalone = ref(false)

export function useAuth() {
  // ...
  return { isReady, isStandalone, initAuth }
}

/** For tests — reset composable state. */
export function _resetAuth(): void {
  isReady.value = false
  isStandalone.value = false
}
```

**Воздействие:** Нестабильные тесты, потенциальные проблемы с HMR в dev-режиме.

---

### 🔴 CRITICAL — 10.5: Внешний nginx — `X-Frame-Options DENY` ломает Telegram WebApp

**Файл:** `scripts/install_velo.sh:519`

```nginx
# ❌ Было:
add_header X-Frame-Options DENY always;
```

Telegram WebApp загружается внутри iframe на `web.telegram.org`. Заголовок `X-Frame-Options DENY` **запрещает** загрузку в iframe — приложение полностью не работает в Telegram!

Также на внешнем nginx отсутствуют `Referrer-Policy` и `Permissions-Policy`. Внутренний `frontend/nginx.conf` трогать не нужно — headers с внешнего проксируются клиенту.

```nginx
# ✅ Стало (в scripts/install_velo.sh, секция Security headers):

# Разрешить iframe только для Telegram WebApp
add_header Content-Security-Policy "frame-ancestors 'self' https://web.telegram.org https://*.telegram.org" always;
# НЕ использовать X-Frame-Options — он deprecated и не поддерживает wildcard.
# CSP frame-ancestors заменяет его.

add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
```

**Воздействие:** Приложение не загружается в Telegram. 100% пользователей affected (все заходят через Telegram).

---

### 🟢 SUGGESTION — 10.6: Google Fonts через `@import` — блокирует рендеринг

**Файл:** `frontend/src/styles/global.css:9`

```css
/* ❌ Было: */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
```

`@import url(...)` в CSS — render-blocking запрос. Браузер:
1. Загружает CSS файл
2. Находит `@import`
3. Останавливает рендеринг
4. Загружает Google Fonts CSS
5. Google Fonts CSS ссылается на .woff2 файлы
6. Загружает шрифты

В Telegram WebApp, где первое впечатление критично (пользователь ждёт загрузки mini app), это добавляет ~200-500ms к First Contentful Paint.

```html
<!-- ✅ Стало: Перенести в index.html с preconnect -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet"
  href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap">
```

И убрать `@import` из `global.css`.

**Воздействие:** Замедление FCP на 200-500ms. Заметно в Telegram WebApp.

---

### 🟢 SUGGESTION — 10.7: `window.location.reload()` в logout — double-redirect

**Файл:** `frontend/src/views/HomeView.vue:67-69`

```typescript
// ❌ Было:
async function handleLogout(): Promise<void> {
  await authStore.logout()
  window.location.reload()
}
```

`authStore.logout()` вызывает `api.post('/api/v1/auth/logout')`. Если сессия уже истекла, backend вернёт 401. API client 401 handler (client.ts:116-121) сделает `window.location.href = '/'`. Затем `handleLogout` вызовет `window.location.reload()`. Результат: **два redirect подряд**.

Также `window.location.reload()` — полная перезагрузка страницы в Telegram WebApp: re-parse HTML, re-download всех ресурсов, re-execute Telegram SDK, re-run auth flow. Это ~1-3 секунды белого экрана.

```typescript
// ✅ Стало: Использовать реактивное обновление Vue
async function handleLogout(): Promise<void> {
  await authStore.logout()
  // App.vue реактивно покажет StandaloneStubView,
  // когда isAuthenticated станет false.
  // Не нужен reload — Vue reactivity всё сделает.
}
```

**Воздействие:** Мерцание экрана при logout, лишняя перезагрузка ресурсов.

---

### 🟢 SUGGESTION — 10.8: SVG-логотип дублируется в 3 компонентах

**Файлы:**
- `frontend/src/views/HomeView.vue:13-24`
- `frontend/src/views/auth/LoadingView.vue:12-23`
- `frontend/src/views/auth/StandaloneStubView.vue:13-24`

Одинаковый SVG (64x64, круг + буква "V") скопирован дословно в 3 компонента. При изменении логотипа нужно обновлять 3 файла.

```vue
<!-- ✅ Стало: Извлечь в shared component -->
<!-- src/components/VeloLogo.vue -->
<template>
  <svg :width="size" :height="size" viewBox="0 0 64 64" fill="none"
       xmlns="http://www.w3.org/2000/svg">
    <circle cx="32" cy="32" r="30" fill="var(--velo-primary)" />
    <text x="32" y="40" text-anchor="middle" fill="white"
          font-size="24" font-weight="700"
          font-family="system-ui, sans-serif">V</text>
  </svg>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ size?: number }>(), { size: 64 })
</script>
```

---

### 🟢 SUGGESTION — 10.9: `user-scalable=no` — accessibility issue

**Файл:** `frontend/index.html:5`

```html
<!-- ❌ Было: -->
<meta name="viewport" content="width=device-width, initial-scale=1.0,
  maximum-scale=1.0, user-scalable=no" />
```

Отключение зума нарушает WCAG 1.4.4 (Resize text). Пользователи с нарушениями зрения не могут увеличить текст. Telegram SDK сам по себе не требует `user-scalable=no` — это решение разработчика. Компромисс: разрешить зум до 3x.

```html
<!-- ✅ Стало: -->
<meta name="viewport" content="width=device-width, initial-scale=1.0,
  maximum-scale=3.0, user-scalable=yes" />
```

---

### 🟢 SUGGESTION — 10.10: Нет тёмной темы, хотя API готово (→ Phase F2+)

**Файлы:**
- `frontend/src/platform/types.ts:35` — `getTheme(): 'light' | 'dark'`
- `frontend/src/platform/telegram.ts:41` — `return webApp.colorScheme || 'light'`
- `frontend/src/styles/variables.css` — только light-тема

Platform abstraction поддерживает dark mode (`getTheme()` возвращает `'dark'` из Telegram SDK). Но CSS-переменные определены только для светлой темы. Результат: если у пользователя Telegram в тёмном режиме, VELO отображает слепяще белый интерфейс.

**Scope:** Полноценная тёмная тема — это задача Phase F2+, не F1. Требуется: все токены в `:root[data-theme="dark"]`, детекция через `platform.getTheme()`, переключение атрибута на `<html>`. Каркас из `@media (prefers-color-scheme: dark)` с 7 переменными — это 10 строк CSS, но без привязки к `platform.getTheme()` и `data-theme` атрибуту оно неполноценно в контексте Telegram (где тема определяется SDK, а не `prefers-color-scheme`). Оставить на F2.

**Воздействие:** Плохой UX для ~40% пользователей Telegram, использующих тёмную тему.

---

### Сводка по фронтенду

| Уровень | # | Суть |
|---------|---|------|
| 🔴 CRITICAL | 10.1 | `telegram.ts` — crash при недоступности CDN |
| 🟡 WARNING | 10.2 | 401 handler обходит auth store |
| 🟡 WARNING | 10.3 | Hardcoded bot URL |
| 🟡 WARNING | 10.4 | Singleton state вне composable |
| 🔴 CRITICAL | 10.5 | `X-Frame-Options DENY` ломает Telegram iframe |
| 🟢 SUGGEST | 10.6 | Google Fonts блокирует рендеринг |
| 🟢 SUGGEST | 10.7 | Double redirect при logout |
| 🟢 SUGGEST | 10.8 | SVG-логотип дублируется в 3 местах |
| 🟢 SUGGEST | 10.9 | `user-scalable=no` — accessibility |
| 🟢 SUGGEST | 10.10 | Нет тёмной темы (→ Phase F2+) |

**Оценка фронтенда отдельно: 6/10**

Для Phase F1 (skeleton + auth) — функционально работает. Но 10.1 (CDN crash) убьёт приложение при сбое CDN, 10.5 (`X-Frame-Options DENY`) вообще заблокирует загрузку в Telegram. Эти два бага — блокеры релиза. 401 handler (10.2) создаст проблемы при добавлении новых экранов. Hardcoded bot URL (10.3) сломает деплой в production.

---

## Итоговый блок

**Итоговая оценка:** 7/10 (Backend: 8/10, Frontend: 6/10)

Хорошо спроектированная система с продуманной архитектурой. Double-entry бухгалтерия, consistency semaphores, structured logging, proper concurrency handling — видна рука опытного архитектора. Бэкенд зрелый и готов к проду после исправления 3 critical багов. Фронтенд на ранней стадии (Phase F1), но содержит два блокирующих бага (crash при недоступности CDN + `X-Frame-Options DENY` на внешнем nginx) и несколько архитектурных проблем, которые усложнят жизнь по мере роста кодовой базы.

---

**🔴 Критично исправить:**

1. `confirm_waitlist()` — заменить `session.rollback()` на `begin_nested()` (waitlist/service.py:368-374)
2. `upsert_user_on_login()` — не перезаписывать `language` при update (auth/service.py:193)
3. Session index memory leak — добавить garbage collection в `create_session()` (auth/service.py:244-247)
4. **[FE]** `telegram.ts` — lazy init вместо module-level `window.Telegram!.WebApp` (telegram.ts:15)
5. **[INFRA]** `X-Frame-Options DENY` в внешнем nginx — ломает Telegram iframe (install_velo.sh:519)

**🟡 Рекомендовано исправить:**

1. `process_waitlist()` — подключить к notification system вместо stub (waitlist/service.py:442-450)
2. Добавить rate limiting на `/auth/telegram` endpoint
3. `delete_all_sessions()` — атомарная операция через Redis MULTI/EXEC (auth/service.py:272-299)
4. Test fixtures — добавить per-test transaction isolation (conftest.py)
5. Notification rollup — устранить N+1 запросы (processor.py:416-425)
6. `reschedule_reminders_for_practice()` — устранить N+1 на пользователей (reminders.py:413-419)
7. `list_public_practices()` — DRY для фильтров (practices/service.py:469-507)
8. **[FE]** 401 handler обходит auth store — dual state management (client.ts:116-121)
9. **[FE]** Hardcoded bot URL в StandaloneStubView — не деплоится в production (StandaloneStubView.vue:46)
10. **[FE]** Singleton refs в `useAuth` вне composable — тесты текут (useAuth.ts:21-24)
11. **[INFRA]** Добавить `Referrer-Policy` и `Permissions-Policy` во внешний nginx

**🟢 Nice to have:**

1. Убрать redundant import в `purchase_router.py:122`
2. Обновить misleading "NOT USED" comment на `current_participants`
3. Унифицировать pagination pattern через generic helper
4. Добавить DB CHECK constraint на `practice_type`
5. **[FE]** Google Fonts через `<link>` в `index.html` вместо `@import` в CSS (global.css:9)
6. **[FE]** Убрать `window.location.reload()` при logout — использовать Vue reactivity (HomeView.vue:68)
7. **[FE]** Извлечь SVG-логотип в shared `VeloLogo.vue` компонент (3 дубликата)
8. **[FE]** Viewport `maximum-scale=3.0, user-scalable=yes` для accessibility (index.html:5)
9. **[FE]** Тёмная тема — отложить на Phase F2+ (требует `data-theme` + `platform.getTheme()` интеграцию)

---

## 11. Повторная проверка (Re-review, 2026-03-10)

**Дата:** 2026-03-10
**Scope:** Повторная проверка бэкенда после обновлений (merge main → Phase F9: diary, check-in, feedback, analytics). +8091/-1466 строк в 74 файлах.

### Статус исправления ранее найденных проблем

| # | Проблема | Статус |
|---|----------|--------|
| 🔴 2.1 | `confirm_waitlist()` — `session.rollback()` → `begin_nested()` | ✅ **ИСПРАВЛЕНО** — savepoint pattern на строках 212 и 379 |
| 🔴 2.2 | `upsert_user_on_login()` — перезапись `language` | ✅ **ИСПРАВЛЕНО** — `language` убран из `set_` (строка 213-217) |
| 🔴 2.3 | Session index memory leak (SET без GC) | ✅ **ИСПРАВЛЕНО** — ZSET + `ZREMRANGEBYSCORE` + `MULTI/EXEC` pipeline (строка 252-291) |
| 🟡 3.1 | `process_waitlist()` — stub notification | ✅ **ИСПРАВЛЕНО** — реальный `create_notification()` вызов |
| 🟡 4.1 | Нет rate limiting на `/auth/telegram` | ❌ **НЕ ИСПРАВЛЕНО** |
| 🟡 4.2 | `delete_all_sessions()` — race condition | ✅ **ИСПРАВЛЕНО** — pipeline atomicity (CRITICAL-05) |
| 🟡 5.1 | Notification rollup N+1 | ✅ **ИСПРАВЛЕНО** — GROUP BY |
| 🟡 5.2 | Reminders N+1 на пользователей | ✅ **ИСПРАВЛЕНО** — batch-load (NEW-06) |
| 🟡 5.3 | `list_public_practices()` DRY фильтры | ✅ **ИСПРАВЛЕНО** — FIX 5.3, один `filters` список |
| 🟡 6.1 | Redundant import `purchase_router.py:122` | ❌ **НЕ ИСПРАВЛЕНО** — всё ещё inline `from app.core.exceptions import NotFoundError` |
| 🟡 6.2 | Misleading "NOT USED" comment | ✅ **ИСПРАВЛЕНО** — комментарий обновлён: "Cached counter" (строка 111-113) |
| 🟡 7.1 | Test isolation (conftest.py) | ❌ **НЕ ИСПРАВЛЕНО** — `db_session` без transaction wrapping |

**Итого:** 9 из 12 исправлено (75%). Осталось 3 незакрытых пункта.

---

### Новые проблемы в обновлённом коде

#### 🟡 WARNING — 11.1: `diary/service.py` — pagination filter duplication (аналог бывшего 5.3)

**Файлы:** `diary/service.py:182-199`, `diary/service.py:356-370`, `diary/service.py:613-633`

Три listing-функции (`list_user_checkins`, `list_user_feedbacks`, `list_diary_entries`) дублируют каждый фильтр для `base` и `count_base`:

```python
# ❌ Было (аналогично прежнему 5.3):
if practice_id is not None:
    base = base.where(Checkin.practice_id == practice_id)
    count_base = count_base.where(Checkin.practice_id == practice_id)
```

Тот же паттерн, который был исправлен в `list_public_practices()` (FIX 5.3). Следует применить тот же подход — собрать фильтры в один список и применить `where(*filters)` к обоим запросам.

---

#### 🟡 WARNING — 11.2: `promos/validation.py` — `first_purchase_only` считает PENDING покупки

**Файл:** `backend/app/modules/promos/validation.py:137-148`

```python
existing_stmt = (
    select(Purchase.id)
    .where(
        Purchase.user_id == user_id,
        Purchase.status.in_([
            PurchaseStatus.PENDING.value,
            PurchaseStatus.COMPLETED.value,
        ]),
    )
    .limit(1)
)
```

`PENDING` покупка (ещё не оплачена) блокирует использование `first_purchase_only` промокода. Если пользователь:
1. Начал покупку → Purchase в PENDING
2. Не оплатил (бросил Stripe checkout)
3. Вернулся и хочет использовать промокод на первую покупку → отказ

**Исправление:** Считать только `COMPLETED`:
```python
Purchase.status == PurchaseStatus.COMPLETED.value,
```

---

#### 🟡 WARNING — 11.3: `diary/models.py` — `check_type` без `CheckConstraint`

**Файл:** `backend/app/modules/diary/models.py:117-121`

```python
check_type: Mapped[str] = mapped_column(
    String(10),
    default=CheckType.PRE.value,
    server_default=CheckType.PRE.value,
)
```

`mood` имеет `CheckConstraint("mood IN ('low', 'mid', 'high')")`, `rating` имеет `CheckConstraint` — но `check_type` не имеет. Любая строка до 10 символов будет принята на уровне БД. Для consistency:

```python
CheckConstraint(
    "check_type IN ('pre', 'post')",
    name="ck_checkin_check_type",
),
```

---

#### 🟢 SUGGESTION — 11.4: `diary/service.py` — `diary_comment_max_length` в config не используется

**Файл:** `backend/app/core/config.py` + `backend/app/modules/diary/schemas.py`

`settings.diary_comment_max_length` (default=1000) определён в конфиге, но schemas используют hardcoded `max_length=1000` в `Field()`. Если кто-то изменит конфиг — валидация не изменится.

---

#### 🟢 SUGGESTION — 11.5: `purchase_router.py:122` — inline import всё ещё не убран

Остаточный inline import `from app.core.exceptions import NotFoundError` при том, что `NotFoundError` уже импортирован на уровне модуля (строка 29). Мелочь, но нарушает единообразие.

---

### Обновлённая оценка бэкенда

**Backend: 8.5/10** (было 8/10)

Серьёзная работа проделана: 9 из 12 замечаний исправлены, добавлен целый модуль diary (828 строк service, 373 строки router) с правильной архитектурой, audit trail, time window validation. ZSET + pipeline в auth — хорошее решение. Savepoint pattern в waitlist теперь правильный.

Оставшиеся незакрытые пункты:
1. **Rate limiting** (4.1) — по-прежнему нет, всё ещё вектор DoS
2. **Test isolation** (7.1) — `db_session` fixture без transaction wrapping
3. **Redundant import** (6.1) — мелочь

Новые замечания в diary модуле — не критичные (filter DRY, missing CHECK constraint), но стоит закрыть для consistency с остальной кодовой базой.

---

### Обновлённый итоговый блок

**Итоговая оценка: 7.5/10** (Backend: 8.5/10, Frontend: 6/10 — не пересматривался)

**🔴 Критично исправить:** (все бэкенд-critical закрыты!)
- ~~2.1, 2.2, 2.3~~ — исправлены
- **[FE]** 10.1, 10.5 — по-прежнему critical на фронтенде/инфре (если не уже исправлены в main)

**🟡 Открытые рекомендации:**
1. ~~3.1~~ ✅ | ~~4.2~~ ✅ | ~~5.1~~ ✅ | ~~5.2~~ ✅ | ~~5.3~~ ✅ | ~~6.2~~ ✅
2. **4.1** — Rate limiting на `/auth/telegram` (по-прежнему открыт)
3. **7.1** — Test isolation в `conftest.py` (по-прежнему открыт)
4. **11.1** — DRY фильтры в diary listing functions (новый)
5. **11.2** — `first_purchase_only` считает PENDING (новый)
6. **11.3** — `check_type` без `CheckConstraint` (новый)

**🟢 Открытые suggestions:**
1. **6.1/11.5** — Redundant import в `purchase_router.py:122`
2. **11.4** — `diary_comment_max_length` config не используется в schemas