# 04_Sprint-Closer
> SPEC v3.2-velo | Code audit + sprint close — ProbeKit lite profile, then SNAPSHOT + RETRO
> Triggered by: all phases completed (last cycle of last phase DONE)
> Sequence: 03_Phase-Builder → 04_Sprint-Closer → 05_Clean-Sync → 02_Sprint-Builder

---

## Purpose

Two-part protocol: audit code quality before closing, then capture sprint snapshot
and retrospective, formally close the sprint.

Part 1 (Code Audit): ProbeKit lite profile generates reports → Claude Chat classifies → Claude Code persists.
Part 2 (Sprint Close): SNAPSHOT + RETRO + close.

Critical audit issues block sprint close.
Document synchronization happens in 05_Clean-Sync (not here).

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
□ docs/01_refer/ARCHITECTURE.md
□ docs/01_refer/BACKLOG.md
□ Previous S[N-1]-SNAPSHOT.md (from docs/01_refer/ARCHIVES/SNAPSHOT/, if exists)
□ docs/01_refer/ENVIRONMENT.md

Confirm all phases show DONE in S{N}-SPRINT.md before proceeding.

---

# Part 1: Code Audit

## Step 1: Scout ProbeKit State

Scout current ProbeKit lite profile:

□ Confirm the 6 lite-profile skills are available locally (see Step 2)
□ Report versions
□ Flag any absent skills

Scout output informs Step 2 — no hardcoded assumptions.

## Step 2: Run ProbeKit Lite Profile (Velo)

Run the following skills in order. Skip any that report "not applicable" for current sprint scope.

| Skill | Why included |
|---|---|
| `probekit-type-audit` | TypeScript / Vue 3 type safety; catches unsafe casts, missing types |
| `probekit-code-audit` | General code review — bugs, naming, quality |
| `probekit-a11y-audit` | Accessibility is a wellness-app concern; WCAG checks |
| `probekit-responsive-audit` | Mobile-first PWA — breakpoints, touch targets |
| `probekit-security-audit` | OWASP top 10, secret leaks |
| `probekit-design-audit` | Brand/token compliance against Design_prototype |

Optional (run by explicit Human request, not every sprint):
- `probekit-dependency-audit` — once per 3–4 sprints
- `probekit-i18n-audit` — when localization work is in scope
- `probekit-comprehension-debt` — when churn spikes

Do NOT run the full `probekit-test-suite` (13 stages) in the auto-close pass — it produces noise disproportionate to a 1–2 week frontend sprint. Human may invoke it on demand.

Reports saved to `docs/01_refer/ARCHIVES/CODE-AUDIT/PROBKIT-REVIEW/`.

## Step 3: Review and Classify

Human sends raw report files from `PROBKIT-REVIEW/` to Claude Chat.
Claude Chat does NOT access reports from uploads autonomously (Rule 20).

Claude Chat:
1. Classifies findings by severity (CRITICAL/HIGH/MEDIUM/LOW)
2. Determines blocking vs non-blocking
3. Decides fix/accept/defer for each finding
4. Prepares execute prompts for Claude Code

```
CRITICAL findings?
├── YES → Fix required. Go to Step 6 (Fix Critical Issues)
└── NO  → Proceed to Step 4
```

## Step 4: Persist Audit Results

Create `docs/01_refer/ARCHIVES/CODE-AUDIT/S{N}-CODE-AUDIT.md`:

```markdown
# Code Audit — Sprint [N]: [Name]
Date: [date]
Audited by: ProbeKit lite profile + Claude Chat review

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
| [skill-name] | [version] | [pass/fail or score] |

## Issues

| # | File | Severity | Issue | Source | Action |
|---|------|----------|-------|--------|--------|
| 1 | ... | ... | ... | ... | ... |

## MEDIUM/LOW → Backlog

[List items added to BACKLOG.md]
```

Commit: `git commit -m "audit: CODE-AUDIT-S{N} [sprint-name]"`

Add MEDIUM/LOW items to `BACKLOG.md`.

Clean `PROBKIT-REVIEW/` raw files (already consolidated in `CODE-AUDIT-SN.md`).
Keep the folder (ProbeKit writes here on next run).

## Step 5: Decision — Block or Proceed

```
CRITICAL issues found?
├── YES → Fix required. Go to Step 6.
└── NO  → HIGH issues?
          ├── YES → Present to Human: fix now or accept risk
          └── NO  → Proceed to Part 2 (Step 7)
                    Log MEDIUM/LOW to BACKLOG.md
```

Validation standard: `docs/02_spec/01_Declaration.md §Rule 22`

**Fix-or-defer guidance for HIGH items:**
- HIGH items with effort ≤ M and no structural refactor required → fix during sprint-closer before proceeding to Part 2. Context is warm — Claude Code just scanned the codebase.
- Structural HIGHs (cross-module refactors, architecture changes) → defer with explicit justification in carry-forward.

## Step 6: Fix Critical and Quick-HIGH Issues

For each CRITICAL issue (and quick-HIGH items per Step 5 guidance):

1. Scout the issue area first
2. Claude Chat validates the execute prompt (Prompt Validation Checklist)
3. Execute fix + tests
4. Verify fix passes existing test suite

Re-verification approach (targeted):
- Security CRITICAL → re-run relevant ProbeKit skill after fix
- Quality CRITICAL/HIGH → targeted verification (grep/test confirmation)
- After ALL fixes → one verification scout of all modified files: confirms fix present, no regressions, no secrets in diff

**Multi-Session Handling:**

If fixing CRITICALs requires multiple chats:

```
Next Action: "Continue 04_Sprint-Closer — fixing CRITICAL: [issue name]"
```

Protocol Log row: keep as IN PROGRESS until all CRITICALs resolved.
Do NOT proceed to Part 2 until all CRITICALs are fixed.

---

# Part 2: Sprint Close

## Step 7: Create SNAPSHOT

Create `S{N}-SNAPSHOT.md` in a single pass:

**cloc gate (mandatory):**
Before computing LOC: verify `cloc --version` succeeds.
If cloc absent → **STOP**. Do NOT fall back to `wc -l`.
Report to Human: "cloc not installed — install before running Sprint-Closer Step 7."

1. **Gather data:**

   □ Git log — last 30 commits (hash, date, message)
   □ Test results — run full test suite, output pass/fail/skip counts
   □ File count by top-level directory (`frontend/src/`)
   □ Lines of code via cloc (mandatory — no fallback)
   □ List of cycles in this sprint (C{NN} IDs with dates)
   □ Current `CODE-AUDIT-SN.md` summary (counts by severity)
   □ Previous S[N-1]-SNAPSHOT.md → Sprint Metrics table (if exists, copy rows)

2. **Compose** `S{N}-SNAPSHOT.md` from gathered data using the Embedded SNAPSHOT Template below.

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
> SPEC v3.2-velo
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
| Lines of Code | [N] (frontend/src/) |

---

## Sprint Metrics
> Cumulative tracking across sprints. Copy rows from previous SNAPSHOT
> and add current sprint row. First sprint starts the table.

| Sprint | Tests | CRITICAL | HIGH | MEDIUM | LOW | LOC (src/) |
|--------|-------|----------|------|--------|-----|------------|
| S1 | [N] | [N] | [N] | [N] | [N] | [N] |
| S{N} | [N] | [N] | [N] | [N] | [N] | [N] |

Trend notes: [any notable trends — e.g. "CRITICAL findings trending up", "LOC growing faster than test count". If no concerns — "No adverse trends."]

---

## Completed Phases

| Phase | Name | Cycles | Status |
|-------|------|--------|--------|
| [N] | [name] | [N] | DONE |

---

## Key Decisions

| # | Title | Decision Summary |
|---|-------|-----------------|
| #NNN | [Title] | [One sentence: what was decided] |

If no new decisions: `No new decisions recorded for this sprint.`

---

## Code Audit Result

| Severity | Found | Resolved | Logged to BACKLOG |
|----------|-------|----------|-------------------|
| CRITICAL | [N] | [N] | [N] |
| HIGH | [N] | [N] | [N] |
| MEDIUM | [N] | [N] | [N] |
| LOW | [N] | [N] | [N] |

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

[Tech debt, open issues, or ideas that should be addressed in S[N+1]. These should already be in BACKLOG.md — this section is a summary of the most important ones.]

---

## Framework Lessons

[Observations about the development process, protocol pain points, or workflow improvements discovered during this sprint. If worth acting on — add to BACKLOG.md before closing.]

---

*Snapshot created by: 04_Sprint-Closer protocol*
*Immutable — do not edit after creation*
```

## Step 8: Verify SNAPSHOT

□ `S{N}-SNAPSHOT.md` exists in `docs/01_refer/ARCHIVES/SNAPSHOT/`?
□ No "N/A" values that should have real data?
□ Sprint Metrics table present and rows copied from previous SNAPSHOT?
□ Commit pushed?

If any check fails — fix before proceeding.

---

## Step 9: Verify Sprint Completion

□ All phases in `S{N}-SPRINT.md` marked DONE
□ Any external `P{NN}-{name}.md` files have Status: DONE
□ No unresolved CRITICALs in CODE-AUDIT
□ `S{N}-SNAPSHOT.md` exists and verified (Steps 7–8)
□ All commits pushed to remote

If anything is open — do not proceed. Resolve first.

---

## Step 10: Close S{N}-SPRINT.md

`S{N}-SPRINT.md` stays in the sprint folder forever as immutable history.
Updated to final state, then frozen.

Update Current State:

```
| Item | Value |
|------|-------|
| Phase | All phases DONE |
| Cycle | — |
| Status | SPRINT CLOSED |
```

Fill Plan vs Reality section:
- Planned phases vs actual phases
- Planned cycles vs actual cycles
- Duration: first Protocol Log date → today

Fill What Worked / What Didn't / Carry Forward from `S{N}-SNAPSHOT.md`
sections "Framework Lessons" and "Carry-Forward".

Add Protocol Log row:

```
| S{N}-Sprint-Closer | 04_Sprint-Closer | [date] | DONE — Sprint [N] CLOSED |
```

Update Next Action:

```
SPRINT CLOSED.
Next: Session Code S{N}-Clean-Sync — run 05_Clean-Sync
```

Update For Human:

```
## For Human
> Next chat instruction. Copy-paste.

**Session Code:** S{N}-Clean-Sync
**Load:**
1. Framework: 01_Declaration.md + 05_Clean-Sync.md
2. Project: ENVIRONMENT.md + FILE-TREE.md + BACKLOG.md + ARCHITECTURE.md
3. Sprint: S{N}-SPRINT.md + S{N}-SNAPSHOT.md
**Run:** 05_Clean-Sync
```

Update Last Session:

```
Sprint [N] closed. SNAPSHOT created. RETRO created.
```

This file is now read-only history.

---

## Step 11: Sprint Retrospective

Create `docs/01_refer/ARCHIVES/RETRO/S{N}-RETRO.md`

Content: structured retrospective covering process observations, protocol pain points, and workflow improvements discovered during this sprint. Use data from `S{N}-SNAPSHOT.md` "Framework Lessons" and "What Worked / What Didn't" sections.

`S{N}-RETRO.md` does NOT include a Carry-Forward section — `S{N}-SNAPSHOT.md` is SSOT for carry-forward items. RETRO focuses exclusively on process observations.

Commit with sprint close commit (Step 12).

---

## Step 12: Close — Universal Close Flow

**12a. Cleanup (optional)**

Remove any temp files, draft docs, or scratch notes created during the sprint.

Do NOT delete: `C{NN}-{name}.md` (if exist), `P{NN}-{name}.md` (if exist), `S{N}-SNAPSHOT.md`, `S{N}-SPRINT.md`, `S{N}-RETRO.md`, `CODE-AUDIT-SN.md`.

**12b. Archive DONE items to CHANGELOG (optional)**

Transfer DONE/SUPERSEDED project items from `BACKLOG.md` to `docs/01_refer/ARCHIVES/CHANGELOG.md` if any accumulated.

**12c. Deferred Items Check**

Scan chat for any "do later", "next chat", "handle next time" verbal commitments. If found → write each to `BACKLOG.md` via execute prompt. Unrecorded decisions → `decisions.md` via execute prompt.

**12d. Final Commit**

```
git add docs/
git commit -m "sprint: S{N} [name] — CLOSED"
git push
```

**12e. Hand Off**

```
## For Human
> Next chat instruction. Copy-paste.

**Session Code:** S{N}-Clean-Sync
**Load:**
1. Framework: 01_Declaration.md + 05_Clean-Sync.md
2. Project: ENVIRONMENT.md + FILE-TREE.md + BACKLOG.md + ARCHITECTURE.md
3. Sprint: S{N}-SPRINT.md + S{N}-SNAPSHOT.md
**Run:** 05_Clean-Sync
```

Sequence after this sprint: 05_Clean-Sync → 02_Sprint-Builder.
Each protocol specifies its own load list and hand-off.

## Chat Boundary — MANDATORY STOP

After final commit — this chat is DONE. Close it.
Do NOT start the next protocol in this chat.
One protocol = one chat. No exceptions.
Next protocol = new chat.

---

## Checklist

□ 1: ProbeKit lite profile scouted
□ 2: Lite pipeline run (6 skills), reports in PROBKIT-REVIEW/
□ 3: Findings classified by severity
□ 4: CODE-AUDIT-SN.md created + committed + MEDIUM/LOW in BACKLOG
□ 5: Decision made (block/proceed)
□ 6: CRITICALs fixed (if any)
□ 7: SNAPSHOT created + committed
□ 8: SNAPSHOT verified
□ 9: Sprint completion verified
□ 10: S{N}-SPRINT.md closed (Plan vs Reality, Protocol Log, For Human)
□ 11: RETRO created
□ 12: DONE items archived (optional), deferred items written, final commit, handoff

---

[04_Sprint-Closer] SPEC v3.2-velo
Code audit (ProbeKit lite profile) + sprint close (SNAPSHOT + RETRO)
Sequence: 03_Phase-Builder → 04_Sprint-Closer → 05_Clean-Sync → 02_Sprint-Builder
Output: CODE-AUDIT-SN/ + SNAPSHOT/ + RETRO/
Next chat: S{N}-Clean-Sync — run 05_Clean-Sync
