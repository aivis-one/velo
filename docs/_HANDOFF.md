# VELO — Universal Handoff Prompt

Last refresh: 2026-05-18

> **Это указатель, не свалка контекста.** Состояние проекта живёт в трекинг-файлах под `docs/`. Этот файл — стартовая последовательность, которую читает свежий чат, чтобы самостоятельно понять где мы и что делать дальше.

---

## ПРОМПТ ДЛЯ ЗАПУСКА НОВОЙ СЕССИИ

Скопируй блок ниже целиком в первое сообщение нового чата. Он самодостаточен — больше ничего оператор делать не должен. Промпт **универсален** — версии методологии и roadmap резолвятся через `INDEX.md`, поэтому не требует обновления при version bump. Обновляется только при смене entry point, текущего sprint или ролей исполнителя — это входит в ритуал sprint closure (см. §«Sprint closure» ниже).

```
Это сессия по проекту VELO. Точка входа:
D:\02_Projects\velo\docs\_HANDOFF.md

Действия:
1. Прочитай _HANDOFF.md целиком.
2. Пройди 6-шаговый чек-лист входа (§ВХОД В ПРОЕКТ — 6 ШАГОВ): прочитай docs/INDEX.md → methodology (версия в INDEX) → roadmap (версия в INDEX) → текущий sprint-NN.md (имя в INDEX «Sprint reference») → 03_mockups/INDEX + 02_design-system/INDEX + 02_design-system/COMPONENTS-CATALOG.md. Если задача затрагивает Claude Code track — также прочитай 06_project-inputs/CBSHOME-PATTERNS-FOR-VELO.md.
3. Доложи коротко: что прочитано, текущий sprint и phase, текущая задача (entry point из секции «ЧТО ДЕЛАТЬ ДАЛЬШЕ»), какие правила поведения активны.
4. НЕ начинай работу до моего «погнали».

Текущий спринт: Sprint 2 (EXPANDED, in-progress) — `05_roadmap/sprint-02.md`. Macro-Phase I: DS harvest all blocks. Onboarding ✅ + Dashboard 9 ✅ done. Next: Calendar 11 harvest.

Я — оператор/архитектор. Ты — исполнитель в духе Cowork. Перед любым multi-step действием — план + ожидание подтверждения. До действий — режим анализа. Не плоди новых файлов без явного разрешения — используй существующие docs. Process documentation is English-default (methodology v1.4 P6); Russian only in UI sample data + operator quotes + `06_project-inputs/` (see methodology §11.5 AP-P-8 exception table).
```

---

## ВХОД В ПРОЕКТ — 6 ШАГОВ

Свежий Claude / новая сессия: выполни в порядке.

### 1. Прочитай master-индекс

`D:\02_Projects\velo\docs\INDEX.md`

Там: folder map, текущий sprint, версии методологии и роадмапа, секция **Recent Changes** в хвосте — она самая важная, в ней последний state log по дням.

### 2. Прочитай методологию

`D:\02_Projects\velo\docs\04_methodology\VELO-METHODOLOGY.md` (версия указана в INDEX)

Это **single source of truth** для процесса. Особенно §2.5 (VELO Invariants I1–I8), §1.1 (Six Foundational Principles — **P6 English-default v1.4** для всей process documentation), §6 (Design System layers — **§6.8 DS Promotion Visualisation rule v1.3** добавлен), §7 (Mockup Layer — **§7.0 Block-Harvest-First v1.3** mandatory для SACRED блоков), §8 (Spec Layer), §10 (Gates), §11 (Anti-patterns + token bridge — **§11.5 AP-P-6 + AP-P-7 v1.3** + **AP-P-8 Russian narrative anti-pattern v1.4** с exception table).

### 3. Прочитай роадмап

`D:\02_Projects\velo\docs\05_roadmap\ROADMAP.md` (версия в INDEX)

Общий план по 12 спринтам.

### 4. Открой файл текущего спринта

Имя спринта взять из INDEX.md (раздел `Sprint reference`). Сейчас это **Sprint 2 (expanded, in-progress)**:

`D:\02_Projects\velo\docs\05_roadmap\sprint-02.md`

Самое важное:
- Раздел **Expanded Scope** — два macro-phases (I = DS harvest all blocks, II = all mockups)
- Таблица **Macro-Phase I** — 10 блоков с чекбоксами DS-complete (Onboarding ✅, Dashboard 9 ✅, остальные ⬜)
- Таблица **Macro-Phase II** — 10 mockup viewers с чекбоксами (Onboarding ✅, Dashboard 9 ✅, остальные ⬜)
- Раздел **Daily log** — хронология всех сессий (история Sprint 2 начиная с 2026-05-17)
- Раздел **Gate results** — STYLEGUIDE GATE ✅, Onboarding 8 MOCKUP GATE ✅, DS Complete Gate ⬜

Параллельный sprint-02.5.md (Track B CBSHOME + Track C docs translation) — отдельный standalone sprint, читай его если работаешь над Track B или C.

### 5. Прочитай локальные INDEX-ы по своему скоупу

| Скоуп задачи | Local INDEX |
|---|---|
| Mockups (Phase 4) | `D:\02_Projects\velo\docs\03_mockups\INDEX.md` |
| Design System (Phase 2-3, promotion passes) | `D:\02_Projects\velo\docs\02_design-system\INDEX.md` |
| **DS Components master (mandatory before naming new CSS class)** | `D:\02_Projects\velo\docs\02_design-system\COMPONENTS-CATALOG.md` |
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

**Активный спринт:** Sprint 2 (EXPANDED, in-progress). Файл: `05_roadmap/sprint-02.md`.

**Текущая фаза:** Macro-Phase I — DS Harvest (Phase A + B for each remaining block).
NO mockups until all 10 blocks are DS-complete.

### Что уже сделано

| Block | DS-complete | Mockup |
|---|---|---|
| Onboarding 8 | ✅ (Sprint 2 Phase 4) | ✅ MOCKUP GATE passed 2026-05-18 |
| Dashboard 9 | ✅ (2026-05-18 session) | ✅ viewer built, ready for MOCKUP GATE |

### Entry point для следующей сессии (DS Harvest чат)

**Первая задача:** Calendar 11 DS harvest (Phase A + B).
Figma SACRED root: `541:1553`, 11 frames.

**Phase A — Harvest:**
1. `use_figma` Plugin API. File key `F7PD5isLfLdyc0q1Bd5n5c`. Walk all 11 Calendar frames depth-deep.
2. Sample exact tokens per element: fills (RGB + alpha), strokes, cornerRadius, effects, typography.
3. Export all icon GROUP nodes as SVG via `exportAsync({format:'SVG'})`.
4. Document gaps vs current `variables.css` + `COMPONENTS-CATALOG.md`.

**Phase B — Promote 5 deliverables (all mandatory):**
1. Tokens → `02_design-system/tokens/variables.css` master + deliverable (MD5-mirror!)
2. SVGs → `02_design-system/assets/icons/`
3. `02_design-system/assets/ASSETS-INDEX.md` — add lines with Figma node provenance
4. `02_design-system/COMPONENTS-CATALOG.md` — full per-component profile entries
5. **`02_design-system/styleguide/velo-design-system.html`** — visualise in Tokens/Components/Patterns tabs. Without this, block is NOT DS-complete.

**Then repeat for remaining blocks in order:**
Profile 7 → Diary 20 → Messages 3 → Analytics 3 → Practices 15 → Master Dashboard 8 → Master Onboarding 13.

After ALL 10 blocks DS-complete → operator validates DS COMPLETE GATE → then start Macro-Phase II (mockups).

### Anti-patterns (mandatory — never do these)

- ❌ **AP-P-6** — no reverse-engineering from PNG screenshots. PNG = side-by-side validation only, not extraction source.
- ❌ **AP-P-7** — no token added to `variables.css` without simultaneous visualisation in `velo-design-system.html`.
- ❌ **AP-M-6** — no monolithic inline CSS in mockup files. All tokens/shell/components go in `03_mockups/_shared/` (§7.3). Mockup `<style>` = screen-specific rules only.
- ❌ No new CSS class names without `Grep` in `COMPONENTS-CATALOG.md` first (Before-naming check).
- ❌ No mockups during Macro-Phase I — not until DS COMPLETE GATE passes.

### Parallel Sprint 2.5 (separate chat, Claude Code)

Sprint 2.5 (standalone) runs in parallel with Sprint 2:
- Track B: CBSHOME foundation transfer (`06_project-inputs/CBSHOME-PATTERNS-FOR-VELO.md`, Claude Code)
- Track C: Documentation English translation pass (Conv-1..Conv-4)

Neither track blocks Sprint 2 DS harvest work.

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

### Before-naming check (mandatory)
**Перед тем как изобрести новый CSS-класс** в любом mockup — открой `02_design-system/COMPONENTS-CATALOG.md` и `Grep` по визуальной функции ("badge", "card", "alert", "input", "button"). Если canonical entry существует — используй то имя и варианты. Если нет — добавь `## NEW candidate` в конец каталога в том же edit-проходе. Без этой сверки сессии плодят дубли (`.status-badge` вместо VBadge, `.reservation-row` вместо BookingCard и т.д.) — два месяца спустя никто не знает где правда.

### Block-Harvest-First rule (mandatory for SACRED blocks) — Methodology §7.0 v1.3
**Перед сборкой mockup'ов любого SACRED-блока** (Onboarding 8, Dashboard 9, Calendar 11, Profile 7, Diary 20, Messages 3, Analytics 3, Practices 15, Master Dashboard 8, Master Onboarding 13):

**Phase A — Harvest:** `use_figma` Plugin API walk all frames блока. Sample tokens (fills + strokes + radii + effects + typography) per element. Export icon SVGs via `exportAsync`.

**Phase B — Promote 5 deliverables (все обязательны):**
1. Tokens → `02_design-system/tokens/variables.css` master + deliverable (MD5-mirror)
2. SVG assets → `02_design-system/assets/icons/`
3. `02_design-system/assets/ASSETS-INDEX.md` entries с Figma provenance
4. `02_design-system/COMPONENTS-CATALOG.md` entries (full profile)
5. **`02_design-system/styleguide/velo-design-system.html` visualisation** (Tokens / Components / Patterns tabs)

Блок «DS-complete» только когда все 5 done. Mockup work для блока **заблокирован** до этого.

**Phase C — Mockup rebuild** только после DS-complete. Mockup = валидация DS coverage. Если mockup'у не хватает чего-то → это DS gap, не mockup gap. Закрывать в DS first.

**Когда правило НЕ применять:**
- Admin role (нет Figma SACRED — Sprint 7 строит from scratch на DS tokens + legacy HTML reference)
- Net-new компоненты которых нет в Figma (mockup is first instance; DS-promote после operator MOCKUP GATE)
- Polish iterations после MOCKUP GATE (нет нужды re-harvest если visual approved)

### DS Visualisation rule (mandatory) — Methodology §6.8 v1.3
**Каждый promote в `variables.css`** (новый token / component / pattern) ОБЯЗАН быть visualised в `velo-design-system.html` в том же edit pass. Token "exists in DS" только когда **оба** true:
1. Declared в `02_design-system/tokens/variables.css` master + deliverable (MD5-mirror)
2. Visualised в relevant tab `02_design-system/styleguide/velo-design-system.html`

Без (2) — token "promoted to file" но **НЕ в DS**. Это главная причина drift в Sprint 2 Phase 4: добавление tokens в `variables.css` без styleguide → следующие сессии не знают что добавлено → изобретают заново.

### Why both rules exist (учили на boli в Sprint 2 Phase 4)
SACRED frames в Figma = правда. PNG-эталоны = рендер той правды. `velo-design-system.html` = визуальный мастер DS, единый источник видимости. Сession-by-session плодим дубли и тратим 3× времени когда (a) reverse-engineering из PNG вместо Figma extraction, или (b) promote в `variables.css` без styleguide визуализации.

### English-default documentation rule (mandatory) — Methodology §1.1 P6 + §11.5 AP-P-8 v1.4
**All process docs are written in English.** This covers: methodology, roadmap, handoff, trackers (sprint-NN.md + INDEX files), `COMPONENTS-CATALOG.md`, CSS comments in `variables.css`. Russian narrative in process docs is anti-pattern AP-P-8 (~2× token cost on every read with no value gain).

**Russian is allowed ONLY in three categories (exception table):**

| Where Russian is allowed | Why |
|---|---|
| UI sample data in mockup HTML (`03_mockups/**/*.html`) + `velo-design-system.html` | Product UI is Russian by domain choice — methodology §7.6 no-Lorem-ipsum |
| Verbatim operator quotes in Daily logs (`«…»`) | Accuracy of operator instruction record |
| External source materials in `06_project-inputs/` | Inputs to the project, not products of its methodology |

Specialized proper nouns / project names — exempt as needed (no English equivalent).

**Conversion of legacy Russian → English** is scheduled work — Track C in Sprint 2.5 (ROADMAP §5.5.4). Do not do ad-hoc conversion outside Track C — partial conversion creates churn when Track C re-touches the same file. The exception is **new content added in the current session**: write it in English from the start so the new content doesn't add to Track C's backlog.

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

**Дополнительно** — если меняется entry point, текущий sprint, или роли исполнителя/оператора, обнови блок «ПРОМПТ ДЛЯ ЗАПУСКА НОВОЙ СЕССИИ» в начале этого `_HANDOFF.md`. Промпт должен оставаться валидным для прямого копирования в новый чат без правок. (Версии методологии/roadmap резолвятся через `INDEX.md` — promot их не упоминает, поэтому version bump промпт **не** трогает.)

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
[_HANDOFF.md | v1.6 | 2026-05-18]
Universal entry-point prompt. State lives in INDEX.md + sprint-NN.md + local INDEXes.
Self-contained: startup prompt block at top of file — copy-paste into new chat, no external snippets needed.
Read sequence: INDEX → methodology (version in INDEX) → roadmap (version in INDEX) → sprint-NN → local INDEX → continue from first pending task.
Current entry point (2026-05-18): Sprint 2 (EXPANDED, in-progress) — Macro-Phase I DS harvest all blocks.
Active sprint file: 05_roadmap/sprint-02.md (REOPENED and expanded 2026-05-18).
Completed blocks (DS-complete): Onboarding 8 ✅, Dashboard 9 ✅, Calendar 11 ✅.
Next task: Profile 7 DS harvest (Phase A + B).
Macro-Phase I remaining blocks: Profile 7 → Diary 20 → Messages 3 → Analytics 3 → Practices 15 → Master Dashboard 8 → Master Onboarding 13.
Macro-Phase II (all mockups) starts ONLY after DS COMPLETE GATE passes.
Parallel Sprint 2.5 (standalone): Track B CBSHOME transfer (Claude Code) + Track C docs translation.
Methodology v1.5 rules active: Before-naming check (catalog) · Block-Harvest-First §7.0 · DS Visualisation §6.8 · English-default P6 · AP-P-6 PNG reverse-engineering · AP-P-7 variables.css without styleguide · AP-P-8 Russian narrative in process docs · AP-M-6 monolithic inline CSS in mockups.
v1.5 _HANDOFF changes: Entry point switched from sprint-02.5.md → sprint-02.md (Sprint 2 reopened + expanded). "ЧТО ДЕЛАТЬ ДАЛЬШЕ" rewritten to reflect Macro-Phase I/II structure. Startup prompt gains sprint status line.
v1.6 _HANDOFF changes (2026-05-18): AP-M-6 added (monolithic inline CSS anti-pattern). Methodology ref bumped to v1.5. Completed blocks updated: Calendar 11 DS-complete.
Location: D:\02_Projects\velo\docs\_HANDOFF.md
```
