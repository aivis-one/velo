# Повторная проверка — фиксы к аудиту Calendar iteration (5dfeed1)

**Дата:** 2026-05-22  
**Коммит:** `5dfeed1` feat(calendar): practice taxonomy, week feed with filters & booking flags  
**База:** `cec4b5b`  
**Файлов изменено:** 3 (`router.py`, `service.py`, `calendar.ts`)

---

## Проверка по пунктам

### ✅ C-1 — Роутер импортировал приватную `_user_flags_for_practices`

`backend/app/modules/practices/service.py` + `router.py`

В `service.py` добавлена публичная функция `get_practice_detail()`:

```python
async def get_practice_detail(
    practice_id: UUID,
    user: User,
    session: AsyncSession,
) -> PracticeResponse:
    practice, master_name, master_methods = await get_practice(
        practice_id, user, session,
    )
    flags = await _user_flags_for_practices(user.id, [practice.id], session)
    is_booked, is_paid = flags.get(practice.id, (False, False))
    return practice_to_response(practice, master_name, master_methods,
                                is_booked=is_booked, is_paid=is_paid)
```

Роутер теперь импортирует только `get_practice_detail`, а `_user_flags_for_practices` и `practice_to_response` остаются деталью сервиса. Вариант B из рекомендации реализован точно. Layer boundary восстановлен.

**Статус: устранено.**

---

### ✅ W-2 — Граница недели в локальном TZ, фильтрация на сервере в UTC

`frontend/src/stores/calendar.ts`

Добавлен буфер ±1 день на обе границы:

```typescript
const from = new Date(week[0]!)
from.setHours(0, 0, 0, 0)
from.setDate(from.getDate() - 1)   // -1 день
const to = new Date(week[6]!)
to.setHours(23, 59, 59, 999)
to.setDate(to.getDate() + 1)       // +1 день
```

Комментарий в коде явно объясняет причину: практики вблизи полуночи в экстремальных TZ могли выпасть из UTC-окна. `calendarDateInTz` по-прежнему группирует по TZ практики — лишние дни не протекают в неправильную неделю.

**Статус: устранено.**

---

### ➖ W-1 — Удалена startup-валидация Stripe-ключей

`backend/app/core/config.py` — не исправлено. Принято решение добавить в техдолг; для текущего этапа (pre-production) не блокирует.

**Статус: принято, в техдолге.**

---

### ➖ W-3 — `EditPracticeView.vue`: silent default `'meditation'/'beginner'`

`frontend/src/views/master/EditPracticeView.vue` — не исправлено в этом коммите.

**Статус: не устранено, остаётся открытым.**

---

### ➖ S-1..S-5 — Предложения

Ни одно из 5 предложений не реализовано — `CalendarPracticeCard.vue`, `CalendarView.vue`, `WeekStrip.vue`, `CalendarFilterModal.vue` в diff не затронуты.

**Статус: не устранено, риск низкий.**

---

## Итог повторной проверки

| Замечание | Статус |
|-----------|--------|
| C-1 — Layer boundary (`_user_flags_for_practices` в роутере) | ✅ Устранено |
| W-1 — Stripe startup validation | ➖ Принято в техдолг |
| W-2 — CalendarStore TZ boundary edge case | ✅ Устранено |
| W-3 — EditPracticeView silent taxonomy default | ❌ Остаётся открытым |
| S-1 — Badge variant='free' для платных практик | ❌ Остаётся открытым |
| S-2 — dayLabel T12:00:00.000Z | ❌ Остаётся открытым |
| S-3 — WeekStrip inline SVG вместо icon-системы | ❌ Остаётся открытым |
| S-4 — CalendarFilterModal onReset без auto-apply | ❌ Остаётся открытым |
| S-5 — watch immediate + if guard | ❌ Остаётся открытым |

Новых критических или предупредительных замечаний не выявлено. Фиксы C-1 и W-2 выполнены корректно и согласованно с рекомендациями аудита.
