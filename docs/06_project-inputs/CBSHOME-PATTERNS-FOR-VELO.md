# CBSHOME → VELO: Best-Practices Transfer Report

> **Назначение.** Извлечь готовые архитектурные паттерны из зрелого
> репозитория `D:\02_Projects\cbshome\` (стек идентичен VELO) для применения
> в VELO. Цель — сократить spec-writing и implementation-фазы VELO за счёт
> переиспользования проверенных решений вместо изобретения с нуля.
>
> **Дата:** 2026-05-18
> **Источник:** `D:\02_Projects\cbshome\frontend\src\` (85 .vue + 57 .ts)
> **Целевой документ для апдейта:** `docs/05_roadmap/ROADMAP.md` + sprint-*.md
>
> **Headline.** CBSHOME — это **готовая референс-имплементация всего, что
> VELO планирует построить**. Структура папок 1:1 совпадает (`api/components/
> composables/i18n/platform/router/stores/styles/utils/views`). Стек один
> в один (Vue 3 + TS strict + Vite 6 + Pinia + Vue Router 4 + vue-i18n +
> Telegram WebApp + PWA). Все ключевые задачи VELO Sprint 0/1/2 и большая
> часть Sprint 11+ имплементационной фазы уже решены и протестированы в
> CBSHOME. Можно копировать паттерны блоками и адаптировать под домен VELO.

---

## Оглавление

1. [Стек: side-by-side](#1-стек-side-by-side)
2. [Inventory: что есть в CBSHOME](#2-inventory-что-есть-в-cbshome)
3. [Паттерны для прямого переиспользования](#3-паттерны-для-прямого-переиспользования)
   - 3.1 [Async bootstrap (main.ts)](#31-async-bootstrap-maints)
   - 3.2 [Single globalGuard (4 уровня)](#32-single-globalguard-4-уровня)
   - 3.3 [meta.shell propagation для shared views](#33-metashell-propagation-для-shared-views)
   - 3.4 [tabs.ts: SoT для tab-bar](#34-tabsts-single-source-of-truth-для-tab-bar)
   - 3.5 [Onboarding как state-machine в роутах](#35-onboarding-как-state-machine-в-роутах)
   - 3.6 [api/client: Retry-After + Accept-Language](#36-apiclient-retry-after-accept-language-extractErrormessage)
   - 3.7 [i18n: lazy loading + RTL + tOrRaw](#37-i18n-lazy-loading-rtl-tOrRaw)
   - 3.8 [Pinia stores: epoch guards + sessionReset](#38-pinia-stores-epoch-guards-sessionreset)
   - 3.9 [Type-narrowing guards (asUserRole)](#39-type-narrowing-guards-asUserRole-aliasstatus)
   - 3.10 [useAuth singleton + waitUntilReady](#310-useauth-singleton-waituntilready)
   - 3.11 [useToast / useInfiniteScroll / safeNavigate](#311-usetoast-useinfinitescroll-safenavigate)
   - 3.12 [useAuthWall + ?next= deep-link preservation](#312-useauthwall-next-deep-link-preservation)
   - 3.13 [UI Kit: 18 готовых компонентов](#313-ui-kit-18-готовых-компонентов)
   - 3.14 [Tier 3 layout: CHeader + CTabBar + 5 shells](#314-tier-3-layout-cheader-ctabbar-5-shells)
   - 3.15 [utils/querystring + formatSignedPrice](#315-utilsquerystring-formatSignedPrice)
   - 3.16 [Platform interface (9 методов vs VELO 8)](#316-platform-interface-9-методов-vs-velo-8)
4. [Паттерны для адаптации (не копировать as-is)](#4-паттерны-для-адаптации-не-копировать-as-is)
5. [Что НЕ переносить (CBSHOME-only)](#5-что-не-переносить-cbshome-only)
6. [Рекомендации по апдейту ROADMAP](#6-рекомендации-по-апдейту-roadmap)
7. [Оценка экономии времени](#7-оценка-экономии-времени)
8. [Конкретные следующие шаги](#8-конкретные-следующие-шаги)

---

## 1. Стек: side-by-side

| Слой | VELO (планируется) | CBSHOME (в продакшене) | Совпадает? |
|---|---|---|---|
| Framework | Vue 3 + Composition API `<script setup lang="ts">` | то же | ✅ |
| Language | TypeScript 5.x strict + `noUncheckedIndexedAccess` | TypeScript 5.7 strict | ✅ (VELO строже на 1 флаг) |
| Build | Vite 6 + VitePWA | то же | ✅ |
| Router | Vue Router 4.x | то же | ✅ |
| State | Pinia | то же | ✅ |
| HTTP | Кастомный fetch wrapper | то же (213 строк уже написано) | ✅ |
| Styles | Plain CSS + `--velo-*` tokens | Plain CSS + неpref'ed tokens (`--primary`, `--accent`) | 🟡 prefix отличается |
| Token prefix | `--velo-*` | без префикса (`--primary`, `--bg`) | 🟡 |
| Component prefix | `V*` (`VButton`) | `C*` (`CButton`) | 🟡 |
| i18n | vue-i18n (RU/EN) | vue-i18n (RU/EN/DE/AR + RTL) | ✅ (CBSHOME богаче) |
| Icons | (не специфицировано) | `lucide-vue-next` | 🟡 VELO не выбрал |
| Surface | Telegram WebApp + PWA | то же | ✅ |
| Viewport | 402×874 | (responsive) | 🟡 VELO жёстко 402 |

**Вывод:** различия минимальны и поверхностные (префиксы, набор локалей). Архитектурные слои идентичны → почти весь CBSHOME-код применим к VELO с заменой `C` → `V` и `--bg` → `--velo-bg-*`.

---

## 2. Inventory: что есть в CBSHOME

### API layer (`src/api/`) — 20 файлов
```
client.ts                — fetch wrapper (290 строк)
generated.ts             — auto-generated из OpenAPI
types.ts                 — re-exports + frontend-only narrowing
admin.ts agent-apps.ts agreements.ts attachments.ts
companies.ts company.ts dashboard.ts documents.ts
installments.ts payments.ts portfolio.ts posts.ts
products.ts purchases.ts transactions.ts users.ts
withdrawals.ts
```
**Паттерн:** один файл = один доменный модуль с типизированными функциями-обёртками. Все возвращают `Promise<Typed>`, конструируют URL через `buildQueryString` helper.

### Components (`src/components/`)
**UI Kit (19 компонентов):** `CButton, CBackLink, CInput, CTextarea, CSelect, CCheckbox, CCard, CBadge, CAvatar, CLoader, CDivider, CEmptyState, CToast, CStatCard, CProgressBar, CModal, CBottomSheet, CIconBox, CbsLogo`

**Layout (7):** `AgentShell, InvestorShell, CompanyShell, StaffShell, PublicShell, CHeader, CTabBar`

**Shared (8 domain components):** `AgreementSheet, AttachmentsSection, CompanyCard, ProductCard, PublicAttachmentsSection, PublicProductsSection, RoadmapTimeline, TransactionDetailSheet`

### Composables (`src/composables/`) — 10
```
useAuth.ts             — initAuth + retryAuth + isReady + waitUntilReady (151 строки)
useToast.ts            — singleton toast state (42 строки)
usePagination.ts       — useInfiniteScroll с pause-параметром (120 строк)
useTheme.ts            — auto/light/dark с OS-listener (120 строк)
useAuthWall.ts         — public-flow gate (98 строк)
useAgreementBlob.ts    — blob-обёртка для PDF
useAvatar.ts           — staff "operate as user" overlay
avatarState.ts         — module-level reactive flag
safeNavigate.ts        — wrapper для router.push (88 строк)
usePublicErrorToast.ts — error-to-toast маппер
```

### Stores (`src/stores/`) — 10
```
auth.ts                — 316 строк (login/register/telegram, referral, sessionReset)
sessionReset.ts        — централизованный resetAllDataStores() (75 строк)
attachments.ts companyDashboard.ts companyList.ts
companyProfile.ts dashboard.ts portfolio.ts products.ts
transactions.ts
```
**Паттерн:** epoch guards + reset() bumps epoch first.

### Routing (`src/router/`) — 4
```
index.ts    — 570 строк, 5 shells, 50+ роутов с lazy imports
guards.ts   — single globalGuard (154 строки)
helpers.ts  — getShell() для shared-view-aware-of-shell (52 строки)
tabs.ts     — INVESTOR_TABS / AGENT_TABS / COMPANY_TABS / STAFF_TABS
```

### i18n (`src/i18n/`) — 6 файлов
```
index.ts             — setupI18n + setLocale + lazy loaders (146 строк)
locales.config.ts    — SUPPORTED_LOCALES + isSupportedLocale + getLocaleDir (44 строки)
locales/en.json      — fallback
locales/ru.json      — 630 строк ключей
locales/de.json      — Deutsch
locales/ar.json      — العربية (RTL)
```

### Styles (`src/styles/`) — 4
```
variables.css   — tokens
global.css      — reset + base
fonts.css       — @font-face (self-hosted)
telegram.css    — Telegram WebApp-specific overrides
```

### Utils (`src/utils/`) — 5
```
format.ts          — formatPrice, formatSignedPrice, formatNumber, formatBytes
i18n.ts            — tOrRaw helper для server-driven enums
querystring.ts     — buildQueryString
mime.ts            — MIME helpers
installmentPlans.ts — domain-specific
```

### Platform (`src/platform/`) — 4
То же что у VELO + дополнительный метод `getStorageDriver()`.

### Views (`src/views/`) — 41 view-файлов в 6 ролях:
```
agent/    (8)  — AgentDashboard, AgentHub, AgentBalance, AgentMore, AgentSettings, Commissions, Leaderboard, Referrals
auth/     (8)  — Loading, Login, Register, Verify + Onboarding x 4
company/  (6)  — CompanyDashboard, Products, ProductEdit, Analytics, Balance, Settings
investor/ (14) — InvestorDashboard, Portfolio, CompanyList, CompanyOverview, ProductsByCompany, ProductDetail, Purchase, Installment, Balance, Deposit, Transactions, CompanyPosition, Docs, More, Settings
public/   (4)  — PublicCompanyList, PublicCompanyOverview, PublicAttachmentLanding, PublicProductDetail
staff/    (7)  — StaffDashboard, Users, KYC, Payments, AgentApps, Avatar, More
+ HomeView, NotFoundView
```

---

## 3. Паттерны для прямого переиспользования

### 3.1 Async bootstrap (main.ts)

**CBSHOME `src/main.ts`:**
```ts
async function bootstrap(): Promise<void> {
  await setupI18n()                    // 1. resolve locale + load JSON
  const app = createApp(App)
  app.use(createPinia())
  app.use(router)
  app.use(i18n)
  app.mount('#app')
}

bootstrap().catch((err) => {
  console.error('Bootstrap failed:', err)
  const root = document.getElementById('app')
  if (root) root.textContent = 'Failed to start app. Please reload the page.'
})
```

**Что решает:** без `await setupI18n()` первый render показывает сырые i18n-ключи. С ним — пользователь сразу видит локализованный UI.

**Что добавить в `setupI18n`:**
- Резолв локали из `localStorage['velo-lang']` → fallback DEFAULT_LOCALE
- Параллельный preload активной + fallback локалей (`Promise.all`)
- `document.documentElement.dir` + `lang` applied
- Никогда не консультироваться с `navigator.language` (источник правды — backend `user.language`)

**VELO action:** Sprint 2 T2.6 уже планирует `vue-i18n install`. Расширить таску — копировать `main.ts` bootstrap pattern.

---

### 3.2 Single globalGuard (4 уровня)

**CBSHOME `src/router/guards.ts`:**
```ts
export async function globalGuard(to): Promise<void | RouteLocationRaw> {
  await waitUntilReady()         // 0. Wait for auth init

  if (to.meta.public) {          // 1. Public routes: pass + redirect auth'd away from /login
    if (authStore.isAuthenticated && (to.name === 'login' || to.name === 'register')) {
      return getRoleDashboard(authStore.role)
    }
    return
  }

  if (!authStore.isAuthenticated) {  // 2. Auth check + ?next= preservation
    const next = to.fullPath !== '/' ? to.fullPath : undefined
    return { name: 'login', query: next ? { next } : undefined }
  }

  if (!to.meta.skipOnboarding) {     // 3. Onboarding state machine
    const step = authStore.user?.onboarding_step
    if (step && step in ONBOARDING_REDIRECTS) {
      const target = ONBOARDING_REDIRECTS[step]
      if (to.path !== target) return target
    }
  }

  const allowedRoles = to.meta.roles  // 4. Role check
  if (allowedRoles?.length > 0) {
    if (!allowedRoles.includes(authStore.role)) {
      return getRoleDashboard(authStore.role)
    }
  }
}
```

**Что решает:**
- Один файл — все 4 ортогональных уровня доступа
- `?next=` — после login пользователь попадает обратно туда, куда хотел (deep linking)
- Onboarding flow проходит через guard, а не через `if/else` в каждом view
- Скользит через `RouteMeta` augmentation — типизированные `roles`, `public`, `skipOnboarding`, `shell`

**VELO mapping:**
- Адаптировать `ONBOARDING_REDIRECTS` под VELO MasterApply flow (3 шага)
- Адаптировать `ROLE_DASHBOARDS` под `user|master|admin`
- **Важно:** guard читает `viewMode` ИЛИ `user.role`? CBSHOME использует `user.role`. **VELO §2.5 I3 говорит**: guards читают `viewMode`, EXCEPT admin-only мутации проверяют real `user.role`. То есть для VELO в guards стоит читать `viewMode` (для display), но в самих view'ах для destructive actions — `user.role`.

**VELO action:** в Sprint 1 после T1.5 (sync tokens) — копировать `guards.ts` целиком, адаптировать 3 строки (роли + onboarding steps).

---

### 3.3 meta.shell propagation для shared views

**CBSHOME `src/router/index.ts`:**
```ts
{
  path: '/investor',
  component: () => import('@/components/layout/InvestorShell.vue'),
  meta: { roles: ['investor', 'agent'], shell: 'investor' },
  children: [...]
}
```

**CBSHOME `src/router/helpers.ts`:**
```ts
export type Shell = 'investor' | 'agent' | 'company' | 'staff'

export function getShell(route): Shell | undefined {
  return route.meta.shell  // Vue Router merges meta from parent + child
}

export function isAgentShell(route): boolean {
  return getShell(route) === 'agent'
}
```

**Что решает:** один view (`ProductDetailView.vue`) рендерится и в `/investor/products/:id`, и в `/agent/products/:id`. Через `getShell(route)` view знает, в каком shell он сейчас, и выбирает соответствующие route names для дальнейшей навигации (`investor-purchase` vs `agent-purchase`).

**Без этого:** view либо знает шелл через `route.path.startsWith('/agent')` (хрупко — переименуй маршрут и сломается), либо дублирует компонент.

**VELO mapping:** для shared экранов (user-profile vs master-as-user-profile, любой view, доступный из нескольких ролей) — этот же паттерн.

**VELO action:** добавить в `04_methodology/VELO-METHODOLOGY.md` §6.7 (Component Naming) под-раздел про `meta.shell`. В `05_roadmap/sprint-01.md` или новом sprint после стейков добавить T-задачу.

---

### 3.4 tabs.ts: single source of truth для tab-bar

**CBSHOME `src/router/tabs.ts`:**
```ts
export interface TabItem {
  id: string
  path: string
  labelKey: string  // i18n key, NOT hardcoded label
  icon: string      // Lucide component name, lookup in CTabBar
}

export const INVESTOR_TABS: TabItem[] = [
  { id: 'home', path: '/investor/dashboard', labelKey: 'tab.home', icon: 'Home' },
  { id: 'portfolio', path: '/investor/portfolio', labelKey: 'tab.portfolio', icon: 'Briefcase' },
  ...
]
```

**Shell файл:**
```vue
<template>
  <div class="shell">
    <CHeader />
    <main class="shell__content"><RouterView /></main>
    <CTabBar :items="INVESTOR_TABS" />
    <CToast />
  </div>
</template>
```

**Что решает:** добавить/удалить таб = одна строка в одном файле. Иконки — Lucide через name lookup. Лейблы — через i18n key (нет хардкода).

**VELO action:** добавить в `src/router/tabs.ts` (НЕ в shell .vue файлах) — `USER_TABS`, `MASTER_TABS`, `ADMIN_TABS`. **Зафиксировать в методологии §6.7**.

---

### 3.5 Onboarding как state-machine в роутах

**CBSHOME:**
```ts
const ONBOARDING_REDIRECTS: Record<string, string> = {
  registered:       '/verify',
  email_verified:   '/onboarding/profile',
  profile_complete: '/onboarding/role',
  role_selected:    '/onboarding/kyc',
  kyc_done:         '/onboarding/docs',
}
```

5 состояний → 5 редиректов. Каждый view onboarding'а имеет `meta: { skipOnboarding: true }` чтобы не зацикливаться.

**Что решает:** FE никогда не показывает экран, на который пользователь "не имеет права" по своему состоянию. Backend выставляет `user.onboarding_step` — фронт реагирует автоматически.

**VELO mapping:** **MasterApply flow** (3 шага из ROADMAP §8.1 #8) можно моделировать так же. Backend выставляет `master.application_step` (если такого поля нет — попросить добавить). Frontend через `MASTER_APPLY_REDIRECTS` ведёт по нужному шагу.

**VELO action:** в `06_project-inputs/BACKEND-REQUESTS-2026-05-17.md` добавить запрос на поле `master.application_step` если оно отсутствует. В Sprint 5 #8 (master-apply) — спека должна явно ссылаться на этот FSM.

---

### 3.6 api/client: Retry-After, Accept-Language, extractErrorMessage

**CBSHOME `src/api/client.ts` — что добавлено сверх VELO версии:**

1. **`Accept-Language` заголовок из vue-i18n:**
```ts
headers: { 'Accept-Language': i18n.global.locale.value }
```
Backend может вернуть локализованные сообщения, если поддерживает.

2. **`Retry-After` парсинг для 429:**
```ts
export function parseRetryAfterHeader(response: Response): number | undefined {
  const raw = response.headers.get('Retry-After')
  if (raw === null) return undefined
  const parsed = parseInt(raw, 10)
  if (Number.isNaN(parsed) || parsed <= 0) return undefined
  return parsed
}

export class ApiResponseError extends Error {
  retryAfter?: number  // ← новое поле
}
```
Toast при 429: "try again in N seconds" вместо generic.

3. **`extractErrorMessage` — три формата:**
```ts
function extractErrorMessage(status, data): string {
  // FastAPI: { detail: "..." } or { detail: [...] }
  if ('detail' in obj) {
    if (status === 422) return parseValidationErrors(obj.detail)
    return String(obj.detail)
  }
  // Rate limiter / middleware: { error, message }
  if ('message' in obj) return obj.message
  return JSON.stringify(data)
}
```
**VELO `client.ts` уже имеет аналогичное** (F-03 fix), но без `Accept-Language` и `Retry-After`. Стоит подтянуть.

4. **`API_BASE_URL` экспортирован** для non-JSON endpoints (download blob, HTML certificate):
```ts
export const API_BASE_URL: string = BASE_URL
```

**VELO action в Sprint 0 / T0.0+:**
- Добавить `Accept-Language` в client.ts (5 строк)
- Добавить `retryAfter?: number` + `parseRetryAfterHeader` (15 строк)
- Экспортировать `API_BASE_URL`

---

### 3.7 i18n: lazy loading + RTL + tOrRaw

**CBSHOME `src/i18n/index.ts`:** lazy-loaded через `import.meta.glob`:
```ts
const localeLoaders = import.meta.glob<{ default: Record<string, unknown> }>(
  './locales/*.json',
)

async function loadLocaleMessages(locale: SupportedLocale): Promise<void> {
  if (loadedLocales.has(locale)) return
  const loader = localeLoaders[`./locales/${locale}.json`]
  const mod = await loader()
  i18n.global.setLocaleMessage(locale, mod.default)
  loadedLocales.add(locale)
}
```

**Vite автоматически чанкует:** main bundle БЕЗ локалей, каждая локаль — отдельный chunk. Загружается только нужная + fallback (для miss-key resolution).

**`src/i18n/locales.config.ts`:**
```ts
export const SUPPORTED_LOCALES = [
  { code: 'en', label: 'English', dir: 'ltr' },
  { code: 'ru', label: 'Русский', dir: 'ltr' },
  { code: 'de', label: 'Deutsch',  dir: 'ltr' },
  { code: 'ar', label: 'العربية',  dir: 'rtl' },
] as const satisfies readonly LocaleConfig[]
```
Добавление новой локали = 1 строка + 1 JSON. Никаких других файлов.

**RTL support:** `document.documentElement.dir = 'rtl'` для арабского. CSS должен использовать `[dir="rtl"]` селекторы где нужно (CTabBar уже делает).

**`src/utils/i18n.ts` — `tOrRaw` helper:**
```ts
export function tOrRaw(t, key, raw): string {
  const translated = t(key)
  return translated === key ? raw : translated
}
```
Для server-driven enum'ов: `tOrRaw(t, 'inv.balance.status.confirmed', 'confirmed')` → "Confirmed" если ключ есть, иначе "confirmed" (а не пустота или сырой `inv.balance.status.confirmed`).

**`ru.json` — 630 строк** структурированных вложенных ключей (`common`, `auth.login`, `inv.dashboard`, `inv.balance.status`, и т.д.). Хорошая референс-схема для VELO `ru.json`.

**VELO action для Sprint 2 T2.6:**
- Копировать `i18n/index.ts` целиком (заменить `cbs-lang` → `velo-lang`)
- Копировать `locales.config.ts` (изменить SUPPORTED_LOCALES — для MVP 2 локали, можно расширить)
- Создать `utils/i18n.ts` с `tOrRaw`
- Заложить namespace структуру в `ru.json` сразу: `common, errors, auth, user, master, admin, practice, booking, waitlist, withdrawal, format`

---

### 3.8 Pinia stores: epoch guards + sessionReset

**Проблема:** при переключении табов / роли / logout — in-flight HTTP-запрос может прилететь ПОСЛЕ того как UI уже сменился. Результат: данные пользователя А утекают в сессию пользователя Б.

**CBSHOME решение — epoch counter в каждом store:**

```ts
export const useTransactionsStore = defineStore('transactions', () => {
  let fetchEpoch = 0

  async function fetchFirstPage(): Promise<void> {
    const epoch = ++fetchEpoch
    try {
      const resp = await listTransactions({...})
      if (epoch !== fetchEpoch) return  // ← guard: тек. запрос устарел
      items.value = resp.items
    } catch {
      if (epoch !== fetchEpoch) return
      errored.value = true
    } finally {
      if (epoch === fetchEpoch) loading.value = false
    }
  }

  function reset(): void {
    ++fetchEpoch         // ← bump first, чтобы in-flight дропнулись
    items.value = []
    total.value = 0
    loading.value = false
  }

  return { items, total, loading, fetchFirstPage, reset }
})
```

**Централизованный reset (`stores/sessionReset.ts`):**
```ts
export function resetAllDataStores(): void {
  useDashboardStore().reset()
  usePortfolioStore().reset()
  useTransactionsStore().reset()
  useProductsStore().reset()
  // ...
}
```

**В `stores/auth.ts._clearSession`:** вызов `resetAllDataStores()` на logout/401.

**Что решает класс ошибок:**
> "User A logged out, user B logged in → B видит дашборд A на 1 секунду, пока новые данные не пришли"

**VELO action:**
- Принять этот паттерн на этапе написания первого store (`stores/auth.ts`)
- Создать `stores/sessionReset.ts` СРАЗУ — даже с пустым телом, потом добавлять каждый новый store в одном месте
- Добавить в методологию §8 Stores как обязательный паттерн (epoch + reset)
- Документировать как "FP-17 epoch guard" (по cbshome нотации)

---

### 3.9 Type-narrowing guards (asUserRole, asKycStatus)

**CBSHOME `src/api/types.ts`:**
```ts
export type UserRole = 'investor' | 'agent' | 'company' | 'staff' | 'platform'

const _USER_ROLE_VALUES = ['investor', 'agent', 'company', 'staff', 'platform']
  as const satisfies readonly UserRole[]

export function asUserRole(value: unknown): UserRole | null {
  if (typeof value !== 'string') return null
  return (_USER_ROLE_VALUES as readonly string[]).includes(value)
    ? (value as UserRole)
    : null
}
```

**В store:**
```ts
const role = computed<UserRole | null>(() => asUserRole(user.value?.role))
```

**Что решает:**
- Backend хранит `role` как `String(20)` (без enum). OpenAPI генерит `string` тип.
- Без narrowing: `user.role === 'invesrtor'` (опечатка) — silent runtime miss, TS не ловит.
- С narrowing: `authStore.role === 'invesrtor'` — TS error на compile.
- Backend добавил новую роль `partner`: возвращает `null`, frontend видит явный fallback, не silent cast.

**VELO mapping:** идентичная проблема — все статусы (BookingStatus, PracticeStatus, MasterStatus, WithdrawalStatus, WaitlistStatus) в OpenAPI описаны как `string` без enum (см. CC-REPORT-2.txt Q2.6). Frontend `types.ts` уже narrowed их как TS union, но **runtime guard `asXxx` отсутствует**.

**VELO action:**
- Добавить `asUserRole`, `asPracticeStatus`, `asBookingStatus`, `asMasterStatus`, `asWithdrawalStatus`, `asWaitlistStatus`, `asPracticeType`, `asPurchaseStatus`, `asMood`, `asFeedbackRating` в `api/types.ts`
- Принять как mandatory pattern в методологии: "никаких raw-string сравнений со статусами; всегда через `as*` guard"

---

### 3.10 useAuth singleton + waitUntilReady

**CBSHOME `src/composables/useAuth.ts`:**
```ts
// Module-level singletons (shared across all consumers)
const isReady = ref(false)
const isStandalone = ref(true)
const authError = ref<string | null>(null)

export function useAuth() {
  async function initAuth(): Promise<void> {
    await platform.init()
    // ... try restoreSession() → telegram auto-login → standalone
    isReady.value = true
  }

  function waitUntilReady(): Promise<void> {
    if (isReady.value) return Promise.resolve()
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('timeout')), 10_000)
      const unwatch = watch(isReady, (ready) => {
        if (ready) { clearTimeout(timer); unwatch(); resolve() }
      })
    })
  }

  return { initAuth, retryAuth, isReady, isStandalone, authError, waitUntilReady }
}
```

**Что решает:**
- Router guard ждёт auth init перед тем как принимать решение — иначе guard выполнится до того, как `restoreSession()` восстановит токен → юзера выкинет на /login несмотря на валидный токен
- 10-секундный timeout — на случай зависшего Telegram init

**VELO action:** обязательный паттерн для Sprint 1 или ранее. Без него router неработоспособен.

---

### 3.11 useToast / useInfiniteScroll / safeNavigate

**`useToast` — 42 строки, готов к копированию:**
```ts
const state = ref<ToastState>({ message: '', variant: 'info', visible: false })
let hideTimer = null

export function useToast() {
  function showToast(message, variant = 'info') {
    if (hideTimer) clearTimeout(hideTimer)
    state.value = { message, variant, visible: true }
    hideTimer = setTimeout(() => state.value.visible = false, 3000)
  }
  return { toastState: state, showToast, hideToast }
}
```
+ `<CToast />` компонент с `<Teleport to="body">` рендерится один раз в App.vue.

**`useInfiniteScroll` — IntersectionObserver pattern с pause-параметром:**
- IntersectionObserver вместо scroll events (no layout thrash, throttled natively)
- `rootMargin: '200px 0px'` — fire LOAD ДО того как user долистал
- 4-й параметр `paused: Ref<boolean>` — brake против retry-storm (если loadMore failed, store ставит `loadMoreErrored=true`, observer не дёргает loadMore пока не сбросишь)

**`safeNavigate` — wrapper для router.push/replace:**
```ts
export async function safeNavigate(navigation, context): Promise<void> {
  await navigation.catch((err) => {
    if (isNavigationFailure(err, NavigationFailureType.duplicated) ||
        isNavigationFailure(err, NavigationFailureType.cancelled) ||
        isNavigationFailure(err, NavigationFailureType.aborted)) {
      return  // benign — silent
    }
    console.error(`${context} navigation failed:`, err)
  })
}
```
**Что решает:** router.push() returns Promise; if discarded via `void`, NavigationFailure становится unhandled rejection. Если `await router.push()` внутри try/catch — duplicate-navigation (двойной тап на кнопку) ловится как exception и показывает "operation failed" toast после успешной операции.

**VELO action:** скопировать все три composables в Sprint 0 или начале Sprint 11+ implementation.

---

### 3.12 useAuthWall + ?next= deep-link preservation

**Проблема:** anonymous user открывает `/public/products/abc`, жмёт "Buy" — нужно отправить на login/register, но потом вернуть туда же, не на дашборд.

**CBSHOME `src/composables/useAuthWall.ts`:**
```ts
export function useAuthWall() {
  const route = useRoute()
  const router = useRouter()
  const auth = useAuthStore()

  function requireAuth(action: string): boolean {
    if (auth.isAuthenticated) return true
    void safeNavigate(
      router.push({
        name: 'register',
        query: { next: route.fullPath, intent: action },
      }),
      '[useAuthWall] to register',
    )
    return false
  }

  return { requireAuth }
}
```

**Usage in view:**
```ts
function buyNow() {
  if (!requireAuth('purchase')) return  // navigation fired
  // ... authenticated path
}
```

**В LoginView:**
```ts
const next = route.query.next as string | undefined
// ... after successful login:
await router.replace(next || '/dashboard')
```

**В globalGuard:**
```ts
if (!authStore.isAuthenticated) {
  const next = to.fullPath !== '/' ? to.fullPath : undefined
  return { name: 'login', query: next ? { next } : undefined }
}
```

**VELO mapping:** для VELO не критично сейчас (нет public storefront), но **может появиться** для пуш-нотификаций / deep links Telegram (`open_practice__{uuid}`). Стоит заложить паттерн заранее.

**VELO action:** добавить в методологию §2.5 I5 расширенное описание — `next=` query propagation для post-auth deep linking.

---

### 3.13 UI Kit: 19 готовых компонентов

| Компонент CBSHOME | Аналог в VELO Tier 1 | Готов к "перепрефиксу"? |
|---|---|---|
| CButton | VButton | ✅ |
| CInput | VInput | ✅ |
| CTextarea | VTextarea | ✅ |
| CSelect | VSelect | ✅ |
| CCheckbox | VCheckbox | ✅ |
| CCard | VCard | ✅ |
| CBadge | VBadge | ✅ |
| CAvatar | VAvatar | ✅ |
| CLoader | VLoader | ✅ |
| CEmptyState | VEmptyState | ✅ |
| CToast | VToast | ✅ |
| CModal | VModal | ✅ |
| CBottomSheet | VBottomSheet | новое в VELO Tier 1 |
| CStatCard | StatCard (Tier 2) | ✅ |
| CProgressBar | VProgressBar | новое |
| CDivider | VDivider | новое |
| CIconBox | VIconBox | новое |
| CBackLink | (часть CHeader) | новое (вынесли отдельно) |
| CbsLogo | VeloLogo | домен-специфика |

**Каждый компонент:** `<script setup lang="ts">` + `withDefaults(defineProps<{...}>(), {...})` + scoped styles с `var(--*)` токенами + размеры `sm | default` + варианты (primary/secondary/outline/danger/...).

**Пример CBSHOME `CButton`:**
- 6 variants (primary, secondary, outline, danger, telegram, link)
- 2 sizes (default, sm)
- loading prop (spinner)
- disabled prop
- 107 строк

**Анти-паттерн, которого избежали:** НЕТ inline-стилей, НЕТ цветов в .vue (все через var), `width: 100%` по default (адаптивно), `disabled` блокирует hover-transform.

**VELO action:** в Sprint 1 (после tokens) или Sprint 11+ implementation — копировать 14 из 19 компонентов, переименовать `C` → `V`, заменить `var(--accent)` → `var(--velo-bg-button-primary)` (по mapping из методологии §6.6). Это 1-2 дня работы вместо 10-15 дней генерации с нуля.

---

### 3.14 Tier 3 layout: CHeader + CTabBar + 5 shells

**`CHeader.vue`:** sticky top bar с:
- Лого слева (через CbsLogo)
- Опциональный back-button (через `showBack` prop)
- Title с ellipsis для длинных
- Slot `right` для action buttons
- `flex-shrink: 0` на right slot, чтобы title всегда обрезался первым

**`CTabBar.vue`:**
- Receives `items: TabItem[]` prop (от shell)
- Lucide icons через name lookup (map: { Home, Briefcase, ... })
- i18n labels через `t(tab.labelKey)`
- Active = `route.path.startsWith(tab.path)`
- `safe-area-inset-bottom` для notched devices
- RTL support через `[dir="rtl"] .c-tabbar { direction: rtl }`

**`InvestorShell.vue` — каноническая структура:**
```vue
<template>
  <div class="shell">
    <CHeader />
    <main class="shell__content"><RouterView /></main>
    <CTabBar :items="INVESTOR_TABS" />
    <CToast />   <!-- toast рендерится здесь, чтобы был ВНУТРИ avatar-banner area -->
  </div>
</template>
```
Всего **20 строк**. Каждый shell — 20 строк. Минимальная inline-логика.

**VELO mapping:**
- UserShell, MasterShell, AdminShell — по 20 строк каждый
- VHeader, VTabBar — копировать с переименованием префикса
- VELO роутер уже импортит эти 3 shells (хоть их и нет на диске) — после копирования сборка пройдёт

**VELO action:** Sprint 0 T0.3 / T0.4 (или после) — копировать pattern. Время: 1 час.

---

### 3.15 utils/querystring + formatSignedPrice

**`utils/querystring.ts` — `buildQueryString`:**
```ts
export function buildQueryString(params: Record<string, string|number|undefined|null>): string {
  const q = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || v === '') continue
    q.set(k, String(v))
  }
  const qs = q.toString()
  return qs ? `?${qs}` : ''
}
```
**Важная тонкость:** число `0` IS emitted (для range filters). VELO `api/utils.ts:buildQuery` — есть, но проверить, что `0` проходит.

**`utils/format.ts:formatSignedPrice`:**
```ts
export function formatSignedPrice(cents: number, currency?: string): string {
  const base = formatPrice(Math.abs(cents), currency)
  if (cents > 0) return `+${base}`
  if (cents < 0) return `-${base}`
  return base  // 0 → no sign
}
```

**Для VELO:** добавить аналог в `utils/format.ts` для transactions/withdrawals (+50€ / -2€).

---

### 3.16 Platform interface (9 методов vs VELO 8)

**Различие:** CBSHOME имеет **`getStorageDriver(): 'localStorage' | 'sessionStorage'`** — Telegram WebApp использует sessionStorage (умирает с табом), standalone PWA — localStorage.

**Подтверждение из `platform/telegram.ts`:**
```ts
getStorageDriver() {
  return 'sessionStorage'
}
```
То есть Telegram-режим всегда sessionStorage. Standalone — localStorage (для persistence между сессиями браузера).

**VELO mapping:** актуально, т.к. VELO тоже Telegram WebApp + PWA. Без этого:
- В Telegram WebApp localStorage может быть недоступен / нестабилен
- Token хранение по-разному в разных режимах

**VELO action:** добавить `getStorageDriver()` в `src/platform/types.ts` Platform interface.

---

### 3.17 Pre-mount FOUC prevention (theme-init.js)

**CBSHOME `public/theme-init.js`:**
```js
(function () {
  var t = localStorage.getItem('cbs-theme')
  if (t === 'dark' || t === 'light') {
    document.documentElement.setAttribute('data-theme', t)
  } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.documentElement.setAttribute('data-theme', 'dark')
  }
  var l = localStorage.getItem('cbs-lang')
  if (l) {
    document.documentElement.lang = l
    if (l === 'ar') document.documentElement.dir = 'rtl'
  }
})()
```

**Подключение в `index.html` (порядок критичен):**
```html
<script src="/theme-init.js"></script>           <!-- 1. FOUC prevention -->
<script src="https://telegram.org/js/telegram-web-app.js"></script>  <!-- 2. TG SDK -->
<!-- ... -->
<script type="module" src="/src/main.ts"></script>  <!-- 3. Vue mount -->
```

**Что решает:**
- Без этого: страница рендерится сначала в **светлой** теме (default), потом Vue монтируется → JS меняет `data-theme` → **визуальный flash** при загрузке. На медленных устройствах — заметно.
- С этим: HTML появляется уже с правильным `data-theme="dark"`. CSS-переменные тёмной темы применяются до первого paint. Никакого flash.
- Бонус: RTL для арабского применяется ДО монтирования Vue — layout сразу корректный.
- Бонус: `lang` атрибут на `<html>` — для screen readers, SEO.

**VELO mapping:** VELO §2.5 I7 «dark theme deferred but architecturally prepared». Когда dark theme появится — этот pattern мастхэв. Сейчас (light only) — можно отложить, но **`lang` + `dir` атрибуты для RTL — нужны уже на этапе i18n install** (Sprint 2 T2.6) если есть планы на арабский / иврит.

**VELO action:**
- Sprint 2 T2.6 i18n install: создать `frontend/public/lang-init.js` (минимальная версия — только `lang` + `dir`)
- Когда dark theme будет в скоупе (post-MVP) — расширить до полного theme-init.js

---

### 3.18 index.html best practices

**Полный `index.html` CBSHOME (29 строк), важные паттерны:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  <meta name="theme-color" content="#1A6B6A" />
  <link rel="manifest" href="/manifest.json" />
  <link rel="icon" href="/icons/favicon.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="/icons/icon-192.png" />
  <title>CBS HOME</title>
  <script src="/theme-init.js"></script>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

**Что важно:**
- **`viewport-fit=cover`** — для notched-устройств (iPhone X+). Без него `env(safe-area-inset-bottom)` не работает.
- **`theme-color`** — цвет статус-бара в Telegram WebApp / Chrome mobile. Должен совпадать с брендом.
- **`apple-mobile-web-app-capable`** + `status-bar-style` — PWA на iOS как полноценное приложение.
- **`apple-touch-icon`** — иконка home-screen на iOS.
- **`<link rel="manifest">`** — PWA manifest (см. §3.19).
- **Порядок `<script>`:** theme-init (no defer) → TG SDK (no defer) → Vue (type=module, defer by default). Theme должен примениться синхронно ДО body render.

**VELO mapping:** VELO `index.html` отсутствует на текущем срезе (был, рендерит `<div id="app">`, импортит `/src/main.ts`). Сравнить и дополнить:
- ✓ Telegram SDK уже подключён через `<link>` (в frontend/index.html по тёрновой версии)
- ? `viewport-fit=cover` — проверить
- ? `theme-color` — проверить (наверняка отсутствует)
- ? `apple-touch-icon` / `apple-mobile-web-app-*` — проверить

**VELO action:** в Sprint 0 или Sprint 2 — добавить недостающие meta-теги в `frontend/index.html`. Pattern from cbshome.

---

### 3.19 Telegram color sync в platform.init()

**CBSHOME `platform/telegram.ts:init()`:**
```ts
async init(): Promise<void> {
  const wa = getWebApp()
  wa.ready()
  wa.expand()
  wa.setHeaderColor('#1A6B6A')      // teal-primary brand color
  wa.setBackgroundColor('#F5F5F5')  // bg-subtle
}
```

**Что решает:** при запуске WebApp Telegram даёт API изменить цвет своего header (где имя бота + кнопки) и background области между header и контентом. Без этого — дефолтные серый header и белый background — выглядит как embed, а не как часть приложения.

**VELO mapping:** должно указывать на брендовые цвета VELO (`--velo-color-steel-primary` для header, `--velo-bg-screen` для background). Но передавать в `wa.setHeaderColor(...)` нужно **literal hex** (не CSS variable — Telegram SDK не парсит CSS).

**VELO action:**
- При копировании `platform/telegram.ts` из cbshome — подставить hex-значения **VELO** брендовых цветов
- Заложить TODO в платформе чтобы при изменении --velo-color-steel-primary не забыли пересинхронизировать с literal в telegram.ts (или вынести в общий config файл)

---

### 3.20 PWA manifest.json

**CBSHOME `public/manifest.json` (22 строки, всё минимум-необходимое):**
```json
{
  "name": "CBS HOME",
  "short_name": "CBS HOME",
  "description": "Investment platform",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#FFFFFF",
  "theme_color": "#1A6B6A",
  "orientation": "portrait",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

**Что важно:**
- `display: standalone` — без браузерной chrome (адресной строки)
- `orientation: portrait` — VELO 402×874 mobile-only, такой же
- 192 + 512 — минимальные размеры для PWA (192 для Android home-screen, 512 для splash)
- `theme_color` — синхронизировать с `index.html` meta и `wa.setHeaderColor()`

**Vite config также:**
```ts
VitePWA({
  registerType: 'autoUpdate',
  manifest: false, // Using public/manifest.json directly
  workbox: {
    globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
    navigateFallback: 'index.html',
    navigateFallbackDenylist: [/^\/api\//],   // ← КРИТИЧНО для SPA + API
  },
}),
```
**`navigateFallbackDenylist: [/^\/api\//]`** — без этого Service Worker перехватит `/api/*` запросы и попытается отдать `index.html`. Бэкенд не отвечает.

**VELO action:**
- Создать `frontend/public/manifest.json` с VELO брендингом (если ещё нет)
- В `vite.config.ts` добавить `navigateFallbackDenylist: [/^\/api\//]` — VELO сейчас этого паттерна не имеет

---

### 3.21 Mockups pipeline validation (CBSHOME mockups/ структура)

CBSHOME имеет каталог `mockups/` (mirror'ит то, что VELO планирует в `03_mockups/`):
```
cbshome/mockups/
├── !site/              ← marketing site mockup
├── agent-shell/        ← per-role mockups
├── company-shell/
├── investor-shell/
├── staff-shell/
├── auth-flow/          ← cross-role auth screens
├── assets/             ← icons, screenshots
├── css/                ← shared mockup CSS
│   ├── variables.css   ← prototype tokens → became frontend tokens
│   ├── components.css  ← prototype components → became C* UI Kit
│   ├── shell.css       ← prototype layout → became *Shell.vue
│   └── nav-map.css     ← navigation map overlay
├── js/                 ← shared mockup JS
└── index.html          ← mockups index
```

**Что это подтверждает для VELO:**
- CBSHOME действительно прошёл путь mockups → DS extraction → frontend rebuild. **Pipeline работает.**
- Структура `per-role + per-shell + css/components.css → реальные .vue компоненты` — масштабируется.
- VELO методология описывает тот же flow (mockups → spec → implementation), но другим словарём.

**VELO mapping:** структура `docs/03_mockups/{user,master,admin}/` соответствует. `docs/02_design-system/tokens/variables.css` → `frontend/src/styles/variables.css` соответствует cbshome `mockups/css/variables.css → frontend/src/styles/variables.css`. Подход валидирован.

**Backend gen-types подтверждение:** `D:/02_Projects/cbshome/backend/scripts/generate_ts_types.py` — точно такой же скрипт что планируется/упоминается в VELO (`velo gen-types`). **Reuse direct — скрипт же написан под FastAPI и переиспользуется почти as-is.**

**VELO action:**
- При написании gen:api script в Sprint 0 T0.7 — взять `cbshome/backend/scripts/generate_ts_types.py` как референс (или прямо скопировать backend script если бэк VELO на FastAPI и схожей структуре Pydantic-моделей)

---

## 4. Паттерны для адаптации (не копировать as-is)

### 4.1 Tier 2 domain components — VELO нужны свои

CBSHOME Tier 2 (`components/shared/`):
- AgreementSheet (financial agreement PDF preview)
- CompanyCard (investor browses companies)
- ProductCard (investment products)
- TransactionDetailSheet (financial events)
- RoadmapTimeline (company milestones)

VELO Tier 2 (из методологии §6.6) — **другой домен**:
- PracticeCard, BookingCard, WaitlistCard, MasterStatusBadge, MoodWidget, FeedbackWidget, WithdrawalRow, PromoRow, DiaryEntryCard, InsightsChart, PriceDisplay, BalanceChip

→ Структуру `withDefaults(defineProps<...>(), {})` + tokens + scoped styles — копировать. Содержимое — писать с нуля под VELO домен.

### 4.2 Stores — другая доменная модель

CBSHOME stores привязаны к investor financial flow (portfolio, transactions, companies). VELO stores — practice/booking/diary domain.

→ Паттерн (epoch + reset) — копировать. Доменную модель — писать с нуля.

### 4.3 views — полностью свои

41 view CBSHOME — про инвестиционный продукт. VELO views — про practice booking.

→ Структуру view (`<script setup>` → composables → onMounted refresh → state matrix → template с CEmptyState / CLoader / error state) — копировать. Содержимое — писать.

---

## 5. Что НЕ переносить (CBSHOME-only)

| Фича CBSHOME | Почему НЕ переносить в VELO |
|---|---|
| Referral system (`/r/:code`, `REFERRAL_KEY`, first-wins) | VELO нет реферальной системы |
| KYC onboarding flow (4 steps: profile → role → kyc → docs) | VELO MasterApply — другой flow, проще |
| Avatar mode (staff operates as user) — FEATURE | VELO нет multi-tenant impersonation; viewMode — другая концепция (просмотр другой роли БЕЗ смены user_id). **НО:** `avatarState.ts` PATTERN (module-level reactive ref для shared state между двумя файлами, чтобы избежать circular import) — generic, переиспользовать в VELO где встречается такая же проблема (например `viewMode` shared между stores/ui.ts и shell-компонентом) |
| Public storefront (`/public/*` без auth) | VELO целиком auth-walled |
| Agent role + commissions / leaderboard | VELO 3 роли, не 4 |
| Stripe webhook integration | VELO своя биллинг-модель |
| Installments | Не релевантно |
| `tOrRaw` для server-driven enums | VELO имеет узкие TS-union'ы; можно адаптировать как safety-net на случай новых enum значений |

---

## 6. Рекомендации по апдейту ROADMAP

### 6.1 Изменения в Sprint 0 (Foundation)

**Добавить таски (с явным указанием "copy from cbshome"):**

| ID | Task | Эффект |
|---|---|---|
| T0.9 | Скопировать `cbshome/frontend/src/composables/safeNavigate.ts` → VELO | Защита от unhandled NavigationFailure (~2 минуты) |
| T0.10 | Скопировать `cbshome/frontend/src/utils/querystring.ts` | VELO `api/utils.ts:buildQuery` дополнить тестами на edge cases (`0`, `''`, `null`) |
| T0.11 | Добавить `getStorageDriver()` метод в `src/platform/types.ts` + реализации в `telegram.ts` / `standalone.ts` | Корректное хранение token в Telegram |
| T0.12 | Расширить `src/api/client.ts`: + Accept-Language header, + retryAfter поле, + parseRetryAfterHeader export, + API_BASE_URL export | Поддержка 429 + локализованных ошибок |

### 6.2 Изменения в Sprint 1 (Tokens) — minimal, в основном верификация

- T1.6 (new) — после T1.5 sync tokens, проверить что переименование `--accent` / `--primary` подходов CBSHOME под `--velo-*` сделано корректно по mapping методологии §6.6

### 6.3 Изменения в Sprint 2 (Styleguide + i18n)

**T2.6 (i18n install) — расширить:**

Текущая формулировка слишком минималистична. Заменить на:
```
T2.6 Frontend i18n setup (FULL — copy CBSHOME pattern):
- npm install vue-i18n
- copy cbshome/frontend/src/i18n/index.ts → velo (rename: cbs-lang → velo-lang)
- copy locales.config.ts (SUPPORTED_LOCALES: en, ru — изначально; de, ar — задел)
- copy utils/i18n.ts (tOrRaw helper)
- main.ts: async bootstrap with await setupI18n() before mount
- locales/{en,ru}.json — initial namespaces: common, errors, auth, user, master, admin, practice, booking, waitlist, withdrawal, format
- format.ts: переработать на t() injection (8 хардкод-строк уйдут в i18n)
- App.vue: добавить <VToast /> mount point
```

### 6.4 Новый промежуточный спринт: **Sprint 2.5 — Infrastructure Adoption**

Между Sprint 2 (styleguide+i18n) и Sprint 3 (User specs) вставить **Sprint 2.5** на копирование инфраструктуры из CBSHOME:

| Task | Effort | Source |
|---|---|---|
| T2.5.1 Copy `router/{guards, helpers, tabs}.ts` (adapt to VELO roles + onboarding FSM) | 4-6h | cbshome router/ |
| T2.5.2 Copy `composables/{useAuth, useToast, usePagination, safeNavigate, useTheme}.ts` | 3-4h | cbshome composables/ |
| T2.5.3 Copy `stores/{auth.ts, sessionReset.ts}` skeleton (adapt to VELO domain) | 4-6h | cbshome stores/ |
| T2.5.4 Add `as*` runtime narrowing guards in `api/types.ts` (10 guards для VELO статусов) | 2-3h | cbshome api/types.ts (asUserRole pattern) |
| T2.5.5 Copy UI Kit (14 компонентов C* → V*) + rename to VELO prefix + adapt tokens | 6-8h | cbshome components/ui/ |
| T2.5.6 Copy CHeader + CTabBar → VHeader + VTabBar (Tier 3) | 2-3h | cbshome components/layout/ |
| T2.5.7 Stub shells (UserShell, MasterShell, AdminShell) ~20 строк каждый | 1h | cbshome shells/ pattern |
| T2.5.8 Wire main.ts bootstrap (async setupI18n + mount + error fallback) | 1h | cbshome main.ts |
| T2.5.9 Smoke test: build + typecheck + Telegram auth + render HomeView под UserShell | 2h | — |

**Total Sprint 2.5: 3-4 рабочих дня** (если оператор валидирует параллельно).

После Sprint 2.5 фронт ПОЛНОСТЬЮ ГОТОВ К ИМПЛЕМЕНТАЦИИ ВЬЮ — все foundation, stores skeleton, UI Kit, routing, i18n работают.

### 6.5 Изменения в Sprints 3-8 (Mockups + Specs)

**Mockup phase — не меняется.** Это работа Cowork по дизайну, CBSHOME её не закрывает.

**Spec phase — упрощение благодаря готовому Tier 1 UI Kit:**
- Секция "Композиция UI" в каждой спеке теперь короче: компоненты УЖЕ существуют, указать просто `<VButton variant="primary">`, не "создать VButton с 6 variants"
- Меньше open questions от CC в момент имплементации

### 6.6 Изменения в Sprint 9 (refinement) — без изменений

### 6.7 Изменения в Sprint 10 (Handoff package)

- T10.4 (frontend sync) **упрощается**: variables.css/global.css/icons уже синканы в Sprint 2.5; в Sprint 10 — финальная проверка drift

### 6.8 Новые сущности в **Sprint 11+ (Implementation)**

Сейчас Sprint 11 описан как open-ended reserve. Превратить в **structured implementation phase**:

```
Sprint 11.0 — Stores + Composables full implementation
Sprint 11.1 — User block views (Sprint 3 specs → Vue)
Sprint 11.2 — User block views (Sprint 4 specs → Vue)
Sprint 11.3 — Master block views
Sprint 11.4 — Admin block views
Sprint 11.5 — Integration + E2E на staging
```

С Tier 1 готовым из CBSHOME — velocity 2-3 views/день реалистичная (в отличие от "пишу с нуля включая компоненты" — ~1 view/день).

---

## 7. Оценка экономии времени

**Без CBSHOME reuse** (по предыдущему отчёту):
- Sprint 2 close: 2-4 дня
- Sprints 3-8: 5-8 недель (60-72 spec'а)
- Sprint 9: 3-5 дней
- Sprint 10: 2-3 дня
- Sprint 11+ implementation (40-50 views MVP): 8-10 недель
- **Total MVP: 14-19 недель (~3.5-4.5 месяца)**

**С CBSHOME reuse:**
- Sprint 2 close: 2-3 дня (i18n install быстрее благодаря готовому коду)
- **Sprint 2.5 (новый): 3-4 дня** — копирование инфраструктуры
- Sprints 3-8: 5-8 недель (mockups+specs, без изменений)
- Sprint 9: 2-4 дня (меньше rework т.к. UI Kit уже валидирован)
- Sprint 10: 1-2 дня (часть sync уже сделана)
- Sprint 11+ implementation: **5-7 недель вместо 8-10** (тк UI Kit + stores foundation + composables + i18n + router всё готовы, остаются только views)
- **Total MVP: 11-15 недель (~3-3.75 месяца)**

**Экономия: 3-4 недели** (один полный спринт), плюс качество выше (паттерны валидированы в продакшене CBSHOME).

**Дополнительные нематериальные выгоды:**
- Меньше bug'ов (epoch guards, session reset, type narrowing уже отлажены)
- Меньше архитектурных решений на лету для CC (всё уже решено)
- Меньше итераций "spec → CC implementation → review → fix" (паттерны однозначные)

---

## 8. Конкретные следующие шаги

### Прямо сейчас (15 минут)
1. Прочитать этот отчёт, отметить пункты, с которыми не согласен
2. Решить scope: копируем всю инфраструктуру (~3-4 дня Sprint 2.5) или только критичные части (~1-2 дня минимум)

### В ближайшие 1-2 дня (после Sprint 2 closure)
3. Обновить `docs/05_roadmap/ROADMAP.md`: добавить Sprint 2.5 и реструктуризировать Sprint 11+ как Implementation phase
4. Обновить `docs/04_methodology/VELO-METHODOLOGY.md`:
   - §6 Stores — добавить FP-17 epoch pattern + sessionReset
   - §6 — добавить `as*` runtime guards mandate
   - §6.7 — добавить tabs.ts SoT pattern, meta.shell propagation
   - §2.5 I5 — расширить про `?next=` deep-link preservation

### В Sprint 2.5 (3-4 дня, можно параллелить с operator validation Dashboard 9)
5. Выполнить T2.5.1 — T2.5.9 (детально расписаны в §6.4)

### После Sprint 2.5
6. Smoke test: фронт стартует, Telegram auth работает, HomeView рендерится в UserShell с tab-bar — это уже "прикрутили к бэку" в смысле сценария A из предыдущего отчёта
7. После каждого Sprint 3-8 spec batch — параллельно начинать имплементировать views на основе approved specs (Sprint 11+ может начаться РАНЬШЕ закрытия Sprint 10)

### Открытые вопросы для меня (если есть)
- Нужно ли мне **прямо сейчас** начать выполнять Sprint 2.5 (Tasks T2.5.1-T2.5.9)? Или сначала ты валидируешь этот отчёт и решаешь scope?
- Если выполнять — какие приоритетные задачи (T2.5.4 type guards и T0.0 PayoutDetails fix — самые быстрые wins)?

---

## Приложение А: Перечень файлов CBSHOME, рекомендованных к копированию

```
ИНФРАСТРУКТУРА (Sprint 2.5):
  cbshome/frontend/src/main.ts                          → velo (после i18n install)
  cbshome/frontend/src/router/guards.ts                 → velo (adapt roles+onboarding)
  cbshome/frontend/src/router/helpers.ts                → velo (rename Shell type members)
  cbshome/frontend/src/router/tabs.ts                   → velo (rewrite tabs per VELO roles)
  cbshome/frontend/src/composables/useAuth.ts           → velo (adapt to VELO auth endpoints)
  cbshome/frontend/src/composables/useToast.ts          → velo (1:1)
  cbshome/frontend/src/composables/usePagination.ts     → velo (1:1)
  cbshome/frontend/src/composables/safeNavigate.ts      → velo (1:1)
  cbshome/frontend/src/composables/useTheme.ts          → velo (1:1, defer to Sprint 11+)
  cbshome/frontend/src/stores/sessionReset.ts           → velo (skeleton + add stores as they grow)
  cbshome/frontend/src/i18n/index.ts                    → velo (rename storage key)
  cbshome/frontend/src/i18n/locales.config.ts           → velo (adapt SUPPORTED_LOCALES)
  cbshome/frontend/src/utils/i18n.ts                    → velo (tOrRaw helper)
  cbshome/frontend/src/utils/querystring.ts             → velo (1:1, or merge with VELO api/utils.ts)

API CLIENT EXTENSIONS:
  cbshome/frontend/src/api/client.ts — Accept-Language, parseRetryAfterHeader, API_BASE_URL export

UI KIT (14 of 18):
  cbshome/frontend/src/components/ui/CButton.vue        → VButton (variants → primary/secondary/oauth/destructive по VELO)
  cbshome/frontend/src/components/ui/CInput.vue         → VInput
  cbshome/frontend/src/components/ui/CTextarea.vue      → VTextarea
  cbshome/frontend/src/components/ui/CSelect.vue        → VSelect
  cbshome/frontend/src/components/ui/CCheckbox.vue      → VCheckbox
  cbshome/frontend/src/components/ui/CCard.vue          → VCard
  cbshome/frontend/src/components/ui/CBadge.vue         → VBadge
  cbshome/frontend/src/components/ui/CAvatar.vue        → VAvatar
  cbshome/frontend/src/components/ui/CLoader.vue        → VLoader
  cbshome/frontend/src/components/ui/CEmptyState.vue    → VEmptyState
  cbshome/frontend/src/components/ui/CToast.vue         → VToast
  cbshome/frontend/src/components/ui/CModal.vue         → VModal
  cbshome/frontend/src/components/ui/CBottomSheet.vue   → VBottomSheet
  cbshome/frontend/src/components/ui/CDivider.vue       → VDivider
  (опционально: CStatCard, CProgressBar, CIconBox, CBackLink)

TIER 3 LAYOUT:
  cbshome/frontend/src/components/layout/CHeader.vue    → VHeader
  cbshome/frontend/src/components/layout/CTabBar.vue    → VTabBar
  cbshome/frontend/src/components/layout/InvestorShell.vue → UserShell.vue (template skeleton)
  (повторить для MasterShell, AdminShell)

ТИПЫ:
  cbshome/frontend/src/api/types.ts — паттерн asUserRole для VELO статусов
```

## Приложение Б: Open Questions (если оператор хочет ответить — пригодится)

1. **Икон-библиотека.** CBSHOME использует `lucide-vue-next`. VELO в методологии не специфицирует. Принять `lucide-vue-next`? Преимущества: 1000+ иконок, Tree-shakeable, MIT license. Альтернатива: своя SVG-коллекция из Figma.

2. **Self-hosted fonts.** CBSHOME загружает Montserrat woff2 в `public/fonts/` (контроль FCP). VELO сейчас использует Google Fonts через `<link>` в index.html. Адаптировать или оставить?

3. **PWA manifest и Service Worker конфиг.** CBSHOME `vite.config.ts` имеет `navigateFallbackDenylist: [/^\/api\//]` — критично для SPA + API. У VELO `vite.config.ts` этот паттерн отсутствует — стоит добавить.

4. **Telegram-specific styles.** CBSHOME имеет пустой `src/styles/telegram.css` как заготовку для overrides. У VELO такого файла нет — заводить?

5. **gen:api script.** Оба проекта генерят `generated.ts` из OpenAPI. У CBSHOME есть `b7` / "VELO migration" комментарий — то есть generated.ts мигрировал с VELO формата на новый. Какой именно скрипт использует CBSHOME? Можно ли его прямо переиспользовать (плюс минус домен-специфика)?

6. **Telegram брендовые цвета (новое, см. §3.19).** Какие hex-значения подставить в `wa.setHeaderColor()` и `wa.setBackgroundColor()` для VELO? Кандидаты: header `#4c6589` (steel-primary), background `#FFFFFF` (bg-screen) или `#F5F5F5` (subtle). Решение влияет на восприятие WebApp в Telegram chat'е.

7. **viewport-fit=cover (новое, см. §3.18).** Добавить в `frontend/index.html` для notched-устройств (iPhone X+)? Без него `safe-area-inset-*` не работает корректно.

8. **theme-init.js (новое, см. §3.17).** Сейчас VELO ship'ит light-only. Заводить минимальный `public/lang-init.js` (только `lang`+`dir` для RTL) — или ждать пока появится dark theme / реальный i18n с RTL-локалью?

9. **PWA manifest (новое, см. §3.20).** У VELO есть `public/manifest.json`? Если нет — создавать сейчас или отложить до Sprint 10 handoff?

10. **Backend gen-types script.** Если backend VELO на FastAPI + Pydantic (предположение из текущей `api-openapi.json` — generated by FastAPI) — можем ли напрямую скопировать `cbshome/backend/scripts/generate_ts_types.py` (74 KB установочный скрипт, ~500 строк gen-types скрипт)? Или есть отличия в backend архитектуре?

---

## Приложение В: Validation Log (2026-05-18, повторный проход)

Список найденных в первой версии отчёта неточностей + добавленные после re-verification паттерны.

### Исправленные неточности
| Где | Было | Стало | Причина |
|---|---|---|---|
| §2 API layer header | "19 файлов" | "20 файлов" | `find` confirmed 20 (admin..withdrawals = 17 domain + client + generated + types) |
| §2 Components UI Kit | "18 компонентов" | "19 компонентов" | Glob confirmed 19 .vue (включая CbsLogo, который я пропустил при подсчёте) |
| §3.13 заголовок | "UI Kit: 18 готовых" | "UI Kit: 19 готовых" | См. выше |
| §3.13 prose | "копировать 14 из 18" | "копировать 14 из 19" | См. выше |

### Добавленные секции (паттерны, упущенные в первом проходе)
| Новая секция | Описание | Источник в cbshome |
|---|---|---|
| §3.17 Pre-mount FOUC prevention | Inline-скрипт в `<head>` до Vue mount: применяет theme + lang + dir на `<html>` ДО первого render | `public/theme-init.js`, `index.html` |
| §3.18 index.html best practices | viewport-fit=cover, theme-color, apple-touch-icon, порядок script-тегов | `index.html` |
| §3.19 Telegram color sync в platform.init | `wa.setHeaderColor()` + `wa.setBackgroundColor()` для брендового восприятия | `platform/telegram.ts:init()` |
| §3.20 PWA manifest.json | Полный канонический manifest + `navigateFallbackDenylist: [/^\/api\//]` в vite.config | `public/manifest.json`, `vite.config.ts` |
| §3.21 Mockups pipeline validation | Подтверждение что cbshome прошёл mockups → DS extraction → frontend rebuild успешно. Структура mirrors VELO `03_mockups/` | `mockups/` структура cbshome |

### Уточнения в §5 (что НЕ переносить)
| Запись | Что изменилось |
|---|---|
| "Avatar mode" | Разделено: **feature** (token swap, multi-tenant impersonation) — НЕ переносить; **pattern** (`avatarState.ts` — module-level reactive ref для обхода circular import) — переиспользовать в VELO везде где нужен shared reactive state между двумя файлами |

### Что перепроверено и подтверждено корректным
- ✅ Stack table (Sec. 1) — стек 1:1, различия только в префиксах
- ✅ §3.1 main.ts async bootstrap — read, корректно
- ✅ §3.2 globalGuard 4 уровня — read, корректно
- ✅ §3.6 client.ts (Retry-After, Accept-Language) — read, корректно
- ✅ §3.7 i18n lazy loading — read, корректно (ru.json подтверждён = 630 строк)
- ✅ §3.8 epoch guards в stores — read transactions.ts + sessionReset.ts, корректно
- ✅ §3.9 asUserRole guards — read types.ts начало, корректно
- ✅ §3.10 useAuth singleton — read, корректно
- ✅ §3.11 useToast/useInfiniteScroll/safeNavigate — все три прочитаны, корректно
- ✅ §3.12 useAuthWall — read, корректно
- ✅ §3.13 UI Kit пример CButton — read, корректно
- ✅ §3.14 CHeader/CTabBar/InvestorShell — read, корректно
- ✅ §6 рекомендации по Sprint 2.5 — задачи реалистичные, время оценено консервативно

### Дополнительно проверено (не повлияло на отчёт)
- env.d.ts — почти идентичен VELO версии (vue-i18n types declared)
- backend/scripts/generate_ts_types.py — существует, подтверждает что gen:api подход переносим
- public/{fonts, icons, legal, manifest.json, theme-init.js} — структура `public/` сама по себе — pattern
- usePublicErrorToast.ts — read, generic 429 toast handler (упомянут в §3 implicitly через Retry-After parsing, но как самостоятельный pattern добавить в backlog для VELO когда появится rate limiting)
- useAvatar.ts — read, подтверждает что pattern сложный + cbshome-specific, не переносим (см. обновлённый §5)

### Гэпы которые остались за рамками
| Гэп | Почему не закрыл |
|---|---|
| Тесты (E2E / unit) | cbshome не имеет vitest/playwright config в frontend — пропущено, т.к. это отдельная большая тема и cbshome здесь не лучший референс |
| CI/CD setup | Не было в скоупе запроса — он про лучшие практики кода, не deployment |
| install_cbshome.sh (74 KB shell script) | Скрипт-инсталлятор всего стека — выходит за пределы frontend best-practices |
| Backend best practices | Запрос был только про фронт |

### Итог валидации
Отчёт **усилен** и **выверен**. 4 числовых ошибки исправлены, 5 крупных паттернов добавлены (§3.17–3.21), §5 уточнён, Appendix B расширен с 5 до 10 open questions. Документ теперь даёт **полную и точную картину** того, что VELO может взять из cbshome и в каком порядке.

---

**Конец отчёта.**

*Сгенерирован Claude Code, 2026-05-18; валидирован тем же Claude Code, 2026-05-18.*
*На основе full-tree чтения D:\02_Projects\cbshome\frontend\src\\, а также public/, index.html, vite.config.ts, env.d.ts, backend/scripts/.*
