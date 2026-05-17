# VELO — Frontend Deliverable Package

Date: 2026-05-17 (initial stub — will be finalized at Sprint 10 PACKAGE GATE)
Source: `D:\02_Projects\velo\docs\01_deliverable\`
Target: `D:\02_Projects\velo\frontend\`

> **Status:** stub. This file is finalized during Sprint 10 (Phase 6:
> Handoff Package Assembly) per VELO-METHODOLOGY.md §9.7 and §9.7.1.
> Until then this README documents the intended structure only.

---

## What's in this package (intended; populated through Sprints 1–10)

| Path | Purpose | Action for the developer |
|---|---|---|
| `styles/variables.css` | Design tokens (Layer 1 + Layer 2). Master lives in `../02_design-system/tokens/variables.css`. | Copy to `frontend/src/styles/variables.css` |
| `styles/global.css` | Fonts, reset, `.velo-typo-*` classes. Master lives in `../02_design-system/tokens/global.css`. | Copy to `frontend/src/styles/global.css` |
| `assets/icons/` | All UI icons (PNG + SVG). Mirror of `../02_design-system/assets/icons/`. | Copy to `frontend/src/assets/icons/` |
| `assets/fonts/` | Self-hosted fonts (if applicable; currently empty — fonts loaded from Google Fonts). | Copy to `frontend/src/assets/fonts/` if used |
| `screens/` | Screen specifications `SCR-NNN-*.md`. Active specs only. | Reference during implementation |
| `screens/INDEX.md` | Spec catalog with statuses, mockup links, priorities. | Use as the implementation to-do list |

---

## How to use tokens (canonical example)

In any Vue component `<style scoped>`:

```css
.my-card {
  background: var(--velo-bg-card);
  border: 1px solid var(--velo-border-default);
  border-radius: var(--velo-radius-md);
  padding: var(--velo-space-4);
}
.my-card__title {
  color: var(--velo-text-primary);
  font-size: var(--velo-size-16);
}
```

---

## Hard rules

- Components use **only Layer 2** tokens (`--velo-text-*`, `--velo-bg-*`, etc.).
- Never reference Layer 1 primitives (`--velo-color-*`) from components.
- All user-facing strings go through `t('key')` via vue-i18n.
- Prices are integer cents at API level — use `formatMoney()` from
  `frontend/src/utils/format.ts`.
- `line-height` is always a numeric value, never `normal`.
- Token arithmetic must use `calc()`. Example:
  `calc(var(--velo-space-12) + 2px)`. Never `var(...) + Npx` without
  `calc()` — browsers silently drop such declarations.

(Cross-reference: full hard-rule list in VELO-METHODOLOGY.md §11.6.)

---

## Implementing a screen

1. Open the relevant `screens/SCR-NNN-*.md` spec (status `active` only).
2. Open the matching mockup in `../03_mockups/{role}/`.
3. Implement the screen per spec section by section.
4. Validate against the spec's Section 12 Acceptance Criteria.

---

## Active specs

See `screens/INDEX.md` for the current list and statuses.

At the time of this stub: no specs yet — they arrive in Sprint 3+ per
ROADMAP.md.

---

## Questions / changes

If a spec is ambiguous or a token is missing, contact the operator.
Do not implement guesswork. Track open questions in
`../02_design-system/INDEX.md → Open TODOs`.

---

## References

- Methodology: `../04_methodology/VELO-METHODOLOGY.md`
- Roadmap: `../05_roadmap/ROADMAP.md`
- Architecture rules: `../06_project-inputs/ARCHITECTURE.md`
- API contract: `../06_project-inputs/api-openapi.json`
- Top-level docs index: `../INDEX.md`
