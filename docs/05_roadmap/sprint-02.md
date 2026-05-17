# Sprint 2 — Styleguide + First Mockups (P0)

```
Dates:    TBD → TBD (planned 1 week)
Status:   planned
Owner:    Cowork (executor), Operator (validator)
Goal ref: ROADMAP.md §5
Phase:    Phase 3 (Styleguide HTML) + Phase 4 (initial P0 mockups)
```

---

## Goal

Build the living styleguide (Phase 3) and deliver the first batch of
mockups (P0 priority screens — typically one dashboard per role plus a
shared auth flow start, 4–6 mockups total).

---

## Scope

Six tasks. P0 mockups for 4–6 screens; their specs follow in the
respective role-block sprint (Sprint 3 for user-dashboard, Sprint 5 for
master-dashboard, Sprint 7 for admin-dashboard).

| # | Task | Owner | Phase |
|---|---|---|---|
| T2.1 | Phase 3 — Styleguide HTML | Cowork | 3 |
| T2.2 | STYLEGUIDE GATE validation | Operator | 3 |
| T2.3 | P0 mockup identification | Operator | — |
| T2.4 | Phase 4 — Build P0 mockups (4–6 screens) | Cowork | 4 |
| T2.5 | MOCKUP GATE validation per P0 screen | Operator | 4 |
| T2.6 | Frontend i18n setup | Claude Code | — |

---

## Task checklist

### T2.1 — Phase 3: Styleguide HTML

Ref: VELO-METHODOLOGY.md §6.8 + Prompt §9.4.
Owner: Cowork (via `livemockup-studio` skill).

- [ ] File at `02_design-system/styleguide/velo-design-system.html`
- [ ] All VELO tokens inlined in `<style>` (from `variables.css` + `global.css`)
- [ ] Token bridge for `livemockup-studio` shell at top of `<style>` (per §11.3 canonical bridge)
- [ ] Mobile device frame default at 402px width
- [ ] Top-level tab "Tokens":
      - [ ] Colors — swatch per `--velo-color-*` primitive (square + name + hex)
      - [ ] Semantic — table mapping Layer 2 → Layer 1 → resolved value
      - [ ] Typography — live example of every `.velo-typo-*` class
      - [ ] Spacing — visual bar scale per `--velo-space-N`
      - [ ] Radius — rounded box per `--velo-radius-*`
      - [ ] Shadows — card sample per `--velo-shadow-*`
      - [ ] Icons — grid of all PNG icons with names
- [ ] Top-level tab "Components":
      - [ ] All Tier 1 components with all variants × all states (§6.6)
      - [ ] All Tier 2 components with sample VELO data (§7.6)
      - [ ] Each component group labeled with name + variant matrix
- [ ] Top-level tab "Patterns":
      - [ ] Header + TabBar for all 3 role variants
      - [ ] Form pattern: VInput + VSelect + VButton + error state
      - [ ] List pattern: 3 PracticeCards + PaginationLoader
      - [ ] Modal pattern: overlay + content + close
- [ ] Russian sample text throughout (no Lorem ipsum)
- [ ] Every interactive element produces visual feedback (toast or state change)
- [ ] Navigation Map (📍) shows all sections
- [ ] `livemockup-studio` test protocol: 0 BLOCKER, ≤2 MAJOR

### T2.2 — STYLEGUIDE GATE validation

Ref: VELO-METHODOLOGY.md §10.3.
Owner: Operator.

- [ ] File at `02_design-system/styleguide/velo-design-system.html` exists
- [ ] Opens in a modern browser without console errors
- [ ] All three top-level tabs (Tokens, Components, Patterns) populated
- [ ] Every declared Tier 1 component visible with declared variants
- [ ] Every declared Tier 2 component visible with sample data
- [ ] Navigation Map (📍) shows all sections
- [ ] `livemockup-studio` test protocol result: 0 BLOCKER, ≤2 MAJOR
- [ ] Side-by-side check against Figma "Design System" page (if present) or mockup PNGs
- [ ] Approve or revise

### T2.3 — P0 mockup identification

Owner: Operator. Done at sprint start.

- [ ] Declare which 4–6 screens are P0 (developer needs them first)
- [ ] Record the chosen P0 list here:
      1. _________
      2. _________
      3. _________
      4. _________
      5. _________
      6. _________
- [ ] Typical candidates listed in ROADMAP §5.1 T2.3: one dashboard per
      role (user-dashboard, master-dashboard, admin-dashboard) + a
      shared auth flow start (welcome or login)

### T2.4 — Phase 4: P0 Mockups

Ref: VELO-METHODOLOGY.md §7 + Prompt §9.5 (per screen).
Owner: Cowork.

For each of the 4–6 P0 screens, the following must hold (repeat the
checklist below per screen):

- [ ] HTML file at `03_mockups/{role}/{screen-name}.html`
- [ ] Skeleton per §7.3 (tokens inlined, bridge present, device shell)
- [ ] Mobile 402×874 default viewport
- [ ] All visible VELO components used per styleguide (no inline rewrites)
- [ ] Realistic VELO sample data per §7.6 (Russian, domain-correct)
- [ ] State triad demonstrated per §7.7 (loading / empty / populated / error)
      via toolbar toggle
- [ ] Toolbar present: device switcher + zoom + Navigation Map (📍)
- [ ] Toast feedback for every interactive element per §7.5
- [ ] Russian text only; no Lorem ipsum
- [ ] `livemockup-studio` test protocol: 0 BLOCKER, ≤2 MAJOR
- [ ] `03_mockups/INDEX.md` updated with new row (status "🔄 awaiting review")

### T2.5 — MOCKUP GATE validation (per P0 screen)

Ref: VELO-METHODOLOGY.md §10.4.
Owner: Operator. Repeat per screen.

- [ ] HTML opens at 402×874 without horizontal scroll
- [ ] Visual matches Figma screenshot in
      `02_design-system/assets/screenshots/{role}-{name}.png` within AA
      rendering deltas
- [ ] State triad (loading/empty/populated/error) accessible via toolbar
- [ ] All interactions produce visual feedback (toast or state change)
- [ ] Navigation Map shows expected screens/endpoints/destructive counts
- [ ] All text in Russian, no Lorem ipsum, no placeholder names
- [ ] 0 BLOCKER per livemockup-studio test protocol
- [ ] Approve (update `03_mockups/INDEX.md` to ✅) or send revision

### T2.6 — Frontend i18n setup

Ref: ROADMAP.md §5.1 T2.6.
Owner: Claude Code.

- [ ] `npm install vue-i18n` in `frontend/` (or `vue-i18n@latest`)
- [ ] Create `frontend/src/i18n/index.ts` with `createI18n()` configuration
- [ ] Create `frontend/src/i18n/locales/ru.json` (empty `{}` or stub root keys)
- [ ] Create `frontend/src/i18n/locales/en.json` stub
- [ ] Wire i18n into `frontend/src/main.ts` (`app.use(i18n)`)
- [ ] `npm run build` passes
- [ ] `npm run typecheck` passes
- [ ] Unblock Sprint 3 specs that declare i18n keys

---

## Sprint 2 Gate

Ref: ROADMAP.md §5.2.

- [ ] STYLEGUIDE GATE passed (T2.2)
- [ ] 4–6 P0 mockups built; MOCKUP GATE passed for each
- [ ] `03_mockups/INDEX.md` reflects P0 status
- [ ] vue-i18n installed and minimally wired in `frontend/`

---

## Risks

| ID | Risk | Mitigation |
|---|---|---|
| 2.A | Styleguide reveals missing components not yet identified. | Log in `02_design-system/INDEX.md → Open TODOs`, add to Tier 2 list, build before they're needed for mockups. |
| 2.B | P0 screens reveal token gaps (no destructive color, no hover state). | Re-entry into Phase 2 per §4.3, add tokens to master, propagate. Log iteration. |
| 2.C | Sprint 1 left MISSING placeholders that block styleguide content. | Triage at sprint start; either upgrade placeholders to concrete values via §6.4 or skip those styleguide blocks until updated. |

---

## Daily log

- 2026-MM-DD: …

---

## Closure

- STYLEGUIDE GATE: ☐ passed / ☐ failed
- P0 MOCKUP GATEs: ☐ N of M passed (list failures: __________)
- Deferred to Sprint 3+: ☐
- Methodology amendments proposed: ☐
- Token master changed during sprint? ☐ yes → incremental sync to `frontend/` per ROADMAP §15.2 step 4
- Operator signoff (date): ☐

---

## References

- Roadmap: `ROADMAP.md` §5
- Methodology: §6.6 (component tiers), §6.8 (styleguide), §7 (mockup layer), §10.3 (STYLEGUIDE GATE), §10.4 (MOCKUP GATE), §11.2–11.3 (anti-patterns + token bridge), §9.4–9.5 (prompts)
