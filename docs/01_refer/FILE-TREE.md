# Velo — File Tree

> Scope: `frontend/src/` + `docs/` only. Backend and other top-level directories are out of scope.
> Updated: 2026-04-28 (S1-Clean-Sync full refresh — Path B regeneration after S1 close).
> Validated by: `05_Clean-Sync.md` Step 1.

## frontend/src/

```
frontend/src/
├── App.vue                     # root component
├── main.ts                     # entry; mounts App, wires router + Pinia + global styles
├── env.d.ts                    # ambient types (Vite env, Vue SFC, Telegram WebApp SDK)
├── api/                        # backend integration layer
│   ├── client.ts               # fetch base client (15s AbortController, 401 callback, in-flight GET dedup F-09)
│   ├── generated.ts            # auto-generated TypeScript types from backend OpenAPI; do NOT edit (decisions.md #023); regen via self-host pipeline when partner stalls (decisions.md #046)
│   ├── types.ts                # re-export hub from generated + frontend-only union types (decisions.md #023)
│   ├── utils.ts                # buildQuery + shared API helpers
│   ├── admin.ts                # admin-side API
│   ├── bookings.ts             # bookings API
│   ├── diary.ts                # diary entries / check-ins / feedbacks / insights API
│   ├── masters.ts              # masters API
│   ├── payments.ts             # topup / Stripe API
│   └── practices.ts            # practices catalog API
├── assets/                     # bundle-extracted static assets (Phase 01 additions per #006/#024)
│   ├── brand/                  # mandala backdrop + runes + PNG (3 files)
│   ├── brand-icons/            # 12 PNG decorative icons (#024)
│   ├── illustrations/          # 3 SVGs (ai-analytics, live-practices, self-map)
│   ├── masters/                # 2 placeholder SVGs (alex-mindful, maria-flow)
│   ├── mood/                   # 3 mood SVGs (calm, neutral, sad)
│   └── patterns/               # 1 SVG (master-card)
├── components/
│   ├── icons/                  # Vue-SVG baseline icons (#024)
│   │   ├── IconBrain.vue
│   │   ├── IconBreathwork.vue
│   │   ├── IconCalendar.vue
│   │   ├── IconClock.vue
│   │   ├── IconDiary.vue
│   │   ├── IconFeedback.vue
│   │   ├── IconGroup.vue
│   │   ├── IconHome.vue
│   │   ├── IconMeditation.vue
│   │   ├── IconProfile.vue
│   │   ├── IconSuccess.vue
│   │   ├── IconSupport.vue
│   │   ├── IconWarning.vue
│   │   └── index.ts            # barrel export (DS-5)
│   ├── layout/                 # MobileLayout, AdminLayout, VTabBar, VHeader
│   │   ├── AdminLayout.vue
│   │   ├── MobileLayout.vue
│   │   ├── VHeader.vue
│   │   ├── VTabBar.vue
│   │   └── index.ts
│   ├── master/                 # master-role shared pieces
│   │   └── PracticeListItem.vue
│   ├── shared/                 # role-agnostic shared components
│   │   ├── BookingCard.vue
│   │   ├── BookingPopup.vue
│   │   ├── CancelBookingPopup.vue
│   │   ├── DiaryCheckinDetail.vue
│   │   ├── DiaryEntryDetail.vue
│   │   ├── DiaryEntryForm.vue
│   │   ├── DiaryFeedbackDetail.vue
│   │   ├── DiaryList.vue
│   │   ├── FormShell.vue
│   │   └── PracticeCard.vue
│   └── ui/                     # atoms and primitives
│       ├── VAccordion.vue
│       ├── VAvatar.vue
│       ├── VBadge.vue
│       ├── VButton.vue
│       ├── VCard.vue
│       ├── VCheckbox.vue
│       ├── VDivider.vue
│       ├── VEmptyState.vue
│       ├── VInput.vue
│       ├── VLoader.vue
│       ├── VModal.vue
│       ├── VNotification.vue
│       ├── VProgressBar.vue
│       ├── VSelect.vue
│       ├── VStatCard.vue
│       ├── VTag.vue
│       ├── VTextarea.vue
│       ├── VToast.vue
│       ├── VToggle.vue
│       ├── VeloLogo.vue
│       └── index.ts            # barrel export
├── composables/
│   ├── useApiError.ts          # extractApiError(e, fallback) — canonical catch-site narrowing
│   ├── useAuth.ts              # initAuth, waitUntilReady, restoreSession, deep-link parsing
│   ├── usePagination.ts        # generic limit/offset list state (covered by 9 unit tests)
│   ├── usePagination.test.ts   # vitest
│   ├── usePracticeWindows.ts   # check-in / live / feedback time-window helpers
│   └── useToast.ts             # transient toast surface
├── platform/                   # platform-specific adapters (TMA + standalone PWA)
│   ├── index.ts                # platform factory selection (Telegram vs standalone)
│   ├── standalone.ts           # PWA fallback (no Telegram SDK)
│   ├── telegram.ts             # Telegram WebApp SDK adapter (lazy getter; 10.1 fix)
│   └── types.ts                # Platform interface
├── router/
│   ├── index.ts                # routes + global beforeEach (43 path entries post-Phase-03)
│   ├── guards.ts               # roleRedirect, roleGuard, masterStatusGuard, applyGuard
│   └── tabs.ts                 # mobile tab bar definitions per role
├── stores/                     # Pinia (setup-style)
│   ├── auth.ts                 # session token, user, loginViaTelegram, restoreSession, logout
│   ├── balance.ts              # user balance state
│   ├── bookings.ts
│   ├── diary.ts                # entries + checkins + feedbacks + insights LRU cache
│   ├── master.ts               # master profile + my practices
│   ├── practices.ts            # practices catalog with filters
│   └── ui.ts                   # uiMode (user-mode switch for master/admin), theme
├── styles/
│   ├── variables.css           # bundle SSOT tokens (light + dark) — 130 tokens (#006, #009)
│   └── global.css              # CSS reset + base typography + scrollbar + bg layer
├── utils/
│   ├── adminHelpers.ts
│   ├── commission.ts
│   ├── constants.ts
│   ├── currency.ts             # eurStringToCents (FP-03 IEEE-754-aware)
│   ├── displayHelpers.ts
│   ├── format.test.ts          # vitest (23 tests)
│   ├── format.ts               # date / money / time formatters
│   └── practiceOptions.ts
└── views/
    ├── HomeView.vue            # root index
    ├── NotFoundView.vue        # /404 + catch-all
    ├── auth/                   # 4 views
    │   ├── LoadingView.vue
    │   ├── LoadingErrorView.vue
    │   ├── StandaloneStubView.vue
    │   └── WelcomeView.vue     # TMA splash for /welcome (decisions.md #025; created in S1 P03 C11)
    ├── shells/                 # 3 layout shells
    │   ├── UserShell.vue
    │   ├── MasterShell.vue
    │   └── AdminShell.vue
    ├── user/                   # 11 views
    │   ├── UserDashboardView.vue   # bundle DashboardScreen merged (S1 P03 C10; #024)
    │   ├── CalendarView.vue
    │   ├── DiaryView.vue
    │   ├── UserProfileView.vue
    │   ├── PracticeDetailView.vue
    │   ├── MyBookingsView.vue
    │   ├── CheckinView.vue
    │   ├── FeedbackView.vue
    │   ├── TopupView.vue
    │   ├── TopupSuccessView.vue
    │   └── TopupCancelView.vue
    ├── master/                 # 10 views
    │   ├── MasterDashboardView.vue
    │   ├── MasterPracticesView.vue
    │   ├── CreatePracticeView.vue
    │   ├── EditPracticeView.vue
    │   ├── AttendanceView.vue
    │   ├── AnalyticsView.vue
    │   ├── MasterProfileView.vue
    │   ├── MasterFinanceView.vue
    │   ├── MasterApplyView.vue
    │   └── MasterPendingView.vue
    └── admin/                  # 7 views
        ├── AdminDashboardView.vue
        ├── AdminMastersView.vue
        ├── AdminMasterReviewView.vue
        ├── AdminReportsView.vue
        ├── AdminReportDetailView.vue
        ├── AdminConsistencyView.vue
        └── AdminProfileView.vue
```

Total views: 37 (32 page views + 3 shells + 2 root views)
- page views: user/ 11 + master/ 10 + admin/ 7 + auth/ 4 = 32
- shells: 3 (UserShell, MasterShell, AdminShell)
- root: 2 (HomeView, NotFoundView)

## docs/

```
docs/
├── 01_refer/
│   ├── ARCHITECTURE.md             # project overview, components, coding standards, scope
│   ├── ENVIRONMENT.md              # system, tools, git workflow, info map
│   ├── FILE-TREE.md                # this file
│   ├── BACKLOG.md                  # code issues, tech debt, features (54 entries at S1 close)
│   ├── decisions.md                # 26 ACTIVE decisions (#001-#026 at S1 close)
│   ├── SERVER-ACCESS.md            # gitignored
│   ├── ARCHIVES/
│   │   ├── AUDIT/
│   │   │   └── S1-AUDIT.md         # S1 sprint audit (created in C07; archived at sprint close)
│   │   ├── CHANGELOG.md            # cross-sprint Clean-Sync transfer ledger
│   │   ├── CODE-AUDIT/
│   │   │   ├── S1-CODE-AUDIT.md    # consolidated audit record (Sprint-Closer Step 4)
│   │   │   └── PROBKIT-REVIEW/
│   │   │       └── AUDIT-TRACKER.md   # cross-skill metric history
│   │   ├── RETRO/
│   │   │   └── S1-RETRO.md         # moved from S1-pilot/ at Sprint-Closer Step 11
│   │   └── SNAPSHOT/
│   │       └── S1-SNAPSHOT.md      # sprint-close snapshot (Sprint-Closer Step 7)
│   └── GUIDES/
│       └── claude-design-pipeline.md   # design-gen cycle playbook
├── 02_spec/                        # active framework protocols (SPEC v3.2-velo)
│   ├── 01_Declaration.md
│   ├── 02_Sprint-Builder.md
│   ├── 03_Phase-Builder.md
│   ├── 04_Sprint-Closer.md
│   ├── 05_Clean-Sync.md
│   └── Resolution.md
├── 03_sprint/
│   ├── S1-pilot/
│   │   ├── S1-SPRINT.md            # Sprint 1 final-state (CLOSED 2026-04-28)
│   │   ├── HANDOFF-2026-04-24.md
│   │   ├── backend-coord-report.md   # S1 P02 C08 deliverable
│   │   ├── P01-bundle-migration/
│   │   │   ├── C01-bundle-snapshot.md
│   │   │   ├── C02-bundle-tokens-port.md
│   │   │   ├── C03-velo-rename.md
│   │   │   ├── C04-glass-cleanup.md
│   │   │   └── C06-api-contract-patch.md
│   │   └── P02-audit-backend/
│   │       ├── C07-audit-s1.md
│   │       ├── C08-backend-coord.md
│   │       └── C09-icons-strategy.md
│   ├── S2-bundle-port/
│   │   └── S2-SPRINT.md
│   └── S3-greenfield/
│       └── S3-SPRINT.md
├── 04_assets/                      # bundle SSOT (decisions.md #006)
│   └── velo-design-system-2026-04-23/   # 126 files: tokens, components, screens, illustrations, fonts
└── 05_legacy/                      # archives + reference-only snapshots (relocated 2026-04-28)
    ├── Design_prototype_legacy_2026-03-11/   # pre-bundle Figma snapshot (85 files; reference only)
    ├── _archive/
    │   └── DESIGN_MIGRATION_v4_2026-04-12.md   # SUPERSEDED per decisions.md #009
    └── _original_v3.2.0/           # full SPEC v3.2.0 framework snapshot (10 files)
```
