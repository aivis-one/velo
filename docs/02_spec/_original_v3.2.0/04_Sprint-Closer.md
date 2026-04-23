# 04_Sprint-Closer
> SPEC v3.2.0 | Code audit + sprint close — ProbeKit audit then SNAPSHOT + RETRO + close
> Triggered by: all phases completed (last cycle of last phase DONE)
> Sequence: 03_Phase-Builder → 04_Sprint-Closer → 05_Clean-Sync → 06_Spec-Update → 07_Brain-Next → 02_Sprint-Builder

---

## Purpose

Two-part protocol: audit code quality before closing, then capture sprint snapshot
and retrospective, formally close the sprint, and set framework update trigger.

Part 1 (Code Audit): ProbeKit generates raw reports → Claude Chat classifies → Claude Code persists.
Part 2 (Sprint Close): SNAPSHOT + RETRO + ROADMAP update + close + SPEC trigger.

Critical audit issues block sprint close.
Document synchronization and cross-validation happen in 05_Clean-Sync (not here).

## Session Control

Every numbered Step is a checkpoint. STOP after completion.
Do not proceed to the next Step without verification.

---

## Severity Levels

| Level | Meaning | Blocks sprint? |
|-------|---------|----------------|
| CRITICAL | Bug, security issue, data loss risk | YES |
| HIGH | Bad practice with real consequences | Recommended to fix |
| MEDIUM | Code smell, maintainability issue | Fix in next sprint |
| LOW | Minor improvement, style | Backlog |

---

## Before You Begin

Load in chat:

□ S{N}-SPRINT.md (current sprint)
□ 01_Declaration.md
□ ARCHITECTURE-BOGAME.md
□ ROADMAP-BOGAME.md (strategic — for Step 10)
□ docs/01_refer/KNOWLEDGE/BACKLOG-BOGAME.md
□ Previous S[N-1]-SNAPSHOT.md (from docs/01_refer/ARCHIVES/SNAPSHOT/)
□ docs/01_refer/ENVIRONMENT.md

Confirm all phases show DONE in S{N}-SPRINT.md before proceeding.

---

# Part 1: Code Audit

### Step 1: Scout ProbeKit State

Scout current ProbeKit pipeline:

□ List all probekit-* skills (names, versions, modes)
□ Determine pipeline order and stage count
□ Report any new skills added since last audit

Scout output informs Step 2 — no hardcoded pipeline assumptions.

### Step 2: Run ProbeKit Pipeline

Run full ProbeKit pipeline based on Step 1 scout findings (all discovered stages).

Reports saved to `docs/01_refer/ARCHIVES/CODE-AUDIT/PROBKIT-REVIEW/`.

### Step 3: Review and Classify

Human sends raw report files from PROBKIT-REVIEW/ to Claude Chat.
Claude Chat does NOT access reports from uploads autonomously (Rule 20).

Claude Chat:
1. Classifies findings by severity (CRITICAL/HIGH/MEDIUM/LOW)
2. Determines blocking vs non-blocking
3. Decides fix/accept/defer for each finding
4. Prepares execute prompts for Claude Code

**Recurring carry-forward check (mandatory at Step 3):**

For each HIGH item being routed to BACKLOG:
1. Grep last 3 S{N}-SNAPSHOT.md files in `docs/01_refer/ARCHIVES/SNAPSHOT/` for the item description or ID.
   Command: `grep -l "ITEM_KEYWORD" docs/01_refer/ARCHIVES/SNAPSHOT/S*-SNAPSHOT.md | tail -3`
2. If item found in 2+ previous SNAPSHOTs under §Carry-Forward or §What Was Left Out:
   → Mark item as `[RECURRING-2]` or `[RECURRING-3+]` in BACKLOG entry
   → Flag for Sprint-Builder auto-promote (Step 3 Scope Definition picks this up)
3. If item found in 3+ previous SNAPSHOTs:
   → Add note: "3rd consecutive sprint — auto-promotes to P1 at next Sprint-Builder Step 3 Scope Definition"

Record in SNAPSHOT §Carry-Forward: recurring items explicitly noted with sprint count.

Canonical case: M4 (bogame-selfdev dup), M5 (kubi-issuance dangling), M6 (secretary-briefing identity) — S13→S14 2nd recurrence (tagged MB-S14-89/90/91). If unfixed in S15, they become 3rd consecutive → auto-promote triggers.


CRITICAL findings?
├── YES → Fix required. Go to Step 6 (Fix Critical Issues)
└── NO  → Proceed to Step 4


### Step 4: Persist Audit Results

Create `docs/01_refer/ARCHIVES/CODE-AUDIT/S{N}-CODE-AUDIT.md`:

```markdown
# Code Audit — Sprint [N]: [Name]
Date: [date]
Audited by: ProbeKit + Claude Chat review

## Summary

| Severity | Count | Blocked? |
|----------|-------|----------|
| CRITICAL | [N] | YES |
| HIGH | [N] | Recommended |
| MEDIUM | [N] | No |
| LOW | [N] | No |

## Audit Sources

| Source | Report | Gate |
|--------|--------|------|
| [skill-name] | [version] | [score or pass/fail] |

## Issues

| # | File | Severity | Issue | Source | Action |
|---|------|----------|-------|--------|--------|
| 1 | ... | ... | ... | ... | ... |

## MEDIUM/LOW → Backlog

[List items added to BACKLOG-BOGAME.md]

## Codebase Balance

[From test-suite output: test distribution, pattern consistency, error handling]

## Balance Findings

| # | Area | Strong Side | Weak Side | Gap Severity | Recommendation |
|---|------|-------------|-----------|--------------|----------------|
```

Commit: `git commit -m "audit: CODE-AUDIT-S{N} [sprint-name]"`

Add MEDIUM/LOW items to BACKLOG-BOGAME.md.

Clean PROBKIT-REVIEW/ raw files (already consolidated in CODE-AUDIT-SN.md).
Keep the folder (ProbeKit writes here on next run).

### Step 5: Decision — Block or Proceed


CRITICAL issues found?
├── YES → Fix required. Go to Step 6.
└── NO  → HIGH issues?
          ├── YES → Present to Human: fix now or accept risk
          └── NO  → Proceed to Part 2 (Step 7)
                    Log MEDIUM/LOW to BACKLOG-BOGAME.md


Note: Codebase Balance findings do not block sprint close. They are input
for next sprint planning (02_Sprint-Builder). HIGH balance items are
transported via SNAPSHOT Carry-Forward.

Validation standard: `docs/02_spec/01_Declaration.md §Rule 22`

**Fix-or-defer guidance for HIGH items:**
- HIGH items with effort ≤ M and no structural refactor required → fix during sprint-closer
  before proceeding to Part 2. Context is warm — Claude Code just scanned the codebase.
- Structural HIGHs (circular imports, cross-module refactors, architecture changes) → defer
  with explicit justification in carry-forward.

### Step 6: Fix Critical and Quick-HIGH Issues

For each CRITICAL issue (and quick-HIGH items per Step 5 guidance):

1. Scout the issue area first
2. Claude Chat validates the execute prompt (Prompt Validation Checklist)
3. Execute fix + tests
4. Verify fix passes existing test suite

Re-verification approach (targeted):
- Security CRITICAL → re-run relevant ProbeKit skill after fix
- Quality CRITICAL/HIGH → targeted verification (grep/test confirmation)
- After ALL fixes → one verification scout of all modified files:
  confirms fix present, no regressions, no secrets in diff

**Multi-Session Handling:**

If fixing CRITICALs requires multiple chats:

Next Action: "Continue 04_Sprint-Closer — fixing CRITICAL: [issue name]"

Protocol Log row: keep as IN PROGRESS until all CRITICALs resolved.
Do NOT proceed to Part 2 until all CRITICALs are fixed.

---

# Part 2: Sprint Close

### Step 7: Create SNAPSHOT

Create S{N}-SNAPSHOT.md in a single pass:

**cloc gate (mandatory):**
Before computing LOC: verify `cloc --version` succeeds.
If cloc absent → **STOP**. Do NOT fall back to `wc -l`.
Report to Human: "cloc not installed — install before running Sprint-Closer Step 7."
Reason: wc-l inflates counts ~73% vs cloc code-only (methodology break documented in S14 SNAPSHOT).

1. **Gather data:**

   □ Git log — last 30 commits (hash, date, message)
   □ Test results — run full test suite, output pass/fail/skip counts per suite
   □ File count by module/directory (top-level dirs only)
   □ Lines of code via cloc (mandatory — see gate above; wc -l fallback forbidden)
   □ List of all P{NN}-{name}.md files in this sprint (path + phase name)
   □ List of all C{NN}-{name}.md files in this sprint (with date from filename or git log)
   □ List of all ADRs relevant to this sprint
     (filter by Sprint column in KNOWLEDGE-BOGAME.md; filename + title from H1)
   □ Current CODE-AUDIT-SN.md summary (counts by severity)
   □ Current CODE-AUDIT-SN.md → Codebase Balance section
     (Balance Findings table + Balance Summary counts)
   □ Previous S[N-1]-SNAPSHOT.md → Sprint Metrics table (if exists, copy rows)

2. **Compose** S{N}-SNAPSHOT.md from gathered data using the Embedded SNAPSHOT Template below

3. **Save** to: `docs/01_refer/ARCHIVES/SNAPSHOT/S{N}-SNAPSHOT.md`

4. **Commit and push:**

   ```
   git add docs/01_refer/ARCHIVES/SNAPSHOT/S{N}-SNAPSHOT.md
   git commit -m "snapshot: S{N}-SNAPSHOT.md created"
   git push
   ```

If any metric cannot be gathered → writes "N/A — [reason]". Never invents numbers.
No draft-in-chat. No manual paste.

### Embedded SNAPSHOT Template

```markdown
# SNAPSHOT — Sprint [N]: [Name]
> SPEC v3.2.0
> Date: [YYYY-MM-DD]
> Status: CLOSED

---

## Summary

[2-3 sentences: what this sprint delivered and why it matters. Write for a future self who hasn't touched this code in 6 months.]

---

## Stats

| Metric | Value |
|--------|-------|
| Phases | [N] |
| Cycles | [N] (C[XX]–C[YY]) |
| Tests | [N] pass, [N] fail, [N] skip |
| Commits | [N] |
| Files | [N] total |
| Lines of Code | [N] (src/) |

---

## Sprint Metrics
> Cumulative tracking across sprints. Copy rows from previous SNAPSHOT
> and add current sprint row. First sprint starts the table.

| Sprint | Tests | CRITICAL | HIGH | MEDIUM | LOW | LOC (src/) |
|--------|-------|----------|------|--------|-----|------------|
| S1 | [N] | [N] | [N] | [N] | [N] | [N] |
| S{N} | [N] | [N] | [N] | [N] | [N] | [N] |

Trend notes: [any notable trends — e.g. "CRITICAL findings trending up",
"LOC growing faster than test count". If no concerns — "No adverse trends."]

---

## Completed Phases

| Phase | Name | Cycles | Status |
|-------|------|--------|--------|
| [N] | [name] | [N] | DONE |

---

## Key Decisions (ADRs)

| ADR | Title | Decision Summary |
|-----|-------|-----------------|
| ADR-001 | [Title] | [One sentence: what was decided] |

If no ADRs: `No architectural decisions recorded for this sprint.`

---

## Code Audit Result

| Severity | Found | Resolved | Logged to Project Backlog |
|----------|-------|----------|---------------------------|
| CRITICAL | [N] | [N] | [N] |
| HIGH | [N] | [N] | [N] |
| MEDIUM | [N] | [N] | [N] |
| LOW | [N] | [N] | [N] |

---

## Codebase Balance Summary

| Gap Severity | Count |
|--------------|-------|
| HIGH | [N] |
| MEDIUM | [N] |
| LOW | [N] |

Top HIGH findings:
- [area]: [one sentence — what is disproportionate]
- [area]: [one sentence]

---

## Test Coverage

| Suite | Tests |
|-------|-------|
| [suite name] | [N] |
| **Total** | **[N]** |

---

## Git Stats

- Commits this sprint: [N]
- First commit: [hash] — [date] — [message]
- Last commit: [hash] — [date] — [message]
- Branch: [branch]

---

## What Was Left Out

[Anything descoped, deferred, or intentionally not done — and why. If nothing was cut: "All planned scope delivered."]

---

## Carry-Forward to Next Sprint

[Tech debt, open issues, or ideas that should be addressed in S[N+1]. These should already be in BACKLOG-BOGAME.md — this section is a summary of the most important ones.]

**Balance HIGH items** (mandatory — list each individually):
- [area]: [finding] — from CODE-AUDIT-SN.md Balance Findings #[N]

---

## Framework Lessons

[Observations about the development process, protocol pain points, or workflow improvements discovered during this sprint. If worth acting on — add to SPEC BACKLOG before closing.]

---

*Snapshot created by: 04_Sprint-Closer protocol*
*Immutable — do not edit after creation*
```

### Step 8: Verify SNAPSHOT

□ S{N}-SNAPSHOT.md exists in docs/01_refer/ARCHIVES/SNAPSHOT/?
□ No "N/A" values that should have real data?
□ Sprint Metrics table present and rows copied from previous SNAPSHOT?
□ Codebase Balance Summary section present and filled?
□ Balance HIGH items listed individually in Carry-Forward?
□ Commit pushed?

If any check fails — fix before proceeding.

---

### Step 9: Verify Sprint Completion

□ All phases in S{N}-SPRINT.md marked DONE
□ All P{NN}-{name}.md files have Status: DONE
□ No unresolved CRITICALs in CODE-AUDIT
□ S{N}-SNAPSHOT.md exists and verified (Steps 7–8)
□ All commits pushed to remote

If anything is open — do not proceed. Resolve first.

---

### Step 10: Update ROADMAP-BOGAME.md (strategic)

Mark current sprint as complete in the strategic roadmap:

S{N}: [name] — DONE ([date])

Check if next sprint is already listed. If not — add placeholder:

S[N+1]: [name] — PLANNED

---

### Step 11: Close S{N}-SPRINT.md

S{N}-SPRINT.md stays in the sprint folder forever as immutable history.
Updated to final state, then frozen.

Update Current State:

| Item | Value |
|------|-------|
| Phase | All phases DONE |
| Cycle | — |
| Status | SPRINT CLOSED |

Fill Plan vs Reality section:
- Planned phases vs actual phases
- Planned cycles vs actual cycles
- Duration: first Protocol Log date → today

Fill What Worked / What Didn't / Carry Forward from S{N}-SNAPSHOT.md
sections "Framework Lessons" and "Carry-Forward".

Add Protocol Log row:

| S{N}-Sprint-Closer | 04_Sprint-Closer | [date] | DONE — Sprint [N] CLOSED |

Update Next Action:

SPRINT CLOSED.
Next: Session Code S{N}-Clean-Sync — run 05_Clean-Sync

Update For Human:

## For Human
> Next chat instruction. Copy-paste.

**Session Code:** S{N}-Clean-Sync
**Load:**
1. Framework: 01_Declaration.md + 05_Clean-Sync.md
2. Project: ENVIRONMENT.md + FILE-TREE-BOGAME.md + BACKLOG-BOGAME.md + ARCHITECTURE-BOGAME.md + ROADMAP-BOGAME.md
3. Sprint: S{N}-SPRINT.md + S{N}-SNAPSHOT.md
**Run:** 05_Clean-Sync

> Full sequence: 05_Clean-Sync → 06_Spec-Update → 07_Brain-Next → 02_Sprint-Builder.
> ENVIRONMENT.md SPEC Update set to PENDING. Framework-phase protocols run regardless.

Update Last Session:

Sprint [N] closed. SNAPSHOT created.
SPEC Update trigger set to PENDING.
S{N}-RETRO.md created.

This file is now read-only history.

---

### Step 12: Sprint Retrospective

Create `docs/01_refer/ARCHIVES/RETRO/S{N}-RETRO.md`

Content: structured retrospective covering process observations, protocol pain points,
and workflow improvements discovered during this sprint. Use data from S{N}-SNAPSHOT.md
"Framework Lessons" and "What Worked / What Didn't" sections.

S{N}-RETRO.md does NOT include a Carry-Forward section — S{N}-SNAPSHOT.md is SSOT
for carry-forward items. RETRO focuses exclusively on process observations.

Commit with sprint close commit (Step 14).

---

### Step 13: Set SPEC Update Trigger

Update `docs/01_refer/ENVIRONMENT.md`:

## SPEC Update

| Item | Value |
|------|-------|
| Status | **PENDING (after S{N})** |

This triggers enforcement: any new chat that loads ENVIRONMENT.md will see PENDING.
Framework-phase protocols (05, 06, 07) run regardless. Project work (02, 03) is blocked.

**Also write SPEC Update banner to 01_Declaration.md:**

Insert at the top of the Entry Rule section in `docs/02_spec/01_Declaration.md`:

> ⚠️ SPEC UPDATE REQUIRED
> Sprint S{N} closed. Framework phase has NOT been run.
> DO NOT start project work. Run framework phase (05→06→07) first.
> This banner is removed by 06_Spec-Update after completing framework health check.

Tier 3 document — update date stamp in ENVIRONMENT.md header.

---

### Step 14: Close — Universal Close Flow

**14a. Cleanup (optional)**

Remove any temp files, draft docs, or scratch notes created during the sprint.

Do NOT delete: C{NN}-{name}.md, P{NN}-{name}.md, ADR files,
S{N}-SNAPSHOT.md, S{N}-SPRINT.md, S{N}-RETRO.md, CODE-AUDIT-SN.md.

**14b. SPEC-LOG Persist**

Scan this chat for unrecorded decisions or framework findings:

□ Any SPEC-LOG items from this session?
  YES → persist to docs/02_spec/01_refer/KNOWLEDGE/SPEC-BACKLOG.md.
        Wait for Claude Code confirmation.
  NO  → record: "SPEC-LOG: nothing to persist"

**14c. Archive DONE items to CHANGELOG**

Transfer DONE/SUPERSEDED project items from BACKLOG-BOGAME.md
to `docs/01_refer/ARCHIVES/CHANGELOG-BOGAME.md`.

**14d. Final Commit**

```
git add docs/
git commit -m "sprint: S{N} [name] — CLOSED"
git push
```

**14e. Hand Off**

## For Human
> Next chat instruction. Copy-paste.

**Session Code:** S{N}-Clean-Sync
**Load:**
1. Framework: 01_Declaration.md + 05_Clean-Sync.md
2. Project: ENVIRONMENT.md + FILE-TREE-BOGAME.md + BACKLOG-BOGAME.md + ARCHITECTURE-BOGAME.md + ROADMAP-BOGAME.md
3. Sprint: S{N}-SPRINT.md + S{N}-SNAPSHOT.md
**Run:** 05_Clean-Sync

Full sequence after this sprint:
05_Clean-Sync → 06_Spec-Update → 07_Brain-Next → 02_Sprint-Builder.
Each protocol specifies its own load list and hand-off.

## Chat Boundary — MANDATORY STOP

After final commit — this chat is DONE. Close it.
Do NOT start the next protocol in this chat.
One protocol = one chat. No exceptions.
Next protocol = new chat.

---

## Checklist

□ 1: ProbeKit state scouted
□ 2: Pipeline run, reports in PROBKIT-REVIEW/
□ 3: Findings classified by severity
□ 4: CODE-AUDIT-SN.md created + committed + MEDIUM/LOW in BACKLOG
□ 5: Decision made (block/proceed)
□ 6: CRITICALs fixed (if any)
□ 7: SNAPSHOT created + committed
□ 8: SNAPSHOT verified
□ 9: Sprint completion verified
□ 10: ROADMAP updated
□ 11: S{N}-SPRINT.md closed (Plan vs Reality, Protocol Log, For Human)
□ 12: RETRO created
□ 13: SPEC trigger PENDING + Declaration banner
□ 14: SPEC-LOG persisted, DONE items archived, final commit, handoff written

---

[04_Sprint-Closer] SPEC v3.2.0
Code audit (ProbeKit) + sprint close (SNAPSHOT + RETRO + ROADMAP + trigger)
Sequence: 03_Phase-Builder → 04_Sprint-Closer → 05_Clean-Sync → 06_Spec-Update → 07_Brain-Next → 02_Sprint-Builder
Output: CODE-AUDIT-SN/ + SNAPSHOT/ + RETRO/ + ENVIRONMENT trigger PENDING
Next chat: S{N}-Clean-Sync — run 05_Clean-Sync
