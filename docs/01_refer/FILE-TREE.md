# Velo — File Tree

> Scope: `frontend/src/` + `docs/` only. Backend and other top-level directories are out of scope.
> Updated: 2026-04-23 (install).
> Validated by: `05_Clean-Sync.md` Step 1.

## frontend/src/

```
frontend/src/
├── App.vue                     # root component
├── main.ts                     # entry; mounts App, wires router + Pinia + PWA
├── env.d.ts                    # ambient types
├── api/
│   ├── client.ts               # axios/fetch base client
│   ├── types.ts                # API contract SSOT (mirrors backend schemas)
│   ├── utils.ts                # api helpers
│   ├── admin.ts
│   ├── bookings.ts
│   ├── diary.ts
│   ├── masters.ts
│   ├── payments.ts
│   └── practices.ts
├── components/
│   ├── icons/                  # Vue icon components
│   ├── layout/                 # MobileLayout, AdminLayout, VTabBar, VHeader
│   ├── master/                 # master-role shared pieces
│   ├── shared/                 # role-agnostic shared components
│   └── ui/                     # atoms and primitives
├── composables/
│   ├── useApiError.ts
│   ├── useAuth.ts              # waitUntilReady, restoreSession
│   ├── usePagination.ts
│   ├── usePagination.test.ts   # inline unit test (Vitest convention)
│   ├── usePracticeWindows.ts
│   └── useToast.ts
├── platform/                   # platform-specific adapters (PWA, native bridges)
├── router/
│   ├── index.ts                # routes + global beforeEach
│   ├── guards.ts               # roleRedirect, roleGuard, masterStatusGuard
│   └── tabs.ts                 # mobile tab bar definitions
├── stores/
│   ├── auth.ts
│   ├── balance.ts
│   ├── bookings.ts
│   ├── diary.ts
│   ├── master.ts
│   ├── practices.ts
│   └── ui.ts                   # incl. uiMode (user-mode switch for master/admin)
├── styles/
│   ├── variables.css           # --velo-* semantic tokens; MIGRATION rule: values change, names do not
│   └── global.css              # typography, resets, responsive
├── utils/                      # general helpers
└── views/
    ├── HomeView.vue
    ├── NotFoundView.vue
    ├── auth/
    │   ├── LoadingView.vue
    │   ├── LoadingErrorView.vue
    │   └── StandaloneStubView.vue
    ├── shells/
    │   ├── UserShell.vue
    │   ├── MasterShell.vue
    │   └── AdminShell.vue
    ├── user/                   # 11 views
    │   ├── UserDashboardView.vue
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

Total views: 34 (31 page views + 3 shells + 2 root).

## docs/

```
docs/
├── 01_refer/
│   ├── ARCHITECTURE.md
│   ├── ENVIRONMENT.md
│   ├── FILE-TREE.md            # this file
│   ├── BACKLOG.md
│   ├── decisions.md
│   ├── SERVER-ACCESS.md        # gitignored
│   └── GUIDES/
│       └── claude-design-pipeline.md
├── 02_spec/
│   ├── 01_Declaration.md
│   ├── 02_Sprint-Builder.md
│   ├── 03_Phase-Builder.md
│   ├── 04_Sprint-Closer.md
│   ├── 05_Clean-Sync.md
│   ├── Resolution.md
│   └── _original_v3.2.0/       # full v3.2.0 snapshot, reference-only
│       └── (9 files + README.md)
└── 03_sprint/
    └── .gitkeep
```
