# SPRINT
> Velo | Sprint 2: User Foundation + Booking Flow
> Load this file + docs/02_spec/01_Declaration.md + docs/01_refer/ENVIRONMENT.md
> at the start of every working chat.
> Status: NOT STARTED — re-planned 2026-04-30 after new design batch arrival
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
| C16 | design-port | MEDIUM | WelcomeView refresh: TMA-splash branch + PWA-standalone branch with auth choice CTAs | TODO |
| C17 | design-port | LOW | LoginView (PWA only): email + password form + Google/Apple OAuth buttons; mock submit (no backend yet) | TODO |
| C18 | design-port | LOW | RegisterView (PWA only): name + email + password + ToS + OAuth; mock submit | TODO |
| C19 | design-port | LOW | OAuthLoadingView: post-OAuth callback state (mock) | TODO |
| C20 | design-port | MEDIUM | OnboardingCarouselView: 1 view с 3 intro slides + carousel-state (index 0..2) + skip button | TODO |
| C21 | design-port | MEDIUM | OnboardingTimezoneView: city input + autocomplete + IANA resolution + PATCH /users/me; complete onboarding flag в localStorage | TODO |

### Phase 07: Dashboard + Calendar + Theme infrastructure (4 cycles)

**Goal:** dashboard refresh + calendar + theme toggle infra.
**Entry:** Phase 06 DONE.
**Exit:** Dashboard под новой DS; Calendar week-strip + filter overlay работает; theme toggle в headers рабочий, persist через localStorage; reserved by prefers-color-scheme на first visit.

| Cycle | Type | Risk | Name | Status |
|-------|------|------|------|--------|
| C22 | design-port | HIGH | UserDashboardView refresh под новую DS — переписать поверх S1 P03 C10 work | TODO |
| C23 | design-port | MEDIUM | CalendarView root: week strip + arrows + day-grouped practice list | TODO |
| C24 | design-port | LOW | Calendar filter overlay (modal с chip-фильтрами) | TODO |
| C25 | infra | MEDIUM | Theme toggle infrastructure: stores/ui.ts.theme + localStorage + prefers-color-scheme listener + UI toggle в VHeader/AppHeader; works на dashboard + calendar | TODO |

**Note C25:** если дизайнер пришлёт dark variants новой DS до начала фазы — реализуется на новых tokens; иначе — на bundle dark tokens (S1 P01).

### Phase 08: Booking + Practice flow (7 cycles)

**Goal:** полный flow от просмотра practice → booking → check-in → live → feedback.
**Entry:** Phase 07 DONE.
**Exit:** все 7 экранов рабочие; happy path юзер бронирует platnoye практику, делает check-in, заходит в Zoom, оставляет feedback; staging проверен test_account_id 526738615.

| Cycle | Type | Risk | Name | Status |
|-------|------|------|------|--------|
| C26 | design-port | MEDIUM | PracticeDetailView (24 + 28 data variant): pre-book paid + free; Master section + Контраиндикации + Забронировать button | TODO |
| C27 | design-port | MEDIUM | BookingSuccessView (26): hands-clap icon + Запрос мастеру textarea (mock) + В календарь / На главную CTAs | TODO |
| C28 | design-port | MEDIUM | BookedPracticeView (15) "Моя практика": expanded О практике / Что подготовить / Противопоказания / Check-in перед практикой / Отменить — для day-of-practice context | TODO |
| C29 | design-port | LOW | BookingDetailView (18): status-confirmation view + ZOOM info + Отменить — для не-immediate booking | TODO |
| C30 | design-port | MEDIUM | CheckinFormView (12) — 3-icon picker (slider убираем per A.13) + comment + Check-in submit; CheckinSuccessView (13) | TODO |
| C31 | design-port | HIGH | PracticeLiveView (14): video placeholder + Войти (window.open zoom_link) + Check-in (re-open form 12) + Покинуть практику (POST /bookings/{id}/leave) — touches booking lifecycle | TODO |
| C32 | design-port | MEDIUM | FeedbackFormView (29): Practice card "Завершена" + 3-button rating + comment + Отправить; FeedbackSuccessView (30) | TODO |

### Phase 09: Profile basics + S2 close (3 cycles)

**Goal:** базовый Profile + Edit + delete confirm; manual journey test; sprint close.
**Entry:** Phase 08 DONE.
**Exit:** Profile root + Edit Profile + Delete confirm работают; manual journey test report зелёный; sprint closes via 04_Sprint-Closer (separate chat).

| Cycle | Type | Risk | Name | Status |
|-------|------|------|------|--------|
| C33 | design-port | MEDIUM | UserProfileView (70/71): avatar (read-only) + name + email + stats + Аккаунт section + tab bar | TODO |
| C34 | design-port | LOW | EditProfileView (72) + delete confirm modal (73, native style for mock); avatar tap → toast "Telegram-managed" | TODO |
| C35 | manual-test + buffer | MEDIUM | End-to-end user journey test на staging (light + dark): auth → onboarding → dashboard → calendar → practice → booking → check-in → live → feedback → profile; bug fix buffer | TODO |

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
| Phase | 05: DONE (2026-04-30) |
| Cycle | C15: DONE (2026-04-30) |
| Status | Phase 05 closed; ready for S2-P06-OPEN (auth + onboarding views, C16-C21) |
| Tests | 32/32 pass (final gate before §C5 commits) |

---

## Protocol Log

| Cycle      | Protocol              | Date         | Status |
|------------|-----------------------|--------------|--------|
| (S1-Sprint-Builder originally planned this sprint as bundle-port) | 02_Sprint-Builder | 2026-04-24 | DONE then SUPERSEDED |
| (S2-Sprint-Builder re-plan after design batch) | 02_Sprint-Builder | 2026-04-30 | DONE (planning only) |
| C15 / Phase 05 | 03_Phase-Builder OPEN + WORK + CLOSE | 2026-04-30 | DONE — regen + consumer migration. Self-host regen pipeline first applied (decision #046). 5 files modified; 32/32 tests; lint baseline 756 → 752 (−4); generated.ts 762→765 LOC. BACKLOG #26 #27 #32 #37 closed. BACKEND-COORDINATION § E corrected (3 entries) + extended (E.1-E.3 partner-shipped surprises). decision #046 added. Visual verify outcome: GREEN — both pilot screens (WelcomeView, UserDashboardView), both themes (light + dark), no defects. |

---

## Last Session

S2 re-planned 2026-04-30 in single multi-turn chat session. Triggers:
1. New design batch from designer (55 mockups, ~34 unique views) — supersedes bundle visual layer
2. Backend partner unblocked everything: server access + `velo update` self-deploy + fresh openapi with timezone + financial constants fixes
3. User signal: quality > density после S1 опыта

Decisions recorded inline above (#027-#042). 2 new coordination docs created (BACKEND-COORDINATION + DESIGN-DECISIONS-LOG).

---

## Next Action

Run **03_Phase-Builder OPEN** for **Phase 05** (single cycle C15: regen + consumer migration + S1 C13 visual verify).

---

## For Human

**Session Code:** S2-P05-OPEN
**Load:**
1. Framework: 01_Declaration.md + 03_Phase-Builder.md
2. Project: ENVIRONMENT.md + ARCHITECTURE.md + decisions.md + BACKLOG.md + FILE-TREE.md
3. Sprint: S2-SPRINT.md + S1-SNAPSHOT.md
4. Coord docs: BACKEND-COORDINATION.md + DESIGN-DECISIONS-LOG.md
**Run:** 03_Phase-Builder OPEN — Phase 05 single-cycle pre-flight

---

## Sprint Metrics

| Sprint stage | Tests | CRITICAL | HIGH | MEDIUM | LOW | LOC (src/, code-only) |
|--------------|-------|----------|------|--------|-----|------------------------|
| S1 close (baseline, S1-SNAPSHOT) | 32 | 0 | 0 | 0 | 0 | (see S1-SNAPSHOT) |
| S2 in-progress (after P05 C15) | 32 | 0 | 0 | 0 | 0 | 16045 |

**Trend note (P05 close):** −24 net frontend/src code LOC vs pre-cycle baseline (regen +3 generated; consumer cleanup −27 across 4 manual files: constants.ts −11, MasterFinanceView.vue −3, UserDashboardView.vue −5, payments.ts −11). S2 progress is reducing tech-debt LOC alongside other work. CRITICAL/HIGH/MEDIUM/LOW remain 0 because no audit has run in S2 yet — first audit at S2 close per ProbeKit lite profile.

## Plan vs Reality

| Aspect | Planned | Actual | Delta |
|--------|---------|--------|-------|
| Phases | 5 | 1 done (P05) | 4 remaining |
| Cycles | 21 (C15-C35) | 1 done (C15) | 20 remaining |
| Duration | 4-5 weeks (per-cycle test rhythm) | P05 closed day 1 (2026-04-30) | — |

### What Worked
(filled at close)

### What Didn't
(filled at close)

### Carry Forward
(filled at close)

---

*S2-SPRINT.md*
*Velo | Sprint 2: User Foundation + Booking Flow*
*Re-planned 2026-04-30 (decisions #027-#042)*
