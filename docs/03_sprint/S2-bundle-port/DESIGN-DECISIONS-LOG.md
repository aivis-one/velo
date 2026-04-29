# DESIGN-DECISIONS-LOG.md

> Velo — Лог дизайн-решений и открытых вопросов
> Created: 2026-04-30
> Audience: дизайнер, PM, sponsor проекта
> Owner: frontend; Updated: каждое sprint planning, каждый design-batch arrival, каждый resolved-question
> Lives in: `docs/03_sprint/S2-bundle-port/`

---

## Context

После S1 close + получения нового дизайн-батча (2026-04-30, 55 mockups) проведён планировочный анализ под S2/S3. Этот документ — единственный SSOT для команды (дизайнер / PM / sponsor) о том:

1. Какие решения по UI / UX уже приняты — фронт строит ровно так
2. Какие вопросы остались открытыми — нужен input от дизайнера
3. Что осознанно исключено из текущей итерации
4. Какие следующие batch'и скринов ожидаются и для каких спринтов

Документ ОБНОВЛЯЕТСЯ. Закрытые вопросы переносятся в раздел "Resolved" с датой и commit-ссылкой на decisions.md #NNN.

---

## A. Принятые решения

Каждое — реализуется как описано во фронте. Если не согласен — поднимай в discussion.

### A.1 Архитектура аутентификации — hybrid (γ)

- **TMA контекст:** auth через `initData` (Telegram-managed). Welcome-экрана НЕТ — пользователь идёт сразу из Loading → Dashboard.
- **PWA standalone:** Welcome (01) → Login (02) или Register (03) → OAuth (04) или email-вход.
- Скрины 02/03/04 НЕ показываются TMA-юзерам.
- Backend для email/password + OAuth ещё нет — UI работает как mock в S2 (тосты "Скоро будет"), реальное подключение в отдельном цикле когда партнёр выкатит endpoints.

См. decisions.md #028; BACKEND-COORDINATION.md § A.1, A.2.

### A.2 Onboarding flow — carousel view + separate timezone view

- Carousel: ОДИН view (`OnboardingCarouselView`) с 3 intro slides (05/06/07) через index state (0..2). Свайп / "Далее".
- Timezone: ОТДЕЛЬНЫЙ view (`OnboardingTimezoneView`, скрин 08) — финальный шаг с input city → frontend resolve в IANA timezone → `PATCH /users/me { timezone }`.
- Onboarding считается "completed" после успешного timezone capture (PATCH success).
- Persistence: localStorage флаг `velo:onboarding_completed=true` устанавливается после finalization в timezone view (per-device).
- Onboarding показывается ОДИН РАЗ после первого auth (TMA или PWA).

См. decisions.md #034; BACKEND-COORDINATION.md § B.2.

### A.3 City-to-IANA resolution — локальная таблица

- Frontend держит таблицу из ~300 крупных городов с timezone mapping (сборка из `moment-timezone` или эквивалент).
- Поиск по русско-английским названиям + autocomplete.
- Если город не найден → fallback на `Intl.DateTimeFormat().resolvedOptions().timeZone` (browser-detected).

**Open Q:** дизайнер хотел fancy city picker с globe иконкой? Или простой dropdown с поиском достаточно? — См. § B.

### A.4 Dashboard — refresh поверх существующего S1 P03 C10

- Существующий `UserDashboardView.vue` (LOC 741, S1 C10) — переписывается под новый дизайн (10/11).
- Сохраняется существующая логика: ближайшая практика, check-in/feedback alerts, tactical timezone cast (убирается после regen в C15).
- Новые элементы: greeting block, AI summary teaser, progress stats row.

См. decisions.md #029.

### A.5 Calendar — week strip + day-grouped list

- Скрины 21 (root) + 22 (filter overlay).
- Layout: горизонтальный week strip (ПН-ВС) + arrows навигации недель + список практик сгруппированный по дням текущей недели.
- Filter overlay (22) — модал поверх с chip-фильтрами Направление / Вид / Сложность / Длительность / Время.

### A.6 Practice booking flow — 3 разных экрана детали

| Скрин | Когда показывается | Endpoints |
|-------|---------------------|-----------|
| 24 / 28 — Practice Detail (pre-book) | Из Calendar / Master profile, до бронирования | GET `/practices/{id}` + `/masters/{id}` |
| 18 — Booking Detail | Из My Reservations, после бронирования (status-confirmation view) | GET `/bookings/{id}` |
| 15 — Booked Practice Detail (Моя практика) | С Dashboard "ближайшая практика" в day-of-practice окно | GET `/bookings/{id}` (extended) |

Различие 15 vs 18 [uncertain — см. § B.4 open question]. Текущая интерпретация: 18 — статус + ZOOM-info, 15 — операционная карточка с check-in window открытым.

### A.7 Diary — layout toggle, не routes

- Категории Diary (40, 45, 47, 49+50, 53) показываются в timeline-layout (декоративные коннекторы) ИЛИ list-layout (плоские карточки).
- Toggle живёт в **состоянии view** (state, не URL). Persist в localStorage.
- Один Vue-component per category. Внутри `const layout = ref<'timeline'|'list'>('timeline')`.
- 7 unique views в Diary, не 12.

См. decisions.md #032.

### A.8 Diary entry types — 1 view с filter chip

- Дневник (49) и Сонник (50) — НЕ отдельные views, а filter-chip над `EntriesView`.
- Backend получит расширение `DiaryEntry.type: enum('journal','dream','insight')` (decisions.md #033).
- Пока backend не выкатил → frontend filter работает client-side по placeholder атрибуту.

См. decisions.md #033; BACKEND-COORDINATION.md § B.1.

### A.9 Diary entry creation — composer expand

- Composer внизу timeline-screens (40 etc.) — collapsed: `<input>` "Начните писать..." + send + mic icons.
- На tap по input → expand модал с полным набором: textarea + title + mood picker + practice picker.
- Submit → `POST /api/v1/diary` с полным payload.

См. decisions.md (TBD); design uncertainty: дизайнер не нарисовал expanded состояние — frontend строит по analogy с другими mood/title forms.

### A.10 Practice Live (14) — external Zoom + upsert checkin

- Кнопка "Войти" → `window.open(practice.zoom_link, '_blank')` (внешний Zoom клиент).
- Кнопка "Check-in" во время live → re-open pre-practice check-in form (12), upsert через существующий `POST /practices/{id}/checkin`.
- Кнопка "Покинуть практику" → `POST /bookings/{id}/leave` + редирект на Dashboard.
- Никакой embedded video / Zoom SDK на этом этапе.

См. decisions.md #035, #037.

### A.11 Profile avatar — read-only

- Скрин 72 (Edit Profile) показывает аватар, но фронт его НЕ редактирует.
- Avatar = Telegram-managed (как существующее поведение из openapi.json).
- Tap на аватар → toast "Аватар управляется Telegram".

См. decisions.md #038.

### A.12 Booking cancellation — native confirm

- "Отменить бронирование" на 15/18 → нативный confirm dialog (как 73 для delete account).
- Без custom modal, без mockup parity.

### A.13 Mood capture на Check-in form (12) — 3-icon picker, slider убираем

- На скрине показаны и 3-icon picker (sad/neutral/happy) и slider — это редундантность.
- Frontend оставляет только 3-icon picker.
- Backend `CheckinRequest.mood: str` принимает 3 значения: `low | mid | high`.

См. decisions.md (TBD).

### A.14 Check-in / Feedback success — 2 разных экрана

- Скрин 13 — Check-in success (bg-white, turquoise check-icon, "Check-in отправлен!", "Начать практику" + "На главную").
- Скрин 30 — Feedback success (bg-white, turquoise heart, "Спасибо за feedback!", "В дневник" + "На главную").
- Это два разных view, не дубликаты.

### A.15 Notifications screen (74) — localStorage mock

- 4 toggles: Push / Напоминания / От мастеров / От поддержки.
- Backend endpoint отсутствует → state хранится в localStorage.
- Фронт использует флаги для UI-логики (показывать ли reminder card на dashboard etc.) но НЕ шлёт на backend.
- Telegram bot uses default settings до того, как backend endpoint появится.

См. decisions.md (TBD); BACKEND-COORDINATION.md § A.5.

### A.16 Messages (80/81/82) — full UI mock

- Скрины показывают список + thread.
- Backend messaging endpoint НЕТ → frontend строит ПОЛНЫЙ UI на placeholder data (3 fake conversations, 5-10 fake messages).
- Send-кнопка → toast "Сообщения скоро будут доступны".
- 1:1 only (user↔master + user↔support). Group chats — out of scope (см. § C).

См. decisions.md (TBD); BACKEND-COORDINATION.md § A.7.

### A.17 AI summary view (16) — placeholder text

- Backend `/practices/{id}/ai-summary` возвращает placeholder уже сейчас (`is_mock=true`).
- Frontend AI summary view (16) — для weekly summary — строится на static placeholder с фейковыми рекомендациями.
- Реальное подключение когда партнёр выкатит `/users/me/ai-summary?period=week`.

См. decisions.md (TBD); BACKEND-COORDINATION.md § A.8.

### A.18 Stats источник — frontend computed

- "12 практик / 9.5 часов" на Dashboard + Profile — computed client-side из `bookings.list?status=attended` + sum `duration_minutes`.
- Никаких backend endpoints не требуем.
- Если performance проблема (1000+ attended bookings) — добавим endpoint в backlog.

### A.19 Topup flow — as-is из S1

- Существующие TopupView / TopupSuccessView / TopupCancelView (S1) сохраняются БЕЗ изменений в S2.
- Дизайнер не предоставил новые скрины для топапа — линкуется с Dashboard / Profile в существующем виде.
- Когда дизайнер пришлёт refresh — отдельный цикл миграции.

См. decisions.md #039; § D.

### A.20 Master role design — ждём отдельный batch

- В текущем batch'е только 1 master screen (25 — публичный для user'а).
- Master-side (10 views: MasterDashboard, MasterPractices, и т.д.) — текущий код в `views/master/` остаётся на bundle SSOT.
- S4 = старт перевода master role на новую DS — НО только когда дизайнер пришлёт master batch.
- Если master batch не приходит к старту S4 → S4 сдвигается, остаётся в waiting state.

См. decisions.md #030; § D.

### A.21 Dark mode — параллельно с S2

- Бундл dark tokens лежат в variables.css (S1 P01).
- В S2 цикл C25 — implementation theme toggle infrastructure (`stores/ui.ts.theme` + localStorage + `prefers-color-scheme` listener + UI toggle в headers).
- Если дизайнер пришлёт dark variants новой DS до C25 — implementation на новых tokens. Если нет — на существующих bundle dark tokens, refresh переносится в S3+.

См. decisions.md #008 (continued).

### A.22 Empty / loading / error states — minimum viable

- Дизайнер не предоставил empty/loading/error states.
- Frontend строит на existing UI primitives (`VEmptyState.vue`, `VLoader.vue`) consistent across views.
- При получении дизайнерского refresh — отдельный полировочный цикл.

См. § D.

### A.23 Cancellation visualization — 'no_show' label

- Status `no_show` → label "Пропущена" в My Reservations (17). Иконка warning-amber.
- Status `pending` → НИКОГДА не показывается в UI (transient state).

### A.24 Реклама / промокоды UI — defer

- Backend поддерживает promo codes + discount preview, но дизайнер UI не нарисовал.
- Frontend пропускает в S2/S3.
- Когда дизайнер нарисует промокод поле в Practice detail (24) или в Booking flow (26) — отдельный цикл.

См. § D.

### A.25 Waitlist UI — defer

- Backend поддерживает waitlist (`/practices/{id}/waitlist`, `/waitlist/me`, `/waitlist/{id}/confirm`) но дизайнер UI не нарисовал.
- Frontend behavior на full practice: кнопка "Забронировать" disabled или меняется на "Места закончились" (без waitlist option).
- Когда дизайнер нарисует waitlist screens — отдельная фаза.

См. § D.

### A.26 Reports / complaints UI — defer

- Backend поддерживает reports (`POST /api/v1/reports`) с UI hidden access (long-press menu / Support form).
- Frontend интегрирует "Пожаловаться" hint в Support form (76) как short-term path.
- Полноценный UI с long-press menus — когда дизайнер нарисует.

См. § D; BACKEND-COORDINATION.md § A.9.

### A.27 Group chats для Messages — out of scope MVP

- 1:1 only в первой итерации.
- Group chats (например, чат всех участников практики) — backlog.
- Когда понадобится → дизайн + backend extension.

См. BACKLOG (entry to be created).

---

## B. Открытые вопросы — нужны от дизайнера

### B.1 Дашборд (UPDATE) дельта

В исходной cover-картинке упоминается `(UPDATE)` версия Дашборда. В присланном batch'е её нет. **Q:** этот batch — финальная версия (UPDATE applied), или мы получим UPDATE отдельно? Если отдельно — что именно меняется?

### B.2 Calendar (UPDATE) дельта

Аналогично — была отдельная (UPDATE) колонка для Календаря. **Q:** это финал или ждать UPDATE отдельно?

### B.3 City picker UI на onboarding step 4 (08)

Скрин показывает text input. **Q:** ожидается простой text-input с autocomplete dropdown, или fancy globe-picker / map widget?

### B.4 Booked vs Booking detail (15 vs 18)

Текущая frontend интерпретация: 18 — status-confirmation view для booking в неблизком будущем; 15 — day-of-practice operational view с check-in window. **Q:** правильно? Или 15/18 разные сценарии (e.g. Dashboard vs My Reservations entry points)?

### B.5 Diary entry expanded composer

Tap на collapsed composer → expanded форма с textarea + title + mood + practice picker. **Q:** есть mockup для expanded state? Если нет — фронт строит по аналогии с другими формами (Edit Profile 72 / Support 76).

### B.6 Mood scale — picker vs slider

Скрин 12 (Check-in form) показывает И 3-icon picker И continuous slider. **Q:** это redundant дизайн (выбираем picker как simpler) или они захватывают разные шкалы?

### B.7 Mid-practice "Check-in" интент

Скрин 14 показывает кнопку "Check-in" во время live-практики. Frontend interprets как "re-edit pre-practice check-in" (upsert). **Q:** правильно? Или это новый mid-session mood snapshot который должен сохраняться отдельно?

### B.8 Practice Live "video" placeholder

Скрин 14 показывает большой synthetic "video" placeholder. **Q:** это просто placeholder для скрина, реальное приложение в этом месте показывает... что? Логотип Velo? Master avatar? "Открой Zoom"?

### B.9 Booking master-request интент

Скрин 26 показывает textarea "Запрос мастеру". **Q:** этот текст:
- (a) уходит в отдельный thread в Messages с мастером?
- (b) сохраняется на самом booking как `notes` поле?
- (c) cosmetic UI без real persistence до Messages backend готов?

См. BACKEND-COORDINATION.md § B.4.

### B.10 Cancel booking refund window

**Q:** есть ли окно отмены без потерь (e.g. за 24ч до practice → 100% refund, иначе только 50%)? Если да — нужно показывать в native confirm dialog. Если нет (всегда 100% refund) — confirmed.

### B.11 Empty / loading / error mockups

**Q:** дизайнер планирует прислать states? Если да — для каких view приоритетные?

### B.12 Master-side batch ETA

**Q:** master-side новой DS — когда ожидать batch? S4 ждёт его старт.

### B.13 Dark variants

**Q:** dark variants новой DS — когда?

### B.14 Topup / balance visualization

**Q:** в новой DS должен быть визуальный refresh для:
- Profile balance display
- TopupView (Stripe Checkout entry)
- TopupSuccessView / TopupCancelView (Stripe redirect returns)
Или существующая S1-версия остаётся?

### B.15 Promo code UI

**Q:** добавить поле promo code в Practice Detail (24) или Booking flow (26)? Если да — где визуально?

### B.16 Waitlist screens

**Q:** practice fully booked — какое поведение в Practice Detail (24)? Disabled "Забронировать"? Кнопка "В очередь"? Отдельный экран Waitlist Status?

### B.17 Reports / complaint flow

**Q:** как пользователь жалуется на мастера / контент?
- Long-press на master profile?
- Кнопка в Support form?
- Скрытое меню в Settings?

### B.18 Onboarding flow ordering (TMA vs PWA)

**Q:** в TMA — onboarding carousel показывается между auto-auth и Dashboard? В PWA — после signup, до Dashboard? Или один и тот же flow для обоих?

---

## C. Out of scope для текущей итерации

Эти features есть в backend, есть в идее продукта, но НЕ реализуются в S2/S3:

| Feature | Reason | Where lives |
|---------|--------|-------------|
| Group chats для Messages | UI не нарисован, низкий приоритет | BACKLOG (TBD) |
| Account deletion | UI mock в S2 (toast "обратитесь в поддержку") | A.24 + BACKEND-COORDINATION § A.4 |
| Promo codes UI | Дизайнер не нарисовал | A.24 |
| Waitlist UI | Дизайнер не нарисовал | A.25 |
| Reports / complaints UI | Дизайнер не нарисовал | A.26 |
| Master role full implementation | Ждём дизайн-batch для master | A.20; S4 |
| Admin role | Заморожен с S1 (decision #010) | BACKLOG #4-7 → S5+ |
| Real Zoom embed | Out of scope (всегда external link) | A.10 |
| Avatar upload | Telegram-managed | A.11 |
| Empty/loading/error full mockup parity | Minimum viable patterns в S2/S3 | A.22 |

---

## D. Следующие batch'и которые ждём от дизайнера

| Batch | Priority | Blocks | Expected | Notes |
|-------|----------|--------|----------|-------|
| Dark variants новой DS | High | C25 (S2 theme toggle infra) | ASAP | Если до C25 — ОК; если позже — рефреш в S3 |
| Master-side screens (10 views) | High | S4 start | До конца S3 | Master Dashboard, Practices, Analytics, Finance, Profile, Apply, Pending, Attendance, EditPractice, CreatePractice |
| Topup / balance redesign | Medium | A.19 | Когда удобно | TopupView + Profile balance display |
| Empty / loading / error states | Medium | A.22 | Постепенно | Приоритет: Dashboard, Diary, My Reservations, Messages |
| Waitlist screens | Low | A.25 | Когда понадобится | "В очередь" button + waitlist status |
| Promo code UI | Low | A.24 | Когда понадобится | Поле в Practice Detail или Booking flow |
| Reports / complaint flow | Low | A.26 | Когда понадобится | Long-press menu или Support entry point |
| Group chats UI | Backlog | — | Future | Опциональная фича |
| Admin role | Backlog | — | Future | S5+ |

---

## E. Resolved (closed questions)

| Date | Question | Resolution | decisions.md ref |
|------|----------|------------|------------------|
| 2026-04-30 | Layout toggle Diary — state или route? | State (variant A) | #032 |
| 2026-04-30 | Дневник vs Сонник — два view или один с фильтром? | Один с фильтром, backend extension | #033 |
| 2026-04-30 | (UPDATE) интерпретация в batch'е | Этот batch уже = финал (UPDATE applied к старым) | (verbal acceptance) |
| 2026-04-30 | 13 vs 30 check-in success | НЕ дубликаты — 13 = check-in success, 30 = feedback success | A.14 |

---

## F. Update protocol

Когда:
1. Открытый вопрос ответ получен → переноси в § E с date + decisions.md ref + commit hash где fix реализован.
2. Новый batch скринов прибыл → добавь под § A решения по нему + новые open questions в § B.
3. Что-то решено как out-of-scope → § C.
4. Ожидаемый batch получен → удали из § D, добавь в § A где описано принятие.
5. Обновляй header `Updated:` дату.

Дизайнер / PM / sponsor читают § A (что есть) + § B (что нужно ответить) + § D (что они должны прислать). § C и § E — справочно.

---

*Velo project — S2 Sprint planning artifact*
*Format established by decisions.md #041*
