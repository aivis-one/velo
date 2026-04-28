# 03_Phase-Builder
> SPEC v3.2.0 | One entry stream = one chat. All cycles execute within.
> OPEN starts the phase, WORK executes cycles, CLOSE finishes the phase.

---

## Routing

Starting a phase?                    → OPEN
Executing cycle work?                → WORK
All cycles done, ready to close?     → CLOSE

Note: all three sections execute in the SAME chat. This file is loaded once
at phase start. CLOSE is used at the end of the same chat.

**Multi-Entry Note:** If a phase has multiple entries (parallel streams),
each entry = separate chat. CLOSE runs only after ALL entries report DONE.
The last entry to finish runs the full CLOSE with phase verification.
Single-entry phases (most common) ignore this — one chat covers everything.

---

## Before You Begin

Load in chat:

□ S{N}-SPRINT.md (current sprint)
□ 01_Declaration.md
□ Current P{NN}-{name}.md
□ ARCHITECTURE-BOGAME.md (for Coding Standards reference — Rule 17)
□ KB L2 files and ADR files referenced in current P{NN}-{name}.md tasks (if any)
□ docs/01_refer/ENVIRONMENT.md
□ 03_Phase-Builder.md (this file)

Additional loads if this is the last phase of the sprint:
□ ROADMAP-BOGAME.md
□ VISION-BOGAME.md

Check S{N}-SPRINT.md → Current State → confirm which cycle number is next.

This is a deterministic protocol — execute immediately after loading documents.
No Session Plan confirmation required (Rule 6).

---

# OPEN: Phase Start

## Purpose
Open the phase. Load context, plan all cycles, scout the full phase scope.
Runs ONCE at the start of the phase chat.

## Step 1: Session Plan

Output full plan for the phase — all cycles, all tasks, estimated sequence.
Show which cycles are HIGH/MEDIUM/LOW risk and which can be batched.

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
□ KB/ADR references from P{NN}-{name}.md for all tasks
  (per Rule 18 — L2 content enters via scout, not execute prompt)
□ L1 INDEX files for KB/ADR domains referenced in P{NN}-{name}.md:
  - ADR refs → load BOGAME-ADR-INDEX.md (resolves ADR-NNN → actual filename)
  - KB refs → load {DOMAIN}-INDEX.md (resolves topic → actual filename)
  Path: docs/01_refer/KNOWLEDGE/ADR-BOGAME/BOGAME-ADR-INDEX.md
  Path: docs/01_refer/KNOWLEDGE/KB-{DOMAIN}/{DOMAIN}-INDEX.md
□ If any task touches DB tables — Rule 7 checks:
  schema, migration SQL, cross-validation

Scout output per Rule 2 format, with **per-task scope blocks** so each
execute prompt can reference "Scout §R2" instead of re-stating findings:
□ Confirmed scope (per task block — labeled by task ID from P{NN}-{name}.md)
□ Pattern references
□ Relevant ADR/KB refs
□ Resolve ADR-NNN to actual L2 filenames via L1 INDEX (BOGAME-ADR-INDEX.md)
  before attempting to read ADR files (ADR files use topic-based names, not ADR-NNN.md)
□ Context / unexpected findings
□ KB/ADR Assessment (per-ref: Applicable / Not applicable / Conflict)

**Practical ceiling:** ~20 files / ~3 related task blocks per combined scout.
Beyond that, scout output becomes too long and findings blur together.

**Exception:** if phase tasks are in completely unrelated codebases with
no shared context, split into 2-3 focused scouts. Default: one scout.

**Stream scope enforcement (Rule 23):** if the phase has multiple entries,
scout ONLY files within this entry's scope.

**After Scout — STOP.** Claude Chat reviews findings, then proceeds to Step 2.5 or WORK.

## Step 2.5: Design Review Consultation (conditional)

**When to run:**
Run when the phase meets ANY of:
- Has at least one HIGH-risk cycle
- Has 4 or more cycles total
- Cycles touch interlocking modules (shared registry, middleware, ABC, lifespan)

Skip when: phase is pure-LOW (doc/version/changelog only) AND has ≤3 cycles in isolated scope.
Record skip reason in Protocol Log: "Step 2.5: skipped — [pure-LOW / ≤3 isolated cycles]"

**Purpose:**
Claude Code reviews the planned approach before execute prompts are written.
Catches: feasibility gaps, hidden coupling, risk-tier misclassification, cleaner alternatives.
Claude Chat retains final authorship and decision authority (Declaration §Roles and Boundaries).
Claude Code is advisory — not co-author.

**Procedure:**

1. **Claude Chat compiles Phase Design Brief** (.md artifact per Rule 1, not inline text).

   Template (1B shape — one section per cycle):
   ```
   # Phase Design Brief — P{NN} {name}
   ## Cycle {ID}: {name}
   - Intent: [one sentence — what to achieve]
   - Approach: [chosen implementation approach]
   - Risk tier: HIGH / MEDIUM / LOW
   - Alternatives considered: [list or "none"]
   - Open questions: [list or "none"]
   ```

2. **Claude Chat sends Brief to Claude Code** as consultation prompt (read-only, no execute).

   Consultation prompt header (mandatory):
   ```
   Type: consultation (read-only — no file changes, no commits)
   ATTENTION: You are reviewing a plan written by Claude Chat.
   You are biased toward approving it. Compensate: assume design problems exist.
   Hunt for: feasibility gaps, hidden coupling, risk-tier errors, cleaner alternatives.
   Disagreement is expected and valuable. Agreement requires justification.
   ```

3. **Claude Code returns structured feedback** covering per-cycle:
   - (a) Feasibility: any blocker from actual codebase state?
   - (b) Risk-tier sanity: is assigned tier correct?
   - (c) Cleaner alternative: obvious from code?
   - (d) Hidden coupling: what Claude Chat missed?
   - (e) Suggested cycle split/merge
   - (f) Explicit disagreements (not just concerns)

4. **Claude Chat integrates feedback** into final per-cycle execute prompts.
   - Material disagreements that conflict with prior ADR/Architecture → escalate to Human
   - ADR conflicts not resolvable in this phase → log as "v1 pending Brain-Next" in cycle doc, proceed with current plan
   - Non-material disagreements → Claude Chat decides and records rationale in cycle doc

5. **Capture:** After WORK begins, add to the first cycle doc:
   ```
   ## Design Review (Step 2.5)
   Run: YES / SKIPPED ([reason])
   Disagreements: [N] — [brief list or "none"]
   Material changes to plan: [list or "none"]
   ```
   Minimal record only — no full transcript.

**Anti-bias enforcement (Rule 22):**
If Claude Code returns 0 disagreements on a phase with ≥1 HIGH-risk cycle:
Claude Chat MUST issue an adversarial re-prompt:
```
You returned 0 disagreements on a HIGH-risk phase. This is statistically unlikely.
Re-examine the plan assuming at least one design flaw exists.
What did you miss?
```
Record adversarial re-prompt result in cycle doc Design Review section.

**Time cost:** ~5-15 min per phase (one consultation round-trip + integration).
**Rule compliance:** Consultation is a specialized scout (read-only) — fits Rule 2 Scout→Validate→Execute spirit.
One-protocol-one-chat applies: consultation runs in same chat as OPEN.

**Precedents (where this would have caught issues earlier):**
- P81 C367 (HIGH): 3 deviations accepted at Assess (auto_discover called in two places, 4 projects vs 1 assumed, TelegramService≠TelegramPlugin). Each would have been design input at OPEN time.
- P81 C364: §0.5 NodeRegistry investigation R1-R4 was structurally bolted onto the cycle as "investigate-then-decide" — recognition that the design needed code-research before fixing, but too late to use as plan input.
- P82 C383: ASSESS A11 found 5-12 min outage in prompt-as-written vs ~1s in DEPLOY-DISCIPLINE §4 zero-downtime pattern. Caught in time only because A11 was added defensively post-validation.

## Step 3: Design Review

> Distinct from Step 2.5 Design Review Consultation. Step 2.5 = external advisory (Claude Code reviews plan against codebase). Step 3 = Claude Chat mechanical self-check on the plan itself (risk-tier correctness, scope conflicts, deliverable atomicity). Both coexist; Step 3 is always-on, Step 2.5 is conditional.

### Design Review

**Executor:** Claude Chat (runs automatically after Combined Scout validation — no separate Human trigger needed)
**When:** Last step of OPEN, before entering WORK.
**Output:** Inline in Claude Chat as part of Session Plan output (appended after last OPEN step).

Claude Chat runs Design Review on the phase plan. Two modes — determined automatically:

**Quick mode** (all of: ≤ 5 cycles AND all LOW/MEDIUM risk AND no carry-forward items):

| # | Question | Check |
|---|----------|-------|
| Q1 | Any cycle with incorrect Risk tier? | Review each cycle's tier against Declaration Rule 15 tier table |
| Q2 | Any scope overlap between entries (Rule 23)? | Compare entry scope declarations |

Quick mode output: one-line answer per question (2 answers total), inline in chat.

**Full mode** (any of: ≥ 6 cycles OR any HIGH risk cycle OR carry-forward items present):

Runs all Quick questions plus:

| # | Question | Check |
|---|----------|-------|
| Q3 | Any carry-forward items affecting this phase scope? | Cross-check S{N}-SPRINT.md carry-forward section |
| Q4 | All HIGH-risk cycles have concrete acceptance criteria? | Each HIGH cycle must have at least one runnable check defined |
| Q5 | Any cycle where the goal statement contains more than one verifiable deliverable? | Flag if cycle goal has "AND [separate deliverable]" — split candidate |
| Q6 | Cycle order follows dependency order? | No cycle X that depends on output of cycle Y where Y comes after X |

Full mode output: inline table:

| Cycle | Risk Tier | Decision | Rationale |
|-------|-----------|----------|-----------|
| C{NN} | HIGH/MED/LOW | Confirmed / Tier corrected to X / Split into C{NN}a+b | [one line] |

**Escalation rules:**

| Finding type | Action | Human action (if STOP) |
|-------------|--------|----------------------|
| Tier correction (minor) | Claude Chat corrects in plan, notes in Review output, continues to WORK | N/A |
| Carry-forward scope adjustment (minor) | Claude Chat notes adjustment, continues | N/A |
| Cycle count change (add/remove cycle) | **STOP — Human confirmation required** | Confirm (proceed) or redirect (replan). One message. |
| Entry scope overlap (Rule 23 violation) | **STOP — Human confirmation required** | Confirm (proceed) or redirect (replan). One message. |
| LOW/MEDIUM → HIGH reclassification | **STOP — Human confirmation required** | Confirm (proceed) or redirect (replan). One message. |

If STOP triggered: Claude Chat presents finding + proposed resolution. Human responds with one message: confirm or redirect. Apply decision → proceed to WORK.

---

# WORK: Execute Cycles

## Purpose
Execute all phase cycles. Each cycle produces working code + tests.
No intermediate docs, no intermediate commits, no intermediate sprint updates.

## Per-Cycle Flow

Risk determines ceremony level:

### HIGH / MEDIUM risk cycles
Scout (if not covered by Combined Scout) → Assess → Execute → Validate

- **Scout:** only if Combined Scout didn't cover this cycle's scope.
  Create scout prompt per Rule 1 + Rule 2 format.
- **Assess (mandatory for HIGH, advisory for MEDIUM):**
  **HIGH:** execute prompts include Assess step. Claude Code reads current state,
  confirms plan is feasible against actual code, outputs ASSESS REPORT → STOP →
  Human confirms → Execute. Non-negotiable.
  **MEDIUM:** Claude Chat judgment — if scout was recent and code hasn't changed
  between scout and execute, Assess may be skipped. If gap is large or scope is
  complex, include Assess. Human may override: "skip assess" or "add assess."
- **Execute prompt:** .md artifact per Rule 1, with full header
  (Risk/Scope/Anti-scope/Phase). Pre-Execution Validation per Rule 12.
  MUST NOT include git commit/push steps — deferred to CLOSE.
  Include Completion Signal per Rule 24.
- **Validate:** Claude Code runs tests, Claude Chat checks results.
  If validation fails → fix before next cycle.

### LOW risk cycles
Execute only. Scout findings already available from OPEN Step 2.

- Execute prompt may omit separate scout.
- Assess may be skipped (LOW risk = config, docs, formatting).
- MUST NOT include git commit/push steps.
- Include Completion Signal per Rule 24.
- Verify: one-liner command confirming done.

### Task Batching
Multiple LOW-risk tasks MAY be combined into a single execute prompt
when they share no file conflicts and have no decision gates between them.
Claude Chat judgment — not mandatory, not prohibited.

**Practical ceiling:** 3-4 LOW tasks per prompt. For code tasks (even LOW), 2 is
safer. For pure doc tasks (backlog updates, version bumps), 4-5 is fine.
If any single task might fail → keep it separate so failure doesn't block the batch.

**Scope:** These ceilings apply to batching multiple tasks within ONE cycle.
Cross-cycle merging is governed by Rule 16 (decision-gate test) and Batch
Prompt Delivery above — not by task count limits.

### Batch Prompt Delivery

After Combined Scout (OPEN Step 2), Claude Chat creates ONE combined execute
prompt covering all phase cycles as sequential sections — instead of creating
separate prompts per cycle.

**When to use (default for single-entry phases):**
- Combined Scout covered all cycle scopes
- No decision gate between cycles (Rule 16 test: Claude Chat will NOT review
  output of cycle N before cycle N+1 — all derived from same scout)

**Combined prompt structure:**
One .md artifact with sequential cycle sections:

    # P{NN} Combined Execute — [Phase Name]
    ## §C{NN}: [cycle name]
    [Pre-Execution Validation, intent, tasks, acceptance criteria]
    ## §C{NN+1}: [cycle name]
    [Pre-Execution Validation, intent, tasks, acceptance criteria]
    ...
    ## Completion Signal
    [Aggregate: all cycles DONE/FAILED]

One file = one copy-paste to Claude Code. No multi-message delivery.

**Rules:**
- Claude Code executes sections in order — not in parallel
- Each section's Pre-Execution Validation runs against actual codebase state
  (which includes changes from prior sections)
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
- Phase has multiple entries (parallel streams) — each entry is its own chat
- Scout findings were incomplete or uncertain — build sections incrementally
- Cycles have genuine decision gates (output of N determines content of N+1)
- Context overflow risk — combined prompt exceeds Claude Code context window

## Rules During WORK
- No cycle doc creation (deferred to CLOSE)
- No S{N}-SPRINT.md updates (deferred to CLOSE)
- No git commit (deferred to CLOSE)
- Execute prompts MUST NOT include git commit/push steps
- Claude Chat maintains Running SPEC Log inline per Declaration
- If Claude Code reports unexpected issues → Claude Chat decides:
  fix now, defer to backlog, or escalate to Human

## Crash Recovery
For phases with >5 cycles or >1 day duration, Human may request
an intermediate commit checkpoint at any point. At that checkpoint:
- git add + commit + push (all accumulated changes)
- Update S{N}-SPRINT.md Current State (which cycles DONE)
- Resume WORK in same chat after checkpoint

This is a safety valve, not standard flow.

**Deploy-prelude commits (pre-authorized, no Human citation required):**

A mid-phase commit is authorized without invoking §Crash Recovery when:
(a) The commit contains only output required by an upcoming VPS-deploy cycle
(b) The committed content is atomic and tested (no partial state)
(c) The commit does not touch files owned by other concurrent cycles
(d) Commit message explicitly cites: `deploy-prelude: [description] — required for [cycle ID] VPS deploy`

Deploy-prelude commits do not reset the "batch at phase close" discipline for other cycles — only the specific pre-deploy output is committed early.

Canonical case: P79 C350 admin-UI needing browser walkthrough mid-phase — execute prompt's "NO commits" anti-scope contradicted Deploy §1 expectation "origin includes C350 commits". This clause resolves the contradiction by pre-authorizing the specific deploy-prelude commit pattern.

---

# CLOSE: Phase Finish

## Purpose
Close the phase. Verify all work, create all docs, commit everything, close chat.
Runs ONCE after all WORK cycles are done.

## Step 1: Phase Verification

Apply Validation Anti-Bias (Rule 22).

□ All tasks from P{NN}-{name}.md completed
□ All tests passing (full suite or affected subset)
□ No TODO/FIXME left in code touched this phase
□ New code follows Coding Standards from ARCHITECTURE-BOGAME.md
□ No logic duplication introduced

If new modules/components were created OR this is the last phase:
□ Architecture compliance check (two-way):
  Direction 1 — Doc reflects Code (ARCHITECTURE describes what exists)
  Direction 2 — Code follows Architecture (module boundaries, patterns)
□ FILE-TREE-BOGAME.md verify against filesystem (if drift suspected)

If anything incomplete → fix before proceeding.

**Triaged-deferral close (valid §1 outcome):**

A phase may close with incomplete tasks when ALL of the following hold:
(a) Sprint goal was reframed mid-flight and deferred tasks no longer serve the current goal
(b) Every deferred task has a corresponding open BACKLOG entry (Project Backlog or SPEC BACKLOG)
(c) Deferred tasks are enumerated in the phase RETRO or cycle doc Result section
(d) Commit message explicitly cites: `§CLOSE §1 deviation: triaged-deferral — [reason]`

This is NOT a shortcut for incomplete work. All deferred items must be persisted — verbal intent in chat without a written record does not exist.

Canonical case: P79 CLOSE used this pattern for C351 (moved to P82) and C352 (rescoped to P81) when S14-47 + S14-48 blocked verification.

## Step 1.5: Pre-Handoff Audit (handoff phases only)

If this phase ends in a **handoff** — client deploy, operator training,
cross-team transfer, production cutover — invoke the pre-handoff audit
skill before proceeding to Step 2:

```
/probekit-test-suite --handoff projects/<id>/
```

This runs the project-specific deploy-readiness probe (see project runbook
for skill name) composed over its configured probes and emits
`READY-FOR-HANDOFF-<project>-<date>.md` with BLOCKER / REQUIRED /
NICE-TO-HAVE tiers.

Outcome gate:
- **PASS** (0 BLOCKER, all REQUIRED assigned): proceed to Step 2
- **WARN** (≤1 BLOCKER with fix in scope, OR unassigned REQUIRED): resolve
  in-place and re-run. Do not proceed until PASS.
- **FAIL** (>1 BLOCKER, or no viable fix path): do not close. Re-plan the
  phase — either (a) add a cycle to resolve blockers, (b) renegotiate
  handoff scope with Human, or (c) split into staged handoff with explicit
  partial-handoff checklist.

Skip this step when the phase doesn't end in a handoff (internal-only
refactors, infra-only cycles, doc-only phases).

## Step 2: Verification Scout

ONE verification scout covering ALL files changed across ALL cycles in this phase.
Create scout prompt (.md artifact per Rule 1).

Claude Code checks:
□ Coding Standards (Rule 17) across all touched files
□ Logic duplication across all new code
□ Linter (if configured in ENVIRONMENT.md)
□ Tests: all passing, new functionality has tests
□ No TODO/FIXME or placeholder code
□ New modules/components list (for ARCHITECTURE update)
□ Version consistency in updated documents

Scope: git diff from phase start. Not the whole codebase.

After Scout — STOP. Claude Chat reviews. Fix issues if found.

## Step 3: Session Review

Claude Chat scans the chat:
□ SPEC findings (SPEC-LOG items)?
□ Deferred items ("do later", "next chat")?
□ Unrecorded decisions?
□ Any protocol step that felt awkward or unclear?

Findings exist → include in Close Prompt (Step 4e).
No findings → record "Session Review: no SPEC findings."

## Step 4: Close Prompt

ONE execute prompt (.md artifact per Rule 1) that does everything.
Include Completion Signal per Rule 24.

### 4a. Create ALL cycle docs (batch)

One .md file per cycle in:
  Single-entry: docs/03_sprint/S{N}-[name]/P{NN}-[name]/C{NN}-{name}.md
  Multi-entry:  docs/03_sprint/S{N}-[name]/P{NN}-[name]/E{NN}-[name]/C{NN}-{name}.md

Lightweight template (Tier 4):

# Cycle C{NN}: [Name]
> Phase [N]: [Phase Name] | Sprint [N]: [Sprint Name]
> Status: DONE

## Goal
[one sentence]

## Result
[2-3 sentences: what was done, what changed, notable decisions]

Status: DONE
Closed: [date]

Detail (steps, scout findings, KB/ADR decisions) lives in the chat history
and can be reconstructed. Cycle docs capture the outcome, not the process.

### 4b. Update P{NN}-{name}.md
- All Cycles table rows → DONE with dates and one-line results
- Phase status → DONE
- Phase closed date and summary

### 4c. Update ARCHITECTURE-BOGAME.md (if needed)
New modules/components → add to relevant section.
Tier 2 doc: version bump + Changelog row as numbered deliverable.

### 4d. Update S{N}-SPRINT.md

Current State:
  | Phase | [N]: [name] — DONE |
  | Entry | E{NN} — DONE |
  | Cycle | C[last]: [name] — DONE |
  | Status | Ready for next phase / Sprint complete |
  | Tests | [N pass / N fail / N skip] |

Protocol Log — one row per cycle:
  | S{N}-P{NN}-E{NN}-C{NN} | 03_Phase-Builder | [date] | DONE |

Last Session: 3-5 sentences covering the entire phase.
Next Action: [from Step 5 routing]
For Human: [per Declaration template]

### 4e. Persist findings
If SPEC-LOG items → append to SPEC-BACKLOG.md
If deferred project items → append to Project Backlog
If no items → skip

### 4f. Commit and push

git add [all modified files — code + docs from entire phase]
git commit -m "phase: Phase {N} {name} — DONE"
git push

ONE commit for the entire phase.

### 4g. For Human

Per Declaration template:
## For Human
> Next chat instruction. Copy-paste.

**Session Code:** [next]
**Load:**
1. Framework: 01_Declaration.md + [next protocol].md
2. Project: ENVIRONMENT.md + [other project docs]
3. Sprint: S{N}-SPRINT.md + P{NN}-{name}.md [if applicable]
**Run:** [next protocol] — [first step]

## Step 5: Routing

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
         next Session Code: S{N}-P{NN+1}-E{NN}-C{NN+1}

Output current Session Code. Include next Session Code in For Human.

---

## Chat Boundary — MANDATORY STOP

After Step 5 — this chat is DONE. Close it.

Do NOT start the next protocol in this chat.
Next phase or protocol = new chat.
Load S{N}-SPRINT.md → read Next Action → proceed.

---

## Architectural Cleanliness Principle

> Applies from S14-P78-C351 forward. This is a convention, not a policy —
> Claude Chat judgment still applies, but the default choice has shifted.

**Default: cleanliness over minimal patch.**

When choosing between implementation options, prefer architectural cleanliness
over a quick in-place edit. Resolve legacy rather than inherit it.

### Rationale

Deep code inspection during S14 P76-P78 revealed that earlier "minimal patches"
accumulated into structural debt: passthrough nodes, event-name mismatches,
service layers that exist descriptively but not functionally, two-layer
attachment gaps, doc-location drift. The cost of surfacing and fixing these
at integration time exceeded the cost of cleaner original implementation by
several multiples.

The project is transitioning from prototype to production. The standard changes
with it.

### Examples

Prefer cleanliness:
- Named event bridge over implicit convention matching
- Dedicated service class registered in the framework over overloaded method
  on an unrelated class
- Schema-enforced output contract over free-form LLM output parsed downstream
- Explicit artifact propagation through state over implicit context magic
- One source of truth per project (single folder) over scattered references

Minimal patch still acceptable when:
- Refactoring introduces risk disproportionate to the task scope
- Existing code consistently follows the minimal pattern and consistency
  wins over uniformity
- Explicit scope boundary of the cycle prohibits refactoring (rare —
  scope boundaries are usually advisory, not hard)
- The "clean" option is speculative / preemptive abstraction (YAGNI wins
  against over-engineering too)

### Enforcement

Claude Chat surfaces the choice when writing Scout, Assess, and Execute
prompts:
- Scout reports where the two options diverge
- Assess presents both options to Human with trade-offs
- Execute prompts name the chosen approach in the Decisions table

Human may override per-cycle. Default is cleanliness.

---

[*] 03_Phase-Builder SPEC v3.2.0 * ready
One entry stream = one chat. All cycles execute within.
OPEN: session plan + combined scout (once)
WORK: execute cycles — assess/exec/validate per risk tier, no intermediate overhead
CLOSE: verify + batch docs + one commit + close chat
