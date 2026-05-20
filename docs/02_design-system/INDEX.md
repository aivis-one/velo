# VELO Design System — Index

Last updated: 2026-05-20
Iteration: 23 (MOCKUP GATE session 18 — DS component fixes: .section-title font-weight:700, .pc-title font-weight:700, .pc-avatar 38→48px in _shared/components.css; .top-header promoted to ✅ canon in COMPONENTS-CATALOG)
Status: **TOKENS GATE ✅ passed · INVENTORY GATE ✅ passed · STYLEGUIDE GATE ✅ passed · 🎉 DS COMPLETE GATE ✅ PASSED 2026-05-19 (operator confirmed) · Macro-Phase II active — Dashboard 9 MOCKUP GATE in progress (screens 01-03 ✅ pixel-fixed, screens 04-09 pending). Calendar 11 awaiting MOCKUP GATE after Dashboard.**

> Template per VELO-METHODOLOGY.md §12.4. This file is the local catalog
> of the design system. It is updated **immediately** after any DS change
> per §12.2.

---

## Token Status

| Group | Tokens defined | Source | Missing |
|---|---|---|---|
| Colors / Primitives | 36 | 12 figma.variables + 24 promoted from 17-screen mining | — |
| Text semantic | 5 | mapping to steel/neutral primitives | — |
| Background semantic | 4 (screen, input, card, card-subtle) | mapping to white + alpha-steel-light-15 | — |
| Buttons (bg) | 2 (primary, glass) | mapping to steel-light + alpha-white-66 | — |
| Borders | 3 (default, input, button) | mapping to neutral-300 + white | — |
| Icons | 1 (default) | mapping to steel-primary | — |
| Dots | 2 (active, passive) | mapping to steel-primary + alpha-steel-60 | — |
| States — Success | 4 (state, text, bg-soft, bg-tint) | teal family from Dashboard mining | — |
| States — Warning | 4 (state, text, bg-soft, bg-tint) | orange family | — |
| States — Error/Destructive | 4 (state, destructive, text, bg-soft) | coral family | — |
| States — Info | 2 (bg-soft + state) | blue-50 + state-info `#619cd2` (resolved via full mining) | — |
| Interactive | 5 placeholders | neutral defaults | placeholders (no hover/active observed in SACRED) |
| Spacing | 14 (0..25) | DSYS-era 4-base scale (provisional) | — |
| Radius | 8 (xs, **4**, sm, 9, md, lg, xl, pill) | promoted from full mining; `--velo-radius-4: 4px` added Calendar 11 harvest 2026-05-18 | radius-full (not observed) |
| Shadows | 2 glow + 2 blur + card + modal | card/modal added Sprint 2 Phase 3 cleanup with neutral defaults | — |
| Font family | 1 (Marmelad Regular) | figma.textStyles | — |
| Font sizes | 7 (12/14/15/16/18/20/32) | text styles + new 15px from Dashboard | — |
| Weights | 1 (regular 400) | only one observed | — |
| Text styles (utility classes) | 6 (.velo-typo-*) | 1:1 from figma.textStyles with pixel lineHeights | — |

---

## Component Status

> **Master catalog with full per-component profile lives in [`COMPONENTS-CATALOG.md`](./COMPONENTS-CATALOG.md).** That file has the **mandatory before-naming check rule** for every session — read it before inventing a new CSS class name in a mockup.
> This table here is a quick-glance index. Each row has a counterpart entry in the catalog with class names, variants, states, when-to-use, anti-patterns, tokens consumed, related components, provenance, status.

Components visualised in `styleguide/velo-design-system.html` (Sprint 2 Phase 3 ✅).

| Component | Tier | Status in styleguide | Vue file (Sprint 3+) |
|---|---|---|---|
| VButton (primary / glass / oauth / destructive) | 1 | ✅ visualised | ⬜ |
| VInput | 1 | ✅ visualised | ⬜ |
| VCheckbox | 1 | ✅ visualised | ⬜ |
| VBadge (success/warning/error/info/neutral) | 1 | ✅ visualised | ⬜ |
| VAvatar (sm/md/lg, initials-based) | 1 | ✅ visualised | ⬜ |
| VLoader | 1 | ✅ visualised | ⬜ |
| VToast (success/warning/error/info) | 1 | ✅ visualised | ⬜ |
| PracticeCard | 2 | ✅ visualised | ⬜ |
| BookingCard | 2 | ✅ visualised | ⬜ |
| WaitlistCard | 2 | ✅ visualised | ⬜ |
| PriceDisplay | 2 | ✅ visualised | ⬜ |
| BalanceChip | 2 | ✅ visualised | ⬜ |
| MasterStatusBadge | 2 | ✅ visualised | ⬜ |
| FeedbackWidget | 2 | ✅ visualised | ⬜ |
| MoodWidget | 2 | ✅ visualised | ⬜ |

**New components surfaced during Phase 4 (Onboarding mining)** — awaiting promotion to styleguide after Onboarding block MOCKUP GATE:
`v-input` (pill-shape with blur), `v-back-arrow`, `v-link`, `v-divider` («или» line), `v-dots` (carousel pagination), `v-button--oauth` (Google/Apple), `v-button--glass` (new canon: white outline + halo + 5% blue bg), `velo-header-compact` (mini-mandala + wordmark), `velo-bg-mandala` (full-screen watermark), `velo-skip` (top-right link), illustration slot.

---

## Asset Index

See `assets/ASSETS-INDEX.md` for the full asset list with source node IDs.

- Icons: **75 SVG canon icons** (73 after dedup pass + 2 new master nav icons: icon-master-nav-schedule + icon-master-nav-profile; icon-master-nav-students replaced with correct path) — see `assets/ASSETS-INDEX.md` (ASSETS-INDEX iter 14, 78 total including logos)
- Backgrounds: 1 PNG (`velo-bg-app.png` — universal app background, from Figma 01_Welcome)
- Fonts: 1 TTF (`Marmelad-Regular.ttf` — self-hosted, OFL)
- Screenshots: 94 of 97 SACRED PNG (user 55 + master 39) + 1 admin legacy HTML reference

---

## Open TODOs

- [x] Sprint 1 Phase 1 — 97 of 97 SACRED screens mined (full extension complete 2026-05-17).
- [x] Sprint 1 Phase 2 — `variables.css` + `global.css` (master + deliverable, MD5-identical).
- [x] **TOKENS GATE (§10.2)** — passed by operator via `tokens-preview.html` visual validation.
- [x] **INVENTORY GATE (§10.1)** — passed. 94 PNG + 2 DS icons + 1 legacy admin HTML in place.
- [x] Operator decision on `--velo-shadow-card` / `--velo-shadow-modal` — added with real values during Sprint 2 Phase 3 cleanup.
- [x] Sprint 2 Phase 3 Styleguide HTML — closed. STYLEGUIDE GATE ✅ passed.
- [ ] Operator decision on 15px font size — still open; emitted as inline `font-size: var(--velo-size-15)` for now.
- [ ] **Sprint 2 Phase 4 (in progress)** — promotion of new Onboarding-mining components (`v-button--glass`, `v-input` pill+blur, `v-back-arrow`, `v-link`, `v-divider`, `v-dots`, `velo-header-compact`, etc.) into `styleguide/velo-design-system.html` + `tokens/variables.css`. Trigger: after Onboarding block MOCKUP GATE passes.
- [ ] Dark theme — deferred per VELO-METHODOLOGY §2.5 I7. Figma already has Dark mode primitives.

### Architectural finding for Sprint 7
- Admin role has **no Figma SACRED**. Visual design built from scratch using DS tokens + logic from `assets/screenshots/admin/admin-legacy-reference-v2.5.html`.

---

## Iteration Log

| Iteration | Date | What was done |
|---|---|---|
| 0 | 2026-05-17 | Folder structure created per VELO-METHODOLOGY §3. No extraction yet. |
| 1 | 2026-05-17 | Sprint 1 Phase 1 + Phase 2 draft. Live Figma probe via use_figma Plugin API → 12 figma.variables (8 primitives Light+Dark + 4 semantic aliases) + 6 figma.textStyles. Mockup-mining over 17 SACRED screens (Onboarding 8 + Dashboard 9) → 24 promoted primitives. `variables.css` 213 lines + `global.css` 103 lines drafted in master + sync'd to deliverable. Inventory `VELO-DS-INVENTORY.md` with Section A/B/C complete + provenance. |
| 2 | 2026-05-17 | Sprint 1 closure. TOKENS GATE ✅ + INVENTORY GATE ✅ passed. Full mining extension over remaining 80 SACRED screens (97 of 97 complete). New promoted primitives: state-info, radius-md, disabled-bg/text resolved, steel-pale, coral-darker, alpha-white-70/50/25, radius-xs, blur-glass-stronger. variables.css condensed to 169 lines. 94 PNG screenshots saved (operator UI export, role-organized). |
| 3 | 2026-05-17 | Sprint 2 Phase 3 closed — single production styleguide `velo-design-system.html` (Marmelad self-host via base64, 32 SVG icons in 5 categories, real card/modal shadow tokens added, glass shadows + pattern grid fix). STYLEGUIDE GATE ✅ passed. Sprint 2 Phase 4 started — Onboarding flow viewer with 8 columns (welcome at 80%, 5 pending fixes). 2 new DS assets: `velo-bg-app.png` (universal app background) + `velo-logo-mandala.svg` (Group 1944 brand logo). |
| 4 | 2026-05-18 | **COMPONENTS-CATALOG.md created.** Single MD master with full per-component profile (Class+Variants+States, When-to-use+Anti-patterns, Tokens, Provenance+Status). Before-naming check rule active. Cross-linked in INDEX.md and `_HANDOFF.md`. **Dashboard 9 Figma audit done** (`FIGMA-FINDINGS-DASHBOARD-9.md`). **3 bugs fixed in tokens/variables.css**: (a) `--velo-shadow-glow-white` spread 0 → 7px (Figma canon, Sprint 1 promotion accidental); (b) `-strong` variant spread 0 → 8.82px; (c) deliverable copy was missing all Sprint 2 Phase 4 promotions (drift 127 lines — "MD5-identical" entry in Daily log was wrong) — пересинхронизирован. **New token promoted**: `--velo-shadow-button-glass` (simplified single-white halo, Figma canon, alpha 0.8 per operator). Compound `--velo-shadow-button` остаётся только для primary. Onboarding + Dashboard viewers подхватили автоматически. |
| 5 | 2026-05-18 | **Card border + AlertPill promotion pass** (Dashboard 9 T3). `--velo-color-alpha-steel-30: rgba(76,101,137,0.30)` (Layer 1) + `--velo-border-card` (Layer 2 alias) promoted в master + deliverable — Figma uses 30% steel border, not 15%. Mass refactor 11 card borders в `_dashboard-flow.html`. **AlertPill variants formalised** in COMPONENTS-CATALOG: `--warning` (orange theme) · `--info` (teal theme) · `--error` (coral, reserved). HTML col 01/02 — semantic swap: "Пора на check-in!" — `--warning` (urgency), "Оставьте feedback!" — `--info` (invitation). Border weights pulled from Figma probe (`#76dde6@2-3`, `#fbc088@2`, `#f795a2@3`). |
| 6 | 2026-05-18 | **Methodology v1.3 + Roadmap v1.2 + Sprint 2.5 pivot — documentation closure.** Operator surfaced 2 systemic issues: per-element PNG reverse-engineering causes 3× rework; promoting tokens to `variables.css` without visualisation в `velo-design-system.html` breaks DS unity. **Methodology v1.3 amendments:** §6.8 DS Promotion Visualisation rule; §7.0 Block-Harvest-First (mandatory for SACRED blocks, 3 phases: Harvest → 5 deliverables → Mockup rebuild); §11.5 AP-P-6 (PNG reverse-engineering); §11.5 AP-P-7 (variables.css without styleguide). **Roadmap v1.2:** Sprint 2.5 inserted (DS Completion block-by-block Track A + CBSHOME foundation transfer Track B parallel). All 9 remaining SACRED blocks (Dashboard 9 + Calendar 11 + Profile 7 + Diary 20 + Messages 3 + Analytics 3 + Practices 15 + Master Dashboard 8 + Master Onboarding 13) processed in Sprint 2.5 before Sprint 3 starts. `_HANDOFF.md` v1.2 — Block-Harvest-First + DS Visualisation rules в правилах поведения; entry point switched to Sprint 2.5. `_dashboard-flow.html` flagged 🗑 superseded — rebuild after Dashboard 9 DS-complete. No DS content changes in this iteration — only methodology + roadmap + tracker docs. |
| 7 | 2026-05-18 | **English-default rule + Standalone Sprint 2.5 cleanup — second closure session.** Operator audit found 2852 Cyrillic occurrences across 29 docs files; process docs in Russian cost ~2× tokens per session read. Methodology bumped **v1.3 → v1.4** (§1.1 P6 English-default + §11.5 AP-P-8 with exception table for UI sample data / operator quotes / external inputs). Roadmap bumped **v1.2 → v1.3** (Sprint 2.5 gains Track C — Documentation English translation pass, 4 sub-phases Conv-1..Conv-4). Sprint 2 formally closed (sprint-02.md `Status: closed`). New file **sprint-02.5.md created** per methodology §15.1 — standalone sprint, three tracks A+B+C. HANDOFF bumped **v1.3 → v1.4** (Шаг 4 → sprint-02.5.md, English rule in behavior section, startup prompt reminder). All version cross-refs reconciled. Conversion of legacy Russian remains scheduled work in Sprint 2.5 Track C — not done in this session. |
| 8 | 2026-05-18 | **Dashboard 9 Block-Harvest-First — Phase A+B+C complete.** 13 icon SVGs exported from Figma via `exportAsync` (nodes `541:6699`..`541:7628`) → saved to `assets/icons/`. ASSETS-INDEX bumped v1.0→v1.1 (21 total icons). 2 new tokens promoted to `variables.css` master + deliverable (MD5 `e8e37faecb9386e8491e8e71df2ceed3`): `--velo-color-amber-50` + `--velo-blur-layer`. COMPONENTS-CATALOG: 3 new candidates — BottomNav, PaidBadge, MasterTagChip. Styleguide `velo-design-system.html` updated: amber-50 swatch, blur-layer effect card, Dashboard 9 icon group (13 imgs). `_dashboard-flow.html` DS-complete: real Figma SVG icons throughout (nav, practice, verified, calendar, time, mood, warning), paid-badge + master-tag-chip components, token bridge patched. Ready for MOCKUP GATE. |
| 10 | 2026-05-18 | **Calendar 11 DS harvest — Block-Harvest-First Phase A+B complete.** 8 icon SVGs exported from Figma via `exportAsync` (nodes `648:1764`, `648:1768`, `648:1774`, `648:2030`, `648:1872`, `648:1756`, `648:1759`, `541:2354`) → saved to `assets/icons/`. 1 new token promoted to `variables.css` master + deliverable (MD5-mirror): `--velo-radius-4: 4px` (filter chips + small card elements, Calendar frames 24–30). ASSETS-INDEX bumped v1.1→v1.2 (29 total icons). COMPONENTS-CATALOG v1.0→v1.1: 6 new candidates — CalendarGrid, CalendarDayCell, PracticeMetaRow, FilterChip, FilterSheet, FeedbackRating. Styleguide `velo-design-system.html` updated: `--velo-radius-4` swatch (highlighted ★ new), Calendar 11 icon group (8 imgs). Macro-Phase I: 3/10 blocks DS-complete. |
| 11 | 2026-05-18 | **Sprint 2 Quality Audit — 4 gap icons recovered.** Operator audit of icon gallery completeness. Found 4 genuine gaps in already-completed blocks: `icon-feedback-questions.svg` + `icon-feedback-good.svg` + `icon-feedback-fire.svg` (Calendar 11 FeedbackRating, `541:2326/2334/2341`) + `icon-checkin-success.svg` (Dashboard check-in success, `541:6988`). All 4 extracted via `exportAsync`, saved to `assets/icons/`. Styleguide `velo-design-system.html` icon gallery updated (+4). ASSETS-INDEX.md updated. COMPONENTS-CATALOG truncation fixed (3 missing Calendar 11 entries restored). sprint-02.md + INDEX.md updated. Icon count: 29→33. |
| 12 | 2026-05-18 | **Master Onboarding illustrations extracted (Task #16).** 4 illustrations from Figma Master Onboarding block (`758:4694` welcome / `758:4700` space / `758:4707` analytics / `758:4714` approved) exported and saved to `assets/icons/`. `icon-master-approved.svg` required 3-chunk path data extraction (62KB SVG, 20KB MCP limit) — fill-only strategy yielded 9-path 30KB file. All 4 added to `velo-design-system.html` gallery + `ASSETS-INDEX.md` new section. Icon count: 33→37. |
| 14 | 2026-05-19 | **Profile 7 DS Harvest — Block-Harvest-First Phase A+B complete.** Figma root `541:2355`, 7 SACRED frames walked. **Zero new tokens** — all Profile 7 fills/radii/effects map to existing DS tokens. 9 SVG icons exported via `exportAsync`: `icon-profile-{edit,bookings,messages,support,notifications,language,logout,delete,timezone}`. Destructive icons (logout + delete) use `#AD3444` (`--velo-color-coral-darker`). Timezone icon uses `#ffffff` fill (designed for steel-primary bg). 1 icon unavailable: `icon-profile-share` (no visible layers in Figma). ASSETS-INDEX.md iteration 5 (38→47 icons; note: previous count of 37 was off-by-one — actual was 38). COMPONENTS-CATALOG v1.1→v1.2: 4 new candidates — ProfileSettingsRow, ToggleSwitch, ConfirmationDialog, ProfileHeader. `velo-design-system.html` updated: Profile 7 icon group (9 imgs, timezone on dark bg). **Macro-Phase I: 4/10 blocks DS-complete. Next: Diary 20 (`541:2816`).** |
| 16 | 2026-05-19 | **Messages 3 DS Harvest — Block-Harvest-First Phase A+B complete.** Figma root `541:2717`, 3 SACRED frames walked (80_Messages, 81_Thread, 82_Thread Support). **Zero new tokens** — all Messages 3 fills/radii/effects map to existing DS tokens. Glass input bar reuses established canon: `--velo-color-alpha-steel-light-15` fill + `--velo-shadow-glow-white-strong` + `--velo-blur-glass-stronger`. 1 SVG icon exported via `exportAsync`: `icon-messages-send` (Group 2356 `541:2785`, 40×40, steel-light circle + white arrow). Back-arrow already in DS. ASSETS-INDEX.md iteration 7 (58→59 icons). COMPONENTS-CATALOG.md v1.3→v1.4: 3 new candidates — MessageConversationRow, MessageBubble, MessageInputBar. `velo-design-system.html` updated: Messages 3 icon group (1 img). **Macro-Phase I: 6/10 blocks DS-complete. Next: Analytics 3 (`758:1529`).** |
| 17 | 2026-05-19 | **Practices 15 DS Harvest — Block-Harvest-First Phase A+B complete.** Figma root `758:1950`, 15 SACRED frames walked (241_Practices upcoming → 255_Attendance 2). **Zero new tokens** — all Practices 15 fills/radii/effects map to existing DS tokens. 5 SVG icons exported via `exportAsync`: `icon-practices-add` (20×20 white "+" Union, FAB CTA), `icon-practices-attendees` (16×15 3-person group, fill #4C6589), `icon-practices-repeat` (15×15 circular repeat arrows, fill #4C6589), `icon-practices-review-face` (15×15 smiley face, fill #4C6589), `icon-practices-warning` (29×26 orange-light warning triangle, fill #FBC088, distinct from existing icon-warning which uses #A16124). ASSETS-INDEX.md iteration 8→9 (65→70 icons). COMPONENTS-CATALOG.md v1.5→v1.6: 4 new candidates — MasterPracticeCard, PracticesFAB, PracticeWarningPanel, CreatePracticeWizard. `velo-design-system.html` updated: Practices 15 icon group (5 imgs, add icon on steel-primary bg, warning on orange-50 bg), icon count 65→70. **Macro-Phase I: 8/10 blocks DS-complete. Next: Master Dashboard 8 (`758:3246`, 8 screens).** |
| 15 | 2026-05-19 | **Diary 20 DS Harvest — Block-Harvest-First Phase A+B complete.** Figma root `541:2816`, 20 SACRED frames walked (37_Diary All Map → 52_Edit Entry). **Zero new tokens** — all Diary 20 fills/radii/effects map to existing DS tokens (`#627A9C`→steel-light, `#4C6589`→steel-primary). 11 SVG icons exported via `exportAsync`: `icon-diary-tab-all` (40×40 filter tab), `icon-diary-edit` (17×20 white-fill edit), `icon-diary-filter-n5..n11` (38×38 numeral rating chips, 7 items), `icon-diary-pin` + `icon-diary-pin-alt` (28×34 ornate map pins, ~31KB each, extracted via 3-chunk base64 transport). 4 icons unavailable (stroke-only/no visible layers): location marker, view-toggle buttons, round header action buttons. ASSETS-INDEX.md iteration 6 (47→58 icons). COMPONENTS-CATALOG v1.2→v1.3: 6 new candidates — DiaryMapView, DiaryFilterBar, DiaryRatingSelector, DiaryFilterModal, DiaryEntryCard, DiaryEntryView. `velo-design-system.html` updated: Diary 20 icon group (11 imgs, edit shown on dark bg). **Macro-Phase I: 5/10 blocks DS-complete. Next: Messages 3 (`541:2717`).** |
| 19 | 2026-05-19 | **Master Onboarding 13 DS Harvest — Block-Harvest-First Phase A+B complete. 🎉 DS COMPLETE GATE condition met.** Figma root `758:4318`, 13 SACRED frames walked. **Zero new tokens** — all values map to existing DS. 4 canonical SVG icons: `icon-master-onb-community` (`758:4756`), `icon-master-onb-workspace` (`758:4772`), `icon-master-onb-ai` (`758:4796`), `icon-master-application-rejected` (`758:4733`). 3 stale duplicate files (welcome/space/analytics from iteration 12) deleted — identical content to community/workspace/ai, wrong names. `variables.css` MD5 verified unchanged: `eb30f5ddf863fb9fa4d55d6d8174f80f`. ASSETS-INDEX iteration 10→11 (76→77 icons after dedup). COMPONENTS-CATALOG v1.7→v1.8: 6 new ⬜ candidates — MasterLandingCard, MasterApplicationWizard, ApplicationStatusCard, MasterOnboardingStep, SpecializationSelector, FileUploadField. `velo-design-system.html` updated: Master Onboarding 13 icon group (+4), icon count 76→77. **All 10 Macro-Phase I blocks DS-complete. DS COMPLETE GATE awaiting operator validation.** |
| 18 | 2026-05-19 | **Master Dashboard 8 DS Harvest — Block-Harvest-First Phase A+B complete.** Figma root `758:3245`, 8 SACRED frames walked. **4 new Layer 1 tokens promoted** (DS iteration 10): `--velo-color-steel-wash` #dce6f3, `--velo-color-teal-wash` #bdecf1, `--velo-color-coral-wash` #f9cbd1, `--velo-color-peach-wash` #fddfc4 — mood gradient palette, 27 occurrences across Student Profile + Check-ins frames. `#abbfda@15%` in MasterStatCard bar chart below promotion threshold — kept component-local. `variables.css` master + deliverable MD5-mirrored; `_shared/tokens.css` synced (§7.3). 6 SVG icons exported via `exportAsync`: `icon-master-nav-home` (27×27, `758:3384`), `icon-master-nav-students` (27×27, `758:3387`), `icon-master-header-notif` (20×21, `758:3677`), `icon-master-filter` (20×20, `758:3294`), `icon-master-checkin-alert` (37×40, `758:4057`), `icon-master-rating-star` (18×17, `758:3967`). Nav slots 3+4 reuse existing trophy+chart icons. ASSETS-INDEX.md iteration 9→10 (70→76 icons). COMPONENTS-CATALOG.md v1.6→v1.7: 7 new ⬜ candidates — MasterHeaderBar, MasterStatCard, MasterStudentRow, MoodProgressBar, MasterStudentProfile, CheckInRow, MasterNavBar. `velo-design-system.html` updated: Master Dashboard 8 icon group (+6 imgs, bell on steel-primary bg), 4 wash swatches after amber-50. **Macro-Phase I: 9/10 blocks DS-complete. Next: Master Onboarding 13 (`758:4318`, 13 screens).** | || 21 | 2026-05-19 | **Bottom Nav DS-first pass — BottomNav component Macro-Phase II Phase A+B+C.** Figma audit: user nav Group 1988 (node `541:6528`) + master-specific nav Group 2648 (node `758:1748`, АНАЛИТИКА screen only — ДАШБОРД screens share user Group 1988). Master nav distinct icon slots confirmed: home (icon-master-nav-home, reuse) · schedule (icon-master-nav-schedule NEW, `758:1759`, 27×27, firstM=M7.48828) · students (icon-master-nav-students REPLACED — was wrong clipboard icon harvested from ДАШБОРД, now correct person icon from АНАЛИТИКА `758:1765`, 21×27, firstM=M9.28125) · profile (icon-master-nav-profile NEW, `758:1770`, 27×27, firstM=M26.9945 rounded-rect frame with 4 vertical bars). DS deliverables: (1) components.css: `.bottom-nav--user` + `.bottom-nav--master` semantic variants added (1518 lines total); (2) velo-design-system.html: Bottom Navigation section added with 4 demo variants; (3) COMPONENTS-CATALOG.md: BottomNav entry updated with variants, MasterNavBar entry completed (was truncated mid-sentence); (4) _dashboard-flow.html + _calendar-flow.html: `class="bottom-nav"` → `class="bottom-nav bottom-nav--user"` (2 instances each, AP-M-6 compliant); (5) ASSETS-INDEX iter 13→14, icon count 76→78 (net +2 new icons, +1 replaced). sprint-02.md updated. |
| 23 | 2026-05-20 | **MOCKUP GATE session 18 — DS component fixes in `_shared/components.css`.** Three DS-level fixes applied during Dashboard 9 screens 01-03 pixel review: (1) `.section-title` — `font-weight: 700` added (was unset, causing visually lighter section headings vs Figma; affects all 3 section-title usages in `_calendar-flow.html` and Dashboard); (2) `.practice-card .pc-title` — `font-weight: 700` added (same cause, 5 usages in `_calendar-flow.html`); (3) `.practice-card .pc-avatar` — size `38×38 → 48×48px`, `font-size: 16px`, `img { width: 28px; height: 28px }` added to match Figma proportions (5 usages in `_calendar-flow.html`). **COMPONENTS-CATALOG.md update:** `.top-header` promoted from `⬜ candidate (Dashboard 9, 2026-05-18)` to `✅ canon (promoted 2026-05-20, session 18)`. When-to-use updated: "ALL detail/nested app views. ONE canonical header for all app screens. Do NOT use `.velo-back-arrow` in app screens — that pattern is onboarding-only." Usage count: 12 screens (Dashboard 03-09 + Calendar 08-11). No token changes. No new icons. No `velo-design-system.html` changes required (no new visual demos needed for font-weight/size fixes). |
