# VELO `docs/` — Master Index

Last updated: 2026-05-17
Sprint reference: pre-Sprint 0 (foundation established + v1.1 validation pass complete)
Methodology version: `[VELO-METHODOLOGY.md | v1.1 | 2026-05-17]`
Roadmap version: `[VELO-ROADMAP.md | v1.1 | 2026-05-17]`

> **Single entry point.** Read this first in every new chat or session.
> This file is updated at sprint boundaries per VELO-METHODOLOGY §12.2.
> Local INDEX.md files (one per subfolder) update immediately after
> every change in their scope.

---

## What is this folder

`D:\02_Projects\velo\docs\` is the **design-and-handoff workspace** for
VELO. It is kept **outside** the frontend repository. The frontend repo
at `D:\02_Projects\velo\frontend\` is the lean code-only artifact that
ships to production.

This folder produces the handoff package (`01_deliverable/`) that the
frontend consumes.

---

## Folder Map

| Folder | Purpose | Local INDEX | Status |
|---|---|---|---|
| `01_deliverable/` | Handoff package the developer receives | `screens/INDEX.md` + folder-level `README.md` | empty scaffold, populated through Sprints 1–10 |
| `02_design-system/` | Master source of tokens, assets, styleguide | `INDEX.md` + `assets/ASSETS-INDEX.md` | empty scaffold, populated in Sprint 1–2 |
| `03_mockups/` | Operator's visual workspace (not shipped) | `INDEX.md` | empty scaffold, populated from Sprint 2 onward |
| `04_methodology/` | `VELO-METHODOLOGY.md` (single source of truth for process) | — | active (v1.0) |
| `05_roadmap/` | `ROADMAP.md` + `sprint-NN.md` per sprint | — | active (v1.0 + 12 sprint files) |
| `06_project-inputs/` | External read-only references (ARCHITECTURE.md, api-openapi.json, CC-REPORT.txt) | `README.md` | active |

---

## Bootstrap reading order (for a fresh chat)

1. This file (`INDEX.md`) — folder map and current status.
2. `04_methodology/VELO-METHODOLOGY.md` — how we work (full document).
3. `05_roadmap/ROADMAP.md` — when each piece of work happens.
4. `05_roadmap/sprint-NN.md` (current sprint) — what's in flight right now.
5. `02_design-system/INDEX.md` — current DS state.
6. `01_deliverable/screens/INDEX.md` — current spec catalog.
7. `06_project-inputs/ARCHITECTURE.md` — frontend code rules (referenced from specs).
8. `06_project-inputs/api-openapi.json` — backend contract (referenced from specs).

---

## Status Summary

| Dimension | Count | Target | % |
|---|---|---|---|
| Tokens (Layer 2 semantic, §6.3 required) | 0 | ~30 | 0% |
| Components in styleguide | 0 | ~30 (Tier 1+2) | 0% |
| Mockups approved (§10.4 MOCKUP GATE) | 0 | ~120 | 0% |
| Specs active (§10.5 SPEC GATE) | 0 | ~120 | 0% |
| Sprints planned | 12 (00–11) | 12 | 100% |
| Sprints completed | 0 | 11 (00–10) | 0% |

---

## Where to find what

| You need… | Open… |
|---|---|
| The methodology (how we work) | `04_methodology/VELO-METHODOLOGY.md` |
| The roadmap (when things happen) | `05_roadmap/ROADMAP.md` |
| The current sprint's checklist | `05_roadmap/sprint-NN.md` (whichever is in progress) |
| The design tokens master | `02_design-system/tokens/` |
| The styleguide (visual catalog) | `02_design-system/styleguide/velo-design-system.html` |
| The mockups | `03_mockups/{user,master,admin}/` |
| The screen specs | `01_deliverable/screens/SCR-NNN-*.md` |
| Frontend code rules | `06_project-inputs/ARCHITECTURE.md` |
| Backend contract | `06_project-inputs/api-openapi.json` |
| Frontend F0 reconnaissance (historical) | `06_project-inputs/CC-REPORT.txt` |
| Superseded universal methodologies (DS, LIVEMOCKUP) | `04_methodology/_archive/` |

---

## Three critical boundaries (from VELO-METHODOLOGY §3.2)

- **B1** — `01_deliverable/` is the **only** folder the developer/CC sees.
  Folders 02, 03, 04, 05 are internal.
- **B2** — Tokens have **one** master in `02_design-system/tokens/`.
  Copies in `01_deliverable/styles/` are regenerated; never edit copies.
- **B3** — Mockups **never** contain spec content (API contracts, error
  handling, business invariants). Those live in screen specs only.

---

## Open TODOs (high-level)

- [ ] **Sprint 0 execution** — 8 tasks per `05_roadmap/sprint-00.md`:
      - T0.0 (CRITICAL) — fix `types.ts:65` build blocker (one line)
      - T0.3 — router/shells/HomeView token cleanup
      - T0.7 — wire `gen:api` + (optional) pre-commit hook
      - T0.8 — `global.css` token audit
      - Plus closure & sanity check
- [ ] **Sprint 1 execution** — Figma Phase 1 extraction + Phase 2 token
      synthesis. The DSYS-era `variables.css` (now deleted from
      `docs/_archive/`) violated VELO-METHODOLOGY §11.1 (AP-DS-1..5) and
      was missing most §6.3 required groups — Sprint 1 must build
      from scratch via Figma extraction per §6.5.
- [ ] **Dark theme** — deferred per VELO-METHODOLOGY §2.5 I7. Architecture
      ready (two-layer tokens support a second mode block on Layer 2).

---

## Recent Changes

| Date | Summary |
|---|---|
| 2026-05-17 | **v1.0 foundation established.** Adopted VELO-METHODOLOGY.md v1.0 and ROADMAP.md v1.0 as single sources of truth. Restructured `docs/` to canonical layout per §3. Archived universal methodologies (`DS-METHODOLOGY.md`, `LIVEMOCKUP-METHODOLOGY.md`) to `04_methodology/_archive/`. Moved `ARCHITECTURE.md` and `api-openapi.json` to `06_project-inputs/`. Created `sprint-00.md` through `sprint-11.md` checklists. DSYS-era materials (`stage-{0,1,2}-*/`, `extract/`, old `PROGRESS.md`) were temporarily archived in `docs/_archive/` and then deleted from the workspace by the operator — they remain in git history if needed. |
| 2026-05-17 | **Validation pass started.** `CC-REPORT.txt` (pre-v1.0 reconnaissance) moved to `06_project-inputs/` as an input. Recon prompt #2 prepared at `06_project-inputs/CC-RECON-PROMPT-2.md` to gather a fresh delta report for validating v1.0 methodology against current code and API contract. |
| 2026-05-17 | **Validation pass complete; methodology and roadmap bumped to v1.1.** Findings recorded in `06_project-inputs/VALIDATION-REPORT-2026-05-17.md` and `06_project-inputs/CC-REPORT-2.txt`. Methodology amendments: §2.5 I2/I4/I5/I6 expanded; new I8 (status enums are code-only contracts); §3 ARCHITECTURE.md path corrected; §6.6 Tier 2 enum references aligned with code; §8.4 Section Guidelines (5/7/9/11) extended; §8.7 Waitlist FSM corrected to use `notified` (not `offered`). Roadmap amendments: Sprint 0 grew T0.0 (build fix), T0.7 (gen:api), T0.8 (global.css audit); Sprint 3 user-practice-detail adds create_report; Sprint 4 adds user-reports-list; Sprint 5 master-analytics flagged client-side aggregation; Sprint 7 admin-withdrawal-review + admin-user-detail flagged as backend gaps; Risk Register expanded with R-11/R-12/R-13. Backend requests filed in `06_project-inputs/BACKEND-REQUESTS-2026-05-17.md`. |

---

## Anchor

```
[VELO docs/INDEX.md | v1.0 | 2026-05-17]
Master index of the VELO design-and-handoff workspace.
Update frequency: end of each sprint, per VELO-METHODOLOGY §12.2.
```
