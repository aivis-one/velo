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
| Phase | All phases DONE |
| Cycle | — |
| Status | SPRINT CLOSED |
| Tests | 32 pass / 0 fail / 0 skip |

---

## Protocol Log

| Cycle | Protocol | Date | Status |
|-------|----------|------|--------|
| S4-Sprint-Builder | 02_Sprint-Builder | 2026-05-01 | DONE |
| S4-P14-C55 | 03_Phase-Builder | 2026-05-01 | DONE |
| S4-P15-C66 | 03_Phase-Builder | 2026-05-04 | DONE |
| S4-Sprint-Closer | 04_Sprint-Closer | 2026-05-04 | DONE — Sprint 4 CLOSED |

---

## Last Session

Sprint 4 closed. SNAPSHOT created at `docs/01_refer/ARCHIVES/SNAPSHOT/S4-SNAPSHOT.md`. RETRO created at `docs/01_refer/ARCHIVES/RETRO/S4-RETRO.md`. ProbeKit lite audit DEFERRED per BACKLOG #100 + decision #049/#052 (audit reactivation = production promotion gate, not sprint-close gate). 6 S4 commits (c2b5a90 → 8513424) on `new_desing`; LOC 25,839 (Δ +257 vs S3); 0 typecheck errors / 0 lint warnings / 32/32 tests / build green. BACKLOG #107 appended (S4-Clean-Sync doc-trail hygiene cluster: decisions.md status column drift on #010/#030 + FILE-TREE.md off-by-one in commit 8513424). Plan vs Reality already populated at P15 close — Sprint-Closer Step 10 scope narrowed to Current State / Protocol Log / Last Session / Next Action / For Human only.

---

## Next Action

SPRINT CLOSED.
Next: Session Code S4-Clean-Sync — run 05_Clean-Sync.

---

## For Human
> Next chat instruction. Copy-paste.

**Session Code:** S4-Clean-Sync
**Load:**
1. Framework: 01_Declaration.md + 05_Clean-Sync.md
2. Project: ENVIRONMENT.md + FILE-TREE.md + BACKLOG.md + ARCHITECTURE.md + decisions.md
3. Sprint: S4-SPRINT.md + S4-SNAPSHOT.md
**Run:** 05_Clean-Sync — FILE-TREE refresh + path validation + BACKLOG #107 hygiene cluster (decisions.md #010/#030 status column + FILE-TREE.md components/shared off-by-one) + #101 ARCHITECTURE.md §Key Decisions count refresh + general doc-drift sweep.

**Note:** S4 closed at code + verify level on staging; sprint-close commits land on `new_desing` (HEAD post-Sprint-Closer). ProbeKit lite audit deferred per BACKLOG #100 (production promotion gate, not sprint-close gate).

---

## Plan vs Reality

> Filled at 04_Sprint-Closer. Empty during sprint.

| Aspect | Planned | Actual | Delta |
|--------|---------|--------|-------|
| Phases | 2 | 2 | 0 |
| Cycles | 19 (C55-C73) + closure C74 | 20 (C55-C74) + 1 mid-flow fix cycle (role-switch BREAK) | +1 fix cycle |
| MEGA prompts | 2 | 2 | 0 |
| Duration | speedrun (per #052) | speedrun completed; verify gate added 1 fix-loop iteration | minor extension |

### What Worked

- Speedrun mode (#052) extended through both phases without quality regression (lint preserved at 0 across 2 MEGA prompts + 1 fix commit)
- Combined Scout pattern + 8-section MEGA-4 structure scaled cleanly for 8 cycles in single execute prompt
- Anti-scope discipline (router/api/stores untouched through P15) — verified empty diffs at every gate
- ConfirmModal precedent (P14 §C60) translated cleanly to P15 §C70 + §C72 + post-verify RoleSwitcher (shared-component reuse pattern proven 3× in S4)
- Path Y MEDIUM fidelity decision (#047) held — no premature pixel-polish, post-S4 polish coherent with operator's updated DS

### What Didn't

- Bootstrap prompt assumption that uiMode is 3-value was wrong (binary 'default' | 'user') — surfaced only at scout stage; cost: minor design adjustment in role-switch fix, no rework
- AdminMasterReviewView shipped degraded v1 due to backend type GAP — known going in; BACKLOG #104 tracks; not a process issue
- Verify gate exposed UserProfileView role-switch absence as BREAK — was technically scope-correct (P15 was admin views; user views were P11 era) but visible as user-facing bug; reveals weakness in cross-role test coverage during phase planning

### Carry Forward

- BACKLOG #104 — backend extension for AdminMasterListItem (S5+ backend cycle)
- BACKLOG #105 — getMastersList dead code cleanup (micro-task; fold into any S5 cycle touching api/admin.ts)
- **BACKLOG #106 — S5 MAJOR: full DS stack replacement (Velo bundle → new stack TBD; operator delivers materials at S5 planning) + workflow gap fill (missing/new screens). NOT a polish cluster — project-wide breaking change. Path Y #047 fidelity ceiling explicitly raised for S5.**
- **BACKLOG #106 → S6 split: animation + motion pass deferred to S6 (entry condition: S5 closed, new DS landed). Per operator: "когда накатим основной дизайн".**
- BACKLOG #100 — production audit reactivation (independent S5 entry condition; not DS-related; production promotion gate)
- #96 hypothesis refinement (4/6 ≥600 code-LOC) — continue tracking sample count per future deploy
- #103 frontend healthcheck flap (3 reproductions) — cosmetic deferral; partial backend-partner-owned (docker-compose.yml)

---
*S4-SPRINT.md*
*Velo | Sprint 4: Master + Admin Roles Refresh*
