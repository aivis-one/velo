# Sprint 2.5 — DS Completion + Foundation Transfer + Documentation English Translation

```
Dates:    2026-05-18 → in progress
Status:   planned (standalone, opens after Sprint 2 closure on 2026-05-18)
Owner:    Cowork (Tracks A + C), Claude Code (Track B), Operator (validator all tracks)
Goal ref: ROADMAP.md §5.5
Predecessor: Sprint 2 (closed 2026-05-18)
Successor:   Sprint 3 (starts on DS-complete state + frontend foundation in place)
```

---

## Goal

Close the design-system gap left after Sprint 1 (which produced only general per-token statistics, not per-block harvest detail) and pre-stage the frontend foundation by transferring battle-tested patterns from `D:\02_Projects\cbshome\frontend\src\`. Additionally, convert legacy Russian narrative in process documentation to English per methodology v1.4 P6 + §11.5 AP-P-8.

This sprint inserts between Sprint 2 (P0 mockups) and Sprint 3 (User block wave 1) because:

1. Sprint 2 Phase 4 Dashboard 9 attempt showed that per-element PNG reverse-engineering causes 3× rework. Methodology v1.3 codified §7.0 Block-Harvest-First as the fix. This sprint applies the fix to all remaining SACRED blocks before mass mockup production starts.
2. CBSHOME (`D:\02_Projects\cbshome\`) is a production reference implementation with identical stack — 85 .vue + 57 .ts files. ~70% of frontend foundation work is already solved there. Transfer-and-adapt is ~10× faster than re-invention.
3. Operator audit on 2026-05-18 found 2852 Cyrillic occurrences across 29 docs files. Russian narrative in process docs costs ~2× tokens on every session read with no value gain. Methodology v1.4 codified P6 (English-default) + AP-P-8. This sprint executes the conversion as Track C.

---

## Scope

Three parallel tracks. None blocks another — different files, different owners, different deliverables.

| Track | Owner | Scope | Reference |
|---|---|---|---|
| **A — DS completion (block-by-block)** | Cowork | Harvest all 9 SACRED blocks into DS per methodology §7.0. Five deliverables per block: tokens + assets + ASSETS-INDEX + COMPONENTS-CATALOG entry + styleguide visualisation. | ROADMAP §5.5.2 |
| **B — CBSHOME foundation transfer** | Claude Code | Apply 16 patterns + 18 UI Kit components + 7 layout shells from CBSHOME to `frontend/src/`. Rename `C*` → `V*`, swap `--bg-*` → `--velo-bg-*`. 10 PR bundles. | ROADMAP §5.5.3, `06_project-inputs/CBSHOME-PATTERNS-FOR-VELO.md` |
| **C — Documentation English translation** | Cowork | Convert non-exempt Russian narrative to English. Preserve operator quotes in `«…»`, preserve UI sample data, preserve external inputs. 4 phases (Conv-1 HIGH core, Conv-2 HIGH trackers, Conv-3 MED DS technical, Conv-4 LOW reference). | ROADMAP §5.5.4, methodology v1.4 P6 + §11.5 AP-P-8 |

### Track A — block order

1. Dashboard 9 (root `541:6648`, 9 frames) — **first** (continuation of Sprint 2 Phase 4 in-flight work)
2. Calendar 11 (root `541:1553`, 11 frames)
3. Profile 7 (root `541:2355`, 7 frames)
4. Diary 20 (root `541:2816`, 20 frames — biggest block, may need 2 passes)
5. Messages 3 (root `541:2717`, 3 frames)
6. Analytics 3 (root `758:1529`, 3 frames)
7. Practices 15 (root `758:1950`, 15 frames)
8. Master Dashboard 8 (root `758:3245`, 8 frames)
9. Master Onboarding 13 (root `758:4318`, 13 frames)

### Track B — bundle priority

See ROADMAP §5.5.3 table. Order: api/client → stores → composables → router → i18n → main.ts → UI Kit → layout shells → utils → platform.

### Track C — conversion phases

See ROADMAP §5.5.4. Conv-1 (HIGH core process docs) first to remove the per-session entry tax fast.

---

## Tasks

See ROADMAP §5.5.5:

- **T2.5.1** — DS completion: Dashboard 9 block (first pass)
- **T2.5.2** — Mockup rebuild: Dashboard 9 viewer on DS-complete state
- **T2.5.3** — Per-block iteration (Track A blocks 2-9)
- **T2.5.4** — CBSHOME transfer bundles 1-10 (Track B)
- **T2.5.5** — Documentation English translation pass (Track C, Conv-1..Conv-4)
- **T2.5.6** — INDEX maintenance throughout

---

## Daily log

- 2026-05-18: Sprint opened. Files inherit from Sprint 2 closure session. Entry point per `_HANDOFF.md` — Track A T2.5.1 (Dashboard 9 harvest) as first action of new chat.

---

## Gate results

See ROADMAP §5.5.6.

Track A gate per block — pending.
Track B gate per bundle — pending.
Track C gate per file — pending.

Sprint 2.5 closure criterion: all 9 SACRED blocks DS-complete + all 10 CBSHOME pattern bundles merged + all Conv-1..Conv-4 non-exempt files translated.

---

## Deferred to next sprint

(none yet — sprint just opened)

---

## Methodology amendments proposed

(none yet — methodology v1.4 already absorbs all currently known amendments: P6 English-default + §6.8 DS Visualisation + §7.0 Block-Harvest-First + §11.5 AP-P-6/AP-P-7/AP-P-8)

---

## References

- Roadmap: `ROADMAP.md` §5.5 (v1.3 / 2026-05-18)
- Methodology: `04_methodology/VELO-METHODOLOGY.md` (v1.4 / 2026-05-18) — especially §1.1 P6, §6.8, §7.0, §11.5 AP-P-6/AP-P-7/AP-P-8
- CBSHOME reference: `06_project-inputs/CBSHOME-PATTERNS-FOR-VELO.md`
- Components catalog: `02_design-system/COMPONENTS-CATALOG.md`
- Handoff: `_HANDOFF.md` (v1.4)

---

## Anchor

```
[sprint-02.5.md | v1.0 | 2026-05-18]
Sprint 2.5 — standalone sprint between Sprint 2 (closed 2026-05-18) and Sprint 3 (pending DS-complete state).
Three parallel tracks: A=DS completion (Cowork), B=CBSHOME transfer (Claude Code), C=Documentation translation (Cowork).
First action of next chat: Track A T2.5.1 — Dashboard 9 DS harvest via methodology §7.0.
Location: D:\02_Projects\velo\docs\05_roadmap\sprint-02.5.md
```
