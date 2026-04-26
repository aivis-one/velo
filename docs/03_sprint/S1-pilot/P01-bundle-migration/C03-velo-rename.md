# Cycle C03: velo-* → Bundle Namespace Rename

> Phase 01: Bundle Migration | Sprint 1: Pilot
> Type: standard
> Tier: HIGH (affects-global-state — shared tokens across all view files)
> Status: DONE
> Closed: 2026-04-26

## Goal

Rename 29 active velo-* tokens to bundle namespace (`--text-primary`, `--surface-default`, etc.) across 444 usage sites. Apply opportunistic radius semantic migration. Clean up unused legacy tokens. Preserve 8 admin-deferred velo tokens.

## Result

29 active velo-* tokens renamed across 444 usage sites + radius opportunistic migration (62 card-sites + 3 warning-sites) + displayHelpers cleanup (3 inline hex → token references) + legacy cleanup. 67 files directly edited by C03; 513 total substitutions. 8 admin-deferred velo tokens retained in `variables.css` Legacy section per decision #020 (admin views deferred to S4+ per #010). 17/17 acceptance criteria passed.

## Key Decisions

- Cycle split into Assess (Gather + B1 hue decision STOP gate) + Apply (substitution batch) per Rule 16 — HIGH tier required STOP gate for `--velo-error` mapping decision.
- B1 `--velo-error` → `--pink-primary` (warm-palette preserve, exact value match) chosen over bundle `--feedback-error` (deep red); flagged for S2 UX review (BACKLOG #12).
- Admin-deferred marker convention introduced: explicit comment block above 8 retained velo tokens signals intent + blocks re-BACKLOG at future audits (decision #020).
- Scout grep convention gap discovered mid-cycle: closing-paren grep `var(--X)` missed fallback-syntax `var(--X, literal)` at 3 sites; resolved surgically; convention improvement BACKLOG'd.
- E1/E2 substitution group sequencing bug: prompt didn't lock order; 3 warning sites transiently became `--radius-lg` before surgical fix. Lesson: HIGH-tier prompts with adjacent substitution groups MUST specify explicit order (BACKLOG #17).

## Acceptance Summary

17/17 passed. 0 stale velo refs outside admin views + variables.css; bundle namespace consistent; visual parity confirmed via dev server preview; typecheck/lint/build all 0.

Status: DONE
Closed: 2026-04-26
