# `04_methodology/_archive/` — Superseded Methodologies and Historical Snapshots

These are materials that informed the unified `VELO-METHODOLOGY.md` (v1.0,
2026-05-17) but are no longer authoritative. The unified methodology
replaces them in their entirety (see VELO-METHODOLOGY §1, opening
paragraph: *"replaces three universal methodologies (DS, LIVEMOCKUP,
HANDOFF) with one project-specific instrument"*).

**Status:** read-only historical reference. Do not follow rules from
these files for current work.

---

## What's here

### Superseded methodologies

| File | Original role | Replaced by |
|---|---|---|
| `DS-METHODOLOGY.md` | Universal Design System methodology (any stack, any source). Stack-agnostic rules for tokens, naming, two-layer architecture. | VELO-METHODOLOGY §6 (Design System Layer) + §11.1 (DS anti-patterns) |
| `LIVEMOCKUP-METHODOLOGY.md` | Universal single-HTML mockup methodology with device shell, Navigation Map, sample-data conventions. | VELO-METHODOLOGY §7 (Mockup Layer) + §11.2 (Mockup anti-patterns) + §11.3 (Token bridge for mockups) |

The third universal methodology mentioned in VELO-METHODOLOGY §1 (the
HANDOFF methodology) had no separate file in this project — its rules
are folded into VELO-METHODOLOGY §8 (Handoff Layer).

### Historical snapshots and reports (pre-existing in this folder)

| File | What it is | Current canonical location |
|---|---|---|
| `ARCHITECTURE.md` | Frontend architecture guide for Claude Code. Earlier snapshot — byte-identical to the current canonical copy as of 2026-05-17. Kept as a frozen reference of "what was assumed when these methodologies were written." | `../../06_project-inputs/ARCHITECTURE.md` |
| `JSON-ENDPOINT.txt` | Backend OpenAPI dump in `.txt` form. Earlier snapshot — byte-identical to the current canonical copy (113 099 bytes, 64 paths, openapi 3.1.0). | `../../06_project-inputs/api-openapi.json` |
| `CC-REPORT.txt` | **Claude Code reconnaissance report** of the frontend F0 state (501 lines), produced before the unified methodology was written. Cited from `ROADMAP.md` §3.1 T0.3 as the source for Sprint 0 cleanup tasks. Read this when planning Sprint 0 — it documents the gaps the cleanup is responding to. | — (no current replacement; the report is a one-time artifact) |

The two snapshot files (`ARCHITECTURE.md`, `JSON-ENDPOINT.txt`) are not
consumed by current work — always read the canonical copies in
`06_project-inputs/` instead. They are kept solely to provide an
unambiguous historical reference for the version that informed the v1.0
methodology and roadmap.

`CC-REPORT.txt` remains useful operational context for Sprint 0 planning.

---

## When to read these files

Only when:

1. Investigating why a specific rule in `VELO-METHODOLOGY.md` was written.
2. Porting the methodology to another product (universal rules are easier
   to extract from these source documents than to back out of the
   VELO-specific document).
3. Auditing the lineage of an anti-pattern listed in
   `VELO-METHODOLOGY.md §11`.
4. Planning Sprint 0 cleanup — `CC-REPORT.txt` describes the frontend
   F0 baseline.

For **all current work**, ignore these files and follow
`../VELO-METHODOLOGY.md`.

---

*Archived on 2026-05-17 as part of the v1.0 methodology adoption.*
