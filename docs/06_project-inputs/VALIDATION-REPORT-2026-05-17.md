# VELO Validation Report — Methodology v1.0 + Roadmap v1.0

```
Date:          2026-05-17
Method:        cross-reference VELO-METHODOLOGY.md v1.0 + ROADMAP.md v1.0
               against api-openapi.json, ARCHITECTURE.md, CC-REPORT.txt,
               CC-REPORT-2.txt, and frontend/src state
Author:        Chat (Claude in claude.ai), architect role
Status:        DRAFT — awaiting operator approval before Этап 2
Anchor:        [VALIDATION-REPORT-2026-05-17.md | v1.0 | 2026-05-17]
```

---

## Summary

| Severity | Count | Affects |
|---|---|---|
| 🔴 CRITICAL | 1 | frontend build blocker |
| 🟠 MAJOR — methodology I-invariants | 6 | §2.5 |
| 🟠 MAJOR — methodology §6.6 Tier 2 | 4 | §6.6 |
| 🟠 MAJOR — methodology §8 spec template | 4 | §8 |
| 🟠 MAJOR — methodology §3 folder paths | 1 | §3 |
| 🟠 MAJOR — roadmap scope | 6 | §3.1, §6.1, §7.1, §8.1, §10.1, §16 |
| 🔵 BACKEND GAP | 3 | OpenAPI |
| 🟡 MINOR | 2 | misc |
| ✅ CONFIRMED VALID | 9 | various |

**Headline finding:** unified methodology v1.0 is structurally sound. All
amendments are **delta** corrections — no rewrite needed. After applying
the amendments below, version will bump to **v1.1** with a Changelog
entry.

**Operator-approved decisions** (captured during planning, applied below):
- D1 — fix startParam namespace to 4 patterns (`open_practice`,
  `open_master`, `open_booking`, `open_topup`)
- D2 — reports flow: `create_report` as action on `user-practice-detail`
  (Sprint 3), `user-reports-list` as new screen (Sprint 4)

---

# Section A — 🔴 CRITICAL findings

## A1. Build is currently broken — `types.ts:65`

**Source:** CC-REPORT-2.txt Q1.5
**File:** `frontend/src/api/types.ts:65`
**Symptom:** `vue-tsc --noEmit` fails with
`error TS2305: Module '"./generated"' has no exported member 'PayoutDetails'`

**Root cause.** Backend renamed schema `PayoutDetails` →
`PayoutDetailsResponse` and regenerated `generated.ts`. `types.ts:65`
still re-exports the old name. One-line fix.

**Action.** Add as **first task in Sprint 0** (before T0.1). Task name:
`T0.0 — Fix build blocker: PayoutDetails → PayoutDetailsResponse`.

**Owner:** Claude Code.

**Effort:** <5 minutes.

---

# Section B — 🟠 MAJOR — Methodology §2.5 invariants (6 items)

## B1. I2 (timezone) — missing `user.timezone` mention

**Source:** CC-REPORT-2.txt Q2.2
**Current §2.5 I2:** "Timezone is per-practice, not browser-local. Each
practice carries its own `timezone` field (IANA string)."

**Reality.** OpenAPI has `timezone` in 6 schemas — not only in
practices but also in `UserResponse.timezone` and `UserUpdate.timezone`.

**Action.** Expand I2:

> I2 — Timezone is per-entity, not browser-local. Practices carry their
> own `practice.timezone` field (IANA string) — used for all
> practice-related date/time formatting. The user also carries a
> `user.timezone` — used for aggregate views (dashboard, diary,
> calendar) when no practice context is available. Format via
> `formatDate(iso, timezone, locale)` from utils. Never use browser
> default timezone.

## B2. I4 (errors) — VeloError is code-only, not in OpenAPI

**Source:** CC-REPORT-2.txt Q2.4
**Current §2.5 I4:** lists three error formats including VeloError
`{ error: string, message: string }`.

**Reality.** OpenAPI only documents `HTTPValidationError` (Pydantic 422).
VeloError shape `{ error, message }` exists at runtime (`client.ts:164-186`
parses it) but is **not** in `api-openapi.json`. Therefore changes to
the format won't be caught by `vue-tsc` or by `generated.ts` regen.

**Action.** Add a note to I4:

> Implementation note: `VeloError` is a **code-only contract** — its
> shape is enforced by `frontend/src/api/client.ts` parsing logic and
> backend exception handlers, but is **not declared** in
> `api-openapi.json`. Changes to VeloError shape are not caught by
> `vue-tsc` or by `velo gen-types` regen — they must be coordinated
> manually between backend and frontend. See I8 below for the broader
> code-only-contract risk.

## B3. I5 (Telegram deep links) — namespace not fixed

**Source:** CC-REPORT-2.txt Q5.6 / Q7.2 / operator decision D1
**Current §2.5 I5:** mentions only `open_practice__{uuid}` example.

**Reality + operator decision D1.** Fix the namespace to 4 patterns now;
extendable in future versions.

**Action.** Expand I5:

> I5 — Telegram deep links survive auth. Telegram start parameters
> arrive on `Window.Telegram.WebApp.initDataUnsafe.start_param` and
> are accessed via `platform.getStartParam()`. The `/loading` flow must
> preserve them across the redirect.
>
> **Canonical startParam patterns (v1.1 initial set, extendable):**
> - `open_practice__{uuid}` — deep-link to a practice detail screen
> - `open_master__{uuid}` — deep-link to a master profile
> - `open_booking__{uuid}` — deep-link to a booking detail
> - `open_topup` — deep-link to the topup screen (no parameter)
>
> Screen specs that are deep-link entry points must declare which
> startParam pattern they accept and how the parameter maps to route
> params or store state.

## B4. I6 (Waitlist FSM) — `offered` → `notified`

**Source:** CC-REPORT-2.txt Q2.5
**Current §2.5 I6:** `waiting → offered → confirmed | left | expired | declined`

**Reality.**
- `frontend/src/api/types.ts:129`: `'waiting' | 'notified' | 'confirmed' | 'left' | 'expired' | 'declined'`
- OpenAPI `WaitlistEntryResponse.notified_at` field name — confirms `notified` semantics
- Previous CC-REPORT.txt (line 501) also used `notified`

**Action.** Replace `offered` with `notified` in I6 + give a proper
transition diagram:

> I6 — Waitlist FSM has six states. The waitlist for a practice
> progresses through:
> ```
> waiting → notified → confirmed | declined | expired
>         ↘  left  (user leaves before notified)
> ```
> Transitions:
> - `waiting → notified` — backend offers a seat; `notified_at` is set;
>   user receives push
> - `notified → confirmed` — user accepts within deadline (confirm endpoint)
> - `notified → declined` — user explicitly declines
> - `notified → expired` — deadline (`expires_at`) passes without action
> - `waiting → left` — user leaves the waitlist before any offer
>
> Cross-spec references must cite this FSM by ID (I6 + §8.7).

Also update **§6.6 Tier 2 WaitlistCard** entry (see C2).

## B5. I8 (NEW) — Status enums are code-only contracts

**Source:** CC-REPORT-2.txt Q2.6
**Reality.** Only **4 enums** are formally declared in `api-openapi.json`:
- `UserRole`: `['user', 'master', 'admin']`
- `SemaphoreResult.status`: `['OK', 'ALERT']`
- `SemaphoreResult.criticality`: `['critical', 'warning', 'info']`
- `CreateReportRequest.target_type`: `['user', 'master', 'practice']`

All other status fields (`BookingStatus`, `PracticeStatus`,
`MasterStatus`, `WithdrawalStatus`, `WaitlistStatus`, `PurchaseStatus`,
etc.) are typed as `string` in OpenAPI with **no enum constraint**.
The narrowing happens only in `frontend/src/api/types.ts` TypeScript
unions. Therefore the contract is **code-only** — backend can silently
add a new status value and `vue-tsc` won't catch it.

**Action.** Add a new invariant I8 to §2.5:

> I8 — Status enums are code-only contracts. The following enums are
> **not declared in OpenAPI** (the field type is `string`); their real
> values live only in `frontend/src/api/types.ts` as TypeScript unions:
> - `BookingStatus`: `pending | confirmed | attended | no_show | cancelled`
> - `PracticeStatus`: `draft | scheduled | live | completed | cancelled | deleted`
> - `PracticeType`: `live | series | one_on_one | replay`
> - `MasterStatus`: `pending | verified | rejected`
> - `WithdrawalStatus`: `pending | approved | rejected`
> - `WaitlistStatus`: `waiting | notified | confirmed | left | expired | declined`
> - `PurchaseStatus`: `pending | completed | refunded | failed`
> - `AttendanceBookingStatus`: `pending | confirmed | attended | no_show`
> - `Mood`: `low | mid | high`
> - `FeedbackRating`: `fire | good | confused`
>
> Risk: changes to these enums on the backend are not caught by
> `vue-tsc` or by `velo gen-types` regen. Mitigations:
> 1. Specs use these enums by name; if backend adds a new value,
>    spec must be updated (and a switch's `default` branch should warn).
> 2. Status-bearing components (BookingCard, PracticeCard, WaitlistCard,
>    etc.) must use exhaustive `switch` and treat unknown values as
>    an error state, not silently render a blank.

## B6. (Reserved for future I9 if needed)

---

# Section C — 🟠 MAJOR — Methodology §6.6 Tier 2 expansions (4 items)

## C1. PracticeCard — statuses not enumerated

**Source:** CC-REPORT-2.txt Q2.6
**Current §6.6 row:** "Types live / series / one_on_one / replay;
free/paid; statuses"

**Reality.** `PracticeStatus` has 6 values in code:
`draft | scheduled | live | completed | cancelled | deleted`.
`PracticeStatusTransition` (allowed transitions only) has 4:
`scheduled | live | completed | deleted`.

**Action.** Update the §6.6 row:

> | `PracticeCard` | Types `live` / `series` / `one_on_one` / `replay`; `free` / `paid`; Statuses (per I8): `draft` / `scheduled` / `live` / `completed` / `cancelled` / `deleted`. Component must handle unknown status as error state. | PracticeResponse |

## C2. WaitlistCard — wrong + incomplete statuses

**Source:** CC-REPORT-2.txt Q2.5/Q2.6
**Current §6.6 row:** "Statuses waiting / offered / expired / confirmed"

**Action.** Replace with all 6 states from I6 (corrected `offered` →
`notified`):

> | `WaitlistCard` | Statuses (per I6 + I8): `waiting` / `notified` / `confirmed` / `left` / `expired` / `declined`. Component must handle unknown status as error state. | WaitlistEntryResponse / WaitlistWithPracticeResponse |

## C3. PromoRow — "active/inactive" is UI abstraction, not contract

**Source:** CC-REPORT-2.txt Q2.6
**Current §6.6 row:** "PromoRow | active / inactive; usage / limit"

**Reality.** `PromoStatus` enum **does not exist** anywhere — neither
in OpenAPI nor in `types.ts`. Promo activity is derived from
`deactivated_at` (or a boolean), and the deactivate-endpoint
`PATCH .../promos/{id}/deactivate` controls it.

**Action.** Update row:

> | `PromoRow` | `active` / `inactive` (UI abstraction derived from `PromoResponse.deactivated_at` and/or `is_active` boolean — there is no formal `PromoStatus` enum); usage / limit fields. | PromoResponse |

## C4. Missing entries in Tier 2 — Mood, FeedbackRating, etc.

**Source:** CC-REPORT-2.txt Q2.6
**Reality.** The methodology §6.6 lists `MoodWidget` and `FeedbackWidget`
but doesn't enumerate their values. The CC report supplies them:
- `Mood`: `low | mid | high`
- `FeedbackRating`: `fire | good | confused`

**Action.** Update existing rows:

> | `FeedbackWidget` | Values (per I8): `fire` / `good` / `confused`. | FeedbackRequest |
> | `MoodWidget` | Values (per I8): `high` / `mid` / `low`. | CheckinRequest |

Also `AttendanceBookingStatus` is a separate enum (`pending | confirmed |
attended | no_show`) — used by master-practice-attendance screen. Add
to BookingCard variants note:

> | `BookingCard` | Statuses (per I8): `pending` / `confirmed` / `cancelled` / `attended` / `no_show`. Subset `AttendanceBookingStatus` (`pending` / `confirmed` / `attended` / `no_show`) used by master-practice-attendance. | BookingWithPracticeResponse |

---

# Section D — 🟠 MAJOR — Methodology §8 spec template expansions (4 items)

## D1. §8.3 Section 5 — query params not required

**Source:** CC-REPORT-2.txt Q7.1 #1
**Current §8.4 guidance for Section 5:** "Reference operation IDs from
`api-openapi.json` by exact name. Do not paste schemas."

**Gap.** No explicit requirement to declare query params (limit, offset,
filters) for list_* endpoints. CC-REPORT-2 cites this as a real
ambiguity — without it CC picks defaults that mismatch product intent.

**Action.** Add to §8.4 Section 5 guidance:

> For list_* and paginated endpoints, declare the **initial query
> params** explicitly:
> - `limit` (default 20 if not stated)
> - `offset` (default 0)
> - Filters: any `status=`, `master_id=`, `date_from=`, `date_to=`,
>   `sort_by=` that are passed on initial render
> - Pagination strategy: infinite scroll vs page-by-page
>
> If the spec is silent, CC will pick defaults that likely mismatch
> product intent.

## D2. §8.3 Section 7 — partial failure not addressed

**Source:** CC-REPORT-2.txt Q7.1 #2
**Gap.** For aggregating screens (dashboard fetches 3-5 endpoints in
parallel), State Map doesn't say what to do when 1 of 5 fails.

**Action.** Add to §8.4 Section 7 guidance:

> For screens with multi-endpoint initial render, the State Map must
> include a **`partial-error`** state: what to render when some
> endpoints succeed and others fail. Two common patterns:
> - **Best-effort:** render the successful sections with their data;
>   show inline error in failed sections (with retry).
> - **All-or-nothing:** if any required endpoint fails, render
>   full-screen error with retry.
>
> The spec must declare which pattern this screen uses.

## D3. §8.3 Section 11 — Error Code Map without examples

**Source:** CC-REPORT-2.txt Q7.2
**Gap.** Section 11 template is empty; CC reports that spec authors
produce inconsistent tables. The methodology should give a baseline.

**Action.** Add to §8.4 Section 11 guidance + new appendix:

> Minimum baseline (every spec includes at least these where applicable):
>
> | Error code | Source | Default reaction |
> |---|---|---|
> | `unauthorized` | 401 on any endpoint | Trigger `setOnUnauthorized` callback → redirect to `/loading` |
> | `forbidden` | 403 | Toast `errors.forbidden` |
> | `not_found` | 404 on resource fetch | Redirect to parent listing or show 404 view |
> | `rate_limited` | 429 | Toast `errors.rateLimit`; disable action for 30s |
> | `validation_failed` | 422 (Pydantic) | Inline field-level errors from `detail[]` |
> | (network) | `ApiNetworkError` | Toast `errors.network`; offer retry |
> | (timeout) | `ApiTimeoutError` (15s default) | Toast `errors.timeout`; offer retry |
>
> Plus screen-specific VeloError codes the spec explicitly handles.

## D4. §8.3 Section 9 — empty state copy implicit

**Source:** CC-REPORT-2.txt Q7.1 #8
**Gap.** Specs often omit explicit empty-state strings; CC picks
placeholders.

**Action.** Add to §8.4 Section 9 guidance:

> For every state in §7 that requires UI copy (empty, error,
> loading-with-message), the i18n key + proposed Russian text **must**
> be enumerated in Section 9 — no implicit "use a generic empty state."
> Example:
> ```json
> {
>   "dashboard": {
>     "upcoming": {
>       "empty": "Нет запланированных практик",
>       "emptyCta": "Посмотреть каталог"
>     }
>   }
> }
> ```

---

# Section E — 🟠 MAJOR — Methodology §3 folder paths (1 item)

## E1. ARCHITECTURE.md canonical location

**Source:** CC-REPORT-2.txt Q4.1
**Current §3 of methodology:** mentions `frontend/docs/ARCHITECTURE.md`
as canonical location.

**Reality.** Canonical file is `frontend/ARCHITECTURE.md` (root of
frontend repo). `frontend/docs/` does **not** exist.

**Action.** Fix all references in §3 of methodology:
- `frontend/docs/ARCHITECTURE.md` → `frontend/ARCHITECTURE.md`
- Same for `frontend/docs/ENVIRONMENT.md` if mentioned

Also update **`06_project-inputs/README.md`** to reflect canonical
source.

---

# Section F — 🟠 MAJOR — Roadmap scope amendments (6 items)

## F1. Sprint 0 — missing build-fix task

**Source:** A1 above
**Action.** Insert **T0.0** as first task in `sprint-00.md`:

> ### T0.0 — Fix build blocker (CRITICAL)
> Owner: Claude Code (or operator manually).
> - [ ] Edit `frontend/src/api/types.ts:65`: replace `PayoutDetails,`
>       with `PayoutDetailsResponse,`
> - [ ] Run `npm run typecheck` — must pass
> - [ ] Run `npm run build` — verify proceeds further (may still hit
>       router issues; those are T0.3)
> - [ ] Commit: "fix(api): rename PayoutDetails → PayoutDetailsResponse"

## F2. Sprint 0 — global.css token audit

**Source:** CC-REPORT-2.txt Q5.2/Q5.3
**Reality.** `global.css` uses 4 non-velo tokens (`--font-body`,
`--text-base`, `--text-2xl`, `--text-xs`, `--space-2`, `--radius-full`)
and 3 velo-prefixed but mis-named (`--velo-bg-start`, `--velo-primary`,
`--velo-border`).

**Action.** Add **T0.8** to `sprint-00.md`:

> ### T0.8 — Audit `frontend/src/styles/global.css` token names
> Owner: Claude Code.
> - [ ] Greenlist tokens with `--velo-*` prefix to be defined in
>       Sprint 1 variables.css
> - [ ] Yellowlist non-velo tokens (`--font-body`, `--text-base`,
>       `--text-2xl`, `--text-xs`, `--space-2`, `--radius-full`) —
>       either rename to `--velo-*` or replace with literal values
>       pending Sprint 1
> - [ ] Yellowlist mis-named velo tokens (`--velo-bg-start`,
>       `--velo-primary`, `--velo-border`) — pending Sprint 1 will be
>       replaced with canonical names (`--velo-bg-screen`,
>       `--velo-bg-button-primary`, `--velo-border-default`)
> - [ ] Document decisions in `02_design-system/INDEX.md → Open TODOs`
>       to be resolved during Sprint 1 Phase 2

## F3. Sprint 0 — gen:api script + pre-commit hook

**Source:** CC-REPORT-2.txt Q7.4
**Reality.** No `gen:api` script in `package.json`, no pre-commit hook,
no CI check. The PayoutDetails bug (A1) would have been caught.

**Action.** Add **T0.7** to `sprint-00.md`:

> ### T0.7 — Wire up `gen:api` automation
> Owner: Claude Code.
> - [ ] Add to `frontend/package.json` scripts:
>   ```json
>   "gen:api": "cd ../backend && python -m scripts.generate_ts_types",
>   "gen:api:check": "cd ../backend && python -m scripts.generate_ts_types --check"
>   ```
> - [ ] Verify command runs end-to-end (smoke test)
> - [ ] (Optional, recommended) Install husky or write
>       `scripts/install-hooks.sh` for pre-commit:
>       `npm run typecheck && npm run gen:api:check`
> - [ ] Commit

## F4. Roadmap §6.1 — user-practice-detail needs `create_report` action

**Source:** CC-REPORT-2.txt Q3.5 + operator decision D2
**Action.** Update ROADMAP.md §6.1 row for user-practice-detail:

> | 2 | user-practice-detail | `/practice/:id` | Core booking flow start. Includes `create_report` ("Пожаловаться") as a one-off action — see §6 Action Contract of its SCR. |

Also reflect in `sprint-03.md` T3.3 spec checklist for that SCR.

## F5. Roadmap §7.1 — add user-reports-list to wave 2

**Source:** CC-REPORT-2.txt Q3.5 + operator decision D2
**Action.** Add to ROADMAP.md §7.1 indicative list:

> | user-reports-list | `/reports` | List of user's own reports (status: pending/resolved/dismissed). Uses `get_my_reports`. Allows `update_report` (edit own report) per spec. |

Add corresponding entry to `sprint-04.md` scope.

## F6. Roadmap §10.1 — admin-user-detail + admin-withdrawal-review are blocked on backend

**Source:** CC-REPORT-2.txt Q3.4
**Reality.**
- `admin-user-detail` needs `GET /api/v1/admin/users/{id}` — not in OpenAPI
- `admin-withdrawal-review` needs `GET /api/v1/admin/withdrawals/{id}` — not in OpenAPI

**Action.** Update ROADMAP.md §10.1 entries:

> | 7 | admin-withdrawal-review | `/admin/withdrawals/:id` | **Blocked on backend:** requires `GET /api/v1/admin/withdrawals/{id}` (not yet in OpenAPI). Workaround: pass row via router state. See `06_project-inputs/BACKEND-REQUESTS-2026-05-17.md`. |
> | 10 | admin-user-detail | `/admin/users/:id` | **Blocked on backend:** requires `GET /api/v1/admin/users/{id}` (not yet in OpenAPI). See backend requests document. |

Add corresponding notes to `sprint-07.md` scope.

## F7. Roadmap §16 Risk Register — add R-11

**Source:** B5 (new I8)
**Action.** Append to ROADMAP.md §16:

> | R-11 | Code-only contracts (status enums, VeloError shape) drift between backend and frontend. | Medium | High | Operator + backend coordination; mitigations in I8 (exhaustive switch + unknown-as-error). Long-term: backend should declare enums in OpenAPI. |

## F8. Master analytics — client-side aggregation note

**Source:** CC-REPORT-2.txt Q3.3 #5
**Action.** Update ROADMAP.md §8.1 row #5:

> | 5 | master-analytics | `/master/analytics` | **Known limit:** aggregate analytics across all master's practices is **client-side only** (loop `get_practice_insights` per practice). No backend aggregate endpoint exists. Spec must document this constraint and pagination strategy. |

---

# Section G — 🔵 BACKEND GAPS — outside our scope (3 items)

These are for the **backend team**, not for us. Listed for tracking.

| ID | Endpoint missing | Used by | Workaround |
|---|---|---|---|
| BG1 | `GET /api/v1/admin/withdrawals/{id}` | admin-withdrawal-review | Pass row via router state from list view; cannot deep-link |
| BG2 | `GET /api/v1/admin/users/{id}` | admin-user-detail | Pass row via router state from list view; if user is master, fall back to `get_master` |
| BG3 | Aggregate master analytics endpoint | master-analytics | Client-side loop over `get_practice_insights` per practice |

**Action.** Create `06_project-inputs/BACKEND-REQUESTS-2026-05-17.md`
documenting these requests for the operator to forward to backend team.
Methodology and roadmap remain valid; specs for the affected screens
will mark them as `Blocked on backend` (per F6).

---

# Section H — 🟡 MINOR — observations not requiring action (2 items)

## H1. `get_ai_summary` operationId — not pinned to a screen

**Source:** CC-REPORT-2.txt Q3.5 #7
**Observation.** `GET /api/v1/practices/{id}/ai-summary` is available
but no SCR currently uses it.

**Recommendation.** Place on `user-practice-detail` and/or
`master-analytics` per-practice view. Not blocking. Address in
Sprint 3 / Sprint 5 spec authoring.

## H2. Tier 1 list confirmation deferred to Sprint 1

**Source:** CC-REPORT-2.txt Q7.2
**Observation.** Methodology §6.6 already says "planning target,
confirmed or revised after extraction." This is a deliberate methodology
property, not a defect. No action.

---

# Section I — ✅ CONFIRMED VALID

These methodology/roadmap claims are confirmed by CC-REPORT-2 against
real code/contract:

| Item | Source |
|---|---|
| I1 (cents) — all 26 money fields end with `_cents` | Q2.1 |
| I3 (role) — `'user' \| 'master' \| 'admin'` exact match | Q2.3 |
| I4 first format — VeloError parsed in `client.ts:164-186` | Q2.4 |
| §2.2 frontend stack — matches ARCHITECTURE.md §1 element-by-element | Q4.2 |
| §11.6 anti-patterns — fully compatible with ARCHITECTURE.md rules | Q4.3 |
| §6.1–6.4 token rules — compatible with ARCHITECTURE.md §3.0 | Q4.4 |
| §8.3 spec template structure — covers all CC questions raised in Q7.1 (gaps are about **density**, not structure) | Q7.1 |
| User block endpoint coverage (§6.1) — 100% covered | Q3.2 |
| Master block endpoint coverage (§8.1) — 100% covered (with client-side aggregation caveat) | Q3.3 |

---

# Section J — Frontend code to preserve (Q6 from CC-REPORT-2)

Sprint 1+ must **NOT** rewrite or replace the following — they are
mature, tested, documented:

| File | Why preserve |
|---|---|
| `frontend/src/api/client.ts` | Full wrapper: AbortController, 15s timeout, in-flight GET dedup, 401 callback, error normalisation. |
| `frontend/src/api/utils.ts` | `buildQuery()` helper, correct type-narrowing |
| `frontend/src/api/types.ts` | Re-export pattern (after A1 fix) |
| `frontend/src/utils/currency.ts` | `eurStringToCents` / `centsToEurString` — solves float trap |
| `frontend/src/utils/format.ts` (functions) | `formatMoney`, `formatDate`, `formatDateShort`, `formatTime`, `formatDuration`, `formatParticipants`, `isFull`. 8 Russian strings move to i18n in Sprint 2 T2.6. |
| `frontend/src/utils/constants.ts` | `CHECKIN_WINDOW_H=3`, `FEEDBACK_WINDOW_H=72`, `MIN_WITHDRAWAL_EUROS=50`, `WITHDRAWAL_FEE_EUROS=2`. Mirrors backend config.py. |
| `frontend/src/platform/` (4 files) | Telegram/standalone autodetect; `initData` / `startParam` / `haptic` / `backButton` abstraction. |
| `frontend/tsconfig.json` | strict + `noUncheckedIndexedAccess` etc. |
| `frontend/env.d.ts` | Vite env + Telegram WebApp SDK type declarations |
| `frontend/vite.config.ts` | Vue + VitePWA + proxy `/api → 127.0.0.1:8000` |
| `frontend/index.html` | Telegram WebApp SDK via CDN `<script>`, Google Fonts via `<link>` (FIX 10.6: better FCP) |

Spec acceptance criteria should not duplicate the rules implied by these
files. ARCHITECTURE.md §1 + §11.6 reference is sufficient.

---

# Section K — Approved decisions captured

These are operator decisions taken during planning (2026-05-17) that
form the basis for amendments below.

**D1 — Telegram startParam namespace (4 initial patterns):**
- `open_practice__{uuid}`
- `open_master__{uuid}`
- `open_booking__{uuid}`
- `open_topup` (no param)

Applied in B3 (I5 expansion).

**D2 — Reports flow placement:**
- `create_report` is an action on `user-practice-detail` (Sprint 3) —
  added to that SCR's Action Contract
- `user-reports-list` is a new screen in `sprint-04` wave 2 — uses
  `get_my_reports` and `update_report`

Applied in F4 (Sprint 3) and F5 (Sprint 4).

---

# Section L — Execution plan (Этапы 2–7)

**Этап 2 — Methodology v1.0 → v1.1.** Apply B1–B6, C1–C4, D1–D4, E1.
Bump version, add Changelog row.

**Этап 3 — Roadmap.** Apply F4, F5, F6, F7, F8. No version bump
needed (roadmap is operator-facing planning doc — annotate Recent
Changes only).

**Этап 4 — Sprint files.** Apply F1, F2, F3 to `sprint-00.md`. Apply
F4 to `sprint-03.md`. Apply F5 to `sprint-04.md`. Apply F8 to
`sprint-05.md`. Apply F6 to `sprint-07.md`.

**Этап 5 — Backend requests.** Create
`06_project-inputs/BACKEND-REQUESTS-2026-05-17.md` covering BG1, BG2,
BG3.

**Этап 6 — `docs/INDEX.md`.** Methodology version → v1.1; new Recent
Changes entry; Open TODOs updated.

**Этап 7 — Verification.**
- `grep -rn 'offered' docs/04_methodology docs/05_roadmap` → must be 0
- `grep -rn 'frontend/docs/ARCHITECTURE' docs/04_methodology` → must be 0
- All §2.5 cross-references in updated docs still resolve
- All `T0.0` / `T0.7` / `T0.8` checkboxes coherent
- No broken internal links

Total estimated execution time after operator approval: **~45–60 min**.

---

# Operator approval

To proceed to Этап 2:

- [ ] Approve all amendments (B1–B6, C1–C4, D1–D4, E1, F1–F8)
- [ ] Or: list specific amendments to skip / change
- [ ] Or: request additional clarification

Once approved, I run Этапы 2–7 in one pass and report back.

---

## Anchor

```
[VALIDATION-REPORT-2026-05-17.md | v1.0 | 2026-05-17]
Full validation pass of VELO-METHODOLOGY.md v1.0 + ROADMAP.md v1.0
against api-openapi.json, ARCHITECTURE.md, CC-REPORT.txt, CC-REPORT-2.txt.
26 findings, 1 critical, severity-tagged, with concrete proposed actions.
Status: DRAFT — awaiting operator approval before Этап 2.
Location: D:\02_Projects\velo\docs\06_project-inputs\VALIDATION-REPORT-2026-05-17.md
```
