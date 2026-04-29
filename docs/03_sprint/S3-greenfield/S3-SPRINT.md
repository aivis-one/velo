# SPRINT
> Velo | Sprint 3: User Content (Diary + Messages + AI + Profile sub)
> Load this file + docs/02_spec/01_Declaration.md + docs/01_refer/ENVIRONMENT.md
> at the start of every working chat.
> Status: NOT STARTED — re-planned 2026-04-30 after new design batch arrival
> Supersedes previous S3-SPRINT.md (which was user-greenfield + master-existing)

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
| FILE-TREE | docs/01_refer/FILE-TREE.md |
| S2-SPRINT | docs/03_sprint/S2-bundle-port/S2-SPRINT.md |
| S2-SNAPSHOT | docs/01_refer/ARCHIVES/SNAPSHOT/S2-SNAPSHOT.md (created at S2 close) |
| S2-RETRO | docs/01_refer/ARCHIVES/RETRO/S2-RETRO.md (created at S2 close) |
| BACKEND-COORDINATION | docs/03_sprint/S2-bundle-port/BACKEND-COORDINATION.md |
| DESIGN-DECISIONS-LOG | docs/03_sprint/S2-bundle-port/DESIGN-DECISIONS-LOG.md |

---

## Goal
Реализовать user role часть 2: полный Diary (timeline + list toggle + 4 sub-категории + entry detail + relationships + composer expand) + Messages (full UI mock) + Profile sub-screens (notifications/language/support, mock) + AI summary view + bookings refinement (My Reservations) + Master profile public view.

## Success Criteria

- **Diary core (C36-C41):** root /diary с timeline+list toggle (state in localStorage); filter overlay + date picker; search overlay (mock результаты); sub-router (Check-ins / Feedbacks / Entries Дневник + Сонник via type-filter chip); composer expand с full form; типизация entries client-side через placeholder атрибут.
- **Diary entry detail (C42-C45):** view entry (read mode) + action menu state (edit/delete buttons) + delete with undo snackbar + edit mode + relationships view (chain icons + AI commentary state).
- **Profile sub + Messages + AI (C46-C51):** Notifications (localStorage mock) + Language/Timezone view + Support form (mock submit) + Messages list + Thread (full UI on placeholder data) + AI summary view (placeholder weekly text) + Master profile public view (public detail с практиками + "Задать вопрос").
- **Bookings refinement (C52-C53):** My Reservations с past/upcoming sections + status chips ("Завтра"/"Завершена"/"Отменена"/"Пропущена" для no_show); end-to-end manual journey test на staging; bug fix buffer.
- **Sprint close (C54):** KB-sync (если применимо) + close через 04_Sprint-Closer.

## Out of Scope

- Master role (10 views) → S4 (после получения master design batch)
- Admin role → S5+ (BACKLOG #4)
- Group chats для Messages → BACKLOG
- Real Messages backend → coordination через BACKEND-COORDINATION § A.7
- Real diary search backend → coordination через § A.3
- Real notification preferences backend → coordination через § A.5
- Real support backend → coordination через § A.6
- Real AI weekly summary → coordination через § A.8
- Account deletion implementation → coordination через § A.4
- Promo codes UI → BACKLOG (DESIGN-DECISIONS-LOG § A.24)
- Waitlist UI → BACKLOG (DESIGN-DECISIONS-LOG § A.25)
- Reports/complaints полный UI → BACKLOG (DESIGN-DECISIONS-LOG § A.26)
- Topup redesign → ждём designer batch (DESIGN-DECISIONS-LOG § B.14)
- Empty/loading/error full mockup parity → minimum viable patterns (S2/S3 inherited approach)

---

## Phases

### Phase 10: Diary core (6 cycles)

**Goal:** root Diary view + 4 sub-categories + filter + search + composer expand.
**Entry:** S2 closed (Sprint-Closer DONE).
**Exit:** /diary рабочий с layout toggle, filter, search; 4 sub-categories доступны через router; entry creation через expanded composer работает + сохраняет в backend.

| Cycle | Type | Risk | Name | Status |
|-------|------|------|------|--------|
| C36 | design-port | HIGH | DiaryView root (40/41) — timeline + list layout toggle (single view, state в localStorage); spine connectors на timeline; flat cards на list | TODO |
| C37 | design-port | MEDIUM | Diary filter overlay (42/43): chip filters + date picker collapsed/expanded states | TODO |
| C38 | design-port | MEDIUM | Diary search overlay (44): input field + history list (localStorage); placeholder result rendering (без реального backend search) | TODO |
| C39 | design-port | MEDIUM | Diary sub-routes: Check-ins (45/46) / Feedbacks (47/48) / Entries Дневник + Сонник with type-filter chip (49/50/51) — все share root Diary layout toggle | TODO |
| C40 | design-port | HIGH | Diary entry composer expand: collapsed input → tap → expanded form (textarea + title + mood picker + practice picker); POST /api/v1/diary с full payload | TODO |
| C41 | refactor | LOW | Diary type-filter implementation: client-side filter chip + placeholder атрибут на DiaryEntry; readme в коде "migrate when backend B.1 lands" | TODO |

### Phase 11: Diary entry detail + relationships (4 cycles)

**Goal:** entry detail view + edit/delete + relationships visualization.
**Entry:** Phase 10 DONE.
**Exit:** entry view работает с action menu, delete (с undo snackbar), edit mode; relationships view показывает chain + AI commentary state; staging проверен.

| Cycle | Type | Risk | Name | Status |
|-------|------|------|------|--------|
| C42 | design-port | MEDIUM | DiaryEntryView (52/56): view entry в read mode — practice card + check-in chip / entry text + "Найдена взаимосвязь" CTA | TODO |
| C43 | design-port | MEDIUM | DiaryEntryView states: action menu (57) edit/delete buttons + delete with undo snackbar (58) | TODO |
| C44 | design-port | MEDIUM | DiaryEntryView edit mode (59): textarea editable + Сохранить button + cancel handling | TODO |
| C45 | design-port | HIGH | RelationshipsView (53/54/55): day header + entry + check-in cards + AI commentary card variant + chained icons state | TODO |

### Phase 12: Profile sub + Messages + AI (6 cycles)

**Goal:** все sub-views Profile + Messages full mock + AI summary + Master profile public view.
**Entry:** Phase 11 DONE.
**Exit:** все 6 экранов работают; Messages выглядит полнофункциональным на placeholder data; AI summary показывает фейковые еженедельные данные; Master public profile линкуется из booking flow.

| Cycle | Type | Risk | Name | Status |
|-------|------|------|------|--------|
| C46 | design-port | LOW | NotificationsView (74): 4 toggles (Push / Напоминания / От мастеров / От поддержки), localStorage mock state | TODO |
| C47 | design-port | MEDIUM | LanguageTimezoneView (75): язык интерфейса (Русский/English) + timezone city picker (re-uses S2 C21 city resolver) | TODO |
| C48 | design-port | LOW | SupportFormView (76): subject + message textarea + Отправить (mock submit, toast "сообщение отправлено") | TODO |
| C49 | design-port | HIGH | MessagesListView (80) + ThreadView (81/82): полный UI on placeholder data (3 fake conversations + thread messages); send-button toast "скоро будет"; unread badges; counterparty display (master/support) | TODO |
| C50 | design-port | MEDIUM | AISummaryView (16): "Саммари недели" header + recommendations list; placeholder text from constant; linked from Dashboard | TODO |
| C51 | design-port | MEDIUM | MasterProfilePublicView (25): avatar + Верифицирован + опыт + bio + методы chips + Ближайшие практики + Задать вопрос (links to Messages thread) | TODO |

### Phase 13: Bookings refinement + sprint close (3 cycles)

**Goal:** My Reservations реализован + end-to-end test + close.
**Entry:** Phase 12 DONE.
**Exit:** My Reservations показывает корректно past/upcoming с правильными status chips; manual journey test пройден; KB sync если необходимо; sprint closes.

| Cycle | Type | Risk | Name | Status |
|-------|------|------|------|--------|
| C52 | design-port | MEDIUM | MyReservationsView (17): Предстоящие / Прошедшие sections + status chips ("Завтра" / "Завершена" / "Отменена" / "Пропущена" для no_show) + tap → BookingDetail (18) или BookedPracticeView (15) per timing logic | TODO |
| C53 | manual-test + buffer | MEDIUM | End-to-end S3 user journey test на staging (light + dark): dashboard → diary creation → diary categories navigation → entry detail → relationships → messages → profile sub-screens → my reservations; bug fix buffer | TODO |
| C54 | refactor + KB-sync | LOW | KB sync (если screens.md/components.md существуют) + Architecture compliance check + cleanup; sprint close handoff to 04_Sprint-Closer | TODO |

---

## Carry-Forward from S2

> Filled at S2 Sprint-Closer.

Expected to include:
- Items closed in S2 Sprint-Closer
- Reduced-priority items
- New process discipline lessons from S2
- High-priority BACKLOG items relevant to S3
- Status of partner-side coordination (regen workflow, missing endpoints)
- Status of designer-side coordination (master batch ETA, dark variants ETA, etc.)

---

## Key Decisions

Inherited from S2 (decisions #027-#042 plus inherited active from S1).

S3-specific decisions (added at S3 Sprint-Builder pre-plan):
- Diary entry detail view + edit/delete pattern: native confirm для destructive + undo snackbar для delete (300ms grace) — alignment with S2 booking cancel pattern
- Messages mock format: 3 conversations × 5-10 messages stored in `frontend/src/utils/mockMessagesData.ts` constant; replace by API client when backend lands

---

## Sprint Context

| Sprint | Status | Scope summary |
|--------|--------|---------------|
| S1 pilot | CLOSED 2026-04-28 | Bundle migration + audit + 2 pilot screens |
| S2 user foundation | NOT STARTED | Auth + onboarding + dashboard + calendar + booking flow + profile basics |
| S3 user content | NOT STARTED | Diary + Messages + Profile sub + AI + bookings refinement |
| S4 master role | PRE-PLANNED (contingent on designer batch) | Master role start |
| S5+ admin + cleanup | BACKLOG | TBD |

---

## Current State

| Item | Value |
|------|-------|
| Phase | 10: NOT STARTED |
| Cycle | C36: not started |
| Status | Pre-planned ahead; activates after S2 Sprint-Closer |
| Tests | N/A |

---

## Protocol Log

| Cycle      | Protocol              | Date         | Status |
|------------|-----------------------|--------------|--------|
| (S1-Sprint-Builder originally planned S3 as user-greenfield + master-existing) | 02_Sprint-Builder | 2026-04-24 | DONE then SUPERSEDED |
| (S2-Sprint-Builder re-plan after design batch) | 02_Sprint-Builder | 2026-04-30 | DONE (planning only) |

---

## Last Session

S3 re-planned 2026-04-30 in same session as S2 re-plan. Reasoning:
1. Original S3 = user-greenfield + master-existing — inappropriate after design batch arrival
2. Master role moved to S4 (contingent on master design batch)
3. User role split S2 + S3 to honor quality > density signal from S1 retrospective
4. S3 covers everything user-facing not in S2: diary heavy + messages mock + profile sub + AI mock + bookings refinement

---

## Next Action

После закрытия S2 (через 04_Sprint-Closer) — run **03_Phase-Builder OPEN** для **Phase 10** (start C36).

---

## For Human

**Session Code:** S3-P10-OPEN (активируется после S2 Sprint-Closer)
**Load:**
1. Framework: 01_Declaration.md + 03_Phase-Builder.md
2. Project: ENVIRONMENT.md + ARCHITECTURE.md + decisions.md + BACKLOG.md + FILE-TREE.md
3. Sprint: S3-SPRINT.md + S2-SNAPSHOT.md + S2-RETRO.md
4. Coord docs: BACKEND-COORDINATION.md + DESIGN-DECISIONS-LOG.md (continuously updated)
**Run:** 03_Phase-Builder OPEN — Phase 10 (Diary core, 6 cycles)

---

## Plan vs Reality

| Aspect | Planned | Actual | Delta |
|--------|---------|--------|-------|
| Phases | 4 | — | — |
| Cycles | 19 (C36-C54) | — | — |
| Duration | 4-5 weeks (per-cycle test rhythm) | — | — |

### What Worked
(filled at close)

### What Didn't
(filled at close)

### Carry Forward
(filled at close)

---

*S3-SPRINT.md*
*Velo | Sprint 3: User Content (Diary + Messages + AI + Profile sub)*
*Re-planned 2026-04-30 (decisions #027-#042 inherited from S2 re-plan)*
