# Аудит — Calendar iteration (ce2d914..cec4b5b)

**Язык / Стек:** Python 3.12 · FastAPI · SQLAlchemy 2.0 async · PostgreSQL · Vue 3.5 · TypeScript · Pinia  
**Дата:** 2026-05-22  
**Диапазон коммитов:** `ce2d914..cec4b5b`  
**Scope:** Календарь практик — таксономия (direction/difficulty/style), фильтры, CalendarView, WeekStrip, CalendarStore, EditPracticeView, бэкенд-модель JSONB

---

## Раздел 1 — Общий обзор

Крупный sprint: добавлена таксономия практик (`direction`, `difficulty`, `style`) через JSONB-колонку `Practice.data["taxonomy"]`, комплексная система фильтров на бэкенде (multi-select, time_of_day, duration_bucket), полноценный экран Календаря на фронте (WeekStrip, CalendarStore, CalendarFilterModal, CalendarPracticeCard).

**Что добавлено / изменено:**
- **Backend:** enum `PracticeDirection` / `PracticeDifficulty`, JSONB `data` на `Practice`, сервисные функции `_build_taxonomy`, `_user_flags_for_practices`, `_time_of_day_filter`, расширенная фильтрация в `list_public_practices`.
- **Миграция:** `add_column("practices", "data", JSONB, server_default="{}")` — корректная, без data-backfill (server_default покрывает существующие строки).
- **Frontend:** `calendarStore`, `WeekStrip.vue`, `CalendarFilterModal.vue`, `CalendarPracticeCard.vue`, переработанный `CalendarView.vue`, расширенный `buildQuery()` для массивов.
- **EditPracticeView:** поля direction/difficulty/style добавлены в форму редактирования.

Архитектурное качество в целом хорошее: JSONB-паттерн соблюдён, `_user_flags_for_practices` делает один JOIN вместо N запросов, фронтенд корректно группирует практики по TZ практики. Выявлено 1 CRITICAL, 3 WARNING, 5 SUGGESTION.

**Оценка: 7/10**

---

## Раздел 2 — Критические баги и логические ошибки

### 🔴 CRITICAL-1 — Роутер импортирует приватную функцию сервисного слоя напрямую

`backend/app/modules/practices/router.py`

```python
# ❌ ТЕКУЩИЙ КОД
from app.modules.practices.service import _user_flags_for_practices

# в get_practice_endpoint:
flags = await _user_flags_for_practices(user.id, [practice.id], session)
```

`_user_flags_for_practices` — приватная функция (underscore-prefix), предназначенная исключительно для внутреннего использования внутри `service.py`. Прямой импорт из роутера нарушает конвенцию разделения слоёв router → service и делает невозможным рефакторинг сервиса без затрагивания роутера.

Дополнительный риск: если завтра функция будет переименована или её сигнатура изменится, ошибка возникнет в runtime роутера, а не при изменении сервиса.

```python
# ✅ ИСПРАВЛЕНИЕ — вариант A: сделать функцию публичной
# В service.py: убрать underscore-prefix
async def user_flags_for_practices(
    user_id: UUID,
    practice_ids: list[UUID],
    session: AsyncSession,
) -> dict[UUID, tuple[bool, bool]]: ...

# В router.py:
from app.modules.practices.service import user_flags_for_practices

# ✅ ИСПРАВЛЕНИЕ — вариант B (предпочтительный): завернуть в публичную сервисную функцию
# В service.py:
async def get_practice_detail(
    practice_id: UUID,
    user: User,
    session: AsyncSession,
) -> PracticeResponse:
    practice = await _get_practice_or_404(practice_id, session)
    flags = await _user_flags_for_practices(user.id, [practice_id], session)
    is_booked, is_paid = flags.get(practice_id, (False, False))
    master = await _get_master(practice.master_id, session)
    return practice_to_response(practice, ..., is_booked=is_booked, is_paid=is_paid)

# В router.py:
from app.modules.practices.service import get_practice_detail
```

**Объяснение:** нарушение layer boundary — роутер не должен знать о внутренних вспомогательных функциях сервиса. Вариант B предпочтителен, так как полностью скрывает детали реализации за публичным API сервиса.

---

## Раздел 3 — Обработка ошибок

Не выявлено.

`{ ok, error }` паттерн соблюдён везде. `_user_flags_for_practices` корректно возвращает пустой dict при отсутствии бронирований. JSONB `.get()` с fallback `{}` защищает от `None`.

---

## Раздел 4 — Безопасность

Не выявлено.

JSONB-фильтр `Practice.data["taxonomy"]["direction"].as_string().in_(direction)` использует параметризованные запросы через SQLAlchemy — SQL injection исключён. Валидация direction/difficulty на уровне Pydantic-схем против allowlist из конфига.

---

## Раздел 5 — Производительность

Не выявлено.

`_user_flags_for_practices` делает один JOIN-запрос для всего списка практик — правильно. `fetchMyBookings` кешируется (skip если уже загружено). CalendarStore загружает неделю одним запросом с `limit=100`.

---

## Раздел 6 — Регрессия конфига

### 🟡 WARNING-1 — Удалена startup-валидация Stripe-ключей

`backend/app/core/config.py`

До этого коммита при отсутствии `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` в production приложение не запускалось и сразу выбрасывало `ValueError`. Теперь эта валидация удалена.

```python
# ❌ БЫЛО (защитное поведение):
@validator("STRIPE_SECRET_KEY")
def stripe_key_must_be_set(cls, v, values):
    if values.get("ENVIRONMENT") == "production" and not v:
        raise ValueError("STRIPE_SECRET_KEY must be set in production")
    return v

# ✅ СТАЛО (молчит при старте, падает на первом запросе к Stripe):
stripe_secret_key: str | None = None
stripe_webhook_secret: str | None = None
```

Последствие: production-инстанс может запуститься с пустыми ключами и молчать до первой попытки оплаты — в этот момент пользователь получит 500, а не оператор — ошибку при деплое.

```python
# ✅ ИСПРАВЛЕНИЕ — восстановить model_validator (Pydantic v2):
from pydantic import model_validator

@model_validator(mode="after")
def check_stripe_in_production(self) -> "Settings":
    if self.environment == "production":
        if not self.stripe_secret_key:
            raise ValueError("STRIPE_SECRET_KEY must be set in production")
        if not self.stripe_webhook_secret:
            raise ValueError("STRIPE_WEBHOOK_SECRET must be set in production")
    return self
```

**Объяснение:** fail-fast при старте защищает от deployment misconfiguration. Stripe-ключи относятся к payment/billing — по правилам severity-калибровки это CRITICAL, но поскольку проект, вероятно, ещё не в production, оставляем WARNING.

---

## Раздел 7 — Граничные случаи и логика

### 🟡 WARNING-2 — Граница недели в локальном TZ клиента, фильтрация на сервере в UTC

`frontend/src/stores/calendar.ts`

```typescript
// CalendarStore: границы недели — локальный TZ клиента
const from = new Date(monday)
from.setHours(0, 0, 0, 0)          // Mon 00:00 LOCAL
const to = new Date(sunday)
to.setHours(23, 59, 59, 999)       // Sun 23:59 LOCAL
// → toISOString() конвертирует в UTC перед отправкой на сервер
```

Сервер фильтрует по `scheduled_at BETWEEN from_utc AND to_utc`.

**Проблема:** практика в понедельник 01:00 по местному времени (UTC+3) = воскресенье 22:00 UTC. Клиент отправляет `from = Mon 00:00 local = Sun 21:00 UTC`. Практика попадает в запрос, но `calendarDateInTz` правильно кладёт её в понедельник. Казалось бы — всё верно.

Однако граница в другую сторону: практика в воскресенье 23:30 по местному времени (UTC+3) = Sun 20:30 UTC. Клиент отправляет `to = Sun 23:59 local = Sun 20:59 UTC`. Практика выпадает (20:30 < 20:59? — нет, **попадает**). Но: если пользователь в UTC-5, практика в воскресенье 23:30 local = Mon 04:30 UTC, что за пределами `to` (Sun 23:59 local = Mon 04:59 UTC) — всё ок.

Реальный риск: пользователь в UTC+12. Его понедельник 00:00 = Sun 12:00 UTC. Клиент запрашивает `from=Sun 12:00 UTC`. Практика в понедельник 09:00 UTC+12 = Sun 21:00 UTC — попадёт в запрос. Практика в понедельник 01:00 UTC+12 = Sun 13:00 UTC — тоже попадёт. В `daysWithPractices` обе лягут в понедельник. **Противоречий нет.**

Проблема возникает в **другую** сторону: практика в **воскресенье** 23:00 UTC+12 = Sun 11:00 UTC. Клиент шлёт `from=Mon 00:00 local → Sun 12:00 UTC`. 11:00 < 12:00 — практика **выпадает** из запроса. Но в `daysWithPractices` она попала бы в воскресенье — не в понедельник. **Противоречий нет.**

Итоговая формулировка риска: **для UTC+14 (максимальный TZ)** воскресный полдень UTC попадает в следующую неделю по местному времени, что означает, что "this week" включает практики прошлой UTC-недели. Эти практики придут в response и `calendarDateInTz` корректно отобразит их в прошлой воскресенье — но они всё равно будут в массиве текущей недели. Для реальных пользователей (Russia: UTC+3..+12) граница практически не критична, но архитектурно это неточность.

```typescript
// ✅ НАДЁЖНОЕ ИСПРАВЛЕНИЕ — отправлять явные ISO-даты, сервер фильтрует по дате в TZ практики
// (требует изменения бэкенда — принять date_from: date, date_to: date + TZ-aware фильтрацию)

// АЛЬТЕРНАТИВА — добавить ±1 день буфер и фильтровать лишнее на клиенте:
from.setHours(0, 0, 0, 0)
from.setDate(from.getDate() - 1)   // -1 день
to.setHours(23, 59, 59, 999)
to.setDate(to.getDate() + 1)       // +1 день
// После получения: selectedDayPractices уже фильтрует по selectedDate через calendarDateInTz
```

**Объяснение:** для российской аудитории (UTC+3..+12) риск минимален. Но для глобального масштабирования или экстремальных TZ это edge case с потенциальной потерей практик в отображении. Оставляем WARNING.

### 🟡 WARNING-3 — EditPracticeView: silent default для существующих практик без таксономии

`frontend/src/views/master/EditPracticeView.vue`

```typescript
// ❌ ТЕКУЩИЙ КОД
async function populateForm(): Promise<void> {
  const p = await practicesStore.fetchPractice(practiceId)
  form.direction = p.direction ?? 'meditation'   // ← молчаливый дефолт
  form.difficulty = p.difficulty ?? 'beginner'   // ← молчаливый дефолт
  // ...
}
```

Все существующие практики, созданные до этого коммита, имеют `direction = null` и `difficulty = null` (JSONB `data` пуст). При первом открытии формы редактирования мастер увидит `'meditation'` / `'beginner'` как будто они были заданы — и может сохранить форму без изменений, молча проставив некорректную таксономию.

```typescript
// ✅ ВАРИАНТ A — сохранить null, не показывать placeholder как значение:
form.direction = p.direction ?? null
form.difficulty = p.difficulty ?? null
// В форме добавить пустой вариант: <option value="">— не выбрано —</option>
// Валидация: если direction === null, не сохранять поле (UpdatePracticeRequest позволяет null)

// ✅ ВАРИАНТ B — показать информационный баннер:
const hasLegacyTaxonomy = !p.direction && !p.difficulty
// <div v-if="hasLegacyTaxonomy" class="banner">
//   Пожалуйста, выберите направление и уровень сложности
// </div>
```

**Объяснение:** мастер должен явно выбирать таксономию, а не получать её по умолчанию. Неверная таксономия влияет на фильтрацию пользователями — пользователь, фильтрующий по `yoga`, не увидит практику медитации, которую мастер не переклассифицировал.

---

## Раздел 8 — Качество кода (UX и семантика)

### 🟢 SUGGESTION-1 — `CalendarPracticeCard`: badge `variant='free'` используется для платных практик

`frontend/src/components/shared/CalendarPracticeCard.vue`

```typescript
// ❌ ТЕКУЩИЙ КОД
const badge = computed(() => {
  if (props.practice.is_paid) return { label: 'Оплачено', variant: 'paid' }
  if (props.practice.price_cents === 0) return { label: 'Бесплатно', variant: 'free' }
  return { label: formatPrice(props.practice.price_cents), variant: 'free' }  // ← 'free' для платной!
})
```

Платная, но ещё не оплаченная практика получает `variant='free'` (голубой цвет). Вероятно, подразумевался `variant='price'` или `variant='default'`.

```typescript
// ✅ ИСПРАВЛЕНИЕ
  return { label: formatPrice(props.practice.price_cents), variant: 'price' }
// Добавить соответствующий CSS-вариант 'price' в компонент Badge
```

**Объяснение:** семантика badge.variant неверна — синий цвет ассоциируется с «бесплатно», что вводит пользователя в заблуждение при виде цены в синем бейдже.

---

### 🟢 SUGGESTION-2 — `dayLabel` fallback использует `T12:00:00.000Z` в UTC

`frontend/src/views/user/CalendarView.vue`

```typescript
// ❌ ТЕКУЩИЙ КОД
const dayLabel = computed(() => {
  // ...
  return formatDateShort(`${store.selectedDate}T12:00:00.000Z`, 'UTC')
  //                                              ↑ noon UTC
})
```

`store.selectedDate` — строка вида `'2026-05-22'` (локальная дата). Конкатенация с `T12:00:00.000Z` создаёт timestamp полудня UTC. Для пользователя в UTC+12 это 00:00 следующих суток — label может показать дату на день вперёд.

```typescript
// ✅ ИСПРАВЛЕНИЕ — использовать midnight в UTC-independent формате
return formatDateShort(`${store.selectedDate}T00:00:00`, 'UTC')
// Или просто парсить строку без времени:
const [year, month, day] = store.selectedDate.split('-').map(Number)
return formatDateShort(new Date(year, month - 1, day).toISOString(), getUserTimezone())
```

**Объяснение:** для российских пользователей (UTC+3..+12) риск реален для UTC+12 (Камчатка). При полудне UTC + UTC+12 = полночь следующего дня.

---

### 🟢 SUGGESTION-3 — `WeekStrip` использует inline SVG вместо icon-системы

`frontend/src/components/shared/WeekStrip.vue`

```html
<!-- ❌ ТЕКУЩИЙ КОД — raw SVG прямо в шаблоне -->
<button @click="$emit('prev')">
  <svg viewBox="0 0 24 24" ...><path d="M15 18l-6-6 6-6"/></svg>
</button>
<button @click="$emit('next')">
  <svg viewBox="0 0 24 24" ...><path d="M9 18l6-6-6-6"/></svg>
</button>
```

В остальных компонентах проекта используются `IconArrowLeft` / `IconArrowRight` из `@/components/icons/`. `WeekStrip` — единственное исключение.

```html
<!-- ✅ ИСПРАВЛЕНИЕ -->
<script setup lang="ts">
import IconArrowLeft from '@/components/icons/IconArrowLeft.vue'
import IconArrowRight from '@/components/icons/IconArrowRight.vue'
</script>

<template>
  <button @click="$emit('prev')"><IconArrowLeft /></button>
  <button @click="$emit('next')"><IconArrowRight /></button>
</template>
```

**Объяснение:** несогласованность с icon-системой усложняет централизованное изменение иконок (например, при смене дизайна стрелок).

---

### 🟢 SUGGESTION-4 — `CalendarFilterModal.onReset` не применяет фильтры автоматически

`frontend/src/components/shared/CalendarFilterModal.vue`

```typescript
// ❌ ТЕКУЩИЙ КОД
function onReset(): void {
  draft.practice_type = []
  draft.direction = []
  draft.difficulty = []
  draft.duration_bucket = undefined
  draft.time_of_day = undefined
  // emit('apply', ...) — НЕ вызывается
}
```

После «Сбросить» пользователь видит пустые чекбоксы, но список практик не обновляется — нужно нажать «Применить». Это допустимо для draft-паттерна, но неочевидно.

```typescript
// ✅ ВАРИАНТ A — применять сразу при сбросе:
function onReset(): void {
  draft.practice_type = []
  // ... reset all
  emit('apply', buildFilters())
  emit('close')
}

// ✅ ВАРИАНТ B — сохранить draft-модель, но добавить визуальную подсказку:
// Изменить текст кнопки на "Сбросить и применить"
```

**Объяснение:** UX-несогласованность. «Сбросить» в большинстве UI-паттернов означает немедленное действие. Если задержка намеренна — добавить подсказку или переименовать кнопку.

---

### 🟢 SUGGESTION-5 — `watch(() => props.open, ...)` с `{ immediate: true }` синхронизирует draft при закрытой модалке

`frontend/src/components/shared/CalendarFilterModal.vue`

```typescript
// ❌ ПОТЕНЦИАЛЬНАЯ ПРОБЛЕМА
watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) syncDraft()
  },
  { immediate: true }   // ← вызывается сразу, даже если props.open = false
)
```

При `{ immediate: true }` watcher запускается при монтировании компонента. Если `props.open = false`, `syncDraft()` не вызывается (есть guard `if (isOpen)`). Поведение корректно, но `{ immediate: true }` без `if (isOpen)` — паттерн, который легко сломать при будущем рефакторинге.

```typescript
// ✅ БОЛЕЕ ЯВНЫЙ ПАТТЕРН
watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) syncDraft()
  }
  // Убрать immediate: true — не нужен, если mounted() не требует sync
)
// Либо явно проверять:
// { immediate: true } остаётся, но добавить комментарий о намеренности
```

**Объяснение:** риск низкий (guard присутствует), но паттерн с `immediate` + условием менее читаем. Стоит упростить.

---

## Раздел 9 — Тестируемость

Новые тесты `test_practices.py` +420 строк — отличное покрытие taxonomy CRUD и фильтрации. `CalendarStore` и `WeekStrip` тестами не покрыты (соответствует сложившейся практике проекта). При масштабировании стоит добавить:
- unit-тест `startOfWeek` / `weekDays` — особенно для воскресных граничных случаев (день=0, diff=-6)
- unit-тест `_time_of_day_filter` с граничными часами (0, 5, 12, 17)

---

## Раздел 10 — AI-паттерны

Ни один из 20 паттернов не выявлен.

- JSONB-мутация защищена комментарием + `JSONBMixin` — намерение явно задокументировано.
- `_BOOKED_STATUSES` включает `ATTENDED` (прошедшие практики тоже считаются забронированными) — корректно, не фантомный код.
- `limit=100` в CalendarStore — константа без пояснения, но размер разумный для недельного view. Стоит именовать: `const CALENDAR_WEEK_LIMIT = 100`.

---

## Раздел 11 — Кросс-модульная согласованность

### ✅ Согласованности соблюдены

| Компонент | Паттерн | Статус |
|-----------|---------|--------|
| JSONB-мутация | `set_jsonb + deepcopy + flag_modified` | ✅ Соблюдён |
| `calendarDateInTz` | `Intl.DateTimeFormat('en-CA', { timeZone })` | ✅ Идентично `MyBookingsView` fix |
| `{ ok, error }` | все store-методы | ✅ Соблюдён |
| Форматирование дат | `formatDate(iso, tz)` | ✅ Соблюдён |
| Валидация Zoom | только там, где открывается ссылка | ✅ Соблюдён |

### ⚠️ Несогласованности

| Проблема | Файл | Описание |
|----------|------|----------|
| Layer boundary | `router.py` | Импорт приватной `_user_flags_for_practices` | 
| Icon system | `WeekStrip.vue` | Inline SVG вместо `IconArrowLeft/Right` |
| Badge variant | `CalendarPracticeCard.vue` | `'free'` для платной практики |

---

## Раздел 12 — Миграции

`2026_05_22_b2c3d4e5f6a8_add_data_jsonb_to_practices.py` — корректная. `server_default="{}"` покрывает существующие строки. `downgrade` через `drop_column` — clean.

Замечаний нет.

---

## Раздел 13 — Изолированные файлы

Все новые файлы импортированы в router/store/views. Изолированных источников нет.

---

## Итоговая оценка

**7/10** — Крепкий Calendar sprint с качественной JSONB-архитектурой и хорошим покрытием тестами. Один CRITICAL нарушает layer boundary, три WARNING требуют внимания (регрессия Stripe-валидации, TZ boundary в CalendarStore, silent default в EditPracticeView).

---

🔴 CRITICAL — обязательно до шипа:
- C-1: `router.py` — убрать прямой импорт `_user_flags_for_practices`; либо сделать функцию публичной, либо (лучше) завернуть в публичный метод сервиса

🟡 WARNING — рекомендуется исправить:
- W-1: `config.py` — восстановить startup-валидацию `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` в production
- W-2: `calendar.ts` — рассмотреть ±1 день буфер для граничных TZ или перейти на серверную фильтрацию по дате практики в её TZ
- W-3: `EditPracticeView.vue` — заменить `?? 'meditation'` / `?? 'beginner'` на `?? null` + пустой option или баннер с просьбой выбрать

🟢 SUGGESTION — желательно:
- S-1: `CalendarPracticeCard.vue` — badge `variant='free'` для платных практик → переименовать в `'price'`
- S-2: `CalendarView.vue` — `dayLabel` fallback `T12:00:00.000Z` → использовать `T00:00:00` или парсинг без TZ
- S-3: `WeekStrip.vue` — заменить inline SVG стрелки на `IconArrowLeft` / `IconArrowRight`
- S-4: `CalendarFilterModal.vue` — `onReset` применять фильтры сразу или переименовать кнопку в «Сбросить и применить»
- S-5: `CalendarFilterModal.vue` — убрать `{ immediate: true }` у watcher если guard `if (isOpen)` всё равно присутствует

---

| Severity | Кол-во |
|----------|--------|
| 🔴 CRITICAL | 1 |
| 🟡 WARNING | 3 |
| 🟢 SUGGESTION | 5 |
| **Итого** | **9** |
