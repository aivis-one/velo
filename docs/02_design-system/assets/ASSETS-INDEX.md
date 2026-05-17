# VELO Design System — Assets Index

```
Last updated: 2026-05-18
Iteration:    1 (Sprint 1 Phase 1 — extraction COMPLETE)
Figma file:   F7PD5isLfLdyc0q1Bd5n5c
Status:       ✅ 94 of 97 SACRED screens saved (operator UI export) +
              ✅ 2 DS canon icons saved (Plugin API) +
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
│   └── icon-onb-chat.svg         (174×174 viewBox, ~7KB)  — onboarding step 3 icon
│                                   Group `648:1253` from Figma. Vector, fill #4C6589.
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
| `admin-legacy-reference-v2.5.html` | Legacy admin panel mockup (pre-DSYS era) | Reference for **admin UI logic + interface structure** for Sprint 7 admin block. Visual design is OLD (not aligned with current DS); only logic/IA carries forward. Sprint 7 will rebuild visually using our v1.2 DS tokens. |

### How to use the admin reference in Sprint 7

1. **Read the HTML** to understand admin interface logic (what
   sections, what actions, what data displays, what workflows).
2. **Map the operationIds** from `06_project-inputs/api-openapi.json`
   to the admin actions visible in the HTML.
3. **Build the admin mockups in HTML** (Sprint 7 Phase 4) using:
   - Our DS tokens (`02_design-system/tokens/variables.css`)
   - Layer 2 components from styleguide
   - Admin shell (3-tab bottom bar per ROADMAP §10.1)
   - Logic and IA from this legacy reference
4. **Do not copy the legacy HTML's visual styling** — it predates our
   DS. Only the logic and structure transfer.

This is documented in ROADMAP §10 (Sprint 7 — Admin Block) and will be
referenced explicitly in the admin SCR specs.

---

## Summary

| Category | Count | Status |
|---|---|---|
| **Icons** | 2 | ✅ saved |
| **User screenshots** | 55 of 58 | ✅ saved (3 calendar optional deferred) |
| **Master screenshots** | 39 of 39 | ✅ all saved |
| **Admin** | 1 legacy HTML | ✅ saved as reference |
| **TOTAL SCREENSHOT PNG** | **94 of 97** | ✅ INVENTORY GATE proceeds |
| **Coverage** | ~97% | ✅ acceptable; deferred 3 = optional re-export |

**Native resolution:** All PNGs at 2× retina (804×1748 / 804×1752 from 402×874/876 frames) — high quality for crisp side-by-side comparison with HTML mockups during MOCKUP GATE reviews in Sprint 3+.

---

## References

- Extraction sequence: `../../04_methodology/VELO-METHODOLOGY.md` §6.5
- Asset placement rules: §6.5 step 1.3 (screenshots), 1.4 (icons)
- Export procedure used: `./_FIGMA-EXPORT-INSTRUCTIONS.md` (operator UI multi-select export)
- Parent index: `../INDEX.md`
- Companion file: `../FIGMA-OPERATIONS-GUIDE.md` (use_figma rules)
- Source v3 methodology page IDs: `../../06_project-inputs/VELO_METHODOLOGY.md` §1

---

## Anchor

```
[ASSETS-INDEX.md | v1.0-final | 2026-05-17]
Sprint 1 Phase 1 extraction complete:
  • 2 DS canon icons saved (Plugin API)
  • 94 SACRED PNG screenshots saved (operator UI export at 2× retina)
  • 1 admin legacy HTML reference saved (Sprint 7 input)
  • 3 user calendar PNGs deferred (optional re-export)
Status: ✅ INVENTORY GATE clearable. Sprint 1 closes cleanly.
Location: D:\02_Projects\velo\docs\02_design-system\assets\ASSETS-INDEX.md
```
