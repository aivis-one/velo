# Sprint 0 — Foundation Cleanup

```
Dates:    TBD → TBD (planned 1–2 days)
Status:   planned
Owner:    Operator + Claude Code (frontend) + Cowork (docs)
Goal ref: ROADMAP.md §3
Phase:    — (pre-pipeline foundation)
```

---

## Goal

Clean up the F0 state of `frontend/` and finalize the `docs/` folder
structure so subsequent sprints have a sane starting point.

Reality check (recorded 2026-05-17 during methodology adoption): the
folder restructure described in T0.1/T0.2/T0.4 below has **already been
performed** as part of the v1.0 methodology adoption. What remains in
Sprint 0 is verification + frontend cleanup (T0.3) + INDEX initialization
sweep.

---

## Scope

Nine tasks. T0.1, T0.2, T0.4 are verification (already executed during
v1.0 adoption). T0.0 is a **critical one-line build fix** discovered
during the v1.1 validation pass. T0.3, T0.7, T0.8 are the real
frontend cleanup. T0.5 is closure.

| # | Task | Owner | Real status as of 2026-05-17 |
|---|---|---|---|
| **T0.0** | **Fix build blocker: `PayoutDetails` → `PayoutDetailsResponse`** | **Claude Code** | ⬜ **pending — BLOCKER** |
| T0.1 | Create `docs/` folder structure per methodology §3 | Operator/Cowork | ✅ done during v1.0 adoption |
| T0.2 | Place methodology + roadmap + ARCHITECTURE + API into new structure | Operator | ✅ done |
| T0.3 | Clean up `frontend/` F0 state (shells, router, HomeView tokens) | Claude Code | ⬜ pending |
| T0.4 | Initialize INDEX.md files | Cowork | ✅ done (top-level + 4 local stubs) |
| T0.7 | Wire up `gen:api` automation + (optional) pre-commit hook | Claude Code | ⬜ pending |
| T0.8 | Audit `frontend/src/styles/global.css` token names | Claude Code | ⬜ pending |
| T0.5 | Sprint 0 closure & sanity check | Operator | ⬜ pending (last) |

---

## Task checklist

### T0.0 — Fix build blocker: `PayoutDetails` → `PayoutDetailsResponse` 🔴 CRITICAL

Ref: `06_project-inputs/VALIDATION-REPORT-2026-05-17.md` Section A1
(source: `06_project-inputs/CC-REPORT-2.txt` Q1.5).

**Symptom:** `npm run typecheck` (`vue-tsc --noEmit`) fails with
`src/api/types.ts(65,3): error TS2305: Module '"./generated"' has no
exported member 'PayoutDetails'`. Backend renamed schema to
`PayoutDetailsResponse`; `generated.ts` was regenerated, `types.ts`
re-export was not updated. **Build is broken** on the current branch.

Owner: Claude Code (or operator manually — it's one line).

- [ ] Open `frontend/src/api/types.ts`
- [ ] On line 65 (or nearby — find the re-export), change `PayoutDetails,` to `PayoutDetailsResponse,`
- [ ] Verify there are no other references to the old `PayoutDetails` name (`grep -n PayoutDetails frontend/src/`)
- [ ] Run `npm run typecheck` from `frontend/` — must pass on this error (router-related errors may still appear; those are T0.3)
- [ ] If clean: run `npm run build` — confirm any remaining failures are router/shell related (expected, handled in T0.3)
- [ ] Commit: `fix(api): rename PayoutDetails → PayoutDetailsResponse (matches backend OpenAPI)`

Effort: < 5 minutes.

### T0.1 — Folder structure (verification)

Ref: VELO-METHODOLOGY.md §3 (Canonical Layout).

- [x] `docs/01_deliverable/{styles,assets/{icons,fonts},screens}/` exists
- [x] `docs/02_design-system/{tokens,assets/{icons,screenshots},styleguide}/` exists
- [x] `docs/03_mockups/{user,master,admin}/` exists
- [x] `docs/04_methodology/` contains only `VELO-METHODOLOGY.md` (+ `_archive/`)
- [x] `docs/05_roadmap/` contains `ROADMAP.md` + sprint files
- [x] `docs/06_project-inputs/` exists
- [x] `docs/04_methodology/_archive/` exists with its README.md (root-level `docs/_archive/` was deleted by the operator after the v1.0 adoption — DSYS-era materials remain only in git history)

### T0.2 — Place key documents (verification)

- [x] `04_methodology/VELO-METHODOLOGY.md` in place (v1.0)
- [x] `05_roadmap/ROADMAP.md` in place (v1.0)
- [x] `06_project-inputs/ARCHITECTURE.md` in place (moved from `04_methodology/`)
- [x] `06_project-inputs/api-openapi.json` in place (moved + renamed from `04_methodology/API-JSON.txt`)
- [x] `06_project-inputs/README.md` explains the read-only nature of inputs

### T0.3 — Frontend F0 cleanup (router + shells + HomeView)

Ref: ROADMAP.md §3.1; `06_project-inputs/CC-REPORT-2.txt` Q1.3, Q5.1, Q5.2.

**Reality (from CC-REPORT-2.txt Q5.1):** `frontend/src/router/index.ts`
has **3 statement-level imports** referencing missing shells:

- `import UserShell from '@/views/shells/UserShell.vue'`
- `import MasterShell from '@/views/shells/MasterShell.vue'`
- `import AdminShell from '@/views/shells/AdminShell.vue'`

Plus **21 lazy imports** referencing missing views under
`@/views/{user,master,admin}/*.vue`. Statement-level imports fail
synchronously at build time; lazy imports fail at runtime on first
navigation. Build is currently blocked by T0.0 first; after that fix,
this T0.3 work is the next blocker.

`HomeView.vue` (the **only** existing view) references undefined
tokens: `--font-body`, `--text-2xl`, `--text-xs`, `--space-2`
(non-velo prefix) plus `--velo-text-primary`, `--velo-text-muted`
(velo prefix but `variables.css` doesn't exist yet).

Owner: Claude Code, instructed by Operator.

- [ ] Run `npm run build` (after T0.0 fix) and record the error output
- [ ] Choose strategy for shells:
      - [ ] **Option A — stub shells now** (recommended): create
            `src/views/shells/{User,Master,Admin}Shell.vue` each with
            `<template><router-view /></template>` and `<script setup
            lang="ts">` blocks. Minimum viable so `vue-tsc` passes.
      - [ ] Option B — comment out shell imports + the corresponding
            route children in `router/index.ts` (less recommended;
            requires later un-commenting per role-block sprint)
- [ ] Choose strategy for 21 lazy view imports:
      - [ ] Option A — leave as-is (lazy imports fail only at runtime;
            `vue-tsc` is happy with lazy `() => import(...)` even if
            target missing — verify)
      - [ ] Option B — comment them out until views materialize per
            role-block sprint (Sprint 3/5/7)
- [ ] HomeView.vue token fix:
      - [ ] Option A — replace non-velo tokens (`--font-body`,
            `--text-2xl`, `--text-xs`, `--space-2`) with literal CSS
            values pending Sprint 1 tokens (minimal change)
      - [ ] Option B — declare HomeView as Sprint 2 P0 candidate (gets
            rewritten with proper VELO tokens then; in the interim it
            renders with browser defaults — acceptable for a placeholder)
- [ ] Verify both `npm run typecheck` and `npm run build` succeed
- [ ] Decide on i18n install timing:
      - [ ] Option A — install `vue-i18n` now (aligns with ARCHITECTURE
            §1 "all UI strings via t('key') from day 1")
      - [ ] Option B — defer to Sprint 2 T2.6 (acceptable per ROADMAP;
            keeps Sprint 0 minimal)
- [ ] `utils/format.ts` hardcoded Russian strings (8 of them — see
      CC-REPORT-2 Q5.4):
      - [ ] Option A — extract to i18n keys now (only if vue-i18n
            installed in this sprint)
      - [ ] Option B — defer to Sprint 2 T2.6 (recommended — coupled
            with i18n install)
- [ ] Commit the F0 cleanup as a single PR/commit with clear message

### T0.4 — INDEX.md initialization (verification)

Ref: VELO-METHODOLOGY.md §12.

- [x] `docs/INDEX.md` per §12.3 template
- [x] `docs/01_deliverable/screens/INDEX.md` per §12.5 template (empty catalog)
- [x] `docs/02_design-system/INDEX.md` per §12.4 template
- [x] `docs/02_design-system/assets/ASSETS-INDEX.md` (empty catalog)
- [x] `docs/03_mockups/INDEX.md` per §12.6 template
- [x] `docs/01_deliverable/README.md` stub (will be finalized in Sprint 10)

### T0.5 — Sprint 0 closure sanity check

Owner: Operator.

- [ ] Walk `docs/` top to bottom: every expected file/folder present
- [ ] Open `docs/INDEX.md` — Bootstrap reading order reachable
- [ ] Open `04_methodology/VELO-METHODOLOGY.md` — opens, no broken
      internal anchors; version is v1.1
- [ ] Open `05_roadmap/ROADMAP.md` — opens, references to methodology
      sections valid; version is v1.1
- [ ] Open `06_project-inputs/api-openapi.json` — valid JSON
      (`python -c "import json; json.load(open('...'))"`)
- [ ] Open `06_project-inputs/ARCHITECTURE.md` — section structure
      intact, no garbled formatting
- [ ] T0.0 fix committed (build no longer fails on `PayoutDetails`)
- [ ] T0.3 frontend cleanup complete (`npm run build` passes)
- [ ] T0.7 `gen:api` script wired
- [ ] T0.8 `global.css` audit decisions documented in
      `02_design-system/INDEX.md → Open TODOs`
- [ ] Verbally approve Sprint 0 closure and move to Sprint 1

### T0.7 — Wire up `gen:api` automation

Ref: `06_project-inputs/VALIDATION-REPORT-2026-05-17.md` Section F3
(source: CC-REPORT-2.txt Q7.4). The `PayoutDetails` rename that broke
the build (T0.0) is exactly the class of error this task prevents.

Owner: Claude Code.

- [ ] Add to `frontend/package.json` scripts:
  ```json
  "gen:api": "cd ../backend && python -m scripts.generate_ts_types",
  "gen:api:check": "cd ../backend && python -m scripts.generate_ts_types --check"
  ```
  (the exact command may differ depending on how `velo gen-types` is
  packaged — operator confirms; the `--check` flag is the dry-run mode
  that exits non-zero if regen would change `generated.ts`)
- [ ] Smoke-test `npm run gen:api` end-to-end — `generated.ts` is
      written/identical
- [ ] Smoke-test `npm run gen:api:check` — exits 0 when no drift
- [ ] (Recommended) Install pre-commit hook (husky or
      `scripts/install-hooks.sh`):
      ```sh
      npm run typecheck && npm run gen:api:check
      ```
- [ ] Commit: `chore(frontend): add gen:api + gen:api:check scripts`

### T0.8 — Audit `frontend/src/styles/global.css` token names

Ref: `06_project-inputs/VALIDATION-REPORT-2026-05-17.md` Section F2
(source: CC-REPORT-2.txt Q5.3).

**Reality.** `global.css` uses 6 non-velo tokens and 3 mis-named
velo tokens:

Non-velo (no `--velo-*` prefix — must be either renamed to velo or
replaced with literal values):
- `--font-body`, `--text-base`, `--text-2xl`, `--text-xs`, `--space-2`, `--radius-full`

Velo-prefixed but mis-named (must be renamed to canonical Sprint 1
semantics):
- `--velo-bg-start` → `--velo-bg-screen`
- `--velo-primary` → `--velo-bg-button-primary` (or
  `--velo-text-primary` depending on context)
- `--velo-border` → `--velo-border-default`

Owner: Claude Code.

- [ ] Inventory all token references in `frontend/src/styles/global.css`
      with line numbers
- [ ] For each token:
      - [ ] If non-velo: decide rename to `--velo-*` (preferred) or
            replace with literal pending Sprint 1
      - [ ] If mis-named velo: rename to canonical form
- [ ] Document all decisions in
      `02_design-system/INDEX.md → Open TODOs`
      under heading "Sprint 0 global.css audit" so Sprint 1 Phase 2
      synthesis is aware of the names Cowork must produce
- [ ] Apply renames in `global.css`; verify `npm run build` still
      passes (will render with undefined tokens until Sprint 1 lands
      `variables.css` — acceptable, no visual deliverable yet)
- [ ] Commit: `chore(styles): audit global.css token names → --velo-* canonical`

---

## Sprint 0 Gate

Ref: ROADMAP.md §3.2. No formal gate document; operator verbally
approves and proceeds to Sprint 1.

Criteria:

- [ ] T0.0 — build-blocker fix (`PayoutDetails` rename) applied;
      `npm run typecheck` no longer fails on this error
- [ ] T0.3 — `npm run build` in `frontend/` succeeds (shells stubbed or
      router neutralized; undefined-token tolerance for global.css /
      HomeView pending Sprint 1)
- [ ] All folders per §3 of methodology exist
- [ ] Methodology v1.1, roadmap v1.1, ARCHITECTURE.md, api-openapi.json
      in place
- [ ] T0.7 — `npm run gen:api` + `npm run gen:api:check` scripts exist
      in `package.json`; smoke-tested
- [ ] T0.8 — global.css token audit decisions logged in
      `02_design-system/INDEX.md → Open TODOs`
- [ ] All INDEX.md stubs present

---

## Risks

| ID | Risk | Mitigation |
|---|---|---|
| 0.A | Frontend skeleton is even sparser than ROADMAP assumed (no router, no api, no shells). | Recorded above; T0.3 simplified to "stand up the skeleton" rather than "fix the existing skeleton." |
| 0.B | `npm install` for `vue-i18n` introduces dependency surprises. | If Option A (install now) fails, fall back to Option B (defer to Sprint 2). |
| 0.C | Operator wants `frontend/docs/ARCHITECTURE.md` to remain the canonical authoring location, not `docs/06_project-inputs/`. | `06_project-inputs/ARCHITECTURE.md` is a **snapshot**, not the master. If a separate canonical exists in `frontend/docs/`, sync from there to `06_project-inputs/` at the start of each sprint. |

---

## Daily log

- 2026-MM-DD: …

---

## Closure

- Gates passed: ☐
- Deferred to Sprint 1: ☐
- Methodology amendments proposed: ☐
- Operator signoff (date): ☐

---

## References

- Roadmap: `ROADMAP.md` §3
- Methodology: `../04_methodology/VELO-METHODOLOGY.md` §3 (folders), §12 (INDEX protocol)
- Sprint tracking template: ROADMAP.md §15.1
