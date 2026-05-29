# Code Review: VELO — полный аудит обновлений (origin/main vs 2f17518)
**Language/Framework:** Python 3.12 / FastAPI / SQLAlchemy 2.0 async / Pydantic v2 / Vue 3.5 / TypeScript / Pinia / Telegram Mini App SDK  
**Reviewed:** 2026-05-29  
**Scope:** 153 коммита на origin/main с момента последнего аудита (2f17518). Ключевые изменения: профиль пользователя (экраны A–F), таксономия практик v2 (10 направлений, direction-conditional styles), фикс logout→re-login (удаление anti-replay), рефактор CalendarFilterModal (style multi-select), новые иконки и DS-компоненты.

---

## Section 1 — General Overview

Cерьёзная итерация: добавлен полноценный профиль пользователя с 5 экранами (просмотр, редактирование, уведомления, язык/тайм-зона, удаление аккаунта), переработана таксономия практик (10 направлений, стили теперь direction-conditional), закрыт критический баг logout→re-login. Архитектура остаётся чистой: JSONB sandbox pattern соблюдён для phone/bio/notifications, валидаторы config-driven (NO-LITERALS), Pydantic v2 field_validator / computed_field / model_validator использованы корректно.

Выявлена одна дыра в слое сервиса (перекрёстная валидация style↔direction при PATCH без direction) и семантическое несоответствие между текстом UI-модала удаления и реальным поведением бэкенда. Остальные находки — рекомендации.

**Итоговая оценка: 7/10**

---

## Section 2 — Critical Bugs and Logic Errors

No issues found.

---

## Section 3 — Error Handling

No issues found.

---

## Section 4 — Security and Vulnerabilities

🟡 WARNING — W-3: Удаление anti-replay открывает окно повторного использования initData  
Location: `backend/app/modules/auth/service.py` строки 168–183 (комментарий к удалённому коду)

Баг logout→re-login был правильно диагностирован и исправлен: anti-replay ключ `init_data_used:{sha256}` удалён, добавлен подробный комментарий с объяснением почему. Это **корректное** решение.

Тем не менее, теперь злоумышленник, перехвативший действующий initData (MITM в незащищённой сети), может использовать его несколько раз в течение 5-минутного окна TTL. Единственная защита — rate limiter (5 req / 60s per telegram_id), который ограничивает частоту, но не запрещает повторное использование как таковое. В Telegram-контексте это приемлемый компромисс (протокол зашифрован, HTTPS обязателен), однако факт должен быть задокументирован.

```python
# Нынешнее состояние (сервис):
# 1. validate_telegram_init_data() — HMAC + auth_date TTL (5 мин)
# 2. check_auth_rate_limit() — 5 req / 60s per telegram_id
# (anti-replay удалён намеренно)

# Суть оставшегося риска:
# Перехваченный initData можно использовать до 5 раз за 60 секунд
# в течение 5 минут действия auth_date.
# Вектор атаки: MITM + перехват инициальной передачи initData.
# Вероятность: крайне мала (HTTPS + Telegram encrypted transport).
# Документировать в threat model, не требует кода.
```

**Рекомендация:** внести в документ threat model; при появлении server-side пуш-нотификаций или критичных операций рассмотреть device fingerprint как дополнительный слой.

---

## Section 5 — Performance

No issues found.

---

## Section 6 — Code Quality and Best Practices

🟡 WARNING — W-2: DELETE /users/me — текст подтверждения противоречит реальному поведению  
Location: `frontend/src/views/user/EditProfileView.vue` строка 56

```html
<!-- ТЕКУЩЕЕ (в модале подтверждения) -->
<p class="edit-profile__modal-text">
  Вы уверены? После удаления восстановить аккаунт будет уже невозможно.
</p>
```

**Реальное поведение:** `DELETE /api/v1/users/me` → `reset_user_to_onboarding()` — сбрасывает только `onboarding_completed = False`. Данные (имя, телефон, бронирования, телеграм-профиль) **сохраняются**. При следующем логине пользователь видит онбординг, но всё его старое содержимое на месте. Фраза «восстановить будет невозможно» — ложная.

Это создаёт юридический и UX-риск: пользователь соглашается с одним поведением, а получает другое.

```html
<!-- ПОСЛЕ: честный текст для MVP -->
<p class="edit-profile__modal-text">
  Сбросить аккаунт? Вы пройдёте настройку заново.
  Ваши данные и бронирования сохранятся.
</p>
```

Когда реальное удаление будет реализовано — поменять текст обратно на жёсткий. Код бэкенда уже подготовлен к этому: комментарий «FUTURE: real deletion ... change THIS function body only».

---

## Section 7 — Testability

🟡 WARNING — W-1: `update_practice` не ре-валидирует style против сохранённого direction при PATCH без direction  
Location: `backend/app/modules/practices/service.py` `update_practice()`, строки 515–583

**Суть бага:**

При PATCH `{"style": "silence"}` на практику с `direction="yoga"`:

1. **Pydantic-валидатор** `_check_style_vs_direction` в `UpdatePracticeRequest` получает `direction=None` (не прислан). Переходит к flat-union проверке: `"silence"` есть в flat_allowed_styles (он там через meditation). **Проходит**.

2. **Сервис** загружает практику (хранится `direction="yoga"`), строит `taxonomy_updates = {"style": "silence"}`, мёрджит в `data.taxonomy`:
   ```
   {"direction": "yoga", "difficulty": "beginner", "style": "silence"}
   ```
   Это невалидное состояние: `yoga` принимает `["nidra", "yin", "hatha", "vinyasa", "kundalini", "ashtanga"]`, но не `"silence"`.

3. Аналогично для `direction="breathwork"` (вообще не допускает style): `PATCH {"style": "hatha"}` запишет `{"direction": "breathwork", ..., "style": "hatha"}`.

```python
# ТЕКУЩИЙ КОД (service.py — update_practice, без кросс-валидации):
taxonomy_updates = {
    field: update_data.pop(field)
    for field in _TAXONOMY_FIELDS
    if field in update_data
}
# ... (нет перекрёстной проверки style vs stored direction)
if taxonomy_updates:
    data = copy.deepcopy(practice.data) if practice.data else {}
    taxonomy = data.get("taxonomy", {})
    taxonomy.update(taxonomy_updates)   # ← невалидное состояние если style ≠ stored direction
    data["taxonomy"] = taxonomy
    practice.set_jsonb("data", data)

# ИСПРАВЛЕНИЕ (добавить ПЕРЕД применением taxonomy_updates):
from app.modules.practices.schemas import _validate_style_for_direction

if taxonomy_updates:
    # Если style обновляется без direction — проверить против сохранённого direction.
    if "style" in taxonomy_updates and "direction" not in taxonomy_updates:
        stored_taxonomy = (practice.data or {}).get("taxonomy", {})
        stored_direction = stored_taxonomy.get("direction")
        try:
            _validate_style_for_direction(stored_direction, taxonomy_updates["style"])
        except ValueError as e:
            raise BadRequestError(str(e)) from e

    data = copy.deepcopy(practice.data) if practice.data else {}
    taxonomy = data.get("taxonomy", {})
    taxonomy.update(taxonomy_updates)
    data["taxonomy"] = taxonomy
    practice.set_jsonb("data", data)
```

**Почему это WARNING а не CRITICAL:** бэкенд не падает, данные не теряются, это data integrity issue (невалидная таксономия в JSONB), не security. Но фронт может показать неправильные иконки/фильтры.

---

## Section 8 — Refactoring Recommendations

No issues found.

---

## Section 9 — Minor Improvements and Polish

🟢 SUGGESTION — S-1: `form.bio` отправляется без `.trim()` в EditProfileView  
Location: `frontend/src/views/user/EditProfileView.vue` строка 212

`form.phone` перед сравнением и отправкой тримируется (`form.phone.trim()`). `form.bio` — нет. Небольшая непоследовательность; лишние пробелы в начале/конце bio запишутся в JSONB.

```ts
// ТЕКУЩЕЕ:
if (form.bio !== (user.value?.bio ?? '')) {
  body.bio = form.bio
}

// ПОСЛЕ (для текстовых полей достаточно trimEnd):
if (form.bio.trimEnd() !== (user.value?.bio ?? '')) {
  body.bio = form.bio.trimEnd()
}
```

---

🟢 SUGGESTION — S-2: Обработчик `onSelectLanguage` — no-op при единственном варианте  
Location: `frontend/src/views/user/LanguageTimezoneView.vue` строка 151

```ts
// ТЕКУЩЕЕ:
function onSelectLanguage(value: string): void {
  // Single option for now -- nothing to switch to, nothing to persist.
  selectedLanguage.value = value   // state обновляется, но...
}
```

Нажатие на «Русский» обновляет локальный `selectedLanguage`, но сеть не вызывается. При единственном варианте это корректно. Однако кнопка имеет `cursor: pointer` и выглядит кликабельной. Рекомендуется добавить `:disabled="true"` (или убрать cursor pointer) пока вариантов больше одного нет, чтобы избежать пустого взаимодействия.

---

🟢 SUGGESTION — S-3: `hours_attended` — banker's rounding может давать неожиданный результат  
Location: `backend/app/modules/bookings/service.py` `get_user_practice_stats()`

```python
hours_attended = round(int(total_minutes) / 60, 1)
```

Python `round()` использует banker's rounding (к чётному). `round(0.25, 1)` → `0.2`, `round(0.35, 1)` → `0.4`. Для статистики профиля это не критично, но если позднее появится финансовый расчёт — заменить на `Decimal`.

---

## Section 10 — AI-Generated Code Patterns

🟢 SUGGESTION — S-4: Prompt residue в `delete_me` роутере  
Location: `backend/app/modules/users/router.py` строка 45

```python
"""Delete the authenticated user's account.

MVP SEMANTICS (see reset_user_to_onboarding): this does NOT erase data or
deactivate the account. It resets the onboarding flag so the next login
sends the user through the welcome flow again, with their old data intact.
The endpoint contract ("DELETE my account") is kept so that real deletion
can later be implemented by changing only the service body.
```

Докстринг откровенно описывает несоответствие между именем эндпоинта и реализацией. Сам по себе это не баг кода, но вместе с вводящим пользователя в заблуждение текстом модала (W-2) формирует системный UX-долг. Паттерн 10.14 (specification drift): endpoint реализует «близкое» поведение, а не заявленное.

---

## Section 11 — Cross-Module Consistency

🟢 SUGGESTION — S-5: `_validate_style_for_direction` используется в schemas, но не в service  
Location: `backend/app/modules/practices/schemas.py` vs `backend/app/modules/practices/service.py`

В schemas она вызывается из `model_validator(mode="after")` обоих реквестов. В service — не импортируется и не вызывается при мёрдже. Функция есть (и экспортируется — она использована в router через `_flat_allowed_styles`), но на service-слое отсутствует повторная валидация. Это источник W-1.

После применения фикса из W-1 непоследовательность устранится.

---

## Section 12 — Test Quality Audit

🟡 WARNING — W-4: Отсутствует тест на PATCH style без direction с невалидным cross-direction сочетанием  
Location: `backend/tests/test_practices.py`

Файл тестов хорошо покрывает: сохранение таксономии при create, мёрдж при PATCH (direction/style/difficulty отдельно), multiselect фильтры. Но нет теста, который проверяет что `PATCH {"style": "silence"}` на `direction="yoga"` — отклоняется.

```python
# ДОБАВИТЬ в test_practices.py:
async def test_update_style_rejected_for_wrong_direction(
    client: AsyncClient, master_auth: dict,
) -> None:
    """PATCH style that is not valid for the stored direction → 400."""
    # Create yoga practice
    base_body = {**PRACTICE_BASE, "direction": "yoga", "difficulty": "beginner"}
    create_resp = await client.post(PRACTICES_URL, headers=master_auth, json=base_body)
    practice_id = create_resp.json()["id"]

    # Try setting a meditation-only style on a yoga practice
    patch_resp = await client.patch(
        f"{PRACTICES_URL}/{practice_id}",
        headers=master_auth,
        json={"style": "silence"},  # silence belongs to meditation, not yoga
    )
    assert patch_resp.status_code == 400
```

---

## Section 13 — Orphan Source Files

Проверены новые файлы в `frontend/src/views/user/` и `frontend/src/components/`:

- `UserProfileView.vue` — зарегистрирован в router, используется → OK  
- `EditProfileView.vue` — зарегистрирован, используется → OK  
- `NotificationsView.vue` — зарегистрирован, используется → OK  
- `LanguageTimezoneView.vue` — зарегистрирован, используется → OK  
- `VSwitch.vue` — экспортируется через `ui/index.ts`, используется в NotificationsView → OK  
- `IconArrowRight.vue`, `IconBell.vue`, `IconGlobe.vue` и прочие иконки — экспортируются через `icons/index.ts` → OK

Orphan-файлов не обнаружено.

---

## Final Score Block

---

Final Score: 7/10

🔴 CRITICAL — нет

🟡 WARNING — рекомендуется исправить:
- W-1: `update_practice` не ре-валидирует style против хранимого direction при PATCH без direction → невалидная таксономия в БД (`practices/service.py`)
- W-2: Текст модала «восстановить будет невозможно» — ложный; бэкенд лишь сбрасывает onboarding (`EditProfileView.vue`)
- W-3: Удаление anti-replay оставляет 5-минутное окно повторного использования перехваченного initData — приемлемый компромисс, требует документирования в threat model
- W-4: Отсутствует тест PATCH style с cross-direction конфликтом (`test_practices.py`)

🟢 SUGGESTION — желательно:
- S-1: `form.bio` отправляется без `.trimEnd()` (`EditProfileView.vue`)
- S-2: Кнопка «Русский» выглядит интерактивной при единственном варианте (`LanguageTimezoneView.vue`)
- S-3: `round()` с banker's rounding для `hours_attended` — безвреден для stats, заменить на `Decimal` если пойдёт в финансовые расчёты
- S-4: Specification drift: `DELETE /users/me` реализует не то что обещает — задокументировано в роутере, но создаёт UX-долг вместе с W-2
- S-5: `_validate_style_for_direction` не вызывается в service (источник W-1)

---

## Totals Table

| Severity | Count |
|----------|-------|
| 🔴 CRITICAL | 0 |
| 🟡 WARNING | 4 |
| 🟢 SUGGESTION | 5 |
| 💎 DIAMOND | 0 |
| **Total** | **9** |

---

## Что сделано хорошо (не требует изменений)

- **Фикс logout→re-login**: anti-replay удалён правильно, с чётким объяснением в комментарии
- **JSONB sandbox** для phone/bio/notifications: copy + set_jsonb() + flag_modified — шаблон соблюдён повсюду
- **Notifications: partial merge** — только изменённые ключи слились, остальные сохранились
- **Taxonomy v2**: direction-conditional styles централизованы в config + `_validate_style_for_direction`, NO-LITERALS соблюдён
- **TD-029**: общая сессия для get_current_user_write и endpoint — merge() убран корректно
- **Profile stats**: `get_user_practice_stats` — единственный ORM-запрос с COUNT + SUM + COALESCE, эффективно
- **useAuth composable**: `isLoggingOut` гейт предотвращает мигание StandaloneStubView при logout в Telegram
- **Deep link**: `pendingDeepLink` паттерн (parseStartParam → `open_practice__{uuid}`) чистый
- **Test coverage**: test_users.py покрывает phone/bio/notifications/onboarding/relogin — хороший набор regression-тестов
