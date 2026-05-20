# Повторная проверка онбординга — fd13830

**Дата:** 2026-05-20  
**Коммит:** `fd13830` fix(onboarding): address review — guard double-click, null flag, NULL-merge  
**Базовый коммит:** `7475b0c` feat(onboarding): add welcome + onboarding flow for new users  
**Файлы в диффе:** 5  

---

## Итог

Все четыре замечания из предыдущей проверки устранены корректно. Новых критических проблем и предупреждений не выявлено. Одно незначительное замечание.

---

## Проверка по пунктам

### ✅ CRITICAL — Двойной клик пропускает экран часового пояса

`frontend/src/views/auth/OnboardingView.vue`

Реализован через два флага: `advancing` и `finishArmed`.

**Механизм:**
- `advancing` блокирует повторный вход в `onPrimaryAction` на интро-шагах пока выполняется переход.
- `finishArmed` взводится только после того, как переход на шаг таймзоны осел в микрозаданиях (`await Promise.resolve()`). Клик, опередивший это ожидание, находит `finishArmed=false` и игнорируется; намеренное нажатие после завершения перехода — `finishArmed=true` и вызывает `finish()`.
- `goToTimezoneStep()` («Пропустить») также переведён на `void enterTimezoneStep()`, то есть защищён тем же механизмом.

Реализация корректна и охватывает все пути перехода:
- шаги 0→1, 1→2: синхронные, без await, гонка невозможна в принципе.
- шаг 2→3 (к таймзоне): асинхронный через `enterTimezoneStep()`, защищён двойным барьером.

**Статус: устранено.**

---

### ✅ WARNING — `onboarding_completed: null` записывался в JSONB

`backend/app/modules/users/service.py`

Добавлено условие `and value is not None` в comprehension при формировании `jsonb_updates`. Значение `None` больше не попадает в `set_jsonb()` и не записывается в базу.

**Статус: устранено.**

---

### ✅ WARNING — JSONB-мёрж без COALESCE (`NULL || json = NULL`)

`backend/app/modules/auth/service.py`

Выражение заменено:

```python
# было
"credentials": User.credentials.op("||")(credentials),

# стало
"credentials": func.coalesce(
    User.credentials, text("'{}'::jsonb")
).op("||")(credentials),
```

`text("'{}'::jsonb")` — типизированный литерал PostgreSQL, гарантирует правильный тип для `COALESCE`. Поведение при `NULL`-столбце теперь эквивалентно `{} || fresh`, то есть возвращает `fresh` без потерь.

**Статус: устранено.**

---

### ✅ WARNING — Отсутствовал тест инварианта «логин сохраняет флаг»

`backend/tests/test_users.py` — добавлены 5 новых тестов:

| Тест | Что проверяет |
|------|--------------|
| `test_onboarding_completed_defaults_false_for_new_user` | Новый пользователь → `false` |
| `test_onboarding_completed_can_be_set_true` | `PATCH true` сохраняется и возвращается |
| `test_onboarding_completed_survives_relogin` | **Ключевой инвариант:** повторный логин не сбрасывает флаг |
| `test_onboarding_completed_relogin_refreshes_telegram_fields` | Мёрж: флаг сохранён + Telegram-поля обновлены |
| `test_onboarding_completed_null_does_not_reset_flag` | `PATCH null` игнорируется, не стирает `true` |

Покрытие полное: все четыре сценария из замечаний плюс регрессионный тест Telegram-полей.

**Статус: устранено.**

---

## Прочее (попутно)

### ☑ Переименование `credentials_raw` → `credentials_in`

`backend/app/modules/users/schemas.py`

Не связано с замечаниями, но улучшает читаемость: `credentials_in` точнее передаёт семантику (input-only поле, не выводится в ответ). Изменение безопасное — имя поля внешне не видно (excluded + internal).

---

## Предложение (1)

### SUGGESTION — `advancing` не сбрасывается в `finally`

`frontend/src/views/auth/OnboardingView.vue`, функция `onPrimaryAction`

```typescript
// текущий код
advancing.value = true
const next = Math.min(step.value + 1, TIMEZONE_STEP_INDEX)
if (next === TIMEZONE_STEP_INDEX) {
  await enterTimezoneStep()   // <-- если бросит исключение (нереально, но…)
} else {
  step.value = next
}
advancing.value = false       // не выполнится при исключении
```

`enterTimezoneStep` выполняет только синхронные присвоения и `await Promise.resolve()` — бросить исключение не может на практике. Тем не менее канонически безопаснее обернуть в `try/finally`:

```typescript
advancing.value = true
try {
  const next = Math.min(step.value + 1, TIMEZONE_STEP_INDEX)
  if (next === TIMEZONE_STEP_INDEX) {
    await enterTimezoneStep()
  } else {
    step.value = next
  }
} finally {
  advancing.value = false
}
```

Риск: низкий (практически нулевой). Рекомендация: желательно, не обязательно.

---

## Вывод

Фиксы качественные, механизм защиты от двойного клика хорошо задокументирован комментариями прямо в коде. Тесты покрывают все заявленные сценарии. Ветка готова к мёржу с точки зрения онбординг-потока.
