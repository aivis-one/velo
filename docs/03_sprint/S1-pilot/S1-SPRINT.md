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
| C07 | scout | AUDIT-S1.md — gap map (база scout §2) + финальные verdict'ы | TODO | | |
| C08 | standard | Backend-coord report: 7 missing endpoints + формат для партнёра | TODO | | |
| C09 | standard | Icons audit per D3: Vue-SVG baseline + bundle PNG дополнение | TODO | | |

### Phase 03: Pilot Port (3 cycles)
**Goal:** 2 pilot экрана работают на staging, dark tokens применены.
**Entry:** Phase 02 DONE.
**Exit:** DashboardScreen ported в UserDashboardView.vue (merge bundle visual + preserve logic); WelcomeView.vue новый + route `/welcome`; оба в dark+light (через DevTools [data-theme]); `npm run typecheck && lint && test` passes.

**Dependency on Human:** до C11 Human присылает handoff из Claude Design (Telegram-only Welcome, TMA-aware).

**Cycles:**

| Cycle | Type | Name | Status | Date | Result |
|-------|------|------|--------|------|--------|
| C10 | standard | Port DashboardScreen → UserDashboardView.vue (668 lines merge, HIGH complexity) | TODO | | |
| C11 | standard | Welcome greenfield → new WelcomeView.vue + route `/welcome` (from Claude Design handoff, NOT from bundle AuthScreen) | TODO | | |
| C12 | standard | Pilot verify: dark/light tokens, typecheck + lint + test | TODO | | |

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
| Phase | 01: Bundle Migration — DONE |
| Cycle | C06b: post-regen consumer migration — DONE |
| Status | Ready for Phase 02 (Audit + Backend Coordination) |
| Tests | typecheck 0 errors · lint 758 warnings (delta 0) · build ✓ 1.36s, PWA 96 entries |

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

---

## Last Session

Phase 01 closed 2026-04-26. Bundle migration complete: 6 cycle commits effectively (C01-C04 bundled in C05 deploy-prelude `364893d`; C06+C06b uncommitted at HEAD `83d287a` then folded into Phase commit). ~750 substitution points across ~70 files in C01-C04. C06 reduced from 4 to 2 fixes after Pre-Exec discovered `types.ts` is re-export hub from auto-generated `generated.ts` (partner pipeline introduced at `81304a6`); B.1 was already resolved by prior regen, A.2 blocked on stale-openapi regen artifact. C06b followed up: 38 typecheck errors at HEAD `83d287a` (all pre-existing, partner-introduced) → 0 via Option 3 broaden (`Record<string, X>` standard) + tactical patches across 11 files. Final gates: typecheck 0, lint 758 (delta 0 vs baseline), vite build ✓ 1.36s.

8 new decisions (#015-#022) + 1 architectural follow-up decision (#023 types.ts SSOT reinterpretation post-regen). 19 new BACKLOG items (10-28); 2 gated on backend regen coordination (#26 A.2 financial constants; #27 Zodd CRITICAL #1 PracticeSummary.timezone).

Documentary deviations noted at CLOSE: (1) Phase 01 diff range includes 13 ancillary upstream/partner commits — phase cycle work scope is `364893d` + uncommitted C06/C06b at this commit; (2) C01 file count amended from brief's "92" to verifiable scope description (~250 files contributed via bundle snapshot + assets + renames + font).

---

## Next Action

Phase 02: Audit + Backend Coordination (C07-C09). Run `03_Phase-Builder` OPEN in new chat. Phase 02 OPEN must resolve BLOCKING BACKLOG #19 (D3 icons decision) before C09 runs.

---

## For Human

**Session Code:** S1-P02-C07
**Load:**
1. Framework: `01_Declaration.md` + `03_Phase-Builder.md`
2. Project: `ENVIRONMENT.md` + `ARCHITECTURE.md` + `decisions.md` + `BACKLOG.md`
3. Sprint: `S1-SPRINT.md`
**Run:** `03_Phase-Builder` OPEN — Phase 02 (Audit + Backend Coordination, 3 cycles: C07 AUDIT-S1.md scout, C08 backend-coord 7 missing endpoints, C09 icons audit per D3 decision — see BACKLOG #19, must resolve before C09)

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
