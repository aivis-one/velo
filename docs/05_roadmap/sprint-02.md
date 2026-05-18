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
| 4 | Profile 7 | `541:2355` | 7 | ⬜ pending |
| 5 | Diary 20 | `541:2816` | 20 | ⬜ pending |
| 6 | Messages 3 | `541:2717` | 3 | ⬜ pending |
| 7 | Analytics 3 | `758:1529` | 3 | ⬜ pending |
| 8 | Practices 15 | `758:1950` | 15 | ⬜ pending |
| 9 | Master Dashboard 8 | `758:3245` | 8 | ⬜ pending |
| 10 | Master Onboarding 13 | `758:4318` | 13 | ⬜ pending |

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
| 2 | Dashboard 9 | `03_mockups/user/_dashboard-flow.html` | ✅ MOCKUP GATE ready (2026-05-18 session) |
| 3 | Calendar 11 | `03_mockups/user/_calendar-flow.html` | ⬜ pending DS-complete |
| 4 | Profile 7 | `03_mockups/user/_profile-flow.html` | ⬜ pending DS-complete |
| 5 | Diary 20 | `03_mockups/user/_diary-flow.html` | ⬜ pending DS-complete |
| 6 | Messages 3 | `03_mockups/user/_messages-flow.html` | ⬜ pending DS-complete |
| 7 | Analytics 3 | `03_mockups/user/_analytics-flow.html` | ⬜ pending DS-complete |
| 8 | Practices 15 | `03_mockups/user/_practices-flow.html` | ⬜ pending DS-complete |
| 9 | Master Dashboard 8 | `03_mockups/master/_dashboard-flow.html` | ⬜ pending DS-complete |
| 10 | Master Onboarding 13 | `03_mockups/master/_onboarding-flow.html` | ⬜ pending DS-complete |

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
| 01 | dashboard-1 | 🔧 skeleton iteration 1 |
| 02 | dashboard-2 | 🔧 skeleton iteration 1 |
| 03 | check-in | 🔧 skeleton iteration 1 |
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
- [ ] **DS COMPLETE GATE** — all 10 blocks DS-complete (Macro-Phase I checklist above all ✅)
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

- **2026-05-18 (session 5) — Sprint 2 Quality Audit:**
  - **Audit triggered by operator:** operator observed onboarding illustration icons absent from DS and questioned whether previous sessions had fully transferred all assets. Previous sessions correctly tokenized all 97 SACRED screens in Sprint 1 Phase A but did NOT extract SVGs from Master Onboarding block (block #10) — this is expected behavior (Phase B only happens per-block during DS harvest, and Master Onboarding was not yet harvested). Correctly identified as a future Macro-Phase I item, not a previous-session failure.
  - **4 genuine gaps found in already-completed blocks (Dashboard 9 + Calendar 11):** Three FeedbackRating icons (`icon-feedback-questions`, `icon-feedback-good`, `icon-feedback-fire`) from Calendar 11 screen 29 (`541:2286`) + one Dashboard check-in success circle graphic (`icon-checkin-success`) from Dashboard screen 04 (`541:6988`) — all absent from ASSETS-INDEX and `velo-design-system.html`.
  - **All 4 gaps remediated:** Exported individually via `use_figma` Plugin API `exportAsync` to avoid 20KB truncation. Saved to `02_design-system/assets/icons/`. ASSETS-INDEX updated (29 → 33 icons). `velo-design-system.html` icon gallery updated with "Audit-recovered" group.
  - **COMPONENTS-CATALOG.md corruption fixed:** File was truncated at line 565 mid-word ("Anatom") in PracticeMetaRow entry. FilterChip, FilterSheet, FeedbackRating entries were completely absent despite being named in sprint-02 iteration 10. All 4 entries now complete with full anatomy/tokens/icons/provenance.
  - **Net effect this session:** 4 new SVG files created, ASSETS-INDEX +4 rows, COMPONENTS-CATALOG +4 complete entries (PracticeMetaRow restored + FilterChip + FilterSheet + FeedbackRating added), velo-design-system.html +4 icons in gallery. No token changes. No mockup changes.

---

## Closure

- STYLEGUIDE GATE: ☑ passed 2026-05-17
- **P0 MOCKUP GATEs (Onboarding 8): ☑ 8/8 passed 2026-05-18**
- P0 MOCKUP GATEs (Dashboard 9): ☐ not yet started — следующий блок Phase 4
- Deferred to Sprint 3+: ☐
- Methodology amendments proposed: ☐
- Token master changed during sprint? ☑ yes — Phase 3 cleanup (`--velo-shadow-card/modal`) + Phase 4 onboarding promotion (text re-alias, component heights, stack gaps, typography canon, glass canon, button halo composition). variables.css master ↔ deliverable MD5-identical 2026-05-18.
- Operator signoff Onboarding 8 (date): ☑ 2026-05-18 ("приняты экраны и дизайн")

---

## References

- Roadmap: `ROADMAP.md` §5
- Methodology: §6.6 (component tiers), §6.8 (styleguide), §7 (mockup layer), §10.3 (STYLEGUIDE GATE), §10.4 (MOCKUP GATE), §11.2–11.3 (anti-patterns + token bridge), §9.4–9.5 (prompts)
m Dashboard screen `user-dashboard-04-checkin-success` (`541:6648`). All 4 extracted, saved to `assets/icons/`, added to `velo-design-system.html` + `ASSETS-INDEX.md`. COMPONENTS-CATALOG, sprint-02, INDEX.md all updated.
  - **Master Onboarding illustrations extraction (Task #16):** Operator confirmed all 4 Master Onboarding illustrations (`758:4694` welcome / `758:4700` space / `758:4707` analytics / `758:4714` approved) must be in DS. Three exported normally via `exportAsync`. Fourth (`icon-master-approved.svg`, Group 2523, 62KB SVG) exceeded 20KB Figma MCP response limit — required 3-chunk path data extraction strategy (`.substring(0, 7000)` / `.substring(7000, 14000)` / `.substring(14000, end)`). Fill-only export (no stroke/mask duplication) yielded 9-element ~30KB SVG. All 4 saved to `assets/icons/`, gallery entries added to `velo-design-system.html`, `ASSETS-INDEX.md` updated with new table section. Task #16 complete.
  - **Net effect session 5 + session 6:** 4 gap icons + 4 Master Onboarding illustrations = **8 new SVG assets** extracted and integrated. `velo-design-system.html` icon gallery now reflects all known Figma icon assets. `ASSETS-INDEX.md` icon count +8.
