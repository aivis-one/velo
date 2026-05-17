# VELO — Backend Requests Arising from Validation Pass 2026-05-17

```
Date:           2026-05-17
Source:         VALIDATION-REPORT-2026-05-17.md, Section G
Owner forward:  Operator → backend team
Anchor:         [BACKEND-REQUESTS-2026-05-17.md | v1.0 | 2026-05-17]
```

> **Purpose.** During the v1.1 validation pass of the VELO design
> methodology and roadmap against `api-openapi.json`, three contract
> gaps were identified that prevent specific admin-side screens from
> being implementable as deep-linked entry points. This document lists
> those gaps for the backend team's consideration.
>
> **None of these gaps block the design-and-handoff timeline.** Each
> has a documented frontend workaround in the affected SCR spec (to be
> written in the respective sprint). If the backend resolves them
> before the corresponding sprint, the screens become cleaner; if not,
> we proceed with the workaround.

---

## Request 1 — `GET /api/v1/admin/withdrawals/{id}`

### What is needed

A single-resource endpoint returning the full `AdminWithdrawalResponse`
for one withdrawal by its UUID.

### Why

Frontend screen `admin-withdrawal-review` at route
`/admin/withdrawals/:id` (Sprint 7) is intended as a deep-linkable
review page: an admin clicks a withdrawal in a notification, or
bookmarks a specific case, and lands directly on its review screen.
Without a GET-by-id endpoint, the admin cannot deep-link — they must
navigate via the list view, which is fragile (state lost on refresh).

### Current OpenAPI state

`GET /api/v1/admin/withdrawals` (list, paginated) ✓
`POST /api/v1/admin/withdrawals/{id}/approve` ✓
`POST /api/v1/admin/withdrawals/{id}/reject` ✓
`GET /api/v1/admin/withdrawals/{id}` ❌ — missing

### Proposed shape

```yaml
get:
  tags: [admin]
  operationId: get_admin_withdrawal
  summary: Get admin view of one withdrawal
  parameters:
    - name: id
      in: path
      required: true
      schema: { type: string, format: uuid }
  responses:
    '200':
      description: OK
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/AdminWithdrawalResponse'
    '404': { description: Not found }
    '403': { description: Forbidden (non-admin) }
```

### Frontend workaround if not delivered

Spec for `admin-withdrawal-review` (Sprint 7) declares:
- Entry only via row click from `admin-withdrawals` list
- Withdrawal payload passed via Vue Router state (`router.push({ name: 'admin-withdrawal-review', state: { withdrawal: row } })`)
- Refresh on the deep URL falls back to redirecting to
  `admin-withdrawals` list with a toast "Откройте заявку из списка"

---

## Request 2 — `GET /api/v1/admin/users/{id}`

### What is needed

A single-resource endpoint returning a full user profile for admin view.

### Why

Frontend screen `admin-user-detail` at route `/admin/users/:id`
(Sprint 7) is the admin-side counterpart of the public user profile.
Currently OpenAPI exposes only the paginated user list
(`GET /api/v1/admin/users`) and, separately, `GET /api/v1/admin/masters/{id}`
for master profiles. There is no general user-by-id endpoint.

### Current OpenAPI state

`GET /api/v1/admin/users` (list, paginated) ✓
`GET /api/v1/admin/masters/{id}` ✓ (master-specific)
`GET /api/v1/admin/users/{id}` ❌ — missing

### Proposed shape

```yaml
get:
  tags: [admin]
  operationId: get_admin_user
  summary: Get admin view of one user (any role)
  parameters:
    - name: id
      in: path
      required: true
      schema: { type: string, format: uuid }
  responses:
    '200':
      description: OK
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/AdminUserResponse'
            # or UserResponse with admin-side fields if no separate schema
    '404': { description: Not found }
    '403': { description: Forbidden (non-admin) }
```

### Frontend workaround if not delivered

Spec for `admin-user-detail` (Sprint 7) declares:
- Entry only via row click from `admin-users` list (state pass-through)
- If user has `role === 'master'`, **secondary** endpoint
  `get_master` (`GET /api/v1/admin/masters/{id}`) is used to enrich
  the view; otherwise only the data passed via router state is shown
- Refresh on the deep URL falls back to `admin-users` with toast

---

## Request 3 — Aggregate master analytics endpoint (optional / nice-to-have)

### What is needed

A single endpoint returning aggregated metrics across **all** of one
master's practices (e.g., total feedbacks by rating, mood distribution,
attendance trends over a date range).

### Why

Frontend screen `master-analytics` at `/master/analytics` (Sprint 5)
is intended as the master's high-level dashboard for their practice
business. Currently OpenAPI only exposes
`GET /api/v1/practices/{practice_id}/insights` — per-practice metrics.
To populate the aggregate dashboard, the frontend must loop the
per-practice endpoint over each of the master's practices and
aggregate client-side. For masters with many practices this is slow
and fragile.

### Current OpenAPI state

`GET /api/v1/practices/{id}/insights` ✓ (per-practice)
`GET /api/v1/masters/me/practices` ✓ (master's practice list)
Aggregate endpoint ❌ — missing

### Proposed shape (suggestion, not prescriptive)

```yaml
get:
  tags: [masters, analytics]
  operationId: get_master_aggregate_insights
  summary: Aggregate insights across master's practices
  parameters:
    - name: date_from
      in: query
      schema: { type: string, format: date }
    - name: date_to
      in: query
      schema: { type: string, format: date }
  responses:
    '200':
      description: OK
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/MasterAggregateInsightsResponse'
```

### Frontend workaround (current plan if not delivered)

Spec for `master-analytics` declares:
- Aggregate is **client-side**: loop `get_practice_insights` over the
  master's practices
- Pagination: aggregate only the N most recent practices (N=20 default;
  configurable in spec)
- A note in the UI: "Аналитика по последним N практикам"
- This is functional but slower than a backend aggregate; treat as a
  known performance debt

---

## Priority

| Request | Severity | Sprint where it surfaces |
|---|---|---|
| 1 — admin-withdrawal-review GET | Medium | Sprint 7 |
| 2 — admin-user-detail GET | Medium | Sprint 7 |
| 3 — master aggregate analytics | Low (optimization, not blocker) | Sprint 5 |

All three are **non-blocking** for the design-and-handoff roadmap.
Requests 1 and 2 affect deep-link UX in admin; request 3 affects
analytics page performance for masters with many practices.

---

## Cross-references

- `06_project-inputs/VALIDATION-REPORT-2026-05-17.md` Section G
- `04_methodology/VELO-METHODOLOGY.md` v1.1 (no direct references — these
  are backend-side; the frontend mitigation lives in I8 and §8.4)
- `05_roadmap/ROADMAP.md` v1.1 §16 Risk Register R-13
- `05_roadmap/sprint-05.md` (master-analytics — BG3 note)
- `05_roadmap/sprint-07.md` (admin-withdrawal-review — BG1, admin-user-detail — BG2)

---

## Anchor

```
[BACKEND-REQUESTS-2026-05-17.md | v1.0 | 2026-05-17]
Three OpenAPI gaps identified during v1.1 validation pass.
For operator to forward to the backend team.
None block the design-and-handoff timeline.
Location: D:\02_Projects\velo\docs\06_project-inputs\BACKEND-REQUESTS-2026-05-17.md
```
