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
| C01 | standard | Bundle snapshot + extract assets + chat1.md delete + Design_prototype refs grep | TODO | | |
| C02 | standard | Add bundle tokens (light + dark) to variables.css | TODO | | |
| C03 | standard | Grep/replace 577 usages `--velo-*` → bundle namespace (affects-global-state) | TODO | | |
| C04 | standard | Glass-tokens cleanup: grep `--velo-glass-*` usages + tokens removal | TODO | | |
| C05 | standard+manual | Shadows audit: все `<VCard>`, `FormShell`, `MobileLayout` визуально на staging | TODO | | |
| C06 | standard | ARCHITECTURE.md + decisions.md #006-#014 + BACKLOG init 9 карточек + DESIGN_MIGRATION.md archive | TODO | | |

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
| Phase | 01: Bundle Migration — NOT STARTED |
| Cycle | C01: not started |
| Status | Planning complete, ready for first cycle |
| Tests | N/A |

---

## Protocol Log

| Cycle      | Protocol              | Date         | Status |
|------------|-----------------------|--------------|--------|
| S1-Sprint-Builder | 02_Sprint-Builder | 2026-04-24 | DONE |

---

## Last Session

Sprint-Builder session 2026-04-24. Planned S1 + S2 + S3 in one chat (decision #011). Scout через Claude Code выявил 5 критических gap'ов (TMA auth, 577 token usages, shadows=none в velo, 7 greenfield экранов вместо port, DESIGN_MIGRATION.md конфликт). План пересчитан с учётом scout: S1 = 14 cycles (+2 от scout findings), S2 = 17, S3 = 19. Phase plans зафиксированы в S1/S2/S3 sprint files. Для полной картины — все три sprint files созданы в этой же сессии.

---

## Next Action

C01 — run 03_Phase-Builder OPEN in new chat.

---

## For Human

**Session Code:** S1-P01-C01
**Load:**
1. Framework: 01_Declaration.md + 03_Phase-Builder.md
2. Project: ENVIRONMENT.md + ARCHITECTURE.md
3. Sprint: S1-SPRINT.md
**Run:** 03_Phase-Builder OPEN — plan first cycle C01 (bundle snapshot + assets extract)

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
