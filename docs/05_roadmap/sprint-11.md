# Sprint 11 — Reserve / Polish / Iteration

```
Dates:    TBD → TBD (open-ended)
Status:   planned (stub — finalized at start of each reserve sprint)
Owner:    Operator drives priorities
Goal ref: ROADMAP.md §14
Phase:    flexible — Phase 4, 5, 6, or methodology evolution
```

---

## Goal

Absorb slippage from earlier sprints. Respond to implementation-stage
feedback from Claude Code. Cover deferred items (dark theme,
accessibility audit, performance audit) when stakeholders prioritize.

---

## How this sprint is planned

At the start of each reserve sprint, the operator surveys:

- [ ] `01_deliverable/screens/INDEX.md` — any specs not `active`?
- [ ] Frontend implementation status — any blockers reported by CC?
- [ ] `02_design-system/INDEX.md` — any open TODOs?
- [ ] Stakeholder feedback — any new requirements?
- [ ] Methodology open amendments — any v1.x → v2.0 candidates?

The sprint scope is then finalized: top 5–7 priorities, recorded below.

**Sprint 11 scope (fill at start of sprint):**

| Priority | Item | Owner | Methodology phase |
|---|---|---|---|
| P0 | __________ | __________ | __________ |
| P1 | __________ | __________ | __________ |
| P2 | __________ | __________ | __________ |
| ... | __________ | __________ | __________ |

---

## Typical reserve activities (catalog)

Examples of work that lives in reserve sprints (per ROADMAP §14.1):

### Implementation feedback

- [ ] Spec ambiguity report from Claude Code triaged
- [ ] Affected specs edited in place per §8.9 (or superseded per §8.8)
- [ ] Re-validated against §10.5 SPEC GATE
- [ ] Frontend re-synced if tokens changed

### Late-arriving screens (product additions)

- [ ] New screens added to mockups (`03_mockups/{role}/...`)
- [ ] New SCR-NNN specs written per §8 + §9.6
- [ ] INDEX.md catalogs updated

### Dark theme implementation

Ref: VELO-METHODOLOGY.md §2.5 I7 (currently deferred).

- [ ] Add dark-mode block to Layer 2 in `02_design-system/tokens/variables.css`
- [ ] Update styleguide to demonstrate dark mode toggle
- [ ] Spot-check critical mockups for dark-mode rendering
- [ ] If breaking change to tokens, log in `02_design-system/INDEX.md → Iteration Log`
- [ ] Frontend sync per ROADMAP §15.2 step 4

### Accessibility audit pass

Currently out of scope per VELO-METHODOLOGY.md §14. If brought in:

- [ ] Audit method chosen (WCAG 2.1 AA target?)
- [ ] Color contrast verification across token semantic pairs
- [ ] Focus-ring visibility on every interactive component
- [ ] Screen-reader testing on representative flows
- [ ] Document findings; raise tokens or component changes as separate tasks

### Performance audit pass

Currently out of scope per VELO-METHODOLOGY.md §14. If brought in:

- [ ] Budget targets agreed (bundle, FCP, LCP)
- [ ] Measurement method agreed
- [ ] Document findings; raise as separate tasks

### Methodology v2.0

If accumulated learnings warrant major version bump (§13.1):

- [ ] Draft v2.0 of `VELO-METHODOLOGY.md`
- [ ] Operator + Chat (Claude) co-author
- [ ] Cowork validates executability (per RP7)
- [ ] Apply with full Changelog entry
- [ ] Propagate sprint-NN.md template updates as needed

---

## Sprint 11 Gate

Per the chosen scope. No fixed criteria — gate is "all P0/P1 scope items
delivered to operator satisfaction." Lower priorities may carry to
Sprint 12+ if velocity is constrained.

- [ ] All P0 scope items complete
- [ ] All P1 scope items complete (or explicitly deferred with reason)
- [ ] Sprint file closure ritual per ROADMAP §15.2

---

## Daily log

- 2026-MM-DD: …

---

## Closure

- P0 items completed: ☐ N of ____
- P1 items completed: ☐ M of ____
- Methodology version after sprint: ☐ v_____
- Final coverage: ☐ ____ of ~120 (~XX%)
- Next reserve sprint planned (sprint-12.md)? ☐ yes / ☐ no (project closed)
- Operator signoff (date): ☐

---

## Notes for subsequent reserve sprints

Copy this file as `sprint-12.md`, `sprint-13.md`, etc., when more
reserve sprints are needed. Methodology stays unchanged; roadmap may
gain a §14.x section describing the new sprint's specific focus if it's
substantively different from generic reserve work.

---

## References

- Roadmap: `ROADMAP.md` §14
- Methodology: §2.5 I7 (dark theme), §13 (versioning), §14 (out-of-scope topics that can return here), §8.8–8.9 (spec lifecycle for refinement)
