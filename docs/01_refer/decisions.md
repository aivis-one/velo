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
