# Sprint 3 — User Block Mockups + Specs (Wave 1)

```
Dates:    TBD → TBD (planned 1 week)
Status:   planned
Owner:    Cowork (executor), Operator (validator)
Goal ref: ROADMAP.md §6
Phase:    Phase 4 (Mockup Assembly) + Phase 5 (Spec Writing)
```

---

## Goal

Start per-screen mockup+spec production for the User role. First wave
covers ~10–12 user screens. First sprint where the full pipeline runs at
scale.

---

## Scope (planning target — confirm at sprint start)

User screens, wave 1 (highest priority first):

| Order | Screen | Route | Notes |
|---|---|---|---|
| 1 | user-dashboard | `/` | P0 from Sprint 2 — spec only this sprint |
| 2 | user-practice-detail | `/practice/:id` | Core booking flow start. **Action set** includes `create_report` ("Пожаловаться") as a one-off action — declared in this SCR's Section 6 Action Contract. Operation: `create_report`. |
| 3 | user-bookings | `/bookings` | All booking statuses |
| 4 | user-calendar | `/calendar` | Calendar grid + slots |
| 5 | user-profile | `/profile` | Avatar, balance, settings |
| 6 | user-waitlist | `/waitlist` | WaitlistCard list — Waitlist FSM (methodology §8.7, I6 with **canonical state name `notified`**, not `offered`). |
| 7 | user-diary | `/diary` | DiaryEntryCard list, mood filter |
| 8 | user-topup | `/topup` | Balance topup flow |
| 9 | user-practice-buy-preview | step in `/practice/:id` flow | Preview → purchase |
| 10 | user-onboarding-welcome | `/welcome` | Onboarding step 1 |

Targets: 9–10 new mockups + 10–12 specs (the +1/+2 includes the
user-dashboard spec for the Sprint 2 P0 mockup).

---

## Task checklist

### T3.1 — Mockup batch (Phase 4) for screens 2–10

Ref: VELO-METHODOLOGY.md §7 + Prompt §9.5, repeated per screen.
Owner: Cowork.

Per-screen checklist (repeat for every screen above except #1):

- [ ] HTML at `03_mockups/user/{screen-name}.html`
- [ ] Skeleton per §7.3
- [ ] 402×874 mobile default
- [ ] VELO components used (no inline rewrites)
- [ ] Realistic VELO sample data (§7.6)
- [ ] State triad (loading/empty/populated/error)
- [ ] Toolbar + Navigation Map (📍)
- [ ] Toast feedback for interactions (§7.5)
- [ ] Russian text only
- [ ] livemockup-studio check: 0 BLOCKER, ≤2 MAJOR
- [ ] `03_mockups/INDEX.md` updated (status `🔄 awaiting review`)

### T3.2 — Operator review pass for mockups

Ref: VELO-METHODOLOGY.md §10.4.
Owner: Operator. Per screen:

- [ ] Open at 402×874 without horizontal scroll
- [ ] Side-by-side with Figma PNG — visual match within AA deltas
- [ ] Toggle through state triad — all states render
- [ ] Click every interactive element — visual feedback present
- [ ] Navigation Map counts correct
- [ ] Russian copy throughout
- [ ] Approve (`✅` in INDEX.md) or send revision

### T3.3 — Spec batch (Phase 5) for approved mockups

Ref: VELO-METHODOLOGY.md §8 + Prompt §9.6, per spec.
Owner: Cowork. Numbering starts SCR-001 (user-dashboard) and increments.

Per-spec checklist (repeat per spec, ~10–12 specs total):

- [ ] File at `01_deliverable/screens/SCR-{NNN}-{name}.md`
- [ ] YAML front-matter complete (§8.5): id, name, status=draft,
      last-updated, mockup, mockup-approved-on, figma-screenshot, roles,
      route, priority
- [ ] All 12 sections present (§8.3):
      - [ ] §1 Context (≤3 sentences)
      - [ ] §2 Visual Reference (paths only)
      - [ ] §3 Route & Access (URL, role guard, auth guard, redirects)
      - [ ] §4 Layout Structure (top-to-bottom block list)
      - [ ] §5 Data Contract (GET endpoints, operationIds)
      - [ ] §6 Action Contract (mutations per interaction)
      - [ ] §7 State Map (loading/empty/error/populated/...)
      - [ ] §8 Store Dependencies (read/write/watch)
      - [ ] §9 i18n Keys (new + reused, nested JSON)
      - [ ] §10 Business Rules (cite I1–I7 by ID)
      - [ ] §11 Error Code Map (VeloError codes)
      - [ ] §12 Acceptance Criteria (testable, 8–15 items)
- [ ] Sections marked `N/A — {reason}` where inapplicable (no skipped sections)
- [ ] Every `operationId` references an entry in `api-openapi.json`
- [ ] Every VELO Invariant cited as I1, I2, etc. (per §2.5)
- [ ] Every ARCHITECTURE.md citation verified against
      `06_project-inputs/ARCHITECTURE.md`
- [ ] i18n keys nested under screen-specific namespace
- [ ] Changelog row added: "{date} — Initial spec"
- [ ] `01_deliverable/screens/INDEX.md` updated (status `🔄`)

### T3.4 — Operator review pass for specs

Ref: VELO-METHODOLOGY.md §10.5.
Owner: Operator. Per spec:

- [ ] Read end-to-end; structure clear
- [ ] Spot-check 1–2 operationIds against `api-openapi.json`
- [ ] Spot-check 1–2 ARCHITECTURE.md citations resolve to real sections
- [ ] Acceptance criteria are Y/N testable
- [ ] Mockup field points to an approved mockup (T3.2 ✅)
- [ ] Approve: change status `draft` → `active`, update INDEX.md `🔄 → ✅`

### T3.5 — INDEX.md updates

Ref: VELO-METHODOLOGY.md §12.2.
Owner: Cowork (immediately after each artifact).

- [ ] `03_mockups/INDEX.md` reflects every mockup added in T3.1 with correct status
- [ ] `01_deliverable/screens/INDEX.md` reflects every spec from T3.3 with correct status
- [ ] Summary row counts at bottom of each INDEX kept current

---

## Sprint 3 Gate

Ref: ROADMAP.md §6.3.

- [ ] 9–10 new user mockups approved (MOCKUP GATE per screen)
- [ ] 10–12 user specs approved (SPEC GATE per screen)
- [ ] `01_deliverable/screens/INDEX.md` shows SCR-001 through ~SCR-010 active
- [ ] `03_mockups/INDEX.md` reflects user-block progress
- [ ] Sprint file closure ritual per ROADMAP §15.2

---

## Risks

| ID | Risk | Mitigation |
|---|---|---|
| 3.A | First specs reveal that the 12-section template is overkill or underkill for actual VELO screens. | At sprint end, operator notes findings; if methodology needs adjustment, apply amendments per §13. Carry-over to Sprint 9 if rework needed. |
| 3.B | Waitlist FSM proves more complex than declared in §8.7. | Refine the FSM in methodology before writing waitlist-related specs (T3.3 for user-waitlist). |
| 3.C | API contract is missing endpoints required by user screens. | Spec authoring exposes the gap; operator coordinates with backend. Block specific specs until contract is in place; carry over. |
| 3.D | New Tier 2 components emerge that weren't in Sprint 2 styleguide (e.g., balance-topup widget). | Build component in DS first; update styleguide; re-validate per §10.3 incrementally; resume mockup work. |

---

## Daily log

- 2026-MM-DD: …

---

## Closure

- Mockup gates passed: ☐ N of 9–10
- Spec gates passed: ☐ M of 10–12
- Deferred to Sprint 4 / Sprint 9: ☐
- Methodology amendments proposed: ☐
- Token master changed during sprint? ☐ yes → incremental sync per ROADMAP §15.2 step 4
- Velocity recorded (screens completed): ☐ ____
- Operator signoff (date): ☐

---

## References

- Roadmap: `ROADMAP.md` §6
- Methodology: §7 (mockup layer), §8 (spec layer), §10.4–10.5 (gates), §11.2 + §11.4 (anti-patterns), §9.5–9.6 (prompts), §2.5 (I1–I7 invariants), §8.7 (Waitlist FSM)
- Inputs: `../06_project-inputs/api-openapi.json` (operationIds), `../06_project-inputs/ARCHITECTURE.md`
