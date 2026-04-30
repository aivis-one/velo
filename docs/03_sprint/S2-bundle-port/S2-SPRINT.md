# SPRINT
> Velo | Sprint 2: User Foundation + Booking Flow
> Load this file + docs/02_spec/01_Declaration.md + docs/01_refer/ENVIRONMENT.md
> at the start of every working chat.
> Status: CLOSED 2026-04-30 (S2-S3-Speedrun closure — see S2-SNAPSHOT.md + S2-RETRO.md)
> Supersedes previous S2-SPRINT.md (which was bundle-port complete)

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
| S1-SNAPSHOT | docs/01_refer/ARCHIVES/SNAPSHOT/S1-SNAPSHOT.md |
| S1-RETRO | docs/01_refer/ARCHIVES/RETRO/S1-RETRO.md |
| S1-AUDIT | docs/01_refer/ARCHIVES/AUDIT/S1-AUDIT.md |
| BACKEND-COORDINATION | docs/03_sprint/S2-bundle-port/BACKEND-COORDINATION.md |
| DESIGN-DECISIONS-LOG | docs/03_sprint/S2-bundle-port/DESIGN-DECISIONS-LOG.md |
| S3-SPRINT (look-ahead) | docs/03_sprint/S3-greenfield/S3-SPRINT.md |
| Process discipline | BACKLOG → #10, #17, #33, #34 (apply at prompt-design time) |

---

## Goal
Реализовать user role часть 1: auth (TMA + PWA fallback hybrid) + onboarding + dashboard + calendar + полный booking/practice/feedback flow + базовый profile. Качество > плотность; тестирование per-cycle на staging.

## Success Criteria

- **Pre-flight (C15):** regen `generated.ts` против свежего openapi.json + миграция consumers; закрытие BACKLOG #26 #27 #32; tactical cast removal в `UserDashboardView.vue:300`.
- **Auth (C16-C19):** WelcomeView расщеплён на TMA-splash + PWA-standalone branches; LoginView + RegisterView + OAuthLoadingView созданы как UI-mock (PWA only).
- **Onboarding (C20-C21):** OnboardingCarouselView (1 view, 3 intro slides + timezone step) + city→IANA resolver работает локально + persistence в localStorage.
- **Dashboard refresh (C22):** UserDashboardView переписан под новую DS; существующая логика (check-in/feedback alerts, AI summary teaser, nearest practice) сохранена.
- **Calendar (C23-C24):** CalendarView + filter overlay; week strip navigation; день-сгруппированный список практик.
- **Theme toggle (C25):** stores/ui.ts.theme + localStorage + prefers-color-scheme listener + UI toggle в headers; работает в обеих темах.
- **Booking/Practice flow (C26-C32):** Practice Detail (paid + free) + Booking Success (с master-request mock) + Booked Practice Detail (15) + Booking Detail (18) + Check-in form + Check-in success + Practice Live + Feedback form + Feedback success.
- **Profile basics (C33-C34):** Profile root + Edit Profile + Delete confirm modal (mock).
- **Manual journey test (C35):** end-to-end auth → onboarding → dashboard → booking → check-in → practice live → feedback flow на staging, light + dark.
- **Self-deploy:** каждый cycle's CLOSE завершается push'ем + `velo update` запуском; визуальная проверка test_account_id 526738615.

## Out of Scope

- Diary в полном объёме → S3 (Phase 10-11)
- Messages → S3 (Phase 12)
- Profile sub-screens (Notifications/Language/Support) → S3 (Phase 12)
- AI summary view (16) → S3 (Phase 12)
- Master profile public view (25) → S3 (Phase 12)
- My Reservations (17) → S3 (Phase 13)
- Master role целиком → S4 (после получения master design batch)
- Admin role → S5+ (BACKLOG #4)
- Group chats для Messages → BACKLOG
- Promo codes UI → BACKLOG (DESIGN-DECISIONS-LOG § A.24)
- Waitlist UI → BACKLOG (DESIGN-DECISIONS-LOG § A.25)
- Real-time messaging / WebSocket → out of scope
- Reports/complaint UI → BACKLOG (DESIGN-DECISIONS-LOG § A.26)

---

## Phases

### Phase 05: Pre-flight — Regen + consumer migration (1 cycle)

**Goal:** очистить tactical debt оставленный в S1 (Berlin fallback, financial constants); регенерировать types.ts против свежего openapi.json.
**Entry:** S1 closed, openapi.json свежий получен от партнёра, deploy capability подтверждён.
**Exit:** typecheck + lint + tests зелёные; UserDashboardView.vue без tactical cast; constants.ts без MIN_WITHDRAWAL_EUROS / WITHDRAWAL_FEE_EUROS; staging push + visual verify pre-existing screens.

| Cycle | Type | Risk | Name | Status |
|-------|------|------|------|--------|
| C15 | standard | MEDIUM | Regen generated.ts + миграция consumers (#26 #27 #32) + S1 deferred C13 visual verification | DONE (2026-04-30) |

**Phase 06 unblock note (2026-04-30):** regen pipeline self-host policy proven (decision #046); auth views can consume any further regen-required types without partner-signal gate.

### Phase 06: Auth + Onboarding (6 cycles)

**Goal:** hybrid auth UX (TMA + PWA standalone) + onboarding carousel + timezone capture.
**Entry:** Phase 05 DONE.
**Exit:** TMA-юзер видит Loading → Dashboard; PWA-юзер видит Welcome → Login/Register/OAuth (mock) → Onboarding → Timezone → Dashboard. Onboarding completion persisted в localStorage.

| Cycle | Type | Risk | Name | Status |
|-------|------|------|------|--------|
| C16 | design-port | HIGH (was MEDIUM — affects-global-state) | WelcomeView refresh: TMA-splash branch + PWA-standalone branch with auth choice CTAs | DONE (2026-04-30) |
| C17 | design-port | LOW | LoginView (PWA only): email + password form + Google/Apple OAuth buttons; mock submit (no backend yet) | DONE (2026-04-30) |
| C18 | design-port | LOW | RegisterView (PWA only): name + email + password + ToS + OAuth; mock submit | DONE (2026-04-30) |
| C19 | design-port | LOW | OAuthLoadingView: post-OAuth callback state (mock) | DONE (2026-04-30) |
| C20 | design-port | MEDIUM | OnboardingCarouselView: 1 view с 3 intro slides + carousel-state (index 0..2) + skip button | DONE (2026-04-30) |
| C21 | design-port | MEDIUM | OnboardingTimezoneView: city input + autocomplete + IANA resolution + PATCH /users/me; complete onboarding flag в localStorage | DONE (2026-04-30) |

### Phase 07: Dashboard + Calendar + Theme infrastructure (4 cycles)

**Goal:** dashboard refresh + calendar + theme toggle infra.
**Entry:** Phase 06 DONE.
**Exit:** Dashboard под новой DS; Calendar week-strip + filter overlay работает; theme toggle в headers рабочий, persist через localStorage; reserved by prefers-color-scheme на first visit.

| Cycle | Type | Risk | Name | Status |
|-------|------|------|------|--------|
| C22 | design-port | HIGH | UserDashboardView refresh под новую DS — переписать поверх S1 P03 C10 work | DONE (2026-04-30, MEGA-1 `6c5fd1f`) |
| C23 | design-port | MEDIUM | CalendarView root: week strip + arrows + day-grouped practice list | DONE (2026-04-30, MEGA-1 `6c5fd1f`) |
| C24 | design-port | LOW | Calendar filter overlay (modal с chip-фильтрами) | DONE (2026-04-30, MEGA-1 `6c5fd1f`) |
| C25 | infra | MEDIUM | Theme toggle infrastructure: stores/ui.ts.theme + localStorage + prefers-color-scheme listener + UI toggle в VHeader/AppHeader; works на dashboard + calendar | DONE (2026-04-30, MEGA-1 `6c5fd1f`) |

**Note C25:** если дизайнер пришлёт dark variants новой DS до начала фазы — реализуется на новых tokens; иначе — на bundle dark tokens (S1 P01).

### Phase 08: Booking + Practice flow (7 cycles)

**Goal:** полный flow от просмотра practice → booking → check-in → live → feedback.
**Entry:** Phase 07 DONE.
**Exit:** все 7 экранов рабочие; happy path юзер бронирует platnoye практику, делает check-in, заходит в Zoom, оставляет feedback; staging проверен test_account_id 526738615.

| Cycle | Type | Risk | Name | Status |
|-------|------|------|------|--------|
| C26 | design-port | MEDIUM | PracticeDetailView (24 + 28 data variant): pre-book paid + free; Master section + Контраиндикации + Забронировать button | DONE (2026-04-30, MEGA-1 `6c5fd1f`) |
| C27 | design-port | MEDIUM | BookingSuccessView (26): hands-clap icon + Запрос мастеру textarea (mock) + В календарь / На главную CTAs | DONE (2026-04-30, MEGA-1 `6c5fd1f`) |
| C28 | design-port | MEDIUM | BookedPracticeView (15) "Моя практика": expanded О практике / Что подготовить / Противопоказания / Check-in перед практикой / Отменить — для day-of-practice context | DONE (2026-04-30, MEGA-1 `6c5fd1f`) |
| C29 | design-port | LOW | BookingDetailView (18): status-confirmation view + ZOOM info + Отменить — для не-immediate booking | DONE (2026-04-30, MEGA-1 `6c5fd1f`) |
| C30 | design-port | MEDIUM | CheckinFormView (12) — 3-icon picker (slider убираем per A.13) + comment + Check-in submit; CheckinSuccessView (13) | DONE (2026-04-30, MEGA-1 `6c5fd1f`) |
| C31 | design-port | HIGH | PracticeLiveView (14): video placeholder + Войти (window.open zoom_link) + Check-in (re-open form 12) + Покинуть практику (POST /bookings/{id}/leave) — touches booking lifecycle | DONE (2026-04-30, MEGA-1 `6c5fd1f`) |
| C32 | design-port | MEDIUM | FeedbackFormView (29): Practice card "Завершена" + 3-button rating + comment + Отправить; FeedbackSuccessView (30) | DONE (2026-04-30, MEGA-1 `6c5fd1f`) |

### Phase 09: Profile basics + S2 close (3 cycles)

**Goal:** базовый Profile + Edit + delete confirm; manual journey test; sprint close.
**Entry:** Phase 08 DONE.
**Exit:** Profile root + Edit Profile + Delete confirm работают; manual journey test report зелёный; sprint closes via 04_Sprint-Closer (separate chat).

| Cycle | Type | Risk | Name | Status |
|-------|------|------|------|--------|
| C33 | design-port | MEDIUM | UserProfileView (70/71): avatar (read-only) + name + email + stats + Аккаунт section + tab bar | DONE (2026-04-30, MEGA-1 `6c5fd1f`) |
| C34 | design-port | LOW | EditProfileView (72) + delete confirm modal (73, native style for mock); avatar tap → toast "Telegram-managed" | DONE (2026-04-30, MEGA-1 `6c5fd1f`) |
| C35 | manual-test + buffer | MEDIUM | End-to-end user journey test на staging (light + dark): auth → onboarding → dashboard → calendar → practice → booking → check-in → live → feedback → profile; bug fix buffer | DONE (2026-04-30, MEGA-1 `6c5fd1f`) |

---

## Carry-Forward from S1

### Closed at this re-plan (2026-04-30) and confirmed at C15 close (2026-04-30)

- BACKLOG #24 (regen workflow) — workflow discipline documented в BACKEND-COORDINATION § D + extended at C15 close with self-host fallback (decision #046)
- BACKLOG #26 (financial constants) — CLOSED at C15: `MIN_WITHDRAWAL_EUROS` + `WITHDRAWAL_FEE_EUROS` removed; MasterFinanceView.vue reads cents from `masterStore.profile`
- BACKLOG #27 (PracticeSummary.timezone Berlin fallback) — CLOSED at C15: cast + `?? 'Europe/Berlin'` fallback removed from UserDashboardView.vue; direct `practice.timezone` read
- BACKLOG #32 (TopupRequest/Response duplicate) — CLOSED at C15: local interfaces removed from `api/payments.ts`; consume via `@/api/types` (decision #023)
- BACKLOG #55 (SERVER-ACCESS.md populate) — closed by S2 P05 OPEN: deploy capability + endpoint + procedure documented
- BACKLOG #37 (S1 C13 manual visual verification) — CLOSED at C15: visual verify gate executed against staging deploy (light + dark, both pilot screens, TG account 526738615); outcome in BACKLOG #37 closure note

### Reduced priority

- BACKLOG #39 (main vs new_desing divergence) — LOW priority. Сервер деплоит из new_desing напрямую (`velo update`), merge в main опциональный/будущий шаг.

### Process discipline (apply at prompt-design time)

- BACKLOG #10 (fallback-syntax-aware grep)
- BACKLOG #17 (explicit substitution group ordering в HIGH-tier prompts)
- BACKLOG #33 (NEGATIVE-grep comment-collision)
- BACKLOG #34 (FP-01 hex regex over-fire on decision-#NNN refs)

### S1 high-priority still open

- BACKLOG #40 a11y polish cluster (3 HIGH from S1 audit)
- BACKLOG #41 design-tokens bulk-tighten
- BACKLOG #42 mobile polish
- BACKLOG #43 view-layer extractApiError adoption
- BACKLOG #44 test-coverage backfill

These are NOT S2 phases — folded into S2 cycles where naturally relevant (e.g. extractApiError adoption in any view-touching cycle).

### NPM audit residual

- BACKLOG #54 (npm audit 5 residual CVEs, dev/build-time only) — paired with #45 major-version bumps; deferred to S5+.

---

## Key Decisions (newly added at re-plan)

### Из этой сессии — добавляются в decisions.md через execute prompt

- **#027** Self-deploy capability — staging deploy unblocked via `velo update` on `new_desing`
- **#028** Hybrid auth model (γ) — TMA primary + email/OAuth для PWA standalone fallback
- **#029** New design batch (2026-04-30) — supersedes bundle SSOT for visual layer; bundle SSOT остаётся для tokens
- **#030** User role split S2+S3; Master role → S4 contingent on designer batch
- **#031** Regen pipeline ad-hoc trigger (manual when partner signals openapi update)
- **#032** Diary layout toggle = single view + state (Variant A)
- **#033** Diary entry type — frontend-side filter chip + backend extension queued
- **#034** Onboarding completion persistence — localStorage v1
- **#035** Mid-practice check-in = upsert (re-open pre-practice form)
- **#036** Welcome view — TMA splash branch + PWA standalone branch (different paths)
- **#037** Practice Live join = external Zoom link via window.open
- **#038** Avatar read-only — Telegram-managed
- **#039** Topup flow as-is from S1 (designer batch missing balance/topup screens)
- **#040** Booking endpoint defaults to /purchase для всех практик (бесплатные тоже через purchase, paid_cents=0) — pending partner clarification
- **#041** Coordination doc format established
- **#042** Sprint scope quality > density — S2/S3 split user role across 2 sprints

### Inherited active

- #006 Bundle SSOT (для tokens; visual layer теперь под новый design batch)
- #007 Flat aesthetic, no glassmorphism
- #008 Dark mode tokens in scope, UI toggle infra in C25
- #009 Bundle namespace tokens
- #010 Admin views deferred to S5+
- #013 VELO = TMA + PWA
- #017 Shadows permitted (clarification of #007)
- #019 CSS via JS imports
- #023 generated.ts SSOT post-regen; types.ts re-export hub

### Inherited superseded by this session

- #012 Bundle AuthScreen NOT 1:1 → SUPERSEDED partially; теперь hybrid model #028 — TMA остаётся initData, PWA standalone получает email/OAuth UI

---

## Sprint Context

| Sprint | Status | Scope summary |
|--------|--------|---------------|
| S1 pilot | CLOSED 2026-04-28 | Bundle migration + audit + 2 pilot screens |
| S2 user foundation | NOT STARTED | Auth + onboarding + dashboard + calendar + booking flow + profile basics |
| S3 user content | PRE-PLANNED | Diary + Messages + Profile sub + AI + bookings refinement |
| S4 master role | PRE-PLANNED (contingent on designer batch) | Master role start |
| S5+ admin + cleanup | BACKLOG | TBD |

---

## Current State

| Item | Value |
|------|-------|
| Phase | All 5 phases DONE (P05-P09) |
| Cycle | All 21 cycles DONE (C15-C35) |
| Status | CLOSED 2026-04-30 (S2-S3-Speedrun closure commit) — see S2-SNAPSHOT.md + S2-RETRO.md |
| Tests | 32/32 pass | Lint 0/0 (cleared from 748 baseline in MEGA-1) | PWA precache 135 (post-MEGA-1) |

---

## Protocol Log

| Cycle      | Protocol              | Date         | Status |
|------------|-----------------------|--------------|--------|
| (S1-Sprint-Builder originally planned this sprint as bundle-port) | 02_Sprint-Builder | 2026-04-24 | DONE then SUPERSEDED |
| (S2-Sprint-Builder re-plan after design batch) | 02_Sprint-Builder | 2026-04-30 | DONE (planning only) |
| C15 / Phase 05 | 03_Phase-Builder OPEN + WORK + CLOSE | 2026-04-30 | DONE — regen + consumer migration. Self-host regen pipeline first applied (decision #046). 5 files modified; 32/32 tests; lint baseline 756 → 752 (−4); generated.ts 762→765 LOC. BACKLOG #26 #27 #32 #37 closed. BACKEND-COORDINATION § E corrected (3 entries) + extended (E.1-E.3 partner-shipped surprises). decision #046 added. Visual verify outcome: GREEN — both pilot screens (WelcomeView, UserDashboardView), both themes (light + dark), no defects. |
| C16 / Phase 06 | 03_Phase-Builder OPEN + WORK + CLOSE | 2026-04-30 | DONE — WelcomeView two-branch refactor + App.vue gate restructure + #47/#49/#50 fold (HIGH, affects-global-state). Path Y first application. Visual verify A clean. Commit cc4e2fd. |
| C17/C18/C19 batch | 03_Phase-Builder WORK | 2026-04-30 | DONE — LoginView + RegisterView + OAuthLoadingView (PWA mock, batch per Rule 16). 3 cycles in 1 commit. Visual verify A clean. Commit b060ba3. |
| C20/C21 batch | 03_Phase-Builder WORK | 2026-04-30 | DONE — OnboardingCarouselView + OnboardingTimezoneView (PWA mock, batch per Rule 16). 2 cycles in 1 commit. cities.json 118 entries. Visual verify A clean. Commit de496f6. |
| Phase 06 CLOSE | 03_Phase-Builder CLOSE | 2026-04-30 | DONE — single docs commit: ARCHITECTURE Phase 06 additions + S2-SPRINT Phase 06 close + decisions #047 Path Y + 4 BACKLOG entries (#93-#96). |
| C22-C35 (P07/P08/P09 batched) | S2-S3 SPEEDRUN MEGA-1 | 2026-04-30 | DONE — 14 cycles in 1 commit (`6c5fd1f`, +5218 LOC, 107 files). UserDashboard refresh + Calendar + theme infra (P07) + 7 booking-flow views (P08) + UserProfile + EditProfile (P09). Decision #048 (no-emoji) first applied. Per BACKLOG #98 — 23 in-scope emoji hits remain (resolved at MEGA-2). Visual verify A clean (TG account 526738615, light + dark). |
| Phase 09 close + Visual verify gate | speedrun aggregate gate | 2026-04-30 | DONE — staging deploy via paramiko (BACKLOG #96 transient on attempt 1, retry succeeded — 3rd recurrence). All 32/32 tests; 0/0 lint. |
| S2 closure commit | 04_Sprint-Closer (speedrun-deferred audit) | 2026-04-30 | DONE — combined S2 + S3 closure commit. SNAPSHOT + RETRO authored. Code Audit deferred to BACKLOG #100 per decision #049. |

---

## Last Session

S2 + S3 closed 2026-04-30 in single closure commit. S2 contributed: P05 regen pipeline (decision #046 first application) + P06 auth/onboarding (Path Y decision #047 first application across cycles C16-C21) + P07/P08/P09 batched in MEGA-1 (commit `6c5fd1f`, +5218 LOC, 107 files; decision #048 no-emoji first application; decision #049 speedrun mode). All 21 cycles closed; visual verify A clean per stage (3 staging deploys: regen `ad4ce7d` + Phase 06 commits + MEGA-1 `6c5fd1f`); BACKLOG #96 size-correlation hypothesis CONFIRMED. Audit deferred to BACKLOG #100 per #049.

---

## Next Action

**SPRINT CLOSED.** This file is immutable history per Sprint-Closer §Step 10.

Future actions:
- S4-Sprint-Builder for master role refresh (per decision #042 + #010).
- Post-demo audit cycle reactivation per BACKLOG #100 (CRITICAL gate before production promotion).
- Backend coordination cycle to wire 23 mock-pending items in BACKEND-COORDINATION.md § A/B/C.

---

## For Human

**Session Code:** S2-S3-SPEEDRUN
**Load:** see HANDOFF-S2-S3-SPEEDRUN.md (artifact created at Phase 06 close 2026-04-30; lists all framework + project + sprint files needed)
**Run:** Combined Scout (Step 1) — covers all S2 remaining + entire S3 cycle inventory.

If you choose standard non-speedrun path: Session Code S2-P07-OPEN; load 01_Declaration.md + 03_Phase-Builder.md + ENVIRONMENT.md + ARCHITECTURE.md + decisions.md + BACKLOG.md + S2-SPRINT.md; run 03_Phase-Builder OPEN for Phase 07 (4 cycles C22-C25).

---

## Sprint Metrics

| Sprint stage | Tests | CRITICAL | HIGH | MEDIUM | LOW | LOC (src/, code-only) |
|--------------|-------|----------|------|--------|-----|------------------------|
| S1 close (baseline, S1-SNAPSHOT) | 32 | 0 | 0 | 0 | 0 | 16,061 |
| S2 in-progress (after P05 C15) | 32 | 0 | 0 | 0 | 0 | 16,045 |
| S2 P06 close | 32 | 0 | 0 | 0 | 0 (3 NIT/GAP logged to BACKLOG) | 17,326 |
| S2 close (post-MEGA-1 `6c5fd1f`) | 32 | N/A — deferred per BACKLOG #100 | — | — | — | 20,157 |

**Trend note (S2 close):** +4,096 LOC from S1 baseline (16,061 → 20,157) on +28 files (Vue +27 + JSON +1). Lint 0/0 (cleared from 748 baseline in MEGA-1 lint:fix pass). Audit cells N/A per decision #049 (speedrun mode); reactivation gate on production promotion via BACKLOG #100. See S2-SNAPSHOT.md for full SNAPSHOT format with cumulative cross-sprint metrics.

## Plan vs Reality

| Aspect | Planned | Actual | Delta |
|--------|---------|--------|-------|
| Phases | 5 (P05-P09) | 5 done | 0 |
| Cycles | 21 (C15-C35) | 21 done | 0 |
| Duration | 4-5 weeks (per-cycle test rhythm) | 1 day (2026-04-30) — P05 + P06 standard rhythm; P07/P08/P09 collapsed into MEGA-1 per speedrun (#049) | −4 weeks (speedrun trade-off explicit per #049) |
| Audit | Sprint-Closer Step 1+ ProbeKit lite | DEFERRED to BACKLOG #100 per #049 | gates production promotion |

### What Worked

(see S2-RETRO.md §What worked for full prose)

- Regen self-host pipeline (#046) closed 3 carry-forward items in C15
- Path Y discipline (#047) at MEDIUM fidelity proven across C16-C21 then scaled to MEGA-1
- Speedrun mode (#049) — 14 cycles in 1 commit on first build attempt
- Hybrid visual verify A reply rate: 3/3 deploys clean
- BACKLOG #96 retry pattern proven 3/3 occurrences in S2 deploys
- Rule 28 Server Action Plan caught wrong-branch push in first deploy

### What Didn't

(see S2-RETRO.md §What didn't work for full prose)

- BACKLOG #92 commit-discipline gap (designer batch referenced before commit; resolved via Rule 29)
- MEGA-1/MEGA-2 split required against handoff (context budget) — not a quality issue, just a planning observation
- `1f37a61` intermediate gitignore commit unplanned (between MEGA-1 and MEGA-2)

### Carry Forward

(authoritative source: S2-SNAPSHOT.md §Carry-Forward)

- BACKLOG #100 — Post-demo audit cycle reactivation (CRITICAL gate)
- BACKLOG #97 — Backend `POST /bookings/{id}/leave` endpoint
- BACKLOG #99 — Backend public master endpoint + MasterPublicResponse fields
- BACKLOG #96 — `velo update` script transient (server-side fix candidate)
- 23 mock-pending items in BACKEND-COORDINATION.md § A/B/C

---

*S2-SPRINT.md*
*Velo | Sprint 2: User Foundation + Booking Flow*
*Re-planned 2026-04-30 (decisions #027-#042)*
