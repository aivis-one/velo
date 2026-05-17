# `06_project-inputs/` — External Reference Documents

This folder holds **read-only** snapshots of documents authored outside the
design-and-handoff pipeline. They are consumed by the pipeline; they are
never edited in this folder.

> Per VELO-METHODOLOGY.md §3.1: this folder's contents are inputs, not
> deliverables. The pipeline references them; it does not modify them.

---

## Files

| File | Origin | Purpose | Update protocol |
|---|---|---|---|
| `ARCHITECTURE.md` | `D:\02_Projects\velo\frontend\docs\ARCHITECTURE.md` (intended canonical location) | Frontend code rules (Vue patterns, store conventions, API wrapper). Screen specs reference this by section number. | Manual sync when the canonical version changes. Note in `../INDEX.md → Recent Changes` when synced. |
| `api-openapi.json` | Backend OpenAPI generator output | Single source of truth for endpoint operationIds, request/response shapes, error codes. Screen specs reference operationIds from this file (§8.3 spec template, Section 5). | Snapshot. When the backend contract changes, replace this file and bump the snapshot date in `../INDEX.md`. |

---

## How the pipeline uses these inputs

- **Spec authoring (VELO-METHODOLOGY §8 + §9.6):** Cowork reads
  `api-openapi.json` to map endpoint operationIds and response types to
  store fields. Cowork reads `ARCHITECTURE.md` to ground spec rules in
  the project's frontend code conventions.
- **Methodology cross-references (VELO-METHODOLOGY §1.3):** the
  methodology cites ARCHITECTURE.md by section number; when in conflict,
  ARCHITECTURE.md wins for code-level rules and the methodology wins for
  design-and-handoff process.

---

## Hard rules

- **Do not edit files here.** They are mirrors of upstream documents.
- **Do not generate code from a stale snapshot.** Re-sync before
  starting a new sprint.
- When citing an ARCHITECTURE.md section in a screen spec, verify the
  section exists (see VELO-METHODOLOGY §11.1 AP-DS-6 for the failure mode).

---

## References

- Methodology: `../04_methodology/VELO-METHODOLOGY.md` §1.3 (relationship
  to other documents), §3 (folder structure), §8 (spec layer that
  consumes these inputs)
- Top-level: `../INDEX.md`
