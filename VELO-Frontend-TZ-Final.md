# VELO Frontend — Финальное ТЗ (Снапшот)

**Версия:** 1.2  
**Дата:** 16 мая 2026  
**Статус:** Рабочий документ — обновляется после каждого спринта

---

## §0 Стек и принципы

| Компонент | Технология |
|-----------|-----------|
| Фреймворк | Vue 3 + Composition API |
| Язык | TypeScript 5.x |
| Сборка | Vite |
| Роутинг | Vue Router 4.x |
| Стейт | Pinia |
| HTTP | Fetch-обёртка (`src/api/client.ts`) |
| Стили | Custom CSS + Design Tokens (`src/styles/variables.css`) |
| i18n | vue-i18n (ru основной, en) |
| Платформа | Telegram WebApp (основной), PWA (fallback) |

**Принципы:**
- Каждый экран = один `.vue` файл в `src/views/{role}/`
- Все API-вызовы через типизированные методы в `src/api/`
- Стили только через `var(--velo-*)` из design tokens
- Никаких хардкодов URL — через `import.meta.env.VITE_API_BASE_URL`
- Cents → display всегда через `formatMoney()`
- **Никаких русских литералов в `.vue`/`.ts` — все строки через `t('key')` с первого экрана**

> Полная конституция фронта (генерационные стадии, code rules, auth wiring) — в `frontend/ARCHITECTURE.md`. Этот документ — бэклог экранов и спринтов.

---

## §1 Shared Layer (общее для всех Shell'ов)

### Дизайн-система

| Компонент | Путь | Статус |
|-----------|------|--------|
| VButton | `components/ui/VButton.vue` | ❌ |
| VInput | `components/ui/VInput.vue` | ❌ |
| VTextarea | `components/ui/VTextarea.vue` | ❌ |
| VSelect | `components/ui/VSelect.vue` | ❌ |
| VCard | `components/ui/VCard.vue` | ❌ |
| VBadge | `components/ui/VBadge.vue` | ❌ |
| VAvatar | `components/ui/VAvatar.vue` | ❌ |
| VLoader | `components/ui/VLoader.vue` | ❌ |
| VModal | `components/ui/VModal.vue` | ❌ |
| VToast | `components/ui/VToast.vue` | ❌ |
| VEmptyState | `components/ui/VEmptyState.vue` | ❌ |
| VStatCard | `components/ui/VStatCard.vue` | ❌ |
| VHeader | `components/layout/VHeader.vue` | ❌ |
| VTabBar | `components/layout/VTabBar.vue` | ❌ |
| MobileLayout | `components/layout/MobileLayout.vue` | ❌ |
| PracticeCard | `components/shared/PracticeCard.vue` | ❌ |
| BookingCard | `components/shared/BookingCard.vue` | ❌ |
| AdminLayout | `components/layout/AdminLayout.vue` | ❌ |
| VCheckbox | `components/ui/VCheckbox.vue` | ❌ |
| VDivider | `components/ui/VDivider.vue` | ❌ |
| VProgressBar | `components/ui/VProgressBar.vue` | ❌ |

### Роутинг и Auth

- TMA-авторизация через `POST /api/v1/auth/telegram` ❌
- Ролевые guards (user / master / admin) ❌
- 3 Tab Bar конфигурации по ролям ❌
- Скелет роутера (`router/index.ts`) ✅

---

## §2 User Shell

### Легенда

| Символ | Значение |
|--------|----------|
| ✅ | Экран и API-интеграция готовы |
| 🎨 | Экран в Figma есть, нужно подключить API |
| ❌ | Экран отсутствует (нужно создать) |
| 🔌 | Endpoint готов на бэкенде |
| 📭 | Endpoint отсутствует → mock/заглушка |

---

### 🔴 ОЧЕРЕДЬ 1 — P0 (делаем в первые 3 дня)

Только то, что можно подключить к реальным endpoint'ам прямо сейчас.

#### Auth & Onboarding

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `user-auth-welcome` | ❌ | — | TMA: сразу в dashboard. PWA: показывает экран |
| TMA-авторизация (flow) | ❌ | `POST /api/v1/auth/telegram` 🔌 | |
| `user-onboarding-timezone` | ❌ | `PATCH /api/v1/users/me` 🔌 | Сохранить timezone после онбординга |

#### Dashboard

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `user-dashboard` | ❌ | `GET /api/v1/practices` 🔌<br>`GET /api/v1/users/me` 🔌 | Список ближайших практик + баланс |

#### Calendar & Practice

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `user-calendar` | ❌ | `GET /api/v1/practices` 🔌 | Фильтры: тип, дата. Сортировка по `scheduled_at` |
| `user-calendar-filter` | ❌ | — | Клиентская фильтрация |
| `user-practice-detail-prebook-paid` | ❌ | `GET /api/v1/practices/:id` 🔌<br>`POST /api/v1/practices/:id/preview-purchase` 🔌 | Платная практика до бронирования |
| `user-practice-detail-prebook-free` | ❌ | `GET /api/v1/practices/:id` 🔌 | Бесплатная практика до бронирования |
| `user-master-profile` | ❌ | `GET /api/v1/practices?master_id=X` 🔌 | Профиль строится из embedded-полей PracticeResponse: `master_name`, `master_methods[]`. Bio, avatar, experience — нет публичного endpoint'а (§7). Минимальный вариант работает |

#### Booking Flow

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `user-payment-checkout` | ❌ | `POST /api/v1/practices/:id/purchase` 🔌 | **P0 Critical** — экран подтверждения покупки перед оплатой |
| `user-payment-success` | ❌ | `GET /api/v1/bookings/:id` 🔌 | Успешная оплата, показать booking detail |
| `user-payment-error` | ❌ | — | Ошибка оплаты, кнопка "Попробовать снова" |
| `user-booking-success` | ❌ | `GET /api/v1/bookings/:id` 🔌 | После бронирования бесплатной практики |
| `user-bookings-list` | ❌ | `GET /api/v1/bookings/me` 🔌 | Мои записи: upcoming / past |
| `user-booking-detail` | ❌ | `GET /api/v1/bookings/:id` 🔌 | Детали бронирования |

#### Practice Day

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `user-practice-day-operational` | ❌ | `GET /api/v1/bookings/:id` 🔌<br>`POST /api/v1/bookings/:id/join` 🔌 | День практики: Zoom deep-link + check-in |
| `user-practice-live` | ❌ | `POST /api/v1/bookings/:id/leave` 🔌 | Во время практики |
| `user-practice-checkin-form` | ❌ | `POST /api/v1/practices/:id/checkin` 🔌 | Форма: mood picker + slider + textarea |
| `user-practice-checkin-success` | ❌ | — | Успех после check-in |
| `user-practice-feedback-form` | ❌ | `POST /api/v1/practices/:id/feedback` 🔌 | После практики: rating (fire/good/confused) + комментарий |
| `user-practice-feedback-success` | ❌ | — | Успех после feedback |

#### Top-up (Stripe)

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `user-topup` | ❌ | `POST /api/v1/payments/topup` 🔌 | |
| `user-topup-success` | ❌ | `GET /api/v1/users/me` 🔌 | |
| `user-topup-cancel` | ❌ | — | |

#### Profile

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `user-profile-stats` | ❌ | `GET /api/v1/users/me` 🔌<br>`GET /api/v1/bookings/me` 🔌 | Имя, аватар, статкарточки (практики, часы) |
| `user-profile-actions` | ❌ | `POST /api/v1/auth/logout` 🔌 | Logout, edit, delete account |
| `user-profile-edit` | ❌ | `PATCH /api/v1/users/me` 🔌 | first_name, last_name, timezone, language |
| `user-account-delete-confirm` | ❌ | — | Custom modal с глагольными лейблами, destructive pink |

#### Settings

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `user-settings-notifications` | ❌ | — 📭 | 4 toggle. Хранить в localStorage до endpoint'а |

#### Support

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `user-support-form` | ❌ | `POST /api/v1/reports` 🔌 | Форма обращения |
| `user-support-success` | ❌ | — | **P0** — success после отправки |

---

### 🟡 ОЧЕРЕДЬ 2 — P1/P2 (после первых 3 дней)

#### Auth (нет endpoint'ов → mock)

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `user-auth-login` | ❌ | — 📭 | Mock: "Email-вход в разработке" |
| `user-auth-register` | ❌ | — 📭 | Mock: OAuth заглушка |
| `user-auth-oauth-loading` | ❌ | — 📭 | Mock |
| `user-auth-password-reset-request` | ❌ | — 📭 | Нужен endpoint |
| `user-auth-password-reset-confirm` | ❌ | — 📭 | Нужен endpoint |

#### Onboarding

| Экран | Статус | Примечание |
|-------|--------|-----------|
| `user-onboarding-intro-1` | ❌ | Карусель слайд 1 |
| `user-onboarding-intro-2` | ❌ | Карусель слайд 2 |
| `user-onboarding-intro-3` | ❌ | Карусель слайд 3 |

#### Diary (частично с API)

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `user-diary-list-timeline` | ❌ | `GET /api/v1/diary` 🔌 | — |
| `user-diary-list-flat` | ❌ | `GET /api/v1/diary` 🔌 | — |
| `user-diary-filter-collapsed` | ❌ | — | Client-side |
| `user-diary-filter-expanded` | ❌ | — | Client-side |
| `user-diary-search` | ❌ | — | Client-side |
| `user-diary-entry-view` | ❌ | `GET /api/v1/diary/:id` 🔌 | — |
| `user-diary-entry-actions` | ❌ | — | Actions overlay |
| `user-diary-entry-edit` | ❌ | `PATCH /api/v1/diary/:id` 🔌 | — |
| `user-diary-entry-delete-undo` | ❌ | `DELETE /api/v1/diary/:id` 🔌 | Undo-banner 5 сек |
| `user-diary-entry-create-expanded` | ❌ | `POST /api/v1/diary` 🔌 | Полный модал |
| `user-diary-dreams-merged-list` | ❌ | `GET /api/v1/diary` 🔌 | Client-side фильтр по type=dream. Тип в текущем API отсутствует — ждём backend-расширения `DiaryEntry.type` |
| `user-dreams-list-timeline` | ❌ | `GET /api/v1/diary` 🔌 | — |

#### Check-ins History

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `user-checkins-list-timeline` | ❌ | `GET /api/v1/users/me/checkins` 🔌 | — |
| `user-checkins-list-flat` | ❌ | `GET /api/v1/users/me/checkins` 🔌 | — |
| `user-checkin-detail` | ❌ | `GET /api/v1/users/me/checkins?practice_id=X` 🔌 | Endpoint возвращает список. Берём первый элемент после фильтра по practice_id |
| `user-feedbacks-list-timeline` | ❌ | `GET /api/v1/users/me/feedbacks` 🔌 | — |
| `user-feedbacks-list-flat` | ❌ | `GET /api/v1/users/me/feedbacks` 🔌 | — |

#### Correlations (нет endpoint'ов → mock)

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `user-correlations-2-icons` | ❌ | — 📭 | Mock data |
| `user-correlations-3-icons` | ❌ | — 📭 | Mock data |
| `user-correlations-graph` | ❌ | — 📭 | Mock AI-выводы |
| `user-summary-week` | ❌ | `GET /api/v1/practices/:id/ai-summary` 🔌 | Placeholder `is_mock=true` |

#### Messages (нет endpoint'а → mock)

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `user-messages-list` | ❌ | — 📭 | 3 fake conversations, кнопка → toast |
| `user-chat-master` | ❌ | — 📭 | 5-10 mock-сообщений, "Отправить" → toast |
| `user-chat-support` | ❌ | `POST /api/v1/reports` 🔌 | Через reports endpoint |

#### Booking Cancel (P0 — endpoint существует)

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `user-practice-cancel-confirm` | ❌ | `DELETE /api/v1/bookings/:id` 🔌 | **P0** — Custom modal: сумма возврата, условия |

---

## §3 Master Shell

### 🔴 ОЧЕРЕДЬ 1 — P0

#### Application & Verification

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `master-application-step1-profile` | ❌ | — | display_name, email, phone |
| `master-application-step2-experience` | ❌ | — | methods, experience_years, bio, certifications |
| `master-application-step3-documents` | ❌ | `POST /api/v1/masters/apply` 🔌 | Submit на шаге 3 |
| `master-application-submitted` | ❌ | — | После submit |
| `master-application-approved` | ❌ | `GET /api/v1/masters/me` 🔌 | status=verified |
| `master-application-rejected` | ❌ | `GET /api/v1/masters/me` 🔌 | status=rejected + кнопка "Подать повторно" |

#### Dashboard

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `master-dashboard-week` | ❌ | `GET /api/v1/masters/me` 🔌<br>`GET /api/v1/masters/me/practices` 🔌 | Метрики недели + ближайшая практика |
| `master-dashboard-month` | ❌ | `GET /api/v1/masters/me` 🔌<br>`GET /api/v1/masters/me/practices` 🔌 | Метрики месяца |

#### Practices Management

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `master-practices-upcoming` | ❌ | `GET /api/v1/masters/me/practices` 🔌 | Предстоящие практики |
| `master-practices-past` | ❌ | `GET /api/v1/masters/me/practices` 🔌 | Прошедшие |
| `master-practice-create` | ❌ | `POST /api/v1/practices` 🔌 | Один scroll: title, type, datetime, duration, timezone, participants, price, zoom_link |
| `master-practice-edit` | ❌ | `GET /api/v1/practices/:id` 🔌<br>`PATCH /api/v1/practices/:id` 🔌 | Только редактируемые поля |
| `master-practice-upcoming` | ❌ | `GET /api/v1/practices/:id` 🔌 | Детали предстоящей |
| `master-practice-upcoming-actions` | ❌ | `POST /api/v1/practices/:id/finalize` 🔌 | Завершить + Zoom deep-link |
| `master-practice-cancel-confirm` | ❌ | `POST /api/v1/practices/:id/cancel` 🔌 | Custom modal + 100% refund warning |
| `master-practice-finished` | ❌ | `GET /api/v1/practices/:id` 🔌<br>`GET /api/v1/practices/:id/insights` 🔌 | Прошедшая: финансы + аналитика |
| `master-practice-attendance` | ❌ | `GET /api/v1/practices/:id/attendance` 🔌 | Список: attended / no_show / pending |

#### Analytics & Finance

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `master-analytics-feedback` | ❌ | `GET /api/v1/practices/:id/insights` 🔌 | Распределение fire/good/confused |
| `master-analytics-finance` | ❌ | `GET /api/v1/masters/me` 🔌 | frozen_cents, available_cents + блок к выводу |
| `master-summary-week` | ❌ | `GET /api/v1/masters/me/practices` 🔌<br>`GET /api/v1/practices/:id/ai-summary` 🔌 | AI summary placeholder |

#### Students

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `master-students-list` | ❌ | `GET /api/v1/practices/:id/attendance` 🔌 | Агрегат по всем практикам = N вызовов или нужен aggregate endpoint (§7) |
| `master-students-checkins-list` | ❌ | `GET /api/v1/practices/:id/insights` 🔌 | Check-in stats учеников |

#### Payout (P0 — endpoint готов)

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `master-payout-request` | ❌ | `POST /api/v1/masters/me/withdraw` 🔌 | **P0 Critical** — запрос вывода средств |
| `master-payout-status-tracker` | ❌ | `GET /api/v1/masters/me/withdrawals` 🔌 | **P0 Critical** — статус запроса |

#### Support

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `master-support-form` | ❌ | `POST /api/v1/reports` 🔌 | **P0 Critical** |
| `master-support-success` | ❌ | — | **P0** |

---

### 🟡 ОЧЕРЕДЬ 2 — P1/P2

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `master-onboarding-intro-1/2/3` | ❌ | — | Карусель после одобрения |
| `master-application-pending-tracker` | ❌ | `GET /api/v1/masters/me` 🔌 | Этапы верификации |
| `master-dashboard-empty` | ❌ | — | Empty-state нового мастера |
| `master-chat-student` | ❌ | — 📭 | Нужен endpoint чата |
| `master-messages-list` | ❌ | — 📭 | Нужен endpoint |
| `master-profile-overview` | ❌ | `GET /api/v1/masters/me` 🔌 | Главный экран профиля |
| `master-settings-payout-methods` | ❌ | `PATCH /api/v1/masters/me/payout` 🔌 | Реквизиты вывода |
| `master-settings-language` | ❌ | `PATCH /api/v1/users/me` 🔌 | language field |
| `master-settings-timezone` | ❌ | `PATCH /api/v1/users/me` 🔌 | timezone field |
| `master-settings-notifications` | ❌ | — 📭 | localStorage до endpoint'а |
| `master-notifications-center` | ❌ | — 📭 | Нужен endpoint |
| `master-practice-kick-confirm` | ❌ | — 📭 | Endpoint для kick студента отсутствует в API (§7) |
| `master-practice-delete-confirm` | ❌ | `DELETE /api/v1/practices/:id` 🔌 | Только draft без записавшихся |
| `master-practice-preview` | ❌ | `GET /api/v1/practices/:id` 🔌 | Превью "как видит ученик" |
| `master-students-empty` | ❌ | — | Empty-state |
| `master-practices-upcoming-empty` | ❌ | — | Empty-state |
| `master-practices-past-empty` | ❌ | — | Empty-state |

---

## §4 Admin Shell

### 🔴 ОЧЕРЕДЬ 1 — P0

#### Auth & Dashboard

> **Примечание по admin auth:** В TMA-режиме admin авторизуется через тот же `POST /api/v1/auth/telegram` — role=admin приходит в UserResponse, ролевой guard перенаправляет на /admin. Отдельный `admin-auth-login` + 2FA нужен только для standalone web-панели (десктоп), что вне scope текущего спринта. Перенесены в Очередь 2.

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `admin-dashboard` | ❌ | `GET /api/v1/admin/stats` 🔌 | users_count, masters_count, practices_count, pending_verifications |

#### Users & Masters

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `admin-users-list` | ❌ | `GET /api/v1/admin/users` 🔌 | Фильтр role + is_active, пагинация |
| `admin-masters-list` | ❌ | `GET /api/v1/admin/masters/list` 🔌 | 3 таба: Все / На проверке / Верифицированы |
| `admin-master-application-review` | ❌ | `GET /api/v1/admin/masters/:id` 🔌<br>`POST /api/v1/admin/masters/:id/verify` 🔌 | Просмотр заявки + кнопка Approve |
| `admin-master-reject-modal` | ❌ | `POST /api/v1/admin/masters/:id/reject` 🔌 | **P0 Critical** — модал с причиной отказа |
| `admin-document-viewer` | ❌ | — | **P0** — просмотр документов мастера |

#### Moderation

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `admin-moderation-list` | ❌ | `GET /api/v1/admin/reports` 🔌 | Фильтр status + target_type |
| `admin-moderation-ticket-detail` | ❌ | `GET /api/v1/admin/reports/:id` 🔌<br>`POST /api/v1/admin/reports/:id/resolve` 🔌<br>`POST /api/v1/admin/reports/:id/dismiss` 🔌 | **P0 Critical** |

#### Finance & Payouts

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `admin-revenue-detail` | ❌ | `GET /api/v1/admin/withdrawals` 🔌 | Список запросов вывода |
| `admin-payout-request-detail` | ❌ | `POST /api/v1/admin/withdrawals/:id/approve` 🔌<br>`POST /api/v1/admin/withdrawals/:id/reject` 🔌 | **P0 Critical** — approve с confirm-step |

#### Practices

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `admin-practices-list` | ❌ | `GET /api/v1/practices` 🔌 | Список всех практик |
| `admin-practice-upcoming` | ❌ | `GET /api/v1/practices/:id` 🔌 | Детали предстоящей |
| `admin-practice-past` | ❌ | `GET /api/v1/practices/:id` 🔌<br>`GET /api/v1/practices/:id/attendance` 🔌 | Прошедшая |

#### Analytics

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `admin-analytics-checkin-rate` | ❌ | — 📭 | Детальная аналитика check-in. Нужен новый endpoint (§7) |
| `admin-analytics-feedback-rate` | ❌ | — 📭 | Нужен новый endpoint (§7) |
| `admin-analytics-return-rate` | ❌ | — 📭 | Нужен новый endpoint (§7) |

#### Sandbox

| Экран | Статус | Endpoint(s) | Примечание |
|-------|--------|-------------|-----------|
| `admin-sandbox-user` | ❌ | `GET /api/v1/users/me` 🔌<br>`GET /api/v1/bookings/me` 🔌 | Read-only режим юзера |

---

### 🟡 ОЧЕРЕДЬ 2 — P1/P2 (нет endpoint'ов или не критично для демо)

| Экран | Статус | Нужен endpoint | Примечание |
|-------|--------|---------------|-----------|
| `admin-auth-login` | ❌ | — 📭 | Только для standalone web-панели (десктоп). В TMA не нужен |
| `admin-auth-2fa-setup` | ❌ | — 📭 | TOTP setup — только для web-панели |
| `admin-auth-2fa-confirm` | ❌ | — 📭 | Ввод TOTP — только для web-панели |
| `admin-auth-password-reset-request` | ❌ | — 📭 | Нужен endpoint — только для web-панели |
| `admin-auth-password-reset-confirm` | ❌ | — 📭 | Нужен endpoint — только для web-панели |
| `admin-user-profile` | ❌ | `GET /api/v1/admin/users` 🔌 | Детальный профиль юзера |
| `admin-master-profile` | ❌ | `GET /api/v1/admin/masters/:id` 🔌 | Профиль верифицированного мастера |
| `admin-user-actions-modal` | ❌ | — 📭 | suspend/ban/reset/delete — нет endpoint'ов |
| `admin-master-actions-modal` | ❌ | — 📭 | suspend/ban/change commission |
| `admin-refund-modal` | ❌ | — 📭 | Возврат конкретному ученику |
| `admin-practice-force-cancel-modal` | ❌ | `POST /api/v1/practices/:id/cancel` 🔌 | Force cancel от лица админа |
| `admin-platform-settings` | ❌ | — 📭 | Настройки платформы |
| `admin-audit-log` | ❌ | — 📭 | Лог действий |
| `admin-sandbox-master` | ❌ | `GET /api/v1/masters/me` 🔌 | Режим мастера |
| `admin-consistency-checks` | ❌ | `GET /api/v1/admin/consistency` 🔌 | 21 проверка целостности — endpoint готов |
| `admin-master-approve-modal` | ❌ | — | Welcome message при одобрении |
| `admin-master-clarification-modal` | ❌ | — 📭 | Запрос уточнения у мастера |
| `admin-users-filter-modal` | ❌ | — | Клиентский фильтр |
| `admin-masters-filter-modal` | ❌ | — | Клиентский фильтр |
| `admin-practices-filter-modal` | ❌ | — | Клиентский фильтр |
| `admin-moderation-filter-modal` | ❌ | — | Клиентский фильтр |

---

## §5 Что в mock — нет endpoint'ов

Эти фичи есть в UI, но бэкенд ещё не готов. Фронт строит на mock-данных, финальные точки → toast-заглушки. Все строки toast'ов идут через `t('key')` (см. `frontend/ARCHITECTURE.md §6.11`).

| Фича | Что делаем |
|------|-----------|
| Email/OAuth логин | Кнопка → `toast.info(t('common.inDevelopment'))` |
| Восстановление пароля | Экраны нужно нарисовать, кнопка → `toast.info(t('common.inDevelopment'))` |
| Messaging / Chat | 3 fake conversations, "Отправить" → `toast.info(t('common.comingSoon'))` |
| Notification preferences | localStorage до endpoint'а |
| Admin 2FA / auth | Mock до endpoint'а |
| Admin user/master actions (suspend, ban) | Кнопки → `toast.info(t('common.comingSoon'))` |
| Promo codes UI | Не делаем в первой версии |
| Waitlist UI | Не делаем в первой версии |

---

## §6 Sprint-план — первые 3 дня

### Sprint 1 (День 1) — User Shell P0

**Цель:** пользователь открывает Telegram, авторизуется, видит практики, бронирует, платит, может отменить запись.

| # | Задача | Экраны |
|---|--------|--------|
| 1 | Auth + Onboarding | `user-auth-welcome`, `user-onboarding-timezone` |
| 2 | Dashboard подключить к API | `user-dashboard` |
| 3 | Calendar + filters | `user-calendar`, `user-calendar-filter` |
| 4 | Practice detail + purchase + cancel | `user-practice-detail-prebook-paid/free`, `user-payment-checkout`, `user-payment-success/error`, `user-booking-success`, `user-practice-cancel-confirm` |
| 5 | Bookings list + detail | `user-bookings-list`, `user-booking-detail` |
| 6 | Profile (stats + edit + logout + delete modal) | `user-profile-stats`, `user-profile-actions`, `user-profile-edit`, `user-account-delete-confirm` |
| 7 | Support | `user-support-form`, `user-support-success` |

### Sprint 2 (День 2) — Master Shell P0

**Цель:** мастер видит дашборд, создаёт практику, управляет ею, видит финансы, может запросить вывод.

| # | Задача | Экраны |
|---|--------|--------|
| 1 | Dashboard + practice list | `master-dashboard-week/month`, `master-practices-upcoming/past` |
| 2 | Create + edit practice | `master-practice-create`, `master-practice-edit` |
| 3 | Practice day ops | `master-practice-upcoming`, `master-practice-upcoming-actions`, `master-practice-cancel-confirm` |
| 4 | Attendance + finalize | `master-practice-attendance`, `master-practice-finished` |
| 5 | Finance + payout | `master-analytics-finance`, `master-payout-request`, `master-payout-status-tracker` |
| 6 | Support form | `master-support-form`, `master-support-success` |

### Sprint 3 (День 3) — Admin Shell P0 + Practice Day User

**Цель:** админ может верифицировать мастеров, модерировать, обрабатывать выводы. Пользователь может пройти день практики.

| # | Задача | Экраны |
|---|--------|--------|
| 1 | Admin dashboard + stats | `admin-dashboard` |
| 2 | Masters verification flow | `admin-masters-list`, `admin-master-application-review`, `admin-master-reject-modal` |
| 3 | Moderation | `admin-moderation-list`, `admin-moderation-ticket-detail` |
| 4 | Payout approve/reject | `admin-revenue-detail`, `admin-payout-request-detail` |
| 5 | User practice day | `user-practice-day-operational`, `user-practice-live`, `user-practice-checkin-form`, `user-practice-feedback-form` |
| 6 | Check-in + feedback success | `user-practice-checkin-success`, `user-practice-feedback-success` |

---

## §7 Недостающие endpoint'ы (для бэкенда)

Фичи, которые нарисованы в Figma и нужны пользователям, но endpoint'ов пока нет. Список для бэкенд-партнёра.

| Приоритет | Фича | Нужный endpoint |
|-----------|------|----------------|
| P2 | Admin standalone auth + 2FA | `POST /api/v1/admin/auth/login`, `POST /api/v1/admin/auth/2fa` — нужно только для web-панели (не TMA) |
| P1 | Email/password auth | `POST /api/v1/auth/email`, `POST /api/v1/auth/oauth` |
| P1 | Password reset | `POST /api/v1/auth/password-reset`, `POST /api/v1/auth/password-reset/confirm` |
| P1 | Messaging / Chat | `GET/POST /api/v1/messages`, `GET /api/v1/conversations` |
| P1 | Notification preferences | `GET/PATCH /api/v1/users/me/notification-preferences` |
| P1 | Admin user actions | `POST /api/v1/admin/users/:id/suspend`, `POST /api/v1/admin/users/:id/ban` |
| P1 | Admin master actions | `PATCH /api/v1/admin/masters/:id/commission` |
| P1 | Refund manual | `POST /api/v1/admin/bookings/:id/refund` |
| P1 | Account deletion | `DELETE /api/v1/users/me` — нет в API, `user-account-delete-confirm` сейчас mock |
| P1 | Kick студента мастером | `POST /api/v1/practices/:id/kick` или `DELETE /api/v1/bookings/:id` с master-scope — нет в API |
| P1 | Публичный профиль мастера | `GET /api/v1/masters/:id` — нет в API, `user-master-profile` строится из PracticeResponse embedded fields |
| P1 | Aggregate students list | `GET /api/v1/masters/me/students` — нет в API, `master-students-list` требует N вызовов |
| P1 | Admin detailed analytics | `GET /api/v1/admin/analytics/checkin-rate`, `/feedback-rate`, `/return-rate` — нет в API |
| P2 | Promo codes UI | Endpoint уже есть — нужен только UI |
| P2 | Waitlist UI | Endpoint уже есть — нужен только UI |

---

## §7.5 Переключение ролей (для тестирования)

### Назначение

Позволяет admin и master видеть интерфейс от лица другой роли без смены роли в БД. Нужно для тестирования UX и демо.

### Логика по ролям

| Реальная роль (из БД) | Доступные кнопки переключения |
|-----------------------|-------------------------------|
| `admin` | «Смотреть как мастер» + «Смотреть как пользователь» |
| `master` | «Смотреть как пользователь» |
| `user` | — (кнопок нет) |

### Как работает технически

**Хранение состояния:**
- Pinia store: `viewMode: 'admin' | 'master' | 'user'` (по умолчанию = реальная роль из `user.role`)
- Персистируется в `sessionStorage` под ключом `velo_view_mode`
- Сбрасывается при logout

**При переключении:**
1. Записать `viewMode` в store + sessionStorage
2. Роутер и Tab Bar переключаются на новый Shell
3. Redirect на dashboard новой роли (`/user/dashboard` или `/master/dashboard`)

**Роутер / guards:**
- Все ролевые guard'ы читают `viewMode` из store, а не `user.role` напрямую
- Исключение: admin-only endpoints (verify master, payout approve) — проверяют `user.role === 'admin'` (реальную роль), игнорируют viewMode. Это защита от случайных действий в тестовом режиме

**Возврат в исходную роль:**
- Кнопка «Вернуться как [реальная роль]» появляется в profile/settings когда `viewMode !== user.role`
- Или просто перезайти — sessionStorage очистится

### Где отображаются кнопки

- `user-profile-actions` (User Shell) — если `user.role === 'master'` или `user.role === 'admin'`, показать кнопку переключения
- `master-profile-overview` (Master Shell) — кнопки переключения для master и admin
- Все shell'ы — sticky баннер «🔍 Режим просмотра: [роль]» когда viewMode ≠ user.role + кнопка «Выйти из режима»

### Нет нового endpoint'а

Это чисто клиентская фича. API-вызовы не меняются. Реальные действия (verify, payout) всегда идут от имени `user.role`, не `viewMode`.

---

## §8 Правила обновления этого документа

После каждого завершённого спринта:

1. Экраны со статусом ❌ → отмечать ✅ если созданы и подключены к API
2. Добавить новые экраны если появились в процессе
3. Обновить `§7` если бэкенд выкатил новые endpoint'ы
4. Зафиксировать принятые архитектурные решения в конце файла

### Лог решений

| Дата | Решение | Причина |
|------|---------|---------|
| 13.05.26 | P0 = все 3 Shell'а только с реальными endpoint'ами | Цель: альфа за 3 дня для демо |
| 13.05.26 | Messaging → mock, "Отправить" → toast | Нет endpoint'а чата на бэкенде |
| 13.05.26 | Notification preferences → localStorage | Нет endpoint'а на бэкенде |
| 13.05.26 | admin-masters-pending упразднён как экран | Стал табом в admin-masters-list |
| 13.05.26 | admin-auth-login/2FA перенесены в Очередь 2 | В TMA admin авторизуется через POST /auth/telegram (role=admin). Отдельный admin-auth нужен только для будущей standalone web-панели |
| 13.05.26 | viewMode (переключение ролей) — sessionStorage, не localStorage | Telegram WebApp закрывает вкладку → sessionStorage очищается, viewMode сбрасывается автоматически |
| 13.05.26 | Admin-only API actions игнорируют viewMode | Защита от случайного вызова admin endpoint в тестовом режиме |
| 16.05.26 | Фронт откачен на Phase 0 foundation | Смена дизайна. Все компоненты, вьюхи, stores, composables удалены. Генерация заново из Figma через CC |
| 16.05.26 | vue-i18n с первого экрана, ru + en | Старого фронта с накопленными литералами больше нет — мигрировать нечего. Все новые views сразу через `t('key')`. Отдельный VELO-i18n-Plan.md больше не нужен |
