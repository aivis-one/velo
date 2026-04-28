# security-audit — frontend/src — 2026-04-28

**Skill**: probekit-security-audit v1.1.0
**Target**: `frontend/src` (140 source files)
**Scope**: client-side security only — does NOT cover backend authz, infra, or runtime vulnerabilities. Assumes backend enforces real authorization on every API endpoint (bearer-token validation; per-endpoint role + ownership checks). Frontend issues here would either weaken UX-side hardening or leak data via the client itself.

**Stack context**: TypeScript 5.7 / Vue 3.5 / Pinia 2.3 / vue-router 4.5 / Vite 6.1, Telegram Mini App + PWA fallback (per `decisions.md` #013).

---

## Summary

| Section | Findings (🔴 / 🟡 / 🟢 / 💎) |
|---|---|
| Step 3 — OWASP Top 10 scan | 0 / 0 / 2 / 1 |
| Step 3.5 — Data flow tracing | 0 / 0 / 1 / 1 |
| Step 4 — Secret detection | 0 / 0 / 0 / 1 |
| Step 5 — Auth/AuthZ matrix | 0 / 1 / 1 / — |
| Step 6 — Insecure defaults | 0 / 0 / 0 / 1 |
| **TOTAL** | **0 🔴 / 1 🟡 / 4 🟢 / 4 💎** |

**Verdict**: client-side security is in good shape. Zero CRITICAL findings. The frontend takes the right architectural choices (bearer tokens in Authorization header, no v-html / no eval / no innerHTML, per-tab sessionStorage, allowlist on payment redirect, AbortController on every fetch). The single WARNING is around `roleGuard()` synchronicity — defensive against future architecture changes, not a current exploit.

**Stronger** than `code-audit` Section 4: deeper OWASP-by-category traversal, secret-pattern scan (15+ regex), data-flow tracing on session token + user PII.

---

## Step 3 — OWASP Top 10 Scan

### A01 — Broken Access Control

**Frontend angle**: client-side route guards (`router/guards.ts`) implement role-based redirects. Real authorization MUST be enforced server-side; client guards are UX hardening only.

#### 💎 DIAMOND — Layered guard architecture

`router/guards.ts` defines three composable guards with clear separation of concerns:
- `roleRedirect` — entry-point routing based on role + deep-link consumption
- `roleGuard(required)` — factory for role-based access (`master` allows master+admin per design; `admin` allows admin only)
- `masterStatusGuard` — verified-master gate on profile-status-sensitive routes

The architecture is clean. Client cannot prevent unauthorized access to data — but it consistently routes users away from screens they shouldn't see.

#### 🟢 SUGGESTION — `roleGuard` does not await initAuth

`router/guards.ts:85-102` — `roleGuard()` is synchronous and reads `auth.role` directly. If invoked before `initAuth()` completes (race), role could be null and users would be redirected to `/user/dashboard`. Currently safe because `App.vue` blocks RouterView via `isReady` and `router.beforeEach` awaits on first navigation, but the guard is fragile against future architecture changes.

Fix sketch:
```diff
  export function roleGuard(required: ...): NavigationGuardWithThis<undefined> {
-   return () => {
+   return async () => {
+     await waitUntilReady()
      const auth = useAuthStore()
      ...
```

Defensive change; ensures roleGuard remains correct independently of App.vue gate.

**Severity**: 🟢 SUGGESTION (no current exploit; hardens against regression).

### A02 — Cryptographic Failures

**No cryptography is performed in the frontend.** Auth tokens are issued by backend (after `init_data` validation per Telegram's HMAC scheme). Frontend stores the opaque bearer token and forwards it. No password-based auth on the client side; no client-side crypto operations.

`grep md5|sha1|MD5|SHA1|Math\.random` — 0 matches. No weak crypto. No `Math.random()` for security purposes.

#### 💎 DIAMOND — No client-side cryptography surface

The choice to delegate all crypto to the backend (Telegram initData verification) and use opaque bearer tokens client-side eliminates this entire OWASP category at the frontend.

### A03 — Injection (XSS, SQL, command, template)

#### 💎 DIAMOND — Zero XSS sinks

Confirmed across all 87 .vue + 42 .ts files:
- `grep 'v-html'` → **0 matches**
- `grep 'innerHTML'` → **0 matches**
- `grep 'eval\b\|new Function'` → **0 matches**
- No template-injection sinks (`document.write`, `outerHTML`, etc.)

Vue's default text interpolation (`{{ }}`) auto-escapes; no opt-out is used anywhere.

#### Confirms

- No SQL injection surface — frontend doesn't construct queries; only consumes typed REST endpoints.
- No command injection — no Node API access; no `child_process`, no `shelljs`, no shell-out paths.

### A04 — Insecure Design

`api/client.ts` provides:
- 15-second AbortController timeout on every request (`REQUEST_TIMEOUT_MS = 15_000`) — defends against hanging-fetch DoS-from-stuck-backend.
- 401 → `_clearSession()` callback — auto-logout on token revocation.
- In-flight GET deduplication (F-09) — prevents duplicate-fetch storms.

Frontend cannot enforce backend rate limiting; that is a backend concern.

No findings.

### A05 — Security Misconfiguration

Scan for:
- `DEBUG = True` / `debug: true` in non-test code → **0 matches**
- `verify=False` / `rejectUnauthorized: false` → **0 matches**
- `CORS=*` / `Access-Control-Allow-Origin: *` → **0 matches** (frontend doesn't set CORS)
- `ALLOWED_HOSTS = ['*']` → not applicable (frontend)

Vite's prod build strips dev-only patterns; `import.meta.env.DEV` gate at `api/client.ts:23` ensures the «VITE_API_BASE_URL not set» warning fires only in dev.

No findings.

### A06 — Vulnerable Components

Out of scope per protocol — defer to `probekit-dependency-audit`. `frontend/package.json` exists. No deeper analysis here.

### A07 — Identification & Authentication Failures

Frontend uses Telegram-issued initData for primary auth (`stores/auth.ts:51-69` `loginViaTelegram`) and session token via Bearer header. Token is stored in `sessionStorage` (per-tab, cleared on close — correct for TMA). 401 invalidates immediately via callback.

No password-based auth on frontend. No MFA hooks needed (Telegram handles upstream identity).

#### 🟢 SUGGESTION — No telemetry on auth failures

`stores/auth.ts:61-65, 81-83` — auth failures are silenced (NEW-8 justifies this for production normality of expired initData). Currently no Sentry/error-pipe hook; when one lands (S2+), restore lightweight `event=auth_failure_expected` log even for «expected» failures. Already noted in code-audit Section 3.

### A08 — Software and Data Integrity Failures

Frontend uses `response.json()` only — no `eval`, no `pickle`, no unsafe deserializer. Vue templates auto-escape.

CSRF: frontend uses bearer tokens in Authorization header (not cookies). `grep credentials:` in `fetch()` calls returns 0 — defaults to 'same-origin'. CSRF is **not applicable** to this auth model.

No findings.

### A09 — Security Logging and Monitoring Failures

`grep 'console\.(log|error|warn|debug|info).*token|console.*password|console.*secret'` → **0 matches**.

The 3 `console.warn`/`console.error` sites in the code (router timeout, client.ts dev warning, auth comment-only) do NOT log sensitive data.

No findings.

### A10 — Server-Side Request Forgery

Frontend doesn't make server-side requests (it's the client). All fetches go to one origin (`VITE_API_BASE_URL`). No URL is constructed from user input that could redirect to a third-party.

#### 💎 DIAMOND — Open-redirect protection on payment flow

`views/user/TopupView.vue:104-185` — the only place where `window.location.href` is set from a backend-supplied URL. Protected by:
- `ALLOWED_REDIRECT_PREFIXES` allowlist (Stripe checkout + the configured API origin)
- `isAllowedRedirectUrl(url)` check before redirect (line 170-172)
- User-visible error toast on rejection (line 183)

This is exactly the protection the OWASP A10 category warns about. Already 💎 in code-audit Section 4; restated here at the security-audit depth.

---

## Step 3.5 — Data Flow Tracing

### Sensitive data: session token

#### 💎 DIAMOND — Token flow is tightly bounded

```
Entry:   backend response { session_token: string } at /api/v1/auth/telegram
  ↓
Storage: stores/auth.ts:_setToken() → sessionStorage.setItem('velo_token', ...)
  ↓     (per-tab; cleared on tab close)
  ↓     api/client.ts:_token (module-private)
  ↓     setAuthToken() — exclusive setter
  ↓
Use:     api/client.ts:request() → headers['Authorization'] = `Bearer ${_token}`
  ↓     (TLS-protected transport assumed at fetch level)
  ↓
Exit:    backend ↓
  ↓
Logging: NEVER — confirmed via grep on console.* + JSON.stringify on token-related code paths.
Errors:  ApiResponseError(401, 'Session expired', 'unauthorized') — message is generic, no token content
Cleanup: 401 callback → _clearSession() → setAuthToken(null) + sessionStorage.removeItem
         logout() → same path + master store reset (W-1)
```

The token is never:
- written to `localStorage` (would persist beyond tab close)
- logged via console.*
- serialized to JSON for any purpose
- transmitted to a third-party origin (CORS would prevent it; bearer tokens don't auto-attach to fetches)
- exposed via `window.X` (single-module-private `_token` variable)

### Sensitive data: user PII (name, telegram_id, role, balance)

```
Entry:   backend response { user: UserResponse } at /api/v1/auth/telegram
  ↓
Storage: stores/auth.ts:_setUser() → user ref (Pinia reactive — in-memory only)
  ↓
Use:     stores/auth.ts:role computed (exposed read-only); component renders
Exit:    not transmitted out of the client
```

PII is in-memory only. On logout, `_clearSession()` nulls the user ref. No persistence.

#### 🟢 SUGGESTION — User object visible in Vue DevTools

Pinia stores are inspectable via Vue DevTools in development. In production builds, `import.meta.env.PROD` removes DevTools registration. Confirm `vite.config.ts` does not enable Pinia debugging in prod. Not a code-level vulnerability — a build-config note. Since no prod build was run during this audit, flagged as SUGGESTION pending build-config confirmation.

---

## Step 4 — Secret Detection

Scanned all source files for:
- AWS / GCP / Azure cloud keys (AKIA*, AIza*, GOCSPX-, Azure connection strings)
- Stripe (sk_live_*, sk_test_*, whsec_*)
- GitHub PAT (ghp_*, github_pat_*)
- OpenAI (sk-*)
- SendGrid (SG.*)
- Twilio (AC*, SK*)
- Private keys (`-----BEGIN RSA PRIVATE KEY-----` etc.)
- DB connection strings with embedded credentials
- Generic `password=`, `secret=`, `api_key=`, `access_token=` literal-string assignments

**Result: 0 matches across 140 source files.**

#### 💎 DIAMOND — Clean secret hygiene

The codebase relies on `import.meta.env.VITE_*` for runtime config:
- `VITE_API_BASE_URL` (api origin)
- `VITE_TELEGRAM_BOT_URL` (bot deep link)

Both are non-secrets (URLs are public). True secrets (Stripe keys, Telegram bot token, DB credentials) are correctly held only on the backend.

False-positive watch (would normally flag, ignored here as documented placeholders):
- `'https://t.me/velo_testbot'` — public test bot URL (already SUGGESTION-tier in code-audit Section 4)
- `'https://api.talentir.info'` — public production API URL

No real secrets detected.

---

## Step 5 — Auth/AuthZ Matrix (frontend-side)

| Surface | Auth required? | AuthZ check | Owner check | Issue |
|---|---|---|---|---|
| `App.vue` `isReady && !isAuthenticated` gate | yes (renders StandaloneStubView if not auth) | n/a (gate) | n/a | clean |
| `router/index.ts` beforeEach (`/user/dashboard`) | yes (waitUntilReady on first nav) | role check (master/admin → redirected to own dashboard unless uiMode=user) | n/a | clean |
| `roleRedirect` (`/`) | awaits ready | switch on role | n/a | clean |
| `roleGuard('admin')` on `/admin/*` | implicit (App.vue gate) | role==='admin' | n/a (no resource ID at route level) | clean — but synchronous (see SUGGESTION below) |
| `roleGuard('master')` on `/master/*` | implicit | role∈{master, admin} | n/a | clean — but synchronous |
| `masterStatusGuard` on practices/finance | yes | profile.status==='verified' | implicit (master's own profile) | clean |
| `applyGuard` on `/master/apply` | yes (waitUntilReady) | role!=='master' OR status!=='verified' | n/a | clean |

#### 🟡 WARNING — `roleGuard` is synchronous; doesn't await initAuth

Already detailed in A01 above. Single 🟡 finding for the entire skill.

#### 🟢 SUGGESTION — Owner check on `/master/practices/:id` etc. happens server-side only

Frontend route `/master/practices/:id` (edit practice) doesn't check whether the practice belongs to the current master before rendering the form. If the backend has an IDOR vulnerability, the master could load and edit another master's practice via direct URL. Currently safe because backend enforces `master_id == current_user.master_id` on `getPractice(id)`. Frontend defense-in-depth: the master store's `myPractices` list could be cross-checked, but this is overengineering when backend authz is correct.

**Severity**: 🟢 SUGGESTION (defense-in-depth, not a frontend bug).

---

## Step 6 — Insecure Defaults

Scanned for:
- `DEBUG = True` / `debug: true` → 0 matches
- `verify=False` / `rejectUnauthorized: false` → 0 matches
- `CORS *` / `origins: *` → 0 matches
- `Math.random()` for tokens → 0 matches (no token generation client-side)
- Weak crypto (MD5, SHA1) → 0 matches
- Insecure storage (localStorage for tokens) → 0 matches (uses sessionStorage)

#### 💎 DIAMOND — No insecure defaults

Production configuration discipline is consistent. The only env-driven behavior gates correctly on `import.meta.env.DEV` (dev warning) or `import.meta.env.PROD`.

---

## External-link Hygiene (extension)

`grep 'target="_blank"'` → 2 matches:
- `views/auth/WelcomeView.vue:34` — has `rel="noopener"`
- `views/auth/StandaloneStubView.vue:18` — has `rel="noopener"`

#### 🟢 SUGGESTION — Add `noreferrer` to `_blank` links

`rel="noopener"` prevents reverse tab-nabbing (the new tab can't access `window.opener`). Adding `noreferrer` also strips the Referer header on the outbound request (best practice for opaque external links).

```diff
- <a :href="botUrl" target="_blank" rel="noopener">
+ <a :href="botUrl" target="_blank" rel="noopener noreferrer">
```

The destination (Telegram bot deep link) is owned by the same project; referrer leak is minor. Still recommended for completeness. Single-cycle 2-line fix.

---

## Cross-Reference

- **#013** — TMA + PWA. Telegram-side identity is the primary auth source; bearer token is opaque to frontend.
- **C-1 fix** — TopupView open-redirect protection (DIAMOND in A10).
- **NEW-8** — auth-failure silence justified.
- **W-1** — logout resets master store before clearing session (prevents data leak between user sessions on the same tab).

---

## Step 3 Classification Suggestions

Single classification group:

| Group | Findings | Effort |
|---|---|---|
| A. Auth-flow hardening | A01 SUGGESTION (await in roleGuard) + Step 5 WARNING (same) + A07 SUGGESTION (telemetry) + external-link rel | 1 cycle, S |

Total: 1 small cycle. No CRITICAL/HIGH blockers from security-audit at S1 close.

---

## Anchor

[*] security-audit v1.1.0 * report ready
[>] | NEXT: Run 6 (probekit-design-audit)
