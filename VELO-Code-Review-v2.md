# VELO — Комплексный Code Review (v2)

**Дата:** 2026-03-08
**Ревьюер:** Senior Software Engineer (Claude Code)
**Стек:** Python 3.12 / FastAPI / SQLAlchemy async / PostgreSQL / Redis / Vue 3 / TypeScript / Pinia
**Охват:** Полный codebase включая Phase F9 (diary, check-in, feedback, analytics)

---

## 1. Общий обзор

**Оценка: 7.8 / 10** (↑ от 7.5 — за рефакторинг displayHelpers, устранение code duplication, исправление CRITICAL-1)

Проект демонстрирует зрелый архитектурный подход: модульная структура бэкенда, выделенные паттерны
(P-01 no-commit-in-service, P-07 FOR UPDATE, P-08 404-not-403), двойная бухгалтерия для финансов,
HMAC-валидация Telegram initData. Бэкенд покрыт тестами (33 файла). В Phase F9 проведён заметный
рефакторинг фронтенда: `displayHelpers.ts` как single source of truth для emoji/label маппингов,
устранение code duplication из W-2/S-3.

**Что улучшилось с прошлого ревью:**
- ✅ CRITICAL-1 ИСПРАВЛЕН: `roleRedirect` теперь `async` с `await waitUntilReady()`, global `beforeEach` guard обеспечивает auth readiness
- ✅ W-2/S-3 code duplication ИСПРАВЛЕН: emoji/label маппинги в `displayHelpers.ts`
- ✅ DiaryStore хорошо структурирован с `usePagination` composable

**Остаётся:**
- API-клиент без retry, timeout, отмены запросов
- CSS дублируется между CheckinView и FeedbackView (~200 строк)
- Фронтенд — только 2 тест-файла
- Нет единого механизма обработки ошибок — каждый store свой try/catch
- Константы `CHECKIN_WINDOW_H` / `FEEDBACK_WINDOW_H` дублируются между views
- DiaryView — монолит на 1000 строк

---

## 2. Критические проблемы и баги

### ✅ CRITICAL-1: Race condition в roleGuard — ИСПРАВЛЕНО

`roleRedirect` теперь async с `await waitUntilReady()` (guards.ts:37-39).
Global `beforeEach` вызывает `waitUntilReady()` при первой навигации.

---

### 🔴 CRITICAL-2: Нет таймаута запросов в API-клиенте

**Файл:** `frontend/src/api/client.ts`
**Статус:** ОТКРЫТО

`fetch()` без `AbortController` и timeout. При сетевых проблемах запрос висит бесконечно.
В мобильной Telegram WebApp потеря сети — обычное дело.

```ts
// ✅ Исправление:
const controller = new AbortController()
const timeoutId = setTimeout(() => controller.abort(), 15_000)
try {
  response = await fetch(`${BASE_URL}${path}`, {
    method, headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal: controller.signal,
  })
} catch (e) {
  if (e instanceof DOMException && e.name === 'AbortError') {
    throw new ApiTimeoutError()
  }
  throw new ApiNetworkError()
} finally {
  clearTimeout(timeoutId)
}
```

---

### 🔴 CRITICAL-3: `record_master_ledger` при отсутствии профиля

**Файл:** `backend/app/modules/payments/service.py`
**Статус:** ОТКРЫТО

Когда `MasterProfile` не найден, функция создаёт ledger entry но НЕ обновляет cached balance → расхождение.

```python
# ✅ Исправление:
if profile is None:
    raise BadRequestError("Cannot record ledger: master profile not found")
```

---

### 🔴 CRITICAL-4: Нет rate limiting на `/auth/telegram`

**Файл:** `backend/app/modules/auth/router.py`
**Статус:** ОТКРЫТО

Endpoint без rate limiting. При replay valid initData в 5-минутном окне — возможно создание
тысяч Redis-сессий.

---

## 3. Новые проблемы (Phase F9)

### 🟡 NEW-1: Дублирование констант `CHECKIN_WINDOW_H` / `FEEDBACK_WINDOW_H`

**Файлы:** `UserDashboardView.vue:123-124`, `PracticeDetailView.vue:192-193`

```ts
// Одинаковые магические числа в двух файлах:
const CHECKIN_WINDOW_H  = 3
const FEEDBACK_WINDOW_H = 72

// ✅ Вынести в utils/constants.ts:
export const CHECKIN_WINDOW_H = 3
export const FEEDBACK_WINDOW_H = 72
```

---

### 🟡 NEW-2: `formatShortDate` переопределена в DiaryView несовместимо

**Файл:** `frontend/src/views/user/DiaryView.vue:624-626`

```ts
// DiaryView (month: 'long') → "22 января"
function formatShortDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
}
// displayHelpers.ts (month: 'short') → "22 янв"
```

Одноимённые функции с разным поведением. **Исправление:** переименовать в DiaryView в `formatLongDate`.

---

### 🟡 NEW-3: DiaryView — монолит ~1000 строк

**Файл:** `frontend/src/views/user/DiaryView.vue` (1001 строка)

6 internal states через ручной state machine (`list`, `detail-checkin`, `detail-feedback`,
`detail-entry`, `new`, `edit`). Нельзя тестировать sub-view изолированно.

**Рекомендация:** Выделить `DiaryList.vue`, `DiaryEntryForm.vue`, `DiaryDetailView.vue`.

---

### 🟡 NEW-4: `onMounted` в DiaryView не обрабатывает ошибки Promise.all

**Файл:** `frontend/src/views/user/DiaryView.vue:649-656`

```ts
// ❌ Ошибки уходят в unhandled rejection:
onMounted(() => {
  Promise.all([
    diaryStore.fetchEntries(),
    diaryStore.fetchCheckins(),
    diaryStore.fetchFeedbacks(),
  ])
})

// ✅ С обработкой:
onMounted(async () => {
  try {
    await Promise.all([...])
  } catch (e) {
    toast.error('Не удалось загрузить дневник')
  }
})
```

---

### 🟡 NEW-5: `background: white` вместо CSS-переменной

**Файлы:** `CheckinView.vue:357`, `FeedbackView.vue:335`, `DiaryView.vue:791`

```css
background: white;                /* ❌ hardcoded */
background: var(--velo-bg-card);  /* ✅ токен */
```

---

### 🟢 NEW-6: insights cache не ограничен

**Файл:** `frontend/src/stores/diary.ts`

`insightsCache = reactive(new Map())` растёт бесконечно.
У мастера с сотнями практик — утечка памяти в рамках сессии.
**Рекомендация:** LRU-ограничение (50-100 записей).

---

## 4. Обработка ошибок

### 🟡 WARNING-1: Непоследовательная обработка ошибок на фронтенде

Каждый store — свой паттерн try/catch. `diary.ts` — 7 дублирующихся блоков.

```ts
// ✅ Единый хелпер (composables/useApiError.ts):
function handleApiError(e: unknown, fallback: string): SubmitResult {
  if (e instanceof ApiResponseError) return { ok: false, error: e.detail }
  if (e instanceof ApiNetworkError) return { ok: false, error: 'Нет подключения' }
  return { ok: false, error: fallback }
}
```

---

### 🟡 WARNING-2: Глобальный 500-обработчик без контекста

**Файл:** `backend/app/main.py`

Нет `request.method`, нет `trace_id` в логах при 500.

---

### 🟡 WARNING-3: `waitUntilReady()` не различает success/timeout

**Файл:** `frontend/src/composables/useAuth.ts`

При таймауте резолвится без ошибки — код считает что auth готов, хотя это не так.

---

## 5. Безопасность

### 🟡 WARNING-4: Telegram initData replay в 5-минутном окне

initData валидна 5 минут. Нет Redis SET с TTL для защиты от повторного использования.
**Исправление:** Redis SET `used_init_data:{hash}` с TTL 5 минут.

---

### 🟡 WARNING-5: Stripe webhook signature не проверяется в stub mode

При `STRIPE_STUB=true` signature verification отключена. Нужен запрет `STRIPE_STUB` в production.

---

### 🟢 SUGGESTION-1: Session token в sessionStorage (XSS-уязвимость)

Рассмотреть httpOnly cookie как альтернативу sessionStorage.

---

### 🟢 SUGGESTION-2: `maxlength` только на клиенте

Проверить Pydantic-схемы: `max_length` на полях комментариев check-in/feedback/diary entries.

---

## 6. Производительность

### 🟡 WARNING-6: N+1 в `finalize_practice`

**Файл:** `backend/app/modules/practices/service.py`

Цикл по bookings с отдельным `session.get(User)` для каждого участника.
**Исправление:** Один `SELECT ... WHERE id IN (...)` вместо N запросов.

---

### 🟡 WARNING-7: `list_public_practices` без составного индекса

**Файл:** `backend/app/modules/practices/models.py`

Фильтр `WHERE status=... AND scheduled_at >= ... ORDER BY scheduled_at` без составного индекса.
**Исправление:** `Index('ix_practices_status_scheduled', 'status', 'scheduled_at')`.

---

### 🟡 WARNING-8: Избыточный fetch practice в checkin/feedback views

**Файлы:** `CheckinView.vue`, `FeedbackView.vue`

```ts
// Пользователь только что был на PracticeDetailView — practice уже в store.
onMounted(() => {
  practicesStore.fetchPractice(practiceId)  // всегда, даже если уже есть
})

// ✅ С проверкой кэша:
if (practicesStore.selected?.id !== practiceId) {
  practicesStore.fetchPractice(practiceId)
}
```

---

### 🟢 SUGGESTION-3: `pool_recycle` не нужен для PostgreSQL

Убрать из конфига — это MySQL-специфичный параметр.

---

## 7. Чистота кода

### 🟡 WARNING-9: CSS дублирование между CheckinView и FeedbackView (~200 строк)

Header, back button, practice info, textarea, actions, success screen — ~200 строк идентичного CSS.
**Решение:** Извлечь `FormShell.vue` с слотами.

---

### ✅ WARNING-10 (W-2/S-3): Дублирование emoji/label маппингов — ИСПРАВЛЕНО

Вынесено в `displayHelpers.ts`.

---

### 🟡 WARNING-10: Magic numbers в стилях

`font-size: 80px`, `font-size: 56px`, `min-width: 90px` без CSS design tokens.

---

### 🟡 WARNING-11: `platform.hapticFeedback` без fallback

Если `platform` не инициализирован или среда не поддерживает haptic — silent crash.

---

## 8. Тестируемость

### 🟡 WARNING-12: Фронтенд практически не покрыт тестами

2 тест-файла (`usePagination.test.ts`, `format.test.ts`). F9 добавила значительный объём
бизнес-логики без тестов.

**Приоритет:**
1. DiaryStore CRUD + pagination
2. Time window logic (`inCheckinWindow` / `inFeedbackWindow`)
3. Alert banners computeds в UserDashboardView
4. Router guards integration

---

### 🟡 WARNING-13: Module-level mutable state затрудняет тестирование

**Файлы:** `api/client.ts` (`_token`, `_onUnauthorized`), `useAuth.ts` (`isReady`, `isStandalone`)

Module-level state не сбрасывается между тестами без явного `resetAuthState()`.

---

### 🟡 WARNING-14: Бэкенд-сервисы зависят от глобальных settings

Сервисы импортируют `settings` напрямую — затрудняет unit-тестирование с другими конфигами.

---

## 9. Рекомендации по рефакторингу

| ID | Описание | Экономия |
|----|----------|---------|
| REFACTOR-1 | Извлечь `FormShell.vue` (CheckinView + FeedbackView) | ~300 строк CSS + ~50 шаблона |
| REFACTOR-2 | Единый `useApiError.ts` composable для stores | Убрать 7+ дублей try/catch |
| REFACTOR-3 | `utils/constants.ts` для `CHECKIN_WINDOW_H` / `FEEDBACK_WINDOW_H` | Убрать 2 дубля |
| REFACTOR-4 | DiaryView decomposition → 4-5 компонентов | Изолируемость, тестируемость |
| REFACTOR-5 | `core/financial.py` с `assert_double_entry()` | Явная проверка инварианта |

---

## 10. Мелкие улучшения

- **POLISH-1:** Back-кнопки `←` заменить на SVG-иконку
- **POLISH-2:** i18n-ready строки (вынести в `@/locales/ru.ts`)
- **POLISH-3:** Redis ping в readiness check
- **POLISH-4:** Убрать `pool_recycle` из PostgreSQL config
- **POLISH-5:** `route.params.id as string` → safe extraction с type guard

---

## 11. Итоговый блок

### 🔴 Исправить немедленно:

| ID | Файл | Описание |
|----|------|----------|
| CRITICAL-2 | `api/client.ts` | AbortController + 15с timeout |
| CRITICAL-3 | `payments/service.py` | Raise при отсутствующем MasterProfile в record_master_ledger |
| CRITICAL-4 | `auth/router.py` | Rate limiting на `/auth/telegram` |

### 🟡 Исправить в ближайших спринтах:

| ID | Файл | Описание |
|----|------|----------|
| NEW-1 | `UserDashboardView`, `PracticeDetailView` | Вынести CHECKIN/FEEDBACK_WINDOW_H в constants.ts |
| NEW-2 | `DiaryView.vue` | Переименовать `formatShortDate` → `formatLongDate` |
| NEW-3 | `DiaryView.vue` | Декомпозиция монолита |
| NEW-4 | `DiaryView.vue` | Обработка ошибок в onMounted Promise.all |
| NEW-5 | `CheckinView`, `FeedbackView`, `DiaryView` | `background: white` → CSS variable |
| WARNING-1 | stores/* | Единый error handler |
| WARNING-2 | `main.py` | 500-обработчик с request context |
| WARNING-3 | `useAuth.ts` | waitUntilReady() с различением timeout vs success |
| WARNING-4 | `auth/router.py` | Anti-replay для initData |
| WARNING-5 | `payments/webhook.py` | Запрет STRIPE_STUB в production |
| WARNING-6 | `practices/service.py` | N+1 в finalize_practice |
| WARNING-8 | `CheckinView`, `FeedbackView` | Кэш practice до fetch |
| WARNING-9 | `CheckinView`, `FeedbackView` | FormShell — CSS deduplication |
| WARNING-12 | `tests/` | Покрыть фронтенд тестами (time window логика, DiaryStore) |

### 🟢 При возможности:

- `ApiNetworkError` отдельно в UI
- httpOnly cookies для токена
- Server-side `max_length` на комментариях
- LRU-ограничение insights cache
- i18n-ready строки, SVG back-иконка, Redis health check

---

## 12. Статус предыдущих находок

| ID | Статус | Комментарий |
|----|--------|-------------|
| CRITICAL-1 | ✅ Исправлено | roleRedirect async + global beforeEach |
| CRITICAL-2 | 🔴 Открыто | API client без timeout |
| CRITICAL-3 | 🔴 Открыто | Orphaned ledger entry |
| CRITICAL-4 | 🔴 Открыто | No rate limiting |
| W-2/S-3 | ✅ Исправлено | displayHelpers.ts |
| WARNING-1..14 | 🟡 Открыто | |

---

**Вердикт:** Оценка 7.8/10. CRITICAL-1 закрыт. Бэкенд — сильная сторона (402 теста, двойная бухгалтерия,
FOR UPDATE). Фронтенд улучшился архитектурно (displayHelpers, usePagination в DiaryStore), но:
нет timeout в API client (CRITICAL-2), 2 тест-файла при растущей бизнес-логике, CSS-дублирование,
DiaryView как монолит 1000 строк.
