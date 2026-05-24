# Аудит — экран подтверждения бронирования + публичный профиль мастера (ef7b703..3a8b698)

**Язык / Стек:** Vue 3.5 · TypeScript · Pinia · Vue Router · Python 3.12 · FastAPI  
**Дата:** 2026-05-24  
**Диапазон коммитов:** `ef7b703..3a8b698`  
**Файлов проверено:** 23

---

## Раздел 1 — Общий обзор

Итерация объединяет два экрана пользовательского потока (frame 4 и frame 5) с точечными улучшениями бэкенда. Добавлен экран успешного бронирования (`BookingConfirmedView.vue`), публичный профиль мастера (`MasterPublicView.vue`), навигация между ними, CSS-токены рейтинговых иконок, рефакторинг компонентов `MasterCard` и `PracticeHeroCard`, а также устранение расхождений, зафиксированных в предыдущем аудите.

**Что добавлено / изменено:**

- **Backend (config/main):** флаг `notification_processor_enabled` гейтирует запуск фонового обработчика уведомлений; в тестах выключается во избежание гонки с `FOR UPDATE SKIP LOCKED`.
- **Backend (masters/service):** добавлены два комментария — о нецелесообразности `asyncio.gather` (AsyncSession non-reentrant) и о намеренном включении отзывов на удалённые практики в `reviews_count`. Прямой ответ на S-1 и S-2 предыдущего аудита.
- **Backend (masters/schemas):** мелкое: отсутствует trailing newline.
- **Frontend (новые вью):** `BookingConfirmedView.vue` (255 строк), `MasterPublicView.vue` (324 строки).
- **Frontend (компоненты):** `MasterCard` получил реальную навигацию и `VAvatar` вместо иконки-заглушки; `PracticeHeroCard` — пропы `direction`/`difficultyDots`/`difficultyLabel` и иконку направления; `FeedbackView` — векторные иконки рейтинга вместо emoji.
- **Frontend (утилиты/стили):** `displayHelpers.ts` — `DIRECTION_ICON` (Partial), `DIRECTION_ICON_FALLBACK`, `RATING_ICON_COLOR`; `variables.css` — токены `--velo-rating-*`; `router/index.ts` — два новых маршрута; `api/masters.ts` — `getPublicMaster`; `api/types.ts` — реэкспорт `MasterPublicResponse`.

Архитектурное качество высокое. Критических ошибок и предупреждений не выявлено. Выявлено 3 SUGGESTION.

**Оценка: 9/10**

---

## Раздел 2 — Критические баги и логические ошибки

Не выявлено.

Поток покупки (`onPurchased → router.push → BookingConfirmedView.onMounted`) логически корректен: данные загружаются по актуальному `practiceId` в новом вью. Навигационный guard для `user-booking-confirmed` и `user-master-public` зарегистрирован корректно. `MasterPublicView` обрабатывает ошибку загрузки ближайших практик в отдельном `try/catch`, не прерывая рендеринг профиля — профиль видим даже при частичном сбое.

---

## Раздел 3 — Обработка ошибок

Не выявлено.

`MasterPublicView` применяет двухуровневую стратегию: основной `try/catch` (загрузка профиля) является fatal — при сбое показывается состояние ошибки; вторичный `try/catch` (загрузка предстоящих практик) non-fatal — профиль рендерится без секции практик. Разделение уровней критичности реализовано правильно. `BookingConfirmedView.onMounted` вызывает `store.fetchPractice(id)` — store содержит централизованную обработку ошибок, повторная обработка во вью не требуется. `MasterCard.onMore()` содержит defensive guard: при отсутствии `masterId` — fallback на toast вместо навигации с `undefined` в параметрах маршрута.

---

## Раздел 4 — Безопасность

Не выявлено.

`getPublicMaster(userId)` вызывает backend-endpoint `/masters/{userId}`, который возвращает только `MasterPublicResponse` — финансовые и контактные поля исключены на уровне схемы. Фронтенд не обращается к `/masters/me` или к приватным endpoint'ам из публичного вью. Заглушки (`TD-ASK-MASTER`, `toast.info('Вопросы мастеру -- скоро')`) не раскрывают никаких данных и явно помечены как временные. UUID в параметрах маршрута (`masterId`, `practiceId`) валидируются бэкендом с возвратом 422 при невалидном формате.

---

## Раздел 5 — Производительность

### 🟢 SUGGESTION-1 — Двойной `fetchPractice` в потоке покупки

`frontend/src/views/user/PracticeDetailView.vue` · `onPurchased` + `frontend/src/views/user/BookingConfirmedView.vue` · `onMounted`

```typescript
// PracticeDetailView.onPurchased — текущий код:
function onPurchased(): void {
  showBookingPopup.value = false
  justPurchased.value = true
  const id = route.params.id as string
  store.fetchPractice(id)          // ← fetch #1 (немедленно)
  bookingsStore.refreshBookings()
  router.push({ name: 'user-booking-confirmed', params: { practiceId: id } })
}

// BookingConfirmedView.onMounted:
onMounted(() => {
  const id = route.params.practiceId as string
  store.fetchPractice(id)          // ← fetch #2 (при монтировании нового вью)
})
```

После вызова `router.push()` `PracticeDetailView` размонтируется, а первый `fetchPractice` обновляет store для вью, которое уже неактивно. `BookingConfirmedView.onMounted` запускает второй запрос — он и является авторитетным. Два сетевых запроса подряд к `GET /practices/{id}`.

```typescript
// ✅ ВАРИАНТ — убрать fetchPractice из onPurchased; он нужен только при возврате на detail:
function onPurchased(): void {
  showBookingPopup.value = false
  const id = route.params.id as string
  bookingsStore.refreshBookings()
  router.push({ name: 'user-booking-confirmed', params: { practiceId: id } })
  // BookingConfirmedView.onMounted загрузит свежие данные самостоятельно.
  // При возврате назад (router.back()) PracticeDetailView перезагрузит
  // практику через onActivated/fetchPractice — либо добавить onActivated.
}
```

Риск: только лишний сетевой запрос, данные корректны. Низкий.

---

## Раздел 6 — Регрессия конфига

Не выявлено.

Флаг `notification_processor_enabled: bool = True` добавлен с безопасным default `True` — поведение в production не изменяется. Выключение в `conftest.py` происходит на уровне session-scoped фикстуры `setup_infrastructure` до запуска ASGI lifespan, что гарантирует отсутствие гонки в тестовой среде. Два новых маршрута (`user-master-public`, `user-booking-confirmed`) добавлены без изменения существующих маршрутов. CSS-токены `--velo-rating-*` в `variables.css` не перекрывают существующие переменные.

---

## Раздел 7 — Граничные случаи и логика

### 🟢 SUGGESTION-2 — Статичный текст «Ссылка на Zoom придёт за 10 минут до начала»

`frontend/src/views/user/BookingConfirmedView.vue`

```html
<p class="booking-confirmed__text">
  Вы записаны на {{ practice.title }}. Ссылка на Zoom придёт
  за 10 минут до начала.
</p>
```

Текст упоминает Zoom независимо от типа практики. Если в будущем появятся практики in-person, по Telegram или через другую платформу — формулировка будет вводить в заблуждение. Сейчас все практики предполагают Zoom, поэтому не блокирует.

```typescript
// ✅ Вариант — условный текст или generic формулировка:
// "Детали подключения придут за 10 минут до начала."
// Или: показывать Zoom-строку только если practice.zoom_link !== null
```

Риск: только UX, не функциональный. Актуален до появления не-Zoom практик.

---

## Раздел 8 — Качество кода (UX и семантика)

Не выявлено.

`DIRECTION_ICON` объявлен как `Partial<Record<PracticeDirection, Component>>` с явным комментарием о причине: новые значения `direction` из бэкенда не сломают сборку vue-tsc, пока соответствующая иконка не добавлена во фронтенде. `DIRECTION_ICON_FALLBACK` обеспечивает визуальный fallback. `RATING_ICON` оставлен локально в `FeedbackView.vue` с комментарием, а не вынесен в `displayHelpers` — корректная архитектурная граница: утилитарный модуль не должен импортировать `.vue`-компоненты. Difficulty dots перенесены из `PracticeDetailView` в `PracticeHeroCard` — компонент теперь сам владеет своим визуальным представлением, рефакторинг уменьшает связанность. Контекстный заголовок `booked ? 'Моя практика' : 'Практика'` в `PracticeDetailView` повышает ясность UI без усложнения логики.

---

## Раздел 9 — Тестируемость

Не выявлено.

Флаг `notification_processor_enabled` решает конкретную проблему тестируемости: фоновый `FOR UPDATE SKIP LOCKED` ранее конкурировал с ручными вызовами `_stage_resolve`/`_stage_deliver` в тестах. Отключение флага в session-scoped фикстуре `setup_infrastructure` — прагматичное и корректное решение для последовательного запуска тестов. Новые вью (`BookingConfirmedView`, `MasterPublicView`) используют store-паттерн, что упрощает юнит-тестирование через mock store. Заглушки явно помечены комментариями (`TD-ASK-MASTER`), что позволяет легко найти их при написании тестов в V2.

---

## Раздел 10 — AI-паттерны

Ни один из 20 паттернов не выявлен.

- Нет фантомных функций: `getPublicMaster` зарегистрирована в `api/masters.ts` и вызывается в `MasterPublicView`; маршруты `user-master-public` и `user-booking-confirmed` подключены в `router/index.ts`.
- Нет дублирования логики: `store.fetchPractice` вызывается централизованно, store управляет состоянием загрузки.
- `DIRECTION_ICON[direction] || DIRECTION_ICON_FALLBACK` — защитный паттерн, не магическое значение.
- Комментарии в `masters/service.py` документируют причины архитектурных решений (`asyncio.gather`, `reviews_count`), а не описывают очевидное.

---

## Раздел 11 — Кросс-модульная согласованность

### Согласованности соблюдены

| Компонент | Паттерн | Статус |
|-----------|---------|--------|
| `MasterCard.onMore()` | defensive guard при отсутствии `masterId` | Соблюдён |
| `MasterPublicView` | двухуровневая обработка ошибок (fatal/non-fatal) | Соблюдён |
| `DIRECTION_ICON` | `Partial<Record<...>>` с fallback | Соблюдён |
| `router/index.ts` | именованные маршруты, `params` через объект | Соблюдён |
| `api/masters.ts` | стиль API-функций соответствует `api/practices.ts` | Соблюдён |
| `notification_processor_enabled` | default `True`, безопасный для production | Соблюдён |
| CSS-токены | именование `--velo-rating-*` соответствует паттерну `--velo-*` | Соблюдён |

### 🟢 SUGGESTION-3 — Отсутствует trailing newline в `masters/schemas.py`

`backend/app/modules/masters/schemas.py`

```python
# ❌ ТЕКУЩИЙ КОД (конец файла):
    practices_count: int
    reviews_count: int   # ← нет \n
```

```python
# ✅ ИСПРАВЛЕНИЕ:
    practices_count: int
    reviews_count: int
    # ← пустая строка / \n
```

Большинство линтеров (ruff, flake8 W292, git diff) флагируют отсутствие trailing newline. Автоисправление: настройка редактора или `echo "" >> schemas.py`. Несогласованность с остальными файлами проекта, где trailing newline присутствует.

---

## Раздел 12 — Миграции

Не выявлено.

Изменений в схеме БД нет. Новые вью и компоненты работают с существующими endpoint'ами и моделями. Флаг `notification_processor_enabled` — runtime-конфиг, не миграция. Реэкспорт `MasterPublicResponse` в `api/types.ts` не требует изменений в ORM-моделях.

---

## Раздел 13 — Изолированные файлы

Не выявлено.

Все новые файлы и функции подключены и достижимы:
- `BookingConfirmedView.vue` зарегистрирована в `router/index.ts` под маршрутом `user-booking-confirmed`; вызывается из `PracticeDetailView.onPurchased`
- `MasterPublicView.vue` зарегистрирована под маршрутом `user-master-public`; вызывается из `MasterCard.onMore()`
- `getPublicMaster` в `api/masters.ts` вызывается в `MasterPublicView`
- `DIRECTION_ICON`, `DIRECTION_ICON_FALLBACK`, `RATING_ICON_COLOR` в `displayHelpers.ts` импортируются в `PracticeHeroCard.vue` и `FeedbackView.vue`
- CSS-токены `--velo-rating-*` используются в компонентах через `variables.css`
- `notification_processor_enabled` читается в `main.py` при запуске ASGI lifespan

Изолированных источников нет.

---

## Итоговая оценка

**9/10** — Качественная итерация, закрывающая два экрана пользовательского потока. Ответы на S-1 и S-2 предыдущего аудита задокументированы в коде. Рефакторинг difficulty dots и переход на `VAvatar` в `MasterCard` улучшают инкапсуляцию компонентов. Двухуровневая обработка ошибок в `MasterPublicView` (fatal/non-fatal) — правильный паттерн для составных страниц. Три SUGGESTION носят профилактический характер: устранение лишнего сетевого запроса, подготовка к не-Zoom практикам, trailing newline.

---

🔴 CRITICAL — обязательно до шипа:
- нет

🟡 WARNING — рекомендуется исправить:
- нет

🟢 SUGGESTION — желательно:
- S-1: `PracticeDetailView.onPurchased` — убрать первый `store.fetchPractice(id)`, так как `BookingConfirmedView.onMounted` выполняет авторитетный запрос; при необходимости добавить `onActivated` для корректного рефреша при возврате назад
- S-2: `BookingConfirmedView.vue` — заменить статичный текст «Ссылка на Zoom» на универсальную формулировку или условный рендеринг по наличию `zoom_link`
- S-3: `masters/schemas.py` — добавить trailing newline в конец файла

---

| Severity | Кол-во |
|----------|--------|
| 🔴 CRITICAL | 0 |
| 🟡 WARNING | 0 |
| 🟢 SUGGESTION | 3 |
| **Итого** | **3** |
