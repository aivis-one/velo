# Sprint 6 — Master Block Completion (Wave 2)

```
Dates:    TBD → TBD (planned 1 week)
Status:   planned
Owner:    Cowork (executor), Operator (validator)
Goal ref: ROADMAP.md §9
Phase:    Phase 4 + Phase 5
```

---

## Goal

Finish remaining Master-role screens not covered in Sprint 5.

---

## Scope (planning target)

Remaining master screens, typical 10–15. Indicative list from ROADMAP §9.1:

| # | Screen | Notes |
|---|---|---|
| 1 | master-practice-detail-public | Preview "as viewer" |
| 2 | master-promos-list | Owner promo overview |
| 3 | master-promo-create | Create promo |
| 4 | master-withdrawal-create | Create withdrawal request |
| 5 | master-withdrawal-history | List of withdrawals |
| 6 | master-bookings-overview | All bookings across master's practices |
| 7 | master-messages | Inbox (if exists in API) |
| 8 | master-settings | Privacy, notifications |
| 9 | master-help | Static help / FAQ |
| 10 | master-onboarding | Post-approval first-time tour |

Operator finalizes at sprint start.

Targets: ~10–15 mockups + ~10–15 specs.

---

## Task checklist

Identical structure to Sprint 3 / Sprint 5.

### T6.1 — Mockup batch (Phase 4)

Owner: Cowork. Per screen:

- [ ] HTML at `03_mockups/master/{screen-name}.html`
- [ ] Skeleton, 402×874, components from styleguide
- [ ] §7.6 sample data
- [ ] State triad, toolbar, Navigation Map, toast feedback
- [ ] livemockup-studio check: 0 BLOCKER, ≤2 MAJOR
- [ ] `03_mockups/INDEX.md` updated

### T6.2 — Operator review for mockups (§10.4)

Same as Sprint 3 T3.2.

### T6.3 — Spec batch (Phase 5)

Owner: Cowork. Per spec, same as Sprint 3 T3.3. Special:

- [ ] master-withdrawal-create + master-withdrawal-history: use
      `depends-on` front-matter to chain admin-side specs that will
      appear in Sprint 7 (`SCR-NNN-admin-withdrawal-review`)
- [ ] Promo specs: reference promo lifecycle if it has FSM-like behavior
      (add to §8.7 of methodology if needed)

### T6.4 — Operator review for specs (§10.5)

Same as Sprint 3 T3.4.

### T6.5 — INDEX.md updates (§12.2)

- [ ] `03_mockups/INDEX.md` reflects master-block completion
- [ ] `01_deliverable/screens/INDEX.md` reflects new SCR-NNN entries
- [ ] Master block in INDEX shows ~20–25 active SCRs total

---

## Sprint 6 Gate

Ref: ROADMAP.md §9.3.

- [ ] All approved master screens have mockup + spec
- [ ] Master block in `screens/INDEX.md` shows ~20–25 active SCR entries
- [ ] Sprint file closure ritual per ROADMAP §15.2

---

## Risks

| ID | Risk | Mitigation |
|---|---|---|
| 6.A | Withdrawal flow is multi-screen (master creates → admin approves). Need cross-spec references. | Use `depends-on` front-matter per §8.5 to declare dependency on Sprint 7 admin specs. The master-side spec can be `active` even while the admin-side is still `draft` — `depends-on` is a hint, not a blocker. |
| 6.B | "Messages" screen may not have backend support; product undecided. | If no backend endpoints exist, defer to Sprint 9 reserve. Don't write a spec without contract. |

---

## Daily log

- 2026-MM-DD: …

---

## Closure

- Mockup gates passed: ☐ N of ____
- Spec gates passed: ☐ M of ____
- Deferred to Sprint 9: ☐
- Methodology amendments proposed: ☐
- Token master changed during sprint? ☐ yes → incremental sync
- Velocity recorded: ☐ ____
- Operator signoff (date): ☐

---

## References

- Roadmap: `ROADMAP.md` §9
- Methodology: §7, §8, §8.5 (depends-on), §8.7 (FSMs), §10.4–10.5, §9.5–9.6
