# Code Audit — Sprint 1: Pilot

Date: 2026-04-28
Audited by: ProbeKit lite profile (6 skills) + backender code review pass + Claude Chat classification
Audit base: HEAD `bd439ec` at audit run time (Step 2 commit); CRITICAL fix applied on top.

---

## Summary

| Severity | Count | Blocked? |
|----------|-------|----------|
| CRITICAL | 1 | Resolved — `npm audit fix` (no `--force`) closed prod-relevant CVE; residual 5 reclassified MEDIUM (dev/build-time only) and routed to BACKLOG #54 |
| HIGH | 3 | Recommended; deferred to S2 a11y polish cluster (#40) per Step 5 structural-HIGH rule |
| MEDIUM | 16 | No — BACKLOG entries #40–#48, #54 |
| LOW | 14 | No — BACKLOG entries #49–#53 + folded into clusters |

---

## Audit Sources

| Source | Version | Score / Verdict | Findings (🔴/🟡/🟢/💎) |
|--------|---------|-----------------|------------------------|
| probekit-type-audit | 1.0.0 | 10/10 — 💎 DIAMOND clean | 0 / 0 / 0 / 1 |
| probekit-code-audit | 2.3.0 | 8/10 — PASS | 0 / 4 / 11 / 5 |
| probekit-a11y-audit | 1.0.0 | 6.25/10 — WARN gate | 0 / 6 / 4 / 0 |
| probekit-responsive-audit | 1.0.0 | 7.86/10 | 0 / 3 / 4 / 2 |
| probekit-security-audit | 1.1.0 | clean | 0 / 1 / 4 / 4 |
| probekit-design-audit | 1.0.0 | bundle SSOT intact | 0 / 5 / 0 / 1 |
| backender-review (russian) | per #022 protocol | 8/10 | 1 / 6 / 11 / 0 |
| **Combined headline** | | | **1 / 25 / 34 / 13** |

After cross-skill dedup: 1 CRITICAL (resolved + residual reclassified) + 3 HIGH + ~30 unique MEDIUM/LOW findings. 12 DIAMONDs + 11 already-tracked BACKLOG entries confirmed.

---

## npm audit fix outcome

**Pre-fix baseline**: 11 vulnerabilities — 1 critical, 8 high, 2 moderate.

**Command applied**: `cd frontend && npm audit fix` (no `--force`).

**Post-partial-fix state**: 5 vulnerabilities — 1 critical, 4 high.

**Resolved (6 CVEs)** — including the only prod-runtime-relevant one:
- vite GHSA-p9ff-h696-f583 (dev-server arbitrary file read via WebSocket) — **prod-relevant for developer/staging dev-server; closed**
- vite GHSA-4w7w-66w2-5vf9 (Path Traversal in optimized deps `.map`) — closed
- flatted GHSA-25h7-pfq9-p65f (unbounded recursion DoS) — closed
- flatted GHSA-rf6f-7fwh-wjgh (prototype pollution) — closed
- brace-expansion GHSA-f886-m6hf-6m8v (DoS / memory exhaustion) — closed
- (1 transitive) — closed

**Residual (5 CVEs, all dev/build-time only — zero end-user attack surface)**:

| Severity | Package | Type | Reaches prod bundle? |
|---|---|---|---|
| critical | happy-dom (17.x → 20.x major) | direct devDep | No — vitest DOM env, test-only |
| high | serialize-javascript | transitive (workbox-build) | No — build-time |
| high | @rollup/plugin-terser | transitive (workbox-build) | No — build-time |
| high | workbox-build | transitive (vite-plugin-pwa) | No — build-time |
| high | vite-plugin-pwa (0.21.2 → 0.19.x downgrade or major bump) | direct devDep | No — build-time |

**Why not `--force`**: forces happy-dom 17→20 + vite-plugin-pwa major bump (or downgrade to 0.19.x). Both require breaking-change verification (test refactoring + PWA precache regeneration validation). Out of Sprint-Closer scope per Backender §10 («if `--force` needed → feature-branch + smoke-test»). Routed to dependency-update cycle alongside BACKLOG #45 (pinia 2→3, vue-router 4→5, vite 6→8, vitest 3→4, ts 5→6, eslint 9→10).

**Build verification post-partial-fix**:
- `npm run typecheck` → 0 errors
- `npm run lint` → 0 errors / 756 warnings (baseline #14 preserved)
- `npm run test` → 32/32 pass
- `npm run build` → green; PWA precache 99 entries

**Lockfile delta**: `frontend/package-lock.json` updated (33 lines changed); `frontend/package.json` unchanged. Per #018, lockfile changes from `npm audit fix` are implicit scope.

**Reclassification rationale**: residual 5 are reclassified MEDIUM because:
1. Zero end-user attack surface (build/test packages don't ship in `dist/`)
2. Build-time supply-chain risk is real but contained — would require npm registry compromise of one specific package + the project to consume the malicious version on next install
3. happy-dom test-runner risk is bounded to developer machines running self-authored test fixtures
4. Resolution requires breaking-change cycle, not Sprint-Closer scope

The residual is tracked in BACKLOG #54 with explicit deferral to dep-update cycle.

---

## Issues

| # | File | Severity | Issue | Source | Action |
|---|------|----------|-------|--------|--------|
| 1 | frontend/package.json + lockfile | CRITICAL → resolved (prod) + residual MEDIUM | npm audit: was 1 critical + 8 high + 2 moderate; partial fix resolved 6 incl. all prod-relevant. 5 residual all dev/build-time | Backender §10 | **PARTIAL FIX in Step 6**: 6/11 CVEs closed; 5 residual deferred to dep-update cycle per BACKLOG #54 |
| 2 | UserProfileView, MasterDashboardView, PracticeCard | HIGH | 7 `<div @click>` — keyboard-inaccessible (incl. logout button) | A11Y P1+P3 | Defer S2 — cluster #40 |
| 3 | components/ui/VModal.vue | HIGH | No focus-trap, no focus-return, Tab leaves dialog | A11Y P4 | Defer S2 — cluster #40 |
| 4 | VInput, VTextarea, VSelect, VCheckbox | HIGH | Form labels not associated with inputs (no `for`/`id`) | A11Y P6 | Defer S2 — cluster #40 |
| 5 | 9 large views | MEDIUM | View-level `extractApiError` not adopted (~25-30 try/catch dup sites) | Code §6 + Backender §6+§8 | Defer S2 — singleton #43 |
| 6 | frontend/src (multiple) | MEDIUM | 21 hardcoded radii (12 × 5px, 8 × 100px, 1 × 20px) | Design P4 | Defer S2 — cluster #41 |
| 7 | frontend/src (multiple) | MEDIUM | ~12 spacing px values where tokens exist | Design P3 | Defer S2 — cluster #41 |
| 8 | frontend/src (multiple) | MEDIUM | 30 `white` named-color + 8 rgba overlay sites | Design P1 | Defer S2 — cluster #41 |
| 9 | frontend/index.html | MEDIUM | viewport meta missing `viewport-fit=cover` | Resp P1 | Defer S2 — cluster #42 |
| 10 | components/layout/VHeader.vue | MEDIUM | Missing `safe-area-inset-top` (iPhone notch) | Resp P2 | Defer S2 — cluster #42 |
| 11 | components/ui/VButton, VTabBar, VInput | MEDIUM | Touch targets below WCAG 44px (36/40/42px) | Resp P3 | Defer S2 — cluster #42 |
| 12 | components/layout/VTabBar.vue + components/ui/VToast.vue | MEDIUM | Missing `aria-current` on active tab + `role=status aria-live` on toasts | A11Y P2 | Defer S2 — cluster #40 |
| 13 | components/ui/VToast.vue | MEDIUM | Toast keyboard-dismiss missing | A11Y P3 | Defer S2 — cluster #40 |
| 14 | frontend/index.html + global.css | MEDIUM | No skip-to-content link + `<main id>` | A11Y P7 | Defer S2 — cluster #40 |
| 15 | components/icons/Icon*.vue + loading states | MEDIUM | ~16 icons missing `aria-hidden=true`; loading missing `aria-busy` | A11Y P8 | Defer S2 — cluster #40 |
| 16 | router/index.ts | MEDIUM | Auth-init timeout silent fallback (`console.warn` only); App.vue gate masks it | Code §3 + Backender §3 | Defer S2 — singleton #46 |
| 17 | router/guards.ts | MEDIUM | `roleGuard()` synchronous (defense-in-depth gap) | Sec §A01 + Backender §4 | Defer S2 — singleton #47 |
| 18 | EditPracticeView, AttendanceView | MEDIUM | Custom confirm-modal duplicates VModal (3 implementations) | Backender §6+§8 | Defer S2 — singleton #48 |
| 19 | Test surface (api-client / auth-store / router-guards / 6 stores) | MEDIUM | Test coverage gap — 32 tests in 2 files | Code §7+§12 + Backender §7 | Defer S2 — singleton #44 |
| 20 | frontend/package.json | MEDIUM | Major-version updates available: pinia, vue-router, vite, vitest, ts, eslint | Backender §10 | Defer S5+ — singleton #45 (pairs with #54 — same dep-update cycle) |
| 21 | components/ui/VToast.vue | LOW | Hardcoded `box-shadow: 0 4px 12px rgba(0,0,0,0.3)` → `--shadow-md` | Design P5 | Defer S2 — folded into cluster #41 |
| 22 | stores/diary.ts | LOW | LRU comment vs FIFO impl | Code §5 + Backender §5 | Defer S2 — singleton #51 |
| 23 | views/auth/WelcomeView, StandaloneStubView | LOW | Hardcoded fallback `https://t.me/velo_testbot` if env var missing in PROD | Code §4 + Backender §9 | Defer S2 — singleton #49 |
| 24 | views/auth/WelcomeView, StandaloneStubView | LOW | `_blank` 2 sites missing `noreferrer` | Sec ext-link + Backender §9 | Defer S2 — singleton #50 |
| 25 | frontend/src/styles/variables.css | LOW | `--text-secondary` / `--text-muted` sub-AA if used as body text | A11Y P5 | Defer S2 — folded into cluster #40 |
| 26 | frontend/src/styles/global.css | LOW | No global `:focus-visible` style | A11Y P4 | Defer S2 — folded into cluster #40 |
| 27 | App.vue / router | LOW | No focus-on-route-change for screen readers | A11Y P4 | Defer S2 — folded into cluster #40 |
| 28 | components/layout/* | LOW | Two `<nav>` regions need unique `aria-label` | A11Y P7 | Defer S2 — folded into cluster #40 |
| 29 | components/ui/VModal.vue + decisions.md | LOW | Single 640px breakpoint not formally documented | Resp P7 | Defer S2 — singleton #52 |
| 30 | views/master/MasterFinanceView.vue + others | LOW | File-header FIX-ID provenance comments will rot | Code §6 + Backender §6 | Defer per-sprint-close — singleton #53 |

Suppressed (defense-in-depth, accept; not new BACKLOG):
- Sec §Step5 — `/master/practices/:id` no client-side owner check (backend authz is the gate)
- Sec §A07 — auth-failure telemetry (gated on absent Sentry pipeline)
- Sec §Step3.5 — Pinia DevTools prod-build verification
- Code §5 — 9 view files >500 LOC (no functional impact; partly resolved by #43)

Already in BACKLOG (auditors confirmed, not new findings):
#11, #13, #14, #26, #27, #29, #32, #34, #35, #36, #37 — 11 confirmations.

---

## MEDIUM/LOW → BACKLOG

Added entries:
- #40 — S2 a11y polish cluster (14 findings)
- #41 — S2 design-tokens bulk-tighten cluster (5 findings)
- #42 — S2 mobile-polish cluster (3 findings)
- #43 — S2 view-layer extractApiError adoption
- #44 — S2 test-coverage backfill
- #45 — S5+ major-version dependency updates
- #46 — Router timeout silent fallback
- #47 — `roleGuard()` async-await defense-in-depth
- #48 — Confirm-modal unification
- #49 — `VITE_TELEGRAM_BOT_URL` fail-fast in prod
- #50 — `rel="noopener noreferrer"` for `_blank` links
- #51 — diary.ts LRU vs FIFO comment
- #52 — Breakpoint convention doc
- #53 — File-header FIX-ID housekeeping
- #54 — npm audit residual + partial-fix archive

---

## Anchor

[S1-CODE-AUDIT.md | SPEC v3.2-velo]
Sprint 1 code audit consolidated record
Location: docs/01_refer/ARCHIVES/CODE-AUDIT/S1-CODE-AUDIT.md
Sources: ProbeKit lite (6 skills) + backender review pass + Claude Chat classification
Immutable post-commit.
