# Cycle C08: Backend coordination report
> Phase 02: Audit + Backend Coordination | Sprint 1: Pilot
> Type: standard (partner handoff doc)
> Status: DONE

## Goal
Produce a single document for the backend partner enumerating endpoints needed for S2/S3 frontend work — formatted by feature group (per Human decision) rather than flat route list.

## Result
backend-coord-report.md created at `docs/03_sprint/S1-pilot/backend-coord-report.md` (143 lines, 9.9 KB).

Structure:
- Header: from/date/base commit (`47a6cd8`)/audit method.
- TL;DR: 7 partner-owed feature groups + 6 dop items.
- 7 partner-owed features: 1. Waitlist API (4 routes), 2. Profile editing (PATCH /users/me), 3. Logout-all (POST /auth/logout-all), 4. Purchase history (GET /purchases/me), 5. User-side reports (3 routes), 6. Promo management (3+ routes), 7. Live-session join/leave (2 routes).
- Дополнительно block: 2 frontend-wrapper-only (AISummary backend ready in generated.ts:18; BookingDetail backend ready) + 2 new partner schema asks (MasterProfile public read; MH-17 practice room) + 2 regen-trigger asks (CR-01 financial fields per BACKLOG #26; Zodd CRITICAL #1 timezone per BACKLOG #27).
- Запрос section: 3 specific asks (confirm 7-feature plan; run regen for #5+#6; discuss MasterProfile/MH-17 schema later).

Tone: collegial, на ты. References Zodd_review.md §B.5 + BACKLOG entries #21/#26/#27.

Status: DONE
Closed: 2026-04-26
