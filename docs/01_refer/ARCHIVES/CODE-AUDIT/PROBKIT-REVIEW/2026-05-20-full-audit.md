# VELO — Полный аудит кодовой базы (ветка main)
**Дата:** 2026-05-20  
**Стек:** Python 3.12 / FastAPI / SQLAlchemy 2.0 async / PostgreSQL / Redis / Vue 3 / TypeScript / Pinia  
**Тип проекта:** Монолит (API) + SPA (Telegram Mini App)  
**Стадия:** MVP / Production-ready  
**Критичность:** Высокая (финансовые транзакции, двойная бухгалтерия)

---

## 1. Обзор

VELO — платформа для велнес-практик. Бэкенд: FastAPI + SQLAlchemy async с модульной структурой (auth, practices, bookings, payments, promos, diary, notifications, withdrawals, admin). Фронтенд: Vue 3 + Pinia как Telegram Mini App.

**Архитектурные особенности:**
- Двойная бухгалтерия (UserLedger / MasterLedger / CompanyLedger) с кэшируемыми балансами и `SUM = 0` инвариантом
- Optimistic locking через `SELECT ... FOR UPDATE` на критических путях
- Антиреплей + rate-limiting для Telegram auth через Redis
- Система семафоров консистентности (22 проверки)
- Нотификационный процессор как фоновый asyncio.Task

**Качество в целом высокое**: аккуратная обработка транзакций, последовательное применение паттернов, хорошая документация в комментариях. Ошибки сосредоточены в нескольких точках с высокой ценой.

**Оценка: 7/10**

---

## 2. Критические баги и логические ошибки

### 🔴 CRITICAL — Bypass верификации суммы Stripe при `amount_total=null`

**Файл:** `backend/app/modules/payments/stripe.py:367`

```python
# ❌ Текущий код
stripe_amount = event_data.get("amount_total")
if stripe_amount is not None and stripe_amount != payment.amount_cents:
    # ... mark as FAILED
    return payment

# Если stripe_amount is None — проверка пропускается, баланс кредитуется
```

**Проблема:** Если Stripe возвращает событие без поля `amount_total` (edge case в некоторых версиях API, либо при форсированном тест-вебхуке без суммы), условие `stripe_amount is not None` равно `False`, вся проверка пропускается, и функция продолжает кредитовать баланс пользователя. Это критический обход защиты от суммовых несоответствий (CRITICAL-3, который явно задокументирован в заголовке файла).

**Вектор:** Атакующий или баг в интеграции → баланс кредитуется на произвольную сумму при нулевом `amount_total`.

```python
# ✅ Исправление: treat None как несоответствие
stripe_amount = event_data.get("amount_total")
if stripe_amount is None or stripe_amount != payment.amount_cents:
    logger.critical(
        "stripe_amount_mismatch",
        payment_id=str(payment.id),
        expected_cents=payment.amount_cents,
        stripe_cents=stripe_amount,
        stripe_session_id=stripe_session_id,
    )
    payment.status = PaymentStatus.FAILED.value
    payment.stripe_metadata = {
        "stripe_event": {
            "customer_email": event_data.get("customer_email"),
            "amount_total": stripe_amount,
            "currency": event_data.get("currency"),
        },
        "failure_reason": "amount_mismatch" if stripe_amount is not None else "missing_amount_total",
    }
    await record_audit(...)
    return payment
```

---

### 🔴 CRITICAL — `zoom_link` не валидируется как URL

**Файл:** `backend/app/modules/practices/schemas.py:81-82`

```python
# ❌ Текущий код
zoom_link: str | None = Field(
    default=None, max_length=settings.practice_zoom_link_max_length,
)
```

Поле принимает любую строку до 500 символов. Мастер может ввести `javascript:alert(1)`, `file:///etc/passwd`, `data:text/html,...`, или просто случайный текст. Это поле отображается в интерфейсе как ссылка для пользователей, что создаёт XSS-вектор через `javascript:` scheme, а также фишинг через произвольные домены.

```python
# ✅ Исправление: добавить field_validator
from pydantic import AnyHttpUrl, field_validator

zoom_link: str | None = Field(
    default=None, max_length=settings.practice_zoom_link_max_length,
)

@field_validator("zoom_link")
@classmethod
def zoom_link_must_be_https(cls, v: str | None) -> str | None:
    if v is None:
        return v
    if not v.startswith("https://"):
        raise ValueError("zoom_link must be an HTTPS URL")
    return v
```

---

### 🟡 WARNING — Race condition в `validate_promo` + `create_booking`

**Файл:** `backend/app/modules/payments/purchase_router.py:83-93`

```python
# ❌ Текущий код
if body and body.promo_code:
    practice = await session.get(Practice, practice_id)  # без FOR UPDATE
    if not practice:
        raise NotFoundError("Practice not found")
    promo = await validate_promo(code=body.promo_code, practice=practice, ...)

booking = await create_booking(user, practice_id, session, promo=promo)
```

`validate_promo` проверяет `max_uses` мягко (soft check), но между валидацией и атомарным инкрементом в `increment_promo_usage` есть окно гонки. Если N запросов одновременно пройдут `validate_promo` с `used_count = max_uses - 1`, все пройдут soft check, но только один пройдёт атомарный `UPDATE`. Остальные получат `ConflictError` — **это корректное поведение**, но ещё есть более тонкая проблема: `practice` загружается без `FOR UPDATE` в роутере, а затем та же практика загружается с `FOR UPDATE` внутри `create_booking`. Это двойная нагрузка на БД при каждом бронировании с промокодом. Не критично, но избыточно.

```python
# ✅ Исправление: убрать преждевременную загрузку практики
# create_booking уже загружает practice с FOR UPDATE — используем её
booking = await create_booking(user, practice_id, session, promo_code=body.promo_code if body else None)
# Или: выполнять validate_promo внутри create_booking/create_purchase_for_booking
```

---

## 3. Обработка ошибок

### 🟡 WARNING — `get_db_reader` не ставит `READ ONLY` на уровне БД

**Файл:** `backend/app/core/database.py:106-113`

```python
# ❌ Текущий код
async def get_db_reader() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()
```

Сессия откатывается после каждого запроса, но без `SET TRANSACTION READ ONLY`. Код, случайно вызывающий `session.add()` или `session.execute(UPDATE ...)` внутри read-only эндпоинта, выполнит мутацию до роллбека. Защита — только на уровне дисциплины.

```python
# ✅ Исправление
async def get_db_reader() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    session = factory()
    try:
        await session.execute(text("SET TRANSACTION READ ONLY"))
        yield session
    finally:
        await session.rollback()
        await session.close()
```

---

### 🟡 WARNING — `updated_at` не обновляется при bulk UPDATE через core

**Файл:** `backend/app/modules/payments/purchase.py:279-287`, `backend/app/modules/payments/refund.py:448-456`

```python
# ❌ Текущий код — bulk UPDATE через SQLAlchemy core
unfreeze_stmt = (
    update(MasterLedger)
    .where(...)
    .values(is_frozen=False)
)
await session.execute(unfreeze_stmt)
```

`TimestampMixin.updated_at` использует `onupdate=func.now()` — это SQLAlchemy ORM hook, который срабатывает только при изменении через ORM. Bulk `update()` обходит этот механизм. `MasterLedger` не использует `TimestampMixin` (это задокументировано), но `Waitlist` — использует, и bulk update в `refund.py:451` не обновит `updated_at`. Это не критично, но приводит к некорректным метаданным.

---

### 🟡 WARNING — Потеря деталей ошибки Stripe в логах

**Файл:** `backend/app/modules/payments/stripe.py:150-158`

```python
# ❌ Текущий код
except stripe.StripeError as exc:
    logger.error(
        "stripe_checkout_creation_failed",
        error=str(exc),
    )
    raise BadRequestError("Failed to create payment session") from None
```

`from None` подавляет оригинальный traceback. При анализе инцидентов в логах будет только `str(exc)`, без stack trace. Stripe ошибки могут включать `request_id`, `code`, `http_status` — всё это теряется.

```python
# ✅ Исправление
except stripe.StripeError as exc:
    logger.error(
        "stripe_checkout_creation_failed",
        error=str(exc),
        stripe_code=getattr(exc, 'code', None),
        stripe_request_id=getattr(exc, 'request_id', None),
    )
    raise BadRequestError("Failed to create payment session") from exc
```

---

## 4. Безопасность

### 🟡 WARNING — `X-Forwarded-For` доверяется без проверки trusted proxies

**Файл:** `backend/app/core/middleware.py:122-124`

```python
# ❌ Текущий код
forwarded = _extract_header(scope, b"x-forwarded-for")
if forwarded:
    return forwarded.split(",")[0].strip()
```

Клиент может отправить заголовок `X-Forwarded-For: 1.2.3.4` и он будет записан в audit log как подлинный IP. Это позволяет подделывать IP в финансовых записях аудита, что критично при юридическом расследовании.

```python
# ✅ Исправление: брать последний IP из цепочки (выставляется доверенным Nginx)
# или принимать X-Forwarded-For только при наличии trusted proxy list
if forwarded:
    # Last entry is set by the trusted upstream proxy
    ips = [ip.strip() for ip in forwarded.split(",")]
    return ips[-1]  # Nginx добавляет реальный IP последним
```

---

### 🟡 WARNING — `avatar_url` из Telegram не валидируется

**Файл:** `backend/app/modules/auth/service.py:276, 299`

```python
# ❌ Текущий код
avatar_url=telegram_user.get("photo_url"),
```

`photo_url` из Telegram initData не проверяется на формат URL. Хотя Telegram подписывает initData и подпись верифицируется, поле `photo_url` — строка в JSON. Если бы подпись была каким-то образом скомпрометирована или в тестовом режиме с `dev-fake-bot-token`, произвольный URL может быть сохранён в `users.credentials` и `users.avatar_url`. В production эта угроза минимальна из-за HMAC, но стоит добавить базовую проверку.

---

### 🟢 SUGGESTION — Rate limiting только на auth, не на topup/purchase

**Файл:** `backend/app/modules/payments/router.py`, `purchase_router.py`

Эндпоинты `POST /payments/topup` и `POST /practices/{id}/purchase` не имеют rate limiting. Аутентифицированный пользователь может выполнять сотни запросов в секунду. Для топапа это может создавать большой объём Stripe Checkout Sessions (платная операция). Рекомендуется добавить лимит (например, 10 запросов в минуту) через Redis, по аналогии с auth.

---

### 🟢 SUGGESTION — `sessionStorage` для токена аутентификации

**Файл:** `frontend/src/stores/auth.ts:38`

```typescript
sessionStorage.setItem(TOKEN_KEY, newToken)
```

`sessionStorage` доступен всем JS-скриптам на странице (без `HttpOnly`). Для Telegram Mini App это стандартная практика, поскольку используется WebView без cookie поддержки. Однако стоит убедиться, что никакие сторонние скрипты не подключаются к фронтенду.

---

## 5. Производительность

### 🟡 WARNING — N+1 запросы в `refund_booking` при отмене практики

**Файл:** `backend/app/modules/payments/refund.py:434-444`

```python
# ❌ Текущий код — цикл с await внутри
for booking in bookings:
    booking.status = BookingStatus.CANCELLED.value
    ...
    await refund_booking(booking=booking, practice=practice, session=session, ...)
    # Внутри refund_booking:
    #   await session.get(Purchase, ...)       — 1 запрос на booking
    #   await _get_master_frozen_amount(...)   — 1 запрос (load Promo)
    #   await _is_company_promo(...)           — ещё 1 запрос (load Promo снова!)
    #   await record_master_ledger(...)        — несколько запросов
    #   await record_user_ledger(...)          — несколько запросов
```

При отмене практики со 100 участниками это даёт ~600+ SQL запросов в одной транзакции. Для `_get_master_frozen_amount` и `_is_company_promo` — загрузка одной и той же `Promo` дважды на каждый booking.

```python
# ✅ Исправление: объединить в один метод, загружать Promo один раз
async def _resolve_promo_type(purchase: Purchase, session: AsyncSession) -> tuple[bool, int]:
    """Returns (is_company, master_frozen_amount) — один DB запрос."""
    if purchase.promo_id and purchase.discount_cents > 0:
        promo = await session.get(Promo, purchase.promo_id)
        if promo and promo.type == PromoType.COMPANY.value:
            return True, purchase.amount_cents
    return False, purchase.paid_cents
```

---

### 🟡 WARNING — Дублирование паттерна подсчёта в `list_withdrawals_admin`

**Файл:** `backend/app/modules/admin/withdrawals/service.py:216-222`

```python
# ❌ Текущий код — устаревший паттерн с двумя base queries
base = select(Withdrawal)
count_base = select(func.count(Withdrawal.id))

if status_filter:
    base = base.where(Withdrawal.status == status_filter)
    count_base = count_base.where(Withdrawal.status == status_filter)  # дублирование фильтра
```

Все остальные сервисы (bookings, purchases, diary) используют subquery-паттерн (B-05). Это нарушение консистентности и потенциальный источник бага при добавлении нового фильтра.

```python
# ✅ Исправление: subquery-паттерн
base = select(Withdrawal)
if status_filter:
    base = base.where(Withdrawal.status == status_filter)

total = (
    await session.execute(
        select(func.count()).select_from(base.subquery())
    )
).scalar_one()
```

---

### 🟢 SUGGESTION — Двойная загрузка `Practice` в purchase endpoint при промокоде

**Файл:** `backend/app/modules/payments/purchase_router.py:84-95`

```python
# ❌ Текущий код
if body and body.promo_code:
    practice = await session.get(Practice, practice_id)  # загрузка #1, без FOR UPDATE
    ...
booking = await create_booking(...)
# create_booking → select Practice WHERE id=... WITH FOR UPDATE            # загрузка #2
```

При наличии промокода практика загружается дважды. Решение: передавать `promo_code` в `create_booking` и выполнять `validate_promo` уже после блокировки практики.

---

## 6. Качество кода

### 🟡 WARNING — Циклический импорт через lazy import внутри функции

**Файл:** `backend/app/modules/bookings/service.py:382`, `backend/app/modules/payments/refund.py:462`

```python
# ❌ Текущий код
from app.modules.waitlist.service import process_waitlist   # внутри cancel_booking()
from app.modules.bookings.service import recalculate_participants  # внутри refund.py
```

Lazy imports — признак циклической зависимости между модулями. Это работает, но затрудняет понимание графа зависимостей и может вызвать проблемы при рефакторинге. Рекомендуется вынести `recalculate_participants` в отдельный модуль `bookings/participants.py` и импортировать из него.

---

### 🟢 SUGGESTION — `_FINALIZABLE_PRACTICE_STATUSES` == `_JOINABLE_PRACTICE_STATUSES`

**Файл:** `backend/app/modules/bookings/service.py:97-105`

```python
# ❌ Текущий код — две идентичные константы
_JOINABLE_PRACTICE_STATUSES = {
    PracticeStatus.SCHEDULED.value,
    PracticeStatus.LIVE.value,
}
_FINALIZABLE_PRACTICE_STATUSES = {
    PracticeStatus.SCHEDULED.value,
    PracticeStatus.LIVE.value,
}
```

Если в будущем семантика разойдётся — один будет забыт. Если они семантически одинаковы — одна константа с говорящим именем.

---

### 🟢 SUGGESTION — Жёстко зашитые строки в `refund_all_bookings_for_practice`

**Файл:** `backend/app/modules/payments/refund.py:437`

```python
booking.cancellation_reason = "Practice cancelled by master"  # magic string
```

Если frontend или другой код switch'ится по этой строке — хрупко. Лучше константа или enum.

---

## 7. Тестируемость

### 🟡 WARNING — Тест для Stripe `amount_total=None` отсутствует

**Файл:** `backend/tests/test_payments_topup.py`

В тестах Stripe webhook проверяются сценарии: completed (match), completed (mismatch), expired. Но не проверяется сценарий `amount_total=None` (отсутствующее поле). Именно этот кейс является Critical-уязвимостью (п.2.1 выше) и должен быть покрыт тестом:

```python
# ✅ Добавить тест:
async def test_webhook_completed_missing_amount_total(db_session, ...):
    """Если amount_total отсутствует — платёж должен быть помечен как FAILED."""
    event_data = {
        "id": payment.stripe_session_id,
        # amount_total намеренно отсутствует
        "customer_email": "test@example.com",
    }
    result = await handle_checkout_completed(event_data, db_session)
    assert result.status == PaymentStatus.FAILED.value
```

---

### 🟡 WARNING — Отсутствие интеграционных тестов для фронтенда

Фронтенд (Vue 3 + Pinia) покрыт только юнит-тестами для утилит (`format.test.ts`, `usePagination.test.ts`). Отсутствуют:
- E2E тесты критических флоу (auth → book → pay → cancel)
- Компонентные тесты для `BookingCard`, `TopupView`, `PracticeDetailView`
- Тест для URL-whitelist в `TopupView` (C-1 fix)

---

### 🟢 SUGGESTION — Тесты используют общий Redis без изоляции между тестовыми файлами

**Файл:** `backend/tests/conftest.py:65-80`

`flush_auth_redis_keys` очищает `init_data_used:*` и `auth_rate:*` перед каждым тестом. При параллельном запуске тестов (`pytest-xdist`) это условие нарушается: два теста могут очищать ключи одновременно. В текущей конфигурации тесты запускаются последовательно, поэтому не критично, но стоит иметь в виду.

---

## 8. Предложения по рефакторингу

### Унифицировать паттерн подсчёта записей

Три файла (`withdrawals/service.py`) используют устаревший паттерн с `count_base`, остальные 10+ используют subquery. Привести `list_withdrawals_admin` к единому стандарту (уже описано в п.5.2).

### Вынести `recalculate_participants` из `bookings/service.py`

Функция `recalculate_participants` импортируется из `bookings/service.py` в `payments/refund.py` через lazy import (циклическая зависимость). Вынести в `bookings/participants.py`:

```
bookings/
  service.py      — booking CRUD
  participants.py — recalculate_participants (без зависимостей от payments)
```

---

## 9. Мелкие улучшения

### 🟢 SUGGESTION — `stripe.py` использует `stripe>=8.0.0,<9.0` — Stripe v9 уже вышел

**Файл:** `backend/pyproject.toml:22`

```toml
# ❌ Текущий
"stripe>=8.0.0,<9.0",

# ✅ Проверить совместимость и обновить до stripe v9
# Stripe v9 содержит улучшения в типах и безопасности
```

---

### 🟢 SUGGESTION — `VITE_API_BASE_URL` defaults to `''` без явного fallback

**Файл:** `frontend/src/api/client.ts:21`

```typescript
const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
```

Пустая строка означает same-origin. Это корректно для production за Nginx, но в dev без переменной все запросы уйдут на порт 5173 (Vite dev server), что может смущать разработчиков. Добавить явный комментарий или дефолт для dev.

---

### 🟢 SUGGESTION — `get_current_master` делает два DB-запроса

**Файл:** `backend/app/modules/auth/dependencies.py:183-213`

`get_current_master` зависит от `get_current_user` (который читает User из БД), а потом читает `MasterProfile` отдельным запросом — в той же read-only сессии. Это 2 SELECT на каждый запрос мастера. Можно объединить в один JOIN-запрос, хотя оба запроса быстрые (по PK).

---

## 10. AI-паттерны

### 🟢 SUGGESTION — Избыточная документация комментариями

По всему бэкенду каждый файл открывается большим docblock с историей изменений (`updated Phase X.Y`, `FIX 2.2`, `CRITICAL-4`, `WARNING-4`). Это напоминает AI-generated annotations. Такие истории изменений быстро устаревают и должны жить в git commits, а не в коде. Текущее решение создаёт maintenance burden: при рефакторинге нужно обновлять и код, и заголовки.

### 🟡 WARNING — Privilege escalation risk при смене роли

**Файл:** `backend/app/modules/admin/users/service.py`

Эндпоинты изменения роли пользователя (если существуют) должны быть защищены особо тщательно. В коде роль проверяется через `user.role != UserRole.ADMIN` — это корректно, но любое изменение логики проверки роли должно проходить через security review. Код демонстрирует повышенную осторожность (паттерн P-08 — 404 вместо 403), что положительно.

---

## 11. Межмодульная согласованность

### 🟡 WARNING — Непоследовательность паттерна count в сервисах

| Сервис | Паттерн |
|--------|---------|
| `bookings/service.py` | subquery (B-05) ✅ |
| `payments/purchase.py` | subquery (B-05) ✅ |
| `diary/service.py` | subquery (B-05) ✅ |
| `admin/withdrawals/service.py` | parallel count_base ❌ |
| `promos/service.py` | параллельный count ❌ |
| `withdrawals/service.py` | параллельный count ❌ |

Три модуля используют устаревший паттерн с дублированием фильтров. При добавлении нового фильтра легко забыть продублировать его в `count_base`.

---

### 🟢 SUGGESTION — Inconsistent: `list_master_practices` vs `list_public_practices` count queries

**Файл:** `backend/app/modules/practices/service.py:530, 613`

`list_master_practices` использует отдельный `count_query` (параллельный паттерн), тогда как `list_public_practices` тоже использует отдельный — оба не используют subquery. В отличие от bookings/purchases которые уже мигрированы на subquery. Это `TODO` для единообразия.

---

## 12. Аудит тестов

**Обнаружено тестовых файлов:** 31 файл, ~16 800 строк тестов.

**Покрытие критических путей:**
| Функциональность | Покрытие |
|---|---|
| Auth (Telegram + replay + rate limit) | ✅ Хорошее |
| Bookings (create/cancel/finalize) | ✅ Хорошее |
| Payments (topup, webhook, idempotency) | ✅ Хорошее |
| Promo (validate, apply, race condition) | ✅ Хорошее |
| Cancellation policy (deadline) | ✅ Хорошее |
| Double-entry invariant | ✅ test_ledger.py |
| Consistency semaphores | ✅ test_admin_consistency.py |
| **Stripe amount_total=None** | ❌ **Отсутствует** |
| **zoom_link XSS** | ❌ **Отсутствует** |
| **Frontend integration** | ❌ **Отсутствует** |

**Качество тестов:** Высокое. Тесты проверяют бизнес-логику (не только happy path), используют реальную БД (не моки), покрывают race conditions через отдельные тесты с concurrent requests.

---

## 13. Orphan Source Files

Все исходные файлы модулей подключены через `main.py` или импортируются из других модулей.

**Потенциальные orphans:**
- `backend/app/modules/library/models.py` — модуль упоминается как `Phase 9.2 stub` в `main.py`. Модели импортированы только для Alembic. Фактического использования нет.
- `backend/scripts/repair_*.py` — одноразовые repair-скрипты. Нет механизма предотвращения случайного повторного запуска.

---

## Итог

**Оценка: 7/10**

### 🔴 Обязательно исправить:
- `stripe.py:367` — Bypass суммовой верификации при `amount_total=None` → кредитование баланса без проверки суммы
- `practices/schemas.py:81` — `zoom_link` без URL-валидации → XSS через `javascript:` scheme

### 🟡 Стоит исправить:
- `middleware.py:122` — `X-Forwarded-For` без trusted proxy check → подделка IP в audit log
- `database.py:106` — `get_db_reader` без `SET TRANSACTION READ ONLY`
- `payments/stripe.py:150` — потеря Stripe error details через `from None`
- `payments/refund.py:91` — двойная загрузка `Promo` в `_get_master_frozen_amount` + `_is_company_promo`
- `admin/withdrawals/service.py:216` — устаревший паттерн count (несоответствие стандарту проекта)
- Тест: добавить кейс `amount_total=None` в `test_payments_topup.py`

### 🟢 Хорошо бы:
- Rate limiting на `/payments/topup` и `POST /practices/{id}/purchase`
- Вынести `recalculate_participants` для устранения циклического импорта
- Унифицировать count-паттерн в `promos/service.py`, `withdrawals/service.py`
- Добавить компонентные/E2E тесты для фронтенда
