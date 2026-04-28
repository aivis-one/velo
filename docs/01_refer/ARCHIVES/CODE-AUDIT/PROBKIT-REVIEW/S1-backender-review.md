# Ревью Velo Frontend — закрытие спринта S1

**Дата ревью**: 2026-04-28
**Audit base**: `9cf88fa..HEAD` (S1 sprint plan → текущий HEAD `1330f59`).
**Объём**: 346 файлов, +9 963 / −1 623 строки. 74 файла кода (.ts / .vue / .css) в `frontend/src/` затронуты.
**Стек**: TypeScript 5.7 / Vue 3.5 (Composition API + `<script setup>`) / Pinia 2.3 / vue-router 4.5 / Vite 6.1 / Vitest 3.0 / vite-plugin-pwa.
**Тип проекта**: Telegram Mini App (TMA) с PWA-fallback (decisions #013).
**Стадия**: MVP, sprint 1 закрывается.
**Критичность**: medium (wellness/mindfulness app; не fintech, не медицинское ПО; работает с балансом, бронированиями, PII через Telegram initData).
**Mode**: diff-review.
**Калибровка**: предыдущий проход партнёра — `Zodd_review.md` против `364893d` (decisions #022); этот пасс даёт сравнительную точку.

---

## Headline

**Качество**: 8/10. Архитектура зрелая для S1 close. Критических находок нет. Главная инвестиционная зона — покрытие тестами. Зависимости имеют известные CVE — требуется `npm audit fix` до выхода в прод.

| Раздел | 🔴 | 🟡 | 🟢 |
|---|---|---|---|
| 1. Overview / архитектура | — | — | — |
| 2. Bugs and logic errors | 0 | 0 | 0 |
| 3. Error handling | 0 | 1 | 1 |
| 4. Security | 0 | 0 | 1 |
| 5. Performance | 0 | 1 | 1 |
| 6. Code quality | 0 | 1 | 2 |
| 7. Testability | 0 | 1 | 1 |
| 8. Refactoring proposals | — | — | 2 |
| 9. Minor improvements | — | — | 2 |
| 10. Dependencies | **1** | 2 | 1 |
| **TOTAL** | **1** | 6 | 11 |

Единственный 🔴 — известные CVE в дев-зависимостях (`npm audit`: 1 critical, 8 high, 2 moderate). Прод-сборка использует `vite` с CVE на arbitrary file read через WebSocket (CVE по dev-серверу — в проде не работает, но dev-окружение партнёра/девелопера потенциально уязвимо).

---

## 1. Overview

**Что делает код**: фронт wellness-приложения. Пользователь (`user`) бронирует практики мастеров, ведёт дневник (записи / check-ins / отзывы), пополняет баланс через Stripe. Мастер (`master`) проводит практики, видит финансы, аналитику. Админ (`admin`) модерирует мастеров, просматривает отчёты. Авторизация через Telegram initData (TMA) или standalone-PWA fallback при отсутствии Telegram.

**Архитектура**:
- Точка входа `main.ts` → `App.vue`. App.vue показывает `LoadingView` → `StandaloneStubView` (если не TMA или не аутентифицирован) → `<RouterView>`.
- Auth-flow: `composables/useAuth.ts:initAuth()` → `restoreSession()` (sessionStorage) → `loginViaTelegram()` (initData) → standalone fallback.
- API-клиент `api/client.ts` — централизованный fetch с 15-секундным AbortController, in-flight GET-дедупликацией, нормализацией двух форматов ошибок бэкенда (VeloError + Pydantic 422), 401-callback в auth-store.
- 7 Pinia-сторов (auth, balance, bookings, diary, master, practices, ui), 6 composables (useAuth, useApiError, usePagination, usePracticeWindows, useToast — последний — 1 утилитный setup), 10 api-модулей (1 авто-генерируемый — `generated.ts` из бэкенд OpenAPI per #023).
- 30+ view-файлов, разбитых по ролям (`auth/`, `user/`, `master/`, `admin/`).

**Cross-file**: дисциплина невероятно ровная для MVP. Каждый стор использует `extractApiError()` из общего composable. Каждый список — `usePagination`. Каждый toast — `useToast`. Заголовки файлов содержат FIX-ID (10.1, 10.2, 10.4, F-03, F-09, NEW-6, NEW-8, WARNING-1, WARNING-3, W-1, QW-4, C-1, P-1, BUG-role-redirect, TD-F01, TD-FE-ROLE-SWITCH) — провенанс изменений отслеживаем.

**Архитектурное замечание**: `roleGuard()` в `router/guards.ts:85-102` синхронен и не ждёт `waitUntilReady()` — текущий код безопасен, потому что App.vue блокирует RouterView через `isReady`, но это хрупкая зависимость от двух разных слоёв (App.vue gate + router guard). Защитный фикс — добавить `await waitUntilReady()` в guard. Detail в Section 4.

**Quality score: 8/10.**
- Production-ready по архитектуре (slot 9-10).
- Минус 1 за тестовое покрытие (только 2 test-файла, 32 теста — `usePagination` + `format`).
- Минус 1 за зависимости (CVE + outdated major versions).
- Без минусов: типобезопасность (vue-tsc 0 ошибок), безопасность кода (0 hardcoded secrets, 0 XSS sinks, allowlist на Stripe redirect), error handling discipline, dark-mode token coverage.

---

## 2. Bugs and Logic Errors

**No issues found.**

vue-tsc проходит чисто (0 ошибок). Все async/await пути имеют корректное распространение ошибок. `instanceof`-narrowing на ApiResponseError — везде. Off-by-one не наблюдается в просмотренных hot paths (`composables/usePagination.ts`, `stores/diary.ts:loadInsights` LRU eviction, `views/user/TopupView.vue:eurStringToCents` IEEE-754 trap-aware).

Замечание: BACKLOG #27 (PracticeSummary.timezone fallback в `Europe/Berlin`) — это data-correctness gap бэкенда (Pydantic-схема не отдаёт timezone), не баг фронта. Frontend применяет тактический cast в `UserDashboardView.vue:300` (per C06b). Данное audit-base уже учитывает фикс.

---

## 3. Error Handling

### 🟡 WARNING — `router/index.ts:329-331` тихий fallback при таймауте auth

`router.beforeEach` ждёт `waitUntilReady()` на первой навигации; при таймауте просто логирует `console.warn` и пропускает запрос дальше. На практике App.vue gate (`App.vue:14-17`: `isReady && !isAuthenticated → StandaloneStubView`) перехватывает ситуацию, но эта подстраховка молчаливая — при изменении App.vue в будущих спринтах режим «таймаут + null role» оставит пользователя на запрошенном роуте без видимой ошибки.

```diff
  if (!authInitialized) {
    const { timedOut }: ReadyResult = await waitUntilReady()
    authInitialized = true
    if (timedOut) {
-     console.warn('[router] auth initialization timed out on first navigation')
+     return { path: '/auth-error' }
    }
  }
```

Альтернатива — задокументировать инвариант `App.vue.isReady-as-gate` явным комментарием здесь.

### 🟢 SUGGESTION — `stores/auth.ts:61-65, 81-83, 110-112` — 3 silent catch без телеметрии

NEW-8 в комментарии явно оправдывает молчание для `loginViaTelegram` («auth failure — нормальный flow в проде: expired initData, banned user»). Но без Sentry/log-pipe нет ни одного сигнала о deteriorating signup rate. Когда придёт логирование (S2+), восстановить минимальный `event=auth_failure_expected` с категорией.

---

## 4. Security

### 🟢 SUGGESTION — `roleGuard()` синхронный

`router/guards.ts:85-102`. Не ждёт `waitUntilReady()`. Если когда-нибудь `App.vue.isReady` gate перестанет быть единственным барьером (например, при прямом доступе к route через deep-link), guard прочитает `auth.role === null` и отправит пользователя на `/user/dashboard`, что для admin/master выглядит как несанкционированный доступ к чужому интерфейсу.

```diff
  export function roleGuard(required: ...): NavigationGuardWithThis<undefined> {
-   return () => {
+   return async () => {
+     await waitUntilReady()
      const auth = useAuthStore()
      ...
```

Defense-in-depth, не текущий exploit.

### Проверено и чисто

- Hardcoded secrets: 0 (full regex-scan пройден на 15+ паттернах, в т.ч. AWS / Stripe / GitHub / OpenAI / private keys).
- XSS surface: 0 (`v-html`, `innerHTML`, `eval`, `new Function`, `outerHTML` — все 0 совпадений).
- Token storage: `sessionStorage` (per-tab; не localStorage, что было бы регрессом). 401 → callback `_clearSession()` через `setOnUnauthorized`. Token не логируется и не сериализуется в JSON нигде.
- AbortController + 15s timeout: `api/client.ts:122-141`.
- CSRF: not applicable (Bearer token в Authorization header, не cookies; `credentials:` в fetch не выставляется).
- Open-redirect: `views/user/TopupView.vue:104-185` имеет allowlist `ALLOWED_REDIRECT_PREFIXES` + проверку `isAllowedRedirectUrl(url)` перед `window.location.href = response.checkout_url`. Защита C-1 от компрометации бэкенда.
- `target="_blank"` external links имеют `rel="noopener"` (`WelcomeView.vue:34`, `StandaloneStubView.vue:18`); `noreferrer` отсутствует — мелочь, отдельно в Section 9.

---

## 5. Performance

### 🟡 WARNING — Размер view-файлов

9 view-файлов превышают 500 LOC:
- `EditPracticeView.vue` 939
- `AnalyticsView.vue` 812
- `UserDashboardView.vue` 741
- `PracticeDetailView.vue` 706
- `MasterProfileView.vue` 668
- `MasterFinanceView.vue` 615
- `CreatePracticeView.vue` 551
- `MasterApplyView.vue` 544
- `MasterDashboardView.vue` 542

Render-влияния нет (Vite chunks per-route via `() => import(...)` в `router/index.ts`). Cost — maintenance: `EditPracticeView.vue:519-700` содержит 9 параллельных try/catch для разных state-transitions (publish, startLive, finalize, cancel, remove, save и др.) с дубликатным паттерном `toast.error(e instanceof ApiResponseError ? e.detail : 'fallback')`. Stores уже мигрировали на `extractApiError`; views — нет. Mechanical refactor: ~25-30 сайтов в крупных views.

### 🟢 SUGGESTION — `stores/diary.ts:296-300` LRU vs FIFO

Комментарий говорит «LRU eviction», реализация — FIFO (`insightsCache.keys().next().value`). Для immutable-after-fetch insights cache разница академическая — все обращения происходят сразу после set. Поправить или комментарий, или реализацию (Map re-insertion on access). SUGGESTION-уровень.

### Проверено и чисто

- F-09 in-flight GET dedup: `api/client.ts:87-103, 198-208`. Map-based; `.finally()` снимает entry; subsequent calls идут в сеть.
- N+1: не наблюдается. Все list-fetch методы — single round-trip с `(limit, offset)`.
- Pagination: 5 сторов используют общий `composables/usePagination.ts` (9 unit-тестов).
- Lazy routes: каждый route в `router/index.ts` использует `() => import(...)`.
- PWA precache: 99 entries (per S1 P03 close).

---

## 6. Code Quality

### 🟡 WARNING — Дублирование try/catch + toast.error в views

См. Section 5 — то же явление. ~25-30 сайтов в крупных views. Каждый раз пишут:
```ts
} catch (e) {
  toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось <action>')
}
```
вместо единственного:
```ts
} catch (e) {
  toast.error(extractApiError(e, 'Не удалось <action>'))
}
```

`extractApiError` уже импортируется из `@/composables/useApiError` в сторах. Перенести паттерн в views — 1 cycle, mechanical.

### 🟢 SUGGESTION — Заголовки файлов с FIX-ID будут «гнить»

Каждый view карет `Phase F1.1, fixed 10.1, fixed BUG-role-redirect, TD-F01` в шапке. Это **исключительно полезно** сейчас (audit provenance), но через 5-10 спринтов половина FIX-ID станет устаревшей или будет относиться к коду, который уже отрефакторен. BACKLOG #26 уже фиксирует один такой драift в `MasterFinanceView.vue:25-26`. Рекомендую: на каждом sprint-close раунд аудита заголовков.

### 🟢 SUGGESTION — `views/master/EditPracticeView.vue:900-915` ре-имплементация модального диалога

Кастомный confirm overlay (`fixed; rgba(0,0,0,0.5)` overlay) дублирует `components/ui/VModal.vue`. Тот же паттерн в `views/master/AttendanceView.vue:504-506`. Использовать VModal — снимет 2 hardcoded `rgba(0, 0, 0, 0.5)` (design-audit P1 находки) и три дубликата.

### Проверено и чисто

- Naming: единообразный (camelCase / PascalCase / SCREAMING_SNAKE_CASE).
- SOLID: stores имеют single responsibility. Composables инкапсулируют один concern.
- Dead code: только IconRuble.vue (BACKLOG #29) — flagged.
- Modern features: optional chaining, nullish coalescing, async/await — везде.

---

## 7. Testability

### 🟡 WARNING — Покрытие тестами недостаточное для S1 close

Тестов: 32 в 2 файлах (`composables/usePagination.test.ts` 9 тестов, `utils/format.test.ts` 23 теста). Все проходят за 535мс.

Не покрытые critical paths:
- `api/client.ts` — timeout, dedup, error normalize, 401-callback (0 тестов)
- `stores/auth.ts` — login, restore, fetchMe, logout (0 тестов)
- `router/guards.ts` — roleRedirect, roleGuard, masterStatusGuard (0 тестов)
- 6 из 7 stores — 0 тестов
- 30+ views — 0 тестов (UI можно отложить до E2E, но stores и composables — нет)

Архитектура хорошо подготовлена для тестов: есть hooks `resetClientState()` (api/client.ts:99-103) и `resetAuthState()` (composables/useAuth.ts:66-70) — DI-friendly. Quantity-проблема, не testability.

Минимально достаточный объём для S2 (≈30 тестов): `auth-store.test.ts` + `api-client.test.ts` + `router-guards.test.ts` + 1-2 store-теста.

### 🟢 SUGGESTION — Существующие тесты — образцовые

`usePagination.test.ts` использует closure-based mock fetch, тестирует state-machine (loadMore returns true/false, items length, hasMore, error captured), есть error-path и concurrency-test (deferred-resolve pattern, без `setTimeout`-flakes). При расширении test suite — придерживаться того же стиля.

---

## 8. Refactoring Proposals

### 🟢 SUGGESTION — Унифицировать confirm-modal

Сейчас 3 имплементации диалога подтверждения: VModal (`components/ui/VModal.vue`), кастом overlay в `EditPracticeView.vue:900-915`, кастом в `AttendanceView.vue:504-516`. Все три — один паттерн. Убрать кастомы → использовать VModal:

```diff
- <div v-if="confirmDialog.visible" class="edit-practice__overlay">
-   <div class="edit-practice__dialog">
+ <VModal :open="confirmDialog.visible" @close="confirmDialog.visible = false">
    <h3>{{ confirmDialog.message }}</h3>
    <VButton variant="danger" @click="confirmDialog.onConfirm">{{ confirmDialog.confirmLabel }}</VButton>
+ </VModal>
```

Дополнительно решит:
- design-audit P1 (3 × `rgba(0,0,0,0.5)` overlay → `var(--surface-overlay-50)` через VModal)
- a11y P4 (focus-trap, focus-return уже частично есть в VModal — там Escape работает, тут нет)
- code-quality DRY

### 🟢 SUGGESTION — Перенести view-level catch в `extractApiError`

См. Section 6. Mechanical, 1 cycle.

---

## 9. Minor Improvements

### 🟢 SUGGESTION — `rel="noopener noreferrer"` для `_blank` ссылок

`views/auth/WelcomeView.vue:34`, `views/auth/StandaloneStubView.vue:18` — оба с `rel="noopener"`. Добавить `noreferrer` для полноты:

```diff
- <a :href="botUrl" target="_blank" rel="noopener">
+ <a :href="botUrl" target="_blank" rel="noopener noreferrer">
```

Telegram bot URL — собственный, утечка Referer некритична. Best practice без compromise.

### 🟢 SUGGESTION — Hardcoded fallback URL в WelcomeView/StandaloneStub

`views/auth/WelcomeView.vue:43`:
```ts
const botUrl = import.meta.env.VITE_TELEGRAM_BOT_URL || 'https://t.me/velo_testbot'
```

Если `VITE_TELEGRAM_BOT_URL` отсутствует в prod-сборке, пользователи молча уходят на test-bot. Защититься через assert на `import.meta.env.PROD && !VITE_TELEGRAM_BOT_URL → throw`.

---

## 10. Dependencies

### 🔴 CRITICAL — `npm audit` отчитывает 11 vulnerabilities (1 critical, 8 high, 2 moderate)

```
brace-expansion <=1.1.12 || 2.0.0 - 2.0.2 || 4.0.0 - 5.0.4
  Severity: moderate
  GHSA-f886-m6hf-6m8v (zero-step DoS / memory exhaustion)

flatted <=3.4.1
  Severity: high
  GHSA-25h7-pfq9-p65f (unbounded recursion DoS)
  GHSA-rf6f-7fwh-wjgh (prototype pollution)

vite <=6.4.1
  Severity: high
  GHSA-4w7w-66w2-5vf9 (Path Traversal in optimized deps `.map`)
  GHSA-p9ff-h696-f583 (arbitrary file read via dev WebSocket)

(плюс ещё 7 транзитивных)
```

**Контекст**: большинство уязвимостей — в dev-зависимостях (`@typescript-eslint`, `vue-tsc`, `workbox-build`). Vite GHSA-p9ff-h696-f583 — dev-server only (production build не запускает dev WebSocket). Однако:
- Локальное dev-окружение разработчика/партнёра уязвимо при работе на untrusted сети (открыт WebSocket порт).
- 1 critical-vuln (без детальной инспекции непонятно, в какой именно зависимости — `npm audit` группирует) требует ручной верификации — может быть и в прод-bundle.

**Действие**: запустить `npm audit fix` (без `--force`). Если что-то ломается — прокатиться `npm audit fix --force` в feature-branch + smoke-test перед мерджем. Важно сделать **до** прод-deploy на staging.

### 🟡 WARNING — Outdated major versions (без security impact, technical debt)

```
pinia        2.3.1 → 3.0.4 (major)
vue-router   4.6.4 → 5.0.6 (major)
eslint       9.39.3 → 10.2.1 (major)
vite         6.4.1 → 8.0.10 (major)
vitest       3.2.4 → 4.1.5 (major)
typescript   5.7.3 → 6.0.3 (major)
@vitejs/plugin-vue 5.2.4 → 6.0.6 (major)
vite-plugin-pwa 0.21.2 → 1.2.0 (major)
typescript-eslint 8.56.1 → 8.59.1 (minor)
+ ещё 4 minor
```

Pinia 3.x и vue-router 5.x — major-bump'ы с breaking changes. Отдельный sprint-cycle (S5+ или Clean-Sync) на постепенную миграцию. Не блокирующий.

### 🟡 WARNING — `frontend/src/api/payments.ts:13-22` дублирует `generated.ts`

`TopupRequest` / `TopupResponse` declared дважды — в payments.ts и в auto-generated.ts. Per #023 SSOT pattern должно быть `re-export from generated.ts`. BACKLOG #32 уже tracked.

### 🟢 SUGGESTION — Минимальный набор runtime deps

`package.json` deps: только `vue`, `vue-router`, `pinia` — 3 runtime-зависимости. Никакого чарт-бандлинга, никакого date-fns/lodash/axios — всё пишется руками или через composables. Это **очень хорошо** для bundle size. Сохранять дисциплину при добавлении функционала в S2/S3.

---

## Cross-Reference (decisions.md / BACKLOG)

- Подтверждены ACTIVE: #006 bundle SSOT, #007 flat aesthetic, #008 dark mode tokens, #009 token rename, #013 TMA+PWA, #017 shadows permitted, #018 lockfile implicit, #019 main.ts CSS imports, #020 admin-deferred markers, #021 project-extension tokens, #022 partner audit calibration, #023 generated.ts SSOT, #024 icons strategy, #025 WelcomeView fast-track, #026 ProbeKit hardening.
- Подтверждены known-issues (не новые находки): BACKLOG #11 stale hex comments, #13 visual convergence post-glass, #14 lint baseline, #26 financial constants migration (gated on regen), #27 PracticeSummary.timezone (gated on regen), #29 IconRuble dead, #32 TopupRequest duplication, #34 hex regex over-fires, #35 commit convention cleanup, #37 post-deploy visual.
- Новый material для Step 3 классификации: см. Section 3-10.

---

## Сравнение с предыдущим Zodd_review (decisions #022)

Партнёр в предыдущем ревью (`Zodd_review.md` @ `364893d`) идентифицировал 4 фронт-находки:
- B.1 (UserResponse stale shape) — RESOLVED партнёром через regen
- B.3, B.11 — fixed в C06
- A.2 (financial constants) — gated on regen, BACKLOG #26
- B.4 / B.5 / B.12 / etc. — backlogged

Новых находок такого же класса (post-regen consumer drift, contract mismatches) этот audit не нашёл — что подтверждает: regen-pipeline #023 сейчас работает, и `generated.ts` синхронизирован с бэкендом.

---

## Step 3 Classification Suggestion

Срочные (до прод-deploy):
- `npm audit fix` — Section 10 🔴

Высокая полезность (S2 hardening):
- view-level `extractApiError` адаптация — Section 6 + 8
- Confirm-modal унификация — Section 8 + design-audit P1 + a11y P4
- auth-store + api-client + router-guards тесты — Section 7

Низкоприоритетные (S2-S5, по потоку):
- `roleGuard` async-await — Section 4
- `noreferrer` для _blank — Section 9
- VITE_TELEGRAM_BOT_URL fail-fast — Section 9
- LRU vs FIFO в insightsCache — Section 5
- File-header FIX-ID housekeeping — Section 6
- Major-version dependency updates — Section 10

---

## Score: 8/10

Обоснование: production-ready archive, чистый type system, дисциплинированная error normalization, правильные security choices. Инвестиционные точки — тестовое покрытие и dependency hygiene. CRITICAL единственный — обновить vulnerable deps до прод-deploy.

S1 готова к закрытию по своим S1 success criteria. Прод-deploy блокируется на 🔴 npm audit fix; всё остальное может уйти в S2-S3 backlog.
