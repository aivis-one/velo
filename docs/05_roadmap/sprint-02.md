# Sprint 2 — Styleguide + First Mockups (P0)

```
Dates:    2026-05-17 → in progress
Status:   in progress (Phase 3 ✅ closed, Phase 4 🔄 — Onboarding 8 ✅, Dashboard 9 ⬜ next)
Owner:    Cowork (executor), Operator (validator)
Goal ref: ROADMAP.md §5
Phase:    Phase 3 (Styleguide HTML) ✅ + Phase 4 (P0 mockups) 🔄
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
Status: 🔄 **in progress** — Onboarding-блок (8) ✅ ЗАКРЫТ оператором 2026-05-18 ("приняты экраны и дизайн"). Dashboard-блок (9) — следующий focus.

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

- [x] STYLEGUIDE GATE passed (T2.2) — 2026-05-17
- [ ] P0 mockups built; MOCKUP GATE passed for each (operator expanded P0 to Onboarding 8 + Dashboard 9)
- [ ] `03_mockups/INDEX.md` reflects P0 status
- [ ] vue-i18n installed and minimally wired in `frontend/` (Claude Code task T2.6)

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
