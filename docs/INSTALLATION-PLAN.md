# SPEC v3.2 → Velo Installation Plan

> Ephemeral document. Created before install, deleted after successful validation.
> Language: English (artifacts rule). Chat discussion stays Russian.
> Confirmed answers: Q1–Q24 in conversation (2026-04-22 … 2026-04-23).

---

## 0. Meta

| Item | Value |
|---|---|
| Goal | Install adapted SPEC v3.2 framework in `docs/` — Velo-lite profile, frontend-only, single developer |
| Source framework | SPEC v3.2.0 (nine files currently in `docs/02_spec/`) |
| Target framework label | `SPEC v3.2-velo` |
| Branch | `new_desing` (continue existing, no new branch) |
| Commit strategy | Execute prompt performs install + commit + push in one pass (Q23=b) |
| Scope boundary | **Everything created stays under `docs/`. Never touch `backend/`, `frontend/`, or root-level `VELO-*.md` files. Reference them via links only.** |
| Artifact language | English |
| Validation | Run full validation template (§11) against final state — single pass over all changes |
| Success trigger | Sprint 1 produces one fully-rendered screen through Claude Design → Git commit → server deploy → visual verification |

---

## 1. Pre-flight Checks

Before the execute prompt runs, these conditions must hold (Claude Code verifies in prompt Pre-Exec block):

- [ ] Working tree clean on branch `new_desing` (no uncommitted changes)
- [ ] `docs/02_spec/` contains all 9 original SPEC v3.2.0 files (01_Declaration, 02_Sprint-Builder, 03_Phase-Builder, 04_Sprint-Closer, 05_Clean-Sync, 06_Spec-Update, 07_Brain-Next, Resolution, Spec-Install)
- [ ] `docs/ENVIRONMENT.md` (BOGame version, to be deleted) present
- [ ] `docs/01-audit-current-state.md` and `docs/02-sprint-plan-preliminary.md` present (to be deleted)
- [ ] `.gitignore` accessible at repo root
- [ ] Root-level `VELO-*.md` files and `Design_prototype/` untouched (sanity reference)

If any pre-flight fails → STOP and report. Do not proceed with partial state.

---

## 2. Operations Overview (at-a-glance)

| # | Operation | Target | Result |
|---|---|---|---|
| A | DELETE | `docs/01-audit-current-state.md` | Superseded by new SPEC artifacts |
| B | DELETE | `docs/02-sprint-plan-preliminary.md` | Superseded by `S1-SPRINT.md` (created in Sprint 1) |
| C | DELETE | `docs/ENVIRONMENT.md` | BOGame version, replaced by Velo version under `01_refer/` |
| D | CREATE | `docs/02_spec/_original_v3.2.0/` | Snapshot of all 9 unmodified SPEC v3.2.0 files |
| E | MOVE | `docs/02_spec/06_Spec-Update.md` → `_original_v3.2.0/` only (remove from active) | Not used in Velo profile |
| F | MOVE | `docs/02_spec/07_Brain-Next.md` → `_original_v3.2.0/` only | Not used in Velo profile |
| G | MOVE | `docs/02_spec/Spec-Install.md` → `_original_v3.2.0/` only | Not used (install is this plan) |
| H | MODIFY | `docs/02_spec/01_Declaration.md` | Apply universal rules + file-specific cuts (§5.3) |
| I | MODIFY | `docs/02_spec/02_Sprint-Builder.md` | Same |
| J | MODIFY | `docs/02_spec/03_Phase-Builder.md` | Same + ADD design-gen cycle type (§5.4) |
| K | MODIFY | `docs/02_spec/04_Sprint-Closer.md` | Same + ADD ProbeKit lite profile (§5.4) |
| L | MODIFY | `docs/02_spec/05_Clean-Sync.md` | Same |
| M | MODIFY | `docs/02_spec/Resolution.md` | BOGAME cleanup only; otherwise intact |
| N | CREATE | `docs/01_refer/ARCHITECTURE.md` | Full content per §6.1 |
| O | CREATE | `docs/01_refer/ENVIRONMENT.md` | Full content per §6.2 |
| P | CREATE | `docs/01_refer/FILE-TREE.md` | Full content per §6.3 |
| Q | CREATE | `docs/01_refer/BACKLOG.md` | Template per §6.4 |
| R | CREATE | `docs/01_refer/decisions.md` | Template per §6.5 |
| S | CREATE | `docs/01_refer/SERVER-ACCESS.md` | Template per §6.6 (filled in Sprint 1) |
| T | CREATE | `docs/01_refer/GUIDES/claude-design-pipeline.md` | Template per §6.7 (filled in Sprint 1) |
| U | CREATE | `docs/03_sprint/` | Empty directory with `.gitkeep` |
| V | MODIFY | `.gitignore` | Add `SERVER-ACCESS.md` safeguard (§8) |
| W | COMMIT + PUSH | All of the above in one commit | Message per §9 |

Total: 3 deletions, 3 moves, 6 file modifications, 8 new files, 1 new directory, 1 gitignore edit, 1 commit.

---

## 3. Deletion Operations (A, B, C)

Straight `rm` (via Claude Code). No archival — these files have no long-term value.

| File | Reason |
|---|---|
| `docs/01-audit-current-state.md` | Working draft; its data is migrated into `FILE-TREE.md` + `ARCHITECTURE.md` |
| `docs/02-sprint-plan-preliminary.md` | Preliminary thinking; superseded by actual Sprint 1 plan in `S1-SPRINT.md` |
| `docs/ENVIRONMENT.md` | BOGame-specific; replaced by clean Velo version at `docs/01_refer/ENVIRONMENT.md` |

---

## 4. Original Snapshot (D)

Create directory `docs/02_spec/_original_v3.2.0/`.

Copy **all 9 files** from `docs/02_spec/` into it, **unmodified**, before any editing starts:

```
docs/02_spec/_original_v3.2.0/
├── 01_Declaration.md
├── 02_Sprint-Builder.md
├── 03_Phase-Builder.md
├── 04_Sprint-Closer.md
├── 05_Clean-Sync.md
├── 06_Spec-Update.md
├── 07_Brain-Next.md
├── Resolution.md
└── Spec-Install.md
```

Add `docs/02_spec/_original_v3.2.0/README.md`:

```markdown
# SPEC v3.2.0 — Original Snapshot

Untouched copies of the nine files from https://github.com/.../spec-v3.2.0 as received on 2026-04-23.

**Not loaded in working chats.** Kept as reference for:
- Recovering concepts dropped in Velo profile
- Auditing what was changed and why
- Upstream sync if we ever re-adopt the full framework

Active Velo-profile files live in the parent directory.
```

---

## 5. Protocol Modifications (E–M)

### 5.1 Universal rules (apply to every active protocol file)

**a) BOGAME suffix removal — search-and-replace table**

| Find | Replace with |
|---|---|
| `ARCHITECTURE-BOGAME.md` | `ARCHITECTURE.md` |
| `FILE-TREE-BOGAME.md` | `FILE-TREE.md` |
| `BACKLOG-BOGAME.md` | `BACKLOG.md` |
| `docs/01_refer/KNOWLEDGE/ADR-BOGAME/` | `docs/01_refer/decisions.md` |
| `docs/01_refer/KNOWLEDGE/BACKLOG-BOGAME.md` | `docs/01_refer/BACKLOG.md` |
| `docs/01_refer/KNOWLEDGE/` (any remaining hit) | `docs/01_refer/` |
| `KNOWLEDGE-BOGAME.md` | (remove reference; replace with `decisions.md` if context is ADR-lookup, else remove sentence) |
| `VISION-BOGAME.md` | (remove reference; replace with `ARCHITECTURE.md` §Project overview if needed) |
| `ROADMAP-BOGAME.md` | (remove reference; replace with `ARCHITECTURE.md` §Roadmap if needed) |
| `CHANGELOG-BOGAME.md` | (remove references entirely — concept not kept) |
| `SPEC-BACKLOG.md` | (remove references entirely) |
| `SPEC-CHANGELOG.md` | (remove references entirely) |
| `Information-Flow-Matrix.md` | (remove references entirely) |
| `Rule-Enforcement-Matrix.md` | (remove references entirely) |
| `SPEC-ARCHITECTURE.md`, `SPEC-VISION.md`, `SPEC-ROADMAP.md`, `SPEC-FILE-TREE.md`, `SPEC-KNOWLEDGE.md` | (remove references entirely) |
| ` - BOGame ` (inline project name) | ` - Velo ` |
| `BOGame` (standalone) | `Velo` |

**b) Concepts to strip from every protocol** (any section, bullet, or rule exclusively about these — delete):

- Entry (E{NN}) numbering, parallel streams, stream scope
- Stream Planning (Sprint-Builder Step 5 construct)
- Global entry number assignment (E90+)
- Balance Review / Codebase Balance findings / Balance assessment
- Capacity Check at 40–60 cycles (replace with "15–25 cycles" where the concept is preserved)
- Recurring carry-forward `[RECURRING-3+]` auto-promote
- SPEC versioning (Tier 1/2/3, header-anchor sync rule, SPEC-CHANGELOG writeback)
- Framework Balance Check, Gene Analysis
- KB/ADR L0/L1/L2 knowledge hierarchy (Rule 18 style) — replace with single-file `decisions.md` lookup
- ADR lifecycle workflow (PROPOSED → ACCEPTED → IMPLEMENTED)
- vector-debates / kb-rag-builder skill orchestration
- SPEC BACKLOG / SPEC-LOG / SPEC Update Banner / SPEC Phase handoff
- Information-Flow-Matrix / Rule-Enforcement-Matrix / Tier Registry / Versioning Rules section / Changelog Rule section

**c) Rules to drop (remove from Declaration, remove any reference elsewhere):**

| Rule # | Title | Reason dropped |
|---|---|---|
| Rule 13 | SPEC Protocol Work Separation | We do not maintain SPEC |
| Rule 18 | Knowledge Consumption Chain | Flat `decisions.md`, no L0/L1/L2 |
| Rule 21 | Document Write Boundary | No SSOT Write Map without matrices |
| Rule 23 | Stream Scope Lock | No parallel streams |

Rules 1–12, 14–17, 19–20, 22, 24–25 — **kept** (renumber only if explicit numbering would break; otherwise keep gaps for auditability).

**d) Session Code simplification** (affects Declaration, all protocol headers referencing Session Code):

| Old | New |
|---|---|
| `S{N}-P{NN}-E{NN}-C{NN}` | `S{N}-P{NN}-C{NN}` |
| `E{NN} is a globally unique entry number` | (delete) |

**e) Lifecycle diagram replacement** (Declaration "Lifecycle at a Glance" — replace with):

```
[once] this INSTALLATION-PLAN.md → SPEC-Velo ready
    ↓
02_Sprint-Builder → S{N}-SPRINT.md
    ↓
  ┌────────────────────────────────────────────┐
  │ 03_Phase-Builder (OPEN → WORK → CLOSE)     │
  │ WORK cycles include: standard and          │
  │ design-gen (Claude Design pipeline).       │
  │ Repeat per phase until all phases DONE.    │
  └────────────────────────────────────────────┘
    ↓
04_Sprint-Closer (code audit + SNAPSHOT + RETRO)
    ↓
05_Clean-Sync (FILE-TREE sync + paths consistency)
    ↓
next 02_Sprint-Builder
```

No 06/07 in the lifecycle.

**f) Anchor update** — at end of every active protocol file, replace `[XX] SPEC v3.2.0` with `[XX] SPEC v3.2-velo`.

### 5.2 Files to remove from active set (E, F, G)

After Step 4 snapshot is complete:

- Remove `docs/02_spec/06_Spec-Update.md` from active (kept only in `_original_v3.2.0/`)
- Remove `docs/02_spec/07_Brain-Next.md` from active
- Remove `docs/02_spec/Spec-Install.md` from active

Rationale: per Q9, these protocols are disabled permanently for Velo profile. Physical removal from the active directory prevents accidental load into a working chat.

### 5.3 Per-file modifications

#### 5.3.1 `01_Declaration.md` (H)

Apply §5.1a–f. Additionally remove these sections entirely:
- `## Roles and Boundaries` → simplify to a 4-line paragraph (keep Claude Chat vs Claude Code split, drop SPEC-specific duties)
- `### SPEC Update Banner` inside Entry Rule — delete
- `### Running SPEC Log (per session)` — delete
- `### SPEC Finding Standard` — delete
- `## Tier Registry` (if present in this file) — delete
- `### Versioning Rules` — delete
- `### Changelog Rule` — delete
- Any subsection mentioning only Stream/Entry/E{NN}/parallel — delete

Simplify "Protocol Map" table: remove rows for 06, 07, Spec-Install (they live only in `_original/`).

Keep intact: Self-ID, Roles, Prompt Discipline (Rules 1–12, 14–17, 19–20, 22, 24–25), Session Structure, Universal Close Flow, Recovery Patterns, Prompt Validation Checklist, Quick Reference (pruned), Drift Indicator, Anchor (updated).

#### 5.3.2 `02_Sprint-Builder.md` (I)

Apply §5.1a–f. Additional cuts:
- Step 3 (Balance Review) — delete entire step, renumber subsequent
- Step 5 (Stream Planning) — delete entire step, renumber
- Capacity Check language: "40–60 cycles per sprint" → "15–25 cycles per sprint (single-dev frontend scope)"
- Recurring carry-forward auto-promote — delete wherever it appears
- Output change: protocol produces **one** `S{N}-SPRINT.md` with inline phase list. `P{NN}-{name}.md` files are **optional**; if a phase has >5 cycles, break out into its own file, otherwise keep inline.
- Delete any "PENDING → DONE" SPEC trigger references

#### 5.3.3 `03_Phase-Builder.md` (J)

Apply §5.1a–f. Additional cuts:
- Step 2.5 (Design Review Consultation) — simplify: keep a 5-line "Design Review" checklist (scan loaded refs, confirm scope, note conflicts), remove the full consultation subprotocol
- Remove all Stream Planning / Entry references
- Remove E{NN} entry numbering examples (C40 on stream E1 etc.)
- CLOSE simplify: verify → commit → update `S{N}-SPRINT.md`. Remove Phase Verification Scout as separate step (fold into verify).

**Addition:** new subsection in WORK phase — see §5.4.1.

#### 5.3.4 `04_Sprint-Closer.md` (K)

Apply §5.1a–f. Additional cuts:
- Step 2 (ProbeKit full pipeline) — replace with lite profile, see §5.4.2
- Codebase Balance findings (Step 3) — delete
- Recurring carry-forward check (Step 3) — delete
- SPEC PENDING trigger (Step 13 area) — delete
- SNAPSHOT simplify: drop balance assessment section; keep cloc + git log + completed items + carry-forward

Keep: Code audit → CODE-AUDIT-S{N}.md, SNAPSHOT, RETRO, commit.

#### 5.3.5 `05_Clean-Sync.md` (L)

Apply §5.1a–f. Additional cuts:
- Step 2d (Information Map Boundary Check) — delete
- Step 3d (Backlog Health statistics recount) — delete
- Step 4a (Sprint Archive Decision Human gate) — simplify: archive when 3+ completed sprints exist, no gate
- Version consistency checks (tier 1/2/3 sync) — delete

Keep: FILE-TREE sync, paths consistency, stale pruning.

#### 5.3.6 `Resolution.md` (M)

Apply §5.1a (BOGAME removal) only. No structural cuts.

### 5.4 Per-file additions

#### 5.4.1 `03_Phase-Builder.md` — add design-gen cycle type

Insert new subsection in WORK phase, after the existing cycle execution guidance:

```markdown
## Cycle Types

Two cycle types exist in WORK phase:

### Standard cycle

Code change, refactor, test, doc. Follow Scout → Validate → Execute pattern per Rule 2. Risk tier per Rule 15.

### Design-gen cycle (Velo-specific)

Used for redesigning or creating a screen via Claude Design. Required precondition: Figma reference exists and is approved.

Steps:
1. **Ground:** open Figma reference, read its spec. Capture target screen name, route, role (user/master/admin), route file (`frontend/src/views/<role>/<File>.vue`), and relevant tokens from `Design_prototype/tokens.md`.
2. **Sponsor-spec cross-check:** verify the screen exists in the sponsor-approved functional scope. If missing or ambiguous → STOP, escalate.
3. **Compose Claude Design prompt** (6 slots): artifact type, product, stage, structure (screens/states), tone, audience. Brand lock required — explicitly forbid cream/beige/serif/italic/terracotta/amber; require Marmelad + blue-slate + glass + radii 15/200/5/100.
4. **Attach context** before first generation: codebase link, Figma link, tokens file, reference screenshot.
5. **Generate** in claude.ai/design. Single variant first.
6. **Iterate** with Edit / Comment / Tweaks until visual parity with Figma. Do not regenerate unless direction is fundamentally wrong.
7. **Handoff** via "Handoff to Claude Code" export. Supply path `frontend/src/views/<role>/<File>.vue` and instructions to use existing tokens + conventions.
8. **Claude Code** fetches the bundle, scaffolds the Vue component, wires up to existing store + API client + guards.
9. **Verify:** `npm run typecheck && npm run lint && npm run test`, then visual check in dev server, then deploy to staging server (Velo is wired to one), final visual check in production-like env.
10. **Commit** on branch `new_desing`.

Acceptance: visual parity with Figma, typecheck/lint/test pass, staging deploy renders correctly.

See `docs/01_refer/GUIDES/claude-design-pipeline.md` for the current execution playbook (updated each sprint from lessons learned).
```

#### 5.4.2 `04_Sprint-Closer.md` — ProbeKit lite profile

Replace the full-pipeline language in Step 2 with:

```markdown
## Step 2 — ProbeKit Lite Profile (Velo)

Run the following skills in order. Skip any that report "not applicable" for current sprint scope.

| Skill | Why included |
|---|---|
| `probekit-type-audit` | TypeScript / Vue 3 type safety; catches unsafe casts, missing types |
| `probekit-code-audit` | General code review — bugs, naming, quality |
| `probekit-a11y-audit` | Accessibility is a wellness-app concern; WCAG checks |
| `probekit-responsive-audit` | Mobile-first PWA — breakpoints, touch targets |
| `probekit-security-audit` | OWASP top 10, secret leaks |
| `probekit-design-audit` | Brand/token compliance against Design_prototype |

Optional (run by explicit Human request, not every sprint):
- `probekit-dependency-audit` — once per 3–4 sprints
- `probekit-i18n-audit` — when localization work is in scope
- `probekit-comprehension-debt` — when churn spikes

Do NOT run the full `probekit-test-suite` (13 stages) in the auto-close pass — it produces noise disproportionate to a 1–2 week frontend sprint. Human may invoke it on demand.

Findings are classified by severity (BREAK / GAP / NIT) and routed to `BACKLOG.md` (MEDIUM/LOW) or fixed inline (CRITICAL, see Step 6).
```

---

## 6. New Files in `docs/01_refer/` (N–T)

### 6.1 `ARCHITECTURE.md` (N)

```markdown
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

See `03_Phase-Builder.md` § Design-Gen Cycle Type for the canonical procedure. Operational notes and lessons learned: `GUIDES/claude-design-pipeline.md`.

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
```

### 6.2 `ENVIRONMENT.md` (O)

```markdown
# Velo — Environment

> Loaded in every working chat. Bridge between framework rules and project reality.
> Updated: 2026-04-23.

---

## System

| Item | Value |
|---|---|
| OS | Windows 11 |
| Shell (Claude Code) | bash |
| Project path | `D:\03_Projects\velo` |
| Prompt detail level | FULL |

Developer works on a single Windows laptop; Claude Code runs with bash as its shell. Prompts target bash syntax. PowerShell is not used.

---

## Tools

| Tool | Version | Notes |
|---|---|---|
| Node | 24.13.0 | Frontend runtime (Vite dev server, build) |
| npm | bundled with Node | Package manager |
| Vite | ^6.1 | Build tool |
| Vue | ^3.5 | Framework |
| TypeScript | ~5.7 | Strict mode |
| Pinia | ^2.3 | State |
| vue-router | ^4.5 | Routing |
| Vitest | ^3.0 | Test runner |
| ESLint | ^9.20 | Linter |
| Prettier | ^3.5 | Formatter |
| Docker | — | Compose v2 for local full-stack |
| cloc | — | Used in Sprint-Closer SNAPSHOT for LOC count |
| gh | 2.88.1 | GitHub CLI; auth: `abalyakno` (keyring) |
| Claude Design | claude.ai/design | UI generation surface (see ARCHITECTURE.md) |
| ProbeKit skills | probekit-* | Auto-run lite profile at sprint close |

Not required for frontend work: Python, pytest, Godot, PostgreSQL (runs in Docker), Stripe CLI.

---

## Quality Tools

| Tool | Command | Purpose |
|---|---|---|
| Linter | `cd frontend && npm run lint` | ESLint 9 |
| Formatter | `cd frontend && npm run format` | Prettier |
| Type checker | `cd frontend && npm run typecheck` | vue-tsc |
| Test runner | `cd frontend && npm run test` | Vitest |
| Pre-commit | (not configured) | Candidate for `BACKLOG.md` |

---

## Git Workflow

| Item | Value |
|---|---|
| Main branch | `main` |
| Active branch | `new_desing` (note: "desing" is the intentional branch name from S0; do not "correct") |
| Strategy | Work continues on `new_desing`; merge to `main` per milestone, no feature branches |
| Remote | GitHub (project repo; resolve with `gh repo view` when needed) |

### Commit convention

| Context | Format | Example |
|---|---|---|
| Cycle work | `cycle: C{NN} <short description>` | `cycle: C03 redesign UserDashboardView` |
| Cycle close | `cycle: C{NN} <short name> — DONE` | `cycle: C03 user-dashboard — DONE` |
| Phase close | `phase: P{NN} <name> — DONE` | `phase: P01 pilot — DONE` |
| Sprint close | `sprint: S{N} <name> — CLOSED` | `sprint: S1 pilot — CLOSED` |
| Doc update | `docs: <what changed>` | `docs: ARCHITECTURE.md — add coding standards` |
| Decision | `decision: <short title>` | `decision: choose vue 3.5 for Velo` |
| Refactor | `refactor: <short description>` | `refactor: extract topup error state` |
| Fix | `fix: <short description>` | `fix: topup webhook race condition` |
| Clean-Sync | `clean-sync: S{N} <description>` | `clean-sync: S1 FILE-TREE refresh` |
| Audit | `audit: CODE-AUDIT-S{N} <name>` | `audit: CODE-AUDIT-S1 pilot` |

### Rules

- Never force-push without explicit Human authorization (e.g., git history security remediation).
- Never commit secrets, API keys, server credentials. `SERVER-ACCESS.md` is gitignored.
- Commit messages must be meaningful.
- Execute prompts end with `git add ... && git commit ... && git push` unless the prompt explicitly states otherwise.

---

## Backlogs

Single backlog: `BACKLOG.md` at `docs/01_refer/BACKLOG.md`. All code issues, tech debt, features, tooling gaps go here. No separate SPEC backlog (we do not maintain SPEC in Velo profile).

---

## Known Limitations

| Limitation | Workaround |
|---|---|
| Cannot push directly to production server | Server deploys happen via `new_desing` push → staging auto-pulls. Production promotion requires manual Human action (see `SERVER-ACCESS.md` after it is populated). |
| Cannot edit backend | `backend/` is out of scope; friend owns it. Consume via `frontend/src/api/types.ts`. |
| Cannot browser-test frontend from Claude Code | Visual verification happens on staging after push (Sprint 1 trigger). Alternative: ask Human to screenshot local dev server. |
| Cannot guess missing API endpoints | If `frontend/src/api/types.ts` lacks the needed type, STOP and ask Human to coordinate with backend owner. |

---

## Information Map

Files under `docs/` and what they own:

| File | Contains | Does NOT Contain |
|---|---|---|
| `01_refer/ARCHITECTURE.md` | Project overview, components summary, coding standards, tools/pipelines, scope boundaries, links to root VELO-*.md | Implementation code, sprint plans, cycle detail |
| `01_refer/ENVIRONMENT.md` | System, tools, git workflow, commit convention, backlogs location, known limitations, information map | Architecture, decisions, sprint state |
| `01_refer/FILE-TREE.md` | `frontend/src/` + `docs/` tree with per-file notes | `backend/`, root-level files (referenced elsewhere) |
| `01_refer/BACKLOG.md` | Code issues, tech debt, features, tooling gaps | Protocol improvements (none kept) |
| `01_refer/decisions.md` | Flat table of key decisions (what/why/when) | Research artifacts, debates |
| `01_refer/SERVER-ACCESS.md` | Staging/prod endpoints, safe-command list, deploy procedure | Credentials as plaintext (use env refs) — gitignored regardless |
| `01_refer/GUIDES/claude-design-pipeline.md` | Operational playbook for design-gen cycles | Framework rules (→ `03_Phase-Builder.md`) |
| `03_sprint/S{N}-SPRINT.md` | Sprint goal, phases inline, protocol log, current state, next action | Cycle-level detail (in phase sections or separate `C{NN}.md` if large) |

---

## Shell Notes (bash)

- Forward slashes in paths everywhere.
- For Windows drive roots, `/d/03_Projects/velo/` style or `D:/03_Projects/velo/` both work in Git Bash.
- `npm` commands run from `frontend/` directory. Use `(cd frontend && npm run ...)` pattern to avoid leaving working directory.
- `docker compose` (v2 syntax, no hyphen).

---

## Tool Notes

### Vite dev server
- Config: `frontend/vite.config.ts`. PWA plugin enabled.
- Default port 5173 unless overridden.
- For API proxy behavior: check current `vite.config.ts` state before assuming.

### vue-tsc
- `npm run build` runs `vue-tsc --noEmit && vite build`. Build fails on any type error — do not bypass.

### Claude Design
- Access: claude.ai/design (Pro/Max/Team required).
- Brand lock language is mandatory (see `ARCHITECTURE.md` §Tools).
- One cycle = one screen. Do not batch multiple screens into one Claude Design project.

### ProbeKit
- All skills invoked by name `/probekit-<skill>`. Lite profile runs automatically in Sprint-Closer Step 2.
- If a skill reports "not applicable" for current scope, record and skip.

---

## Anchor

```
[ENVIRONMENT.md | SPEC v3.2-velo]
Project environment — system, tools, git workflow, information map
Location: docs/01_refer/ENVIRONMENT.md
Referenced from: S{N}-SPRINT.md + loaded in every working chat
Update when: tools change, new pitfalls discovered, sprint close
```
```

### 6.3 `FILE-TREE.md` (P)

```markdown
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
│       └── (9 files)
└── 03_sprint/
    └── .gitkeep
```
```

### 6.4 `BACKLOG.md` (Q)

```markdown
# Velo — Project Backlog

> Code issues, tech debt, features, tooling gaps.
> Consumed by: `02_Sprint-Builder.md` during sprint planning.
> Updated: 2026-04-23 (install — empty at start).

| # | Item | Source | Priority | Status | Notes |
|---|---|---|---|---|---|

_No items yet. Items are added during sprint work and by Sprint-Closer from code audit findings._
```

### 6.5 `decisions.md` (R)

```markdown
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

Status values: ACTIVE, SUPERSEDED (by #NNN), DEPRECATED.
```

### 6.6 `SERVER-ACCESS.md` (S)

```markdown
# Velo — Server Access

> GITIGNORED. Do not commit contents.
> Fill during Sprint 1 when we first deploy a screen and validate on the server.

## Staging

| Item | Value |
|---|---|
| Host | (fill: IP or hostname) |
| Deploy trigger | Push to `new_desing` (fill: mechanism — webhook / auto-pull / manual) |
| Preview URL | (fill) |
| SSH | (fill: user@host — actual key/password stored in local env, not here) |
| Safe commands | See list below |

## Safe commands (read-only / low-risk)

When Claude Code needs server state, Human authorizes one of these verbatim. Nothing else.

- `docker compose ps`
- `docker compose logs --tail=200 <service>`
- `git -C <repo> log --oneline -5`
- `curl -sS <staging-url>/health`

## Deploy procedure

(fill in Sprint 1 as we work out the actual flow)

## Production

(fill only after staging is stable; do not populate on install)
```

### 6.7 `GUIDES/claude-design-pipeline.md` (T)

```markdown
# Claude Design Pipeline — Velo Playbook

> Operational notes for design-gen cycles. Updated from Sprint 1 lessons onward.
> Governed by `03_Phase-Builder.md` § Design-Gen Cycle Type.
> Updated: 2026-04-23 (install — initial skeleton).

## Pre-flight per screen

- [ ] Figma reference open and approved
- [ ] Target route/view file identified in `FILE-TREE.md`
- [ ] Sponsor scope confirms screen is in scope
- [ ] Existing tokens in `Design_prototype/tokens.md` reviewed
- [ ] claude.ai/design project named `VELO / <screen> / <YYYY-MM-DD>`

## Claude Design prompt template (6 slots)

```
Artifact: high-fidelity clickable prototype of a single mobile screen.
Product: Velo — mobile Vue 3 PWA for wellness/meditation practices;
         three roles (user, master, admin).
Stage: MVP, continuing on branch new_desing.
Structure: screen "<name>", states: <default | loading | empty | error | success>;
           route: <path>; role: <role>.
Tone: soft glassmorphism, spacious, wellness-first, not marketing-fluffy.
Audience: mobile-first end users (Russian-first locale).

BRAND LOCK (mandatory):
NEVER use: cream/beige backgrounds, serif display fonts (Georgia, Fraunces,
Playfair), italic word accents, terracotta/amber accent colors.
USE: Marmelad font only, blue-slate base #4c6589, teal/peach/pink accents
per Design_prototype/tokens.md, glassmorphism with backdrop-blur(2px),
radii 15/200/5/100 strictly, shadow 0 0 20.9px 7px white on buttons.

References attached: codebase link, Figma link, tokens file,
screenshot of Figma target.
```

## Attachments to include before first generation

1. Codebase (GitHub repo or `frontend/` folder)
2. Figma file link
3. `Design_prototype/tokens.md` as a separate file (if tool doesn't parse md subfolders)
4. Screenshot of the Figma target screen

## Iteration rules

- First generation: single variant only (token economy).
- Revise via Edit / Comment / Tweaks. Regenerate only if direction is fundamentally wrong.
- If output drifts to default Opus 4.7 aesthetic (cream, serif, italic) — stop, re-paste brand lock, regenerate.

## Handoff

- Use "Handoff to Claude Code" export.
- In the extra instructions field, specify the target file path and reuse-existing-tokens rule.

## Post-handoff verification

- [ ] `npm run typecheck` passes
- [ ] `npm run lint` passes
- [ ] `npm run test` passes
- [ ] Visual parity with Figma in local dev server
- [ ] Push to `new_desing` → staging deploys → visual verification on staging URL

## Lessons (populated from Sprint 1 onward)

_None yet. First entries will land during Sprint 1 pilot._
```

---

## 7. Directory Structure After Install

```
docs/
├── 01_refer/
│   ├── ARCHITECTURE.md               (new)
│   ├── ENVIRONMENT.md                (new)
│   ├── FILE-TREE.md                  (new)
│   ├── BACKLOG.md                    (new)
│   ├── decisions.md                  (new)
│   ├── SERVER-ACCESS.md              (new, gitignored)
│   └── GUIDES/
│       └── claude-design-pipeline.md (new)
├── 02_spec/
│   ├── 01_Declaration.md             (modified)
│   ├── 02_Sprint-Builder.md          (modified)
│   ├── 03_Phase-Builder.md           (modified + new section)
│   ├── 04_Sprint-Closer.md           (modified + new section)
│   ├── 05_Clean-Sync.md              (modified)
│   ├── Resolution.md                 (modified — BOGAME cleanup only)
│   └── _original_v3.2.0/             (new; 9 files copied unchanged + README.md)
├── 03_sprint/
│   └── .gitkeep                      (new)
└── INSTALLATION-PLAN.md              (this file — deleted after validation)
```

Removed: `ENVIRONMENT.md` (root of docs), `01-audit-current-state.md`, `02-sprint-plan-preliminary.md`, active copies of `06_Spec-Update.md`, `07_Brain-Next.md`, `Spec-Install.md`.

---

## 8. `.gitignore` Update (V)

Append to existing `.gitignore`:

```
# Velo — server access details kept out of git
docs/01_refer/SERVER-ACCESS.md
docs/01_refer/SERVER-ACCESS.*.md
```

Rationale: the file will hold staging/prod deploy details starting Sprint 1. Extra pattern catches any future variant like `.local.md`.

Verify the rule works by staging `SERVER-ACCESS.md` after creation and confirming `git status` does NOT list it.

---

## 9. Commit & Push (W)

Single commit covering all operations A–V.

```
docs: install SPEC v3.2-velo framework

- Adapted SPEC v3.2.0 to frontend-only single-dev profile
- Disabled protocols 06/07/Spec-Install (kept under _original_v3.2.0/)
- Removed Entry/Stream/Balance/KB-hierarchy/SPEC-versioning concepts
- Added design-gen cycle type (Claude Design) in 03_Phase-Builder
- Added ProbeKit lite profile (6 skills) in 04_Sprint-Closer
- Created 01_refer/ with ARCHITECTURE, ENVIRONMENT, FILE-TREE, BACKLOG, decisions,
  SERVER-ACCESS (gitignored), GUIDES/claude-design-pipeline
- Removed obsolete BOGame ENVIRONMENT and preliminary drafts
- Snapshotted all 9 original SPEC v3.2.0 files under 02_spec/_original_v3.2.0/
```

Then `git push origin new_desing`.

---

## 10. Post-Install Handoff

After install lands, close this chat. **Next chat:**

```
Session Code: S1-Sprint-Builder
Load:
1. Framework: docs/02_spec/01_Declaration.md + docs/02_spec/02_Sprint-Builder.md
2. Project: docs/01_refer/ARCHITECTURE.md + docs/01_refer/ENVIRONMENT.md
            + docs/01_refer/BACKLOG.md + docs/01_refer/decisions.md
3. Design sources: Design_prototype/CLAUDE.md + Design_prototype/tokens.md
                   + Design_prototype/screens.md + Design_prototype/components.md
Run: 02_Sprint-Builder for Sprint 1 (pilot — walk all 21 screens through
     Claude Design pipeline + Figma cross-check + sponsor-scope cross-check;
     output: sprint deliverables, acceptance metrics, plan for Sprint 2+).
```

---

## 11. Validation Procedure

Run this template against the installed state as a single pass after the execute prompt completes. Instruction text is verbatim (do not paraphrase).

You are validating your own output. You are biased toward confirming it is correct. Compensate: assume problems exist and hunt for them. "VALID" requires more proof than finding issues does.

ARTIFACT TYPES (apply rules accordingly):
- TEXT (prompt, doc, markdown, config, short code): full read + str_replace fixes + inline or file delivery. Default case.
- CODE (source files, scripts): same as TEXT, plus FEASIBILITY is critical — if behavior can only be confirmed by execution and execution is unavailable, mark [UNVERIFIED].
- MULTI-FILE (skill, repo, bundle): treat the set as one artifact. Walk every file. CASCADE and NEGATIVE principles apply across files, not only within one.
- BINARY (pptx, xlsx, pdf, images): "read in full" means inspecting via the appropriate tool, not raw dump. str_replace does not apply — fixes go through the native builder. If neither is available, mark [UNVERIFIED] and state what is needed.

BEFORE VALIDATING:
Read the artifact in full from source (file or message). No working from memory, no partial read, no summary. Build an explicit map of every claim, reference, version, count, and constraint it contains. Validate against the map. For artifacts >100 lines or with >10 cross-references, or MULTI-FILE, the map is emitted as step 0 of OUTPUT. Otherwise the map is internal.

CHAT SALVAGE (run before Problems):
Scan the current conversation for content that was discussed, agreed, or produced but did not make it into the artifact: decisions, constraints, examples, edge cases, renamings, rejected-then-revived ideas, user corrections. For each, decide: (a) belongs in the artifact and is missing → add as a GAP in Problems; (b) intentionally excluded → ignore; (c) unclear → list under UNVERIFIED with a one-line question. Do not invent — only salvage what is actually in the chat.

COMPETENCE BOUNDARY:
Before reporting any finding, check: does validating this claim require domain knowledge you do not actually have (legal, medical, deep technical, company-internal)? If yes — do not pretend to validate. Mark the claim [UNVERIFIED: requires <domain>] and state what would be needed. Silent confabulation in unfamiliar domains is the worst failure mode for this prompt.

INTENT CHECK:
Before flagging something as BREAK or GAP for violating a standard, look for markers of deliberate deviation: comments like "intentional", explicit rationale in the artifact, prior decision in chat to do it this way. If such a marker exists — do not flag, or flag as UNVERIFIED with a one-line question. Non-standard ≠ wrong.

PRINCIPLES:
COMPLETENESS — everything declared is present, nothing promised is missing.
CONSISTENCY — zero contradictions within the material and against context.
LOGIC — check for internal logical defects, not only surface contradictions. Classes to hunt explicitly:
  (a) Rule conflict — rule A requires X, rule B requires not-X.
  (b) Dangling reference — rule points to a section, field, or step that does not exist or is named differently.
  (c) Undefined combination — rule defines behavior for case A and case B separately, but A+B (or neither) is silent.
  (d) Unenforceable rule — rule demands an action for which no mechanism or definition exists elsewhere in the artifact.
  (e) Circular dependency — A requires B, B requires A, with no entry point.
  (f) Dead branch — condition can never be true given other constraints, or branch is unreachable.
  For each defect found: report as BREAK if it blocks correct use, GAP if it leaves behavior undefined.
CASCADE — every change traced to all downstream references (across files for MULTI-FILE).
NEGATIVE — everything removed is gone everywhere, no ghost references.
ENVIRONMENT — material respects the rules and boundaries of the system.
FEASIBILITY — for each claim of "works", "uses", "calls" — can the target actually do what's described? If you can't verify — mark [UNVERIFIED].
NAMING — read every title, label, and term as a new reader. Does the name match the actual content?
SESSION CONSISTENCY — verify earlier decisions in this conversation are faithfully represented, not drifted. If no session context, mark [N/A: no session context] and skip.
SCOPE — only issues listed in Problems get fixed. No unrequested improvements, no stylistic rewrites.
SPOT-CHECK: numbers, versions, dates, counts, cross-references — verify each explicitly.

DECISION RULE: when fixing, choose architectural cleanliness over minimal patch. Resolve legacy, don't inherit it. INVARIANT: semantics and author intent are preserved. Cleanup touches form, not meaning. If a fix changes meaning, flag it explicitly with rationale.

SEVERITY:
BREAK — artifact is wrong, broken, or breaks something downstream. Must fix.
GAP — missing piece or undefined behavior that will cause problems under foreseeable use. Must fix.
NIT — minor (style, wording, formatting). Fix only if cheap; otherwise note and skip.
UNVERIFIED — cannot be checked without external access or execution. Report, do not silently pass.
Do not downgrade severity to make results look cleaner. Breaks downstream = BREAK.

FIX EFFICIENCY: apply fixes via str_replace (точечные правки), not full file rewrite. Rewrite only if >50% of document changes or structure shifts. Never burn tokens rewriting a file for ≤5 edits. For BINARY — fixes via native builder only.

FIX ORDER: BREAK before GAP before NIT. Within the same severity: fix root causes before symptoms — if fixing problem A would make problem B trivial or obsolete, fix A first. If two BREAKs conflict in their fixes, resolve the conflict explicitly before applying either.

FIX VALIDATION: before applying each fix, verify: (1) it actually resolves the reported problem, not a neighbor; (2) it does not introduce a new defect from the LOGIC checklist; (3) it does not violate SCOPE (no scope creep dressed as fix); (4) it respects the DECISION RULE invariant (semantics preserved unless explicitly flagged). If a fix fails any check — revise the fix, do not apply and hope.

OUTPUT:
0. MAP (only if artifact >100 lines, >10 cross-references, or MULTI-FILE). Short structured list: claim → location.
1. PROBLEMS — numbered list: [BREAK|GAP|NIT|UNVERIFIED] + location + problem + fix. If none: "VALID — no issues found".
2. APPLY — execute all fixes in FIX ORDER, each passing FIX VALIDATION.
3. RE-SCAN — after all fixes applied, re-check the artifact against the MAP and the LOGIC checklist. If new problems introduced → loop back to step 1 with a new Problems sub-list labeled "post-fix". Max 3 loops; if not stable by then, report remaining as UNVERIFIED and stop.
4. CHANGELOG (only if >3 fixes applied across all loops) — one-line-per-fix summary of what changed.
5. DELIVERY — always, at the end of the cycle:
   - CHANGED + file → call present_files with the final path.
   - CHANGED + inline → re-output the final corrected artifact in full.
   - VALID + file → restate path, confirm unchanged, call present_files.
   - VALID + inline → confirm unchanged, restate title/first line as anchor, do not re-output in full.

### Validation scope for this install

Apply the template above as MULTI-FILE over:
- All files under `docs/01_refer/` created by this install
- All modified files under `docs/02_spec/` (01, 02, 03, 04, 05, Resolution)
- `docs/02_spec/_original_v3.2.0/` inventory (presence check only, contents unmodified)
- `.gitignore` (delta check)
- Commit message (§9)

Then `git status` must be clean, `git log -1` must show the install commit, push must be complete.

---

## 12. Cleanup

After validation returns VALID (or a maximum of 3 fix loops have converged):

1. Delete `docs/INSTALLATION-PLAN.md` (this file)
2. Commit: `docs: remove INSTALLATION-PLAN.md (install validated)`
3. Push

If validation does NOT converge within 3 loops, leave this file in place, report remaining UNVERIFIED items, STOP. Human decides next action.
