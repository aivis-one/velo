# SNAPSHOT — Sprint 1: Pilot

> SPEC v3.2-velo
> Date: 2026-04-28
> Status: CLOSED

---

## Summary

S1 reframed Velo's design system around the bundle SSOT (decisions #006–#009): bundle snapshot ported, variables.css migrated to bundle nomenclature (light + dark), 444 token-usage sites renamed, glassmorphism removed (138 backdrop-filter lines). Two pilot screens delivered via deliberately divergent paths — UserDashboardView merged from bundle DashboardScreen with Velo state preserved, WelcomeView fast-tracked as TMA-only splash without Claude Design pipeline (#025). Audit pipeline shakedown ran: ProbeKit lite profile + backender pass produced consolidated S1-CODE-AUDIT.md; CRITICAL npm-audit partial-fix closed all prod-relevant CVEs.

---

## Stats

| Metric | Value |
|--------|-------|
| Phases | 4 (P01–P04) |
| Cycles | 14 (C01–C14, with C03 split + C06b absorbed per #015) |
| Tests | 32 pass, 0 fail, 0 skip |
| Commits | 24 (9cf88fa..HEAD) |
| Files | 163 total (frontend/src/) |
| Lines of Code | 16,061 (frontend/src/, cloc 2.08 — Vue 12,722 + TS 2,905 + CSS 272 + SVG 162) |

---

## Sprint Metrics

| Sprint | Tests | CRITICAL | HIGH | MEDIUM | LOW | LOC (src/) |
|--------|-------|----------|------|--------|-----|------------|
| S1     | 32    | 1        | 3    | 16     | 14  | 16,061     |

Trend notes: First sprint with this protocol — no prior baseline. S2 will populate first delta row.

---

## Completed Phases

| Phase | Name | Cycles | Status |
|-------|------|--------|--------|
| P01 | Bundle Migration | 6 (C01–C06; C03 split; original C06 removed per #015) | DONE |
| P02 | Audit + Backend Coordination | 3 (C07–C09) | DONE |
| P03 | Pilot Port | 3 (C10–C12) | DONE |
| P04 | Manual Test + Retrospective | 2 (C13 deferred per BACKLOG #37; C14 retrospective) | DONE |

---

## Key Decisions

| # | Title | Decision Summary |
|---|-------|-----------------|
| #006 | Bundle = SSOT of design system | Bundle (2026-04-23) supersedes Design_prototype (2026-03-11); pixel-perfect recreation approach |
| #009 | Token rename to bundle namespace | velo-* → bundle namespace; DESIGN_MIGRATION.md v4 SUPERSEDED; 444 substitution sites |
| #013 | VELO = TMA + PWA | Telegram Mini App primary surface; PWA fallback for non-Telegram browsers |
| #022 | API contract patch C06 reduced post-regen | Partner regen pipeline introduced; types auto-generated; Velo-side scope reduced 4→2 fixes |
| #023 | types.ts SSOT reinterpretation; Option 3 broaden | generated.ts is post-regen SSOT for backend shapes; types.ts re-export hub for frontend-only types |
| #025 | C11 WelcomeView fast-track without Claude Design | TMA-only splash; Claude Design pipeline not warranted for static landing |
| #026 | ProbeKit hardened to Velo paths | Sprint-Closer Step 1+ — 9 CBS-HOME hardcoded path fields scrubbed; brand_ref repointed to bundle SSOT |

(21 total new decisions in S1: #006–#026. Full list in `decisions.md`.)

---

## Code Audit Result

| Severity | Found | Resolved | Logged to BACKLOG |
|----------|-------|----------|-------------------|
| CRITICAL | 1 | 1 (partial — 6/11 CVE closed including all prod-relevant; 5 residual reclassified MEDIUM, dev/build-time only) | 1 (#54) |
| HIGH | 3 | 0 | 3 (folded into #40 a11y polish cluster) |
| MEDIUM | 16 | 0 | 16 (across #40–#48, #54) |
| LOW | 14 | 0 | 14 (across #49–#53 + folded into clusters) |

Audit sources: ProbeKit lite profile (6 skills) + backender code review pass + Claude Chat classification. Full record: `docs/01_refer/ARCHIVES/CODE-AUDIT/S1-CODE-AUDIT.md`.

---

## Test Coverage

| Suite | Tests |
|-------|-------|
| composables/usePagination | 9 |
| utils/format | 23 |
| **Total** | **32** |

Coverage gap (test backfill required) tracked in BACKLOG #44 — api/client + stores/auth + router/guards + 5 of 6 composables + 6 of 7 stores untested.

---

## Git Stats

- Commits this sprint: 24
- First commit: 9cf88fa — 2026-04-24 — sprint: S1+S2+S3 — Sprint-Builder planning complete, ready to start S1
- Last commit: 6595aae — 2026-04-28 — audit: CODE-AUDIT-S1 + npm audit partial-fix + BACKLOG #40-54
- Branch: new_desing

---

## What Was Left Out

- **C13 manual visual verification** of pilot screens — deferred post-staging-deploy (BACKLOG #37; gated on partner-coordination pipeline: Velo push → partner code audit → partner deploy → staging exposure).
- **Backend coordination items** (BACKLOG #21 waitlist, #24 partner regen workflow, #26 financial constants, #27 timezone) — gated on backend-partner action; not addressable in-sprint.
- **Admin views (7) + MH-08/11/12 master-side cards** — deferred to S4+ per #010 capacity scope.
- **npm audit residual 5 CVEs** — partial-fix accepted (closed all prod-relevant); `--force` deferred to dep-update cycle (#54 paired with #45 major-version bumps).
- **3 HIGH a11y findings** (`<div @click>` keyboard-inaccessibility, VModal focus-trap, form-label association) — deferred to S2 polish cluster (#40) per Sprint-Closer Step 5 structural-HIGH rule.

---

## Carry-Forward to Next Sprint

- **Pre-S2 Human action**: backend partner regen workflow doc + first fresh regen — unblocks BACKLOG #24/#26/#27.
- **Main-divergence resolution** (BACKLOG #39): partner force-pushed pre-S1 tech-debt refactor to `origin/main`; resolution requires partner rebase or post-merge re-implementation. Do NOT merge main → new_desing under any circumstance until resolved.
- **Top BACKLOG priorities for S2**: #40 a11y polish cluster, #41 design-tokens bulk-tighten, #42 mobile-polish, #43 view-layer extractApiError adoption, #44 test-coverage backfill.
- **Pre-existing S2 plan items**: #18 utility classes migration (already in S2 OPEN), #25 user-ai-summary (S2 C24 per existing plan).
- **Out-of-sprint follow-up**: C13 visual verification (BACKLOG #37) executes once partner-deploy lands.

---

## Framework Lessons

- **Sprint-Builder first-phase scope estimates are unreliable in novel domains.** P01 plan «~577 token-usages, 6 glass tokens» vs reality «633 token-usages, ≈263 glass edits» triggered #015 mid-flight reclassifications. S2+ Sprint-Builder anchors first-phase scope to «TBD by P{NN} OPEN scout», time-boxed not scope-boxed.
- **Phase-Builder Combined Scout proven as calibration point.** Caught all P01 reclassifications BEFORE damage; corrected C10 risk-tier (HIGH→MEDIUM) before execute prompt was written. Routine, not process defect.
- **Phase-bundled commits gave clean git log.** 4 phase-bundled commits (P01–P04) accommodated mid-flight cycle additions without git noise. Cycle-tagged commits (per old ENVIRONMENT.md template) were never used; routed to S1-Clean-Sync (BACKLOG #35).
- **Wall-clock vs effort-hours**: 3–4 weeks calendar plan vs ≈12–14 hours intensive across 2–3 days (~10× faster than typical distributed pace). Useful only if intensive-session mode is steady-state; track session intensity in S2.
- **Prompt-design lessons captured in BACKLOG #10/#17/#33/#34** (token-grep fallback syntax, HIGH-tier prompt step ordering, NEGATIVE keyword-blocklist regex collisions, FP-01 verification regex over-fires) — applied at S2 prompt-design time per S2-SPRINT.md References row.

---

*Snapshot created by: 04_Sprint-Closer protocol*
*Immutable — do not edit after creation*
