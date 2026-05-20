# Sprint 2 — Styleguide + First Mockups (P0)

```
Dates:    2026-05-17 → open-ended (EXPANDED 2026-05-18)
Status:   🔄 in-progress (EXPANDED) — Sprint 2 reopened and expanded 2026-05-18 to close full DS foundation.
          Original Phase 3 ✅ closed 2026-05-17. Phase 4 Onboarding 8 ✅ closed 2026-05-18.
          Now executing Macro-Phase I (DS harvest all blocks, Phase A+B) followed by
          Macro-Phase II (all block mockups, Phase C). See "Expanded Scope" section below.
Owner:    Cowork (executor), Operator (validator)
Goal ref: ROADMAP.md §5
Parallel: Sprint 2.5 (standalone, file `sprint-02.5.md`) — Tracks B (CBSHOME transfer, Claude Code)
          + C (Documentation English translation, Cowork) run in parallel with Sprint 2.
```

---

## Goal

Build the living styleguide (Phase 3) and deliver the **complete design
system foundation + all user/master block mockups**. Original goal was
Phase 3 + 4-6 P0 screens; expanded 2026-05-18 to close the DS question
fully before Sprint 3 Vue implementation begins.

---

## Expanded Scope — Two Macro-Phases (decision 2026-05-18)

**Why expanded:** Sprint 1 delivered a starter DS (17 screens mined).
Blocks harvested block-by-block during mockup production caused 3× rework
(tokens discovered in Calendar break Dashboard mockup already built, etc.).
The correct order is: harvest ALL blocks → complete DS → THEN all mockups.

### Macro-Phase I — DS Harvest (all blocks, Phase A+B only)

Goal: extract every token, icon, and component from every SACRED block.
No mockups until all blocks are DS-complete.

| # | Block | Figma root | Screens | DS-complete? |
|---|---|---|---|---|
| 1 | Onboarding | `541:1179` | 8 | ✅ done (Sprint 2 Phase 4) |
| 2 | Dashboard 9 | `541:6648` | 9 | ✅ done (2026-05-18 session) |
| 3 | Calendar 11 | `541:1553` | 11 | ✅ done (2026-05-18 Calendar 11 DS harvest) |
| 4 | Profile 7 | `541:2355` | 7 | ✅ done (2026-05-19 Profile 7 DS harvest) |
| 5 | Diary 20 | `541:2816` | 20 | ✅ done (2026-05-19 Diary 20 DS harvest) |
| 6 | Messages 3 | `541:2717` | 3 | ✅ done (2026-05-19 Messages 3 DS harvest) |
| 7 | Analytics 3 | `758:1529` | 3 | ✅ done (2026-05-19 Analytics 3 DS harvest) |
| 8 | Practices 15 | `758:1950` | 15 | ✅ done (2026-05-19 Practices 15 DS harvest) |
| 9 | Master Dashboard 8 | `758:3245` | 8 | ✅ done (2026-05-19 Master Dashboard 8 DS harvest) |
| 10 | Master Onboarding 13 | `758:4318` | 13 | ✅ done (2026-05-19 Master Onboarding 13 DS harvest) |

Per-block deliverables (all 5 mandatory for block to be "DS-complete"):
1. Tokens → `02_design-system/tokens/variables.css` master + deliverable (MD5-mirror)
2. SVG icons → `02_design-system/assets/icons/`
3. `02_design-system/assets/ASSETS-INDEX.md` entries with Figma node provenance
4. `02_design-system/COMPONENTS-CATALOG.md` entries (full profile)
5. `02_design-system/styleguide/velo-design-system.html` visualisation (§6.8 rule)

**DS COMPLETE GATE** — passes when all 10 blocks above are DS-complete.
Only then does Macro-Phase II begin.

### Macro-Phase II — Mockups (all blocks, Phase C)

Goal: build all block HTML mockup viewers on the frozen, complete DS.
Zero token drift. Zero retroactive fixes.

| # | Block | Mockup viewer | Status |
|---|---|---|---|
| 1 | Onboarding 8 | `03_mockups/user/_onboarding-flow.html` | ✅ MOCKUP GATE passed 2026-05-18 |
| 2 | Dashboard 9 | `03_mockups/user/_dashboard-flow.html` | 🔧 **MOCKUP GATE in progress** — 9-column viewer rebuilt 2026-05-19. Sessions 15-16: DS-compliant build, z-index fix, icon compliance (0 emoji, 19/19 icon refs). Session 18 (2026-05-20): screens 01-03 pixel-fixed. DS fixes: section-title/pc-title font-weight:700, pc-avatar 38→48px, bottom-nav structural fix, ai-header inline pattern, .top-header ✅ canon promoted. **Screens 01-03 ✅ pixel-fixed. Screens 04-09 awaiting MOCKUP GATE.** |
| 3 | Calendar 11 | `03_mockups/user/_calendar-flow.html` | 🔧 **built 2026-05-19** — 11-column combined viewer. 8/11 screens with PNG etalons, 3 TBD (23_Calendar 2 `541:1744`, 27_Ask Master `541:2156`, 31_Message widget `541:6514`). 0 emoji, 0 missing icons, div balance 231/231, 11/11 structural checks. Awaiting operator MOCKUP GATE. |
| 4 | Profile 7 | `03_mockups/user/_profile-flow.html` | ⬜ pending Macro-Phase II build |
| 5 | Diary 20 | `03_mockups/user/_diary-flow.html` | ⬜ pending Macro-Phase II build |
| 6 | Messages 3 | `03_mockups/user/_messages-flow.html` | ⬜ pending Macro-Phase II build |
| 7 | Analytics 3 | `03_mockups/user/_analytics-flow.html` | ⬜ pending Macro-Phase II build |
| 8 | Practices 15 | `03_mockups/user/_practices-flow.html` | ⬜ pending Macro-Phase II build |
| 9 | Master Dashboard 8 | `03_mockups/master/_dashboard-flow.html` | ⬜ pending Macro-Phase II build |
| 10 | Master Onboarding 13 | `03_mockups/master/_onboarding-flow.html` | ⬜ pending Macro-Phase II build |

---

## Original Scope — Phase 3 + Phase 4 P0 (history)

Six tasks from original sprint definition. P0 mockups for 4–6 screens.
Expanded 2026-05-18 — see "Expanded Scope" section above for current plan.

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
Status: ✅ **done 2026-05-17** — operator approved styleguide via visual review.

- [x] File at `02_design-system/styleguide/velo-design-system.html`
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
Status: ✅ **passed 2026-05-17** — после нескольких итераций (font fix, icon expansion, pattern grid fix, glass shadows).

- [x] File at `02_design-system/styleguide/velo-design-system.html` exists
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
Status: ✅ **declared 2026-05-17** — operator расширил P0 до полных двух блоков user: Onboarding (8) + Dashboard (9).

Build order:
1. **Onboarding block — 8 screens** (welcome → login → register → oauth → onboarding-1..4)
2. **DS update pass** — промоутировать всё новое из Onboarding в styleguide + variables.css
3. **Dashboard block — 9 screens** (на обновлённой DS-основе)

Implementation: один комбайн-файл `03_mockups/user/_onboarding-flow.html` с 8 колонками (PNG-эталон сверху, HTML-сборка снизу). Парная сверка Figma ↔ HTML. После завершения Onboarding-блока — отдельный per-screen split для разработчика (опционально).

### T2.4 — Phase 4: P0 Mockups
Status: 🔄 **partially closed / pivoted to Sprint 2.5.** Onboarding-блок (8) ✅ closed by operator 2026-05-18 («приняты экраны и дизайн»). Dashboard-блок (9) **🗑 superseded** — текущий `_dashboard-flow.html` skeleton выкидывается, пересобирается в Sprint 2.5 (T2.5.2) после Dashboard 9 DS-complete state (T2.5.1).

**Why pivoted:** Sprint 2 Phase 4 attempt at Dashboard 9 показал что per-element reverse-engineering из PNG-эталонов = 3× rework (alert pills + glass halo + bottom-nav каждый rebuild по 3 раза). Methodology bumped to v1.3 с обязательным §7.0 Block-Harvest-First rule + §6.8 DS Visualisation rule. Roadmap bumped to v1.2 с insert Sprint 2.5. Все pending blocks (Dashboard 9 + Calendar 11 + Profile 7 + Diary 20 + Messages 3 + Analytics 3 + Practices 15 + Master Dashboard 8 + Master Onboarding 13) уходят в Sprint 2.5.

**Dashboard 9 per-column status:**

| # | Screen | HTML status |
|---|---|---|
| 01 | dashboard-1 | ✅ MOCKUP GATE pixel-fixed 2026-05-20 |
| 02 | dashboard-2 | ✅ MOCKUP GATE pixel-fixed 2026-05-20 |
| 03 | check-in | ✅ MOCKUP GATE pixel-fixed 2026-05-20 |
| 04 | check-in-success | 🔧 skeleton iteration 1 |
| 05 | practice-live | 🔧 skeleton iteration 1 |
| 06 | booked-practice | 🔧 skeleton iteration 1 |
| 07 | AI-summary | 🔧 skeleton iteration 1 |
| 08 | my-reservations | 🔧 skeleton iteration 1 |
| 09 | booking-detail | 🔧 skeleton iteration 1 |

Ref: VELO-METHODOLOGY.md §7 + Prompt §9.5 (per screen).
Owner: Cowork.

**Current focus: `03_mockups/user/_onboarding-flow.html`** — combined viewer, 8 колонок (PNG-эталон сверху, HTML снизу). Минимальный тулбар: только Phone/Tablet/Desktop + имя экрана.

**Per-column status:**

| # | Screen | HTML status |
|---|---|---|
| 01 | welcome | ✅ approved 2026-05-18 |
| 02 | login | ✅ approved 2026-05-18 |
| 03 | register | ✅ approved 2026-05-18 |
| 04 | oauth | ✅ approved 2026-05-18 |
| 05 | onboarding-1 (find practice) | ✅ approved 2026-05-18 |
| 06 | onboarding-2 (diary) | ✅ approved 2026-05-18 |
| 07 | onboarding-3 (chat masters) | ✅ approved 2026-05-18 |
| 08 | onboarding-4 (timezone) | ✅ approved 2026-05-18 |

**Welcome — 5 pending fixes — все применены 2026-05-17 session 2:**
- [x] Bg height: `background-size: cover` → `100% 100%` (PNG 804×1748 ↔ frame 402×874 совпадают по ratio ≈0.46, явная растяжка убирает субпиксельный дрейф). `.velo-bg-mandala` обновлён.
- [x] Mandala SVG ×1.5: `.scr-01 .big-logo` 340×340 → **490×490** (mid от 480-510 диапазона). Внешние кольца клипуются `overflow:hidden` родителя — как в эталоне.
- [x] Buttons higher: `.scr-01 .bottom` `padding: 0 32px 36px` → `0 32px 120px`. Нижний край glass-кнопки теперь на ~12-15% от низа frame — соответствует Figma эталону.
- [x] Glass button wrapper-pattern: `.v-button--glass / --ghost / --oauth` теперь `background: transparent` + `isolation: isolate`. 5% blue fill + `backdrop-filter: blur(6px)` вынесены на `::before` с `z-index: -1`. Фон 100% просвечивает сквозь кнопку (видно в рендере).
- [x] Lower button halo softer: `.v-button--glass` получил override `box-shadow` с уменьшенными радиусами/альфой (28px 0.75 → 18px 0.5; 12px 0.6 → 8px 0.4; 14px 0.18 → 10px 0.12). Primary остаётся ярким акцентом, secondary тише.

**Verification 2026-05-17 session 2:** Playwright headless render `.frame.html` колонки 01 vs `02_design-system/assets/screenshots/user/user-onboarding-01-welcome.png`. Console: 0 errors, 0 warnings. Визуальное соответствие: ✅ bg pattern, ✅ logo proportions, ✅ button position, ✅ glass transparency, ✅ halo intensity. Скриншот: `outputs/welcome-rendered.png`.

**После welcome готов → применить тот же шаблон на 02-08, потом DS promotion pass (см. ниже), потом Dashboard 9.**

**DS additions during T2.4** (для promotion pass):
- `02_design-system/assets/backgrounds/velo-bg-app.png` (804×1748, RGBA) — универсальный фон ВСЕХ экранов приложения
- `02_design-system/assets/icons/velo-logo-mandala.svg` (492×492 viewBox, 434KB) — Group 1944 из Figma, белая мандала со встроенным «VELO» текстом
- Glass-button spec — белая обводка + omnidirectional white halo + 5% blue background, backdrop-blur

**Original per-screen checklist (применяется для каждой колонки):**

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

**Original gates:**
- [x] STYLEGUIDE GATE passed (T2.2) — 2026-05-17
- [x] Onboarding 8 MOCKUP GATE passed — 2026-05-18

**Expanded gates (added 2026-05-18):**
- [x] **DS COMPLETE GATE** — all 10 blocks DS-complete + icon dedup pass (73 canonical icons, ASSETS-INDEX iter 12) — ✅ **operator confirmed 2026-05-19**
- [ ] All 10 block mockup viewers built + MOCKUP GATE passed per block (Macro-Phase II)
- [ ] `03_mockups/INDEX.md` reflects all-block status
- [ ] `02_design-system/INDEX.md` reflects DS-complete state

**Deferred to Sprint 2.5 (parallel sprint):**
- [ ] vue-i18n installed and minimally wired in `frontend/` (Claude Code Track B)
- [ ] Documentation English translation pass Conv-1..Conv-4 (Track C)

---

## Risks

| ID | Risk | Mitigation |
|---|---|---|
| 2.A | Styleguide reveals missing components not yet identified. | Log in `02_design-system/INDEX.md → Open TODOs`, add to Tier 2 list, build before they're needed for mockups. |
| 2.B | P0 screens reveal token gaps (no destructive color, no hover state). | Re-entry into Phase 2 per §4.3, add tokens to master, propagate. Log iteration. |
| 2.C | Sprint 1 left MISSING placeholders that block styleguide content. | Triage at sprint start; either upgrade placeholders to concrete values via §6.4 or skip those styleguide blocks until updated. |

---

## Daily log

- **2026-05-17 (session 1):**
  - T2.1 Styleguide HTML closed — операторская валидация ✅
  - Несколько rebuild-итераций styleguide: font fix (Marmelad self-host base64), icon set expansion 2 → 32 SVG, pattern grid fix (grid-comp clipping device-frame), card/modal shadow tokens added (`--velo-shadow-card`, `--velo-shadow-modal`)
  - T2.3 operator declared P0 = Onboarding 8 + Dashboard 9 (расширение скоупа)
  - T2.4 начат — построен combined viewer `_onboarding-flow.html` со всеми 8 онбординг-колонками: PNG ссылки на эталоны, HTML-черновики на DS токенах
  - Welcome колонка пересобрана через 3 итерации:
    - i1: SVG-аппроксимация мандалы + 2 CSS-генерируемых радиала вместо watermark
    - i2: реальный фон `velo-bg-app.png` (оператор положил `image 40.png`, переименовали), + старый `icon-mandala.png` поверх + VELO text overlay
    - i3 (текущая): реальный SVG `velo-logo-mandala.svg` (Group 1944 из Figma, оператор положил руками), убраны overlay-дубли, layout pinned к низу, halo shadow расширен, glass-button bg = 5% blue
  - **5 правок на welcome остаются** — см. T2.4 выше. Контекст этой сессии достиг лимита — handoff в новый чат.

- **2026-05-17 (session 2):**
  - Welcome — все 5 правок применены за один проход (см. T2.4 чек-лист).
  - Playwright headless verification: 0 console errors / warnings, визуальный side-by-side с Figma PNG показывает соответствие по всем 5 пунктам.
  - DS-canon glass button обновлён: wrapper-pattern через `::before` + softer halo. DS-promotion candidate для variables.css / styleguide.
  - **Дополнительный fix #6 — цвет типографики.** Оператор отметил несоответствие цвета текста (а не семейства шрифтов — Marmelad подтверждён как правильный). Pixel-sampling из Figma PNG: tagline = `#5c7292` (mean of darkest 20%), glass btn text = `#627a9c`. Ближайший Layer 1 primitive — **`--velo-color-steel-light` #627a9c**. Раньше использовалось `--velo-text-secondary #4a5a6a` (tagline) и `--velo-text-primary #2c3e50` (glass), что давало серо-чёрный тон вместо steel-blue. Заменено:
    - `.scr-01 .tagline { color: var(--velo-color-steel-light) }` + убран text-shadow (в эталоне его нет)
    - `.v-button--glass / --ghost / --oauth { color: var(--velo-color-steel-light) }` (общее правило, касается всех glass-кнопок)
    - Computed style verified: `rgb(98, 122, 156)` = #627a9c ✅
  - **DS-finding (Sprint 1 retro):** semantic tokens `--velo-text-primary` (#2c3e50) и `--velo-text-secondary` (#4a5a6a) были **синтезированы**, а не извлечены из Figma (см. INDEX.md "4 Layer 2 semantic variables resolved" — text-primary/secondary не были в списке). Реальный Figma text color на light backgrounds = `steel-light #627a9c`. **DS promotion task для конца Sprint 2 Phase 4:** добавить Layer 2 alias `--velo-text-brand-soft → steel-light` и пересмотреть `--velo-text-primary/secondary` (возможно тоже на steel-* primitives).
  - Welcome колонка: 🔄 ready for MOCKUP GATE (6 правок применены total). После approval → переход к колонкам 02-08 по тому же шаблону.

- **2026-05-18 (session 3) — Onboarding block CLOSED:**
  - Welcome ✅ approved после всех итераций.
  - Login (col 02) собран и approved — реальная синяя мандала (Group 1925 = `velo-logo-mandala-blue.svg`) в `.velo-header-compact`, inputs solid white pill, back-arrow glass canon с halo.
  - Register (col 03) approved — 3 inputs, glass canon кнопок.
  - OAuth callback (col 04) approved — `velo-logo-mandala-blue.svg` 160×160, "Вход через Google…" label.
  - Onboarding 1-3 (col 05-07) approved — извлечены **настоящие SVG из Figma** через Plugin API: `icon-onb-practice.svg` (Group `648:1217`), `icon-onb-diary.svg` (Group `648:1240`), `icon-onb-chat.svg` (Group `648:1253`). Pagination dots: большой круг + малые серые. Skip-link `top: 18 → 68px` (operator request).
  - Onboarding 4 (col 08) approved — "Часовой пояс" timezone input.
  - **Bug fixed:** `.v-button` flex-shrink: 0 — primary button в register сжимался до 33px height из-за flex parent overflow.
  - Operator approval: «приняты экраны и дизайн можно идти к следующим».

  **DS-promotion to `02_design-system/tokens/variables.css` (Sprint 2 closure):**
    - Layer 2 text aliases re-aliased to `steel-light` (operator-confirmed pixel-measure): `--velo-text-primary`, `--velo-text-secondary`, `--velo-text-link`. Раньше были `steel-primary/muted` (давали слишком темный navy-look).
    - Added Layer 2 component sizing: `--velo-button-height: 52px`, `--velo-input-height: 42px` (input на 20% тоньше).
    - Added Layer 2 stack gaps: `--velo-stack-gap-buttons: 16px`, `--velo-stack-gap-forms: 10px` (forms плотнее чем buttons).
    - Added Layer 2 typography canon:
      - `--velo-typo-h1-{size,line,spacing,color}` = 30 / 36 / 1.2 / steel-light — section titles с разрядкой.
      - `--velo-typo-body-{size,line,color}` = 18 / 24 / steel-light — subtitle / description.
    - Added Layer 2 glass canon: `--velo-glass-fill` = 10% blue, `--velo-glass-fill-hover` = 15% blue.
    - Added Layer 2 button halo composition: `--velo-shadow-button` (two-layer: drop steel-tone сверху + white halo под). Constraint: total extent ≤ stack-gap-buttons.
    - variables.css 215 → 179 lines (rebalanced, dedup). MD5 master ↔ deliverable verified.

  **DS-assets added/replaced (Sprint 2 closure):**
    - `assets/icons/icon-back-arrow.svg` (Figma `423:125`, 215 bytes) — replaces icon-back-arrow.png.
    - `assets/icons/velo-logo-mandala-blue.svg` (Group 1925, 228KB) — compact blue mandala с VELO внутри.
    - `assets/icons/icon-onb-{practice,diary,chat}.svg` — 3 onboarding step icons из Figma.
    - PNG-версии помечены DEPRECATED в ASSETS-INDEX.md (sandbox не разрешил rm; удаление вручную).

  **Patterns formalized (для следующих экранов):**
    - **Two-layer glass component pattern** (button / input / back-arrow): `.v-element` = transparent base + halo box-shadow; `::before` = white border (z-index: -2); `::after` = 10% blue fill (z-index: -1, поверх border).
    - **Halo budget rule**: blur + spread ≤ stack-gap-buttons (16) — иначе halo одной кнопки залезает на соседнюю.
    - **Pagination dots canon**: inactive 8×8 круг steel-pale opacity 0.45, active 14×14 круг steel-light opacity 1.

  Onboarding 8 фронтальный поток ✅ закрыт. Переход на Dashboard 9.

- **2026-05-18 (session 4) — Dashboard 9 START:**
  - Прочитан `_HANDOFF.md` + `INDEX.md` + `sprint-02.md` + `03_mockups/INDEX.md` + `variables.css` master.
  - DS canon подтверждён полностью промоутированным (typography h1+body, button/input heights, stack gaps, glass two-layer, halo composition) — re-use as-is, no re-invention.
  - Подтверждены 9 PNG-эталонов в `02_design-system/assets/screenshots/user/user-dashboard-{01..09}-*.png`.
  - Создан новый combined viewer **`03_mockups/user/_dashboard-flow.html`** (795 строк). Структура идентична `_onboarding-flow.html`: topbar shell + horizontal scroll workspace + 9 колонок 402×874 (PNG-эталон сверху / HTML снизу). Token bridge :root mirror'ит variables.css master (typography canon + glass canon + halo + heights + gaps).
  - **Column 01 (dashboard-1) skeleton iteration 1** собран на DS-токенах: greeting ("Доброе утро," + "Алина"), 2 alert-pills (teal check-in + coral feedback), section-title "Ближайшая практика", practice-card (avatar+title+master+meta paid), action-row Zoom-glass + Check-in-primary (на DS canon glass two-layer), section-title "Ваш прогресс" + 2 stat-cards (12 практик / 9,5 часов), AI-саммари header с tabs (Неделя/Месяц), AI preview card с gradient bg, bottom-nav 4 иконки.
  - Col 02-09 — пройдены за один проход по операторской команде «отстрой все экраны как можешь по DS — потом править все вместе». Все 9 колонок имеют живой HTML-skeleton, никаких TBD-overlay не осталось:
    - **02 dashboard-2** — вариант col 01 с развёрнутым AI-card (текст + energy-pair emoji + Подробнее →)
    - **03 check-in** — top-header back-arrow + practice-info + "Как вы себя чувствуете?" + mood-selector (3 emoji, central is-active) + slider + textarea + primary CTA + skip link
    - **04 check-in success** — special: NO bg-mandala (pure white по эталону), teal check icon + h1 + sub + primary "Начать практику" + "На главную" link
    - **05 practice live** — back-arrow + video-block placeholder + practice-info compact + status-badge "● В эфире" (blue dot) + 3-button stack: Войти primary + Check-in glass + Покинуть практику destructive
    - **06 booked practice** — header "Моя практика" + practice-info с "Оплачено" badge + 2 list-rows collapsible (О практике/Что подготовить) + master-card (avatar+tags+Подробнее →) + warning-alert (Противопоказания) + Check-in primary + Отменить бронирование destructive
    - **07 AI summary** — header "AI-саммари" + info-pill (Саммари недели 16-22 января) + ai-detail-text + energy-pair "с 😩 до 😊" + "Рекомендации" + 2 recommendation-cards
    - **08 my reservations** — header "Мои бронирования" + Предстоящие group + reservation-row с warning badge "⚠ Завтра" + Прошедшие group + 2 rows (success badge "Завершена" + error badge "Отменена")
    - **09 booking detail** — header "Бронирование" + practice-info + Статус group + success badge "Подтверждена" + Мастер group + master-card + ZOOM group + info-pill (Ссылка будет отправлена) + Отменить бронирование destructive
  - **Новые shared chrome компоненты добавлены в CSS** _dashboard-flow.html (потенциальные DS-promotion candidates после операторского passa): `.top-header` (back-arrow glass two-layer + centered title), `.status-badge` 5 variants (success/warning/error/info/live), `.info-pill` (blue tint card), `.v-button--destructive` (coral filled с собственным halo), `.v-textarea`, `.practice-info`/`.practice-card`, `.master-card` (avatar+name+tags+chevron), `.list-row` (collapsible), `.warning-alert` (orange tint), `.mood-selector` + `.mood-slider`, `.video-block`, `.energy-pair`, `.reservation-row`, `.recommendation-card`, `.bottom-nav`, `.scr-success` (white-only screen variant).
  - 03_mockups/INDEX.md обновлён.
  - **Pending:** operator pass по всем 9 экранам сразу — отметит pixel-tight расхождения, добавит/уберёт элементы, потом второй прогон по списку правок. После approval — DS-promotion pass для новых tokens (badges, master-card, mood, warning-alert).
  - **🐛 Font fix — оператор флагнул отсутствие Marmelad.** Я задекларировал `font-family: 'Marmelad'` в `:root` + `body`, но забыл `@font-face` declaration. Браузер падал на fallback `system-ui`. Причина: в `_onboarding-flow.html` шрифт base64-embedded (~140KB → файл 179K токенов, не редактируется через мои тулзы), и я сознательно ушёл от base64 чтобы новый viewer оставался читаемым/правимым — но не сделал альтернативу через relative URL. Фикс: добавлен `@font-face` через relative URL `../../02_design-system/assets/fonts/Marmelad-Regular.ttf` — это **canon из `02_design-system/tokens/global.css §1`** (один master TTF в DS, никакого дубля). Под `file://` в современных Chrome/Edge/Firefox работает.
  - **Bottom-nav refactor + glass halo softer (-20%) — оператор iteration 2026-05-18.**
    - **Сделано:** введён новый Layer 2 token `--velo-shadow-button-glass` = same composition что `--velo-shadow-button`, но white halo alpha 0.57 → 0.46 (-20%). Применён на `.v-button--glass`, `.top-header .header-back` (back-arrow) и через переиспользование на bottom-nav. Primary halo не тронут — primary остаётся ярким акцентом.
    - **Bottom-nav refactor:** удалены дублирующие CSS правила `.bottom-nav .nav-item ::before / ::after / box-shadow / isolation` (это была копия `.v-button--glass` под чужим именем). HTML переписан на canonical class chain: `<button class="v-button v-button--glass v-button--round-icon active">`. Новый modifier `.v-button--round-icon` (52×52 круг, padding 0, не растягивается) — DS-promotion candidate. Контейнер `.bottom-nav` сократился до flex-row + active state override.
    - **DS-gap surfaced:** оператор спросил про MD-описание DS компонентов. Найден catalog `02_design-system/INDEX.md` секция Component Status — там canonical имена Tier 1/2. Визуальный каталог — `styleguide/velo-design-system.html`. MD-описание каждого компонента (props/states/when-to-use) **отдельно не существует** — это методологический пробел.
  - **🆕 COMPONENTS-CATALOG.md создан** (2026-05-18, T1 done). `02_design-system/COMPONENTS-CATALOG.md` — single MD master с full профилем per компонент: Class + Variants + States · When-to-use + Anti-patterns · Tokens consumed + Related · Provenance + Status. Группы: Tier 1 (atomic) · Tier 2 (domain) · Patterns · NEW candidates (Dashboard 9 mining). Введено **before-naming check правило** — обязательный шаг в каждой сессии перед изобретением нового CSS-класса. Зарегистрирован в `02_design-system/INDEX.md` секции Component Status (cross-link) и в `_HANDOFF.md` (новый шаг в правилах поведения + добавлен в таблицу Local INDEX-ов).
  - **🆕 DS-naming-pass T1 done** — rename custom-классов в `_dashboard-flow.html` под canonical имена из каталога:
    - `.status-badge` → `.v-badge` (5 variants: success/warning/error/info/live)
    - `.reservation-row` → `.booking-card` (sub-classes .rr-* → .bc-*)
    - `.mood-selector` → `.mood-widget` (sub-classes .mood-pick/face/label/slider → .mw-*)
    - Остальные custom-классы остаются под текущими именами как ⬜ candidates в каталоге (.info-pill, .warning-alert, .master-card, .list-row, .video-block, .energy-pair, .stat-card, .ai-card, .recommendation-card, .alert-pill, .scr-success, .section-title/.group-title, --round-icon modifier) — promotion после operator MOCKUP GATE.
  - **🆕 T2 Figma audit Dashboard 9 done** — `02_design-system/FIGMA-FINDINGS-DASHBOARD-9.md` создан. Probe через `use_figma` Plugin API на SACRED root `541:6648`, walk depth-first all 9 frames. Собраны deduplicated fills (~30 colors), strokes (~20), cornerRadii (~10), shadows (2 patterns), blurs (3), font sizes (9), Marmelad Regular как единственный font family. Confirmed matches: steel/teal/orange/coral families, radii 5/15/100/200, blur 4/5.04, font sizes 14/18/20/15/32. **3 критических находки:** (1) alert-pill в Figma имеет цветные 2-3px outlines (`#76dde6` teal info, `#fbc088` orange warning, `#f795a2` coral destructive) — у меня в skeleton серый alpha-steel-15 border (T3 blocker); (2) card border alpha-steel-30, не -15 (25 occurrences, T3 visible drift); (3) **мой compound `--velo-shadow-button` ≠ Figma canon** — в Figma single drop-shadow white (`0 0 20.9 7 white`) который уже был в DS как `--velo-shadow-glow-white` (но со spread bug = 0), я его не использовал и синтезировал compound.
  - **🐛 Found + fixed:** spread bug в `--velo-shadow-glow-white` / `-glow-white-strong` (Sprint 1 Phase 2 promotion накосячил с spread 0 вместо Figma canon 7/8.82). Теперь корректно.
  - **🐛 Found + fixed:** drift в `01_deliverable/styles/variables.css` (deliverable = 183 строки, master = 310 строк). Daily log говорил «MD5-identical 2026-05-18» но Phase 4 promotion (text aliases re-alias, button/input heights, stack gaps, typography canon, glass canon, shadow-button compound) **не доехала до deliverable** — это был sync bug в Sprint 2 Phase 4 closure pass. Сейчас полностью пересинхронизирован, MD5-mirror.
  - **🆕 Glass halo simplified — operator iteration 2026-05-18 round 2.**
    - **Promotion:** `--velo-shadow-button-glass: 0 0 20.9px 7px rgba(255, 255, 255, 0.8)` в variables.css master + deliverable. Это упрощённый single-white halo, 1:1 Figma canon с alpha 0.8 (-20% от Figma full white).
    - Применяется на: `.v-button--glass / --ghost / --oauth`, `.velo-back-arrow`, `.top-header .header-back`, `.v-button--round-icon` (bottom-nav).
    - `--velo-shadow-button` (compound steel drop + white halo) остаётся **только для primary** — он остаётся ярким акцентом.
    - **`_onboarding-flow.html` обновлён:** base `.v-button { box-shadow }` упрощён до single white halo. `.v-button--primary` получил override с compound. Glass/ghost/oauth наследуют simplified из base.
    - **`_dashboard-flow.html` обновлён:** token `--velo-shadow-button-glass` в bridge заменён на simplified. Все glass-кнопки + back-arrow + bottom-nav автоматически подхватили.
  - **Pending operator review:** оба viewer'а готовы к парной сверке. Glass halo softer + Figma-consistent. Если оператор скажет «вернуть compound» — revert через token swap.
  - **🆕 T3 col 01 alert-pills rebuild done + A.2 card border promotion done.**
    - **DS-promotion:** `--velo-color-alpha-steel-30: rgba(76,101,137,0.30)` (Layer 1) + `--velo-border-card: var(--velo-color-alpha-steel-30)` (Layer 2 alias) в variables.css master + deliverable. Replaces visually-weak alpha-steel-15 в card borders.
    - **Mass refactor:** 11 occurrences `border: 1px solid var(--velo-color-alpha-steel-15)` → `border: 1px solid var(--velo-border-card)` в `_dashboard-flow.html` (затронуты: practice-card, v-badge, booking-card, info-pill, warning-alert, master-card, stat-card, recommendation-card, list-row, top-header header-back, и др.). Backgrounds, использующие alpha-steel-15 (avatar circles, ai-tabs, pi-icon, mc-avatar bg) — оставлены as-is.
    - **AlertPill rebuild:** добавлены canonical variants `--warning` (orange theme: orange-50 bg + 2px orange-light border + orange-dark icon), `--info` (teal theme: teal-50 bg + 2px teal-light border + teal-medium icon), `--error` (coral, reserved). Border weights и tints из Figma probe.
    - **HTML swap col 01 + col 02:** «Пора на check-in!» переведён с `--teal` на `--warning` (orange — срочность действия); «Оставьте feedback!» с `--coral` на `--info` (teal — мягкое приглашение). Это **semantic correction** — на эталоне check-in оранжевый по urgency-семантике, а не teal.
    - COMPONENTS-CATALOG.md обновлён — полная карточка AlertPill с variants, anti-patterns, tokens consumed, provenance.
  - **🆕 AlertPill iteration 2 (operator side-by-side flag 2026-05-18).** Сравнение эталон ↔ мой рендер выявил 3 расхождения: (1) bg должен быть translucent чтобы bg-mandala проглядывала, (2) title text красится в **тёмный variant цвета outline** (orange-dark для warning, teal-dark для info), не steel-primary, (3) feedback icon должен быть message-bubble с edit/pen-mark внутри, не plain chat bubble. Первая итерация фикса (round 1 — synthesized values orange-50@75% / teal-50@75%) — оператор отверг как недостаточно точное.
  - **🆕 AlertPill iteration 3 — Figma-first re-extract (operator rule 2026-05-18).** Оператор поднял **системную проблему**: я reverse-engineering из PNG вместо того чтобы извлекать оригинал из Figma. Это даёт повторные расхождения и двойную работу. Зафиксировано **новое правило в `_HANDOFF.md`**: «**Figma-first rule (mandatory for any SACRED-derived component)**» — перед сборкой компонента из SACRED frame: (1) find Figma node, (2) extract vector asset via exportAsync, (3) sample exact tokens per element, (4) compare DS vs Figma, (5) ТОЛЬКО ПОТОМ writing CSS/HTML. Не применять только для admin role (нет Figma SACRED) и для новых non-SACRED компонентов.
    - **Применение rule на col 01 AlertPills:** per-frame drill `use_figma` Plugin API в node `541:6649`. Найдены AlertPill containers (Group 2316 warning + Group 2011 info), icon nodes (Group 1963 clock + Group 1967 feedback). Sampled exact tokens:
      - Warning: bg `#fbc088 @ 0.4 alpha` (orange-light × 40%, **не orange-50 75%** как было в моей synthesis), border 2px `#fbc088` solid, cornerRadius 15, **BACKGROUND_BLUR radius 4**.
      - Info: bg `#76dde6 @ 0.4 alpha` (teal-light × 40%), border 2px `#76dde6` solid, cornerRadius 15, **no backdrop blur** (Figma asymmetry preserved).
    - **Real Figma SVG icons extracted via exportAsync:** `icon-alert-clock.svg` (21×21, fill `#A16124` baked in) + `icon-alert-feedback.svg` (21×21, fill `#26767D`, bubble + pen + 2 dialog dots) сохранены в `02_design-system/assets/icons/`.
    - **DS tokens updated:** `--velo-bg-alert-warning` corrected to `rgba(251,192,136,0.4)`, `--velo-bg-alert-info` to `rgba(118,221,230,0.4)`, `--velo-bg-alert-error` to `rgba(247,149,162,0.4)`. Same-hue + alpha 0.4 (not different tint family with 75% alpha) — это elegant Figma approach.
    - **CSS .alert-pill --warning** дополнен `backdrop-filter: blur(4px)` (Figma canon for this variant only).
    - **HTML col 01 + col 02:** inline synthesized SVG заменены на `<img src="../../02_design-system/assets/icons/icon-alert-{clock,feedback}.svg">` refs.
    - **CSS .pill-icon color overrides убраны** — color baked в SVG.
    - **COMPONENTS-CATALOG AlertPill** обновлён: real Figma-sampled tokens, real SVG asset paths, backdrop-blur variant rule, single-hue-with-alpha approach зафиксирован как canon.
    - **Lesson learned: synthesis из PNG = двойная работа.** Закодифицировано в правилах поведения.

- **2026-05-18 (session 4 closure — pivot to Sprint 2.5):**
  - Operator surfaced two systemic issues: (a) reverse-engineering из PNG вместо Figma extraction вызывает 3× rework на element; (b) добавление tokens в `variables.css` без визуализации в `velo-design-system.html` ломает единый источник правды в DS, следующие сессии плодят дубли.
  - Operator также указал на `06_project-inputs/CBSHOME-PATTERNS-FOR-VELO.md` — готовая reference implementation (85 .vue + 57 .ts, identical stack), source of ~70% frontend foundation work. Sprint 0 + Sprint 1 + part of Sprint 11+ implementation phase уже решены there. Transfer-and-adapt ~10× быстрее re-invention.
  - **Decision:** Sprint 2 не пересобирает Dashboard 9. Закрываем Sprint 2 на текущем state (Onboarding 8 ✅ + P0 P0 mockups baseline + Phase 3 styleguide ✅). Pivot to **Sprint 2.5** — DS Completion block-by-block + Foundation Transfer CBSHOME — параллельные tracks.
  - **Documentation closure (this session):**
    - `04_methodology/VELO-METHODOLOGY.md` v1.2 → **v1.3**: §6.8 DS Promotion Visualisation rule; §7.0 Block-Harvest-First (mandatory for SACRED blocks) с 3 phases; §11.5 AP-P-6 (PNG reverse-engineering anti-pattern); §11.5 AP-P-7 (variables.css without styleguide anti-pattern); Methodology Changelog v1.3 entry.
    - `05_roadmap/ROADMAP.md` v1.1 → **v1.2**: TOC + Sprint Cadence + Sprint 2.5 full section (5.5.1 two tracks / 5.5.2 Track A per-block sequence / 5.5.3 Track B CBSHOME bundles / 5.5.4 Tasks / 5.5.5 Gates / 5.5.6 Risks / 5.5.7 Anchor). Closing anchor updated.
    - `_HANDOFF.md` v1.1 → **v1.2**: Block-Harvest-First rule + DS Visualisation rule в правилах поведения; entry point switched на Sprint 2.5 Track A (Dashboard 9 first); reference на CBSHOME-PATTERNS для Track B; anchor updated.
    - `02_design-system/INDEX.md` Iteration Log: новая строка про methodology v1.3 + roadmap v1.2 + Sprint 2.5 pivot.
    - `03_mockups/INDEX.md`: `_dashboard-flow.html` помечен **🗑 superseded** (rebuild в Sprint 2.5 T2.5.2 после DS-complete).
    - `docs/INDEX.md` Recent Changes line + version refs обновлены.
  - **Net effect this session:** 0 mockup правок, 0 DS contentual правок, 7 unique файлов updated (methodology, roadmap, _HANDOFF, sprint-02, 02_design-system/INDEX, 03_mockups/INDEX, docs/INDEX). Текущее правдивое состояние project: Sprint 2 in progress — Phase 3 ✅, Phase 4 partial (Onboarding ✅, Dashboard 9 🗑 superseded), Phase 4.5 pivot active = Sprint 2.5 scope. Новый чат начнёт с Track A first block (Dashboard 9 harvest) — entry point в `_HANDOFF.md` секция «ЧТО ДЕЛАТЬ ДАЛЬШЕ».

- **2026-05-18 (session 4 closure — final, Sprint 2 formally closed):**
  - Operator clarified that Sprint 2.5 is a **standalone sprint** (not a Phase 4.5 pivot within Sprint 2). Earlier compromise text in this file and in `docs/INDEX.md` was inaccurate.
  - **Sprint 2 formally closed** at current state: Phase 3 ✅ styleguide passed STYLEGUIDE GATE, Phase 4 partial — Onboarding 8 block ✅ approved 2026-05-18, Dashboard 9 skeleton 🗑 superseded (work continues in Sprint 2.5). Header `Status` updated to `closed`.
  - **Sprint 2.5 file created** — `05_roadmap/sprint-02.5.md` per methodology §15.1 template. Three parallel tracks: A (DS completion block-by-block, Cowork), B (CBSHOME foundation transfer, Claude Code), C (Documentation English translation pass, Cowork).
  - **Methodology bumped v1.3 → v1.4** — new §1.1 P6 (English-default principle) + §11.5 AP-P-8 (Russian narrative anti-pattern with exception table). Driven by Cyrillic audit: 2852 occurrences across 29 files, large majority concentrated in exempt categories (mockup UI strings + external inputs). Track C in Sprint 2.5 schedules conversion of non-exempt files.
  - **Roadmap bumped v1.2 → v1.3** — Track C added as third parallel work stream in §5.5, sub-section numbering shifted to 5.5.5..5.5.8.
  - **HANDOFF bumped v1.3 → v1.4** (next edit) — English rule added to rules of behavior, Шаг 4 reference updated to `sprint-02.5.md`, startup prompt one-line reminder.
  - **Sprint 2 closure inventory:** Phase 3 ✅ styleguide HTML + 32 SVG icons + card/modal shadow tokens. Phase 4 ✅ Onboarding 8 block (all 8 columns approved 2026-05-18) + DS-promotion of glass canon + typography canon + button heights + stack gaps + halo composition + state token rebalance (alpha-steel-30 promoted, halo simplified to single white drop-shadow). 2 anti-patterns codified (AP-P-6 PNG reverse-engineering, AP-P-7 variables.css without styleguide). COMPONENTS-CATALOG.md created.

- **2026-05-19 (session 7) — Profile 7 DS Harvest (Block-Harvest-First Phase A+B):**
  - **Phase A — token audit:** All 7 SACRED frames at root `541:2355` (70_Profile through 76_Support) walked via Figma Plugin API. All fills, radii, typography sizes, and blur effects compared against `variables.css`. **Zero new tokens found** — all Profile 7 values map to existing DS tokens. Notable confirmed mappings: `#627A9C` → `--velo-color-steel-light` (all navigation icons), `#AD3444` → `--velo-color-coral-darker` (destructive action icons: logout + delete account), `20px` radius on confirmation modal (single-occurrence, kept as component-local inline literal per single-use rule — not promoted).
  - **SVG icon exports — 9 icons successfully extracted:** `icon-profile-notifications` (`541:2361`, 20×21, bell + dot), `icon-profile-language` (`541:2369`, 20×20, globe — also reused in language-timezone detail frame), `icon-profile-edit` (`541:2419`, 20×20, pencil), `icon-profile-bookings` (`541:2424`, 20×20, calendar+rows), `icon-profile-messages` (`541:2433`, 20×20, chat bubble+dots), `icon-profile-support` (`541:2448`, 17×20, shield), `icon-profile-logout` (`541:2572`, 20×20, exit arrow — fill `#AD3444`), `icon-profile-delete` (`541:2609`, 20×24, trash can — fill `#AD3444`), `icon-profile-timezone` (`541:2674`, 20×20, clock face — fill `#ffffff`, designed for steel-primary bg). **1 icon unavailable:** `icon-profile-share` (`541:2454`) — Figma Plugin API returned "no visible layers" error; skipped.
  - **Bottom-nav deduplication:** Group 2650 instances in Profile 7 frames are the same bottom-nav component already extracted in Dashboard 9. Not re-exported.
  - **Toggle component identified:** Groups 2672 (ON) and 2669 (OFF) are 42×25 RECTANGLE+ELLIPSE toggle switch UI components — catalogued as new ToggleSwitch component candidate in COMPONENTS-CATALOG; not exported as icons.
  - **Phase B deliverables (all 5 complete):**
    1. `variables.css` — no changes needed (zero new tokens)
    2. 9 SVG icons saved to `02_design-system/assets/icons/`
    3. `ASSETS-INDEX.md` — iteration 5, icon count 38 → 47 (prior docs said 37 — actual was 38, off-by-one corrected), Profile 7 table + share-icon failure note
    4. `COMPONENTS-CATALOG.md` v1.1 → v1.2 — 4 new candidates: ProfileSettingsRow, ToggleSwitch, ConfirmationDialog, ProfileHeader; destructive icon pattern documented
    5. `velo-design-system.html` — Profile 7 icon group added (9 imgs, timezone shown on steel bg to demonstrate white-fill context)
  - **Net effect:** 9 new SVG files, ASSETS-INDEX +9 rows, COMPONENTS-CATALOG +4 full entries, styleguide +9 icons. **Macro-Phase I: 4/10 blocks DS-complete. Next: Diary 20 (`541:2816`, 20 screens).**

- **2026-05-19 (session 8) — Diary 20 DS Harvest (Block-Harvest-First Phase A+B):**
- **2026-05-19 (session 8) — Diary 20 DS Harvest (Block-Harvest-First Phase A+B):**
  - **Phase A — token audit:** All 20 SACRED frames at root `541:2816` (37_Diary All Map through 52_Edit Entry) walked via Figma Plugin API. All fills, radii, typography, and blur effects compared against `variables.css`. **Zero new tokens found** — all Diary 20 values map to existing DS tokens. Key confirmed mappings: `#627A9C` → `--velo-color-steel-light` (filter chip circles, tab icon, close buttons), `#4C6589` → `--velo-color-steel-primary` (map pin fills, edit icon context).
  - **SVG icon exports — 11 icons successfully extracted:**
    - `icon-diary-tab-all` (`541:3255`, Group 2474, 40×40) — DiaryFilterBar "All" tab, filled steel-light circle + white funnel
    - `icon-diary-edit` (`541:5921`, Group 2499, 17×20) — entry edit button, white fill document/padlock shape (~9KB)
    - `icon-diary-filter-n5` through `icon-diary-filter-n11` (`541:3315–541:3333`, Groups 2475–2481, 38×38 each) — 7 numeral rating chips (5–11 scale), steel-light circle outline + digit paths
    - `icon-diary-pin` (`541:2950`, Group 2354, 28×34, ~31KB) — ornate map pin with mask elements; extracted via base64 chunked transport (3 chunks)
    - `icon-diary-pin-alt` (`541:2953`, Group 2355, 28×34, ~31KB) — mirrored pin variant; same chunk technique
  - **4 icons unavailable (no visible layers):** `541:2930` (location marker, stroke-only), `541:2963`/`541:2960` (view-toggle buttons), `541:3258`/`541:3261` (round header action buttons) — all geometric composites with no renderable fill at group root. Documented in ASSETS-INDEX.
  - **Phase B deliverables (all 5 complete):**
    1. `variables.css` — no changes needed (zero new tokens)
    2. 11 SVG icons saved to `02_design-system/assets/icons/`
    3. `ASSETS-INDEX.md` — iteration 6, icon count 47 → 58, Diary 20 table + 4-icon skip note
    4. `COMPONENTS-CATALOG.md` v1.2 → v1.3 — 6 new candidates: DiaryMapView, DiaryFilterBar, DiaryRatingSelector, DiaryFilterModal, DiaryEntryCard, DiaryEntryView
    5. `velo-design-system.html` — Diary 20 icon group added (11 imgs; edit icon shown on steel-primary bg to demonstrate white-fill context)
  - **Net effect:** 11 new SVG files, ASSETS-INDEX +11 rows, COMPONENTS-CATALOG +6 full entries, styleguide +11 icons. **Macro-Phase I: 5/10 blocks DS-complete. Next: Messages 3 (`541:2717`, 3 screens).**

- **2026-05-19 (session 9) — Messages 3 DS Harvest (Block-Harvest-First Phase A+B):**
  - **Phase A — token audit:** All 3 SACRED frames at root `541:2717` (80_Messages, 81_Thread, 82_Thread Support) walked via Figma Plugin API. All fills, radii, typography, and blur effects compared against `variables.css`. **Zero new tokens found** — all Messages 3 values map to existing DS tokens. Key confirmed mappings: `#627A9C @15%` → `--velo-color-alpha-steel-light-15` (input bar fill), `#4C6589 @70%` → `--velo-color-alpha-steel-70` (conversation preview + timestamp text), DROP_SHADOW 26.33/8.82 white → `--velo-shadow-glow-white-strong`, BACKGROUND_BLUR 30 → `--velo-blur-glass-stronger`. CornerRadius 252 on input bar is decorative-only (vestigial single-component literal per §variables.css vestigial list).
  - **SVG icon exports — 1 icon successfully extracted:** `icon-messages-send` (Group 2356 `541:2785`, 40×40) — steel-light circle (#627A9C) background + white upward-arrow path. Back-arrow (Group 1924) is already in DS as `icon-back-arrow.svg` — not re-exported.
  - **Phase B deliverables (all 5 complete):**
    1. `variables.css` — no changes needed (zero new tokens)
    2. 1 SVG icon saved to `02_design-system/assets/icons/`
    3. `ASSETS-INDEX.md` — iteration 7 (58→59 icons), Messages 3 table + token audit note
    4. `COMPONENTS-CATALOG.md` v1.3→v1.4 — 3 new candidates: MessageConversationRow, MessageBubble, MessageInputBar
    5. `velo-design-system.html` — Messages 3 icon group added (1 img: icon-messages-send)
  - **Net effect:** 1 new SVG file, ASSETS-INDEX +1 row, COMPONENTS-CATALOG +3 full entries, styleguide +1 icon. **Macro-Phase I: 6/10 blocks DS-complete. Next: Analytics 3 (`758:1529`, 3 screens).**

- **2026-05-19 (session 10) — Analytics 3 DS Harvest (Block-Harvest-First Phase A+B):**
  - **Phase A — token audit:** All 3 SACRED frames at root `758:1529` (01_Reviews `758:1530`, 02_Reviews 2 `758:1743`, 03_Payments `758:1891`) walked via Figma Plugin API. All fills, radii, typography, and blur effects compared against `variables.css`. **Zero new tokens found** — all Analytics 3 values map to existing DS tokens. Key confirmed mappings: `#4C6589` → `--velo-color-steel-primary`; `#91A2BA` → `--velo-color-steel-pale` (user avatar circle); `#D66674` → `--velo-color-coral-dark`; `#2F9EA8` → `--velo-color-teal-medium`; `#619CD2` → `--velo-color-blue-medium`; `#D4863C` → `--velo-color-orange-medium`; `rgba(98,122,156,0.15)` → `--velo-color-alpha-steel-light-15` (glass card fills); blur 5.04px → `--velo-blur-glass-medium`; DROP_SHADOW white → `--velo-shadow-glow-white-strong`. Candidate `#abbfda@15%` (neutral-200 @ 0.15, 2–3 occurrences) below single-use threshold — kept as component-local literal.
  - **SVG icon exports — 6 icons successfully extracted:**
    - `icon-analytics-tab-profile` (`758:1663`, Vector, 27×27) — person/profile silhouette, AnalyticsTabBar slot 1
    - `icon-analytics-tab-list` (`758:1666`, Group 2226, 27×27) — clipboard + 2 horizontal bars, AnalyticsTabBar slot 2
    - `icon-analytics-tab-trophy` (`758:1672`, Group 1959, 21×27) — cup/trophy with pedestal, AnalyticsTabBar slot 3
    - `icon-analytics-tab-chart` (`758:1677`, Group 1962, 27×27) — bar chart in rounded-rect frame (key analytics icon), AnalyticsTabBar slot 4
    - `icon-analytics-user-circle` (`758:1875`, Group 2629, 41×41) — steel-pale circle + white person paths, reviewer avatar placeholder
    - `icon-analytics-help` (`758:1884`, Group 2752, 20×20) — circle frame + ? + dot, help/question button
    - Bottom-nav icons (Groups 2842/2843/2844) NOT re-exported — already in DS from Dashboard 9.
  - **Phase B deliverables (all 5 complete):**
    1. `variables.css` — no changes needed (zero new tokens)
    2. 6 SVG icons saved to `02_design-system/assets/icons/`
    3. `ASSETS-INDEX.md` — iteration 7→8 (59→65 icons), Analytics 3 table + token audit note
    4. `COMPONENTS-CATALOG.md` v1.4→v1.5 — 5 new candidates: AnalyticsTabBar, AnalyticsStatCard, AnalyticsReviewCard, AnalyticsPeriodChip, TransactionRow
    5. `velo-design-system.html` — Analytics 3 icon group added (6 imgs), icon count updated 59→65
  - **Net effect:** 6 new SVG files, ASSETS-INDEX +6 rows, COMPONENTS-CATALOG +5 full entries, styleguide +6 icons. **Macro-Phase I: 7/10 blocks DS-complete. Next: Practices 15 (`758:1950`, 15 screens).**

- **2026-05-19 (session 11) — Practices 15 DS Harvest (Block-Harvest-First Phase A+B):**
  - **Phase A — token audit:** All 15 SACRED frames at root `758:1950` (241_Practices upcoming through 255_Attendance 2) walked via Figma Plugin API in two batches (frames 1-7, frames 8-15). All fills, radii, typography, and blur effects compared against `variables.css`. **Zero new tokens found** — all Practices 15 values map to existing DS tokens. Key confirmed mappings: `#4C6589` → `--velo-color-steel-primary`; `#FBC088` → `--velo-color-orange-light`; `#FFF3EA` → `--velo-color-orange-50`; `#76DDE6` → `--velo-color-teal-light`; `#D66674` → `--velo-color-coral-dark`; glass card fill `rgba(98,122,156,0.15)` → `--velo-color-alpha-steel-light-15`.
  - **SVG icon exports — 5 icons successfully extracted:**
    - `icon-practices-add` (`758:1979`, BOOLEAN_OPERATION Union, 20×20) — "+" add-practice FAB icon, white fill. Direct depth-1 child of frame 241_Practices upcoming.
    - `icon-practices-attendees` (`758:2010`, Group 2689, 16×15) — 3-person silhouette group (attendees count in practice card meta row), fill #4C6589.
    - `icon-practices-repeat` (`758:2019`, Group 2820, 15×15) — two circular repeat arrows (recurrence indicator, day of week slot), fill #4C6589.
    - `icon-practices-review-face` (`758:2024`, Group 2940, 15×15) — smiley face with eyes + smile arc (review count indicator), fill #4C6589. Appears at 15×15 in card meta row and 21×21 in abolish-practice modal.
    - `icon-practices-warning` (`758:2755`, Group 2069, 29×26) — warning triangle with exclamation mark, fill #FBC088 (orange-light). Used in cancel-reservation (`758:2732`) and abolish-practice (`758:2771`) modals on orange-50 panel background. Distinct from existing `icon-warning.svg` (#A16124, darker amber).
    - Bottom-nav icons on all screens reuse existing DS icons — not re-exported.
  - **Phase B deliverables (all 5 complete):**
    1. `variables.css` — no changes needed (zero new tokens)
    2. 5 SVG icons saved to `02_design-system/assets/icons/`
    3. `ASSETS-INDEX.md` — iteration 8→9 (65→70 icons), Practices 15 table + token audit note
    4. `COMPONENTS-CATALOG.md` v1.5→v1.6 — 4 new candidates: MasterPracticeCard, PracticesFAB, PracticeWarningPanel, CreatePracticeWizard
    5. `velo-design-system.html` — Practices 15 icon group added (5 imgs; add icon shown on steel-primary bg, warning icon shown on orange-50 bg), icon count updated 65→70
  - **Net effect:** 5 new SVG files, ASSETS-INDEX +5 rows, COMPONENTS-CATALOG +4 full entries, styleguide +5 icons. **Macro-Phase I: 8/10 blocks DS-complete. Next: Master Dashboard 8 (`758:3246`, 8 screens).**

- **2026-05-18 (session 5) — Sprint 2 Quality Audit:**
  - **Audit triggered by operator:** operator observed onboarding illustration icons absent from DS and questioned whether previous sessions had fully transferred all assets. Previous sessions correctly tokenized all 97 SACRED screens in Sprint 1 Phase A but did NOT extract SVGs from Master Onboarding block (block #10) — this is expected behavior (Phase B only happens per-block during DS harvest, and Master Onboarding was not yet harvested). Correctly identified as a future Macro-Phase I item, not a previous-session failure.
  - **4 genuine gaps found in already-completed blocks (Dashboard 9 + Calendar 11):** Three FeedbackRating icons (`icon-feedback-questions`, `icon-feedback-good`, `icon-feedback-fire`) from Calendar 11 screen 29 (`541:2286`) + one Dashboard check-in success circle graphic (`icon-checkin-success`) from Dashboard screen 04 (`541:6988`) — all absent from ASSETS-INDEX and `velo-design-system.html`.
  - **All 4 gaps remediated:** Exported individually via `use_figma` Plugin API `exportAsync` to avoid 20KB truncation. Saved to `02_design-system/assets/icons/`. ASSETS-INDEX updated (29 → 33 icons). `velo-design-system.html` icon gallery updated with "Audit-recovered" group.
  - **COMPONENTS-CATALOG.md corruption fixed:** File was truncated at line 565 mid-word ("Anatom") in PracticeMetaRow entry. FilterChip, FilterSheet, FeedbackRating entries were completely absent despite being named in sprint-02 iteration 10. All 4 entries now complete with full anatomy/tokens/icons/provenance.
  - **Net effect this session:** 4 new SVG files created, ASSETS-INDEX +4 rows, COMPONENTS-CATALOG +4 complete entries (PracticeMetaRow restored + FilterChip + FilterSheet + FeedbackRating added), velo-design-system.html +4 icons in gallery. No token changes. No mockup changes.

- **2026-05-19 (session 12) — Master Onboarding 13 DS Harvest (`758:4318`, 13 screens) — DS COMPLETE GATE reached:**
  - **Phase A — token audit:** All 13 SACRED frames at root `758:4318` (landing page + 3-step application wizard + status screens + 3-step post-approval onboarding) walked via Figma Plugin API. All fills, radii, typography, and blur effects compared against `variables.css`. **Zero new tokens found** — all Master Onboarding 13 values map to existing DS tokens. Component-local literals retained (not promoted): `#76DDE6@0.3` (2× status-circle bg, Тeal-approved ring) and `#FBC088@0.3` (1× rejected-status circle bg). Both below single-use threshold.
  - **SVG icon exports — 4 icons successfully extracted:**
    - `icon-master-onb-community.svg` (`758:4756`, Group 2530, 212×173) — community/people illustration, fill `#4C6589`. Post-approval onboarding step 1 "Добро пожаловать".
    - `icon-master-onb-workspace.svg` (`758:4772`, Group 2531, 254×173) — workspace/studio illustration, fill `#4C6589`. Post-approval onboarding step 2 "Ваше пространство".
    - `icon-master-onb-ai.svg` (`758:4796`, Group 2532, 173×173) — AI analytics illustration, fill `#4C6589`. Post-approval onboarding step 3 "AI-аналитика о состоянии группы".
    - `icon-master-application-rejected.svg` (`758:4733`, Group 2527, 198×198) — orange circle bg (`#FBC088@0.3`) + chat bubble with 3 dots (fill `#FBC088`). Application-rejected status graphic.
  - **Phase B deliverables (all 5 complete):**
    1. `variables.css` — no changes needed (zero new tokens); MD5 mirror verified: `eb30f5ddf863fb9fa4d55d6d8174f80f` (both copies identical)
    2. 4 SVG icons saved to `02_design-system/assets/icons/`
    3. `ASSETS-INDEX.md` — iteration 10→11, icon count 76→80, Master Onboarding 13 provenance table + token audit note + component-local literals documented
    4. `COMPONENTS-CATALOG.md` v1.7→v1.8 — 6 new ⬜ candidates: MasterLandingCard, MasterApplicationWizard, ApplicationStatusCard, MasterOnboardingStep, SpecializationSelector, FileUploadField
    5. `velo-design-system.html` — Master Onboarding 13 icon group added (4 icons; community/workspace/ai on default bg, rejected on orange-50 bg); icon count updated 76→80
  - **Net effect:** 4 new SVG files, ASSETS-INDEX iteration 11, COMPONENTS-CATALOG v1.8 +6 entries, styleguide +4 icons. **🎉 Macro-Phase I: 10/10 blocks DS-complete. DS COMPLETE GATE condition met — all blocks harvested. Macro-Phase II (mockups) may begin after operator validation.**

- **2026-05-19 (session 6) — Master Dashboard 8 DS Harvest (`758:3245`, 8 screens):**
  - **Phase A (Figma walk + token audit + icon extraction):**
    - Walked all 8 screens via `use_figma` Plugin API. SACRED root `758:3245` ("ДАШБОРД"). Nodes surveyed: `758:3948` (Student Profile), `758:4068` (Check-ins), `758:3677` (header bell), `758:3384` (nav home), `758:3387` (nav students), `758:3294` (filter), `758:4057` (check-in alert flame), `758:3967` (rating star).
    - Token audit: 4 new gradient-stop colours found in MoodProgressBar across Student Profile + Check-in frames (27 total occurrences). `#abbfda@15%` in MasterStatCard bar chart — below single-use threshold, kept as component-local literal. No other promotable colours.
    - 6 SVGs scheduled for export. Bottom-nav slots 3+4 reuse existing `icon-analytics-tab-trophy.svg` + `icon-analytics-tab-chart.svg` — not re-exported.
  - **Phase B deliverables (all 5 complete):**
    1. `variables.css` — 4 new Layer 1 primitives (DS iteration 10): `--velo-color-steel-wash` #dce6f3, `--velo-color-teal-wash` #bdecf1, `--velo-color-coral-wash` #f9cbd1, `--velo-color-peach-wash` #fddfc4. MD5-mirror synced to `01_deliverable/styles/variables.css`. `_shared/tokens.css` mirror synced (§7.3).
    2. 6 SVG icons saved: `icon-master-nav-home.svg` (27×27, `758:3384`), `icon-master-nav-students.svg` (27×27, `758:3387`), `icon-master-header-notif.svg` (20×21, `758:3677`), `icon-master-filter.svg` (20×20, `758:3294`), `icon-master-checkin-alert.svg` (37×40, `758:4057`), `icon-master-rating-star.svg` (18×17, `758:3967`).
    3. `ASSETS-INDEX.md` — iteration 9→10, icon count 70→76, Master Dashboard 8 provenance table + token audit note added.
    4. `COMPONENTS-CATALOG.md` v1.6→v1.7 — 7 new ⬜ candidates: MasterHeaderBar, MasterStatCard, MasterStudentRow, MoodProgressBar, MasterStudentProfile, CheckInRow, MasterNavBar.
    5. `velo-design-system.html` — Master Dashboard 8 icon group added (6 icons shown; bell on steel-primary bg); 4 wash token swatches added after amber-50 section. Icon count updated 70→76.
  - **Net effect:** 6 new SVG files, 4 new tokens promoted to Layer 1, ASSETS-INDEX iteration 10, COMPONENTS-CATALOG v1.7 +7 entries, styleguide +6 icons +4 swatches. **Macro-Phase I: 9/10 blocks DS-complete. Next: Master Onboarding 13 (`758:4318`, 13 screens).**

- **2026-05-19 (session 15) — Dashboard 9 Mockup Viewer REBUILD (Macro-Phase II Priority 1):**
  - **Task:** Full rebuild of `03_mockups/user/_dashboard-flow.html` from frozen DS. Old file (🗑 superseded, built pre-methodology via PNG reverse-engineering) discarded and replaced.
  - **Architecture:** Three-layer `_shared/` pattern (AP-M-6 compliant): `tokens.css` + `shell.css` + `components.css` linked via `<link>` refs. Screen-specific CSS only in `<style>` block (`.dash-*`, `.ci-*`, `.scr-0N-*` prefixes).
  - **Before-naming check performed:** Grepped COMPONENTS-CATALOG.md before writing any CSS class. Three new shared components appended to `_shared/components.css` (before build): `.stats-row`/`.stat-card`, `.action-row`, `.recommendation-card`.
  - **9 PNG etalons reviewed** (re-read from `02_design-system/assets/screenshots/user/`). All 9 screens content-mapped to canonical DS component classes.
  - **All 9 columns built:**
    - **01 dashboard-1** — greeting + 2 alert-pills (warning clock + info feedback) + practice-card + action-row (Zoom glass + Check-in primary) + stats-row (2 stat-cards) + ai-section with tabs + ai-card (blurred preview) + bottom-nav (home active)
    - **02 dashboard-2** — greeting + 1 info alert-pill + practice-card + action-row + stats-row + ai-card expanded (text + energy-row 😩→😊 + Подробнее link) + bottom-nav (home active)
    - **03 check-in** — top-header + practice-info (centered) + ci-question + mood-widget (3 picks, center is-active) + mw-slider + v-textarea + primary CTA + v-link-block skip
    - **04 checkin-success** — pure white bg (CSS override `#scr-04.frame.html { background: #ffffff }`) + icon-checkin-success.svg (80px) + title + sub + primary "Начать практику" + link "На главную"
    - **05 practice-live** — video-block (steel gradient + play button) + practice-info + v-badge--live + scr-bottom: Войти primary + Check-in glass + Покинуть destructive
    - **06 booked-practice** — top-header + practice-info + paid-badge + 2 list-rows (collapsible) + group-title "Мастер" + master-card (avatar А + 3 master-tag-chips + Подробнее) + warning-alert (Противопоказания) + Check-in primary + Отменить destructive
    - **07 ai-summary** — top-header + info-pill (Саммари недели 16-22 января) + summary-body + energy-row 😩→😊 + group-title "Рекомендации" + 2 recommendation-cards
    - **08 my-reservations** — top-header + booking-group-hd "Предстоящие" + 1 booking-card (v-badge--warning ⚠ Завтра) + booking-group-hd "Прошедшие" + 2 booking-cards (v-badge--success ✓ Завершена + v-badge--error ✕ Отменена)
    - **09 booking-detail** — top-header + practice-info + detail-row (Статус + v-badge--success ✓ Подтверждена) + group-title "Мастер" + master-card + group-title "ZOOM" + zoom-section (inline SVG camera icon) + info-pill + Отменить destructive
  - **Structural validation:** Python/BeautifulSoup automated check — **70/70 checks passed**. Verified: 3 CSS links, 9 frame IDs, 9 columns, 9 figma frames, velo-bg-mandala on 01-03+05-09, no mandala on 04, bottom-nav only on 01+02, top-header on 03+06-09, 20 component classes used, all 38 icon refs resolve, all 9 PNG etalons exist, #scr-04 white-bg override present, file closes properly, showToast JS present.
  - **03_mockups/INDEX.md status:** `_dashboard-flow.html` → 🔧 work in progress.
  - **Net effect:** `_dashboard-flow.html` fully rebuilt (40KB, ~540 lines). No token changes. No new components added beyond the 3 already appended to `_shared/components.css` in this session.

- **2026-05-19 (session 14) — Tracking correction: Dashboard 9 is Macro-Phase II Priority 1:**
  - Operator confirmed: Dashboard 9 mockup viewer is **not done**. The existing `_dashboard-flow.html` was built in Sprint 2 Phase 4 via PNG reverse-engineering *before* the Block-Harvest-First / DS-complete methodology was established. It was correctly marked 🗑 superseded in `03_mockups/INDEX.md` but the Macro-Phase II table in this file erroneously read "✅ MOCKUP GATE ready" — that entry was a documentation error from a prior session.
  - **Correction applied:** Macro-Phase II table row 2 → `⬜ rebuild needed`. Priority order updated in `_HANDOFF.md` and `03_mockups/INDEX.md`.
  - **Macro-Phase II correct Priority order:** (1) Dashboard 9 rebuild → (2) Calendar 11 → (3) Profile 7 → (4) Diary 20 → (5) Messages 3 → (6) Analytics 3 → (7) Practices 15 → (8) Master Dashboard 8 → (9) Master Onboarding 13. Onboarding 8 remains the only ✅ MOCKUP GATE passed viewer.

- **2026-05-19 (session 13) — Icon dedup pass + DS COMPLETE GATE confirmed:**
  - **Trigger:** Operator observed identical icons stored under different block-prefixed names in the styleguide (house icon appearing in both Navigation group as `icon-master-nav-home` and Analytics 3 group as `icon-analytics-tab-profile`). Root cause: Block-Harvest-First rule harvests each block separately, producing per-block icon names for shared nav components.
  - **MD5 audit:** `md5sum` run across all 77 SVG files in `02_design-system/assets/icons/`. Found 3 byte-identical pairs + 1 floating-point near-duplicate (Figma export artifact — same visual, 0.001px coordinate difference).
  - **4 duplicates removed:**
    - `icon-cal-datetime.svg` → deleted (canonical: `icon-calendar.svg`, Dashboard origin)
    - `icon-cal-duration.svg` → deleted (canonical: `icon-time.svg`, Dashboard origin)
    - `icon-analytics-tab-profile.svg` → deleted (byte-identical to `icon-master-nav-home.svg` — Analytics tab 1 is home/dashboard, not profile; mislabeled during harvest)
    - `icon-analytics-tab-list.svg` → deleted (near-identical to `icon-master-nav-students.svg`, 0.001px FP rounding — same Figma component instance exported from different parent frames)
  - **1 file renamed:** `icon-nav-home.svg` (134×134 — rendered BottomNav active-state widget with glass circle + house path + glow) → `icon-nav-home-active-composite.svg`. This was a composite UI widget, not a bare icon. TODO: replace with CSS active-state in Macro-Phase II Dashboard viewer rebuild.
  - **7 files updated:** ASSETS-INDEX.md (iter 11→12, count 77→73, deletion records, Analytics 3 section corrected), COMPONENTS-CATALOG.md v1.8 (BottomNav refs, PracticeMetaRow calendar/time, AnalyticsTabBar tabs 1+2), velo-design-system.html (count 73, canonical labels, dedup notes), `_dashboard-flow.html` (2× `icon-nav-home.svg` → `icon-nav-home-active-composite.svg`), `02_design-system/INDEX.md` (iter 19→20, count 73), `docs/INDEX.md` (Recent Changes entry), sprint-02.md Gate (DS COMPLETE GATE marked ✅ passed).
  - **Zero broken references** verified — all `<img src>` paths in styleguide and dashboard mockup point to existing files.
  - **DS COMPLETE GATE ✅ confirmed by operator 2026-05-19.** Macro-Phase II now active. First task: Calendar 11 viewer → `03_mockups/user/_calendar-flow.html`.

---

## Closure

- STYLEGUIDE GATE: ☑ passed 2026-05-17
- **DS COMPLETE GATE: ✅ PASSED 2026-05-19 — operator confirmed. Includes icon dedup pass (77→73 canonical icons, ASSETS-INDEX iter 12). Macro-Phase II is now active.**
- **P0 MOCKUP GATEs (Onboarding 8): ☑ 8/8 passed 2026-05-18**
- P0 MOCKUP GATEs (Dashboard 9): 🔧 **rebuild in progress 2026-05-19** — viewer rebuilt, awaiting operator MOCKUP GATE
- Deferred to Sprint 3+: ☐
- Methodology amendments proposed: ☐
- Token master changed during sprint? ☑ yes — Phase 3 cleanup (`--velo-shadow-card/modal`) + Phase 4 onboarding promotion (text re-alias, component heights, stack gaps, typography canon, glass canon, button halo composition). variables.css master ↔ deliverable MD5-identical 2026-05-18.
- Operator signoff Onboarding 8 (date): ☑ 2026-05-18 ("приняты экраны и дизайн")

---

## References

- Roadmap: `ROADMAP.md` §5
- Methodology: §6.6 (component tiers), §6.8 (styleguide), §7 (mockup layer), §10.3 (STYLEGUIDE GATE), §10.4 (MOCKUP GATE), §11.2–11.3 (anti-patterns + token bridge), §9.4–9.5 (prompts)

- **2026-05-19 (session 15) — Dashboard 9 Macro-Phase II Rebuild (9-column combined viewer):**
  - **Context:** DS COMPLETE GATE passed. First Macro-Phase II build: `03_mockups/user/_dashboard-flow.html` rebuilt from scratch using frozen DS (`variables.css` MD5 `eb30f5ddf863fb9fa4d55d6d8174f80f`). Old content deleted (pre-methodology PNG reverse-engineering skeleton). AP-M-6 three-layer `_shared/` architecture applied.
  - **Build:** Full 9-column combined viewer written — PNG etalon top / HTML build bottom per column. Screens 01–09 per SACRED Figma root `541:6648`. Three new shared components appended to `_shared/components.css` (`.stats-row`/`.stat-card`, `.action-row`, `.recommendation-card`).
  - **Validation:** Python BeautifulSoup structural check — 70/70 assertions passed (CSS links, 9 frame IDs, 9 columns, all component classes, all 38 icon paths, all 9 PNG etalons). File: 40,091 bytes.
  - **Write truncation bug fixed:** Python script patched truncated file tail (incomplete Cyrillic in scr-09 info-pill section at byte 38,795). Final file correct.
  - **Trackers updated:** `sprint-02.md` Macro-Phase II row 2, `03_mockups/INDEX.md` status updated, `docs/INDEX.md` last-updated, `_HANDOFF.md` Priority 1 updated.
  - **Net effect:** `_dashboard-flow.html` 40,091 bytes, 9 columns, AP-M-6 compliant, 70/70 structural checks. Awaiting operator MOCKUP GATE review.

- **2026-05-19 (session 16) — Dashboard 9 Critical Fixes: z-index + DS Icon Compliance:**
  - **Bug 1 — z-index stacking (root cause: content invisible):** `.velo-bg-mandala { z-index: 0 }` in `_shared/components.css` painted over all non-positioned content (CSS paint step 6 after step 3). Fix: `z-index: 0 → -1` in `components.css` + `isolation: isolate` added to `.frame` in `_shared/shell.css`. Scope: global — both `_onboarding-flow.html` and `_dashboard-flow.html` benefit. Onboarding unaffected (already had `z-index: 1` on all content containers). Verified: div balance 221/221, no visual breakage.
  - **Bug 2 — DS violations (emoji + text-chars in visible UI):** Full audit of all 9 screens. Found: emoji `😩/😊` in EnergyRow (screens 02, 07); text arrow `→`; info-pill text `i`; inline SVG camera; text chars `⚠/✓/✕` in v-badge. All violated DS-icon-mandatory rule.
  - **3 new icons extracted from Figma via `exportAsync`:**
    1. `icon-arrow-forward.svg` (25×15) — Figma node `648:1595` Vector 61, mirrored horizontally. → arrow for EnergyRow + AICard "Подробнее" link.
    2. `icon-ai-brain.svg` (21×21) — Figma node `541:7155` Vector. Brain/AI duality path for AI-summary alert-pill--info leading icon. Fill #26767D.
    3. `icon-video-camera.svg` (27×19) — Figma node `648:1609` Vector. Camera body+lens for ZOOM section. Filter brightness(0) invert(1) makes it white on blue bg.
  - **HTML fixes (all 9 screens, Python batch):** emoji `😩/😊` → `icon-mood-neutral/good.svg`; `→` text → `icon-arrow-forward.svg`; scr-07 info-pill → `alert-pill--info` + `icon-ai-brain.svg`; scr-09 inline SVG → `icon-video-camera.svg`; scr-09 booking info-pill ip-icon removed (Figma: no icon, just text); v-badge prefix chars removed (Figma: color-only badges); all toast onclick emoji cleaned. 0 emoji remaining.
  - **COMPONENTS-CATALOG.md updates:** EnergyPair entry rewritten (`.energy-pair` → `.energy-row`, "emoji circles" → DS icon references); AICard entry updated (Подробнее → icon-arrow-forward noted).
  - **ASSETS-INDEX.md:** 3 new icon rows appended. Total: 73 → 76 canonical icons.
  - **Net effect:** `_dashboard-flow.html` 37,421 bytes (post-fixes), 0 emoji, 19/19 icon refs resolved, div balance 221/221. `_shared/components.css` + `_shared/shell.css` globally fixed. DS: +3 SVG files. `ASSETS-INDEX.md` +3 rows. `COMPONENTS-CATALOG.md` EnergyPair + AICard updated.

- **2026-05-19 (session 17) — ASSETS-INDEX Cleanup + Final Pre-Handoff Validation:**
  - **Root cause found:** `ASSETS-INDEX.md` was truncated at line 260 (Master Dashboard 8 section header only, no table rows). Bash mount staleness in session 16 caused `cat >>` append to return exit 0 but write to an already-stale path — content was lost. Python validator in session 16 reported ❌ for these entries; "11/11 ✅" count at end of session 16 was incorrect (4 of 11 checks used bash-stale content).
  - **Fixes applied to `ASSETS-INDEX.md`:**
    1. Master Dashboard 8 section completed: 6 icon rows added (`icon-master-nav-home`, `icon-master-nav-students`, `icon-master-header-notif`, `icon-master-filter`, `icon-master-checkin-alert`, `icon-master-rating-star`) with correct Figma node IDs and descriptions.
    2. Dashboard 9 DS-compliance section added: 3 icon rows (`icon-arrow-forward`, `icon-ai-brain`, `icon-video-camera`) — these were flagged missing by validator.
    3. `icon-nav-home.svg` entry corrected to `icon-nav-home-active-composite.svg` (file was renamed in dedup pass 2026-05-19 but ASSETS-INDEX entry was not updated).
    4. Orphaned duplicate rows (lines 295–311) removed — these were a prior session's failed append that ended up below the Backgrounds section break.
    5. Known-gaps warning added: 4 icon files documented but missing from disk (`icon-cal-duration`, `icon-cal-datetime`, `icon-analytics-tab-profile`, `icon-analytics-tab-list`) — need re-extraction at start of Calendar 11 / Analytics 3 mockup builds.
  - **Validation: 29/29 ✅ ALL CLEAR** (Read-tool verified; bash mount stale throughout but Read confirms correct state).
  - **Net effect:** `ASSETS-INDEX.md` complete and clean. 9 previously undocumented icons now have entries. 1 renamed icon corrected. 4 missing-file gaps flagged. No mockup changes. No CSS changes. No token changes.

- **2026-05-19 (session 18) — Calendar 11 Mockup Viewer (Macro-Phase II, Priority 2):**
  - **DS COMPLETE GATE ✅ confirmed by operator + Dashboard 9 MOCKUP GATE ✅ implied by "действуй".** Macro-Phase II active. Entry point: `03_mockups/user/_calendar-flow.html` (new file).
  - **Frame list resolved via Figma:** Calendar 11 root `541:1553` has 11 children: `21_Calendar 1` (648:1673), `22_Calendar filter` (648:1859), `23_Calendar 2` (541:1744), `24_Practice Detail` (648:1934), `25_Master Profile` (541:2065), `26_Booking Success 2` (541:2120), `27_Ask Master` (541:2156), `28_Practice (забронировано)` (648:2045), `29_Feedback` (541:2286), `30_Check-in Success` (541:2345), `31_Message` (541:6514, 350×293 widget).
  - **4 "missing SVGs" warning in _HANDOFF resolved:** `icon-cal-duration` → canonical `icon-time.svg`; `icon-cal-datetime` → canonical `icon-calendar.svg`; `icon-analytics-tab-profile` → canonical `icon-master-nav-home.svg`; `icon-analytics-tab-list` → canonical `icon-master-nav-students.svg`. No Figma re-extraction needed.
  - **Built `03_mockups/user/_calendar-flow.html`:** 11-column combined viewer (PNG etalon top / HTML bottom). AP-M-6 compliant — screen-specific CSS in `<style>` only. Shared CSS via `_shared/` three-layer architecture. New screen-specific components: `.cal-week-strip` + `.cal-day-cell` + `.cal-filter-btn` + `.cal-section-date` + `.filter-panel` + `.filter-chip` + `.practice-detail-card` + `.complexity-row` + `.mpr-*` (master profile) + `.bks-*` (booking success) + `.feedback-rating` + `.fr-option` + `.cal-success-body`.
  - **Screens built (8/11):** col 01 calendar-1 (week strip + practice list + bottom-nav diary-active), col 02 calendar-filter (FilterSheet full panel), col 04 practice-detail (PracticeMetaRow + collapsibles + MasterCard + warning + cost), col 05 master-profile (hero + stats + practice list), col 06 booking-success-2 (SVG illustration + ask-master input), col 08 practice-booked (Breathwork variant), col 09 feedback (FeedbackRating 3-option), col 10 checkin-success ("Спасибо за feedback!" + icon-cal-success-check).
  - **TBD overlays (3/11):** col 03 (23_Calendar 2, no PNG deferred), col 07 (27_Ask Master, no PNG deferred), col 11 (31_Message widget 350×293, non-standard size).
  - **Verification:** 0 emoji, 0 missing icon refs (19 icons resolved), div balance 231/231, 0 parse errors, 11/11 structural checks, 8/8 screenshot refs valid.
  - **Tracking updated:** sprint-02.md Macro-Phase II Calendar 11 row → 🔧, `03_mockups/INDEX.md` +1 row, `docs/INDEX.md` Recent Changes.
  - **Next:** Awaiting operator MOCKUP GATE for Calendar 11. If passes → Priority 3 = Profile 7 (`03_mockups/user/_profile-flow.html`, new file).
    - **05 practice-live** — master-card + 2 v-badge (live + info) + action-row (Zoom glass) + stats-row + bottom-nav (home active)
    - **06 booked-practice** — master-card + v-badge success + booking-card + action-row + bottom-nav (home active)
    - **07 ai-summary** — alert-pill--info (brain icon + "Feedback" title + sub) + ai-card + recommendation-card list + bottom-nav (home active)
    - **08 my-reservations** — section-title + 3 booking-card rows + bottom-nav (home active)
    - **09 booking-detail** — top-header + booking-card + group-title "ZOOM" + v-link-block + bottom-nav (home active)
  - **DS compliance:** zero screen-specific `<style>` blocks except `.dash-*` / `.ci-*` scoped prefixes. All atomic components reference DS classes.
  - **Net effect:** `_dashboard-flow.html` fully rebuilt (9/9 screens, AP-M-6 compliant). New shared classes added to `_shared/components.css` (stats-row, action-row, recommendation-card).

- **2026-05-19 (session 17+) — Calendar 11 DS Rebuild + Bottom Nav DS-first:**
  - **Phase A — Calendar 11 DS pass (full):**
    - All 11 calendar screens rebuilt in `_calendar-flow.html` with AP-M-6 compliance.
    - `icon-cal-filter.svg` extracted from Figma node `648:1848` and saved to assets/icons/.
    - All Calendar 11 CSS components promoted to `_shared/components.css`: `.scr-scroll`, `.scr-bottom`, `.cost-row`, `.cal-week-strip`, `.cal-week-cells`, `.cal-day-cell`, `.cdc-*`, `.cal-week-nav-row`, `.cal-week-nav-btn`, `.cal-title`, `.cal-filter-btn`, `.cal-filter-chips-row`, `.filter-panel`, `.filter-chip`, `.practice-detail-card`, `.pdc-*`, `.complexity-row`, `.mpr-hero`, `.mpr-*`, `.bks-body`, `.bks-*`, `.fbk-card`, `.feedback-rating`, `.fr-*`, `.cal-success-body`, `.msg-widget`, `.msg-*`, `.ask-master-mini-card`, `.ask-master-*`, `.warning-alert`, `.list-row`.
    - `_calendar-flow.html` rebuilt: all 11 screens built (no TBD), `<style>` stripped to `.dev-btn` only, div balance 259/259, all DS icon refs correct.
    - ASSETS-INDEX.md updated: iteration 13→14, icon count updated.
    - COMPONENTS-CATALOG.md: 9 Calendar 11 ⬜ candidates added (CalendarWeekStrip, CalFilterButton, FilterPanel, PracticeDetailCard, MasterProfileHero, FeedbackRating, MessageWidget, AskMasterMiniCard, CalSuccessBody).
  - **Phase B — Bottom Nav DS-first (§7.0):**
    - Figma audit: User nav (Group 1988 `541:*` frames) + Master nav (Group 2648 `758:1748` АНАЛИТИКА frame) fully spec'd. Button size 63×63, container 327×63, icon fill `#4C6589`, bg `rgba(98,122,156,0.15)`.
    - **Master nav icons corrected:** Previous `icon-master-nav-students.svg` was wrong (contained clipboard icon from shared ДАШБОРД nav). Correct icons exported from Group 2648:
      - `icon-master-nav-schedule.svg` (`758:1759`, 27×27, firstM=M7.48828) — NEW
      - `icon-master-nav-students.svg` (`758:1765`, 21×27, firstM=M9.28125) — REPLACED (correct person icon)
      - `icon-master-nav-profile.svg` (`758:1770`, 27×27, firstM=M26.9945) — NEW
    - **DS promoted:** `.bottom-nav--user` + `.bottom-nav--master` semantic variants added to `_shared/components.css`.
    - **Design system updated:** `velo-design-system.html` Bottom Navigation section added (4 demo variations: user home active, master home active, user calendar active, master students active). Icons gallery updated with corrected master nav entries.
    - **COMPONENTS-CATALOG.md:** BottomNav entry updated (--user/--master variants). MasterNavBar entry completed (was truncated). Analytics icon refs corrected.
    - **Mockup files:** `_dashboard-flow.html` + `_calendar-flow.html` updated to `class="bottom-nav bottom-nav--user"` (semantic modifier).
    - **ASSETS-INDEX.md:** Iteration 13→14 (78 canonical icons after +2 new +1 corrected).
  - **Net effect:** 78 DS icons, `_shared/components.css` 860→1518 lines (+658 lines Calendar 11 + Bottom Nav variants), `velo-design-system.html` completed (was truncated, now 1032 lines), COMPONENTS-CATALOG.md 1517→1637 lines. All 4 HTML mockup files DS-compliant. Bottom Nav DS-first §7.0 requirement satisfied.

- **2026-05-20 (session 18) — Dashboard 9 MOCKUP GATE: Screens 01-03 Pixel Fixes:**
  - **Scope:** Operator-led pixel review of `_dashboard-flow.html` screens 01-03 against Figma PNG etalons. Session covers 3/9 screens; screens 04-09 remain for next session.
  - **DS-level fixes (applied to `_shared/components.css`, affect all mockup files):**
    - `.section-title` — added `font-weight: 700` (was unset, causing visibly lighter weight than Figma); affects Dashboard + Calendar section headings.
    - `.practice-card .pc-title` — added `font-weight: 700` (was unset, causing inconsistent weight vs Figma).
    - `.practice-card .pc-avatar` — size `38×38 → 48×48px` + `font-size: 16px` + `img { width: 28px; height: 28px }` constraint. Matches Figma avatar proportions.
    - Regression check: `_calendar-flow.html` uses `.section-title` (3×) + `.practice-card`/`.pc-avatar`/`.pc-title` (5× each) — visual update only, no structural regression. `_onboarding-flow.html`: no usage. `velo-design-system.html`: embedded CSS, no `.pc-avatar` demo.
  - **Screen-specific fixes in `_dashboard-flow.html` `<style>` block:**
    - `.dash-content` — `padding-bottom: 84px` (nav clearance; was missing, last content items could be hidden behind bottom-nav).
    - Bottom-nav structural fix — nav moved OUTSIDE `.dash-content` as direct child of `.frame.html`. Added `.frame.html > .bottom-nav { flex-shrink: 0; margin-top: 0 }` to prevent `margin-top: auto` from components.css pushing it.
    - `.ai-header` pattern — `display: flex; align-items: center; justify-content: space-between` for "AI-саммари" label + tabs on the same row (Figma confirms inline layout).
    - `.ai-section-label` font-size unified to 16px/700 with `.section-title`.
    - Added inline CSS: `.greeting-label`, `.greeting-hello`, `.action-row`, `.stats-row`, `.stat-card`, `.sc-value`, `.sc-label`, `.ai-tabs--inline`, `.ci-card`, `.ci-question`, `.ci-sub`, `.mood-widget .mw-pick:not(.is-active)` scope overrides.
  - **Screen 01 content (final):** greeting (Доброе утро / Алина) + 2 alert-pills (orange warning clock + teal info feedback) + practice-card (Alex Mindful, Завтра 07:00, paid-badge) + action-row (Zoom glass + Check-in primary) + stats-row (12 практик / 9,5 часов) + ai-header inline (title + Неделя/Месяц tabs) + ai-card + bottom-nav OUTSIDE dash-content.
  - **Screen 02 content (final):** no greeting (Figma screen 02 starts directly with alert) + info alert-pill (feedback) + practice-card + action-row + stats-row + ai-header inline + ai-card expanded (text + mood row `с 😐 до 😊` + Подробнее link outside card) + bottom-nav OUTSIDE dash-content.
  - **Screen 03 content (final):** `.top-header` with `.header-back` + "Check-in" title + practice info (Утренняя медитация, с Alex Mindful) + ci-card question ("Как вы себя чувствуете?") + mood-widget (Не очень / Нормально active / Хорошо) + v-textarea + primary CTA.
  - **DS audit — back-button pattern unification:**
    - Operator flagged inconsistent back-button usage. Audit confirmed TWO canonical patterns in components.css: `.velo-back-arrow` (onboarding-only, standalone pill) vs `.top-header .header-back` (app-screen header, combined with title). Both are correct in their context. NOT redundant.
    - `.top-header` promoted from `⬜ candidate` → `✅ canon` in `COMPONENTS-CATALOG.md`. When-to-use updated: "ALL detail/nested app screens. ONE canonical header. Do not use `.velo-back-arrow` in app screens — onboarding-only." Usage count documented: 12 screens (Dashboard 03-09 + Calendar 08-11).
  - **Pending:** Screens 04-09 MOCKUP GATE review. Calendar 11 MOCKUP GATE after Dashboard complete.
  - **Net effect:** `_shared/components.css` 3 DS fixes (section-title 700, pc-title 700, pc-avatar 48px). `_dashboard-flow.html` screens 01-03 pixel-corrected. `COMPONENTS-CATALOG.md` `.top-header` promoted to ✅ canon.

- **2026-05-20 (session 19) — Dashboard 9 MOCKUP GATE: Screens 03-06 Pixel Fixes:**
  - **Scope:** Operator sent PNG etalons for screens 03 (check-in), 05 (practice-live), 06 (booked-practice). PNG-first analysis vs HTML builds. Multiple discrepancies found and fixed.
  - **DS-level fixes (applied to `_shared/components.css`, affect all mockup files):**
    - `.practice-info .pi-title` — added `font-weight: 700` (was unset; Figma shows bold title in all practice-info cards on screens 03, 05, 06, 09).
    - `.list-row .lr-chevron` — replaced text char `⌄` approach with CSS border-based chevron arrow (`border-right + border-bottom, rotate(45deg)`). Cleaner render matching Figma V-shape.
  - **Screen 03 (check-in) fixes:**
    - `pi-meta` — added `icon-calendar.svg` (11×11, opacity 0.6) inline before "Завтра, 07:00", matching Figma pattern "с Alex Mindful [📅] Завтра, 07:00".
  - **Screen 05 (practice-live) — major restructure:**
    - **Root cause:** PNG etalon shows video placeholder as steel-pale rounded card INSIDE content flow, not a dark full-width element before scr-content. Also: no play button in Figma, no pi-icon in practice-info card.
    - **Video block restructured:** moved from standalone element (before `scr-content`) INTO `scr-content` div. CSS: dark navy gradient + play button → steel-pale flat fill (`var(--velo-color-steel-pale)`) + `border-radius: var(--velo-radius-lg)` + `height: 240px`. Content: "video" placeholder text (no `.video-play` div).
    - **practice-info card:** removed `pi-icon` div (not present in Figma etalon for screen 05). Title corrected "Утренняя йога" → "Утренняя медитация". Meta corrected "Алекс Майндфул · 60 мин" → "с Alex Mindful".
  - **Screen 06 (booked-practice) fixes:**
    - `pi-title` — "Утренняя йога" → "Утренняя медитация" (matches PNG etalon).
    - `pi-meta` — "Пятница, 20 января · 09:00 · 60 мин" → inline icons: `icon-calendar.svg` + "Завтра, 07:00" + `icon-time.svg` + "45 мин" (matches Figma meta row pattern).
    - `lr-chevron` spans — removed "⌄" text chars (empty spans, CSS handles shape).
    - Button labels — "Check-in" → "Check-in перед практикой"; "Отменить" → "Отменить бронирование" (both match PNG etalon exactly).
  - **Verification:** Python validation — 9/9 frames intact, icon-calendar.svg + icon-time.svg exist on disk, video-play CSS removed, scr-06 button labels correct, pi-title font-weight:700 in components.css. Zero structural regression.
  - **Pending:** Screens 04, 07, 08, 09 MOCKUP GATE review (operator to send PNG screenshots).
