# ZOD BACKEND TASKS — consolidated backend wishlist (user / master / admin)

> **Provenance.** This document is the result of a full transition-trace audit of all three
> zones (Orchestrator-9, PROMPT #38 master / #39 admin / #40 user) cross-referenced with
> `master-ds-zod-roadmap.md` (per-screen findings, Screens 1–18 + the ADMIN section) and verified
> against the live backend contract in `frontend/src/api/generated.ts` and the `api/*.ts` wrappers.
> Every stub that today shows a «недоступно» (unavailable) toast, an em-dash «—», or a
> captured-only form field is recorded here as a backend task.
>
> **How the frontend got here.** The UI is built to the operator's approved design *in full*,
> following the project rule "build the full design now, stub the missing backend". Where a
> control has no backend, the frontend does not fake a result — it renders the real layout and
> the tap raises a «недоступно» (unavailable) toast, or the value renders «—». This document is the
> list of those gaps, for the backend (Zod) to close.
>
> **Priority legend.**
> - **P0** — a screen that is already built does **not function** without this. Highest urgency.
> - **P1** — the endpoint exists or the screen partly works; this **enriches** a partially-working screen.
> - **P2** — nice-to-have; the screen is usable without it.

---

## ⏱ STATUS — actualized 2026-06-28 (re-verified against live `generated.ts` on `origin/test=4713c60`)

Each epic carries a **STATUS** line. Numbering / names unchanged so they map 1:1 to Zod's version.
**E12–E17 are new** (post-audit gaps: E12–E14 + E15 master-onboarding-flag / E16 apply-languages /
E17 master-web-auth, all added 2026-06-26/27). Re-audited field-by-field vs the live `4713c60`
contract. **Sole status change since 2026-06-24: E8 OPEN → PARTIAL** (master-notifications contract +
capability gate delivered). Everything else unchanged, no regression. One-glance state:

- **DELIVERED (do not rebuild):** **E1** named reviews · **E2** income/ledger+transactions ·
  **E5** students/CRM · **E7** period stats (master + admin) · **E9 (core)** admin practices/revenue/metrics.
- **PARTIAL (some delivered, a remainder open):** **E3** (create-recurrence done; PATCH-edit open) ·
  **E8** ⬆ (master-notifications contract `MasterNotificationSettings` gen:486 + on UserResponse gen:1118
  /UserUpdate gen:1138 + master-capability gate DELIVERED; push-delivery worker + unread bell-feed open) ·
  **E9** (rich masters/reports/withdrawals open) · **E10** (POST done; GET-list + DELETE open) ·
  **E11** (real `DELETE /users/me` done; rest open) · **E1** (cross-practice needs-attention *filter* open).
- **OPEN (untouched, field absent on `4713c60`):** **E4** messaging · **E6** weekly summary ·
  **E12** checkin_count · **E13** apply-doc/photo-upload · **E14** application rejection_reason ·
  **E15** master_onboarding_completed · **E16** apply languages · **E17** master web-auth (PARKED).
- **Delivered OUTSIDE the epic set (not E-numbered):** auto-complete-by-duration (lifecycle worker);
  **W-6/W-7** (user dashboard full attended-stats + bookings load-more, commit `028ae7e`); plus
  frontend/test self-fixes (`StudentDetailResponse.name/avatar`, admin-metrics test isolation) — for
  coordination, not Zod work.

---

## Environment note — admin/finance seed data

Originally the admin/finance domains had no seed, so admin screens rendered empty even where the
contract existed. **UPDATE 2026-06-24:** a priced + `as_master` seed now populates masters / practices
/ participants / check-ins / reviews on TEST, so master + most admin screens render real values. The
admin **consistency / withdrawals** domains may still need dedicated seed coverage. This is an
**environment / seed-script gap, not a backend-contract gap** — do not assume an admin endpoint is
missing just because a less-seeded screen looks thin.

---

## Grounding facts (verified in `generated.ts`; ⟳ = updated 2026-06-24)

**Already present in the backend (do NOT rebuild):**
- `GET /admin/stats` ⟳ now `AdminStatsOverviewResponse` (deltas/revenue/rates/period, gen:113),
  `GET /admin/masters` + verify/reject, `GET /admin/reports`, `GET/POST /admin/withdrawals` +
  approve/reject, `GET /admin/consistency`, `GET /admin/users`. ⟳ NEW since: `GET /admin/practices`
  (+/{id}) gen:567/59, `GET /admin/revenue` gen:97, `/admin/metrics/{check-in,feedback,return}`.
- Promo module: `POST /admin/promos`, `POST /masters/me/promos` (gen:320), `PaginatedPromosResponse`
  (gen:639), `promo_code` on booking. (GET-own-list + DELETE still absent — E10.)
- `email` exists on the master-application interface but ⟳ still NOT on `UserResponse` (gen:1059) — E11.
- Master balance `available_cents` / `frozen_cents` on `MasterProfileResponse`.
- `GET /practices/{id}/ai-summary` — a per-practice mock summary (NOT the weekly summary — E6).
- `GET /practices/{id}/attendance` → `AttendanceResponse` (gen:181) carries `attended`/`no_show`/
  `total`/`pending` + per-item projection. (The per-card LIST aggregate is still absent — E11.)

**Key contract shapes:**
- ⟳ `NotificationSettings` / `…Update` still carry **exactly four keys** (`push`, `practice_reminders`,
  `master_messages`, `support_messages`, gen:551) — the +9 master keys + `schedule` are still OPEN (E8).
- ⟳ `PracticeType` includes `'series'` AND now a real recurrence model exists: `RecurrenceSpec`
  (gen:876), `CreatePracticeRequest.recurrence` (gen:350), `recurrence_days`/`total_sessions`/
  `completed_sessions` on `PracticeResponse` (gen:765-767). **But `UpdatePracticeRequest` (gen:1032)
  has no `recurrence`** — edit-a-series is still OPEN (E3).
- ⟳ `ReportResponse` (gen:895) still carries `reporter_id` only — no category/priority/reporter_name/
  date filter (E9).
- ⟳ `AdminWithdrawalResponse` (gen:141) still has no master display name + no 2FA (E9).

---

## SELF-FIX LOG — batch №227 (2026-07-01, operator-authorized backend exception)

Minor gaps closed by us (backend projection + manual `generated.ts` + frontend wire), NOT Zod:
- **E18** `zoom_link` on `PracticeSummary` — from_attributes projection (no migration); `generated.ts` + Zoom wired (user dashboard / live / master dashboard).
- **E14** `rejection_reason` on `MasterProfileResponse` — projected from `data.account.rejection_reason` in the router; `MasterPendingView` shows the real reason.
- **E1 (increment)** `user_id` on `MasterReviewItem` + diary `ReviewItem` — projected from the joined `User`; per-practice review cards (`PracticeReviewsView`) navigate to the student profile. *(Attention-filter remainder still open — see E1; AnalyticsView attention card left on its existing message action pending operator UX call.)*
- **E10** GET `list_my_promos` + PATCH deactivate were already delivered by Zod — frontend now wired (`api/promos.ts` + `MasterPromocodesView`, active-list + soft-deactivate); no hard DELETE added.

TARGETED Zod one-liners (small, but in Zod-hot files — Zod to slot; we did NOT touch these):
- **E12** add a grouped-COUNT `checkin_count` to `PracticeResponse`/`PracticeSummary`, batched like `_series_meta_for_practices` (practices/service.py:372). Zod-hot: practices/service.py (E3).
- **E15** mirror `onboarding_completed` → `master_onboarding_completed` on `UserResponse` + accept on PATCH-self (users/, credentials JSONB, service.py:45 frozenset). Zod-hot: users/ (E8).
- **E3a** add `Practice.status != PracticeStatus.DELETED.value` to the occurrence-count filter (practices/service.py:427) — soft-deleted occurrences currently inflate `total_sessions`. Zod-hot: E3 engine.

## A) EPICS

Each epic states **(a) why · (b) screens · (c) what breaks · (d) backend state**, plus a
**STATUS (2026-06-24)** line.

### E1 — Non-anonymous feedback (de-anonymise reviews). **P0.**
- **(a) Why.** Three master-facing screens must show *who* left a review and *what they wrote*; the
  insights endpoint is deliberately anonymous — de-anonymisation is a conscious new contract.
- **(b) Screens (3, ONE endpoint).** Master analytics → «Требуют внимания»; per-practice
  `PracticeReviewsView`; master past-practice detail → «Отзывы участников».
- **(c) Breaks.** All three sections rendered empty (numeric counts were real, named reviews missing).
- **(d) Backend.** `GET /practices/{id}/insights` is anonymous; no named-reviews endpoint existed.
- **Request.** NEW `GET /practices/{id}/reviews` → `{ reviewer_name, avatar, rating, comment,
  created_at }` + an attention filter (negative items only) so it serves both the per-practice list and
  the dashboard "needs attention" feed.
- **STATUS (2026-06-24): DELIVERED** — `GET /practices/{id}/reviews` → `PaginatedReviewsResponse`
  (gen:663), `ReviewItem` (gen:922), `getPracticeReviews` practices.ts:170. The **cross-practice**
  needs-attention feed (the former internal "#3") is also DELIVERED: `GET /masters/me/reviews` →
  `PaginatedMasterReviewsResponse` (gen:615) with `MasterReviewItem.practice_title` (gen:521).
  **OPEN remainder:** the cross-practice feed has **no negative-only/attention filter param** (only
  limit/offset) — add `attention=true` (or a rating filter) so «Требуют внимания» shows only the
  low-rated. **Also OPEN: `MasterReviewItem` (gen:521) / `ReviewItem` (gen:922) carry no `user_id`** —
  the reviewer is name-only, so a review card cannot navigate to that student's profile. Add a reviewer
  `user_id` to the review item so the frontend can link a review → student profile. *(The per-practice
  `attention` filter EXISTS on the backend — test-verified — but the frontend wrapper doesn't pass it;
  that side is frontend-wiring, see section D.)*

### E2 — Income / ledger + transactions. **P0.**
- **(a) Why.** Income earned over a period + a transactions list. Balance ≠ income.
- **(b) Screens.** Master income (period-scoped) + transactions list. **Reused by** admin revenue (E9).
  *(Frontend-coordination: income/transactions are consumed by `AnalyticsView`, not `MasterFinanceView`
  — Finance = payout/withdrawal only.)*
- **(c) Breaks.** Income rendered «—»; transactions list empty.
- **(d) Backend.** Balance fields existed; no income/transaction API.
- **Requests.** NEW `GET /masters/me/income?period=week|month`; NEW `GET /masters/me/transactions`.
- **STATUS (2026-06-24): DELIVERED** — `IncomeResponse` (gen:442, `getIncome` masters.ts:145);
  `MasterTransactionItem` (gen:536) + `PaginatedTransactionsResponse` (gen:679, `getTransactions` :154).
- **⟳ ENRICHED 2026-06-25 (transaction title = practice name — recon item C).** The transactions list
  (AnalyticsView) shows a generic `MasterTransactionItem.title` («Оплата за практику» / «Комиссия»)
  because `MasterTransactionItem` (gen:536 = `title` / `created_at` / `counterparty_name` /
  `amount_cents`) carries **no practice reference** — no `practice_title` / `practice_id` exists on it
  (verified, grep: `practice_title` is absent app-wide). Operator wants the PRACTICE NAME on sale/refund
  rows. Add `practice_title` (and/or `practice_id`) to `MasterTransactionItem` for sale/refund rows so
  the list shows which practice the payment was for; commission / platform-side rows have no practice
  and keep «Комиссия». The frontend will then render `practice_title` when present, falling back to
  `title`. **P1.**

### E3 — Recurrence / series engine. **P1.**
- **(a) Why.** Create/Edit lets a master configure a repeating practice; `series` was a label only.
- **(b) Screens.** Master Create/Edit → «Повторение»; practices list (weekday line + "N of M left");
  WI-B cancel-scope.
- **(c) Breaks.** Recurrence period/weekdays/end/count were captured-only (not sent); cancel had no scope.
- **(d) Backend.** `series` tag persisted; no recurrence model; cancel had no scope.
- **Requests.** EXTEND `POST/PATCH /practices`: `recurrence{period,days_of_week,end,count}` + instance
  generation. EXTEND `POST /practices/{id}/cancel`: `scope`.
- **STATUS (2026-06-24): PARTIAL.** DELIVERED: `RecurrenceSpec` (gen:876),
  `CreatePracticeRequest.recurrence` (gen:350), `CancelPracticeRequest.scope` (gen:253),
  `recurrence_days`/`total_sessions`/`completed_sessions` on `PracticeResponse` (gen:765-767).
  **OPEN:** `UpdatePracticeRequest` (gen:1032) has **no `recurrence`** → `PATCH /practices/{id}` cannot
  edit an existing series' recurrence. Add it + regenerate the affected child instances on edit.
- **⟳ ENRICHED 2026-06-25 (master practice card/list recon — items 1/5/6).** (1) **Daily series renders
  «Регулярная», not «Ежедневно»:** `PracticeResponse` returns `recurrence_days` but **no `period`**, and
  a daily series sends **no days** on create (`CreatePracticeView.buildRecurrence` — "Daily ignores
  days"), so the frontend receives empty `recurrence_days` and cannot distinguish daily from generic.
  Fix — either expose `period` on `PracticeResponse`, OR (zero-FE-change) have the backend populate
  `recurrence_days=[1..7]` for a daily series so the existing `recurrenceDaysLabel()` already renders
  «Ежедневно». (2) **Series occurrences invisible in «Предстоящие»:** the list renders exactly what
  `GET /masters/me/practices` returns; if the engine emits only the parent series row (no per-occurrence
  projection), individual dated occurrences never appear. Need the list to surface generated occurrences.
  (3) **Deleting one occurrence removes the whole series from the list:** cancel has `scope` (gen:253,
  DELIVERED) but DELETE has none. Define a delete scope (this-occurrence vs whole-series) mirroring
  cancel, so removing one date does not kill the series.
- **⟳ ENRICHED 2026-06-26 (seed-phase recon — series occurrence-count metadata).** The "N of M left"
  count query (`service.py:427`) filters `status != CANCELLED` but **not** `status != DELETED`, so a
  soft-deleted draft occurrence is still counted in the series total. Minor metadata skew only — **never a
  data wipe** (confirmed by code read: `delete_practice` is draft-only + single-row soft-delete + no cascade;
  `cancel_practice` is correctly series-scoped via `root_expr==root_id ∧ scheduled_at>=primary`). Fix: add
  `Practice.status != PracticeStatus.DELETED.value` to the count filter. **P3 (cosmetic).**

### E4 — Messaging module. **P1.**
- **(a) Why.** Real one-to-one messaging across all zones (list, thread, send, unread). No conversation/
  message entity exists; `master_messages`/`support_messages` are notification toggles, not a store.
- **(b) Screens (one module).** Master Messages/Chat; students «Написать сообщение»; check-in bubbles;
  hub «Сообщения N»; admin → user; **user → master «Вопрос мастеру»** (public profile + booking-confirmed);
  the support thread (see E11).
- **(c) Breaks.** Sample data everywhere; every send raises «недоступно»; unread stubbed to 0.
- **(d) Backend.** No conversation/message entity.
- **Requests.** NEW `GET /conversations`; `GET/POST /conversations/{id}/messages`;
  `GET /conversations/unread-total`. Decide: is «Поддержка VELΘ» a real thread or a separate channel?
  Persist the user's «запрос мастеру» (today `TD-ASK-MASTER`, not persisted) + add a `request` field to
  the check-in item (the 4 check-in/request states).
- **STATUS (2026-06-24): OPEN** — no conversation/message DTO or endpoint exists.
- **⟳ ENRICHED 2026-06-25 (master student-profile request-states — ex «item-3», precise contract).** The «запрос мастеру» must also surface on the MASTER's student profile (`MasterStudentProfileView`), not only as a chat thread. Verified now against `generated.ts`: (1) **No ask-master endpoint exists** — `BookingConfirmedView.onSendRequest` only fires a toast and **discards** the text (`TD-ASK-MASTER`); nothing is persisted. Need: persist it as **ONE request per booking, attached to that practice**, created from the booking-confirmed flow. (2) **The master cannot render it** — `StudentDetailResponse` (gen:966) / `StudentCheckinItem` (gen:959 = `{mood, comment, created_at}`) carry **no request field and no practice link**. Need the student-profile recent items to be **practice-keyed** so one row can carry check-in AND/OR request — e.g. add `request_text` + `practice_id` to `StudentCheckinItem`, or a parallel `recent_requests[]` on `StudentDetailResponse`. (3) Add the reviewer/student **`user_id`** (same gap as E1 gen:521/922 + E6) so a profile row can navigate to the student. **Frontend status:** until this lands, `MasterStudentProfileView` renders the **check-in state only** (real data); the request states are **deferred, not faked** (with the data contract undefined we render the real state, spec the contract here, and defer the dependent states rather than invent a shape or wire a POST to a non-existent endpoint).
- **⟳ 2026-06-30 (user «Сообщения» entry built — honest stub).** Profile ▸ «Аккаунт» now has a «Сообщения» row → `UserMessagesView` (route `user-messages`), an honest **empty-state** («Здесь появятся ваши переписки с мастерами» / «Функция в разработке») — **no fake threads**, no chat route, no send box. It is the swap point for the real conversations list once `GET /conversations` (above) lands; the profile-row unread badge stays OFF until `GET /conversations/unread-total` exists. **Known cleanup (deferred, F2=А):** `MasterMessagesView` / `MasterChatView` still render hardcoded fake conversations (pre-existing seed-only stub) — convert them to real data / honest empty-state when the API lands.

### E5 — Students / CRM aggregate. **P0.**
- **(a) Why.** "A master's students" — people who book/attend, aggregated per person.
- **(b) Screens.** Master dashboard → «Мои ученики»; `MasterStudentsView`; `MasterStudentProfileView`.
- **(c) Breaks.** Stubs; tap = «недоступно»; client-side search over a stub list.
- **(d) Backend.** No students aggregate.
- **Requests.** NEW `GET /masters/me/students`; NEW `GET /masters/me/students/{id}`.
- **STATUS (2026-06-24): DELIVERED** — `PaginatedStudentsResponse` (gen:671),
  `StudentListItem`(+needs_attention) (gen:984), `StudentDetailResponse` (gen:966); `getStudents`/
  `getStudent` masters.ts:120/130.

### E6 — Weekly AI summary (master + user). **P2.**
- **(a) Why.** A weekly personalised summary (insight + key feedbacks + who needs attention). The
  existing AI summary is per-practice and mock.
- **(b) Screens.** Master dashboard → «Саммари» + `MasterSummaryView`; user → «Подробнее» + `AiSummaryView`.
- **(c) Breaks.** Placeholder over no data.
- **(d) Backend.** `GET /practices/{id}/ai-summary` is mock + per-practice.
- **Requests.** NEW `GET /masters/me/weekly-summary`; NEW `GET /users/me/weekly-summary`. Each
  `key_feedbacks[]` / `needs_attention[]` item must carry a `student_id` (not just a name) so the
  summary cards can navigate to the student profile (`MasterSummaryView`).
- **STATUS (2026-06-24): OPEN** — only the per-practice `AISummaryResponse` (gen:33) exists; no
  weekly-summary endpoint. *(Frontend now renders «Требуют внимания» from the real `getStudents`
  feed + navigates; «Ключевые отзывы» stays non-navigable until a `student_id` / reviewer `user_id`
  lands — see E1.)*

### E7 — Period-scoped stats + deltas. **P1.**
- **(a) Why.** Master + admin dashboards show stat cards with a Неделя/Месяц toggle + a delta vs the
  previous period.
- **(b) Screens.** Master dashboard (cards + toggle), master analytics, admin dashboard.
- **(c) Breaks.** Master: only practices total real; participants/income/deltas stubbed. Admin: deltas/
  revenue/rates «—».
- **(d) Backend.** `AdminStatsResponse` was 4 bare counters; no master stats endpoint.
- **Requests.** EXTEND `GET /admin/stats` (deltas/revenue/rates/period); NEW `GET /masters/me/stats?period`.
- **STATUS (2026-06-24): DELIVERED** — master `MasterStatsResponse`(+deltas) (gen:526,
  `getMasterStats(period)` masters.ts:171); admin `AdminStatsOverviewResponse`(deltas/revenue/rates/
  period) (gen:113) + `/admin/metrics/{check-in,feedback,return}` + `AdminRevenueResponse` (gen:97).

### E8 — Notifications: contract + delivery. **P1 (contract) / P2 (delivery).**
- **(a) Why.** The master notifications screen exposes 9 types + a delivery schedule, but the contract
  carries only the four user keys. Push delivery itself is also unwired.
- **(b) Screens.** `MasterNotificationsView` (local-only); user `NotificationsView`; the dashboard bells.
- **(c) Breaks.** The master screen holds all state locally + does not persist; the bell has no feed.
- **(d) Backend.** `NotificationSettings`/`…Update` = exactly four keys (gen:551). No unread-feed.
- **Requests.** EXTEND with `new_booking, booking_cancelled, reminder, new_checkin, new_feedback,
  msg_participants, msg_support, ai_summary, monthly_report` + a `schedule{from,to,days}`; NEW push
  delivery + quiet-hours scheduler; NEW unread-feed for the bell.
- **STATUS (2026-06-28): PARTIAL ⬆ (was OPEN).** **DELIVERED:** the full master-notifications contract —
  `MasterNotificationSettings` (gen:486, 9 toggles) + `MasterNotificationSettingsUpdate` (gen:500) +
  `NotificationSchedule` (gen:579, `from_`/to/days) + `master_notifications` on `UserResponse` (gen:1118)
  & `UserUpdate` (gen:1138), persisted under credentials, gated by master **capability** (not role) incl.
  PATCH/POST (commits `7df02e7`/`e9fabb7`/`74ee56c`). User `NotificationSettings` correctly still 4 keys
  (gen:593). **OPEN:** push-delivery worker + quiet-hours scheduler runtime; unread bell-feed (no feed DTO).

### E9 — Admin oversight endpoints. **P0 (data) / P1 (rich).**
- **(a) Why.** The admin role is built to the design; most admin lists/details have no endpoint or a
  minimal one lacking the rich fields.
- **(b) Screens.** All admin screens.
- **(c) Breaks.** Lists honest-empty; rich fields «—»; withdrawal hero shows holder/«—»; 2FA is UI-only.
- **(d) Backend.** Mix of EXTEND + NEW (per item).
- **Requests.** EXTEND `/admin/masters/list`+`/{id}` (rich + application profile + docs[] + history +
  edit-fields + doc view/download; verify/reject already real); EXTEND `/admin/reports` (category/
  priority/date/reporter_name); EXTEND `/admin/users` (participants rich + filters); EXTEND
  `AdminWithdrawalResponse` (+master_display_name) + NEW real 2FA; NEW `/admin/metrics/*`; NEW
  `/admin/revenue`; NEW `/admin/practices`(+/{id}).
- **STATUS (2026-06-24): PARTIAL.** DELIVERED: `/admin/practices`(+/{id}) (gen:567/59), `/admin/revenue`
  (gen:97), `/admin/metrics/*`, verify/reject. **OPEN:** reports category/priority/reporter_name
  (`ReportResponse` gen:895 = reporter_id + status/target_type filters only); masters `/{id}` rich
  application profile + `documents[]` (returns minimal `AdminMasterListItem` gen:47) + edit-master-fields;
  `AdminWithdrawalResponse` (gen:141) `master_display_name` + real 2FA; participants rich fields + filters.

### E10 — Promo module (verify-only). **P2.**
- **(a) Why.** Mostly already built; flagged so the small gap (a master's own list + delete) is closed.
- **(b) Screens.** `MasterPromocodesView` / `MasterNewPromocodeView`.
- **(c) Breaks.** Sample data + stubbed taps (frontend wrappers unwritten).
- **(d) Backend.** POST promos + `PaginatedPromosResponse` + `promo_code` on booking exist.
- **Request.** ADD `GET /masters/me/promos` (list) + `DELETE /masters/me/promos/{id}`.
- **STATUS (2026-07-01): DELIVERED + FRONTEND-WIRED (batch №227).** `POST` + **`GET /masters/me/promos`**
  (list_my_promos, router.py:72) + **`PATCH /masters/me/promos/{id}/deactivate`** (router.py:88) all exist;
  frontend wired (`api/promos.ts`, `MasterPromocodesView` active-list + soft-deactivate). A hard `DELETE`
  was NOT added (PATCH-deactivate covers it) — reopen only if a real hard-delete need surfaces.

### E11 — One-offs.
- NEW master-side `DELETE` of a participant's booking (refund + notify) — `cancelBooking` is self-only. **P1.**
- NEW support-ticket intake `{ topic, message, attachments[] }` + upload (max 5 / 5 MB, server-side). **P1.**
- NEW connection-link auto-generation + delivery (~10 min pre-start). **P2.**
- NEW `DELETE /masters/me/payout` — only `PATCH` exists. **P2.** *(⟳ confirmed 2026-06-25, recon item #2 — `removePayout` is a stub toast «Удаление способа выплаты появится позже»; no delete endpoint, frontend does not fake a removal.)*
- NEW **card payout method** (card storage + one-time payout) — `savePayout` stubs `method==='card'` → toast «Выплата по номеру карты появится позже»; bank_transfer / PayPal / Revolut **already persist** via `PATCH /masters/me/payout`. So "doesn't save the card" = the card method only. ⟳ recon item #3 (2026-06-25). **P2.**
- EXTEND real account deletion + balance forfeiture. **P2.**
- EXTEND `UserResponse.email` (capture + expose). **P1.**
- **Master-application → profile data exposure (⟳ recon 2026-06-25, EditProfile).** (a) **`methods`** — onboarding
  captures the master's `methods` and the profile response carries a `methods?` field; the frontend renders
  locked method-chips gated on `profile.methods.length > 0` → VERIFY the backend COPIES the application's
  `methods` onto the profile, else the chips never render (recon item E2). (b) **application PHOTO** — there is
  **NO** `photo` / `photo_url` field anywhere in the contract (verified, grep); the profile avatar falls back to
  the Telegram `avatar_url`. To show an onboarding-captured photo, the application must capture + store a photo and
  expose it on the profile — contract undefined → define + spec (frontend defers, does not invent). **P2** (recon item E3).
- NEW i18n EN catalog + language render layer + date-format pref + formatter. **P2.**
- EXTEND `PracticeResponse` per-card `{ attended, no_show }` aggregate. **P2.**
- **STATUS (2026-06-24): PARTIAL.** DELIVERED: real `DELETE /users/me` (forfeit) — users.ts:50.
  **OPEN:** master-delete-participant booking; support-ticket intake + upload; connection-link;
  `DELETE /masters/me/payout` (only PATCH); `UserResponse.email` (gen:1059 has none); per-card
  `{attended,no_show}` aggregate (data on `AttendanceResponse` gen:181); i18n EN (partly frontend).

### E12 — Check-in count aggregate (NEW post-audit). **P1.**
- **(a) Why.** Dashboard + practice cards show a «😊 N/M» check-in indicator.
- **(b) Screens.** Master dashboard cards; practice list/detail cards.
- **(c) Breaks.** No data source → the indicator can't render.
- **(d) Backend.** `checkin_count` is **absent** on `PracticeResponse` (gen:740) AND `PracticeSummary`
  (gen:775).
- **Request.** ADD `checkin_count` to the practice/list aggregate (groups with `recurrence_days` /
  `total_sessions` / `completed_sessions`, E3).
- **STATUS (2026-06-24): OPEN.**

### E13 — Master-application document upload (NEW post-audit). **P2.**
- **(a) Why.** The master-application flow shows document tiles, but there is no upload.
- **(b) Screens.** `MasterApplyView` (intake) + admin master-review (view/download — ties to E9 docs[]).
- **(c) Breaks.** `MasterApplyView` renders static placeholder tiles and always sends `documents: []`;
  no file input, no upload endpoint.
- **(d) Backend.** `MasterApplyRequest.documents` (gen:475) is a freeform JSON array in the apply body
  — no file-upload intake / storage. Ties to support-upload (E11) / E4 attachments.
- **Request.** NEW document upload intake + storage; surface on the admin master-review (E9 docs[]).
- **EXTEND (slice-2 2026-06-27):** the redesigned Step-3 also adds a **profile photo** (public) upload
  — no `photo_url` on `MasterProfileResponse` (gen:486). Build the UI (drop-zone + uploaded-chip),
  tap = honest «недоступно» until storage ships. Add `photo_url` intake on apply + surface on profile.
- **STATUS (2026-06-24): OPEN.**

### E14 — Master-application rejection reason, surfaced (NEW post-audit). **P2.**
- **(a) Why.** A rejected applicant should see *why* (`MasterPendingView` shows a hardcoded «Причина: …»).
- **(b) Screens.** `MasterPendingView`.
- **(c) Breaks.** No `rejection_reason` on any DTO the applicant can read.
- **(d) Backend.** `RejectMasterRequest.reason` (gen:885) is admin **input** only; it is **not exposed**
  on `MasterProfileResponse` (gen:486) / `MasterApplyResponse`.
- **Request.** Surface `rejection_reason` on the applicant-readable profile/apply response.
- **EXTEND (slice-2 2026-06-27):** the redesigned «Отказ» screen renders the specific reason + keeps a
  «Подать новую заявку» path (operator fork-4=Б). Confirm a rejected applicant's role/status keeps the
  rejected screen REACHABLE and the re-apply path allowed after rejection.
- **STATUS (2026-07-01): SELF-FIXED (batch №227) — see SELF-FIX LOG.** `rejection_reason` projected onto
  `MasterProfileResponse` from `data.account.rejection_reason`; `MasterPendingView` renders the real reason.

### E15 — Master-onboarding "completed" flag (NEW 2026-06-26). **P2.**
- **(a) Why.** A freshly-verified master currently lands straight on `MasterDashboardView` with no intro.
  We are building a one-time master-onboarding carousel (clone of the user `OnboardingView` pattern). It
  must show ONCE, cross-device — so it needs its OWN persisted flag, distinct from `onboarding_completed`
  (which is already `true` by the time a user becomes a master, so it cannot be reused).
- **(b) Screens.** new master `OnboardingView` (master-flavored), gated in `App.vue`/router on first
  master-dashboard entry after verification.
- **(c) Breaks.** No `master_onboarding_completed` field exists on `UserResponse` (gen:1072 has only
  `onboarding_completed`), and the PATCH-self endpoint does not accept/persist it. Frontend is built
  defensively (absent field → treat as not-completed → show once); persistence + gate go live on delivery.
- **(d) Backend.** Mirror the existing `onboarding_completed`: add `master_onboarding_completed: boolean`
  to `UserResponse`; accept `{ master_onboarding_completed: true }` on the user self-update PATCH (same
  path the user carousel uses to persist `{ timezone, onboarding_completed: true }`); store in the same
  credentials JSONB.
- **Request.** Add the field to `UserResponse` + accept it on PATCH-self, mirroring `onboarding_completed`.
- **STATUS (2026-06-26): OPEN.** (Frontend built against it under build-full-design; deploy gate with the batch.)

### E16 — Master-application "languages" field (NEW slice-2 2026-06-27). **P2.**
- **(a) Why.** The redesigned Step-2 «Опыт» adds a «Язык проведения практик» control (Русский /
  English). Operator fork-3=А: build the full UI now, persist later.
- **(b) Screens.** `MasterApplyView` step 2; later the public/admin master profile.
- **(c) Breaks.** `MasterApplyExperience` / `MasterApplyRequest` (gen:472) has no `languages` field;
  `MasterProfileResponse` (gen:486) has no `languages`. The control persists nothing until added.
- **Request.** Add `languages: string[]` to the apply experience intake + surface on the profile.
- **STATUS (2026-06-27): OPEN.** (Frontend stub built under build-full-design.)

### E17 — Master web auth (Phase A) (NEW slice-3 2026-06-27). **P3 (future web build).**
- **(a) Why.** The Figma Phase A is a standalone WEB master portal: Landing / Login (email+password) /
  Recover-password (request + set-new). The Telegram Mini App authenticates via `initData` and has NO
  password concept, so Phase A has no place in the Telegram flow. Built now as PARKED, INERT screens
  (unlinked `/auth/*` routes, no fake auth) so they exist in the project and wait for the web build.
- **(b) Screens.** new `views/auth/{Landing,Login,RecoverPasswordRequest,RecoverPasswordSet}View.vue`.
- **(c) Breaks.** No email/password auth surface exists: no register/login-by-password endpoint, no
  password hashing/sessions, no password-reset email flow. The current only auth is `/auth/telegram`
  (initData). The parked screens render fields but submit is a no-op / «недоступно».
- **Request.** When the standalone web build is real: email/password registration + login + session +
  password-reset email. Wire the parked `/auth/*` screens to it. Entirely a future web-build concern.
- **STATUS (2026-06-27): OPEN — PARKED.** (Frontend inert screens built; not wired; no Telegram impact.)

### E18 — Zoom link on `PracticeSummary` (NEW 2026-07-01). **P2.**
- **(a) Why.** The user «Ближайшая практика» (dashboard) + «Мои бронирования» booking cards have a Zoom
  button. The booking object (`BookingWithPracticeResponse.practice`) embeds a `PracticeSummary`, which
  has NO `zoom_link` — so the button cannot open the meeting without a second round-trip.
- **(b) Screens.** `UserDashboardView` (Zoom button); `MyBookingsView` / booking cards.
- **(c) Breaks.** `UserDashboardView.onZoomClick` is an honest stub (toast «Ссылка появится ближе к
  началу») — we deliberately do NOT fire a per-click `GET /practices/{id}` just to read the link. (The
  in-session `PracticeLiveView` already opens the real link — it fetches the full `PracticeResponse`.)
- **(d) Backend.** `zoom_link` exists on `PracticeResponse` (gen:799) but is **absent** on
  `PracticeSummary` (gen:775 — the same object that lacks `checkin_count`, E12).
- **Request.** ADD `zoom_link` to `PracticeSummary` so booking cards can open Zoom without a separate GET;
  then wire `platform.openLink(...)` on the user dashboard (master screens already open it via the full
  `PracticeResponse`).
- **STATUS (2026-07-01): SELF-FIXED (batch №227) — see SELF-FIX LOG.** `zoom_link` added to `PracticeSummary` (from_attributes, no migration) + `generated.ts` + Zoom wired. No Zod action.

---

## B) PER-ENDPOINT TABLE (with STATUS)

| Endpoint (method + path) | NEW/EXTEND | Fields | Prio | Status (2026-06-24) |
|---|---|---|---|---|
| GET /practices/{id}/reviews | NEW | reviewer_name, avatar, rating, comment, date; attention | P0 | DELIVERED (gen:663) |
| GET /masters/me/reviews (cross-practice feed) | NEW | + practice_title; attention filter | P1 | PARTIAL — feed done (gen:615), attention param OPEN |
| GET /masters/me/income?period | NEW | income_cents, delta | P0 | DELIVERED (gen:442) |
| GET /masters/me/transactions | NEW | title, date, counterparty, amount (signed) | P0 | DELIVERED (gen:536/679) |
| GET /masters/me/students (+/{id}) | NEW | name, avatar, counts, checkins[], feedbacks[] | P0 | DELIVERED (gen:671/966) |
| GET /masters/me/stats?period | NEW | practices, participants, income + deltas | P1 | DELIVERED (gen:526) |
| GET /masters/me/weekly-summary | NEW | insight, key_feedbacks[], needs_attention[] | P2 | OPEN |
| GET /users/me/weekly-summary | NEW | insight, … | P2 | OPEN |
| POST /practices (recurrence) | EXTEND | recurrence{…} + generation | P1 | DELIVERED (gen:350/876) |
| PATCH /practices/{id} (recurrence) | EXTEND | add recurrence to UpdatePracticeRequest + regen | P1 | OPEN (gen:1032 lacks it) |
| POST /practices/{id}/cancel (scope) | EXTEND | scope: this \| this_and_future | P1 | DELIVERED (gen:253) |
| GET /conversations (+messages, POST, unread) | NEW | peer, preview, time, unread, messages[] | P1 | OPEN |
| NotificationSettings (+Update) | EXTEND | +9 keys + schedule{from,to,days} | P1 | OPEN (still 4 keys, gen:551) |
| push delivery + quiet-hours | NEW | scheduler honours window / days | P2 | OPEN |
| notifications unread-feed | NEW | bell feed + badge | P1 | OPEN |
| GET /admin/stats | EXTEND | deltas, revenue, rates, pending, period | P1 | DELIVERED (gen:113) |
| GET /admin/masters/list + /{id} | EXTEND | rich + application profile + docs[] + history[] | P1 | OPEN (minimal, gen:47) |
| admin edit-master-fields | NEW | save Направление / Вид | P2 | OPEN |
| GET /admin/reports | EXTEND | category, priority, date, reporter_name | P1 | OPEN (gen:895 reporter_id only) |
| GET /admin/users (participants) | EXTEND | practices_attended, last_active, joined, filters | P1 | OPEN |
| AdminWithdrawalResponse + 2FA | EXTEND + NEW | master_display_name; real 2FA step | P2 | OPEN (gen:141) |
| GET /admin/metrics/check-in\|feedback\|return | NEW | rate, totals, series, low/distribution/top | P0 | DELIVERED |
| GET /admin/revenue | NEW | revenue, commission, payable, per-master (= E2) | P0 | DELIVERED (gen:97) |
| GET /admin/practices (+/{id}) | NEW | global list + detail + roster | P0 | DELIVERED (gen:567/59) |
| GET /masters/me/promos + DELETE | NEW | list; delete | P2 | OPEN (POST exists gen:320) |
| DELETE participant's booking (master) | NEW | refund + notify | P1 | OPEN |
| POST support ticket + upload | NEW | topic, message, attachments[] | P1 | OPEN |
| connection-link auto-gen | NEW | link generation + delivery | P2 | OPEN |
| DELETE /masters/me/payout | NEW | remove payout method | P2 | OPEN |
| DELETE /users/me (real) | EXTEND | forfeit balance + erase semantics | P2 | DELIVERED (users.ts:50) |
| UserResponse.email | EXTEND | email capture + expose | P1 | OPEN (gen:1059) |
| i18n EN + date-format pref | NEW | locale catalog + format pref + formatter | P2 | OPEN |
| PracticeResponse {attended, no_show} | EXTEND | per-practice card aggregate | P2 | OPEN |
| PracticeResponse.checkin_count (E12) | EXTEND | «😊 N/M» aggregate | P1 | OPEN (gen:740/775) |
| apply document-upload (E13) | NEW | file intake + storage | P2 | OPEN |
| application rejection_reason — expose (E14) | EXTEND | surface on profile/apply response | P2 | OPEN (gen:885 input only) |

---

## C) CROSS-ZONE DEDUP NOTES

- **E1** = ONE endpoint serving three master screens. The cross-practice needs-attention feed is the
  same E1 work (do not build a separate "#3").
- **E2 (income/ledger) ≡ E9 admin revenue** — same ledger layer. *(Both DELIVERED.)*
- **E4 (messaging)** = ONE module: master ↔ participant + admin → user + user → master + support thread.
- **E7 (period stats)** — master `/masters/me/stats` and admin `/admin/stats` = the same period-summary
  contract. *(Both DELIVERED.)*
- **email** — on the apply profile; two exposure points: `UserResponse` (E11) + admin master-review (E9).
- **connection-link** — master Create «Подключение» + user dashboard "Zoom недоступен" = same backend.
- **documents** — E13 upload intake feeds the E9 admin master-review `documents[]` view/download.

## D) NOT A ZOD TASK (frontend-only — do NOT build)

- **E1 per-practice `attention` filter — frontend-wiring, not backend.** The backend filter EXISTS on
  `GET /practices/{id}/reviews` (test-verified, `test_reviews_attention_filter` passes); the frontend
  wrapper `getPracticeReviews` (practices.ts) just doesn't pass it. Do NOT rebuild it. *(The genuine
  backend gap is the cross-practice **filter param** on `/masters/me/reviews` — see E1 STATUS.)*
- **Promo wiring** — the backend POST/list DTOs exist (E10); the `api/promos.ts` GET/DELETE wrappers +
  view connection are frontend. Only the GET-list / DELETE endpoints (E10) are a small Zod add.
- **E2 income attribution** — income/transactions are consumed by `AnalyticsView`, NOT
  `MasterFinanceView` (Finance = payout/withdrawal). Frontend-coordination note, no backend change.
- **Currency ₽ / €, SHELL debts, standalone top-up entry, withdrawal «Выплаты» list (option Б over the
  existing `GET /admin/withdrawals`)** — frontend / operator product decisions, no new backend.

---

## Delivered OUTSIDE the E-epic set (not E-numbered — recorded for coordination)

- **Auto-complete practice by duration (prod-critical lifecycle worker) — DELIVERED.** The backend
  autofinalize worker transitions `scheduled`/`live` → `completed` on `scheduled_at + duration`,
  resolves attendance, and releases frozen funds (autofinalize.py present + enabled). Not in
  `generated.ts` because it is a worker, not an endpoint. *(Was a round-2/3 prod-critical add, not an
  original epic.)*
  - **⟳ VERIFY 2026-06-25 (recon item 4).** On TEST a past-dated practice (e.g. 16 июня, today the 19th)
    still shows `scheduled` and stays in the master's «Предстоящие» (the list filters by status only, no
    date guard; «Прошедшие» is `completed`-only). Since the worker is DELIVERED, this is likely either
    the autofinalize worker not enabled/running on TEST, or a seed artifact (a practice seeded as
    `scheduled` with a past `scheduled_at`, which the worker may not retroactively finalize). Please
    verify the worker is enabled on TEST and finalizes already-past practices (or fix the seed). Per the
    environment note above this may be a seed/env gap, not a contract gap — the frontend deliberately
    ships no hack that would hide a non-completed practice from both tabs.
- **#1 (self-fix, NOT Zod):** `StudentDetailResponse.name` + `avatar_url` added (deployed).
- **#2 (self-fix, NOT Zod):** `test_admin_metrics.py` made seed-tolerant (test-isolation, not a contract
  bug). Optional Zod follow-up: harden `conftest` isolation (transactional rollback / clean DB).

---

**Summary (actualized 2026-06-28 vs live `origin/test=4713c60`).** Epics E1–E11 + new E12–E17. Of E1–E11:
E1/E2/E5/E7 DELIVERED; E9 core delivered (rich remainder open); E3/E8/E10/E11 PARTIAL; E4/E6 OPEN.
E12–E17 OPEN (E17 PARKED — master web-auth, future web build). **Only delta since 2026-06-24: E8 OPEN →
PARTIAL** (master-notifications contract + capability gate delivered; push/feed open). No regression.
Auto-complete-by-duration + W-6/W-7 (user dashboard) delivered outside the epic set. This is the current
state to hand to Zod against his own numbering.
