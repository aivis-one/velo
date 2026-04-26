# SPRINT
> Velo | Sprint 2: Bundle-Port Complete
> Load this file + docs/02_spec/01_Declaration.md + docs/01_refer/ENVIRONMENT.md
> at the start of every working chat.
> Status: NOT STARTED (pre-planned in S1-Sprint-Builder session, decision #011)

---

## SPEC
| File | Path |
|------|------|
| Declaration | docs/02_spec/01_Declaration.md |
| Protocols | docs/02_spec/ |

---

## Environment
> See: docs/01_refer/ENVIRONMENT.md

---

## References

| Doc | Path |
|-----|------|
| ARCHITECTURE | docs/01_refer/ARCHITECTURE.md |
| ENVIRONMENT | docs/01_refer/ENVIRONMENT.md |
| BACKLOG | docs/01_refer/BACKLOG.md |
| DECISIONS | docs/01_refer/decisions.md |
| AUDIT-S1 | docs/01_refer/AUDIT-S1.md |
| S1-RETRO | docs/03_sprint/S1-pilot/S1-RETRO.md |
| S1-SNAPSHOT | docs/03_sprint/S1-pilot/S1-SNAPSHOT.md |
| RETRO-S2 | docs/03_sprint/S2-bundle-port/S2-RETRO.md (created at close) |
| Process discipline | docs/01_refer/BACKLOG.md → #10, #17, #33, #34 (apply at prompt-design time) |

---

## Goal
Port всех оставшихся 11 экранов из bundle в Vue + TMA Auth + user journey end-to-end на staging.

## Success Criteria
- 5 port-existing экранов: Calendar, MyReservations, PracticeDetail, CheckIn, StateScreens shared component
- 6 greenfield-port-from-bundle экранов: Onboarding (3 шага), PracticeLive, BookingDetail, BookingSuccess, AISummary, MasterProfilePublic
- TMA Auth полирован (decision #012): Welcome/Launch TMA-only, без OAuth
- KB-sync: screens.md + components.md обновлены под новые компоненты
- Theme toggle infrastructure (stores/ui.ts + localStorage + prefers-color-scheme listener + UI toggle в headers)
- Manual user-journey test: auth → onboarding → dashboard → calendar → practice → booking → check-in → AI summary — в light+dark

## Out of Scope
- User-greenfield экраны без дизайна в bundle (MH-03, MH-09, MH-10, MH-13) — в S3
- Master-side (все) — в S3
- Admin views — BACKLOG
- MH-08 Masters Account, MH-11 Feedback analytics, MH-12 Group report — BACKLOG (decision #010)
- Merge new_desing → main — в S4+

---

## Phases

### Phase 05: Bundle-port Existing Screens (5 cycles)
**Goal:** 5 экранов с аналогами в коде портированы.
**Entry:** S1 closed (Sprint-Closer DONE); AUDIT-S1.md подтверждает что эти 5 — port (keep-visual-replace), не regenerate.
**Exit:** 5 cycles DONE; все экраны работают на staging в обеих темах.

**Cycles:**

| Cycle | Type | Name | Status | Date | Result |
|-------|------|------|--------|------|--------|
| C15 | standard | Port CalendarScreen → CalendarView.vue | TODO | | |
| C16 | standard | Port MyReservationsScreen → MyBookingsView.vue | TODO | | |
| C17 | standard | Port PracticeDetailScreen → PracticeDetailView.vue | TODO | | |
| C18 | standard | Port CheckInScreen → CheckinView.vue | TODO | | |
| C19 | standard+infra | StateScreens shared component + theme toggle infrastructure (stores/ui.ts theme + localStorage + prefers-color-scheme + UI toggle) | TODO | | |

### Phase 06: Bundle Greenfield Screens (6 cycles)
**Goal:** 6 экранов из bundle, которых нет в коде, — создать новые views с bundle как pattern reference.
**Entry:** Phase 05 DONE.
**Exit:** 6 new views + routes созданы; работают на staging.

**Cycles:**

| Cycle | Type | Name | Status | Date | Result |
|-------|------|------|--------|------|--------|
| C20 | standard | Onboarding greenfield: 3 steps → 3 new views + router routes | TODO | | |
| C21 | standard | PracticeLive greenfield → new PracticeLiveView.vue + route | TODO | | |
| C22 | standard | BookingDetail greenfield → new BookingDetailView.vue + route `/user/bookings/:id` | TODO | | |
| C23 | standard | BookingSuccess greenfield → new BookingSuccessView.vue + route (separated from TopupSuccess) | TODO | | |
| C24 | standard | AISummary greenfield → new AISummaryView.vue; endpoint placeholder if missing | TODO | | |
| C25 | standard | MasterProfilePublic greenfield → new views/user/MasterProfilePublicView.vue + route `/user/masters/:id` | TODO | | |

### Phase 07: TMA Auth + KB Sync (2 cycles)
**Goal:** TMA-only Welcome/Auth полностью реализован; KB отражает реальность после S2.
**Entry:** Phase 06 DONE.
**Exit:** AuthView.vue полирован (без OAuth, через platform/telegram.ts initData); screens.md + components.md обновлены.

**Dependency on Human:** handoff из Claude Design на TMA auth до C26.

**Cycles:**

| Cycle | Type | Name | Status | Date | Result |
|-------|------|------|--------|------|--------|
| C26 | standard | TMA Auth polish: WelcomeView расширение, platform/telegram.ts integration, no OAuth UI (HIGH — touches auth boundary) | TODO | | |
| C27 | standard | KB-sync: screens.md + components.md update, Design_prototype_legacy refs cleanup | TODO | | |

### Phase 08: Test + Buffer (4 cycles)
**Goal:** End-to-end user journey test + fix buffer.
**Entry:** Phase 07 DONE.
**Exit:** Manual test report от Human; все bugs fix'нуты или routed в BACKLOG.

**Cycles:**

| Cycle | Type | Name | Status | Date | Result |
|-------|------|------|--------|------|--------|
| C28 | manual-test | User journey end-to-end на staging, light+dark | TODO | | |
| C29 | standard | Fix buffer cycle 1 | TODO | | |
| C30 | standard | Fix buffer cycle 2 | TODO | | |
| C31 | standard | Fix buffer cycle 3 | TODO | | |

---

## Carry-Forward from S1

- **Pre-S2 Human action (out-of-chat):** coordinate with backend partner to (a) document the regen workflow trigger (CI vs pre-commit vs manual) — resolves BACKLOG #24, (b) run a fresh regen against current backend `openapi.json` — unblocks BACKLOG #26 (financial constants migration) and BACKLOG #27 (`PracticeSummary.timezone` schema add → frontend Berlin-fallback removal). Until this completes, the gated entries remain in BACKLOG and S2 cycles work around them with tactical patches.
- **Process discipline lessons** captured at S1 close — apply during S2 scout / execute prompt design: BACKLOG #10 (fallback-syntax-aware grep), #17 (explicit substitution group ordering), #33 (NEGATIVE-grep comment-collision), #34 (FP-01 hex regex over-fire on decision-#NNN refs). See References table for pinned entry.
- **S1-Clean-Sync batch** (between S1-Sprint-Closer and S2-Sprint-Builder): BACKLOG #29 (IconRuble dead-import check), #31 (ENVIRONMENT.md path drift), #35 (ENVIRONMENT.md commit convention cleanup), AUDIT-S1.md §10 #5 (FILE-TREE.md views count). These do NOT block S2 start; cleanup runs in parallel.

## Key Decisions
- (inherited from S1 decisions #006–#014)

---

## Sprint Context

| Sprint | Status |
|--------|--------|
| S1 pilot | (see S1-SPRINT.md) |
| S2 bundle-port | NOT STARTED |
| S3 greenfield | NOT STARTED |

---

## Current State

| Item | Value |
|------|-------|
| Phase | 05: NOT STARTED |
| Cycle | C15: not started |
| Status | Planned ahead in S1-Sprint-Builder session; activates after S1 Sprint-Closer |
| Tests | N/A |

---

## Protocol Log

| Cycle      | Protocol              | Date         | Status |
|------------|-----------------------|--------------|--------|
| (S1-Sprint-Builder planned this sprint) | 02_Sprint-Builder | 2026-04-24 | DONE (planning only) |

---

## Last Session

Pre-planned during S1-Sprint-Builder session (decision #011). Full activation after S1 is closed via 04_Sprint-Closer.

---

## Next Action

После закрытия S1 (04_Sprint-Closer) — run 03_Phase-Builder OPEN для C15.

---

## For Human

**Session Code:** S2-P05-C15 (активируется после S1-Sprint-Closer)
**Load:**
1. Framework: 01_Declaration.md + 03_Phase-Builder.md
2. Project: ENVIRONMENT.md + ARCHITECTURE.md
3. Sprint: S2-SPRINT.md + (AUDIT-S1.md, S1-RETRO.md для контекста)
**Run:** 03_Phase-Builder OPEN — plan first cycle C15

---

## Plan vs Reality

| Aspect | Planned | Actual | Delta |
|--------|---------|--------|-------|
| Phases | 4 | — | — |
| Cycles | 17 | — | — |
| Duration | 4 weeks | — | — |

### What Worked
(filled at close)

### What Didn't
(filled at close)

### Carry Forward
(filled at close)

---
*S2-SPRINT.md*
*Velo | Sprint 2: Bundle-Port Complete*
