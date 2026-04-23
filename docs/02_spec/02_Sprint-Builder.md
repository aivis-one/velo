# 02_Sprint-Builder
> SPEC v3.2-velo | Strategic sprint planning + phase setup
> Triggered by: project start (via INSTALLATION-PLAN.md one-time) OR after 05_Clean-Sync
> Sequence: 05_Clean-Sync → 02_Sprint-Builder → 03_Phase-Builder

---

## Purpose

Strategic planning for a new sprint AND tactical phase setup in ONE chat.
Review architecture, define sprint scope, scout codebase, plan all phases
with cycles, create S{N}-SPRINT.md.

If a question arises mid-sprint, log it in `BACKLOG.md` or (if a decision is made) `decisions.md`.

Output: `S{N}-SPRINT.md` with phases inline. Optional: `P{NN}-{name}.md` if a phase has >5 cycles.

---

## Before You Begin

Load in chat:

□ 01_Declaration.md
□ docs/01_refer/ARCHITECTURE.md
□ docs/01_refer/ENVIRONMENT.md
□ docs/01_refer/BACKLOG.md
□ docs/01_refer/decisions.md
□ Previous sprint S{N-1}-SNAPSHOT.md (if exists)
□ CODE-AUDIT-S[N-1].md (if exists — detailed findings context)
□ S{N-1}-RETRO.md (if exists)

No S{N}-SPRINT.md yet — it will be created during Step 7 of this protocol.

Human confirmation of Session Plan required before proceeding (Rule 6).

---

## Step 1: Review Architecture

> **Gate:** `ARCHITECTURE.md` reflects current system, no gaps, no stale sections?
> → YES: confirm in one sentence, proceed to Step 2.
> → NO: run full review below.

Read `ARCHITECTURE.md`. Ask:

□ Does it reflect current system state?
□ What architectural gaps exist?
□ What technical debt is relevant to this sprint?
□ Coding Standards section exists and is current?
□ Standards still match how code is actually written?

Note any architectural questions — log to `BACKLOG.md` if they cannot be resolved here. If a decision is reached, append to `decisions.md`.

If `ARCHITECTURE.md` is modified during this step — plain update (no versioning in Velo profile).

---

## Step 2: Define Sprint Scope

Claude Chat proposes sprint scope based on:
- Carry-forward items from previous SNAPSHOT (if exists)
- `BACKLOG.md` items (prioritized)
- Any open decisions in `decisions.md`

Define:

```
Sprint Goal: [one sentence — what this sprint delivers]
Out of Scope: [what is explicitly NOT in this sprint]
Success Criteria: [how we know it's done]
```

Present to Human. Human confirms or adjusts.

**Sprint Capacity Check (mandatory):**

Target: **15–25 cycles per sprint** (single-dev frontend scope). Count planned cycles across all phases.

- Below 15 → sprint is underfilled. Pull additional items from `BACKLOG.md`. Mark each pulled item in source: "→ S{N}" with date.
- 15–25 → healthy range. Proceed.
- Above 25 → sprint is overfilled. Cut lowest-priority phases or move Should-Have phases to S{N+1}.

Re-present to Human after capacity adjustment.

**Backlog Assignment Marking:**

Every item pulled from `BACKLOG.md` into this sprint must be marked in-place:

| # | Item | ... | Status | Notes |
|---|------|-----|--------|-------|
| 12 | ... | ... | → S{N} P{NN} | Assigned [date] |

This prevents duplicate assignment in future sprints.

**Look-Ahead: S{N+1} direction (lightweight):**

Before finalizing scope, Claude Chat sketches the likely direction for the NEXT sprint (S{N+1}). One paragraph — not formal planning:

- What S{N+1} will likely focus on
- Which deliverables from S{N} are prerequisites for S{N+1}
- Any scope that should be deferred from S{N} to S{N+1} (or vice versa)

Purpose: prevents over-scoping the current sprint and ensures clean handoff. This is a vector, not a plan.

**Metrics review (if previous SNAPSHOT has Sprint Metrics table):**

Claude Chat reviews trends across sprints:

□ CRITICAL/HIGH findings from ProbeKit: trending up? → flag to Human
□ Test count vs LOC: tests growing proportionally?
□ Any metric with 3+ sprints of continuous degradation? → mandatory discussion

If no previous metrics or first sprint — skip.

---

## Step 3: Scout Codebase

> Run BEFORE phase definition so scout findings inform planning.
> **Skip conditions (any one is sufficient):**
> - Brand new sprint with no code change yet (Sprint 1 pilot)
> - CODE-AUDIT-S{N-1} loaded in Before You Begin (audit replaces scout)
>
> If none apply — scout first, then proceed to Step 4.

Create scout prompt. Claude Code reads:

□ Current module/file structure relevant to this sprint
□ Existing test files for affected areas
□ Any interfaces or contracts this sprint will touch
□ State of modules targeted by Must-Have items

Output: findings that will inform phase content and distribution.

**After Scout — STOP. Claude Chat reviews.**

---

## Step 4: Plan All Phases

For each phase, Claude Chat defines:

```
Phase [N]: [Name]
  Cycles:
    C{NN}: [goal — one sentence]
    C{NN+1}: [goal — one sentence]
    ...
  Cycle types: standard | design-gen (see 03_Phase-Builder § Cycle Types)
  Tests:
    - [test scenario 1]
    - [test scenario 2]
  Entry condition: [what must be true before this phase starts]
  Exit condition: [what must be true to close this phase]
```

**Phase verification:** The last working cycle of each phase includes phase verification and closure as part of its CLOSE flow (see 03_Phase-Builder CLOSE).

**Sizing guidance:** Aim for 2–5 phases per sprint, 3–9 cycles per phase. Each phase should be completable in 3–10 days. Fewer cycles for focused deliverables, more for cross-cutting work. Phases with only 1–2 cycles are likely too granular — merge with adjacent phase or expand scope.

**Decision references:**

For each task, Claude Chat checks `decisions.md` for any constraint. Write decision ID into the phase doc task descriptions if relevant:
- If task is constrained by decision #NNN → cite it
- If no relevant decisions exist → omit

**Phase distribution principles:**

- **Dependency-first** — phases that are prerequisites go before phases that depend on them.
- **Spike-early** — if any phase carries technical uncertainty, move a validation spike into the first phase.
- **Must-have first** — P1 phases go early. If the sprint runs short on time, later phases can be cut.
- **One coherent deliverable per phase** — each phase should produce something meaningful and testable on its own.
- **No Sprint Close as a phase** — Sprint Close is handled by 04_Sprint-Closer, not as a phase.
- **Code audit prohibition** — never plan code-audit or security-audit as a cycle task inside a phase. Code audit is handled by 04_Sprint-Closer Part 1 (ProbeKit lite profile).

**After listing phases — prioritize explicitly:**

| Priority | Meaning | Action if time runs out |
|----------|---------|------------------------|
| **Must have** | Sprint is not complete without this | Cannot cut |
| **Should have** | Important but deliverable without it | Cut to next sprint |
| **Nice to have** | If time allows | Drop without guilt |

Present phases with priorities to Human. Human confirms or adjusts.

---

## Step 5: Optional — Per-Phase Files

If a phase has **>5 cycles** or combines heterogeneous work, break it out into `P{NN}-{name}.md` in a phase folder.

Otherwise, keep phase content inline in `S{N}-SPRINT.md` (default for small sprints).

**When a phase file is created** — it lives at:

```
docs/03_sprint/S{N}-[name]/P{NN}-[name]/P{NN}-{name}.md
```

Template (Tier 4 — no SPEC version):

```markdown
# Phase {N}: [Name]
> Sprint {N}: [Sprint Name]
> Status: NOT STARTED

## Goal
[one sentence]

## Entry Condition
[what must be true before this phase starts]

## Exit Condition
[what must be true to close this phase]

## Tasks

Task 1: [name]
Scope: [what to build]
Cycle type: standard | design-gen
Decision ref: [#NNN if applicable]
Test: [what to verify]

## Cycles

| Cycle | Type | Name | Status | Date | Result |
|-------|------|------|--------|------|--------|
| C{NN} | standard | [name] | TODO | | |
| C{NN+1} | design-gen | [name] | TODO | | |

## Tests Summary

| # | Test | Command/Check |
|---|------|---------------|
| T1 | [test name] | [how to verify] |

## Exit Criteria

- [ ] [criterion 1]
- [ ] [criterion 2]
```

**After creation — STOP.**

---

## Step 6: Create S{N}-SPRINT.md

Create execute prompt. Claude Code creates:

```
docs/03_sprint/S{N}-[name]/S{N}-SPRINT.md
```

### Embedded S{N}-SPRINT.md Template

```markdown
# SPRINT
> Velo | Sprint {N}: [Name]
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
> Stable paths to project documents. Update only if files move.

| Doc | Path |
|-----|------|
| ARCHITECTURE | docs/01_refer/ARCHITECTURE.md |
| ENVIRONMENT | docs/01_refer/ENVIRONMENT.md |
| FILE-TREE | docs/01_refer/FILE-TREE.md |
| BACKLOG | docs/01_refer/BACKLOG.md |
| DECISIONS | docs/01_refer/decisions.md |
| RETRO-S{N} | docs/03_sprint/S{N}-[name]/S{N}-RETRO.md |

---

## Goal
[one sentence — what this sprint delivers]

## Success Criteria
- [criterion 1]
- [criterion 2]

## Out of Scope
- [item]

---

## Phases

### Phase {N}: [Name]
**Goal:** [one sentence]
**Entry:** [condition]
**Exit:** [condition]
**Cycles:**

| Cycle | Type | Name | Status | Date | Result |
|-------|------|------|--------|------|--------|
| C{NN} | standard | [name] | TODO | | |
| C{NN+1} | design-gen | [name] | TODO | | |

### Phase {N+1}: [Name]
**Goal:** [one sentence]
...

---

## Carry-Forward from S{N-1}
- [item from previous snapshot]

## Key Decisions
- #NNN: [title] — from decisions.md

---

## Sprint Context
> Brief history — what came before this sprint.

| Sprint | Status |
|--------|--------|
| S1: [Name] | DONE |
| S{N}: [Name] | IN PROGRESS |

---

## Current State
> The most critical section. Must be accurate at the start of every chat.

| Item | Value |
|------|-------|
| Phase | {N}: [Phase Name] — [NOT STARTED / IN PROGRESS / DONE] |
| Cycle | C{NN}: [short name or "not started"] |
| Status | [One sentence: what is the situation right now] |
| Tests | [N pass / N fail / N skip] |

---

## Protocol Log
> Record of every protocol run in this sprint. Add a row after EVERY session.
> Cycle column uses Session Code (see 01_Declaration → Session Code table).

| Cycle      | Protocol              | Date         | Status |
|------------|-----------------------|--------------|--------|
| S{N}-Sprint-Builder | 02_Sprint-Builder     | [YYYY-MM-DD] | DONE   |
| S{N}-P{NN}-C{NN} | 03_Phase-Builder OPEN | [YYYY-MM-DD] | DONE   |
| S{N}-P{NN}-C{NN} | 03_Phase-Builder CLOSE | [YYYY-MM-DD] | DONE   |

---

## Last Session
> 3-5 sentences: what was done, what decisions were made, what's notable.

[What was done. What decisions were made. Any blockers encountered.]

---

## Next Action
> One concrete action. Not "continue work" — exactly what protocol or step to run.

[Exact next step]

---

## For Human
> Copy-paste instruction for opening the next chat. Update at every Phase-Builder CLOSE.

**Session Code:** S{N}-P{NN}-C{NN}
**Load:**
1. Framework: 01_Declaration.md + 03_Phase-Builder.md
2. Project: ENVIRONMENT.md + ARCHITECTURE.md
3. Sprint: S{N}-SPRINT.md [+ P{NN}-{name}.md if phase has external file]
**Run:** 03_Phase-Builder OPEN — plan first cycle

---

## Plan vs Reality
> Filled during 04_Sprint-Closer at sprint close. Empty while sprint is active.

| Aspect | Planned | Actual | Delta |
|--------|---------|--------|-------|
| Phases | — | — | — |
| Cycles | — | — | — |
| Duration | — | — | — |

### What Worked
(filled at close)

### What Didn't
(filled at close)

### Carry Forward
(filled at close)

---
*S{N}-SPRINT.md*
*Velo | Sprint [N]: [Name]*
```

---

### Plan Validation Gates

Plans iterate before execution. This is intentional, not a deficiency.

```
v1.0 (draft) → validate → issues → v1.1 (fix) → v1.2 → ... → vN.0 (approved)
```

**Minimum:** 1 validation pass (every plan).
**Complex plans:** 2–3 passes.

**What each pass checks:**
- Completeness: all declared changes present
- Consistency: no contradictions within plan or against existing docs
- Cascade: every change traced to downstream references
- Feasibility: code-level verification where applicable (Assess step)

**Human gate:** Human approves final version before ANY execution begins.
No partial execution of unapproved plans.

Validation standard: `docs/02_spec/01_Declaration.md §Rule 22`
**Decision framework:** For ambiguous scope decisions, apply `docs/02_spec/Resolution.md`.

**After creation — STOP.**

---

## Step 7: Close — Universal Close Flow

### 7a. Verify Completion

□ Step 1 (Architecture): confirmed or updated
□ Step 2 (Scope): Human confirmed
□ Step 3 (Scout): DONE or skipped
□ Step 4 (Plan): all phases defined, Human confirmed
□ Step 5 (P{NN}-{name}.md if applicable): created
□ Step 6 (S{N}-SPRINT.md): created with Protocol Log entries

**Executable verification (mandatory):** Create execute prompt for Claude Code.
Replace S{N} with actual sprint number in all commands below.

Claude Code runs these checks and reports results:

1. BACKLOG items marked: `grep -c "→ S[actual_number]" docs/01_refer/BACKLOG.md` → expect ≥ count of items pulled
2. Look-ahead present: `grep "S{N+1}" docs/03_sprint/S{N}-[name]/S{N}-SPRINT.md` → expect found
3. Protocol Log: `grep "S{N}-Sprint-Builder" docs/03_sprint/S{N}-[name]/S{N}-SPRINT.md` → expect found
4. For Human: `grep "Session Code: S{N}-P" docs/03_sprint/S{N}-[name]/S{N}-SPRINT.md` → expect found
5. Cycle numbering sequential: no gaps in C{NN} across all phases

Output: checklist with PASS/FAIL per item. If ANY FAIL → fix before committing.

### 7b. Update S{N}-SPRINT.md

Create execute prompt. Claude Code updates:

```
Current State:
| Phase | 1: [Name] — NOT STARTED |
| Cycle | C{NN}: not started |
| Status | Planning complete, ready for first cycle |
```

Protocol Log — add row:
```
| S{N}-Sprint-Builder | 02_Sprint-Builder | [date] | DONE |
```

Next Action: `C{first cycle number} — run 03_Phase-Builder OPEN`

For Human section already populated via the template above.

### 7c. Deferred Items Check

□ Scan chat for any "do later", "next chat", "handle next time" verbal commitments.
□ If found → write each item to `BACKLOG.md` immediately via execute prompt.
□ Unrecorded decisions → append to `decisions.md` via execute prompt.

### 7d. Final Commit

```
git add docs/03_sprint/S{N}-[name]/ docs/01_refer/
git commit -m "sprint: S{N} [name] — planning complete, ready to start"
git push
```

### 7e. Sprint Comprehension Check

Create execute prompt. Claude Code reads `S{N}-SPRINT.md` (+ any `P{NN}-{name}.md`) and outputs:

```
Sprint Comprehension Report:
  Total phases: [N]
  Total cycles: [N] (C[first]-C[last])
  Cycle types: [N standard, N design-gen]
  Missing sections: [any required section absent]
  Cycle gaps: [any non-sequential cycle numbers]
  Cross-references: [phase entry/exit conditions chain correctly?]
  Verdict: READY / ISSUES FOUND
```

If ISSUES FOUND → fix before closing chat.

### 7f. Close Chat

Output current Session Code: `S{N}-Sprint-Builder`

## Chat Boundary — MANDATORY STOP

After final commit — this chat is DONE. Close it.
Do NOT start the next protocol in this chat.
One protocol = one chat. No exceptions.
Next protocol = new chat.

**STOP — close this chat.**

---

[*] 02_Sprint-Builder SPEC v3.2-velo * ready
Strategic sprint planning + phase setup
Output: S{N}-SPRINT.md (with phases inline) + optional P{NN}-{name}.md for large phases
Includes: S{N+1} look-ahead for strategic continuity, cycle-type tagging (standard | design-gen)
Session Code: S{N}-Sprint-Builder
Next chat: S{N}-P{NN}-C{first cycle} — run 03_Phase-Builder OPEN
