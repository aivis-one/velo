# Cycle C09: Icons strategy (D3 ratified)
> Phase 02: Audit + Backend Coordination | Sprint 1: Pilot
> Type: standard (decision + audit)
> Status: DONE

## Goal
Resolve BACKLOG #19 (D3 icons decision missing from decisions.md). Inventory Velo Vue-SVG components vs bundle PNG icons; identify collision points; ratify strategy for S2/S3 work.

## Result
D3 ratified as decision #024 (`Icons strategy: Vue-SVG baseline + bundle PNG decorative supplement`).

Inventory findings:
- 14 Velo Vue-SVG icons in `frontend/src/components/icons/` (currentColor + size prop, theme-aware).
- 12 bundle PNG icons in `frontend/src/assets/brand-icons/` (raster, brand-aligned wellness vocabulary).
- Real collisions: only 2 (`brain`, `meditation`) — resolved as Vue-SVG.
- 7 Velo-only navigation/state primitives (no bundle equivalents).
- 10 bundle-only decorative wellness PNGs (no Velo equivalents).
- 1 potentially-orphan: `IconRuble` (Velo on EUR per backend) — flagged for review at BACKLOG #29.
- 3 consumer files only: PracticeDetailView.vue, components/icons/index.ts, router/tabs.ts.

Strategy (binding for S2/S3):
1. UI primitives → Velo-SVG only.
2. Decorative wellness accents → bundle PNG OK.
3. New nav/state icon → create new Velo-SVG, do NOT import bundle PNG.
4. Conflict resolution: Velo-SVG wins for 2 collisions.

Documented in AUDIT-S1.md §9. Decision row #024 in decisions.md. BACKLOG resolutions: #19 (D3 BLOCKING) → RESOLVED. BACKLOG additions: #29 IconRuble removal candidate, #30 future SVG migration for 10 decorative PNGs.

Status: DONE
Closed: 2026-04-26
