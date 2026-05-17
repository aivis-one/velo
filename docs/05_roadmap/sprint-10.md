# Sprint 10 — Handoff Package + Final Sync

```
Dates:    TBD → TBD (planned 1 week)
Status:   planned
Owner:    Cowork (assembler), Operator (validator), Claude Code (frontend sync)
Goal ref: ROADMAP.md §13
Phase:    Phase 6 (Handoff Package Assembly)
```

---

## Goal

Assemble the deliverable package per Phase 6 of methodology. Synchronize
all artifacts. Prepare handoff to Claude Code / direct developer.

---

## Scope

Five tasks. End state: a clean, self-contained `01_deliverable/` folder
that the developer can consume without referencing any other folder.

| # | Task | Owner |
|---|---|---|
| T10.1 | Phase 6 assembly | Cowork |
| T10.2 | README finalization | Cowork |
| T10.3 | PACKAGE GATE validation | Operator |
| T10.4 | Frontend sync (final) | Claude Code |
| T10.5 | Handoff communication | Operator |

---

## Task checklist

### T10.1 — Phase 6: Handoff Package Assembly

Ref: VELO-METHODOLOGY.md §3, §10.6 + Prompt §9.7.
Owner: Cowork.

Sync master → deliverable:

- [ ] `cp 02_design-system/tokens/variables.css → 01_deliverable/styles/variables.css`
- [ ] `cp 02_design-system/tokens/global.css → 01_deliverable/styles/global.css`
- [ ] `rsync 02_design-system/assets/icons/ → 01_deliverable/assets/icons/`
- [ ] If self-hosted fonts: `rsync` to `01_deliverable/assets/fonts/`
- [ ] Byte-diff check: master vs deliverable copies are identical (or
      diff is documented in a sync log)

Spec curation in `01_deliverable/screens/`:

- [ ] Every spec status is `active` or `archived`. **No `draft` in delivery.**
- [ ] Drafts removed or completed before package gate
- [ ] `01_deliverable/screens/INDEX.md` reflects current spec catalog
- [ ] Every spec's `mockup-approved-on` date is present in front-matter

### T10.2 — README finalization

Ref: VELO-METHODOLOGY.md §9.7.1 template.
Owner: Cowork.

- [ ] Replace stub `01_deliverable/README.md` with full §9.7.1 template
- [ ] Date filled (today's ISO date)
- [ ] Source + Target paths correct
- [ ] "What's in this package" table — every row present, no
      placeholders, all paths real
- [ ] "How to use tokens" canonical example block included
- [ ] "Hard rules" section copied from methodology §11.6 quick-reference
- [ ] "Implementing a screen" 4-step flow correct
- [ ] "Active specs" links to `screens/INDEX.md`
- [ ] No `{placeholder}` text left anywhere

### T10.3 — PACKAGE GATE validation

Ref: VELO-METHODOLOGY.md §10.6.
Owner: Operator.

- [ ] `01_deliverable/README.md` complete with no placeholders
- [ ] `01_deliverable/styles/variables.css` equals `02_design-system/tokens/variables.css` byte-for-byte
- [ ] `01_deliverable/styles/global.css` equals master byte-for-byte
- [ ] `01_deliverable/assets/icons/` mirrors master (file count + checksum match)
- [ ] `01_deliverable/screens/INDEX.md` reflects current spec catalog
- [ ] No spec with status `draft` present (only `active` or `archived`)
- [ ] Top-level `docs/INDEX.md` updated with package version + date
- [ ] Approve or revise

### T10.4 — Frontend sync (final)

Owner: Claude Code, instructed by Operator after T10.3 passes.

- [ ] `cp 01_deliverable/styles/variables.css → frontend/src/styles/variables.css`
- [ ] `cp 01_deliverable/styles/global.css → frontend/src/styles/global.css`
- [ ] `rsync 01_deliverable/assets/icons/ → frontend/src/assets/icons/`
- [ ] Import chain verified: `main.ts` imports `global.css` (or
      `variables.css`) before any component CSS
- [ ] `npm run build` passes
- [ ] `npm run typecheck` (`vue-tsc --noEmit`) passes
- [ ] `npm run lint` passes
- [ ] Commit + push: "phase: P6 handoff package delivered (v{version})"

### T10.5 — Handoff communication

Owner: Operator.

- [ ] Notify Claude Code / developer that the package is ready
- [ ] Provide location: `D:\02_Projects\velo\docs\01_deliverable\`
- [ ] Provide the methodology + roadmap pointers for context
- [ ] Schedule follow-up review (Sprint 11+ reserve)

---

## Sprint 10 Gate

Ref: ROADMAP.md §13.2.

- [ ] PACKAGE GATE passed (T10.3)
- [ ] `frontend/src/` reflects deliverable
- [ ] Build + typecheck + lint green
- [ ] Developer notified

---

## Risks

| ID | Risk | Mitigation |
|---|---|---|
| 10.A | Token drift discovered during sync (master vs deliverable differ). | Regenerate deliverable from master; log drift cause in `02_design-system/INDEX.md → Iteration Log`. |
| 10.B | Implementation-stage feedback exposes spec gaps. | Normal and expected; flows into Sprint 11 reserve. Don't block PACKAGE GATE on this. |
| 10.C | Some specs still `draft` at sprint start. | Carry to Sprint 11 reserve OR complete in Sprint 10 ahead of T10.3. Do not push drafts into delivery. |

---

## Daily log

- 2026-MM-DD: …

---

## Closure

- PACKAGE GATE: ☐ passed / ☐ failed
- Frontend build green: ☐
- Final coverage delivered: ☐ ____ of ~120 (~XX%)
- Developer notified: ☐ (date: ____)
- Reserve sprint scope identified: ☐
- Operator signoff (date): ☐

---

## References

- Roadmap: `ROADMAP.md` §13
- Methodology: §3 (folder structure), §9.7 (assembly prompt), §9.7.1 (README template), §10.6 (PACKAGE GATE), §11.6 (hard-rules quick reference)
