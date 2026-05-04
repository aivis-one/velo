# Phase 15: Admin Role Refresh
> Sprint 4: Master + Admin Roles Refresh
> Status: DONE
> Closed: 2026-05-04
> Mode: speedrun (decision #052 continuation of #049) — single MEGA-4 execute prompt covered all 8 cycles

## Goal

Refresh 7 admin role views под Velo DS using UI-mockups on user-role patterns + speedrun shared components. Emoji cleanup per #048 (25 hits → 0 in `views/admin/`). Resolve `stores/admin.ts` decision: create store OR continue direct-api pattern (current state). Designer-batch-independent per #051.

## Entry Condition

- Phase 14 closed (MEGA-3 commit pushed, paramiko deploy A clean)
- Admin role unfreeze decision #051 ratified in S4-SPRINT.md
- C66 admin store decision spike completed (lightweight ~30 min decision)

## Exit Condition

- All 7 admin views refreshed (no glass / no emoji / Velo DS tokens / Path Y MEDIUM fidelity)
- Routes preserved: 7 admin path entries unchanged in router/index.ts
- Guards preserved: parent `roleGuard('admin')` on all 7 admin routes
- TD-FE-ROLE-SWITCH preserved in AdminProfileView (uses `useUiStore.uiMode`)
- admin store decision documented (create stores/admin.ts OR continue direct-api with rationale)
- Emoji audit: `grep -rIEn "[emoji_pattern]" frontend/src/views/admin/` returns 0 in-scope hits
- typecheck 0 errors, lint warnings ≤ baseline
- MEGA-4 commit pushed to `new_desing`
- paramiko deploy via `velo update` returns A clean (or B/C with documented findings)

## Tasks

### C66 — Admin store decision spike
**Scope:** decision-only cycle (~30 min); MAY produce `frontend/src/stores/admin.ts` skeleton if create-path chosen
**Cycle type:** standard (decision spike)
**Action:** Evaluate trade-off — current state: 6 of 7 admin views call `api/admin.ts` directly + local refs (no store). Create-path: introduce `stores/admin.ts` for cross-view state (moderation queue cache, master verification working set). Continue-path: per-view local refs + direct-api preserved.
**Decision criteria:**
- If any 2+ admin views need shared state (e.g. AdminMastersView + AdminMasterReviewView both reading verification queue) → create
- If all 7 views are independent (current state per scout) → continue
**Documentation:** decision recorded in P15 task notes + decisions.md if create-path (new decision #053 candidate)
**Test:** N/A (planning cycle)

### C67 — AdminProfileView refresh
**Scope:** `frontend/src/views/admin/AdminProfileView.vue` (157 LOC, simplest)
**Cycle type:** standard
**Skin reference:** UserProfileView (skin 70/71) — minimal version (no stat cards needed)
**Pattern reuse:** ProfileMenuItem, Callout (admin context warning if applicable)
**Critical preserve:** TD-FE-ROLE-SWITCH section — uses `useUiStore.uiMode` for admin ↔ user mode toggle
**Emoji cleanup:** TBD
**Decision refs:** #047, #048, #051
**Test:** typecheck + role-switch toggle + visual

### C68 — AdminDashboardView refresh
**Scope:** `frontend/src/views/admin/AdminDashboardView.vue` (286 LOC)
**Cycle type:** standard
**Skin reference:** UserDashboardView (skin 10/11) pattern — adapted to admin metrics (total users / total masters / pending verifications / open reports / etc.)
**Pattern reuse:** StatCard, Callout (alert for pending counts), MasterCardSummary or ConversationListItem-like rows for recent activity
**Emoji cleanup:** TBD (9 hits — highest in admin)
**Generated.ts:** consume `AdminStatsResponse` (confirmed in scout)
**Decision refs:** #047, #048, #051
**Test:** typecheck + visual + dashboard data load

### C69 — AdminMastersView refresh
**Scope:** `frontend/src/views/admin/AdminMastersView.vue` (245 LOC, list)
**Cycle type:** standard
**Skin reference:** MyReservationsView (skin 17) pattern — list with status chips (verified mint / pending amber / rejected pink)
**Pattern reuse:** ReservationCard variant or new AdminMasterListItem if methods/specialization chips needed; ProfileMenuItem-like rows
**Emoji cleanup:** TBD
**Generated.ts:** consume `AdminMasterListItem[]` (E.1 in BEC § E — `role: string → UserRole` narrowed; confirmed in scout)
**Decision refs:** #047, #048, #051
**Test:** typecheck + list pagination + filter by status + visual

### C70 — AdminMasterReviewView refresh
**Scope:** `frontend/src/views/admin/AdminMasterReviewView.vue` (362 LOC, verification flow)
**Cycle type:** standard
**Skin reference:** UI-mockup based on EditProfileView (skin 72/73) + verify/reject CTAs
**Pattern reuse:** FormShell + Callout (verify warnings) + VModal (verify/reject confirm) + StatCard (master stats)
**Emoji cleanup:** TBD
**Generated.ts:** consume `MasterApplyResponse` + `AdminMasterActionResponse`
**Decision refs:** #047, #048, #051
**Test:** typecheck + verify flow + reject flow + visual

### C71 — AdminReportsView refresh
**Scope:** `frontend/src/views/admin/AdminReportsView.vue` (305 LOC, list)
**Cycle type:** standard
**Skin reference:** MyReservationsView (skin 17) — list with severity chips
**Pattern reuse:** ReservationCard variant or new AdminReportListItem; status chips (open / resolved / dismissed)
**Emoji cleanup:** TBD (4 hits)
**Generated.ts:** consume `ReportResponse[]`
**Decision refs:** #047, #048, #051
**BEC ref:** § A.9 reports UI integration — admin-side already has endpoints; user-side surface deferred (design pending)
**Test:** typecheck + list filter + visual

### C72 — AdminReportDetailView refresh
**Scope:** `frontend/src/views/admin/AdminReportDetailView.vue` (383 LOC, triage flow)
**Cycle type:** standard
**Skin reference:** UI-mockup based on DiaryEntryView (skins 52/56-59) — content card + action menu (resolve / dismiss)
**Pattern reuse:** EntryActionMenu (resolve/dismiss buttons), Callout (severity warning), VModal (action confirm), AICommentaryCard (if AI-flagged content)
**Emoji cleanup:** TBD
**Decision refs:** #047, #048, #051
**Test:** typecheck + resolve flow + dismiss flow + visual

### C73 — AdminConsistencyView refresh
**Scope:** `frontend/src/views/admin/AdminConsistencyView.vue` (337 LOC, probe results)
**Cycle type:** standard
**Skin reference:** UI-mockup based on AISummaryView (skin 16) — sectioned probe results with status indicators
**Pattern reuse:** Callout (probe failures), StatCard (probe pass/fail counts), AccordionItem if expandable sections
**Emoji cleanup:** TBD
**Decision refs:** #047, #048, #051
**Test:** typecheck + probe data load + visual

## Cycles

| Cycle | Type | Name | Status | Date | Result |
|-------|------|------|--------|------|--------|
| C66 | standard | Admin store decision spike | DONE | 2026-05-04 | Verdict: continue direct-api (zero shared methods, zero cross-view state); no stores/admin.ts created |
| C67 | standard | AdminProfileView refresh | DONE | 2026-05-04 | Refreshed (skin 70/71); TD-FE-ROLE-SWITCH 1-marker baseline preserved; setUiMode logic intact |
| C68 | standard | AdminDashboardView refresh | DONE | 2026-05-04 | Refreshed; 4-card StatCards row consuming AdminStatsResponse; Callout amber when pending_verifications > 0 |
| C69 | standard | AdminMastersView refresh | DONE | 2026-05-04 | Refreshed (skin 17); status chips via masterStatusVariant; VEmptyState branch; usePagination preserved |
| C70 | standard | AdminMasterReviewView refresh | DONE | 2026-05-04 | Refreshed degraded v1 per Context #2; ConfirmModal verify/reject; BACKLOG #104 anchor in placeholder Callout |
| C71 | standard | AdminReportsView refresh | DONE | 2026-05-04 | Refreshed (skin 17); status chips via reportStatusVariant; VEmptyState branch |
| C72 | standard | AdminReportDetailView refresh | DONE | 2026-05-04 | Refreshed; compose VButton + ConfirmModal (resolve/dismiss); EntryActionMenu intentionally absent per Context #4 |
| C73 | standard | AdminConsistencyView refresh | DONE | 2026-05-04 | Refreshed; typed ConsistencyResponse + SemaphoreResult; VAccordion expandable details; P15 risk #3 closed |
| C74 | standard | S4 closure: visual verify + closure commit | IN PROGRESS | 2026-05-04 | Phase commit + push complete; visual verify gate pending paramiko deploy |

## Tests Summary

| # | Test | Command/Check |
|---|------|---------------|
| T1 | typecheck | `(cd frontend && npm run typecheck)` → 0 errors |
| T2 | lint | `(cd frontend && npm run lint)` → ≤ 756 warnings (S1 baseline) |
| T3 | test | `(cd frontend && npm run test)` → 32 pass / 0 fail / 0 skip |
| T4 | build | `(cd frontend && npm run build)` → green |
| T5 | emoji audit | `grep -rIEn "[full emoji pattern from BACKLOG #98]" frontend/src/views/admin/` → 0 hits |
| T6 | routes preserved | `grep -cE "views/admin" frontend/src/router/index.ts` → 7 |
| T7 | guards preserved | `grep -E "roleGuard\('admin'\)" frontend/src/router/index.ts` → 1 hit (parent) |
| T8 | TD-FE-ROLE-SWITCH preserved | `grep -c "TD-FE-ROLE-SWITCH" frontend/src/views/admin/AdminProfileView.vue` → existing count preserved |
| T9 | paramiko deploy A clean | `python deploy script` → exit 0 + service Healthy + visual verify A reply |

## Exit Criteria

- [ ] T1-T9 all pass
- [ ] MEGA-4 commit pushed: `phase: S4 P15 admin-refresh — DONE — speedrun (MEGA-4)`
- [ ] paramiko deploy completes A clean
- [ ] admin store decision documented (create OR continue with rationale)
- [ ] S4 closure commit pushed: `sprint: S4 master-admin — CLOSED — speedrun continuation`

## Risks

1. **Admin store decision underestimated** — if C66 spike reveals 3+ views need shared state (not 0-1 expected), create-path expands to 2+ cycles.
2. **AdminMasterReviewView verify/reject flow** — these are destructive actions. VModal confirm-modal must be reliable; regression risk if patterns from MEGA-1 (Callout) misapplied.
3. **AdminConsistencyView probe rendering** — backend response shape unclear from generated.ts grep (no `ConsistencyDetailResponse` visible); may require live API call inspection during cycle.
4. **TD-FE-ROLE-SWITCH preservation** — analogous risk to MasterProfileView (P14 C65); admin → user mode toggle must remain functional.
5. **Emoji cleanup full sweep** — 25 hits scattered across 5 files; cleanup grep at MEGA-4 close must verify 0 in-scope hits across all 7 views.
6. **No `stores/admin.ts` baseline** — if create-path chosen, no precedent in master.ts to copy directly (master.ts is also small, 121 LOC); use bookings.ts or diary.ts patterns from MEGA-1/2 as reference.
