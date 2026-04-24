Сейчас у меня есть карты обоих контрактов. Сравню детали по нескольким критическим точкам в коде, прежде чем формировать отчёт.

Найдены расхождения в схеме `UserResponse` между фронтом и бэком. Проверю детальнее.

Достаточно данных собрано. Готовлю отчёт.

# Code Review: Соответствие Фронтенда Бэкенду VELO

**Stack:** Python/FastAPI + TypeScript/Vue 3 + Pinia
**Project type:** Monolith (Telegram WebApp + REST API)
**Stage:** MVP (фазы F1–F9 завершены)
**Criticality:** medium-high (есть денежные операции — топап, выводы, комиссии)
**Mode:** full — сравнение TS-клиента (`frontend/src/api/`) против Pydantic-схем и роутеров (`backend/app/modules/`)

---

## 1. Overview

Бэкенд экспонирует **75 HTTP-эндпоинтов** (FastAPI, префикс `/api/v1`, Bearer-токен из Redis). Фронтенд использует **fetch-обёртку** в `api/client.ts` с типизированными модулями (`api/practices.ts`, `api/bookings.ts` и т.д.) и Pinia-сторами поверх. Архитектурно подход чистый: один HTTP-клиент, явная де-дупликация GET-запросов (F-09), нормализация двух форматов ошибок (VeloError vs Pydantic 422), отдельный TOKEN-стор.

**Главные кросс-файловые проблемы:**

1. **Контракт `PracticeSummary` рассинхронизирован** — фронтенд читает поле `timezone`, которого бэкенд не возвращает. Это **рабочий продакшн-баг**: время всех бронирований у пользователя отрисовывается в Берлинском поясе из-за fallback'а.
2. **UserResponse-схемы расходятся в названиях полей** (`language` vs `language_code`, `last_login_at` vs `updated_at`, лишний `username`). TypeScript не ловит это, потому что `JSON.parse` принимает любую структуру.
3. **Большой кусок бэкенд-API не имеет фронтенд-клиента** (waitlist полностью, purchases/me, reports CRUD юзера, promos master/admin, AI summary, admin/withdrawals, admin/users, logout-all, PATCH users/me, finalize practice, booking join/leave). Фронтенд при этом ссылается на маршрут `user-ai-summary`, для которого нет ни view, ни API-вызова.
4. **Типы дублируются** между `api/types.ts` и `api/payments.ts` (TopupRequest/Response объявлены дважды).

**Quality score: 6/10** — солидная инфраструктура клиента, но контракт «плывёт», потому что типы пишутся вручную, а не генерируются из OpenAPI. Один из расхождений (timezone в PracticeSummary) — реальный продакшн-баг с финансовым побочным эффектом (пользователь видит неверное время практики, может пропустить).

---

## 2. Bugs and logic errors

### 🔴 CRITICAL — `PracticeSummary.timezone` есть на фронте, но бэкенд его не возвращает

`backend/app/modules/practices/schemas.py:332-348` — `PracticeSummary` НЕ содержит поле `timezone`. Это используется как embed в `BookingWithPracticeResponse`, `WaitlistWithPracticeResponse`, `PurchaseWithPracticeResponse`.

`frontend/src/api/types.ts:148-157` декларирует `timezone: string` (NOT NULL).

`frontend/src/views/user/UserDashboardView.vue:303-308` использует поле:
```ts
// ❌ Current — practice.timezone всегда undefined → fallback всегда срабатывает
const tz = nearestBooking.value.practice.timezone ?? 'Europe/Berlin'
return `${formatDateShort(iso, tz)}, ${formatTime(iso, tz)}`
```

**Импакт:** время ближайшей практики и продолжительность на дашборде, в `MyBookingsView`, в любых карточках с PracticeSummary рисуются в Берлинском поясе независимо от реального TZ практики. Пользователь в Москве, забронировавший практику мастера в Стамбуле, увидит время «как будто это Берлин».

**Fix (бэкенд):**
```python
# ❌ Current — backend/app/modules/practices/schemas.py:332
class PracticeSummary(BaseModel):
    id: UUID
    title: str
    practice_type: str
    scheduled_at: datetime
    duration_minutes: int
    master_id: UUID
    master_name: str | None = None
    model_config = {"from_attributes": True}

# ✅ Proposed
class PracticeSummary(BaseModel):
    id: UUID
    title: str
    practice_type: str
    scheduled_at: datetime
    duration_minutes: int
    timezone: str           # ← add (NOT NULL в Practice ORM)
    master_id: UUID
    master_name: str | None = None
    model_config = {"from_attributes": True}
```

И обязательно — убрать молчаливый fallback на фронте, чтобы баг такого типа в будущем падал громко, а не показывал «приблизительное» время:
```ts
// ✅ Proposed — frontend/src/views/user/UserDashboardView.vue:306
const tz = nearestBooking.value.practice.timezone
if (!tz) {
  // Лучше явная ошибка, чем неверные данные пользователю
  return ''
}
```

### 🔴 CRITICAL — `UserResponse` поля не совпадают между бэком и фронтом

`backend/app/modules/users/schemas.py:20-36`:
```python
class UserResponse(BaseModel):
    id, telegram_id, role, first_name, last_name, avatar_url,
    timezone, language, is_active, balance_cents, created_at, last_login_at
```

`frontend/src/api/types.ts:33-47`:
```ts
export interface UserResponse {
  id, telegram_id, first_name, last_name,
  username,           // ❌ НЕТ на бэке
  avatar_url, role, is_active, balance_cents, timezone,
  language_code,      // ❌ Бэк присылает `language`
  created_at,
  updated_at          // ❌ Бэк присылает `last_login_at`
}
```

**Импакт:** сейчас фронт эти поля не читает (поиск по коду подтвердил), поэтому регрессии не видно. Но любая попытка использовать `user.language_code` или `user.updated_at` молча вернёт `undefined`. Это латентная мина — TypeScript типы лгут.

**Fix:**
```ts
// ✅ Proposed — frontend/src/api/types.ts:33
export interface UserResponse {
  id: string
  telegram_id: number | null
  role: UserRole
  first_name: string | null
  last_name: string | null
  avatar_url: string | null
  timezone: string                 // backend: NOT NULL
  language: string                 // ← переименовать из language_code
  is_active: boolean
  balance_cents: number
  created_at: string
  last_login_at: string | null    // ← переименовать из updated_at
}
// удалить поле `username` — его нет в API-ответе
```

### 🔴 CRITICAL — `cancelBooking` молча выбрасывает payload

`backend/app/modules/bookings/router.py:219` возвращает `BookingResponse` (200 OK с телом).
`frontend/src/api/bookings.ts:83`:
```ts
// ❌ Current — типизировано как void, тело ответа выбрасывается
export function cancelBooking(bookingId: string): Promise<void> {
  return api.delete(`/api/v1/bookings/${bookingId}`)
}
```
А в `client.ts:210` `delete()` всегда возвращает `Promise<void>`. JSON парсится, но теряется. Сейчас стор делает `await refresh()` сразу после, поэтому это работает «через сеть», но это лишний RTT и оптимистично-обновляемого UX нет.

**Fix:**
```ts
// ✅ Proposed — frontend/src/api/client.ts
delete<T = void>(path: string): Promise<T> {
  return request<T>('DELETE', path)
}

// frontend/src/api/bookings.ts
export function cancelBooking(bookingId: string): Promise<BookingWithPracticeResponse> {
  return api.delete<BookingWithPracticeResponse>(`/api/v1/bookings/${bookingId}`)
}
```
И в `cancelPractice`/`finalizePractice` бэкенд тоже возвращает `PracticeResponse`, фронт тоже читает — здесь ОК.

### 🔴 CRITICAL — мёртвая ссылка на `user-ai-summary`

`frontend/src/views/user/UserDashboardView.vue:190` пушит роут `user-ai-summary`, но:
- В `frontend/src/views/user/` нет файла `AiSummaryView.vue`
- В `frontend/src/api/` нет вызова `GET /api/v1/practices/{id}/ai-summary`, хотя бэкенд (`backend/app/modules/ai/router.py:36`) его экспонирует.

**Импакт:** клик по кнопке либо сломает роутер, либо отрисует пустой экран. Нужно либо реализовать view, либо убрать кнопку.

```vue
<!-- ❌ Current — frontend/src/views/user/UserDashboardView.vue:190 -->
@click.stop="router.push({ name: 'user-ai-summary' })"

<!-- ✅ Proposed: пока нет реализации — убрать обработчик и v-if-нуть кнопку -->
<button v-if="false" @click.stop="...">…</button>
<!-- Или закрыть PR с реализацией: router + view + api/ai.ts -->
```

### 🟡 WARNING — `CreateMasterPromoRequest.valid_from` обязателен на бэке, опционален во фронте

`backend/app/modules/promos/schemas.py:39`:
```python
valid_from: datetime = Field(description="Start of validity window (UTC).")  # без default → required
```
`frontend/src/api/types.ts:555`:
```ts
valid_from?: string | null   // optional
```
Фронт сейчас этот эндпоинт не вызывает (нет UI создания промо мастером, что само по себе пробел — см. секцию 3). Но как только UI появится — попытка отправить промо без `valid_from` → 422.

```ts
// ✅ Proposed — frontend/src/api/types.ts:550
export interface CreatePromoRequest {
  code: string
  discount_percent: number
  valid_from: string         // ← required, ISO 8601
  valid_until?: string | null
  max_uses?: number | null
  practice_id?: string | null
  first_purchase_only?: boolean
}
```

### 🟡 WARNING — `auth.ts` упускает обработку случая 401 в `loginViaTelegram`

`frontend/src/stores/auth.ts:51-69` — `loginViaTelegram` проглатывает любой `catch` и возвращает `false`. Но если бэк ответит 401 (например, replay-attack отбит), `_onUnauthorized` срабатывает и сбрасывает сессию — что норм. Но 401 здесь невозможен (это сам логин), а реальные 4xx (badRequest от валидации initData) теряют detail. Caller получает `false` без возможности отличить «токен бота не настроен» от «replay-attack».

```ts
// ❌ Current
} catch {
  _clearSession()
  return false
}

// ✅ Proposed — пробросить ApiResponseError, чтобы caller мог toast.error(e.detail)
} catch (e) {
  _clearSession()
  if (e instanceof ApiResponseError) throw e
  return false
}
```

### 🟡 WARNING — токен в `sessionStorage`, не в `localStorage`

`frontend/src/stores/auth.ts:15` — `sessionStorage`. Это значит:
- закрытие вкладки = логаут
- открытие сайта в новой вкладке = логаут (initData переподписать снова, что ок для TG WebApp, но плохо для веб-входа)

В контексте Telegram Mini App это допустимо (initData выдаётся при каждом открытии), но если планируется обычный веб-доступ — пользователь будет перелогиниваться. Решение зависит от продуктовых требований; стоит явно зафиксировать выбор в комментарии.

---

## 3. Эндпоинты бэкенда без фронтенд-клиента

Это не баги в строгом смысле, но контрактные пробелы. Список эндпоинтов, которые бэк экспонирует, а фронт не использует:

### 🔴 CRITICAL — Waitlist полностью не реализован на фронте
Бэк предоставляет 4 эндпоинта (`POST /practices/{id}/waitlist`, `GET /waitlist/me`, `DELETE /waitlist/{id}`, `POST /waitlist/{id}/confirm`) и шлёт нотификации, но фронт не имеет ни одной кнопки «встать в лист ожидания». Пользователь, видя «нет мест», не сможет ничего сделать. `WaitlistEntryResponse` в `types.ts` объявлен и не используется.

### 🟡 WARNING — Прочие незаимплементенные пути

| Эндпоинт | Назначение | Влияние |
|---|---|---|
| `PATCH /api/v1/users/me` | Обновление профиля | UserProfileView не позволяет изменить first_name/timezone/language |
| `POST /api/v1/auth/logout-all` | Выйти со всех устройств | Нет соответствующей кнопки в настройках |
| `GET /api/v1/purchases/me` | История покупок | `MyBookings` показывает бронирования, но не платёжную историю |
| `POST /api/v1/reports` + `GET /reports/me` + `PATCH /reports/{id}` | Жалобы юзера | Юзер не может пожаловаться, хотя админ-часть готова |
| `POST/GET/PATCH /masters/me/promos` | Управление промокодами мастером | Мастер не может создать промокод |
| `POST/GET/PATCH /admin/promos` | Управление компанийскими промо | Админ не может создать платформенный промо |
| `GET /admin/users` | Список пользователей | В админке есть только мастера |
| `GET /admin/withdrawals` + approve/reject | Модерация выводов | Мастер вывод запрашивает, но админ его обработать не может через UI |
| `GET /practices/{id}/ai-summary` | AI-отчёт | См. CRITICAL выше — ссылка ведёт в никуда |
| `POST /admin/templates/reload` | Перезагрузка шаблонов нотификаций | Только через curl |
| `POST /bookings/{id}/join` + `/leave` | Чек-ин на лайв-сессию | Бэкенд готов, UI нет |
| `POST /practices/{id}/finalize` | Финализация мастером | Wrapper в `practices.ts` есть, но я не нашёл UI-вызова |
| `GET /admin/masters/rejected` | Отклонённые заявки | Нет фильтра в `AdminMastersView` |

**Fix:** провести inventory-сессию с продактом — что осознанно отложено в backlog (waitlist, AI), а что упущено (purchases/me, reports/me, withdrawals admin). Незакрытые пробелы → либо удалить эндпоинты с бэка, либо добавить UI.

---

## 4. Error handling

### 🟡 WARNING — `client.ts:142` сбрасывает сессию даже при «ложных» 401

```ts
if (response.status === 401) {
  _onUnauthorized?.()
  throw new ApiResponseError(401, 'Session expired', 'unauthorized')
}
```

Любая 401, даже от случайного 401 на не-сессионных эндпоинтах (например, 401 от Stripe-вебхука, если фронт случайно туда дёрнется), сбросит сессию пользователя. На практике маловероятно, но архитектурно опасно — нужно проверять, что 401 реально про токен. Например, бэк может присылать `code: "unauthorized"` против `code: "stripe_signature_invalid"`. Сейчас этого различия нет.

```ts
// ✅ Proposed — выгружать сессию только если код === 'unauthorized'
if (response.status === 401) {
  const data = await safeJson(response)
  const code = data?.error ?? 'unauthorized'
  if (code === 'unauthorized' || code === 'session_expired') {
    _onUnauthorized?.()
  }
  throw new ApiResponseError(401, data?.message ?? 'Session expired', code)
}
```

### 🟡 WARNING — 15-сек timeout убьёт Stripe-redirect при медленном бэке

`client.ts:22` — `REQUEST_TIMEOUT_MS = 15_000`. Создание `checkout_url` через Stripe API может занимать >15с в моменты их деградации. Топап провалится, юзер увидит «Не удалось создать платёж», хотя на бэке может остаться pending Payment-запись.

**Fix:** для платёжных мутаций — таймаут 30–45с, либо отдельный helper `apiSlow.post(...)`.

---

## 5. Security

### 🟡 WARNING — `UserUpdate` не позволяет менять `balance_cents` (это хорошо), но фронт держит тип `UpdateUserRequest` без него — двойной защиты нет

`frontend/src/api/types.ts:49-53` — `UpdateUserRequest` не включает `balance_cents`, бэкенд (`schemas.py:39`) тоже не принимает. Защита есть. Однако стоит добавить тест/контракт-комментарий, что это именно намеренная защита (TD-029 объясняет cache, но не security).

### 🟢 SUGGESTION — `nginx.conf` URL-белый список редиректа в `TopupView.vue:106-108`

```ts
const ALLOWED_REDIRECT_PREFIXES = [
  'https://checkout.stripe.com/',
  import.meta.env.VITE_API_BASE_URL || 'https://api.talentir.info',
]
```
`startsWith` уязвим к ловушке `https://checkout.stripe.com.evil.com/` — стандартная ошибка whitelist'ов. URL надо парсить:

```ts
// ✅ Proposed
function isAllowedRedirectUrl(url: string): boolean {
  try {
    const u = new URL(url)
    return u.protocol === 'https:' &&
      (u.host === 'checkout.stripe.com' || u.host === 'api.talentir.info')
  } catch { return false }
}
```

---

## 6. Performance

No major issues found. F-09 (in-flight deduplication для GET) — хорошая практика. Pagination реализована корректно (offset/limit), без N+1 на фронте. Бэкенд возвращает `PracticeSummary` embed'ом в bookings/waitlist/purchases — это сознательно избегает N+1 на стороне клиента.

### 🟢 SUGGESTION — `getMastersList` дёргает 100 записей сразу
`api/admin.ts:73`:
```ts
limit = 100
```
Default 100 vs. 20 в остальных endpoint'ах — несогласованно. Если у платформы будут тысячи мастеров — нужна нормальная пагинация в `AdminMastersView`.

---

## 7. Code quality

### 🟡 WARNING — Дублирование типов TopupRequest/TopupResponse

`frontend/src/api/payments.ts:13-22` объявляет:
```ts
export interface TopupRequest { amount_cents: number }
export interface TopupResponse { payment_id: string; checkout_url: string; amount_cents: number; currency: string }
```
А все остальные типы лежат в `api/types.ts`. Несогласованность — `api/admin.ts:37-48` имеет re-exports именно потому, что types.ts — единый источник правды. Перенести.

### 🟡 WARNING — Хардкод финансовых констант на фронте

`frontend/src/utils/constants.ts:29-32`:
```ts
export const MIN_WITHDRAWAL_EUROS = 50
export const WITHDRAWAL_FEE_EUROS = 2
```
Комментарий честно говорит: «Mirror: backend config.py min_withdrawal_cents=5000». Если бэк изменит — фронт молча разъедется (форма даст создать вывод 30€, бэк вернёт 422). Решения два:
1. Отдать через `GET /api/v1/config` (один лёгкий endpoint).
2. Положить в `MasterProfileResponse` вместе с `available_cents` поля `min_withdrawal_cents`, `withdrawal_fee_cents`.

```python
# ✅ Proposed — backend/app/modules/masters/schemas.py
class MasterProfileResponse(BaseModel):
    ...
    available_cents: int
    min_withdrawal_cents: int  # ← из settings
    withdrawal_fee_cents: int  # ← из settings
```

### 🟡 WARNING — `BASE_URL = ''` по умолчанию

`frontend/src/api/client.ts:21`:
```ts
const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
```
Если переменная не задана — все запросы пойдут на same-origin. Это работает только если nginx-proxy в `frontend/nginx.conf` настроен. Локальная разработка через `vite dev` без proxy упадёт в CORS.

```ts
// ✅ Proposed — fail-fast в dev режиме
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''
if (import.meta.env.DEV && !BASE_URL && !import.meta.env.VITE_USE_PROXY) {
  console.warn('VITE_API_BASE_URL not set; ensure dev proxy is configured')
}
```

### 🟢 SUGGESTION — `AdminMasterListItem.role` типизирован как `string`

`frontend/src/api/types.ts:323`:
```ts
role: string
```
А в `UserResponse` `role: UserRole`. На бэке тоже `str`, не enum. Можно сузить до `UserRole`.

---

## 8. Refactoring proposals

### 🔴 CRITICAL — Сгенерировать TS-типы из OpenAPI

Корневая причина всех расхождений в секциях 2 и 7 — типы пишутся вручную. FastAPI бесплатно отдаёт OpenAPI на `/openapi.json`. Прогон через `openapi-typescript` или `orval` уберёт целый класс багов:

```bash
# ✅ Proposed
npx openapi-typescript http://localhost:8000/openapi.json \
  -o frontend/src/api/generated.ts
```

Затем в `api/types.ts` экспортировать только те типы, что не выводятся из OpenAPI (UI-only DTO). Контракт, расхождение которого нашло этот ревью (`PracticeSummary.timezone`, `UserResponse.language` vs `language_code`), невозможен при генерации.

### 🟡 WARNING — Один источник для UrlPath'ов

Сейчас в `api/practices.ts`, `api/admin.ts` и т.д. URL-строки разбросаны и иногда с опечатками риск (за всё ревью я не нашёл, но прецедент типов показывает, что ручная синхронизация ошибочна). Завести `api/routes.ts` с константами:

```ts
export const ROUTES = {
  practices: {
    list: '/api/v1/practices',
    detail: (id: string) => `/api/v1/practices/${id}`,
    cancel: (id: string) => `/api/v1/practices/${id}/cancel`,
    // ...
  },
} as const
```

---

## 9. Minor improvements

- 🟢 `frontend/src/api/types.ts:60` — `PracticeStatus` включает `'deleted'`, но фронт никогда не покажет deleted-практику (бэк фильтрует). Можно сузить.
- 🟢 `frontend/src/api/admin.ts:140` — `dismissReport` всегда шлёт `resolution_note: null`, если опционален. Бэк (`DismissReportRequest`) принимает. Стоит сделать `body` опциональным (`api.post(path, undefined)`), чтобы не слать `{"resolution_note": null}`.
- 🟢 Бэкенд возвращает `ExistingReportResponse` (200) вместо нового репорта при дубликате. Фронта для этого нет, но если/когда появится — нужно различать 200 + `report` vs 201 + `ReportResponse` по shape, иначе UX будет неотличим.

---

## 10. Dependencies

Не входит в скоуп ревью контракта (`package.json` и `pyproject.toml` не анализировал глубоко).

---

## Summary

**Score: 6/10** — инфраструктура клиента достойная, но контракт между сервисами прихрамывает и есть один реальный продакшн-баг, влияющий на отображение времени практик.

🔴 **Must fix:**
- `PracticeSummary` без `timezone` на бэке + молчаливый Berlin-fallback на фронте → неверное время практик в дашборде/брони (бэк: добавить `timezone`; фронт: убрать fallback)
- `UserResponse` поля `username` / `language_code` / `updated_at` во фронт-типах не соответствуют ответу бэка (`language` / `last_login_at`, нет `username`)
- `cancelBooking` типизирован как `Promise<void>` — теряет `BookingResponse`, лишний refresh round-trip
- Кнопка `user-ai-summary` в `UserDashboardView` ведёт на несуществующий маршрут
- Waitlist полностью не реализован на фронте, при том что бэк готов и шлёт нотификации
- Сгенерировать типы из OpenAPI, чтобы такие расхождения было невозможно создать

🟡 **Should fix:**
- `CreateMasterPromoRequest.valid_from` — required на бэке, optional во фронте
- `loginViaTelegram` глотает `ApiResponseError.detail`
- 15-сек timeout убьёт Stripe-redirect при их деградации
- 401 от любого endpoint'а сбрасывает сессию (нужно различать по `error.code`)
- Дублирование типов `TopupRequest/Response` между `api/payments.ts` и `api/types.ts`
- Хардкод `MIN_WITHDRAWAL_EUROS` / `WITHDRAWAL_FEE_EUROS` в `utils/constants.ts` — drift-риск
- Отсутствие фронт-UI для покупок (`/purchases/me`), репортов юзера (`/reports/me`), управления промо мастером, админ-вывода средств, `PATCH /users/me`, `logout-all`, finalize practice, join/leave booking
- `BASE_URL = ''` по умолчанию — тихо работает в Docker, ломается в `vite dev` без явного объяснения

🟢 **Nice to have:**
- `isAllowedRedirectUrl` использовать `new URL()`, а не `startsWith`
- `PracticeStatus` сузить, убрав `'deleted'`
- `dismissReport` не слать `resolution_note: null`, если не передано
- `getMastersList` дефолтный limit=100 vs 20 в остальных — унифицировать
- Завести `api/routes.ts` с константами URL'ов
- Token в `sessionStorage` vs `localStorage` — задокументировать сознательный выбор для TG WebApp
