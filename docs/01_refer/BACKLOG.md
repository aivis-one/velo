# Velo — Project Backlog

> Code issues, tech debt, features, tooling gaps.
> Consumed by: `02_Sprint-Builder.md` during sprint planning.
> Updated: 2026-04-28 (S1-Clean-Sync).

| # | Item | Source | Priority | Status | Notes |
|---|---|---|---|---|---|
| 1 | Audit `VELO-Anti-Patterns.md` FP-01..FP-08 against bundle-flat approach — flag conflicts | S1 scout §4 | MEDIUM | → S1 P01 C06 | 8 patterns found (not 6 as ARCHITECTURE previously said) |
| 2 | Install `velo-design` Claude Skill to `.claude/skills/velo-design/` | S1 Q#6 decision | LOW | → S4+ | Evaluate after S1 retrospective C14 |
| 3 | Decide fate of `velo-mockups/` + `docs/05_legacy/Design_prototype_legacy_2026-03-11/` | ARCH gap | LOW | → S4+ | After S3 complete |
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
| 20 | B.2 cancelBooking — verified clean (false positive) | Zodd_review C06 | — | Documented | Audit flagged `cancelBooking` typed `Promise<void>`; actual code typed `Promise<BookingResponse>` correctly. False positive. Re-verify if backend contract changes. |
| 21 | B.4 Waitlist endpoints (4) not implemented on frontend | Zodd_review C06 | LOW | → S2/S3 | Backend has 4 waitlist endpoints; frontend has zero waitlist code. Decide if greenfield (S3) or post-S3 backlog. |
| 22 | B.5 Missing UI screens (9 features) | Zodd_review C06 | varies | → S3/S4+ | `purchases/me`, `reports/me`, `master-promos`, `admin/withdrawals`, `admin/users`, `logout-all`, `PATCH users/me`, `finalize`, `join/leave`. Overlap with S3 greenfield + S4+ admin per #010. Per-feature scope at S3 OPEN. |
| 23 | B.12 getMastersList default limit=100 | Zodd_review C06 | LOW | Recurring | Inconsistent with 20-default on other list endpoints. Normalize when next touching `api/masters.ts`. |
| 24 | Regen workflow integration (post-backend Pydantic changes) | C06b Scout | MEDIUM | CLOSED | CLOSED 2026-04-30 — workflow discipline documented in `docs/03_sprint/S2-bundle-port/BACKEND-COORDINATION.md § D` (manual on partner signal per decision #031). |
| 26 | A.2 follow-up cycle: financial constants migration | C06b P01 | P2 | CLOSED | CLOSED 2026-04-30 — S2 P05 C15: regen surfaced `MasterProfileResponse.{min_withdrawal_cents, withdrawal_fee_cents}`; `MIN_WITHDRAWAL_EUROS` + `WITHDRAWAL_FEE_EUROS` removed from `utils/constants.ts`; `MasterFinanceView.vue` reads cents directly from `masterStore.profile`. |
| 27 | Zodd CRITICAL #1: PracticeSummary.timezone fix | Zodd_review / C06b | P1 | CLOSED | CLOSED 2026-04-30 — S2 P05 C15: regen surfaced `PracticeSummary.timezone: string`; tactical cast `(... as PracticeSummary & { timezone?: string }).timezone ?? 'Europe/Berlin'` in `UserDashboardView.vue` removed; direct `practice.timezone` read. |
| 28 | Audit-snapshot fingerprint convention | C06 / C06b | LOW | → P02 | Partner audits (Zodd_review.md authored against `364893d`, picked up after partner shipped CR-01 + regen → effective HEAD `83d287a`) require fingerprinted commit base. Without fingerprint, "is finding still applicable" requires manual diff. Convention: every external audit doc starts with `Audit base: <commit-sha>` line. Apply to future partner reviews. |
| 30 | Bundle PNG → SVG migration (10 decorative icons) | C09 P02 / D3 future-cleanup | LOW | → S5+ | `bolt, circle-microphone, flame, heart, high-five, love, quill-pen, quill-pen-story, spa, wind` — convert from PNG to SVG when Vue-SVG asset volume justifies. Currently used decoratively per #024; raster sufficient for current scale. |
| 32 | TopupRequest / TopupResponse type duplication | P02 Combined Scout / Zodd_review §7 | LOW | CLOSED | CLOSED 2026-04-30 — S2 P05 C15: local interface declarations removed from `api/payments.ts`; consume `TopupResponse` via `@/api/types` re-export hub (decision #023). |

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
**Status**: CLOSED 2026-04-30 — S2 P05 C15 staging push verification gate. Visual verify result: ALL CLEAN — both screens, both themes, executed against staging deploy `ad4ce7d`, TG account 526738615 (2026-04-30).

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
- `main` does NOT contain: bundle namespace tokens (still `--velo-*`), bundle SSOT references (still `velo-mockups/css/variables.css`), `WelcomeView.vue`, brand assets (`frontend/src/assets/brand/`, `brand-icons/`, `illustrations/`, `masters/`, `mood/`, `patterns/`), `Marmelad-Regular.ttf`, `Design_prototype` → `docs/05_legacy/Design_prototype_legacy_2026-03-11` rename.
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

**Severity**: LOW (downgraded 2026-04-30) — Server deploys from new_desing via `velo update`; merge to main is optional/future. No urgency.

**Sprint**: deferred — address only when merge-to-main milestone is planned.

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

---

### #55 — SERVER-ACCESS.md population (pre-S2 Human action)

**Context**: BACKLOG #36 (RESOLVED in S1-Clean-Sync Step 2 §A4 + §B1 per variant d framing) repointed deploy-flow documentation in ENVIRONMENT.md §Known Limitations and ARCHITECTURE.md §Server & Deploy to `SERVER-ACCESS.md` (gitignored) as the live source of truth. The S1 deploy is performed jointly with the backend partner who hands over the procedure during the deploy session (occurs at S1 close). From S2 onward Velo deploys independently per `SERVER-ACCESS.md`. Population of `SERVER-ACCESS.md` (commands, host endpoint, access credentials reference, audit/promote workflow notes if partner-gated portions persist) is a Human action gated on the partner deploy session.

**Action**: Populate `docs/01_refer/SERVER-ACCESS.md` with partner-provided staging deploy procedure:
- Host endpoint(s) for staging server.
- Deploy commands (or pull-trigger mechanism).
- SSH/credential access notes — env-var references, NEVER plaintext credentials (file is gitignored regardless, but discipline matters).
- Audit/promote workflow if any partner-gated portions persist into S2.
- Rollback / hotfix procedure if provided.

**Severity**: pre-S2 blocker. The «we deploy independently per SERVER-ACCESS.md» claim now embedded in ENVIRONMENT.md + ARCHITECTURE.md depends on this file being populated before S2 begins any work that may require deploy.

**Sprint**: pre-S2 Human action (out-of-sprint follow-up). Pairs with BACKLOG #39 (main vs new_desing divergence resolution) and BACKLOG #24 (regen workflow integration) as the three Human-action blockers between S1 close and S2 start.

**Source**: S1-Clean-Sync Step 2 §C5 (RESOLVED note for BACKLOG #36); chat agreement on variant (d) framing (Human-confirmed: S1 partner-joint deploy → S2+ self-deploy transition); deploy-flow promise embedded in ENVIRONMENT.md §Known Limitations row 1 + ARCHITECTURE.md §Server & Deploy.
**Status**: CLOSED 2026-04-30 — `SERVER-ACCESS.md` populated separately by Human; deploy procedure: `git push origin new_desing && ssh root@<staging-host> 'velo update'`; password storage per Human's choice (gitignored inline OK).

---

### #56 — Backend: email/password auth endpoints

**Priority**: P1 (S3 blocker).
**Source**: BACKEND-COORDINATION § A.1.
**Notes**: UI is mock until ready (LoginView, RegisterView in S2 P06).

---

### #57 — Backend: Google + Apple OAuth endpoints

**Priority**: P2.
**Source**: BACKEND-COORDINATION § A.2.
**Notes**: UI mock (OAuthLoadingView in S2 P06).

---

### #58 — Backend: Diary search endpoint

**Priority**: P2.
**Source**: BACKEND-COORDINATION § A.3.
**Notes**: UI mock + localStorage history (DiaryView search overlay in S3 C38).

---

### #59 — Backend: Account deletion endpoint

**Priority**: P2.
**Source**: BACKEND-COORDINATION § A.4.
**Notes**: UI mock toast (Delete confirm modal in S2 C34).

---

### #60 — Backend: Notification preferences endpoint group

**Priority**: P2.
**Source**: BACKEND-COORDINATION § A.5.
**Notes**: UI localStorage mock (NotificationsView in S3 C46).

---

### #61 — Backend: Support tickets endpoint

**Priority**: P2.
**Source**: BACKEND-COORDINATION § A.6.
**Notes**: UI mock submit (SupportFormView in S3 C48).

---

### #62 — Backend: Messages CRUD endpoint group

**Priority**: P1 (S3 blocker).
**Source**: BACKEND-COORDINATION § A.7.
**Notes**: UI full mock on placeholder data (MessagesListView + ThreadView in S3 C49).

---

### #63 — Backend: Weekly AI summary endpoint

**Priority**: P2.
**Source**: BACKEND-COORDINATION § A.8.
**Notes**: UI placeholder (AISummaryView in S3 C50).

---

### #64 — Backend: DiaryEntry.type schema extension (journal/dream/insight)

**Priority**: P1.
**Source**: BACKEND-COORDINATION § B.1.
**Notes**: Frontend filter chip placeholder until ready (S3 C41 readme: «migrate when backend B.1 lands»). Decision #033.

---

### #65 — Backend: User.onboarding_completed schema extension (optional)

**Priority**: P3.
**Source**: BACKEND-COORDINATION § B.2.
**Notes**: localStorage v1 in S2 C20-C21 per decision #034. Cross-device parity deferred.

---

### #66 — Backend: User.language enum verification

**Priority**: P3.
**Source**: BACKEND-COORDINATION § B.3.
**Notes**: Verify enum supports values used by LanguageTimezoneView (S3 C47).

---

### #67 — Backend: Booking.notes field (master-request)

**Priority**: P2.
**Source**: BACKEND-COORDINATION § B.4.
**Notes**: BookingSuccessView (S2 C27) Запрос мастеру textarea — mock until field lands.

---

### #68 — Backend: Clarify /bookings vs /purchase endpoint usage

**Priority**: P0.
**Source**: BACKEND-COORDINATION § C.1.
**Notes**: Frontend default uses /purchase pending response per decision #040 (revisit if partner says free → /bookings).

---

### #69 — Backend: Stats source endpoint (if frontend computed insufficient)

**Priority**: P3.
**Source**: BACKEND-COORDINATION § C.2.

---

### #70 — Backend: ZOOM link delivery model

**Priority**: P2.
**Source**: BACKEND-COORDINATION § C.3.
**Notes**: Practice Live external Zoom link via window.open per decision #037.

---

### #71 — Backend: Refund window policy

**Priority**: P2.
**Source**: BACKEND-COORDINATION § C.5.

---

### #72 — Designer: Master-side batch (10 views)

**Priority**: High.
**Source**: DESIGN-DECISIONS-LOG § D.
**Notes**: Blocks S4 start per decision #030.

---

### #73 — Designer: Dark variants of new DS

**Priority**: High.
**Source**: DESIGN-DECISIONS-LOG § D.
**Notes**: Optional for S2 C25 theme toggle; otherwise S3+ refresh.

---

### #74 — Designer: Topup / balance redesign

**Priority**: Medium.
**Source**: DESIGN-DECISIONS-LOG § A.19 + § B.14.
**Notes**: S1 topup views remain as-is in S2 per decision #039.

---

### #75 — Designer: Empty/loading/error states

**Priority**: Medium.
**Source**: DESIGN-DECISIONS-LOG § A.22 + § B.11.
**Notes**: Minimum viable patterns inherited from S2/S3 until designer ships full mockup parity.

---

### #76 — Designer: Waitlist screens

**Priority**: Low.
**Source**: DESIGN-DECISIONS-LOG § A.25 + § D.

---

### #77 — Designer: Promo code UI

**Priority**: Low.
**Source**: DESIGN-DECISIONS-LOG § A.24 + § D.

---

### #78 — Designer: Reports/complaint flow

**Priority**: Low.
**Source**: DESIGN-DECISIONS-LOG § A.26 + § D.

---

### #79 — Designer: Diary expanded composer mockup

**Priority**: Medium.
**Source**: DESIGN-DECISIONS-LOG § B.5.
**Notes**: Frontend builds by analogy if not provided (S3 C40).

---

### #80 — Designer: City picker UI on onboarding (08)

**Priority**: Low.
**Source**: DESIGN-DECISIONS-LOG § B.3.

---

### #81 — Designer: Practice Live "video" placeholder real intent

**Priority**: Medium.
**Source**: DESIGN-DECISIONS-LOG § B.8.

---

### #82 — Designer: Booked vs Booking detail clarification (15 vs 18)

**Priority**: Medium.
**Source**: DESIGN-DECISIONS-LOG § B.4.

---

### #83 — Designer: Cancel booking refund window UI

**Priority**: Medium.
**Source**: DESIGN-DECISIONS-LOG § B.10.

---

### #84 — Designer: Onboarding flow ordering TMA vs PWA

**Priority**: Medium.
**Source**: DESIGN-DECISIONS-LOG § B.18.

---

### #85 — Future: Group chats for Messages

**Priority**: Backlog.
**Notes**: Out-of-scope MVP; future feature when Messages 1:1 stabilizes.

---

### #86 — i18n infrastructure when language switching reaches MVP

**Priority**: P3.
**Notes**: Implied by skin language toggle in NotificationsView (74) / LanguageTimezoneView (75). Pairs with BACKLOG #38 (probekit-i18n-audit hardening).

---

### #87 — ProbeKit: bundle-drift skill

**Priority**: P3 (defer).
**Source**: ProbeKit enhancement triage 2026-04-29; reaffirmed by S2 P05 C15 user roadmap 2026-04-30 §🟡-4 (medium-effort follow-up for S2 close audit retrospective).
**Notes**: Detect drift between `frontend/src/styles/variables.css` and bundle SSOT (`docs/04_assets/velo-design-system-2026-04-23/`) — extra/missing tokens, value mismatches, broken token namespacing per decision #009. **Defer until** S2/S3 close + new design batch landed (decision #029) — token ground-truth is mid-flux until the supersede settles. Re-evaluate at S3-Sprint-Closer.

---

### #88 — ProbeKit: decisions cross-reference skill

**Priority**: P3 (defer).
**Source**: ProbeKit enhancement triage 2026-04-29; reaffirmed by S2 P05 C15 user roadmap 2026-04-30 §🟡-5 (medium-effort follow-up for S2 close audit retrospective).
**Notes**: Auto-cross-reference findings against `docs/01_refer/decisions.md` ACTIVE rows; annotate findings with "covered by decision #NNN; defer/skip" so human review skips known-OK patterns. Roadmap variant also calls for scanning all docs for `decisions.md #NNN` references and flagging references to SUPERSEDED/DEPRECATED entries, references to non-existent numbers, and ACTIVE decisions without back-references (Clean-Sync §3 automation). **Defer until** decisions count > 60 — at 46 (post-#046) the manual list in `velo-presets.md` (Top decisions section) is sufficient.

---

### #89 — ProbeKit: CHANGELOG entry generator

**Priority**: P3 (defer).
**Source**: ProbeKit enhancement triage 2026-04-29; reaffirmed by S2 P05 C15 user roadmap 2026-04-30 §🟡-6 (medium-effort follow-up for S2 close audit retrospective).
**Notes**: Skill that scans Sprint-Closer/Clean-Sync diffs and proposes `docs/01_refer/ARCHIVES/CHANGELOG.md` entries (file moves, renames, archive relocations). Roadmap variant extends scope to auto-generating CHANGELOG entries from RESOLVED-eligible BACKLOG items in Clean-Sync Step 3 (preserves quotations from BACKLOG body for traceability, removes manual transcription). **Defer until** Clean-Sync scale demands — at S1 close the manual entry took ~5 min; not worth tooling yet.

---

### #90 — ProbeKit: Vue-3-specific architecture probe

**Priority**: P4.
**Source**: ProbeKit enhancement triage 2026-04-29.
**Notes**: Vue 3 idioms beyond what `probekit-arch-review` covers — Composition API misuse (`ref` vs `reactive` choice, `computed` vs `watchEffect`), `<script setup>` adherence, props/emits typing, store boundary discipline (Pinia setup vs options stores). Would complement `probekit-type-audit` (which is type-safety) and `probekit-arch-review` (which is project-independent). Low priority — current Velo code is small and reviewed.

---

### #91 — ProbeKit: PWA manifest probe

**Priority**: P4.
**Source**: ProbeKit enhancement triage 2026-04-29.
**Notes**: Validate `frontend/public/manifest.webmanifest` and `vite.config.ts` PWA plugin config — required icons present (192/512/maskable), `display: standalone`, `theme_color` matches `--bg-base` token, `start_url` correct, screenshots block present for richer install UI. Would surface PWA install-prompt issues before they hit staging. Low priority — manifest is currently stable.

---

### #92 — Designer batch commit-discipline: artefacts referenced in framework docs must be committed to repo at reference time

**Source**: S2-P06-OPEN §2 Combined Scout §S1 prerequisite gap (2026-04-30).

**Context**: The 2026-04-30 designer batch (decision #029, ~55 mockups, ~34 unique views per the decision narrative; actual fetch was 50 files including 8 phase-06 skin PNGs + DS reference layer) was referenced as a known artefact in:
- `docs/01_refer/decisions.md` row #029 (narrative)
- `docs/01_refer/ARCHITECTURE.md` §Components — Phase 03 additions / §S2 re-plan additions (narrative)
- `docs/03_sprint/S2-bundle-port/S2-SPRINT.md` (narrative)
- `docs/03_sprint/S2-bundle-port/DESIGN-DECISIONS-LOG.md` Context (narrative; cites `velo_screens_inventory.md` as "offline analysis artifact")

…but was NOT committed to the repository at any point during the 2026-04-30 re-plan session. The first Phase 06 scout (S2-P06-OPEN §2) pre-flight §S1 search returned `NOT FOUND ANYWHERE`, blocking Phase 06 design-port cycles C16–C21 entirely (each cycle requires a per-skin visual source for Claude Design pipeline + post-deploy visual verify gate). Resolved by the S2-P06-PREREQ-FETCH-DESIGN-BATCH execute prompt which fetched the batch from a Claude Design handoff URL and committed it to `docs/04_assets/velo-design-system-2026-04-30/`.

**Lesson / discipline rule** (proposed convention, not yet a decision): **whenever a framework or sprint doc references an external artefact (designer batch, partner schema, bundle update, ProbeKit version, etc.) by name, the same commit (or an immediately-following commit in the same chat session) MUST place the artefact in the repo at a stable path AND cite that path in the referencing doc.** Narrative-only references without a repo path create downstream gaps that surface only when consuming work begins (often weeks later, in fresh chats with no original-author context).

**Application checklist**:
1. Sprint-Builder / Phase-Builder OPEN: when a phase plan cites an external artefact, OPEN's first action is repo-commit of the artefact, NOT subsequent Combined Scout.
2. `decisions.md`: every row that references an artefact (by name, version, or external URL) must include a `Where it lives` cell pointing to a committed repo path. If `Where it lives` is "external (not in repo)" — that itself is a flag requiring justification.
3. Coord docs (BACKEND-COORDINATION, DESIGN-DECISIONS-LOG): rows referencing batches / schemas / mockups must cite repo paths or explicit "external — track in BACKLOG #NN" markers.

**Severity**: process-improvement (not blocking once batch committed).

**Sprint**: convention applies forward from S2-P06 onward. Apply at:
- S4 master design batch arrival (next likely repeat)
- Future bundle / DS updates
- Any partner deliverable referenced before commit (OpenAPI snapshots, etc.)

**Status**: OPEN (convention is informal; promote to `decisions.md` when convention is tested at next batch arrival).

**Related**: decision #029 (the trigger), Rule 29 (persist-or-lose; this entry is its first application — Rule 29 covers chat-internal lessons, this BACKLOG entry covers cross-session-reference artefacts).

---

### #93 — `--text-display-lg` token absent (WelcomeView wordmark hardcoded)

**Source**: S2-P06-C16 Validate stage (2026-04-30).

**Context**: `frontend/src/views/auth/WelcomeView.vue` styles VELΘ wordmark with `font-size: 56px` hardcoded. Token `--text-display-lg` absent both in `frontend/src/styles/variables.css` AND in new design batch's `docs/04_assets/velo-design-system-2026-04-30/project/colors_and_type.css`. Path Y polish-deferred at C16 close: TODO comment added in scoped style block, BACKLOG entry per Rule 29.

**Action**: at next DS update (designer-driven), propose adding `--text-display-lg: 56px` (or similar) to `colors_and_type.css`; then swap WelcomeView hardcoded to token reference. Affects future wordmark uses (LoginView/RegisterView/Onboarding screens currently use `--text-2xl` for compact title — different scale).

**Severity**: LOW (visual polish; no functional impact).
**Sprint**: S5+ polish cluster.
**Status**: OPEN.

---

### #94 — Onboarding illustrations don't match skins 05/06/07 designer assets

**Source**: S2-P06-C20 Pre-Exec G5 + Visual verify NIT findings (2026-04-30).

**Context**: `frontend/src/views/auth/OnboardingCarouselView.vue` uses 3 SVGs from `frontend/src/assets/illustrations/` (`live-practices.svg`, `ai-analytics.svg`, `self-map.svg`) as carousel slide illustrations. Designer's skins 05/06/07 in `docs/04_assets/velo-design-system-2026-04-30/project/uploads/` show DIFFERENT illustrations (people-cluster, feather-rising-from-book, figure-with-spiral-aura) — not present as separate SVG/PNG assets in the new batch (designer may have inlined them into the PNG mockups).

Path Y polish-deferred: existing 3 abstract SVGs used as placeholders during C20 to ship working carousel logic. Visual mismatch acknowledged.

**Action**: request designer to extract per-slide illustrations from skin PNGs as separate SVG/PNG assets in next batch. Then swap C20 imports.

**Severity**: NIT (visual polish; carousel functionally works with placeholders).
**Sprint**: S5+ polish cluster, contingent on designer asset delivery.
**Status**: OPEN.

---

### #95 — `cities.json` expansion from 118 to ~300 entries

**Source**: S2-P06-C21 implementation (2026-04-30).

**Context**: `frontend/src/data/cities.json` ships with 118 hand-curated entries covering Russian-speaking world + major Western/Asian cities. `DESIGN-DECISIONS-LOG.md` § A.3 originally targeted ~300 entries. 118 covers happy-path for ~80% of users; tail of ~180 cities (smaller European, Latin American, African, Asian-tier-2) absent. Native `Intl.DateTimeFormat().resolvedOptions().timeZone` browser fallback handles unmatched cities — graceful, but city name not stored explicitly in user record.

**Action**: at next polish cycle, expand JSON to ~300 entries; consider auto-generating from `Intl.supportedValuesOf('timeZone')` + IANA TZ DB if available.

**Severity**: LOW (current 118-entry coverage handles ~80% of users; browser fallback for the rest).
**Sprint**: S5+ polish cluster.
**Status**: OPEN.

---

### #96 — `velo update` script transient "Uncommitted changes" first-attempt issue

**Source**: S2-P06 deploy ops (recurred at C17/C18/C19 deploy + C20/C21 deploy, 2026-04-30).

**Context**: `velo update` SSH script on staging server (37.1.204.171) reported "Uncommitted changes detected" on first attempt of two consecutive Phase 06 batch deploys (b060ba3 push + de496f6 push). Both times the dirty-file list was empty in captured output. Retry succeeded both times — server tree was clean by retry diagnostic. Likely script timing artifact: `git status` runs before fetch/cleanup completes, OR a parallel watcher writes-then-cleans a build artifact.

**Action**: investigate `velo update` script implementation on staging server; determine root cause. Either:
1. Add brief `sleep` before `git status` check
2. Use `git status --porcelain --untracked-files=no` to ignore transient untracked files
3. Document the retry pattern in `SERVER-ACCESS.md` as known transient

Two consecutive recurrences suggest systematic, not random. C16 deploy (cc4e2fd) did NOT exhibit this — possibly tied to commit size (b060ba3 = +805 LOC, de496f6 = +661 LOC, cc4e2fd = +131 LOC) — large commits trigger longer build → more chance of timing race.

**Severity**: P2 (was LOW; promoted at S2-S3-Speedrun closure 2026-04-30 — hypothesis confirmed).
**Sprint**: post-demo investigation cycle (S5+).
**Status**: OPEN — hypothesis CONFIRMED.

**Update 2026-04-30 (post-MEGA-2 deploy)**: hypothesis CONFIRMED. Cumulative deploy data:

| Deploy | Commit | LOC delta | Transient |
|---|---|---|---|
| C16 | cc4e2fd | +131 | ✗ no |
| C17–C19 | b060ba3 | +805 | ✓ yes |
| C20–C21 | de496f6 | +661 | ✓ yes |
| MEGA-1 | 6c5fd1f | +5218 | ✓ yes |
| MEGA-2 | af39b41 | +6443 | ✓ yes |

4/4 deploys ≥600 LOC fire transient; 1/1 small deploy (+131) clean. Mechanism: timing race in `velo update` script's pre-fetch `git status` check when build window from prior deploy hasn't fully released file locks / git index. Larger commit = longer rebuild = wider race window. Frontend-side workaround (paramiko retry on transient) confirmed working but masks root cause. **Server-side fix candidate**: add defensive `git diff --quiet HEAD || git stash` line OR retry-loop in `velo update` script.

---

### #97 — Backend endpoint `POST /bookings/{id}/leave` not implemented

**Source**: S2-S3 SPEEDRUN MEGA-1 cycles C29/C32 (PracticeLiveView + BookedPracticeView leave/cancel flows), 2026-04-30.

**Context**: Demo flow allows a user to "Покинуть" a live practice (PracticeLiveView) and to cancel a booked-but-not-yet-attended slot (BookedPracticeView). MEGA-1 wired both buttons to `useBookingsStore.cancelBooking(bookingId)` (existing endpoint `DELETE /bookings/{id}` → `cancelled` status). This is functionally correct for the demo but semantically conflates two states:
1. Cancel-before-start (user changes mind, slot opens for waitlist)
2. Leave-mid-session (user joined Zoom, then left early)

For attendance/analytics fidelity, `leave` should mark the booking with status `attended_partial` or similar, not `cancelled` (which inflates cancellation rate).

**Action**: Backend partner — add `POST /bookings/{id}/leave` mapping to `attended_partial` status. Frontend call site already isolated in `PracticeLiveView.vue` (currently calls `cancelBooking`). Swap to dedicated method when endpoint lands. Also surfaces in B.5 (#22) — currently lacks dedicated leave/join semantics.

**Severity**: LOW (cancel-as-leave functions for demo; analytics impact post-demo).
**Sprint**: post-demo backend cycle.
**Status**: OPEN.

---

### #98 — Emoji cleanup MEGA-2 carry — 23 in-scope emoji remain (decision #048)

**Source**: S2-S3 SPEEDRUN MEGA-1 close, 2026-04-30.

**Context**: Decision #048 (no-emoji policy in user-visible UI) requires removal of 71 in-scope emoji surfaced by Phase 06 inventory. MEGA-1 cleared **48 sites** (rewritten user-flow views: Dashboard/Calendar/PracticeDetail/Checkin/Feedback/Profile/Booking* + supporting compat shims in `displayHelpers.ts` left as `@deprecated` empty-string maps for legacy consumers). **23 sites remain** in:
- `frontend/src/components/shared/DiaryList.vue` (mood/rating chips render via deprecated maps)
- `frontend/src/components/shared/PracticeCard.vue` (practice-type accent chip)
- `frontend/src/components/shared/BookingCard.vue` (status accent chip)
- `frontend/src/components/shared/FormShell.vue` (validation feedback chips)
- `frontend/src/views/master/*.vue` (master-side practice/booking lists — 4 views)
- Diary detail components (DiaryCheckinDetail, DiaryFeedbackDetail, DiaryEntryDetail)

These are scheduled to be cleared by MEGA-2 (S3 P10/P11/P12/P13) in cycle C36 (Diary refresh) and the master-suite refresh (C40-C44). Once all 23 callsites are converted to `PRACTICE_TYPE_ICON` / icon-component patterns, the deprecated `PRACTICE_TYPE_EMOJI`/`MOOD_EMOJI`/`RATING_EMOJI` maps can be deleted from `displayHelpers.ts`.

**Action**: Track to MEGA-2 close. Verification grep at MEGA-2 close: `grep -rIE "(😀|😢|😴|😌|🧘|🌬|💆|🎬|✨|🔥|❤|⚠|💔|🧠)" frontend/src/` should return 0 in-scope hits.

**Severity**: LOW (compat shims keep build green; cosmetic carry).
**Sprint**: S3 MEGA-2.
**Status**: CLOSED — 2026-04-30 MEGA-2 close: emoji audit grep returns 0 hits in `frontend/src/views/user/`, `frontend/src/components/shared/`, `frontend/src/utils/`. Cleanup landed across 12 files (DiaryList, BookingCard, PracticeCard, FormShell, CancelBookingPopup, DiaryCheckinDetail/FeedbackDetail/EntryDetail/EntryForm, MyBookingsView, TopupCancel/SuccessView, adminHelpers).

---

### #99 — Backend public master endpoint `GET /api/v1/masters/{id}` + `MasterPublicResponse`

**Source**: S2-S3 SPEEDRUN MEGA-2 §C51 MasterProfilePublicView (2026-04-30).

**Context**: Frontend now renders a public master profile at `/user/master/:id`. There is no `GET /api/v1/masters/{id}` endpoint (Code anomaly #2 from MEGA-2 scout). Current implementation derives master metadata (name + avatar) from `PracticeSummary` via `getPractices({ master_id })` — degraded v1.

Missing fields needed for full skin 25 fidelity:
- `bio: string` — multi-paragraph description (currently placeholder text)
- `methods: string[]` — chip group (currently hidden)
- `experience_years: number` — "10 лет опыта" mint chip (currently hidden)
- `practice_count: number` — "156 / Практик" stat card (currently hidden)
- `review_count: number` — "89 / Отзывов" stat card (currently hidden)
- `is_verified: boolean` — currently always shown as true (placeholder)

**Action**: Backend partner — add public-read endpoint `GET /api/v1/masters/{id}` returning `MasterPublicResponse`. Service-layer source: aggregate `PracticeStats` (count of completed) + `Feedback` count (review count) + `MasterProfile` (bio/methods/experience/is_verified). Frontend swap: replace `getPractices({ master_id, limit:3 })` derive in `MasterProfilePublicView.vue` onMounted with single fetch, then re-enable stat cards + bio + methods + experience chip blocks.

**Severity**: LOW (degraded view functions for demo; full-fidelity post-demo).
**Sprint**: post-demo backend cycle.
**Status**: OPEN.

---

### #100 — Post-demo S2/S3 audit cycle reactivation

**Source**: Speedrun mode (decision #049) deferred audit ceremony for sponsor-demo target.

**Context**: S2 + S3 closure commit (2026-04-30) was authored without running Sprint-Closer Step 1+ ProbeKit lite audit profile (6 skills: type-audit, code-audit, a11y-audit, responsive-audit, security-audit, design-audit). The deferral is explicit in decision #049 — a quality-vs-throughput trade for sponsor-demo target. Audit + retro rigor + pixel polish must be backfilled prior to production promotion.

Speedrun delta requiring audit:
- ~9,521 LOC delta (S1 16,061 → S3-end 25,582 — derived from cloc on git-archive trees of 4029343, 6c5fd1f, af39b41)
- 73 new files (Vue + TS + JSON)
- 28 new view files (S2 P07-P09 + S3 P10-P13)
- ~25 new shared components
- 25 new icon components (11 MEGA-1 + 14 MEGA-2)
- 3 new stores (notifications, messages, bookings extension via getters)
- 2 store extensions (ui theme, diary search/filter/history)
- 13 new routes (path count 48 → 68)

**Action**: Run Sprint-Closer Step 1+ ProbeKit lite profile (6 skills) against actual S2 + S3 code state. Author `docs/01_refer/ARCHIVES/CODE-AUDIT/S2-CODE-AUDIT.md` + `S3-CODE-AUDIT.md` per Sprint-Closer Step 4 format. Classify findings (CRITICAL / HIGH / MEDIUM / LOW); persist MEDIUM/LOW to BACKLOG; resolve CRITICAL/HIGH inline before promotion.

**Severity**: MEDIUM (deferred quality gate; not blocking demo; required prior to production promotion).

**Sprint**: post-demo polish cluster (S5+); reactivation gates production promotion of S2 + S3 work.

**Cross-refs**: decision #049 (speedrun mode), CHANGELOG.md S2-S3 closure entry, S2-SNAPSHOT.md + S3-SNAPSHOT.md "Code Audit Result" rows (deferred).

**Status**: OPEN.
