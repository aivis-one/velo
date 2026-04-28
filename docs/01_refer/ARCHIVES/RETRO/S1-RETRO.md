# S1 — Pilot Sprint Retrospective

> Sprint 1: Pilot
> Range: 2026-04-24 (S1 plan commit `9cf88fa`) → 2026-04-26 (P03 close `823bdec`)
> Status: closing pending C13 manual-test results + Phase 04 CLOSE
> Companion docs: `S1-SPRINT.md` (live state), `S1-AUDIT.md` (gap map deliverable), `backend-coord-report.md` (C08 partner handoff)

---

## Summary

S1 reframed Velo's design system around the bundle SSOT (decisions #006–#009), executed full token migration + glass-cleanup (29 active tokens, 444 substitution sites, 138 backdrop-filter lines removed), absorbed a partner-introduced regen pipeline (decision #023), audited the gap map between current codebase / bundle / sponsor MH cards (`S1-AUDIT.md`, 47-row mapping table), and ported the first 2 pilot screens via deliberately different paths (Dashboard merge per #002 with bundle visual structure; Welcome fast-track per #025 without Claude Design pipeline). Sprint goal — «отладить процесс bundle → Vue (infra + 2 pilot экрана) и зафиксировать handoff'ы» — achieved subject to C13 staging verification.

## Goal vs Outcome

Per `S1-SPRINT.md` Success Criteria (8 items):

| # | Criterion | Status |
|---|---|---|
| 1 | Bundle snapshot in `docs/04_assets/velo-design-system-2026-04-23/` + chat1.md removed | ✓ |
| 2 | Fonts / icons / illustrations extracted into `frontend/public/` + `frontend/src/assets/` | ✓ |
| 3 | `frontend/src/styles/variables.css` migrated to bundle nomenclature (light + dark) | ✓ |
| 4 | `ARCHITECTURE.md` + `decisions.md` + `BACKLOG.md` + `DESIGN_MIGRATION.md` archive — DONE | ✓ |
| 5 | `S1-AUDIT.md` built — real vs bundle vs MH gap map | ✓ |
| 6 | 7 missing backend endpoints handed off to Human | ✓ (C08 `backend-coord-report.md`, 143 lines) |
| 7 | 2 pilot screens (Dashboard merge + Welcome greenfield) work on staging | conditional — verified at C13 |
| 8 | Retrospective with real cycle speed and process baselines | ✓ (this document) |

7 of 8 confirmed at RETRO write time. Item 7 verdict written into `S1-SPRINT.md` Phase 04 row at Phase-Builder CLOSE based on C13 manual-test report.

## Plan vs Reality

| Aspect | Planned | Actual | Delta |
|---|---|---|---|
| Phases | 4 | 4 (P01–P04) | 0 |
| Cycles (Protocol Log net) | 14 | 14 (C03 split + C06b absorbed in count) | 0 |
| Phases closed cleanly on first plan | 4 | 3 (P01 required mid-flight replanning per #015) | −1 |
| Commit window | — | 2 days (2026-04-24 → 2026-04-26) | — |
| Calendar work-days | — | 2–3 days | — |
| Sessions count | — | ≈3 | — |
| Avg hours per session | — | ≈4–5 | — |
| Wall-clock hours total | 3–4 weeks initial estimate | ≈12–14 hours | massive overestimate (3–4 weeks at typical pace ≈ 80–160 hrs; actual ≈10× faster) |
| Decisions added | not estimated | 20 (#006–#025) | high — bundle migration is once-per-project event |
| BACKLOG entries added | not estimated | 37 (34 sprint scout/audit + 1 RETRO entry #35 ENVIRONMENT.md cleanup + 2 CLOSE entries #36 staging-deploy doc clarification & #37 post-deploy visual spec) | mostly emerged during scout/audit, not deferred-defects |

The wall-clock surprise is the headline. Initial sprint plan «3–4 weeks» anchored to typical single-dev side-project pace (1–2 hrs/day mixed with other work). Actual execution was 3 intensive Claude Code sessions of ≈4–5 hours each, condensed across 2–3 calendar days. **Implication for S2/S3:** original «3–4 weeks each» duration in S2/S3 plan reflects calendar elapsed-time at distributed mode, not effort-hours; if intensive-session mode continues, S2 and S3 may close in similar 12–20-hour wall-clock budget each. Not a guarantee — depends on session intensity and partner-coord blocker resolution.

## What Worked

**Combined Scout as calibration point.** Phase-Builder OPEN §2 Combined Scout caught all P01 reclassifications BEFORE damage (scope expansion #015, glass scope from «6 tokens» estimate to ≈263 edits actual). Without scout, plan estimates would have committed to wrong scope. Same calibration prevented the C10 HIGH→MEDIUM mistake at OPEN §3 Design Review (Risk tier corrected before execute prompt was written).

**Phase-bundled commits.** Single `phase: P{NN} — DONE` commit per phase (per Phase-Builder CLOSE Step 4f) gave clean git log with one row per delivery, kept WORK chats free of intermediate commit ceremony, and naturally absorbed the C03 split + C06b cycle-additions without commit-history fragmentation.

**Bundle SSOT decision early.** #006 fixed the bundle-vs-Design_prototype tension at S1 start; subsequent #007 (no glass), #008 (dark tokens scope), #009 (token rename) cascaded cleanly without further reframing. Architectural anchor before code-cycles = less in-flight churn.

**Partner regen pipeline absorption.** #022 + #023 turned a partner-introduced `generated.ts` from disruption into a systematic SSOT pattern (Option 3 broaden across 11 files in C06b). Reframing #003 (`types.ts` SSOT) into the post-regen-aware version preserved migration progress without breaking existing `types.ts` callers.

**Process improvements found and BACKLOG'd in real time.** 4 prompt-design lessons captured during execution (BACKLOG #10, #17, #33, #34) — applied at S2 prompt-design rather than discovered next sprint.

## What Didn't

**P01 plan vs P01 reality gap.** Sprint-Builder estimated P01 with `~577 token-usages` and `«6 tokens»` glass scope; actual was 633 token-usages and ≈263 glass edits. Gap caused 5 in-flight reclassifications (#015). Mitigation: Phase-Builder Combined Scout caught it before execute, but post-fact this means Sprint-Builder estimates for first-phase-in-new-domain are fiction. **Lesson for S2 Sprint-Builder:** don't anchor first-phase scope numbers; mark as «TBD by P{NN} OPEN scout» and time-box rather than scope-box.

**Causation framing for P01-storm vs P02/P03-calm.** Two factors compounded in P01: (a) first-phase-in-novel-domain — bundle reality unknown until scout collided with code; (b) code-phase volatility — P01 was code-heavy migration while P02 was audit/doc-heavy and P03 was small-surface code. Phase-Builder OPEN Combined Scout is the calibration point where plan meets reality; replanning at that point is normal. Not a process defect — a frame for sprint-planning expectations.

**Commit convention divergence with `ENVIRONMENT.md`.** S1 used phase-bundled commits exclusively (per Phase-Builder); `ENVIRONMENT.md` §Git Workflow still describes `cycle: C{NN}` cycle-work format that was never used. Doc-vs-practice drift. Routed to S1-Clean-Sync via BACKLOG #35.

**Partner-coordination blockers stalled 4 BACKLOG items.** #21, #24, #26, #27 all gated on regen workflow + partner schema additions. S1 worked around with tactical patches (`UserDashboardView` Berlin-fallback per BACKLOG #27, financial constants frozen per BACKLOG #26) but real fixes deferred. Pattern: external coordination is single-dev's blind spot — needs explicit out-of-chat Human-partner action, not encoded in Claude work cycles.

**Wall-clock estimation off by ≈10×.** 3–4 weeks plan vs ≈12–14 hours actual. Useful for future sprint planning iff intensive-session mode is the intended steady state. If casual/distributed mode resumes, plan numbers re-anchor. Track session intensity for S2.

## Decisions Density Commentary

20 decisions added in S1 (#006–#025), distribution:

| Group | Count | Rows |
|---|---|---|
| Bundle SSOT reframing | 4 | #006–#009 |
| In-flight architectural clarifications | 7 | #015–#021 |
| Partner coordination | 2 | #022, #023 |
| Pilot screen handling (TMA-only flow + icons + fast-track) | 3 | #012, #024, #025 |
| Other (scope / framework profile / phase numbering) | 4 | #010, #011, #013, #014 |

**Prediction for S2:** lower density expected. Bundle SSOT adoption is a one-time event (#006–#009 won't repeat) and Phase 01 first-domain churn is behind. **Caveat:** novel territory may still produce in-flight clarifications similar to #015–#021. Known-novel S2 surfaces: utility classes migration (BACKLOG #18) and dark-mode UI toggle (C19). Anticipated S2 density: 3–7 decisions if no major reframes; 8–15 if utility-classes or dark-mode introduce architectural surprises.

## Process Lessons (applied at S2 prompt-design time)

Pinned in `S2-SPRINT.md` References table; enumerated here for RETRO completeness:

| # | Lesson |
|---|---|
| BACKLOG #10 | Scout grep for token-usage must accept fallback syntax `var(--X[,)]`, not closing-paren only `var(--X)`. C03/C04 found 4 fallback sites missed by closing-paren grep. |
| BACKLOG #17 | HIGH-tier execute prompts with multiple substitution groups must specify explicit Steps order. C03 E1/E2 sequencing bug created transient `--radius-lg` warning sites. |
| BACKLOG #33 | NEGATIVE keyword-blocklist greps in Acceptance Criteria can collide with own explanatory comments. Constrain grep to non-comment lines OR scope to specific syntactic positions OR allow comment-presence with explicit prose rule. |
| BACKLOG #34 | FP-01 verification regex `#[0-9a-fA-F]{3,8}` over-fires on decision-references like `#012`/`#013` (3-digit hex collision). Refine regex or exclude lines matching decision-numbering pattern. |

## Conditional — Pilot Verification (deferred post-S1)

C13 manual visual verification did not run within S1 timeline. Reason: staging visibility for pushed work is gated on an external pipeline that S1 cannot itself complete — Velo push → backend partner code audit → partner deploy → staging exposure → Human visual test. At Phase 04 close, the partner-audit step was the open gate.

Closure handled per Phase-Builder §CLOSE §1 triaged-deferral:

- **C13 outcome at S1 close:** deferred — visual verification scheduled post-partner-deploy as out-of-sprint follow-up. Verification spec preserved at BACKLOG #37 (stand-alone — does not depend on chat artifact).
- **Defects logged:** none yet — C13 not executed. Partner code-audit may surface its own issues; those land in BACKLOG separately when audit returns.
- **Sprint goal final verdict (Velo-side):** ACHIEVED — code-complete, all gates green at Phase 03 close (typecheck 0 errors, test 32/0/0, lint 756 warnings (-2 vs 758 baseline), build green, PWA precache 99 entries). Pilot-screen visual confirmation is the final acceptance step and runs once the external pipeline completes.
- **Success Criterion #7 «работают на staging»:** code-side ready; visual-on-staging confirmation deferred to post-deploy. Doc drift on staging deploy description (ENVIRONMENT.md / ARCHITECTURE.md «auto-pulls» wording vs partner-gated workflow) logged at BACKLOG #36 for S1-Clean-Sync.

This is consistent with the partner-gated deploy flow: Velo side delivers code; partner audits; partner deploys; visual verification follows. The «works on staging» phrasing in Success Criteria assumed in-sprint visual reachability, which the actual workflow does not provide. Velo-side delivery is complete; downstream verification is post-S1.

## Anchor

```
[S1-RETRO.md | SPEC v3.2-velo]
Sprint 1 retrospective — pilot
Location: docs/01_refer/ARCHIVES/RETRO/S1-RETRO.md
Closes Phase 04, final phase of S1.
Companion: S1-SPRINT.md (live state during sprint), S1-AUDIT.md (gap map deliverable).
```
