# VELO — Фронтовый Кодекс

**Версия:** 1.13
**Дата:** 6 июля 2026
**Статус:** Active

> **ИСТОЧНИК ДИЗАЙНА (канон, 2026-06):** Figma выведена из источников
> **навсегда**. Источник дизайна каждого экрана — присланный оператором **SVG
> текущего состояния экрана**. Любое UI-значение проходит через DS-токен
> `--velo-*` или DS-компонент; SVG-референс лишь говорит, КАКОЙ токен применить
> (DS-first). Ссылки на Figma-node (`541:…`, `4715-3463` и т.п.), оставшиеся ниже
> в исторических заметках и в таблице техдолга, — артефакты первоначальной
> сборки, НЕ действующий источник.

> **v1.13 (мастер-роль/capability батч T1–T5 + Bug2, 6 июля 2026, база `54bdf0a` — held ahead-8 [эта сессия] поверх задеплоенного `ca66e0e`, НЕ задеплоено; деплой-дельта `ca66e0e..54bdf0a` = 11 коммитов, включая 3 Зода [Z-7 zoom-фабрика · R-1 clear-admin-marker · реген]):**
> — **T4 — апрув даёт CAPABILITY, не роль (ПРОМТ №295, locked call-design):** админ-верификация мастера ставит `status=verified` ТОЛЬКО, роль остаётся `user`. Одобренный заявитель приземляется обратно в юзер-зону; в Настройках («Переключение роли») появляется «перейти в режим мастера» (capability-derived: `derive_allowed_roles` ключит на `status=="verified"`). `roleGuard('master')` держит мастер-зону недостижимой до свитча (не «застрял» — корректно загейчено). `MasterPendingView` детектит одобрение по мастер-capability (`allowedRoles`) для аккаунта role=`user` и рендерит CTA «Одобрено» → `switchRole('master')` → мастер-дашборд на месте; убрана self-serve «Подать новую заявку». Отменяет прежний «апрув флипает роль».
> — **T2 — все юзеры + явная выдача мастера (ПРОМТ №292):** новый экран `AdminUsersView` (все аккаунты) + явная кнопка **«Сделать мастером»** с confirm-модалкой → `POST /admin/users/{id}/make-master` (создаёт/ре-верифицирует профиль + флипает роль=master + чистит admin-home-маркер R-1; 409 `already_master`). Отдельно от апрув-пути T4 (это ЯВНЫЙ админ-грант).
> — **T3 — реальные методы/опыт/био + редактор методов в ревью (ПРОМТ №293):** `AdminMasterReviewView` показывает НАСТОЯЩИЕ методы / опыт / «О себе» (было `—`) через `GET /admin/masters/{id}`→`AdminMasterDetail`; чип-редактор методов прямо в ревью → `PATCH /admin/masters/{id}/methods` (`EditMasterMethodsRequest`, min 1 / max 20). Свободный ввод кастом-метода — follow-up (пока выбор из набора).
> — **T1 — заявка мастера: «Пропустить» документы + «О себе» обязательно (ПРОМТ №288/290):** шаг документов в `MasterApplyView` можно **пропустить** (аплоуд недоступен — honest-skip, не блокирует заявку); поле **«О себе» (bio) сделано обязательным** (было опционально).
> — **T5 — reject-visibility + generic одноразовая инвайт-ссылка (ПРОМТ №298/299):** (a) отклонённый заявитель с role=`user` видит вердикт (причину отказа) на `MasterPendingView` через `GET /me` → `UserResponse.master_application` (`MasterApplicationInfo`); reject-ветка = причина + «Написать в поддержку» (админ пере-выдаёт ссылку). (b) **Инвайт-ссылка стала GENERIC** (заменяет account-bound ID-инвайт из v1.11/№258): админ-экран `AdminMasterInviteView` теряет ввод Telegram ID → одна кнопка **«Создать ссылку»** (без цели); `POST /admin/masters/invite` без тела → Redis `master_invite:{sha256}` без TTL → композит-ссылка. Claim (`MasterInviteClaimView`) → `POST /masters/invite/claim` атомарно гасит токен (GETDEL, first-claim-wins; повторный/неизвестный → 404 `invite_invalid`) → визард заявки; мёртвая ветка `already_master` убрана (applyGuard и так отбивает мастеров). Требует `TELEGRAM_BOT_URL` на сервере (иначе 503). Пре-деплой account-bound ссылки после деплоя не гасятся (Redis-модель) — админ пере-выдаёт.
> — **Bug2 — клэмп списка мастеров (ПРОМТ №289):** запрос списка мастеров в админке ужат до бэкенд-капа страницы **100** (было превышение → 422).
>
> _Известные follow-up'ы (self/later, зафиксированы в `VELO-Backend-Tasks.md`):_ редефиниция consistency-семафора **1.3** (T4 создаёт verified-профиль + role=user → расхождение `role∈{master,admin} == verified profiles`, monitoring-only ALERT на припаркованном DB-integrity экране) · свободный кастом-метод в T3-редакторе · кросс-сессионный persistent-индикатор отказа в юзер-зоне · durable `MasterInvite`-таблица если Redis-эфемерность окажется недостаточной.

> **v1.12 (M3 методы-через-модерацию + языки/e-mail/attention + keyboard-fog VARIANT-3 + участник-X removal, 5 июля 2026, база `87387d4` — held ahead-24 поверх задеплоенного `97cb445`, НЕ задеплоено):**
> — **M3 — методы мастера через админ-модерацию (E19, FLAT-ветка):** «Методы» в edit-profile из locked-чипов → редактируемый плоский набор; смена авто-шлёт change-request (`POST /masters/me/method-change-request`), пока pending — бейдж «Ожидает подтверждения» + примечание (авто-отправка, до 3 раб. дней). Новый админ-экран `AdminMethodRequestsView` («Заявки на смену методов», DS-composed) + вход с админ-дашборда: список pending → одобрить (методы становятся живыми) / отклонить (причина). JSONB `data.profile.method_change_request` (additive, без миграции). Двухуровневая таксономия Направление→Вид из мокапа PE-3 **ОТЛОЖЕНА** (out of scope); M3 = FLAT (оператор F-M3-1=А). Отменяет honest-stub «Методы = locked flat-chip / E19 НЕ построена» из v1.10 §PE-3.
> — **E16 — языки практик:** стаб `langRu`/`langEn` в заявке теперь УХОДИТ (`experience.languages`); на профиле — блок «Языки практик», свободно редактируемый БЕЗ модерации (`PATCH /masters/me/languages`, Q2=А); `MasterProfileResponse.languages`, `utils/languages.ts`. Additive JSONB `data.profile.languages`. Закрывает TD-FE-E16-APPLY-LANGS.
> — **E11 — e-mail юзера:** поле e-mail в edit-profile из disabled-заглушки «появится позже» → редактируемое; `UserResponse.email` / `UserUpdate.email` (credentials JSONB, паттерн phone/bio, «» очищает; без колонки/миграции). Self-built в users/ (Zod-лейн E8) — additive, remote-cold, reconcile-before-push обязателен.
> — **E1 — фильтр «Требуют внимания»:** `getMasterReviews(…, attention)` + `AnalyticsView` тянет `attention=true` (серверный негатив-бакет — бэк уже задеплоен; «нет фильтра» в задачах было устаревшим). Frontend-only.
> — **OT-A — фон при вводе (VARIANT 3):** на fog-экранах при клавиатуре верхний dissolve СОХРАНЯЕТСЯ, убирается только НИЖНИЙ (было: `mask:none` целиком → фон «переключался»); `#app::before` доп-приколот (`min-height:100lvh`, гейт `is-keyboard-open`/`is-field-focused`) против webview-ресайза мандалы. В покое / на non-fog — байт-идентично. Уточняет KB-1…4/SP-2/SP-3.
> — **OT-B — крестик отмены записи убран:** stub-X на ростере детали практики (модалка → тост «недоступно», эндпоинта нет) удалён целиком; строки участников read-only; вернём с remove-participant эндпоинтом (E11).
> — **PACK#1/#2 (U1/U2/U4 · M1/M2/M5-M7):** honest-disable master-request на BookingConfirmed; фикс «Вчера»-даты (`dayLabelOf`→format.ts); no-show reflection flow (`ReflectionView` на стабе); чат-композер над клавиатурой (fill); keyboard-scroll settle; short-fog / form-fog-top-hard токены; снят мёртвый `solid` VHeader-вариант.

> **v1.11 (capability-роль-свитч + E15 end-to-end + честный вход мастера + инвайт-ссылка + Batch-STRIP + zoom-мини-фиксы, 3 июля 2026, база `d01f6f9` [Zod-батч zoom-гейт/setrole] + held-батч №255-263, НЕ задеплоено):**
> — **Zoom-мини-фиксы (№263, pre-push):** owner-CRUD-ответы (create/update/delete/cancel в `practices/router.py`) отдают СВОЙ `zoom_link` (передан `zoom_link_visible=True`) — консистентно с owner-always-sees (M-3/Z-6); кнопка «Zoom» на юзер-дашборде `:disabled` без валидной ссылки (честное состояние вместо мёртвого клика); карточка ZOOM в детали практики — честный текст «доступна после записи» вместо ложного «за 10 минут до начала» (reveal привязан к статусу брони, не к таймеру).
> — **Batch-STRIP (№260, operator-locked «тест==прод»):** тестер-скаффолдинг УДАЛЁН из кода целиком — `ui.forceOnboarding` (повтор онбординга на свитч: сигнал, `App.vue`-watcher, dashboard-`forced`) и `ui.previewApplyFlow` (5-экранное превью заявки: сигнал, `PREVIEW_ROUTE_NAMES`, ветки в `applyGuard`/`masterPendingGuard`/`beforeEach`/Landing/Apply/Pending, кнопка «Просмотреть экраны заявки»). `shouldShowMasterOnboarding` без `forced` — единственный триггер онбординга = естественный прод-путь. **Ruling по находке №259:** свитч в проде = НАМЕРЕННАЯ прод-фича (theme A); `RoleSwitchSection` переименован «Режим тестировщика» → **«Переключение роли»** (только strip+retitle, без рестайла; финальный вид — device-eyeball оператора).
> — **Role-switch = capability-derived (A1=Б); флаг `ROLE_SWITCH_ENABLED` УДАЛЁН (F1=А, `15d5b0d`):** `POST /users/me/role` всегда включён; целевые роли выводит `derive_allowed_roles()` (users/schemas.py — single source of truth и для write-пути, и для блока `role_switch` в `GET /me`): `{USER}` всегда · +`MASTER` при ВЕРИФИЦИРОВАННОМ мастер-профиле · админ (текущая роль ИЛИ server-side маркер `credentials.role_switch.home_role="admin"` — round-trip ушедшего в user/master админа; ставится при уходе, чистится при возврате) — все три. НЕ-админ НИКОГДА не получает admin (только CLI/DB — `velo setrole`). Старые seeded `allowed_roles` МЕРТВЫ (403). Старый 409 `master_profile_required` упразднён — не-capability цель = обычный 403 `role_not_allowed`. `RoleSwitchSection` рендерится по прежнему условию (непустой `allowedRoles`), но это теперь capability, а не тест-флаг. **Ruling (№260):** прод-видимость свитча = намеренная фича; секция → «Переключение роли», превью-строка удалена (см. Batch-STRIP выше, §3.3).
> — **E15 закрыт end-to-end:** `master_onboarding_completed` персистится бэком (credentials JSONB, PATCH-whitelist `_JSONB_CREDENTIAL_FIELDS`), типизирован в `generated.ts` (hand-add до регена: `UserResponse.master_onboarding_completed: boolean` + `UserUpdate.master_onboarding_completed?: boolean | null`), `persistMasterOnboarding()` пишет плоским PATCH без каста. Карусель мастера больше НЕ пере-показывается на новой сессии/устройстве. TD-FE-E15 закрыт (§10).
> — **Честный вход мастера без профиля (№257, Q4=А):** `get_current_master` теперь отдаёт различимые 403-коды `master_profile_not_found` / `master_profile_not_verified`; стор `master.profileMissing` взводится ТОЛЬКО по коду (transient network error НЕ роутит в визард); подтверждённый no-profile мастер (например, админ после свитча) → `/master/apply` (dashboard — новый `masterNoProfileGuard`; sub-routes — первый чек в `masterStatusGuard`); pending/rejected/suspended → `/master/pending` байт-идентично прежнему.
> — **Batch-INVITE (№258, C1=Б/TTL=В/F2=А):** одноразовая инвайт-ссылка мастера. Админ: «Мастера» → кнопка «Пригласить мастера» → экран `admin-master-invite` (VInput Telegram ID, inline-404 «должен один раз открыть бота», 409-toast) → `POST /admin/masters/invite` → полная ссылка `<bot_url>?startapp=master_onboarding__<token>` + «Скопировать» (B2) + подпись «одноразовая · действует до погашения». Хранение: ТОЛЬКО sha256 в `credentials.master_invite` (server-written, не PATCHable); re-issue перезаписывает (старая ссылка умирает); срока нет. Приглашённый: диплинк-kind `master_onboarding__<token>` (парсер `useAuth.parseStartParam`) → `/master/invite/:token` (`MasterInviteClaimView`, [applyGuard]) → claim `POST /masters/invite/claim` (структурная привязка к СВОЕМУ аккаунту, constant-time, consume single-use) → существующий визард заявки + админ-апрув; ошибка (чужая/погашенная/битая) → честный экран с выходом.
> — **Опер-заметка (№255):** bare `velo seed-practices` теперь требует typed-«yes» перед мегапак-сценарием `default` (~300 практик / 12 мастеров); `--scenario NAME` / `--yes` / `--dry-run` обходят гейт; reset+default = ОДИН объединённый prompt.

> **v1.10 (клавиатура/туман polish + чат fill-режим + focus-freeze фона, 2 июля 2026, база `583e765` — ДВЕ задеплоенные мили `67b95ef`+`583e765`, задеплоено на TEST):**
> — **Focus-freeze фона (SP-3):** `useBackgroundStabilizer` тогглит `html.is-field-focused` на `focusin`/`focusout` текстовых полей; `global.css` морозит `#app::before` (`transform:none`) на этом классе — ДО того как клавиатура-анимация пересечёт `KEYBOARD_VIEWPORT_THRESHOLD` (150px) `is-keyboard-open`, иначе фото «сползает» в окне анимации (сильнее всего на высоких формах вроде Поддержки). Композитится с `is-keyboard-open` (любой класс ⇒ `transform:none`). Только freeze фона включается рано; max-height-кап + снятие маски остаются на 150px-пороге (без преждевременного reflow). Действует на ВСЕ экраны с клавиатурой.
> — **Чат fill-режим (MC-2):** `MasterShell` получил `isFillRoute = route.name==='master-chat'` + `:fill` — per-route opt-in `fill`-режима `MobileLayout` (как дневник в `UserShell`), прочие мастер-роуты байт-идентичны. `MasterChatView` пересобран в 3-слойный layout дневника: `position:relative;height:100%` → absolute internal-scroll тред с собственной верх/низ fog-маской → absolute приклеенный композер (был `position:sticky` — плавал посреди короткого треда). Верхний туман чата теперь во вью (шелл-туман MC-1 снят как мёртвый — `fill` даёт `mask:none`).
> — **Keyboard-scroll (visualViewport) на edit-profile / промокод / поддержку (PE-2c/PC-1/SP-1):** `scrollFieldIntoView` переведён с фикс-300ms на visualViewport-`resize` (центрирует поле по мере открытия клавиатуры, detach на blur; координируется с `is-keyboard-open`, не пишет его shared-state). У textarea поддержки `@focus`-хендлера не было вовсе — добавлен.
> — **Туман (SP-2/PE-2a):** `master-support` возвращён в `FOG_ROUTES` + `CTA_SAFE_FOG_ROUTES` (реверс un-fog #8/#9 — безопасен: маска снимается при вводе, CTA-safe низ держит «Отправить»); `user-edit-profile` добавлен в `UserShell` `FOG_ROUTES` (паритет с мастер-вариантом, стандартный туман БЕЗ белой плашки).
> — **Мастер-профиль (PE-1):** headerless-хаб → `masterProfileFog()` в `MasterShell` подаёт отрицательный top-gap (токен `--velo-fog-mp-top-gap`) через существующий per-screen fog-API; `MobileLayout`/`HEADER_FALLBACK` НЕ тронуты.
> — **edit-profile ещё (PE-4/PE-3):** авто-скролл поля «УДАЛИТЬ» в модалке удаления при появлении; «Методы» = честный locked flat-chip показ (полная таксономия Направление→Вид + change-request + admin-approval + «Ожидает подтверждения» = бэк **E19**, НЕ построена — no-fake).
> — **Первая миля `67b95ef` (тоже живая):** live-aware «Ближайшие практики» юзер-дашборда (`utils/nearestBookings.ts` — pin идущей + до 2 предстоящих), **KB#4-композит** (freeze фото + снятие тумана при вводе + reset на смене роута), №233 (компактный нижний туман форм + full-width `UseTemplateBlock` + тонкий скролл-thumb), фронт-провязка E18/E14/E1/E10 (Zoom/причина отказа/отзыв→ученик/промокоды). **AN-1** — рейтинг-% центрирован в пилюлях аналитики.

> **v1.9 (мастер-зона polish + клавиатура-aware viewport + User «Сообщения», 30 июня 2026, база `00bb5f2`, батч ahead-22, push held):**
> — **Клавиатура-aware viewport** (`e95e05a`): `useBackgroundStabilizer` публикует ВЫСОТУ visual-viewport в `--velo-vvh` + тогглит `html.is-keyboard-open` (порог `KEYBOARD_VIEWPORT_THRESHOLD`); гейтнутые правила `global.css` ужимают скролл-контейнер `.mobile-layout__main` и модалки `.v-modal__*` до `--velo-vvh` ТОЛЬКО при открытой клавиатуре (at-rest байт-идентично). Плюс прежний job#1 «танцующий фон» — counter-translate `#app::before` на `--velo-bg-shift = visualViewport.offsetTop`.
> — **Аналитика рестайл (AN-1…7):** бейджи рейтинга в карточках прошедших практик — на всю ширину карты; «Требуют внимания» — крупная иконка-идентификатор (confused «?») вместо аватара + мета = только название практики; «Отзывы о практике» — иконка-рейтинг как идентификатор слева, без даты/подписи. **Из `VRatingBadges` ПОЛНОСТЬЮ удалён механизм «?»-подсказки** (sheet «Оценки участников» больше не существует).
> — **Мастер-туман (FOG-1/FOG-2):** `master-edit-profile` + `master-language-timezone` добавлены в `FOG_ROUTES`; `master-practice-detail` получил собственный мастер-тюнинг (`practiceDetailFog` — мягкий верх + компактный низ через `--velo-fog-list-z3/z4`, юзер-practice-detail не тронут).
> — **Дашборд (DB-1/DB-2):** карточка «Ближайшие практики» — паритет меты со списком практик (чек-ины/регулярность/осталось занятий) через НОВЫЙ общий `utils/practiceCardMeta.ts` (вынесен из `MasterPracticesView`); подтянут верхний отступ.
> — **Профиль (PR-1/PR-2):** подтянут верхний отступ мастер-профиля; `@focus`-скролл на textarea «О себе» (band-aid семейства e95e05a).
> — **User «Сообщения» (`0b8ef14`):** в Профиль ▸ «Аккаунт» добавлена строка «Сообщения» → `UserMessagesView` (роут `user-messages`) — honest empty-state (НЕТ фейковых тредов; swap-точка под реальный список, когда придёт API). Бэк-гэп — E4 в `VELO-Backend-Tasks.md`.
> — **Также в батче (косметика):** снятие solid-плашки + туман на 3 формах мастера (promocode/create/edit), редизайн `UseTemplateBlock` + recurrence-UX «Новой практики» (NP), рестайл «Практики/Прошедшие» (CP/EP/PD/PP), фикс UTC-даты `todayLocalISO()` в `utils/format.ts`.

> **v1.8 (Мастер-программа + TEST-only превью заявки, 29 июня 2026, база `00bb5f2`):**
> построена и задеплоена мастер-программа (DS-first, honest-stub):
>
> - **Онбординг мастера** — пост-апрув карусель `MasterOnboardingView` (full-screen
>   overlay на дашборде через `Teleport`; гейт `master_onboarding_completed` = Zod
>   **E15**, читается defensive-каст — флаг ещё не в `generated.ts`).
> - **Заявка мастера — рестайл** — `MasterApplyView` (3 шага Профиль/Опыт/Документы;
>   honest-стабы: загрузка файлов = Zod **E13**, язык практик = Zod **E16**).
> - **Вердикт-экраны** — `MasterPendingView` отправлена / одобрено / отказ
>   (generic-причина отказа до Zod **E14**).
> - **`VPaginationDots`** (DS-точки) + токены `--text-28`/`--text-46` + `VeloLogo`
>   вариант `lockup`.
> - **Phase A parked-auth** — `LandingView`/`LoginView`/`RecoverPassword{Request,Set}View`
>   + спящие незалинкованные `/auth/*` маршруты (web-auth-бэкенд = Zod **E17**; в
>   Telegram недостижимы — `App.vue` рендерит StandaloneStubView для браузера).
> - **TEST-only повтор онбординга на role-switch** (`ui.forceOnboarding`) и **TEST-only
>   5-экранное превью заявки** (`ui.previewApplyFlow`, `ffca7a0`) — оба
>   **прод-недостижимы**: единственная точка входа — `RoleSwitchSection`, который
>   рендерится только при непустом `allowedRoles` (= `ROLE_SWITCH_ENABLED` на TEST).
> - Фикс клиент-валидации условий окончания серии в `CreatePracticeView`
>   (until_date / after_count / weekday). E7 период-статы мастера подключены
>   (`getMasterStats`); E8 уведомления — контракт частично (лента/воркер открыты).
>
> Зоны Мастер + Админ — живые на TEST; зона Пользователь — припаркована. Детали
> мастер-программы — §3.8; TEST-only гейты — §2.2/§2.3; стабы — §10.

> **v1.7 (DS-rebuild ролей Мастер/Админ + фронт-wiring E1/E2/E5/E9, 17 июня 2026):**
> зоны **Мастер и Админ пересобраны на дизайн-систему** (операторские SVG) и
> **подключены к реальному бэку** (волна Zod `0038566`):
>
> - **E1** именованные отзывы — `PracticeReviewsView` + PAST-ветка
>   `MasterPracticeDetailView` (`getPracticeReviews`).
> - **E2** финансы мастера — `AnalyticsView` «Платежи» (доход за период с
>   `delta_pct` + лента транзакций) и доход-стат на `MasterDashboardView`
>   (`getIncome`/`getTransactions`).
> - **E5** ученики/CRM — `MasterStudentsView` + `MasterStudentProfileView`
>   (`getStudents`/`getStudent`; имя/аватар в детали).
> - **E9** админ-надзор — метрики вовлечённости (check-in/feedback/return),
>   практики (лист + детали + ростер) и выручка (`AdminCheckinRateView` /
>   `AdminFeedbackRateView` / `AdminReturnRateView` / `AdminPracticesView` /
>   `AdminPracticeDetailView` / `AdminRevenueView` + карточки `AdminDashboardView`).
>   Сид с платными практиками → финансы/выручка показывают реальные суммы.
> - DS-shell: `hideTabBar` на drill-in роутах, fog-режим, `VSegmentTrack`
>   (track+thumb сегмент), новый общий `VRatingBadges` (трио fire/good/confused —
>   §3.1). Деньги — `formatMoney(cents, 'EUR', 'ru', true)` (валюта канон €).
> - Незакрытые эпики (Zod в работе): **E7** (period-дельты метрик), **E4**
>   (сообщения), **E3/E6** — соответствующие контролы = честные стабы.
>
> **Зоны ролей сейчас:** Мастер + Админ — живые, data-driven на TEST. Зона
> **Пользователь — припаркована** (рабочая, не в активной переработке).
> Бэкенд-контракты — `@/api/types` (реэкспорт автогена `generated.ts`).

> **История (v1.4–v1.6, май 2026):** USER-зона — флоу Календарь (стор
> `calendar.ts`, мульти-фасетные `PracticeFilters`), Calendar flow 4-7 +
> публичный профиль мастера (`MasterPublicView`, `BookingConfirmedView`,
> `VAvatar`), раздел Профиль (`LanguageTimezoneView`/`EditProfileView`/
> `NotificationsView`, `VSwitch`). i18n в проекте по-прежнему НЕТ (язык — задел).
> Детали — §3.5–3.7, §10.

---

## 1. Архитектура

### 1.1. Одно SPA — три роли

Единое приложение с ролевым роутингом. Роль определяется из `GET /api/v1/users/me`
после авторизации. Каждая роль имеет свой Shell (layout-обёртку) и Tab Bar.

| Роль     | Shell         | Tab Bar                                                                              |
| -------- | ------------- | ------------------------------------------------------------------------------------ |
| `user`   | `UserShell`   | IconHome Дашборд / IconCalendar Календарь / IconDiary Дневник / IconProfile Я        |
| `master` | `MasterShell` | IconHome Дашборд / IconPractices Практики / IconBrain Аналитика / IconProfile Я      |
| `admin`  | `AdminShell`  | IconDashboard Дашборд / IconGroup Мастера / IconModeration Модерация / IconProfile Я |

Мастер и Админ имеют доступ к user-интерфейсу через переключение режима (см. TD-FE-ROLE-SWITCH).

### 1.2. Платформенная абстракция

Приложение работает в двух средах. Различия инкапсулированы в `src/platform/`:

| Файл                     | Назначение                                                         |
| ------------------------ | ------------------------------------------------------------------ |
| `platform/types.ts`      | Интерфейс `Platform` (общий контракт)                              |
| `platform/telegram.ts`   | Реализация для Telegram WebApp SDK                                 |
| `platform/standalone.ts` | Заглушки для браузера (Phase F10)                                  |
| `platform/index.ts`      | Автодетект: `window.Telegram?.WebApp` → telegram, иначе standalone |

Интерфейс `Platform`:

```typescript
interface Platform {
  name: "telegram" | "standalone";
  init(): Promise<void>;
  getInitData(): string | null;
  getTheme(): "light" | "dark";
  hapticFeedback(type: string): void;
  showBackButton(cb: () => void): void;
  hideBackButton(): void;
  openLink(url: string): void; // external link: Telegram WebApp.openLink / window.open(noopener)
  close(): void;
}
```

MVP работает только в Telegram. Standalone — Phase F10.

`openLink` добавлен для экрана Practice-Live (кнопка "Войти" в Zoom). В Telegram —
`WebApp.openLink(url)`, в standalone — `window.open(url, '_blank', 'noopener')`.

### 1.3. Структура проекта

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts          -- Base fetch обёртка, 401 handler
│   │   ├── generated.ts       -- Auto-generated from backend OpenAPI (DO NOT EDIT)
│   │   ├── types.ts           -- Re-export from generated.ts + frontend-only types
│   │   ├── utils.ts           -- buildQuery() и прочие shared helpers
│   │   ├── auth.ts            -- POST /auth/telegram, logout
│   │   ├── users.ts           -- GET/PATCH /users/me
│   │   ├── practices.ts       -- CRUD практик, finalize, attendance
│   │   ├── bookings.ts        -- Бронирования, purchase, waitlist
│   │   ├── payments.ts        -- Topup
│   │   ├── masters.ts         -- Apply, profile, payout, withdrawals
│   │   ├── diary.ts           -- Check-ins, feedbacks, entries, insights, listDiaryFeed (cursor)
│   │   └── admin.ts           -- Stats, verify, reports, consistency
│   │
│   ├── components/
│   │   ├── ui/                -- Примитивы (V-префикс)
│   │   │   ├── icons/         -- SVG-иконки из Design_prototype (Vue-компоненты)
│   │   │   └── index.ts       -- Barrel export всех UI-компонентов
│   │   ├── layout/            -- Shell-компоненты, VHeader, VTabBar
│   │   └── shared/            -- Доменные: PracticeCard, BookingCard...
│   │
│   ├── composables/
│   │   ├── useAuth.ts         -- Login/logout flow + waitUntilReady()
│   │   ├── usePagination.ts   -- Пагинация + infinite scroll (offset)
│   │   ├── useCursorPagination.ts -- Курсорная пагинация (Diary feed: {items,next_cursor})
│   │   ├── useToast.ts        -- Всплывающие уведомления
│   │   └── useForm.ts         -- Валидация форм
│   │
│   ├── platform/              -- Платформенная абстракция (см. 1.2)
│   │
│   ├── router/
│   │   ├── index.ts           -- Маршруты + beforeEach guard
│   │   ├── guards.ts          -- roleRedirect, roleGuard, masterStatusGuard
│   │   └── tabs.ts            -- USER_TABS, MASTER_TABS, ADMIN_TABS
│   │
│   ├── stores/
│   │   ├── auth.ts            -- user, token, role, isAuthenticated
│   │   ├── practices.ts       -- list, filters, selected
│   │   ├── calendar.ts        -- Calendar screen: week load, selected day, facet filters (Calendar iteration)
│   │   ├── bookings.ts        -- my bookings
│   │   ├── balance.ts         -- balance_cents, operations
│   │   ├── master.ts          -- master profile, practices, finance
│   │   └── diary.ts           -- unified cursor feed (feedItems/filters), submit checkin/feedback, entry CRUD, insights cache
│   │
│   ├── styles/
│   │   ├── variables.css      -- Дизайн-токены (единственный источник цветов)
│   │   └── global.css         -- Reset, typography, Google Fonts
│   │
│   ├── utils/
│   │   ├── format.ts          -- formatMoney, formatDate, formatDateShort
│   │   ├── currency.ts        -- eurStringToCents, centsToEurString
│   │   ├── displayHelpers.ts  -- MOOD_*/RATING_*/PRACTICE_TYPE_* + DIRECTION/DIFFICULTY/DURATION_BUCKET/TIME_OF_DAY (Calendar)
│   │   ├── adminHelpers.ts    -- Хелперы форматирования для admin-вью
│   │   ├── commission.ts      -- COMMISSION_RATE константа
│   │   └── practiceOptions.ts -- DURATION_OPTIONS, TIMEZONE_OPTIONS, DIRECTION_OPTIONS, DIFFICULTY_OPTIONS
│   │
│   └── views/
│       ├── auth/              -- LoadingView, StandaloneStubView, WelcomeView, OnboardingView
│       ├── shells/            -- UserShell, MasterShell, AdminShell
│       ├── user/              -- Dashboard, Calendar, Diary, Profile...
│       ├── master/            -- Dashboard, Practices, Analytics, Profile...
│       └── admin/             -- Dashboard, Masters, Reports, Consistency...
│
├── public/
│   ├── js/telegram-web-app.js -- Локальная копия Telegram SDK (CDN заблокирован ТСПУ)
│   ├── bg/                    -- Фоновое изображение VELΘ (background.png)
│   ├── icons/                 -- PWA иконки + логотипы VELΘ (logo.svg, logo-white.svg)
│   └── manifest.json          -- PWA manifest
├── Dockerfile
└── package.json
```

---

## 2. Роутинг

### 2.1. Все маршруты

```
/                           → roleRedirect (→ /user/dashboard, /master/dashboard, /admin/dashboard)
/loading                    → LoadingView

-- User --
/user/dashboard             → UserDashboardView
/user/calendar              → CalendarView
/user/diary                 → DiaryFeedView             (name: user-diary -- единая лента-нить, экран 40; шелл в fill-режиме)
/user/diary/entry/:id       → EntryView                 (name: user-diary-entry)
/user/diary/:type(checkin|feedback)/:id → DetailView    (name: user-diary-detail)
/user/profile               → UserProfileView
/user/profile/language-timezone → LanguageTimezoneView  (name: user-language-timezone -- Профиль, экран F)
/user/profile/edit          → EditProfileView            (name: user-edit-profile -- Профиль, экраны C+D)
/user/profile/notifications → NotificationsView          (name: user-notifications -- Профиль, экран E)
/user/practices/:id         → PracticeDetailView         (name: practice-detail)
/user/masters/:id           → MasterPublicView           (name: user-master-public)
/user/booking-confirmed/:practiceId → BookingConfirmedView (activeTab: Календарь)
/user/practice-live/:practiceId → PracticeLiveView      (name: practice-live -- экран 14, live-сессия + Zoom)
/user/bookings              → MyBookingsView
/user/ai-summary            → AiSummaryView              (name: user-ai-summary -- экран 16, заглушка, ждёт AI-бэк юзера)
/user/checkin/:practiceId   → CheckinView
/user/feedback/:practiceId  → FeedbackView
/user/topup                 → TopupView
/user/topup/success         → TopupSuccessView
/user/topup/cancel          → TopupCancelView

-- Master -- (MasterShell, beforeEnter roleGuard('master'))
/master/dashboard           → MasterDashboardView   [masterNoProfileGuard, v1.11] (+ пост-апрув онбординг-overlay §3.8)
/master/practices           → MasterPracticesView          [masterStatusGuard]
/master/practices/new       → CreatePracticeView           [masterStatusGuard, hideTabBar]
/master/practices/:id       → EditPracticeView             [masterStatusGuard, hideTabBar]
/master/practices/:id/attendance → AttendanceView          [masterStatusGuard, hideTabBar]
/master/practices/:id/detail → MasterPracticeDetailView    [masterStatusGuard, hideTabBar]
/master/practices/:id/roster → AttendanceRosterView        [masterStatusGuard, hideTabBar]
/master/analytics           → AnalyticsView
/master/analytics/practice/:id → PracticeReviewsView       [masterStatusGuard, hideTabBar]
/master/profile             → MasterProfileView
/master/profile/edit        → EditProfileView (reuse)      [hideTabBar]
/master/profile/notifications → MasterNotificationsView    [hideTabBar]
/master/profile/language-timezone → LanguageTimezoneView   [hideTabBar]
/master/support             → MasterSupportView            [hideTabBar]
/master/messages[/:id]      → MasterMessagesView / MasterChatView   [hideTabBar; чат (master-chat) в fill-режиме — MC-2, как /user/diary]
/master/promocodes[/new]    → MasterPromocodesView / MasterNewPromocodeView  [hideTabBar]
/master/finance             → MasterFinanceView            [masterStatusGuard, hideTabBar]
/master/students[/:id]      → MasterStudentsView / MasterStudentProfileView  [masterStatusGuard, hideTabBar]
/master/summary             → MasterSummaryView            [masterStatusGuard, hideTabBar]
-- standalone (вне MasterShell) --
/master/apply               → MasterApplyView              [applyGuard]
/master/invite/:token       → MasterInviteClaimView        [applyGuard] (v1.11: claim одноразового инвайта → визард заявки; standalone, вне шелла)
/master/pending             → MasterPendingView            [masterPendingGuard]

-- Admin -- (AdminShell, beforeEnter roleGuard('admin'))
/admin/dashboard            → AdminDashboardView
/admin/masters[/:id]        → AdminMastersView / AdminMasterReviewView
/admin/masters/invite       → AdminMasterInviteView  (v1.11: «Пригласить мастера», объявлен ДО masters/:id — литерал выигрывает)
/admin/reports[/:id]        → AdminReportsView / AdminReportDetailView
/admin/consistency          → AdminConsistencyView
/admin/profile              → AdminProfileView
/admin/metrics/check-in     → AdminCheckinRateView
/admin/metrics/feedback     → AdminFeedbackRateView
/admin/metrics/return       → AdminReturnRateView
/admin/revenue              → AdminRevenueView
/admin/participants         → AdminParticipantsView
/admin/practices[/:id]      → AdminPracticesView / AdminPracticeDetailView
/admin/withdrawals[/:id]    → AdminWithdrawalsView / AdminWithdrawalDetailView

-- Parked Phase A web-auth (DORMANT + UNLINKED; недостижимы в Telegram, ждут Zod E17) --
/auth/landing               → LandingView
/auth/login                 → LoginView
/auth/recover               → RecoverPasswordRequestView
/auth/recover/reset         → RecoverPasswordSetView

/auth-error                 → LoadingErrorView
/404                        → NotFoundView
/:pathMatch(.*)             → redirect /404
```

> **Превью заявки — УДАЛЕНО (№260 Batch-STRIP).** Кнопка «Просмотреть экраны заявки»,
> сигнал `ui.previewApplyFlow` и все превью-ветки гардов/вью вынуты из кода — путь заявки
> проверяется только настоящим флоу (тест==прод).

### 2.2. Guards

| Guard                 | Логика                                                                                         |
| --------------------- | ---------------------------------------------------------------------------------------------- |
| `roleRedirect`        | Редирект `/` на dashboard по роли. `async` — ждёт `waitUntilReady()` перед чтением `auth.role` |
| `roleGuard('master')` | Пропускает master + admin, остальных → `/user/dashboard`                                       |
| `roleGuard('admin')`  | Пропускает только admin → `/user/dashboard`                                                    |
| `masterStatusGuard`   | v1.11: сперва общий чек no-profile (`master.profileMissing` по 403-коду `master_profile_not_found` → `/master/apply`); дальше как раньше — не-verified → `/master/pending` |
| `masterNoProfileGuard` | v1.11 (№257): на `/master/dashboard` — подтверждённый no-profile мастер → `/master/apply` (честный вход вместо немого дашборда); pending/rejected остаются на дашборде байт-идентично |
| `applyGuard`          | Верифицированный мастер не может повторно подать заявку (также на `/master/invite/:token`). (Превью-ветка удалена — №260) |
| `masterPendingGuard`  | Гейтит standalone `/master/pending`: admin → `/admin/dashboard`; master → пропуск; user с маркером `MASTER_APPLIED_KEY` → пропуск; иначе → `/user/dashboard`. (Превью-ветка удалена — №260) |

**`beforeEach` (global guard):**

Блокирует `/user/dashboard` для мастера/админа (редирект на свой dashboard), КРОМЕ случая
`uiStore.uiMode === 'user'` — мастер/админ, сам выбравший user-режим, проходит (реализовано).
(Превью-сброс `ui.previewApplyFlow`, живший в этом же `beforeEach`, удалён вместе со всем
превью-скаффолдингом — №260 Batch-STRIP.)

### 2.3. Auth инициализация

`waitUntilReady()` в `composables/useAuth.ts` — `Promise`, который резолвится когда `restoreSession()` завершён (или по таймауту 10s). Используется в `roleRedirect` и `beforeEach` чтобы не читать `auth.role` до готовности сессии.

**Шлюз входа в `App.vue` (welcome + onboarding).** После успешной авторизации
`App.vue` не сразу рендерит `RouterView`, а проходит через локальную машину
состояний `stage: 'welcome' | 'onboarding' | 'app'` (обычный `ref`, вне роутера —
консистентно с тем, как LoadingView/StandaloneStubView гейтят доступ):

```
!isReady                       -> LoadingView
isStandalone || !isAuthenticated -> StandaloneStubView
иначе по stage:
  'welcome'    -> WelcomeView      (показывается всем, при каждом открытии)
  'onboarding' -> OnboardingView   (только новым: onboarding_completed === false)
  'app'        -> RouterView
```

Переходы:

- WelcomeView `@enter` ("Войти"): `onboarding_completed === true` -> `stage='app'`;
  иначе -> `stage='onboarding'`.
- OnboardingView `@done` (завершил или пропустил; флаг уже сохранён в нём самом
  через `authStore.updateProfile({ timezone, onboarding_completed: true })`) -> `stage='app'`.
- WelcomeView `@create-account`: только standalone/браузерная сборка (F10); в Telegram
  кнопка скрыта (`v-if="isStandalone"`).

**Продуктовое решение:** Welcome показывается при каждом открытии приложения, для всех
(перезагрузка = новый запуск = снова Welcome). `stage` живёт в памяти компонента, не в
роутере и не персистится. Онбординг-карусель новый юзер видит один раз — после успешного
финиша флаг `onboarding_completed` остаётся `true` (переживает релогин, см. Бэковый
Кодекс 3.7), и при следующем "Войти" он идёт сразу в `app`.

Файлы: `views/auth/WelcomeView.vue` (экран 01), `views/auth/OnboardingView.vue`
(экраны 05-08: 3 интро + шаг таймзоны), `App.vue` (машина состояний).

**Повтор онбординга на свитч — УДАЛЁН (№260 Batch-STRIP).** Сигнал `ui.forceOnboarding`,
`App.vue`-watcher и `forced`-параметр гейта вынуты из кода. Онбординги живут только на
естественных прод-триггерах: user — по `onboarding_completed` (welcome-флоу), master — по
`master_onboarding_completed` (E15, §3.8).

---

## 3. Компоненты

### 3.1. UI-примитивы (src/components/ui/)

Источник истины — барель `src/components/ui/index.ts`. Текущий набор:

| Компонент                                    | Ключевые пропсы / назначение                                                                                                                                                                                                  |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `VButton`                                    | `variant` (primary/secondary/ghost/outline/danger), `size`, `block`, `disabled`, `loading`                                                                                                                                    |
| `VBackButton` / `VMoreLink`                  | кнопка «назад» / строка-переход «подробнее»                                                                                                                                                                                   |
| `VInput` / `VTextarea` / `VSelect`           | поля формы (`label`, `placeholder`, `options`, `error`)                                                                                                                                                                       |
| `VSwitch` / `VCheckbox` / `VRadioGroup`      | on/off pill · квадратный чек · группа радио                                                                                                                                                                                   |
| `VDayPicker` / `VWheel`                      | выбор дня · колесо (дата/время пикеры)                                                                                                                                                                                        |
| `VBottomSheet` / `VModal` / `VConfirmDialog` | нижний лист · модалка · диалог подтверждения                                                                                                                                                                                  |
| `VCard`                                      | slot, `clickable`, `padding`                                                                                                                                                                                                  |
| `VBadge` / `VTag` / `VChip`                  | статус-бейдж · категориальный pill (blue/pink/sand) · чип-фильтр                                                                                                                                                              |
| `VAvatar`                                    | `name`, `url`, `size` (sm/md/lg/xl) — фото или инициалы                                                                                                                                                                       |
| `VLoader` / `VEmptyState` / `VToast`         | спиннер · пустое/ошибка состояние · тосты (`useToast()`)                                                                                                                                                                      |
| `VStatCard`                                  | `value`, `label`, `delta`, `deltaTone` (up/muted), `valueTone`                                                                                                                                                                |
| `VProgressRow` / `VRatingBar`                | строка-прогресс (label+трек+%) · бар распределения оценок                                                                                                                                                                     |
| `VRatingBadges`                              | **трио fire/good/confused %** (DS, извлечён 2026-06). Пропы `fire`/`good`/`confused` (percent) + `size` (`sm` icon 14 / `lg` icon 16). Заменил дублированный inline-trio в Analytics / MasterPractices / MasterPracticeDetail |
| `VMetricHero` / `VBarChart`                  | hero-метрика (admin) · недельный бар-чарт                                                                                                                                                                                     |
| `VListRow`                                   | строка списка (`title`/`subtitle` + слоты `#lead`/`#trailing`)                                                                                                                                                                |
| `VSegment` / `VSegmentTrack`                 | сегмент 2-pill · сегмент track+thumb (variant `tabs`/`toggle`)                                                                                                                                                                |
| `VMenu` / `VMenuItem` / `VMenuRow`           | «…»-меню (popover) + его строки                                                                                                                                                                                               |
| `VAccordion`                                 | `title` — раскрывающаяся строка                                                                                                                                                                                               |
| `VeloLogo`                                   | `size`, `variant` (default/white/**lockup**) — `<img>` из `public/icons/` (lockup = знак+слово, Phase A Landing)                                                                                                                                                                |

**Новое (v1.8):** `VPaginationDots` — DS-точки пагинации для онбординг-каруселей (юзер +
мастер) и визарда заявки. Пропы `total` / `active`: активная точка 13×13, неактивные 7×7.
Ретрофитнут на обе карусели (заменил локальные пилюли-индикаторы).

**Иконки** (`src/components/ui/icons/`): SVG-компоненты из `Design_prototype/assets/icons/`. Все принимают проп `size?: number` (default 24). Используются в `VTabBar` через `TabItem.icon: string | Component`.

**Доменные иконки** (`src/components/icons/`, barrel `index.ts`): отдельный набор Vue-компонентов
для контентных экранов (НЕ путать с табовыми из `ui/icons/`). Все: `fill="currentColor"`,
проп `:size` (default 24). Цветные mood-иконки используют `useId()` для уникальных id градиентов.

| Иконка                                                                                                  | Назначение                                                                                    |
| ------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `IconMeditation` / `IconBreathwork`                                                                     | тип практики (meditation -- круг teal-аватар; breathwork -- эвристика по заголовку, см. ниже) |
| `IconCalendar` / `IconClock`                                                                            | мета практики (дата / длительность)                                                           |
| `IconBrain`                                                                                             | AI-блок / экран AI-саммари                                                                    |
| `IconCheck`                                                                                             | success-галочка (экран 13), verified-бейдж мастера                                            |
| `IconArrowRight`                                                                                        | "Подробнее" в MasterCard                                                                      |
| `IconClose`                                                                                             | крестик закрытия (попапы)                                                                     |
| `IconMoodLow` / `IconMoodMid` / `IconMoodHigh`                                                          | цветные mood-лица для check-in (экран 12)                                                     |
| `IconHome` / `IconGroup` / `IconWarning` / `IconRuble` / `IconSuccess` / `IconSupport` / `IconFeedback` | прочие контентные                                                                             |

> **Эвристика типа практики:** в `practice_type` НЕТ значения `breathwork`
> (enum: `live | series | one_on_one | replay`). Иконка дыхания выбирается эвристикой
> по заголовку практики -- это намеренно (см. `BookingCard.typeIcon`).

### 3.2. Layout-компоненты (src/components/layout/)

| Компонент      | Описание                                                                                                                                                                                                                                                                                                                                                                                  |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `VHeader`      | Заголовок с кнопкой назад и action-слотом справа                                                                                                                                                                                                                                                                                                                                          |
| `VTabBar`      | Нижняя навигация, конфигурируется через `items` пропс. Редизайн по Figma: круглые стеклянные "пузыри" 63x63, без подписей (aria-label сохранён). Активная вкладка — растворённый пузырь + `box-shadow: var(--velo-shadow-glow)` (мягкое свечение), различается ТОЛЬКО свечением, не размером. Иконки 27x27 (`fill="currentColor"`). Поле `badge` в интерфейсе оставлено, но не рендерится |
| `MobileLayout` | Header-слот + `<slot>` + VTabBar (user и master). Проп `fill?` (по умолчанию false): в fill-режиме `main` не скроллится сам, а отдаёт полную высоту дочернему вью (для чат-экранов с фиксированным низом — дневник). Включается в UserShell по роуту `user-diary`                                                                                                                         |
| `AdminLayout`  | Аналогично, отдельный для будущего desktop-варианта                                                                                                                                                                                                                                                                                                                                       |

### 3.3. Shared-компоненты (src/components/shared/)

| Компонент              | Описание                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `PracticeCard`         | карточка практики в каталоге                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `PracticeHeroCard`     | hero-шапка практики (иконка teal-круг 46px, title, мета date/duration, проп `participants?`, слот `#badge`). Используется на экранах 15 и 18                                                                                                                                                                                                                                                                                                                                                              |
| `MasterCard`           | карточка мастера (аватар `IconMeditation`-плейсхолдер, имя + `IconCheck` verified, теги `VTag` чередованием `[blue,pink,sand][i%3]`, "Подробнее" → toast "скоро"). Пропы `masterName`, `methods`. Используется на 15 и 18                                                                                                                                                                                                                                                                                 |
| `BookingCard`          | dumb-компонент брони. Пропы `{ booking, badge?, clickable? }` — бейдж считается во вью-родителе (`badgeFor`), сам компонент не содержит бизнес-логики. Экспортит `interface BookingBadge { label; variant }`, `variant: 'live' \| 'today' \| 'tomorrow' \| 'done' \| 'cancelled' \| 'no_show'`                                                                                                                                                                                                            |
| `FormShell`            | общая оболочка форм (header + контент + actions + success-экран). Извлечена из CheckinView/FeedbackView — закрыла WARNING-9 (~200 строк дублей CSS)                                                                                                                                                                                                                                                                                                                                                       |
| `BookingPopup`         | попап бронирования                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `CancelBookingPopup`   | попап отмены брони. Тип пропа структурный: `interface CancellableBooking { practice: { title; scheduled_at } }` — принимает и `BookingWithPracticeResponse`, и `BookingDetailResponse`. Refund deadline 24h. Используется в `PracticeDetailView` (после слияния booking-detail, Батч 6)                                                                                                                                                                                                                   |
| `WeekStrip`            | (Calendar) недельная лента: 7 пилюль ПН-ВС (день+число+точка-маркер), активный день залит `--velo-primary`, стрелки ←→. Dumb: пропы `days/selectedDate/daysWithPractices/localDateKey`, эмиты `select-day/prev-week/next-week`. Пилюли rounded-15 (Figma 44×71), стрелки — inline SVG (в DS нет компонента-стрелки)                                                                                                                                                                                       |
| `CalendarPracticeCard` | (Calendar) карточка практики фида на визуальном языке `BookingCard` (иконка-в-круге 46px, мастер+verified, мета 🗓️/🕐). Бейдж: `is_paid`→«Оплачено» (teal), иначе `is_free`→«Бесплатно» (blue). Проп `practice: PracticeResponse`, эмит `click`                                                                                                                                                                                                                                                           |
| `CalendarFilterModal`  | (Calendar) модалка фильтра на `VModal` (кадр 2). Группы: Направление/Сложность/Тип (мульти-чипы), Длительность/Время (одиночный выбор, 4 корзины времени), Вид практики (свободный `VInput` — см. техдолг). Работает на draft-копии, применяет по «Применить». Пропы `open/filters`, эмиты `apply/close`                                                                                                                                                                                                  |
| `DiaryFeedCard`        | (Diary redesign) карточка события ленты, 3 формы по `kind`: **banner** (бирюзовый для `booking_confirmed`, нейтральный для отмен/переносов), **practice** (белая: practice_outcome — мастер+дата+бейдж Done/Не состоялась, без аватара — TD-DIARY-PRACTICE-AVATAR), **standard** (иконка+заголовок+превью+дата для checkin/feedback/note/dream). Читает `snapshot` защитно. `@tap` эмитит `{ item, editable }` (note/dream → editable). kind→иконка-маппинг локально во вью (utils не импортируют `.vue`) |
| `DiaryComposer`        | (Diary redesign) нижний композер-pill: поле + mic-стаб (toast) + send. Создаёт note через `diaryStore.createEntry`. Стекло: `--velo-glass-blue-15`, backdrop-blur, glow-тень                                                                                                                                                                                                                                                                                                                              |
| `DiaryTimeline`        | (Diary redesign) нить с альтернированием (экран 40, Уровень 2 упрощённый): центральная ось (CSS), дата-узлы по календарным дням в tz юзера, banner/practice по центру, standard чередуются L/R сквозным счётчиком со **сбросом каждый день**, сторона детерминирована позицией (пагинация не перетасовывает). Коннекторы — CSS-штрихи (не Figma-кривые)                                                                                                                                                   |

**`RoleSwitchSection`** (`components/shared/`, v1.8; прод-фича с v1.11/№260) — секция
**«Переключение роли»** в профиле всех трёх ролей. Рендерится при непустом `allowedRoles`,
который выводится capability-политикой бэка (`derive_allowed_roles`: verified-master →
user/master; admin → все три; обычный юзер → пусто/нет секции); флаг `ROLE_SWITCH_ENABLED`
удалён. Содержит ТОЛЬКО кнопки смены роли (свитч → сброс `uiMode` → dashboard целевой роли).
**Ruling №260 (закрывает ОТКРЫТО №259):** прод-видимость для верифицированных
мастеров/админов = намеренная фича (theme A); тестер-обвязка (повтор онбординга + превью
заявки) удалена Batch-STRIP'ом; финальный вид секции — device-eyeball оператора.

### 3.4. Флоу ДАШБОРД (экраны 10–18)

Реализован по операторскому SVG (текущее состояние; Figma выведена — см. шапку). Карта вью:

| Экран                    | View                                                         | Примечания                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ------------------------ | ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 10/11 Dashboard          | `views/user/UserDashboardView.vue`                           | белые карточки `--velo-bg-card-solid`, алерты, карточка ближайшей практики, AI-блок (тоггл Неделя/Месяц + mood). `nearestIsLive` + `openNearest()`: live → practice-live, иначе practice-detail                                                                                                                                                                                                                                                |
| 12/13 Check-in + Success | `views/user/CheckinView.vue` (+ `shared/FormShell.vue`)      | mood-лица `IconMood*`, success `IconCheck`. `onBack()` → `router.back()` (фикс петли 12↔15)                                                                                                                                                                                                                                                                                                                                                    |
| 14 Practice-Live         | `views/user/PracticeLiveView.vue`                            | видео-плейсхолдер, бейдж "● В эфире", "Войти" (`platform.openLink`, дизейбл без `https`-zoom), "Check-in", "Покинуть". Достижим из дашборда при live                                                                                                                                                                                                                                                                                           |
| 15 Practice Detail       | `views/user/PracticeDetailView.vue`                          | каталог + booked + бронь (после Батча 6 — единый экран). Hero/master в `PracticeHeroCard`/`MasterCard`. Поглотил бывший «Бронирование» (экран 18): строка «Статус» (`VBadge` по `myAnyBooking` — любой статус, вкл. cancelled/no_show) и секция ZOOM (только при активной брони). Заголовок «Моя практика» при любой брони; «Забронировать» скрыт для attended/no_show. `myBooking`/`booked` (активные статусы) и check-in/feedback не тронуты |
| 16 AI-summary            | `views/user/AiSummaryView.vue`                               | честная заглушка "в разработке" (`IconBrain`). Персонального AI-саммари юзера на бэке НЕТ                                                                                                                                                                                                                                                                                                                                                      |
| 17 My reservations       | `views/user/MyBookingsView.vue` (+ `shared/BookingCard.vue`) | две секции Предстоящие/Прошедшие. Деление по правилу B (24ч-потолок + статус completed/cancelled, как дашборд), реактивный clock 60с. Бейдж "В эфире" приоритетнее today/tomorrow; live сортируются вверх (`upcomingRank`). Даты в TZ зрителя (`calendarDate(d, tz)` ← `useViewerTimezone`). Тап ведёт на `practice-detail` по `practice_id` (Батч 6)                                                                                          |
| 18 Booking Detail        | — УДАЛЁН (Батч 6)                                            | Бывший `BookingDetailView` слит в экран 15 (`PracticeDetailView`): уникальные «Статус»-строка и ZOOM перенесены туда. Роут `booking-detail` удалён; `MyBookingsView` ведёт на `practice-detail`                                                                                                                                                                                                                                                |

**Бэк-разблокировка:** `PracticeSummary` получил поле `status` (см. Бэковый Кодекс §2)
→ дашборд и список броней показывают бейдж "В эфире" и ведут на `practice-live`
без дополнительного запроса деталей.

---

### 3.5. Флоу КАЛЕНДАРЬ (кадры 1-3, Calendar iteration)

Реализован по операторскому SVG (кадры 1/2/3; Figma выведена — см. шапку). Карта вью:

| Кадр                          | View / компонент                    | Примечания                                                                                                                                                                                                                                |
| ----------------------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 Лента «Календарь»           | `views/user/CalendarView.vue`       | заголовок, `WeekStrip`, контрол «Выбрать практики», секции по дням (`formatDateShort`), `CalendarPracticeCard`, состояния loading/error/empty. Данные из `useCalendarStore`                                                               |
| 2 Модалка «Фильтр»            | `shared/CalendarFilterModal.vue`    | направление/сложность/тип (мульти), длительность/время (одиночный, 4 корзины), вид практики (VInput)                                                                                                                                      |
| 3 «Выбрать практики» раскрыто | часть `CalendarView`                | свёрнуто — пилюля + воронка (→ модалка); развёрнуто — чипы активных фильтров (тап снимает фильтр) + кнопка свернуть. **Вариант 1:** модалка — единственный источник редактирования фильтров, inline-чипы лишь отображают/снимают активные |
| — Индикатор сложности         | `views/user/PracticeDetailView.vue` | точки ●●○ (`DIFFICULTY_DOTS`) + лейбл (`DIFFICULTY_LABEL`) в body детали; показывается только если `practice.difficulty` задан. `PracticeHeroCard` не тронут                                                                              |

**Стор `useCalendarStore`** (`stores/calendar.ts`) — намеренно ОТДЕЛЬНЫЙ от `usePracticesStore`,
чтобы навигация по неделям и фасет-фильтры Календаря не задевали общий фид (Дашборд использует
`usePracticesStore`/`useBookingsStore`). Грузит всю видимую неделю одним запросом
(`date_from..date_to` = локальные Пн..Вс **с буфером ±1 день** — фикс W-2 для экстремальных TZ),
маркеры дней и список выбранного дня выводятся клиентом по `calendarDateInTz` (TZ практики).

**Контракт фильтров:** `PracticeFilters` стал мульти-фасетным — `practice_type` теперь
массив, добавлены `direction[]/difficulty[]/style/duration_bucket/time_of_day`. `buildQuery`
(`api/utils.ts`) сериализует массивы повторяемыми ключами, пустой массив/undefined/null —
пропускает. Старый `CalendarView` (до итерации) был единственным потребителем одиночного
`practice_type` и переработан полностью; Дашборд `practice_type` не использует — не затронут.

### 3.6. Флоу КАЛЕНДАРЬ (кадры 4-7 + профиль мастера, Calendar flow)

Завершение флоу по операторскому SVG (кадры 4-7; Figma выведена — см. шапку). Карта вью:

| Кадр                        | View / компонент                             | Примечания                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| --------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 4 + master profile          | `views/user/MasterPublicView.vue`            | публичный профиль мастера для юзера: hero (`VAvatar xl` + имя + ✓Верифицирован + «N лет опыта» + bio), две стат-карточки (`practices_count`/`reviews_count` с рус. плюрализацией), аккордеон «Методы», «Ближайшие практики» (`getPractices({master_id, status:'scheduled'})`). «Задать вопрос» → toast-заглушка (TD-ASK-MASTER). Роут `user-master-public` (`masters/:id`). Грузит профиль через `getPublicMaster(userId)`; loading/error/not-found через `VEmptyState`; ошибка списка практик не фатальна (отдельный try/catch → `upcoming=[]`) |
| 5 «Практика забронирована!» | `views/user/BookingConfirmedView.vue`        | экран после успешной брони: success-карточка (`IconSuccess` celebration в teal-круге + статичный Zoom-текст), блок «запрос мастеру» (textarea + инфо-баннер + «Отправить запрос» = toast-заглушка, TD-ASK-MASTER), «В календарь» → calendar, «На главную» → dashboard. Роут `user-booking-confirmed` (`booking-confirmed/:practiceId`). Самодостаточен: грузит практику по id в `onMounted` (переживает reload/deep-link). `PracticeDetailView.onPurchased` редиректит сюда                                                                      |
| 6 «Вопрос мастеру»          | — отложен                                    | См. TD-ASK-MASTER: вопросы мастеру — отдельная сквозная фича с бэком. Кадр не реализован                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| 7 Feedback (рейтинг)        | `views/user/FeedbackView.vue`                | emoji-рейтинг (❓👍🔥) заменён векторными иконками из Figma `IconRatingConfused/Good/Fire` (`<component :is>`), цвет каждой через `RATING_ICON_COLOR` (токены `--velo-rating-*`). `RATING_ICON` map — локально во вью (utils не импортируют `.vue`, как `MOOD_ICON` в Checkin)                                                                                                                                                                                                                                                                   |
| 7 Feedback success          | `views/user/FeedbackView.vue` (success-слот) | success-сердце `💚` заменено векторным `IconHeart` (Figma, teal через `--velo-teal-400`) в слоте `#success-icon` FormShell                                                                                                                                                                                                                                                                                                                                                                                                                       |

**Аватары — `VAvatar` (закрыт TD-FE-AVATAR).** Везде, где раньше был плейсхолдер
`IconMeditation`, теперь `VAvatar` (`ui/VAvatar.vue`): показывает фото по `url` или
инициалы из `name`, размеры sm/md/lg/xl. `MasterCard` — `VAvatar lg`, `MasterPublicView`
hero — `VAvatar xl`. Единый паттерн вызова `:url="avatarUrl ?? ''"` + `:name`. Seed-мастер
без Telegram-фото корректно показывает инициалы (ожидаемо, не баг). Бэк отдаёт
`master_avatar_url` в деталях практики (Бэковый Кодекс §3.9).

**Иконка hero практики — по `direction`, не по типу.** `PracticeHeroCard` выбирает иконку
через `DIRECTION_ICON: Partial<Record<PracticeDirection, Component>>` (meditation/yoga/breathwork)

- `DIRECTION_ICON_FALLBACK = IconMeditation`. **Partial + fallback намеренно:** бэк будет
  расширять список направлений (somatic/womens_circle/mens_circle/tantra/kundalini, TD-CAL-DIRECTIONS-EXPAND) —
  новые значения не сломают `vue-tsc` до появления иконки, просто получат fallback.
  `IconYoga` сейчас — Claude-плейсхолдер (TD-CAL-ICON-YOGA).

**Иконки — контракт DS.** Рейтинг/сердце — DS-иконки-компоненты: чистый
`<svg :width :height viewBox fill="currentColor">`, проп `size`, один viewBox.
Каждая одноцветная → цвет задаёт родитель через токен.
Новые токены `--velo-rating-confused/good/fire` (good = новый `#d66674`; confused/fire —
ссылки на `--velo-primary-dark`/`--velo-peach-500`); ОТДЕЛЬНО от `RATING_COLOR`
(заливки баров аналитики — не трогать, иначе ломается AnalyticsView).

---

### 3.7. Флоу ПРОФИЛЬ (раздел Профиль, USER)

Реализован раздел «Профиль» по операторскому SVG (Figma выведена — см. шапку). Это USER-профиль.
Карта вью:

| Экран                      | View / роут                                           | Примечания                                                                                                                                                                                                                                                                                                                                                                                                  |
| -------------------------- | ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A — главный (70/71)        | `UserProfileView.vue` (`user-profile`)                | две стат-карточки из `GET /bookings/me/stats` (`getMyStats` в `api/bookings.ts`); векторные иконки (IconEdit/Bookings/Messages/Bell/Globe/Share/Logout); пункты-переходы. Балансовая карта и email УБРАНЫ с главного. **«Сообщения» (v1.9):** строка в «Аккаунт» после «Мои бронирования» → `UserMessagesView` (роут `user-messages`, honest empty-state, бэк-гэп E4) — без бейджа непрочитанных (нет источника). «Изменить фото» / share / прочие заглушки — toast                                                                                                             |
| F — Язык/Часовой пояс (75) | `LanguageTimezoneView.vue` (`user-language-timezone`) | таймзона = переиспользуемый `VSelect` + `TIMEZONE_OPTIONS` (`practiceOptions.ts`), автосейв `updateProfile({timezone})` + revert-on-error. Язык — заглушка из ОДНОГО пункта «Русский» (i18n НЕТ), рендер через `v-for` по `LANGUAGE_OPTIONS` (расширяемо), неинтерактивна пока язык один (`isLanguageStatic`), НЕ сохраняется. «Изменить город»/radio-список из макета НЕ делаем — выбор пояса через select |
| C — Редактирование (72)    | `EditProfileView.vue` (`user-edit-profile`)           | Имя=`first_name`; E-mail=disabled-заглушка «появится позже» (не сохраняется); Телефон=`phone`, О себе=`bio` (оба в credentials JSONB, см. Бэк §3.11); «Изменить фото»=toast. Сохранение шлёт только изменённые поля; очистка phone/bio = пустая строка. `VInput` БЕЗ пропа `error` — ошибка телефона рисуется отдельным `<p>`. `bio` сравнивается/шлётся через `.trimEnd()` (S-1)                           |
| D — Удаление (73)          | модалка в `EditProfileView` (`VModal`)                | «Удалить аккаунт» -> подтверждение -> `deleteMe()` (`DELETE /users/me`) -> `authStore.logout()`. MVP = сброс онбординга (Бэк §3.11), данные сохраняются. Текст модала ЧЕСТНЫЙ: «вернётся к начальному состоянию… данные сохранятся» (W-2), кнопка осталась «Удалить»                                                                                                                                        |
| E — Уведомления (74)       | `NotificationsView.vue` (`user-notifications`)        | 4 свича (push / practice_reminders / master_messages / support_messages), все ON по умолчанию; хранение — вложенный `credentials.notifications` (Бэк §3.11); автосейв при флипе ТИХО (без тоста), revert-on-error; шлётся только флипнутый ключ                                                                                                                                                             |
| G — Поддержка (76)         | — отложен                                             | Не реализован по решению заказчика. Пункт «Поддержка» на экране A — toast-заглушка. Задумано: форма (Тема+Сообщение+Отправить) + тост, без бэка                                                                                                                                                                                                                                                             |

**Новый UI-примитив `VSwitch`** (`components/ui/VSwitch.vue`, в barrel рядом с
`VCheckbox`): boolean on/off (pill + ползунок), `v-model`, `disabled`, `aria-label`.
Отличается от `VToggle` (segmented control) и `VCheckbox` (квадратный чек). Цвета —
токены (`--velo-primary` вкл).

**i18n НЕ существует** — язык на экране F это задел: переключатель показан, но
интерфейс не переключает и предпочтение не сохраняется. Полноценная локализация —
отдельная крупная задача, в MVP не входит.

---

### 3.8. Флоу МАСТЕР-ПРОГРАММА (DS-rebuild, v1.8)

Путь «стать мастером → онбординг» + Phase A web-auth. DS-first; контролы без бэка =
honest-стабы (тост «недоступно» + запись для Zod), НЕ фейк.

**Онбординг мастера (пост-апрув).** `views/master/MasterOnboardingView.vue` — карусель,
показывается ОДИН раз свежеверифицированному мастеру как full-screen overlay (через
`Teleport` поверх шелла) при входе на дашборд. Гейт — `utils/masterOnboarding.ts`
(`shouldShowMasterOnboarding`: role=master + profileStatus=verified + не completed + не
показан в сессии; `forced` обходит гарды для TEST-повтора). Флаг
`master_onboarding_completed` — **E15 ЗАКРЫТ (v1.11, №256/257):** персистится бэком в
credentials JSONB, типизирован в `generated.ts`, пишется плоским PATCH на done/skip;
переживает re-login и смену устройства — пере-показа на новой сессии больше нет.
Per-session гард — `master.onboardingShownThisSession` (быстрый путь внутри сессии).
Индикатор — `VPaginationDots`.

**Заявка мастера.** `views/master/MasterApplyView.vue` — 3 шага в одном вью (`step` 1→3,
локальный стейт, без бэка до финала): **Профиль** (имя/email/телефон + согласие) → **Опыт**
(методы `VChip` + «Свой вариант», стаж `VSelect`, bio, язык) → **Документы**
(паспорт/сертификаты/фото — зоны загрузки). Honest-стабы: загрузка файлов = Zod **E13**
(тап → тост, без POST файла), язык практик = Zod **E16** (локальный тоггл, не уходит в
заявку). Финал «Отправить» → `POST /masters/apply` (без language/files) →
`/master/pending`. Standalone-роут (вне MasterShell), доступен роли `user`; `applyGuard`
уводит верифиц-мастера на дашборд.

**Вердикт-экраны.** `views/master/MasterPendingView.vue` — три состояния по статусу:
**«Заявка отправлена»** (pending; polling «Обновить статус» + «Вернуться к каталогу»),
**«Заявка одобрена»** (verified; «Войти в кабинет» → дашборд+онбординг), **«Отказ»**
(rejected; **generic-причина** до Zod **E14** + 2 CTA: «Написать в поддержку» / «Подать
новую заявку»). Иллюстрации — `public/onboarding/master-verdict-*.svg`.

**Phase A parked web-auth.** `views/auth/{LandingView,LoginView,RecoverPasswordRequestView,
RecoverPasswordSetView}.vue` + спящие `/auth/*` маршруты (§2.1). Построены 100% из DS над
классическим app-фоном; web-auth-бэкенд = Zod **E17**. **Недостижимы в Telegram-флоу:**
`App.vue` рендерит `StandaloneStubView` для браузерной сессии, role-redirect никогда не ведёт
на `/auth/*`, и ничто не линкует туда. `LandingView` «Подать заявку» / `LoginView` — инертные
стабы (тост) до E17.

**5-экранное превью заявки (`ffca7a0`) — УДАЛЕНО (№260 Batch-STRIP).** Вся превью-механика
(`ui.previewApplyFlow`, кнопка, превью-ветки Landing/Apply/Pending/гардов, `beforeEach`-сброс)
вынута из кода; путь заявки проверяется настоящим флоу (тест==прод).

---

## 4. Stores (Pinia)

| Store       | Ключевые поля                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `auth`      | `user`, `token` (module-level var в client.ts), `role`, `isAuthenticated`; методы `restoreSession`/`fetchMe` (через `getMe`), `updateProfile(body)` (через `updateMe` + `_setUser`, бросает ошибку наверх — карусель не "проскакивает" при сбое сохранения)                                                                                                                                                                                                                                                                                                                                                                                  |
| `practices` | `practices[]`, `total`, `filters`, `loading`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `calendar`  | `weekAnchor`, `selectedDate`, `weekPractices[]`, `filters` (facets); computed `days`, `daysWithPractices`, `selectedDayPractices`; actions `loadWeek`, `selectDay`, `prevWeek`, `nextWeek`, `applyFilters`, `init`. Экспортит `CalendarFacetFilters`, `localDateKey`                                                                                                                                                                                                                                                                                                                                                                         |
| `bookings`  | `bookings[]`, `total`, `loading`; `selectedBooking`, `selectedLoading`, `selectedError`; методы `fetchBooking(id)` (через `getBooking` → `BookingDetailResponse`), `joinBooking`/`leaveBooking` (возвращают `{ ok, error }` через `extractApiError`)                                                                                                                                                                                                                                                                                                                                                                                         |
| `balance`   | `balance_cents`, `operations[]`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `master`    | `profile` (MasterProfile), `practices[]` (пагинация), `profileLoaded`/`practicesLoaded`, `onboardingShownThisSession` (per-session гард пост-апрув онбординга §3.8); `$reset` на логауте чистит и `MASTER_APPLIED_KEY`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `diary`     | Переписан (Diary redesign). Единая курсорная лента: `feedItems[]`, `feedLoading`, `feedError`, `feedHasMore`, реактивные `feedFilters` (categories/date_from/date_to/search); actions `fetchFeed`/`loadMoreFeed`/`refreshFeed`/`setFeedFilters`/`clearFeedFilters`/`runFeedSearch` (на `useCursorPagination`). Сохранены `submitCheckin`/`submitFeedback` (Checkin/FeedbackView), CRUD записей `createEntry`/`updateEntry`/`deleteEntry` (рефрешат ленту), `selectedEntry`+`fetchEntry`, `insightsCache` (master-facing), `$reset`. Удалены три offset-списка (checkins/feedbacks/entries) и их `fetch*`/`loadMore*` — их роль забрала лента |

**`ui`-store (TD-FE-ROLE-SWITCH; №260 ужат).** Только `uiMode` (`'default' | 'user'` —
мастер/админ просматривают юзер-интерфейс). Не персистится (сброс при открытии). TEST-сигналы
`forceOnboarding`/`previewApplyFlow` удалены Batch-STRIP'ом (№260).

**Осознанное решение:** `token` хранится как module-level переменная в `api/client.ts`, не в Pinia — исключает circular dependency `client → store → client`.

---

## 5. Утилиты

### 5.1. displayHelpers.ts — единственный источник маппингов

Все emoji, лейблы и CSS-цвета для mood/rating/type живут только здесь.
Дублировать в компонентах запрещено.

```typescript
// Mood (check-in)
MOOD_OPTIONS: { value, emoji, label }[]
MOOD_EMOJI: Record<string, string>   -- { low: '😔', mid: '😐', high: '😊' }
MOOD_LABEL: Record<string, string>
MOOD_COLOR: Record<string, string>   -- CSS-переменные, не hex

// Rating (feedback)
RATING_OPTIONS: { value, emoji, label }[]
RATING_EMOJI: Record<string, string>  -- { fire: '🔥', good: '👍', confused: '❓' }
RATING_LABEL: Record<string, string>
RATING_COLOR: Record<string, string>  -- CSS-переменные

// Practice type
PRACTICE_TYPE_EMOJI: Record<string, string>
PRACTICE_TYPE_LABEL: Record<string, string>

// Calendar taxonomy + feed buckets (Calendar iteration)
DIRECTION_LABEL: Record<PracticeDirection, string>      -- meditation→Медитация, yoga→Йога, breathwork→Дыхательные практики
DIFFICULTY_LABEL: Record<PracticeDifficulty, string>    -- beginner→Начальная, medium→Средняя, high→Высокая
DIFFICULTY_DOTS: Record<PracticeDifficulty, number>     -- beginner→1, medium→2, high→3 (индикатор ●●○ на детали)
DURATION_BUCKET_LABEL: Record<DurationBucket, string>   -- short→«До 1 часа», long→«1 час и больше»
TIME_OF_DAY_LABEL: Record<TimeOfDay, string>            -- night→Ночь, morning→Утро, day→День, evening→Вечер
```

### 5.2. currency.ts

```typescript
eurStringToCents(str: string): number   -- "14.57" → 1457 (без float-ловушки)
centsToEurString(cents: number): string -- 1457 → "14.57"
```

Прямое `parseFloat(x) * 100` запрещено — IEEE-754 float precision trap.

### 5.3. format.ts

`formatMoney(cents, currency, locale)`, `formatDate(iso, timezone?, locale?)`,
`formatDateShort(iso, timezone?, locale?)`, `formatTime(iso, timezone?, locale?)`,
`formatFeedDateTime(...)`. Все дата/время-функции принимают IANA-`timezone`
(дефолт `'UTC'`). Вызыватели передают пояс ЗРИТЕЛЯ через `useViewerTimezone()`
(см. §10, «Осознанные решения» — таймзона профиля решает везде).

### 5.4. commission.ts

`COMMISSION_RATE = 0.15` — единственный источник. Используется в `CreatePracticeView` и `EditPracticeView` для подсказки "Вы получите".

### 5.5. practiceCardMeta.ts (v1.9)

Общие хелперы меты карточки практики — `checkinLabel(p, insightsCache)` («N/M» чек-инов из `diaryStore.insightsCache`), `recurrenceLabel(p)` (регулярность серии), `remainingSessionsLabel(p)` («Осталось N из M занятий»). Вынесены из `MasterPracticesView` и переиспользуются в `MasterDashboardView` (паритет «Ближайшие практики» со списком, DB-2) — без дублирования логики. Данные чек-инов — из insights (корректность — Zod E12).

### 5.6. nearestBookings.ts (v1.10)

`selectNearestBookings(bookings, now, maxUpcoming = DEFAULT_MAX_UPCOMING)` — выбор карточек «Ближайшие практики» юзер-дашборда (TASK-2, `6fe0272`): pin идущей практики (latest-started, если есть live) + до `DEFAULT_MAX_UPCOMING` (=2) ближайших предстоящих по абсолютному времени → массив ≤3. Заменил прежний single-slot nearest (idущая больше не прячет предстоящую в единственном слоте); per-card поведение (Zoom/чек-ин/live-badge) не тронуто. Покрыт `nearestBookings.test.ts`.

---

## 6. Правила разработки

### FP-01: Только CSS-переменные, никаких hex

```css
/* ЗАПРЕЩЕНО: */
color: #334d6e;
background: #fef2f2;

/* ПРАВИЛЬНО: */
color: var(--velo-primary);
background: var(--velo-error-bg-subtle);
```

Все токены определены в `src/styles/variables.css`. При необходимости нового токена — добавлять туда.

### FP-02: displayHelpers — единственный источник маппингов

```typescript
// ЗАПРЕЩЕНО — локальный дубль:
const MOOD_EMOJI = { low: "😔", mid: "😐", high: "😊" };

// ПРАВИЛЬНО:
import { MOOD_EMOJI } from "@/utils/displayHelpers";
```

### FP-03: Деньги — только через currency.ts

```typescript
// ЗАПРЕЩЕНО:
const cents = parseFloat(input) * 100;

// ПРАВИЛЬНО:
const cents = eurStringToCents(input);
```

### FP-04: Double-submit guard — ДО валидации

```typescript
// ПРАВИЛЬНО — guard первым:
if (submitting.value) return;
submitting.value = true;
try {
  // validate, then submit
} finally {
  submitting.value = false;
}
```

### FP-05: Комментарии — только английский

```typescript
// ЗАПРЕЩЕНО:
// Получаем список практик

// ПРАВИЛЬНО:
// Fetch paginated practice list
```

### FP-06: Типизация — никаких `any`

```typescript
// ЗАПРЕЩЕНО:
const data: any = await api.get(...)

// ПРАВИЛЬНО:
const data: PracticeResponse = await getPractice(id)
```

### FP-07: Ошибки API — только через ApiResponseError

```typescript
import { ApiResponseError } from "@/api/client";

try {
  await someApiCall();
} catch (e) {
  if (e instanceof ApiResponseError) {
    toast.error(e.message);
  }
}
```

### FP-08: sessionStorage для token, не localStorage

Telegram WebApp закрывает вкладку — `sessionStorage` очищается автоматически.
`localStorage` оставлял бы протухший токен навсегда.

### FP-09: API-типы генерируются из OpenAPI, не пишутся вручную

```typescript
// ЗАПРЕЩЕНО — ручной интерфейс для бэкенд-схемы:
export interface PracticeResponse { ... }  // в types.ts

// ПРАВИЛЬНО — автогенерация + реэкспорт:
// generated.ts — создаётся скриптом, НЕ ТРОГАТЬ
// types.ts — реэкспорт из generated + frontend-only типы
export type { PracticeResponse } from './generated'
```

Скрипт: `backend/scripts/generate_ts_types.py`. Запускается при `velo update` автоматически.
Frontend-only типы (PracticeFilters, ApiError и т.д.) остаются в `types.ts`.

### FP-10: `vue-tsc` проверяет ШАБЛОН, а не только `<script setup>`

Серверный GATE (`vue-tsc --noEmit` в build) проверяет типы и в шаблоне — в т.ч.
**передачу пропов в дочерние компоненты** и обращения к optional-полям в биндингах.
Скрипт-эмуляция, проверяющая только извлечённый `<script setup>` со стаб-компонентами
(`Component = {}`), эти ошибки НЕ видит — стаб не несёт сигнатуру пропов.

```vue
<!-- FormShell объявляет successIcon: string (REQUIRED). Слот #success-icon
     лишь переопределяет рендер (<slot name="success-icon">{{ successIcon }}</slot>),
     но проп всё равно обязателен по типам. -->

<!-- ❌ vue-tsc TS2345: Property 'successIcon' is missing -->
<FormShell ...>
  <template #success-icon><IconHeart /></template>
</FormShell>

<!-- ✅ передать проп (пустой) + слот: тип удовлетворён, слот рисует иконку -->
<FormShell success-icon="" ...>
  <template #success-icon><IconHeart /></template>
</FormShell>
```

Та же категория ошибки ловила дважды: optional generated-поле (`profile.methods?.length`
в шаблоне) и required-проп дочернего компонента. **Правило проверки перед отдачей:** для
вью, которые передают пропы в дочерние компоненты (FormShell, hero-карточки и т.п.),
гонять НАСТОЯЩИЙ `vue-tsc` с типизированными стабами дочерних компонентов, а не
script-эмуляцию. Контр-тест (убрать фикс → ошибка воспроизводится) подтверждает, что
проверка реальная.

---

## 7. Дизайн-система

Токены в `src/styles/variables.css`. Дизайн-система VELΘ — soft glassmorphism, перенесена из `Design_prototype/` (DS-1 — DS-9, март 2026).

Основные группы:

```css
/* Цвета */
--velo-primary:
  #627a9c -- основной синий --velo-brand-text: #4c6589 -- текст,
  заголовки --velo-glass-blue-15/60 -- glass-поверхности --velo-glass-teal-30/40
    -- teal glass (success) --velo-glass-peach-40 -- peach glass (warning)
    --velo-glass-white-01 -- ghost-кнопки --velo-teal- *,
  --velo-peach- *, --velo-pink- *,
  --velo-sand- * -- примитивная палитра /* Семантика */
    --velo-warning-bg/border/text/text-light --velo-error-bg/border/text
    --velo-success-bg/text --velo-info-bg/text --velo-mood-low/mid/high
    /* Типографика */ --font-body: "Marmelad",
  "Noto Sans", sans-serif -- единственный шрифт,
  weight 400 --font-heading: "Marmelad", ... -- алиас,
  тот же шрифт /* Spacing */ --space-1..10, --velo-content-width: 336px,
  --velo-screen-padding: 33px /* Радиусы */ --radius-sm/md/lg: 15px -- карточки
    --radius-xl: 100px -- теги --radius-full: 9999px -- pill (кнопки)
    --radius-input: 5px -- инпуты /* Тени */ --velo-shadow-glow: 0px 0px 20.9px
    7px #ffffff -- glow на всех кнопках;
```

Шрифт: Marmelad Regular 400 — единственный вес, единственное начертание. Подключён через `<link>` в `index.html`.

Фон: красится на `#app::before { position: fixed; inset: 0; z-index: -1; background: url('/bg/background.png') center / cover no-repeat }` (`global.css` ~116-127), **НЕ на `body`** — фиксированный слой под контентом. `transform: translateY(var(--velo-bg-shift))` контр-сдвигает «танцующий фон» при reflow visual-viewport (клавиатура); at-rest `--velo-bg-shift = 0px` → инертно. Клавиатура-aware: `useBackgroundStabilizer` пишет высоту visual-viewport в `--velo-vvh` + тогглит `html.is-keyboard-open` (порог `KEYBOARD_VIEWPORT_THRESHOLD` = 150px) — гейтнутые правила ужимают `.mobile-layout__main` / `.v-modal__*` до видимой области + снимают fog-маску (`убрать туман при вводе`) ТОЛЬКО при открытой клавиатуре (at-rest байт-идентично). **Заморозка фото (KB#4 + SP-3, v1.10):** `#app::before` морозится (`transform:none`) при `html.is-keyboard-open`, а с v1.10 — ТАКЖЕ при `html.is-field-focused` (тогглится `useBackgroundStabilizer` на `focusin`/`focusout` текстового поля), чтобы фото не «сползало» в окне анимации клавиатуры ДО 150px-порога; классы композитятся (любой ⇒ `transform:none`). `resetKeyboardViewportState` (через `router.afterEach`) синхронно сбрасывает `--velo-bg-shift`/`--velo-vvh`/оба класса на смене роута. Фото из `Design_prototype`, sacred geometry overlay. Все layout-контейнеры прозрачные.

**Правило FP-01 уточняется:** стекло-эффекты используют `rgba`-значения через переменные (`var(--velo-glass-blue-15)`), не через прямые hex.

---

**Новое (v1.8):** типографские токены `--text-28` / `--text-46` (заголовки онбординга
мастера и Phase A Landing). `VPaginationDots` — геометрия точек 13×13 (активная) / 7×7
(неактивные) через DS-токены.

---

## 8. Phase F9 ✅

Выполнено. Check-in, Feedback, Дневник, Аналитика мастера реализованы и задеплоены.

---

## 9. Phase F10 (не начата)

| Задача                 | Описание                                                                                           | Зависимость                   |
| ---------------------- | -------------------------------------------------------------------------------------------------- | ----------------------------- |
| Standalone-авторизация | `platform/standalone.ts` — полноценная реализация. Новый бэкенд-эндпоинт `POST /api/v1/auth/email` | Новый бэкенд                  |
| Push-уведомления       | Service Worker + Web Push channel в notification formatters                                        | Бэкенд Phase 7 частично готов |
| Skeleton-загрузки      | Заменить спиннеры на skeleton placeholders                                                         | —                             |
| Тёмная тема            | CSS-переменные позволяют, нужен toggle + сохранение                                                | —                             |
| Pull-to-refresh        | —                                                                                                  | —                             |
| Haptic feedback        | На кнопках и успешных действиях                                                                    | —                             |
| Offline-заглушка       | "Нет подключения" + кнопка "Повторить"                                                             | —                             |

---

## 10. Технический долг

### Обозначения

- **Среда:** 🧪 низкий приоритет / 🚀 перед публичным запуском
- **Статус:** ⬜ Open

### Перед публичным запуском 🚀

| ID              | Файл                                             | Описание                                                                                                                                                                               | Решение                                                                                  |
| --------------- | ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **TD-RU-PROXY** | Инфра                                            | Hetzner IP заблокирован ТСПУ. Недоступен из России без VPN (и Telegram WebView, и обычные браузеры)                                                                                    | Российский reverse proxy (Timeweb/Selectel ~300-500₽/мес) или DDoS-Guard CDN             |
| **TD-F01**      | `platform/telegram.ts`, `composables/useAuth.ts` | Deep links не обрабатываются. `startapp=open_practice__{uuid}` открывает дашборд вместо практики. Бэкенд уже генерирует корректные ссылки через `TelegramFormatter.format_deep_link()` | Парсить `startapp` параметр в `useAuth.ts` при инициализации, редиректить на нужный роут |
| **TD-FE-WD-DEEPLINK** | `views/admin/AdminWithdrawalDetailView.vue` | Внешний аудит (E3/F8), W-5: вью читает вывод из `window.history.state` (~стр.118). При deep-link / перезагрузке `w.value=null` -> заглушки `'—'`, кнопки заблокированы (`!w.value`), `VBackButton` -> `router.back()` выходит из приложения (тупик) | Минимум: `onMounted` -> `if (!w.value) router.replace('/admin/withdrawals')`. Полнее: грузить вывод по id, чтобы deep-link открывал деталь |

### Переключение режима мастер ↔ юзер

| ID                    | Среда | Описание                                                                                                                                                                                                     | Решение                |
| --------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------- |
| **TD-FE-ROLE-SWITCH** | 🧪    | Мастер и Админ не имеют UI-точки входа в юзерский интерфейс (каталог, бронирования, дневник). `/user/dashboard` редиректит обратно. Маршруты `/user/*` (кроме dashboard) технически доступны, но недосягаемы | **Подробное решение:** |

**Детали TD-FE-ROLE-SWITCH:**

Хранение режима: Pinia (`src/stores/ui.ts`, поле `uiMode: 'default' | 'user'`).
Сброс при старте: `uiMode = 'default'` при каждом открытии приложения (не персистится).
Область: мастер и админ (админ тоже является мастером для тестирования).

Файлы для изменения:

| Файл                                     | Изменение                                                                                                                                                                                 |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/stores/ui.ts`                       | **Создать.** Поле `uiMode: 'default' \| 'user'`, action `setUiMode(mode)`                                                                                                                 |
| `src/views/master/MasterProfileView.vue` | Кнопка "Перейти в интерфейс юзера" → `uiMode = 'user'` + `router.push('/user/profile')`                                                                                                   |
| `src/views/admin/AdminProfileView.vue`   | **Создать.** Минимальный профиль администратора с той же кнопкой переключения                                                                                                             |
| `src/router/tabs.ts`                     | Добавить 4-й таб в `ADMIN_TABS`: `{ icon: '👤', label: 'Я', to: '/admin/profile' }`                                                                                                       |
| `src/router/index.ts`                    | Добавить маршрут `/admin/profile`. Адаптировать `beforeEach`: если `uiStore.uiMode === 'user'` — пропускать `/user/dashboard` без редиректа                                               |
| `src/views/user/UserProfileView.vue`     | Кнопка "Вернуться в режим мастера/админа", видна только если `role === 'master' \|\| role === 'admin'` → `uiMode = 'default'` + `router.push('/master/dashboard')` или `/admin/dashboard` |

Логика `beforeEach` после изменения:

```
if (role === 'master' || role === 'admin') && to === /user/dashboard:
  if uiMode === 'user' → пропустить (return true)
  else → redirect /master/dashboard или /admin/dashboard
```

### Ревью v2 — критические (март 2026)

| ID             | Среда | Файл            | Описание                                                                                                               | Решение                                                        |
| -------------- | ----- | --------------- | ---------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| **CRITICAL-2** | 🚀    | `api/client.ts` | `fetch()` без `AbortController` и timeout. При потере сети запрос висит вечно — в Telegram WebApp это обычная ситуация | `AbortController` + 15с timeout, новый класс `ApiTimeoutError` |

### Ревью v2 — открытые находки (март 2026)

| ID             | Среда | Файл                                                   | Описание                                                                                                                                                                                                                                                     | Решение                                                                                                                                       |
| -------------- | ----- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **NEW-1**      | 🧪    | `UserDashboardView.vue`, `PracticeDetailView.vue`      | `CHECKIN_WINDOW_H=3` и `FEEDBACK_WINDOW_H=72` захардкожены в двух местах — рассинхрон при изменении                                                                                                                                                          | Вынести в `utils/constants.ts`                                                                                                                |
| **NEW-2**      | ✅    | ~~`DiaryView.vue`~~                                    | Снято Diary redesign: `DiaryView.vue` удалён (заменён `DiaryFeedView`), локальной `formatShortDate` больше нет; дата ленты — `formatFeedDateTime` в `utils/format.ts`                                                                                        |
| **NEW-3**      | ✅    | ~~`DiaryView.vue`~~                                    | Снято Diary redesign: монолит-вкладки удалён целиком вместе с 5 sub-компонентами (DiaryList/DiaryCheckinDetail/DiaryFeedbackDetail/DiaryEntryDetail/DiaryEntryForm). Новая структура — `DiaryFeedView` + `DiaryTimeline` + `DiaryFeedCard` + `DiaryComposer` |
| **NEW-4**      | ✅    | ~~`DiaryView.vue`~~                                    | Снято Diary redesign: старый `onMounted` с `Promise.all` удалён; `DiaryFeedView` грузит ленту через стор с обработкой ошибок (`feedError` + состояние ошибки во вью)                                                                                         |
| **NEW-5**      | ✅    | `CheckinView.vue`, `FeedbackView.vue`, `DiaryView.vue` | `background: white` хардкод                                                                                                                                                                                                                                  | Закрыто в DS-7 — заменено на `transparent` / glass-токены                                                                                     |
| **NEW-6**      | ✅    | `stores/diary.ts`                                      | Снято Diary redesign: в переписанном сторе у `insightsCache` есть LRU-ограничение (`MAX_INSIGHTS_CACHE=100` + эвикция старейшего ключа при переполнении)                                                                                                     |
| **WARNING-1**  | ✅    | `stores/*.ts`                                          | Каждый store реализует свой паттерн try/catch — 7+ дублей одинаковой структуры                                                                                                                                                                               | ЗАКРЫТО: единый `composables/useApiError.ts` (`extractApiError`), применён в bookings-store (join/leave/fetchBooking) и далее по мере касания |
| **WARNING-3**  | 🧪    | `composables/useAuth.ts`                               | `waitUntilReady()` при таймауте резолвится без ошибки — код дальше думает что auth готов                                                                                                                                                                     | Возвращать `{ ok: boolean, timedOut: boolean }`                                                                                               |
| **WARNING-8**  | 🧪    | `CheckinView.vue`, `FeedbackView.vue`                  | `fetchPractice()` вызывается всегда в `onMounted`, даже если practice уже в store                                                                                                                                                                            | `if (store.selected?.id !== practiceId)` перед fetch                                                                                          |
| **WARNING-9**  | ✅    | `CheckinView.vue`, `FeedbackView.vue`                  | ~200 строк идентичного CSS (header, textarea, actions, success screen)                                                                                                                                                                                       | ЗАКРЫТО (флоу дашборд): извлечён `shared/FormShell.vue` со слотами, CheckinView переведён на него                                             |
| **WARNING-10** | 🧪    | Стили                                                  | Magic numbers: `font-size: 80px`, `56px`, `min-width: 90px` без CSS-токенов                                                                                                                                                                                  | Добавить токены в `variables.css`                                                                                                             |
| **WARNING-11** | 🧪    | Компоненты                                             | `platform.hapticFeedback()` без fallback — silent crash если platform не инициализирован                                                                                                                                                                     | try/catch вокруг вызовов haptic                                                                                                               |
| **WARNING-12** | 🧪    | `tests/`                                               | 2 тест-файла при значительной бизнес-логике F9 (DiaryStore, time window, alert banners, guards)                                                                                                                                                              | Покрыть: DiaryStore CRUD, `inCheckinWindow`, `inFeedbackWindow`, `checkinAlert`, router guards                                                |
| **WARNING-13** | 🧪    | `api/client.ts`, `composables/useAuth.ts`              | Module-level mutable state (`_token`, `isReady`) не сбрасывается между тестами                                                                                                                                                                               | Явный `reset()` или DI через параметры                                                                                                        |

### Фронтенд — открытые

| ID                           | Среда | Файл                                                                                       | Описание                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Решение                                                                                                                                                                                                        |
| ---------------------------- | ----- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| TD-SDK                       | 🧪    | `public/js/telegram-web-app.js`                                                            | SDK — локальная копия (3331 строка). Ручное обновление при новых версиях                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Миграция на `@telegram-apps/sdk` (npm)                                                                                                                                                                         |
| TD-FE-W4                     | 🧪    | `MasterProfileView.vue`                                                                    | `v-show` на payout-форме — весь DOM всегда присутствует                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Заменить на `v-if` если форма не нужна при анимированном переходе                                                                                                                                              |
| TD-FE-W6                     | ✅    | `MasterFinanceView.vue`                                                                    | `MIN_WITHDRAWAL_EUROS=50` и `WITHDRAWAL_FEE_EUROS=2` захардкожены — рассинхрон с `config.py` при изменении                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | CR-01: бэкенд отдаёт `min_withdrawal_cents` и `withdrawal_fee_cents` в `MasterProfileResponse`                                                                                                                 |
| TD-FE-A11Y                   | 🧪    | Admin views (5 файлов)                                                                     | Clickable `<div>` без `role="button"`, `tabindex="0"`, `@keydown` handlers. Нарушает WCAG 2.1 AA 2.1.1. Затронуто: алертовый баннер, stat cards, action cards, master cards, report cards                                                                                                                                                                                                                                                                                                                                                                                                  | Добавить `role="button"`, `tabindex="0"`, `@keydown.enter.stop`, `@keydown.space.prevent`                                                                                                                      |
| TD-FE-LOGO-SVGO              | 🧪    | `public/icons/logo.svg`, `public/icons/logo-white.svg`                                     | SVG-логотипы загружены через `<img>` как есть из Figma-экспорта: `logo.svg` — 228KB, `logo-white.svg` — 434KB. Избыточный размер из-за неоптимизированных path-данных                                                                                                                                                                                                                                                                                                                                                                                                                      | Прогнать через `svgo` с дефолтными настройками — ожидаемое уменьшение в 5–10× без видимых изменений                                                                                                            |
| AUDIT-0520-FE                | 🧪    | `src/**`                                                                                   | Нет компонентных тестов фронтенда (отмечено аудитом 2026-05-20). Логика вью покрыта только ручной проверкой                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Vitest + Vue Test Utils для ключевых вью (OnboardingView gate-машина, BookingPopup, формы)                                                                                                                     |
| **TD-FE-AISUM**              | 🧪    | `views/user/AiSummaryView.vue`                                                             | Экран 16 — честная заглушка "в разработке". Персонального AI-саммари юзера на бэке нет (есть только мастерский per-practice, розетка Phase 9)                                                                                                                                                                                                                                                                                                                                                                                                                                              | Реализовать полноценный экран, когда появится бэк-эндпоинт юзерского AI-саммари                                                                                                                                |
| **TD-FE-DASH-STATS** | 🧪 | `views/user/UserDashboardView.vue` | Внешний аудит (E3/F8), W-6: прогресс-статы считаются из пагинированного списка броней (~20) -- у юзера с >20 посещёнными числа частичны. Задокументировано в коде (~стр.16) как осознанный MVP-компромисс | Пост-MVP: брать из `getMyStats()` (`GET /bookings/me/stats`), а не выводить из страницы броней. Не блокер прод-запуска |
| **TD-FE-BOOK-LOADMORE** | 🧪 | `views/user/MyBookingsView.vue` | Внешний аудит (E3/F8), W-7: список броней показывает только первую страницу (нет «Загрузить ещё»). Задокументировано в коде (~стр.10) как MVP | Пост-MVP: load-more по уже пагинированному эндпоинту (`{items,total,limit,offset}`). Не блокер прод-запуска |
| **TD-FE-AVATAR**             | ✅    | `shared/MasterCard.vue`, `PracticeHeroCard.vue`, `MasterPublicView.vue`                    | Аватарки мастеров — плейсхолдер `IconMeditation` (нет поля с URL аватара)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | ЗАКРЫТО (Calendar flow): бэк отдаёт `master_avatar_url`; фронт перешёл на `VAvatar` (фото по `url` или инициалы по `name`). MasterCard — lg, MasterPublicView hero — xl                                        |
| **TD-FE-ICONSVG**            | 🧪    | `src/components/icons/`                                                                    | В каталоге доменных иконок остались сырые `.svg`-файлы рядом с `.vue`-компонентами (артефакт экспорта)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | `git rm` сырых `.svg` (операция в рабочей копии)                                                                                                                                                               |
| **S-4**                      | 🧪    | `shared/MasterCard.vue`                                                                    | Кнопка "Подробнее" (профиль мастера) кликабельна и показывает toast "скоро", хотя экрана профиля мастера для юзера ещё нет                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Осознанно отложено: либо disabled-state, либо реальный экран профиля. Аудит 2026-05-20 предлагал disabled — решено оставить toast-заглушку до появления экрана                                                 |
| **TD-CAL-STYLE**             | 🧪    | `shared/CalendarFilterModal.vue`                                                           | «Вид практики» (style) — свободный `VInput`, в Figma (кадр 2) задуман дропдаун. Справочника стилей пока нет, бэк принимает свободную строку (точное совпадение)                                                                                                                                                                                                                                                                                                                                                                                                                            | Заменить на дропдаун, когда появится каталог стилей практик                                                                                                                                                    |
| **TD-CAL-ARROW**             | 🧪    | `shared/WeekStrip.vue`, `CalendarView.vue`                                                 | Стрелки недели и шеврон/воронка — inline SVG (в `components/icons` нет `IconChevron`/левой стрелки/воронки)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Завести `IconChevronLeft/Right`, `IconFilter` в DS и заменить inline SVG                                                                                                                                       |
| **TD-ASK-MASTER**            | 🧪    | `MasterPublicView.vue`, `BookingConfirmedView.vue`, и везде, где есть «вопрос мастеру»     | Вопросы мастеру — сквозная фича: задаются из профиля мастера («в общем», без привязки к практике), ИЛИ до брони, ИЛИ после; улетают в Telegram-бот мастера, мастер отвечает юзеру тоже в бот. Требует серьёзного бэка. Сейчас ВСЕ кнопки/поля «вопрос мастеру» ЕСТЬ визуально, но ведут в toast-заглушку. Кадр 6 флоу отложен. **Решение (2026-06-02):** это диалог юзер↔мастер = отдельная сущность+флоу на бэке, НЕ строка `master_request` на брони; вне MVP. Чек-ин клиента мастеру УЖЕ отдаётся через attendance (`AttendanceItemResponse.checkin/user_display_name/user_avatar_url`) | Спроектировать и реализовать бэк диалогов (маршрутизация в бота, треды вопрос/ответ), затем подключить все точки входа                                                                                         |
| **TD-CAL-ICON-YOGA**         | 🧪    | `components/icons/IconYoga.vue`                                                            | `IconYoga` — Claude-сгенерированный плейсхолдер                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Заменить на ассет дизайнера (тот же filename/viewBox/`currentColor` → замена без правок кода)                                                                                                                  |
| **TD-DIARY-PRACTICE-AVATAR** | 🧪    | `shared/DiaryFeedCard.vue` (practice-форма), бэк `diary/projections.py`                    | В practice-карточке ленты убраны аватар мастера и verified-галочка: бэк не кладёт `master_avatar_url`/`master_verified` в `_practice_snapshot`. Карточка показывает имя мастера                                                                                                                                                                                                                                                                                                                                                                                                            | Добавить эти поля в `_practice_snapshot` (бэк), затем вернуть аватар+галочку в карточку (слоты под них уже есть)                                                                                               |
| **TD-DIARY-TAP-VARIANT-B**   | 🧪    | `views/user/DiaryFeedView.vue` (`onTap`)                                                   | Вариант A: тап по note/dream → toast «Функция временно недоступна», остальное no-op. Редактирования/удаления записи из ленты пока нет                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Вариант B: тап по note/dream открывает редактор (bottom-sheet или экран) с правкой/удалением. Меняется только обработчик `onTap` во вью; карточки и нить не трогаются (`@tap` уже эмитит `{ item, editable }`) |
| **TD-DIARY-LIST-VIEW**       | 🧪    | дневник                                                                                    | В MVP дневник = только нить (экран 40). Плоский список (экран 41) и переключатель list/map не сделаны                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Добавить list-вид (плоский стек карточек, 1:1 с feed) и переключатель, когда понадобится                                                                                                                       |
| **TD-DIARY-FILTER-SEARCH**   | 🧪    | `views/user/DiaryFeedView.vue` («...» меню), стор (`feedFilters`/`runFeedSearch` уже есть) | Фильтр по категориям + поиск + диапазон дат на бэке и в сторе готовы, но UI («...» меню → модалка фильтра/поиск) — заглушка-toast                                                                                                                                                                                                                                                                                                                                                                                                                                                          | Реализовать модалку фильтра/поиск на `VModal`, повесить на готовые `setFeedFilters`/`runFeedSearch`                                                                                                            |
| **TD-DIARY-ORNAMENT**        | 🧪    | `components/icons/IconDateLeaf.vue`                                                        | Орнамент дата-узлов нити — лёгкий рисованный (`IconDateLeaf`), не оригинальный Figma-SVG (тот — 2×31KB с масками). Аутентичные сохранены                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Вернуть аутентичные орнаменты, если заказчик захочет «точь-в-точь макет»                                                                                                                                       |
| **TD-CAL-DIRECTIONS-EXPAND** | 🧪    | `utils/displayHelpers.ts` (`DIRECTION_ICON`)                                               | Бэк добавит направления (somatic/womens_circle/mens_circle/tantra/kundalini)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Иконки уже Partial+fallback — добавить новые иконки в `DIRECTION_ICON` по мере появления (рост списка код не ломает)                                                                                           |
| **TD-ZOOM-TEXT**             | 🧪    | `views/user/BookingConfirmedView.vue`                                                      | Текст «Ссылка на Zoom придёт за 10 минут» статичен независимо от типа практики (аудит S-2, осознанно отложено — все практики сейчас через Zoom)                                                                                                                                                                                                                                                                                                                                                                                                                                            | Сделать нейтральным («Детали подключения…») или условным по `practice.zoom_link`, когда появятся не-Zoom практики                                                                                              |
| **TD-PROFILE-SUPPORT**       | 🧪    | раздел Профиль, экран G (node 76)                                                          | Экран «Поддержка» не реализован (отложен заказчиком). Пункт «Поддержка» на экране A — toast-заглушка. Единственный незакрытый экран раздела                                                                                                                                                                                                                                                                                                                                                                                                                                                | Сверстать форму (Тема+Сообщение+Отправить) + тост; бэка нет (витрина)                                                                                                                                          |
| **TD-PROFILE-LANG-I18N**     | 🧪    | `LanguageTimezoneView.vue`                                                                 | Переключатель языка — заглушка из одного пункта: i18n в проекте нет, выбор не сохраняется и интерфейс не меняется                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | Реализовать локализацию (vue-i18n), снять `isLanguageStatic`, добавить языки в `LANGUAGE_OPTIONS`, сохранять `user.language`                                                                                   |
| **TD-PROFILE-AVATAR-UPLOAD** | 🧪    | `EditProfileView.vue`                                                                      | «Изменить фото» — toast-заглушка: инфраструктуры загрузки аватара нет (аватар приходит из Telegram `photo_url`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Реализовать загрузку при появлении файлового бэка/хранилища                                                                                                                                                    |

> **Аудит итерации «Профиль» (2026-05-29):** закрыты W-2 (честный текст модала
> удаления в `EditProfileView` — поведение = сброс онбординга, данные сохраняются),
> S-1 (`bio.trimEnd()` перед сравнением/отправкой), S-2 (язык-строка `:disabled`
>
> - `cursor:default` при одном языке, авто-снимается при добавлении второго).
>   W-1/W-4/S-5 — на бэке (Бэковый Кодекс §9). W-3/S-3 — осознанно не код.

### Мастер-программа — honest-стабы (Zod E13–E17, v1.8)

| ID | Среда | Файл | Описание | Решение |
| --- | --- | --- | --- | --- |
| TD-FE-E13-APPLY-DOCS | 🧪 | `MasterApplyView.vue` | Зоны загрузки паспорт/сертификаты/фото — honest-стаб: тап → тост, файл не уходит на бэк | Zod E13: хранилище файлов заявки |
| TD-FE-E14-REJECT-REASON | 🧪 | `MasterPendingView.vue` | Экран отказа — generic-причина; реальная `rejection_reason` не на `MasterProfileResponse` | Zod E14: отдать причину отказа |
| TD-FE-E15-ONBOARDING-FLAG | ✅ | `utils/masterOnboarding.ts`, `MasterDashboardView.vue` | **ЗАКРЫТ (v1.11, №256/257):** `master_onboarding_completed` персистится бэком + типизирован в `generated.ts`; пере-показа на новой сессии нет | закрыт (E15 сделан своими силами) |
| TD-FE-E16-APPLY-LANGS | 🧪 | `MasterApplyView.vue` | Тоггл языка практик — локальный, не уходит с заявкой | Zod E16: поле языков в заявке |
| TD-FE-E17-WEB-AUTH | 🧪 | `views/auth/*`, `/auth/*` | Phase A экраны (Landing/Login/восстановление×2) — спящие/незалинкованные, инертные стабы | Zod E17: web-auth-бэкенд (email/OAuth) |

> **TEST-аффордансы — УДАЛЕНЫ (№260 Batch-STRIP, «тест==прод»).** Повтор онбординга
> (`ui.forceOnboarding`) и 5-экранное превью заявки (`ui.previewApplyFlow`) вынуты из кода.
> Роль-свитч (`RoleSwitchSection` «Переключение роли») — прод-фича с capability-политикой
> №256. Прод-переключение режима мастер↔юзер (`uiMode`) — отдельная живая фича.

### Осознанные решения (не техдолг)

| Решение                                                                  | Обоснование                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| API-типы генерируются из OpenAPI (CR-01)                                 | Единый источник правды — Pydantic-схемы бэкенда. `generated.ts` создаётся автоматически при `velo update`. Drift невозможен конструктивно                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `sessionStorage` для token (не `localStorage`)                           | Telegram WebApp закрывает вкладку — sessionStorage очищается автоматически                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Свой CSS вместо Tailwind                                                 | Дизайн-система VELΘ готова в мокапах, перенос 1:1 проще                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Внутренний Nginx в Docker фронтенда                                      | SPA fallback + кеширование без усложнения хост-конфига                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Telegram SDK через локальную копию (не npm)                              | CDN Telegram заблокирован ТСПУ; локальная копия гарантирует загрузку                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `token` в module-level var в `client.ts`, не в Pinia                     | Исключает circular dependency `client → store → client`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `v-show` на payout-форме                                                 | Анимированное скрытие; `v-if` ломает CSS-переход                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Auth guard в `App.vue` (Phase F1), не в router                           | В F1 один маршрут; guards добавлены в F2.2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Фон через `body { background }` в `global.css`, не через `#app::before`  | `#app::before` — статический CSS, Telegram WebApp кеширует и не обновляет. `global.css` импортируется в `main.ts` и попадает в JS-бандл, который обновляется при каждом деплое                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| SVG-логотипы через `<img>` (не inline)                                   | Файлы из Figma-экспорта весят 228KB и 434KB — inline SVG раздует HTML. `<img>` позволяет браузеру кешировать отдельно (TD-FE-LOGO-SVGO покроет оптимизацию)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Один `PracticeDetailView` на каталог + booked + бронь (экран 15)         | Состояния практики (доступна к брони / забронирована / прошедшая-отменённая бронь) различаются в одном вью. Батч 6: поглотил бывший «Бронирование» (экран 18) — статус-строка и ZOOM перенесены сюда (`myAnyBooking`), `BookingDetailView` и роут `booking-detail` удалены. God-component-долг смягчён выносом hero/master в `PracticeHeroCard`/`MasterCard`                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `MasterCard` "Подробнее" → toast вместо disabled (S-4)                   | ЗАКРЫТО (Calendar flow): экран профиля мастера для юзера реализован (`MasterPublicView`), `onMore()` теперь ведёт на `user-master-public` (с guard `if (!masterId)` → toast). Toast-заглушка убрана                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Отдельный `useCalendarStore` (не общий `usePracticesStore`)              | Навигация по неделям и фасет-фильтры Календаря не должны задевать общий фид. Дашборд использует `usePracticesStore`/`useBookingsStore` — изолирован                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Календарь грузит неделю одним запросом + буфер ±1 день                   | Объём недели мал; маркеры/список дня группируются клиентом по TZ ЗРИТЕЛЯ (`useViewerTimezone`, фолбэк 'UTC' — Батч 5b, не по TZ практики). Буфер ±1д закрывает W-2 (практики экстремальных TZ у границы недели). Границы окна недели остаются в браузерном TZ (это лишь выбор 7 ячеек, не отображение времени)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **Время практики — всегда в TZ профиля ЗРИТЕЛЯ** (Батч 5)                | Каждый видит время практик в своей таймзоне из профиля (`authStore.user.timezone`), а НЕ в TZ практики и НЕ в TZ браузера. Единый источник — `composables/useViewerTimezone.ts` (`ComputedRef<string｜undefined>` = `authStore.user?.timezone ?? undefined`); `format.ts`-функции применяют свой дефолт `'UTC'`, когда пояс не задан. Применено везде: карточки (`PracticeCard`/`CalendarPracticeCard`/`BookingCard`), детали (`PracticeDetailView`), дашборд, `MyBookings`, группировка календаря (`stores/calendar.ts`). На бэке симметрично — фасет `time_of_day` считается в TZ зрителя (Бэковый Кодекс, блок-цитата 2026-05-31). Обоснование: профиль решает; единая точка правды исключает рассинхрон «время на карточке vs день в календаре vs фильтр». Снят прежний хардкод-фолбэк `Europe/Berlin`/`Europe/Moscow` |
| «Выбрать практики»: модалка — единственный источник фильтров (Вариант 1) | Inline-чипы лишь отображают/снимают активные фильтры; редактирование — в `CalendarFilterModal`. Не дублируем UI выбора, нет рассинхрона                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |

---

### Бэкенд-контракты — синхронизация (backend-sourced, 2026-06-20)

> Ведётся бэкендом (Zod). Здесь — только контрактные факты с бэк-стороны; описания
> вью/сторов/обёрток `api/*.ts` и статусы фронт-фаз НЕ трогаются (это ведёт фронт-дев).

- **Новые бэкенд-эндпоинты под вайринг/сверку** (типы в `generated.ts`, автоген при
  `velo update`): `/masters/me/{income,transactions,students,students/{id},reviews}`,
  `/practices/{id}/reviews`, `/admin/{metrics/check-in|feedback|return,revenue,practices,practices/{id}}`.
  Контракты — Бэковый Кодекс §2. Статус вайринга на фронте — за фронт-командой (P0
  сделан в `f6c9744`).
- **E3 серии (новые контракты в `generated.ts`).** Создание серии: `POST /practices`
  с `practice_type="series"` шлёт `recurrence: RecurrenceSpec` (period
  daily|weekly|biweekly; days ISO 1=Пн..7=Вс — обязательны для weekly/biweekly; end
  never|until_date|after_count; `count` = ВСЕГО сессий ВКЛЮЧАЯ первую, потолок 40;
  `until_date` должен давать >=1 сессию после первой, иначе бэк 400 на публикации).
  Отмена: опциональное тело `CancelPracticeRequest { scope: "this" |
  "this_and_future" }`. Карточка: `PracticeResponse` несёт `recurrence_days /
  total_sessions / completed_sessions` (`MasterPracticesView` читает их структурно —
  уже работает; форма создания и диалог отмены — вайринг за фронт-девом). Контракты —
  Бэковый Кодекс §2 / §3.13.
- **E7 период-статы (новые эндпоинты).** `GET /masters/me/stats?period=week|month`
  (`MasterStatsResponse`: practices/participants/income + `*_delta_pct`) и
  `GET /admin/stats/overview?period=week|month` (`AdminStatsOverviewResponse`: рост,
  выручка, ставки вовлечённости + дельты, `pending_reports`). Admin-overview одним
  вызовом заменяет фан-аут дашборда (`/admin/stats` + `/admin/revenue` + три
  `/admin/metrics`) и делает тоггл Неделя/Месяц реальным. Вайринг — за фронт-девом.
- **Авто-финализация по длительности закрыта бэкендом** — `finalizePractice` / ручная
  кнопка «Завершить» больше не нужны; практики завершаются фоновым воркером по
  `end + buffer` (15 мин). Если в техдолге/фазах это числилось открытым — закрыто.
- **Чек-ин Zoom-независим** (инвариант под W-1): явка засчитывается и по PRE-чек-ину,
  поэтому точка входа в чек-ин (баннер дашборда / кнопка live-экрана) не должна
  гейтиться `zoom_link`/`hasValidZoom`. Проверено: сейчас гейтится только «Войти».
- **`ROLE_SWITCH_ENABLED` удалён (v1.11, `15d5b0d`)** — вместе с W-4 security-WARNING;
  безопасность роль-свитча теперь в самой capability-политике (`derive_allowed_roles`).
  Строку `ROLE_SWITCH_ENABLED=False` в TEST `.env` удалить при деплое (№264-точность):
  под Docker она БЕЗВРЕДНА (compose инжектит `.env` как env-переменные, pydantic-settings
  игнорит неизвестный ключ; `.env` в образ не копируется — dockerignore), НО на bare-metal
  запуске ФАТАЛЬНА (pydantic-settings кидает `extra_forbidden` на неизвестный ключ в dotenv-файле).
  Раннбук №261 её всё равно удаляет.

---

**Конец документа**
