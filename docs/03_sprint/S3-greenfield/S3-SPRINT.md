# SPRINT
> Velo | Sprint 3: User-Greenfield + Master-Existing + MH-17
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
| S2-SNAPSHOT | docs/03_sprint/S2-bundle-port/S2-SNAPSHOT.md |
| S2-RETRO | docs/03_sprint/S2-bundle-port/S2-RETRO.md |
| RETRO-S3 | docs/03_sprint/S3-greenfield/S3-RETRO.md (created at close) |

---

## Goal
Закрыть user-greenfield (MH-03/09/10/13), портировать master-existing views, реализовать MH-17 Masters Practice room.

## Success Criteria
- 5 user-greenfield экранов: MH-03 Post-session feedback, MH-09 Diary ×2 (user + master), MH-10 Dream diary, MH-13 User profile — design-gen в Claude Design + port в Vue
- Master-existing 10 views из views/master/ audited: keep / tweak / regenerate per AUDIT cycle C40
- MH-17 Masters Practice room greenfield: design-gen + port + api/types.ts integration
- Manual master-journey test на staging в обеих темах

## Out of Scope
- MH-08 Masters Account → BACKLOG (decision #010)
- MH-11 Feedback analytics → BACKLOG
- MH-12 Group report → BACKLOG
- Admin views 7 files → BACKLOG
- Merge new_desing → main — в S4+
- velo-mockups/ + Design_prototype_legacy_* cleanup — в S4+

---

## Phases

### Phase 09: User-Greenfield (8 cycles)
**Goal:** 5 user-facing экранов без bundle и без полной реализации — design-gen + port.
**Entry:** S2 closed (04_Sprint-Closer DONE); handoff'ы для design-gen готовятся Human в Claude Design по мере проходки.
**Exit:** 5 экранов работают на staging в обеих темах.

**Cycles (design-gen / port pairs):**

| Cycle | Type | Name | Status | Date | Result |
|-------|------|------|--------|------|--------|
| C32 | design-gen | MH-03 Post-session feedback screen design-gen в Claude Design | TODO | | |
| C33 | standard | MH-03 port → FeedbackView.vue full implementation | TODO | | |
| C34 | design-gen | MH-09 Diary user + MH-10 Dream diary — design-gen в одном cycle | TODO | | |
| C35 | standard | MH-09 user port → DiaryView.vue + MH-10 port → new DreamDiaryView.vue + route | TODO | | |
| C36 | design-gen | MH-13 User profile design-gen | TODO | | |
| C37 | standard | MH-13 port → UserProfileView.vue | TODO | | |
| C38 | design-gen | MH-09 Diary master-side design-gen | TODO | | |
| C39 | standard | MH-09 master port → new views/master/MasterDiaryView.vue + route | TODO | | |

### Phase 10: Master-Existing Audit + Port (6 cycles)
**Goal:** 10 master views audited; значимые регенерации выполнены.
**Entry:** Phase 09 DONE.
**Exit:** Master-existing views соответствуют bundle визуальному языку; AUDIT C40 verdict'ы реализованы.

**Cycles:**

| Cycle | Type | Name | Status | Date | Result |
|-------|------|------|--------|------|--------|
| C40 | scout | Audit views/master/ 10 views vs bundle visual language: keep/tweak/regenerate verdict each | TODO | | |
| C41 | standard | Master port/regen cycle 1 (scope per C40) | TODO | | |
| C42 | standard | Master port/regen cycle 2 | TODO | | |
| C43 | standard | Master port/regen cycle 3 | TODO | | |
| C44 | standard | Master port/regen cycle 4 | TODO | | |
| C45 | standard | Master port/regen cycle 5 | TODO | | |

### Phase 11: MH-17 Masters Practice Room (3 cycles)
**Goal:** MH-17 реализован end-to-end.
**Entry:** Phase 10 DONE; api/types.ts contains endpoints для MH-17 (если missing → backlog-coord первым шагом).
**Exit:** Master Practice room работает на staging.

**Cycles:**

| Cycle | Type | Name | Status | Date | Result |
|-------|------|------|--------|------|--------|
| C46 | design-gen | MH-17 Masters Practice room design-gen в Claude Design | TODO | | |
| C47 | standard | MH-17 port → new views/master/MasterPracticeRoomView.vue + route | TODO | | |
| C48 | standard | MH-17 integration: api/types.ts check + use stores/master (HIGH if endpoints missing) | TODO | | |

### Phase 12: Master Test + Buffer + KB Sync (2 cycles)
**Goal:** End-to-end master journey test + KB-sync + buffer.
**Entry:** Phase 11 DONE.
**Exit:** Manual test report; screens.md + components.md обновлены; все S3 findings routed.

**Cycles:**

| Cycle | Type | Name | Status | Date | Result |
|-------|------|------|--------|------|--------|
| C49 | manual-test + KB-sync | Master journey end-to-end staging light+dark + screens.md/components.md update | TODO | | |
| C50 | standard | Fix buffer (1 cycle на post-test баги) | TODO | | |

---

## Carry-Forward from S2
> Filled at S2 Sprint-Closer.

## Key Decisions
- (inherited from S1/S2 decisions)

---

## Sprint Context

| Sprint | Status |
|--------|--------|
| S1 pilot | (see S1-SPRINT.md) |
| S2 bundle-port | (see S2-SPRINT.md) |
| S3 greenfield | NOT STARTED |

---

## Current State

| Item | Value |
|------|-------|
| Phase | 09: NOT STARTED |
| Cycle | C32: not started |
| Status | Pre-planned ahead; activates after S2 Sprint-Closer |
| Tests | N/A |

---

## Protocol Log

| Cycle      | Protocol              | Date         | Status |
|------------|-----------------------|--------------|--------|
| (S1-Sprint-Builder planned this sprint) | 02_Sprint-Builder | 2026-04-24 | DONE (planning only) |

---

## Last Session

Pre-planned during S1-Sprint-Builder session (decision #011). Full activation after S2 Sprint-Closer.

---

## Next Action

После закрытия S2 — run 03_Phase-Builder OPEN для C32.

---

## For Human

**Session Code:** S3-P09-C32 (активируется после S2-Sprint-Closer)
**Load:**
1. Framework: 01_Declaration.md + 03_Phase-Builder.md
2. Project: ENVIRONMENT.md + ARCHITECTURE.md
3. Sprint: S3-SPRINT.md + (AUDIT-S1.md, S2-RETRO.md для контекста)
**Run:** 03_Phase-Builder OPEN — plan first cycle C32

---

## Plan vs Reality

| Aspect | Planned | Actual | Delta |
|--------|---------|--------|-------|
| Phases | 4 | — | — |
| Cycles | 19 | — | — |
| Duration | 4–5 weeks | — | — |

### What Worked
(filled at close)

### What Didn't
(filled at close)

### Carry Forward
(filled at close)

---
*S3-SPRINT.md*
*Velo | Sprint 3: User-Greenfield + Master-Existing + MH-17*
