# Velo — Architecture & Project Reference

> Frontend-only scope. Backend lives in `backend/` and is maintained separately.
> Loaded in every working chat alongside `01_Declaration.md`.
> Last updated: install (2026-04-23).

---

## Project Overview

Velo is a mobile Vue 3 PWA for wellness/meditation practices. Three user roles: `user`, `master`, `admin`. Modular monolith backend (FastAPI), separate code ownership.

Full functional and technical background: see root-level documents
- `VELO-Technical-Specification.md` — master technical spec
- `VELO-Frontend.md` — frontend architecture
- `VELO-Frontend-Specification.md` — UI/UX detailed spec
- `VELO-Design-Document.md` — design system principles
- `VELO-Anti-Patterns.md` — 6 frontend anti-patterns (FP-01..FP-06) to check

These are authoritative and read-only for this framework — do not edit from SPEC protocols, only reference.

---

## Components (frontend/src/)

See `FILE-TREE.md` for current inventory. Compact:

- `views/` — 31 page components across `user/` (11) · `master/` (10) · `admin/` (7) · `auth/` (3), plus three shells
- `components/` — icons, layout, shared, ui, master-specific
- `stores/` — Pinia: auth, balance, bookings, diary, master, practices, ui
- `composables/` — useAuth, useApiError, useToast, usePagination, usePracticeWindows
- `api/` — 9 files including client base, per-module modules, types, utils
- `router/` — index, guards, tabs (shell-layout with role guards)
- `styles/` — variables.css (semantic tokens), global.css
- `platform/`, `utils/`

---

## Out of Scope for This Framework

- `backend/` — written by collaborating engineer; we consume, we do not edit
- Root-level `VELO-*.md` files — reference only, maintained in `main`
- `Design_prototype/` — Figma-exported KB; referenced from Claude Design pipeline, not edited here
- `velo-mockups/` — static HTML mocks; kept as legacy reference
- `diagrams/` — 9 mermaid diagrams; reference only

API contract SSOT for the frontend: `frontend/src/api/types.ts`. We do not maintain a separate `api-contract.md`.

---

## Coding Standards (Rule 17)

### Naming

- Files: PascalCase for Vue components (`UserDashboardView.vue`), camelCase for composables (`useAuth.ts`), kebab-case for CSS (`variables.css`)
- Routes: kebab-case (`/user/topup-success`)
- Pinia stores: singular, camelCase (`auth`, `balance`, `practices`)
- CSS variables: `--velo-<domain>-<token>` (e.g., `--velo-bg-card`, `--velo-primary`). Do not rename existing variables — only change values. Add new variables at file end. See `DESIGN_MIGRATION.md` v4 in repo root.

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

Brand lock (mandatory in every Claude Design prompt):

```
NEVER use: cream/beige backgrounds, serif display fonts, italic word accents,
terracotta/amber accents.
USE: Marmelad font only, blue-slate base #4c6589, teal/peach/pink accents
per Design_prototype/tokens.md, glassmorphism with backdrop-blur(2px),
radii 15/200/5/100 strictly.
```

### ProbeKit lite profile

Six skills auto-run on Sprint close (`04_Sprint-Closer.md`): type-audit, code-audit, a11y-audit, responsive-audit, security-audit, design-audit. Full list and rationale in that protocol.

---

## Key Decisions

Flat log: `decisions.md`.

---

## Server & Deploy

Staging server is wired to branch `new_desing`. After commit + push, server updates and we verify the screen visually.

Server access details: `SERVER-ACCESS.md` (gitignored; filled in Sprint 1).

---

## Framework Profile

This project runs a reduced profile of SPEC v3.2 — labelled **SPEC v3.2-velo**. Divergences from stock v3.2:

- Disabled protocols: `06_Spec-Update`, `07_Brain-Next`, `Spec-Install`
- Disabled concepts: Entry/Stream parallel work, Balance Review, SPEC versioning layer, KB L0/L1/L2 hierarchy, ADR lifecycle
- Added: design-gen cycle type (see `03_Phase-Builder.md`), ProbeKit lite profile (see `04_Sprint-Closer.md`)

Original SPEC v3.2.0 files: `../02_spec/_original_v3.2.0/`.
