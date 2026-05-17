# Sprint 9 — Spec Refinement + Edge Cases

```
Dates:    TBD → TBD (planned 1 week)
Status:   planned
Owner:    Cowork (executor) + Operator (validator) + Claude Code (optional consult)
Goal ref: ROADMAP.md §12
Phase:    Phase 5 (rework) + new Phase 4+5 for remaining screens
```

---

## Goal

Refine specs that earlier sprints flagged for rework. Cover edge-case
screens identified during waves 1–2 but deferred.

---

## Scope

Inputs to this sprint (no fixed scope; assembled at sprint start):

- All specs with rework flags from Sprints 3–8
- All screens identified during waves 1–2 but not yet covered
- Any new screens identified by the operator during the project

Sprint 9 targets bringing coverage from ~70–80 to ~95–110 of ~120 total.

---

## Task checklist

### T9.1 — Refinement triage

Owner: Operator.

- [ ] Walk through `01_deliverable/screens/INDEX.md` end-to-end
- [ ] For each `active` spec, decide if rework needed; flag in Notes column
- [ ] For each carryover from prior sprints (Closure → Deferred), confirm scope
- [ ] Walk through `03_mockups/INDEX.md` — identify any approved mockups
      without specs (gap to close)
- [ ] List any new screens to add (not yet in either INDEX)
- [ ] Produce the Sprint 9 backlog below:

**Refinement backlog (filled at sprint start):**

| Item type | Target | Reason | Owner |
|---|---|---|---|
| (e.g.) SCR-007 update | user-waitlist | Waitlist FSM refined in Sprint 5 — propagate to spec | Cowork |
| (new) | shared-help-faq | Missed in Sprint 8 | Cowork |
| ... | ... | ... | ... |

### T9.2 — Refinement execution

Owner: Cowork.

For each in-place edit (status stays the same SCR-NNN per §8.9):

- [ ] Edit spec content
- [ ] Update Changelog at end of spec with "{date} — {one-line summary}"
- [ ] Bump `last-updated` in front-matter
- [ ] If status change needed: per §8.8 lifecycle, with `superseded-by`
      filled if applicable
- [ ] Update `01_deliverable/screens/INDEX.md`

For superseding (new SCR-NNN replaces old):

- [ ] Mark old spec `status: superseded` with `superseded-by: SCR-{new}`
- [ ] Write new SCR-NNN-{name}.md with full 12-section structure
- [ ] Update INDEX with both rows

### T9.3 — New edge-case mockups + specs

Owner: Cowork. Per new screen, same Sprint 3 T3.1 + T3.3 checklists.

Target additions: bring coverage from ~70–80 to ~95–110 of ~120.

### T9.4 — Methodology amendments (if needed)

Owner: Operator + Chat (Claude in claude.ai).

- [ ] Collect amendments proposed during Sprints 3–8 closures
- [ ] Draft amendments to `VELO-METHODOLOGY.md`
- [ ] Apply per §13.4 with Changelog entry
- [ ] Bump version (minor vs major per §13.1):
      - [ ] Minor (v1.x) — clarifications, new anti-patterns, refined templates
      - [ ] Major (v2.0) — structural change to pipeline, gate criteria, or spec template
- [ ] Notify all consumers (Cowork, Claude Code) of the version bump

### T9.5 — INDEX.md updates (§12.2)

- [ ] All edited specs reflected in `01_deliverable/screens/INDEX.md`
- [ ] All new mockups reflected in `03_mockups/INDEX.md`
- [ ] `02_design-system/INDEX.md → Iteration Log` updated if DS changed
- [ ] Top-level `docs/INDEX.md` — Status Summary updated (this is a
      major milestone — see §12.2 hybrid strategy)

---

## Sprint 9 Gate

Ref: ROADMAP.md §12.3.

- [ ] All flagged specs reworked and re-approved
- [ ] Edge-case coverage closes remaining gaps (~95–110 of ~120)
- [ ] Methodology version bumped if amendments applied
- [ ] Sprint file closure ritual per ROADMAP §15.2

---

## Risks

| ID | Risk | Mitigation |
|---|---|---|
| 9.A | Refinement triage uncovers more rework than capacity allows. | Prioritize ruthlessly: P0/P1 first; defer P2/P3 to Sprint 11 reserve. |
| 9.B | Methodology amendments conflict between Cowork practice and operator intent. | Vector-debates skill or it-debates skill for the contentious points. Record decision in methodology Changelog. |
| 9.C | Operator-only triage (T9.1) takes more than half the sprint. | Cap T9.1 at 1.5 days; remaining time goes to T9.2/T9.3 execution by Cowork. |

---

## Daily log

- 2026-MM-DD: …

---

## Closure

- Refinement items completed: ☐ N of ____
- New screens added: ☐ M
- Methodology version after sprint: ☐ v_____
- Coverage at sprint end: ☐ ____ of ~120 (~XX%)
- Deferred to Sprint 10 / Sprint 11: ☐
- Token master changed during sprint? ☐ yes → incremental sync
- Operator signoff (date): ☐

---

## References

- Roadmap: `ROADMAP.md` §12
- Methodology: §8.8–8.9 (status lifecycle and in-place edit rules), §13 (versioning), §12.2 (INDEX update strategy)
