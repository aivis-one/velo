# Velo — Project Backlog

> Code issues, tech debt, features, tooling gaps.
> Consumed by: `02_Sprint-Builder.md` during sprint planning.
> Updated: 2026-04-23 (install — empty at start).

| # | Item | Source | Priority | Status | Notes |
|---|---|---|---|---|---|
| 1 | Audit `VELO-Anti-Patterns.md` FP-01..FP-08 against bundle-flat approach — flag conflicts | S1 scout §4 | MEDIUM | → S1 P01 C06 | 8 patterns found (not 6 as ARCHITECTURE previously said) |
| 2 | Install `velo-design` Claude Skill to `.claude/skills/velo-design/` | S1 Q#6 decision | LOW | → S4+ | Evaluate after S1 retrospective C14 |
| 3 | Decide fate of `velo-mockups/` + `Design_prototype_legacy_2026-03-11/` | ARCH gap | LOW | → S4+ | After S3 complete |
| 4 | Migrate admin views (7 files in `views/admin/`) | decision #010 | LOW | → S4+ | Outside user/master scope of S1–S3 |
| 5 | MH-08 Masters Account (main master dashboard) — design-gen + port | decision #010 | MEDIUM | → S4 | Moved from S3 |
| 6 | MH-11 Feedback analytics (master-side) — design-gen + port | decision #010 | MEDIUM | → S4 | Moved from S3 |
| 7 | MH-12 Group report (master-side) — design-gen + port | decision #010 | MEDIUM | → S4 | Moved from S3 |
| 8 | Post-handoff checklist: verify flat (no backdrop-blur) in all screens before accepting bundle export | S1 Q#2 process | LOW | Recurring | Per each Claude Design export |
| 9 | Verify `frontend/src/api/types.ts` updates after each backend-partner delivery | S1 Q#5 decision | MEDIUM | Recurring | Per release |
| 10 | Scout convention: fallback-syntax-aware grep | C03/C04 P01 | LOW | Recurring | Scout/grep boundary should match `var(--x[,)]` pattern or open-paren form. C03 found 3 fallback sites (`var(--X, literal)`); C04 found nested fallback at VModal.vue:111 (`var(--X, var(--Y))`). Closing-paren grep `var(--X)` misses these. Apply to all token-audit operations from S2 onward. |
| 11 | displayHelpers.ts:77-79 stale hex comments | C03 P01 | LOW | → S2 | Inline comments `// #DC2626 / #22C55E / #F59E0B` describe colors that don't match actual token values (`--warm-deep #a16124` ≠ #DC2626 etc). Update to reflect real values or remove. |
| 12 | S2 UX review: --velo-error → --pink-primary mapping | C03 P01 | MEDIUM | → S2 | C03 B1 chose `--pink-primary` (#f795a2 salmon, exact value-preserve) over bundle `--feedback-error` (#ad3444). Confirm with sponsor: warm palette intentional or legacy? If bundle red desired, dedicated cycle to flip. |
| 13 | S2 visual convergence check post-glass | C03/C04 P01 | LOW | → S2 | 184 sites across 4 tokens renamed C03 from rgba-transparent velo to solid bundle; C04 removed glass/backdrop. Post-S2-deploy visual should show converged appearance on solid backgrounds. |
| 14 | Lint warnings 758 baseline audit | C01 P01 | LOW | → S4+ | C01 surfaced 758 pre-existing ESLint warnings (0 errors). Baseline-stable through Phase 01 (delta 0). Audit origin, categorize by rule, reduce trivial. Quality-of-life. |
| 15 | VELO-Frontend.md:401 doc drift — `--velo-brand-text` | Governance scout C03 | LOW | → S4+ | VELO-Frontend.md §7 lists `--velo-brand-text: #4c6589` but token NOT defined in current variables.css. Doc stale; cleanup at next VELO-Frontend.md touch. |
| 16 | VELO FP-numbering conflict across docs | Governance scout | LOW | → S2 master/admin | FP-01 has two definitions: VELO-Anti-Patterns.md (8 patterns, FP-01="Хардкод API URL") vs VELO-Frontend.md / VELO-Frontend-Specification.md (9 patterns, FP-01="Only CSS-vars"). Unify at next touch. |
| 17 | Prompt discipline: explicit substitution group ordering | C03 P01 | LOW | Recurring | C03 E1/E2 sequencing bug (E2 ran before E1; 3 warning sites transient `--radius-lg` before fix). HIGH-tier prompts with multiple substitution groups MUST specify explicit order in Steps. |
| 18 | Bundle utility classes + html/body defaults migration plan | C02 P01 | MEDIUM | → S2 OPEN | Bundle `colors_and_type.css` contains utility classes (`.t-display-lg`, `.velo-card`, etc.) + html/body defaults. C02 scope-locked to tokens. Decide at S2 OPEN: (a) port to global.css, (b) extract to styles/bundle.css, (c) scope to components on-demand. |
| 19 | D3 decision clarification | Governance scout C09 | MEDIUM | RESOLVED via #024 | D3 ratified at P02 OPEN as decision #024 (Vue-SVG baseline + bundle PNG decorative supplement). 2 collisions (brain, meditation) → Vue-SVG; 10 bundle-only PNGs adopted as decorative supplement; IconRuble flagged for removal review (BACKLOG #29). Detail in AUDIT-S1.md §9. |
| 20 | B.2 cancelBooking — verified clean (false positive) | Zodd_review C06 | — | Documented | Audit flagged `cancelBooking` typed `Promise<void>`; actual code typed `Promise<BookingResponse>` correctly. False positive. Re-verify if backend contract changes. |
| 21 | B.4 Waitlist endpoints (4) not implemented on frontend | Zodd_review C06 | LOW | → S2/S3 | Backend has 4 waitlist endpoints; frontend has zero waitlist code. Decide if greenfield (S3) or post-S3 backlog. |
| 22 | B.5 Missing UI screens (9 features) | Zodd_review C06 | varies | → S3/S4+ | `purchases/me`, `reports/me`, `master-promos`, `admin/withdrawals`, `admin/users`, `logout-all`, `PATCH users/me`, `finalize`, `join/leave`. Overlap with S3 greenfield + S4+ admin per #010. Per-feature scope at S3 OPEN. |
| 23 | B.12 getMastersList default limit=100 | Zodd_review C06 | LOW | Recurring | Inconsistent with 20-default on other list endpoints. Normalize when next touching `api/masters.ts`. |
| 24 | Regen workflow integration (post-backend Pydantic changes) | C06b Scout | MEDIUM | → P02 | Pipeline EXISTS (`backend/scripts/generate_ts_types.py`). Real gap: no documented regen trigger (CI? pre-commit? manual?). Without disciplined trigger, audit-staleness pattern repeats every partner review (B.1 already-resolved discovery, A.2 blocked-on-stale-regen). Document procedure: backend restart → openapi dump → regen invocation. Coordinate with partner. Pre-S2 priority. |
| 25 | user-ai-summary feature gap | C06 P01 | LOW | RESOLVED | Status now known: AISummary backend exists (`AISummaryResponse` in `generated.ts:18`); no frontend wrapper yet. Categorized as bundle-greenfield in AUDIT-S1.md §4 + closure note in §10 #6; S2 C24 implements wrapper. Superseded by S2 C24. |
| 26 | A.2 follow-up cycle: financial constants migration | C06b P01 | P2 | → P02 (gated on regen) | Backend shipped CR-01 (`masters/schemas.py` Pydantic + router population), but `generated.ts:MasterProfileResponse` missing `min_withdrawal_cents`/`withdrawal_fee_cents` (regen ran against stale openapi.json). Fresh regen unblocks. Cycle scope: remove `MIN_WITHDRAWAL_EUROS`/`WITHDRAWAL_FEE_EUROS` from `constants.ts`, migrate `MasterFinanceView.vue` consumers (lines 93/106-107/266-267/279) + head comment lines 25-26 + script comment lines 203-205. Functional drift today: zero (50/2 mirror backend 5000/200). |
| 27 | Zodd CRITICAL #1: PracticeSummary.timezone fix | Zodd_review / C06b | P1 | → P02 (gated on regen) | Backend `PracticeSummary` Pydantic schema lacks `timezone` field. Frontend silently falls back to `'Europe/Berlin'` — practice times render in Berlin TZ regardless of actual practice timezone. C06b applied tactical cast at `UserDashboardView.vue:300` to unblock typecheck; real fix: backend adds `timezone: str` to PracticeSummary → regen → frontend removes cast + Berlin fallback. Functional impact: user sees wrong time for non-Berlin practices. |
| 28 | Audit-snapshot fingerprint convention | C06 / C06b | LOW | → P02 | Partner audits (Zodd_review.md authored against `364893d`, picked up after partner shipped CR-01 + regen → effective HEAD `83d287a`) require fingerprinted commit base. Without fingerprint, "is finding still applicable" requires manual diff. Convention: every external audit doc starts with `Audit base: <commit-sha>` line. Apply to future partner reviews. |
| 29 | IconRuble candidate for removal — Velo backend operates in EUR; IconRuble.vue likely dead import | C09 P02 / D3 ratification | LOW | → S4+ | grep `IconRuble` across frontend/src/ to verify zero consumers; if confirmed dead → delete + remove from icons/index.ts barrel. If used in legacy admin/master views — keep until #010 admin reactivation. |
| 30 | Bundle PNG → SVG migration (10 decorative icons) | C09 P02 / D3 future-cleanup | LOW | → S5+ | `bolt, circle-microphone, flame, heart, high-five, love, quill-pen, quill-pen-story, spa, wind` — convert from PNG to SVG when Vue-SVG asset volume justifies. Currently used decoratively per #024; raster sufficient for current scale. |
| 31 | ENVIRONMENT.md path drift (D:\03_Projects → D:\02_Projects) | P02 Combined Scout pre-flight | LOW | Recurring | ENVIRONMENT.md line 14 + line 127 cite `D:\03_Projects\velo`; actual project path is `D:\02_Projects\velo` (verified via shell pwd). Pre-existing doc drift, not introduced by P02. Fix at next ENVIRONMENT.md touch. |
| 32 | TopupRequest / TopupResponse type duplication | P02 Combined Scout / Zodd_review §7 | LOW | → S2/S3 | `TopupRequest` + `TopupResponse` declared locally in `frontend/src/api/payments.ts:13-22` AND in `generated.ts`. Duplicate definition — should be re-export from generated.ts per #023 SSOT pattern. Fix at next payments.ts touch. |

---

### #33 — NEGATIVE-grep AC pattern: protect against keyword-collision in comments

**Context**: During S1 P03 C11 execute (WelcomeView.vue), the AC `grep -ic 'oauth\|google\|apple' → 0` triggered on Claude Code's own explanatory header comment which contained the words "OAuth", "Google", "Apple" while explaining what was being EXCLUDED per #012. Claude Code rephrased the comment to satisfy the strict grep while preserving intent.

**Lesson**: NEGATIVE keyword-blocklist greps cannot distinguish code from comments. AC patterns that rely on raw keyword presence/absence are vulnerable to comment-collision when the keyword is part of the cycle's explanatory rationale.

**Action for future cycles**: When designing NEGATIVE greps for "must-not-contain" keywords, either:
1. Constrain grep to non-comment lines (e.g., grep with `-v '^[[:space:]]*<!--\|^[[:space:]]*//' filter`), OR
2. Scope grep to specific syntactic positions (e.g., `<button>` text content, attribute values), OR
3. Accept comment-presence as valid and add explicit prose rule "may appear in comments explaining exclusion".

Tracked for application to S2/S3 NEGATIVE-AC design.

**Source**: S1 P03 C11 execute log; CLOSE Step 3 Session Review.
**Severity**: process-improvement (not blocking).
**Sprint**: S2 (apply when designing next NEGATIVE-AC).

---

### #34 — Verification grep regex: `#[0-9a-fA-F]{3,8}` over-fires on decision-number references

**Context**: During S1 P03 CLOSE Verification Scout, the FP-01 hex/rgba violation grep over the new WelcomeView.vue matched header comment lines containing `#012`, `#013` (decision-number references in cycle context comment). The regex `#[0-9a-fA-F]{3,8}` accepts these as 3-digit hex codes since `012` and `013` are valid hex.

**Lesson**: Project-wide convention of citing decisions as `#NNN` collides with hex-color regex. NIT only — false positives are easily disposed in scout output, but recurs every cycle that touches docs/comments mentioning decisions.

**Action**: Refine FP-01 verification regex to exclude decision references. Candidates:
1. `#[0-9a-fA-F]{3,8}\b` with negative lookahead — but `\b` already at word boundary; doesn't help since `#012` IS at word boundary.
2. Filter pattern: exclude lines matching `decisions?\.md|#0[0-9]{2}` from results before counting.
3. Stricter regex: `#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b` (only 3 or 6 hex digits, drop 4/5/7/8) — this excludes `#012` (3 digits but starts with 0 which is valid hex char `0` so still over-fires).
4. Position-based: only match inside `style=`, `style scoped`, `:style`, or CSS context.

Tracked for refinement during S1-Clean-Sync or as standing improvement to verification scout templates.

**Source**: S1 P03 CLOSE Step 2 Verification Scout output (NIT row).
**Severity**: process-improvement (not blocking).
**Sprint**: S2 or S1-Clean-Sync.

---

### #35 — ENVIRONMENT.md commit convention cleanup

**Context**: S1 used phase-bundled commits exclusively per Phase-Builder CLOSE Step 4f (one commit per phase, no cycle-tagged commits during WORK). ENVIRONMENT.md §Git Workflow still describes `cycle: C{NN} <short>` (cycle work) and `cycle: C{NN} <name> — DONE` (cycle close) formats that were never used during S1 and have no path to be used given current Phase-Builder rules.

**Action**: Remove both `cycle:`-prefix rows from ENVIRONMENT.md §Git Workflow Commit convention table. Keep `phase:`, `sprint:`, `docs:`, `decision:`, `refactor:`, `fix:`, `clean-sync:`, `audit:`, `deploy-prelude:`. Crash-recovery commits use ad-hoc message without dedicated format prefix.

**Source**: S1-RETRO.md §What Didn't (Commit convention divergence with ENVIRONMENT.md).
**Severity**: doc-cleanup (not blocking).
**Sprint**: S1-Clean-Sync.

---

### #36 — Staging deploy flow doc clarification

**Context**: `ENVIRONMENT.md` §Known Limitations row 1 + `ARCHITECTURE.md` §Server & Deploy describe staging deploy as `push to new_desing → staging auto-pulls`. S1 Phase 04 close revealed the practical workflow includes a backend-partner code-audit gate before staging exposure (Velo push → partner audits → partner promotes/deploys → staging visible). The «auto-pulls» wording risks misleading future planning into expecting in-sprint visual verification on push (which is what the original C13 plan assumed and which led to the triaged-deferral close).

**Action**: Reconcile description. Options: (a) clarify that auto-pull is the technical mechanism but workflow includes partner-audit gate before staging exposure, OR (b) remove «auto-pulls» phrasing if staging is fully partner-gated, OR (c) add an explicit deploy-flow sequence to ENVIRONMENT.md / ARCHITECTURE.md §Server & Deploy. Coordinate with Human at Clean-Sync time to confirm the actual workflow before edit.

**Source**: S1 Phase 04 CLOSE — Human-stated deploy flow correction.
**Severity**: doc-clarification (not blocking; prevents mis-planning of future visual-test cycles).
**Sprint**: S1-Clean-Sync.

---

### #37 — Post-deploy visual verification of S1 pilot screens

**Context**: S1 Phase 04 C13 was a manual-test cycle (Human visual on staging) deferred at phase close per Phase-Builder §CLOSE §1 triaged-deferral. Reason: visual verification gates on external pipeline (Velo push → backend partner code audit → partner deploy → staging exposure) which cannot complete in-sprint. Velo-side code work for both pilot screens is complete with all gates green at Phase 03 close (typecheck 0 errors / test 32 passed / lint 756 / build green / PWA precache 99). Visual confirmation is the final acceptance step.

**Action**: Once staging reflects commit `823bdec` (Phase 03 close) or successor with same pilot-screen content (after partner-audit + deploy), perform visual test:

- **WelcomeView** at `/welcome` — light + dark themes via DevTools `[data-theme="dark"]` on root.
  - Mandala backdrop (centered, behind content); VELΘ wordmark in Marmelad font with correct Θ glyph; tagline below wordmark; single primary CTA «Открыть в Telegram» linking to `import.meta.env.VITE_TELEGRAM_BOT_URL` (inspect anchor `href`; not `#` / empty / placeholder).
  - No backdrop-filter / glassmorphism (per #007). No third-party login UI — no Google / Apple buttons (per #012).
  - Mobile-first layout stable at ~380px and ~1024px viewport widths.
  - 0 console errors. Mandala remains visible against dark background in dark theme; no tokens fall back to light values.

- **UserDashboardView** at `/user/dashboard` — login as `user` role to bypass the global `beforeEach` guard at `to.name === 'user-dashboard'` (master / admin sessions redirect via `uiStore.uiMode`). Light + dark themes.
  - WeekdayStrip at top (7 day cells, current day highlighted) + Stats row from real `bookingsStore` data (not placeholders, not zero-state if user has bookings).
  - AI summary card visible (existing Velo behavior preserved per C10 scope).
  - Check-in alert + feedback alert when applicable.
  - Nearest practice card with practice time formatted in correct timezone (Berlin fallback known per BACKLOG #27 — non-Berlin practices may show wrong time; flag in defects with `decision-impact: BACKLOG #27`).
  - NO Contraindications callout (skipped per C10 scope-lock — bundle's element not ported because no backend flag).
  - NO Recommendations list (deferred to S2 P05).
  - Bundle dark `--surface-*` tokens applied in dark mode (no rgba leftovers from pre-#009 velo namespace).

- **Console / Network**:
  - 0 errors across all 4 theme×screen combinations (warnings noted but not blocking).
  - No 404s on assets (fonts, illustrations, mandala, brand-icons).
  - `Marmelad-Regular.ttf` loaded 200 OK (Network → fonts).
  - PWA precache: 99 entries served (DevTools → Application → Cache Storage).

**Defects format** for each finding:
- `severity`: BREAK / GAP / NIT
- `screen`: welcome / dashboard
- `theme`: light / dark
- `what`: one-line description
- `expected`: what bundle / decision says it should be (cite #NNN if applicable)
- `evidence`: screenshot filename or DOM snippet or console error text
- `decision-impact`: cite contradicted decision or BACKLOG entry if applicable

**Source**: S1 Phase 04 C13 deferred per `S1-RETRO.md` §Conditional + Phase-Builder §CLOSE §1 triaged-deferral.
**Severity**: post-S1 follow-up (not blocking S1 close; gates the «работают на staging» Success Criterion #7 final acceptance).
**Sprint**: post-S1 (run when partner deploy to staging completes).

---

### #38 — probekit-i18n-audit hardening when i18n lands in Velo

**Context**: probekit-i18n-audit is currently CBS-HOME-hardcoded (`source_dir=mockups/frontend/src`, `locales_dir=mockups/frontend/src/i18n/locales`, `supported_locales=[en,ru,de,ar]`). Velo has no i18n infrastructure yet (`frontend/src/i18n/` does not exist; project is Russian-only per `velo-design-system-2026-04-23/project/README.md`). Skill was deliberately skipped during S1-Sprint-Closer Step 1+ ProbeKit hardening (decision #026) — repathing without arch knowledge would create a false illusion of i18n-readiness.

**Action**: When i18n lands in Velo (separate sprint, design phase), as part of that work harden probekit-i18n-audit: repath `source_dir` → `frontend/src`, repath `locales_dir` → actual Velo locales folder, set `supported_locales` to Velo's actual locale set, scrub "CBS HOME" prose from description + body header.

**Source**: S1-Sprint-Closer Step 1+ scout output §1B + §1C i18n applicability note; decision #026.
**Severity**: deferred (skill is not in lite profile; not blocking S1 close).
**Sprint**: post-i18n-introduction (likely S5+).

---

### #39 — main vs new_desing divergence: partner force-pushed pre-S1 tech-debt refactor to main

**Discovered**: 2026-04-26, S1-Sprint-Closer Step 2 Pre-Exec context (during diff-range setup for backender review pass).

**State**:
- `origin/new_desing` (HEAD `7c28a7b`) — Velo-side S1 work: bundle migration (#006, #009), brand assets port (#024), WelcomeView fast-track (#025), 17 phase-bundled commits across P01–P03.
- `origin/main` — 4 commits from `inzoddwetrust` (`265793c`, `7fc2e93`, `8581506`, `19be8fa`), all titled "refactor(frontend): close tech debt blocks 1-2 (F-03, WARNING-1/9, ...)" — clearly amend/force-push iterations of one logical change.
- `main` is based on a commit BEFORE S1 bundle migration (likely `83d287a` or earlier — last common ancestor pre-S1).
- `main` does NOT contain: bundle namespace tokens (still `--velo-*`), bundle SSOT references (still `velo-mockups/css/variables.css`), `WelcomeView.vue`, brand assets (`frontend/src/assets/brand/`, `brand-icons/`, `illustrations/`, `masters/`, `mood/`, `patterns/`), `Marmelad-Regular.ttf`, `Design_prototype` → `Design_prototype_legacy_2026-03-11` rename.
- Diff scale: ~100 files, −1417 / +1006 in main's direction = main lags new_desing by the entire S1.

**Hypothesis**: Backend partner did the frontend tech-debt refactor (F-03, WARNING-1/9, NEW-3/6/7/10, F-06/09) on a fork/branch based on a pre-S1 commit, unaware of bundle migration on `new_desing`. Force-pushed to main.

**Risk**:
- `git merge origin/main → new_desing` would destroy the entire S1: token rename (#009), bundle SSOT (#006), WelcomeView (#025), brand assets (#024), 17 phase-bundled commits.
- `merge new_desing → main` is the correct direction: main catches up to S1, and partner's tech-debt refactor (F-03, WARNING-1/9, NEW-3/6/7/10, F-06/09) re-applies on top of the actual S1 base.

**Action — partner coordination required (out-of-chat, post-S1-close)**:
1. Notify partner of divergence + the loss-risk if main were merged into new_desing.
2. Choose one resolution path with partner:
   - (a) Partner rebases their tech-debt refactor onto `new_desing` (preferred — S1 not lost; their refactor lands cleanly on top).
   - (b) After we merge `new_desing` → `main`, partner re-implements their refactor on the actual S1 base (use only if rebase too complex).
3. Until resolved: do NOT merge main → new_desing under any circumstance.

**Severity**: HIGH for branch-state hygiene; not blocking S1-close itself (S1 work lives on `new_desing` and can close independently). Becomes blocking for any future "merge S1 work to main" milestone.

**Sprint**: pre-S2 Human action item — coordinate with partner before any branch-merge work begins.

**Source**: S1-Sprint-Closer Step 2 Pre-Exec divergence discovery; pairs with BACKLOG #36 (staging-deploy doc clarification) and #37 (post-deploy visual verification) as the third partner-coordination item from S1 close.

---

### #40 — S2 a11y polish cluster

**Source**: S1-Sprint-Closer ProbeKit lite a11y-audit + cross-skill confirmations (backender §6, security ext-link, design P5).

**Bundled findings (14)**:
- A11Y P1+P3 (HIGH): 7 `<div @click>` sites — UserProfileView 5 menu items incl. logout, MasterDashboardView balance card, PracticeCard primary nav. Keyboard-inaccessible. Convert to `<button>` (preferred) or pad with `tabindex="0"` + `@keydown.enter.space`.
- A11Y P4 (HIGH): VModal lacks focus-trap, focus-return, focus-on-open. Tab leaves dialog. Recommend `focus-trap-vue` library (~2 KB gzipped).
- A11Y P6 (HIGH): VInput / VTextarea / VSelect / VCheckbox labels not associated. Use Vue 3.5 `useId()` to add `for`/`id` linkage. Cascades across ~12 view files.
- A11Y P2 (MEDIUM): VTabBar active item missing `aria-current="page"`; VToast container missing `role="status"` + `aria-live="polite"`.
- A11Y P3 (MEDIUM): VToast keyboard-dismiss missing.
- A11Y P7 (MEDIUM): No skip-to-content link in `index.html`; `<main id="main-content">` missing.
- A11Y P8 (MEDIUM): ~16 inline SVG icons in `components/icons/Icon*.vue` missing `aria-hidden="true"`; loading states missing `aria-busy`.
- A11Y P4 (LOW): No global `:focus-visible` styles in `styles/global.css`.
- A11Y P4 (LOW): No focus-on-route-change handler in App.vue or router after-each.
- A11Y P7 (LOW): Two `<nav>` regions (header + tabbar) need unique `aria-label`.
- A11Y P5 (LOW): `--text-secondary` (3.4:1) / `--text-muted` (2.5:1) sub-AA if used as body text — audit usage scope (placeholder/hint/disabled use is exempt; body text is not).

**Severity**: HIGH for the 3 first items (keyboard accessibility blockers); MEDIUM/LOW for the rest.

**Sprint**: S2 — single coherent a11y polish cycle. Effort: M-L (4 components + ~12 forms verification + 1 new dep).

**Source**: S1-CODE-AUDIT.md issues 2, 3, 4, 12, 13, 14, 15, 25, 26, 27, 28.

---

### #41 — S2 design-tokens bulk-tighten cluster

**Source**: S1-Sprint-Closer ProbeKit design-audit.

**Bundled findings (5)**:
- Design P4 (MEDIUM): 21 hardcoded radius values — 12 × `border-radius: 5px` (→ `--radius-sm`), 8 × `border-radius: 100px` (→ `--radius-full` per #016), 1 × VModal `20px` (→ `--radius-xl`). Affected: VInput, VSelect, VTextarea, VCheckbox, FormShell, BookingPopup, DiaryEntryForm, TopupView, EditPracticeView (×2), CreatePracticeView, MasterApplyView, MasterFinanceView, DiaryList, AnalyticsView, MasterDashboardView, MasterPracticesView (×2), MasterProfileView, CalendarView, MyBookingsView, VModal.
- Design P3 (MEDIUM): ~12 hardcoded spacing px sites where tokens exist. Consider adding `--space-2xs: 6px`, `--space-3xs: 12px` for non-token gaps.
- Design P1 (MEDIUM): 30 `color: white` / `background: white` named-color sites across 21 files → `var(--neutral-white)` or `#ffffff`.
- Design P1 (MEDIUM): 8 rgba overlay sites — UserProfile (×2), MasterPractices, VTabBar, VModal, AttendanceView, EditPracticeView, VToast. Need new tokens `--surface-overlay-50`, `--surface-white-alpha-*`.
- Design P5 (LOW): VToast hardcoded `box-shadow: 0 4px 12px rgba(0,0,0,0.3)` → `var(--shadow-md)` (1:1 match per variables.css).

**Severity**: MEDIUM (design-system discipline; visually identical output; system-consistency cost).

**Sprint**: S2. Effort: M (mostly mechanical bulk substitution + 1-2 new token definitions).

**Source**: S1-CODE-AUDIT.md issues 6, 7, 8, 21.

---

### #42 — S2 mobile-polish cluster

**Source**: S1-Sprint-Closer ProbeKit responsive-audit.

**Bundled findings (3)**:
- Resp P1 (MEDIUM): `frontend/index.html` viewport meta missing `viewport-fit=cover` — iOS notch on iPhone X+ won't extend content edge-to-edge. Single-line fix.
- Resp P2 (MEDIUM): VHeader missing `padding-top: calc(var(--space-3) + env(safe-area-inset-top, 0px))`. Header content can be obscured by notch on TMA fullscreen.
- Resp P3 (MEDIUM): VButton `size="sm"` min-height 36px (below WCAG 44×44); VTabBar item ≈42px; VInput height 40px. Either bump to 44 or expand clickable via `::before` pseudo-element.

**Severity**: MEDIUM (real-device usability on notched iOS; WCAG 2.5.5 compliance).

**Sprint**: S2 mobile-polish or hardening cycle. Effort: S (3 small fixes; can be one cycle).

**Source**: S1-CODE-AUDIT.md issues 9, 10, 11.

---

### #43 — S2 view-layer extractApiError adoption

**Source**: S1-Sprint-Closer code-audit §6 + backender review §6+§8.

**Action**: ~25-30 try/catch sites across 9 large views (EditPracticeView 9 sites at 519-700, AnalyticsView, UserDashboardView, PracticeDetailView, MasterProfileView, MasterFinanceView, CreatePracticeView, MasterApplyView, MasterDashboardView) follow the pattern:

```diff
- } catch (e) {
-   toast.error(e instanceof ApiResponseError ? e.detail : 'Не удалось <action>')
- }
+ } catch (e) {
+   toast.error(extractApiError(e, 'Не удалось <action>'))
+ }
```

`composables/useApiError.ts:24` provides `extractApiError(e, fallback)`. Stores already migrated via WARNING-1; views were left out. Mechanical refactor.

**Severity**: MEDIUM (DRY; observable code-volume cost).

**Sprint**: S2. Effort: M (mechanical, one cycle).

**Source**: S1-CODE-AUDIT.md issue 5.

---

### #44 — S2 test-coverage backfill

**Source**: S1-Sprint-Closer code-audit §7+§12 + backender §7.

**Current state**: 32 tests in 2 files (`composables/usePagination.test.ts` 9 tests; `utils/format.test.ts` 23 tests). All pass.

**Untested critical paths**:
- `api/client.ts` — timeout, GET dedup, error normalize, 401 callback
- `stores/auth.ts` — login, restore, logout, fetchMe
- `router/guards.ts` — roleRedirect, roleGuard, masterStatusGuard, applyGuard
- 6 of 7 stores (bookings, diary, master, practices, balance, ui)
- 5 of 6 composables (useAuth, useToast, useApiError, usePracticeWindows)

**Architecture** is test-friendly: `resetClientState()` (api/client.ts:99-103), `resetAuthState()` (composables/useAuth.ts:66-70). Quantity gap, not testability.

**Minimum target for S2**: ~30 tests covering api-client + auth-store + router-guards + 1-2 store-tests.

**Severity**: MEDIUM at S1 close; will be HIGH for S2 sprint planning.

**Sprint**: S2 test-backfill cycle. Effort: M-L (~30 tests).

**Source**: S1-CODE-AUDIT.md issue 19.

---

### #45 — S5+ major-version dependency updates

**Source**: S1-Sprint-Closer backender §10.

**Action**: Major-version updates available with breaking changes:
- pinia 2.3.1 → 3.0.4
- vue-router 4.6.4 → 5.0.6
- vite 6.4.1 → 8.0.10
- vitest 3.2.4 → 4.1.5
- typescript 5.7.3 → 6.0.3
- eslint 9.39.3 → 10.2.1
- @vitejs/plugin-vue 5.2.4 → 6.0.6
- vite-plugin-pwa 0.21.2 → 1.2.0
- (+ 4 minor updates)

**Severity**: MEDIUM (technical debt; not blocking).

**Sprint**: S5+ — separate sprint cycle for major bumps with breaking-change verification. Defer until S1-S4 deliverables stabilize. Pairs with #54 dep-update cycle (overlapping scope: vite-plugin-pwa + happy-dom upgrades resolve both #45 and #54 residual).

**Source**: S1-CODE-AUDIT.md issue 20.

---

### #46 — Router timeout silent fallback

**Source**: S1-Sprint-Closer code-audit §3 + backender §3.

**Action**: `router/index.ts:329-331` — auth-init timeout produces only `console.warn`. App.vue gate (`isReady && !isAuthenticated → StandaloneStubView`) currently catches the situation, but silent fallback is fragile against future App.vue refactors.

Two options:
1. Hard fix: `if (timedOut) return { path: '/auth-error' }` (need to add `/auth-error` route + view)
2. Soft fix: explicit invariant comment in router referencing App.vue gate dependency

**Severity**: MEDIUM (defense-in-depth; not a current bug).

**Sprint**: S2 — single-line fix, can fold with #47 in a single auth-flow cycle.

**Source**: S1-CODE-AUDIT.md issue 16.

---

### #47 — `roleGuard()` async-await defense-in-depth

**Source**: S1-Sprint-Closer security-audit §A01 + backender §4.

**Action**: `router/guards.ts:85-102` — `roleGuard()` is synchronous; reads `auth.role` without awaiting `waitUntilReady()`. If invoked before `initAuth()` completes, role could be null and users redirect to `/user/dashboard`. Currently safe because App.vue gate blocks RouterView, but future regression in App.vue gate would silently break authorization.

```diff
  export function roleGuard(required: ...): NavigationGuardWithThis<undefined> {
-   return () => {
+   return async () => {
+     await waitUntilReady()
      const auth = useAuthStore()
      ...
```

**Severity**: MEDIUM (defense-in-depth; no current exploit).

**Sprint**: S2. Effort: S — fold with #46 in one auth-flow cycle.

**Source**: S1-CODE-AUDIT.md issue 17.

---

### #48 — Confirm-modal unification

**Source**: S1-Sprint-Closer backender §6+§8 + a11y P4 + design P1.

**Action**: 3 confirm-dialog implementations exist:
1. `components/ui/VModal.vue` — canonical
2. `views/master/EditPracticeView.vue:900-915` — custom overlay (`fixed; rgba(0,0,0,0.5)`)
3. `views/master/AttendanceView.vue:504-516` — custom overlay (same pattern)

Replace 2 + 3 with VModal. Single fix resolves three reports' findings:
- DRY violation (Backender §6)
- Custom overlays' a11y gaps (no focus-trap, no focus-return; A11Y P4 — partially addresses #40)
- 3 hardcoded `rgba(0,0,0,0.5)` overlay sites (Design P1 — partially addresses #41)

**Severity**: MEDIUM.

**Sprint**: S2. Effort: M (touches 2 view files + relies on #40's VModal focus-trap fix landing first).

**Source**: S1-CODE-AUDIT.md issue 18.

---

### #49 — `VITE_TELEGRAM_BOT_URL` fail-fast in PROD

**Source**: S1-Sprint-Closer code-audit §4 + backender §9.

**Action**: `views/auth/WelcomeView.vue:43` and `views/auth/StandaloneStubView.vue:30`:
```ts
const botUrl = import.meta.env.VITE_TELEGRAM_BOT_URL || 'https://t.me/velo_testbot'
```

If `VITE_TELEGRAM_BOT_URL` missing in a production build, users silently route to test bot. Add fail-fast to `main.ts` boot:
```ts
if (import.meta.env.PROD && !import.meta.env.VITE_TELEGRAM_BOT_URL) {
  throw new Error('VITE_TELEGRAM_BOT_URL must be set in production builds')
}
```

**Severity**: LOW (config discipline; not a vulnerability).

**Sprint**: S2 — single cycle, can fold with #46/#47 auth-flow cycle.

**Source**: S1-CODE-AUDIT.md issue 23.

---

### #50 — `rel="noopener noreferrer"` for `_blank` links

**Source**: S1-Sprint-Closer security-audit external-links + backender §9.

**Action**: 2 sites have `rel="noopener"` only:
- `views/auth/WelcomeView.vue:34`
- `views/auth/StandaloneStubView.vue:18`

Add `noreferrer`:
```diff
- <a :href="botUrl" target="_blank" rel="noopener">
+ <a :href="botUrl" target="_blank" rel="noopener noreferrer">
```

Telegram bot URL is project-owned; referrer leak is minor. Best-practice completeness.

**Severity**: LOW.

**Sprint**: S2 — trivial 2-line fix; can fold into any unrelated auth-view-touch cycle.

**Source**: S1-CODE-AUDIT.md issue 24.

---

### #51 — `stores/diary.ts` LRU vs FIFO comment

**Source**: S1-Sprint-Closer code-audit §5 + backender §5.

**Action**: `stores/diary.ts:284, 296-300` — comment says «LRU eviction», implementation is FIFO (`insightsCache.keys().next().value` evicts insertion-order). For immutable-after-fetch insights cache, distinction is academic. Either:
1. Adjust comment to «FIFO eviction»
2. Implement true LRU via Map re-insertion on access

Recommend option 1 (comment-only fix).

**Severity**: LOW.

**Sprint**: Next file touch — opportunistic.

**Source**: S1-CODE-AUDIT.md issue 22.

---

### #52 — Breakpoint convention doc

**Source**: S1-Sprint-Closer responsive-audit P7.

**Action**: Single `@media (min-width: 640px)` site at `components/ui/VModal.vue:166`. Mobile-first architecture is correct (#013), single breakpoint intentional. But:
- Not formally documented in `decisions.md` or `ARCHITECTURE.md`
- No `--bp-*` token in variables.css

If S2/S3 introduce more responsive elements without doc, drift risk increases. Action: add convention to decisions.md OR introduce `--bp-mobile`, `--bp-tablet` tokens with usage examples.

**Severity**: LOW.

**Sprint**: S2 — doc-touch, 0.5 cycle.

**Source**: S1-CODE-AUDIT.md issue 29.

---

### #53 — File-header FIX-ID housekeeping

**Source**: S1-Sprint-Closer code-audit §6 + backender §6.

**Action**: View file headers carry FIX-ID provenance comments (10.1, F-03, F-09, NEW-6, NEW-8, WARNING-1, etc.) — currently exceptional discipline, but will rot as fixes consolidate or get superseded. Already partially observed: `views/master/MasterFinanceView.vue:25-26` financial-constants references documented in BACKLOG #26.

Action: at each sprint close, audit file headers for stale FIX-ID references. Can be a Sprint-Closer Step 12 sub-step from S2 onward, OR a Clean-Sync routine task.

**Severity**: LOW.

**Sprint**: per-sprint-close ongoing — implement at S2-Clean-Sync as recurring routine.

**Source**: S1-CODE-AUDIT.md issue 30.

---

### #54 — npm audit residual + partial-fix archive

**Source**: S1-Sprint-Closer Step 6 partial CRITICAL fix.

**Pre-fix state**: 11 vulnerabilities — 1 critical, 8 high, 2 moderate.

**Fix applied**: `cd frontend && npm audit fix` (no `--force`).

**Post-partial-fix state**: 5 vulnerabilities — 1 critical, 4 high. All dev/build-time; zero end-user attack surface.

**Resolved (6/11)**, including the prod-relevant CVE:
- vite GHSA-p9ff-h696-f583 — dev-server arbitrary file read via WebSocket (closed)
- vite GHSA-4w7w-66w2-5vf9 — Path Traversal in optimized deps `.map` (closed)
- flatted GHSA-25h7-pfq9-p65f — unbounded recursion DoS (closed)
- flatted GHSA-rf6f-7fwh-wjgh — prototype pollution (closed)
- brace-expansion GHSA-f886-m6hf-6m8v — DoS / memory exhaustion (closed)
- + 1 transitive (closed)

**Residual (5 CVEs, all dev/build-time only)**:
- happy-dom 17.x → 20.x: GHSA-37j7-fg3j-429f (VM Context Escape RCE), GHSA-w4gp-fjgq-3q4g (fetch credentials misuse), GHSA-6q6h-j7hj-3r64 (ECMAScriptModuleCompiler unsanitized export names) — test-runner only
- serialize-javascript: GHSA-5c6j-r48x-rmvq (RegExp.flags RCE), GHSA-qj8w-gfj5-8c6v (CPU exhaustion DoS) — transitive via workbox-build, build-time only
- @rollup/plugin-terser — transitive via workbox-build, build-time only
- workbox-build — transitive via vite-plugin-pwa, build-time only
- vite-plugin-pwa 0.21.2 → 0.19.x downgrade or major bump — direct devDep, build-time only

**Why partial accepted**:
1. Zero end-user attack surface — none of these packages ship in `dist/`. The shipped service worker uses `workbox-window` (runtime), distinct from `workbox-build` (build-time).
2. Resolution requires `--force` which triggers major-version bumps with breaking changes (happy-dom 17→20 needs test refactoring; vite-plugin-pwa version change needs PWA precache regeneration validation).
3. Out of Sprint-Closer scope per Backender §10 recommendation: «если `--force` нужен — feature-branch + smoke-test».
4. Build verification post-partial-fix: typecheck ✓, lint ✓ (756 warnings = baseline #14), test ✓ (32/32), build ✓, PWA precache 99 entries.

**Action — when to close**: dependency-update cycle (S5+ recommended; can fold with #45 major-version updates which has overlapping scope — pinia 2→3, vue-router 4→5, vite 6→8, vitest 3→4, ts 5→6, eslint 9→10, +vite-plugin-pwa, +happy-dom). Pre-merge gate: full `npm test` + `npm run build` smoke-test in feature-branch; verify PWA precache list unchanged or intentional delta.

**Severity**: MEDIUM (downgraded from CRITICAL because residual is contained to dev/build-time and end-user surface is zero).

**Sprint**: S5+ — paired with #45 dep-update cycle.

**Source**: S1-CODE-AUDIT.md issue 1; this Sprint-Closer Step 6 partial-fix outcome.
