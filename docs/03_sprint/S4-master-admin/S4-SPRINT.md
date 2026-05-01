# SPRINT
> Velo | Sprint 4: Master + Admin Roles Refresh
> Load this file + docs/02_spec/01_Declaration.md + docs/01_refer/ENVIRONMENT.md
> at the start of every working chat.

---

## SPEC
| File | Path |
|------|------|
| Declaration | docs/02_spec/01_Declaration.md |
| Protocols | docs/02_spec/ |

---

## Environment
> See: docs/01_refer/ENVIRONMENT.md
> Override below ONLY if this sprint differs from project defaults.

No overrides. Standard Velo environment + paramiko deploy + speedrun mode (decision #052 continuation of #049).

---

## References
> Stable paths to project documents.

| Doc | Path |
|-----|------|
| ARCHITECTURE | docs/01_refer/ARCHITECTURE.md |
| ENVIRONMENT | docs/01_refer/ENVIRONMENT.md |
| FILE-TREE | docs/01_refer/FILE-TREE.md |
| BACKLOG | docs/01_refer/BACKLOG.md |
| DECISIONS | docs/01_refer/decisions.md |
| BACKEND-COORDINATION | docs/03_sprint/S2-bundle-port/BACKEND-COORDINATION.md |
| DESIGN-DECISIONS-LOG | docs/03_sprint/S2-bundle-port/DESIGN-DECISIONS-LOG.md |
| S3-SNAPSHOT | docs/01_refer/ARCHIVES/SNAPSHOT/S3-SNAPSHOT.md |
| S3-RETRO | docs/01_refer/ARCHIVES/RETRO/S3-RETRO.md |
| P14 | docs/03_sprint/S4-master-admin/P14-master-refresh/P14-master-refresh.md |
| P15 | docs/03_sprint/S4-master-admin/P15-admin-refresh/P15-admin-refresh.md |

---

## Goal

Реализовать master role (10 views) + admin role (7 views) под Velo DS используя UI-mockups на базе user-role patterns + DS elements; designer-batch-independent (decision #050 supersedes #030; decision #051 supersedes #010). Speedrun mode continuation (decision #052 extends #049): 2 MEGA-execute prompts (MEGA-3 = P14 master, MEGA-4 = P15 admin) + 2 commits + closure commit.

## Success Criteria

- 10 master views refreshed под Velo DS (P14 / MEGA-3)
- 7 admin views refreshed под Velo DS (P15 / MEGA-4)
- 0 emoji hits в `frontend/src/views/master/` + `frontend/src/views/admin/` per decision #048 (cleanup 110 hits → 0; verified via emoji audit grep)
- 0 typecheck errors / 0 lint warnings (lint baseline 756 from S1; preserve or reduce)
- All 17 routes + auth-gate state preserved (parent `roleGuard('master')` / `roleGuard('admin')` + `masterStatusGuard` on 5 child routes + `applyGuard` on `/master/apply` standalone)
- TD-FE-ROLE-SWITCH preserved in MasterProfileView + AdminProfileView (uses `useUiStore.uiMode`)
- 2 MEGA commits + 1 closure commit pushed to `new_desing` + paramiko deploy A clean for both MEGA gates

## Out of Scope

- Pixel polish (S5+ polish cluster per #047)
- BACKLOG #100 audit reactivation (S5+ — ProbeKit lite profile run gates production promotion)
- Backend wiring new master/admin endpoints (BEC § A.* + B.* mock-until-ready pattern per #049 + S3 mockMessagesData precedent)
- New admin views beyond current 7 (e.g. AdminWithdrawalResponse-backed view) — deferred S5+
- i18n + a11y backfill (S5+ per BACKLOG #40 + #86)
- master.ts / admin.ts major refactor (point extensions only)
- Test backfill (BACKLOG #44 deferred per #042 inverted in #049/#052)
- Topup flow refresh (per #039 — designer didn't ship)
- Master design batch wait (BACKLOG #72 — supersede via #050)
- Admin design batch wait (no separate BACKLOG; supersede via #051)

---

## Phases

### Phase 14: Master Role Refresh
**Goal:** 10 master views refreshed под Velo DS + emoji cleanup (85 hits → 0) + master.ts point extensions
**Entry:** S2-S3 closure commit pushed; designer-batch-independent decision #050 ratified in this S4-SPRINT.md
**Exit:** 10 views refreshed, 0 emoji hits в views/master/, typecheck/lint clean, MEGA-3 commit pushed, paramiko deploy A clean
**Detail:** see `P14-master-refresh/P14-master-refresh.md`

### Phase 15: Admin Role Refresh
**Goal:** 7 admin views refreshed под Velo DS + emoji cleanup (25 hits → 0) + admin.ts store decision (create vs continue direct-api)
**Entry:** Phase 14 closed; MEGA-3 commit pushed; admin role unfreeze decision #051 ratified in this S4-SPRINT.md
**Exit:** 7 views refreshed, 0 emoji hits в views/admin/, typecheck/lint clean, MEGA-4 commit pushed, paramiko deploy A clean
**Detail:** see `P15-admin-refresh/P15-admin-refresh.md`

---

## Carry-Forward from S3

Production promotion gates (S5+):
- BACKLOG #100 — audit reactivation (CRITICAL gate)
- BACKLOG #97 — backend `POST /bookings/{id}/leave` endpoint
- BACKLOG #99 — backend public master endpoint + MasterPublicResponse fields
- BACKLOG #96 — `velo update` script transient (CONFIRMED 4/4 deploys ≥600 LOC)
- BEC § A.3 + § A.6 + § A.7 + § A.8 + § B.1 + § B.3 + § B.4 + § B.5 — 23 mock-pending items

---

## Key Decisions

S4-introduced (ratified in this sprint):
- **#050** — Master role implementation independent of designer batch (UI-mockups + user-role pattern reuse) — supersedes #030
- **#051** — Admin role unfreeze for S4 scope — supersedes #010
- **#052** — Speedrun mode S4 continuation — extends #049

S4 inherits (must respect):
- #042 quality > density (inverted via #049/#052 for S4)
- #047 Path Y MEDIUM visual fidelity, polish to S5+
- #048 no-emoji rule + icon-component discipline
- #027 self-deploy via paramiko + `velo update`
- #043 Human-only-relay execution model
- #044 paramiko as primary SSH primitive
- #045 SSH key auth standard

---

## Sprint Context

| Sprint | Status |
|--------|--------|
| S1: Pilot | DONE |
| S2: User Foundation + Booking Flow | DONE (speedrun #049) |
| S3: User Content (Diary + Messages + AI + Profile sub) | DONE (speedrun #049) |
| S4: Master + Admin Roles Refresh | IN PROGRESS |

---

## Current State

| Item | Value |
|------|-------|
| Phase | 14: Master Role Refresh — NOT STARTED |
| Cycle | C55: not started |
| Status | Planning complete, ready for first cycle |
| Tests | 32 pass / 0 fail / 0 skip |

---

## Protocol Log

| Cycle | Protocol | Date | Status |
|-------|----------|------|--------|
| S4-Sprint-Builder | 02_Sprint-Builder | 2026-05-01 | DONE |

---

## Last Session

S4 Sprint-Builder session: reviewed ARCHITECTURE.md (no updates needed — reflects post-MEGA-2 state), defined sprint scope (master + admin roles in single sprint via 2 MEGA-execute prompts per Human directive), ran scout (10 master + 7 admin views inventory + 110 emoji hits + 31 reusable shared components + 20 master/admin domain types in generated.ts; stores/admin.ts confirmed absent; api/payouts.ts confirmed absent — withdrawal lives in api/masters.ts), planned 2 phases (P14 master 11 cycles C55-C65 with EditPracticeView split into 2 cycles per 988 LOC; P15 admin 8 cycles C66-C73 + closure C74). Three new decisions ratified: #050 (master designer-independent), #051 (admin unfreeze), #052 (speedrun S4 continuation).

---

## Next Action

Open new chat with Session Code S4-P14-C55. Run 03_Phase-Builder OPEN — plan first cycle (C55: MasterPendingView refresh — pattern warmup, 260 LOC, simplest master view).

---

## For Human

> Next chat instruction. Copy-paste.

**Session Code:** S4-P14-C55
**Load:**
1. Framework: 01_Declaration.md + 03_Phase-Builder.md
2. Project: ENVIRONMENT.md + ARCHITECTURE.md + FILE-TREE.md + BACKLOG.md + decisions.md
3. Sprint: S4-SPRINT.md + P14-master-refresh.md + BACKEND-COORDINATION.md + DESIGN-DECISIONS-LOG.md
**Run:** 03_Phase-Builder OPEN — plan first cycle (C55 MasterPendingView)

---

## Plan vs Reality

> Filled at 04_Sprint-Closer. Empty during sprint.

| Aspect | Planned | Actual | Delta |
|--------|---------|--------|-------|
| Phases | 2 | — | — |
| Cycles | 19 (C55-C73) + closure C74 | — | — |
| MEGA prompts | 2 | — | — |
| Duration | speedrun (per #052) | — | — |

### What Worked
(filled at close)

### What Didn't
(filled at close)

### Carry Forward
(filled at close)

---
*S4-SPRINT.md*
*Velo | Sprint 4: Master + Admin Roles Refresh*
