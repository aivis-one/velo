# 06_Spec-Update
> SPEC v3.2.0 | Framework health check + backlog review + apply changes
> Triggered by: after 05_Clean-Sync (mandatory) or any time framework feels off
> Sequence: 05_Clean-Sync → 06_Spec-Update → 07_Brain-Next → 02_Sprint-Builder

---

## Purpose

Check framework health, review SPEC BACKLOG, apply improvements, clear SPEC Update trigger, commit. This is the single protocol for all framework maintenance — diagnostics and action in one.

Run 06_Spec-Update when:
- After every 05_Clean-Sync (mandatory — before next 02_Sprint-Builder)
- Protocol files were modified
- Framework feels "off" — protocols not followed, structure unclear

---

## Before You Begin

Load in chat:

□ 01_Declaration.md
□ docs/01_refer/ENVIRONMENT.md
□ SPEC BACKLOG (docs/02_spec/01_refer/KNOWLEDGE/SPEC-BACKLOG.md)
□ S{N}-SNAPSHOT.md (latest closed sprint, if exists)
□ Resolution.md (optional — load if decisions needed during triage)
□ docs/01_refer/KNOWLEDGE/BACKLOG-BOGAME.md (for Backlog Routing Check)
□ S{N}-SPRINT.md (if exists — Step 16 writes Protocol Log)


Note: S{N}-SPRINT.md may not exist yet (between sprints). This is expected.

Confirm: ENVIRONMENT.md → SPEC Update → Status = PENDING.
If Status = DONE and this is a routine post-sprint run — something is wrong. Investigate.

---

## Part 1: Health Check

### Step 1: File Structure Check

Create scout prompt. Claude Code lists all files in `docs/02_spec/` and `docs/02_spec/01_refer/`.

Claude Chat verifies against expected file list:


Expected in docs/02_spec/ (root — protocol files only):
□ 01_Declaration.md
□ 02_Sprint-Builder.md
□ 03_Phase-Builder.md
□ 04_Sprint-Closer.md
□ 05_Clean-Sync.md
□ 06_Spec-Update.md
□ 07_Brain-Next.md
□ Resolution.md
□ Spec-Install.md

Expected in docs/02_spec/01_refer/ (reference + governance + knowledge):
□ SPEC-ARCHITECTURE.md
□ SPEC-VISION.md
□ SPEC-ROADMAP.md
□ SPEC-FILE-TREE.md
□ SPEC-KNOWLEDGE.md
□ GOVERNANCE/Information-Flow-Matrix.md
□ GOVERNANCE/Rule-Enforcement-Matrix.md
□ GOVERNANCE/SPEC-CHANGELOG.md
□ KNOWLEDGE/SPEC-BACKLOG.md
□ GOVERNANCE/SPEC-Diagram-v{current}.mermaid (one file — renamed on version bump)


Missing files = BREAK. Extra unexpected files = flag for review.

### Step 1b: Protocol Consistency Check

**Executor:** Claude Code (scout prompt) + Claude Chat (review)

Claude Code verifies protocol references against filesystem reality:

**Protocol Filename Consistency:**

□ Declaration → Protocol Map filenames → match actual files in docs/02_spec/?
□ FILE-TREE-BOGAME.md protocol filenames → match actual files on disk?
  (Claude Code reads FILE-TREE-BOGAME.md from `docs/01_refer/FILE-TREE-BOGAME.md`)


**Before You Begin Path Validation:**

□ For each protocol file in docs/02_spec/: all paths listed in Before You Begin → exist on disk?
  Output: [BREAK] if path does not exist, [GAP] if path exists but filename differs.


This check was moved here from 05_Clean-Sync (Rule 13 — framework layer separation).
Protocol files and their internal references are SPEC territory.

**After Scout — STOP.**

---

### Step 1c: Cross-Protocol Template Validation

**Executor:** Claude Code (scout prompt) + Claude Chat (review)

Every protocol (02–07, Spec-Install, Deploy) contains embedded templates,
placeholder formats, numbering conventions, and cross-references to Declaration rules.
These drift when Declaration is updated but protocols are not.

Create scout prompt. Claude Code performs:

**Template-vs-Declaration consistency:**

□ Extract all embedded templates from protocols 02–07 + Spec-Install
  (Step 6/7 templates in Sprint-Builder, Phase template, Protocol Log format, For Human format)
□ For each template: compare every {placeholder}, numbering format, and Session Code pattern
  against Declaration § Session Code, § Cycle Numbering Rule, § Entry Rule, § Hierarchy
□ Report: [MATCH] or [DRIFT] with specific mismatch per template


**Hardcoded values check:**

□ Grep all protocol files for numeric patterns in template blocks:
  E[0-9], P[0-9], C[0-9] outside of {placeholder} format
□ Compare against Declaration numbering rules
□ Report: [OK] or [HARDCODED] with location


**Cross-reference validation:**

□ Grep all protocol files for "Rule [0-9]" references
□ For each: verify the rule number matches the actual rule title in Declaration
□ Grep all protocol files for "§ " section references to other protocols
□ For each: verify the referenced section exists in the target protocol
□ Report: [OK] or [STALE REF] with location and expected vs actual


**After Scout — STOP. Review findings before proceeding to Step 2.**

---

### Step 2: BREAKS Check (critical issues)

Claude Chat checks for critical problems that break the framework:


□ S{N}-SPRINT.md exists in current sprint folder? (skip if between sprints)
□ S{N}-SPRINT.md contains all required sections?
  Required sections defined in: 02_Sprint-Builder Step 7 → Embedded Template
  Open template and verify section by section.
□ 01_Declaration.md is readable and complete?
□ Current P{NN}-{name}.md exists for active phase? (skip if between sprints)
□ No protocol file is empty (0 bytes)?
□ P{NN}-{name}.md Tests Summary section present in current phase? (skip if between sprints)
□ S{N}-SNAPSHOT.md exists in sprint folder root? (skip if between sprints)
□ ENVIRONMENT.md → SPEC Update → Status field present and valid?


Any NO = BREAK. Must fix before continuing.

---

### Step 3: DEGRADES Check (quality issues)

Claude Chat checks for practices that degrade framework quality over time.

**Session Discipline**

□ Protocol Log in S{N}-SPRINT.md — being updated each session?
□ For Human section — contains actionable instruction (not empty/vague)?
□ Last Session — filled with what was done (not left as placeholder)?
□ Session Codes in Protocol Log — cycle numbers (C{NN} part) sequential
  across the whole project, not restarted per phase? (check last 3 entries)


**Cycle Docs Quality**

□ Cycle docs — Result section filled at 03_Phase-Builder CLOSE (not left empty)?
□ 03_Phase-Builder CLOSE Session Review run each cycle?
  (check last 3 cycle docs for framework findings entry)
□ 03_Phase-Builder CLOSE Verification Scout run each cycle?
  (check last 3 cycle docs for verification results)


**Document Hygiene**

□ P{NN}-{name}.md Tests Summary — contains test scenarios (not empty placeholder)?
□ ARCHITECTURE-BOGAME.md — updated when new modules or folders were created?
□ ARCHITECTURE-BOGAME.md — Changelog section updated when architecture changed?
□ ARCHITECTURE-BOGAME.md — Coding Standards section exists and is current? (Rule 17)
□ S{N}-SPRINT.md — phase statuses match P{NN}-{name}.md files?
□ Tier 1 files: header version = anchor version? (canonical-source rule)
□ Tier 2 files (ARCHITECTURE-BOGAME.md, VISION-BOGAME.md): version + changelog present and current?
□ Tier 3 files (ENVIRONMENT.md, ROADMAP-BOGAME.md, FILE-TREE-BOGAME.md): Updated date recent?
□ SPEC BACKLOG — ideas being logged (not lost in chat)?


**Prompt Discipline**

□ Execute prompts have Risk/Scope/Anti-scope header? (check last 3 cycle docs)
□ Scout prompt names — neutral titles used?
□ Scout prompts — single artifact with all commands (not split)?
□ Git commits — meaningful messages (not "update" or "fix")?
□ Scout → Validate → Execute order — being followed (Rule 2)?
□ Prompts delivered as downloadable .md files (not inline text in chat — Rule 1)?
□ Acceptance Criteria present in MEDIUM/HIGH prompts? (check last 3 cycle docs)


**Sprint-Level (check once per sprint, skip during phase work)**

□ SPEC BACKLOG — items from previous sprint reviewed?


Each NO = DEGRADE.

---

### Step 4: Matrix Validation

Validate the two reference matrices against actual protocol state.

**Step 4a: Information Flow Matrix**

Read `docs/02_spec/01_refer/GOVERNANCE/Information-Flow-Matrix.md`.

For each row (Document × Protocol):

□ Producer listed? Does that protocol actually create this document?
□ Consumer(s) listed? Do those protocols actually load this document in Before You Begin?
□ Updater(s) listed? Do those protocols actually modify this document?


**Content Delivery Test:**

□ Every document has at least one producer (protocol that creates it)
□ Every document has at least one consumer (protocol that reads it)
□ No orphan documents (created but never consumed downstream)
□ No broken references (protocol expects file that no protocol creates)


**Step 4b: Rule Enforcement Matrix**

Read `docs/02_spec/01_refer/GOVERNANCE/Rule-Enforcement-Matrix.md`.

For each rule row:

□ At least one protocol explicitly checks/enforces this rule?
□ Each rule has a declared consequence for violation?
□ No dead rules (declared in 01_Declaration but never enforced anywhere)?
□ No enforcement gaps (rule enforced in some protocols but missed in others where relevant)?


Output: findings table for each matrix.

If either matrix is stale or inaccurate — update it in Part 3 (Step 10).

**After analysis — STOP.**

---

### Step 5: Framework Balance Check (conditional)

Run ONLY if ANY of the following:
- More than 2 sprints have passed without a full balance check, OR
- Human explicitly requested it, OR
- DEGRADES list from Step 3 contains 3 or more structural/terminological issues

Otherwise — skip entirely.
At Step 16 (Protocol Log update), record: "Balance Check: skipped"

Not "what is broken or degrading" — but "what is disproportionate across the framework itself."

Claude Chat reads all protocol files and checks four contexts:

**Context 1: Gene Analysis**
For each protocol:

□ IDENTITY: version, trigger, name correct?
□ FLOW: clear path, anchor block, STOP gates on decision points?
□ REQUIREMENTS: pre-read if deps>=2, input/output defined?
□ CONTENT: minimal prose, tables where needed?
□ INVARIANTS: testable rules, consequences declared?
□ DEPENDENCIES: all references live, no duplication (SSOT)?
□ RECOVERY: failure modes, actionable steps?


**Context 2: SSOT**

□ Same definition in two or more places?
□ Templates referenced that do not exist?
□ If X changes in one place — where else must it change?


**Context 3: Structural Consistency**

□ STOP gates formatted uniformly?
□ Changelog Rule formatted uniformly in all protocols where it appears?
□ Anchor blocks correct and consistent?
□ Terminology: one concept — one word across all files?
  Concrete check: (1) Extract Session Code patterns from Protocol Log templates across protocols.
  (2) Extract Entry/Phase/Cycle numbering from embedded templates.
  (3) Compare each against Declaration § Session Code, § Cycle Numbering, § Entry Rule.
  (4) Report mismatches.
□ Before You Begin — consistent structure?
□ Universal close flow — consistent structure across all protocols?


**Context 4: Attention Budget**

□ Sections <=7, list items <=9, nesting <=3?
□ High-frequency protocols (03_Phase-Builder) — compact?
□ Low-frequency protocols (Spec-Install, 04_Sprint-Closer, 06_Spec-Update) — volume proportional, not unlimited?


Note: Information Flow and Rule Enforcement checks (old Context 1 + Context 6)
are now handled by Step 4 via matrices. Not duplicated here.

Output: findings table per context.

**After analysis — STOP. Proceed to Tier 2 Freshness Check.**

---

### Step 6: Tier 2 Freshness Check

Validate that Tier 2 documents (ARCHITECTURE-BOGAME.md, VISION-BOGAME.md) were maintained during the sprint.


□ ARCHITECTURE-BOGAME.md → Changelog section: last entry date within current sprint period?
  If sprint had cycles that modified architecture (new modules, renamed components,
  structural changes) but Changelog has no entry → DEGRADE
□ VISION-BOGAME.md → Changelog section: last entry date reasonable?
  (VISION changes less frequently — flag only if known VISION-affecting decisions
  were made this sprint without a corresponding entry)
□ ARCHITECTURE-BOGAME.md header version matches latest Changelog entry version?
□ VISION-BOGAME.md header version matches latest Changelog entry version?


If any DEGRADE found → add to Health Report.

**After check — STOP.**

---

### Step 7: Build Health Report

Claude Chat outputs:

markdown
## SPEC Health Report
Date: [date]
Sprint: [N] — [Name] (or "Between sprints")

### BREAKS (must fix)
[list or "None"]

### DEGRADES (should fix)
[list or "None"]

### MATRIX VALIDATION
Information Flow: [PASS / N issues found]
Rule Enforcement: [PASS / N issues found]
Content Delivery Test: [PASS / N orphans / N broken refs]

### TIER 2 FRESHNESS
ARCHITECTURE-BOGAME.md: [CURRENT / STALE — last entry: date]
VISION-BOGAME.md: [CURRENT / STALE — last entry: date]

### BALANCE (if run)
| # | Area | Finding | Severity | Recommendation |
|---|------|---------|----------|----------------|

BALANCE summary: [N] HIGH, [N] MEDIUM, [N] LOW
(or "Balance Check: skipped — [reason]")

### Overall Status
[HEALTHY / BREAKS FOUND / DEGRADES ONLY / MATRIX GAPS / BALANCE GAPS FOUND]


---

### Step 8: Fix BREAKs

For each BREAK — fix immediately before continuing.

Create execute prompt for each fix.

---

## Part 2: SPEC Backlog Review

### Step 9: Triage SPEC BACKLOG

Claude Chat reads all open items in SPEC BACKLOG (docs/02_spec/01_refer/KNOWLEDGE/SPEC-BACKLOG.md).

For each item, decide:


Item actionable now?
├── YES + P1/P2 → Plan for execution in Step 10
├── YES + P3/LOW → Keep in backlog, skip this round
├── NO — needs more info → Keep in backlog with note
└── DONE or WON'T DO → Mark status in table


Present triage result to Human:

## Triage Result
Execute now: [list of items with IDs]
Keep in backlog: [list with reasons]
Close: [list with reasons]


Human confirms.

**Decision framework:** For framework improvement decisions requiring architectural analysis,
apply `docs/02_spec/Resolution.md`.

### Step 9b: Backlog Routing Check

Scan both backlogs for misrouted items:

□ SPEC BACKLOG: any project items that belong in Project Backlog?
  (code bugs, tech debt, features → move to BACKLOG-BOGAME.md)
□ Project Backlog: any framework items that belong in SPEC BACKLOG?
  (protocol improvements, rule changes → move to SPEC BACKLOG)
□ Verify routing rules (Declaration Rule 10) applied correctly

If moves needed — create execute prompt.

---

## Part 3: Apply Changes

### Step 10: Execute Framework Improvements

For each item approved in Step 9 + matrix/freshness fixes from Steps 4-6:

1. Create execute prompt for Claude Code
2. Claude Code modifies protocol files in `docs/02_spec/` or matrices in `docs/02_spec/01_refer/`
3. After each change — STOP, Claude Chat validates

Changes may include:
- Protocol file updates (rules, steps, checklists)
- New rules added to 01_Declaration.md
- Protocol merges, splits, or restructuring
- Template updates
- Matrix updates (Information Flow, Rule Enforcement)
- Tier 2 document version bumps (if ARCHITECTURE-BOGAME.md or VISION-BOGAME.md updated)

---

### Step 11: Log DEGRADEs and Balance Gaps to SPEC BACKLOG

Create execute prompt. Claude Code appends unresolved DEGRADEs and BALANCE gaps
to SPEC BACKLOG (docs/02_spec/01_refer/KNOWLEDGE/SPEC-BACKLOG.md):

markdown
| [next #] | [description] | S{N}-SPEC Health Check [date] | [priority] | TODO |


---

### Step 12: Update SPEC Version (if rules/protocols changed)

If any protocol files or 01_Declaration.md were modified:

1. Determine version bump: MAJOR.MINOR.PATCH
   - MAJOR: breaking changes to protocol structure or lifecycle
   - MINOR: new rules, merged protocols, significant additions
   - PATCH: typo fixes, clarifications, minor adjustments

2. Execute version-sync prompt (from ADR):


# Version Sync — SPEC vOLD → vNEW
Type: execute
Risk: HIGH
Scope: [list all Tier 1 files — 9 protocol files + SPEC-BACKLOG.md, SPEC-CHANGELOG.md, matrices]
Anti-scope: SPEC-Diagram file (handled in Step 15); all Tier 2, 3, 4 documents

## Content replacement (Tier 1 files)

Steps 1–2: Replace version strings
1. In every Tier 1 file header, replace "SPEC vOLD" with "SPEC vNEW"
2. In every Tier 1 protocol file anchor block footer, replace "SPEC vOLD" with "SPEC vNEW"
   Note: SPEC-BACKLOG.md, SPEC-CHANGELOG.md, and matrices may not have anchor blocks —
   replace only in header for those files.

Steps 3–5: Validate content replacement
3. Count remaining occurrences of "SPEC vOLD" across all Tier 1 files → must be 0
4. Count occurrences of "SPEC vNEW" in headers → must equal [HEADER_COUNT]
5. Scan all 9 protocol files: verify header version = anchor block version per file

## Report
- Files modified: [list]
- Header count: [actual vs expected]
- Anchor match failures: [list — protocol files only]

## Acceptance Criteria
- [ ] grep "SPEC vOLD" docs/02_spec/ docs/02_spec/01_refer/ → 0 results
- [ ] grep "SPEC vNEW" docs/02_spec/ docs/02_spec/01_refer/ → [HEADER_COUNT + anchor_count] results
- [ ] All 9 protocol file header/anchor pairs match


**Sprint close is BLOCKED if count-validate fails or any header/anchor mismatch.**

3. Add CHANGELOG entry:

Create execute prompt. Claude Code adds a new entry to
`docs/02_spec/01_refer/GOVERNANCE/SPEC-CHANGELOG.md`:

markdown
## SPEC vNEW — YYYY-MM-DD

[Bullet list: what changed this 06_Spec-Update session]


This is separate from the version-sync string replacement. The version-sync
updates the version number in the CHANGELOG header. This step adds a new
content entry describing the changes.

---

### Step 13: Update SPEC BACKLOG Statuses

Create execute prompt. Claude Code updates SPEC BACKLOG (docs/02_spec/01_refer/KNOWLEDGE/SPEC-BACKLOG.md):

- Items executed in Step 10 → Status: DONE
- Items closed in Step 9 → Status: DONE or WON'T DO
- DEGRADEs and Balance gaps logged in Step 11 → new entries added
- Update header date

**Cleanup rule (mandatory):**
After status updates, remove all completed items from SPEC-BACKLOG:
1. Items with Status = DONE or WON'T DO in Open Items → verify each is reflected
   in SPEC-CHANGELOG.md (by version entry) → then DELETE the row from SPEC-BACKLOG
2. Dedicated "Closed Items" sections → verify all items reflected in SPEC-CHANGELOG.md
   → then DELETE the entire section
3. SPEC-BACKLOG must contain ONLY active items (TODO, IN PROGRESS)
   — it is a work queue, not an archive

If an item is DONE but not yet in SPEC-CHANGELOG → add it to the relevant version
entry in SPEC-CHANGELOG first, then delete from SPEC-BACKLOG.

---

### Step 14: Clear SPEC Update Trigger

Create execute prompt. Claude Code updates ENVIRONMENT.md:


SPEC Update:
| Status | **DONE (S{N} — [date])** |


**Tier 3 exception — header version bump:**
If SPEC version was incremented in Step 12, also update ENVIRONMENT.md header:

> BOGame | SPEC vNEW

ENVIRONMENT.md carries SPEC version for quick reference in every chat.
This bump happens here (during trigger clear), not in Tier 1 version-sync batch.

**Also remove SPEC Update banner from 01_Declaration.md:**

In the same execute prompt, remove the active banner block from the Entry Rule section of `docs/02_spec/01_Declaration.md` (the block starting with "⚠️ SPEC UPDATE REQUIRED"). Keep the "### SPEC Update Banner" mechanism description intact — only remove the active banner instance.

Verify: grep "⚠️ SPEC UPDATE REQUIRED" docs/02_spec/01_Declaration.md → 0 active banners (the mechanism description uses indented/quoted format and will not match a top-level banner).

This unblocks normal project work. Next chat loading ENVIRONMENT.md will see DONE
and proceed to 07_Brain-Next instead of looping back to 06_Spec-Update.

**After update — STOP.**

---

### Step 15: Update SPEC Diagram (conditional)

Run ONLY if SPEC version was incremented in Step 12.

Create execute prompt. Claude Code renames (or recreates) the diagram:
  `docs/02_spec/01_refer/GOVERNANCE/SPEC-Diagram-vOLD.mermaid`
  → `docs/02_spec/01_refer/GOVERNANCE/SPEC-Diagram-vNEW.mermaid`

If diagram content needs updating (protocol changes affected lifecycle flow):
update content before renaming. Otherwise rename only.

Diagram must show:
- All protocols (01_Declaration, 02–08, Spec-Install) as nodes
- Lifecycle transitions between protocols (directed arrows with Session Code labels)
- 07_Brain-Next as on-demand node with dashed link to L0 Strategy
- For each protocol: key steps as sub-nodes with STOP gate markers

Previous version file is NOT retained after rename — only one diagram file exists
at a time, carrying the current SPEC version in its filename.

**Verify:**

□ SPEC-Diagram-vNEW.mermaid exists in docs/02_spec/01_refer/GOVERNANCE/
□ SPEC-Diagram-vOLD.mermaid removed
□ No references to old diagram filename in Tier 1 files


After update — STOP.

---

### Step 16: Update S{N}-SPRINT.md (if exists)

If a S{N}-SPRINT.md exists for current/recent sprint:

Create execute prompt. Claude Code updates Protocol Log:


| S{N}-SPEC | 06_Spec-Update | [date] | DONE — [HEALTHY/N breaks fixed/N items implemented/N matrix gaps found] |


If between sprints and no active S{N}-SPRINT.md — skip this step.

**After update — STOP.**

---

### Step 17: Universal Close Flow

1. Verify all steps DONE (Steps 1–16)
2. Scan this chat: unrecorded decisions? SPEC-LOG items?
3. If items found → execute prompt to persist to SPEC BACKLOG
   (docs/02_spec/01_refer/KNOWLEDGE/SPEC-BACKLOG.md). Wait for Claude Code confirmation.
4. If no items → record: "SPEC-LOG: nothing to persist"
5. Final commit:
   
   git add docs/02_spec/ docs/01_refer/ENVIRONMENT.md
   git commit -m "spec-update: SPEC health check + [N items implemented / backlog reviewed]"
   git push
   
6. Output: current Session Code (S{N}-SPEC) + next Session Code + what to load
7. STOP — close chat

---

### Step 18: Hand Off to Brain-Next

Framework Phase complete. SPEC Update trigger cleared.

Close this chat.

Next chat: Session Code S{N}-Brain-Next
Load:
  □ 01_Declaration.md
  □ 07_Brain-Next.md
  □ KNOWLEDGE-BOGAME.md (from docs/01_refer/KNOWLEDGE/)
  □ ARCHITECTURE-BOGAME.md
  □ ROADMAP-BOGAME.md (strategic)
  □ ENVIRONMENT.md
  □ BACKLOG-BOGAME.md
  □ S{N}-SNAPSHOT.md (latest closed sprint)
Run: 07_Brain-Next

After 07_Brain-Next → Session Code S{N+1}-Sprint-Builder → 02_Sprint-Builder.

## Chat Boundary — MANDATORY STOP

After final commit — this chat is DONE. Close it.
Do NOT start the next protocol in this chat.
One protocol = one chat. No exceptions.
Next protocol = new chat.

---


[*] 06_Spec-Update SPEC v3.2.0 * ready
Framework health check + matrix validation + backlog review + apply changes
Run: after every sprint close (mandatory) + any time framework feels off
Sequence: 05_Clean-Sync → 06_Spec-Update → 07_Brain-Next → 02_Sprint-Builder

