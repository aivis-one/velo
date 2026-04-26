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
| C13 | manual-test | Human тестирует Welcome + Dashboard на staging, скриншоты light+dark | TODO | | |
| C14 | standard | Retrospective: real cycle speed, правки S2/S3 в отдельных файлах если нужно | TODO | | |

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
| Phase | 03: Pilot Port — DONE |
| Cycle | C12: pilot verify — DONE |
| Status | Phase 03 complete; ready for Phase 04 (Manual Test + Retrospective) |
| Tests | 32 passed / 0 failed / 0 skipped |

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

---

## Last Session

Phase 03 closed 2026-04-26. Pilot Port delivered as combined execute (Batch Prompt Delivery per Rule 16) covering all 3 cycles in one Claude Code session: (1) C10 — UserDashboardView merged with bundle DashboardScreen visual structure, real-data WeekdayStrip + Stats row from `bookingsStore`, scope-locked NEGATIVE on Contraindications + Recommendations, all existing Velo behavior preserved including timezone tactical cast at `nearestPracticeDate` per BACKLOG #27 (LOC 637 → 741, 12/12 acceptance); (2) C11 — WelcomeView greenfield 123 LOC at `/welcome` route, TMA splash landing per #012/#013, fast-tracked without Claude Design pipeline (decision #025 records explicit deviation от #002 for this single screen — Welcome is simple-by-nature splash; Claude Design pipeline learns on C10 Dashboard merge which is more representative; 10/10 acceptance); (3) C12 — verify gates clean: typecheck 0 errors, test 32 passed, lint 756 warnings (-2 net vs 758 baseline), build green PWA 99 precache entries, dark-block 1, toggle-code 0 per #008, 177 tokens (7/7 acceptance).

Process notes: (a) C10 tier re-classified HIGH→MEDIUM at OPEN §3 Design Review per Rule 15 strict reading (single view-level change, no router/guards/main.ts/global state mutation; sprint-plan tag `affects-global-state` over-classified). (b) C11 fast-track decision recorded explicitly because pipeline learning value of single-CTA splash < cost of Claude Design round-trip; protocol §3 design-gen precondition gate handled correctly. (c) Verification Scout caught 0 BREAK / 0 GAP / 1 NIT (regex over-fire on `#012`/`#013` decision-number references — non-actionable, tracked at BACKLOG #34). (d) Live lesson during C11 execute: NEGATIVE keyword-block AC `grep -ic 'oauth|google|apple' → 0` triggered on Claude Code's own explanatory comment; Claude Code rephrased comment, AC passed — tracked at BACKLOG #33 as future AC-design improvement.

ARCHITECTURE.md §Key Decisions counter advanced #024 → #025; auth views count 3 → 4; new Phase 03 additions block documents WelcomeView.vue + UserDashboardView merge + router /welcome entry.

---

## Next Action

Phase 04: Manual Test + Retrospective (C13 + C14). C13 = Human manual test on staging (Welcome + Dashboard light + dark via DevTools); C14 = retrospective with real cycle speed + S2/S3 adjustments if needed. Run `03_Phase-Builder` OPEN in new chat. C13 is `manual-test` cycle type — primarily Human action with Claude Code only assisting screenshot collection and report drafting if requested.

---

## For Human

**Session Code:** S1-P04-C13
**Load:**
1. Framework: `01_Declaration.md` + `03_Phase-Builder.md`
2. Project: `ENVIRONMENT.md` + `ARCHITECTURE.md` + `decisions.md` + `BACKLOG.md`
3. Sprint: `S1-SPRINT.md` (Phase 04 cycle table for C13 + C14)
**Run:** `03_Phase-Builder` OPEN — Phase 04 (Manual Test + Retrospective, 2 cycles: C13 manual-test on staging cleartext deploy verify Welcome + Dashboard в обеих темах; C14 retrospective с real cycle speed metrics + правки S2/S3 если delta существенный). Phase 04 is the last phase of S1 — sprint-readiness check at CLOSE will route to S1-Sprint-Closer.

---

## Plan vs Reality

| Aspect | Planned | Actual | Delta |
|--------|---------|--------|-------|
| Phases | 4 | — | — |
| Cycles | 14 | — | — |
| Duration | 3–4 weeks | — | — |

### What Worked
(filled at close)

### What Didn't
(filled at close)

### Carry Forward
(filled at close)

---
*S1-SPRINT.md*
*Velo | Sprint 1: Pilot*
