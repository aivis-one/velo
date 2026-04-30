# SPRINT
> Velo | Sprint 3: User Content (Diary + Messages + AI + Profile sub)
> Load this file + docs/02_spec/01_Declaration.md + docs/01_refer/ENVIRONMENT.md
> at the start of every working chat.
> Status: CLOSED 2026-04-30 (S2-S3-Speedrun closure — see S3-SNAPSHOT.md + S3-RETRO.md)
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
| C36 | design-port | HIGH | DiaryView root (40/41) — timeline + list layout toggle (single view, state в localStorage); spine connectors на timeline; flat cards на list | DONE (2026-04-30, MEGA-2 `af39b41`) |
| C37 | design-port | MEDIUM | Diary filter overlay (42/43): chip filters + date picker collapsed/expanded states | DONE (2026-04-30, MEGA-2 `af39b41`) |
| C38 | design-port | MEDIUM | Diary search overlay (44): input field + history list (localStorage); placeholder result rendering (без реального backend search) | DONE (2026-04-30, MEGA-2 `af39b41`) |
| C39 | design-port | MEDIUM | Diary sub-routes: Check-ins (45/46) / Feedbacks (47/48) / Entries Дневник + Сонник with type-filter chip (49/50/51) — все share root Diary layout toggle | DONE (2026-04-30, MEGA-2 `af39b41`) |
| C40 | design-port | HIGH | Diary entry composer expand: collapsed input → tap → expanded form (textarea + title + mood picker + practice picker); POST /api/v1/diary с full payload | DONE (2026-04-30, MEGA-2 `af39b41`) |
| C41 | refactor | LOW | Diary type-filter implementation: client-side filter chip + placeholder атрибут на DiaryEntry; readme в коде "migrate when backend B.1 lands" | DONE (2026-04-30, MEGA-2 `af39b41`) |

### Phase 11: Diary entry detail + relationships (4 cycles)

**Goal:** entry detail view + edit/delete + relationships visualization.
**Entry:** Phase 10 DONE.
**Exit:** entry view работает с action menu, delete (с undo snackbar), edit mode; relationships view показывает chain + AI commentary state; staging проверен.

| Cycle | Type | Risk | Name | Status |
|-------|------|------|------|--------|
| C42 | design-port | MEDIUM | DiaryEntryView (52/56): view entry в read mode — practice card + check-in chip / entry text + "Найдена взаимосвязь" CTA | DONE (2026-04-30, MEGA-2 `af39b41`) |
| C43 | design-port | MEDIUM | DiaryEntryView states: action menu (57) edit/delete buttons + delete with undo snackbar (58) | DONE (2026-04-30, MEGA-2 `af39b41`) |
| C44 | design-port | MEDIUM | DiaryEntryView edit mode (59): textarea editable + Сохранить button + cancel handling | DONE (2026-04-30, MEGA-2 `af39b41`) |
| C45 | design-port | HIGH | RelationshipsView (53/54/55): day header + entry + check-in cards + AI commentary card variant + chained icons state | DONE (2026-04-30, MEGA-2 `af39b41`) |

### Phase 12: Profile sub + Messages + AI (6 cycles)

**Goal:** все sub-views Profile + Messages full mock + AI summary + Master profile public view.
**Entry:** Phase 11 DONE.
**Exit:** все 6 экранов работают; Messages выглядит полнофункциональным на placeholder data; AI summary показывает фейковые еженедельные данные; Master public profile линкуется из booking flow.

| Cycle | Type | Risk | Name | Status |
|-------|------|------|------|--------|
| C46 | design-port | LOW | NotificationsView (74): 4 toggles (Push / Напоминания / От мастеров / От поддержки), localStorage mock state | DONE (2026-04-30, MEGA-2 `af39b41`) |
| C47 | design-port | MEDIUM | LanguageTimezoneView (75): язык интерфейса (Русский/English) + timezone city picker (re-uses S2 C21 city resolver) | DONE (2026-04-30, MEGA-2 `af39b41`) |
| C48 | design-port | LOW | SupportFormView (76): subject + message textarea + Отправить (mock submit, toast "сообщение отправлено") | DONE (2026-04-30, MEGA-2 `af39b41`) |
| C49 | design-port | HIGH | MessagesListView (80) + ThreadView (81/82): полный UI on placeholder data (3 fake conversations + thread messages); send-button toast "скоро будет"; unread badges; counterparty display (master/support) | DONE (2026-04-30, MEGA-2 `af39b41`) |
| C50 | design-port | MEDIUM | AISummaryView (16): "Саммари недели" header + recommendations list; placeholder text from constant; linked from Dashboard | DONE (2026-04-30, MEGA-2 `af39b41`) |
| C51 | design-port | MEDIUM | MasterProfilePublicView (25): avatar + Верифицирован + опыт + bio + методы chips + Ближайшие практики + Задать вопрос (links to Messages thread) | DONE (2026-04-30, MEGA-2 `af39b41`) |

### Phase 13: Bookings refinement + sprint close (3 cycles)

**Goal:** My Reservations реализован + end-to-end test + close.
**Entry:** Phase 12 DONE.
**Exit:** My Reservations показывает корректно past/upcoming с правильными status chips; manual journey test пройден; KB sync если необходимо; sprint closes.

| Cycle | Type | Risk | Name | Status |
|-------|------|------|------|--------|
| C52 | design-port | MEDIUM | MyReservationsView (17): Предстоящие / Прошедшие sections + status chips ("Завтра" / "Завершена" / "Отменена" / "Пропущена" для no_show) + tap → BookingDetail (18) или BookedPracticeView (15) per timing logic | DONE (2026-04-30, MEGA-2 `af39b41`) |
| C53 | manual-test + buffer | MEDIUM | End-to-end S3 user journey test на staging (light + dark): dashboard → diary creation → diary categories navigation → entry detail → relationships → messages → profile sub-screens → my reservations; bug fix buffer | DONE (2026-04-30, MEGA-2 `af39b41`) |
| C54 | refactor + KB-sync | LOW | KB sync (если screens.md/components.md существуют) + Architecture compliance check + cleanup; sprint close handoff to 04_Sprint-Closer | DONE (2026-04-30, MEGA-2 `af39b41`) |

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
| S2 user foundation | CLOSED 2026-04-30 | Auth + onboarding + dashboard + calendar + booking flow + profile basics |
| S3 user content | CLOSED 2026-04-30 | Diary + Messages + Profile sub + AI + bookings refinement |
| S4 master role | PRE-PLANNED (contingent on designer batch) | Master role start |
| S5+ admin + cleanup | BACKLOG | TBD |

---

## Current State

| Item | Value |
|------|-------|
| Phase | All 4 phases DONE (P10-P13) |
| Cycle | All 19 cycles DONE (C36-C54) |
| Status | CLOSED 2026-04-30 (S2-S3-Speedrun closure commit) — see S3-SNAPSHOT.md + S3-RETRO.md |
| Tests | 32/32 pass | Lint 0/0 (maintained from MEGA-1 baseline) | PWA precache 180 (post-MEGA-2) |

---

## Protocol Log

| Cycle      | Protocol              | Date         | Status |
|------------|-----------------------|--------------|--------|
| (S1-Sprint-Builder originally planned S3 as user-greenfield + master-existing) | 02_Sprint-Builder | 2026-04-24 | DONE then SUPERSEDED |
| (S2-Sprint-Builder re-plan after design batch) | 02_Sprint-Builder | 2026-04-30 | DONE (planning only) |
| C36-C52 (P10/P11/P12/P13 batched) | S2-S3 SPEEDRUN MEGA-2 | 2026-04-30 | DONE — 17 cycles in 1 commit (`af39b41`, +6443 LOC, 65 files). Diary refresh + Messages + AI summary + Master public + Reservations + Notifications + Language/TZ + Support form + 14 new icons. BACKLOG #98 emoji carry RESOLVED (0 in-scope hits). Visual verify A clean. |
| C53 Visual verify gate | speedrun aggregate gate | 2026-04-30 | DONE — staging deploy via paramiko (BACKLOG #96 transient on attempt 1, retry succeeded — 4th recurrence, hypothesis CONFIRMED). All services Healthy on staging. |
| C54 closure commit | 04_Sprint-Closer (speedrun-deferred audit) | 2026-04-30 | DONE — combined S2 + S3 closure commit. SNAPSHOT + RETRO authored. Code Audit deferred to BACKLOG #100 per decision #049. |

---

## Last Session

S3 closed 2026-04-30 in single closure commit alongside S2. S3 contributed: full Diary refresh (P10 = root + filter + search + 3 sub-routes + composer expand + type-filter cleanup) + Diary entry detail (P11 = read + edit + delete with undo + relationships placeholder) + Profile sub-views + Messages + AI summary + Master public (P12 = 6 cycles incl. degraded v1 per #99) + Reservations (P13 C52). 17 implementation cycles batched in MEGA-2 (commit `af39b41`); C53 visual verify A clean; C54 = closure commit (this commit). BACKLOG #98 emoji carry RESOLVED at MEGA-2 close.

---

## Next Action

**SPRINT CLOSED.** This file is immutable history per Sprint-Closer §Step 10.

Future actions:
- S4-Sprint-Builder for master role refresh (per decision #042 + #010).
- Post-demo audit cycle reactivation per BACKLOG #100 (CRITICAL gate before production promotion).
- Backend coordination cycle to wire 23 mock-pending items in BACKEND-COORDINATION.md § A/B/C.

---

## Plan vs Reality

| Aspect | Planned | Actual | Delta |
|--------|---------|--------|-------|
| Phases | 4 (P10-P13) | 4 done | 0 |
| Cycles | 19 (C36-C54) | 19 done | 0 |
| Duration | 4-5 weeks (per-cycle test rhythm) | 1 day (2026-04-30) — all 17 implementation cycles in MEGA-2; C53 visual verify + C54 closure same day | −4 weeks (speedrun trade-off explicit per #049) |
| Audit | Sprint-Closer Step 1+ ProbeKit lite | DEFERRED to BACKLOG #100 per #049 | gates production promotion |

### What Worked

(see S3-RETRO.md §What worked for full prose)

- Single MEGA-execute prompt covering 17 cycles produced 65 files / +6443 LOC / 0 errors on first build attempt
- mockMessagesData inline pattern (C49) proven for backend-pending features
- Degraded v1 strategy (C51) demonstrated as named pattern with explicit BACKLOG entry (#99)
- ProfileMenuItem reuse across 6+ rows validated component extraction approach
- BACKLOG #98 emoji audit pattern resolved cleanly (12 files touched + audit grep returned 0 in-scope hits)
- Composer expand modal split (C40) — collapsed pill vs full-screen modal as separate components

### What Didn't

(see S3-RETRO.md §What didn't work for full prose)

- Bash-bridge stdout buffering on Windows held first MEGA-2 deploy output for ~10 minutes (single occurrence; not blocking)
- "Already up to date" race when retrying after lost output (briefly ambiguous deploy state for ~30s)
- Spine ornament SVG glyphs deferred (Path Y MEDIUM uses text characters; ornate work to S5+ polish)

### Carry Forward

(authoritative source: S3-SNAPSHOT.md §Carry-Forward)

- BACKLOG #100 — Post-demo audit cycle reactivation (CRITICAL gate before production promotion)
- BACKLOG #97 — Backend `POST /bookings/{id}/leave` endpoint (mid-practice exit semantics)
- BACKLOG #99 — Backend public master endpoint + MasterPublicResponse fields (lifts C51 to full skin 25 fidelity)
- BACKLOG #96 — `velo update` script transient (CONFIRMED 4/4 deploys ≥600 LOC; server-side fix candidate)
- 23 mock-pending items in BACKEND-COORDINATION.md § A/B/C (search, support, messages, AI commentary, language enum, master public stats, leave endpoint)
- Cities.json expansion (BACKLOG #95)
- i18n (BACKLOG #86)
- Spine ornament SVG glyphs (S5+ polish cluster)
- Master/admin emoji cleanup (~145 hits remaining; S4/S5+ scope per decision #048)

---

*S3-SPRINT.md*
*Velo | Sprint 3: User Content (Diary + Messages + AI + Profile sub)*
*Re-planned 2026-04-30 (decisions #027-#042 inherited from S2 re-plan)*
