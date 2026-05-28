# VELO — Таксономия практик (frontend)

> Единая модель направлений и стилей практик на фронте. Источник правды
> для типов, иконок, плейсхолдеров, фильтра и форм мастера. Обновлено
> 2026-05-28 — раскладка согласована оператором.

## 1. Direction × Style — финальный список

10 направлений. Стили есть только у трёх (meditation / yoga / circles).
У остальных семи направлений стилей нет (фильтр и форма мастера это учитывают).

| # | Direction (ключ)  | Label (RU)             | Иконка                  | Стили (style.value → label)                                                                                                                                                                                          |
| - | ----------------- | ---------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | `meditation`      | Медитация              | `IconMeditation.vue`    | `silence` — Медитация молчания · `presence` — Медитация присутствия · `sound` — Звуковая медитация · `taoist` — Даосская медитация                                                                                   |
| 2 | `yoga`            | Йога                   | `IconYoga.vue`          | `nidra` — Йога-нидра · `yin` — Инь-йога · `hatha` — Хатха-йога · `vinyasa` — Виньяса · `kundalini` — Кундалини-йога · `ashtanga` — Аштанга-йога                                                                       |
| 3 | `breathwork`      | Дыхательные практики   | `IconBreathwork.vue`    | —                                                                                                                                                                                                                    |
| 4 | `somatic`         | Соматика               | `IconSomatic.vue`       | —                                                                                                                                                                                                                    |
| 5 | `tantra`          | Тантра                 | `IconTantra.vue`        | —                                                                                                                                                                                                                    |
| 6 | `circles`         | Круги                  | `IconCircles.vue`       | `womens` — Женский круг · `mens` — Мужской круг · `sharing` — Круг шеринга                                                                                                                                           |
| 7 | `sound_healing`   | Саундхиллинг           | `IconSoundHealing.vue`  | —                                                                                                                                                                                                                    |
| 8 | `art`             | Арт-практики           | `IconArt.vue`           | —                                                                                                                                                                                                                    |
| 9 | `narrative`       | Нарративные практики   | `IconNarrative.vue`     | —                                                                                                                                                                                                                    |
|10 | `movement`        | Движение               | `IconMovement.vue`      | —                                                                                                                                                                                                                    |

## 2. Где это живёт в коде

- Литеральный юнион ключей — [`frontend/src/api/types.ts`](../../frontend/src/api/types.ts) (`PracticeDirection`). **Hand-maintained**, держать в синхроне с backend `practice_allowed_directions`.
- Лейблы и карта direction → иконка — [`frontend/src/utils/displayHelpers.ts`](../../frontend/src/utils/displayHelpers.ts) (`DIRECTION_LABEL`, `DIRECTION_ICON`).
- Form options — [`frontend/src/utils/practiceOptions.ts`](../../frontend/src/utils/practiceOptions.ts) (`DIRECTION_OPTIONS`, `STYLE_OPTIONS_BY_DIRECTION`, хелперы `stylesForDirection`, `directionHasStyles`).
- Иконки — `frontend/src/components/icons/Icon{Meditation,Yoga,Breathwork,Somatic,Tantra,Circles,SoundHealing,Art,Narrative,Movement}.vue`. Все используют `currentColor` (наследуют цвет от родителя), есть проп `size`.
- Шарный плейсхолдер видео-зоны — [`frontend/src/components/shared/PracticePlaceholder.vue`](../../frontend/src/components/shared/PracticePlaceholder.vue), 336×199 glass-blue + центрированная белая иконка через `practiceIconFor()`.
- Hero — [`PracticeHeroCard.vue`](../../frontend/src/components/shared/PracticeHeroCard.vue) подбирает иконку из `DIRECTION_ICON` или fallback.
- Карточка списка — [`PracticeListCard.vue`](../../frontend/src/components/shared/PracticeListCard.vue) использует тот же `practiceIconFor()`.

## 3. UX-правила

- **Фильтр (Calendar):** Направление = **single-select** (chips, плюс «Все»). «Вид практики» (style dropdown) показывается ТОЛЬКО когда выбрано ровно одно направление со стилями (meditation / yoga / circles). При смене направления style сбрасывается.
- **Форма мастера (Create/Edit):** Style — `VSelect`, динамические опции. Если у выбранного direction стилей нет — селектор скрыт. При смене direction style сбрасывается.
- **Плейсхолдер видео:** на `PracticeLiveView` вместо fake-блока с текстом «video» рендерится `<PracticePlaceholder :direction>` — белая иконка направления в glass-blue боксе 336×199.

## 4. Связанные задачи

- **B-2 (backend, открыта 2026-05-28):** расширить `practice_allowed_directions` до 10 значений, ввести direction-conditional `practice_allowed_styles`, миграция данных:
  - `direction='womens_circle'` → `direction='circles'`, `style='womens'`
  - `direction='mens_circle'`   → `direction='circles'`, `style='mens'`
  - `direction='kundalini'`     → `direction='yoga'`,    `style='kundalini'`
  Фронт-код уже готов и ждёт деплоя бэка — коммит фронта НЕ пушится до того, как бэк уехал. См. `frontend_session_kickoff.md` §9.
- **B-1 (backend, открыта 2026-05-28):** добавить `direction` в `PracticeSummary`. После релиза удалить title-эвристику в `practiceIconFor`.
- **F-1 (frontend, ЗАКРЫТА 2026-05-28):** полный набор иконок направлений — этот документ закрывает её.

## 5. Истоки

- Иконки экспортированы оператором из Figma как единый SVG `icon_practics.svg` (10 иконок в сетке 4-4-2), извлечены и нормализованы скриптом `.tmp/extract_assets.py` + `.tmp/gen_vue_icons.py`.
- Плейсхолдеры — оригинальный `plase_holder.svg` (1 hero + 10 grid). В коде сейчас используется реконструкция (icon + glass-blue фон) без переноса исходного SVG-pattern'а; при необходимости тематического фонового pattern'а — extract'ить из `plase_holder.svg`.
- Раскладка иконка ↔ направление сверена оператором (скриншот Figma с подписями, 2026-05-28).
