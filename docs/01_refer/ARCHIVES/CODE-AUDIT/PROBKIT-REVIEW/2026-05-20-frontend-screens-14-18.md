# Аудит фронтенда — экраны 14–18 (коммиты 0023676..a43791b)

**Язык / Стек:** Vue 3.5 · TypeScript · Pinia · Vue Router · Telegram Mini App WebApp API  
**Дата:** 2026-05-20  
**Диапазон коммитов:** `0023676..a43791b`  
**Файлов проверено:** 18

---

## Раздел 1 — Общий обзор

Крупный sprint: добавлены экраны 14–18 пользовательского потока и инфраструктура под них.

**Что добавлено:**
- **AiSummaryView** (экран 16) — честная заглушка «раздел в разработке»; маршрут `user-ai-summary` подключён, dashboard «Подробнее» теперь кликабелен.
- **MyBookingsView** (экран 17) — разбивка на «Предстоящие» / «Прошедшие» без вкладок, сортировка по дате, бейджи «Сегодня» / «Завтра» / «Завершена».
- **BookingDetailView** (экран 18) — полная карточка бронирования с отменой через попап.
- **PracticeLiveView** (экран 14) — Войти (join + Zoom) / Check-in / Покинуть; валидация Zoom URL (только `https://`).
- **CheckinView** обновлён: кнопка «Назад» теперь `router.back()` (устранена петля 12↔15).
- **Shared компоненты:** `PracticeHeroCard`, `MasterCard` — извлечены из PracticeDetailView, переиспользуются на экранах 15, 18.
- **BookingCard** — dumb-компонент для экрана 17; бейдж передаётся снаружи.
- **Platform abstraction** — `types.ts`, `telegram.ts`, `standalone.ts`: добавлен `getStartParam()` для deep link.
- **Bookings store** — `fetchBooking`, `joinBooking`, `leaveBooking`, `selectedBooking`.
- **Router** — маршруты `booking-detail`, `practice-live`, `user-ai-summary`.

Архитектурная чистота хорошая: dumb/smart разделение соблюдено, ошибки возвращаются через `{ ok, error }` паттерн, Zoom URL валидируется. Одна WARNING-находка (молчаливая ошибка при отмене на экране 15) и четыре предложения.

**Оценка: 8/10**

---

## Раздел 2 — Критические баги и логические ошибки

Не выявлены.

---

## Раздел 3 — Обработка ошибок

### 🟡 WARNING-1 — Ошибка отмены бронирования молчит на экране 15

`frontend/src/views/user/PracticeDetailView.vue:onCancelBooking`

```typescript
// ❌ ТЕКУЩИЙ КОД
async function onCancelBooking(): Promise<void> {
  if (!myBooking.value || cancelling.value) return
  cancelling.value = true
  const result = await bookingsStore.cancelBooking(myBooking.value.id)
  cancelling.value = false
  if (!result.ok) {
    // Toast is shown by the store on error; no local handling needed.  ← НЕВЕРНО
    return
  }
  justPurchased.value = false
}
```

Комментарий ошибочен: `bookingsStore.cancelBooking` только возвращает `{ ok: false, error }` — тост не показывает. API может вернуть 409 / 400 / 500, пользователь кликает «Отменить», ничего не происходит, причина неизвестна.

Для сравнения: `BookingDetailView.onConfirmCancel` корректно вызывает `toast.error(result.error)`.

```typescript
// ✅ ИСПРАВЛЕНИЕ
async function onCancelBooking(): Promise<void> {
  if (!myBooking.value || cancelling.value) return
  cancelling.value = true
  const result = await bookingsStore.cancelBooking(myBooking.value.id)
  cancelling.value = false
  if (!result.ok) {
    toast.error(result.error)
    return
  }
  toast.success('Бронирование отменено')
  justPurchased.value = false
}
```

**Объяснение:** единственное исправление унифицирует поведение экранов 15 и 18. Нужно также добавить import `useToast` — он уже используется в файле, просто не вызван в этой ветке.

---

## Раздел 4 — Безопасность

Не выявлены.

`PracticeLiveView.hasValidZoom` проверяет `startsWith('https://')` перед открытием ссылки — корректно закрывает AUDIT-0520-02.

---

## Раздел 5 — Производительность

Не выявлены.

`fetchMyBookings` в store пропускает сетевой запрос если список уже загружен (`if (pagination.items.value.length > 0) return`) — правильно, повторные переходы не делают лишних запросов.

---

## Раздел 6 — Качество кода

Не выявлены.

---

## Раздел 7 — Тестируемость

Для новых вьюх и компонентов тестов нет (соответствует сложившейся практике проекта: протестированы только `usePagination` и `format.ts`). При масштабировании стоит добавить тесты хотя бы для:
- `MyBookingsView` — логика `isToday / isTomorrow / badgeFor`
- `bookingsStore.cancelBooking` — путь `ok: false`

---

## Раздел 8 — Рефакторинг

Не выявлены.

`PracticeHeroCard` и `MasterCard` удачно выделены из `PracticeDetailView` и переиспользуются на экранах 15 и 18 — хороший рефакторинг.

---

## Раздел 9 — Мелкие улучшения и polish

### 🟢 SUGGESTION-1 — `isToday`/`isTomorrow` использует локальное время браузера, а не часовой пояс практики

`frontend/src/views/user/MyBookingsView.vue:isToday, isTomorrow`

```typescript
// Текущий код — использует компоненты даты в локальном TZ браузера
function isToday(iso: string): boolean {
  const d = new Date(iso)   // UTC timestamp → local date
  const now = new Date()
  return d.getDate() === now.getDate() && ...
}
```

У пользователя в Новосибирске (UTC+7) практика `"2026-05-20T18:00Z"` = 21 мая 01:00 по местному времени, а `formatDate` выводит `"21 мая"`. Бейдж `isToday` при этом сравнивает `new Date(iso)` в локальном TZ — для UTC+7 это также 21 мая, совпадает. Однако если практика хранит `timezone = "Europe/Berlin"` (UTC+2), а пользователь в UTC+7, отображаемая дата и бейдж могут разойтись на граничных значениях.

Правильная проверка — сравнивать «сегодня в часовом поясе практики»:

```typescript
function isSameDay(iso: string, tz: string, offsetDays = 0): boolean {
  const target = new Date(iso)
  const now = new Date(Date.now() + offsetDays * 86_400_000)
  const fmt = (d: Date) =>
    d.toLocaleDateString('en-CA', { timeZone: tz })   // 'YYYY-MM-DD'
  return fmt(target) === fmt(now)
}
```

`badgeFor` при этом получает `b.practice.timezone` из `PracticeSummary`.

Риск: низкий для российских пользователей (одна TZ), но корректнее для будущего расширения.

---

### 🟢 SUGGESTION-2 — `BookingCard.typeIcon` определяется по вхождению слова в название

`frontend/src/components/shared/BookingCard.vue:typeIcon`

```typescript
// ❌ Текущий — title heuristic
const typeIcon = computed(() =>
  props.booking.practice.title.toLowerCase().includes('breathwork')
    ? IconBreathwork
    : IconMeditation,
)
```

`PracticeSummary.practice_type: PracticeType` существует (`'live' | 'series' | 'one_on_one' | 'replay'`). Но типа `'breathwork'` в enum нет — поэтому хористика по заголовку сейчас неизбежна. Тем не менее, когда `breathwork` добавят в `PracticeType`, стоит переключить на прямое сравнение типа. Сейчас это технический долг.

Для документирования намерения:

```typescript
// TODO: когда breathwork появится в PracticeType, использовать practice_type напрямую
const typeIcon = computed(() =>
  props.booking.practice.title.toLowerCase().includes('breathwork')
    ? IconBreathwork
    : IconMeditation,
)
```

Риск: только визуальный (иконка), не блокирует.

---

### 🟢 SUGGESTION-3 — Стале TODO в `CheckinView`

`frontend/src/views/user/CheckinView.vue:goToPracticeLive`

```typescript
// TODO(screen 14): route 'practice-live' is created in the next step.
// Until then this navigation will warn in console -- expected.
function goToPracticeLive(): void {
  router.push({ name: 'practice-live', params: { practiceId } })
}
```

Маршрут `practice-live` создан в этом же коммите (`router/index.ts`). Комментарий устарел, предупреждение в консоли больше не происходит. Строки к удалению.

---

### 🟢 SUGGESTION-4 — `MasterCard` «Подробнее» — кнопка без disabled-состояния

`frontend/src/components/shared/MasterCard.vue:onMore`

Стрелка-кнопка "Профиль мастера" (`cursor: pointer`, hover opacity) всегда вызывает toast «Профиль мастера — скоро». В production пользователь будет многократно нажимать, ожидая навигации.

Вариант до появления маршрута — убрать `cursor: pointer`, снизить opacity до 0.5, убрать hover-transition:

```css
/* Временно */
.master-card__arrow {
  opacity: 0.4;
  cursor: default;
  pointer-events: none;
}
```

После появления маршрута — убрать эти правила, подключить `router.push`.

Риск: UX, не функциональный.

---

## Раздел 10 — AI-паттерны

Ни один из 20 паттернов не выявлен.

- Нет неизвестных зависимостей (только стандартный Vue экосистема).
- Нет устаревших паттернов (Vue 3.5 composition API повсюду, без `Options API`).
- Нет фантомного кода — все экспортированные компоненты и функции импортированы из вью.
- Нет утечки тренировочных данных (нет `example.com`, `test@test.com` вне тестов).
- Нет смешанных парадигм: все файлы — `<script setup>` + Pinia composable.

---

## Раздел 11 — Кросс-модульная согласованность

### ⚠️ Несогласованность: отмена бронирования на экранах 15 и 18

| Экран | Файл | При ошибке | При успехе |
|-------|------|-----------|-----------|
| 15 (PracticeDetail) | `PracticeDetailView.vue` | ❌ Молчит | ❌ Молчит |
| 18 (BookingDetail) | `BookingDetailView.vue` | ✅ `toast.error` | ✅ `toast.success` + `router.back()` |

Одна функция store, два разных UX результата. Это и есть WARNING-1 выше.

### ✅ Согласованности соблюдены

- Паттерн `{ ok, error }` — `cancelBooking`, `joinBooking`, `leaveBooking` в store.
- Форматирование дат — `formatDate(scheduled_at, timezone)` везде (BookingCard, PracticeHeroCard, CheckinView, PracticeDetailView, BookingDetailView).
- Валидация Zoom URL — `hasValidZoom = startsWith('https://')` применена только там, где открывается ссылка (PracticeLiveView).
- `PracticeHeroCard` + `MasterCard` — одни компоненты на экранах 15 и 18.
- `bookingsStore.fetchMyBookings()` — все вьюхи используют один store-метод с cache skip.

---

## Раздел 12 — Тесты

Тестовых файлов для новых вьюх и компонентов не обнаружено. Существующие тесты (`usePagination.test.ts`, `format.test.ts`) не затронуты.

---

## Раздел 13 — Изолированные файлы

Все новые файлы импортированы в router или в другие компоненты. Изолированных источников нет.

---

## Итоговая оценка

**8/10** — Архитектурно грамотный sprint. Одна WARNING (молчащая ошибка UX) и четыре предложения, не блокирующих мёрж.

---

🔴 CRITICAL — обязательно до шипа:
- нет

🟡 WARNING — рекомендуется исправить:
- W-1: `PracticeDetailView.onCancelBooking` — добавить `toast.error(result.error)` при `result.ok === false`, и `toast.success` при успехе

🟢 SUGGESTION — желательно:
- S-1: `isToday`/`isTomorrow` — учитывать `practice.timezone` при сравнении дат
- S-2: `BookingCard.typeIcon` — задокументировать намерение, когда `breathwork` появится в `PracticeType`
- S-3: `CheckinView` — удалить устаревший TODO про `practice-live` (маршрут уже создан)
- S-4: `MasterCard` — добавить `pointer-events: none` / `opacity: 0.4` до появления реального маршрута профиля мастера

---

| Severity | Кол-во |
|----------|--------|
| 🔴 CRITICAL | 0 |
| 🟡 WARNING | 1 |
| 🟢 SUGGESTION | 4 |
| **Итого** | **5** |
