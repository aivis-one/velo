# Backend Coordination Report — Velo Frontend Sprint Planning

> From: Velo frontend track
> Date: 2026-04-26
> Base commit: `47a6cd8` (Velo frontend HEAD post-S1-P01 close)
> Reference: S1-SPRINT.md success criteria — "Список 7 missing backend endpoints передан Human"
> Audit method: P02 scout (frontend api/*.ts consumer surface vs backend openapi schemas in generated.ts)

## TL;DR

Привет! Подвожу итог по тому, что нужно фронту для S2/S3 sprints (бандл-port + greenfield пользовательских и мастер-фич).

**7 фич которые требуют backend-работы:** Waitlist, Profile editing, Logout-all, Purchase history, User-side reports, Promo management, Live-session join/leave. Детали ниже.

**Дополнительно (не партнёрские задачи):**
- 2 endpoint'а уже у тебя готовы — нам нужно дописать обёртку на фронте (AISummary, BookingDetail). Не блокеры.
- 2 новых endpoint'а нужны для S2/S3 фич которых раньше в плане не было (MasterProfile public read, MH-17 Practice room).
- 2 регресса в regen-pipeline ожидают свежей openapi.json генерации (CR-01 financial fields + Zodd CRITICAL #1 timezone).

---

## 7 фич — детали

### 1. Waitlist API (запись в очередь когда мест нет)

**Зачем:** Сейчас фронт показывает "Мест нет, попробуйте позже" — юзер уходит. С waitlist пользователь записывается в очередь, при освобождении места получает push, может подтвердить или отказаться.

**Endpoints:**
- `POST /api/v1/practices/{id}/waitlist` — подать заявку
- `GET /api/v1/waitlist/me` — список своих заявок
- `POST /api/v1/waitlist/{id}/confirm` — подтвердить освободившееся место
- `DELETE /api/v1/waitlist/{id}` — отказаться

**Текущее состояние:** 4 типа уже определены в generated.ts (`WaitlistEntryResponse`, `WaitlistConfirmResponse`, `WaitlistWithPracticeResponse`, `PaginatedWaitlistResponse`) — структура есть, реализации backend нет (или не задокументированы в openapi). На фронте — ноль вызовов. BACKLOG #21.

**Используется в:** S2 P05 (порт CalendarView/PracticeDetailView) — там нужен путь "записаться в очередь" когда нет мест. Желательно к S2 P05 (start ~ S2 неделя 1).

### 2. Profile editing (редактирование профиля пользователя)

**Зачем:** Сейчас профиль read-only. Нет API для смены имени, таймзоны, языка.

**Endpoint:**
- `PATCH /api/v1/users/me` — изменить first_name, timezone, language

**Текущее состояние:** UserProfileView.vue read-only. Zodd_review §B.5.

**Используется в:** S3 P09 C36-C37 (regen UserProfileView с editable fields).

### 3. Logout-all (выход со всех устройств)

**Зачем:** Security. Если юзер потерял доступ к устройству — нужна возможность инвалидировать все сессии.

**Endpoint:**
- `POST /api/v1/auth/logout-all`

**Текущее состояние:** только one-device logout. Zodd_review §B.5.

**Используется в:** S3 P09 C36-C37 (UserProfileView regen) или ранее, по приоритету.

### 4. Purchase history (история покупок пользователя)

**Зачем:** MyBookings показывает букинги, но не платежи. Пользователю иногда нужно посмотреть историю транзакций.

**Endpoint:**
- `GET /api/v1/purchases/me` — список покупок текущего пользователя

**Текущее состояние:** на фронте нет UI для этого. Zodd_review §B.5.

**Используется в:** S3 P09 (вероятно расширение UserProfileView или отдельный экран — TBD).

### 5. User-side reports (жалобы пользователей)

**Зачем:** Сейчас admin может смотреть отчёты, но юзер не может их подавать. Нужен flow "пожаловаться на мастера/практику".

**Endpoints:**
- `POST /api/v1/reports` — подать отчёт
- `GET /api/v1/reports/me` — свои отчёты
- `PATCH /api/v1/reports/{id}` — редактировать (если status позволяет)

**Текущее состояние:** только admin-side endpoints (admin/reports). User-side нет. Zodd_review §B.5.

**Используется в:** S3 (вероятно при regen UserProfileView или отдельный flow). Не блокер для S2.

### 6. Promo management (промокоды)

**Зачем:** Master хочет создать промокод для своих практик; admin — глобальные промо.

**Endpoints:**
- `POST /api/v1/masters/me/promos` — мастер создаёт
- `GET /api/v1/masters/me/promos` — список своих
- `PATCH /api/v1/masters/me/promos/{id}` — редактировать
- `POST /api/v1/admin/promos` — admin global (если применимо)

**Текущее состояние:** типы в generated.ts (`CreatePromoRequest`, `PromoResponse`) есть, но client calls нет. Master не может создавать промо. Zodd_review §B.5.

**Заметка:** generated.ts имеет `CreateMasterPromoRequest` + `CreateCompanyPromoRequest` отдельно; types.ts на фронте имеет unified `CreatePromoRequest` (потенциальный divergence — мини-цикл фронта на типизацию после твоего фикса).

**Используется в:** S3 P10 master-existing audit (в одном из master views) — не блокер.

### 7. Live-session join/leave (вход в живую сессию)

**Зачем:** Текущий check-in (CheckinView) — это mood-gate ДО сессии. Для самой сессии (Zoom) нужна отдельная отметка "я в комнате" / "я вышел" — для master-side analytics и MH-17 Practice room.

**Endpoints:**
- `POST /api/v1/bookings/{id}/join` — отметка входа в live-сессию
- `POST /api/v1/bookings/{id}/leave` — отметка выхода

**Текущее состояние:** UI не реализован. Zodd_review §B.5.

**Используется в:** S2 P06 C21 (PracticeLiveView) + S3 P11 (MH-17 Practice room).

---

## Дополнительно — не партнёрские задачи

### Backend готов, фронт не дописал обёртку (НЕ требует твоей работы):

1. **AISummary API** — `GET /api/v1/practices/{id}/ai-summary`. У тебя уже есть (`AISummaryResponse` в generated.ts:18). На фронте client wrapper отсутствует. Я добавлю в S2 C24.

2. **BookingDetail API** — `GET /api/v1/bookings/{id}`. У тебя уже есть (`BookingDetailResponse` в generated.ts). На фронте wrapper отсутствует. Я добавлю в S2 C22.

### Новые endpoints для фич которых раньше в плане не было (требуется backend-работа, P1):

3. **MasterProfile public read** — `GET /api/v1/masters/{id}` (публичный, без admin guard). Сейчас только admin endpoint существует. Нужно для S2 C25 (новый MasterProfilePublicView — публичная карточка мастера для пользователя).

4. **MH-17 Masters Practice room** — целая группа endpoints для управления live-практикой мастером: real-time participant list, mood broadcast, master controls (mute/unmute/end), AI-summary trigger. Schema TBD — обсудим отдельно когда дойдём до S3 P11. На S3 неделе 5-6 примерно.

### Regen-trigger ask (свежий openapi.json + перезапуск generate_ts_types.py):

5. **CR-01 financial fields:** `MasterProfileResponse.min_withdrawal_cents` + `MasterProfileResponse.withdrawal_fee_cents` — твои Pydantic schema + router population уже шипнуты (commit `81304a6` или ранее), но текущий generated.ts ушёл от устаревшего openapi.json. Свежая регенерация unblock'нет фронт от deprecated фронт-констант (BACKLOG #26).

6. **Zodd CRITICAL #1:** `PracticeSummary.timezone` — Pydantic schema нужно расширить полем `timezone: str`. Сейчас фронт fallback'ом подставляет 'Europe/Berlin' для всех практик (тактически закостылено в `UserDashboardView.vue:300` cast в C06b). Когда добавишь поле + сделаешь regen — фронт уберёт cast и Berlin fallback (BACKLOG #27).

---

## Запрос

Можешь:
1. Подтвердить план реализации для 7 фич (сейчас / в S2 / в S3)?
2. Запустить regen openapi.json → generate_ts_types.py для разблокирования #5 + #6?
3. По MasterProfile public read и MH-17 — обсудим schema когда будет удобно (не P0 сейчас).

Спасибо! 🙏
