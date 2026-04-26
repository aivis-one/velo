# Cycle C04: Glass Cleanup + backdrop-filter Removal

> Phase 01: Bundle Migration | Sprint 1: Pilot
> Type: standard
> Tier: HIGH (affects-global-state — VHeader.vue + VTabBar.vue shell components)
> Status: DONE
> Closed: 2026-04-26

## Goal

Remove all `--velo-glass-*` tokens + their usages. Strip `backdrop-filter` lines from CSS (per decision #007 flat aesthetic). Replace semi-transparent surface usages with project-extension alpha tokens. Apply across shell components + 117 component-level rename sites.

## Result

117 glass token renames + 2 drops (entire glass block removed from variables.css) + 138 `backdrop-filter` / `-webkit-backdrop-filter` lines removed across CSS + 5 project-extension alpha tokens added (`--surface-steel-alpha-15/60`, `--surface-teal-alpha-30/40`, `--surface-warm-alpha-40`) per decision #021 pattern. 0 stale glass references remaining. 15/15 acceptance criteria passed.

## Key Decisions

- Path A chosen over inline rgba: project-extension token pattern (decision #021) preserves FP-01 compliance (no inline hex/rgba) + bundle namespace consistency.
- Nested-fallback discovery at `VModal.vue:111` (`var(--X, var(--Y))`) — second instance of fallback-syntax gap from C03; resolved surgically; reinforces BACKLOG #10 scout convention improvement.

## Acceptance Summary

15/15 passed. 0 backdrop-filter outside doc-comments; 0 velo-glass refs; 5 alpha tokens defined and consumed; visual flat aesthetic preserved per #007/#017; typecheck/lint/build all 0.

Status: DONE
Closed: 2026-04-26
