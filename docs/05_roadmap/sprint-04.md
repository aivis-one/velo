# Sprint 4 — User Block Completion (Wave 2)

```
Dates:    TBD → TBD (planned 1 week)
Status:   planned
Owner:    Cowork (executor), Operator (validator)
Goal ref: ROADMAP.md §7
Phase:    Phase 4 + Phase 5
```

---

## Goal

Finish remaining User-role screens not covered in Sprint 3. Close out
the user block.

---

## Scope (planning target — finalize at sprint start)

Remaining user screens. Typical count 10–15 depending on velocity. The
indicative list from ROADMAP §7.1:

| # | Screen | Route | Notes |
|---|---|---|---|
| 1 | user-onboarding step 2..N | `/welcome/...` | Multi-step onboarding |
| 2 | user-login | `/login` | Telegram WebApp auth landing |
| 3 | user-register | `/register` | GDPR-aware registration |
| 4 | user-oauth-callback | `/oauth-callback` | Returning from provider |
| 5 | user-notification-center | `/notifications` | Inbox/system notifications |
| 6 | user-settings | `/settings` | Privacy, notifications |
| 7 | user-account-delete-confirm | `/settings/delete-account` | Destructive flow |
| 8 | user-history | `/history` | Booking history archive |
| 9 | user-feedback-submit | `/practice/:id/feedback` | Post-practice feedback |
| 10 | user-promo-redeem | `/promo` | Promo code entry |
| 11 | user-reports-list | `/reports` | List of user's own reports (status: pending/resolved/dismissed). Operations: `get_my_reports`, `update_report` (edit own report). Added per VALIDATION-REPORT 2026-05-17 D2 to close gap on `get_my_reports` not being mapped to any screen. |
| 12 | user-error-404 | (catch-all) | Generic 404 (may move to shared in Sprint 8) |

Operator finalizes the exact list at sprint start (record below):

- 1. _________
- 2. _________
- ...

Targets: ~10–15 mockups + ~10–15 specs.

---

## Task checklist

Identical structure to Sprint 3. Per task, follow the methodology
references in Sprint 3 — they apply unchanged.

### T4.1 — Mockup batch (Phase 4)

Owner: Cowork. Per screen, same checklist as Sprint 3 T3.1:

- [ ] HTML at `03_mockups/user/{screen-name}.html`
- [ ] Skeleton per §7.3, 402×874 mobile, components from styleguide, §7.6 sample data
- [ ] State triad, toolbar + Navigation Map, toast feedback, Russian only
- [ ] livemockup-studio check: 0 BLOCKER, ≤2 MAJOR
- [ ] `03_mockups/INDEX.md` updated

(Repeat for each screen in scope above.)

### T4.2 — Operator review pass for mockups (§10.4)

Owner: Operator. Per screen, same criteria as Sprint 3 T3.2.

### T4.3 — Spec batch (Phase 5)

Owner: Cowork. Per spec, same checklist as Sprint 3 T3.3. SCR numbering
continues from where Sprint 3 ended.

### T4.4 — Operator review pass for specs (§10.5)

Owner: Operator. Per spec, same criteria as Sprint 3 T3.4.

### T4.5 — INDEX.md updates (§12.2)

Owner: Cowork.

- [ ] `03_mockups/INDEX.md` reflects all user-block additions in this sprint
- [ ] `01_deliverable/screens/INDEX.md` reflects all new SCR-NNN specs
- [ ] Summary rows updated

---

## Sprint 4 Gate

Ref: ROADMAP.md §7.3.

- [ ] All approved user screens have mockup + spec
- [ ] User block in `screens/INDEX.md` shows ~20–25 SCR entries active
- [ ] No user-block screen left in `draft` without operator feedback
- [ ] Sprint file closure ritual per ROADMAP §15.2

---

## Risks

| ID | Risk | Mitigation |
|---|---|---|
| 4.A | OAuth + Telegram deep-link complexity reveals gaps in VELO Invariant I5 (Telegram deep links survive auth). | Refine I5 in methodology, propagate to onboarding specs. Block specific specs until decided. |
| 4.B | Sprint 3 specs need rework based on Sprint 4 learnings. | §8.9 in-place editing; or defer batch rework to Sprint 9 refinement sprint. |
| 4.C | Onboarding step 2..N is fundamentally a flow not a screen — splitting into per-step SCRs feels wrong. | Decide between (a) one SCR per step with `flow: user-onboarding` front-matter, or (b) one SCR for the entire flow with explicit step sections. Decision at sprint start; document in INDEX. |

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
- Velocity calibration note (per ROADMAP §15.3): ☐ on-track / below 10 / above 15
- Operator signoff (date): ☐

---

## References

- Roadmap: `ROADMAP.md` §7
- Methodology: §7, §8, §10.4–10.5, §11.2, §11.4, §9.5, §9.6, §2.5 I5
