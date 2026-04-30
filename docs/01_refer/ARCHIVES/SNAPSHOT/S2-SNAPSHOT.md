# SNAPSHOT — Sprint 2: User Foundation + Booking Flow

> SPEC v3.2-velo
> Date: 2026-04-30
> Status: CLOSED

---

## Summary

S2 ported the new designer batch (2026-04-30) for the user role's foundation: regen pipeline (Phase 05) closed three carry-forward backend coordination items, then Phases 06-09 delivered auth/onboarding (Welcome two-branch + Login + Register + OAuthLoading + Onboarding carousel + Onboarding timezone), Dashboard + Calendar + theme infrastructure, full booking flow (Practice detail + BookingSuccess + BookedPractice + BookingDetail + Checkin + PracticeLive + Feedback + their success splashes), and Profile foundation (UserProfile + EditProfile). 21 cycles (C15-C35) across 5 phases. Phase 06 ratified Path Y (decision #047) — logic-first build at MEDIUM visual fidelity with polish deferred to S5+. Phases 07-09 executed in single MEGA-1 mega-execute prompt (commit `6c5fd1f`) per speedrun mode (decision #049).

---

## Stats

| Metric | Value |
|--------|-------|
| Phases | 5 (P05–P09) |
| Cycles | 21 (C15–C35) |
| Tests | 32 pass, 0 fail, 0 skip |
| Commits | 17 (4029343..6c5fd1f) |
| Files | 168 total (frontend/src/, post-MEGA-1 commit `6c5fd1f`) |
| Lines of Code | 20,157 (frontend/src/, cloc 2.08 — Vue 16,519 + TS 3,084 + CSS 272 + SVG 162 + JSON 120) |

---

## Sprint Metrics
> Cumulative tracking across sprints. Copy rows from previous SNAPSHOT
> and add current sprint row.

| Sprint | Tests | CRITICAL | HIGH | MEDIUM | LOW | LOC (src/) |
|--------|-------|----------|------|--------|-----|------------|
| S1 | 32 | 1 | 3 | 16 | 14 | 16,061 |
| S2 | 32 | — | — | — | — | 20,157 |

Trend notes: Test count flat at 32 (BACKLOG #44 deferred per #042 inverted in speedrun #049 — no new tests added). LOC grew by 4,096 (+25.5%) on +28 files (Vue +27 + JSON +1 — auth flow + booking flow + dashboard/calendar/profile refresh + onboarding). Severity rows blank — Code Audit deferred to BACKLOG #100 per decision #049.

---

## Completed Phases

| Phase | Name | Cycles | Status |
|-------|------|--------|--------|
| P05 | Regen pipeline + consumer migration | 1 (C15) | DONE |
| P06 | Auth + onboarding | 6 (C16–C21) | DONE |
| P07 | Dashboard + calendar + theme | 4 (C22–C25 — bundled in MEGA-1) | DONE |
| P08 | Booking flow (Practice → Live → Feedback) | 9 (C26–C32 + supporting cycles, MEGA-1) | DONE |
| P09 | Profile foundation | 3 (C33–C35 — bundled in MEGA-1; C35 = visual verify) | DONE |

---

## Key Decisions

| # | Title | Decision Summary |
|---|-------|-----------------|
| #027 | Self-deploy from S2 | Frontend deploys independently via paramiko + `velo update`; partner-joint deploys retired post-S1 |
| #028 | Hybrid auth γ (TMA + PWA) | Welcome splits into platform-aware branches; PWA email/OAuth UI built but auth backend deferred to BACKEND § A.1 |
| #029 | Bundle tokens 80% retained over new designer batch | Tokens (colors / typography / surfaces) preserve from bundle SSOT; new batch is visual-layer-only |
| #030 | Designer batch 2 = primary visual SSOT for S2/S3 | `docs/04_assets/velo-design-system-2026-04-30/` supersedes bundle visuals where conflict |
| #031 | Generated.ts regen path = partner-signal-driven (preferred) | Regen happens when partner pushes Pydantic changes + signal; #046 fallback for stalls |
| #032 | Diary layout toggle = single view + state | Timeline ↔ list = layout state, not separate routes; localStorage persist |
| #033 | Diary entry type via frontend filter chip + backend extension queued | `e.type` placeholder until BACKEND § B.1 lands |
| #034 | Onboarding completion persistence — localStorage v1 | `velo:onboarding_completed` flag; cross-device parity deferred |
| #035 | Mid-practice "Check-in" = upsert (re-open form 12) | No new endpoint; existing `POST /practices/{id}/checkin` is upsert |
| #036 | WelcomeView splits into TMA-splash + PWA-standalone branches | Single SFC with `platform.name === 'telegram'` discriminator |
| #037 | Practice Live "Войти" = external Zoom link (window.open) | No embedded Zoom SDK |
| #038 | Avatar read-only — Telegram-managed | Backend openapi excludes avatar from UserUpdate |
| #039 | Topup flow remains S1-as-is in S2 | Designer didn't ship topup screens in 2026-04-30 batch |
| #040 | Booking endpoint defaults to /purchase for all practices | Unification per backend; partner confirmation pending |
| #041 | Coordination doc format established | BACKEND-COORDINATION.md (partner) + DESIGN-DECISIONS-LOG.md (designer/PM/sponsor) as continuously-updated SSOTs |
| #042 | Sprint scope discipline: quality > density | S2/S3 split user role across two sprints; per-cycle staging push rhythm |
| #043 | Human-only-relay execution model | Human never executes commands directly; Claude Code + Claude Chat collaboration via Human relay |
| #044 | paramiko as primary SSH primitive for Claude Code | ssh.exe sandboxed on Windows; paramiko sandbox-friendly + reads OpenSSH keys natively |
| #045 | SSH key auth as standard for staging access | ed25519 keypair; password retired to emergency-fallback role |
| #046 | Self-host backend dev stack for openapi regen when partner stalls | Fallback to #031 — frontend-side `docker compose up postgres redis app` + dump openapi |
| #047 | Path Y — logic-first build mass; visual polish deferred to S5+ | First applied S2-P06-C16; inherited by speedrun MEGA-1/2 |
| #048 | No-emoji rule + icon-component discipline | Bare emoji replaced with inline SVG icon components; first applied speedrun MEGA-1 |
| #049 | Speedrun mode — explicit inversion of #042 for sponsor-demo target | 33 cycles in 2 mega-execute prompts; audit ceremony deferred to BACKLOG #100 |

---

## Code Audit Result

| Severity | Found | Resolved | Logged to BACKLOG |
|----------|-------|----------|-------------------|
| CRITICAL | N/A — deferred per BACKLOG #100 | — | — |
| HIGH | N/A — deferred per BACKLOG #100 | — | — |
| MEDIUM | N/A — deferred per BACKLOG #100 | — | — |
| LOW | N/A — deferred per BACKLOG #100 | — | — |

Sprint-Closer Step 1+ ProbeKit lite audit profile NOT run at S2 close per decision #049 (speedrun mode). Reactivation tracked as BACKLOG #100; gates production promotion.

---

## Test Coverage

| Suite | Tests |
|-------|-------|
| `src/utils/format.test.ts` | 23 |
| `src/composables/usePagination.test.ts` | 9 |
| **Total** | **32** |

No new test files added in S2 (BACKLOG #44 deferred per #042 inverted in speedrun #049).

---

## Git Stats

- Commits this sprint: 17
- First commit: `5b97b59` — 2026-04-28 — `docs: rename 02_spec_assets→04_assets + move 3 legacy folders to 05_legacy/`
- Last commit: `6c5fd1f` — 2026-04-30 — `phase: S2 P07/P08/P09 — DONE — speedrun (S2 closed)`
- Branch: `new_desing`

Notable commits:
- `5b97b59` — 02_spec_assets → 04_assets rename + legacy relocation
- `680db36` — S1 Clean-Sync data hygiene
- `79b5b9d` — Sprint-Builder re-plan after design batch
- `325ebcc` — ENVIRONMENT.md test infrastructure record
- `632ff2b` — Human-only-relay execution model (decision #043)
- `cc659ea` — SSH infrastructure (decisions #044 #045) + Rule 28 Server Action Plan
- `b6bcabf` — ProbeKit cross-skill velo-presets + lite mode
- `68fa5cd` — Self-host openapi regen (decision #046 first application)
- `ad4ce7d` — Phase 05 close
- `64c94c8` — Phase 05 visual verify backfill (ALL CLEAN)
- `6af88f3` — Rule 29 persist-or-lose discipline
- `26efb8d` — Designer batch 2026-04-30 commit (BACKLOG #92 first application of Rule 29)
- `cc4e2fd` — C16 WelcomeView two-branch + App.vue gate (Phase 06 start)
- `b060ba3` — C17/C18/C19 Login + Register + OAuth (mock per BACKEND § A.1/A.2)
- `de496f6` — C20/C21 OnboardingCarousel + OnboardingTimezone (PWA mock)
- `0b03f6a` — Phase 06 close
- `6c5fd1f` — MEGA-1: Phase 07/08/09 (S2 closed; speedrun)

---

## What Was Left Out

- **Code Audit** — Sprint-Closer Step 1+ ProbeKit lite profile NOT run; deferred to BACKLOG #100 per decision #049 (speedrun mode).
- **New tests** — BACKLOG #44 deferred; speedrun discipline #049 explicitly waives quality-density inversion.
- **Master role refresh** — out of scope for S2 (decision #042 split user vs master across S2/S3 vs S4).
- **Admin role refresh** — out of scope (S5+).
- **Topup flow refresh** — designer didn't include in batch (decision #039); S1 implementation retained.
- **Backend coordination items** — 23 mock-pending entries in BACKEND-COORDINATION.md § A/B/C remain unwired (auth, support form, messaging endpoints, AI summary content endpoint, master public stats, leave endpoint, language/i18n switch).

---

## Carry-Forward to Next Sprint

S3 carry (already executed; close 2026-04-30):
- Phase 10-13 user role content (Diary refresh + Messages + AI summary + Profile sub-views + Master public + Reservations).

Production promotion gates (S5+):
- BACKLOG #100 — Post-demo audit cycle reactivation (CRITICAL gate before production promotion).
- BACKLOG #97 — Backend `POST /bookings/{id}/leave` endpoint.
- BACKLOG #99 — Backend public master endpoint + MasterPublicResponse fields.
- BACKLOG #98 — RESOLVED at MEGA-2 close (emoji audit 0 hits in scope).
- BACKLOG #96 — `velo update` transient (hypothesis CONFIRMED 4/4 deploys ≥600 LOC).

S4+ scope:
- Master role refresh (per decision #042 + #010).
- Admin role refresh (S5+).
- Pixel polish cluster (per decision #047).

---

## Framework Lessons

- **Speedrun mode (decision #049) proven viable for sponsor-demo target.** Single MEGA-execute prompt produces single commit covering 14 cycles (Phase 07/08/09 in MEGA-1) without per-cycle Claude Design pipeline. Trade-off: audit + retro rigor + pixel polish deferred to BACKLOG #100. Throughput multiplier vs S1 baseline: ~5× cycles per closure commit.
- **Hybrid visual verify policy (3-tier A/B/C) cost-effective at scale.** All 3 deploy gates closed A clean (C15 regen, MEGA-1, MEGA-2). No B/C reply paths exercised — speedrun delivers acceptable visual fidelity at first attempt when scope is well-defined per skin reference.
- **BACKLOG #96 size-correlation hypothesis CONFIRMED.** 4/4 deploys ≥600 LOC fire transient; 1/1 small deploy clean. Mechanism: timing race in `velo update` script's pre-fetch `git status` check during build window of prior deploy. Frontend-side workaround (paramiko retry on transient) confirmed working but masks root cause; server-side fix candidate logged.
- **Rule 28 Server Action Plan + Rule 29 persist-or-lose** proven essential at speedrun pace. STOP-on-modify gates prevent runaway destructive operations; persist-or-lose discipline ensures designer batch artifacts in repo before reference.
- **paramiko + ed25519 SSH stack (decisions #044 + #045) proven** across 4 deploys including BACKLOG #96 retry recovery. Output stream buffering on Windows Bash bridge documented as known quirk (single occurrence; not blocking).
- **PRACTICE_TYPE_EMOJI → PRACTICE_TYPE_ICON refactor pattern** established in MEGA-1; applied with backwards-compat empty-string shims for legacy callers (master/admin views S4/S5+ cleanup). Pattern documented for future displayHelpers cleanups.

---

*Snapshot created by: 04_Sprint-Closer protocol (speedrun-deferred audit)*
*Immutable — do not edit after creation*
