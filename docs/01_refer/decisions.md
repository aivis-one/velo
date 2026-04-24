# Velo — Decisions Log

> Flat replacement for ADR hierarchy. One row per meaningful decision.
> Consumed by: anyone planning work that might conflict with a past decision.
> Updated: 2026-04-23 (install).

| # | Date | Decision | Why | Where it lives | Status |
|---|---|---|---|---|---|
| 001 | 2026-04-23 | Adopt SPEC v3.2-velo reduced profile | Full SPEC v3.2 is over-scaled for single-dev frontend project | `ARCHITECTURE.md` § Framework Profile | ACTIVE |
| 002 | 2026-04-23 | Use Claude Design for every screen in Sprint 1 pilot | Learn the tool fully before committing to a rollout strategy | `03_Phase-Builder.md` § Design-Gen, Sprint 1 plan | ACTIVE |
| 003 | 2026-04-23 | No separate `api-contract.md` | `frontend/src/api/types.ts` is the SSOT for frontend | `ARCHITECTURE.md` § Out of Scope | ACTIVE |
| 004 | 2026-04-23 | Drop protocols 06/07/Spec-Install from active set | Framework maintenance not applicable; first-install is this plan | `02_spec/` (active) + `_original_v3.2.0/` | ACTIVE |
| 005 | 2026-04-23 | Single ARCHITECTURE.md instead of separate VISION / ROADMAP | Project is small; splits add overhead without value | `ARCHITECTURE.md` | ACTIVE |
| 006 | 2026-04-24 | Bundle (2026-04-23) = SSOT of design system | Bundle is newer than Design_prototype (2026-03-11); bundle README declares pixel-perfect recreation approach | `ARCHITECTURE.md` §Tools + §Out of Scope; `docs/02_spec_assets/velo-design-system-2026-04-23/` | ACTIVE |
| 007 | 2026-04-24 | Flat aesthetic; no backdrop-filter / no glassmorphism | Bundle README explicitly declares "No backdrop-filter: blur"; performance on Telegram WebView | `ARCHITECTURE.md` §Brand-lock; variables.css cleanup in C04 | ACTIVE |
| 008 | 2026-04-24 | Dark mode in scope S1 — tokens only; UI toggle infrastructure deferred to C19 (S2) | Bundle provides full dark-mode tokens via `[data-theme="dark"]`; stores/ui.ts needs theme field + localStorage + prefers-color-scheme listener | `ARCHITECTURE.md` §Coding Standards Theme support; C02 (tokens), C19 (UI) | ACTIVE |
| 009 | 2026-04-24 | Token rename to bundle namespace; DESIGN_MIGRATION.md v4 SUPERSEDED | Bundle introduces new token names (`--text-primary`, `--surface-default`, etc.). Maintaining velo-prefixed names requires ongoing translation layer; trade-off favors bundle compliance | `ARCHITECTURE.md` §Coding Standards; `docs/_archive/DESIGN_MIGRATION_v4_2026-04-12.md`; C03 grep/replace 577 usages | ACTIVE |
| 010 | 2026-04-24 | Admin views (7) + MH-08 + MH-11 + MH-12 → BACKLOG for S4+ | 3-sprint capacity fits user-core + master-core + MH-17 only; admin has no MH card | `BACKLOG.md` cards 4–7; `S3-SPRINT.md` Out of Scope | ACTIVE |
| 011 | 2026-04-24 | 3 sprints planned in one Sprint-Builder session (S1 + S2 + S3) | Single-dev continuity; scout-driven planning benefits all sprints together; risk of carry-forward handled via C14 retrospective | `S2-SPRINT.md` Status header; `S3-SPRINT.md` Status header; Sprint-Builder v3.2-velo deviation | ACTIVE |
| 012 | 2026-04-24 | Bundle AuthScreen NOT copied 1:1; Velo remains Telegram-first | Bundle AuthScreen shows Google/Apple OAuth which Velo does not use (TMA-only auth via initData). Bundle AuthScreen retained as landing/desktop reference | C11 WelcomeView design-gen; C26 TMA Auth polish; `frontend/src/platform/telegram.ts` | ACTIVE |
| 013 | 2026-04-24 | VELO = Telegram Mini App with PWA fallback for non-Telegram browsers | Confirmed via `frontend/src/platform/` (telegram.ts + standalone.ts + App.vue routing); vite-plugin-pwa in deps; no `@telegram-apps/sdk` npm pkg (uses global `window.Telegram.WebApp`) | `ARCHITECTURE.md` §Project Overview; `frontend/src/platform/*` | ACTIVE |
| 014 | 2026-04-24 | Phases numbered globally across project (P01–P12 in S1–S3 plan) | Matches cycle numbering rule; avoids phase-number collision across sprints | `01_Declaration.md` §Cycle Numbering Rule (applies to phases by analogy); S1/S2/S3 SPRINT files | ACTIVE |

Status values: ACTIVE, SUPERSEDED (by #NNN), DEPRECATED.
