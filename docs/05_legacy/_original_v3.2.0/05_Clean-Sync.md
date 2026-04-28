# 05_Clean-Sync
> SPEC v3.2.0 | Project data hygiene — FILE-TREE sync, path/version consistency, backlog health, stale pruning
> Triggered by: after 04_Sprint-Closer (mandatory before 06_Spec-Update)
> Sequence: 04_Sprint-Closer → 05_Clean-Sync → 06_Spec-Update → 07_Brain-Next → 02_Sprint-Builder

---

## Purpose

Physical hygiene of project files. Sync FILE-TREE with disk, cross-validate
paths and versions between documents, prune stale content from active files,
rebalance backlogs, archive dead information.

Clean-Sync does NOT do:
- Strategy review (→ 02_Sprint-Builder)
- Knowledge/ADR audit (→ 07_Brain-Next)
- Code quality review (→ 04_Sprint-Closer Part 1)
- VISION/ARCHITECTURE content review (→ 07_Brain-Next / 02_Sprint-Builder)

Clean-Sync runs AFTER Sprint-Closer which may create filesystem drift from code audit fixes, SNAPSHOT creation, RETRO creation. Clean-Sync catches this drift before Spec-Update uses these files for framework review.

---

## Before You Begin

Load in chat:

□ 01_Declaration.md
□ docs/01_refer/ENVIRONMENT.md
□ docs/01_refer/FILE-TREE-BOGAME.md
□ docs/01_refer/KNOWLEDGE/BACKLOG-BOGAME.md
□ ARCHITECTURE-BOGAME.md
□ ROADMAP-BOGAME.md
□ S{N}-SNAPSHOT.md (latest closed sprint)
□ S{N}-SPRINT.md (current or just-closed sprint)

Note: ENVIRONMENT.md SPEC Update may show PENDING — expected. 05_Clean-Sync runs regardless (framework-phase protocol).

This is a deterministic protocol — execute immediately after loading documents.
No Session Plan confirmation required (Rule 6).

---

### Operational Limits

| Operation | Per-session limit | Notes |
|-----------|------------------|-------|
| FILE-TREE scan + fix (combined) | 1 prompt | Scout+execute merged for drift ≤ 10 |
| Cross-doc consistency scout | 1 prompt | All checks in one scout |
| Cross-doc fixes | 1-2 prompts | Depends on BREAK count |
| Backlog prune + transfers | 1-2 prompts | Depends on volume |
| Total expected | 3-6 Claude Code prompts per session | Down from 4-8 |

---

### Prompt Discipline

All prompts for Claude Code MUST follow Declaration Rule 15 header schema:
```
# [Prompt Title]
Type: scout | execute
Risk: LOW
Scope: [file paths or module names]
Anti-scope: [explicitly excluded]
```

All commits follow ENVIRONMENT.md commit conventions.
Commit prefix for this protocol: `clean-sync:` (see ENVIRONMENT.md).

---

## Step 1: FILE-TREE Sync

**Executor:** Claude Code (combined prompt — scout + execute)

**Rule 16 exception note:** FILE-TREE sync is combined (scout+execute in one prompt) because it is deterministic when findings are expected. This is a conditional gate: if unexpected findings emerge → STOP path activates, preserving Rule 16 intent. No Human review needed for expected drift (phantom/missing entries).

Create combined prompt. Claude Code:
1. Generates fresh file tree from actual filesystem
2. Compares with existing FILE-TREE-BOGAME.md
3. Reports findings:

```
[PHANTOM] Listed in FILE-TREE but not on disk: [path]
[MISSING] On disk but not in FILE-TREE: [path]
[RENAMED] Was [old], now [new]
```

4. Also runs: `python --version`, `node --version`, etc. from ENVIRONMENT.md Tools table — reports any mismatch
5. **If drift count ≤ 10 AND no unexpected findings:** applies fixes in same prompt — adds MISSING entries (with placeholder comment `# [describe]`), removes PHANTOM entries, preserves all existing comments
6. **If drift count > 10:** regenerates FILE-TREE-BOGAME.md from filesystem. Uses ARCHITECTURE-BOGAME.md layer descriptions for top-level comments. Preserves per-file comments where entry existed in previous version
7. **If unexpected findings (files in wrong locations, structural anomalies):** STOP — reports to Claude Chat before applying any fixes

FILE-TREE-BOGAME.md is Tier 3 — update date stamp in header.
If tool versions drifted — updates ENVIRONMENT.md (Tier 3 — update date stamp).

**After combined prompt — STOP.**

---

## Step 2: Cross-Doc Consistency

**Executor:** Claude Code (scout prompt) + Claude Chat (review + fix decision)

Create scout prompt. Claude Code runs all four sub-checks in one prompt:

### 2a. Path Consistency (project files only)

□ All paths in ENVIRONMENT.md → Information Map → exist on disk?
□ All paths in ENVIRONMENT.md → Project Structure → match FILE-TREE?
□ ROADMAP → Document Structure folder paths → match disk?
□ ARCHITECTURE → Satellite Documents paths → match disk?
□ SPRINT-S{N}.md → References table paths → match disk?
□ BACKLOG → routing path to SPEC BACKLOG → matches actual location?

Note: Protocol filename consistency and Before You Begin path validation
belong to 06_Spec-Update (framework layer). Not checked here.

### 2b. Version Alignment

□ Tier 2 docs (ARCHITECTURE, VISION): header version = changelog latest row version?
□ FILE-TREE version pins → match current doc header versions?
□ Cross-references: grep for old version numbers in active docs
  (exclude changelog entries, archives, KB source citations)
□ SYNC lines in footers: referenced doc versions current?

### 2c. Terminology Consistency

□ Stale M-prefix (M4, M5, M6...) in active prose/tables?
  Historical names in changelog/history = OK. Active text = must use S-prefix.

### 2d. Information Map Boundary Check

For each file listed in ENVIRONMENT.md → Information Map:
□ Does the actual file content stay within its declared "Contains" boundaries?
□ Has any "Does NOT Contain" content crept in?
Claude Code reads file headers/TOC and reports if content appears outside declared boundaries.

**Output:** Numbered finding list per sub-check:

```
[BREAK|GAP|NIT] Location: [file:section]
Problem: [what's wrong]
Expected: [correct value]
Actual: [current value]
```

**After scout — STOP. Claude Chat reviews findings and decides:**
- BREAK → must fix before Step 3
- GAP → fix now or create BACKLOG item
- NIT → fix now (low cost) or defer

If fixes needed — create execute prompt. Apply fixes.

Rules for fixes:
- Documents describe what IS, not what was planned
- Remove references to deleted/renamed things
- Never invent — only document what actually exists
- Tier 2 documents: version bump + changelog row
- Tier 3 documents: update date stamp

Validation standard: Declaration §Rule 22

**After fixes — STOP.**

---

## Step 3: Backlog Prune

**Executor:** Claude Code (scout prompt) + Claude Code (execute prompt for transfers)

### Scout: Stale Content + Backlog Health

Create scout prompt. Claude Code checks:

**3a. Document Staleness**
□ ARCHITECTURE: descriptions of deleted/renamed modules or components?
□ ENVIRONMENT: obsolete tools, outdated Shell/Tool Notes, stale Known Limitations?
□ Any project doc with information older than 2 sprints and no current consumer?

**3b. Stale Files on Disk**
□ Sprint folders older than current-6 — flag as archive candidates (handled in Step 4a)
□ Orphaned phase folders (docs/03_sprint/S{N}-*/P{NN}-*/) with no C{NN}-{name}.md files?
  → Never auto-delete — flag to Human if uncertain

**3c. Backlog Staleness**
□ BACKLOG-BOGAME.md: resolved/DONE/SUPERSEDED items still in active tables?
□ BACKLOG items with Target referencing sprints >2 behind current — flag as stale
□ CODE-AUDIT items >3 sprints old — flag for re-evaluate or archive
□ BACKLOG items with Target = completed sprint but Status not ✅/DONE — flag as "completed but unmarked"

**3d. Backlog Health**
□ BACKLOG-BOGAME.md Statistics table — counts match actual item counts?
□ Categories still make sense? Any sections with 0 active items → flag for collapse
□ DONE/SUPERSEDED items all transferred (should be clean after execute below)

Output: stale items per file + stale files on disk + backlog health findings.

**After scout — STOP. Claude Chat reviews. Ambiguous items → Human.**

### Execute: Transfer + Fix

Create execute prompt. Claude Code:

Transfer clear-cut DONE/SUPERSEDED items to CHANGELOG-BOGAME.md.
Leave ambiguous items for Human to decide — do not auto-transfer anything flagged as ambiguous in scout.

Location: `docs/01_refer/ARCHIVES/CHANGELOG-BOGAME.md`
Created if it doesn't exist yet.

**CASCADE:** If CHANGELOG-BOGAME.md created for first time → update FILE-TREE-BOGAME.md.

Format:
```markdown
## S{N} Cleanup — [date]

### From BACKLOG-BOGAME.md
- [DONE/SUPERSEDED item] — removed from active table

### From ARCHITECTURE-BOGAME.md
- [stale description] — module renamed/removed

### From ENVIRONMENT.md
- [obsolete tool/note] — no longer installed/relevant

### Stale Files Archived
- [file path] — reason for archive
```

1. Removes transferred items from source active files
2. Updates BACKLOG-BOGAME.md Statistics counts
3. Tier 2 documents modified: version bump + changelog row
4. Tier 3 documents modified: update date stamp

**After transfers — STOP.**

---

## Step 4: Close

**Executor:** Claude Chat (Sprint Archive decision) + Claude Code (execute prompts)

### 4a. Sprint Archive Decision (Human gate)

□ Count sprint folders in `docs/03_sprint/`

**Archive threshold:** Archive sprint folders older than current-10.
Example: at S14 close, archive S01-S04 (if S14-10=S04 folders exist).
This threshold is fixed — do not re-ask Human each cycle.

□ Sprints older than current-10:
  - **Human confirmation required** for any deletion or compression
  - If Human approves — create execute prompt to archive
  - If Human declines — record decision, proceed

**After decision — STOP.**

### 4b. SPEC-LOG Persist

□ Scan this chat: any unrecorded decisions or framework findings?
□ YES → create execute prompt to append to `docs/02_spec/01_refer/KNOWLEDGE/SPEC-BACKLOG.md`.
         Wait for Claude Code confirmation before proceeding.
□ NO  → record: "SPEC-LOG: nothing to persist"

### 4c. Deferred Items Check

□ Scan chat for any "do later", "next chat", "handle next time" verbal commitments.
□ If found → write each item to Project Backlog or SPEC BACKLOG immediately
  via execute prompt. Verbal intent without a written record does not exist.

### 4d. SPRINT.md Update

S{N}-SPRINT.md is already CLOSED at this point.
If accessible: append Clean-Sync row to Protocol Log.
If not loaded or inaccessible: skip.

### 4e. Final Commit + Handoff

```
git add docs/
git commit -m "clean-sync: S{N} project data hygiene"
git push
```

Next: Session Code S{N}-SPEC — 06_Spec-Update
Load:
  □ 01_Declaration.md
  □ 06_Spec-Update.md
  □ Resolution.md (optional)
  □ docs/01_refer/ENVIRONMENT.md
  □ docs/01_refer/KNOWLEDGE/BACKLOG-BOGAME.md
  □ docs/02_spec/01_refer/KNOWLEDGE/SPEC-BACKLOG.md
  □ S{N}-SNAPSHOT.md
  □ S{N}-SPRINT.md (if exists)
Run: 06_Spec-Update

**STOP — close this chat.**

---

## Removed from v2 → v3

| Element | Reason | Now lives in |
|---------|--------|--------------|
| KNOWLEDGE-BOGAME.md (L0) checks | Brain-Next v2 Phase 4d does L0 rebuild | 07_Brain-Next |
| ADR index/status checks | Brain-Next v2 Phase 4c does status updates | 07_Brain-Next |
| VISION strategic review ("Problem still relevant?") | Strategy question, not hygiene | 02_Sprint-Builder |
| ARCHITECTURE deep content review ("Module relationships accurate?") | Code/knowledge review | 07_Brain-Next / 04_Sprint-Closer |
| Changelog Centralization (4e-CL per-file changelog management) | Dual bookkeeping with Brain-Next | Removed — CHANGELOG-BOGAME.md is archive only |
| MOTHERBOARD.md loading in Before You Begin | Not consumed by any Clean-Sync step | Removed |
| VISION-BOGAME.md loading in Before You Begin | Not consumed — deep review removed | Removed |
| Cross-document SYNC absorbed from Sprint-Closer (full 4a) | Scoped down to paths/versions only | Step 2 (lean version) |
| Scope Traceability (4d) | Sprint-Builder validates scope | 02_Sprint-Builder |
| Analytical Input Traceability (4g) | Brain-Next tracks recommendations | 07_Brain-Next |
| Protocol filename consistency check | Framework layer (Rule 13) | 06_Spec-Update Step 1 |
| Protocol Before You Begin path validation | Framework layer (Rule 13) | 06_Spec-Update Step 1 |
| SPEC BACKLOG items closed by this session | Framework layer (Rule 13) | 06_Spec-Update Step 13 |

## Added in v3

| Element | Source | Step |
|---------|--------|------|
| Operational Limits table | Brain-Next v2 pattern | Header |
| Stale file scan (physical files on disk) | SPEC BACKLOG #46 | Step 3b |
| Sprint archive maintenance | SPEC BACKLOG #47 | Step 7 |
| Concrete pruning criteria (>2 sprints, >3 sprints) | SPEC BACKLOG #53 | Step 3c |
| Reference path validation (Before You Begin paths) | SPEC BACKLOG #65 | Moved to 06_Spec-Update Step 1b |
| CASCADE to FILE-TREE on new file creation | SPEC BACKLOG #45 | Step 4 |
| Backlog Health step (structure, statistics, routing) | BACKLOG TD082 | Step 5 |
| Brain-Next feedback integration | Moved to 02_Sprint-Builder | Removed |
| Chat vs Code executor labels per step | Brain-Next v2 pattern | All steps |
| Tool version check in FILE-TREE step | Moved from Step 2 into Step 1 | Step 1 |

## Changes at Brain-Next S14

| Element | Change | Rationale |
|---------|--------|-----------|
| 8 steps → 4 steps | Steps 2+6 merged into Step 2 (Cross-Doc Consistency, 4 sub-checks); Steps 3+4+5 merged into Step 3 (Backlog Prune); Step 7 absorbed into Step 4a; Step 8 → Step 4 | ADR Brain-Next S14 #98 restructure |
| Scout+execute merge for Step 1 | FILE-TREE sync combined when drift ≤ 10 and no unexpected findings | Rule 16 conditional gate — fallback clause handles anomalies |
| Operational Limits updated | 3-6 prompts (was 4-8) | Fewer round-trips from scout+execute merge |
| Information Map boundary check | Absorbed into Step 2d | Part of Cross-Doc Consistency, not standalone step |
| Sprint Archive | Absorbed into Step 4a with Human gate preserved | Close-phase action |
| Backlog Health statistics | Absorbed into Step 3d | Part of backlog prune scope |

---

[*] 05_Clean-Sync SPEC v3.2.0 * ready
Project data hygiene — FILE-TREE sync, path/version consistency, backlog health, stale pruning
Sequence: 04_Sprint-Closer → 05_Clean-Sync → 06_Spec-Update → 07_Brain-Next → 02_Sprint-Builder
Session Code: S{N}-Clean-Sync
Output: clean FILE-TREE, consistent paths/versions, healthy backlogs, lean active files, CHANGELOG-BOGAME.md
Next chat: S{N+1}-Sprint-Builder — run 02_Sprint-Builder
