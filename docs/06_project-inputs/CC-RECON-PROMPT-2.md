# CC Recon Prompt #2 — Validation Pass for v1.0 Methodology

> **Назначение этого промпта.** Дать Claude Code запрос на свежую разведку
> проекта, чтобы проверить, что `VELO-METHODOLOGY.md` v1.0 и
> `ROADMAP.md` v1.0 согласованы с текущей реальностью кода и контракта.
>
> **Предыдущий отчёт:** `06_project-inputs/CC-REPORT.txt` (готовился перед
> написанием HANDOFF-методологии). Был использован как один из источников
> при сборке v1.0 методологии. Сейчас мне (Чату-архитектору) нужна
> **delta**: что изменилось с того момента + ответы на вопросы, которые
> возникли при валидации v1.0.
>
> **Куда положить ответ:** `D:\02_Projects\velo\docs\06_project-inputs\CC-REPORT-2.txt`
> в том же текстовом формате, что и оригинальный CC-REPORT.txt (Q/A
> блоки, прямые цитаты файлов, источник в каждом A).

---

## Контекст для CC

1. **С 2026-05-17** в проекте принята **унифицированная методология**
   `D:\02_Projects\velo\docs\04_methodology\VELO-METHODOLOGY.md` v1.0 и
   **роадмап** `D:\02_Projects\velo\docs\05_roadmap\ROADMAP.md` v1.0.
   Они заменяют три универсальные методологии (DS, LIVEMOCKUP, HANDOFF)
   и старую DSYS Stage 0/1/2 модель.

2. **Папка `D:\02_Projects\DSYS\` устарела.** Её содержимое перенесено в
   `D:\02_Projects\velo\docs\` (через два архива и пересборку). Сейчас
   единственный канонический workspace — `D:\02_Projects\velo\docs\`.

3. **Цель этого отчёта** — подтвердить или опровергнуть, что v1.0
   методология/роадмап **корректно описывают реальный VELO** на уровне:
   - actual frontend code state (что изменилось с предыдущего отчёта)
   - API contract в `api-openapi.json`
   - ARCHITECTURE.md в `frontend/` (если он там как канон) и в
     `06_project-inputs/` (snapshot)

---

## Q-блоки — что ответить

### Q1. Дельта от предыдущего CC-REPORT.txt

Q1.1 — Появились ли новые файлы в `frontend/src/` с момента предыдущего
отчёта? Дай полный `find src -type f -name "*.ts" -o -name "*.vue" -o
-name "*.json" -o -name "*.css" | sort`. Сравни с тем что было в
БЛОК 1.1–1.11 CC-REPORT.txt.

Q1.2 — Изменился ли `package.json`? Список dependencies + scripts —
полностью.

Q1.3 — Изменился ли `frontend/src/router/index.ts`? Если да — содержимое
полностью.

Q1.4 — Стало ли что-то новое в `frontend/src/views/`, `stores/`,
`components/{ui,layout,shared}/`, `composables/`, `i18n/`? Полный листинг
каждой папки.

Q1.5 — `vue-tsc --noEmit` сейчас проходит? `npm run build` сейчас
проходит? Если нет — какие ошибки (полная output).

### Q2. Валидация инвариантов методологии (I1–I7) через api-openapi.json

Файл: `D:\02_Projects\velo\docs\06_project-inputs\api-openapi.json`
(копия backend OpenAPI 3.1.0, 64 paths). Также проверь
`frontend/src/api/generated.ts`, `frontend/src/api/types.ts`.

Q2.1 — **I1 cents.** Перечисли все response поля, оканчивающиеся на
`_cents`. Дай таблицу: `{ schema_name, field_name }`. Проверь что нет
ни одного денежного поля **без** суффикса `_cents` (например, `price`,
`amount`, `balance` без `_cents`).

Q2.2 — **I2 timezone.** В каких response shapes есть поле `timezone`?
Это IANA string? Особенно — в `PracticeResponse` (или как там
называется). Если поля нет — какова реальность: backend хранит timezone
per practice или нет?

Q2.3 — **I3 role.** Найди enum `UserRole`. Точные значения. Сверь с
методологией §2.5 I3: `'user' | 'master' | 'admin'`. Сходится?

Q2.4 — **I4 error format.** В components OpenAPI есть VeloError schema
(или похожая)? Какие у неё поля? Сходится с
`{ error: string, message: string }`?

Q2.5 — **I6 Waitlist FSM.** В OpenAPI и/или в `types.ts` найди enum
`WaitlistStatus` (или подобный). Точные значения. Сравни с двумя
вариантами:
- Методология §2.5 I6: `waiting → offered → confirmed | left | expired | declined`
- Предыдущий CC-REPORT.txt стр. 501: `waiting → notified → confirmed | left | expired | declined`

Какое из имён состояний реальное в API? Перечисли все 6 (или сколько
есть на самом деле) значений в порядке lifecycle.

Q2.6 — Другие enum'ы, которые методология упоминает в §6.6 Tier 2
(BookingStatus: pending/confirmed/cancelled/attended/no_show; PracticeType:
live/series/one_on_one/replay; MasterStatus: pending/verified/rejected;
PromoStatus: active/inactive; WithdrawalStatus: pending/approved/rejected;
PracticeStatus). Перечисли реальные значения каждого enum'а из API.
Подсвети расхождения с методологией.

### Q3. Endpoint coverage для ROADMAP скринов

В роадмапе перечислены ~120 скринов в Sprints 3–8. Я проверяю, что для
каждого скрина в OpenAPI есть нужный operationId.

Q3.1 — Перечисли все operationIds из `api-openapi.json` по тегам:
- `auth` (login, telegram, etc.)
- `users` (me, etc.)
- `practices` (CRUD + finalize + attendance)
- `bookings` (CRUD + waitlist)
- `payments` (topup)
- `masters` (apply, profile, payout, withdrawals)
- `admin` (stats, verify, reports, consistency)

Q3.2 — Для каждого user-блока скрина из ROADMAP §6.1 (user-dashboard,
user-practice-detail, user-bookings, user-calendar, user-profile,
user-waitlist, user-diary, user-topup, user-practice-buy-preview,
user-onboarding-welcome) — назови ожидаемые operationIds. Если такого
endpoint'a НЕТ в API — отметь явно.

Q3.3 — То же для master-блока (§8.1): master-dashboard, master-practices,
master-practice-create, master-practice-edit, master-analytics,
master-finance, master-profile, master-apply, master-pending,
master-practice-attendance.

Q3.4 — То же для admin-блока (§10.1): admin-dashboard, admin-masters,
admin-master-review, admin-reports, admin-report-resolve,
admin-withdrawals, admin-withdrawal-review, admin-consistency,
admin-users, admin-user-detail.

Q3.5 — Если в API есть operationIds **не покрытые** ROADMAP'ом скринами
— перечисли. Это потенциально пропущенные экраны.

### Q4. ARCHITECTURE.md vs методология

Файл: `D:\02_Projects\velo\docs\06_project-inputs\ARCHITECTURE.md`
(snapshot). Также `D:\02_Projects\velo\frontend\docs\ARCHITECTURE.md`
если там лежит канонический.

Q4.1 — Канонический ARCHITECTURE.md живёт в `frontend/docs/` или в
`frontend/` (root)? Какая версия актуальнее (по mtime/контенту)?

Q4.2 — Stack table в ARCHITECTURE.md §1 vs методология §2.2. Совпадает
ли поэлементно? Если различия — какие.

Q4.3 — В ARCHITECTURE.md есть anti-patterns или "запреты" (раздел про
"never use raw fetch()", "import V* only via barrel", "no hardcoded
Russian strings", и т.д.)? Перечисли. Сверь с методологией §11.6.
Подсвети любое противоречие.

Q4.4 — В ARCHITECTURE.md есть **правила про tokens**? Если да — какие.
Сверь с методологией §6.1–6.4 (two-layer, MISSING protocol). Совместимо?

Q4.5 — Какой раздел ARCHITECTURE.md описывает store layer (Pinia)?
Какие "правила" про сторы? Сверь с методологией §8 (Section 8 Store
Dependencies в spec template).

### Q5. Frontend state — критичные блокеры для Sprint 0/1

Q5.1 — `router/index.ts` импортирует несуществующие shells
(UserShell/MasterShell/AdminShell) — это всё ещё так? Какие views
вообще импортируются — список из import statements.

Q5.2 — `HomeView.vue` ссылается на токены, которых нет (`--font-body`,
`--text-2xl`, `--text-xs`, `--space-2`). Это всё ещё так? Полный список
undefined-токенов в каждом `.vue` / `.css` файле.

Q5.3 — `frontend/src/styles/global.css` ссылается на токены без
`variables.css`. Какие токены он использует. Что произойдёт после
переноса `variables.css` из v1.0 deliverable.

Q5.4 — `frontend/src/utils/format.ts` — захардкоженные русские строки
по-прежнему 8 штук? Дай актуальный список (line + string).

Q5.5 — `frontend/src/api/client.ts` — изменился ли? Какие методы
экспортирует? Какие callbacks (`onUnauthorized` и пр.)?

Q5.6 — `frontend/src/platform/` — изменился? Какие методы у Platform
interface? Сверь с методологией §2.5 I5 (`open_practice__{uuid}` через
`getStartParam`).

### Q6. Хорошее, что не надо ломать (баланс к §11 anti-patterns)

Q6.1 — Перечисли что в текущем `frontend/src/` стоит **сохранить
как есть** при выполнении Sprint 1+. Например: `api/client.ts`,
`utils/currency.ts`, `utils/format.ts` (для функций, не для строк),
`utils/constants.ts`, `platform/`, `tsconfig.json` settings.

Q6.2 — Есть ли тесты? `find src -name "*.test.ts" -o -name "*.spec.ts"`.
Что они покрывают.

Q6.3 — `.env.example` / `.env` — какие environment variables есть.
Что-то критичное для design pipeline?

### Q7. Экспертная позиция (как в прошлом отчёте)

Q7.1 — Если бы CC сегодня получил от Cowork финальный handoff package
(`01_deliverable/` со specs+tokens+icons+screens) и должен был сгенерить
первый экран по SCR-001 — какие вопросы у него остались бы открытыми?
Что в формате specs (методология §8.3) недостаточно конкретно?

Q7.2 — Что в методологии или роадмапе CC бы пометил как
**избыточное** для генерации Vue-кода? Что — как **недостаточное**?

Q7.3 — Какой объём specs (страниц) — оптимальный для одного screen с
учётом существующей кодовой базы (где api/client, platform, utils уже
готовы)?

Q7.4 — Если в `api-openapi.json` поле / endpoint меняется — текущий
pipeline `velo gen-types` → `generated.ts` сейчас автоматизирован
(CI hook, pre-commit), или всё ещё manual? Если manual — что должно
быть добавлено?

---

## Формат ответа

- Файл `06_project-inputs/CC-REPORT-2.txt` в текстовом формате
- Тот же Q/A стиль, что в CC-REPORT.txt
- В каждом A — указание источника (`Source: frontend/src/api/client.ts:33`)
- Не цитировать целиком большие файлы — снимать **ключевые строки**
  и давать line-numbers
- Допустимо: цитата >10 строк, если меньше нельзя обойтись (например,
  full Platform interface)
- Russian или English — на твоё усмотрение (CC-REPORT.txt был на русском)
- В конце — Блок 8 "Сводка из 5 строк" как в оригинале

---

## Что НЕ делать в этом recon

- **Не править** код — только observation
- **Не править** методологию или роадмап — только наблюдения, что
  стоит изменить (это будет следующий шаг, после моей сверки)
- **Не трогать** Figma — у меня (Cowork) свой канал к Figma через MCP
- **Не делать** глубокого аудита `VELO-Frontend-TZ-Final.md`,
  `VELO-Technical-Specification.md` и других продуктовых документов —
  оператор сказал, они вне scope сейчас

---

## Анкер

```
[CC-RECON-PROMPT-2.md | v1.0 | 2026-05-17]
Recon prompt для Claude Code, чтобы свежим взглядом провалидировать
v1.0 методологию и роадмап против реальности кода + API contract.
Ожидаемый output: 06_project-inputs/CC-REPORT-2.txt в том же формате,
что 06_project-inputs/CC-REPORT.txt.
```
