# VELO Frontend — Architecture Guide for CC

> This document is the **single source of truth** for Claude Code (CC) when generating
> views, components, stores, composables, and API modules.
> Read it fully before touching any file.
>
> Backlog of screens, sprint plan, and endpoint mapping live in
> `VELO-Frontend-TZ-Final.md` (in repo root).

---

## 1. Stack

| Layer | Technology |
|-------|-----------|
| Framework | Vue 3 + Composition API (`<script setup lang="ts">`) |
| Language | TypeScript 5.x strict mode |
| Build | Vite |
| Router | Vue Router 4.x |
| State | Pinia |
| HTTP | Fetch wrapper (`src/api/client.ts`) — never use raw `fetch()` |
| Styles | Custom CSS + Design Tokens (`src/styles/variables.css`) |
| i18n | vue-i18n (ru primary, en) — all UI strings via `t('key')` from day 1 |
| Platform | Telegram WebApp (primary), PWA fallback |

---

## 2. Project Structure

```
frontend/src/
├── api/
│   ├── client.ts          -- Fetch wrapper + 401 handler (DO NOT EDIT)
│   ├── generated.ts       -- Auto-generated from backend OpenAPI (DO NOT EDIT)
│   ├── types.ts           -- Re-export from generated.ts + frontend-only types
│   ├── utils.ts           -- buildQuery() and shared helpers
│   ├── auth.ts            -- POST /auth/telegram, logout
│   ├── users.ts           -- GET/PATCH /users/me
│   ├── practices.ts       -- CRUD practices, finalize, attendance
│   ├── bookings.ts        -- Bookings, purchase, waitlist
│   ├── payments.ts        -- Topup
│   ├── masters.ts         -- Apply, profile, payout, withdrawals
│   └── admin.ts           -- Stats, verify, reports, consistency
│
├── components/
│   ├── ui/                -- Primitives (V-prefix). Import ONLY via barrel.
│   │   └── index.ts       -- Barrel export (add new components here)
│   ├── layout/            -- VHeader, VTabBar, MobileLayout, AdminLayout
│   └── shared/            -- Domain components: PracticeCard, BookingCard...
│
├── composables/
│   ├── useAuth.ts         -- Login/logout flow + waitUntilReady()
│   ├── useToast.ts        -- Toast notifications
│   ├── usePagination.ts   -- Pagination + infinite scroll
│   └── useForm.ts         -- Form validation
│
├── i18n/
│   ├── index.ts           -- createI18n() configuration
│   └── locales/
│       ├── ru.json        -- Russian (primary)
│       └── en.json        -- English
│
├── platform/              -- Telegram/standalone abstraction (DO NOT EDIT)
│   ├── index.ts           -- Auto-detect: telegram vs standalone
│   ├── telegram.ts        -- Real Telegram WebApp SDK
│   ├── standalone.ts      -- Browser stubs
│   └── types.ts           -- Platform interface
│
├── router/
│   ├── index.ts           -- Routes + beforeEach guard
│   └── guards.ts          -- roleRedirect, roleGuard, masterStatusGuard
│
├── stores/
│   ├── auth.ts            -- user, token, role, isAuthenticated
│   ├── practices.ts       -- list, filters, selected
│   ├── bookings.ts        -- my bookings
│   ├── balance.ts         -- balance_cents, operations
│   ├── master.ts          -- master profile, practices, finance
│   └── ui.ts              -- viewMode (role switching)
│
├── styles/
│   ├── variables.css      -- Design tokens (generated from Figma)
│   └── global.css         -- Reset, typography, Google Fonts
│
├── utils/
│   ├── format.ts          -- formatMoney, formatDate, formatDateShort
│   ├── currency.ts        -- eurStringToCents, centsToEurString
│   └── constants.ts       -- CHECKIN_WINDOW_H, FEEDBACK_WINDOW_H, etc.
│
└── views/
    ├── shells/            -- UserShell, MasterShell, AdminShell
    ├── auth/              -- LoginView, LoadingView, StandaloneStubView
    ├── user/              -- Dashboard, Calendar, Practice, Bookings...
    ├── master/            -- Dashboard, Practices, Analytics, Profile...
    └── admin/             -- Dashboard, Masters, Reports, Consistency...
```

---

## 3. Generation Stages

CC generates in this order. **Do not skip stages** — each stage depends on the previous.

### Stage 0 — Design Tokens (must be done first, before any component)
- Extract all CSS variables from Figma Design System frame
- Write to `src/styles/variables.css`
- This file is the **only source of colors, spacing, radius, typography**

### Stage 0.5 — i18n Setup (before any component or view)
- Create `src/i18n/index.ts` with `createI18n({ legacy: false, locale: 'ru', fallbackLocale: 'en' })`
- Create empty namespaces in `src/i18n/locales/ru.json` and `en.json`:
  `common`, `errors`, `auth`, `user`, `master`, `admin`, `practice`, `booking`
- Register in `main.ts`: `app.use(i18n)`
- From this point on, **every string in `.vue` or `.ts` goes through `t('key')`**.
  No Russian (or English) literals in templates, toasts, or error messages.

### Stage 1 — UI Kit (`src/components/ui/`)
- Generate each primitive from its Figma component frame
- After each component: add its export to `src/components/ui/index.ts`
- Components must use only `var(--velo-*)` tokens — no hardcoded values
- Every component gets a `size` prop where applicable

### Stage 2 — Layout Components (`src/components/layout/`)
- `VHeader.vue` — top bar with back button + action slot
- `VTabBar.vue` — bottom nav, configured via `items` prop
- `MobileLayout.vue` — header slot + scrollable content + VTabBar (user + master)
- `AdminLayout.vue` — same pattern, separate for admin

### Stage 3 — Shells (`src/views/shells/`)
- `UserShell.vue` — wraps all `/user/*` routes
- `MasterShell.vue` — wraps all `/master/*` routes
- `AdminShell.vue` — wraps all `/admin/*` routes
- Each shell sets up its Tab Bar configuration and exposes `<RouterView />`

### Stage 4 — API Modules (`src/api/`)
- Generate typed wrappers for each endpoint group
- Always use the `api` object from `client.ts` (`api.get`, `api.post`, `api.patch`, `api.delete`) — never raw `fetch()`
- Types come from `src/api/types.ts` (re-exports from `generated.ts`)

### Stage 5 — Stores (`src/stores/`)
- Generate Pinia stores with typed state + actions
- See store rules in §6 below
- `stores/auth.ts` must wire up the client on initialisation (see §6.12)

### Stage 6 — Composables (`src/composables/`)
- `useAuth.ts` — auth flow
- `useToast.ts` — toast notifications
- `usePagination.ts` — pagination + infinite scroll

### Stage 7 — Views (per shell, per sprint)
- One `.vue` file per screen in `src/views/{role}/`
- Sprint order: User Shell → Master Shell → Admin Shell
- See `VELO-Frontend-TZ-Final.md` for screen list and endpoint mapping

---

## 4. Three Roles — One App

Role is determined from `GET /api/v1/users/me` after auth.

| Role | Shell | Tab Bar |
|------|-------|---------|
| `user` | `UserShell` | Dashboard / Calendar / Diary / Profile |
| `master` | `MasterShell` | Dashboard / Practices / Analytics / Profile |
| `admin` | `AdminShell` | Dashboard / Masters / Moderation / Profile |

### Role Switching (viewMode)

Master and Admin can preview other role interfaces without DB role change.

- State: `viewMode: 'admin' | 'master' | 'user'` in `stores/ui.ts`
- Persisted in `sessionStorage` under key `velo_view_mode`
- Reset on logout
- Router guards read `viewMode`, not `user.role` directly
- **Exception:** admin-only API actions always check `user.role === 'admin'` (real role), ignoring viewMode

| Real role | Available switches |
|-----------|-------------------|
| `admin` | "View as master" + "View as user" |
| `master` | "View as user" |
| `user` | none |

---

## 5. Routing

```
/                           -> roleRedirect (-> /user/dashboard or /master/dashboard or /admin/dashboard)

-- User --
/user/dashboard             -> UserDashboardView
/user/calendar              -> CalendarView
/user/diary                 -> DiaryView
/user/profile               -> UserProfileView
/user/practices/:id         -> PracticeDetailView
/user/bookings              -> MyBookingsView
/user/bookings/:id          -> BookingDetailView
/user/topup                 -> TopupView

-- Master --
/master/dashboard           -> MasterDashboardView
/master/practices           -> MasterPracticesView
/master/practices/new       -> CreatePracticeView
/master/practices/:id       -> EditPracticeView
/master/practices/:id/attendance -> AttendanceView
/master/profile             -> MasterProfileView
/master/finance             -> MasterFinanceView
/master/apply               -> MasterApplyView
/master/pending             -> MasterPendingView

-- Admin --
/admin/dashboard            -> AdminDashboardView
/admin/masters              -> AdminMastersView
/admin/masters/:id          -> AdminMasterReviewView
/admin/reports              -> AdminReportsView
/admin/consistency          -> AdminConsistencyView
```

Guards:
- `authGuard` — unauthenticated -> `/loading`
- `roleGuard('master')` — not master/admin -> `/user/dashboard`
- `roleGuard('admin')` — not admin -> `/user/dashboard`
- All guards read `viewMode` from `stores/ui.ts`, not `user.role`

---

## 6. Code Rules

### 6.1 Components

```typescript
// -- Always use Composition API with script setup --
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// -- Import UI components ONLY from barrel --
import { VButton, VInput, VCard } from '@/components/ui'

// -- Props with TypeScript interface --
const props = defineProps<{
  title: string
  loading?: boolean
}>()
</script>
```

### 6.2 Styles

```css
/* -- Always use design tokens, never hardcode values -- */

/* FORBIDDEN */
color: #4c6589;
padding: 16px;
border-radius: 15px;

/* CORRECT */
color: var(--velo-text-primary);
padding: var(--space-4);
border-radius: var(--radius-md);
```

CSS class naming: BEM — `.practice-card__title`, `.practice-card--active`.
All styles in `<style scoped>` inside the `.vue` file.

### 6.3 API Calls

```typescript
// FORBIDDEN — raw fetch, hardcoded URL
const res = await fetch('https://api.example.com/practices')

// CORRECT — typed wrapper from api/ module
import { getPractices } from '@/api/practices'
const data = await getPractices({ page: 1, limit: 20 })
```

### 6.4 Error Handling + Loading State

Every async action must have loading + error handling. No exceptions.

```typescript
const loading = ref(false)

async function loadData(): Promise<void> {
  if (loading.value) return  // prevent double-click
  loading.value = true
  try {
    data.value = await getPractices()
  } catch {
    toast.error(t('errors.loadFailed'))
  } finally {
    loading.value = false
  }
}
```

### 6.5 Pinia Stores

```typescript
// FORBIDDEN — mutate store directly from component
authStore.user = response.data

// CORRECT — through action
authStore.setUser(response.data)
```

When to use store vs local ref:
- **Store:** data shared between multiple views (user, practices list, balance)
- **Local ref:** data used only within one view (form state, modal open/close)

### 6.6 Money

```typescript
// FORBIDDEN — float precision trap
const cents = Math.round(parseFloat(input) * 100)
<span>{{ price / 100 }}€</span>

// CORRECT
import { eurStringToCents, centsToEurString } from '@/utils/currency'
import { formatMoney } from '@/utils/format'

const cents = eurStringToCents('14.57')       // '14.57' -> 1457
const display = centsToEurString(cents)        // 1457 -> '14.57'
const formatted = formatMoney(cents, 'EUR')    // -> '€14.57'
```

### 6.7 Platform Abstraction

```typescript
// FORBIDDEN — direct Telegram SDK call in component
window.Telegram.WebApp.HapticFeedback.impactOccurred('medium')

// CORRECT — through platform abstraction
import { platform } from '@/platform'
platform.hapticFeedback('medium')
```

### 6.8 TypeScript

```typescript
// FORBIDDEN
function handle(data: any) { ... }

// CORRECT — types from generated.ts via types.ts
import type { PracticeResponse } from '@/api/types'
function handle(data: PracticeResponse) { ... }
```

### 6.9 Token Storage

`token` is stored as a module-level variable in `api/client.ts`, **not in Pinia**.
This avoids circular dependency: `client -> store -> client`.
Do not move it to a store.

```typescript
// In api/client.ts — correct pattern:
let _token: string | null = null
export function setToken(t: string | null) { _token = t }

// Token is persisted in sessionStorage (not localStorage):
// Telegram WebApp closes the tab -> sessionStorage clears automatically.
sessionStorage.setItem('velo_token', token)
```

### 6.10 Environment Variables

```typescript
// FORBIDDEN
fetch('https://api.vel-app.com/api/v1/users/me')

// CORRECT
const BASE_URL = import.meta.env.VITE_API_BASE_URL
fetch(`${BASE_URL}/api/v1/users/me`)
```

### 6.11 i18n / Strings

**Every user-facing string goes through `t('key')`. No exceptions, no "fix later".**

```vue
<!-- FORBIDDEN — literal in template -->
<template>
  <button>Записаться</button>
  <h1>Мои бронирования</h1>
</template>

<!-- CORRECT -->
<template>
  <button>{{ t('practice.book') }}</button>
  <h1>{{ t('booking.myList.title') }}</h1>
</template>
```

```typescript
// FORBIDDEN — literal in toast / error / alert
toast.success('Бронирование создано')
toast.error('Не удалось загрузить')

// CORRECT
toast.success(t('booking.created'))
toast.error(t('errors.loadFailed'))
```

Key naming convention: `<namespace>.<scope>.<element>`, lowercase, dot-separated.
Namespaces are fixed (see Stage 0.5): `common`, `errors`, `auth`, `user`, `master`,
`admin`, `practice`, `booking`. Add new namespaces only if a whole new domain appears.

Setup in `<script setup>`:

```typescript
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
```

If a string needs a value, use interpolation, not concatenation:

```typescript
// FORBIDDEN
toast.error('Не хватает ' + amount + ' евро')

// CORRECT — locale file: "balance.shortBy": "Не хватает {amount} €"
toast.error(t('balance.shortBy', { amount }))
```

### 6.12 Auth Wiring (hidden but mandatory)

`api/client.ts` exposes two functions that `stores/auth.ts` **must** call.
Without this wiring, 401 responses won't clear the session and the token
won't be sent with requests.

```typescript
// src/stores/auth.ts
import { defineStore } from 'pinia'
import { setToken, setOnUnauthorized } from '@/api/client'
import { loginTelegram, logoutCall } from '@/api/auth'
import { getMe } from '@/api/users'
import type { UserResponse } from '@/api/types'

const TOKEN_STORAGE_KEY = 'velo_token'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as UserResponse | null,
    token: sessionStorage.getItem(TOKEN_STORAGE_KEY),
  }),

  getters: {
    isAuthenticated: (s) => !!s.token && !!s.user,
    role: (s) => s.user?.role ?? null,
  },

  actions: {
    // Call ONCE on app startup (from main.ts after pinia is installed).
    init(): void {
      // Wire 401 handler: client calls this when it gets a 401.
      setOnUnauthorized(() => this.clearSession())

      // Restore token from sessionStorage into the client.
      if (this.token) {
        setToken(this.token)
      }
    },

    async login(initData: string): Promise<void> {
      const { session_token, user } = await loginTelegram(initData)
      this.token = session_token
      this.user = user
      sessionStorage.setItem(TOKEN_STORAGE_KEY, session_token)
      setToken(session_token)
    },

    async refreshMe(): Promise<void> {
      this.user = await getMe()
    },

    async logout(): Promise<void> {
      try { await logoutCall() } catch { /* ignore */ }
      this.clearSession()
    },

    clearSession(): void {
      this.token = null
      this.user = null
      sessionStorage.removeItem(TOKEN_STORAGE_KEY)
      setToken(null)
    },
  },
})
```

In `main.ts`, call `init()` once after Pinia is installed and before any
view tries to use the API:

```typescript
import { useAuthStore } from '@/stores/auth'

app.use(createPinia())
app.use(router)
app.use(i18n)

useAuthStore().init()   // <-- wires client.ts callbacks + restores token

app.mount('#app')
```

---

## 7. View File Template

Every view file follows this structure:

```vue
<!--
  VELO Frontend -- [ViewName] ([role]/[screen-name])
  [One-line description of what this screen does]
-->

<template>
  <!-- markup here. All visible strings via {{ t('...') }} -->
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { VButton, VLoader } from '@/components/ui'
import { useToast } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'
import { getSomething } from '@/api/something'
import type { SomeResponse } from '@/api/types'

// -- Router + stores + i18n --
const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()
const { t } = useI18n()

// -- State --
const loading = ref(false)
const data = ref<SomeResponse | null>(null)

// -- Lifecycle --
onMounted(async () => {
  await loadData()
})

// -- Methods --
async function loadData(): Promise<void> {
  loading.value = true
  try {
    data.value = await getSomething()
  } catch {
    toast.error(t('errors.loadFailed'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* BEM naming, only var(--velo-*) tokens */
</style>
```

---

## 8. What CC Must NOT Do

- Import from `@/components/ui/VButton.vue` directly — always use barrel `@/components/ui`
- Use hardcoded colors, sizes, or spacing — always `var(--velo-*)`
- Use raw `fetch()` — always use wrappers from `src/api/`
- Use `any` type
- Call `window.Telegram.WebApp.*` directly — always use `platform.*`
- Hardcode `https://api.*` URLs — always `import.meta.env.VITE_API_BASE_URL`
- Mutate Pinia store fields directly from components — always through actions
- Do math on cents with floats — always use `currency.ts` utils
- Forget loading state on async actions
- Forget error handling (try/catch) on every API call
- Create new CSS variables — only use existing tokens from `variables.css`
- Write inline styles
- Hardcode user-facing strings in `.vue` or `.ts` — always `t('key')` via vue-i18n
- Store the auth token in Pinia — it lives as a module-level var in `client.ts`
- Skip the `useAuthStore().init()` call in `main.ts` — without it 401 won't clear session

---

## 9. Mock Strategy

Some features have no backend endpoint yet. Use this pattern:

```typescript
// Button with no endpoint -> toast stub (still goes through t())
async function sendMessage(): Promise<void> {
  toast.info(t('common.comingSoon'))
}
```

| Feature | Strategy |
|---------|---------|
| Email/OAuth login | Button -> toast `t('common.inDevelopment')` |
| Messaging / Chat | 3 fake conversations, send -> toast `t('common.comingSoon')` |
| Notification preferences | localStorage until endpoint |
| Promo codes | Not in first version |
| Waitlist | Not in first version |

---

**End of document.**
