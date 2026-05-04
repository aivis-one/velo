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
| Phase | 15: Admin Role Refresh — DONE (verify gate pending) |
| Cycle | C73: AdminConsistencyView refresh — DONE (chat S4-P15-C66 covered all 8 cycles via MEGA-4 + closure C74 in progress) |
| Status | Phase 15 closed at code level; paramiko deploy + combined verify gate (P14 #102 backfill + P15 admin) pending |
| Tests | 32 pass / 0 fail / 0 skip |

---

## Protocol Log

| Cycle | Protocol | Date | Status |
|-------|----------|------|--------|
| S4-Sprint-Builder | 02_Sprint-Builder | 2026-05-01 | DONE |
| S4-P14-C55 | 03_Phase-Builder | 2026-05-01 | DONE |
| S4-P15-C66 | 03_Phase-Builder | 2026-05-04 | DONE (verify gate pending) |

---

## Last Session

S4 P15 admin-refresh executed via single MEGA-4 combined execute prompt covering all 8 cycles (C66-C73) per #052 speedrun. 7 admin views refreshed under Velo DS + admin store decision spike (C66 verdict: continue direct-api; no stores/admin.ts created — rationale: zero shared methods across api/admin.ts, zero cross-view state candidates; Path Y discipline #047). 0 emoji in admin scope (was 25). Lint baseline preserved at 0 warnings (P14 → P15). 0 typecheck errors / 32/32 tests pass / build green / PWA precache 188 → 190 entries (+2 = IconQuestion + ConfirmModal chunk-split; benign). Anti-scope file diffs verified empty (router x3, api x3, stores, components/shared, components/ui, utils x2, package.json). TD-FE-ROLE-SWITCH preserved at 1-marker baseline in AdminProfileView (different from MasterProfileView 4-marker; preserved as-is per Path Y — do NOT normalize across roles). AdminMasterReviewView shipped as degraded v1 — full-fidelity v2 gated on backend extension (BACKLOG #104) exposing master application content (bio/methods/experience/certifications). 1 dead-code method (`getMastersList` in api/admin.ts) deferred to S5+ cleanup per BACKLOG #105. Verification Scout returned 0 BREAK / 0 GAP / 2 NIT (both pre-existing — extractApiError adoption gap covered by BACKLOG #41/#43; #ffffff border pattern from S1 bundle convention).

**P15 deploy operational notes** (post-close 2026-05-04): paramiko deploy of MEGA-4 commit + combined visual verify gate (P14 #102 backfill: 10 master views + P15: 7 admin views; both light/dark themes) pending. Operator runs `velo seed` self-service (per ENVIRONMENT.md §velo CLI commands) to provision admin/master/user roles on operator's chosen Telegram IDs without partner-relay. GAP-noted seed limitations from OPEN scout §S7: AdminMasterReviewView verify/reject flow + AdminReportsView/AdminReportDetailView populated states limited to empty-state cosmetic verify (no pending masters / no Reports in default seed data); functional-flow verify deferred until backend partner extends seed OR S5+ test data injection. Hybrid policy reply A/B/C captured in subsequent hygiene commit.

**P14 deploy operational notes** (preserved for context, post-close 2026-05-01): paramiko deploy of 27a604f succeeded on attempt 1 — BACKLOG #96 transient did not fire (refinement data point logged in #96). Server-side velo-frontend container exhibited a pre-existing healthcheck flap (Up but `unhealthy` per `wget --spider` on port 3000) reproduced post-P14; not a P14 regression — observed since MEGA-2 deploy 2026-04-30. External access via reverse proxy (`https://api.vel-app.com/health`) functional throughout. BACKLOG entry #103 logs the healthcheck flap. Visual verify deferred per Branch 2 (BACKLOG #102) — master-role staging account coordination pending; folded into P15 close combined verify above.

---

## Next Action

Within current chat (S4-P15-C66), run paramiko deploy of MEGA-4 commit → operator runs `velo seed` interactively → operator visual-verifies combined gate (10 master views from P14 #102 backfill + 7 admin views from P15 × {light theme, dark theme}) per checklist issued by Claude Chat. Hybrid policy: A clean → post-verify hygiene commit (close BACKLOG #102, S4-SPRINT.md verify-result narrative, optional NIT entries) → CLOSE Step 5 routing to S4-Sprint-Closer (last phase of S4 → next protocol = 04_Sprint-Closer). B BREAK → inline-fix loop with new commits → re-deploy → re-verify. C NIT → BACKLOG entries during hygiene commit, then close.

---

## For Human

> Next chat instruction. Copy-paste.

**Session Code:** S4-Sprint-Closer
**Load:**
1. Framework: 01_Declaration.md + 04_Sprint-Closer.md
2. Project: ENVIRONMENT.md + ARCHITECTURE.md + FILE-TREE.md + BACKLOG.md + decisions.md
3. Sprint: S4-SPRINT.md + P14-master-refresh.md + P15-admin-refresh.md + BACKEND-COORDINATION.md + DESIGN-DECISIONS-LOG.md
**Run:** 04_Sprint-Closer — Step 1 sprint readiness check + Step 1+ ProbeKit lite profile (deferred per #049/#052 to S5+ per BACKLOG #100; Sprint-Closer should explicitly defer + log status, not run audit) + Step 2-N sprint snapshot/retro/closure

**Note:** Pending visual verify outcome in current chat (S4-P15-C66) before this transition signal triggers. If verify reply is A clean → proceed to Sprint-Closer. If B BREAK → fix-loop in current chat first. If C NIT → BACKLOG hygiene commit, then proceed.

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
