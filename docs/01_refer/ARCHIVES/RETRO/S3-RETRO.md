# RETRO — Sprint 3: User Content (Diary + Messages + AI + Profile sub)

> SPEC v3.2-velo
> Date: 2026-04-30
> Status: CLOSED — process observations only (Carry-Forward in S3-SNAPSHOT.md)

---

## Process observations

S3 was the second half of the speedrun (decision #049). Where S2 stretched the protocol stack at non-pilot density, S3 collapsed 17 implementation cycles (C36-C52) into a single mega-execute prompt (MEGA-2, commit `af39b41`). The result — 65 files / +6443 LOC / 0 typecheck errors / 0 lint warnings on first build attempt — validated the pattern at full speedrun density. Three new patterns landed (mockMessagesData, degraded v1, large-scale component reuse) that are worth documenting for future demo-target sprints.

---

## What worked

### mockMessagesData.ts inline pattern (§C49)

Messages list + thread views needed believable content for the demo (3 conversations, varying counterparty roles, unread state, timestamps). Backend coordination § A.7 was nowhere near landing. The solution was a named utility file `frontend/src/utils/mockMessagesData.ts` with typed `Conversation` + `ConversationMessage` exports + 3 conversations × 2 messages mock fixtures. The store (`stores/messages.ts`) imports the fixtures, deep-clones to `ref` state, exposes `setActiveConversation` + `sendMessage` (which fires `toast.info('Сообщения скоро будут доступны')`).

Pattern: when backend coordination lags but UI surface is rich, ship a named mock fixture file with proper TypeScript types. Replace the import with API call when the endpoint lands; the rest of the store + views need no refactoring. This is structurally cleaner than inlining the fixtures inside the store, because the swap surface is one line.

### Degraded v1 strategy (§C51 MasterProfilePublicView)

The Master public profile view (skin 25) needs 6 backend fields not present in the current API: `bio`, `methods`, `experience_years`, `practice_count`, `review_count`, `is_verified`. There's no `GET /api/v1/masters/{id}` public endpoint at all. Speedrun mode (#049) doesn't have time for backend coordination round-trips.

The solution was to ship a **degraded v1**: derive name + avatar from `getPractices({ master_id }).first().master_name + master_avatar_url` (single API call), render bio/methods/experience as placeholder text "Информация о мастере временно ограничена", hide stat cards entirely. The view is functional + visually identifiable + has a working "Ближайшие практики" section + "Задать вопрос" CTA → toast. BACKLOG #99 contains the exact backend lift list to take this from degraded v1 to full skin 25 fidelity.

Pattern: when backend coordination is incomplete and full fidelity isn't achievable in-cycle, ship a degraded surface with documented gaps. Inline code comment + BACKLOG entry. Frontend is functional; backend lift is itemized. Avoids both blocking on backend and shipping nothing.

### ProfileMenuItem reuse across 6+ rows (§C33 → C46-48 → C52)

The shared `ProfileMenuItem` component (extracted in MEGA-1 for UserProfileView §C33) absorbed 8+ menu rows across MEGA-2: Edit profile / Reservations / Messages / Notifications / Language / Support / Logout / etc. Each call site is `<ProfileMenuItem :icon="..." :label="..." :to="..." :badge="..." />` — no parameterization stress, no per-instance variants. The component takes icon component + label + optional to/href + optional badge + emits click.

Validates the component extraction threshold: when 3+ similar interactive rows appear in a single view, extract to shared component. The reuse compounds across views (UserProfile + multiple sub-views all use the same row primitive). Pattern documented for future menu / list / row scenarios.

### Emoji audit cleanup pattern (BACKLOG #98 RESOLVED)

Decision #048 (no-emoji) landed mid-MEGA-1; not all emoji hits could be cleaned in-cycle. BACKLOG #98 captured the carry: 23 in-scope hits in 12 files (DiaryList, BookingCard, PracticeCard, FormShell, CancelBookingPopup, DiaryCheckin/Feedback/EntryDetail, DiaryEntryForm, MyBookingsView, TopupCancel/SuccessView, adminHelpers). At MEGA-2 close, all 12 files were touched + cleanup grep returned 0 in-scope hits. BACKLOG #98 RESOLVED.

Pattern: when a refactoring rule lands (e.g. #048 no-emoji), surface the cleanup as a BACKLOG ticket with explicit grep audit. Resolve incrementally over subsequent cycles touching affected files. Compute audit at close; close condition is 0 hits in scope. Avoids big-bang refactor commits while ensuring nothing gets forgotten.

### Composer expand modal split (§C40 vs §C36)

The Diary composer needed two states: collapsed (pill at bottom of Diary view) and expanded (full-screen modal with title + textarea + mood + practice picker). Splitting these into two components — `DiaryComposer.vue` (collapsed pill) + `DiaryComposerExpanded.vue` (modal) — kept each component focused. The collapsed pill emits `expand`; the parent toggles modal-open state; the modal handles the form. Submit calls existing `useDiaryStore.createEntry` so backend-side is unchanged.

Pattern: when a UI primitive has clearly distinct collapsed vs expanded states with different concerns (display vs form), split into two components rather than v-if conditional inside one. The interface is `emit('expand')` from collapsed → parent state → modal open. Reusable across DiaryView + sub-route views (Checkins/Feedbacks/Entries each instantiate the modal independently).

---

## What didn't work

### Bash-bridge stdout buffering on Windows (post-MEGA-2 deploy)

The first MEGA-2 deploy via paramiko was launched as a background Bash task. The Python process completed successfully (containers Up, HEAD updated, services Healthy) but stdout was held in buffer for ~10 minutes before flushing. The completion event eventually fired. Not a deploy issue; a tooling latency quirk on Windows. Documented in S2-RETRO and again here. Going forward: run paramiko deploys synchronously to avoid buffer-flush surprises. Single occurrence in 4 deploys; not worth a BACKLOG entry yet.

### "Already up to date" race when retrying after lost output

Because the first MEGA-2 deploy's output was lost in buffer, I ran a synchronous follow-up to confirm state. The follow-up hit "Already up to date" (deploy was already done) — useful confirmation, but for ~30 seconds I thought the deploy hadn't run. Pattern: for paramiko deploy verification, always run a fresh `git rev-parse HEAD` + `docker ps` post-flight inside the same script as the deploy itself, so stale-output and lost-output scenarios are unambiguous.

### Spine ornament SVG glyphs deferred (Path Y MEDIUM trade)

The skin 40 timeline shows ornate "▶ date ◀" arrow glyphs as the SpineDivider. Path Y MEDIUM ships these as text characters (`▶`) rather than custom SVG. The visual fidelity is MEDIUM; pixel-perfect ornament work is deferred to S5+ polish cluster per decision #047. This is a known-and-accepted trade — but the gap is visible to anyone comparing skin to staging. BACKLOG NIT entry would help; logged here for next polish cycle planning.

---

## Process refinements (carry to S4+)

### MEGA-execute split rule of thumb

S2 (MEGA-1) was 14 cycles / +5218 LOC / 107 files. S3 (MEGA-2) was 17 cycles / +6443 LOC / 65 files. Both completed cleanly on first build attempt. The natural ceiling is somewhere around 6500-8000 LOC per MEGA based on context budget. Beyond that, split into multiple MEGAs or revert to per-cycle. Documented for future speedrun planning.

### Mock fixture utility file pattern

When a backend feature is mock-only (no API call), the mock data lives in `frontend/src/utils/mock<Feature>Data.ts` with proper TypeScript types. Store imports + deep-clones to ref state. Replace the import with `from '@/api/<feature>'` when endpoint lands. Pattern reusable for future C-equivalent integrations (notifications real backend, AI summary content from backend, etc.).

### Degraded v1 + BACKLOG lift list pattern

When shipping a feature with incomplete backend, document the exact lift list in BACKLOG before commit. Frontend code includes inline comment pointing to the BACKLOG entry. View is functional + visually identifiable. Avoids both blocking on backend and shipping nothing. Reusable for any future feature where backend coordination is incomplete but UI surface needs to ship.

---

*Retro authored at S2-S3-Speedrun closure (sponsor-demo target).*
*Process observations only — Carry-Forward authoritative source: S3-SNAPSHOT.md.*
