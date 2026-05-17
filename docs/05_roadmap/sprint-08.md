# Sprint 8 — Admin Block + Shared Screens (Wave 2)

```
Dates:    TBD → TBD (planned 1 week)
Status:   planned
Owner:    Cowork (executor), Operator (validator)
Goal ref: ROADMAP.md §11
Phase:    Phase 4 + Phase 5
```

---

## Goal

Finish Admin screens not covered in Sprint 7. Cover shared screens
(auth, error, loading, generic modals).

---

## Scope (planning target)

| Block | Examples | Approx count |
|---|---|---|
| Admin remaining | admin-stats-detail, admin-promos-overview, admin-broadcast, admin-settings | ~5 |
| Shared auth | welcome, login, register, oauth-callback, loading, reset-password | ~6 |
| Shared error | 404, 500, network-error, session-expired, role-mismatch | ~5 |
| Shared modal | confirm-destructive, generic-modal-template | ~2 |

Total target: ~15–18 mockups + specs.

Operator finalizes the exact list at sprint start.

---

## Task checklist

### T8.1 — Mockup batch (Phase 4)

Owner: Cowork. Per screen:

- [ ] HTML at `03_mockups/{role-or-shared}/{screen-name}.html`
      (`shared/` folder added under `03_mockups/` if not present —
      log in `02_design-system/INDEX.md → Iteration Log`)
- [ ] Skeleton per §7.3
- [ ] For shared auth screens: outside of `UserShell`/`MasterShell`/
      `AdminShell` (no bottom tab bar; full-bleed layout)
- [ ] §7.6 sample data; error screens use realistic error copy
- [ ] State triad where applicable (e.g., loading screen demonstrates
      multiple progress states)
- [ ] Toolbar + Navigation Map + toast feedback
- [ ] livemockup-studio check: 0 BLOCKER, ≤2 MAJOR
- [ ] `03_mockups/INDEX.md` updated

### T8.2 — Operator review for mockups (§10.4)

Same as Sprint 3 T3.2.

### T8.3 — Spec batch (Phase 5)

Owner: Cowork. Per spec, same as Sprint 3 T3.3. Special considerations
for shared/auth/error screens:

- [ ] Auth specs (welcome/login/register/oauth-callback/loading):
      explicitly handle Telegram deep-link preservation per I5
- [ ] Error specs (404/500/network-error/session-expired/role-mismatch):
      Section 5 Data Contract = `N/A — error screen, no fetch`;
      Section 11 Error Code Map = `N/A — this IS the error display`
- [ ] Loading spec: Section 7 State Map specifically covers retry
      semantics and timeout behavior
- [ ] role-mismatch spec: explicit pointers to all three role
      dashboards (redirect targets)

### T8.4 — Operator review for specs (§10.5)

Same as Sprint 3 T3.4 plus:

- [ ] Auth flow specs reviewed end-to-end as a flow (welcome → login →
      oauth-callback → loading → user-dashboard) — sequence intact
- [ ] Deep-link preservation captured at every step per I5

### T8.5 — INDEX.md updates (§12.2)

- [ ] `03_mockups/INDEX.md` reflects admin + shared additions
- [ ] If a new `shared/` block created in mockups, INDEX has its own
      sub-section under §12.6 template

---

## Sprint 8 Gate

Ref: ROADMAP.md §11.3.

- [ ] All approved admin and shared screens have mockup + spec
- [ ] Total coverage: ~70–80 screens with mockup+spec status `active`
- [ ] `screens/INDEX.md` summary section shows tally
- [ ] Sprint file closure ritual per ROADMAP §15.2

---

## Risks

| ID | Risk | Mitigation |
|---|---|---|
| 8.A | Auth flow with Telegram deep links is harder than expected. | Dedicate extra time in this sprint specifically to the auth flow; if still incomplete by sprint end, defer remaining to Sprint 9. |
| 8.B | Shared screens require a new `03_mockups/shared/` folder that wasn't in §3. | This is OK per §3 spirit; just add the folder, log iteration, update §12.6 template usage in `03_mockups/INDEX.md`. No methodology amendment needed unless folder becomes a permanent fixture (then update methodology §3 in next minor bump). |
| 8.C | Error screens read too thin for full 12-section spec. | Use `N/A — {reason}` markers liberally per §8.6 / §11.4 AP-S-1. Section 12 still has testable criteria (e.g., "404 displays for unknown route X"). |

---

## Daily log

- 2026-MM-DD: …

---

## Closure

- Mockup gates passed: ☐ N of ____
- Spec gates passed: ☐ M of ____
- Total coverage at sprint end: ☐ ____ of ~120 (~XX%)
- Deferred to Sprint 9 / 10: ☐
- Methodology amendments proposed: ☐
- Token master changed during sprint? ☐ yes → incremental sync
- Velocity recorded: ☐ ____
- Operator signoff (date): ☐

---

## References

- Roadmap: `ROADMAP.md` §11
- Methodology: §7, §8, §8.6 (N/A for thin specs), §10.4–10.5, §2.5 I5, §11.2, §11.4 AP-S-1
