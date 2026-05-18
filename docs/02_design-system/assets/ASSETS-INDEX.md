# VELO Design System — Assets Index

```
Last updated: 2026-05-18
Iteration:    4 (Sprint 2 Audit — 4 missing FeedbackRating + check-in icons recovered)
Figma file:   F7PD5isLfLdyc0q1Bd5n5c
Status:       ✅ 94 of 97 SACRED screens saved (operator UI export) +
              ✅ 33 DS canon icons saved (Plugin API) +
              📄 1 legacy admin HTML reference saved
              ⏳ 3 user/calendar screens deferred (re-export at operator's discretion)
```

> Per VELO-METHODOLOGY.md §6.5 step 1.3/1.4. Each row records the
> Figma source node ID and the local target file path. Files
> exported at native 1× scale (804×1748 / 804×1752 for 402×874/876
> base frames — this is 2× retina-quality PNG for crisp visual
> reference during mockup review).

---

## Top-level structure (role-organized)

```
02_design-system/assets/
├── backgrounds/              ← Full-screen background plates (added 2026-05-17)
│   └── velo-bg-app.png           (804×1748 RGBA, ~1.5MB) — universal app background
│                                   (from Figma 01_Welcome composition; used on ALL screens)
│
├── icons/                    ← DS canon icons (SVG vector, source from Figma)
│   ├── icon-back-arrow.svg       (23×23 viewBox, 215 bytes) — Figma `423:125` COMPONENT
│   │                               chevron-back, #4C6589 stroke. DS canon survivor.
│   ├── velo-logo-mandala.svg     (492×492 viewBox, ~434KB) — Group 1944 from Figma:
│   │                               large white mandala with embedded "VELO" wordmark.
│   │                               Used as brand logo on welcome (large hero).
│   ├── velo-logo-mandala-blue.svg (153×154 viewBox, ~228KB) — Group 1925 (instance of
│   │                               COMPONENT `916:1662` "Mandala Decor Small Blue").
│   │                               Compact blue mandala (#4C6589) с VELO text внутри.
│   │                               Used в .velo-header-compact на login/register/oauth
│   │                               и в .scr-04 .oauth-logo (callback screen).
│   ├── icon-onb-practice.svg     (163×174 viewBox, ~13KB) — onboarding step 1 icon
│   │                               Group `648:1217` from Figma. Vector, fill #4C6589.
│   ├── icon-onb-diary.svg        (184×174 viewBox, ~6KB)  — onboarding step 2 icon
│   │                               Group `648:1240` from Figma. Vector, fill #4C6589.
│   ├── icon-onb-chat.svg         (174×174 viewBox, ~7KB)  — onboarding step 3 icon
│   │                               Group `648:1253` from Figma. Vector, fill #4C6589.
│   ├── icon-alert-clock.svg      Sprint 2 Ph4 alert pill — clock variant (teal)
│   ├── icon-alert-feedback.svg   Sprint 2 Ph4 alert pill — feedback variant (teal)
│   ├── icon-practice.svg         (46×46) Dashboard — yoga figure in circle. Group 1969 `541:6699`
│   ├── icon-verified.svg         (16×16) Dashboard — teal checkmark chip. Group 1972 `541:6693`
│   ├── icon-calendar.svg         (15×15) Dashboard — calendar date. Group 1975 `541:6711`
│   ├── icon-time.svg             (15×15) Dashboard — clock face. Group 1976 `541:6705`
│   ├── icon-check-sm.svg         (15×12) Dashboard — small teal tick (paid badge). Group 1970 `541:6718`
│   ├── icon-mood-neutral.svg         (40×40) Dashboard — neutral mood face (flat mouth, teal→coral). Group 2096 `541:6741`
│   ├── icon-mood-bad.svg          (40×40) Dashboard — sad mood face (frown + brow marks, blue-gray→teal). Group 2099 `541:6968`. MoodWidget ("Не очень").
│   ├── icon-mood-good.svg        (40×40) Dashboard — happy mood face (smile + cheeks, coral→amber). Group 2097 `541:6749`
│   ├── icon-nav-home.svg         (134×134) Dashboard — home nav button (active, glass glow). Group 1984 `541:6756`
│   ├── icon-nav-diary.svg        (27×27) Bottom nav — diary/calendar tab. Group 1961 `541:6761`
│   ├── icon-nav-profile.svg      (21×27) Bottom nav — profile tab. Group 1959 `541:6767`
│   ├── icon-nav-reservations.svg (27×27) Bottom nav — reservations tab. Group 1962 `541:6772`
│   ├── icon-warning.svg          (23×21) Dashboard — amber warning triangle. Group 2069 `541:7650`
│   ├── icon-verified-master.svg  (26×26) Dashboard — large teal checkmark badge (master). Group 1971 `541:7628`
│   ├── icon-cal-practice.svg     (27×27) Calendar 11 — two-figure meeting/zoom icon. Group 1968 `648:1764`. Fill #4C6589.
│   ├── icon-cal-duration.svg     (15×15) Calendar 11 — clock/duration icon. Group 1976 `648:1768`. Fill #4C6589.
│   ├── icon-cal-datetime.svg     (15×15) Calendar 11 — calendar grid/date icon. Group 1975 `648:1774`. Fill #4C6589.
│   ├── icon-cal-capacity.svg     (15×15) Calendar 11 — people/participants icon. Group 2238 `648:2030`. Fill #4C6589.
│   ├── icon-cal-close.svg        (24×24) Calendar 11 — X/close dismiss button. BOOLEAN_OPERATION `648:1872`. Fill #627A9C.
│   ├── icon-cal-day-done.svg     (16×16) Calendar 11 — calendar day "attended" indicator. Group 1972 `648:1756`. Teal circle + stroke.
│   ├── icon-cal-day-booked.svg   (16×16) Calendar 11 — calendar day "booked" indicator. Group 1973 `648:1759`. Dark steel circle + white text.
│   ├── icon-cal-success-check.svg (93×87) Calendar 11 — large teal blob success graphic. Vector `541:2354`. 30_Check-in Success screen.
│   │
│   │   ── Audit-recovered (Sprint 2 quality audit, 2026-05-18) ──
│   ├── icon-feedback-questions.svg (52×52) Calendar 11 FeedbackRating — "Есть вопросы" option. Group 2336 `541:2326`. Circle + question mark. Fill #4C6589.
│   ├── icon-feedback-good.svg   (52×52) Calendar 11 FeedbackRating — "Хорошо" option. Group 2335 `541:2334`. Rounded rect frame. Fill #D66674 (coral-dark).
│   ├── icon-feedback-fire.svg   (48×52) Calendar 11 FeedbackRating — "Огонь!" option. Vector `541:2341`. Flame shape. Fill #D4863C (amber).
│   ├── icon-checkin-success.svg (93×93) Dashboard — check-in success modal circle. Group 1970 `541:6988`. Teal 30%-fill circle + stroke checkmark (#76DDE6).
│   │
│   │   ── Master Onboarding illustrations (Sprint 2, 2026-05-18) ──
│   ├── icon-master-onb-welcome.svg   (198×198) Master Onboarding step 1. Group 2518 `758:4694`. Welcome figure. Fill #76DDE6.
│   ├── icon-master-onb-space.svg     (198×198) Master Onboarding step 2. Group 2519 `758:4700`. Studio silhouette. Fill #76DDE6.
│   ├── icon-master-onb-analytics.svg (198×198) Master Onboarding step 3. Group 2520 `758:4707`. Bar chart graphic. Fill #76DDE6.
│   └── icon-master-approved.svg      (198×198) Master Onboarding step 4. Group 2523 `758:4714`. Standing figure. Fill #76DDE6.
│
└── screenshots/              ← SACRED visual references, role-organized
    ├── user/    (55 PNG)         ← user-role screens
    ├── master/  (39 PNG)         ← master-role screens
    └── admin/   (1 HTML)         ← legacy reference, no Figma SACRED for admin
```

---

## Icons (`icons/`)

✅ **Status: extracted and saved (Plugin API exports).**

| File | Source node ID | Native size | Saved as | Bytes | Notes |
|---|---|---|---|---|---|
| `icon-back-arrow.svg` | `423:125` | 23×23 viewBox | SVG vector | 215 | DS canon. Chevron-back. Promoted from PNG → SVG 2026-05-18 via `use_figma` Plugin API. |
| `velo-logo-mandala.svg` | `541:1182` (Group 1944) | 492×492 viewBox | SVG vector | 434096 | Large white brand logo with embedded VELO wordmark — welcome hero. Exported via Figma UI (Plugin API chunked-transport too slow for 434KB). |
| `velo-logo-mandala-blue.svg` | Group 1925 (instance of COMPONENT `916:1662`) | 153×154 viewBox | SVG vector | 228380 | Compact blue mandala (#4C6589) с VELO внутри. Used в `.velo-header-compact` (login/register/oauth header) + `.scr-04 .oauth-logo` (callback). Operator-dropped 2026-05-17, integrated 2026-05-18. |
| `icon-onb-practice.svg` | Group `648:1217` | 163×174 viewBox | SVG vector | 13499 | Onboarding step 1 icon (3 meditation figures). Vector from Figma `use_figma` Plugin API 2026-05-18. |
| `icon-onb-diary.svg` | Group `648:1240` | 184×174 viewBox | SVG vector | 5974 | Onboarding step 2 icon (feather + book). Vector from Figma 2026-05-18. |
| `icon-onb-chat.svg` | Group `648:1253` | 174×174 viewBox | SVG vector | 6825 | Onboarding step 3 icon (master + spiral). Vector from Figma 2026-05-18. |
| `icon-alert-clock.svg` | Sprint 2 Ph4 extraction | — | SVG vector | — | Alert pill clock icon — teal. Used in Dashboard AlertPill `--info` variant. |
| `icon-alert-feedback.svg` | Sprint 2 Ph4 extraction | — | SVG vector | — | Alert pill feedback icon — teal. Used in Dashboard AlertPill `--warning` variant. |

**Dashboard 9 icons — added Sprint 2 Phase 4 (2026-05-18) via `use_figma` Plugin API `exportAsync`:**

| File | Source node ID | Figma group | Native size | Notes |
|---|---|---|---|---|
| `icon-practice.svg` | `541:6699` | Group 1969 | 46×46 | Yoga/practice figure in circle. PracticeCard hero icon. Fill #4C6589. |
| `icon-verified.svg` | `541:6693` | Group 1972 | 16×16 | Small teal checkmark in circle (30% fill). Master verified badge on PracticeCard. |
| `icon-calendar.svg` | `541:6711` | Group 1975 | 15×15 | Calendar date icon. Used in PracticeCard date row. Fill #4C6589. |
| `icon-time.svg` | `541:6705` | Group 1976 | 15×15 | Clock face icon. Used in PracticeCard time row. Fill #4C6589. |
| `icon-check-sm.svg` | `541:6718` | Group 1970 | 15×12 | Small teal tick / paid badge. Used in `PaidBadge` component. |
| `icon-mood-neutral.svg` | `541:6741` | Group 2096 | 40×40 | Neutral mood face — flat mouth, teal→coral gradient. MoodWidget ("Нормально"). |
| `icon-mood-good.svg` | `541:6749` | Group 2097 | 40×40 | Happy mood face — upward smile + cheek arcs, coral→amber gradient. MoodWidget ("Хорошо"). |
| `icon-mood-bad.svg` | `541:6968` | Group 2099 | 40×40 | Sad mood face — frown + brow marks, blue-gray→teal gradient. MoodWidget ("Не очень"). Added manually 2026-05-18. |
| `icon-nav-home.svg` | `541:6756` | Group 1984 | 134×134 | Home nav button — active state with glass circle + white glow shadow. BottomNav. |
| `icon-nav-diary.svg` | `541:6761` | Group 1961 | 27×27 | Calendar/diary tab icon. BottomNav inactive. Fill #4C6589. |
| `icon-nav-profile.svg` | `541:6767` | Group 1959 | 21×27 | Profile/person tab icon. BottomNav inactive. Fill #4C6589. |
| `icon-nav-reservations.svg` | `541:6772` | Group 1962 | 27×27 | Reservations/list tab icon. BottomNav inactive. Fill #4C6589. |
| `icon-warning.svg` | `541:7650` | Group 2069 | 23×21 | Warning triangle. AlertPill `--warning` variant. Fill #A16124 (amber-warning). |
| `icon-verified-master.svg` | `541:7628` | Group 1971 | 26×26 | Large teal checkmark in circle. Verified master badge on booked-practice / BookingCard. |

**Calendar 11 icons — added Sprint 2 Calendar DS harvest (2026-05-18) via `use_figma` Plugin API `exportAsync`:**

| File | Source node ID | Figma group | Native size | Notes |
|---|---|---|---|---|
| `icon-cal-practice.svg` | `648:1764` | Group 1968 | 27×27 | Two-figure meeting/zoom icon. Identifies practice type in PracticeMetaRow. Fill #4C6589. |
| `icon-cal-duration.svg` | `648:1768` | Group 1976 | 15×15 | Clock/duration icon. Used next to "45 мин" duration text. Fill #4C6589. |
| `icon-cal-datetime.svg` | `648:1774` | Group 1975 | 15×15 | Calendar grid/date icon. Used next to "Завтра, 07:00" datetime text. Fill #4C6589. |
| `icon-cal-capacity.svg` | `648:2030` | Group 2238 | 15×15 | People/participants icon. Used next to capacity count. Fill #4C6589. |
| `icon-cal-close.svg` | `648:1872` | BOOLEAN_OPERATION (Union) | 24×24 | X/close dismiss button — used in filter overlay header. Fill #627A9C (steel-light). |
| `icon-cal-day-done.svg` | `648:1756` | Group 1972 | 16×16 | Calendar day "attended" indicator. Teal 30%-fill circle + teal checkmark stroke. |
| `icon-cal-day-booked.svg` | `648:1759` | Group 1973 | 16×16 | Calendar day "booked" indicator. Dark steel (#4C6589) filled circle + white "pic" text overlay. |
| `icon-cal-success-check.svg` | `541:2354` | Vector | 93×87 | Large teal blob (#76DDE6) success graphic. 30_Check-in Success screen decorative element. |

**Audit-recovered icons — Sprint 2 quality audit (2026-05-18). Previously missing from all completed blocks:**

| File | Source node ID | Figma group | Native size | Notes |
|---|---|---|---|---|
| `icon-feedback-questions.svg` | `541:2326` | Group 2336 | 52×52 | FeedbackRating "Есть вопросы" option icon. Circle with question mark. Fill #4C6589 (steel-primary). Calendar 11 FeedbackRating widget. |
| `icon-feedback-good.svg` | `541:2334` | Group 2335 | 52×52 | FeedbackRating "Хорошо" option icon. Rounded-rect frame with inner paths. Fill #D66674 (coral-dark). Calendar 11 FeedbackRating widget. |
| `icon-feedback-fire.svg` | `541:2341` | Vector | 48×52 | FeedbackRating "Огонь!" option icon. Flame shape. Fill #D4863C (amber-orange). Calendar 11 FeedbackRating widget. |
| `icon-checkin-success.svg` | `541:6988` | Group 1970 | 93×93 | Dashboard check-in success modal graphic. Teal 30%-opacity circle fill (#76DDE6) + stroke-only checkmark path. Used in `user-dashboard-04-checkin-success` screen. |

**Master Onboarding illustrations — Sprint 2 (2026-05-18) via `use_figma` Plugin API chunked extraction:**

| File | Source node ID | Figma group | Native size | Notes |
|---|---|---|---|---|
| `icon-master-onb-welcome.svg` | `758:4694` | Group 2518 | 198×198 | Master Onboarding step 1 "Welcome" — figure with stars/sparkles. Teal 30%-fill circle background + teal fill illustration. Fill #76DDE6. |
| `icon-master-onb-space.svg` | `758:4700` | Group 2519 | 198×198 | Master Onboarding step 2 "Your Space" — building/studio silhouette. Teal 30%-fill circle background + teal fill illustration. Fill #76DDE6. |
| `icon-master-onb-analytics.svg` | `758:4707` | Group 2520 | 198×198 | Master Onboarding step 3 "Analytics" — bar chart / growth graphic. Teal 30%-fill circle background + teal fill illustration. Fill #76DDE6. |
| `icon-master-approved.svg` | `758:4714` | Group 2523 | 198×198 | Master Onboarding step 4 "Approved" — standing figure with detail elements. Teal 30%-fill circle background + teal fill illustration. Fill #76DDE6. Chunked extraction (62KB source, 9 path elements). |

> Other DS canon icons were destroyed in chain-69 catastrophe.
> 8 COMPONENT_SETs + 3 standalone COMPONENTs lost. They must be
> rebuilt from SACRED frames as needed during Sprint 2+ component
> construction. See `06_project-inputs/VELO_METHODOLOGY.md` §1 for
> the destroyed list.

---

## Backgrounds (`backgrounds/`)

✅ **Status: 1 universal background plate added during Sprint 2 Phase 4.**

| File | Source | Native size | Bytes | Notes |
|---|---|---|---|---|
| `velo-bg-app.png` | Figma 01_Welcome (`541:1180`) composition | 804×1748 RGBA | 1591677 | Universal app background — rune-ornament watermark with central mandala. Used as `.velo-bg-mandala` background-image on ALL onboarding screens (and intended for ALL app screens going forward). Operator dropped manually as `image 40.png`, renamed by Cowork. |

---

## User-role screenshots (`screenshots/user/`)

✅ **55 of 58 user screens saved** (3 from calendar section pending optional re-export).

### Onboarding (8 screens, 804×1748 native 2× scale)

| File | Source node ID | Sprint 3 SCR target |
|---|---|---|
| `user-onboarding-01-welcome.png` | `541:1180` | Welcome (Sprint 3+ shared auth) |
| `user-onboarding-02-login.png` | `541:1216` | user-login (Sprint 4) |
| `user-onboarding-03-register.png` | `648:1152` | user-register (Sprint 4) |
| `user-onboarding-04-oauth.png` | `541:1331` | user-oauth-callback (Sprint 4) |
| `user-onboarding-05-onboarding-1.png` | `648:1212` | user-onboarding step 1 (Sprint 4) |
| `user-onboarding-06-onboarding-2.png` | `648:1235` | user-onboarding step 2 |
| `user-onboarding-07-onboarding-3.png` | `648:1248` | user-onboarding step 3 |
| `user-onboarding-08-onboarding-4.png` | `648:1269` | user-onboarding step 4 |

### Dashboard (9 screens, 804×1752)

| File | Source node ID | Sprint 3 SCR target |
|---|---|---|
| `user-dashboard-01-dashboard-1.png` | `541:6649` | user-dashboard P0 (Sprint 2) |
| `user-dashboard-02-dashboard-2.png` | `648:1283` | user-dashboard alt state |
| `user-dashboard-03-checkin.png` | `541:6913` | check-in modal flow |
| `user-dashboard-04-checkin-success.png` | `541:6987` | check-in success modal |
| `user-dashboard-05-practice-live.png` | `541:6999` | live practice view |
| `user-dashboard-06-booked-practice.png` | `541:7573` | booked practice view |
| `user-dashboard-07-ai-summary.png` | `541:7144` | AI summary (post-practice) |
| `user-dashboard-08-my-reservations.png` | `541:7182` | user-bookings (Sprint 3) |
| `user-dashboard-09-booking-detail.png` | `648:1589` | booking detail (Sprint 3) |

### Calendar (8 of 11 screens)

| File | Source node ID | Sprint 3 SCR target |
|---|---|---|
| `user-calendar-01-calendar-1.png` | `648:1673` | user-calendar (Sprint 3) |
| `user-calendar-02-calendar-filter.png` | `648:1859` | calendar filter modal |
| `user-calendar-03-practice-detail.png` | `648:1934` | user-practice-detail (Sprint 3) |
| `user-calendar-04-master-profile.png` | `541:2065` | master profile (public view) |
| `user-calendar-05-booking-success-2.png` | `541:2120` | booking success state |
| `user-calendar-06-practice-booked.png` | `648:2045` | practice already booked |
| `user-calendar-07-feedback.png` | `541:2286` | user-feedback-submit (Sprint 4) |
| `user-calendar-08-checkin-success.png` | `541:2345` | checkin success (calendar context) |

> ⏳ **3 screens deferred** (optional, can be re-exported by operator if needed):
> - `541:1744` (23_Calendar 2) — alt calendar view
> - `541:2156` (27_Ask Master) — ask master modal
> - `541:6514` (31_Message, 350×293) — message tooltip/modal
>
> These were missing from the Figma multi-select on 2026-05-17.
> Sprint 3 user-calendar spec can proceed without them; they're
> useful additional context if added later.

### Diary (20 screens, 804×1752)

| File | Source node ID | Section |
|---|---|---|
| `user-diary-01-all-map.png` | `541:2817` | All entries, map view |
| `user-diary-02-all-list.png` | `541:3076` | All entries, list view |
| `user-diary-03-filter.png` | `541:3251` | Filter modal |
| `user-diary-04-filter-2.png` | `541:3284` | Filter modal alt |
| `user-diary-05-search.png` | `541:3406` | Search view |
| `user-diary-06-checkins-map.png` | `541:3446` | Checkins, map |
| `user-diary-07-checkins-list.png` | `541:3708` | Checkins, list |
| `user-diary-08-feedbacks-map.png` | `541:3926` | Feedbacks, map |
| `user-diary-09-feedbacks-list.png` | `541:4177` | Feedbacks, list |
| `user-diary-10-entries-map.png` | `541:4362` | Entries, map |
| `user-diary-11-entries-map-2.png` | `541:4556` | Entries, map alt |
| `user-diary-12-entries-list.png` | `541:4775` | Entries, list |
| `user-diary-13-view-entry.png` | `541:4925` | View single entry |
| `user-diary-14-relationships-2.png` | `541:5093` | Relationships view 2 |
| `user-diary-15-relationships-3.png` | `541:5294` | Relationships view 3 |
| `user-diary-16-relationships.png` | `541:5484` | Relationships main |
| `user-diary-17-view-entry-diary.png` | `541:5662` | View entry, diary mode |
| `user-diary-18-view-entry-diary-2.png` | `541:5816` | View entry, alt state |
| `user-diary-19-view-entry-diary-delete.png` | `541:5925` | View entry, delete confirm |
| `user-diary-20-view-entry-diary-edit.png` | `541:6042` | View entry, edit mode |

### Profile (7 screens, 804×1752 except confirmation)

| File | Source node ID | Sprint 3 SCR target |
|---|---|---|
| `user-profile-01-profile.png` | `541:2356` | user-profile main (Sprint 3) |
| `user-profile-02-profile-2.png` | `541:2460` | user-profile alt state |
| `user-profile-03-edit-profile.png` | `541:2577` | edit profile |
| `user-profile-04-confirmation.png` | `541:2616` | confirmation modal (small 496×310) |
| `user-profile-05-notifications.png` | `541:2627` | notifications settings (Sprint 4) |
| `user-profile-06-language-timezone.png` | `541:2655` | language/timezone settings (Sprint 4) |
| `user-profile-07-support.png` | `541:2689` | support / help (Sprint 4) |

### Messages (3 screens, 804×1752)

| File | Source node ID | Sprint 4 target |
|---|---|---|
| `user-messages-01-messages.png` | `541:2718` | user-messages list |
| `user-messages-02-thread.png` | `541:2775` | message thread |
| `user-messages-03-thread-support.png` | `541:2796` | support thread |

---

## Master-role screenshots (`screenshots/master/`)

✅ **All 39 master screens saved.**

### Onboarding (Master sign-up + verification, 13 screens, 804×1748)

| File | Source node ID | Section context |
|---|---|---|
| `master-onboarding-01-landing.png` | `758:4319` | Master landing page |
| `master-onboarding-02-login.png` | `758:4377` | Master login |
| `master-onboarding-03-application-1.png` | `758:4426` | Application step 1 |
| `master-onboarding-04-application-2.png` | `758:4460` | Application step 2 |
| `master-onboarding-05-application-2-alt.png` | `758:4515` | Application step 2 alt |
| `master-onboarding-06-application-3.png` | `758:4571` | Application step 3 |
| `master-onboarding-07-application-3-alt.png` | `758:4637` | Application step 3 alt |
| `master-onboarding-08-application-sent.png` | `758:4701` | Application sent (master-pending) |
| `master-onboarding-09-application-approved.png` | `758:4710` | Application approved |
| `master-onboarding-10-application-rejected.png` | `758:4729` | Application rejected |
| `master-onboarding-11-onboarding-1.png` | `758:4747` | Post-approval onboarding 1 |
| `master-onboarding-12-onboarding-2.png` | `758:4763` | Post-approval onboarding 2 |
| `master-onboarding-13-onboarding-3.png` | `758:4787` | Post-approval onboarding 3 |

### Dashboard (8 screens, 804×1752)

| File | Source node ID | Sprint 5 SCR target |
|---|---|---|
| `master-dashboard-01-week.png` | `758:3246` | master-dashboard (week view, P0 Sprint 2) |
| `master-dashboard-02-month.png` | `758:3404` | master-dashboard (month view) |
| `master-dashboard-03-dashboard-2.png` | `758:3561` | master-dashboard alt |
| `master-dashboard-04-summary.png` | `758:3759` | summary |
| `master-dashboard-05-students.png` | `758:3821` | students list |
| `master-dashboard-06-frame.png` | `758:3928` | small modal/frame (350×293) |
| `master-dashboard-07-student-profile.png` | `758:3946` | student profile |
| `master-dashboard-08-checkins.png` | `758:4066` | master checkins view |

### Practices (15 screens — own practice management)

| File | Source node ID | Native | Sprint 5 SCR target |
|---|---|---|---|
| `master-practices-01-upcoming.png` | `758:1951` | 804×1752 | master-practices list (Sprint 5) |
| `master-practices-02-past.png` | `758:2111` | 804×1752 | past practices |
| `master-practices-03-new.png` | `758:2249` | 804×1748 | master-practice-create step 1 (Sprint 5) |
| `master-practices-04-new-2.png` | `758:2349` | 804×1748 | master-practice-create step 2 |
| `master-practices-05-new-3.png` | `758:2459` | 804×1748 | master-practice-create step 3 |
| `master-practices-06-practice-upcoming.png` | `758:2500` | 804×1752 | upcoming practice detail |
| `master-practices-07-practice-upcoming-2.png` | `758:2626` | 804×1752 | upcoming alt |
| `master-practices-08-cancel-reservation.png` | `758:2732` | 350×365 | cancel modal |
| `master-practices-09-abolish-practice.png` | `758:2771` | 350×466 | abolish practice modal |
| `master-practices-10-edit-practice.png` | `758:2832` | 804×1752 | master-practice-edit |
| `master-practices-11-edit-practice-2.png` | `758:2873` | 804×1752 | master-practice-edit alt |
| `master-practices-12-past-alt.png` | `758:2914` | 804×1752 | past practices alt |
| `master-practices-13-past-3.png` | `758:3003` | 804×1752 | past practices view 3 |
| `master-practices-14-attendance.png` | `758:3065` | 804×1752 | master-practice-attendance |
| `master-practices-15-attendance-2.png` | `758:3169` | 804×1752 | attendance alt |

### Analytics (3 screens, 804×1752)

| File | Source node ID | Sprint 5 SCR target |
|---|---|---|
| `master-analytics-01-reviews.png` | `758:1530` | master-analytics reviews tab (Sprint 5) |
| `master-analytics-02-reviews-2.png` | `758:1743` | reviews alt view |
| `master-analytics-03-payments.png` | `758:1891` | master-finance / payments (Sprint 5) |

---

## Admin-role reference (`screenshots/admin/`)

⚠️ **Important architectural note:** Admin role has **no SACRED screens in
Figma**. The Figma file's 10 SACRED roots cover only user + master roles.
Admin visual design must be **built from scratch** during Sprint 7 using
our DS tokens, with **logic and structure derived from the legacy HTML
mockup below**.

| File | Source | Purpose |
|---|---|---|
| `admin-legacy-reference-v2.5.html` | Legacy admin panel mockup (pre-DSYS era) | Reference for **admin UI logic + interface structure** for Sprint 7 admin block. Visual design is OLD (not aligned with current DS); only logic/IA carries forward. Sprint 7 will rebuild visually using our v1.3 DS tokens. |

### How to use the admin reference in Sprint 7

1. **Read the HTML** to understand admin interface logic (what
   sections, what actions, what data displays, what workflows).
2. **Map the operationIds** from `06_project-inputs/api-openapi.json`
   to the