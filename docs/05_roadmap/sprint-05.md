# Sprint 5 — Master Block Mockups + Specs (Wave 1)

```
Dates:    TBD → TBD (planned 1 week)
Status:   planned
Owner:    Cowork (executor), Operator (validator)
Goal ref: ROADMAP.md §8
Phase:    Phase 4 + Phase 5
```

---

## Goal

Start Master role coverage. The Master role introduces new domain
components (PromoRow, WithdrawalRow, InsightsChart) and new business
rules (balance ≥ threshold for withdrawal, master application flow).

---

## Scope (planning target)

Master screens, wave 1:

| Order | Screen | Route | Notes |
|---|---|---|---|
| 1 | master-dashboard | `/master` | P0 from Sprint 2 — spec only |
| 2 | master-practices | `/master/practices` | PracticeCard owner view |
| 3 | master-practice-create | `/master/practices/new` | 3-step form |
| 4 | master-practice-edit | `/master/practices/:id` | Edit existing |
| 5 | master-analytics | `/master/analytics` | InsightsChart aggregate. **Known limit (per VALIDATION-REPORT BG3):** aggregate analytics across all master's practices is **client-side only** — loop `get_practice_insights` per practice. No backend aggregate endpoint exists. Spec must document this constraint and pagination strategy (e.g., aggregate only N most recent practices). |
| 6 | master-finance | `/master/finance` | Balance + withdrawals + promos |
| 7 | master-profile | `/master/profile` | MasterStatusBadge |
| 8 | master-apply | `/master/apply` | 3-step apply flow |
| 9 | master-pending | `/master/pending` | Awaiting verification |
| 10 | master-practice-attendance | `/master/practices/:id/attendance` | Check-in users |

Targets: 9–10 new mockups + 10–12 specs (the +1/+2 includes
master-dashboard spec for Sprint 2 P0 mockup).

---

## Task checklist

Identical structure to Sprint 3. Adjusted for master-block specifics.

### T5.0 — Pre-flight: new domain components

Owner: Cowork + Operator at sprint start.

- [ ] Confirm presence in styleguide of: PromoRow, WithdrawalRow, InsightsChart
- [ ] If any missing: build component, update styleguide, re-validate
      partial STYLEGUIDE GATE (§10.3) for the new components only
- [ ] Log iteration in `02_design-system/INDEX.md → Iteration Log`

### T5.1 — Mockup batch (Phase 4) for screens 2–10

Owner: Cowork. Per screen, same checklist as Sprint 3 T3.1:

- [ ] HTML at `03_mockups/master/{screen-name}.html`
- [ ] Skeleton, 402×874, components from styleguide
- [ ] §7.6 sample data (Russian, domain-correct)
- [ ] State triad, toolbar, Navigation Map, toast feedback
- [ ] livemockup-studio check: 0 BLOCKER, ≤2 MAJOR
- [ ] `03_mockups/INDEX.md` updated

### T5.2 — Operator review for mockups (§10.4)

Owner: Operator. Same criteria as Sprint 3 T3.2.

### T5.3 — Spec batch (Phase 5)

Owner: Cowork. Per spec, same checklist as Sprint 3 T3.3. SCR numbering
continues. Special considerations for master role:

- [ ] Section 10 Business Rules — cite I3 (role vs viewMode) explicitly
      for any mutation-bearing master spec; security check uses `user.role`
- [ ] Section 11 Error Code Map — cover `forbidden` (403) for
      master-only mutations
- [ ] master-apply spec: decide flow handling (one SCR with
      `flow: master-apply` or three SCRs with `depends-on` chain) —
      record decision in spec front-matter
- [ ] master-finance spec: reference Withdrawal lifecycle (§8.7) if added

### T5.4 — Operator review for specs (§10.5)

Owner: Operator. Same criteria as Sprint 3 T3.4 plus:

- [ ] Every withdrawal-touching spec correctly uses `user.role === 'master'`
- [ ] Insights/Analytics specs reference correct backend operationIds (likely under `/api/v1/masters/...`)

### T5.5 — INDEX.md updates (§12.2)

- [ ] `03_mockups/INDEX.md` reflects master-block additions
- [ ] `01_deliverable/screens/INDEX.md` reflects new SCR-NNN entries
- [ ] Summary rows current

---

## Sprint 5 Gate

Ref: ROADMAP.md §8.3.

- [ ] 9–10 master mockups approved
- [ ] 10–12 master specs approved
- [ ] New domain components (PromoRow, WithdrawalRow, InsightsChart) in styleguide
- [ ] Sprint file closure ritual per ROADMAP §15.2

---

## Risks

| ID | Risk | Mitigation |
|---|---|---|
| 5.A | Withdrawal flow exposes role-vs-viewMode question (I3). Spec must reference real `user.role === 'master'`. | Covered by I3; reviewers verify explicitly at T5.4. |
| 5.B | master-apply 3-step flow doesn't fit in one SCR-NNN. | Split into SCR-NNN-master-apply-step-1, -2, -3 OR one SCR with `flow: master-apply` front-matter. Decision at sprint start, recorded in T5.3. |
| 5.C | Analytics charting requires data shapes not in api-openapi.json. | Spec captures expected shape; operator coordinates with backend. Spec can stay `draft` until contract lands. |

---

## Daily log

- 2026-MM-DD: …

---

## Closure

- Mockup gates passed: ☐ N of 9–10
- Spec gates passed: ☐ M of 10–12
- Deferred to Sprint 6 / Sprint 9: ☐
- New DS components added during sprint: ☐ ____
- Methodology amendments proposed: ☐
- Token master changed during sprint? ☐ yes → incremental sync
- Velocity recorded: ☐ ____
- Operator signoff (date): ☐

---

## References

- Roadmap: `ROADMAP.md` §8
- Methodology: §6.6 (Tier 2 components), §7, §8, §10.4–10.5, §2.5 I3, §8.7 (FSMs), §9.5–9.6
