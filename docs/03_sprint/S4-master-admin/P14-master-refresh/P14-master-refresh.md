# Phase 14: Master Role Refresh
> Sprint 4: Master + Admin Roles Refresh
> Status: NOT STARTED
> Mode: speedrun (decision #052 continuation of #049) — single MEGA-3 execute prompt covers all 11 cycles

## Goal

Refresh 10 master role views под Velo DS using UI-mockups on user-role patterns + speedrun shared components. Emoji cleanup per #048 (85 hits → 0 in `views/master/`). master.ts point extensions where needed (analogous to bookings.ts MEGA-1 + diary.ts MEGA-2 patterns). Designer-batch-independent per #050.

## Entry Condition

- S2-S3 closure commit `af39b41` (or successor) on `new_desing`
- S4-SPRINT.md created with decision #050 ratified
- All 31 speedrun shared components present in `frontend/src/components/shared/` (verified at scout)
- generated.ts post-S2 P05 C15 self-host regen (20 master/admin domain types confirmed)

## Exit Condition

- All 10 master views refreshed (no glass / no emoji / Velo DS tokens / Path Y MEDIUM fidelity)
- Routes preserved: 10 master path entries unchanged in router/index.ts
- Guards preserved: parent `roleGuard('master')` + `masterStatusGuard` on 5 child routes + `applyGuard` on `/master/apply` standalone
- TD-FE-ROLE-SWITCH preserved in MasterProfileView (uses `useUiStore.uiMode`)
- master.ts extension landed (point extensions only — no major refactor)
- Emoji audit: `grep -rIEn "[emoji_pattern]" frontend/src/views/master/` returns 0 in-scope hits
- typecheck 0 errors, lint warnings ≤ baseline (756 from S1)
- MEGA-3 commit pushed to `new_desing`
- paramiko deploy via `velo update` returns A clean (or B/C with documented findings)

## Tasks

### C55 — MasterPendingView refresh
**Scope:** `frontend/src/views/master/MasterPendingView.vue` (260 LOC, simplest)
**Cycle type:** standard (Path Y direct port)
**Skin reference:** UI-mockup based on user pattern + DS elements (no designer skin needed; status-pending splash analogous to S1 OAuthLoading splash)
**Pattern reuse:** Callout (amber variant for pending status) + StatCard (if status-detail metrics displayed) + ProfileMenuItem (logout row)
**Emoji cleanup:** count from scout
**Decision refs:** #047 Path Y, #048 no-emoji, #050 designer-independent
**Test:** typecheck pass + visual check (light + dark via VHeader IconTheme)

### C56 — MasterApplyView refresh
**Scope:** `frontend/src/views/master/MasterApplyView.vue` (583 LOC, standalone form)
**Cycle type:** standard
**Skin reference:** UI-mockup based on user form patterns (LoginView/RegisterView/EditProfileView refs from MEGA-1)
**Pattern reuse:** FormShell (existing) + Callout + form field primitives (VInput + VTextarea + VSelect)
**Emoji cleanup:** TBD
**Decision refs:** #047, #048, #050
**Standalone constraint:** no MasterShell wrapper, `applyGuard` (NOT `roleGuard('master')`) preserved
**Test:** typecheck + form validation flow + visual

### C57 — MasterDashboardView refresh
**Scope:** `frontend/src/views/master/MasterDashboardView.vue` (585 LOC)
**Cycle type:** standard
**Skin reference:** Mirror UserDashboardView (skin 10/11) — greeting block + StatCards row + recent practices + financial summary callout
**Pattern reuse:** StatCard, Callout, WeekStrip, MasterCardSummary (if applicable), BookingCard (for upcoming master practices)
**Emoji cleanup:** TBD (12 hits)
**Store extension:** if dashboard needs `myUpcomingPractices` getter — add to master.ts (analogous to bookings.ts upcomingBookings)
**Decision refs:** #047, #048, #050
**Test:** typecheck + visual

### C58 — MasterPracticesView refresh
**Scope:** `frontend/src/views/master/MasterPracticesView.vue` (306 LOC, list)
**Cycle type:** standard
**Skin reference:** MyReservationsView (skin 17) pattern — list with status chips
**Pattern reuse:** PracticeCard (existing) or new MasterPracticeListItem if status-chip variant needed; ReservationCard pattern
**Emoji cleanup:** TBD
**Decision refs:** #047, #048, #050
**CASCADE check:** api/practices.ts shared with user CalendarView; verify no breaking changes
**Test:** typecheck + visual

### C59 — CreatePracticeView refresh
**Scope:** `frontend/src/views/master/CreatePracticeView.vue` (584 LOC, form)
**Cycle type:** standard
**Skin reference:** UI-mockup form + DS elements
**Pattern reuse:** FormShell, VInput, VTextarea, VSelect, mood/icon glyphs from MEGA-1/2
**Emoji cleanup:** TBD (18 hits — highest in master)
**Decision refs:** #047, #048, #050
**Test:** typecheck + form submit flow + visual

### C60 — EditPracticeView extract sub-components
**Scope:** `frontend/src/views/master/EditPracticeView.vue` (988 LOC — split-cycle 1 of 2)
**Cycle type:** standard (refactor)
**Action:** Extract logical sections into sub-components (analogous to MEGA-1 PracticeDetailView extraction). Likely sub-components: practice info section + zoom config section + capacity/pricing section + cancellation modal section.
**Pattern reuse:** FormShell + VModal (replace custom overlay per BACKLOG #48 — confirm-modal unification)
**Decision refs:** #047, #048, #050; addresses BACKLOG #48 partially
**Test:** typecheck + extracted components mount correctly + parent view still functional (regression check)

### C61 — EditPracticeView refresh integration
**Scope:** `frontend/src/views/master/EditPracticeView.vue` (split-cycle 2 of 2)
**Cycle type:** standard
**Action:** Wire extracted sub-components + apply Velo DS visual refresh + emoji cleanup (14 hits)
**Pattern reuse:** confirmed sub-components from C60
**Decision refs:** #047, #048, #050
**Test:** typecheck + edit flow E2E (load → modify → save → reload + verify) + visual

### C62 — AttendanceView refresh
**Scope:** `frontend/src/views/master/AttendanceView.vue` (592 LOC)
**Cycle type:** standard
**Skin reference:** MyReservationsView pattern + status chips
**Pattern reuse:** ReservationCard (status chip variant — Присутствует mint / Не пришёл pink / Late amber); VModal (replace custom overlay per BACKLOG #48)
**Emoji cleanup:** TBD (10 hits)
**BEC ref:** B.4 master-request notes display (mock-until-ready)
**Decision refs:** #047, #048, #050; BACKLOG #48 partial
**Test:** typecheck + attendance mark flow + visual

### C63 — AnalyticsView refresh
**Scope:** `frontend/src/views/master/AnalyticsView.vue` (866 LOC)
**Cycle type:** standard
**Skin reference:** UI-mockup based on AISummaryView (skin 16) + StatCards + Callout patterns
**Pattern reuse:** StatCard, Callout, AICommentaryCard (placeholder for AI insights), MasterCardSummary if cross-master comparison
**Emoji cleanup:** TBD (14 hits, including PRACTICE_TYPE_EMOJI fallback `?? '🧘'` at line 483 → replace with PRACTICE_TYPE_ICON pattern + IconMeditation default)
**BEC ref:** C.2 stats source (frontend computed; existing pattern preserved)
**Decision refs:** #047, #048, #050
**Test:** typecheck + chart render + visual

### C64 — MasterFinanceView refresh
**Scope:** `frontend/src/views/master/MasterFinanceView.vue` (645 LOC)
**Cycle type:** standard
**Skin reference:** UI-mockup based on UserProfile balance display + payout/withdrawal flow
**Pattern reuse:** StatCard (balance + monthly), Callout (withdrawal limits warning), VModal (withdrawal confirm), FormShell (payout details form)
**Emoji cleanup:** TBD
**Critical preserve:** `min_withdrawal_cents` + `withdrawal_fee_cents` reads from `masterStore.profile` (per #022, BACKLOG #26 closed)
**Decision refs:** #047, #048, #050
**Test:** typecheck + withdrawal create flow + visual

### C65 — MasterProfileView refresh
**Scope:** `frontend/src/views/master/MasterProfileView.vue` (732 LOC)
**Cycle type:** standard
**Skin reference:** UserProfileView (skin 70/71) — avatar card + StatCards row + sectioned ProfileMenuItem groups
**Pattern reuse:** StatCard, ProfileMenuItem, Callout
**Critical preserve:** TD-FE-ROLE-SWITCH section (lines 24, 267, 513 per scout) — uses `useUiStore.uiMode` to switch master ↔ user mode UI affordance
**Emoji cleanup:** TBD
**Decision refs:** #047, #048, #050
**Test:** typecheck + role-switch toggle + visual

## Cycles

| Cycle | Type | Name | Status | Date | Result |
|-------|------|------|--------|------|--------|
| C55 | standard | MasterPendingView refresh | TODO | | |
| C56 | standard | MasterApplyView refresh | TODO | | |
| C57 | standard | MasterDashboardView refresh | TODO | | |
| C58 | standard | MasterPracticesView refresh | TODO | | |
| C59 | standard | CreatePracticeView refresh | TODO | | |
| C60 | standard | EditPracticeView extract sub-components | TODO | | |
| C61 | standard | EditPracticeView refresh integration | TODO | | |
| C62 | standard | AttendanceView refresh | TODO | | |
| C63 | standard | AnalyticsView refresh | TODO | | |
| C64 | standard | MasterFinanceView refresh | TODO | | |
| C65 | standard | MasterProfileView refresh | TODO | | |

## Tests Summary

| # | Test | Command/Check |
|---|------|---------------|
| T1 | typecheck | `(cd frontend && npm run typecheck)` → 0 errors |
| T2 | lint | `(cd frontend && npm run lint)` → ≤ 756 warnings (S1 baseline) |
| T3 | test | `(cd frontend && npm run test)` → 32 pass / 0 fail / 0 skip |
| T4 | build | `(cd frontend && npm run build)` → green |
| T5 | emoji audit | `grep -rIEn "[full emoji pattern from BACKLOG #98]" frontend/src/views/master/` → 0 hits |
| T6 | routes preserved | `grep -cE "views/master" frontend/src/router/index.ts` → 10 |
| T7 | guards preserved | `grep -E "roleGuard\('master'\)\|masterStatusGuard\|applyGuard" frontend/src/router/index.ts` → 7 hits (1 parent + 5 status + 1 apply) |
| T8 | TD-FE-ROLE-SWITCH preserved | `grep -c "TD-FE-ROLE-SWITCH" frontend/src/views/master/MasterProfileView.vue` → 3 hits (preserved from current count; C60 extraction targets EditPracticeView, not MasterProfileView) |
| T9 | paramiko deploy A clean | `python deploy script` → exit 0 + service Healthy + visual verify A reply |

## Exit Criteria

- [ ] T1-T9 all pass
- [ ] MEGA-3 commit pushed: `phase: S4 P14 master-refresh — DONE — speedrun (MEGA-3)`
- [ ] paramiko deploy completes A clean
- [ ] master.ts extension (if any) committed
- [ ] BACKLOG #48 confirm-modal unification: progress noted (full close OR partial with remaining sites)

## Risks

1. **EditPracticeView 988 LOC split** — if C60 extraction produces >4 sub-components or sub-components themselves exceed 300 LOC, surface in C60 close as scope adjustment (consider C60a + C60b further split).
2. **api/practices.ts CASCADE** — shared with user CalendarView (MEGA-1) + admin (admin masters lookup); any signature change in master refresh must verify user side unchanged.
3. **TD-FE-ROLE-SWITCH preservation** — pattern uses `useUiStore.uiMode`; refresh must not break the toggle. Visual verify must include a switch-to-user-mode test.
4. **masterStatusGuard granularity** — refresh must not change which 5 of 8 child routes use the guard (dashboard / analytics / profile remain exempt).
5. **Emoji cleanup completeness** — scout found 85 hits in master; cleanup grep at MEGA-3 close must verify 0 in-scope hits across all 10 views (not just refreshed ones — full sweep).
