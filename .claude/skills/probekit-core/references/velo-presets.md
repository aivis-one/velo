# Velo Project Presets — ProbeKit Cross-Skill Context

> Reference loaded by ProbeKit skills when auditing Velo. Contains project-specific paths,
> ACTIVE decisions (false-positive avoidance), and platform-context notes.
> Last updated: 2026-04-30 (post S1-Clean-Sync, after #044 #045 added).
>
> **How to use:** any ProbeKit skill auditing Velo should read this file at Step 1
> (input/environment) before applying its detection patterns. Treat all listed
> patterns as DECIDED — do not flag them as findings.

---

## Project paths (canonical)

| Surface | Path |
|---|---|
| Frontend source | `frontend/src/` |
| Frontend public | `frontend/public/` |
| Bundle SSOT (design system) | `docs/04_assets/velo-design-system-2026-04-23/` |
| Bundle README (brand reference) | `docs/04_assets/velo-design-system-2026-04-23/project/README.md` |
| Token file | `frontend/src/styles/variables.css` |
| Tsconfig | `frontend/tsconfig.json` |
| Index.html (viewport, manifest) | `frontend/index.html` |
| Audit reports archive | `docs/01_refer/ARCHIVES/CODE-AUDIT/PROBKIT-REVIEW/` |
| Sprint-close audit consolidated | `docs/01_refer/ARCHIVES/CODE-AUDIT/S{N}-CODE-AUDIT.md` |
| Decisions log | `docs/01_refer/decisions.md` |
| Backlog | `docs/01_refer/BACKLOG.md` |
| Out-of-scope (legacy) | `docs/05_legacy/` |
| Out-of-scope (backend) | `backend/` |
| Out-of-scope (root VELO-*.md) | repo root |

## Platform context

- **Telegram Mini App (TMA) primary** + PWA fallback for non-Telegram browsers (decision #013)
- Auth: TMA initData (HMAC-validated by backend) for TMA users; email/OAuth UI mock for PWA users (decision #028 hybrid γ)
- Mobile-first: phone (≤480px) primary; tablet/desktop are PWA fallback only
- Russian-only locale at MVP; i18n infrastructure deferred (BACKLOG #38, #86)

## False-positive avoidance — Velo-decided patterns (DO NOT flag)

The following patterns are intentional per ACTIVE decisions. Skills must not flag them as findings.

### CSS / styling

| Pattern | Decision | Rationale |
|---|---|---|
| `box-shadow` with `--shadow-*` tokens | #017 | Shadows permitted; only `backdrop-filter` and glassmorphism forbidden |
| CSS imported via `main.ts` lines 16-17, NOT `@import` in `variables.css` | #019 | Vite/Vue convention; bundler optimization |
| 8 admin-deferred tokens at `variables.css:230-241` (legacy section, marker comment block lists using files) | #020 | Tokens used only by admin views (deferred until #010 admin reactivation) |
| 6 project-extension tokens (`--nav-inactive-bg`, `--surface-{steel,teal,warm}-alpha-*`) | #021 | Used after glass-cleanup; FP-01 compliant |

### Frontend code

| Pattern | Decision | Rationale |
|---|---|---|
| `frontend/src/api/generated.ts` auto-generated, header "DO NOT EDIT MANUALLY" | #023 | Regen pipeline (`backend/scripts/generate_ts_types.py`); manual edits override on next regen |
| `frontend/src/api/types.ts` re-exports from `./generated` + adds frontend-only union types | #023 | SSOT split — backend shapes from generated, frontend unions local |
| `sessionStorage` (not localStorage) for auth token | (architectural; verified clean in S1 audit) | Per-tab scope correct for TMA session |
| `Math.random()`, MD5, SHA1 absent | (no client-side crypto) | Frontend doesn't perform crypto; Telegram initData verified by backend |
| Bundle PNG decorative icons in `frontend/src/assets/brand-icons/` | #024 | Vue-SVG baseline + bundle PNG decorative supplement; conflict resolution Vue-SVG wins |
| `frontend/src/views/auth/WelcomeView.vue` fast-track (123 LOC, no Claude Design pipeline) | #025 | Static landing exception to #002 |

### Tooling / build

| Pattern | Decision | Rationale |
|---|---|---|
| `frontend/package-lock.json` modified after `npm install` (peer markers, metadata) without version changes | #018 | Lockfile implicit scope when build/test/lint in cycle AC |
| Major-version dep updates pending (pinia 2→3, vue-router 4→5, etc.) | #045 | Deferred to dep-update sprint |
| 5 residual npm audit CVEs all dev/build-time | (BACKLOG #54) | Zero end-user attack surface; resolution requires `--force` (deferred to dep-update) |

### Velo UI library conventions

| Pattern | Note |
|---|---|
| `VButton size="sm"` min-height 36px | Below WCAG 44×44 touch target. Tracked in BACKLOG #42 (S2 mobile-polish cluster). Skills should flag if probing touch targets but cite #42 as known. |
| `VInput height: 40px` | Same as above. Form input "inline" exception in WCAG 2.5.5 partly applies; tracked in #42. |
| `outline: none` paired with alternative focus indicator (border-color or background) at 11+ sites | WCAG-acceptable when alternative is visible; not a finding. |

## Sprint context

- Current sprint at this revision: post-S1-close, pre-S2-P05 (S2 first phase = "Bundle-port Existing Screens", 5 cycles starting C15)
- Last full ProbeKit lite-profile run: S1-Sprint-Closer Step 2 (2026-04-28); reports consolidated to `docs/01_refer/ARCHIVES/CODE-AUDIT/S1-CODE-AUDIT.md`

## Active decisions snapshot (#001–#045)

For the authoritative list, parse `docs/01_refer/decisions.md` and filter rows where `Status` contains `ACTIVE`. As of 2026-04-30 there are **45 decisions**, **44 ACTIVE** (none SUPERSEDED yet; #002 has explicit deviation noted in #025 but remains ACTIVE).

**Top decisions a probe-skill is likely to encounter:**

- #006 Bundle = SSOT
- #007 Flat aesthetic; no backdrop-filter
- #008 Dark mode tokens in S1, UI toggle in C25 (re-numbered from C19 by S2 re-plan)
- #009 Token rename to bundle namespace; DESIGN_MIGRATION.md v4 SUPERSEDED
- #013 VELO = TMA + PWA
- #023 generated.ts SSOT
- #028 Hybrid auth model (γ): TMA + PWA-OAuth (partial supersede of #012)
- #029 New design batch supersedes bundle for visual layer; bundle keeps token SSOT (~80% retained)
- #044 paramiko as Claude Code SSH primitive
- #045 SSH key auth standard

When auditing, **always cross-reference decisions.md before flagging a pattern as finding**. Quote decision number in finding's "covered by decision #NNN; defer/skip" annotation if known-OK.

## Maintenance

This file is updated when:
- New decisions added that change probe applicability
- Sprint close adds new patterns to false-positive list
- New project-wide path conventions introduced (e.g., new top-level dir)

Stale-content gate: at Sprint-Closer Step 2 Pre-Exec, scout this file; if any cited decision is SUPERSEDED/DEPRECATED, flag for refresh in next Clean-Sync.
