# VELO `docs/` — Master Index

Last updated: 2026-05-18 (session 4 closure — Sprint 2 closed, Sprint 2.5 opened)
Sprint reference: **Sprint 0 + Sprint 1 + Sprint 2 closed · Sprint 2.5 active (standalone, file `05_roadmap/sprint-02.5.md`) — three parallel tracks per ROADMAP §5.5: Track A DS Completion block-by-block (Cowork) + Track B CBSHOME Foundation Transfer (Claude Code) + Track C Documentation English Translation pass (Cowork). First action: T2.5.1 Dashboard 9 DS harvest.**
Methodology version: `[VELO-METHODOLOGY.md | v1.4 | 2026-05-18]`
Roadmap version: `[VELO-ROADMAP.md | v1.3 | 2026-05-18]`

> **Single entry point.** Read this first in every new chat or session.
> This file is updated at sprint boundaries per VELO-METHODOLOGY §12.2.
> Local INDEX.md files (one per subfolder) update immediately after
> every change in their scope.
>
> **For fresh chat / handoff:** start with `_HANDOFF.md` in this folder —
> универсальный entry-point prompt с последовательностью загрузки контекста.

---

## What is this folder

`D:\02_Projects\velo\docs\` is the **design-and-handoff workspace** for
VELO. It is kept **outside** the frontend repository. The frontend repo
at `D:\02_Projects\velo\frontend\` is the lean code-only artifact that
ships to production.

This folder produces the handoff package (`01_deliverable/`) that the
frontend consumes.

---

## Folder Map

| Folder | Purpose | Local INDEX | Status |
|---|---|---|---|
| `01_deliverable/` | Handoff package the developer receives | `screens/INDEX.md` + folder-level `README.md` | empty scaffold, populated through Sprints 1–10 |
| `02_design-system/` | Master source of tokens, assets, styleguide | `INDEX.md` + `assets/ASSETS-INDEX.md` | populated — Sprint 1 ✅, Sprint 2 Phase 3 ✅, Phase 4 🔄 |
| `03_mockups/` | Operator's visual workspace (not shipped) | `INDEX.md` | populating — Sprint 2 Phase 4 in progress (Onboarding viewer) |
| `04_methodology/` | `VELO-METHODOLOGY.md` (single source of truth for process) | — | active (v1.2) |
| `05_roadmap/` | `ROADMAP.md` + `sprint-NN.md` per sprint | — | active (v1.1 + 12 sprint files) |
| `06_project-inputs/` | External read-only references (ARCHITECTURE.md, api-openapi.json, CC-REPORT.txt, CC-REPORT-2.txt, **VELO_METHODOLOGY.md v3** — operator's Figma-native workflow, used as Figma rules reference) | `README.md` | active |

---

## Bootstrap reading order (for a fresh chat)

1. This file (`INDEX.md`) — folder map and current status.
2. `04_methodology/VELO-METHODOLOGY.md` — how we work (full document).
3. `05_roadmap/ROADMAP.md` — when each piece of work happens.
4. `05_roadmap/sprint-NN.md` (current sprint) — what's in flight right now.
5. `02_design-system/INDEX.md` — current DS state.
6. `01_deliverable/screens/INDEX.md` — current spec catalog.
7. `06_project-inputs/ARCHITECTURE.md` — frontend code rules (referenced from specs).
8. `06_project-inputs/api-openapi.json` — backend contract (referenced from specs).

---

## Status Summary

| Dimension | Count | Target | % |
|---|---|---|---|
| Tokens (Layer 2 semantic, §6.3 required) | many (see `02_design-system/INDEX.md`) | ~30 | ✅ |
| Components in styleguide | 15 visualised (Tier 1: 7, Tier 2: 8) | ~30 | ~50% |
| Mockups built (Phase 4) | 1 combined viewer with 8 onboarding cols (all ✅ approved 2026-05-18) | ~120 | ~7% |
| Mockups approved (§10.4 MOCKUP GATE) | 8 (Onboarding flow) | ~120 | ~7% |
| Specs active (§10.5 SPEC GATE) | 0 | ~120 | 0% |
| Sprints planned | 12 (00–11) | 12 | 100% |
| Sprints completed | 2 (Sprint 0 + Sprint 1) | 11 (00–10) | ~18% |
| Sprint 2 phases | Phase 3 ✅ · Phase 4 🔄 (Onboarding ✅ · Dashboard ⬜ next) | — | — |

---

## Where to find what

| You need… | Open… |
|---|---|
| The methodology (how we work) | `04_methodology/VELO-METHODOLOGY.md` |
| The roadmap (when things happen) | `05_roadmap/ROADMAP.md` |
| The current sprint's checklist | `05_roadmap/sprint-NN.md` (whichever is in progress) |
| The design tokens master | `02_design-system/tokens/` |
| The styleguide (visual catalog) | `02_design-system/styleguide/velo-design-system.html` |
| The mockups | `03_mockups/{user,master,admin}/` |
| The screen specs | `01_deliverable/screens/SCR-NNN-*.md` |
| Frontend code rules | `06_project-inputs/ARCHITECTURE.md` |
| Backend contract | `06_project-inputs/api-openapi.json` |
| Frontend F0 reconnaissance (historical) | `06_project-inputs/CC-REPORT.txt` |
| Superseded universal methodologies (DS, LIVEMOCKUP) | `04_methodology/_archive/` |

---

## Three critical boundaries (from VELO-METHODOLOGY §3.2)

- **B1** — `01_deliverable/` is the **only** folder the developer/CC sees.
  Folders 02, 03, 04, 05 are internal.
- **B2** — Tokens have **one** master in `02_design-system/tokens/`.
  Copies in `01_deliverable/styles/` are regenerated; never edit copies.
- **B3** — Mockups **never** contain spec content (API contracts, error
  handling, business invariants). Those live in screen specs only.

---

## Open TODOs (high-level)

- [x] **Sprint 0 (docs side) — closed 2026-05-17.** Folder structure + methodology v1.1 + roadmap v1.1 + 12 sprint files + 4 INDEX.md stubs + VALIDATION-REPORT + BACKEND-REQUESTS.
- [ ] **Sprint 0 (programmer side) — deferred to Claude Code:** T0.0 (build fix), T0.3 (router/shells/HomeView), T0.7 (gen:api script), T0.8 (global.css audit). Documented in `05_roadmap/sprint-00.md` as a reference for the programmer; runs in parallel with our Sprint 1.
- [x] **STRATEGIC DECISION resolved 2026-05-17:** **v1.1 active.** v3 stays as Figma operations reference only (its "Frontend Prep Mode deprecated chain 70" wording was relevant to that chain — current strategy is v1.1 frontend handoff). Operations rules from v3 captured in `02_design-system/FIGMA-OPERATIONS-GUIDE.md`.
- [x] **Sprint 1 FULLY CLOSED 2026-05-17.** Both TOKENS GATE ✅ and INVENTORY GATE ✅ passed. Deliverables: variables.css + global.css (213+103 lines, master + deliverable copies, MD5-identical), VELO-DS-INVENTORY.md with provenance, 2 DS icons (Plugin API), **94 of 97 SACRED PNG screenshots saved at 2× retina** (operator UI export, role-organized: user/55 + master/39 + admin/1 legacy HTML).
- [ ] **Architectural finding for Sprint 7:** Admin role has NO Figma SACRED. Sprint 7 admin block builds from scratch using DS tokens + logic from `admin/admin-legacy-reference-v2.5.html`. Documented in ASSETS-INDEX.md.
- [x] **Sprint 2 Phase 3 ✅ closed 2026-05-17** — Styleguide HTML approved by operator (consolidated `velo-design-system.html`, 32 SVG icons in 5 categories, glass shadows, pattern grid fix, real card/modal shadow tokens).
- [ ] **Sprint 2 Phase 4 🔄 in progress** — P0 = Onboarding (8) ✅ + Dashboard (9) ⬜. Onboarding flow viewer `03_mockups/user/_onboarding-flow.html` MOCKUP GATE passed 2026-05-18 (все 8 колонок approved). DS promotion pass завершён: typography canon (h1+body), component heights, stack gaps, glass canon, button halo composition промоутированы в variables.css master + deliverable. Реальные SVG icons извлечены из Figma через Plugin API. **Следующий блок: Dashboard 9** — отдельный combined viewer, строится на готовом DS canon.
- [ ] **Dark theme** — deferred per VELO-METHODOLOGY §2.5 I7. Architecture
      ready (two-layer tokens support a second mode block on Layer 2).

---

## Recent Changes

| Date | Summary |
|---|---|
| 2026-05-17 | **v1.0 foundation established.** Adopted VELO-METHODOLOGY.md v1.0 and ROADMAP.md v1.0 as single sources of truth. Restructured `docs/` to canonical layout per §3. Archived universal methodologies (`DS-METHODOLOGY.md`, `LIVEMOCKUP-METHODOLOGY.md`) to `04_methodology/_archive/`. Moved `ARCHITECTURE.md` and `api-openapi.json` to `06_project-inputs/`. Created `sprint-00.md` through `sprint-11.md` checklists. DSYS-era materials (`stage-{0,1,2}-*/`, `extract/`, old `PROGRESS.md`) were temporarily archived in `docs/_archive/` and then deleted from the workspace by the operator — they remain in git history if needed. |
| 2026-05-17 | **Validation pass started.** `CC-REPORT.txt` (pre-v1.0 reconnaissance) moved to `06_project-inputs/` as an input. Recon prompt #2 prepared at `06_project-inputs/CC-RECON-PROMPT-2.md` to gather a fresh delta report for validating v1.0 methodology against current code and API contract. |
| 2026-05-17 | **Validation pass complete; methodology and roadmap bumped to v1.1.** Findings recorded in `06_project-inputs/VALIDATION-REPORT-2026-05-17.md` and `06_project-inputs/CC-REPORT-2.txt`. Methodology amendments: §2.5 I2/I4/I5/I6 expanded; new I8 (status enums are code-only contracts); §3 ARCHITECTURE.md path corrected; §6.6 Tier 2 enum references aligned with code; §8.4 Section Guidelines (5/7/9/11) extended; §8.7 Waitlist FSM corrected to use `notified` (not `offered`). Roadmap amendments: Sprint 0 grew T0.0 (build fix), T0.7 (gen:api), T0.8 (global.css audit); Sprint 3 user-practice-detail adds create_report; Sprint 4 adds user-reports-list; Sprint 5 master-analytics flagged client-side aggregation; Sprint 7 admin-withdrawal-review + admin-user-detail flagged as backend gaps; Risk Register expanded with R-11/R-12/R-13. Backend requests filed in `06_project-inputs/BACKEND-REQUESTS-2026-05-17.md`. |
| 2026-05-17 | **Sprint 0 (docs side) closed.** All folder structure + methodology + roadmap + sprint files + INDEX.md stubs in place. Sprint 0 programmer-side tasks (T0.0/T0.3/T0.7/T0.8) deferred to Claude Code as a reference deliverable; they run in parallel with our Sprint 1 execution. → Sprint 1 (Figma extraction + token synthesis) ready to start. |
| 2026-05-17 | **Operator's v3 methodology added as input.** `06_project-inputs/VELO_METHODOLOGY.md` (822 lines) — operator's separate Figma-native workflow ("Mockups Production Mode") with detailed Figma Plugin API rules (R-1..R-9 + L-30..L-58 + G-1..G-19 + AP-1..AP-10). Useful subset extracted into `02_design-system/FIGMA-OPERATIONS-GUIDE.md` (page IDs, SACRED roots, safe extraction patterns, F-68 untouchable rule). **Strategic conflict surfaced:** v3 §1 declares "Frontend Prep Mode deprecated chain 70" — this directly conflicts with our v1.1 pipeline whose entire purpose is frontend handoff. Awaiting operator decision (see Open TODOs). |
| 2026-05-17 | **First live Figma probe via use_figma Plugin API.** 7 color variables + 6 text styles + DS canon survivors (Scaffold 4110:316, Mandala 916:1662, back-arrow 423:125) extracted and captured in `02_design-system/tokens/VELO-DS-INVENTORY.md`. All text styles have **concrete pixel lineHeights** from Figma — solves §11.1 AP-DS-3 at source. Mockup-mining (Sprint 1 Step 1.5) still needed for spacing / radii / shadows. |
| 2026-05-17 | **Second Figma probe: full primitive resolution.** 8 Layer 1 primitives now fully resolved with hex (steel/primary `#4c6589`, steel/muted `#5c7292`, neutral/white `#ffffff`, neutral/200 `#abbfda`, neutral/300 `#b0bccd`, neutral/700 `#4f5969`, neutral/900 `#1e2837`, neutral/950 `#141c2a`). 4 Layer 2 semantic variables resolved via aliases (surface/default, text/inverse, border/default, icon/default — all mapped to primitives, both Light + Dark modes). Onboarding SACRED root `541:1179` structure mapped — 8 screens 402×874 with exact node IDs. **Figma has Dark mode primitives already** — methodology §2.5 I7 architectural readiness confirmed. |
| 2026-05-17 | **Methodology v1.1 → v1.2.** Cross-pollination from operator's v3 Figma-native methodology. 3 targeted amendments: §6.4 promote-not-invent (mock-mine SACRED before declaring MISSING), §10.3 STYLEGUIDE GATE adjacent re-probe, §10.4 MOCKUP GATE adjacent re-probe. Companion: `02_design-system/FIGMA-OPERATIONS-GUIDE.md` extended with L-32 (no-throw), L-37 (chunked reads + `loadAllPagesAsync` not supported), AP-6 (font loading per call) — apply during Sprint 1 only. Roadmap stays v1.1 (no roadmap changes from v3). |
| 2026-05-17 | **Sprint 1 closed.** TOKENS GATE passed by operator via `tokens-preview.html` visual validation. Sprint 1 deliverables: `02_design-system/tokens/{variables,global}.css` (master + deliverable copies, MD5-identical), `VELO-DS-INVENTORY.md` with Sections A/B/C and full provenance, `ASSETS-INDEX.md` manifest, 2 DS canon icons saved (Mandala + back-arrow), `tokens-preview.html` for visual validation. **Deferred:** PNG export of 97 SACRED screens to operator local action per `_FIGMA-EXPORT-INSTRUCTIONS.md` (Plugin API 20KB transport cap blocks bulk extraction — same limitation as DSYS D-009). Sprint 2 can proceed in parallel. → **Sprint 2 ready** (Phase 3 styleguide HTML + Phase 4 P0 mockups). |
| 2026-05-17 | **Sprint 1 INVENTORY GATE finalized — operator UI export complete.** Operator did Figma UI multi-select export of 94 SACRED PNGs at native 2× retina (804×1748/1752), organized into role folders: `user/` (55 PNG), `master/` (39 PNG), `admin/` (1 legacy HTML reference `admin-legacy-reference-v2.5.html`). All files renamed by Cowork-Chat into convention `{role}-{section}-{NN}-{slug}.png` with consecutive per-section numbering. Master section renumbered cleanly (201-272 → 01-13/01-08/01-15/01-03). ASSETS-INDEX.md rewritten with role-based catalog and Sprint 3+ SCR mapping. **Architectural finding:** Admin role has NO Figma SACRED — visual design will be built from scratch in Sprint 7 using DS tokens + logic from legacy HTML reference. Both Sprint 1 gates ✅ passed. → **Sprint 2 fully unblocked.** |
| 2026-05-17 | **Font self-hosted (mid-Sprint-2 fix).** Operator caught that Google Fonts `@import` in `global.css` wasn't loading Marmelad (fell back to Noto Sans). Operator provided `Marmelad.zip` (Google Fonts OFL). Unzipped `Marmelad-Regular.ttf` (140KB) to `02_design-system/assets/fonts/` (master) + `01_deliverable/assets/fonts/` (deliverable). Replaced `@import url(google fonts)` with `@font-face` self-hosted in `global.css` + `styleguide HTML` + `tokens-preview.html`. Deterministic rendering, no network dependency. |
| 2026-05-17 | **Sprint 1 EXTENSION — Full Figma mining complete. 🔒 Figma officially closed forever.** Per operator request to fully close Sprint 1, Cowork-Chat executed full mockup-mining across remaining 80 SACRED screens (9 batches via `use_figma`): Calendar 11 + Profile 7 + Messages 3 + Analytics 3 + Diary 20 + Practices 15 + Master Dashboard 8 + Master Onboarding 13. **Total mined: 97/97 SACRED screens (~6700 nodes processed).** New promoted primitives: `--velo-state-info` (#619cd2 — was MISSING, now ✅ RESOLVED), `--velo-radius-md` (10px — was MISSING, now ✅ RESOLVED), `--velo-disabled-bg/text` (grey family #a4a4a4/#919191 — placeholders → real values), `--velo-color-steel-pale` (#91a2ba), `--velo-color-coral-darker` (#ad3444), `--velo-color-alpha-white-70/50/25`, `--velo-radius-xs` (2px), sizes 24/28, `--velo-blur-glass-stronger` (blur 30). variables.css updated to 169 lines (was 213, condensed). **Confirmed truly absent after full mining:** card shadow, modal shadow, focus-ring, hover/active overlays, radius-full — these remain placeholders. ✅ Sprint 1 100% complete. **Figma access is no longer needed for downstream sprints** — DS tokens fully captured. → Sprint 2 ready (styleguide HTML + P0 mockups). |
| 2026-05-17 | **Sprint 2 Phase 3 — single production styleguide.** Tokens preview and styleguide merged into one self-contained page: `02_design-system/styleguide/velo-design-system.html` — three tabs (Tokens / Components / Patterns), Marmelad embedded as base64 (works under `file://`, no network), SVG icon set inline, no external avatars (initials-based). variables.css gained real card/modal shadows: `--velo-shadow-card: 0 2px 8px 0 rgba(76, 101, 137, 0.08)`, `--velo-shadow-modal: 0 8px 32px 0 rgba(76, 101, 137, 0.16)` (master + deliverable MD5-identical). Old `02_design-system/tokens/tokens-preview.html` now redirects to the consolidated styleguide. → STYLEGUIDE GATE: awaiting operator visual review. |
| 2026-05-17 | **Sprint 2 Phase 3 closed.** STYLEGUIDE GATE passed by operator after icon set expansion (2 → 32 SVG, 5 categories), Pattern grid fix (grid-comp clipping device-frame at 340px min — replaced with grid-patterns at 442px min), shadow tokens promotion. |
| 2026-05-17 | **Sprint 2 Phase 4 started — Onboarding block in progress.** Operator declared P0 = full Onboarding (8) + Dashboard (9) under user role (expanded scope from typical 4-6). Implementation choice: one combined viewer file `03_mockups/user/_onboarding-flow.html` with 8 side-by-side columns (PNG etalon top / HTML build bottom), minimal toolbar (only device switcher + screen name). Welcome column at ~80%: real DS assets (`velo-bg-app.png` 804×1748 universal background dropped by operator + `velo-logo-mandala.svg` 492×492 Figma Group 1944 exported as SVG via operator drop), new glass-button canon (white outline + omnidirectional white halo + 5% blue background, no separate VELO text overlay since SVG has it embedded). 5 pending welcome fixes recorded in `sprint-02.md` T2.4. **Session 1 context exhausted → handoff to new chat.** Continuation entry point: `D:\02_Projects\velo\docs\_HANDOFF.md`. |
| 2026-05-17 | **Sprint 2 Phase 4 session 2 — welcome колонка финализирована.** Все 5 операторских правок применены в `_onboarding-flow.html` за один проход: (1) `.velo-bg-mandala` `background-size: cover` → `100% 100%` (PNG ratio совпадает с frame, явная растяжка устраняет субпиксельный дрейф); (2) `.scr-01 .big-logo` 340×340 → **490×490** (внешние кольца мандалы клипуются overflow родителя как в Figma); (3) `.scr-01 .bottom` `padding-bottom` 36px → **120px** (низ кнопок на ~12-15% от низа frame); (4) `.v-button--glass / --ghost / --oauth` переделаны на **wrapper-pattern через `::before`** — base `transparent` + `isolation: isolate`, 5% blue fill + backdrop-blur на `::before` с `z-index: -1` (теперь фон 100% просвечивает сквозь кнопку); (5) `.v-button--glass` получил **softer halo box-shadow** override (18px 0.5 / 8px 0.4 / 10px 0.12 вместо 28px 0.75 / 12px 0.6 / 14px 0.18 — primary остаётся ярким акцентом, secondary тише). Playwright headless verification: 0 console errors, 0 warnings, визуальный side-by-side с Figma PNG ✅. Welcome теперь 🔄 ready for MOCKUP GATE. **DS promotion candidates** для variables.css/styleguide (после полного onboarding-блока): glass-button wrapper-pattern + softer-halo shadow токены. |
| 2026-05-18 | **English-default rule + Standalone Sprint 2.5 cleanup.** Operator audit: 2852 Cyrillic occurrences across 29 docs files. Process docs in Russian = ~2× tokens cost on every session read with no informational gain. **Methodology bumped v1.3 → v1.4:** new §1.1 P6 (English-default principle); new §11.5 AP-P-8 (Russian narrative anti-pattern) with full exception table — UI sample data in mockups, verbatim operator quotes in Daily logs, external inputs in `06_project-inputs/` stay Russian. **Roadmap bumped v1.2 → v1.3:** Sprint 2.5 gains **Track C — Documentation English translation pass** as third parallel work stream (4 sub-phases Conv-1..Conv-4, ETA ~75 min sequential, parallelizable with Tracks A/B). Sub-section numbering shifted to 5.5.5..5.5.8. **Sprint 2 formally closed.** sprint-02.md `Status: closed`. **sprint-02.5.md created** per methodology §15.1 — standalone sprint with three tracks. **_HANDOFF v1.3 → v1.4:** Шаг 4 reference updated to sprint-02.5.md, English rule added to rules of behavior with exception table, startup prompt gains one-line reminder. Conversion of legacy Russian narrative is scheduled work in Sprint 2.5 Track C — not done in this closure session. |
| 2026-05-18 | **Sprint 2 closure + Sprint 2.5 pivot.** Operator surfaced 2 systemic issues during Dashboard 9 attempt: (1) per-element PNG reverse-engineering instead of Figma extraction causes 3× rework on each component; (2) promoting tokens to `variables.css` without simultaneous visualisation in `velo-design-system.html` breaks DS unity (next sessions don't know what's been added, plodят дубли). **Methodology bumped v1.2 → v1.3:** §6.8 DS Promotion Visualisation rule; §7.0 Block-Harvest-First (mandatory for SACRED blocks, three phases: harvest → 5 deliverables → mockup rebuild); AP-P-6 + AP-P-7 anti-patterns. **Roadmap bumped v1.1 → v1.2:** Sprint 2.5 inserted — DS Completion block-by-block (Track A, Cowork) + CBSHOME foundation transfer (Track B, Claude Code) parallel. Reference `06_project-inputs/CBSHOME-PATTERNS-FOR-VELO.md` for 16 ready-to-port patterns. `_HANDOFF.md` v1.2 — both rules in правила поведения; entry point switched to Sprint 2.5 Track A first block (Dashboard 9). `_dashboard-flow.html` skeleton flagged 🗑 superseded (rebuild after Dashboard 9 DS-complete). 8 docs updated this session, 0 new files, 0 mockup/DS content changes. |
| 2026-05-18 | **Sprint 2 Phase 4 — ONBOARDING BLOCK CLOSED.** Все 8 колонок (welcome / login / register / oauth / onboarding-1..4) approved оператором: «приняты экраны и дизайн можно идти к следующим». Финальная итерация (~40 правок) через 1 чат: pixel-measured layout / sizing / typography из Figma этолонов; structural pattern shifts (glass two-layer = ::before border + ::after fill ПОВЕРХ border, halo budget ≤ stack-gap, drop-on-top layer order); реальные SVG icons извлечены из Figma через `use_figma` Plugin API (icon-back-arrow, icon-onb-{practice,diary,chat}, плюс уже имеющиеся velo-logo-mandala/blue) — все PNG icon-ассеты deprecated. **DS promotion to variables.css master + deliverable (MD5-identical):** (a) text aliases re-aliased to `steel-light` (`--velo-text-primary/secondary/link`); (b) Layer 2 component sizing `--velo-button-height: 52px`, `--velo-input-height: 42px`; (c) Layer 2 stack gaps `--velo-stack-gap-buttons: 16px`, `--velo-stack-gap-forms: 10px`; (d) Layer 2 typography canon `--velo-typo-h1-*` (30/36/1.2 letter-spacing/steel-light) + `--velo-typo-body-*` (18/24/steel-light); (e) Layer 2 glass canon `--velo-glass-fill: rgba(76,101,137,0.10)` + hover-state; (f) Layer 2 button halo composition `--velo-shadow-button` (drop 6/14 steel-tone сверху + 7px blur / 11px spread white halo под, alpha 0.57). Total halo extent (18) ≤ button gap (16) — soft falloff допускается, hard center не пересекает соседнюю кнопку. **Next block:** Dashboard 9 — построим в отдельном combined viewer, на уже готовом DS canon. |

---

## Anchor

```
[VELO docs/INDEX.md | v1.0 | 2026-05-17]
Master index of the VELO design-and-handoff workspace.
Update frequency: end of each sprint, per VELO-METHODOLOGY §12.2.
```
