# Cycle C02: variables.css Bundle SSOT Port

> Phase 01: Bundle Migration | Sprint 1: Pilot
> Type: standard
> Tier: MEDIUM
> Status: DONE
> Closed: 2026-04-26

## Goal

Port bundle's `colors_and_type.css` token definitions into `frontend/src/styles/variables.css` as bundle-SSOT source. Add `@font-face` for Marmelad. Light + dark theme tokens. Preserve legacy tokens still in active use.

## Result

`variables.css` restructured: `@font-face` block (line 9), `:root` block with 101 bundle canonical tokens (line 17), `[data-theme="dark"]` overrides with 32 dark-mode tokens (line 250), and Legacy section preserving 86 still-active legacy tokens. Total 177 custom property declarations. Bundle utility classes + html/body defaults from bundle's `colors_and_type.css` NOT ported (scope-locked to token definitions only — BACKLOG'd for S2 decision). 11/11 acceptance criteria passed.

## Key Decisions

- 9 conflict tokens (radius/shadow) where variables.css and bundle differed: adopted bundle values across all 9 (decision #016). Per-site semantic migration (62 `--radius-md` card-sites → `--radius-lg`; 3 `--radius-sm` warning-sites → `--radius-md`) deferred to C03.
- decision #007 (no backdrop-filter) clarified: shadows permitted via bundle `--shadow-*` tokens; only `backdrop-filter` / glassmorphism forbidden (decision #017).
- Pre-Exec literal-STOP misfired on assumption of `@import` chain in CSS files; resolved by recognizing main.ts module-import architecture (decision #019).

## Acceptance Summary

11/11 passed. Bundle tokens accessible at runtime; dark mode tokens loaded via `[data-theme="dark"]`; Marmelad @font-face working; 86 legacy tokens preserved without conflict; typecheck/lint/build all 0.

Status: DONE
Closed: 2026-04-26
