# AUDIT-S1 — Velo Code × Bundle × MH Cards

> Generated at S1-P02-C07 (audit cycle).
> Base HEAD: `47a6cd8` (post-P01-CLOSE).
> Source data: combined scout output P02 + sprint plans S1/S2/S3 + sponsor MH-card list 2026-04-26.
> Updated: 2026-04-26.
> Consumed by: S2 P05/P06, S3 P09/P10/P11 cycle planning.

---

## Section 1: Header

This document is the single source of truth for "what exists in code today vs what bundle SSOT expects vs what MH-card functional spec demands". It feeds S2 and S3 cycle planning by classifying every screen/feature into one of the 9 buckets defined in Section 3, with explicit cycle assignments.

Reproducibility: all claims here are derived from filesystem state at HEAD `47a6cd8`. Re-run the P02 Combined Scout to verify if HEAD has advanced.

---

## Section 2: Executive Summary

- Total view files in `frontend/src/views/`: **36** (3 shells + 11 user + 10 master + 7 admin + 3 auth + 2 root). Total view LOC: **~11,561**. `FILE-TREE.md` previously claimed 31; this audit reconciles to 36 (documentary drift; FILE-TREE.md sync deferred to CLOSE/Clean-Sync).
- Bundle has **14 screens** at `docs/02_spec_assets/velo-design-system-2026-04-23/project/ui_kits/mobile/screens/` (1,488 LOC total). All target user-side; bundle has **ZERO** master-side or admin-side screens.
- MH-card set: **17 cards** confirmed by sponsor (full text in Section 5). Decomposition: **10 mapped to views** (MH-01/02/03/09/10/13/14/15/16/17 — note MH-09 splits into user + master per cycle planning), **3 deferred to BACKLOG** (MH-08/11/12 per #010), **3 infrastructure-not-views** (MH-04/05/06 — Telegram/Stripe/Zoom integrations), **1 cross-cutting flow** (MH-07 quick-booking funnel). Total 10 + 3 + 3 + 1 = 17 ✓.
- S1 Phase 03 (DashboardScreen merge C10 + WelcomeScreen greenfield C11) is **NOT YET RUN**. Treat as `S1-P03-pending` for sprint scope clarity.
- D3 icons strategy ratified at C09 OPEN (decision #024): **Vue-SVG baseline + bundle PNG decorative supplement**. See Section 9.

---

## Section 3: Categorization Buckets

Definitions used throughout Section 4 and Section 5:

| Bucket | Definition | Where it goes |
|--------|------------|---------------|
| `port-existing` | Bundle screen exists AND matching Vue view exists | S2 P05 (5 cycles) |
| `bundle-greenfield` | Bundle screen exists, Vue view absent | S2 P06 (6 cycles) |
| `user-regen-existing` | No bundle, Vue view EXISTS but needs design-gen regen | S3 P09 partial |
| `user-greenfield-new` | No bundle, Vue view absent | S3 P09 partial |
| `master-existing-audit` | Bundle absent, master Vue view exists, audit verdict per file | S3 P10 (per-file) |
| `master-greenfield-MH-17` | No bundle, Vue absent (MH-17) | S3 P11 |
| `S1-P03-pending` | DashboardScreen + WelcomeScreen — C10/C11 NOT YET RUN | S1 P03 (deferred from S1) |
| `infrastructure-not-view` | MH card represents backend/integration, not a view | N/A (different track) |
| `cross-cutting-flow` | MH card spans multiple views as a flow | N/A (per-step assigned) |
| `deferred` | Per decision #010 (admin views, MH-08/11/12) | BACKLOG → S4+ |

---

## Section 4: Master Mapping Table — Views × Bundle × MH × Bucket × Cycle

### 4.1 User views (existing)

| View file | LOC | Bundle file | MH card | Bucket | Sprint cycle | Notes |
|-----------|-----|-------------|---------|--------|--------------|-------|
| HomeView.vue | 128 | DashboardScreen.jsx | MH-14 (partial) | S1-P03-pending | C10 | Root view; routes to UserShell |
| NotFoundView.vue | 65 | — | — | — | — | 404 utility view |
| UserShell.vue | 34 | — | — | — | — | Layout shell |
| MasterShell.vue | 32 | — | — | — | — | Master role shell |
| AdminShell.vue | 32 | — | — | — | — | Admin role shell |
| UserDashboardView.vue | 637 | DashboardScreen.jsx | MH-14 | S1-P03-pending | C10 (HIGH merge) | F3.1 impl differs from bundle visual; merge required |
| CalendarView.vue | 236 | CalendarScreen.jsx | MH-01 | port-existing | S2 P05 C15 | Direct port-replace |
| DiaryView.vue | 238 | (no bundle) | MH-09 user | user-regen-existing | S3 P09 C34-C35 | Regen via design-gen, not pure greenfield |
| UserProfileView.vue | 345 | (no bundle) | MH-13 | user-regen-existing | S3 P09 C36-C37 | Regen |
| PracticeDetailView.vue | 706 | PracticeDetailScreen.jsx | MH-15 (Card ДО брони) | port-existing | S2 P05 C17 | Largest user view |
| MyBookingsView.vue | 208 | MyReservationsScreen.jsx | (none) | port-existing | S2 P05 C16 | Name-mismatch: bundle="Reservations", Vue="Bookings" |
| CheckinView.vue | 203 | CheckInScreen.jsx | MH-02 (semantic mismatch — see Section 10) | port-existing | S2 P05 C18 | Bundle CheckInScreen = mood-gate; MH-02 = pre-session анкета "что хочу проработать". Verify scope at C18 OPEN. |
| FeedbackView.vue | 186 | (no bundle) | MH-03 | user-regen-existing | S3 P09 C32-C33 | Regen |
| TopupView.vue | 360 | (no bundle) | (none — balance recharge, NOT MH-05) | — | — | Stripe Checkout for balance top-up via `POST /payments/topup`; distinct from MH-05 session payment (which routes through PracticeDetailView purchase via `POST /practices/{id}/purchase`) |
| TopupSuccessView.vue | 108 | (no bundle) | (none — balance flow) | — | — | NB: BookingSuccessScreen.jsx is DIFFERENT (S2 C23 creates separate BookingSuccessView) |
| TopupCancelView.vue | 84 | (no bundle) | (none — balance flow) | — | — | |

### 4.2 User views — bundle-greenfield (S2 P06)

| View file (NEW) | LOC | Bundle file | MH card | Bucket | Sprint cycle | Notes |
|-----------------|-----|-------------|---------|--------|--------------|-------|
| Onboarding step 1/2/3 | — | OnboardingScreen.jsx | (none) | bundle-greenfield | S2 P06 C20 | Bundle has 3 slides inline; create 3 view files |
| PracticeLiveView.vue | — | PracticeLiveScreen.jsx | (related to MH-06 Zoom integration UI surface) | bundle-greenfield | S2 P06 C21 | |
| BookingDetailView.vue | — | BookingDetailScreen.jsx | MH-16 (Card ПОСЛЕ брони) | bundle-greenfield | S2 P06 C22 | Distinct from PracticeDetailView (MH-15) |
| BookingSuccessView.vue | — | BookingSuccessScreen.jsx | (related to MH-07 quick booking flow tail) | bundle-greenfield | S2 P06 C23 | Distinct from TopupSuccessView |
| AISummaryView.vue | — | AISummaryScreen.jsx | (none — AI summary is post-MH; reference in MH-17) | bundle-greenfield | S2 P06 C24 | Backend already exists (generated.ts:18 `AISummaryResponse`) |
| MasterProfilePublicView.vue | — | MasterProfileScreen.jsx | (none — public master view) | bundle-greenfield | S2 P06 C25 | Public read; distinct from views/master/MasterProfileView.vue (master-self-edit) |
| StateScreens shared comp + theme infra | — | StateScreens.jsx | (none) | bundle-greenfield + infra | S2 P05 C19 | Loading/Empty/Error 3-in-1 + theme toggle stores/ui.ts |

### 4.3 User views — user-greenfield-new (S3 P09)

| View file (NEW) | LOC | Bundle file | MH card | Bucket | Sprint cycle | Notes |
|-----------------|-----|-------------|---------|--------|--------------|-------|
| DreamDiaryView.vue | — | (no bundle) | MH-10 | user-greenfield-new | S3 P09 C34-C35 | Free-tier entry per MH-10 spec |

### 4.4 Auth views

| View file | LOC | Bundle file | MH card | Bucket | Sprint cycle | Notes |
|-----------|-----|-------------|---------|--------|--------------|-------|
| LoadingView.vue | 72 | (no bundle 1:1) | (none — TMA boot phase) | — | — | Bundle AuthScreen NOT 1:1 per #012 |
| LoadingErrorView.vue | 97 | — | — | — | — | |
| StandaloneStubView.vue | 104 | — | — | — | — | TMA-only gate per #013 |
| WelcomeView.vue (NEW) | — | WelcomeScreen.jsx (reference only, NOT 1:1) | (auth landing) | S1-P03-pending | C11 | Greenfield from Claude Design handoff per #012 |

### 4.5 Master views (all → S3 P10 master-existing-audit, C40 verdict per file)

| View file | LOC | Bundle file | MH card | Bucket | Sprint cycle | Notes |
|-----------|-----|-------------|---------|--------|--------------|-------|
| MasterDashboardView.vue | 542 | (no bundle) | MH-08 (composite) | master-existing-audit | S3 P10 C40-C45 | Per-file audit verdict |
| MasterPracticesView.vue | 274 | — | MH-08 | master-existing-audit | S3 P10 | |
| CreatePracticeView.vue | 551 | — | MH-08 | master-existing-audit | S3 P10 | |
| EditPracticeView.vue | 939 | — | MH-08 | master-existing-audit | S3 P10 | Largest in repo |
| AttendanceView.vue | 539 | — | MH-08 | master-existing-audit | S3 P10 | |
| AnalyticsView.vue | 812 | — | MH-11 (deferred) | deferred (#010) | BACKLOG → S4+ | Pre-built but per #010 deferred |
| MasterProfileView.vue | 668 | — | MH-08 | master-existing-audit | S3 P10 | Master-self-edit; ≠ MasterProfilePublicView (S2 C25) |
| MasterFinanceView.vue | 615 | — | MH-08 | master-existing-audit | S3 P10 | |
| MasterApplyView.vue | 544 | — | MH-08 | master-existing-audit | S3 P10 | |
| MasterPendingView.vue | 249 | — | MH-08 | master-existing-audit | S3 P10 | |
| MasterPracticeRoomView.vue (NEW) | — | (no bundle) | MH-17 | master-greenfield-MH-17 | S3 P11 C46-C48 | HIGH if endpoints missing |
| MasterDiaryView.vue (NEW) | — | (no bundle) | MH-09 master | user-greenfield-new (master-side) | S3 P09 C38-C39 | |

### 4.6 Admin views (all deferred per #010, → BACKLOG #4)

| View file | LOC | Bundle file | MH card | Bucket | Sprint cycle | Notes |
|-----------|-----|-------------|---------|--------|--------------|-------|
| AdminDashboardView.vue | 268 | — | (admin) | deferred | BACKLOG → S4+ | |
| AdminMastersView.vue | 232 | — | (admin) | deferred | BACKLOG → S4+ | |
| AdminMasterReviewView.vue | 342 | — | (admin) | deferred | BACKLOG → S4+ | |
| AdminReportsView.vue | 297 | — | (admin) | deferred | BACKLOG → S4+ | |
| AdminReportDetailView.vue | 354 | — | (admin) | deferred | BACKLOG → S4+ | |
| AdminConsistencyView.vue | 319 | — | (admin) | deferred | BACKLOG → S4+ | |
| AdminProfileView.vue | 141 | — | (admin) | deferred | BACKLOG → S4+ | |

**Total rows in Section 4: 47** (36 existing view files + 11 NEW entries: Onboarding, PracticeLive, BookingDetail, BookingSuccess, AISummary, MasterProfilePublic, StateScreens, DreamDiary, MasterDiary, WelcomeView, MasterPracticeRoom).

---

## Section 5: MH-Card Master Index (all 17 cards)

Source: sponsor message 2026-04-26. MH-09 split into 2 rows (user + master) per S3 P09 cycle planning. Total rows: **18** (17 MH numbers + MH-09 split).

| MH | Title | Что делает (краткое) | Artifact | Bucket | Cycle |
|----|-------|---------------------|----------|--------|-------|
| MH-01 | Calendar | Календарь практик + слоты + фильтр; пользователь записывается, мастер видит расписание | CalendarView.vue + bundle CalendarScreen.jsx | port-existing | S2 P05 C15 |
| MH-02 | Pre-session check-in | Анкета ДО сессии (самочувствие, запрос) — отправляется мастеру | CheckinView.vue (semantic mismatch with bundle CheckInScreen = mood-gate; verify at C18) | port-existing | S2 P05 C18 |
| MH-03 | Post-session feedback | Форма обратной связи после сессии (24h окно) — рейтинг + текст | FeedbackView.vue | user-regen-existing | S3 P09 C32-C33 |
| MH-04 | Automated reminders | Telegram push о сессии/чек-ине/фидбеке — без отдельного app | infrastructure (`platform/telegram.ts` + backend bot) | infrastructure-not-view | — |
| MH-05 | Stripe payments | Оплата сессии через Stripe Checkout (10% VELO platform-referral) | infrastructure (`api/payments.ts` + Stripe backend) + UI surface in TopupView/Success/Cancel | infrastructure-not-view (UI surface present) | — |
| MH-06 | Zoom integration | Zoom API (VELO как хост, 1-2 Business аккаунта) | infrastructure (backend + UI in PracticeLiveView S2 C21) | infrastructure-not-view (UI surface in C21) | — |
| MH-07 | Quick booking | Минимум кликов: мастер → слот → оплата → ссылка | flow: PracticeDetailView → MyBookingsView → BookingDetailView → BookingSuccessView (C17/C16/C22/C23) | cross-cutting-flow | (multi-cycle) |
| MH-08 | Masters Account | Базовый кабинет мастера (профиль/расписание/сессии/платежи) | **CONCEPT DEFERRED per #010 → BACKLOG #5.** Pre-existing pieces in views/master/ (10 files) are S3 P10 audit-only — they are NOT closing MH-08 in S3; full MH-08 dashboard concept reactivates in S4+. | deferred (concept) / master-existing-audit (pieces) | BACKLOG #5 (concept); S3 P10 C40-C45 (existing pieces audit only) |
| MH-09 user | Diary/reflection (user) | Текстовый дневник-рефлексия (без AI — AI в 2.0) | DiaryView.vue | user-regen-existing | S3 P09 C34-C35 |
| MH-09 master | Diary/reflection (master) | Тот же модуль для мастера | (NEW) MasterDiaryView.vue | user-greenfield-new (master-side) | S3 P09 C38-C39 |
| MH-10 | Dream diary | Дневник снов — отдельный модуль, Free tier | (NEW) DreamDiaryView.vue | user-greenfield-new | S3 P09 C34-C35 |
| MH-11 | Feedback analytics | Аналитика для мастера по его сессиям | AnalyticsView.vue (pre-built but deferred per #010) | deferred | BACKLOG → S4+ |
| MH-12 | Group report | Агрегированный отчёт по клиентам мастера | (no view yet) | deferred | BACKLOG → S4+ |
| MH-13 | User profile | Текстовый профиль (прогресс, паттерны) | UserProfileView.vue | user-regen-existing | S3 P09 C36-C37 |
| MH-14 | Dashboard | Основное меню навигации + уведомления + метрики | UserDashboardView.vue + bundle DashboardScreen.jsx (merge required) | S1-P03-pending | S1 P03 C10 |
| MH-15 | Practice menu Card (ДО брони) | Информативная карточка практики (длит/слоты/мест) + кнопка брони | PracticeDetailView.vue + bundle PracticeDetailScreen.jsx | port-existing | S2 P05 C17 |
| MH-16 | Practice menu Card (ПОСЛЕ брони) | Карточка с управлением (check-in / feedback / отмена) | (NEW) BookingDetailView.vue + bundle BookingDetailScreen.jsx | bundle-greenfield | S2 P06 C22 |
| MH-17 | Masters Practice room | Кабинет управления практикой для мастера (записи, отметки, саммари, AI-summary группы) | (NEW) MasterPracticeRoomView.vue | master-greenfield-MH-17 | S3 P11 C46-C48 |

---

## Section 6: Theme support — current state (for S2 C19 prep)

- **Dark token count**: 32 confirmed (`[data-theme="dark"]` block at `frontend/src/styles/variables.css:250-291`)
- **Total project tokens**: 177 custom property declarations
- **stores/ui.ts shape**: `UiMode = 'default' | 'user'`; `uiMode` ref + `setUiMode` setter; **NO `theme` field**, **NO localStorage persistence** (intentional comment: "resets on every session start"), **NO `prefers-color-scheme` listener**
- **UI toggle**: NONE in repo (grep `[data-theme=` outside variables.css → 0)

S2 C19 must add:
- `theme` field to ui store
- localStorage persistence
- `prefers-color-scheme` media-query listener
- UI toggle component (likely in headers)

---

## Section 7: AuthScreen — current state (for S2 C26 prep)

- **Bundle**: AuthScreen.jsx EXISTS (239 LOC, largest bundle screen). Per decision #012 NOT-1:1 (Velo TMA-only; bundle has Google/Apple OAuth — not used).
- **Vue auth/ stub views (3)**:
  - `LoadingView.vue` (72 LOC) — mandala spinner during TMA initData parse
  - `LoadingErrorView.vue` (97 LOC) — auth init timeout fallback
  - `StandaloneStubView.vue` (104 LOC) — "Open in Telegram" gate for non-TMA browsers per #013
- **WelcomeView.vue / AuthView.vue**: NEITHER EXISTS
- **S1 P03 C11 plan**: WelcomeView greenfield → NOT YET RUN (P03 entirely pending)
- **S2 C26 plan**: "TMA Auth polish: WelcomeView расширение, platform/telegram.ts integration, no OAuth UI (HIGH — touches auth boundary)"

S2 C26 must polish: full WelcomeView (assuming C11 ran first OR C26 absorbs C11's scope at S2 OPEN).

---

## Section 8: Bundle screen list (14 .jsx)

Reference table — bundle screens for S2/S3 cycle dispatch:

| Bundle file | LOC | Bucket | Sprint cycle |
|-------------|-----|--------|--------------|
| AuthScreen.jsx | 239 | NOT-1:1 reference per #012 | S2 P07 C26 (polish only) |
| WelcomeScreen.jsx | 82 | S1-P03-pending | S1 P03 C11 |
| OnboardingScreen.jsx | 95 | bundle-greenfield (3-slides) | S2 P06 C20 |
| DashboardScreen.jsx | 118 | S1-P03-pending (merge into UserDashboardView) | S1 P03 C10 |
| CalendarScreen.jsx | 80 | port-existing | S2 P05 C15 |
| MyReservationsScreen.jsx | 61 | port-existing (rename) | S2 P05 C16 |
| PracticeDetailScreen.jsx | 93 | port-existing | S2 P05 C17 |
| PracticeLiveScreen.jsx | 113 | bundle-greenfield | S2 P06 C21 |
| BookingDetailScreen.jsx | 105 | bundle-greenfield (MH-16) | S2 P06 C22 |
| BookingSuccessScreen.jsx | 67 | bundle-greenfield (NOT TopupSuccess) | S2 P06 C23 |
| CheckInScreen.jsx | 119 | port-existing (semantic mismatch) | S2 P05 C18 |
| AISummaryScreen.jsx | 108 | bundle-greenfield (backend ready) | S2 P06 C24 |
| MasterProfileScreen.jsx | 119 | bundle-greenfield (PUBLIC) | S2 P06 C25 |
| StateScreens.jsx | 89 | bundle-greenfield + infra | S2 P05 C19 |

Total bundle: 1,488 LOC.

---

## Section 9: Icons strategy (D3 ratified) — C09 deliverable

**Decision (#024 — see decisions.md):** Vue-SVG baseline + bundle PNG decorative supplement.

### Velo-SVG baseline (14 files in `frontend/src/components/icons/`)

Used for: ALL UI primitives — navigation tabs, state indicators, action buttons, currency, time. Vue components with `currentColor` fill + `size` prop. Theme-aware (dark/light auto), scalable, no extra HTTP requests.

Components: IconBrain, IconBreathwork, IconCalendar, IconClock, IconDiary, IconFeedback, IconGroup, IconHome, IconMeditation, IconProfile, IconRuble, IconSuccess, IconSupport, IconWarning.

Note: IconRuble flagged for review — Velo backend operates in EUR; potential dead code (BACKLOG #29).

### Bundle PNG decorative supplement (12 files in `frontend/src/assets/brand-icons/`)

Used for: decorative wellness contexts ONLY — mood cards, master profile flair, onboarding illustrations, success-state emotional accents. NOT for navigation or UI state primitives.

Files: bolt, brain, circle-microphone, flame, heart, high-five, love, meditation, quill-pen, quill-pen-story, spa, wind.

Of these, 2 collide conceptually with Velo-SVG (`brain`, `meditation`). For these 2, **use Velo-SVG**. PNG versions remain available in assets/ for future revisit but not consumed by code.

### Future migration (BACKLOG)

10 bundle-only PNGs (bolt, circle-microphone, flame, heart, high-five, love, quill-pen, quill-pen-story, spa, wind) are decoratively useful but raster format. Future-cleanup: convert to SVG when Vue-SVG asset volume justifies the work. Tracked at BACKLOG #30.

### Usage rules (binding for S2/S3)

1. UI primitives → Velo-SVG only. Never PNG.
2. Decorative wellness accents → bundle PNG OK (mood cards, master flair, onboarding illustrations).
3. New tab-bar / nav / state icon needed → create new Velo-SVG, do NOT import bundle PNG.
4. Conflict resolution: if both formats exist for same concept (currently: brain, meditation) → Velo-SVG wins.

### Current consumer sites (3 files; verified clean)

- `frontend/src/views/user/PracticeDetailView.vue` — uses Velo icons
- `frontend/src/components/icons/index.ts` — barrel export
- `frontend/src/router/tabs.ts` — 7 Velo icons for tab bars

Composables, stores: confirmed icon-clean (no scan needed).

---

## Section 10: Open questions / gaps

1. **MH-02 vs CheckinView.vue semantic match.** MH-02 = pre-session анкета ("самочувствие, запрос, что прорабатываем"). CheckinView.vue = mood-gate per scout. Are these the same fixture or different? Verify at S2 C18 OPEN. If different — separate cycle for MH-02 анкета view (not in S1/S2/S3 plan today).

2. **MasterProfilePublic backend gap.** S2 C25 needs `GET /api/v1/masters/{id}` (public read). NOT in generated.ts. Partner ask in backend-coord-report.

3. **MH-17 endpoints.** S3 C48 needs practice-room API (real-time join/leave, mood broadcast, master controls). NOT in generated.ts. Partner ask in backend-coord-report.

4. **Regen pending fields.** Bundle CR-01 fields (`min_withdrawal_cents`, `withdrawal_fee_cents` in `MasterProfileResponse`) + Zodd CRITICAL #1 (`PracticeSummary.timezone`) — both await fresh openapi.json regen. Bundled in backend-coord-report as "regen-trigger ask".

5. **HEAD documentary drift.** S1-SPRINT.md "Last Session" still cites HEAD `83d287a`. Current HEAD: `47a6cd8` (post-CLOSE commit). Cosmetic, fix at S1-SPRINT.md next-touch (CLOSE).

6. **BACKLOG #25 user-ai-summary feature gap — RESOLVED.** Per #25 ("B.3 fix removed broken trigger; actual AI summary feature status unknown. Catalog as known gap in Phase 02 C07 AUDIT-S1.md") — feature status now KNOWN: backend exists (`AISummaryResponse` in `generated.ts:18`), no frontend wrapper. S2 C24 implements (categorized as bundle-greenfield in Section 4 of this audit). #25 superseded by S2 C24 cycle plan; mark as DONE at next BACKLOG.md touch.

---

## Anchor

```
[AUDIT-S1.md | SPEC v3.2-velo]
Sprint-1 audit — code reality × bundle SSOT × MH-card spec
Location: docs/01_refer/AUDIT-S1.md
Referenced from: S1-SPRINT.md, S2-SPRINT.md, S3-SPRINT.md References blocks
Update when: end of S2 or S3 if scope drifts; superseded at S4+ planning
```
