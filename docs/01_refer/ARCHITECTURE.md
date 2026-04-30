# Velo — Architecture & Project Reference

> Frontend-only scope. Backend lives in `backend/` and is maintained separately.
> Loaded in every working chat alongside `01_Declaration.md`.
> Last updated: 2026-04-28 (S1-Clean-Sync).

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

- `views/` — 32 page components across `user/` (11) · `master/` (10) · `admin/` (7) · `auth/` (4), plus three shells
- `components/` — icons, layout, shared, ui, master-specific
- `stores/` — Pinia: auth, balance, bookings, diary, master, practices, ui
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

Flat log: `decisions.md`. Active decisions #001-#026 as of S1 close (2026-04-28).

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
