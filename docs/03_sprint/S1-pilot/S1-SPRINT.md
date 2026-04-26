# SPRINT
> Velo | Sprint 1: Pilot
> Load this file + docs/02_spec/01_Declaration.md + docs/01_refer/ENVIRONMENT.md
> at the start of every working chat.

---

## SPEC
| File | Path |
|------|------|
| Declaration | docs/02_spec/01_Declaration.md |
| Protocols | docs/02_spec/ |

---

## Environment
> See: docs/01_refer/ENVIRONMENT.md
> Override below ONLY if this sprint differs from project defaults.

---

## References

| Doc | Path |
|-----|------|
| ARCHITECTURE | docs/01_refer/ARCHITECTURE.md |
| ENVIRONMENT | docs/01_refer/ENVIRONMENT.md |
| FILE-TREE | docs/01_refer/FILE-TREE.md |
| BACKLOG | docs/01_refer/BACKLOG.md |
| DECISIONS | docs/01_refer/decisions.md |
| BUNDLE SNAPSHOT | docs/02_spec_assets/velo-design-system-2026-04-23/ (created in C01) |
| AUDIT | docs/01_refer/AUDIT-S1.md (created in C07) |
| RETRO-S1 | docs/03_sprint/S1-pilot/S1-RETRO.md (created in C14) |

---

## Goal
Отладить процесс bundle → Vue (infra + 2 pilot экрана) и зафиксировать все рабочие handoff'ы.

## Success Criteria
- Bundle snapshot в docs/02_spec_assets/velo-design-system-2026-04-23/ + chat1.md удалён
- Fonts / icons / illustrations извлечены в frontend/public/ и frontend/src/assets/
- frontend/src/styles/variables.css мигрирован под bundle nomenclature (light + dark)
- ARCHITECTURE.md + decisions.md + BACKLOG.md + DESIGN_MIGRATION.md archive DONE
- AUDIT-S1.md построен — покажет реальное vs bundle vs MH
- Список 7 missing backend endpoints передан Human для партнёра
- 2 pilot экрана (DashboardScreen merge + WelcomeScreen greenfield) реализованы в Vue, работают на staging
- Retrospective зафиксировал реальную скорость port-cycle и baselines процесса

## Out of Scope
- Любые экраны кроме Dashboard + Welcome
- Любая master-работа
- User-greenfield экраны (MH-03/09/10/13)
- Install velo-design Claude Skill (BACKLOG)
- Admin views (BACKLOG)
- Dark mode UI toggle implementation (только tokens в S1, UI toggle в C19)

---

## Phases

### Phase 01: Bundle Migration (6 cycles)
**Goal:** Bundle tokens + assets в репо, Vue-код переименован под bundle namespace, shadows восстановлены, docs обновлены.
**Entry:** Bundle снапшот в /tmp/velo-bundle/; scout выполнен.
**Exit:** `npm run build` проходит; 577 usages `--velo-*` переименованы; glass-tokens удалены; ARCHITECTURE.md + decisions.md + BACKLOG.md обновлены; DESIGN_MIGRATION.md в docs/_archive/.

**Cycles:**

| Cycle | Type | Name | Status | Date | Result |
|-------|------|------|--------|------|--------|
| C01 | standard | Bundle snapshot + assets extract + legacy rename + 5 doc refs | DONE | 2026-04-24 | Bundle snapshot (~140 files) + 24 frontend assets + Marmelad font + 85 renames + 5 doc refs. 15/15 acceptance. |
| C02 | standard | variables.css bundle SSOT port (light + dark) | DONE | 2026-04-24 | @font-face + 101 bundle + 32 dark + 86 legacy. Total 177 custom properties. 11/11 acceptance. |
| C03 | standard | Grep/replace velo-* → bundle namespace (HIGH affects-global-state) | DONE | 2026-04-24 | 29 active tokens, 444 sites + radius opportunistic + displayHelpers + Legacy cleanup. 67 files; 513 substitutions. 17/17 acceptance. |
| C04 | standard | Glass-tokens cleanup + backdrop-filter removal (HIGH affects-global-state) | DONE | 2026-04-24 | 117 renames + 2 drops + 138 backdrop-filter lines + 5 alpha tokens. 15/15 acceptance. |
| ~~C06~~ original | — | (Pre-empted) | REMOVED | — | Removed per decision #015 — Sprint-Builder commit `9cf88fa` pre-empted decision/BACKLOG/archive work. |
| C05 | standard+manual | Shadows audit + deploy-prelude + staging push | DONE | 2026-04-24 | Deploy-prelude commit `364893d` push; staging visual verify suspended pending partner audit feedback. |
| C06 | standard | API contract patch (B.3 + B.11; B.1 no-op; A.2 deferred) | DONE | 2026-04-26 | 2 files. B.3 dead trigger removed (strict scope); B.11 dev warning at client.ts. B.1 verified-already-fixed by partner regen. A.2 deferred (regen blocker — BACKLOG #26). |
| C06b | standard | Post-regen consumer migration (38 typecheck errors → 0) | DONE | 2026-04-26 | 11 files. Option 3 broaden + tactical patches. Class A+B 17, C 16, D 2, E 1, F 1 (tactical-include for Zodd CRITICAL #1 timezone — BACKLOG #27), G 1. Final gates green. |

### Phase 02: Audit + Backend Coordination (3 cycles)
**Goal:** План S2/S3 основан на данных; backend-coord список готов; icons collision разрешена.
**Entry:** Phase 01 DONE.
**Exit:** AUDIT-S1.md содержит финальные verdict'ы; 7 missing endpoints передано Human; 14 Vue-SVG + 12 PNG bundle collision разрешена per decision D3.

**Cycles:**

| Cycle | Type | Name | Status | Date | Result |
|-------|------|------|--------|------|--------|
| C07 | scout | AUDIT-S1.md — gap map (база scout §2) + финальные verdict'ы | DONE | 2026-04-26 | docs/01_refer/AUDIT-S1.md created (278 lines, 10 sections, 47-row mapping table, 18 MH-card rows, theme + auth state). Consumes by S2 P05/P06 + S3 P09/P10/P11. |
| C08 | standard | Backend-coord report: 7 missing endpoints + формат для партнёра | DONE | 2026-04-26 | docs/03_sprint/S1-pilot/backend-coord-report.md (143 lines): 7 partner-owed feature groups + 2 frontend-wrapper-only + 2 new partner schema asks + 2 regen-trigger asks. |
| C09 | standard | Icons audit per D3: Vue-SVG baseline + bundle PNG дополнение | DONE | 2026-04-26 | D3 ratified as decision #024. AUDIT-S1.md §9 + 4 BACKLOG entries (#29-#32). BACKLOG #19 (D3 BLOCKING) RESOLVED. |

### Phase 03: Pilot Port (3 cycles)
**Goal:** 2 pilot экрана работают на staging, dark tokens применены.
**Entry:** Phase 02 DONE.
**Exit:** DashboardScreen ported в UserDashboardView.vue (merge bundle visual + preserve logic); WelcomeView.vue новый + route `/welcome`; оба в dark+light (через DevTools [data-theme]); `npm run typecheck && lint && test` passes.

**Dependency on Human:** до C11 Human присылает handoff из Claude Design (Telegram-only Welcome, TMA-aware).

**Cycles:**

| Cycle | Type | Name | Status | Date | Result |
|-------|------|------|--------|------|--------|
| C10 | standard | Port DashboardScreen → UserDashboardView.vue (637 → 741 LOC merge) | DONE | 2026-04-26 | Bundle DashboardScreen merged: WeekdayStrip + Stats row from real bookingsStore data; Contraindications + Recommendations skipped per scope-lock; existing alerts/AI-card/timezone-cast preserved. 12/12 acceptance. Tier MEDIUM (re-classified from sprint-plan HIGH per Rule 15 strict reading). |
| C11 | standard | Welcome greenfield → new WelcomeView.vue + route `/welcome` (fast-track, NOT design-gen) | DONE | 2026-04-26 | TMA splash 123 LOC; mandala + VELΘ wordmark + tagline + single CTA. Decision #025 records explicit deviation от #002 для одного экрана. 10/10 acceptance. |
| C12 | standard | Pilot verify: typecheck + lint + test + build + theme NEGATIVE | DONE | 2026-04-26 | typecheck 0 errors; test 32 passed; lint -2 net (756 vs 758 baseline); build green PWA 99 precache; dark-block 1; toggle-code 0 (per #008 — UI toggle deferred to S2 C19); 177 tokens preserved. 7/7 acceptance. |

### Phase 04: Manual Test + Retrospective (2 cycles)
**Goal:** Human протестировал на staging; retrospective показал реальную скорость; S2/S3 скорректированы если нужно.
**Entry:** Phase 03 DONE.
**Exit:** Manual test report от Human (скриншоты обе темы); docs/03_sprint/S1-pilot/S1-RETRO.md создан; S2-SPRINT.md + S3-SPRINT.md обновлены если скорость отличается.

**Cycles:**

| Cycle | Type | Name | Status | Date | Result |
|-------|------|------|--------|------|--------|
| C13 | manual-test | Human тестирует Welcome + Dashboard на staging, скриншоты light+dark | DEFERRED | 2026-04-26 | Visual verification gated on external pipeline (Velo push → partner code audit → partner deploy → staging). Verification spec preserved at BACKLOG #37 (stand-alone). Will execute post-deploy as out-of-sprint follow-up. Triaged-deferral close per Phase-Builder §CLOSE §1. |
| C14 | standard | Retrospective: real cycle speed, правки S2/S3 в отдельных файлах если нужно | DONE | 2026-04-26 | S1-RETRO.md created (full retrospective: Summary + Goal vs Outcome + Plan vs Reality + What Worked + What Didn't + Carry Forward + Decisions Density + Process Lessons + Conditional + Anchor). S2-SPRINT.md updated (1 References row + 3 Carry-Forward items per H1 minimal). BACKLOG #35 appended (ENVIRONMENT.md commit-convention cleanup → S1-Clean-Sync). All AC pass. |

---

## Carry-Forward from S0
- (install complete; no carry-forward)

## Key Decisions
- #006: Bundle (2026-04-23) = SSOT
- #007: Flat эстетика, no backdrop-filter
- #008: Dark mode — tokens in S1, UI audit deferred
- #009: Token rename, DESIGN_MIGRATION.md v4 SUPERSEDED
- #010: Admin views + MH-08/11/12 → BACKLOG
- #011: 3 sprints planned together (отклонение от Sprint-Builder v3.2-velo)
- #012: TMA-only auth, bundle AuthScreen не 1:1
- #013: VELO = TMA with PWA fallback
- #014: Phases numbered globally (P01–P12)

---

## Sprint Context

| Sprint | Status |
|--------|--------|
| S0 install | DONE |
| S1 pilot | IN PROGRESS |
| S2 bundle-port | NOT STARTED |
| S3 greenfield | NOT STARTED |

---

## Current State

| Item | Value |
|------|-------|
| Phase | 04: Manual Test + Retrospective — DONE (triaged-deferral §CLOSE §1) |
| Cycle | C14: retrospective — DONE; C13: visual verification deferred (external pipeline gate) |
| Status | Phase 04 closed; S1 Velo-side code-complete; ready for S1-Sprint-Closer |
| Tests | 32 passed / 0 failed / 0 skipped (Phase 03 baseline preserved through P04 — doc-only phase, no code changes) |

---

## Protocol Log

| Cycle      | Protocol              | Date         | Status |
|------------|-----------------------|--------------|--------|
| S1-Sprint-Builder | 02_Sprint-Builder | 2026-04-24 | DONE |
| S1-P01-C01 | 03_Phase-Builder | 2026-04-24 | DONE |
| S1-P01-C02 | 03_Phase-Builder | 2026-04-24 | DONE |
| S1-P01-C03-Assess | 03_Phase-Builder | 2026-04-24 | DONE |
| S1-P01-C03-Apply | 03_Phase-Builder | 2026-04-24 | DONE |
| S1-P01-C04 | 03_Phase-Builder | 2026-04-24 | DONE |
| S1-P01-C05 | 03_Phase-Builder | 2026-04-24 | DONE |
| S1-P01-C06 | 03_Phase-Builder | 2026-04-26 | DONE |
| S1-P01-C06b | 03_Phase-Builder | 2026-04-26 | DONE |
| S1-P01-CLOSE | 03_Phase-Builder | 2026-04-26 | DONE |
| S1-P02-C07 | 03_Phase-Builder | 2026-04-26 | DONE |
| S1-P02-C08 | 03_Phase-Builder | 2026-04-26 | DONE |
| S1-P02-C09 | 03_Phase-Builder | 2026-04-26 | DONE |
| S1-P02-CLOSE | 03_Phase-Builder | 2026-04-26 | DONE |
| S1-P03-C10 | 03_Phase-Builder | 2026-04-26 | DONE |
| S1-P03-C11 | 03_Phase-Builder | 2026-04-26 | DONE |
| S1-P03-C12 | 03_Phase-Builder | 2026-04-26 | DONE |
| S1-P03-CLOSE | 03_Phase-Builder | 2026-04-26 | DONE |
| S1-P04-C14 | 03_Phase-Builder | 2026-04-26 | DONE |
| S1-P04-C13 | 03_Phase-Builder | 2026-04-26 | DEFERRED |
| S1-P04-CLOSE | 03_Phase-Builder | 2026-04-26 | DONE |

---

## Last Session

Phase 04 closed 2026-04-26 via triaged-deferral per Phase-Builder §CLOSE §1. Two cycles planned (C13 manual-test + C14 retrospective); C14 delivered in full, C13 deferred to post-deploy as out-of-sprint follow-up.

C14 (DONE): produced `S1-RETRO.md` (Summary + Goal vs Outcome + Plan vs Reality + What Worked + What Didn't + Carry Forward + Decisions Density + Process Lessons + Conditional + Anchor). Updated `S2-SPRINT.md` with one References row pointing to BACKLOG #10/#17/#33/#34 (process-discipline lessons applied at S2 prompt-design time) and three Carry-Forward items: pre-S2 Human-partner action on regen workflow doc + first fresh regen (resolves BACKLOG #24, unblocks #26 + #27), process-discipline lessons summary, S1-Clean-Sync batch identifier (#29/#31/#35/#36 + AUDIT-S1.md §10 #5). Appended BACKLOG #35 (ENVIRONMENT.md commit-convention cleanup → S1-Clean-Sync; cite: S1 used phase-bundled commits exclusively per Phase-Builder CLOSE Step 4f, ENVIRONMENT.md `cycle: C{NN}` formats unused).

C13 (DEFERRED): manual visual verification of WelcomeView (`/welcome`) + UserDashboardView (`/user/dashboard`) in light + dark themes on staging. Did not execute because the staging visibility chain includes a backend-partner code-audit gate before deploy — the gate was open at S1 close. Verification spec preserved at BACKLOG #37 (stand-alone; does not depend on chat artifact). Triaged-deferral conditions: (a) goal scope clarified (visual-on-staging requires external pipeline; not Velo-side blocker), (b) BACKLOG #37 persists deferred task, (c) S1-RETRO.md §Conditional documents the deferral, (d) commit cites §CLOSE §1 deviation.

Sprint goal Velo-side ACHIEVED: bundle → Vue process debugged (P01 token migration + glass cleanup), 2 pilot screens implemented (Dashboard merged with bundle visual structure per #002, Welcome fast-tracked per #025), handoffs captured (`AUDIT-S1.md` 47-row gap map, `backend-coord-report.md` 7 missing endpoints). 7 of 8 Success Criteria fully met; #7 («работают на staging») code-side ready, post-deploy visual confirmation pending.

Phase 04 also surfaced two doc-drift findings persisted as BACKLOG entries: #36 staging deploy flow doc clarification (ENVIRONMENT.md / ARCHITECTURE.md «auto-pulls» wording underspecifies the partner-audit gate), #37 post-deploy visual verification spec for the deferred C13 work. Both flagged S1-Clean-Sync / post-S1.

Process notes for retro context (already captured in S1-RETRO.md §What Worked / §What Didn't): Combined Scout consistently caught scope-discovery issues before damage; phase-bundled commits worked cleanly; partner regen pipeline absorbed without disruption (#022 + #023); wall-clock ≈12-14 hrs across 3 sessions vs 3-4 weeks planned (≈10× faster than plan).

---

## Next Action

Phase 04 closed. S1 Velo-side code-complete. Run `04_Sprint-Closer` in new chat (Session Code: `S1-Sprint-Closer`). Sprint-Closer handles: ProbeKit lite profile (type-audit, code-audit, a11y-audit, responsive-audit, security-audit, design-audit) + SNAPSHOT (cloc LOC count, cycle metrics from Protocol Log, decisions/BACKLOG counts) + sprint close. After Sprint-Closer: `S1-Clean-Sync` (FILE-TREE refresh + BACKLOG #29/#31/#35/#36 + AUDIT-S1.md §10 #5 cleanups), then `S2-Sprint-Builder` (S2 plan already drafted in `S2-SPRINT.md`, may need refinement based on Sprint-Closer findings + post-deploy C13 outcome if available by then).

Out-of-chat parallel: backend partner code audit on Phase 03 push (`origin/new_desing` HEAD `823bdec`) → partner deploy → C13 visual verification per BACKLOG #37 spec.

---

## For Human

**Session Code:** S1-Sprint-Closer
**Load:**
1. Framework: `01_Declaration.md` + `04_Sprint-Closer.md`
2. Project: `ENVIRONMENT.md` + `ARCHITECTURE.md` + `decisions.md` + `BACKLOG.md`
3. Sprint: `S1-SPRINT.md` + `S1-RETRO.md`
**Run:** `04_Sprint-Closer` — Part 1 (ProbeKit lite profile code audit) + Part 2 (SNAPSHOT — cloc LOC count, cycle metrics, decisions/BACKLOG counts, sprint close prose).

**Out-of-chat parallel action:** backend partner code audit on `origin/new_desing` HEAD `823bdec` → partner deploy → C13 post-deploy visual verification per BACKLOG #37 stand-alone spec. Visual outcome can fold into S2 Carry-Forward at S2-Sprint-Builder time, or open new BACKLOG entry if defects.

---

## Plan vs Reality

| Aspect | Planned | Actual | Delta |
|--------|---------|--------|-------|
| Phases | 4 | 4 (P01–P04 all closed) | 0 |
| Cycles | 14 | 14 net (13 DONE — C01..C12, C06b — + 1 DEFERRED — C13 visual; C03 split absorbed in count) | 0 |
| Duration (commit-window) | 3–4 weeks | 2 days (2026-04-24 → 2026-04-26) | massive overestimate |
| Duration (calendar work-days) | — | 2–3 days | — |
| Duration (sessions) | — | ≈3 intensive Claude Code sessions | — |
| Duration (wall-clock hours) | — | ≈12–14 hours total (≈4–5 hrs avg per session) | ≈10× faster than plan |
| Decisions added | not estimated | 20 (#006–#025) | bundle migration once-per-project |
| BACKLOG entries added | not estimated | 37 (34 sprint scout/audit + 1 RETRO #35 + 2 CLOSE #36/#37) | mostly emerged during scout/audit, not deferred-defects |

### What Worked

See `docs/03_sprint/S1-pilot/S1-RETRO.md` §What Worked. Headline items: Combined Scout as calibration point (caught all P01 reclassifications + C10 tier mistake before damage); phase-bundled commits; bundle SSOT decision early (#006); partner regen pipeline absorption (#022, #023); process improvements found and BACKLOG'd in real time.

### What Didn't

See `S1-RETRO.md` §What Didn't. Headline items: P01 plan vs reality scope gap (Sprint-Builder estimates for first-phase-in-new-domain are fiction); commit convention divergence with `ENVIRONMENT.md`; partner-coordination blockers stalled 4 BACKLOG items; wall-clock estimation off by ≈10×; staging deploy flow doc drift surfaced at P04 close (BACKLOG #36).

### Carry Forward

See `S1-RETRO.md` §Carry Forward. To S2 plan (already applied in `S2-SPRINT.md` by C14): References row + Carry-Forward items including pre-S2 Human-partner action. To S1-Clean-Sync (between Sprint-Closer and S2-Sprint-Builder): BACKLOG #29 + #31 + #35 + #36 + AUDIT-S1.md §10 #5. Plain BACKLOG carry-forward: #18 + #25 + #21 + #30. Out-of-sprint: #37 post-deploy visual verification.

---
*S1-SPRINT.md*
*Velo | Sprint 1: Pilot*
