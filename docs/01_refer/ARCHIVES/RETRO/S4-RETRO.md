# RETRO — Sprint 4: Master + Admin Roles Refresh
> SPEC v3.2-velo
> Date: 2026-05-04
> Status: CLOSED

> Process observations only. Carry-forward items live in S4-SNAPSHOT.md (SSOT per 04_Sprint-Closer Step 11).

---

## What Worked

1. **Speedrun mode (#052) through both phases without quality regression** — lint preserved at 0 across 2 MEGA prompts + 1 fix commit. The throughput trade encoded in #049 continues to hold for refresh-character work where logic is portable from analogous user views.

2. **Combined Scout + 8-section MEGA-4 structure** — single prompt covered 8 cycles (C66-C73) cleanly. Same shape as MEGA-1/2/3 of S2/S3/S4-P14; pattern is now reproducible across sprints.

3. **Anti-scope discipline through P15** — router/api/stores/components/ui untouched; verified empty diffs at every gate. Operator's mental model of "this section is locked" survived 4 MEGA prompts now.

4. **ConfirmModal precedent (P14 §C60) translated cleanly to P15 §C70 + §C72 + post-verify RoleSwitcher** — shared-component reuse pattern proven 3× in S4. Confirms the BACKLOG #48 closure path framing (Teleport-inline > VModal adoption) was correct.

5. **Path Y MEDIUM fidelity decision (#047) held** — no premature pixel-polish through 17-view refresh, post-S4 polish coherent with operator's updated DS scope (BACKLOG #106).

---

## What Didn't

1. **Bootstrap prompt assumption that uiMode is 3-value was wrong** (binary `'default' | 'user'`). Surfaced only at scout stage; cost minor design adjustment in role-switch fix, no rework. Indicates assumption-validation belongs at scout, not at OPEN — but this works because Pre-Exec catches it before code lands.

2. **AdminMasterReviewView shipped degraded v1 due to backend type GAP** — known going in; BACKLOG #104 tracks; not a process issue. Worth flagging as a class of risk: views consuming admin-only types may not have full-fidelity backing until backend partner extends.

3. **Verify gate exposed UserProfileView role-switch absence as BREAK** — was technically scope-correct (P15 was admin views; user views were P11 era) but visible as user-facing bug. Reveals weakness in cross-role test coverage during phase planning. The mid-flow fix worked, but the absence shouldn't have reached verify in the first place. Process improvement candidate: phase planning checklist should include "cross-role state-toggle flows touched by this phase".

---

## Protocol Pain Points

1. **Audit defer routing has ceremony cost.** Sprint-Closer Step 1+ scout currently has to acknowledge defer per BACKLOG #100 with no actual ProbeKit work. Could collapse: if BACKLOG entry exists with active defer rationale, Step 1+ output = 1 line "DEFERRED per #NNN" without scouting ProbeKit state. Consider for next protocol revision.

2. **Plan vs Reality population timing not codified.** S4-SPRINT.md Plan vs Reality was filled at P15 close (post-verify), with operator findings still warm. This is the right time but isn't prescribed in Phase-Builder CLOSE — currently happens by virtue of comprehensive Last Session updates. Codifying would help future sprints; for now, the precedent stands.

3. **Sprint Metrics column DEFERRED placeholders ripple from S2 onwards.** With audit deferred at S2-S3-Speedrun close (#049) and again at S4 (#052), the cumulative Sprint Metrics table now has 3 DEFERRED rows. Once BACKLOG #100 reactivates and audits backfill, the table needs explicit retroactive update. Worth a Sprint-Closer note when #100 closes.

---

## Workflow Improvements Discovered

1. **Mid-flow fix commit pattern** — role-switch BREAK fix landed as standalone `fix:` commit (8eede07) between P15 phase commit and closure. Clean: targeted scope (~75 LOC), no anti-scope violations, paramiko deploy succeeded without firing BACKLOG #96 transient (delta below threshold). Pattern reusable for any verify-surfaced BREAK small enough to fix without re-opening the phase.

2. **#106 MAJOR scope ceiling captured at sprint close, not at next-sprint OPEN.** Operator's S5 framing ("полная замена DS — это major-spec событие") needed an explicit Sprint-Closer pre-signal: S5 ≠ polish, S5 = DS stack swap. Codified in S4-SPRINT.md Note + BACKLOG #106. Future sprints should similarly capture operator scope-shifts at close, not at next-sprint OPEN, so that Sprint-Builder loads the correct ceiling from day one.

3. **#96 hypothesis refinement via deploy-by-deploy data points** — sample N=6 now (4 fired, 2 didn't), with counter-examples isolating the trigger to frontend-code-LOC threshold rather than total-LOC. Continuing the per-deploy log is providing real refinement, not noise. Pattern reusable for any infrastructure-quirk hypothesis tracking: keep the data-points table inline in BACKLOG entry rather than separate doc.

---

*Retrospective created by: 04_Sprint-Closer protocol*
*Immutable — do not edit after creation*
