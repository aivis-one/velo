# Velo — Architecture & Project Reference

> Frontend-only scope. Backend lives in `backend/` and is maintained separately.
> Loaded in every working chat alongside `01_Declaration.md`.
> Last updated: 2026-05-05 (S4-Clean-Sync — counter refreshes; VModal claim corrected; Phase 14 + 15 narratives accurate as of S4 close 2026-05-04).

---

## Project Overview

Velo is a Telegram Mini App with PWA fallback for non-Telegram browsers. Vue 3 mobile-first. Three user roles: `user`, `master`, `admin`. Modular monolith backend (FastAPI), separate code ownership. See decisions.md #013. Platform abstraction lives in `frontend/src/platform/`.

Full functional and technical background: see root-level documents
- `VELO-Technical-Specification.md` — master technical spec
- `VELO-Frontend.md` — frontend architecture
- `VELO-Frontend-Specification.md` — UI/UX detailed spec
- `VELO-Design-Document.md` — design system principles
- `VELO-Anti-Patterns.md` — 8 frontend anti-patterns (FP-01..FP-08) to check

These are authoritative and read-only for this framework — do not edit from SPEC protocols, only reference.

---

## Components (frontend/src/)

See `FILE-TREE.md` for current inventory. Compact:

- `views/` — 57 page components across `user/` (31) · `master/` (10) · `admin/` (7) · `auth/` (9), plus 3 shells + 2 root views (HomeView, NotFoundView)
- `components/` — icons, layout, shared, ui, master-specific
- `stores/` — Pinia: auth, balance, bookings, diary, master, messages, notifications, practices, ui
- `composables/` — useAuth, useApiError, useToast, usePagination, usePracticeWindows
- `api/` — 9 files including client base, per-module modules, types, utils
- `router/` — index, guards, tabs (shell-layout with role guards)
- `styles/` — variables.css (semantic tokens), global.css
- `platform/`, `utils/`

**Bundle-sourced shared components** (ported during S1 infra + S2 bundle-port): Accordion, AppHeader, Avatar, BackHeader, Backdrop, Button, Callout, Cards, Chip, Chips, Input, MandalaBackdrop, MasterCard, MoodPicker, TabBar, WeekdayStrip — 16 components from `docs/04_assets/velo-design-system-2026-04-23/project/ui_kits/mobile/components/`.

**Phase 01 additions (2026-04-26 close):**

- `frontend/public/fonts/` — bundled fonts for app: `Marmelad-Regular.ttf` (used via `@font-face` in `variables.css`).
- `frontend/src/assets/` — extracted bundle assets organized by category:
  - `brand/` (3 files: mandala backdrop/runes/png)
  - `brand-icons/` (12 PNG icons)
  - `illustrations/` (3 SVG: ai-analytics, live-practices, self-map)
  - `masters/` (2 placeholder SVGs: alex-mindful, maria-flow)
  - `mood/` (3 SVGs: mood-calm, mood-neutral, mood-sad)
  - `patterns/` (1 SVG: master-card)
- `frontend/src/styles/variables.css` — restructured to bundle-SSOT: `@font-face` (Marmelad), `:root` (101 bundle canonical light tokens), `[data-theme="dark"]` (32 dark overrides), Legacy section (86 preserved tokens including 8 admin-deferred per #020), 6 project-extension tokens per #021 (`--nav-inactive-bg`, `--surface-{steel,teal,warm}-alpha-{15,30,40,60}`).
- `frontend/src/api/generated.ts` — partner-introduced auto-generated TypeScript types from backend OpenAPI schema (commit `81304a6`); do NOT edit manually. Regen pipeline at `backend/scripts/generate_ts_types.py`. See decisions.md #023.
- `frontend/src/api/types.ts` — re-export hub from `./generated` for backend-derived types + local declarations for frontend-only union types (`PracticeType`, `PracticeStatus`, `BookingStatus`, `WithdrawalStatus`, etc.). See decisions.md #023.

**Phase 03 additions (2026-04-26 close):**

- `frontend/src/views/auth/WelcomeView.vue` — TMA splash landing for `/welcome` route. Mandala backdrop + VELΘ wordmark + tagline + single primary CTA "Открыть в Telegram" linking to `import.meta.env.VITE_TELEGRAM_BOT_URL`. Per decision #012 NOT 1:1 with bundle AuthScreen (no third-party login UI in Velo TMA-only flow); fast-track without Claude Design pipeline per decision #025.
- `frontend/src/views/user/UserDashboardView.vue` — merged bundle DashboardScreen visual structure (WeekdayStrip + Stats row from real `bookingsStore` data) preserving all existing Velo behavior (check-in/feedback alerts, AI summary card, timezone tactical cast at `nearestPracticeDate` per BACKLOG #27). Bundle elements skipped per scope-lock: Contraindications callout (no backend flag), Recommendations list (deferred to S2 P05). LOC 637 → 741.
- `frontend/src/router/index.ts` — added `/welcome` top-level route (name `welcome`, lazy-loaded WelcomeView), no meta, no guards. Total `path:` count 42 → 43.

**Phase 05 additions (2026-04-30 close):**

- `frontend/src/api/generated.ts` — regenerated against fresh openapi via self-host pipeline (decision #046, first application). Adds `MasterProfileResponse.{min_withdrawal_cents,withdrawal_fee_cents}`, `PracticeSummary.timezone`, narrows `AdminMasterListItem.role: string → UserRole`, makes `valid_from` nullable on both promo-create requests. 762 → 765 LOC.
- Consumer migrations: `MasterFinanceView.vue` reads withdrawal limits from `masterStore.profile?.{min_withdrawal_cents,withdrawal_fee_cents}` (BACKLOG #26 closed); `UserDashboardView.vue` `nearestPracticeDate` drops tactical `as PracticeSummary` cast + Berlin fallback in favor of direct `practice.timezone` read (BACKLOG #27 closed); `api/payments.ts` drops local `TopupRequest`/`TopupResponse` declarations and consumes via `@/api/types` re-export hub per decision #023 (BACKLOG #32 closed).
- `utils/constants.ts` — `MIN_WITHDRAWAL_EUROS` + `WITHDRAWAL_FEE_EUROS` removed; only time-window constants (`CHECKIN_WINDOW_H`, `FEEDBACK_WINDOW_H`) remain.

**S2 re-plan additions (2026-04-30):**

- New design batch from designer (~55 mockups, ~34 unique views) supersedes bundle visual layer. Bundle tokens (colors / typography / surfaces) ~80% retained per decision #029.
- Hybrid auth model #028: TMA primary (initData) + PWA standalone (email/OAuth UI) — Welcome (`WelcomeView.vue`) splits into platform-aware branches.
- Coord docs: `docs/03_sprint/S2-bundle-port/BACKEND-COORDINATION.md` + `DESIGN-DECISIONS-LOG.md` are continuously-updated SSOTs for cross-team coordination per decision #041.
- New views planned for S2/S3: `LoginView`, `RegisterView`, `OAuthLoadingView`, `OnboardingCarouselView`, `OnboardingTimezoneView`, `BookingSuccessView`, `BookedPracticeView`, `BookingDetailView`, `CheckinSuccessView`, `PracticeLiveView`, `FeedbackSuccessView`, `EditProfileView`, `NotificationsView`, `LanguageTimezoneView`, `SupportFormView`, `MessagesListView`, `ThreadView`, `AISummaryView`, `MasterProfilePublicView`, `MyReservationsView`, `DiaryView` refresh, sub-Diary routes, `DiaryEntryView`, `RelationshipsView`. See S2-SPRINT.md + S3-SPRINT.md for cycle assignment.

**Phase 06 additions (2026-04-30 close):**

- `frontend/src/views/auth/WelcomeView.vue` — refactored from S1 C11 single-CTA TMA splash to dual-branch hybrid: TMA branch (preserved S1 visual: mandala backdrop + VELΘ wordmark + tagline + "Открыть в Telegram" anchor) + PWA branch (new — Войти / Создать аккаунт CTAs from skin 01_Welcome.png). Branch selection via `platform.name === 'telegram'` discriminator. Decision #028 (hybrid auth γ) + #036 (single-file conditional template). C16 commit `cc4e2fd`.
- `frontend/src/App.vue` — gate restructured: removed `<StandaloneStubView v-else-if="isStandalone || !isAuthenticated">` short-circuit blocking PWA users; standalone unauthenticated users now reach RouterView and route through `/welcome` PWA branch. `StandaloneStubView.vue` retained on disk for potential auth-error reuse. C16 commit `cc4e2fd`.
- `frontend/src/router/guards.ts` — `roleGuard` converted sync → async with `await waitUntilReady()` before reading `auth.role` (BACKLOG #47 fold). Defense-in-depth against future App.vue gate regressions. C16 commit `cc4e2fd`.
- `frontend/src/main.ts` — fail-fast PROD guard for `VITE_TELEGRAM_BOT_URL` (BACKLOG #49 fold). Throws at boot if PROD build missing env var; prevents silent test-bot fallback. C16 commit `cc4e2fd`.
- `frontend/src/views/auth/LoginView.vue` (NEW, ~330 LOC) — PWA-only email/password form + Google/Apple OAuth text-only buttons + forgot-password link + footer to RegisterView. All submits mock via `useToast` per BACKEND § A.1/A.2 not landed. Skin reference: 02_Login.png. C17 commit `b060ba3`.
- `frontend/src/views/auth/RegisterView.vue` (NEW, ~350 LOC) — PWA-only name/email/password form + ToS/Privacy placeholder links + OAuth + footer to LoginView. Mock submit. Skin reference: 03_Register.png. C18 commit `b060ba3`.
- `frontend/src/views/auth/OAuthLoadingView.vue` (NEW, ~95 LOC) — mock OAuth callback splash; 1500ms spinner → `toast.info` → `router.replace('/welcome')`. Skin reference: 04_OAuth.png. C19 commit `b060ba3`.
- `frontend/src/views/auth/OnboardingCarouselView.vue` (NEW, ~250 LOC) — single view with 3-slide carousel (index 0..2 state) + skip button + dot indicator + back chevron on slides 1-2. Reuses existing illustrations from `frontend/src/assets/illustrations/` (visual mismatch with skin 05/06/07 logged as BACKLOG NIT — designer per-slide assets pending future batch). Decision #034 onboarding flow. C20 commit `de496f6`.
- `frontend/src/views/auth/OnboardingTimezoneView.vue` (NEW, ~285 LOC) — city autocomplete input + timezone resolution via local JSON + PATCH `/api/v1/users/me { timezone }` + localStorage `velo:onboarding_completed=true` + redirect to `/user/dashboard`. PATCH failures (401 PWA-no-auth) swallowed silently per Path Y graceful degrade. Skin reference: 08_Onboarding 4.png. C21 commit `de496f6`.
- `frontend/src/data/cities.json` (NEW) — hand-curated 118-entry city → IANA mapping prioritizing Russian-speaking world + major Western/Asian cities. Native `Intl.DateTimeFormat` fallback for unmatched cities. Full ~300 expansion deferred to BACKLOG polish cluster. C21 commit `de496f6`.
- `frontend/src/router/index.ts` — 5 new public routes added across phase: `/login`, `/register`, `/oauth/callback`, `/onboarding/intro`, `/onboarding/timezone`. Path count 43 → 48. No meta, no guards (auth gate is at App.vue layer per Phase 06 architecture).

**Phase 07 additions (2026-04-30 — S2-S3 speedrun MEGA-1, commit `6c5fd1f`):**

- `frontend/src/views/user/UserDashboardView.vue` — refreshed under new design system (skin 10/11). Greeting block + check-in/feedback alert cards (window-based via `usePracticeWindows`) + nearest-booking BookingCard + Zoom/Check-in pill row + StatCards row (Прогресс) + AI-саммари teaser. PRACTICE_TYPE_ICON map adoption.
- `frontend/src/views/user/CalendarView.vue` — refreshed under new DS (skin 21). NEW WeekStrip component, day-grouped practice list, "Выбрать практики" filter trigger.
- `frontend/src/components/shared/CalendarFilterOverlay.vue` (NEW) — chip-based filter modal (skin 22): practice direction single-select.
- `frontend/src/components/shared/WeekStrip.vue` (NEW) — 7-day strip with current-day highlight + practice dot indicators + arrow nav.
- `frontend/src/stores/ui.ts` — extended with `theme: 'light' | 'dark'`, `setTheme(t)`, `initTheme()` + localStorage `velo:theme` + prefers-color-scheme media listener (C25). Boot wired in `main.ts` after Pinia mount, before router.
- `frontend/src/components/layout/VHeader.vue` — added IconTheme toggle button + IconArrowBack pattern in back navigation (replacing legacy "← " text).

**Phase 08 additions (S2-S3 speedrun MEGA-1, commit `6c5fd1f`):**

- `frontend/src/views/user/PracticeDetailView.vue` — refreshed (skin 24 paid + 28 free, single component conditional pricing). MasterCardSummary + Callout (Контраиндикации) extracted.
- `frontend/src/components/shared/MasterCardSummary.vue` (NEW) — reusable master section: avatar + name + verified chip + methods + "Подробнее →" link to `/user/master/:id`.
- `frontend/src/components/shared/Callout.vue` (NEW) — variant `'amber' | 'mint'` for warnings + info hints.
- `frontend/src/views/user/BookingSuccessView.vue` (NEW, skin 26) — IconHandsClap + master-request mock textarea (per BACKEND § B.4) + В календарь / На главную CTAs.
- `frontend/src/views/user/BookedPracticeView.vue` (NEW, skin 15) — day-of-practice context with Check-in window CTA + cancel via native confirm.
- `frontend/src/views/user/BookingDetailView.vue` (NEW, skin 18) — status confirmation + ZOOM info card + cancel.
- `frontend/src/views/user/CheckinView.vue` (refresh) + `CheckinSuccessView.vue` (NEW, skin 12 + 13) — 3-icon mood picker (sad/neutral/calm SVGs from `assets/mood/` per slider deprecated A.13) + comment textarea + IconSuccess splash → "Начать практику".
- `frontend/src/views/user/PracticeLiveView.vue` (NEW, skin 14) — video placeholder (Velo emblem on ink-soft bg per D4) + "Войти" `window.open` zoom_link (#037) + "Check-in" re-open form 12 upsert (#035) + "Покинуть практику" via `cancelBooking` (BACKLOG #97 leave endpoint queued).
- `frontend/src/views/user/FeedbackView.vue` (refresh) + `FeedbackSuccessView.vue` (NEW, skin 29 + 30) — 3-button rating (IconWarning / IconHeart / IconBrain) + comment + heart success.

**Phase 09 additions (S2-S3 speedrun MEGA-1, commit `6c5fd1f`):**

- `frontend/src/views/user/UserProfileView.vue` — refreshed (skin 70/71). Avatar card + StatCards row (Практик / Часов / Дней подряд) + 3 sections (Аккаунт / Настройки / Помощь) + Выйти red row → `auth.logout()` → `/welcome`.
- `frontend/src/components/shared/ProfileMenuItem.vue` (NEW) — reusable RouterLink/button row: icon + label + optional badge + IconChevronRight.
- `frontend/src/components/shared/StatCard.vue` (NEW) — reusable stat tile (value + label).
- `frontend/src/views/user/EditProfileView.vue` (NEW, skin 72 + 73) — form fields + Удалить аккаунт red link → native confirm → toast (mock per BACKEND § A.4) + Сохранить → `api.patch('/api/v1/users/me')` direct call (no `api/users.ts` file per Code anomaly).

**Phase 10 additions (S2-S3 speedrun MEGA-2, commit `af39b41`):**

- `frontend/src/views/user/DiaryView.vue` — full rewrite (skin 40 timeline + 41 list). Layout state `'timeline' | 'list'` persisted via localStorage `velo:diary-layout` per decision #032. ••• menu opens layout toggle / filter overlay / search overlay.
- `frontend/src/components/shared/SpineDivider.vue` (NEW) — date divider with simple text-glyph ornament (▶ date ◀); ornate SVG glyphs deferred to BACKLOG NIT polish.
- `frontend/src/components/shared/DiaryEntryBubble.vue` (NEW) — timeline-mode entry display (mood/kind circle + chat-bubble card).
- `frontend/src/components/shared/DiaryEntryFlat.vue` (NEW) — list-mode flat card (icon + title + preview).
- `frontend/src/components/shared/DiaryComposer.vue` (NEW) — collapsed pill bar with IconMic + IconArrowUp; tap → modal expand.
- `frontend/src/components/shared/DiaryComposerExpanded.vue` (NEW) — full composer modal: title input + textarea + 3-mood picker + practice picker (linkable from `bookingsStore.upcomingBookings`) + Сохранить → `useDiaryStore.createEntry`.
- `frontend/src/components/shared/DiaryFilterOverlay.vue` (NEW, skin 42 + 43) — slide-up panel: month-grid date picker (single + range select via two-tap) + type chips (Все / Дневник / Сонник / Insights) wired to `useDiaryStore.typeFilter`.
- `frontend/src/components/shared/DiarySearchOverlay.vue` (NEW, skin 44) — slide-down panel: input + IconSearch + history pills (localStorage `velo:diary-search-history`) + mock results placeholder per BACKEND § A.3.
- `frontend/src/views/user/CheckinsCategoryView.vue` (NEW, skin 45 + 46) — category-filtered: only check-ins.
- `frontend/src/views/user/FeedbacksCategoryView.vue` (NEW, skin 47 + 48) — category-filtered: only feedbacks.
- `frontend/src/views/user/EntriesCategoryView.vue` (NEW, skin 49 + 50 + 51) — combined Дневник + Сонник + type-filter chip group (Все / Дневник / Сонник) wired to `useDiaryStore.typeFilter`.
- `frontend/src/stores/diary.ts` — extended with `typeFilter`, `searchQuery`, `searchHistory`, `filteredEntries` computed, `pushSearchHistory` / `clearSearchHistory` / `setSearchQuery` / `initSearchHistory` helpers. Type filter operates on placeholder `e.type` until BACKEND § B.1 lands per decision #033.

**Phase 11 additions (S2-S3 speedrun MEGA-2, commit `af39b41`):**

- `frontend/src/views/user/DiaryEntryView.vue` (NEW, skins 52 + 56 + 57 + 58 + 59) — single-entry view with read mode (optional practice card + check-in chip + entry text card + "Найдена взаимосвязь" CTA) + action menu (•••, edit pencil, trash) + delete with undo snackbar (3s grace) + edit mode in-place (textarea + Сохранить).
- `frontend/src/components/shared/EntryActionMenu.vue` (NEW) — floating right-rail action stack: ••• reveals/hides Edit + Trash buttons.
- `frontend/src/components/shared/UndoSnackbar.vue` (NEW) — auto-dismiss timer + action button; emits `action` on user click, `timeout` on natural expiry.
- `frontend/src/views/user/RelationshipsView.vue` (NEW, skins 53 + 54 + 55) — chained icons + entry context cards + AI commentary placeholder per BACKEND § A.8.
- `frontend/src/components/shared/RelationshipChain.vue` (NEW) — horizontal SVG chain with white pill connectors between mood/flame/feather/dream icons.
- `frontend/src/components/shared/AICommentaryCard.vue` (NEW) — VELO AI mint tag + placeholder content; `isPlaceholder` prop default true at v1.

**Phase 12 additions (S2-S3 speedrun MEGA-2, commit `af39b41`):**

- `frontend/src/views/user/NotificationsView.vue` (NEW, skin 74) — 4 toggles (push / reminders / from masters / from support) via `useNotificationsStore`; localStorage `velo:notif-*`.
- `frontend/src/stores/notifications.ts` (NEW) — 4 boolean refs + `init()` reader + watch persistence; `init()` wired in `main.ts`.
- `frontend/src/views/user/LanguageTimezoneView.vue` (NEW, skin 75) — language radio (Русский / English) + timezone presets (Москва / Лондон) + city picker autocomplete (reuses cities.json from C21). PATCH `/api/v1/users/me { language | timezone }` direct.
- `frontend/src/views/user/SupportFormView.vue` (NEW, skin 76) — IconQuestion hero card + subject + message form + mock submit per BACKEND § A.6.
- `frontend/src/views/user/MessagesListView.vue` (NEW, skin 80) — 3 conversations from `useMessagesStore`; tap → setActiveConversation + push to thread.
- `frontend/src/views/user/ThreadView.vue` (NEW, skins 81 + 82) — ChatBubble list + ThreadComposer; mock send per BACKEND § A.7.
- `frontend/src/components/shared/ConversationListItem.vue` (NEW) — avatar / name / preview / timestamp / unread badge.
- `frontend/src/components/shared/ChatBubble.vue` (NEW) — incoming white / outgoing ink-soft fill variants with timestamp.
- `frontend/src/components/shared/ThreadComposer.vue` (NEW) — input + IconArrowUp send only (distinct from DiaryComposer per D2 — no mic, no expand modal).
- `frontend/src/stores/messages.ts` (NEW) + `frontend/src/utils/mockMessagesData.ts` (NEW) — 3 conversations × 2 messages mock fixtures (Alex Mindful master / Поддержка VELΘ system / Maria Flow master).
- `frontend/src/views/user/AISummaryView.vue` (NEW, skin 16) — placeholder weekly summary per BACKEND § A.8 (header chip + paragraphs + inline mood SVGs + recommendation cards).
- `frontend/src/views/user/MasterProfilePublicView.vue` (NEW, skin 25) — DEGRADED v1 per BACKLOG #99 + decision D12; name/avatar derived from `getPractices({ master_id }).first().master_name + master_avatar_url`; bio/methods/experience placeholder; stats hidden.

**Phase 13 additions (S2-S3 speedrun MEGA-2, commit `af39b41`):**

- `frontend/src/views/user/MyReservationsView.vue` (NEW, skin 17) — Предстоящие + Прошедшие sections from `bookingsStore.upcomingBookings` + `pastBookings` (MEGA-1 getters); status chips via `statusChipVariant(b)` helper.
- `frontend/src/components/shared/ReservationCard.vue` (NEW) — practice icon + title + master row + date + status chip.
- `frontend/src/stores/bookings.ts` — extended with `upcomingBookings` + `pastBookings` computed getters + `statusChipVariant(b)` helper (Завтра amber / Завершена mint / Отменена pink / Пропущена pink / Сегодня amber / Подтверждена mint).

**Phase 14 additions (S4 master-refresh, MEGA-3, commit pending push):**

- `frontend/src/views/master/MasterPendingView.vue` — refreshed under Velo DS (status splash with IconSuccess/IconWarning + Callout amber for rejection reason). Standalone view (no MasterShell, no tab bar). 260 → ~300 LOC.
- `frontend/src/views/master/MasterApplyView.vue` — refreshed (3-step form preserved; native checkboxes preserved per design comment lines 18-19; IconCheck checkbox marks + IconShield upload icons). 583 → 599 LOC.
- `frontend/src/views/master/MasterDashboardView.vue` — refreshed (greeting + StatCards row + AICommentaryCard teaser + nearest-practice card; PRACTICE_TYPE_ICON migration). `nearestPractice` computed kept in-component per Path Y simpler default. 585 → 574 LOC.
- `frontend/src/views/master/MasterPracticesView.vue` — refreshed (header emoji stripped; client-side status filtering at lines 202/209 preserved; api/practices.ts unchanged). 306 LOC unchanged.
- `frontend/src/views/master/CreatePracticeView.vue` — refreshed (6 section headers stripped of emoji prefixes; W-2/W-6/W-7/W-9 audit markers preserved per S1 lineage). 583 → 586 LOC.
- `frontend/src/views/master/EditPracticeView.vue` — refreshed (section headers + action button labels stripped; ConfirmModal integration replacing inline Teleport modal at lines 369-401; 40+ LOC orphan CSS removed). 988 → 931 LOC (-57 net).
- `frontend/src/views/master/AttendanceView.vue` — refreshed (3-section status display; section emoji stripped; status badges → IconCheck/IconClose/IconClock; ConfirmModal integration replacing inline overlay at line 219). 592 → 539 LOC (-53 net).
- `frontend/src/views/master/AnalyticsView.vue` — refreshed (RATING_BARS_CONFIG `emoji: string` → `icon: Component` IconHeart/IconCheck/IconQuestion; `typeEmoji` function fully removed; PRACTICE_TYPE_ICON migration; per BEC §A.8 mock-until-ready AI insights teaser via AICommentaryCard placeholder). 866 → 898 LOC.
- `frontend/src/views/master/MasterFinanceView.vue` — refreshed (IconBookFeather replaces 💰; section headers stripped; **withdrawal `min_withdrawal_cents` / `withdrawal_fee_cents` reads from `masterStore.profile` preserved** per #022 + BACKLOG #26 closure). 645 → 648 LOC.
- `frontend/src/views/master/MasterProfileView.vue` — refreshed (IconCheck verified badge + IconBookFeather finance link; mirror UserProfileView 70/71 layout). **TD-FE-ROLE-SWITCH preserved** — 4 markers (lines 2 / 24 / 270 / 517) + `switchToUserMode()` function at line 520 + `useUiStore` + `setUiMode('user')` invariant intact. 732 → 736 LOC.
- `frontend/src/components/master/PracticeListItem.vue` — cascade-refreshed (PRACTICE_TYPE_EMOJI → PRACTICE_TYPE_ICON migration; IconGroup replaces 👥 in details row). Required cascade for §C58 invariant compliance per Rule 27. 153 → 159 LOC.

**New shared component**:

- `frontend/src/components/shared/ConfirmModal.vue` — NEW (168 LOC). Teleport-inline confirm-dialog with `role="dialog"` + `aria-modal="true"` + Escape-key handler (Path Y minimum a11y). Prop API: `visible / loading / title / message / danger / confirmLabel / cancelLabel`. Emits: `confirm / cancel / update:visible`. Replaces inline overlay+dialog markup in EditPracticeView + AttendanceView. BACKLOG #48 closure path (shared ConfirmModal extraction; supersedes original "VModal adoption" framing — VModal direct view-side adoption is 0; legacy indirect chain remains via BookingPopup + CancelBookingPopup → MyBookingsView (legacy view kept; superseded by MyReservationsView)).

**Cross-cutting Phase 14**:

- 0 emoji in `frontend/src/views/master/` (was 85 hits per OPEN scout); #048 cleanup complete in master scope.
- PRACTICE_TYPE_ICON migration complete in 4 master consumers (MasterDashboardView, MasterPracticesView via PracticeListItem delegation, AnalyticsView, PracticeListItem direct). Deprecated PRACTICE_TYPE_EMOJI shim retained in `displayHelpers.ts` for admin-scope cleanup deferred to S5+.
- Lint baseline shifted: 756 warnings (S1 baseline carried through MEGA-1 + MEGA-2) → 0 warnings (repo-wide post-MEGA-3). Likely cause: master views were the dominant warning source; refresh under current Coding Standards (TS strict, no any, proper imports, scoped styles) cleared them naturally.
- 0 new dependencies (Path Y discipline #047).
- 0 new test files (BACKLOG #44 deferred per #042 inverted in #049/#052).
- Anti-scope diffs verified empty: `router/index.ts`, `router/guards.ts`, `api/masters.ts`, `api/practices.ts`, `stores/ui.ts`, `stores/master.ts` (no extension landed; `nearestPractice` kept in-component), `package.json`.

**Phase 15 additions (S4 admin-refresh, MEGA-4, commit pending push):**

- `frontend/src/views/admin/AdminProfileView.vue` — refreshed under Velo DS using UserProfileView (skin 70/71) layout pattern. Avatar block + ProfileMenuItem-driven sections (Администрирование / Режим / Аккаунт). **TD-FE-ROLE-SWITCH preserved at 1-marker baseline** (admin-side baseline differs from master 4-marker pattern; existing `useUiStore.setUiMode('user')` logic intact; do NOT escalate to 4-marker convention per Path Y discipline). 157 LOC → ~289 LOC.
- `frontend/src/views/admin/AdminDashboardView.vue` — refreshed (skin 10/11 pattern adapted to admin metrics). Greeting block + 4-card StatCards row (Пользователи / Мастера / Практики / На проверке) consuming `AdminStatsResponse` + Callout amber when `pending_verifications > 0` linking to `/admin/masters`. 286 LOC → ~368 LOC.
- `frontend/src/views/admin/AdminMastersView.vue` — refreshed (skin 17 list pattern). Inline list-item template with status chips (verified mint / pending amber / rejected pink via `masterStatusVariant` from `adminHelpers.ts`) + VEmptyState branch + usePagination. Consumes `getPendingMasters` (paginated). 245 LOC → ~251 LOC.
- `frontend/src/views/admin/AdminMasterReviewView.vue` — refreshed (FormShell-pattern adapted) **degraded v1**: renders only fields available in `AdminMasterListItem` / `MasterApplyResponse` (master_status, role, is_active, names, avatar). Application content (bio/methods/experience/certifications/email/phone) NOT exposed by current backend types — placeholder Callout amber «Расширенные данные заявки пока недоступны — backend-расширение в очереди» anchors BACKLOG #104. Verify/reject CTAs via ConfirmModal (1 instance, danger variant for reject + reason textarea preserved from previous shape). 362 LOC → ~431 LOC.
- `frontend/src/views/admin/AdminReportsView.vue` — refreshed (skin 17 list pattern). Inline list-item template with severity/status chips (open amber / resolved mint / dismissed gray via `reportStatusVariant`) + VEmptyState. Consumes `getReports` (paginated). 305 LOC → ~312 LOC.
- `frontend/src/views/admin/AdminReportDetailView.vue` — refreshed. Content card + reporter row + severity Callout + 2 ConfirmModal instances for resolve/dismiss flows (compose pattern: raw VButton + ConfirmModal directly; **EntryActionMenu intentionally NOT consumed** due to emit vocabulary mismatch — edit/delete vs resolve/dismiss). Resolved/dismissed read-only display when status !== 'open'. 383 LOC → ~439 LOC.
- `frontend/src/views/admin/AdminConsistencyView.vue` — refreshed (AISummaryView 16 sectioned-pattern adapted). 3-card StatCards row (Всего / OK / Alert) + per-item rows grouped by category with status indicator (IconCheck mint OK / IconWarning amber ALERT) + criticality chip + VAccordion expandable details rendering `details: Record<string, unknown> | null` as preformatted JSON. Renders typed `ConsistencyResponse { items: SemaphoreResult[], total, ok_count, alert_count, run_at }` (P15 plan risk #3 closed — type was already fully-shaped in generated.ts; no backend gap). 337 LOC → ~368 LOC.
- **Post-verify fix (commit `8eede07` `fix:`)**: NEW `frontend/src/components/shared/RoleSwitcher.vue` (~130 LOC). Centralizes role-switch UX across MasterProfileView + AdminProfileView + UserProfileView (previously asymmetric: master 4 markers, admin 1 marker, user 0 — user view had no return path). Variant Z UX: shows all roles available to the account based on hierarchy ADMIN > MASTER > USER (hardcoded in component per `seed.py` source-of-truth — `UserResponse.role` is single-value); current uiMode marked active via route-prefix detection (NOT uiMode value — preserves binary `'default' | 'user'` uiStore contract); user-only accounts hide block entirely (`v-if="available.length > 1"`). Click on inactive row → `setUiMode + router.push`; click on active row → no-op (early return). TD-FE-ROLE-SWITCH centralized: was 5 scattered markers (master 4 + admin 1 + user 0); now 4 (master 1 + admin 1 + user 1 + RoleSwitcher 1). Anti-scope preserved (uiStore / authStore / router-guards / api unchanged).

**Cross-cutting Phase 15**:

- 0 emoji in `frontend/src/views/admin/` (was 25 hits per OPEN scout §S6); #048 cleanup complete in admin scope.
- **admin.ts store decision: continue direct-api** (no `frontend/src/stores/admin.ts` created). Verdict rationale: zero shared methods across api/admin.ts (every method has exactly 1 caller view); zero cross-view state candidates. Path Y MEDIUM discipline (#047) — no speculative abstraction. Documented inline in C66 cycle result; not promoted to `decisions.md` (sprint-specific evidence, not project doctrine).
- 1 dead-code method (`getMastersList` in api/admin.ts) noted; cleanup deferred to S5+ per BACKLOG #105.
- AdminMasterReviewView is **degraded v1**: full-fidelity v2 gated on backend extension (BACKLOG #104) exposing application content fields.
- Lint baseline preserved: 0 warnings (P14 baseline maintained through P15).
- 0 typecheck errors / 32/32 tests pass / build green / PWA precache 188 → 190 entries (+2 = IconQuestion + ConfirmModal chunk-split for AdminReportDetailView consumer; benign per Verification Scout §V6d).
- 0 new dependencies (Path Y discipline #047).
- 0 new test files (BACKLOG #44 deferred per #042 inverted in #049/#052).
- Anti-scope diffs verified empty: `router/index.ts`, `router/guards.ts`, `router/tabs.ts`, `api/admin.ts`, `api/generated.ts`, `api/types.ts`, `stores/*` (no new admin.ts; no extension), `components/shared/*` (consumed only), `components/ui/*` (consumed only), `utils/displayHelpers.ts`, `utils/adminHelpers.ts`, `package.json`.
- TD-FE-ROLE-SWITCH preserved at 1-marker baseline in AdminProfileView (different from MasterProfileView's 4-marker pattern — preserved as-is per Path Y; do NOT normalize across roles).

**Cross-cutting additions (speedrun, commits `6c5fd1f` + `af39b41`):**

- `frontend/src/components/icons/` — 25 new Vue-SVG icon components: 11 in MEGA-1 (IconArrowBack/Forward/Up, IconClose, IconFilter, IconDots, IconEdit, IconChevronRight, IconHandsClap, IconHeart, IconTheme) + 14 in MEGA-2 (IconMic, IconCheck, IconBookDream, IconBookFeather, IconLink, IconChevronDown, IconQuestion, IconBell, IconGlobe, IconShield, IconShare, IconLogout, IconSearch, IconTrash) + barrel `index.ts` updates. All follow currentColor + viewBox 24×24 + `:size` prop default 24 pattern.
- `frontend/src/utils/displayHelpers.ts` — `PRACTICE_TYPE_EMOJI` map refactored to `PRACTICE_TYPE_ICON: Record<string, Component>` consumed via `<component :is="...">` pattern. PRACTICE_TYPE_EMOJI / MOOD_EMOJI / RATING_EMOJI retained as deprecated empty-string compat shims for master/admin callers (S4/S5+ cleanup).
- `frontend/src/router/index.ts` — 20 new routes added across S2 (7) + S3 (13). Path count: 48 → 68. No `meta.requiresAuth` (auth gate at App.vue layer post-C16); no `roleGuard` wrapping per Phase 06 precedent.
- 0 new dependencies added (Path Y discipline #047).
- 0 new test files (BACKLOG #44 deferred per #042 inverted in speedrun #049).

**Reference (read-only legacy):**

- `docs/05_legacy/Design_prototype_legacy_2026-03-11/` — pre-bundle Figma snapshot (renamed from `Design_prototype/` during C01). Read-only reference.
- `docs/04_assets/velo-design-system-2026-04-23/` — bundle SSOT snapshot (~140 files: tokens, components, screens, illustrations, fonts). Source of truth per decision #006.

---

## Out of Scope for This Framework

- `backend/` — written by collaborating engineer; we consume, we do not edit
- Master role views in S2/S3 (decision #030) — current `views/master/` remains on bundle SSOT until S4
- Group chats for Messages — backlog per #85
- Real-time messaging / WebSocket — out of scope MVP
- Embedded Zoom SDK — Practice Live always external link per #037
- Root-level `VELO-*.md` files — reference only, maintained in `main`
- `docs/05_legacy/Design_prototype_legacy_2026-03-11/` — Figma snapshot before bundle arrival (2026-04-23). Read-only reference only. Bundle at `docs/04_assets/velo-design-system-2026-04-23/` is SSOT for design tokens, components, screens. See decisions.md #006.
- `velo-mockups/` — static HTML mocks; kept as legacy reference
- `diagrams/` — 9 mermaid diagrams; reference only

API contract SSOT for the frontend: `frontend/src/api/types.ts`. We do not maintain a separate `api-contract.md`.

---

## Coding Standards (Rule 17)

### Naming

- Files: PascalCase for Vue components (`UserDashboardView.vue`), camelCase for composables (`useAuth.ts`), kebab-case for CSS (`variables.css`)
- Routes: kebab-case (`/user/topup-success`)
- Pinia stores: singular, camelCase (`auth`, `balance`, `practices`)
- CSS variables: follow bundle naming convention (e.g., `--text-primary`, `--surface-default`, `--shadow-glow-white`) as defined in bundle's `colors_and_type.css`. Bundle is SSOT; token names change when bundle updates. See `decisions.md #009`.
- Prior constraint «do not rename existing variables» — SUPERSEDED (decision #009, 2026-04-24). DESIGN_MIGRATION.md v4 archived (decisions.md #009).

### TypeScript

- `strict: true` in `tsconfig.json`. No `any` without inline justification comment.
- Type imports use `import type { ... }` syntax.
- Vue components use `<script setup lang="ts">` exclusively.

### Error handling

- API errors via `useApiError` composable — never inline try/catch in components for API calls.
- UI error surface via `useToast` composable.
- No silent failures — always log or surface.

### Testing

- Vitest + happy-dom. Test files colocate with source: `SomeModule.ts` + `SomeModule.test.ts`.
- Run order: `npm run typecheck && npm run lint && npm run test` before commit.

### Imports

- Alias `@/` for `frontend/src/`.
- Order: Vue/framework, third-party, `@/` local, relative.

### Theme support

Light (default) + dark via `[data-theme="dark"]` attribute on root. Tokens for both themes defined in `frontend/src/styles/variables.css` (bundle-sourced). All port-to-Vue cycles must verify both themes; screenshots for both in manual test. UI toggle infrastructure lands in C25 (S2 P07). See decisions.md #008. Re-plan 2026-04-30 renumbered cycle from C19 → C25.

### CSS architecture

Token and global CSS files are imported via JavaScript module graph in `frontend/src/main.ts` (`import './styles/variables.css'` line 16; `import './styles/global.css'` line 17), NOT via CSS `@import` directives. This follows Vite/Vue convention for bundler optimization. Any protocol, prompt, or audit assuming `@import`-based cascade is incorrect for this project. See `decisions.md` #019.

### Build & dependency tooling

Any cycle whose Acceptance Criteria includes `npm run typecheck`, `npm run lint`, `npm run test`, or `npm run build` implicitly includes `frontend/package-lock.json` in scope. npm install may normalize the lockfile (peer markers, metadata) without changing versions or dependencies; such diffs commit as part of the cycle's phase. Explicit listing in Scope field is not required. See `decisions.md` #018.

---

## Tools & Pipelines

### Dev workflow

| Task | Command |
|---|---|
| Dev server | `npm run dev` (from `frontend/`) |
| Build | `npm run build` (runs `vue-tsc --noEmit && vite build`) |
| Lint | `npm run lint` / `npm run lint:fix` |
| Format | `npm run format` |
| Typecheck | `npm run typecheck` |
| Test | `npm run test` / `npm run test:watch` |
| Full stack local | `docker compose up` at repo root |

### Claude Design pipeline

See `docs/02_spec/03_Phase-Builder.md` § Design-Gen Cycle Type for the canonical procedure. Operational notes and lessons learned: `GUIDES/claude-design-pipeline.md`.

Claude Design project structure: ONE project per product (VELO = one project, all screens together, shared design system + attached context). Generation is one screen per request (not batch-gen multiple screens in one prompt). Consolidated per decision #006.

Brand lock (mandatory in every Claude Design prompt):

```
NEVER use: cream/beige backgrounds, serif display fonts, italic word accents,
terracotta/amber accents, backdrop-filter blur, glassmorphism effects.
USE: Marmelad Regular only (single weight), bundle tokens from
docs/04_assets/velo-design-system-2026-04-23/project/colors_and_type.css,
teal/peach/pink accents, radii md:8 / lg:15 / xl:24 / full:200,
FLAT semi-transparent surfaces.
See decisions.md #006, #007.
```

### ProbeKit lite profile

Six skills auto-run on Sprint close (`04_Sprint-Closer.md`): type-audit, code-audit, a11y-audit, responsive-audit, security-audit, design-audit. Full list and rationale in that protocol.

---

## Key Decisions

Flat log: `decisions.md`. Decisions #001-#052 as of S4 close (2026-05-04). Status mix: see `decisions.md` (ACTIVE / SUPERSEDED / DEPRECATED columns).

---

## Server & Deploy

Staging server is wired to branch `new_desing`. Deploy procedure and access details live in `SERVER-ACCESS.md` (gitignored). The S1 deploy was performed jointly with the backend partner who handed over the procedure; from S2 onward we deploy independently per `SERVER-ACCESS.md`.

Production promotion remains a separate manual step.

---

## Framework Profile

This project runs a reduced profile of SPEC v3.2 — labelled **SPEC v3.2-velo**. Divergences from stock v3.2:

- Disabled protocols: `06_Spec-Update`, `07_Brain-Next`, `Spec-Install`
- Disabled concepts: Entry/Stream parallel work, Balance Review, SPEC versioning layer, KB L0/L1/L2 hierarchy, ADR lifecycle
- Added: design-gen cycle type (see `03_Phase-Builder.md`), ProbeKit lite profile (see `04_Sprint-Closer.md`)

Original SPEC v3.2.0 files: `../05_legacy/_original_v3.2.0/`.
