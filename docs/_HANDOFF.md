# VELO — Universal Handoff Prompt

Last refresh: 2026-05-18

> **Это указатель, не свалка контекста.** Состояние проекта живёт в трекинг-файлах под `docs/`. Этот файл — стартовая последовательность, которую читает свежий чат, чтобы самостоятельно понять где мы и что делать дальше.

---

## ВХОД В ПРОЕКТ — 6 ШАГОВ

Свежий Claude / новая сессия: выполни в порядке.

### 1. Прочитай master-индекс

`D:\02_Projects\velo\docs\INDEX.md`

Там: folder map, текущий sprint, версии методологии и роадмапа, секция **Recent Changes** в хвосте — она самая важная, в ней последний state log по дням.

### 2. Прочитай методологию

`D:\02_Projects\velo\docs\04_methodology\VELO-METHODOLOGY.md` (версия указана в INDEX)

Это **single source of truth** для процесса. Особенно §2.5 (VELO Invariants I1–I8), §6 (Design System layers), §7 (Mockup Layer), §8 (Spec Layer), §10 (Gates), §11 (Anti-patterns + token bridge).

### 3. Прочитай роадмап

`D:\02_Projects\velo\docs\05_roadmap\ROADMAP.md` (версия в INDEX)

Общий план по 12 спринтам.

### 4. Открой файл текущего спринта

Имя спринта взять из INDEX.md (раздел `Sprint reference`). Сейчас это **Sprint 2**:

`D:\02_Projects\velo\docs\05_roadmap\sprint-02.md`

Самое важное:
- Раздел **Task checklist** — каждая задача T2.X с её статусом (✅ / 🔄 / ⬜) и текущим состоянием
- Раздел **Daily log** — хронология сессий
- В T2.4 (или соответствующей активной задаче) — **per-column статус** и **pending fixes** (если есть)

### 5. Прочитай локальные INDEX-ы по своему скоупу

| Скоуп задачи | Local INDEX |
|---|---|
| Mockups (Phase 4) | `D:\02_Projects\velo\docs\03_mockups\INDEX.md` |
| Design System (Phase 2-3, promotion passes) | `D:\02_Projects\velo\docs\02_design-system\INDEX.md` |
| Assets (icons, backgrounds, screenshots) | `D:\02_Projects\velo\docs\02_design-system\assets\ASSETS-INDEX.md` |
| Specs (Phase 5) | `D:\02_Projects\velo\docs\01_deliverable\screens\INDEX.md` |

### 6. Прочитай project inputs если задача требует

| Когда нужно | Файл |
|---|---|
| Frontend code rules | `D:\02_Projects\velo\docs\06_project-inputs\ARCHITECTURE.md` |
| Backend API contract | `D:\02_Projects\velo\docs\06_project-inputs\api-openapi.json` |
| Figma operations (если придётся снова трогать Figma) | `D:\02_Projects\velo\docs\02_design-system\FIGMA-OPERATIONS-GUIDE.md` |

---

## ЧТО ДЕЛАТЬ ДАЛЬШЕ

**Сейчас Sprint 2 Phase 4 — Onboarding 8 ✅ закрыт (2026-05-18). Следующий блок: Dashboard 9.**

В файле текущего спринта (см. шаг 4) найди первую задачу со статусом 🔄 in progress или первый ⬜ pending в активном Task checklist. Это твой entry point.

Если в **Daily log** последней записи указан конкретный pending список — это и есть стартовая точка.

### Entry point для новой сессии (Dashboard 9 start)

Создать новый combined viewer `03_mockups/user/_dashboard-flow.html` на 9 колонок. Структура идентична `_onboarding-flow.html`:
- frame 402×874, PNG-эталон сверху / HTML снизу
- DS canon ПОЛНОСТЬЮ готов в `02_design-system/tokens/variables.css` — используй tokens напрямую
- Эталоны лежат в `02_design-system/assets/screenshots/user/user-dashboard-*.png`
- Bg плата `velo-bg-app.png` универсальный

**DS canon уже промоутирован — НЕ пересоздавай патерны заново:**
- Typography: `--velo-typo-h1-*` (30/36/letter-spacing 1.2, color steel-light) + `--velo-typo-body-*` (18/24, steel-light)
- Button heights: `--velo-button-height: 52px`, `--velo-input-height: 42px`
- Stack gaps: `--velo-stack-gap-buttons: 16px`, `--velo-stack-gap-forms: 10px`
- Glass canon (two-layer): `.element` transparent + `::before` border + `::after` 10% blue fill ПОВЕРХ border, halo `--velo-shadow-button` (drop-on-top), halo extent ≤ stack-gap-buttons
- Text aliases все на steel-light (#627a9c) — primary/secondary/link
- Pagination dots: big-active 14×14 круг + small-passive 8×8

**Figma access:** есть через `mcp__2d3ce5c3-..__use_figma` Plugin API. File key `F7PD5isLfLdyc0q1Bd5n5c`. Dashboard SACRED root = `541:6648` (9 frames). Используй для извлечения SVG-иконок если они нужны (как делали с `icon-onb-*.svg`). Чтобы найти node IDs — `getNodeByIdAsync('541:6648')` → children → найти GROUP-ы внутри скринов.

**Workflow (best practice из Onboarding):**
1. Открыть эталон PNG в DS → pixel-measure целевые позиции/размеры через Playwright + numpy если нужна точность
2. Построить HTML колонки на готовых DS-токенах (skeleton сначала)
3. Извлечь vector-иконки из Figma через `use_figma` exportAsync (chunk > 20KB через split-response calls)
4. После каждой колонки — render через `python3 /tmp/render_login.py` (адаптируй для dashboard cols)
5. Итерации с оператором — НЕ переоткрывай patterns, они закрыты

После прочтения шагов 1-6 ты должен уметь ответить себе:
- Текущий sprint (номер и название)
- Текущая фаза (Phase 2 / 3 / 4 / 5)
- Текущая конкретная задача (T2.X или артефакт)
- Что закрыто, что в работе, что ждёт
- Файлы которые трогать
- Имя оператора и его роль (см. INDEX «Users» если есть)

Если что-то из этого неясно после чтения — **спроси оператора, не предполагай**.

---

## ПРАВИЛА ПОВЕДЕНИЯ (для исполнителя)

### Test = test
Каждое визуальное изменение проверяется **парной сверкой с Figma-эталоном** (PNG в `02_design-system/assets/screenshots/`). Никакой самоуверенности — открыл скрин, посмотрел рядом с эталоном, отметил расхождения.

Для headless-скриншотов из mockups: Playwright + chromium-headless-shell ставится в новой sandbox-сессии командой `pip3 install playwright --break-system-packages && python3 -m playwright install chromium-headless-shell` (~30 сек). **Не предполагай что он уже стоит** — кэш sandbox-сессионный.

### Не галлюцинировать
Если не уверен в значении — иди в файл и проверь. Если файл недоступен — спроси оператора. Хуже галлюцинации нет ничего.

### Bash mount caveat
Bash-mount `/sessions/.../mnt/docs/` иногда показывает устаревшие/обрезанные версии файлов после Edit. **Истина — это файл-тулы (Read/Edit/Write).** Если bash grep даёт странный результат, доверяй Read.

### Vector vs raster
Иконки и логотипы из Figma — **SVG**, а не PNG. PNG — только для фотографических фонов (например `velo-bg-app.png`). Если в DS лежит PNG там где должен быть SVG, это либо legacy либо ошибка предыдущей сессии — флагуй.

### Asset path canon
- Backgrounds: `02_design-system/assets/backgrounds/`
- Icons + brand logos: `02_design-system/assets/icons/`
- Screen PNG references: `02_design-system/assets/screenshots/{role}/`
- Fonts: `02_design-system/assets/fonts/`

Из мокапов ссылка относительная: `../../02_design-system/assets/{...}`.

### Sprint closure
Когда закрываешь задачу или спринт — обнови **минимум 3 файла**:
1. Текущий `sprint-NN.md` (отметить ✅, добавить запись в Daily log)
2. Локальный INDEX скоупа (mockups / DS / assets / specs)
3. Top-level `INDEX.md` (Recent Changes секция)

Это требование методологии §12.2.

### Когда контекст устал
Симптомы: одна и та же правка повторяется, путаешься в путях, bash truncation начинает блокировать, task list > 50 пунктов. Делай handoff:
1. Зафиксируй state во всех 3 INDEX-ах (см. выше) + sprint-NN.md
2. Обнови этот `_HANDOFF.md` если изменился стартовый чек-лист
3. Скажи оператору «контекст устал, рестартую» — он перезапустит чат
4. Новая сессия читает этот файл, идёт по 6 шагам

---

## ЧТО ЭТОТ ФАЙЛ НЕ ДЕЛАЕТ

- Не дублирует state из других файлов (он уже есть в INDEX/sprint-NN/etc.)
- Не содержит история сессий (она в Daily log соответствующих sprint-NN.md)
- Не содержит конкретных значений / координат / id (они в актуальных трекинг-файлах)
- Не нужно его обновлять каждую сессию — только если меняется **процедура входа** или появляются новые жёсткие правила поведения

---

## Anchor

```
[_HANDOFF.md | v1.1 | 2026-05-18]
Universal entry-point prompt. State lives in INDEX.md + sprint-NN.md + local INDEXes.
Read sequence: INDEX → methodology → roadmap → sprint-NN → local INDEX → continue from first pending task.
Current entry point (2026-05-18): Sprint 2 Phase 4 Dashboard 9 — start new combined viewer
`03_mockups/user/_dashboard-flow.html` on готовом DS canon. Figma access via use_figma Plugin API.
Location: D:\02_Projects\velo\docs\_HANDOFF.md
```
