# 05_Clean-Sync
> SPEC v3.2-velo | Project data hygiene — FILE-TREE sync, path consistency, backlog pruning
> Triggered by: after 04_Sprint-Closer
> Sequence: 04_Sprint-Closer → 05_Clean-Sync → 02_Sprint-Builder

---

## Purpose

Physical hygiene of project files. Sync FILE-TREE with disk, cross-validate
paths between documents, prune stale content from active files,
archive dead information.

Clean-Sync does NOT do:
- Strategy review (→ 02_Sprint-Builder)
- Code quality review (→ 04_Sprint-Closer Part 1)

Clean-Sync runs AFTER Sprint-Closer which may create filesystem drift from code audit fixes, SNAPSHOT creation, RETRO creation.

---

## Before You Begin

Load in chat:

□ 01_Declaration.md
□ docs/01_refer/ENVIRONMENT.md
□ docs/01_refer/FILE-TREE.md
□ docs/01_refer/BACKLOG.md
□ docs/01_refer/ARCHITECTURE.md
□ S{N}-SNAPSHOT.md (latest closed sprint)
□ S{N}-SPRINT.md (current or just-closed sprint)

This is a deterministic protocol — execute immediately after loading documents.
No Session Plan confirmation required (Rule 6).

---

### Operational Limits

| Operation | Per-session limit | Notes |
|-----------|------------------|-------|
| FILE-TREE scan + fix (combined) | 1 prompt | Scout+execute merged for drift ≤ 10 |
| Cross-doc path consistency scout | 1 prompt | All checks in one scout |
| Cross-doc fixes | 1-2 prompts | Depends on BREAK count |
| Backlog prune + transfers | 1-2 prompts | Depends on volume |
| Total expected | 3-5 Claude Code prompts per session |

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
1. Generates fresh file tree from actual filesystem (scope: `frontend/src/` + `docs/`)
2. Compares with existing `FILE-TREE.md`
3. Reports findings:

```
[PHANTOM] Listed in FILE-TREE but not on disk: [path]
[MISSING] On disk but not in FILE-TREE: [path]
[RENAMED] Was [old], now [new]
```

4. Also runs: `node --version`, `npm --version` — reports any mismatch against ENVIRONMENT.md Tools table
5. **If drift count ≤ 10 AND no unexpected findings:** applies fixes in same prompt — adds MISSING entries (with placeholder comment `# [describe]`), removes PHANTOM entries, preserves all existing comments
6. **If drift count > 10:** regenerates `FILE-TREE.md` from filesystem. Uses `ARCHITECTURE.md` layer descriptions for top-level comments. Preserves per-file comments where entry existed in previous version
7. **If unexpected findings (files in wrong locations, structural anomalies):** STOP — reports to Claude Chat before applying any fixes

`FILE-TREE.md` — update date stamp in header.
If tool versions drifted — updates `ENVIRONMENT.md` date stamp.

**After combined prompt — STOP.**

---

## Step 2: Cross-Doc Consistency

**Executor:** Claude Code (scout prompt) + Claude Chat (review + fix decision)

Create scout prompt. Claude Code runs path consistency checks:

### 2a. Path Consistency (project files only)

□ All paths in `ENVIRONMENT.md` → Information Map → exist on disk?
□ All paths in `ENVIRONMENT.md` → references → match `FILE-TREE.md`?
□ `ARCHITECTURE.md` → any file path references → match disk?
□ `S{N}-SPRINT.md` → references table paths → match disk?
□ `BACKLOG.md` → any path references → match disk?

**Output:** Numbered finding list:

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
- Update date stamp on modified files

Validation standard: Declaration §Rule 22

**After fixes — STOP.**

---

## Step 3: Backlog Prune

**Executor:** Claude Code (scout prompt) + Claude Code (execute prompt for transfers)

### Scout: Stale Content

Create scout prompt. Claude Code checks:

**3a. Document Staleness**
□ ARCHITECTURE: descriptions of deleted/renamed modules or components?
□ ENVIRONMENT: obsolete tools, outdated Shell/Tool Notes, stale Known Limitations?
□ Any project doc with information older than 2 sprints and no current consumer?

**3b. Stale Files on Disk**
□ Sprint folders older than current-6 — flag as archive candidates (handled in Step 4a)
□ Orphaned phase folders (`docs/03_sprint/S{N}-*/P{NN}-*/`) with no content?
  → Never auto-delete — flag to Human if uncertain

**3c. Backlog Staleness**
□ `BACKLOG.md`: resolved/DONE/SUPERSEDED items still in active tables?
□ Items with Target referencing sprints >2 behind current — flag as stale
□ Items with Target = completed sprint but Status not DONE — flag as "completed but unmarked"

Output: stale items per file + stale files on disk.

**After scout — STOP. Claude Chat reviews. Ambiguous items → Human.**

### Execute: Transfer + Fix

Create execute prompt. Claude Code:

Transfer clear-cut DONE/SUPERSEDED items to `CHANGELOG.md`.
Leave ambiguous items for Human to decide — do not auto-transfer anything flagged as ambiguous in scout.

Location: `docs/01_refer/ARCHIVES/CHANGELOG.md`
Created if it doesn't exist yet.

**CASCADE:** If `CHANGELOG.md` created for first time → update `FILE-TREE.md`.

Format:
```markdown
## S{N} Cleanup — [date]

### From BACKLOG.md
- [DONE/SUPERSEDED item] — removed from active table

### From ARCHITECTURE.md
- [stale description] — module renamed/removed

### From ENVIRONMENT.md
- [obsolete tool/note] — no longer installed/relevant

### Stale Files Archived
- [file path] — reason for archive
```

1. Removes transferred items from source active files
2. Updates date stamps on modified files

**After transfers — STOP.**

---

## Step 4: Close

**Executor:** Claude Code (execute prompts)

### 4a. Sprint Archive

□ Count sprint folders in `docs/03_sprint/`

**Archive threshold:** Archive sprint folders older than current-10.
Example: at S14 close, archive S01-S04 (if S14-10=S04 folders exist).
This threshold is fixed — no Human gate required below threshold.

If threshold reached → create execute prompt to archive to `docs/03_sprint/_archive/`.
If below threshold → skip, record "no sprints to archive".

### 4b. Deferred Items Check

□ Scan chat for any "do later", "next chat", "handle next time" verbal commitments.
□ If found → write each item to `BACKLOG.md` immediately via execute prompt. Verbal intent without a written record does not exist.

### 4c. SPRINT.md Update

S{N}-SPRINT.md is already CLOSED at this point.
If accessible: append Clean-Sync row to Protocol Log.
If not loaded or inaccessible: skip.

### 4d. Final Commit + Handoff

```
git add docs/
git commit -m "clean-sync: S{N} project data hygiene"
git push
```

## For Human
> Next chat instruction. Copy-paste.

**Session Code:** S{N+1}-Sprint-Builder
**Load:**
1. Framework: 01_Declaration.md + 02_Sprint-Builder.md
2. Project: ENVIRONMENT.md + ARCHITECTURE.md + BACKLOG.md + decisions.md
3. Sprint: S{N}-SNAPSHOT.md (previous closed sprint)
**Run:** 02_Sprint-Builder — plan next sprint

**STOP — close this chat.**

---

[*] 05_Clean-Sync SPEC v3.2-velo * ready
Project data hygiene — FILE-TREE sync, path consistency, backlog pruning
Sequence: 04_Sprint-Closer → 05_Clean-Sync → 02_Sprint-Builder
Session Code: S{N}-Clean-Sync
Output: clean FILE-TREE, consistent paths, lean active files, optional CHANGELOG.md
Next chat: S{N+1}-Sprint-Builder — run 02_Sprint-Builder
