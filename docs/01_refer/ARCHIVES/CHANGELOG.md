# Velo — Cleanup Changelog

> Per-sprint Clean-Sync transfers from active docs.
> Created: 2026-04-28 (S1-Clean-Sync first run).

---

## S1 Cleanup — 2026-04-28

### From BACKLOG.md (6 items transferred)

- **#19 — D3 decision clarification** — RESOLVED via decision #024 (S1 P02 OPEN ratification: Vue-SVG baseline + bundle PNG decorative supplement). Originally surfaced by Governance scout C09; resolved before Clean-Sync. Detail in `ARCHIVES/AUDIT/S1-AUDIT.md` §9.
- **#25 — user-ai-summary feature gap** — RESOLVED in C06b: status now known (backend `AISummaryResponse` exists in `generated.ts:18`; no frontend wrapper yet). Superseded by S2 C24 (frontend wrapper implementation). Categorized as bundle-greenfield in `ARCHIVES/AUDIT/S1-AUDIT.md` §4 + closure note in §10 #6.
- **#29 — IconRuble candidate for removal** — RESOLVED in S1-Clean-Sync Step 3 §B: 0 consumers confirmed via grep across `frontend/src/`; cross-confirmed by S1-AUDIT.md §9 (not in current view inventory). Action: deleted `frontend/src/components/icons/IconRuble.vue`; removed barrel export from `index.ts`. Velo backend operates in EUR.
- **#31 — ENVIRONMENT.md path drift `D:\03_Projects` → `D:\02_Projects`** — RESOLVED in S1-Clean-Sync Step 2 §A1 + §A2 (2 sites: §System Project path table row + §Shell Notes prose).
- **#35 — ENVIRONMENT.md commit convention cleanup** — RESOLVED in S1-Clean-Sync Step 2 §A3: dropped 2 `cycle:`-prefix rows from §Git Workflow Commit convention table (rows never used during S1; phase-bundled commit policy supersedes per Phase-Builder CLOSE Step 4f).
- **#36 — Staging deploy flow doc clarification** — RESOLVED in S1-Clean-Sync Step 2 §A4 + §B1 per variant (d) framing (Human-confirmed): pointer to `SERVER-ACCESS.md` as live source of truth; S1 partner-joint deploy noted; S2+ self-deploy transition noted; «auto-pulls» phrasing removed from both ENVIRONMENT.md and ARCHITECTURE.md.

### From ARCHITECTURE.md

- **§Key Decisions count drift** — `Active decisions #001-#025 as of Phase 03 close (2026-04-26)` updated to `Active decisions #001-#026 as of S1 close (2026-04-28)`. Sprint-Closer Step 1+ added #026 (ProbeKit hardened to Velo paths); ARCHITECTURE.md was not refreshed at sprint close. Updated in S1-Clean-Sync Step 3 §A.

### Stale Files Archived

- **`frontend/src/components/icons/IconRuble.vue`** — deleted in S1-Clean-Sync Step 3 §B per BACKLOG #29 + decision #024 (D3 ratification): Velo backend operates in EUR; 0 consumers verified. Barrel export line removed from `frontend/src/components/icons/index.ts`.

---

## S2-S3 Speedrun Closure — 2026-04-30

> Speedrun mode (decision #049) — explicit inversion of decision #042 (quality > density) for sponsor-demo target.
> Per-cycle Claude Design pipeline + per-cycle visual verify rhythm collapsed into 2 aggregate visual verify gates (post-MEGA-1, post-MEGA-2).
> Audit ceremony (Sprint-Closer Step 1+ ProbeKit lite) deferred to BACKLOG #100 — gates production promotion.

### Decisions added

- **#047** — Path Y discipline (logic-first build mass; visual polish deferred to S5+ cluster). Originally added at S2-P06 close; scope note refreshed at speedrun closure to cover MEGA-1/2 inheritance across C22-C52.
- **#048** — No-emoji rule + icon-component discipline. Bare emoji characters replaced with inline SVG icon components from `frontend/src/components/icons/`. First applied speedrun MEGA-1 (~74 in-scope hits cleaned across user views) + MEGA-2 (BACKLOG #98 carry-over resolved).
- **#049** — Speedrun mode — explicit inversion of #042 for sponsor-demo target. 33 cycles (C22-C54) executed across 2 mega-execute prompts + 2 commits + 1 closure commit. Quality backfill scheduled S5+ polish cluster.

### BACKLOG entries surfaced

- **#97** — Backend `POST /bookings/{id}/leave` endpoint (mid-practice exit semantics). Logged at MEGA-1 close. Frontend C31 PracticeLiveView "Покинуть" currently uses `cancelBooking`; conflates pre-practice cancel vs leave-mid-session. Status: OPEN.
- **#98** — Emoji cleanup MEGA-2 carry. Logged at MEGA-1 close (23 in-scope hits remain in 12 files). Status: **CLOSED 2026-04-30 at MEGA-2** — emoji audit grep returns 0 hits in `frontend/src/views/user/`, `frontend/src/components/shared/`, `frontend/src/utils/`. Cleanup landed across 12 files (DiaryList, BookingCard, PracticeCard, FormShell, CancelBookingPopup, DiaryCheckin/Feedback/EntryDetail, DiaryEntryForm, MyBookingsView, TopupCancel/SuccessView, adminHelpers).
- **#99** — Backend public master endpoint + MasterPublicResponse fields. Logged at MEGA-2 close. C51 MasterProfilePublicView is degraded v1; lift list itemized. Status: OPEN.
- **#100** — Post-demo S2/S3 audit cycle reactivation. Logged at closure commit. CRITICAL gate before production promotion. Status: OPEN.
- **#96** — `velo update` script transient. **Promoted from LOW to P2** at closure commit. Hypothesis CONFIRMED: 4/4 deploys ≥600 LOC fire transient; 1/1 small deploy clean. Server-side fix candidate logged.

### Files added (frontend/src/)

~73 new files total (S1 baseline 140 → S3 close 213):

- **28 new view files** (S2 P07-P09 + S3 P10-P13):
  - S2: 7 (BookingSuccessView, BookedPracticeView, BookingDetailView, CheckinSuccessView, PracticeLiveView, FeedbackSuccessView, EditProfileView)
  - S3: 13 (CheckinsCategoryView, FeedbacksCategoryView, EntriesCategoryView, DiaryEntryView, RelationshipsView, NotificationsView, LanguageTimezoneView, SupportFormView, MessagesListView, ThreadView, AISummaryView, MasterProfilePublicView, MyReservationsView)
  - Phase 06 (pre-speedrun, also in S2): 5 (LoginView, RegisterView, OAuthLoadingView, OnboardingCarouselView, OnboardingTimezoneView)
  - 8 view files refreshed (UserDashboardView, UserProfileView, DiaryView, CalendarView, PracticeDetailView, CheckinView, FeedbackView, WelcomeView)
- **~25 new shared components** (StatCard, ProfileMenuItem, Callout, MasterCardSummary, WeekStrip, CalendarFilterOverlay, SpineDivider, DiaryEntryBubble, DiaryEntryFlat, DiaryComposer, DiaryComposerExpanded, DiaryFilterOverlay, DiarySearchOverlay, EntryActionMenu, UndoSnackbar, RelationshipChain, AICommentaryCard, ConversationListItem, ChatBubble, ThreadComposer, ReservationCard, ...)
- **25 new icon components** (11 MEGA-1 + 14 MEGA-2)
- **3 new stores** (notifications, messages, bookings extension via getters) + **2 store extensions** (ui theme, diary search/filter/history)
- **1 utility data file** (`frontend/src/utils/mockMessagesData.ts`)
- **0 new dependencies** (Path Y discipline #047)
- **0 new test files** (BACKLOG #44 deferred per #042 inverted in #049)

### Cross-sprint hygiene

- `ARCHITECTURE.md` §Components — Phase 07-13 additions appended (5 new phase blocks + 1 cross-cutting block); header date stamp refreshed.
- `FILE-TREE.md` — partial regen of `frontend/src/views/`, `components/icons/`, `components/shared/`, `stores/`, `utils/` subtrees per Clean-Sync §1 conditional gate (drift > 10 entries triggers Path B regen); header date stamp refreshed.
- `ENVIRONMENT.md` — `velo CLI commands` subsection added under §Test Infrastructure (8-row reference + cross-references to decisions #031 #046 + BACKLOG #96); header date stamp refreshed.
- `decisions.md` — #048 + #049 appended (count goes 47 → 49 ACTIVE); #047 scope note refreshed.
- `BACKLOG.md` — #100 appended; #96 promoted to P2 + hypothesis CONFIRMED; #98 marked RESOLVED in MEGA-2 commit.
- `S2-SPRINT.md` — all cycle status flips to DONE; Status header → CLOSED; Plan vs Reality + What Worked / What Didn't / Carry Forward sections filled; Sprint Metrics S2-close row added.
- `S3-SPRINT.md` — same pattern: all cycle status flips, Status header CLOSED, Plan vs Reality + close-state sections filled.
- `1f37a61` intermediate gitignore housekeeping commit (between MEGA-1 and MEGA-2; intentional, preserved in history; documented in S2-RETRO).

### Audit / RETRO status

- **ProbeKit lite profile** run **DEFERRED** per decision #049 + BACKLOG #100.
- `S2-CODE-AUDIT.md` **NOT authored** (deferred to BACKLOG #100 reactivation cycle).
- `S3-CODE-AUDIT.md` **NOT authored** (deferred to BACKLOG #100 reactivation cycle).
- `S2-SNAPSHOT.md` **authored** at `docs/01_refer/ARCHIVES/SNAPSHOT/S2-SNAPSHOT.md`.
- `S2-RETRO.md` **authored** at `docs/01_refer/ARCHIVES/RETRO/S2-RETRO.md`.
- `S3-SNAPSHOT.md` **authored** at `docs/01_refer/ARCHIVES/SNAPSHOT/S3-SNAPSHOT.md`.
- `S3-RETRO.md` **authored** at `docs/01_refer/ARCHIVES/RETRO/S3-RETRO.md`.

### Sprint Metrics (cumulative)

| Sprint | Tests | CRITICAL | HIGH | MEDIUM | LOW | LOC (src/) |
|--------|-------|----------|------|--------|-----|------------|
| S1 | 32 | 1 | 3 | 16 | 14 | 16,061 |
| S2 | 32 | — | — | — | — | 20,157 |
| S3 | 32 | — | — | — | — | 25,582 |

S2 + S3 audit severity rows blank — deferred per BACKLOG #100. Authoritative source: `S2-SNAPSHOT.md` + `S3-SNAPSHOT.md`.

### Production readiness assessment

**Demo-grade.** Audit + polish required before production promotion. Gates:
1. BACKLOG #100 — Audit cycle reactivation (CRITICAL).
2. BACKLOG #97 — Backend `POST /bookings/{id}/leave` (P2; backend coord).
3. BACKLOG #99 — Backend public master endpoint (P2; backend coord; lifts C51 from degraded v1 to full skin 25 fidelity).
4. BACKLOG #96 — `velo update` script transient (P2; server-side fix candidate).
5. 23 mock-pending items in BACKEND-COORDINATION.md § A/B/C (search, support, messaging, AI commentary, language enum, master public stats, leave endpoint).

---

## S4 Cleanup — 2026-05-05

### From BACKLOG.md (main body — CLOSED/SUPERSEDED transferred)

- **#37** — Post-deploy visual verification of S1 pilot screens — CLOSED 2026-04-30 (S2 P05 C15 staging push verification gate; deploy `ad4ce7d`).
- **#48** — Confirm-modal unification — CLOSED 2026-05-01 (S4 P14 MEGA-3 via shared `ConfirmModal.vue` extraction; VModal direct view-side adoption remains 0; indirect chain via BookingPopup + CancelBookingPopup → MyBookingsView preserved pending legacy view migration).
- **#55** — SERVER-ACCESS.md population (pre-S2 Human action) — CLOSED 2026-04-30 (populated by Human; deploy procedure documented).
- **#72** — Designer: Master-side batch (10 views) — SUPERSEDED 2026-05-01 by decision #050 (S4 proceeded without designer batch; UI-mockups + user-role pattern reuse). Re-evaluate at S5+ if designer delivers.
- **#98** — Emoji cleanup MEGA-2 carry (23 in-scope hits remaining) — CLOSED 2026-04-30 MEGA-2 close (emoji audit grep returns 0 hits across 12 files in scope).
- **#102** — P14 master views visual verify deferred — CLOSED 2026-05-04 (S4-P15 combined verify gate; folded with P15 admin verify per speedrun #052).

### From BACKLOG.md (status-flipped during S4-Clean-Sync, then transferred)

- **#101** — ARCHITECTURE.md §Key Decisions counter drift (#001-#026 → #001-#052) — CLOSED 2026-05-05 by S4-Clean-Sync Step 2 edit B3 (counter line refreshed: `Decisions #001-#052 as of S4 close (2026-05-04)`).
- **#107** — S4-Clean-Sync doc-trail hygiene cluster (two sub-items) — CLOSED 2026-05-05 by S4-Clean-Sync Step 2:
  - sub-item .1 — decisions.md status column drift on #010 + #030 — flipped to `SUPERSEDED (by #051)` and `SUPERSEDED (by #050)` respectively (Step 2 edits A1 + A2).
  - sub-item .2 — FILE-TREE.md `components/shared/` annotation off-by-one (34 → 33) — corrected (Step 2 edit D1).

### From BACKLOG.md (legacy table — CLOSED rows transferred)

- **Row 24** — Regen workflow integration (post-backend Pydantic changes) — CLOSED 2026-04-30 (workflow documented in BACKEND-COORDINATION § D).
- **Row 26** — A.2 follow-up: financial constants migration — CLOSED 2026-04-30 (S2 P05 C15 regen surfaced limit fields).
- **Row 27** — Zodd CRITICAL #1: PracticeSummary.timezone fix — CLOSED 2026-04-30 (S2 P05 C15 self-host regen).
- **Row 32** — TopupRequest / TopupResponse type duplication — CLOSED 2026-04-30 (S2 P05 C15 consume via `@/api/types` re-export).

### From ENVIRONMENT.md

- Quality Tools table — Pre-commit row dropped 2026-05-05 (no consumer, no candidate BACKLOG entry; ghost row from S1 era; can be re-added if pre-commit setup becomes a real priority).

### Stale Files Archived

- None (no archive threshold reached: current=S4, archive trigger at S(-6)).

### Counts

- Entries transferred: 12 (6 main-body CLOSED/SUPERSEDED + 2 status-flip + 4 legacy-table)
- Entries retained as ambiguous-but-kept: 1 (legacy table row 20 — B.2 cancelBooking false-positive ledger; audit reference)
- Doc rows dropped: 1 (ENVIRONMENT.md pre-commit Quality Tools row)
- Sprint folders archived: 0

---
