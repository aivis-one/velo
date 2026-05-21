# Повторная проверка — фиксы к аудиту экранов 14–18 (ce2d914)

**Дата:** 2026-05-20  
**Коммит:** `ce2d914` fix(audit): W-1 cancel toast, S-1 TZ-aware dates, S-2/S-3 comments feat(live): dashboard nearest live -> practice-live, "В эфире" badge on bookings  
**База:** `a43791b`  
**Файлов изменено:** 7

---

## Проверка по пунктам

### ✅ W-1 — Молчащая ошибка отмены на экране 15

`frontend/src/views/user/PracticeDetailView.vue`

Добавлены `import useToast`, инициализация `toast`, и в `onCancelBooking`:
```typescript
// при ошибке
toast.error(result.error)
// при успехе
toast.success('Бронирование отменено')
```
Поведение теперь идентично экрану 18. Ошибочный комментарий убран, заменён точным.

**Статус: устранено.**

---

### ✅ S-1 — TZ-aware даты для бейджей «Сегодня» / «Завтра»

`frontend/src/views/user/MyBookingsView.vue`

Реализован `calendarDate(d, timezone)` через `Intl.DateTimeFormat('en-CA', { timeZone })` — тот же паттерн, что в `utils/format.ts`. `isToday(iso, tz)` и `isTomorrow(iso, tz)` теперь принимают часовой пояс практики и сравнивают в нём.

Попутно добавлена логика «В эфире» (`isLive` по `practice.status === 'live'`), которая занимает 0-й ранг в сортировке (выше «Сегодня»). Для работы `practice.status` добавлен в `PracticeSummary` на бэкенде (`schemas.py`), `generated.ts` регенерирован.

**Статус: устранено. Плюс — живые практики всплывают наверх списка.**

---

### ✅ S-2 — Комментарий к title-эвристике в `BookingCard`

`frontend/src/components/shared/BookingCard.vue`

Уточнён комментарий: объясняет, что `breathwork` не входит в `PracticeType` enum (`live | series | one_on_one | replay`), поэтому эвристика по заголовку — намеренный обходной путь, а не ошибка.

**Статус: устранено.**

---

### ✅ S-3 — Стале TODO в `CheckinView`

`frontend/src/views/user/CheckinView.vue`

Две строки удалены:
```
// TODO(screen 14): route 'practice-live' is created in the next step.
// Until then this navigation will warn in console -- expected.
```
Заменены нейтральным комментарием «Navigate to the live practice screen (route exists, see router/index.ts)».

**Статус: устранено.**

---

### ➖ S-4 — `MasterCard` «Подробнее» без disabled-состояния

Не исправлено — принято решение оставить как есть (UI заглушка до спринта профиля мастера). Риск низкий.

**Статус: принято, не исправляется.**

---

## Попутные улучшения (не из списка замечаний)

### «В эфире» на дашборде и бронированиях

`UserDashboardView.vue` + `BookingCard.vue`

- `nearestIsLive` computed: если ближайшая практика `status === 'live'` — показывает бейдж «В эфире» вместо «Оплачено».
- `openNearest()`: клик на карточку ближайшей практики теперь ведёт на `practice-live` вместо `practice-detail`, если практика идёт.
- `BookingCard` получил вариант бейджа `'live'` с зелёным dot (аналогично `PracticeLiveView`).

Изменения согласованы с существующей архитектурой: `practice.status` теперь в `PracticeSummary`, никаких лишних сетевых запросов.

---

## Итог повторной проверки

| Замечание | Статус |
|-----------|--------|
| W-1 — Молчащий toast при отмене (экран 15) | ✅ Устранено |
| S-1 — TZ-aware isToday/isTomorrow | ✅ Устранено |
| S-2 — Комментарий к title-эвристике | ✅ Устранено |
| S-3 — Стале TODO в CheckinView | ✅ Устранено |
| S-4 — MasterCard disabled-state | ➖ Принято |

Новых критических или предупредительных замечаний не выявлено. Попутные улучшения («В эфире» badge и smart-навигация с дашборда) выполнены качественно и согласованно.
