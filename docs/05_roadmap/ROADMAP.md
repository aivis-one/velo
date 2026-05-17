# VELO — Project Roadmap

> **Operating plan for VELO design-to-handoff work.**
> Built on top of `VELO-METHODOLOGY.md`. The methodology defines **how**
> we work; this roadmap defines **when** each piece of work happens, in
> which sprint, and by whom.
>
> **Audience:** the operator (you), Cowork (Figma + HTML execution),
> Claude Code (frontend implementation, downstream consumer).
>
> **Status:** Draft for operator approval before execution.
>
> **Anchor:** `[VELO-ROADMAP.md | v1.1 | 2026-05-17]`

---

## Table of Contents

1. Roadmap Principles
2. Sprint Cadence and Sizing
3. Sprint 0 — Foundation Cleanup
4. Sprint 1 — Figma Extraction + Token Synthesis
5. Sprint 2 — Styleguide + First Mockups (P0)
6. Sprint 3 — User Block Mockups + Specs (Wave 1)
7. Sprint 4 — User Block Completion (Wave 2)
8. Sprint 5 — Master Block Mockups + Specs (Wave 1)
9. Sprint 6 — Master Block Completion (Wave 2)
10. Sprint 7 — Admin Block Mockups + Specs (Wave 1)
11. Sprint 8 — Admin Block + Shared Screens (Wave 2)
12. Sprint 9 — Spec Refinement + Edge Cases
13. Sprint 10 — Handoff Package + Final Sync
14. Sprint 11+ — Reserve / Polish / Iteration
15. Sprint Tracking and Reporting
16. Risk Register
17. Out of Scope for This Roadmap

---

## 1. Roadmap Principles

**RP1 — One sprint = one week.**
Five working days. Monday to Friday. Friday afternoon is gate-validation
time (operator reviews artifacts produced during the sprint).

**RP2 — Sprint capacity = ~10-15 screens through Phase 4+5.**
This is a planning anchor for sprints that focus on mockup+spec
production. Sprints 1-2 are foundation work (tokens, styleguide) and
don't measure in screens.

**RP3 — Gate validation happens at sprint end.**
Per-screen gates (MOCKUP, SPEC) accumulate during the sprint. Friday
review: operator validates the batch produced. Failed gates push the
artifact into the next sprint's backlog.

**RP4 — Roadmap is revisable.**
At sprint end, the operator may add, remove, or reorder upcoming sprints
based on what was learned. The methodology is stable; the roadmap
adapts.

**RP5 — Roadmap cites methodology, not duplicates it.**
Every task references the methodology section that governs it. The
operator and Cowork read the methodology for **how**; the roadmap tells
them **when** and **what**.

**RP6 — Backend dependency is decoupled.**
This roadmap describes design-and-handoff work. Backend implementation
proceeds in parallel and is tracked separately. Mockup and spec work
references `api-openapi.json` as the contract — when the contract is
stable for a given screen, that screen can proceed regardless of
backend implementation state.

**RP7 — Cowork validates roadmap before execution.**
Before Sprint 0 begins, the operator hands this roadmap to Cowork for a
read-through. Cowork's job is to confirm that each task in each sprint
is understood and executable, or to flag ambiguity. Cowork's feedback is
folded into v1.1 of this roadmap (if needed) before any work starts.
This pre-flight check prevents the operator from launching Sprint 1
only to discover Cowork doesn't know how to interpret §9.2 prompt.

---

## 2. Sprint Cadence and Sizing

| Sprint | Focus | Phase per methodology | Screens (target) |
|---|---|---|---|
| Sprint 0 | Foundation cleanup | — | 0 |
| Sprint 1 | Figma extraction + tokens | Phase 1 + Phase 2 | 0 |
| Sprint 2 | Styleguide + P0 mockups | Phase 3 + Phase 4 (initial) | 4-6 (P0) |
| Sprint 3 | User block — wave 1 | Phase 4 + 5 | 10-12 |
| Sprint 4 | User block — wave 2 | Phase 4 + 5 | 10-12 |
| Sprint 5 | Master block — wave 1 | Phase 4 + 5 | 10-12 |
| Sprint 6 | Master block — wave 2 | Phase 4 + 5 | 10-12 |
| Sprint 7 | Admin block — wave 1 | Phase 4 + 5 | 10-12 |
| Sprint 8 | Admin block + shared | Phase 4 + 5 | 10-12 |
| Sprint 9 | Spec refinement | Phase 5 (rework) | per-need |
| Sprint 10 | Handoff package | Phase 6 | full package |
| Sprint 11+ | Reserve / iteration | flexible | per-need |

**Total screen coverage target:** ~70-80 screens through mockup+spec by
end of Sprint 8 (assuming 10-12 screens per Sprint 3-8 = 60-72, plus
P0 specs carried in Sprint 3/5/7 = ~3-5 extras). Remaining ~40-50
screens (edge cases, low-priority, admin auxiliary, shared edge
variants) covered in Sprint 9 and reserve sprints.

**Why not all 120 in fixed scope:** the methodology requires operator
approval per screen. Real velocity will reveal itself in Sprints 3-4.
The reserve (Sprint 11+) absorbs slippage and late-arriving screens.

---

## 3. Sprint 0 — Foundation Cleanup

**Goal:** clean up the F0 state of `frontend/` and set up the `docs/`
folder structure so subsequent sprints have a sane starting point.

**Duration:** 1-2 days (not a full week — runs into Sprint 1 if
finished early).

**Owner:** Operator + Claude Code (for frontend cleanup) + Cowork (for
docs structure).

### 3.1 Tasks

**T0.1 — Create the `docs/` folder structure per methodology §3.**
Owner: Operator (manual) or Cowork.
Output: empty folders 01_deliverable, 02_design-system, 03_mockups,
04_methodology, 05_roadmap, 06_project-inputs. Plus INDEX.md at root
(stub).

**T0.2 — Place methodology + roadmap into the new structure.**
Owner: Operator.
Output:
- `docs/04_methodology/VELO-METHODOLOGY.md` (this methodology)
- `docs/05_roadmap/ROADMAP.md` (this roadmap)
- `docs/06_project-inputs/ARCHITECTURE.md` (copy from frontend/docs/)
- `docs/06_project-inputs/api-openapi.json` (snapshot from backend)

**T0.3 — Clean up frontend/ F0 state.**
Owner: Claude Code, instructed by operator.
Per the CC reconnaissance report:
- Either implement stub `UserShell.vue`, `MasterShell.vue`,
  `AdminShell.vue` so `vue-tsc --noEmit` passes, OR comment out the
  imports in `router/index.ts` until shells are built.
- Either replace `HomeView.vue` token references with existing tokens,
  OR pause router-level imports until tokens land in Sprint 1.
- Remove or fix `global.css` references to undefined tokens.
- Add `npm run gen:api` script to `package.json` (wraps `velo gen-types`
  backend command) — closes the "cheapest gap" from the recon report.
- Add `vue-i18n` to dependencies (currently missing per recon).
- Refactor `utils/format.ts` to remove hardcoded Russian strings —
  prepare for i18n keys. **Note:** the full i18n setup (`vue-i18n`
  install + locale files) is deferred to Sprint 2 (T2.6); this Sprint 0
  step is optional and can be deferred too if vue-i18n is not yet
  installed. The strings can be temporarily kept and moved during
  Sprint 2 when i18n is wired.

**T0.4 — Initialize INDEX.md files.**
Owner: Cowork.
Output: stub INDEX.md in each subfolder of docs/, top-level INDEX.md
at docs/ root, all referring to the methodology section §12 template.

### 3.2 Sprint 0 Gate

- All folders per §3 of methodology exist.
- Methodology, roadmap, ARCHITECTURE.md, api-openapi.json in place.
- `npm run build` in frontend/ succeeds (no missing shells, no
  undefined tokens).
- `npm run gen:api` script exists in `package.json`.
- All INDEX.md stubs present.

**Operator action:** quick sanity check; no formal gate document.
Approve verbally and proceed to Sprint 1.

---

## 4. Sprint 1 — Figma Extraction + Token Synthesis

**Goal:** complete Phase 1 (Figma extraction) and Phase 2 (token
synthesis) per methodology. Establish the design-system foundation.

**Duration:** 1 week.

**Owner:** Cowork (executor), Operator (validator).

### 4.1 Tasks

**T1.1 — Phase 1 execution.**
Owner: Cowork.
Prompt: methodology §9.2.
Output: `02_design-system/tokens/VELO-DS-INVENTORY.md` + all assets in
`02_design-system/assets/screenshots/` and `assets/icons/` + filled
`ASSETS-INDEX.md` + updated `02_design-system/INDEX.md`.

**T1.2 — INVENTORY GATE validation.**
Owner: Operator.
Reference: methodology §10.1.
Action: review inventory, spot-check 3-5 screenshots and 3-5 icons
against Figma. Pass or revise.

**T1.3 — Phase 2 execution.**
Owner: Cowork.
Prompt: methodology §9.3.
Output: `02_design-system/tokens/variables.css` and `global.css`
(master copies). Copies in `01_deliverable/styles/`.

**T1.4 — TOKENS GATE validation.**
Owner: Operator.
Reference: methodology §10.2.
Action: verify file split (no mixing per §6.2), zero `line-height:
normal`, zero `var() + Npx` without `calc()`, all required token groups
present. Pass or revise.

**T1.5 — Sync to frontend (initial).**
Owner: Claude Code, instructed by operator after T1.4 passes.
Action: copy `01_deliverable/styles/variables.css` →
`frontend/src/styles/variables.css`, same for `global.css`. Verify
`npm run build` still passes.

### 4.2 Sprint 1 Gate

- INVENTORY GATE passed.
- TOKENS GATE passed.
- `frontend/src/styles/` contains valid tokens.
- `02_design-system/INDEX.md` shows Token Status table filled.

### 4.3 Sprint 1 Risks

- **Risk 1.A:** Figma "Design System" page is empty/absent, mockup-mining
  is the only source. Mitigation: methodology §6.5 step 1.1 covers this;
  Cowork logs and proceeds.
- **Risk 1.B:** Required token groups have many MISSING entries (states,
  hover, focus). Mitigation: methodology §6.4 placeholder protocol;
  TODO logged in DS INDEX.
- **Risk 1.C:** Cowork repeats earlier anti-patterns (mixed
  variables.css/global.css, line-height: normal). Mitigation:
  methodology §11.1 explicit prohibitions; gate validation catches.

---

## 5. Sprint 2 — Styleguide + First Mockups (P0)

**Goal:** build the living styleguide (Phase 3) and deliver the first
batch of mockups (P0 priority screens).

**Duration:** 1 week.

**Owner:** Cowork (executor), Operator (validator).

### 5.1 Tasks

**T2.1 — Phase 3: Styleguide HTML.**
Owner: Cowork.
Prompt: methodology §9.4.
Output: `02_design-system/styleguide/velo-design-system.html` covering
all declared Tier 1 + Tier 2 components.

**T2.2 — STYLEGUIDE GATE validation.**
Owner: Operator.
Reference: methodology §10.3.
Action: open in browser, walk through Tokens / Components / Patterns
tabs. Spot-check each component's variants. Verify side-by-side with
Figma DS page (if present) or mockup PNGs.

**T2.3 — P0 mockups identification.**
Owner: Operator.
Action: at sprint start, declare which 4-6 screens are P0 (developer
needs them first for early integration). Typical candidates: one screen
per role (user-dashboard, master-dashboard, admin-dashboard) + a
shared auth flow start (welcome or login).

**T2.4 — Phase 4: Build P0 mockups.**
Owner: Cowork.
Prompt: methodology §9.5 (per screen).
Output: HTML files in `03_mockups/{role}/`. One file per screen. P0
quantity 4-6.

**T2.5 — MOCKUP GATE validation per P0 screen.**
Owner: Operator.
Reference: methodology §10.4.
Action: open each mockup side-by-side with Figma PNG. Approve or
request revision.

**T2.6 — Setup i18n in frontend.**
Owner: Claude Code.
Action: install `vue-i18n`, create `src/i18n/index.ts` and
`src/i18n/locales/ru.json` (empty + `en.json` stub). Wire to main.ts.
This unblocks Sprint 3 specs that declare i18n keys.

### 5.2 Sprint 2 Gate

- STYLEGUIDE GATE passed.
- 4-6 P0 mockups built, MOCKUP GATE passed for each.
- `03_mockups/INDEX.md` reflects P0 status.
- vue-i18n installed and minimally wired in frontend/.

> **Note on P0 specs:** P0 mockups are produced in Sprint 2, but their
> specs are written in the first sprint of their respective role block
> (user-dashboard spec → Sprint 3, master-dashboard spec → Sprint 5,
> admin-dashboard spec → Sprint 7). This keeps spec work batched per
> role and per Phase 4-then-5 ordering.

### 5.3 Sprint 2 Risks

- **Risk 2.A:** Styleguide reveals missing components not yet
  identified. Mitigation: log in DS INDEX TODOs, add to Tier 2 list,
  build before they're needed for mockups.
- **Risk 2.B:** P0 screens reveal token gaps (no destructive color, no
  hover state). Mitigation: re-entry into Phase 2 per methodology §4.3,
  add tokens to master, propagate.

---

## 6. Sprint 3 — User Block Mockups + Specs (Wave 1)

**Goal:** start the per-screen mockup+spec production for the User role.
First wave covers ~10-12 user screens. This is the first sprint where
the full pipeline runs at scale.

**Duration:** 1 week.

**Owner:** Cowork (executor), Operator (validator).

### 6.1 Sprint 3 Scope (planning target)

User screens, wave 1 — highest priority first:

| Order | Screen | Route | Notes |
|---|---|---|---|
| 1 | user-dashboard | / | Already P0 in Sprint 2 — spec only this sprint |
| 2 | user-practice-detail | /practice/:id | Core booking flow start. Action set includes `create_report` ("Пожаловаться" — one-off action; see SCR Action Contract) per validation pass 2026-05-17. |
| 3 | user-bookings | /bookings | All booking statuses |
| 4 | user-calendar | /calendar | Calendar grid + slots |
| 5 | user-profile | /profile | Avatar, balance, settings |
| 6 | user-waitlist | /waitlist | WaitlistCard list — FSM (methodology §8.7, I6: `waiting → notified → confirmed \| declined \| expired`; `waiting → left`). |
| 7 | user-diary | /diary | DiaryEntryCard list, mood filter |
| 8 | user-topup | /topup | Balance topup flow |
| 9 | user-practice-buy-preview | step in /practice/:id flow | Preview → purchase |
| 10 | user-onboarding-welcome | /welcome | Onboarding step 1 |

Targets: 10-12 mockups, 10-12 specs. If P0 mockups overlap, specs only.

### 6.2 Tasks

**T3.1 — Mockup batch (Phase 4) for screens 2-10.**
Owner: Cowork.
Prompt: methodology §9.5, repeated per screen.
Output: 9-10 new HTML files in `03_mockups/user/`.

**T3.2 — Operator review pass for mockups.**
Owner: Operator.
Reference: methodology §10.4.
Action: review batch. Approve passers, send revisions back.

**T3.3 — Spec batch (Phase 5) for approved mockups.**
Owner: Cowork.
Prompt: methodology §9.6, per spec.
Output: SCR-NNN-{name}.md files in `01_deliverable/screens/`. Numbering
starts at SCR-001 (user-dashboard) and increments.

**T3.4 — Operator review pass for specs.**
Owner: Operator.
Reference: methodology §10.5.
Action: read each spec end-to-end. Verify operationIds against
api-openapi.json. Cross-check VELO Invariants references. Approve
(status → active) or revise.

**T3.5 — INDEX.md updates.**
Owner: Cowork after each artifact.
Action: methodology §12.2 — local INDEX updates immediately.

### 6.3 Sprint 3 Gate

- 9-10 user mockups approved (MOCKUP GATE per screen).
- 10-12 user specs approved (SPEC GATE per screen).
- `01_deliverable/screens/INDEX.md` reflects SCR-001 through ~SCR-010.
- `03_mockups/INDEX.md` reflects user-block progress.

### 6.4 Sprint 3 Risks

- **Risk 3.A:** First specs reveal that the 12-section template is
  overkill or underkill for actual VELO screens. Mitigation: at sprint
  end, operator notes findings; if methodology needs adjustment,
  applies amendments per methodology §13.
- **Risk 3.B:** Waitlist FSM proves more complex than declared in
  methodology §8.7. Mitigation: refine the FSM in methodology before
  writing waitlist-related specs.
- **Risk 3.C:** API contract (api-openapi.json) is missing endpoints
  required by user screens. Mitigation: spec authoring exposes the gap;
  operator coordinates with backend.

---

## 7. Sprint 4 — User Block Completion (Wave 2)

**Goal:** finish remaining User-role screens not covered in Sprint 3.
Close out user block.

**Duration:** 1 week.

**Owner:** Cowork (executor), Operator (validator).

### 7.1 Sprint 4 Scope (planning target)

Remaining user screens. Typical count 10-15 depending on velocity:

| Examples |
|---|
| user-onboarding step 2..N |
| user-login |
| user-register |
| user-oauth-callback |
| user-notification-center |
| user-settings (privacy, notifications) |
| user-account-delete-confirm (destructive) |
| user-history |
| user-feedback-submit |
| user-promo-redeem |
| user-reports-list (`/reports` — list of user's own reports using `get_my_reports`; allows `update_report` to edit own report) |
| user-error-404 / generic error |

Exact list is finalized at sprint start by the operator. The list above
is indicative.

### 7.2 Tasks

Identical structure to Sprint 3 (T3.1-T3.5), applied to wave 2 screens.

### 7.3 Sprint 4 Gate

- All approved user screens have mockup + spec.
- User block in `screens/INDEX.md` shows ~20-25 SCR entries active.
- No user-block screen left in `draft` status without operator
  feedback.

### 7.4 Sprint 4 Risks

- **Risk 4.A:** OAuth + Telegram deep-link complexity reveals gaps in
  VELO Invariant I5 (Telegram deep links survive auth). Mitigation:
  refine I5 in methodology, propagate to onboarding specs.
- **Risk 4.B:** Sprint 3 specs need rework based on Sprint 4 learnings.
  Mitigation: methodology §8.9 in-place editing; defer batch rework to
  Sprint 9 (refinement sprint).

---

## 8. Sprint 5 — Master Block Mockups + Specs (Wave 1)

**Goal:** start Master role coverage. The Master role introduces new
domain components (PromoRow, WithdrawalRow, InsightsChart) and new
business rules (balance ≥ threshold for withdrawal, master application
flow).

**Duration:** 1 week.

**Owner:** Cowork (executor), Operator (validator).

### 8.1 Sprint 5 Scope (planning target)

Master screens, wave 1:

| Order | Screen | Route | Notes |
|---|---|---|---|
| 1 | master-dashboard | /master | Already P0 — spec only |
| 2 | master-practices | /master/practices | PracticeCard owner view |
| 3 | master-practice-create | /master/practices/new | 3-step form |
| 4 | master-practice-edit | /master/practices/:id | Edit existing |
| 5 | master-analytics | /master/analytics | InsightsChart aggregate. **Known limit:** aggregate across all master's practices is **client-side only** (loop `get_practice_insights` per practice). No backend aggregate endpoint exists — spec must document this constraint and pagination strategy. |
| 6 | master-finance | /master/finance | Balance + withdrawals + promos |
| 7 | master-profile | /master/profile | MasterStatusBadge |
| 8 | master-apply | /master/apply | 3-step apply flow |
| 9 | master-pending | /master/pending | Awaiting verification |
| 10 | master-practice-attendance | /master/practices/:id/attendance | Check-in users |

### 8.2 Tasks

Identical structure to Sprint 3.

### 8.3 Sprint 5 Gate

- 10-12 master mockups approved.
- 10-12 master specs approved.
- New domain components needed by master (PromoRow, WithdrawalRow,
  InsightsChart) appear in styleguide; if missing, added to DS in
  parallel.

### 8.4 Sprint 5 Risks

- **Risk 5.A:** Withdrawal flow exposes role-vs-viewMode question (I3
  in methodology). Spec must reference real `user.role === 'master'`
  check. Mitigation: covered by I3; reviewers verify.
- **Risk 5.B:** Master Apply 3-step flow doesn't fit in one SCR-NNN.
  Mitigation: split into SCR-NNN-master-apply-step-1, step-2, step-3 OR
  one SCR with explicit `flow: master-apply` front-matter field.
  Decision at sprint start.

---

## 9. Sprint 6 — Master Block Completion (Wave 2)

**Goal:** finish remaining Master-role screens.

**Duration:** 1 week.

**Owner:** Cowork + Operator.

### 9.1 Sprint 6 Scope

Remaining master screens, typical 10-15:

| Examples |
|---|
| master-practice-detail-public (preview as viewer) |
| master-promos-list |
| master-promo-create |
| master-withdrawal-create |
| master-withdrawal-history |
| master-bookings-overview |
| master-messages |
| master-settings |
| master-help |
| master-onboarding (post-approval first-time) |

### 9.2 Tasks

Identical structure to Sprint 3.

### 9.3 Sprint 6 Gate

- All approved master screens have mockup + spec.
- Master block in `screens/INDEX.md` shows ~20-25 active SCR entries.

### 9.4 Sprint 6 Risks

- **Risk 6.A:** Withdrawal flow is multi-screen (master creates →
  admin approves). Need cross-spec references. Mitigation: front-matter
  `depends-on` field per methodology §8.5.

---

## 10. Sprint 7 — Admin Block Mockups + Specs (Wave 1)

**Goal:** start Admin role coverage. Admin screens are fewer (~15-20)
but introduce permission checks and approval flows.

**Duration:** 1 week.

**Owner:** Cowork + Operator.

### 10.1 Sprint 7 Scope (planning target)

| Order | Screen | Route | Notes |
|---|---|---|---|
| 1 | admin-dashboard | /admin | Already P0 — spec only |
| 2 | admin-masters | /admin/masters | Masters list, status filter |
| 3 | admin-master-review | /admin/masters/:id | Application review |
| 4 | admin-reports | /admin/reports | User reports |
| 5 | admin-report-resolve | /admin/reports/:id | Resolve or dismiss |
| 6 | admin-withdrawals | /admin/withdrawals | List withdrawals |
| 7 | admin-withdrawal-review | /admin/withdrawals/:id | Approve/reject. **Backend gap:** `GET /api/v1/admin/withdrawals/{id}` is not in OpenAPI — pass row via router state from list view; cannot deep-link. See `06_project-inputs/BACKEND-REQUESTS-2026-05-17.md`. |
| 8 | admin-consistency | /admin/consistency | Semaphore results |
| 9 | admin-users | /admin/users | User search |
| 10 | admin-user-detail | /admin/users/:id | User profile (admin view). **Backend gap:** `GET /api/v1/admin/users/{id}` is not in OpenAPI — pass row via router state; if user is master, fall back to `get_master`. See `06_project-inputs/BACKEND-REQUESTS-2026-05-17.md`. |

### 10.2 Tasks

Identical structure to Sprint 3.

### 10.3 Sprint 7 Gate

- 10 admin mockups approved.
- 10 admin specs approved.
- Permission patterns (admin-only mutations) explicitly tested in
  acceptance criteria.

### 10.4 Sprint 7 Risks

- **Risk 7.A:** Admin screens may reveal missing API endpoints
  (admin-specific). Mitigation: spec authoring exposes; operator
  coordinates with backend.
- **Risk 7.B:** Admin role has different shell (3 tabs vs 4). Confirm
  AdminShell handles correctly in mockups. Mitigation: covered by Tier
  3 layout work in DS.

---

## 11. Sprint 8 — Admin Block + Shared Screens (Wave 2)

**Goal:** finish Admin screens; cover shared screens (auth, error,
loading, generic).

**Duration:** 1 week.

**Owner:** Cowork + Operator.

### 11.1 Sprint 8 Scope (planning target)

Remaining admin (~5-10) + shared (~10-15):

| Block | Examples |
|---|---|
| Admin remaining | admin-stats-detail, admin-promos-overview, admin-broadcast, admin-settings |
| Shared auth | welcome, login, register, oauth-callback, loading, reset-password |
| Shared error | 404, 500, network-error, session-expired, role-mismatch |
| Shared modal | confirm-destructive, generic-modal-template |

### 11.2 Tasks

Identical structure to Sprint 3.

### 11.3 Sprint 8 Gate

- All approved admin and shared screens have mockup + spec.
- Total coverage: ~70-80 screens with both mockup and spec (status
  `active`).
- `screens/INDEX.md` summary section shows tally.

### 11.4 Sprint 8 Risks

- **Risk 8.A:** Auth flow with Telegram deep links is harder than
  expected. Mitigation: dedicate extra time in Sprint 8 specifically to
  auth flow; defer to Sprint 9 if needed.

---

## 12. Sprint 9 — Spec Refinement + Edge Cases

**Goal:** refine specs that earlier sprints flagged for rework. Cover
edge-case screens identified during waves 1-2 but deferred.

**Duration:** 1 week.

**Owner:** Cowork + Operator + (optional) Claude Code consult.

### 12.1 Sprint 9 Scope

Inputs to this sprint:
- All specs with rework flags from previous sprints.
- All screens identified during waves 1-2 but not yet covered (typically
  edge cases: empty states, error variants, alternate flows).
- Any new screens identified by the operator during the project.

### 12.2 Tasks

**T9.1 — Refinement triage.**
Owner: Operator.
Action: walk through `01_deliverable/screens/INDEX.md`. Flag specs that
need rework based on accumulated learnings. Add to backlog.

**T9.2 — Refinement execution.**
Owner: Cowork.
Action: in-place edits per methodology §8.9 (or supersede via §8.8).
Update Changelogs.

**T9.3 — New edge-case mockups + specs.**
Owner: Cowork, per methodology §9.5 + §9.6.
Action: add remaining screens to bring coverage closer to ~95-110
(out of ~120 planned). The remaining gap (10-25 screens) is absorbed
by reserve sprints.

**T9.4 — Methodology amendments (if needed).**
Owner: Operator + Chat (Claude).
Action: if learnings from waves 1-2 warrant methodology changes, draft
amendments. Apply per methodology §13. Bump version.

### 12.3 Sprint 9 Gate

- All flagged specs reworked and re-approved.
- Edge-case coverage closes remaining gaps.
- Methodology version bumped if amendments applied.

---

## 13. Sprint 10 — Handoff Package + Final Sync

**Goal:** assemble the deliverable package per Phase 6 of methodology.
Synchronize all artifacts. Prepare for handoff to Claude Code (or
direct developer).

**Duration:** 1 week.

**Owner:** Cowork (assembler), Operator (validator).

### 13.1 Tasks

**T10.1 — Phase 6: Handoff package assembly.**
Owner: Cowork.
Prompt: methodology §9.7.
Output: `01_deliverable/` fully populated and synced with masters.

**T10.2 — README finalization.**
Owner: Cowork, per methodology §9.7.1 template.
Output: `01_deliverable/README.md` with no placeholders, full file map,
all rules, all references.

**T10.3 — PACKAGE GATE validation.**
Owner: Operator.
Reference: methodology §10.6.
Action: byte-diff master vs deliverable. Walk through README. Verify
INDEX.md.

**T10.4 — Frontend sync (final).**
Owner: Claude Code.
Action: copy from `01_deliverable/styles/` and `assets/` to
`frontend/src/`. Verify `npm run build` succeeds. Verify
`vue-tsc --noEmit` succeeds.

**T10.5 — Handoff communication.**
Owner: Operator.
Action: notify Claude Code / developer that package is ready. Provide
the location: `D:\02_Projects\velo\docs\01_deliverable\`. Schedule
follow-up review.

### 13.2 Sprint 10 Gate

- PACKAGE GATE passed.
- `frontend/src/` reflects deliverable.
- Build + typecheck green.
- Developer notified.

### 13.3 Sprint 10 Risks

- **Risk 10.A:** Token drift discovered during sync (master vs
  deliverable differ). Mitigation: regenerate deliverable from master;
  log drift cause in DS INDEX.
- **Risk 10.B:** Implementation-stage feedback exposes spec gaps.
  Mitigation: this is normal and expected; goes into Sprint 11 reserve.

---

## 14. Sprint 11+ — Reserve / Polish / Iteration

**Goal:** absorb slippage from earlier sprints; respond to
implementation-stage feedback from Claude Code.

**Duration:** open-ended.

**Owner:** Operator drives priorities.

### 14.1 Typical Reserve Activities

- Implementation feedback: Claude Code reports spec ambiguities → spec
  refinement in this sprint.
- Late-arriving screens (product additions).
- Dark theme implementation (currently deferred per methodology §2.5
  I7).
- Accessibility audit pass.
- Performance audit pass.
- Methodology v2.0 if major learnings accumulated.

### 14.2 How Reserve Sprints Are Planned

At start of each reserve sprint, operator surveys:
- `01_deliverable/screens/INDEX.md` → any specs not active?
- Frontend implementation status → any blockers from CC?
- `02_design-system/INDEX.md` → any open TODOs?
- Stakeholder feedback → any new requirements?

Sprint scope is finalized based on the top 5-7 priorities.

---

## 15. Sprint Tracking and Reporting

### 15.1 Per-Sprint File Convention

Each sprint has a file: `docs/05_roadmap/sprint-NN.md`. Template:

```markdown
# Sprint N — {Sprint Name}

Dates: 2026-MM-DD → 2026-MM-DD
Status: planned | in-progress | closed

## Goal
{one-paragraph goal from this roadmap}

## Scope
{table of screens / artifacts to deliver, copied from roadmap}

## Daily log
- 2026-MM-DD: {what happened}
- ...

## Gate results
- {Gate name}: passed | failed (reason)
- ...

## Deferred to next sprint
- {item}

## Methodology amendments proposed
- {none | description}
```

### 15.2 Sprint Closure Ritual

Friday afternoon of each sprint:

1. Operator opens `sprint-NN.md`.
2. Walks through gate results — mark each passed/failed.
3. Lists deferred items.
4. **If token master changed during the sprint:** trigger incremental
   token sync — Cowork copies updated `02_design-system/tokens/*.css`
   to `01_deliverable/styles/*.css`, then Claude Code copies to
   `frontend/src/styles/*.css`. Verify `npm run build` still passes.
   This prevents the frontend from accumulating drift from master
   tokens between Sprint 1 and Sprint 10.
5. Updates top-level `docs/INDEX.md` Recent Changes section.
6. Closes sprint file (status: `closed`).
7. Opens `sprint-(N+1).md` with planned scope.

### 15.3 Velocity Calibration

After Sprint 3 and Sprint 4 (first two production sprints), the
operator reviews actual screen throughput:

- If 10-15 screens/sprint is on track: continue plan as-is.
- If <10/sprint: review bottlenecks (Cowork capacity, gate revision
  rate, spec complexity). Adjust either scope per sprint or reserve
  sprints upward.
- If >15/sprint: consider closing project earlier or expanding scope
  (e.g., dark theme moved into roadmap).

Velocity is reported at Sprint 4 closure as a roadmap update.

---

## 16. Risk Register

Consolidated from per-sprint risks. Operator monitors throughout.

| ID | Risk | Probability | Impact | Mitigation owner |
|---|---|---|---|---|
| R-1 | Figma DS frame absent; tokens only from mockup-mining | Medium | Low | Cowork (methodology §6.5 covers) |
| R-2 | Required token groups have many MISSING entries | Medium | Medium | Cowork → Operator decision (§6.4) |
| R-3 | Cowork repeats earlier anti-patterns | Low (with methodology) | High if repeats | Operator (gate validation) |
| R-4 | First specs reveal template is wrong-sized | Medium | Medium | Operator at Sprint 3 closure |
| R-5 | API contract is incomplete for some screens | Medium | High | Operator + backend coordination |
| R-6 | Waitlist FSM proves more complex than declared | Medium | Low | Operator refines methodology §8.7 |
| R-7 | Telegram deep-link auth flow is harder than expected | Medium | Medium | Sprint 8 dedicated focus |
| R-8 | Velocity below 10 screens/sprint | Low-Medium | High (timeline slip) | Operator at Sprint 4 calibration |
| R-9 | Token drift between master and deliverable | Low (rsync discipline) | Medium | Cowork (Phase 6 protocol) |
| R-10 | Implementation feedback exposes spec gaps after handoff | High | Medium | Reserve sprints (Sprint 11+) |
| R-11 | Code-only contracts (status enums, VeloError shape — see methodology I8) drift between backend and frontend (`vue-tsc` cannot catch). | Medium | High | Specs reference enums by exact name; status-bearing components use exhaustive `switch` with explicit error branch (per I8 mitigation). Long-term: backend declares enums in OpenAPI. |
| R-12 | Build is broken on `release @ F0` due to `frontend/src/api/types.ts:65` (`PayoutDetails` rename). Blocks any frontend verification. | Confirmed (existing) | Critical until fix | Sprint 0 T0.0 — one-line fix. Long-term mitigation: Sprint 0 T0.7 wires `gen:api:check` pre-commit hook (R-11 also). |
| R-13 | Backend gaps: `GET /api/v1/admin/withdrawals/{id}` and `GET /api/v1/admin/users/{id}` not in OpenAPI; affects Sprint 7 admin-withdrawal-review + admin-user-detail. | Confirmed (existing) | Medium | Workaround in Sprint 7 specs (router-state pass-through); backend requests filed in `06_project-inputs/BACKEND-REQUESTS-2026-05-17.md`. |

---

## 17. Out of Scope for This Roadmap

This roadmap covers design-to-handoff work. The following are explicitly
out of scope:

- **Frontend implementation timeline** — Claude Code's work consuming
  the deliverable package is tracked separately by the developer or
  operator outside this roadmap.
- **Backend implementation timeline** — backend team works in parallel;
  OpenAPI contract is the interface.
- **Product feature prioritization** — what features VELO has is set by
  product documents; this roadmap delivers whatever screens are
  agreed-upon.
- **User testing / UAT** — not in design-to-handoff scope.
- **Release planning, deployment, rollout** — separate from design
  work.
- **Marketing / launch coordination** — outside engineering scope.

---

## Anchor

```
[VELO-ROADMAP.md | v1.1 | 2026-05-17]
Operating plan for VELO design-to-handoff work.
Built on top of VELO-METHODOLOGY.md v1.1.
v1.1 changes: validation pass — Sprint 3 user-practice-detail Action
Contract includes create_report; Sprint 4 adds user-reports-list;
Sprint 5 master-analytics flagged as client-side aggregation;
Sprint 7 admin-withdrawal-review + admin-user-detail flagged as
backend gaps; Risk Register expanded with R-11/R-12/R-13.
See 06_project-inputs/VALIDATION-REPORT-2026-05-17.md for details.
Location: D:\02_Projects\velo\docs\05_roadmap\ROADMAP.md
Status: Draft for operator approval before execution.
```
