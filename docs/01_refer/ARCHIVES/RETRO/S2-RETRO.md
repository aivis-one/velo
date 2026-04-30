# RETRO — Sprint 2: User Foundation + Booking Flow

> SPEC v3.2-velo
> Date: 2026-04-30
> Status: CLOSED — process observations only (Carry-Forward in S2-SNAPSHOT.md)

---

## Process observations

S2 was the first sprint where the protocol stack was stress-tested at non-pilot pace. S1 had been a deliberate slow-walk (14 cycles, 4 phases, full audit ceremony). S2 ran at 5× density — 21 cycles in 5 phases — and deliberately inverted decision #042 mid-sprint when the sponsor demo target was added (decision #049 speedrun mode). The protocol held up; the audit ceremony deferral is the single gap, and it's tracked.

---

## What worked

### Regen self-host pipeline (decision #046)

Phase 05 C15 was the first application of the self-host openapi regen fallback. Partner had patched Pydantic schemas in `81304a6` but hadn't re-run regen against fresh openapi. Local `docker compose up postgres redis app` + `curl /openapi.json` + `python backend/scripts/generate_ts_types.py` produced a clean `generated.ts` diff that surfaced 3 new fields the partner had landed but not signaled (E.1-E.3). Three carry-forward consumer migrations (BACKLOG #26 #27 #32) closed in the same cycle. The fallback is now battle-tested; future stalls in BACKEND-COORDINATION § E will use it without ceremony.

### Path Y (decision #047) discipline

C16 was the first deliberate deviation from the Claude Design pipeline (decision #002). Direct port from skin PNG produced working SFC + correct logic in ~150 LOC, faster than gen→handoff→wire-up would have. The trade-off (visual fidelity MEDIUM, not pixel-perfect) was made explicit in #047 and reaffirmed at every Phase 06 cycle. The pattern scaled cleanly into the 14-cycle MEGA-1 batch.

### Speedrun mode (decision #049)

The sponsor demo target arrived mid-sprint. The standard density envelope (S1's 14 cycles in 4 phases over 5 days, with full audit ceremony) was incompatible with the timeline. Decision #049 made the trade-off explicit: collapse cycles into mega-execute prompts, defer audit to BACKLOG #100, ship for demo, backfill quality before production. Three deploy gates closed clean (C15 regen, MEGA-1 +5218 LOC, MEGA-2 +6443 LOC). Throughput multiplier vs S1 baseline: ~5× cycles per closure commit.

### Hybrid visual verify (3-tier A/B/C)

A reply rate: 3/3 deploys A clean. No B (BREAK with description → inline-fix) and no C (NIT/GAP list → BACKLOG entries) paths exercised. This validates the policy: when scope is well-defined per skin reference and Path Y MEDIUM fidelity is acceptable, first-attempt visual verify is cheap. Per-cycle staging deploy + A-reply rhythm is the right primitive at this density.

### BACKLOG #96 retry pattern

`velo update` transient ("Uncommitted changes detected") fires on every deploy ≥600 LOC. Paramiko retry on fresh session resolves cleanly. The pattern is documented in BACKLOG #96 and demonstrated 4/4 times during speedrun. The hypothesis (timing race in pre-fetch git status check, scaling with build window) is now CONFIRMED data. Server-side fix candidate logged for post-demo cycle.

### Rule 28 Server Action Plan + Rule 29 persist-or-lose

Rule 28 prevented a catastrophic mis-push in the very first deploy: my initial Server Action Plan proposed `git push origin main`, which Human caught and corrected to `new_desing` (per ENVIRONMENT.md §Git Workflow + BACKLOG #39). Without the PAUSE primitive, the wrong-branch push would have happened. Rule 29 (persist-or-lose) caught the designer batch reference issue at S2-P06 §S1 — the new mockups were referenced in framework docs before being committed to repo; resolved by curl + tar.gz extract + commit, then framework references became valid.

---

## What didn't work

### BACKLOG #92 commit-discipline gap

The new designer batch (`docs/04_assets/velo-design-system-2026-04-30/`) was referenced in S2 re-planning docs before being committed to the repo. Discovered at S2-P06 §S1 when scout couldn't find the assets. Resolved via Rule 29 (#92 first application) but the gap surfaced a process risk: framework docs reference SSOT artifacts that must be persisted to repo, not just available on disk. Pattern now documented in #92 + Rule 29.

### MEGA-1 / MEGA-2 split required against handoff

Speedrun handoff recommended 1 mega-execute covering all 33 cycles. Context budget concerns forced a split into MEGA-1 (S2 P07/P08/P09) + MEGA-2 (S3 P10/P11/P12/P13). The split was clean (no rework, no integration issues at MEGA-2 of MEGA-1 surface) but it does mean the prompt → execute → commit → deploy → verify cycle ran twice instead of once. For future speedruns, plan for split unless the LOC budget is < ~3000 lines.

### Intermediate `1f37a61` gitignore housekeeping commit

Between MEGA-1 and MEGA-2, the `.claude_tmp/` paramiko deploy scratch directory was untracked in working tree. Pre-Exec validation for MEGA-2 required clean `git status --porcelain`. A small intermediate commit (`1f37a61 chore: gitignore .claude_tmp/`) was authored to satisfy the gate. Not planned, not on the roadmap, but harmless and preserved in history. For future speedruns, consider gitignoring `.claude_tmp/` (or analogous scratch dirs) at sprint open to avoid this micro-commit.

### Bash-bridge stdout buffering on Windows (single occurrence)

The first MEGA-2 paramiko deploy run was launched as a background Bash task. The Python process completed successfully (containers Up, HEAD updated, services Healthy) but stdout was held in buffer for ~10 minutes before flushing. The completion event eventually fired. Not a deploy issue; a tooling latency quirk. Going forward: run paramiko deploys synchronously to avoid buffer-flush surprises.

---

## Process refinements (carry to S4+)

### Speedrun mode (#049) as named pattern

The sprint-mode-vs-throughput trade-off is now explicit. Future demos / time-boxed deliverables can invoke #049 with full understanding of what's deferred. Pattern: collapse N cycles into M mega-execute prompts (M ≤ N/5), defer audit ceremony to a BACKLOG ticket gating production promotion, run aggregate visual verify gates instead of per-cycle. Document deferred items in CHANGELOG closure entry.

### PRACTICE_TYPE_EMOJI → PRACTICE_TYPE_ICON refactor

Pattern: when a `Record<string, string>` (emoji map) is replaced with `Record<string, Component>` (icon component map), keep the original export as a deprecated empty-string shim for legacy callers. New callers use the icon map; old callers tolerate the empty string until refactored. Eventually delete the shim. This pattern unblocks gradual migration without a single-commit big-bang refactor.

### Per-cycle staging push + Hybrid visual verify rhythm (#047 + #042)

Inherited from Phase 06 → speedrun MEGA-1/2. At speedrun pace this collapses to per-MEGA gate, but the underlying primitive (push → deploy → A/B/C reply → next cycle) remains the discipline. Useful for any future sprint mode.

---

*Retro authored at S2-S3-Speedrun closure (sponsor-demo target).*
*Process observations only — Carry-Forward authoritative source: S2-SNAPSHOT.md.*
