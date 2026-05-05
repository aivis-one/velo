# Velo — File Tree

> Scope: `frontend/src/` + `docs/` only. Backend and other top-level directories are out of scope.
> Updated: 2026-05-05 (S4-Clean-Sync Step 1 — drift fix: removed 2 PHANTOM entries (env ambient + legacy ruble icon); added frontend/src/data/ block, S4-master-admin sprint subtree, S4 SNAPSHOT + RETRO archives).
> Validated by: `05_Clean-Sync.md` Step 1.

## frontend/src/

```
frontend/src/
├── App.vue                     # root component
├── main.ts                     # entry; mounts App, wires router + Pinia + global styles
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
│   ├── icons/                  # Vue-SVG icon components (38; #024 baseline + speedrun additions #048)
│   │   ├── IconArrowBack.vue   # MEGA-1
│   │   ├── IconArrowForward.vue # MEGA-1
│   │   ├── IconArrowUp.vue     # MEGA-1
│   │   ├── IconBell.vue        # MEGA-2 (notifications row)
│   │   ├── IconBookDream.vue   # MEGA-2 (Сонник entries)
│   │   ├── IconBookFeather.vue # MEGA-2 (Дневник entries)
│   │   ├── IconBrain.vue
│   │   ├── IconBreathwork.vue
│   │   ├── IconCalendar.vue
│   │   ├── IconCheck.vue       # MEGA-2 (selection/done)
│   │   ├── IconChevronDown.vue # MEGA-2 (accordion expand)
│   │   ├── IconChevronRight.vue # MEGA-1
│   │   ├── IconClock.vue
│   │   ├── IconClose.vue       # MEGA-1
│   │   ├── IconDiary.vue
│   │   ├── IconDots.vue        # MEGA-1 (••• menu)
│   │   ├── IconEdit.vue        # MEGA-1 (pencil edit)
│   │   ├── IconFeedback.vue
│   │   ├── IconFilter.vue      # MEGA-1
│   │   ├── IconGlobe.vue       # MEGA-2 (language/timezone row)
│   │   ├── IconGroup.vue
│   │   ├── IconHandsClap.vue   # MEGA-1 (booking-success splash)
│   │   ├── IconHeart.vue       # MEGA-1 (feedback success)
│   │   ├── IconHome.vue
│   │   ├── IconLink.vue        # MEGA-2 (relationships orbit)
│   │   ├── IconLogout.vue      # MEGA-2 (Выйти row)
│   │   ├── IconMeditation.vue
│   │   ├── IconMic.vue         # MEGA-2 (composer mic)
│   │   ├── IconProfile.vue
│   │   ├── IconQuestion.vue    # MEGA-2 (support hero)
│   │   ├── IconSearch.vue      # MEGA-2 (search overlay)
│   │   ├── IconShare.vue       # MEGA-2 (Поделиться row)
│   │   ├── IconShield.vue      # MEGA-2 (Support deco)
│   │   ├── IconSuccess.vue
│   │   ├── IconSupport.vue
│   │   ├── IconTheme.vue       # MEGA-1 (light/dark toggle)
│   │   ├── IconTrash.vue       # MEGA-2 (delete action)
│   │   ├── IconWarning.vue
│   │   └── index.ts            # barrel export (DS-5; updated MEGA-1+MEGA-2)
│   ├── layout/                 # MobileLayout, AdminLayout, VTabBar, VHeader
│   │   ├── AdminLayout.vue
│   │   ├── MobileLayout.vue
│   │   ├── VHeader.vue
│   │   ├── VTabBar.vue
│   │   └── index.ts
│   ├── master/                 # master-role shared pieces
│   │   └── PracticeListItem.vue   # S4-P14 cascade-refreshed (PRACTICE_TYPE_ICON migration)
│   ├── shared/                 # role-agnostic shared components (33; speedrun + S4-P14 + S4-P15 post-verify additions tagged)
│   │   ├── AICommentaryCard.vue       # MEGA-2 (mint VELO AI tag + placeholder body)
│   │   ├── BookingCard.vue
│   │   ├── BookingPopup.vue
│   │   ├── CalendarFilterOverlay.vue  # MEGA-1 (chip filter modal)
│   │   ├── Callout.vue                # MEGA-1 (amber/mint variant warnings)
│   │   ├── CancelBookingPopup.vue
│   │   ├── ChatBubble.vue             # MEGA-2 (incoming/outgoing variants)
│   │   ├── ConfirmModal.vue           # S4-P14 (BACKLOG #48 closure; Teleport-inline confirm dialog)
│   │   ├── ConversationListItem.vue   # MEGA-2 (avatar + preview + unread badge)
│   │   ├── DiaryCheckinDetail.vue
│   │   ├── DiaryComposer.vue          # MEGA-2 (collapsed pill + mic + send)
│   │   ├── DiaryComposerExpanded.vue  # MEGA-2 (full modal with mood + practice picker)
│   │   ├── DiaryEntryBubble.vue       # MEGA-2 (timeline-mode bubble)
│   │   ├── DiaryEntryDetail.vue
│   │   ├── DiaryEntryFlat.vue         # MEGA-2 (list-mode card)
│   │   ├── DiaryEntryForm.vue
│   │   ├── DiaryFeedbackDetail.vue
│   │   ├── DiaryFilterOverlay.vue     # MEGA-2 (date picker + type chips)
│   │   ├── DiaryList.vue              # legacy (delegated by old DiaryView; kept as compat shim)
│   │   ├── DiarySearchOverlay.vue     # MEGA-2 (search input + history pills)
│   │   ├── EntryActionMenu.vue        # MEGA-2 (••• → edit/trash floating stack)
│   │   ├── FormShell.vue
│   │   ├── MasterCardSummary.vue      # MEGA-1 (master row with verified chip)
│   │   ├── PracticeCard.vue
│   │   ├── ProfileMenuItem.vue        # MEGA-1 (RouterLink/button row)
│   │   ├── RelationshipChain.vue      # MEGA-2 (horizontal SVG chain)
│   │   ├── ReservationCard.vue        # MEGA-2 (booking card with status chip)
│   │   ├── RoleSwitcher.vue           # S4-P15 post-verify fix (centralizes TD-FE-ROLE-SWITCH; consumed by Master/Admin/User profile views)
│   │   ├── SpineDivider.vue           # MEGA-2 (date divider with text-glyph ornament)
│   │   ├── StatCard.vue               # MEGA-1 (compact metric tile)
│   │   ├── ThreadComposer.vue         # MEGA-2 (input + send only — no mic)
│   │   ├── UndoSnackbar.vue           # MEGA-2 (auto-dismiss timer + action button)
│   │   └── WeekStrip.vue              # MEGA-1 (7-day strip with practice dots)
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
├── data/                       # static JSON data tables consumed by views
│   └── cities.json             # MEGA-2 (S2-P06 C21 + S3-P12 C47) — 118-entry city → IANA mapping for OnboardingTimezoneView + LanguageTimezoneView (per BACKLOG #95 expansion deferred)
├── platform/                   # platform-specific adapters (TMA + standalone PWA)
│   ├── index.ts                # platform factory selection (Telegram vs standalone)
│   ├── standalone.ts           # PWA fallback (no Telegram SDK)
│   ├── telegram.ts             # Telegram WebApp SDK adapter (lazy getter; 10.1 fix)
│   └── types.ts                # Platform interface
├── router/
│   ├── index.ts                # routes + global beforeEach (43 path entries post-Phase-03)
│   ├── guards.ts               # roleRedirect, roleGuard, masterStatusGuard, applyGuard
│   └── tabs.ts                 # mobile tab bar definitions per role
├── stores/                     # Pinia (setup-style; 9 stores post-speedrun)
│   ├── auth.ts                 # session token, user, loginViaTelegram, restoreSession, logout
│   ├── balance.ts              # user balance state
│   ├── bookings.ts             # MEGA-1 extended: upcomingBookings + pastBookings + statusChipVariant
│   ├── diary.ts                # MEGA-2 extended: typeFilter + searchQuery + searchHistory + filteredEntries
│   ├── master.ts               # master profile + my practices
│   ├── messages.ts             # MEGA-2 NEW (mock conversations + activeMessages + sendMessage toast)
│   ├── notifications.ts        # MEGA-2 NEW (4 toggles + localStorage init/watch)
│   ├── practices.ts            # practices catalog with filters
│   └── ui.ts                   # MEGA-1 extended: theme + initTheme + setTheme (localStorage + media listener)
├── styles/
│   ├── variables.css           # bundle SSOT tokens (light + dark) — 130 tokens (#006, #009)
│   └── global.css              # CSS reset + base typography + scrollbar + bg layer
├── utils/
│   ├── adminHelpers.ts         # report target labels (emoji prefix removed in MEGA-2 per #048)
│   ├── commission.ts
│   ├── constants.ts
│   ├── currency.ts             # eurStringToCents (FP-03 IEEE-754-aware)
│   ├── displayHelpers.ts       # PRACTICE_TYPE_ICON map (refactored from EMOJI in MEGA-1; deprecated emoji shims kept for legacy callers)
│   ├── format.test.ts          # vitest (23 tests)
│   ├── format.ts               # date / money / time formatters
│   ├── mockMessagesData.ts     # MEGA-2 NEW (3 conversations × 2 messages mock fixtures)
│   └── practiceOptions.ts
└── views/
    ├── HomeView.vue            # root index
    ├── NotFoundView.vue        # /404 + catch-all
    ├── auth/                   # 8 views (was 4 at S1)
    │   ├── LoadingView.vue
    │   ├── LoadingErrorView.vue
    │   ├── LoginView.vue       # Phase 06 (S2-P06 C17) — PWA email/password mock
    │   ├── OAuthLoadingView.vue # Phase 06 (S2-P06 C19) — mock OAuth callback splash
    │   ├── OnboardingCarouselView.vue # Phase 06 (S2-P06 C20) — 3-slide carousel
    │   ├── OnboardingTimezoneView.vue # Phase 06 (S2-P06 C21) — city → IANA + PATCH /users/me
    │   ├── RegisterView.vue    # Phase 06 (S2-P06 C18) — PWA register mock
    │   ├── StandaloneStubView.vue # legacy (gate moved to App.vue layer at C16; retained for auth-error reuse)
    │   └── WelcomeView.vue     # Phase 06 (S2-P06 C16) — TMA + PWA dual-branch
    ├── shells/                 # 3 layout shells
    │   ├── UserShell.vue
    │   ├── MasterShell.vue
    │   └── AdminShell.vue
    ├── user/                   # 30 views (was 11 at S1)
    │   ├── AISummaryView.vue           # MEGA-2 (S3-P12 C50) — placeholder weekly summary
    │   ├── BookedPracticeView.vue      # MEGA-1 (S2-P08 C26) — day-of practice context
    │   ├── BookingDetailView.vue       # MEGA-1 (S2-P08 C28) — read-only retrospect view
    │   ├── BookingSuccessView.vue      # MEGA-1 (S2-P08 C26) — IconHandsClap + master-request mock
    │   ├── CalendarView.vue            # MEGA-1 (S2-P07 C23) — refresh
    │   ├── CheckinSuccessView.vue      # MEGA-1 (S2-P08 C30) — IconSuccess + Начать практику CTA
    │   ├── CheckinView.vue             # MEGA-1 (S2-P08 C30) — refresh (3-icon mood picker)
    │   ├── CheckinsCategoryView.vue    # MEGA-2 (S3-P10 C39) — only check-ins
    │   ├── DiaryEntryView.vue          # MEGA-2 (S3-P11 C42-44) — read + edit + delete with undo
    │   ├── DiaryView.vue               # MEGA-2 (S3-P10 C36) — full rewrite (timeline + list)
    │   ├── EditProfileView.vue         # MEGA-1 (S2-P09 C34) — form + delete account mock
    │   ├── EntriesCategoryView.vue     # MEGA-2 (S3-P10 C39) — Дневник + Сонник combined
    │   ├── FeedbackSuccessView.vue     # MEGA-1 (S2-P08 C32) — IconHeart + В дневник
    │   ├── FeedbackView.vue            # MEGA-1 (S2-P08 C32) — refresh (3-button rating)
    │   ├── FeedbacksCategoryView.vue   # MEGA-2 (S3-P10 C39) — only feedbacks
    │   ├── LanguageTimezoneView.vue    # MEGA-2 (S3-P12 C47) — radio + city autocomplete + PATCH
    │   ├── MasterProfilePublicView.vue # MEGA-2 (S3-P12 C51) — DEGRADED v1 per BACKLOG #99
    │   ├── MessagesListView.vue        # MEGA-2 (S3-P12 C49) — 3 mock conversations
    │   ├── MyBookingsView.vue          # legacy (kept; superseded by MyReservationsView)
    │   ├── MyReservationsView.vue      # MEGA-2 (S3-P13 C52) — Предстоящие + Прошедшие
    │   ├── NotificationsView.vue       # MEGA-2 (S3-P12 C46) — 4 toggles
    │   ├── PracticeDetailView.vue      # MEGA-1 (S2-P08 C24) — refresh
    │   ├── PracticeLiveView.vue        # MEGA-1 (S2-P08 C31) — Zoom external + Check-in re-open
    │   ├── RelationshipsView.vue       # MEGA-2 (S3-P11 C45) — chain + AI placeholder
    │   ├── SupportFormView.vue         # MEGA-2 (S3-P12 C48) — subject + message mock
    │   ├── ThreadView.vue              # MEGA-2 (S3-P12 C49) — chat bubbles + composer
    │   ├── TopupCancelView.vue         # legacy (S1; emoji removed in MEGA-2 per #048)
    │   ├── TopupSuccessView.vue        # legacy (S1; emoji removed in MEGA-2 per #048)
    │   ├── TopupView.vue               # legacy (S1)
    │   ├── UserDashboardView.vue       # MEGA-1 (S2-P07 C22) — refresh
    │   └── UserProfileView.vue         # MEGA-1 (S2-P09 C33) — refresh (3 sections + Logout)
    ├── master/                 # 10 views (refreshed S4-P14 MEGA-3; emoji 85 → 0; Path Y MEDIUM)
    │   ├── MasterDashboardView.vue        # S4-P14 (greeting + StatCards + PRACTICE_TYPE_ICON migration)
    │   ├── MasterPracticesView.vue        # S4-P14 (list + status chips; PracticeListItem cascade)
    │   ├── CreatePracticeView.vue         # S4-P14 (6-section form refresh; W-markers preserved)
    │   ├── EditPracticeView.vue           # S4-P14 (refresh + ConfirmModal integration; -57 LOC)
    │   ├── AttendanceView.vue             # S4-P14 (refresh + ConfirmModal integration; -53 LOC)
    │   ├── AnalyticsView.vue              # S4-P14 (refresh + RATING_BARS_CONFIG icon migration)
    │   ├── MasterProfileView.vue          # S4-P14 (refresh; TD-FE-ROLE-SWITCH preserved)
    │   ├── MasterFinanceView.vue          # S4-P14 (refresh; min/fee cents reads preserved per #022)
    │   ├── MasterApplyView.vue            # S4-P14 (3-step form refresh; native checkboxes preserved)
    │   └── MasterPendingView.vue          # S4-P14 (status splash refresh)
    └── admin/                  # 7 views (refreshed S4-P15 MEGA-4; emoji 25 → 0; Path Y MEDIUM)
        ├── AdminDashboardView.vue        # S4-P15 (StatCards row + AdminStatsResponse consumer)
        ├── AdminMastersView.vue          # S4-P15 (paginated list + status chips via masterStatusVariant)
        ├── AdminMasterReviewView.vue     # S4-P15 (degraded v1; ConfirmModal verify/reject; BACKLOG #104 anchor)
        ├── AdminReportsView.vue          # S4-P15 (paginated list + status chips via reportStatusVariant)
        ├── AdminReportDetailView.vue     # S4-P15 (compose VButton + ConfirmModal; EntryActionMenu NOT consumed)
        ├── AdminConsistencyView.vue      # S4-P15 (typed ConsistencyResponse + VAccordion details)
        └── AdminProfileView.vue          # S4-P15 (TD-FE-ROLE-SWITCH 1-marker baseline preserved)
```

Total views: 60 (55 page views + 3 shells + 2 root views)
- page views: user/ 30 + master/ 10 + admin/ 7 + auth/ 8 = 55
- shells: 3 (UserShell, MasterShell, AdminShell)
- root: 2 (HomeView, NotFoundView)
- Router path count: 68 (S1 baseline 43 → Phase 06 close 48 → speedrun close 68)

## docs/

```
docs/
├── 01_refer/
│   ├── ARCHITECTURE.md             # project overview, components, coding standards, scope
│   ├── ENVIRONMENT.md              # system, tools, git workflow, info map
│   ├── FILE-TREE.md                # this file
│   ├── BACKLOG.md                  # code issues, tech debt, features (~100 entries post-S2-S3-Speedrun)
│   ├── decisions.md                # 49 ACTIVE decisions (#001-#049 post-S2-S3-Speedrun)
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
│   │   │   ├── S1-RETRO.md         # moved from S1-pilot/ at Sprint-Closer Step 11
│   │   │   ├── S2-RETRO.md         # S2-S3-Speedrun closure 2026-04-30
│   │   │   ├── S3-RETRO.md         # S2-S3-Speedrun closure 2026-04-30
│   │   │   └── S4-RETRO.md         # S4-Sprint-Closer 2026-05-04
│   │   └── SNAPSHOT/
│   │       ├── S1-SNAPSHOT.md      # sprint-close snapshot (Sprint-Closer Step 7)
│   │       ├── S2-SNAPSHOT.md      # S2-S3-Speedrun closure 2026-04-30
│   │       ├── S3-SNAPSHOT.md      # S2-S3-Speedrun closure 2026-04-30
│   │       └── S4-SNAPSHOT.md      # S4-Sprint-Closer 2026-05-04 (master + admin refresh; speedrun #052)
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
│   │   ├── S2-SPRINT.md            # CLOSED 2026-04-30 (Phase 05-09)
│   │   ├── BACKEND-COORDINATION.md # cross-team coordination SSOT (decision #041)
│   │   └── DESIGN-DECISIONS-LOG.md # designer/PM/sponsor decisions log (decision #041)
│   ├── S3-greenfield/
│   │   └── S3-SPRINT.md            # CLOSED 2026-04-30 (Phase 10-13)
│   └── S4-master-admin/
│       ├── S4-SPRINT.md            # CLOSED 2026-05-04 (Phase 14 master-refresh + Phase 15 admin-refresh; speedrun #052)
│       ├── P14-master-refresh/
│       │   └── P14-master-refresh.md   # MEGA-3 (10 master views refresh; #050 designer-independent)
│       └── P15-admin-refresh/
│           └── P15-admin-refresh.md   # MEGA-4 (7 admin views refresh; #051 admin unfreeze)
├── 04_assets/                      # bundle SSOT (decisions.md #006)
│   ├── velo-design-system-2026-04-23/   # original bundle SSOT (126 files: tokens, components, screens, illustrations, fonts)
│   └── velo-design-system-2026-04-30/   # designer batch 2 (~55 mockups, ~34 unique views; per Phase 06 §S1 + BACKLOG #92)
└── 05_legacy/                      # archives + reference-only snapshots (relocated 2026-04-28)
    ├── Design_prototype_legacy_2026-03-11/   # pre-bundle Figma snapshot (85 files; reference only)
    ├── _archive/
    │   └── DESIGN_MIGRATION_v4_2026-04-12.md   # SUPERSEDED per decisions.md #009
    └── _original_v3.2.0/           # full SPEC v3.2.0 framework snapshot (10 files)
```
