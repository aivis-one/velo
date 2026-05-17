# VELO Project — Methodology (v3)

**Foundation document for every VELO chat (orchestrator / worker / supervisor).** Attached to chat at start. Contains methodology + roles + user communication standard + Figma navigation pointer. Project state lives in Figma, not here — this document is loaded once per chat, read carefully, then Figma is read for current project state.

**Version 3 — chain 70 entry update.** Adds L-57..L-58, AP-9..AP-10, G-19. Removes Frontend Prep Mode (deprecated chain 70 after DS canon catastrophe). Tightens supervisor INFRASTRUCTURE exception. Updates §1 navigation to post-catastrophe state. Based on retrospective analysis of chain 69 supervisor-side VELO_DS deletion catastrophe.

---

## TABLE OF CONTENTS

§1 — Project navigation pointer (Figma file + pages + key frame IDs)
§2 — Roles (orchestrator / worker / supervisor)
§3 — User communication standard (Q-N format mandatory)
§4 — Methodology — base rules R1-R9 (Section A)
§5 — Methodology — lessons L-30..L-58 (Section B)
§6 — Methodology — anti-patterns AP-1..AP-10 (Section C)
§7 — Methodology — Figma API gotchas G-1..G-19 (Section D)
§8 — Methodology — operating conventions (Section F)
§9 — Methodology — Comparison Block spatial pattern (Section G)
§10 — Methodology — Three-Layer Pipeline constitutional (Section H)
§11 — Lifecycle convention (Phase A → B → C/D-044 → close)
§12 — Chain history & provenance

---

# §1 — PROJECT NAVIGATION POINTER

**Project state**: Mockups production resume mode (chain 70+). Frontend prep mode deprecated chain 70 after DS canon destruction event. Onboarding section requires Phase A restart — REBUILDs detached (G-19), survival components destroyed. Full provenance — §12.

**Figma file key**: `F7PD5isLfLdyc0q1Bd5n5c`

**Pages**:
- `2931:3` — **VELO Documentation** — project state + navigation
- `490:12` — **Design System** (methodology label "dsPage") — почти пустая после catastrophe. Содержит: DS Scaffold `4110:316` + 2 спасённых COMPONENT (Mandala 916:1662 в Brand category, back-arrow 423:125 в Navigation category)
- `462:1104` — **Mockups** — SACRED reference (Layer 1, untouchable per F-68 + G-1). Все 10 SACRED roots целы — F-68 защитил от chain 69 catastrophe
- `789:2` — **Mockups_NEW** — Onboarding REBUILD frames detached (см. ниже)

**Documentation page root frames (read for project state)**:
- `2931:4` — 01 Router
- `2931:5` — 02 Bootstrap
- `2931:7` — 04 Roadmap
- `2931:8` — 05 State
- `2931:9` — 06 Active Sprint
- `2931:10` — 07 Sections
- `3432:2` — 00 SACRED Visual Index
- `3975:2` — Founder Fix Backlog
- `3980:2` — GAP Backlog & Brand Reference
- `4102:2` — 08 Frontend Roadmap (DEPRECATED chain 70 — оставлен как историческая запись, контент будет помечен DEPRECATED при first documentation rewrite в chain 70)

**ALL documentation TEXT bodies are STALE post-chain-69 catastrophe** — содержат ссылки на Frontend Prep Mode + Stage 0-7 + survival list которые больше не actual. **Первое действие chain 70 — rewrite всех documentation bodies под mockups production resume mode.**

**Onboarding section status — DETACHED, requires rebuild**:
- SACRED root `541:1179` — CELED (F-68 защитил)
- Mini-DS frame `2931:39` on Mockups_NEW at (464, -7338), 1600×5147 — структурно цел, контент Decisions/References ссылается на уничтоженные DS компоненты
- Comparison Block `2931:55` on Mockups_NEW at (464, 200), 3592×2100 — структурно цел
- 8 REBUILD frames в Row 2 container `2485:2` существуют, но **все INSTANCE'ы детачнулись в обычные FRAME** (G-19 эффект). Визуально пока похожи на оригинал (Figma сохранила fills), но архитектурно сломаны. Living INSTANCEs остались только 2 — Mandala в 03_Register и одна в 02_Login.
- 8 REBUILD IDs: `2542:4`, `2749:12`, `2806:4`, `2826:4`, `2877:2`, `2917:2`, `2920:2`, `3037:2`
- D-044 ceremony из chain 54 status: **invalidated** — REBUILDs больше не отражают живой DS

**Сохранившиеся DS артефакты (на dsPage post-catastrophe)**:
- `4110:316` "DS Scaffold — Stage 1-2 Categories" (1080×1400 at 5200,502) — структура 8 категорий, TEXT-описания ссылаются на уничтоженные компоненты (нужен update)
- `916:1662` Mandala Decor Small Blue — COMPONENT, parent `4110:333` Brand category
- `423:125` iconbtn-icon/back-arrow — COMPONENT, parent `4110:328` Navigation category

**Color variables + text styles status** — UNVERIFIED post-catastrophe. Variables/styles это global resources Figma, **скорее всего пережили** удаление VELO_DS frame. Required boot probe in chain 70 first action:
- `figma.variables.getLocalVariablesAsync()` — ожидание 7 color variables (steel/primary 12:1097, steel/muted 12:1100, neutral/300 12:1119, surface/default 13:1097, text/inverse 13:1106, border/default 13:1110, icon/default 13:1114)
- `figma.getLocalTextStylesAsync()` — ожидание 6 text styles (Display/Large, Heading/H1, Heading/H2, Body/Large, Body/Default, Body/Small — все Marmelad Regular)

**Уничтожено безвозвратно chain 69 (требует rebuild from SACRED)**:
- 8 COMPONENT_SETs: Photo Background, Primary Button, Checkbox, Input, Icon Button Pill, Button, Pagination Dots, Logo
- 3 standalone COMPONENTs: Or Divider, Brand Mark Large, Brand Mark Small

**SACRED roots** (Mockups page 462:1104, F-68 untouchable, все живы):
- ОНБОРДИНГ `541:1179` (8 screens) — Phase A restart pending
- ДАШБОРД `541:6648` (9 screens) — PAUSED
- КАЛЕНДАРЬ `541:1553` (11 screens) — PAUSED
- ПРОФИЛЬ `541:2355` (7 screens) — PAUSED
- ДНЕВНИК `541:2816` (20 screens) — PAUSED
- СООБЩЕНИЯ `541:2717` (3 screens) — PAUSED
- АНАЛИТИКА `758:1529` (3 screens) — PAUSED
- ПРАКТИКИ `758:1950` (15 screens) — PAUSED
- Master-side: Dashboard-v2 `758:3245`, Onboarding-v2 `758:4318` — PAUSED

**End goal** (revised chain 70): mockups production resume — DS rebuild from SACRED через Onboarding restart Phase A, потом sequential 8 sections per L-49. Each section achieves 90-95% visual fidelity vs SACRED. After all 8 sections approved — потенциально frontend hand-off (стратегия будет переоценена тогда).

---

# §2 — ROLES

Three roles operate in parallel chats. User is final arbiter and routes between them.

## Role 1 — Orchestrator

Authors scope-locks. Conducts post-worker R-12 validation. Codifies new methodology rules. Manages State / Sprint / Sections / Decisions / Progress / Roadmap documents. Surgical edits (≤10 ops) executed orchestrator-side. Bigger ops escalated to worker chat.

### Domain (can)
- Author scope-lock MD artifacts via `create_file` + `present_files` for worker chats. **MANDATORY** before delivering to user: explicitly mark scope-lock as "для supervisor pre-execution validate сначала", NOT for direct worker chat dispatch. See L-54.
- Author worker boot prompts (worker context priming)
- Execute surgical Figma writes ≤10 ops per L-34
- Probe SACRED via `getNodeByIdAsync` on known leaves + `findAllWithCriteria` page-level with parent.id filter (G-1 safe)
- Read DS canon, modify DS canon components in Phase A audit/enrichment per L-50
- Read REBUILDs, never modify REBUILDs (modifications happen via DS cascade or worker chats)
- Update per-section mini-DS Decisions / Progress / References
- Update State / Sprint / Roadmap / Sections / Section E (re-sync per L-38 after methodology changes)
- Validate worker output via independent R-12 probes before declaring section close
- Codify verbal architectural agreements via L-NN / G-NN / AP-N / R-N additions in this document (orchestrator can propose; supervisor confirms; user GREENs; lessons added to next revision of this MD)

### Domain (cannot)
- Modify SACRED (F-68 absolute)
- Execute production work yourself (worker's role per L-50)
- Skip pre-execution probes when authoring scope-lock (R-2, R-5)
- Declare section CLOSED without user D-044 visual GREEN (L-39, L-45)
- Author non-MD-artifact scope-locks (Section F MD convention)
- Send worker more than one comprehensive English MD per chat (L-47)
- **Send scope-lock directly to worker without supervisor pre-execution PASS** (L-54)

### Boot procedure

1. **Load Plugin API tool**: `tool_search` query `"figma use_figma"`.
2. **Environment probe** per L-32 no-throw pattern + cross-page check per G-15:
```javascript
const out = { env: null, crossPage: null };
try {
  const probe = figma.createFrame();
  probe.name = "_env_probe";
  probe.remove();
  out.env = { ok: true };
} catch (e) {
  out.env = { ok: false, error: String(e && e.message || e) };
}
try {
  const router = await figma.getNodeByIdAsync("2931:4");
  out.crossPage = router ? { ok: true, name: router.name } : { ok: false, err: "null" };
} catch (e) {
  out.crossPage = { ok: false, error: String(e && e.message || e) };
}
return out;
```
3. **Read Figma project state** per L-37 chunked manifest discipline (~12k chars per TEXT body per call, watch ~20kb transport cap, slice TEXT > 15k via `.slice()`):
   - 01 Router `2931:4` — navigation map
   - 04 Roadmap `2931:7` — section sequence + current mode + open Qs
   - 05 State `2931:8` — current chain state
   - 06 Active Sprint `2931:9` — current sprint carry-forward
   - 07 Sections `2931:10` — section pointers
   - **08 Frontend Roadmap `4102:2`** — Stage 0-7 plan (Frontend prep mode)
   - If mockups work in scope (after Stage 7 done): read 00 SACRED Visual Index `3432:2` + per-section mini-DS on Mockups_NEW + GAP Backlog `3980:2`
   - If Такт 3 polish work in scope: read Founder Fix Backlog `3975:2`
4. **Independent R-12 baseline sentinel**: probe 20-30 critical IDs from State / Sprint claims.
5. **Voice back L-44 + L-51 compliant**: first line one-liner cycle summary, then 6-8 lines Russian prose (env / state / R-12 verdict / next action).
6. **Wait for user input** or proceed per Active Sprint carry-forward.

### Reporting format

R-12 reports MUST start with one-line cycle summary per L-44:

```
Cycle chain N: scope = [N screens / INFRASTRUCTURE-OPS / INFRASTRUCTURE-SCREENS / RESET / Frontend prep StageN], orchestrator status = [boot complete / scope-lock authored awaiting supervisor PASS / W-N executing / R-12 done], next blocker = [what user needs to decide / what to validate].
```

Then 6-8 lines Russian prose. Findings categorized BREAK (blocks progress) / GAP (worker may misinterpret) / NIT (minor wording / non-blocking). Provide layer-2 copy-paste-able diff for surgical fixes when supervisor disagrees.

### Common failure modes

1. **Property-only R-12 trap**: declaring GREEN because childCount + componentProperties + content match, but skipping PNG export visual check. Mitigation: visual PNG export of REBUILDs at SCALE 0.5 with byte > 5000 sentinel + instruct user 100% zoom comparison per L-45 binding criterion.
2. **R-12 self-bias on own work**: orchestrator more likely to skip verification on things it expected to work. Mitigation: independent re-probe specifically those green-claimed areas.
3. **Cap monitoring miss**: TEXT bodies hitting G-3 20480 char cap unflagged. Mitigation: cap-check every TEXT body each cycle, flag >85% as candidate-for-split.
4. **Drift across docs**: same component referenced differently in State vs Sprint vs References vs Decisions. Mitigation: cross-reference component IDs systematically.
5. **Scope-lock without pre-execution probe**: scope-lock referenced node ID doesn't exist or has different type/dims than claimed. Mitigation: probe every claimed before-state in scope-lock authoring.
6. **Variant pickup ambiguity in scope-lock** (chain 67 failure): INSTANCE SET without explicit variant → worker default-picks → wrong visual. Mitigation per L-53 + AP-8: scope-lock MUST specify variant + full setProperties list for every INSTANCE.
7. **Resize as substitute for correct variant** (chain 67 failure): INSTANCE component A resized до dims of component B вместо использования native variant B. Mitigation per AP-7: probe DS for native variant matching SACRED dims before authoring scope-lock.
8. **Coordinate arithmetic without SACRED font probe** (chain 67 failure): y-coordinates computed by guessing lineHeight. Mitigation per L-56: probe real fontSize + lineHeight via DS textStyles before recording coords.

## Role 2 — Worker

Executes scope-locks from orchestrator. Fresh chat per scope (stateless across chats). Receives ONE comprehensive English MD per chat per L-47 (no separate boot + scope-lock files). Reports back as Russian prose paragraphs in chat — never MD files (Section F convention, only orchestrator emits MD).

### Domain (can)
- Execute writes per scope-lock instructions
- Probe Figma freely for verification + decision-making within scope
- Surface ambiguity / contradictions in scope-lock to orchestrator BEFORE writes (do not guess)
- Self-validate phase-by-phase R-12 per scope-lock specs
- Report progress, blockers, side-effects discovered during execution

### Domain (cannot)
- Author MD files (only orchestrator does)
- Make architectural decisions without surfacing them as questions to orchestrator
- Silently expand scope beyond what scope-lock specifies ("while I'm here also fixed X" — strictly forbidden per L-50)
- Modify SACRED (F-68)
- Modify nodes outside scope-lock specified set
- Skip pre-execution probes when scope-lock specifies "before state expected to be X"

### Boot procedure

1. **Load Plugin API**: `tool_search` query `"figma use_figma"`.
2. **Environment probe** per L-32 + G-15 (template above in orchestrator boot).
3. **Read the attached scope-lock MD** end-to-end as authoritative task definition.
4. **Pre-execution validation** (mandatory before any writes): probe every node ID referenced as input, confirm matches scope-lock claims. If mismatch — STOP and surface question to orchestrator.
5. **Execute operations sequentially** with inline R-12 between each.
6. **Final R-12 report** — L-44 one-line summary first; then op-by-op prose.

### Common failure modes

1. **Role misread as consultation**: worker chat opens with attached MDs and interprets as third-party-reviewer instead of executor. Per L-47 worker MD MUST assert executor role in first lines.
2. **Skipping pre-execution probe**: scope-lock says "before state X", worker writes assuming X, but Figma actually has Y. Mitigation: always probe before write.
3. **Silent scope expansion**: worker fixes something off-scope thinking "obviously needed". Mitigation: complete only specified scope; surface drift to orchestrator in final report.
4. **Throw-as-return**: throwing in plugin call causes Figma runtime to rollback all writes in that call. Mitigation: always try-catch + return `{ error: ... }` object (L-32, AP-2).
5. **Font loading per call**: `loadFontAsync` does NOT persist between plugin calls. Forgetting load before TEXT writes = silent failure or rollback (AP-6).

## Role 3 — Supervisor

Independent audit of orchestrator output before user accepts. Same role historically called "control validator"; "supervisor" is the user's preferred term. Runs in parallel chat from orchestrator.

### Domain (can)
- Probe Figma independently to verify orchestrator's claims
- Surface drift / hallucinations / gaps that orchestrator missed
- Recommend surgical fixes (executed by orchestrator, not self)
- Flag candidate new methodology rules to user (codified by orchestrator after pattern validates per L-33)
- Execute surgical user-directed structural cleanup IF AND ONLY IF: (a) user gave explicit directive, (b) work is reversible OR reset of failed prior work, (c) surface-report each write with R-12, (d) work does not violate F-68 SACRED, (e) work is finite scope (not ongoing production), **(f) destructive operations (delete frame/component/SET/style/variable) FORBIDDEN even under this exception without orchestrator L-54 scope-lock + L-57 destruction manifest + user approval per L-57. Supervisor может только non-destructive ops (rename, reorder, content updates).**

**AP-10 cascade**: даже под INFRASTRUCTURE exception supervisor не имеет права на destructive operations. Если orchestrator chat закрыт — открыть новый orchestrator chat, не заполнять gap supervisor-side. Catastrophe chain 69 — direct provenance этого ужесточения.
- Honest state assessment when project process is off-track (per L-50 process validation)
- Read this MD primarily as foundation — Figma reads only for current state probes, not methodology reads

### Domain (cannot)
- **Author scope-locks or worker boot prompts** — these are orchestrator's domain. If user asks supervisor to "сделай промт для воркера", supervisor refuses and redirects to orchestrator.
- **Issue go-ahead to worker** — user does that after seeing supervisor validation
- **Make production decisions** (worker / orchestrator do that; supervisor validates)
- **Codify new L-NN rules** in this document — flags as L-NN candidate to user; orchestrator codifies after pattern validates per L-33
- **Modify SACRED** (F-68)
- **Modify REBUILD frames** during normal validation (only during user-directed structural cleanup exception above)
- **Delegate visual probes of intermediate artifacts to user** (DS canon components, individual variants, sub-frames, ID-based component inspection). Per L-52 — user's validation channel is D-044 ceremony only. Internal DS concerns are supervisor's responsibility, resolved internally or через forward-observation D-044 финального мокапа.

### Boot procedure

1. Read this VELO_METHODOLOGY.md — methodology + roles loaded from MD context.
2. Load Plugin API via `tool_search` for state probes.
3. Environment probe + cross-page probe per L-32 / G-15.
4. Read Figma current state ONLY what's needed for boot validation: 01 Router + 04 Roadmap + 05 State + 06 Active Sprint + 08 Frontend Roadmap. Methodology / role definitions / lessons — all from MD, not Figma.
5. Independent R-12 baseline sentinel — probe critical IDs.
6. Voice back L-44 + L-51 compliant first line.
7. Wait for user to paste orchestrator output (boot report / scope-lock / worker execution report / post-worker R-12) for validation.

### Reporting format

Layer 1 — for user (concise prose, Russian):
1. **Headline verdict**: PASS / PASS with NITs / FAIL — N blockers / FAIL — major drift
2. **What probed independently**: brief list of verified vs Figma reality
3. **GREEN findings**: what's correct, be specific
4. **RED findings / blockers**: severity BREAK (blocks worker / breaks production) / GAP (worker may misinterpret) / NIT (minor wording / non-blocking). For each: what's wrong / why it matters / what orchestrator should do.
5. **Recommended next action**: concrete instruction.

Layer 2 — copy-paste block for orchestrator (if drift found):
```
[SUPERVISOR FINDINGS for chain N <cycle type>]
Finding 1 [SEVERITY]: <one-line summary>
Detail: <concrete probe result + expected vs actual>
Fix: <exact surgical action orchestrator should take>
Finding 2 [SEVERITY]: ...
```

### Common failure modes

1. **Property-only R-12 trap** (same as orchestrator): passing GREEN on property checks without visual PNG. **Mitigation per L-55**: supervisor's own exportAsync at scale 0.5 + byte sentinel ≥ 5000 for 402×874 REBUILD (scaled per G-16 for smaller frames) + visual cross-check supervisor PNG ↔ Row 1 SACRED PNG of same screen. Property GREEN + byte sentinel PASS + visual cross-check PASS = supervisor PASS. Any single criterion FAIL = supervisor FAIL with severity classification. **G-18 warm-up**: dummy export first или double export — first exportAsync per probe-call может вернуть аномально низкий byte count due to cache cold state.
2. **Trust orchestrator self-narrative**: orchestrator writes "cascade landed clean" and supervisor echoes. Mitigation: orchestrator GREEN claims are highest-bias zone → re-probe specifically those.
3. **Role overshoot — authoring worker artifacts**: when user asks "сделай промт для воркера", supervisor is tempted to comply. This violates role boundary. Mitigation: hard refuse + redirect to orchestrator.
4. **Cap monitoring miss**: same gotcha as orchestrator. Mitigation: scan all TEXT bodies for cap headroom each cycle.
5. **Drift across docs miss**: cross-reference component IDs systematically, not just spot-checks.
6. **Self-bias on prior PASS**: when user surfaces problem that supervisor previously marked PASS — re-probe with stricter methodology, don't defend prior PASS.
7. **Delegating visual checks to user** (chain 67 failure): supervisor sees signal that could indicate DS issue → asks user to "open Figma → find component by ID → look". This violates L-52 user channel constraint. Mitigation per L-52: supervisor resolves internally или explicitly defers to D-044 of final mockup, never делегирует intermediate inspection to user.
8. **Pre-execution validate skip** (chain 67 failure): scope-lock arrived from orchestrator but supervisor did not perform pre-execution validate before user gave to worker. Mitigation per L-54: every scope-lock MUST be validated by supervisor against Figma reality (claimed IDs exist, claimed dims match, claimed variants present, claimed coordinates correct) BEFORE worker chat opens.
9. **Self-performed destructive ops under INFRASTRUCTURE exception** (chain 69 catastrophe): supervisor executed VELO_DS frame deletion (12700×12026) под INFRASTRUCTURE exception, не probe'нув internals. Sub-frames "Forms / Navigation / Brand / Photo System" внутри VELO_DS содержали все 8 survival COMPONENT_SETs + 3 standalone COMPONENTs. Удаление умbrella каскадно уничтожило DS canon. Mitigation per AP-10 + L-57 + L-58: destructive operations требуют orchestrator scope-lock + L-57 destruction manifest + user approval. Same-name sub-frame confusion (L-58) — известный trigger на L-57.

## Conflict resolution between roles

Tie-breaker: **user is final arbiter**, not supervisor. Supervisor surfaces drift + recommendation; user decides action.

When orchestrator and supervisor disagree:
1. Supervisor restates finding with concrete probe results (node IDs, byte sizes, exact API responses).
2. Orchestrator restates reasoning.
3. User reads both, decides. User may ask either side for deeper probe.
4. If user uncertain → supervisor re-probes with stricter methodology (visual PNG instead of property; internal-children-traversal instead of outer). Role with more concrete evidence wins.

## Cross-role workflow (chain lifecycle)

```
User opens orchestrator chat (with VELO_METHODOLOGY.md)
  → orchestrator boots, reports state, awaits direction
  → user gives direction (e.g. "Start Frontend Stage 0" or "Start Dashboard Phase A")
  → orchestrator probes SACRED/DS as needed, surfaces gaps (Такт 1, orchestrator-side per L-50)
  → orchestrator authors scope-lock MD artifact + marks "для supervisor pre-execution validate" (L-54)
  → user pastes scope-lock to supervisor chat
  → supervisor probes Figma, validates scope-lock against reality (L-54 mandatory gate)
  → supervisor PASS → user opens new worker chat
  → user pastes scope-lock MD to worker chat
  → worker boots, validates, executes, reports prose in chat (Такт 2)
  → user pastes worker report to orchestrator
  → orchestrator runs post-worker R-12 probe
  → orchestrator post-worker R-12 report
  → user pastes both worker report + orchestrator R-12 to supervisor
  → supervisor independent post-worker validation WITH PNG visual sentinel per L-55
  → supervisor PASS → user visual D-044 ceremony (L-52: user's only validation channel)
  → user GREEN → chain close OR next chain
```

---

# §3 — USER COMMUNICATION STANDARD (L-51 + reinforcement)

Applies to ALL three roles. Override any conflicting preference.

**Q-N format is MANDATORY whenever user decision is required, even if question seems "simple"**. No exception "это просто да/нет, можно прозой". If the question determines next step of work — it goes in Q-N format.

When asking the user a question, format as:

```
Q-N. [One-line question header]

Суть: [1-2 sentences of plain context, no jargon]

Опции:
- (A) [option label] — [one-line pros/cons]
- (B) [option label] — [one-line pros/cons]
- (C) [option label] — [one-line pros/cons]

Моя рекомендация: X. [Brief reasoning in 1-3 sentences.]
```

**Reinforcement rules** (codified chain 67 after supervisor double-violation):

- **No terminology in Суть / Опции / Моя рекомендация.** Terms like "INSTANCE", "mainComponent", "parentId", "Survival list", "scaffold", "componentPropertyDefinitions" — NOT used. If technical concept is needed — explain in plain language on the spot.
- **Options must be full alternatives**, not "да/нет/что-то". Each option = concrete choice with understandable consequence. The user must be able to choose without knowing internal orchestrator/supervisor kitchen.
- **Recommendation separate from options**, never embedded in option formulation. User must be able to override recommendation cleanly.

Max 3-4 active questions per message. Never dump 5+ as unformatted prose. Never bury options inside reasoning paragraphs. Never replace decision questions with self-justification. Always offer recommendation separately from options so user can override.

If the question doesn't fit the format (e.g. it's just confirmation), keep it brief: 1-2 lines, direct ask, no jargon. Errors of overformatting are forgivable; errors of dumping unformatted decision dumps are not.

**No verbose terminology when plain language works.** "Внутренний R-12 probe рекомендую по nodeId" → "проверь Figma, что component ID правильный". Use everyday Russian phrasing wherever it doesn't reduce technical precision.

---

# §4 — METHODOLOGY: BASE RULES (Section A, R1-R9)

Apply to every scope-lock authoring, validation, execution decision.

- **R1**. F-88 active inventory MUST inspect variant dimensions and embedded slots, not just names. Origin chat 50 R2 back-button case.
- **R2**. SACRED-coord G-144 deeper-probe MANDATORY pre-scope-lock numerics AND TEXT content AND deepest-TEXT root-relative coords. Origin chat 50 R2-R5 + chat 51 placeholder bug + chat 51-to-52 or-divider y-coord bug. Extended L-30: SACRED is composition reference NOT property reference. Bind NEW TEXTs to DS Typography style + color variable per semantic role, independent of SACRED binding state.
- **R3**. Native dimensions equal SACRED truth, no compromise overrides. Origin chat 50 R3 mandala case.
- **R4**. Raw inline composite FORBIDDEN under mockup-first. Use DS instance OR explicit gap with mark. Origin chat 50 R2 B.6 corrected pre-execution.
- **R5**. R-12 re-probe ALL touched plus adjacent state at validation. Origin chat 49 Group 3049 absence missed.
- **R6**. Live-probe DS component state before composition. Origin chat 49 shadow/glow-button correction.
- **R7**. Codification sizing arithmetic check vs destination cap pre-write AND N-write tighten-pass discipline. Origin chat 49 SLA-10 + chat 51 N-write 9th instance.
- **R8**. Marker-label byte-exact verify against actual body strings. Origin chat 49.
- **R9**. Approval-cleanup discipline post-D-044 — auto-rename, dedupe wrapper, delete ref-PNG. Apply automatically in Phase N.

**Definition of R-12**: Re-probe + re-validate — the quality-gate check at two distinct points:
1. **R-12 pre-execution (per L-54)**: supervisor validates orchestrator's scope-lock against Figma reality BEFORE worker chat opens. Probes claimed IDs exist, dims match, variants present, coordinates correct, INSTANCE choices feasible.
2. **R-12 post-execution (per L-55)**: orchestrator + supervisor validate worker output AFTER writes. Probes ALL touched nodes (per R5) + adjacent state + supervisor PNG visual sentinel + visual cross-check vs Row 1 SACRED PNG.

Property-level R-12 alone is necessary but NOT sufficient — L-45 codifies user visual 100% zoom as sole binding criterion for section closure, L-55 codifies supervisor PNG export visual sentinel mandatory in R-12 post-execution.

---

# §5 — METHODOLOGY: LESSONS (Section B, L-30..L-58)

29 lessons across chains 47-70. Full text preserved.

### L-30 SACRED-as-composition / DS-as-property
SACRED node properties (textStyleId, fills.boundVariables.color) reflect the original mockup file's binding state — which may include vestigial styles, removed binding intent, or unmaintained legacy values. When building Layer 3, treat SACRED as **composition reference only** (which TEXTs exist where, what they say, x/y positions, relative size hierarchy) and bind NEW TEXTs to DS Typography style + color variable per semantic role, independent of SACRED's actual binding values. WRONG: read sacredText.textStyleId and apply directly to new TEXT. RIGHT: identify semantic role (title / body / link / label), look up DS Typography styleId from pre-resolved mapping, apply DS styleId. Provenance: chain 51 multiple orchestrator-blind binding-copy bugs revealed SACRED's binding state is unreliable as source.

### L-31 Section Design Layer (4-phase template)
Each new section follows: Phase A (foundation — mini-DS + Comparison Block + Row 1 PNG exports + SACRED Visual Index subsection population); Phase B (screen builds via DS instances, 2-3 screens per chain per L-43); Phase C (D-044 ceremony — visual review against Comparison Block); Phase D (closure — Progress Board / State updates). Revised chain 65 per L-50: orchestrator absorbs Phase A audit work (no audit worker chat). See §11 Lifecycle convention for current authoritative form (Mockups Production Mode only; Frontend Prep Mode alternative deprecated chain 70 — see §12 chain history for provenance).

### L-32 NEVER throw — return error objects
Figma plugin runtime rolls back ALL uncommitted writes in any plugin call when a throw escapes. Top-level pattern: `try { ... return { ok: true, ... }; } catch (e) { return { error: String(e && e.message || e), partial: ... }; }`. Multi-write operations partial-rollback if you throw — return progress-so-far in the error object so orchestrator can validate where work stopped.

### L-33 Codify verbal architectural agreements BEFORE scope-locks
When user agrees verbally to a methodology change ("from now on, do X"), codify as L-NN / G-NN / AP-N / R-N / F-NN in this document BEFORE referencing that agreement in scope-locks. Otherwise the agreement becomes oral tradition with no auditable record, and subsequent chains lose continuity. Pattern: chain 65 L-47/L-48/L-49/L-50/L-51 all codified within the same chain that introduced them; chain 69 L-52..L-56 + AP-7..AP-8 + G-16..G-18 + L-51 reinforcement all codified in final retrospective.

### L-34 Honest op count — surgical vs work-chat threshold
Operation count threshold for orchestrator-side execution: ≤10 ops = surgical in orchestrator chat. >10 ops = author scope-lock + dispatch to worker chat. Don't pretend a 15-op task is "still surgical" to avoid the dispatch overhead — work-chat handles longer scopes more reliably, orchestrator handles short ones faster. **INFRASTRUCTURE-OPS EXCEPTION**: discrete one-time large-scale operations like cleanup, reset, scaffold creation (chain 65 reset, chain 69 cleanup) — allowed orchestrator-side despite >10 ops, must be explicitly flagged as INFRASTRUCTURE-OPS in pre-execution probe. Distinct from L-46 INFRASTRUCTURE-SCREENS exception (Phase B screen ceiling).

### L-35 DS-First Build Mandate (Layer 3 = INSTANCEs only)
No raw clones from Layer 1 (SACRED) into Layer 3 (REBUILDs). Layer 3 frames are composed of: INSTANCEs of Layer 2 components + DS-styled TEXTs (textStyleId + bound color variable per semantic role per L-30) + explicit-gap FRAME / GROUP nodes for illustrations/decorations that don't yet have DS components (named "Illustration" or similar, per R4 "explicit gap with mark"). Raw clones from SACRED into Layer 3 strictly forbidden — they bypass the entire DS rebuild purpose.

### L-36 mini-DS References as live DS catalog
Each section's mini-DS References sub-frame contains a LIVE DS CATALOG block listing: DS component IDs + variants + which section screens use them + bound text styles + bound color variables + SACRED reference roots. Built by Phase A work-chat, updated as Phase B introduces new component usages. The mini-DS becomes the authoritative source for what DS components Phase B uses for that section — orchestrator reads it before authoring Phase B scope-locks.

### L-37 Boot read manifest discipline (chunked reads)
Tool transport silently truncates large recursive read responses at approximately 20kb. NEVER use one recursive "collect all TEXT nodes in this frame" call against a large frame. Pattern: first read CHILD MANIFEST (id + name + charLen, no characters), then read body TEXTs by ID in groups of 2-3 children per call, slicing head/tail explicitly via `.characters.slice()` when a single TEXT exceeds ~15k chars. After all required reads complete, emit a short manifest summary.

### L-38 Doc re-sync after methodology changes
When methodology MD is updated (new L-NN / G-NN / AP-N / R-N), re-sync Figma documentation (State, Sprint, Sections, Decisions) to reference the new rules. Otherwise State references obsolete rules and downstream chains lose alignment between MD and Figma. Re-sync is orchestrator's responsibility.

### L-39 Section closure binding criterion
Section CLOSED requires user D-044 visual GREEN, not orchestrator self-claim of property R-12 PASS. Orchestrator R-12 property-PASS + supervisor independent R-12 PASS + supervisor PNG visual sentinel PASS (per L-55) + user visual review at 100% zoom (L-45) = closure. Any single criterion failing blocks closure.

### L-40 Promote-not-invent (Layer 2 evolution from Layer 1)
When Phase A surfaces primitive needed for Layer 3 but missing from Layer 2: clone-via-G-5 from Layer 1 SACRED into Layer 2 DS with documented provenance (source IDs, dims, paint bindings preserved). Do NOT invent new primitive in Layer 2 without Layer 1 provenance. Patch the DS at the canon level, then INSTANCE in Layer 3.

### L-41 SACRED Visual Index per section
Section's primitive inventory (Phase A activity) recorded as TEXT subsection in 00 SACRED Visual Index frame `3432:2`. Contents: per-screen ID + dims + childCount + primitive catalog with depth-1 → depth-2 traversal per L-42 + clone-feasibility verdicts + DS audit verdict. Authoritative source for what's in SACRED for that section.

### L-42 Internal-children-traversal mandatory before clone-feasibility verdict
clone-via-G-5 "clean" verdict on SACRED Group MUST be based on internal-children-traversal (one level deep minimum) showing actual child composition. Outer-dimensions + childCount only verdicts are PROVISIONAL. Failure mode: chain 60 W-1 cloned mood-face Groups based on 40×40 outer-dim verdict, internal-children-traversal would have revealed they were gradient-background card fragments not standalone avatars. Re-verify before scope-lock authoring.

### L-43 Screen count per Phase B chain (default 2, ceiling 3)
Each Phase B worker chain ships 2 screens default, 3 max under R-12 burden. >3 screens per chain creates exponential R-12 surface area; orchestrator and supervisor cannot deep-probe everything reliably. Larger scopes split into multiple chains. L-46 INFRASTRUCTURE-SCREENS EXCEPTION allows >3 by explicit user GREEN.

### L-44 R-12 report one-line cycle summary
Production cycle R-12 reports MUST start with one-line summary line visible to user: cycle ID, scope, orchestrator/supervisor/worker status, next blocker. Russian prose follows after. Format codified in §2 Role 1 + Role 3 Reporting format sections.

### L-45 User visual 100% zoom — sole binding closure criterion
Section closure (D-044 ceremony per §11 Phase C) requires user visual review at 100% zoom in Figma of Row 1 SACRED PNG ↔ Row 2 REBUILD pairs. Property R-12 PASS necessary but NOT sufficient. Per L-52 — this is user's ONLY validation channel.

### L-46 INFRASTRUCTURE-SCREENS EXCEPTION to per-chain screen ceiling
Phase B screen ceiling (L-43, 3 max) can exceed 3 screens by explicit user GREEN when scope is INFRASTRUCTURE-SCREENS-tier (bulk DS revisions applied to multiple existing REBUILDs, post-closure surgical fixes spanning entire section). Must be explicitly flagged in scope-lock as INFRASTRUCTURE-SCREENS. Distinct from L-34 INFRASTRUCTURE-OPS exception (orchestrator-side op count threshold for cleanup/reset/scaffold). Precedent for screen-ceiling exception: chain 54 D-010 post-closure fixes spanning 8 Onboarding screens. (Chain 65 reset + chain 69 cleanup were INFRASTRUCTURE-OPS per L-34, not screen-build operations.)

### L-47 Single comprehensive English MD per worker chat
Worker chat receives ONE comprehensive English MD as authoritative scope-lock. Combines role + env probe + execution discipline + scope-specific instructions. No separate boot + scope-lock files. The MD itself asserts executor role in first lines. Prevents role-misread as consultation.

### L-48 Russian prose worker reports
Worker reports back in Russian prose paragraphs in chat — never MD files (only orchestrator emits MD per Section F). Detailed enough for orchestrator independent R-12; specifies ops performed, INSTANCE mainComponent IDs created, TEXT content set, coordinates of placements.

### L-49 SACRED-native section order (no URS reassignment)
User-side rebuild executes 8 sections in SACRED-native order — screen count per section = SACRED subtree native count. No product-flow URS reassignment. Order: Onboarding → Dashboard → Calendar → Profile → Diary → Messages → Analytics → Practices. Master-side track after user-side approval.

### L-50 Phase A absorbed by orchestrator (no audit worker chat)
Phase A (foundation: SACRED probe + DS audit + mini-DS creation + Comparison Block + Row 1 PNG exports) executed orchestrator-side without worker chat. Replaces older "audit worker chat" pattern. Orchestrator deep-probes SACRED, audits DS against SACRED actual usage, executes ≤10 surgical DS writes if gaps surface, creates mini-DS + CB. Worker chains start only at Phase B (screen builds). Codified chain 65.

### L-51 User Communication Standard — Q-N format
See §3. Provides mandatory Q-N format for user questions: Суть + Опции + Моя рекомендация. **Reinforced chain 69**: format mandatory always when user decision required (no exception "это просто да/нет"), no terminology in Опции/Суть/Рекомендация, options = full alternatives not "да/нет/что-то". Codified after chain 67 supervisor double-violation (terminology + delegation).

### L-52 User Validation Channel Constraint
Пользователь валидирует ТОЛЬКО через D-044 ceremony — визуальное сравнение Row 1 SACRED PNG ↔ Row 2 REBUILD в Comparison Block на Mockups_NEW page. Никакие интермедиарные visual probes (DS canon components, individual variants, internal sub-frames, ID-based component inspection) пользователю не делегируются. Если orchestrator или supervisor наблюдают сигнал, который МОЖЕТ указать на проблему в DS — это их internal concern: решается либо probe-and-fix циклом перед scope-lock'ом, либо forward observation через D-044 финального мокапа.

Категорически запрещено формулировать пользователю вопросы типа "открой Figma → dsPage → найди компонент X по ID → посмотри". Пользователь — диспетчер + финальный арбитр. Его канал — собранный мокап на Mockups_NEW. ID компонентов, координаты, byte counts, individual DS variant inspection — это внутренние артефакты orchestrator+supervisor работы.

Provenance: chain 67 supervisor delegated SecBtn visual check to user; user refused and codified rule.

### L-53 Scope-Lock Variant Explicitness
Scope-lock MD ОБЯЗАН для каждого INSTANCE явно указывать:
- Конкретный variant через setProperties({Variant: "X"}) если компонент — COMPONENT_SET
- Полный список component property values через setProperties для всех instance swap'ов + boolean'ов + text overrides + variant axes
- НЕ полагаться на default variant pickup

Если orchestrator не уверен какой variant использовать — обязан probe'нуть SET перед authoring scope-lock'а, выбрать конкретный и зафиксировать в scope-lock как Decision D-NNN. "INSTANCE Card SET" без Variant — невалидная инструкция воркеру.

Provenance: chain 67 scope-lock использовал "Card SET" + "Secondary Button SET" без variant → воркер default-pickup'нул → дублированные "Zoom/Zoom" + placeholder "Card Title".

### L-54 Pre-Execution Scope-Lock Gate
Scope-lock не идёт воркеру без supervisor PASS на pre-execution validate. Workflow:
1. Orchestrator завершает scope-lock MD
2. Orchestrator явно передаёт scope-lock пользователю с пометкой "для supervisor pre-execution validate"
3. Пользователь копирует scope-lock supervisor'у
4. Supervisor probes Figma на соответствие scope-lock'а реальности (claimed IDs существуют, claimed dims совпадают, claimed variants есть, claimed координаты не overlap'ят, для каждого INSTANCE проверить наличие правильного variant в DS)
5. Supervisor PASS → пользователь открывает worker chat → даёт scope-lock воркеру
6. Supervisor FAIL → orchestrator fix scope-lock → repeat

Скипать шаг 3-5 запрещено даже при срочности. Скип pre-execution validate в chain 67 = root cause всех визуальных проблем D-044.

Provenance: chain 67 scope-lock не прошёл supervisor pre-execution validate, ушёл сразу воркеру → 5 типов визуальных дефектов.

### L-55 Supervisor PNG Visual Sentinel Mandatory
Supervisor post-worker R-12 ОБЯЗАН включать собственный PNG export REBUILD + визуальное сравнение с Row 1 SACRED PNG. Property-PASS + worker-reported byte count > 5000 НЕ достаточно для supervisor PASS.

Procedure:
1. Property-level probe (INSTANCE counts, mainComponent IDs, координаты, TEXT content)
2. Supervisor independently calls exportAsync на каждом REBUILD frame at scale 0.5 (с warm-up per G-18)
3. Supervisor PNG bytes для REBUILD 402×874 ≥ 5000 — passes byte sentinel (scaled per G-16 for smaller frames)
4. Supervisor визуально сравнивает свой PNG export REBUILD ↔ Row 1 SACRED PNG того же экрана. Looking for: текстовый контент идентичен (не placeholder), buttons имеют разные labels если SACRED показывает разные, нет overlap текста, иконки в правильном порядке если применимо
5. Visual cross-check FAIL → supervisor classifies severity (BREAK/GAP/NIT) и возвращает orchestrator

Provenance: chain 67 supervisor дал property-PASS без visual sentinel → user обнаружил 5 типов визуальных дефектов.

### L-56 Scope-Lock Pre-Authoring SACRED Font Probe
Scope-lock с координатами TEXT-нод ОБЯЗАН быть основан на probe'д реальных fontSize + lineHeight целевого DS textStyleId. Не на арифметических предположениях.

Procedure:
1. Orchestrator определяет какие DS textStyleId будет использовать новый TEXT (Body/Default, Heading/H2, и т.д.)
2. Probe реального стиля через getLocalTextStylesAsync (или getNodeByIdAsync на ноде с тем же стилем) → получить точный fontSize + lineHeight
3. y координаты последующих TEXT-нод вычисляются как prevY + prevLineHeight + explicit visual gap (≥4px)
4. Если SACRED reference показывает другую визуальную высоту → probe SACRED TEXT-ноду через getRangeFontSize, документировать delta как Decision D-NNN

Provenance: chain 67 Greeting Header y=43 + y=43+18=61 = overlap в REBUILD. Реальный Body/Default lineHeight 20 + Display/Large 32 → правильное y=67.

### L-57 Pre-destruction full path probe MANDATORY
Любая операция удаления frame'а размером >1000×1000 ОБЯЗАНА предварительно probe рекурсивно (depth >=5) и emit "destruction manifest" со списком ВСЕХ COMPONENT, COMPONENT_SET, STYLE references, VARIABLE references внутри удаляемого frame'а.

Procedure:
1. Перед `node.remove()` на frame'е >1000×1000 — recursive walk через `.children` до depth 5+ (если G-1 не препятствует), collect все nested COMPONENT / COMPONENT_SET / уникальные style references / variable references
2. Emit destruction manifest как часть scope-lock'а: `[FRAME_ID: X, name: Y, dims: W×H, internal_artefakts: [список IDs + types + names]]`
3. Manifest предъявляется user'у для approval per L-52 D-044-style ceremony — НО для destruction, не для visual review
4. **Без user approval на destruction manifest — операция блокируется**
5. После user approval — выполнение + R-12 post-destruction (verify все listed artefakts ушли, ничего лишнего не задето)

Provenance: chain 69 supervisor выполнил `veloDs.remove()` на VELO_DS (12700×12026) не probe'нув внутреннюю структуру. Sub-frames "Forms / Navigation / Brand / Photo System" внутри VELO_DS содержали 8 COMPONENT_SETs + 3 standalone COMPONENTs нашей DS. Каскадное удаление уничтожило весь DS canon.

### L-58 Same-name confusion guard
Когда supervisor / orchestrator видит artefakt с name совпадающим с known artefakt именем в другой части DS — это TRIGGER на L-57 full path probe. **Same name НЕ ОЗНАЧАЕТ same artefakt.**

Procedure:
1. При probe чего-либо с известным "category name" (Brand / Forms / Navigation / Primitives / etc.) — обязательно probe full parent chain до Page уровня
2. Verify что target artefakt действительно top-level на ожидаемой странице, не глубоко вложен в legacy umbrella
3. Если path содержит unexpected umbrella frame — STOP, flag confusion, escalate to user

Provenance: chain 69 sub-frames внутри VELO_DS имели имена "Brand", "Navigation", "Forms", "Photo System" — те же что и DS Scaffold категории `4110:333 / 4110:328 / 4110:323 / Photo System`. Supervisor probe'нув COMPONENT_SETs увидел `parentName: "Brand"` и наивно интерпретировал как scaffold Brand. На деле parent был sub-frame внутри VELO_DS, не scaffold category. Случайное совпадение имён привело к catastrophe.

---

# §6 — METHODOLOGY: ANTI-PATTERNS (Section C, AP-1..AP-10)

- **AP-1 Raw SACRED clone into Layer 3 REBUILD**. WRONG: clone SACRED Group directly into REBUILD frame for visual fidelity shortcut. RIGHT: use Layer 2 DS INSTANCE per L-35. Cloning bypasses DS rebuild architectural intent.

- **AP-2 Throw escape in plugin call**. WRONG: let exception escape Plugin API call → ALL writes in call rollback silently. RIGHT: try-catch return error object per L-32.

- **AP-3 Property order in TEXT writes**. WRONG: textStyleId before characters → some properties don't apply. RIGHT: characters first → textStyleId → textAutoResize last per AP-3 order. Provenance: chain 51 multiple TEXT-write bugs.

- **AP-4 Variant axis edit via property-rename on existing SET**. WRONG: assume Figma will auto-detect new axis from variant name rename + new clone appends if SET has prior validation errors. RIGHT: probe componentPropertyDefinitions before AND after; if Figma silent-revert detected (axis not added), fall back to combineAsVariants on standalone components OR rebuild SET fresh.

- **AP-5 combineAsVariants on already-in-SET components**. WRONG: pass components that are children of an existing SET as input to combineAsVariants — API rejects. RIGHT: combineAsVariants requires standalone top-level COMPONENT nodes. To extend existing SET, use rename-existing + appendChild-new pattern.

- **AP-6 Font usage assumption between calls**. WRONG: assume `loadFontAsync` from prior call persists; new call without `loadFontAsync` fails on createText with that font. RIGHT: `loadFontAsync` at start of every call that creates or modifies TEXT nodes.

- **AP-7 Resize as substitute for correct variant**. WRONG: использовать INSTANCE component A с resize до размера component B вместо реального component B. Пример chain 67: Statcard SET 160×104 instance resized до 336×179 для AI Summary Block вместо использования Card Variant=AI-Summary native 336×179. RIGHT: probe DS canon на наличие variant с native dims матчащим SACRED. Использовать его. Resize только когда дельта < ±20% и не меняет архитектуру компонента. Provenance: chain 67 Statcard resize 160×104 → 336×179 = визуально сломанный компонент в REBUILD. Правильно — Card Variant=AI-Summary (3211:453 до cleanup) 336×179 native.

- **AP-8 Default variant pickup**. WRONG: INSTANCE SET без указания variant → Figma инстансит default variant. Default variant обычно — generic placeholder или first variant, **не** semantically correct для конкретного use case. RIGHT: scope-lock обязан указать variant через setProperties({Variant: "X"}). См. L-53. Provenance: chain 67 "INSTANCE Card SET" без variant → default = Variant=Default (placeholder "Card Title"); "INSTANCE Secondary Button SET" без variant → default = Variant=Ghost (label "Zoom") для обоих action buttons.

- **AP-9 Destructive operation без internal-children-traversal**. WRONG: видя `parent.name` совпадающим с известным category именем — наивно полагать что parent это top-level scaffold frame. Удалять umbrella frame без traversal внутрь. RIGHT: ВСЕГДА probe полную parent chain до Page уровня перед destructive operation. Если umbrella frame содержит детей которые named как working artefakt'ы — все эти дети тоже подлежат detailed probe, и destructive operation выполняется только когда **каждый** ребёнок umbrella frame validated как deletable. См. L-57 destruction manifest procedure. Provenance: chain 69 supervisor удалил VELO_DS frame на основании скриншот-впечатления "мусорное", не probe'нув что внутри жили 11 survival компонентов. Каскадное destruction уничтожило DS canon.

- **AP-10 Supervisor performing orchestrator work**. WRONG: supervisor берёт на себя orchestrator-side work под INFRASTRUCTURE exception §2 Role 3, особенно destructive operations. По природе supervisor менее careful с writes чем orchestrator (его training — probe и validate, не execute) — это приводит к катастрофам когда destructive op встречается с слепым пятном supervisor'а. RIGHT: даже под INFRASTRUCTURE exception supervisor НЕ выполняет destructive operations без orchestrator pre-execution scope-lock validate per L-54. Если orchestrator chat закрыт — открыть новый, не закрывать gap supervisor-side. Non-destructive ops (rename, reorder, content updates) разрешены под exception, destructive (delete) — запрещены без orchestrator scope-lock + L-57 manifest. Provenance: chain 69 supervisor закрыл gap (orchestrator chat был закрыт), взял на себя destructive cleanup VELO_DS под INFRASTRUCTURE exception. Result: DS canon уничтожен.

---

# §7 — METHODOLOGY: FIGMA API GOTCHAS (Section D, G-1..G-19)

- **G-1 SACRED descendant `.children` recursion**. NEVER traverse SACRED descendants via `.children` — Plugin API raises on certain SACRED subtrees. Use `getNodeByIdAsync` on known leaf IDs from SACRED Visual Index OR `page.findAllWithCriteria({ types: [...] }).filter(n => n.parent?.id === knownParentId)` for page-level filtered queries.

- **G-2 Direct property reads on known SACRED leaves are safe**. `getNodeByIdAsync("541:NNN")` returning the leaf node, then reading `.width`, `.height`, `.fills`, `.characters` etc — all safe. Only `.children` recursion is broken.

- **G-3 TEXT character cap 20480 chars**. Any write that would push TEXT.characters past 20480 silently truncates. Pre-check `current charsLen + delta` vs 20480. Split TEXT at 85% threshold or risk silent truncation.

- **G-4 INSTANCE property assignment vs componentProperties read-only**. `instance.componentProperties = {...}` is WRONG (read-only getter). Correct: `instance.setProperties({...})`. Component property values write through setProperties; reads via `instance.componentProperties[propName].value`.

- **G-5 VECTOR clone safe; GROUP clone safe when isolated**. `node.clone()` on VECTOR or isolated GROUP preserves fills bound variables intact. Clone on fused parent (the parent of complex composition containing rectangle bg + other children) loses bound variables on inner descendants. When cloning GROUP, verify clone's inner VECTOR/RECTANGLE fills.boundVariables.color preserved per child.

- **G-6 INSTANCE main reference**. `instance.mainComponent` returns the COMPONENT node (or null if detached). To check what SET an INSTANCE belongs to: `instance.mainComponent.parent?.type === "COMPONENT_SET"` then `instance.mainComponent.parent.id` is the SET id.

- **G-7 Font name lookup on existing TEXT**. To preserve existing TEXT's font when modifying: `const fontName = n.getRangeFontName(0, 1)` then `await figma.loadFontAsync(fontName)` before any `n.characters = ...` or `n.textStyleId = ...`. Multi-style TEXT requires `n.getStyledTextSegments(["fontName"])` to get all distinct fonts.

- **G-8 textAutoResize behavior**. `text.textAutoResize` values: `"NONE"` (fixed w+h), `"HEIGHT"` (fixed w, h grows), `"WIDTH_AND_HEIGHT"` (both grow). Default for createText is HEIGHT. Setting characters before textAutoResize set may produce unexpected dimensions.

- **G-9 Autolayout child positioning**. If `parent.layoutMode !== "NONE"`, child x/y are computed by autolayout — explicit assignments silently fail and get overwritten on next layout pass. To insert child at specific position in HORIZONTAL or VERTICAL autolayout, use `parent.insertChild(index, child)`. Container width math for HORIZONTAL FIXED layout with N children: `total = N × childWidth + (N-1) × itemSpacing + paddingLeft + paddingRight`. Standard Row 1/Row 2 autolayout in Comparison Blocks: paddingLR=48, itemSpacing=40, childWidth=402.

- **G-10 Instance preview ≠ rendered output**. Three known cases: (a) instance overrides during property set may not preview correctly until forced re-render via property change ping; (b) fills opacity override on INSTANCE child propagates only after re-binding via setProperties; (c) per-node opacity (`node.opacity` distinct from `fills[0].opacity`) is durable against fill reconciliation while fills.opacity is not. Cases (a) and (b) discovered chain 51-52; case (c) discovered chain 54 Pagination Dots passive ellipse.

- **G-11 Photo Background instance-resize quirk**. Post-closure surgical fix discovered chain 54 D-010: build chats 52-53 had resized Photo BG instances to 492×874 at x=-45, doubling the master's internal bleed offset. Always reset Photo BG instances to native dims (402×874 at 0,0) — let the master handle internal bleed.

- **G-12 Page-parent commit ordering**. When creating new frame hierarchy via Plugin API, parent frame MUST be appended to page tree (`figma.currentPage.appendChild` OR `explicitPage.appendChild`) BEFORE any child operations. Children appended to a frame that hasn't been committed to the page tree become orphaned silently between plugin calls. Pattern: `const f = figma.createFrame(); f.name = "X"; f.resize(...); page.appendChild(f); /* NOW safe to add children */ const child = figma.createText(); f.appendChild(child);` Verify by checking `f.parent` after every appendChild — should never be null mid-construction.

- **G-13 Top documentation row composition**. Comparison Block umbrella, mini-DS frame, and per-section doc frames composed in top documentation row at y=-7338 (above standard y=120 row). Top row contains all per-section doc frames (mini-DS) side-by-side with x growing rightward per section. Main visual row contains Comparison Blocks (umbrellas with Row 1 SACRED + Row 2 REBUILD) stacked vertically by section.

- **G-14 Column alignment for slot positions in Row 1/Row 2**. With paddingLeft=48, itemSpacing=40, childWidth=402: slot 0 starts at x=48; slot N starts at x = 48 + N × (402 + 40) = 48 + N × 442. For 8-screen section row total = 8 × 402 + 7 × 40 + 2 × 48 = 3216 + 280 + 96 = 3592. For 9-screen section row = 9 × 402 + 8 × 40 + 2 × 48 = 3618 + 320 + 96 = 4034. Slot N with non-standard dims (350×293 Message screen) breaks the formula — uses x calculated from prior slots cumulatively.

- **G-15 Cross-page getNodeByIdAsync without loadAllPagesAsync**. In current Plugin runtime, `await figma.getNodeByIdAsync("X:Y")` returns nodes from any page in the document without first calling `loadAllPagesAsync`. Verify via boot-time probe: `getNodeByIdAsync("2931:4").name === "01 Router"` confirms cross-page access. If null returned, only THEN try `await figma.loadAllPagesAsync()` and re-probe.

- **G-16 PNG byte threshold scales with frame size**. 5000-byte PNG sentinel threshold per L-55 is calibrated for REBUILD frames размера 402×874 (full screen). For smaller frames proportionally smaller thresholds:
  - Frame 402×874 → 5000 bytes minimum
  - Frame 336×179 → ~2000 bytes minimum
  - Frame 160×104 → ~1000 bytes minimum
  - Frame 145×50 → ~300 bytes minimum
  - Frame 64×36 → ~150 bytes minimum
  
  Exact threshold depends on content complexity. Anomalously low bytes (<100 for non-trivial frame) — flag for visual inspection (per L-52 internal supervisor concern, not user delegation). Not anomalously low — may be normal for small simple component.
  
  Provenance: chain 67 supervisor flagged SecBtn 145×50 = 149 bytes as anomaly, attempted to delegate user visual check. User refused, L-52 codified. Reality check: 149 bytes for 145×50 simple pill button — acceptable per scale.

- **G-17 INSTANCE setProperties API rules**. setProperties({propName: value}) is the working API. Common patterns:
  - Variant axis: `setProperties({Variant: "Practice"})` — propName = ось variants property
  - Text override: `setProperties({"Label#NNN:M": "Подробнее"})` — propName = node-level property id с #NNN:M суффиксом
  - Boolean: `setProperties({"Show Icon#NNN:M": false})`
  - Instance swap: `setProperties({"Avatar#NNN:M": iconComponent.id})`
  
  Component property keys получаются через `set.componentPropertyDefinitions` (на COMPONENT_SET) или `component.componentPropertyDefinitions` (на single COMPONENT). Чтобы быть надёжным в scope-lock — orchestrator делает probe componentPropertyDefinitions для каждого SET перед authoring scope-lock'а, документирует exact property keys в scope-lock.
  
  Provenance: chain 67 `setProperties({title})` на Card Default variant не сработал silent no-op (нет такой property у Default; нужен был Variant=Practice с правильным property key). Воркер не surfaced ошибку.

- **G-18 Cold export anomaly**. Первый exportAsync вызов на новой ноде после plugin runtime warm-up может вернуть PNG значительно меньшего размера чем последующие вызовы той же ноды с теми же параметрами. Это артефакт Figma render cache, не реальная проблема визуализации.
  
  Mitigation для supervisor PNG byte sentinel (L-55):
  - **Warm-up pattern**: один dummy exportAsync before measurement (на любой valid ноде, результат игнорируется), затем reliable measurements
  - **OR double export**: export same node twice, use second result
  - **OR sequence**: если экспортируешь несколько нод подряд, первая получает cold cache anomaly, остальные нормально — учитывать при interpretation
  
  Provenance: chain 69 Шаг 3 supervisor PNG sentinel — 01_Welcome первый export 6483 bytes, второй 124910 bytes на той же ноде с теми же параметрами. Семь других Onboarding REBUILDs давали consistent результаты, потому что 01_Welcome был первым в probe-call'е.

- **G-19 Figma INSTANCE detachment on mainComponent delete**. Когда удаляется COMPONENT или COMPONENT_SET, **все INSTANCE'ы которые на него ссылались автоматически detached в обычные FRAMEs Figma движком**. Они сохраняют визуальные свойства (children, fills, dims, geometry) но теряют:
  - `mainComponent` reference (становится null или undefined)
  - `componentProperties` API (больше не доступен)
  - variant switching ability
  - DS cascade при изменении master компонента
  - `setProperties()` perception (просто ignored — это уже не INSTANCE)
  
  **Это означает**: уничтожение DS компонента — не только потеря компонента, но и **тихое разрушение всех REBUILDs которые его инстанцировали**. PNG визуально может выглядеть похоже (Figma сохранила last-rendered fills), но архитектурно — это обычные FRAME'ы без DS связей.
  
  Mitigation после любого destructive DS operation: probe всех REBUILDs которые potentially использовали удалённый компонент. Каждый бывший INSTANCE который теперь `type === "FRAME"` — это разрушение, требующее rebuild через новый INSTANCE.
  
  Provenance: chain 69 удаление VELO_DS уничтожило 8 COMPONENT_SETs + 3 standalone. Все 8 Onboarding REBUILDs (`2542:4` .. `3037:2`) имели INSTANCE'ы этих компонентов — после catastrophe Figma детачнула их в FRAMEs. Probe показал: 01_Welcome 5 children все стали FRAME/TEXT, ни одного INSTANCE. Архитектурно Onboarding REBUILDs больше не Layer 3 — они теперь visual placeholders без DS связей. PNG sentinel 01_Welcome 3861 bytes consistent — это уже не G-18 cold export, это реальная visual deterioration после detachment.

---

# §8 — METHODOLOGY: OPERATING CONVENTIONS (Section F)

**Working language**. User communicates primarily in Russian. Orchestrator and supervisor reply in Russian. Voiceback after boot in Russian (3-4 lines, or 6-8 lines per L-44 format). If user writes in another language, match that language for the reply. Technical strings, node IDs, lessons, MD artifacts — English.

**Response style**. Concise prose by default, no bullets unless user explicitly asks. Inline lists use natural phrasing like "first ... second ... third ..." rather than markdown bullets. Full questions written as sentences (or Q-N format per §3 if decision questions). Status reports use compact prose paragraphs, not headed lists. Tables fine only when comparing genuinely tabular data.

**MD artifact convention**. Every prompt for a work-chat MUST be delivered as an MD file artifact via the `create_file` tool, saved to `/mnt/user-data/outputs/`, then surfaced via `present_files`. NEVER inline a work-chat prompt as plain text in the chat message. Reason: user copies the artifact to give to the work-chat as a clean self-contained input; inline prompts break the workflow. The orchestrator's own chat-side commentary about the prompt (summary of what it does, key decisions, expected outcome) remains in the chat message — not in the MD. **Scope-lock MD MUST be marked "для supervisor pre-execution validate сначала" per L-54.**

**Validation discipline**. After every work-chat report, orchestrator runs an independent R-12 probe via `use_figma` tool to verify claims against actual Figma state. Do not accept work-chat self-reports without independent validation. If validation surfaces drift — fix orchestrator-side if surgical (≤ 5-10 operations), or surface to user with proposed correction work-chat scope if larger. Supervisor performs second-line independent validation in parallel chat **with PNG visual sentinel per L-55**.

**Quality threshold**. Do not propose "as-is" or "ship-at-achieved" when loose ends remain at end of chain. User caught this pattern multiple times across chains 54-65 + 67. If a finding surfaces in honest final review — fix it, don't argue acceptable severity. The cost of one extra surgical fix is always lower than the cost of user discovering the gap and re-opening the chain.

**Boot reading discipline**. Boot read order in this MD §2 boot procedures uses chunked-with-manifest pattern per L-37. Orchestrator probes child manifest first (id + name + charLen, no characters), then reads bodies individually by ID, and emits a BOOT READ MANIFEST report listing per-frame %read and any deferred items. Authoring scope-locks before manifest is closed is forbidden — silent truncation has caused multiple downstream rule violations in past chains.

**Worker bootstrap convention** (per L-47 chain 65 sunset of legacy 08 Worker Bootstrap frame pattern): every work-chat scope-lock IS the worker bootstrap — single comprehensive English MD containing all context (role + env probe + execution discipline + scope-specific instructions). No separate boot file. The user attaches one MD to a fresh worker chat. The MD itself asserts executor role in first lines.

**Production transparency convention**. Per L-44, orchestrator R-12 validation report at end of every work-chat cycle starts with one-line Production cycle summary visible to user. This is mandatory format, not optional preface. User-facing summary line stands separate from technical R-12 probe results — technical detail follows after summary.

**User communication standard** (per L-51 codification chain 65 + reinforcement chain 69). See §3 Q-N format. No infinite text quests. Max 3-4 active Q-N per message. **Q-N mandatory always when user decision required**, no exception "это просто да/нет, можно прозой". No terminology in Опции/Суть/Рекомендация. Options = full alternatives.

**Documentation discipline**. Project state lives in Figma (Roadmap, State, Sprint, Sections, Frontend Roadmap), not in this MD. This MD holds only methodology (rules). Strategy/state/roadmap changes go to Figma; rule changes go to MD. Drift between Figma state and MD rules — orchestrator's responsibility to re-sync per L-38.

---

# §9 — METHODOLOGY: COMPARISON BLOCK SPATIAL PATTERN (Section G)

Mockups_NEW (`789:2`) is the spatial workspace for section deliverables. Each section produces ONE persistent Comparison Block holding both reference (SACRED) and current (REBUILD) state. Per-section mini-DS frame holds doc state and lives **on Mockups_NEW next to its Comparison Block** per chain 64 convention (NOT migrated to Documentation per chain 65 decision; Documentation holds the navigation pointers via 01 Router and Section Library).

**Comparison Block structure**:
- Umbrella frame named "Comparison Block — СЕКЦИЯНАЗВАНИЕ" (e.g. "Comparison Block — Onboarding").
- Inside, top-down:
  - title TEXT (section name + SACRED root frame id reference)
  - Row 1 — SACRED: horizontal strip of N×PNG-exports at native 402×874 each, with 40px itemSpacing and 48px outer padding. For 8-screen section row = 3592 wide. No per-frame labels in Row 1.
  - Row 2 — REBUILD live: horizontal strip of N×REBUILD frames at native 402×874 each, same dims/padding/itemSpacing. These are the LIVE working REBUILD frames (same frames worker builds into during Phase B — single source of truth, not separate copies) so when DS components or REBUILD frames change, Row 2 reflects automatically.
  - Each Row 2 frame has a small label TEXT above it carrying the screen name (e.g. "01_Welcome", "02_Login").

**Mini-DS placement**. Positioned in top documentation row at y=-7338 (above standard y=120 row, per G-13). x-coordinate per section grows rightward as sections close. Onboarding mini-DS at (464, -7338).

**Persistence semantics**. Row 1 PNGs persistent until end-of-full-DS-rebuild. Row 2 references live REBUILD frames; changes propagate automatically. Comparison Blocks NEVER removed during normal section lifecycle (only at explicit user-directed structural cleanup; precedent chain 65 reset + chain 69 Dashboard cleanup).

**Population timing**. Row 1 PNGs exported and placed once at start of section Phase A (immediately after mini-DS creation). All N PNGs for the section exported in the same Phase A. Row 2 starts empty and gains one frame per shipped screen during Phase B — each Phase B work-chat that ships a screen places the resulting REBUILD frame into Row 2.

**D-044 ceremony**. In Phase C, visual-review-only against the already-populated Comparison Block. No row population happens in Phase C. User reviews row-by-row at 100% zoom per L-45 binding criterion, returns approve OR fix-list per screen. **Supervisor PNG visual sentinel happens BEFORE D-044 ceremony per L-55** — supervisor's own export + visual cross-check against Row 1 SACRED PNG must PASS, only then user D-044 is invoked. Apply fixes if any (often as separate work-chat per Такт 3 polish per L-50) and re-converge. After full-section approve, Phase D updates Progress Board and 05 State — Row 1 PNGs stay in place.

**Inter-section layout**. Sections stack vertically by roadmap order. Per-section x-coordinate is constant. Per-section umbrella y-coordinate grows downward by previous section umbrella height plus separator gap (~80px + 1px horizontal divider).

---

# §10 — METHODOLOGY: THREE-LAYER PIPELINE (Section H, CONSTITUTIONAL)

VELO is a three-layer system. Layers exist in strict one-way relationship; violations destroy the architectural intent. **This section is constitutional — every scope-lock must respect it.**

## Layer 1 — SACRED Mockups

The Mockups page `462:1104` contains canonical visual reference frames from the original product design — 9 SACRED root subtrees covering Onboarding (`541:1179`), Dashboard (`541:6648`), Calendar (`541:1553`), Profile (`541:2355`), Diary (`541:2816`), Messages (`541:2717`), Analytics (`758:1529`), Practices (`758:1950`), plus Master-side variants Dashboard-v2 (`758:3245`), Onboarding-v2 (`758:4318`).

**Layer 1 properties**: untouchable per F-68 / G-1. Read-only access via G-2 direct property reads (`getNodeByIdAsync` on known leaves) or page-level `findAllWithCriteria` with parent.id filter. NEVER use `.children` recursion on SACRED descendants — Figma Plugin API raises on certain SACRED subtrees.

**Layer 1 role**: canonical visual truth. What Layer 2 strives to match. What Layer 3 renders, indirectly through Layer 2 instances.

## Layer 2 — Design System (DS canon)

The dsPage `490:12` contains COMPONENT + COMPONENT_SET nodes plus variables + text styles. Components are derived from Layer 1 primitives + refined through audit cycles.

**Layer 2 properties**: live, modifiable during Phase A audit/enrichment cycles per L-50. Never modified during Phase B build cycles (workers consume DS, don't extend it). **Post chain 69 cleanup**: pruned to Onboarding-survival 13 components (8 SET + 5 standalone) + 6 text styles + 7 color variables. Scaffold `4110:316` provides 8-category structure for Stage 1+2 population.

**Layer 2 role**: canonical reusable building blocks. INSTANCEd by Layer 3 to produce on-page UI. Carry visual fidelity through DS-level properties (fill rgba, cornerRadius, strokes, effects, text styles, color variables) — NOT through Layer 3 raw clones.

## Layer 3 — REBUILDs

The Mockups_NEW page `789:2` contains REBUILD frames — the on-page rendering of Layer 2 components in compositional layouts mirroring Layer 1 visual intent.

**Layer 3 properties**: built via INSTANCEs of Layer 2 components only (per L-35 DS-First Build Mandate). NO raw clones from Layer 1 to Layer 3 (per L-35 + AP-1). Layer 3 frames assembled by worker chats per orchestrator scope-locks during Phase B. Comparison Block umbrellas wrap Row 1 (Layer 1 PNG exports for visual reference) + Row 2 (Layer 3 live REBUILDs). **Post chain 69 cleanup**: only Onboarding Row 2 REBUILDs remain (8 frames). All other section REBUILDs deleted.

## Core principles

- **One-way flow**: Layer 1 → Layer 2 → Layer 3. Never the reverse. Layer 3 cannot edit Layer 2; Layer 2 cannot edit Layer 1.
- **Promote-not-invent**: when Phase A surfaces a primitive needed for Layer 3 but missing from Layer 2 — clone-via-G-5 from Layer 1 into Layer 2 with documented provenance per L-40. Do not invent a new primitive without provenance.
- **Extend-not-duplicate**: when Layer 2 already has a similar SET, extend it with a new variant axis per AP-5 rename + appendChild pattern, don't create a parallel SET.
- **Fix-broken-DS-in-place**: when Layer 2 has drift (wrong rgba bound to wrong variable, wrong cornerRadius), fix the DS component, then cascade auto-updates all INSTANCEs in Layer 3.
- **Reuse-first / trace-fallback**: when extracting from Layer 1, first try direct clone of existing primitives; only if no usable primitive exists, trace by hand per L-40.
- **Variant correctness over resize** (per AP-7): probe DS for native variant matching SACRED dims before resorting to INSTANCE resize.
- **Explicit variant in scope-lock** (per L-53 + AP-8): every INSTANCE in scope-lock has explicit variant + full setProperties list.

## Master-side track

Same Three-Layer Pipeline applies against alternative SACRED roots (`758:3245` dashboard-v2, `758:4318` onboarding-v2, `758:1950` практики-master). DS canon is shared between user-side and master-side. Master-side track runs after all 8 user-side sections approved (currently only Onboarding closed; remaining 7 paused pending frontend prep complete + mockups resumption).

## F-68 SACRED untouchable

Absolute constraint. No write operation under any circumstance targets a node under Mockups page `462:1104`. Reads via G-2 only.

---

# §11 — LIFECYCLE CONVENTION

Per L-31 (4-phase template) + L-50 (3-stage workflow refinement) + L-54 (pre-execution gate) + L-55 (PNG visual sentinel). Each section follows mockups production lifecycle.

## Mockups Production Mode (lifecycle)

### Такт 1 / Phase A — Foundation (orchestrator-side, no worker)

Activities:
- Read SACRED root subtree for the section. Read Founder Fix Backlog section relevant to this section. Read GAP Backlog & Brand Reference for context.
- Probe SACRED root frame children via `findAllWithCriteria` page-level with parent.id filter (G-1 safe, F-68 respected)
- Populate SACRED Visual Index subsection for the section per L-41 with primitive catalog + clone-feasibility verdicts per L-40/L-42
- Audit DS canon for primitives needed by this section's SACRED. Per audit-keep convention: each post-Onboarding DS addition probed against SACRED's actual primitive usage; keep if matches, remove drift artifacts. Onboarding bedrock components keep without question.
- Execute surgical DS canon writes if gaps surface (clone-via-G-5 per L-40, SET extensions via AP-5, paint rebinds). ≤10 ops orchestrator-side per L-34. If >10 ops, surface to user with split proposal.
- Build mini-DS frame on Mockups_NEW with 3 sub-frames: References (Live DS Catalog block per L-36), Decisions (D-NNN log starting D-001 for section), Progress Board (screen status table)
- Create section's Comparison Block umbrella frame on Mockups_NEW (**NOT on Mockups page** — F-68 violation; chain 66 lesson)
- Export PNG of every SACRED screen in section. Place inside Row 1 of CB at native 402×874
- Position mini-DS at top documentation row y=-7338, x to right of last existing mini-DS
- Register new mini-DS pointer in 07 Sections
- Update 01 Router with new mini-DS location

Output: Phase A complete report → supervisor independent R-12 validation → user GREEN. Mini-DS + CB ready. DS audit complete with any drift surgical-fixed.

### Такт 2 / Phase B — Screen builds (worker, multiple chains)

Per L-50: worker chat per scope-lock. Per L-47: single comprehensive English MD per chat. Per L-43: 2-3 screens per chain default (target=2, ceiling=3). Per L-46: INFRASTRUCTURE-SCREENS EXCEPTION allows >3 by explicit user GREEN.

**Per L-54 — mandatory gate before worker chat opens**:
1. Orchestrator completes scope-lock MD with explicit variants per L-53 + correct INSTANCE choices per AP-7/AP-8 + coordinates from SACRED font probe per L-56
2. Orchestrator marks scope-lock "для supervisor pre-execution validate"
3. User pastes scope-lock to supervisor chat
4. Supervisor probes Figma against scope-lock claims
5. Supervisor PASS → worker chat opens with scope-lock
6. Supervisor FAIL → orchestrator fix → repeat

Activities per worker chat:
- Receive scope-lock MD as authoritative task definition
- Build N screens with DS-bound TEXTs (textStyleId + color variable per semantic role per L-30)
- Composition follows SACRED visual intent (R3) but binding uses DS values regardless of SACRED's binding state (L-30)
- Each INSTANCE explicit variant + setProperties per L-53
- Illustrations and DS-gaps marked explicitly per R4 (Illustration FRAME/GROUP named explicitly)
- Built REBUILD frames placed into Row 2 of section's Comparison Block (Row 2 IS working location, no separate REBUILD container duplication)
- Each Row 2 frame gets label TEXT above it carrying screen name
- Worker reports in chat as Russian prose paragraphs, no MD output from worker side

Output per worker chat: N REBUILDs built, log Decisions D-NNN in mini-DS Decisions sub-frame.

Orchestrator post-worker R-12: probe each worker-built frame, verify INSTANCE counts, mainComponent IDs, componentProperties, position, text content. PNG byte export for visual sentinel.

**Supervisor post-worker R-12 per L-55**: independent probe + own PNG export at scale 0.5 (with G-18 warm-up) + visual cross-check against Row 1 SACRED PNG. All four criteria must PASS (property + own byte + visual cross-check + Onboarding intact) for supervisor PASS.

### Phase C / D-044 ceremony

Visual review against Comparison Block (Row 1 PNGs from Phase A, Row 2 REBUILDs from Phase B). User reviews each Row 1 / Row 2 vertical pair at 100% zoom in Figma per L-45 binding criterion. **This is user's ONLY validation channel per L-52** — no intermediate DS canon / variant / sub-frame probes delegated to user. Returns approve OR fix-list per screen.

If fixes needed: surgical follow-up Такт 3 polish worker chat OR orchestrator-side surgical if ≤10 ops. Such polish chats also incorporate Founder Fix Backlog items for the section (typos, renames, copy edits, UX adjustments per founder direction).

Re-converge with user.

### Phase D / Section closure

Update Progress Board sub-frame to mark all section screens COMPLETE D-044 ✓. Update 05 State section progress overview. Optionally fold new DS-EVO items discovered during section into Active DS-EVO Queue. Register section CLOSED in 07 Sections + 04 Roadmap.

After closure, the next section per L-49 SACRED-native sequence starts Phase A.

---

# §12 — CHAIN HISTORY & PROVENANCE

Lessons in this MD have specific provenance — real failures or successful patterns from production chains 47-70.

**Chains 47-54** (Onboarding production):
- Established L-30..L-49 + R1..R9 + AP-1..AP-6 + G-1..G-15 + F-68 SACRED untouchable
- 8 Onboarding REBUILDs shipped, all D-044 ✓
- Quality standard for all subsequent DS work

**Chain 65** (project reset):
- Removed all post-Onboarding REBUILDs + Methodology frame migrated to MD
- Established L-47/L-48/L-49/L-50/L-51 codification pattern
- INFRASTRUCTURE-OPS exception established (L-34) + INFRASTRUCTURE-SCREENS exception established (L-46)

**Chain 66** (Dashboard Phase A):
- Orchestrator placed CB on Mockups page (SACRED) instead of Mockups_NEW — F-68 violation caught by supervisor R-12
- SVI body written to wrong node (header vs body) — caught by supervisor R-12
- Hirurgical fix landed clean (4 ops)
- Supervisor first independent R-12 cycle

**Chain 67-68** (Dashboard Phase B failure → DS audit pivot):
- Worker scope-lock had multiple ambiguities (variant pickup, AP-7 resize substitution, coordinate arithmetic without font probe, missing variant axis selections)
- Supervisor missed pre-execution validate (L-54 root cause)
- Supervisor gave property-only R-12 PASS without PNG visual sentinel (L-55 root cause)
- User D-044 caught 5 visual defects
- Supervisor attempted user-delegation of SecBtn visual check (L-52 root cause)
- User refused, demanded codification
- DS audit revealed deep issues — pivoted to full DS rebuild

**Chain 69** (cleanup + frontend prep pivot + catastrophe):
- Phase 1 (cleanup successful): Full DS cleanup (264 ops INFRASTRUCTURE-OPS per L-34): 117 components + 7 text styles + 125 color variables + all Dashboard artefacts removed. Onboarding survival list preserved (13 components: 8 SET + 5 standalone + 6 styles + 7 variables).
- Phase 2 (frontend prep pivot): Frontend Roadmap `4102:2` created (Stage 0-7 plan). DS Scaffold `4110:316` created (8 categories ready for population). Documentation re-synced to Frontend prep mode. Methodology v2 published.
- Phase 3 (CATASTROPHE): Supervisor noticed legacy VELO_DS frame (12700×12026) на dsPage, user identified as "мусорное". Supervisor attempted cleanup без internal-children-traversal (AP-9 violation). VELO_DS sub-frames had names "Forms / Navigation / Brand / Photo System" same as Scaffold categories (L-58 confusion). Supervisor probed COMPONENT_SETs saw `parentName: "Brand"` и assumed scaffold parent, на деле parent был sub-frame inside VELO_DS. Supervisor executed `veloDs.remove()` под INFRASTRUCTURE exception §2 Role 3 (AP-10 violation — destructive op without orchestrator scope-lock + L-57 manifest). Cascade: 8 COMPONENT_SETs + 3 standalone COMPONENTs uniqued, 8 Onboarding REBUILD INSTANCEs detached to FRAMEs (G-19 effect). Mandala + back-arrow survived only because preemptively promoted to scaffold categories. Undo не сработал. DS canon destroyed.
- Lessons codified chain 70 entry: L-57 (pre-destruction manifest), L-58 (same-name confusion guard), AP-9 (destruction without traversal), AP-10 (supervisor destructive overreach), G-19 (INSTANCE detachment cascade). All landed in v3.

**Chain 70** (post-catastrophe entry — mockups production resume):
- Frontend prep mode deprecated — removed from §11
- Methodology v2 → v3: добавлены L-57/L-58/AP-9/AP-10/G-19, ужесточён §2 Role 3 INFRASTRUCTURE exception, §1 navigation pointer переписан под post-catastrophe state, Frontend Prep Mode секция удалена per user directive ("ничего нельзя в общих контейнерах хранить")
- VELO_CHAIN_70_STATE.md создан как live state document (current Figma state + next action) — отделён от methodology (rules)
- Documentation rewrite Onboarding restart Phase A — next action chain 70

**Methodology evolution principle**: every L-NN / G-NN / AP-N / R-N in this document has concrete provenance — a real chain where the lack of this rule cost production work. No theoretical defenses against imaginary threats. Each rule closes a hole that already fired.

---

**End of VELO_METHODOLOGY.md v3.**

This document is the methodology foundation. Update only when methodology / roles / conventions change. Project state is in Figma; this file is loaded once per chat and remains stable across project lifecycle.

Next chain action: Onboarding Phase A restart — SACRED audit + DS rebuild from `541:1179`. Live state pointer: VELO_CHAIN_70_STATE.md (current Figma state + next action — обновляется per chain).
