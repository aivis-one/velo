# 03_Phase-Builder
> SPEC v3.2-velo | One phase = one chat. All cycles execute within.
> OPEN starts the phase, WORK executes cycles, CLOSE finishes the phase.

---

## Routing

```
Starting a phase?                    → OPEN
Executing cycle work?                → WORK
All cycles done, ready to close?     → CLOSE
```

Note: all three sections execute in the SAME chat. This file is loaded once at phase start. CLOSE is used at the end of the same chat.

---

## Before You Begin

Load in chat:

□ S{N}-SPRINT.md (current sprint)
□ 01_Declaration.md
□ Current P{NN}-{name}.md (only if this phase has an external file; most phases are inline in S{N}-SPRINT.md)
□ docs/01_refer/ARCHITECTURE.md (for Coding Standards reference — Rule 17)
□ docs/01_refer/ENVIRONMENT.md
□ docs/01_refer/decisions.md
□ 03_Phase-Builder.md (this file)

Additional loads if this is the last phase of the sprint:
□ docs/01_refer/BACKLOG.md

Check S{N}-SPRINT.md → Current State → confirm which cycle number is next.

This is a deterministic protocol — execute immediately after loading documents.
No Session Plan confirmation required (Rule 6).

---

# OPEN: Phase Start

## Purpose
Open the phase. Load context, plan all cycles, scout the full phase scope.
Runs ONCE at the start of the phase chat.

## Step 1: Session Plan

Output full plan for the phase — all cycles, all tasks, estimated sequence. Show which cycles are HIGH/MEDIUM/LOW risk and which can be batched. Tag each cycle by type: `standard` or `design-gen`.

Claude Chat outputs current Session Code.

No Human confirmation required (Rule 6 — deterministic protocol).

## Step 2: Combined Scout

Create ONE scout prompt (.md artifact per Rule 1) covering ALL phase tasks.
Claude Code reads:

□ All files and modules across all cycle scopes
□ Existing tests for all affected areas
□ Current state of any in-progress work
□ TODO/FIXME markers in scope
□ Coding Standards compliance in files to be touched
□ Patterns in existing code (output as Pattern References)
□ Relevant entries from `decisions.md` (lightweight flat log)
□ If cycle is `design-gen`: read Figma reference metadata, target view file, relevant tokens

Scout output per Rule 2 format, with **per-task scope blocks** so each execute prompt can reference "Scout §R2" instead of re-stating findings:
□ Confirmed scope (per task block — labeled by task ID)
□ Pattern references
□ Relevant decisions (from `decisions.md`)
□ Context / unexpected findings

**Practical ceiling:** ~20 files / ~3 related task blocks per combined scout. Beyond that, scout output becomes too long and findings blur together.

**Exception:** if phase tasks are in unrelated view files with no shared context, split into 2-3 focused scouts. Default: one scout.

**After Scout — STOP.** Claude Chat reviews findings, then proceeds to Step 3 or WORK.

## Step 3: Design Review

**Executor:** Claude Chat (runs automatically after Combined Scout validation — no separate Human trigger needed)
**When:** Last step of OPEN, before entering WORK.
**Output:** Inline in Claude Chat as part of Session Plan output (appended after last OPEN step).

Claude Chat runs a mechanical self-check on the phase plan. Two modes — determined automatically:

**Quick mode** (all of: ≤ 5 cycles AND all LOW/MEDIUM risk AND no carry-forward items):

| # | Question | Check |
|---|----------|-------|
| Q1 | Any cycle with incorrect Risk tier? | Review each cycle's tier against Declaration Rule 15 tier table |
| Q2 | Any scope collision between cycles (same files touched in unplanned ways)? | Compare cycle scope declarations |

Quick mode output: one-line answer per question (2 answers total), inline in chat.

**Full mode** (any of: ≥ 6 cycles OR any HIGH risk cycle OR carry-forward items present):

Runs all Quick questions plus:

| # | Question | Check |
|---|----------|-------|
| Q3 | Any carry-forward items affecting this phase scope? | Cross-check S{N}-SPRINT.md carry-forward section |
| Q4 | All HIGH-risk cycles have concrete acceptance criteria? | Each HIGH cycle must have at least one runnable check defined |
| Q5 | Any cycle where the goal statement contains more than one verifiable deliverable? | Flag if cycle goal has "AND [separate deliverable]" — split candidate |
| Q6 | Cycle order follows dependency order? | No cycle X that depends on output of cycle Y where Y comes after X |
| Q7 | For design-gen cycles: Figma reference approved, sponsor-scope alignment confirmed? | Each design-gen cycle must have both checks marked before entering WORK |

Full mode output: inline table:

| Cycle | Type | Risk Tier | Decision | Rationale |
|-------|------|-----------|----------|-----------|
| C{NN} | standard / design-gen | HIGH/MED/LOW | Confirmed / Tier corrected to X / Split into C{NN}a+b | [one line] |

**Escalation rules:**

| Finding type | Action | Human action (if STOP) |
|-------------|--------|----------------------|
| Tier correction (minor) | Claude Chat corrects in plan, notes in Review output, continues to WORK | N/A |
| Carry-forward scope adjustment (minor) | Claude Chat notes adjustment, continues | N/A |
| Cycle count change (add/remove cycle) | **STOP — Human confirmation required** | Confirm (proceed) or redirect (replan). One message. |
| LOW/MEDIUM → HIGH reclassification | **STOP — Human confirmation required** | Confirm (proceed) or redirect (replan). One message. |
| Design-gen precondition missing (Figma not approved / sponsor gap) | **STOP — Human confirmation required** | Confirm (replan) or authorize fast-track. |

If STOP triggered: Claude Chat presents finding + proposed resolution. Human responds with one message: confirm or redirect. Apply decision → proceed to WORK.

---

# WORK: Execute Cycles

## Purpose
Execute all phase cycles. Each cycle produces working code + tests.
No intermediate docs, no intermediate commits, no intermediate sprint updates.

## Cycle Types

Two cycle types exist in WORK phase:

### Standard cycle

Code change, refactor, test, doc. Follow Scout → Validate → Execute pattern per Rule 2. Risk tier per Rule 15.

### Design-gen cycle (Velo-specific)

Used for redesigning or creating a screen via Claude Design. Required precondition: Figma reference exists and is approved; screen is in sponsor-confirmed scope.

Steps:
1. **Ground:** open Figma reference, read its spec. Capture target screen name, route, role (user/master/admin), target file path (`frontend/src/views/<role>/<File>.vue`), and relevant tokens from `Design_prototype_legacy_2026-03-11/tokens.md`.
2. **Sponsor-spec cross-check:** verify the screen exists in the sponsor-approved functional scope. If missing or ambiguous → STOP, escalate to Human.
3. **Compose Claude Design prompt** (6 slots): artifact type, product, stage, structure (screens/states), tone, audience. Brand lock required — explicitly forbid cream/beige/serif/italic/terracotta/amber; require Marmelad + blue-slate + glass + radii 15/200/5/100.
4. **Attach context** before first generation: codebase link, Figma link, tokens file, reference screenshot.
5. **Generate** in claude.ai/design. Single variant first.
6. **Iterate** with Edit / Comment / Tweaks until visual parity with Figma. Do not regenerate unless direction is fundamentally wrong.
7. **Handoff** via "Handoff to Claude Code" export. Supply path `frontend/src/views/<role>/<File>.vue` and instructions to use existing tokens + conventions.
8. **Claude Code** fetches the bundle, scaffolds the Vue component, wires up to existing store + API client + guards.
9. **Verify:** `(cd frontend && npm run typecheck && npm run lint && npm run test)`, then visual check in dev server, then deploy to staging server (push to `new_desing`), final visual check in staging.
10. **Commit** as part of phase batch (CLOSE Step 4f).

Acceptance: visual parity with Figma, typecheck/lint/test pass, staging deploy renders correctly.

See `docs/01_refer/GUIDES/claude-design-pipeline.md` for the current execution playbook (updated each sprint from lessons learned).

## Per-Cycle Flow (standard cycles)

Risk determines ceremony level:

### HIGH / MEDIUM risk cycles
Scout (if not covered by Combined Scout) → Assess → Execute → Validate

- **Scout:** only if Combined Scout didn't cover this cycle's scope. Create scout prompt per Rule 1 + Rule 2 format.
- **Assess (mandatory for HIGH, advisory for MEDIUM):**
  **HIGH:** execute prompts include Assess step. Claude Code reads current state, confirms plan is feasible against actual code, outputs ASSESS REPORT → STOP → Human confirms → Execute. Non-negotiable.
  **MEDIUM:** Claude Chat judgment — if scout was recent and code hasn't changed between scout and execute, Assess may be skipped. If gap is large or scope is complex, include Assess. Human may override: "skip assess" or "add assess."
- **Execute prompt:** .md artifact per Rule 1, with full header (Risk/Scope/Anti-scope/Phase). Pre-Execution Validation per Rule 12. MUST NOT include git commit/push steps — deferred to CLOSE. Include Completion Signal per Rule 24.
- **Validate:** Claude Code runs tests, Claude Chat checks results. If validation fails → fix before next cycle.

### LOW risk cycles
Execute only. Scout findings already available from OPEN Step 2.

- Execute prompt may omit separate scout.
- Assess may be skipped (LOW risk = config, docs, formatting).
- MUST NOT include git commit/push steps.
- Include Completion Signal per Rule 24.
- Verify: one-liner command confirming done.

### Task Batching
Multiple LOW-risk tasks MAY be combined into a single execute prompt when they share no file conflicts and have no decision gates between them. Claude Chat judgment — not mandatory, not prohibited.

**Practical ceiling:** 3-4 LOW tasks per prompt. For code tasks (even LOW), 2 is safer. For pure doc tasks (backlog updates, token tweaks), 4-5 is fine. If any single task might fail → keep it separate so failure doesn't block the batch.

**Scope:** These ceilings apply to batching multiple tasks within ONE cycle. Cross-cycle merging is governed by Rule 16 (decision-gate test) and Batch Prompt Delivery below — not by task count limits.

### Batch Prompt Delivery

After Combined Scout (OPEN Step 2), Claude Chat creates ONE combined execute prompt covering all phase cycles as sequential sections — instead of creating separate prompts per cycle.

**When to use (default for single-stream phases):**
- Combined Scout covered all cycle scopes
- No decision gate between cycles (Rule 16 test: Claude Chat will NOT review output of cycle N before cycle N+1 — all derived from same scout)

**Combined prompt structure:**
One .md artifact with sequential cycle sections:

```
# P{NN} Combined Execute — [Phase Name]
## §C{NN}: [cycle name]
[Pre-Execution Validation, intent, tasks, acceptance criteria]
## §C{NN+1}: [cycle name]
[Pre-Execution Validation, intent, tasks, acceptance criteria]
...
## Completion Signal
[Aggregate: all cycles DONE/FAILED]
```

One file = one copy-paste to Claude Code. No multi-message delivery.

**Rules:**
- Claude Code executes sections in order — not in parallel
- Each section's Pre-Execution Validation runs against actual codebase state (which includes changes from prior sections)
- Each section's Acceptance Criteria verified before proceeding to next
- If any section FAILS → Claude Code STOPS and reports. Does not continue.
- HIGH risk sections retain Gather → Validate → Apply staging inside Claude Code
- Consolidated report at the end replaces per-cycle reporting to Claude Chat

**What changes vs per-cycle prompts:**
- ONE prompt instead of N separate files
- Claude Chat reviews ONE consolidated report
- Verification Scout (CLOSE Step 2) becomes the primary quality gate
- Faster wall-clock time (no Human round-trips between cycles)

**What does NOT change:**
- Combined Scout still required before the combined execute prompt
- Pre-Execution Validation still in every section
- Acceptance Criteria still in every section
- CLOSE protocol unchanged (verification scout + phase close)
- Risk tiers unchanged (HIGH still gets staged execution within its section)

**When NOT to use:**
- Scout findings were incomplete or uncertain — build sections incrementally
- Cycles have genuine decision gates (output of N determines content of N+1)
- Context overflow risk — combined prompt exceeds Claude Code context window
- Design-gen cycles are interactive (Claude Design prompts issued by Human in claude.ai/design) — batch across design-gen cycles is not applicable

## Rules During WORK
- No cycle doc creation (deferred to CLOSE)
- No S{N}-SPRINT.md updates (deferred to CLOSE)
- No git commit (deferred to CLOSE)
- Execute prompts MUST NOT include git commit/push steps
- If Claude Code reports unexpected issues → Claude Chat decides: fix now, defer to `BACKLOG.md`, or escalate to Human

## Crash Recovery

For phases with >5 cycles or >1 day duration, Human may request an intermediate commit checkpoint at any point. At that checkpoint:
- git add + commit + push (all accumulated changes)
- Update S{N}-SPRINT.md Current State (which cycles DONE)
- Resume WORK in same chat after checkpoint

This is a safety valve, not standard flow.

**Deploy-prelude commits (pre-authorized):**

A mid-phase commit is authorized without invoking §Crash Recovery when:
(a) The commit contains only output required by an upcoming staging-deploy verification (Velo deploys on push to `new_desing`)
(b) The committed content is atomic and tested (no partial state)
(c) The commit does not touch files owned by other concurrent cycles
(d) Commit message explicitly cites: `deploy-prelude: [description] — required for [cycle ID] staging verification`

Deploy-prelude commits do not reset the "batch at phase close" discipline for other cycles — only the specific pre-deploy output is committed early.

Canonical case for Velo: design-gen cycle C{NN} produces a new screen that the Human wants to visually verify on staging before finishing remaining phase cycles.

---

# CLOSE: Phase Finish

## Purpose
Close the phase. Verify all work, create all docs, commit everything, close chat.
Runs ONCE after all WORK cycles are done.

## Step 1: Phase Verification

Apply Validation Anti-Bias (Rule 22).

□ All tasks from the phase completed (per S{N}-SPRINT.md Phase section or P{NN}-{name}.md Tasks)
□ All tests passing (full suite or affected subset)
□ No TODO/FIXME left in code touched this phase
□ New code follows Coding Standards from `ARCHITECTURE.md`
□ No logic duplication introduced
□ For design-gen cycles: visual parity with Figma verified on staging

If new modules/components were created OR this is the last phase:
□ Architecture compliance check (two-way):
  Direction 1 — Doc reflects Code (`ARCHITECTURE.md` describes what exists)
  Direction 2 — Code follows Architecture (module boundaries, patterns)
□ `FILE-TREE.md` verify against filesystem (if drift suspected)

If anything incomplete → fix before proceeding.

**Triaged-deferral close (valid §1 outcome):**

A phase may close with incomplete tasks when ALL of the following hold:
(a) Sprint goal was reframed mid-flight and deferred tasks no longer serve the current goal
(b) Every deferred task has a corresponding open `BACKLOG.md` entry
(c) Deferred tasks are enumerated in the phase RETRO or cycle doc Result section
(d) Commit message explicitly cites: `§CLOSE §1 deviation: triaged-deferral — [reason]`

This is NOT a shortcut for incomplete work. All deferred items must be persisted — verbal intent in chat without a written record does not exist.

## Step 2: Verification Scout

ONE verification scout covering ALL files changed across ALL cycles in this phase. Create scout prompt (.md artifact per Rule 1).

Claude Code checks:
□ Coding Standards (Rule 17) across all touched files
□ Logic duplication across all new code
□ Linter (if configured in ENVIRONMENT.md)
□ Tests: all passing, new functionality has tests
□ No TODO/FIXME or placeholder code
□ New modules/components list (for `ARCHITECTURE.md` update)

Scope: git diff from phase start. Not the whole codebase.

After Scout — STOP. Claude Chat reviews. Fix issues if found.

## Step 3: Session Review

Claude Chat scans the chat:
□ Deferred items ("do later", "next chat")?
□ Unrecorded decisions?
□ Any protocol step that felt awkward or unclear?

Findings exist → include in Close Prompt (Step 4e). No findings → record "Session Review: nothing to persist."

## Step 4: Close Prompt

ONE execute prompt (.md artifact per Rule 1) that does everything.
Include Completion Signal per Rule 24.

### 4a. Create ALL cycle docs (batch) — optional

In Velo profile, separate `C{NN}-{name}.md` files are created ONLY for cycles whose Result section exceeds 5 lines or captures non-trivial decisions. Otherwise, cycle outcomes live inline in the Phase section of `S{N}-SPRINT.md` (or `P{NN}-{name}.md` if phase has an external file).

When created, path:
```
docs/03_sprint/S{N}-[name]/P{NN}-[name]/C{NN}-{name}.md
```

Lightweight template (Tier 4):

```markdown
# Cycle C{NN}: [Name]
> Phase [N]: [Phase Name] | Sprint [N]: [Sprint Name]
> Type: standard | design-gen
> Status: DONE

## Goal
[one sentence]

## Result
[2-3 sentences: what was done, what changed, notable decisions]

Status: DONE
Closed: [date]
```

Detail (steps, scout findings, Claude Design prompt variants) lives in the chat history and can be reconstructed. Cycle docs capture the outcome, not the process.

### 4b. Update P{NN}-{name}.md (only if exists)

If a `P{NN}-{name}.md` external file was created for this phase:
- All Cycles table rows → DONE with dates and one-line results
- Phase status → DONE
- Phase closed date and summary

If phase is inline in `S{N}-SPRINT.md` — skip, handled in 4d.

### 4c. Update ARCHITECTURE.md (if needed)

New modules/components → add to relevant section. Plain update with current date.

### 4d. Update S{N}-SPRINT.md

Current State:
```
| Phase | [N]: [name] — DONE |
| Cycle | C[last]: [name] — DONE |
| Status | Ready for next phase / Sprint complete |
| Tests | [N pass / N fail / N skip] |
```

Protocol Log — one row per cycle:
```
| S{N}-P{NN}-C{NN} | 03_Phase-Builder | [date] | DONE |
```

Phase section Cycles table: all rows → DONE with date and one-line Result.

Last Session: 3-5 sentences covering the entire phase.
Next Action: [from Step 5 routing]
For Human: [per Declaration template]

### 4e. Persist findings

If deferred items → append to `BACKLOG.md` via execute prompt.
If decisions were reached → append to `decisions.md` via execute prompt.
If no items → skip.

### 4f. Commit and push

```
git add [all modified files — code + docs from entire phase]
git commit -m "phase: P{NN} {name} — DONE"
git push
```

ONE commit for the entire phase.

### 4g. For Human

Per Declaration template:

```
## For Human
> Next chat instruction. Copy-paste.

**Session Code:** [next]
**Load:**
1. Framework: 01_Declaration.md + [next protocol].md
2. Project: ENVIRONMENT.md + ARCHITECTURE.md
3. Sprint: S{N}-SPRINT.md [+ P{NN}-{name}.md if applicable]
**Run:** [next protocol] — [first step]
```

## Step 5: Routing

```
Last phase of sprint?
├── YES → Sprint Readiness Check:
│    □ S{N}-SPRINT.md Success Criteria — all met?
│    □ Quality tools from ENVIRONMENT.md ready for 04_Sprint-Closer?
│    □ All known CRITICAL issues resolved?
│    If any NO → log blocker in S{N}-SPRINT.md Last Session.
│    Then: next = 04_Sprint-Closer
│    next Session Code: S{N}-Sprint-Closer
│
└── NO  → next phase
         next Session Code: S{N}-P{NN+1}-C{NN+1}
```

Output current Session Code. Include next Session Code in For Human.

---

## Chat Boundary — MANDATORY STOP

After Step 5 — this chat is DONE. Close it.

Do NOT start the next protocol in this chat.
Next phase or protocol = new chat.
Load S{N}-SPRINT.md → read Next Action → proceed.

---

## Architectural Cleanliness Principle

> Default: cleanliness over minimal patch.

When choosing between implementation options, prefer architectural cleanliness over a quick in-place edit. Resolve legacy rather than inherit it.

### Rationale

Deep code inspection during prior Velo tech-debt sprints revealed that "minimal patches" accumulate into structural debt: passthrough components, event-name mismatches, service layers that exist descriptively but not functionally, two-layer attachment gaps, doc-location drift. The cost of surfacing and fixing these at integration time exceeds the cost of cleaner original implementation by several multiples.

### Examples

Prefer cleanliness:
- Named event bus over implicit convention matching
- Dedicated composable over overloaded method on an unrelated store
- Typed API contract (`frontend/src/api/types.ts`) over free-form response parsing downstream
- Explicit prop/event flow through components over implicit context magic
- One source of truth per domain (single Pinia store) over scattered refs

Minimal patch still acceptable when:
- Refactoring introduces risk disproportionate to the task scope
- Existing code consistently follows the minimal pattern and consistency wins over uniformity
- Explicit scope boundary of the cycle prohibits refactoring (rare — scope boundaries are usually advisory, not hard)
- The "clean" option is speculative / preemptive abstraction (YAGNI wins against over-engineering)

### Enforcement

Claude Chat surfaces the choice when writing Scout, Assess, and Execute prompts:
- Scout reports where the two options diverge
- Assess presents both options to Human with trade-offs
- Execute prompts name the chosen approach in the Decisions table

Human may override per-cycle. Default is cleanliness.

---

[*] 03_Phase-Builder SPEC v3.2-velo * ready
One phase = one chat. All cycles execute within.
OPEN: session plan + combined scout (once)
WORK: execute cycles — standard | design-gen; assess/exec/validate per risk tier
CLOSE: verify + batch docs (optional) + one commit + close chat
