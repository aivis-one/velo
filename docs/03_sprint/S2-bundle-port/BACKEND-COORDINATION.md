# BACKEND-COORDINATION.md

> Velo — Координация с backend-партнёром по итогам S2-Sprint-Builder Re-plan
> Created: 2026-04-30
> Owner: frontend (this side); Recipient: backend-партнёр
> Update on: каждый response от партнёра, каждый regen, каждое resolved-clarification
> Lives in: `docs/03_sprint/S2-bundle-port/`

---

## Context

После S1 close + получения нового дизайн-батча (2026-04-30, 55 mockups → 34 unique views) сделана сверка скринов с текущим backend OpenAPI spec. Этот документ — единственный SSOT для backend-партнёра по тому, что фронт планирует строить в S2/S3 и что от партнёра нужно для этого.

Документ ОБНОВЛЯЕТСЯ. Закрытые позиции переносятся в раздел "Resolved" с датой и commit-hash.

Принятая модель работы: фронт строит ВСЕ экраны из дизайн-батча. Где endpoint есть → подключаем. Где endpoint отсутствует → строим как UI-mock (localStorage / placeholder data) и фиксируем в этом документе требование. Партнёр выкатывает endpoints по своей очереди приоритетов. Когда endpoint появляется + regen проходит → фронт мигрирует mock на реальный API в отдельном цикле.

---

## Priority legend

- **P0** — блокер S2 phase (фронт упирается в отсутствие endpoint'а до старта phase'а)
- **P1** — блокер S3 phase
- **P2** — улучшение качества; фронт работает на mock; partner может выкатить когда удобно
- **P3** — nice-to-have / future feature

---

## A. MISSING endpoints — нужны новые endpoint-группы

### A.1 Email/password authentication — P1

**Why:** decisions.md #028 — hybrid auth (γ): TMA primary + email/OAuth для PWA standalone fallback. PWA-юзер видит Login (02) + Register (03) экраны.

**Required:**
- `POST /api/v1/auth/email/login` — body: `{email, password}` → response: `{user, session_token}` (как `AuthResponse`)
- `POST /api/v1/auth/email/register` — body: `{email, password, first_name}` → response: `{user, session_token}`
- `POST /api/v1/auth/password/reset-request` — body: `{email}` → 204
- `POST /api/v1/auth/password/reset-confirm` — body: `{token, new_password}` → 204

**Schema:** добавить на `User`:
- `email: str | None` (unique, nullable for TMA-only users)
- `password_hash: str | None` (bcrypt, nullable)

**Frontend until ready:** Login + Register экраны строятся как UI-mock, кнопка "Войти" toaster "Email-вход в разработке". TMA flow работает через `/auth/telegram` без изменений.

### A.2 Google + Apple OAuth — P2

**Why:** скрины 02/03 показывают OAuth кнопки + 04 — OAuth callback loading.

**Required:**
- `POST /api/v1/auth/oauth/{provider}` где provider ∈ {google, apple} — body: `{id_token}` → response: `{user, session_token}`

**Schema:** добавить на `User`: `oauth_provider: str | None`, `oauth_subject: str | None`.

**Frontend until ready:** OAuth кнопки в UI присутствуют, при клике → toast "OAuth скоро будет доступен".

### A.3 Diary search — P2

**Why:** скрин 44 показывает search overlay над diary timeline.

**Required:**
- `GET /api/v1/diary/search?q={query}&limit&offset` → `PaginatedDiaryEntriesResponse` (или новый response с подсветкой матчей)
- Search покрывает: `entries.content`, `entries.title`, `checkins.comment`, `feedbacks.comment`. Фронт ожидает один объединённый result-list.

**Frontend until ready:** Search overlay показан с placeholder-history и сообщением "Поиск временно недоступен". История поисков хранится в localStorage (per-device).

### A.4 Account deletion — P2

**Why:** скрин 73 показывает confirmation модал "Удалить аккаунт".

**Required:**
- `DELETE /api/v1/users/me` — body: `{password?}` (если email-юзер); cascade: bookings (cancel + refund), diary entries (hard delete personal data), payments (audit retain), masterprofile (deactivate). Response: 204.

**Frontend until ready:** Кнопка "Удалить аккаунт" → нативный confirm → toast "Удаление аккаунта в разработке. Свяжитесь с поддержкой".

### A.5 Notification preferences — P2

**Why:** скрин 74 показывает 4 toggles (Push / Напоминания / От мастеров / От поддержки).

**Required:**
- `GET /api/v1/users/me/notification-preferences` → `{push, reminders, from_masters, from_support}`
- `PATCH /api/v1/users/me/notification-preferences` — body: same shape (все опциональны).

**Schema:** добавить таблицу `user_notification_preferences` (или JSONB колонка на `users.notification_preferences`).

**Bot-side:** Telegram bot должен gate'ить отправку уведомлений по этим флагам.

**Frontend until ready:** Toggles работают через localStorage. State пере-используется в logic dashboard'а ("показывать reminder card?"), но не доходит до bot'а.

### A.6 Support tickets — P2

**Why:** скрин 76 показывает форму обратной связи.

**Required:**
- `POST /api/v1/support/tickets` — body: `{subject: str, message: str}` → `{ticket_id, created_at}`. Триггерит email/Telegram notification команде поддержки.

**Schema:** новая таблица `support_tickets` (id, user_id, subject, message, status, created_at, resolved_at).

**Frontend until ready:** Форма submit → toast "Сообщение отправлено" (без реальной отправки).

### A.7 Messages — P1

**Why:** скрины 80 (список) + 81/82 (thread). User ↔ Master + User ↔ Support чаты.

**Required (минимум):**
- `GET /api/v1/messages/conversations?limit&offset` → list of `{id, counterparty: {id, name, avatar_url, role}, last_message: {text, created_at, is_unread}, unread_count}`
- `GET /api/v1/messages/conversations/{id}/messages?limit&offset` → list of `{id, sender_id, text, created_at, is_read}`
- `POST /api/v1/messages/conversations/{counterparty_id}` — body: `{text}` → message obj. Создаёт conversation если не существовала.
- `POST /api/v1/messages/conversations/{id}/read` — отмечает все unread как read.

**Notes:**
- 1:1 chats only в первой итерации. Group chats — P3 (см. BACKLOG entry).
- Counterparty types: `master` (по `master_id`), `support` (системный единственный).
- Real-time не требуется на старте; фронт polling по `GET conversations` каждые 30 сек.

**Schema:** новые таблицы `conversations` + `messages`.

**Frontend until ready:** Полный UI работает на placeholder-data из constant в frontend (3 conversations, 5-10 fake messages в каждом). Send-button toaster "Сообщения скоро будут доступны".

### A.8 Weekly AI summary — P2

**Why:** скрин 16 показывает "Саммари недели 16-22 января". Существующий `/practices/{id}/ai-summary` — per-practice, не подходит.

**Required:**
- `GET /api/v1/users/me/ai-summary?period={week|month}&date={iso}` → `{period_start, period_end, summary: str, recommendations: [str], is_mock: bool, generated_at: datetime}`

**Frontend until ready:** Экран рендерится на static placeholder-text. `is_mock=true` всегда.

### A.9 Reports / complaint UI integration — P3

**Why:** существующий `/api/v1/reports` endpoint без UI integration. Дизайнер не предоставил UI screens.

**Action item:** ждём дизайн от дизайнера (long-press menu на master profile / practice card / диалоговое окно). См. DESIGN-DECISIONS-LOG.md.

---

## B. Schema extensions — расширения существующих моделей

### B.1 `DiaryEntry.type` — P1

**Why:** скрины 49 (Дневник) + 50 (Сонник). Frontend строит фильтр-chip в одном view (decision #032).

**Required:**
- `DiaryEntry.type: enum('journal', 'dream', 'insight')`, default `'journal'`. Миграция existing entries → `'journal'`.
- `CreateDiaryEntryRequest.type: str | None` (default `'journal'` если omit)
- `UpdateDiaryEntryRequest.type: str | None`
- GET `/api/v1/diary?type={journal|dream|insight}` query param.

**Frontend until ready:** Filter chip в UI работает client-side по placeholder атрибуту, reload не сохраняет тип. После backend-выкатки + regen — миграция в один цикл.

### B.2 `User.onboarding_completed` — P3 (опционально)

**Why:** decisions.md #034 — текущий план: localStorage. Server-side flag — улучшение для cross-device consistency.

**Required (если решим перейти):**
- `User.onboarding_completed: bool`, default `false`
- `UserUpdate.onboarding_completed: bool | None`
- При первом auth via `/auth/telegram` → server sets `false`. Frontend меняет на `true` после прохождения onboarding carousel.

**Frontend currently:** localStorage flag. Перейдём на server-side когда/если партнёр выкатит — отдельный цикл миграции.

### B.3 `User.language` — P3

**Why:** скрин 75 показывает выбор языка интерфейса (Русский / English).

**Verify:** есть ли уже `language` поле на `User`? OpenAPI schema показывает `language: str` в `UserResponse`. **[uncertain]** — какие значения принимаются? Нужен enum или freeform? Если freeform — frontend валидирует client-side.

**Frontend currently:** Toggle между 'ru' / 'en' через `PATCH /users/me`. Вся i18n инфраструктура — отдельный backlog entry (BACKLOG #..., to be created).

### B.4 `Booking.notes` (master-request на booking) — P2

**Why:** скрин 26 (Booking Success) показывает textarea "Запрос мастеру".

**Required:**
- `Booking.notes: str | None`, max length 2000
- `CreateBookingRequest.notes: str | None`
- `PurchaseRequest.notes: str | None`
- Опционально: триггерит создание message в conversation user↔master с этим текстом (см. A.7).

**Frontend until ready:** Textarea в UI, при отправке текст разрешается локально, на backend booking создаётся без notes. Toast "Запрос мастеру скоро будет доступен".

### B.5 `AdminMasterListItem` schema extension — application content — P2

**Why:** S4-P15 AdminMasterReviewView (admin verify/reject flow) needs to display master's application content for moderation decision. Current `AdminMasterListItem` (generated.ts:32) exposes only `id, telegram_id?, first_name?, last_name?, avatar_url?, role: UserRole, is_active: boolean, master_status: string`. Current `MasterApplyResponse` (generated.ts:307) exposes only `user_id, status, created_at`. Neither type carries the application content the reviewer needs to see (bio, methods, experience, certifications, contact email/phone). View shipped as **degraded v1** with placeholder Callout «Расширенные данные заявки пока недоступны» pending this extension.

**Required (option a — schema extension, preferred):**
- Extend `AdminMasterListItem` with admin-only fields: `bio?: str`, `methods?: str[]`, `experience_years?: int`, `certifications?: str[]`, `email?: str`, `phone?: str`.

**Required (option b — new endpoint, alternative):**
- `GET /api/v1/admin/masters/{id}/application` → richer `AdminMasterApplicationResponse` with the application content above.

**Frontend until ready:** AdminMasterReviewView v1 ships with placeholder Callout amber «Расширенные данные заявки пока недоступны — backend-расширение в очереди» + verify/reject CTAs via ConfirmModal. When backend extends + regen lands → C70-style follow-up cycle wires fields into FormShell rendering, promoting v1 → v2.

**Sprint tag:** S5+ backend cycle (mirror of BACKLOG #104).

---

## C. Behaviour clarifications — уточнения текущих endpoints

### C.1 `/bookings` vs `/practices/{id}/purchase` — P0

**Question:** для платной практики frontend должен использовать `POST /bookings` или `POST /practices/{id}/purchase`?

**Текущее понимание фронта:**
- `POST /bookings` — создаёт только booking, без денежной транзакции; для бесплатных практик
- `POST /purchase` — создаёт booking + purchase; обрабатывает баланс + commission; для платных
- Бесплатная практика через `/purchase` тоже работает (paid_cents=0, ledger entries=0) — backend speccs это явно говорит

**Frontend default до ответа:** ВСЕ бронирования через `POST /practices/{id}/purchase` (унификация). Поле `is_free` на practice определяет UI ("Бесплатно" badge), но endpoint один.

**Confirm or correct.**

### C.2 Practice-level stats источник — P2

**Question:** на скринах Dashboard (10) + Profile (70) показано "12 практик / 9.5 часов". Откуда берётся?

**Frontend default:** computed client-side из `GET /bookings/me?status=attended` + sum `practice.duration_minutes`. Никаких backend endpoints не запрашиваем.

**Risk:** если у пользователя 1000+ attended bookings, client-side aggregation медленно. В этом случае нужен `GET /users/me/stats` endpoint. Откладываем до реальной проблемы.

**Confirm.**

### C.3 ZOOM link delivery — P2

**Question:** на скрине 18 (Booking Detail) написано "Ссылка будет отправлена за 10 минут до начала практики". Текущий `Practice.zoom_link` — public field в `PracticeResponse`. Где живёт правда?

**Possible models:**
- (a) `zoom_link` показывается всегда после booking (поле в `Booking` или `Practice`)
- (b) `zoom_link` гейтится backend-логикой: видим только за 10 мин до start_time
- (c) `zoom_link` приходит через Telegram bot notification, не через API

**Frontend default:** показываем `practice.zoom_link` если оно non-null после `bookings.confirmed`. Если null → текст "Ссылка будет отправлена за 10 минут".

**Confirm — какая модель?**

### C.4 Mid-practice check-in semantics — P3

**Why:** скрин 14 (Practice Live) имеет кнопку "Check-in" во время live-практики.

**Frontend default (decisions.md #035):** "Check-in" на live-экране = re-open pre-practice check-in form (упрощённо), upsert через существующий `POST /practices/{id}/checkin`. Не создаёт новый event.

**Confirm — это корректно или нужен новый endpoint типа `/practices/{id}/checkin/mid-session`?**

### C.5 Cancellation refund logic — P2

**Question:** при `DELETE /bookings/{id}` — что происходит с balance? Refund 100% сразу? С учётом времени до practice (refund window)?

**Frontend default:** показываем "Отменить бронирование" без disclosures. Если backend speccs включают refund window — frontend нужно знать чтобы показать предупреждение в native modal.

**Provide refund policy or confirm "no refund window — always 100%".**

### C.6 `pending` booking status visibility — P3

**Confirmed by frontend (decisions.md #...):** `pending` — transient state, никогда не показывается user'у в UI. Все bookings которые user видит — `confirmed` / `cancelled` / `attended` / `no_show`.

**Confirm correctness of this assumption.**

### C.7 `no_show` UI label — P3

**Question:** label для `no_show` status в My Reservations (17). Frontend default: "Пропущена". Confirm or suggest.

---

## D. Regen pipeline coordination — P0

### D.1 Trigger model

**Current state:** `backend/scripts/generate_ts_types.py` exists и работает. Триггер — manual: партнёр запускает скрипт против `openapi.json` → коммит regenerated `frontend/src/api/generated.ts`.

**Problem:** в S1 C06 partner regen прошёл против stale openapi.json — что привело к B.1 (тогда) с `MasterProfileResponse` без `min_withdrawal_cents`/`withdrawal_fee_cents`.

**Required workflow:**
1. Backend partner вносит изменение в OpenAPI schema (добавляет endpoint / расширяет schema).
2. Backend partner делает локальный run dev-сервера → dumps fresh `openapi.json`.
3. Backend partner запускает `generate_ts_types.py` → updates `frontend/src/api/generated.ts`.
4. Backend partner commits both `openapi.json` (если в repo) + `generated.ts` в одном commit.
5. Backend partner пишет в Telegram/Slack: "regen [date] — добавлен endpoint X / расширена schema Y / [list]".

**Frontend trigger:** при получении сигнала — отдельный cycle migration (скоро после receipt) на consumer-сторону.

### D.2 Verification gate

После каждого regen фронт делает:
- `(cd frontend && npm run typecheck)` — обязан зелёный
- Сравнение diff'а `generated.ts` с changelog от партнёра — нет ли пропущенных полей

Если typecheck падает → migrate consumers в текущем активном цикле (как было в S1 C06b).

### D.3 Дискуссионный пункт

В будущем рассмотреть: pre-commit hook у партнёра который автоматически regenerates `generated.ts` при изменении schemas. Сейчас manual — приемлемо при low partner velocity.

---

## E. Resolved (closed items)

| Date | Item | Resolution | Commit |
|------|------|------------|--------|
| 2026-04-30 | A.2 (S1) — MasterProfileResponse без min_withdrawal_cents/withdrawal_fee_cents | Partner Pydantic CR-01 was shipped pre-`81304a6`, but that regen ran against stale openapi (per decision #022); fields actually surfaced in generated.ts via S2 P05 C15 self-host regen (decision #046) | `68fa5cd` |
| 2026-04-30 | B.1 (S1) — UserResponse stale | Partner regen against fresh openapi at `81304a6` (genuinely landed); verified by S2 P05 C15 pre-flight — `language` + `timezone` present in generated.ts@81304a6 | 81304a6 |
| 2026-04-30 | C.1 (S1) — Zodd CRITICAL #1 PracticeSummary.timezone | Partner Pydantic patch shipped pre-`81304a6` but field absent from generated.ts until S2 P05 C15 self-host regen (decision #046) | `68fa5cd` |
| 2026-04-30 | E.1 — `AdminMasterListItem.role: string → UserRole` (type narrowed) | Partner shipped to Pydantic (date unknown); surfaced in generated.ts by S2 P05 C15 self-host regen | `68fa5cd` |
| 2026-04-30 | E.2 — `CreateCompanyPromoRequest.valid_from: string → string \| null` (nullable optional) | Partner shipped to Pydantic (date unknown); surfaced in generated.ts by S2 P05 C15 self-host regen | `68fa5cd` |
| 2026-04-30 | E.3 — `CreateMasterPromoRequest.valid_from: string → string \| null` (nullable optional) | Partner shipped to Pydantic (date unknown); surfaced in generated.ts by S2 P05 C15 self-host regen | `68fa5cd` |

**Notes on § E reliability (post-S2 P05 C15):** rows are added when partner signals a fix is shipped. Pre-S2 P05, signals were taken at face value — A.2 and C.1 were recorded resolved against `81304a6`, but the regen pipeline at that commit ran against stale openapi and the fixes did not propagate to `frontend/src/api/generated.ts`. Going forward, § E rows are dated to the regen-commit timestamp (when the fix is observable in `generated.ts`), not to the partner-message timestamp. See decision #046 for the self-host fallback recipe.

---

## F. Update protocol

Этот файл — живой документ. При каждом обновлении:
1. Если позиция стала done → перенести в § E (Resolved) с date + commit hash.
2. Если новое требование выявлено в design-batch → добавить в § A или § B/C.
3. Если приоритет меняется → обновить в-line.
4. Bumpить header `Updated:` дату.

Партнёр читает этот файл от верха до E (Resolved пропускает). Фронт читает целиком.

---

*Velo project — S2 Sprint planning artifact*
*Format established by decisions.md #041*
