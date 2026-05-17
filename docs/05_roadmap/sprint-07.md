# Sprint 7 — Admin Block Mockups + Specs (Wave 1)

```
Dates:    TBD → TBD (planned 1 week)
Status:   planned
Owner:    Cowork (executor), Operator (validator)
Goal ref: ROADMAP.md §10
Phase:    Phase 4 + Phase 5
```

---

## Goal

Start Admin role coverage. Admin screens are fewer (~15–20 total) but
introduce permission checks and approval flows.

---

## Scope (planning target)

Admin screens, wave 1:

| Order | Screen | Route | Notes |
|---|---|---|---|
| 1 | admin-dashboard | `/admin` | P0 from Sprint 2 — spec only |
| 2 | admin-masters | `/admin/masters` | Masters list, status filter |
| 3 | admin-master-review | `/admin/masters/:id` | Application review |
| 4 | admin-reports | `/admin/reports` | User reports |
| 5 | admin-report-resolve | `/admin/reports/:id` | Resolve or dismiss |
| 6 | admin-withdrawals | `/admin/withdrawals` | List withdrawals |
| 7 | admin-withdrawal-review | `/admin/withdrawals/:id` | Approve/reject. **Backend gap (per VALIDATION-REPORT BG1):** `GET /api/v1/admin/withdrawals/{id}` is not in OpenAPI — pass row via router state from list view; cannot deep-link. See `../06_project-inputs/BACKEND-REQUESTS-2026-05-17.md`. |
| 8 | admin-consistency | `/admin/consistency` | Semaphore results |
| 9 | admin-users | `/admin/users` | User search |
| 10 | admin-user-detail | `/admin/users/:id` | User profile (admin view). **Backend gap (per VALIDATION-REPORT BG2):** `GET /api/v1/admin/users/{id}` is not in OpenAPI — pass row via router state from admin-users list; if target user is a master, fall back to `get_master`. See `../06_project-inputs/BACKEND-REQUESTS-2026-05-17.md`. |

Targets: 9–10 new mockups + 10 specs.

---

## Task checklist

### T7.0 — Pre-flight: Admin shell verification

- [ ] Confirm `AdminShell` with 3-tab bottom bar is in styleguide
      (Tier 3 component per §6.6)
- [ ] If missing or showing 4 tabs: fix in DS, update styleguide,
      re-validate per §10.3

### T7.1 — Mockup batch (Phase 4)

Owner: Cowork. Per screen, same checklist as Sprint 3 T3.1, with
admin-specific shell:

- [ ] HTML at `03_mockups/admin/{screen-name}.html`
- [ ] AdminShell with 3-tab bottom bar
- [ ] §7.6 sample data — admin scenarios (pending masters,
      flagged reports, withdrawal queue)
- [ ] State triad, toolbar, Navigation Map, toast feedback
- [ ] livemockup-studio check: 0 BLOCKER, ≤2 MAJOR
- [ ] `03_mockups/INDEX.md` updated

### T7.2 — Operator review for mockups (§10.4)

Same as Sprint 3 T3.2.

### T7.3 — Spec batch (Phase 5)

Owner: Cowork. Per spec, same checklist as Sprint 3 T3.3. Admin-specific:

- [ ] Section 3 Route & Access — `user.role === 'admin'` guard
      explicitly stated (never `viewMode`); see I3
- [ ] Section 6 Action Contract — every mutation declared as admin-only;
      Section 11 captures `forbidden` (403) handling
- [ ] Section 12 Acceptance Criteria — explicit test for "non-admin user
      cannot reach this screen / cannot call this mutation"
- [ ] master-review / withdrawal-review specs reference the master-side
      counterpart from Sprint 6 via `depends-on`

### T7.4 — Operator review for specs (§10.5)

Same as Sprint 3 T3.4 plus:

- [ ] Permission test explicit in §12 (admin-only enforcement)
- [ ] `forbidden` error code captured in §11

### T7.5 — INDEX.md updates (§12.2)

- [ ] `03_mockups/INDEX.md` reflects admin-block additions
- [ ] `01_deliverable/screens/INDEX.md` reflects new SCR-NNN entries

---

## Sprint 7 Gate

Ref: ROADMAP.md §10.3.

- [ ] 10 admin mockups approved
- [ ] 10 admin specs approved
- [ ] Permission patterns explicitly tested in §12 of every spec
- [ ] AdminShell 3-tab confirmed in styleguide
- [ ] Sprint file closure ritual per ROADMAP §15.2

---

## Risks

| ID | Risk | Mitigation |
|---|---|---|
| 7.A | Admin screens reveal missing API endpoints (admin-specific actions like consistency-fix, master-approve-with-comment). | Spec captures expected operationId + shape; operator coordinates with backend. Spec stays `draft` until contract lands. |
| 7.B | Admin role has different shell (3 tabs vs 4). Mockups must not accidentally use UserShell layout. | Pre-flight T7.0 catches; per-mockup T7.2 review verifies. |
| 7.C | Permission checks are deep — every admin spec needs explicit role guard text in §12. | T7.3 checklist explicitly calls out the §12 admin-only assertion. |

---

## Daily log

- 2026-MM-DD: …

---

## Closure

- Mockup gates passed: ☐ N of 10
- Spec gates passed: ☐ M of 10
- Deferred to Sprint 8 / Sprint 9: ☐
- Methodology amendments proposed: ☐
- Token master changed during sprint? ☐ yes → incremental sync
- Velocity recorded: ☐ ____
- Operator signoff (date): ☐

---

## References

- Roadmap: `ROADMAP.md` §10
- Methodology: §6.6 (Tier 3 layout — AdminShell), §7, §8, §10.4–10.5, §2.5 I3, §8.5 (`depends-on`), §9.5–9.6
