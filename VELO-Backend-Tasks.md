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
  **E11** (real `DELETE /users/me` + `UserResponse.email` done №280; rest open) · **E1** (cross-practice needs-attention *filter* DONE №280).
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
- **E1 (increment)** `user_id` on `MasterReviewItem` + diary `ReviewItem` — projected from the joined `User`; per-practice review cards (`PracticeReviewsView`) navigate to the student profile. *(Attention-filter DONE №280: `getMasterReviews(…, attention)` + AnalyticsView «Требуют внимания» fetches `attention=true`; the backend param was already deployed. AnalyticsView attention card left on its existing message action pending operator UX call.)*
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
  **CORRECTION (2026-07-04, ПРОМТ №280): the attention param was STALE-OPEN — it already ships.**
  `GET /masters/me/reviews?attention=true` narrows to the negative (confused) bucket server-side
  (`reviews_router.py` `attention: bool = Query`, `reviews_service.list_master_reviews`,
  `Feedback.rating <= ATTENTION_RATING_MAX`) and is LIVE on origin/test. E1-attention = **frontend
  wiring, now DONE**: `getMasterReviews(..., attention)` passes it; `AnalyticsView` «Требуют внимания»
  fetches `attention=true`. **Also OPEN: `MasterReviewItem` (gen:521) / `ReviewItem` (gen:922) carry no `user_id`** —
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
- **STATUS (2026-07-04, email SELF-BUILT — PACK#3, ПРОМТ №280):** `UserResponse.email` capture+expose
  is DONE, additive credentials-JSONB (phone/bio pattern, NO column, NO migration): `"email"` added to
  `_JSONB_CREDENTIAL_FIELDS`, `UserResponse.email` computed_field, `UserUpdate.email` (soft
  email-validator; "" clears). `EditProfileView` email field enabled. Regenerated generated.ts.
  **ZOD HEADS-UP (Q1=А collision note):** Velo orc self-built this in `users/` (Zod's nominal E8 lane).
  It is **additive only** (one credentials key + one response field + one PATCH field) — no schema/
  column/migration, no conflict with E8's `master_notifications`. users/ was re-checked remote-cold at
  build (origin/main 0-ahead vs test, no in-flight users/ push). Reconcile-before-push still mandatory
  at deploy. The OTHER E11 one-offs below remain OPEN.
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
- **STATUS (2026-07-04): SELF-BUILT (PACK#3, ПРОМТ №280).** Additive JSONB `data.profile.languages`
  (mirror `methods`, NO migration): `MasterApplyExperience.languages` (default []) + on
  `MasterProfileResponse`; apply UI wired (`langRu`/`langEn` → experience.languages). Q2=А: FREELY
  editable on the profile (no moderation) via new `PATCH /api/v1/masters/me/languages` +
  `EditProfileView` languages chips. Regenerated generated.ts. HELD (accumulate-then-deploy).

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

### E19 — Master methods change-request workflow (NEW 2026-07-01, operator PE-3). **P2.**
- **(a) Why.** On the master «Редактировать профиль» screen the operator wants the onboarding methods shown,
  LOCKED, and changeable only via an admin-approved request. The operator's mockup (PE-3, image 2 — the
  design spec) shows a **two-level taxonomy** «Направление» (direction, e.g. Йога) → «Вид» (kind, e.g.
  Хатха) per method, each editable via a pencil → inline edit → auto-submitted change request → a
  **«Ожидает подтверждения»** (pending) badge until an admin approves, with the note «Изменение направления
  или вида практики требует подтверждения администратора. Запрос отправляется автоматически. Обработка
  запроса обычно занимает не более 3 рабочих дней.»
- **(b) Screens.** `EditProfileView` (master variant) methods block; an admin approve/reject surface.
- **(c) Breaks.** The current data is a **flat `string[]`** — `MasterProfileResponse.methods` (fed from the
  apply `AVAILABLE_METHODS`, e.g. "Йога","Медитация"). There is NO Направление→Вид (direction→kind) pairing,
  NO method-change-request entity, NO pending/approval status. None of the mockup's structure or workflow
  exists. **Frontend today ships the honest locked flat-chip display** (`EditProfileView` §methods:
  read-only `VChip`s + «Изменить методы можно через поддержку»); it does NOT fake the taxonomy or the
  pending state (no-fake rule).
- **(d) Backend.** Needs: (1) a two-level methods model — each method = { direction, kind } instead of a
  flat string; surface it on `MasterProfileResponse`. (2) A method-change-request endpoint (master submits a
  proposed direction/kind edit). (3) An admin approval/rejection workflow. (4) A per-method **pending**
  status the profile response exposes so the frontend can render «Ожидает подтверждения» until resolved.
- **Request.** Design + build the taxonomy model + change-request + admin-approval + pending status; image 2
  (PE-3) is the visual spec. Then the frontend upgrades the locked flat-chip display into the mockup's
  editable-with-approval rows. Until then the honest locked display stands.
- **STATUS (2026-07-04): SELF-BUILT FLAT (M3, ПРОМТ №278) — two-level taxonomy DEFERRED / out of scope.**
  Operator locked F-M3-1=А (FLAT `string[]`, no direction→kind nesting) after recon surfaced that this E19
  entry contradicted the flat decision. Shipped additively (no migration): JSONB
  `data.profile.method_change_request` + 4 endpoints mirroring the master-application verify/reject loop
  — `POST /masters/me/method-change-request` (master submit), `GET /admin/masters/method-change-requests`
  (admin list-pending), `POST /admin/masters/{id}/method-change-request/approve|reject`. Exposed on
  `MasterProfileResponse.method_change_request` (optional). Frontend: `EditProfileView` master methods block
  upgraded from locked-chips to an editable flat set + «Ожидает подтверждения» pending badge + auto-submit
  note; new admin `AdminMethodRequestsView` moderation screen. The **two-level Направление→Вид taxonomy**
  from the operator's PE-3 mockup (per-method pencil-edit, per-method pending) remains **OPEN / deferred** —
  revisit if the operator re-prioritises the nested design.

---

## B) PER-ENDPOINT TABLE (with STATUS)

| Endpoint (method + path) | NEW/EXTEND | Fields | Prio | Status (2026-06-24) |
|---|---|---|---|---|
| GET /practices/{id}/reviews | NEW | reviewer_name, avatar, rating, comment, date; attention | P0 | DELIVERED (gen:663) |
| GET /masters/me/reviews (cross-practice feed) | NEW | + practice_title; attention filter | P1 | DELIVERED — feed + attention param (gen:615); FE wired №280 (AnalyticsView attention=true) |
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
| UserResponse.email | EXTEND | email capture + expose | P1 | SELF-BUILT №280 (credentials JSONB, no column/migration; UserUpdate.email) |
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

---

## 2026-07-03 — ROLE_SWITCH_ENABLED removed (heads-up for YOUR docs)

**What changed (commit `15d5b0d`, held batch on `d01f6f9`, ПРОМТ №256):** the TEST-only
`ROLE_SWITCH_ENABLED` flag is REMOVED entirely (config field, the 404 router gate on
`POST /users/me/role`, the W-4 startup warning + its test file, and the seeded
`credentials.role_switch.allowed_roles` allow-lists — now ignored). Role-switch security is
capability-derived (`derive_allowed_roles` in `app/modules/users/schemas.py`, single source of
truth for the write path AND the `role_switch` block in `GET /users/me`): USER always ·
+MASTER with a verified MasterProfile · admin keeps all three via a server-written
`credentials.role_switch.home_role` round-trip marker; a non-admin can NEVER switch to admin
(CLI `velo setrole` only). The endpoint is always on; a plain user derives `{USER}` and can do
nothing. `ROLE_SWITCH_ENABLED=False` in the TEST `.env` is inert and can be dropped.

**Stale references left in YOUR docs (we don't edit them — please align on your next pass):**
- `VELO-Backend.md:36` — W-4 summary line («громкий security-WARNING при `role_switch_enabled=True`») — the flag and the warning no longer exist.
- `VELO-Backend.md:1202` — same W-4 warning note.
- `VELO-Backend.md:1244` — «эндпоинт 404 в проде при `role_switch_enabled=False`» — the 404 gate is gone; security = derived policy.
- `VELO-Technical-Specification.md:2726` — W-4 checklist entry.
- `VELO-Technical-Specification.md:3146` — W-4 mention in the hardening summary list.

**Optional one-line follow-up in YOUR `set_role.py`:** demoting an admin (→user/master) while
they are role-switched away leaves a stale `credentials.role_switch.home_role="admin"` marker
(they could self-return to admin via the switch). Clearing the marker in your demote path
closes the edge; operator accepted the edge as-is for now (№257 ruling), so this is optional.

---

## 2026-07-03 — zoom_link exposure matrix: test-debt cells (tied to your E18/M-3/Z-6/Z-7 batch)

Pre-push audit (ПРОМТ №262) mapped `test_zoom_link_visibility.py` onto the full exposure matrix.
The gate itself verified fail-closed (only the two builders set the field). Six cells have NO test —
small additive cases, your file/conventions:

1. `GET /bookings/{id}` — the booking-detail response wipes zoom_link via
   `model_copy(update={"zoom_link": None})` (bookings/router.py:281) — untested.
2. Finalize response — same wipe at bookings/router.py:392-395 — untested.
3. Practice detail for an ATTENDED booking — only CONFIRMED is asserted today
   (test_detail_zoom_link_gated_by_booking); the ATTENDED branch of
   ZOOM_VISIBLE_BOOKING_STATUSES on the DETAIL surface is uncovered.
4. NO_SHOW booking — not asserted on any surface (should be None everywhere).
5. Public catalog list (`GET /practices`) for a user who HAS a confirmed booking —
   the list is unconditionally None even for eligible users (list builder never
   passes visibility); asserting that pins the design.
6. Admin surfaces — zoom_link is structurally absent from all admin serializers
   (grep-verified); one assert would guard against a future admin schema gaining it.

Note: we added the owner-mutation-response cells ourselves in №263
(`test_owner_create_response_shows_zoom_link` / `test_owner_update_response_shows_zoom_link`)
after making the four owner-only CRUD responses in practices/router.py pass
`zoom_link_visible=True` (F1) — consistent with your Z-6 owner-always-sees rule.

---

## 2026-07-03 — U4 no-show reflection: persist endpoint + booking flag (frontend shipped on a stub, ПРОМТ №269)

The User frontend now has a full **no-show reflection** flow, built entirely on a
**stub** (no backend calls). A booking with `status = no_show` («Не состоялась») now shows
a dashboard banner → `/user/reflection/:practiceId` → `ReflectionView` (FormShell, comment
only, NO rating) → submit. The submit path is a client no-op
(`diaryStore.submitReflection`, `TD-REFLECTION`) that resolves ok and dismisses the banner
**client-side for the session only** (`bookingsStore.dismissedReflections`, mirrors the
existing `dismissedCheckins`). Nothing persists yet. Please wire the backend to make it real:

**1. Persist endpoint — mirror the feedback endpoint shape.**
- `POST /api/v1/practices/{practice_id}/reflection` — body `{ "comment": string | null }`
  (NO rating — a no-show reflection does not rate the practice).
- Upsert semantics, one per `(practice, user)`, like feedback.
- **Eligibility (mirror the feedback gate, inverted status):** `booking.status == no_show`,
  within the window `scheduled_at + duration_minutes .. + 72h`
  (`FEEDBACK_WINDOW_H`, identical to feedback — frontend uses `isInFeedbackWindow`).
- Response can mirror `FeedbackResponse` (a `ReflectionResponse` sibling); the frontend does
  not yet read the response body, so its exact shape is your call.
- May project a diary-feed event (like feedback/check-in) — optional; the frontend does not
  depend on it for the stub.

**2. Booking flag — `has_reflection: bool` on `BookingWithPracticeResponse`.**
- Mirror `has_feedback`: `true` once the user has submitted a reflection for that booking.
- This **replaces** the client-only session dismiss. When the field ships, the frontend will
  switch the dashboard `reflectionAlert` computed from `dismissedReflections.includes(...)`
  to `!b.has_reflection` (one-line swap, symmetrical to `feedbackAlert` reading
  `has_feedback`), and `generated.ts` regenerates then (NOT now — the stub adds no types).

**⚠ DEPLOY-GATE WARNING (has burned us before):** adding `has_reflection` to
`BookingWithPracticeResponse` grows the response key-set. **Before** you add the field,
`grep backend/tests` for frozen **exact-key-set** assertions on the bookings serializers
(e.g. `assert set(data.keys()) == {...}`) and update them in the same commit — the local
pre-push gate skips pytest, so a stale key-set only fails at deploy, not locally.

**Frontend wiring already in place (nothing for you to touch there):**
`utils/reflectionVariants.ts` (copy pool, stable per practiceId), `ReflectionView.vue`,
`stores/diary.ts::submitReflection` (the stub to flip to a real `upsertReflection` call),
`stores/bookings.ts::dismissedReflections`, dashboard `reflectionAlert` + banner, route
`user-reflection`. `generated.ts` UNTOUCHED by the frontend batch.
