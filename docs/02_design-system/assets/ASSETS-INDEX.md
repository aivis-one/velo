# VELO Design System — Assets Index

```
Last updated: 2026-05-19
Iteration:    15 (Quality audit 2026-05-20 — 3 Dashboard 9 compliance-pass icons documented:
              icon-arrow-forward, icon-ai-brain, icon-video-camera; stale Calendar 11 + Analytics 3
              table rows for deleted icons annotated; icon count corrected to 79)
Figma file:   F7PD5isLfLdyc0q1Bd5n5c
Status:       ✅ 94 of 97 SACRED screens saved (operator UI export) +
              ✅ 79 DS canon icons (iteration 15: +3 Dashboard 9 compliance-pass icons added) +
              📄 1 legacy admin HTML reference saved
              ⏳ 3 user/calendar screens deferred (re-export at operator's discretion)
              ⚠️ icon-profile-share (541:2454) — export failed "no visible layers"; skipped
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
│   ├── icon-nav-home-active-composite.svg (134×134) Dashboard — BottomNav home active-state composite (glass circle + house path + glow filter). Group 1984 `541:6756`. ⚠️ This is a rendered component state, not a bare icon. TODO: replace with CSS active state in Macro-Phase II BottomNav rebuild.
│   ├── icon-nav-diary.svg        (27×27) Bottom nav — diary/calendar tab. Group 1961 `541:6761`
│   ├── icon-nav-profile.svg      (21×27) Bottom nav — profile tab. Group 1959 `541:6767`
│   ├── icon-nav-reservations.svg (27×27) Bottom nav — reservations tab. Group 1962 `541:6772`
│   ├── icon-warning.svg          (23×21) Dashboard — amber warning triangle. Group 2069 `541:7650`
│   ├── icon-verified-master.svg  (26×26) Dashboard — large teal checkmark badge (master). Group 1971 `541:7628`
│   ├── icon-cal-practice.svg     (27×27) Calendar 11 — two-figure meeting/zoom icon. Group 1968 `648:1764`. Fill #4C6589.
│   │   [icon-cal-duration.svg DELETED 2026-05-19 — floating-point export duplicate of icon-time.svg (Group 1976, same shape, 0.001px coord diff). Use icon-time.svg.]
│   │   [icon-cal-datetime.svg DELETED 2026-05-19 — byte-identical duplicate of icon-calendar.svg (Group 1975, MD5 98cee06b). Use icon-calendar.svg.]
│   ├── icon-cal-capacity.svg     (15×15) Calendar 11 — people/participants icon. Group 2238 `648:2030`. Fill #4C6589.
│   ├── icon-cal-close.svg        (24×24) Calendar 11 — X/close dismiss button. BOOLEAN_OPERATION `648:1872`. Fill #627A9C.
│   ├── icon-cal-filter.svg       (20×20) Calendar 11 — funnel/filter icon for "Выбрать практики" button. Group `648:1848` (Vector 648:1849). Fill **white** — designed for use on dark steel button background. Extracted 2026-05-19.
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
│   │   ── Master Onboarding — approved status icon (Sprint 2, 2026-05-18) ──
│   └── icon-master-approved.svg      (198×198) Application approved status. Group 2523 `758:4714`. Teal circle + standing figure. Fill #76DDE6.
│   │
│   │   ── Messages 3 icons (Sprint 2, 2026-05-19) ──
│   ├── icon-messages-send.svg        (40×40) Messages — send button. Group 2356 `541:2785`. Steel-light circle + white upward-arrow path.
│   │
│   │   ── Analytics 3 icons (Sprint 2, 2026-05-19) ──
│   │   [icon-analytics-tab-profile.svg DELETED 2026-05-19 — byte-identical to icon-master-nav-home.svg (house icon, mislabeled as "profile silhouette"). Use icon-master-nav-home.svg for Analytics tab 1.]
│   │   [icon-analytics-tab-list.svg DELETED 2026-05-19 — byte-identical to icon-master-nav-students.svg (clipboard icon). Use icon-master-nav-students.svg for Analytics tab 2.]
│   ├── icon-analytics-tab-trophy.svg   (21×27) Analytics tab 3 — cup/trophy with base. `758:1672`. Fill #4C6589.
│   ├── icon-analytics-tab-chart.svg    (27×27) Analytics tab 4 — bar chart in rounded-rect frame. `758:1677`. Fill #4C6589.
│   ├── icon-analytics-user-circle.svg  (41×41) Analytics user avatar placeholder. `758:1875`. Steel-pale circle + white person paths.
│   ├── icon-analytics-help.svg         (20×20) Analytics help/question-mark button. `758:1884`. Fill #4C6589.
│   │
│   │   ── Practices 15 icons (Sprint 2, 2026-05-19) ──
│   ├── icon-practices-add.svg          (20×20) Practices — "+" add/new practice CTA. `758:1979` (Union). White fill. Frame 241 direct child.
│   ├── icon-practices-attendees.svg    (16×15) Practices — 3-silhouette group (attendees count). `758:2010` (Group 2689). Fill #4C6589.
│   ├── icon-practices-repeat.svg       (15×15) Practices — circular repeat arrows (recurrence). `758:2019` (Group 2820). Fill #4C6589.
│   ├── icon-practices-review-face.svg  (15×15) Practices — smiley face (review count). `758:2024` (Group 2940). Fill #4C6589.
│   └── icon-practices-warning.svg      (29×26) Practices — warning triangle + exclamation. `758:2755` (Group 2069). Fill #FBC088 (orange-light).
│   │
│   │   ── Master Dashboard 8 icons (Sprint 2, 2026-05-19) ──
│   ├── icon-master-nav-home.svg        (27×27) Master bottom nav — home/dashboard tab (slot 1). `758:3384`. Fill #4C6589.
│   ├── icon-master-nav-schedule.svg   (27×27) Master bottom nav — schedule/calendar tab (slot 2). `758:1759`. Fill #4C6589. ✅ NEW 2026-05-19.
│   ├── icon-master-nav-students.svg   (21×27) Master bottom nav — students/person tab (slot 3). `758:1765`. Fill #4C6589. ⚠️ CORRECTED 2026-05-19.
│   ├── icon-master-nav-profile.svg    (27×27) Master bottom nav — master profile tab (slot 4). `758:1770`. Fill #4C6589. ✅ NEW 2026-05-19.
│   ├── icon-master-header-notif.svg    (20×21) Master header — bell notification icon. `758:3677`. Fill white.
│   ├── icon-master-filter.svg          (20×20) Master students filter — 3-circles social/filter icon. `758:3294`. Fill #627A9C. (6 paths)
│   ├── icon-master-checkin-alert.svg   (37×40) Master checkins — flame/activity alert indicator. `758:4057`. Fill #D4863C.
│   ├── icon-master-rating-star.svg     (18×17) Master student profile — rosette/decorative rating pattern. `758:3967`. Fill #D66674. (2 paths)
│   │
│   │   ── Master Onboarding 13 icons (Sprint 2, 2026-05-19) ──
│   ├── icon-master-onb-community.svg   (212×173) Post-approval onboarding 1. Group 2530 `758:4756`. Community/people illustration. Fill #4C6589.
│   ├── icon-master-onb-workspace.svg   (254×173) Post-approval onboarding 2. Group 2531 `758:4772`. Workspace/studio illustration. Fill #4C6589.
│   ├── icon-master-onb-ai.svg          (173×173) Post-approval onboarding 3. Group 2532 `758:4796`. AI analytics illustration. Fill #4C6589.
│   └── icon-master-application-rejected.svg (198×198) Application rejected status. Group 2527 `758:4733`. Orange chat bubble. Fill #FBC088.
│
└── screenshots/              ← SACRED visual references, role-organized
    ├── user/    (55 PNG)         ← user-role screens
    ├── master/  (39 PNG)         ← master-role screens
    └── admin/   (1 HTML)         ← legacy reference, no Figma SACRED for admin
```

---

## Icons (`icons/`)

✅ **Status: 79 canonical icons (iteration 15, 2026-05-20). History: dedup pass 2026-05-19 reduced 77→73 (deleted 4 byte-identical duplicates, renamed 1 composite). Bottom Nav pass iter 14 added +5 = 78. Quality audit iter 15 documented 3 previously undocumented Dashboard 9 compliance-pass icons = 79. Deleted (stale table refs preserved below for Figma traceability): icon-cal-datetime (= icon-calendar), icon-cal-duration (≈ icon-time), icon-analytics-tab-profile (= icon-master-nav-home), icon-analytics-tab-list (= icon-master-nav-students). Renamed: icon-nav-home → icon-nav-home-active-composite.**

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
| `icon-nav-home-active-composite.svg` | `541:6756` | Group 1984 | 134×134 | Home nav button — active state with glass circle + white glow shadow. BottomNav. ⚠ Renamed from `icon-nav-home.svg` in dedup pass 2026-05-19 (composite clarification). |
| `icon-nav-diary.svg` | `541:6761` | Group 1961 | 27×27 | Calendar/diary tab icon. BottomNav inactive. Fill #4C6589. |
| `icon-nav-profile.svg` | `541:6767` | Group 1959 | 21×27 | Profile/person tab icon. BottomNav inactive. Fill #4C6589. |
| `icon-nav-reservations.svg` | `541:6772` | Group 1962 | 27×27 | Reservations/list tab icon. BottomNav inactive. Fill #4C6589. |
| `icon-warning.svg` | `541:7650` | Group 2069 | 23×21 | Warning triangle. AlertPill `--warning` variant. Fill #A16124 (amber-warning). |
| `icon-verified-master.svg` | `541:7628` | Group 1971 | 26×26 | Large teal checkmark in circle. Verified master badge on booked-practice / BookingCard. |

**Dashboard 9 DS compliance pass — added Sprint 2 session 16 (2026-05-19) via `use_figma` Plugin API `exportAsync`:**

| File | Source node ID | Figma group | Native size | Notes |
|---|---|---|---|---|
| `icon-arrow-forward.svg` | Dashboard 9 | — | 25×15 | Forward/next arrow (left-pointing rendered, mirrored via CSS transform). Used in AI-summary "Подробнее" link row. Fill #4C6589. |
| `icon-ai-brain.svg` | Dashboard 9 | — | 21×21 | AI brain / neural network icon. Used in AI-section tab and AI-card header. Fill #26767D (teal-medium). |
| `icon-video-camera.svg` | Dashboard 9 | — | 27×19 | Video camera icon. Used in practice-live ZOOM section. Fill #4C6589. |

**Calendar 11 icons — added Sprint 2 Calendar DS harvest (2026-05-18) via `use_figma` Plugin API `exportAsync`:**

| File | Source node ID | Figma group | Native size | Notes |
|---|---|---|---|---|
| `icon-cal-practice.svg` | `648:1764` | Group 1968 | 27×27 | Two-figure meeting/zoom icon. Identifies practice type in PracticeMetaRow. Fill #4C6589. |
| ~~`icon-cal-duration.svg`~~ | `648:1768` | Group 1976 | 15×15 | **DELETED 2026-05-19 (dedup iter 12)** — byte-identical to `icon-time.svg`. Use `icon-time.svg`. |
| ~~`icon-cal-datetime.svg`~~ | `648:1774` | Group 1975 | 15×15 | **DELETED 2026-05-19 (dedup iter 12)** — byte-identical to `icon-calendar.svg`. Use `icon-calendar.svg`. |
| `icon-cal-capacity.svg` | `648:2030` | Group 2238 | 15×15 | People/participants icon. Used next to capacity count. Fill #4C6589. |
| `icon-cal-close.svg` | `648:1872` | BOOLEAN_OPERATION (Union) | 24×24 | X/close dismiss button — used in filter overlay header. Fill #627A9C (steel-light). |
| `icon-cal-filter.svg` | `648:1848` | Group 2473 (Vector 648:1849) | 20×20 | Funnel/filter icon for CalendarFilterButton ("Выбрать практики"). Fill **white** — for use on dark steel button background. Extracted 2026-05-19. |
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

**Master Onboarding — approved status icon (Sprint 2, 2026-05-18) via `use_figma` Plugin API chunked extraction:**

| File | Source node ID | Figma group | Native size | Notes |
|---|---|---|---|---|
| `icon-master-approved.svg` | `758:4714` | Group 2523 | 198×198 | Application approved status graphic. Teal 30%-fill circle background + teal fill standing figure. Fill #76DDE6. Chunked extraction (62KB source, 9 path elements). |

**Profile 7 icons — added Sprint 2 Profile DS harvest (2026-05-19) via `use_figma` Plugin API `exportAsync`:**

| File | Source node ID | Figma group | Native size | Notes |
|---|---|---|---|---|
| `icon-profile-notifications.svg` | `541:2361` | Group 2637 | 20×21 | Bell icon with notification dot. Settings row "Уведомления". Fill #627A9C (steel-light). |
| `icon-profile-language.svg` | `541:2369` | Vector | 20×20 | Globe/world icon. Settings row "Язык/Часовой пояс". Same asset reused in language-timezone detail frame (541:2664). Fill #627A9C. |
| `icon-profile-edit.svg` | `541:2419` | Vector | 20×20 | Pencil/edit icon. Settings row "Редактировать профиль". Fill #627A9C. |
| `icon-profile-bookings.svg` | `541:2424` | Group 2616 | 20×20 | Calendar with two horizontal rows icon. Settings row "Мои бронирования". Fill #627A9C. |
| `icon-profile-messages.svg` | `541:2433` | Group 2525 | 20×20 | Chat bubble with 3 dots. Settings row "Сообщения". Fill #627A9C. |
| `icon-profile-support.svg` | `541:2448` | Vector | 17×20 | Shield/protection shape. Settings row "Поддержка". Fill #627A9C. |
| `icon-profile-logout.svg` | `541:2572` | Group 2645 | 20×20 | Exit-door arrow + person silhouette. Settings "Выйти" (destructive). Fill **#AD3444** (coral-darker). |
| `icon-profile-delete.svg` | `541:2609` | Group 2645 | 20×24 | Trash can with lid + two delete-stroke paths. Edit profile "Удалить аккаунт" (destructive). Fill **#AD3444** (coral-darker). |
| `icon-profile-timezone.svg` | `541:2674` | Group 2673 | 20×20 | Clock face (circle + hour/minute hands). Language-Timezone detail row. Fill **#ffffff** — designed for steel-primary (`#4C6589`) background context. |

> ⚠️ **icon-profile-share** (`541:2454`, Group 2641, 17×20) — export failed with "no visible
> layers" error from Plugin API. Node exists in Figma tree as child of settings row "Поделиться"
> but has no renderable content at export time. Skipped; can be re-attempted manually if needed.

**Diary 20 icons — added Sprint 2 Diary DS harvest (2026-05-19) via `use_figma` Plugin API `exportAsync`:**

| File | Source node ID | Figma group | Native size | Notes |
|---|---|---|---|---|
| `icon-diary-tab-all.svg` | `541:3255` | Group 2474 | 40×40 | DiaryFilterBar "All" tab — filled steel-light circle with white hourglass/funnel path. Filter tab active state. Fill `#627A9C` (steel-light). |
| `icon-diary-edit.svg` | `541:5921` | Group 2499 | 17×20 | Diary entry edit button — document/padlock shape with 3 white-filled paths. Used in DiaryEntryView action bar. Fill white (on steel-primary bg). |
| `icon-diary-filter-n5.svg` | `541:3315` | Group 2475 | 38×38 | DiaryRatingSelector numeral "5" — steel-light circle outline + "5" digit path. Rating chip inactive. Fill `#627A9C`. |
| `icon-diary-filter-n6.svg` | `541:3318` | Group 2476 | 38×38 | DiaryRatingSelector numeral "6" — steel-light circle outline + "6" digit path. Rating chip inactive. Fill `#627A9C`. |
| `icon-diary-filter-n7.svg` | `541:3321` | Group 2477 | 38×38 | DiaryRatingSelector numeral "7" — steel-light circle outline + "7" digit path. Rating chip inactive. Fill `#627A9C`. |
| `icon-diary-filter-n8.svg` | `541:3324` | Group 2478 | 38×38 | DiaryRatingSelector numeral "8" — steel-light circle + two-path "8" digit. Rating chip inactive. Fill `#627A9C`. |
| `icon-diary-filter-n9.svg` | `541:3327` | Group 2479 | 38×38 | DiaryRatingSelector numeral "9" — steel-light circle outline + "9" digit path. Rating chip inactive. Fill `#627A9C`. |
| `icon-diary-filter-n10.svg` | `541:3330` | Group 2480 | 38×38 | DiaryRatingSelector numeral "10" — steel-light circle + two separate digit paths "1" and "0". Rating chip inactive. Fill `#627A9C`. |
| `icon-diary-filter-n11.svg` | `541:3333` | Group 2481 | 38×38 | DiaryRatingSelector numeral "11" — steel-light circle + two separate digit paths "1" and "1". Rating chip inactive. Fill `#627A9C`. |
| `icon-diary-pin.svg` | `541:2950` | Group 2354 | 28×34 | DiaryMapView primary map pin marker — ornate pin shape with crescent hole + decorative detail paths, uses SVG `<mask>` elements. Fill `#4C6589` (steel-primary). ~31KB complex path. |
| `icon-diary-pin-alt.svg` | `541:2953` | Group 2355 | 28×34 | DiaryMapView alternate map pin variant — mirrored crescent, same mask technique. Fill `#4C6589` (steel-primary). ~31KB complex path. |

> ⚠️ **Skipped exports (Diary 20 harvest, 2026-05-19):** `541:2930` (Group 2336, location marker — stroke-only vectors, "no visible layers"); `541:2963`/`541:2960` (Groups 2361/2360, view-toggle circle buttons — "no visible layers"); `541:3258`/`541:3261` (Groups 2398/2399, round header action buttons — "no visible layers"). All are geometric composites with no direct bitmap/fill layers at the group root; can be rebuilt from primitives using DS tokens if needed.

**Messages 3 icons — added Sprint 2 Messages DS harvest (2026-05-19) via `use_figma` Plugin API `exportAsync`:**

| File | Source node ID | Figma group | Native size | Notes |
|---|---|---|---|---|
| `icon-messages-send.svg` | `541:2785` | Group 2356 | 40×40 | Message thread send button — steel-light circle (#627A9C) background + white upward-arrow path. Used in MessageInputBar. Back-arrow already in DS as `icon-back-arrow.svg`. |

> ℹ️ **Messages 3 token audit result:** Zero new tokens. All fills/radii/effects/typography map to existing DS tokens. Specifically: input bar glass treatment uses `--velo-color-alpha-steel-light-15` fill + `--velo-shadow-glow-white-strong` + `--velo-blur-glass-stronger` (all already promoted). Message bubbles use `--velo-color-steel-light` (outbound) and `--velo-color-neutral-white` (inbound). Unread badge uses `--velo-color-coral-medium`. Conversation row preview text uses `--velo-color-alpha-steel-70` (0.70 opacity). Corner radius 252 on input bar is decorative-only (single-component literal per §variables.css vestigial list).

**Analytics 3 icons — added Sprint 2 Analytics 3 DS harvest (2026-05-19) via `use_figma` Plugin API `exportAsync`:**

| File | Source node ID | Figma group | Native size | Notes |
|---|---|---|---|---|
| ~~`icon-analytics-tab-profile.svg`~~ | `758:1663` | Vector (child of Group 2225) | 27×27 | **DELETED 2026-05-19 (dedup iter 12)** — byte-identical to `icon-master-nav-home.svg` (mislabeled; Analytics tab 1 is home/dashboard). Use `icon-master-nav-home.svg`. |
| ~~`icon-analytics-tab-list.svg`~~ | `758:1666` | Group 2226 | 27×27 | **DELETED 2026-05-19 (dedup iter 12)** — near-identical to `icon-master-nav-students.svg` (0.001px FP diff). Use `icon-master-nav-students.svg`. |
| `icon-analytics-tab-trophy.svg` | `758:1672` | Group 1959 | 21×27 | Analytics tab bar slot 3 — cup/trophy with pedestal (2 paths). AnalyticsTabBar inactive tab icon. Fill #4C6589. |
| `icon-analytics-tab-chart.svg` | `758:1677` | Group 1962 | 27×27 | Analytics tab bar slot 4 — bar chart with 4 vertical bars in rounded-rect frame (5 paths). AnalyticsTabBar active/key icon. Fill #4C6589. |
| `icon-analytics-user-circle.svg` | `758:1875` | Group 2629 | 41×41 | Analytics reviewer avatar placeholder — steel-pale circle (#91A2BA) background + white head + white shoulders paths. ReviewCard avatar fallback. |
| `icon-analytics-help.svg` | `758:1884` | Group 2752 | 20×20 | Analytics help/question-mark button — circle frame + "?" glyph + "." dot (3 paths). Used in Analytics header action bar. Fill #4C6589. |

> ℹ️ **Analytics 3 token audit result:** Zero new tokens. All fills/effects/typography map to existing DS tokens. Fills: `#4C6589` → `--velo-color-steel-primary`; `#91A2BA` → `--velo-color-steel-pale`; `#D66674` → `--velo-color-coral-dark`; `#2F9EA8` → `--velo-color-teal-medium`; `#619CD2` → `--velo-color-blue-medium`; `#D4863C` → `--velo-color-orange-medium`; glass card fill `rgba(98,122,156,0.15)` → `--velo-color-alpha-steel-light-15`. Blur effects → `--velo-blur-glass-medium`/`--velo-blur-glass`. White glow → `--velo-shadow-glow-white-strong`. Only new colour candidate `#abbfda@15%` (neutral-200 @ 0.15) occurred in 2–3 slots — below single-use threshold, kept as component-local literals per §variables.css rule.

**Practices 15 icons — added Sprint 2 Practices 15 DS harvest (2026-05-19) via `use_figma` Plugin API `exportAsync`:**

| File | Source node ID | Figma group | Native size | Notes |
|---|---|---|---|---|
| `icon-practices-add.svg` | `758:1979` | BOOLEAN_OPERATION (Union) | 20×20 | "+" add/new-practice CTA button icon. White fill. Direct depth-1 child of frame `241_Practices upcoming`. Used on FAB / "Новая практика" button. |
| `icon-practices-attendees.svg` | `758:2010` | Group 2689 | 16×15 | 3-person silhouette group — attendees count in practice card meta row. Used next to "3/10" attendees counter. Fill #4C6589 (steel-primary). |
| `icon-practices-repeat.svg` | `758:2019` | Group 2820 | 15×15 | Two circular repeat arrows — recurrence indicator. Practice card meta row, used next to day abbreviation ("Сб"). Fill #4C6589 (steel-primary). |
| `icon-practices-review-face.svg` | `758:2024` | Group 2940 | 15×15 | Smiley face with two eyes + smile arc — review/satisfaction indicator. Practice card meta row, used next to "0/10" review count. Also appears at 21×21 in abolish-practice modal. Fill #4C6589 (steel-primary). |
| `icon-practices-warning.svg` | `758:2755` | Group 2069 | 29×26 | Warning triangle with exclamation mark. Used in `248_Cancel reservation` and `249_Abolish practice` modals on orange-50 (`#FFF3EA`) background panel. Fill #FBC088 (orange-light). Distinct from existing `icon-warning.svg` (`541:7650`, fill #A16124). |

**Master Onboarding 13 icons — added Sprint 2 Master Onboarding 13 DS harvest (2026-05-19) via `use_figma` Plugin API `exportAsync`:**

| File | Source node ID | Figma group | Native size | Notes |
|---|---|---|---|---|
| `icon-master-onb-community.svg` | `758:4756` | Group 2530 | 212×173 | Post-approval onboarding 1 "Добро пожаловать" — community/people illustration. 7 paths. Fill #4C6589 (steel-primary). Used in MasterOnboardingStep screen 1. |
| `icon-master-onb-workspace.svg` | `758:4772` | Group 2531 | 254×173 | Post-approval onboarding 2 "Ваше пространство" — workspace/studio illustration. 14 paths. Fill #4C6589 (steel-primary). Used in MasterOnboardingStep screen 2. |
| `icon-master-onb-ai.svg` | `758:4796` | Group 2532 | 173×173 | Post-approval onboarding 3 "AI-аналитика о состоянии группы" — AI analytics illustration. ~13 paths. Fill #4C6589 (steel-primary). Used in MasterOnboardingStep screen 3. |
| `icon-master-application-rejected.svg` | `758:4733` | Group 2527 | 198×198 | Application rejected status graphic — orange 30%-fill circle (#FBC088@0.3) + speech bubble with 3 dots (fill #FBC088). Used in ApplicationStatusCard `rejected` state. |

> ℹ️ **Master Onboarding 13 token audit result:** Zero new tokens. All 13 frames fully covered by existing DS. Fills: `#4C6589` → `--velo-color-steel-primary`; `#627A9C` → `--velo-color-steel-light`; `#ABBFDA` → `--velo-color-neutral-200`; `#FBC088` → `--velo-color-orange-light`; `#FBC088@0.4` → `--velo-bg-alert-warning`; `#A16124` → `--velo-color-orange-dark`. Radii: 15 → `--velo-radius-lg`; 5 → `--velo-radius-sm`; 200 → `--velo-radius-pill`. Effects: DROP_SHADOW white → `--velo-shadow-glow-white`; BACKGROUND_BLUR 4px → `--velo-blur-glass`. Size 28px → `--velo-size-28` (already in DS). Component-local literals (below threshold): `#76DDE6@0.3` (2 occurrences, status indicator circles); `#FBC088@0.3` (1 occurrence, rejected circle background).

**Master Dashboard 8 icons — added Sprint 2 Master Dashboard 8 DS harvest (2026-05-19) via `use_figma` Plugin API `exportAsync`:**

| File | Source node ID | Figma group | Native size | Notes |
|---|---|---|---|---|
| `icon-master-nav-home.svg` | `758:3384` | Vector | 27×27 | Master bottom-nav slot 1 — home icon. firstM=M17.1121. Fill #4C6589 (steel-primary). Used in MasterBottomNav active/inactive home tab. |
| `icon-master-nav-schedule.svg` | `758:1759` | Group 2226 | 27×27 | Master bottom-nav slot 2 — schedule/calendar icon. firstM=M7.48828. Fill #4C6589. Extracted 2026-05-19 from Group 2648 (АНАЛИТИКА nav frame). ✅ Replaces previous mislabeled version. |
| `icon-master-nav-students.svg` | `758:1765` | Group 1959 | 21×27 | Master bottom-nav slot 3 — students/person icon. firstM=M9.28125. Fill #4C6589. Extracted 2026-05-19. ⚠️ Previous file had WRONG content (clipboard icon from dashboard-frame nav vs. correct person icon from АНАЛИТИКА nav). Now corrected. |
| `icon-master-nav-profile.svg` | `758:1770` | Group 1962 | 27×27 | Master bottom-nav slot 4 — master profile icon. firstM=M26.9945. Fill #4C6589. Extracted 2026-05-19. Distinct from user profile (firstM=M9.28125). Rounded-rect outer frame with 4 vertical bar paths. |
| `icon-master-header-notif.svg` | `758:3677` | Vector | 20×21 | Master header notification bell icon. Fill #4C6589. Used in MasterDashboard header action bar. |
| `icon-master-filter.svg` | `758:3294` | Vector | 20×20 | Social/people filter icon — 3 circle outlines (NOT a funnel). Fill #627A9C (steel-light). Used in MasterDashboard student list filter button. ⚠️ Do NOT use for calendar filter — use `icon-cal-filter.svg` instead. |
| `icon-master-checkin-alert.svg` | `758:4057` | Vector | 37×40 | Check-in alert flame icon — decorative flame/alert indicator. Fill #4C6589. Used in MasterDashboard check-in alert card. |
| `icon-master-rating-star.svg` | `758:3967` | Vector | 18×17 | Star rating icon — single 5-point star. Fill #4C6589. Used in MasterDashboard student rating display. |

> ℹ️ **Master Dashboard 8 token audit result:** 4 new Layer 1 primitives promoted: `--velo-color-steel-wash` (#dce6f3), `--velo-color-teal-wash` (#bdecf1), `--velo-color-coral-wash` (#f9cbd1), `--velo-color-peach-wash` (#fddfc4) — MoodProgressBar gradient stops (27 occurrences). `#abbfda@15%` in MasterStatCard bar chart kept as component-local literal (below threshold). DS iteration 10.

> ℹ️ **Bottom Nav icon correction (iteration 14, 2026-05-19):** Previous `icon-master-nav-students.svg` (758:3387) was extracted from ДАШБОРД nav frame (Group 1988 shared with user) and contained wrong clipboard icon. Correct master nav slot icons extracted from АНАЛИТИКА screen (Group 2648, 758:1748) — the dedicated distinct master nav: slot 2 = schedule (calendar, 758:1759), slot 3 = students (person, 758:1765), slot 4 = master profile (rounded-rect frame, 758:1770). User nav: slot 1 home composite, slot 2 diary (=M7.48828), slot 3 reservations (document, =M5.61215), slot 4 profile (person, =M9.28125). Master nav: slot 1 home (=M17.1121), slot 2 schedule (=M7.48828), slot 3 students (=M9.28125), slot 4 master-profile (=M26.9945).

---

**Dashboard 9 DS-compliance icons — added Sprint 2 session 16 (2026-05-19) during `_dashboard-flow.html` DS audit pass:**

| File | Source node ID | Figma group | Native size | Notes |
|---|---|---|---|---|
| `icon-arrow-forward.svg` | `648:1595` | Vector 61, Group 1924 | 25×15 | Right-pointing horizontal arrow. Mirrored from Figma left-pointing arrow via SVG `scale(-1,1)` transform. Fill #4C6589. Used in EnergyRow (between mood faces) and AICard "Подробнее" link. |
| `icon-ai-brain.svg` | `541:7155` | Vector in 16_AI-summary | 21×21 | Brain / AI duality icon — dual-hemisphere outline path. Fill #26767D (teal-dark). Used as leading icon in AI-summary `alert-pill--info` header. |
| `icon-video-camera.svg` | `648:1609` | Vector in 18_Booking Detail | 27×19 | Video camera body + lens. Fill #4C6589. Used in BookingDetail ZOOM section icon box (CSS `filter: brightness(0) invert(1)` renders white on blue background). |

> ℹ️ **Dashboard 9 DS-compliance pass (session 16):** Zero new tokens. All three icons use existing fills (`#4C6589` → `--velo-color-steel-primary`; `#26767D` → `--velo-color-teal-dark`). Extracted to resolve DS violations flagged by operator (emoji/text-char usage in `_dashboard-flow.html`).

---

> ⚠️ **Known gaps — SVG files documented but missing from disk (re-extraction needed before Calendar 11 / Analytics 3 mockup builds):**
> - `icon-cal-duration.svg` (`648:1768`) — clock/duration icon, Calendar 11
> - `icon-cal-datetime.svg` (`648:1774`) — calendar grid/date icon, Calendar 11
> - `icon-analytics-tab-profile.svg` (`758:1663`) — person silhouette, Analytics 3 tab bar slot 1
> - `icon-analytics-tab-list.svg` (`758:1666`) — clipboard/document, Analytics 3 tab bar slot 2
>
> All 4 were documented during Phase B harvest but `exportAsync` output was not persisted. Re-extract via `use_figma` Plugin API at start of respective mockup builds.

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
**Dashboard 9 DS-compliance icons — added 2026-05-19 (session 16, DS violation fix pass) via `use_figma` Plugin API `exportAsync`. These 3 icons were discovered missing during mockup audit; all other Dashboard 9 icons were already in DS from prior harvest sessions:**

| File | Source node ID | Figma group | Native size | Notes |
|---|---|---|---|---|
| `icon-arrow-forward.svg` | `648:1595` | Vector 61 (child of Group 1924) | 25×15 | Horizontal right-pointing arrow (→). Figma original is left-pointing (←); exported and mirrored horizontally via SVG `<g transform="scale(-1,1) translate(-25,0)">`. Fill #4C6589. Used in EnergyRow (between mood faces) and AICard "Подробнее" link. |
| `icon-ai-brain.svg` | `541:7155` | Vector (child of info-pill in 16_AI-summary) | 21×21 | Brain / AI duality icon — two-lobe abstract path representing AI analytics. Fill #26767D (teal-medium). Used in AI-summary screen alert-pill--info leading icon. |
| `icon-video-camera.svg` | `648:1609` | Vector (child of ZOOM section in 18_Booking Detail) | 27×19 | Video camera body + lens + zoom lens elements. Fill #4C6589. Used in booking-detail ZOOM section icon box (blue #2D8CFF bg, CSS filter brightness(0) invert(1) makes it white). |

> ℹ️ **Dashboard 9 DS compliance audit result (2026-05-19 session 16):** Root cause of DS violations was use of emoji characters (😩/😊) for EnergyRow faces, text chars (→/i/⚠/✓/✕) instead of DS SVG icons. Fix: emoji → icon-mood-neutral + icon-mood-good (both already in DS); → → icon-arrow-forward (new); "i" text → icon-ai-brain (new, AI-summary only); inline SVG camera → icon-video-camera (new); ⚠/✓/✕ in v-badge removed (Figma uses color-only badges, no icon prefix). Three new SVG files extracted from Figma and saved. `_shared/components.css` z-index fix: `.velo-bg-mandala` z-index 0→-1; `_shared/shell.css` `.frame` gained `isolation: isolate`. DS icon total: 73 + 3 = **76 canonical icons**.
