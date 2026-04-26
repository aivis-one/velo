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
