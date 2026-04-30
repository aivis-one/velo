# Velo design batch — 2026-04-30 inventory

> Designer batch per decision #029 (supersedes bundle visual layer for S2/S3 user-role views; bundle 2026-04-23 retained for tokens per #029 ~80% retention).
> Source: Claude Design handoff URL `https://api.anthropic.com/v1/design/h/pOHHpDU7G3pPpQpWTEf8eg`
> Fetched: 2026-04-30
> Total files: 50 (fetched) + 1 (this inventory) = 51 committed

---

## Skin index (Phase 06 — auth + onboarding, S2)

All 8 phase-06 skin mockups present at `project/uploads/`.

| Skin | Filename | Phase / cycle | Notes |
|---|---|---|---|
| 01 | `project/uploads/01_Welcome.png` | C16 PWA branch | Welcome (PWA standalone). Variant `01_Welcome-d8751fbb.png` is alternate take — see Other assets. |
| 02 | `project/uploads/02_Login.png` | C17 | Login (email + password + Google/Apple OAuth buttons per decision #028) |
| 03 | `project/uploads/03_Register.png` | C18 | Register (name + email + password + ToS + OAuth) |
| 04 | `project/uploads/04_OAuth.png` | C19 | OAuth callback loading state |
| 05 | `project/uploads/05_Onboarding 1.png` | C20 slide 1 | Onboarding intro 1 (carousel index 0) |
| 06 | `project/uploads/06_Onboarding 2.png` | C20 slide 2 | Onboarding intro 2 (carousel index 1) |
| 07 | `project/uploads/07_Onboarding 3.png` | C20 slide 3 | Onboarding intro 3 (carousel index 2) |
| 08 | `project/uploads/08_Onboarding 4.png` | C21 | Onboarding 4 — **likely** timezone capture per S2-SPRINT.md C21 plan (`OnboardingTimezoneView: city input + autocomplete + IANA resolution + PATCH /users/me`). Designer numbered by sequence position; "4" = 4th onboarding step which the plan identifies as timezone capture. **Ambiguity**: filename says "Onboarding 4" not "Timezone" — verify intent at OPEN §3 Design Review by opening the PNG. If skin 08 is a 4th intro slide rather than timezone capture, C20 may need to extend to 4 slides and C21 will need designer follow-up for a timezone-specific skin. |

**8/8 skin files PRESENT.** C16–C21 design-port pipeline unblocked once skin 08 intent is verified.

---

## Skin index (S2 Phase 07–09 + S3 — TBD)

This batch contains **only** the 8 Phase-06 skins (auth + onboarding). No skins for S2 P07 (Dashboard refresh / Calendar / Theme toggle), S2 P08 (Booking / Practice flow), S2 P09 (Profile basics), or S3 (Diary / Messages / Profile sub) are in this batch.

| Cycle | Skin needed | Status |
|---|---|---|
| S2 P07 C22 — UserDashboardView refresh | Dashboard mockup | NOT IN THIS BATCH — designer follow-up required |
| S2 P07 C23 — CalendarView root | Calendar mockup | NOT IN THIS BATCH — `project/preview/13-calendar.html` may serve as DS reference but is component-card not full screen |
| S2 P07 C24 — Calendar filter overlay | Filter overlay mockup | NOT IN THIS BATCH |
| S2 P07 C25 — Theme toggle infra | (tokens only — no screen needed) | DS reference cards `project/preview/02-colors-*.html` + `05-type-display.html` cover token side |
| S2 P08 C26–C32 — Booking + practice flow | 7 screen mockups | NOT IN THIS BATCH — designer follow-up required |
| S2 P09 C33–C34 — Profile basics + Edit | 2-3 screen mockups | NOT IN THIS BATCH — designer follow-up required |
| S3 — Diary / Messages / etc. | ~15+ screen mockups | NOT IN THIS BATCH — separate designer batch expected |

**Open BACKLOG candidate** (not auto-created here — defer to S2 P07 OPEN if still gap): "Designer batch S2 P07–P09 mockups — request from designer". For now Phase 06 is unblocked and S2 P07+ planning continues per the existing S2-SPRINT.md cycle table.

---

## Skin 08 ambiguity flag

The Phase 06 plan in S2-SPRINT.md identifies C21 as `OnboardingTimezoneView` with `city input + autocomplete + IANA resolution + PATCH /users/me; complete onboarding flag в localStorage`. Skin filenames in this batch label slides 05–08 as `Onboarding 1–4` without specifying which is the timezone screen.

Two possibilities:

- **(A)** Skin 08 IS the timezone capture screen, named by sequence position. C20 carousel = 3 intro slides (skins 05–07), C21 = skin 08. Aligns with S2-SPRINT.md plan.
- **(B)** Skin 08 is a 4th intro slide and timezone capture was not designed. C20 needs to extend to 4-slide carousel; C21 timezone screen requires designer follow-up.

**Resolution**: OPEN §3 Design Review for Phase 06 must open `project/uploads/08_Onboarding 4.png` and verify intent. If (A) confirmed → proceed. If (B) confirmed → spawn BACKLOG entry "Designer follow-up: skin 08 is intro slide, need separate timezone-capture mockup for C21" and adjust C21 plan.

---

## Other assets — non-screen content

### Design-system reference cards (S2 P07+ relevant)

15 preview HTML cards at `project/preview/01-logo.html` … `project/preview/15-chips.html`. Cross-reference targets:

- `13-calendar.html` → S2 P07 C23 CalendarView
- `09-buttons.html` + `10-inputs.html` + `11-cards.html` + `15-chips.html` → S2 P08 booking flow + reusable
- `12-tabbar.html` → existing VTabBar refresh candidate
- `02-colors-primary.html` … `06-type-scale.html` → S2 P07 C25 theme toggle reference; `probekit-design-audit` `brand_ref` candidate repoint at S2-Clean-Sync (currently points at bundle 2026-04-23 per decision #026)

### Brand assets

6 files at `project/assets/brand/`: `mandala-large-mask.svg`, `mandala-mask.svg`, `page-bg.png`, `photo-1.png`, `photo-2.png`, `velo-emblem.svg`.

### Designer ↔ Claude Design transcripts

`chats/chat1.md` + `chats/chat2.md` — design intent context; valuable for execute prompts at C16–C21 design time. Convention not yet in ARCHITECTURE.md (lands at S2-Clean-Sync).

### Duplicates / handoff fidelity

- `project/fonts/Marmelad-Regular.ttf` — 3rd copy (already at `frontend/public/fonts/` runtime + duplicated inside `project/uploads/`); preserved per bundle precedent.
- Root `README.md` — generic Claude Design boilerplate; preserved for fidelity. Substantive spec is `project/README.md`.

### Scratchpad / ambiguous

- 4 unnamed SVGs (`Group.svg`, `Group-1.svg`, `Group-2.svg`, `Group 1945.svg`) — Figma-export decoratives; intent unclear without context.
- 5 paste-clipboard PNGs (`back.png`, `pasted-*.png`) — designer scratchpad; preserved as-is.
- `01_Welcome-d8751fbb.png` — variant of `01_Welcome.png`; treat as alternate.
- `screenshots/welcome.png` — preview screenshot, likely matches skin 01.

---

## Provenance

- **Decision**: #029 (2026-04-30) — new design batch supersedes bundle visual layer
- **Bundle retained for tokens**: `docs/04_assets/velo-design-system-2026-04-23/` (per #029 ~80% retention)
- **Fetched into repo by**: S2-P06-PREREQ-FETCH-DESIGN-BATCH execute prompt (resolves S2-P06-OPEN §2 §S1 prerequisite gap)
- **Rule 29 (persist-or-lose) first applied**: this commit
- **Discrepancy with decision #029 narrative**: #029 cites "~55 mockups, ~34 unique views". Actual fetch is 50 files total — 8 phase-06 skin PNGs + 15 DS reference HTML cards + 6 brand assets + 2 chat transcripts + assorted scratchpad. Numbers in #029 appear approximate. Actual content shape is the 8 phase-screens + DS reference layer — sufficient for Phase 06; insufficient for S2 P07+ (next designer batch needed).
