# Аудит — публичный профиль мастера + avatar в деталях практики (5dfeed1..ef7b703)

**Язык / Стек:** Python 3.12 · FastAPI · SQLAlchemy 2.0 async · PostgreSQL · Pydantic v2  
**Дата:** 2026-05-23  
**Диапазон коммитов:** `5dfeed1..ef7b703`  
**Файлов проверено:** 7 (masters/router.py, masters/service.py, masters/schemas.py, practices/schemas.py, practices/service.py, tests/test_master_public.py, scripts/seed.py)

---

## Раздел 1 — Общий обзор

Компактный, хорошо сфокусированный PR: добавлен публичный endpoint `GET /masters/{user_id}` для просмотра профиля мастера любым аутентифицированным пользователем, схема `MasterPublicResponse` с явной границей безопасности по финансовым и контактным полям, поле `master_avatar_url` в деталях практики, и расширение кортежа возвращаемого значения `get_practice()` с 3 до 4 элементов.

**Что добавлено / изменено:**
- **Backend (router):** `GET /masters/{user_id}` объявлен после всех `/me*`-маршрутов — порядок объявления правильный, наличие пояснительного комментария в коде фиксирует намерение.
- **Backend (service):** `get_public_master_profile()` — 3 последовательных DB-запроса (main SELECT + practices_count + reviews_count); 404 при отсутствии профиля или статусе, отличном от `"verified"` — P-08 паттерн соблюдён.
- **Backend (schemas):** `MasterPublicResponse` исключает финансовые (`frozen_cents`, `available_cents`, `payout`, `min_withdrawal_cents`, `withdrawal_fee_cents`) и контактные (`email`, `phone`) поля; docstring явно документирует границу изоляции.
- **practices/service:** кортеж `get_practice()` расширен до 4 элементов (`master_avatar_url`); единственный вызывающий — `get_practice_detail()` — обновлён. `update_practice`, `delete_practice`, `cancel_practice` используют собственные `SELECT … FOR UPDATE` и `get_practice()` не вызывают — изменение безопасно.
- **Тесты:** 525 строк, покрывают все ключевые сценарии: success, 404 по всем причинам, 401 без авторизации, leakage-тест чувствительных полей, защита маршрута `/me` от shadowing динамическим `/{user_id}`.
- **Seed:** все 16 шаблонов практик получили явные `direction/difficulty/style`.

Архитектурное качество высокое. Критических ошибок и предупреждений не выявлено. Выявлено 3 SUGGESTION.

**Оценка: 9/10**

---

## Раздел 2 — Критические баги и логические ошибки

Не выявлено.

Маршрут `/{user_id}` объявлен строго после всех литеральных маршрутов `/me`, `/me/...` — FastAPI не может перехватить `/me` как UUID. P-08 паттерн корректно применён: как несуществующий профиль, так и профиль со статусом, отличным от `"verified"`, возвращают одинаковый 404, не раскрывая факт существования заявки. Поле `status: str` в `MasterPublicResponse` всегда будет равно `"verified"` (иное приводит к 404), что делает его избыточным, но не создаёт логической ошибки.

---

## Раздел 3 — Обработка ошибок

Не выявлено.

Все пути завершения `get_public_master_profile()` покрыты: `None` от main SELECT → 404, `status != "verified"` → 404. Счётчики (`practices_count`, `reviews_count`) используют `func.count()` через `session.scalar()` — при отсутствии строк возвращают `0`, не `None`. `display_name = prof.get("display_name") or first_name` корректно обрабатывает пустую строку через `or`, а не только `None`.

---

## Раздел 4 — Безопасность

Не выявлено.

`MasterPublicResponse` содержит только публичные поля; тест `test_no_sensitive_fields_leaked` явно проверяет отсутствие `frozen_cents`, `available_cents`, `payout`, `min_withdrawal_cents`, `withdrawal_fee_cents`, `email`, `phone`, `certifications`, `documents`, `stats` в ключах ответа. Все запросы параметризованы через SQLAlchemy ORM — SQL injection исключён. `user_id` в пути — UUID, FastAPI автоматически отклоняет невалидные форматы с 422.

---

## Раздел 5 — Производительность

### ~~SUGGESTION-1~~ — `get_public_master_profile`: параллелизация COUNT-запросов через `asyncio.gather`

> **Отозвано** (2026-05-23, по результату review). Первоначальное предложение — использовать `asyncio.gather` для параллельного запуска двух COUNT-запросов — **технически некорректно**.
>
> `AsyncSession` SQLAlchemy **не является потокобезопасной и не поддерживает конкурентные операции на одном объекте сессии**. Два `session.scalar(...)` внутри `asyncio.gather` на одной сессии вызовут `sqlalchemy.exc.InterfaceError: already executing`. Реальная параллелизация требует двух отдельных сессий (`AsyncSession`), overhead которых (2× acquire из connection pool + 2× overhead asyncio task) превышает выигрыш от двух лёгких COUNT по индексу на поле `master_id`.
>
> Текущий последовательный код **корректен** для данного контекста: endpoint за авторизацией, detail-страница (не горячий цикл). **Won't fix** — оба COUNT-запроса лёгкие, выполняются по индексу, endpoint не является узким местом.

---

## Раздел 6 — Регрессия конфига

Не выявлено.

Новый endpoint не вносит изменений в конфиг, env-переменные или middleware. Seed-скрипт получил явные значения `direction/difficulty/style` для всех 16 шаблонов — регрессий в существующих шаблонах нет. Fallback `template.get("direction", "meditation")` фактически мёртвый код (все шаблоны теперь явные), но и вреда не несёт.

---

## Раздел 7 — Граничные случаи и логика

### 🟢 SUGGESTION-2 — `reviews_count` включает отзывы на удалённые и отменённые практики

`backend/app/modules/masters/service.py` · `reviews_count_stmt`

Запрос объединяет `Feedback → Practice WHERE master_id`, но не фильтрует `Practice.status`. Отзывы на удалённые или отменённые практики попадают в счётчик.

```python
# Текущий запрос:
reviews_count_stmt = (
    select(func.count(Feedback.id))
    .join(Practice, Feedback.practice_id == Practice.id)
    .where(Practice.master_id == user_id)
)
```

Поведение может быть намеренным — отзывы являются неизменяемыми историческими записями, и пользователь, оставивший отзыв, вправе видеть его в публичном счётчике. Однако это нигде не задокументировано.

```python
# Вариант, если нужно считать только активные практики:
reviews_count_stmt = (
    select(func.count(Feedback.id))
    .join(Practice, Feedback.practice_id == Practice.id)
    .where(
        Practice.master_id == user_id,
        Practice.status.notin_(_NON_COUNTABLE_PRACTICE_STATUSES),
    )
)
```

Если текущее поведение намеренно — добавить комментарий в коде: `# Intentional: reviews are immutable; deleted/cancelled practices keep their feedback counted`.

---

## Раздел 8 — Качество кода (UX и семантика)

### 🟢 SUGGESTION-3 — Комментарий к `master_avatar_url` описывает реализацию, а не семантику поля

`backend/app/modules/practices/schemas.py` · `PracticeResponse.master_avatar_url`

```python
# Текущий комментарий:
master_avatar_url: str | None = None
# Populated only by the detail endpoint via get_practice(); list endpoints leave it None
```

Комментарий привязан к конкретной функции `get_practice()` и описывает текущее поведение реализации. Если завтра другой endpoint начнёт заполнять это поле (например, `list_my_practices` для мастера), комментарий устареет и станет вводящим в заблуждение.

Правильнее перенести это пояснение в место, где формируется данные:

```python
# В schemas.py — только семантика поля:
master_avatar_url: str | None = None
"""URL аватара мастера. Заполняется только там, где явно передаётся в practice_to_response()."""

# В service.py — practice_to_response() или get_practice_detail():
# NOTE: master_avatar_url populated here; list endpoints intentionally pass None
resp = practice_to_response(..., master_avatar_url=master_avatar_url)
```

**Объяснение:** схема описывает структуру данных, а не детали реализации отдельных endpoint'ов. Миграция комментария делает схему стабильнее при рефакторинге.

---

## Раздел 9 — Тестируемость

Отличное покрытие. 525 строк `test_master_public.py` включают:
- success-кейс с проверкой всех публичных полей
- `practices_count` исключает `draft`/`deleted` (4 считаются, 2 нет)
- `reviews_count` через 2 рецензентов
- 404 для не-мастера, несуществующего UUID, pending-мастера
- 401 без авторизации
- leakage-тест по точному списку запрещённых полей
- `test_me_not_shadowed_by_dynamic_route` — образцовый защитный тест на порядок маршрутов
- `master_avatar_url` present/absent в detail vs list практики

`_insert_feedback` создаёт реальный `Booking` для удовлетворения FK-ограничения и документирует причину в docstring — правильный подход.

---

## Раздел 10 — AI-паттерны

Ни один из 20 паттернов не выявлен.

- Кортеж из 4 элементов в `get_practice()` изменён безопасно: единственный вызывающий обновлён; `update_practice` / `delete_practice` / `cancel_practice` используют собственные `SELECT … FOR UPDATE` и не затронуты. Никакого фантомного кода.
- `display_name = prof.get("display_name") or first_name` — правильный fallback, не генерирует лишние запросы.
- Нет `SELECT *`, нет N+1 паттернов в списке.

---

## Раздел 11 — Кросс-модульная согласованность

### Согласованности соблюдены

| Компонент | Паттерн | Статус |
|-----------|---------|--------|
| Порядок маршрутов | литеральные перед динамическими | Соблюдён |
| Privacy паттерн (P-08) | 404 без раскрытия существования | Соблюдён |
| Схема безопасности | финансовые/контактные поля исключены | Соблюдён |
| `practice_to_response()` | keyword-arg расширение без ломающих изменений | Соблюдён |
| Аутентификация | `get_current_user` — любой авторизованный может смотреть | Соблюдён |
| ORM агрегаты | live COUNT вместо кешированного `data.stats` | Соблюдён |

### Замечаний по несогласованности нет

Все новые компоненты следуют устоявшимся паттернам проекта: стиль импортов, именование функций, структура сервисного слоя.

---

## Раздел 12 — Миграции

Изменений в миграциях нет. Новый endpoint работает с существующей схемой БД. Изменений в моделях не вносилось.

Замечаний нет.

---

## Раздел 13 — Изолированные файлы

Все новые файлы и функции подключены и достижимы:
- `get_public_master_profile()` зарегистрирована в роутере
- `MasterPublicResponse` используется как тип ответа endpoint'а
- `master_avatar_url` в `PracticeResponse` заполняется в `get_practice_detail()` через `practice_to_response()`
- `test_master_public.py` входит в тестовую сборку

Изолированных источников нет.

---

## Итоговая оценка

**9/10** — Чистый, хорошо спроектированный PR. Граница безопасности `MasterPublicResponse` явная и верифицирована тестами. Порядок маршрутов корректен и задокументирован. P-08 паттерн выдержан. S-1 отозвано (asyncio.gather на одной AsyncSession — антипаттерн; реальная параллелизация дороже выигрыша). Два оставшихся SUGGESTION носят профилактический характер: документирование намерения по `reviews_count`, перенос пояснительного комментария из схемы в сервис.

---

🔴 CRITICAL — обязательно до шипа:
- нет

🟡 WARNING — рекомендуется исправить:
- нет

🟢 SUGGESTION — желательно:
- ~~S-1~~: ~~`service.py` — объединить через `asyncio.gather`~~ — **отозвано**: AsyncSession не поддерживает конкурентные запросы; последовательный код корректен
- S-2: `service.py` — задокументировать намерение по `reviews_count`: считать ли отзывы на удалённые/отменённые практики или добавить фильтр по статусу
- S-3: `practices/schemas.py` — перенести комментарий об условиях заполнения `master_avatar_url` из схемы в `practice_to_response()` / `get_practice_detail()`

---

| Severity | Кол-во |
|----------|--------|
| 🔴 CRITICAL | 0 |
| 🟡 WARNING | 0 |
| 🟢 SUGGESTION | 2 (1 отозвано) |
| **Итого** | **2** |
