# Cycle C06 + C06b: API Contract Patch + Post-Regen Consumer Migration

> Phase 01: Bundle Migration | Sprint 1: Pilot
> Type: standard (C06 patch + C06b follow-up combined)
> Tier: MEDIUM
> Status: DONE
> Closed: 2026-04-26

## Goal

Apply backend partner's contract review findings (Zodd_review.md @ commit `105fddd`). Fix B.3 (P1 dead route trigger), B.11 (BASE_URL dev warning). Resolve B.1 (UserResponse cleanup). Address A.2 (financial constants migration).

## Result

C06 (reduced scope): 2 files modified — `UserDashboardView.vue` (button + dedicated CSS removal, strict scope) + `client.ts` (dev-only `console.warn` for empty `VITE_API_BASE_URL`). B.3 + B.11 landed cleanly.

C06 Pre-Exec discovery: B.1 already-resolved by partner regen at commit `81304a6` (generated.ts `UserResponse` matches audit AFTER shape; 0 stale-usage). A.2 blocked: partner shipped CR-01 backend changes (`masters/schemas.py:117-141` Pydantic + `masters/router.py:81-82` population) but regen ran against stale openapi.json (FastAPI not restarted between Pydantic edit at 19:15 UTC and regen at 20:15 UTC) — `MasterProfileResponse` missing `min_withdrawal_cents` + `withdrawal_fee_cents`. A.2 deferred to follow-up cycle (BACKLOG #26).

C06b (post-regen consumer migration): 11 files modified, 38 typecheck errors → 0. Resolved 6 error classes via Option 3 (broaden narrow Records to `Record<string, X>` and function params from union types to `string`) + tactical patches:
- Class A+B (17 errors): broaden Records + function params at `displayHelpers.ts`, `PracticeListItem.vue`, `BookingCard.vue`, `AnalyticsView.vue`, `EditPracticeView.vue`, `MasterDashboardView.vue`, `MasterFinanceView.vue`. Aligns with existing `MOOD_EMOJI`/`RATING_EMOJI`/`METHOD_LABEL` convention in same files.
- Class C (16 errors): `?? 0` pattern at AnalyticsView optional aggregate field accesses.
- Class D (2 errors): `PayoutDetails` rename to `PayoutDetailsUpdate` (request body) / `PayoutDetailsResponse` (response) at `api/masters.ts` + `MasterProfileView.vue`.
- Class E (1 error): `as string` cast at `MasterFinanceView.vue:160` (`payout_details.method`).
- Class F (1 error): tactical-include for `PracticeSummary.timezone` at `UserDashboardView.vue:300` — Berlin fallback preserved verbatim with explicit BACKLOG/Zodd-CRITICAL comment block (real fix gated on backend `PracticeSummary.timezone` field add — BACKLOG #27).
- Class G (1 error): `?? 'info'` fallback at `AdminConsistencyView.vue:76` for optional `criticality`.

Final gates: typecheck 0 errors, lint 758 warnings (delta vs baseline 0), vite build ✓ in 1.36s with PWA 96 precache entries.

## Key Decisions

- **#022** — C06 reduced scope after Pre-Exec discovery (4 audit findings → 2 active fixes + 1 no-op + 1 deferred). Documented in decisions.md.
- **#023** — types.ts SSOT reinterpretation post-`81304a6` regen pipeline + Option 3 broaden as established convention for post-regen consumer migration. Documented in decisions.md.
- B.3 strict scope (button + dedicated CSS only; card-level rules retained) chosen over loose scope per Architectural Cleanliness Principle exception ("explicit scope boundary prohibits CSS layout refactor").
- B.11 inline placement at `client.ts` (no centralized env validator exists). Env var `VITE_API_BASE_URL` corrected from audit's typo `VITE_API_URL`. Audit's `VITE_USE_PROXY` reference dropped (phantom env var).
- Class F tactical-include over real fix: real fix requires backend coordination (out of frontend-only scope this cycle); Berlin fallback bug preserved with explicit code comment + BACKLOG entry.

## Acceptance Summary

C06: 10/10 passed. C06b: 11/11 steps + all post-edit gates passed. Combined cycle: 38 baseline errors → 0; 12 files staged for phase commit; runtime safety preserved via `?? fallback` patterns at consumer sites.

Status: DONE
Closed: 2026-04-26
