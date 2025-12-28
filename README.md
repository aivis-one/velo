# YON Master Rooms — Mermaid Diagrams

**Draft версия для обсуждения с заказчиком**

## Список диаграмм

### 1. Architecture Overview (`01-architecture-overview.mermaid`)
**Что показывает:** Высокоуровневая архитектура всех сервисов

**Включает:**
- Client Layer (Telegram, Web, Mobile)
- API Gateway
- 9 микросервисов (User, Practice, Quiz, Calendar, Notification, Booking, Payment, State, Library)
- Data Layer (PostgreSQL, Redis)
- External Services (Zoom, Stripe, YON State Engine, S3)

**Для кого:** Техлид, архитектор, заказчик (общее понимание)

---

### 2. API Flow: Booking Practice (`02-api-flow-booking.mermaid`)
**Что показывает:** Sequence diagram — как пользователь бронирует практику

**Этапы:**
1. Пользователь смотрит список практик
2. Выбирает практику и видит детали + квиз
3. Создаёт бронь
4. Система проверяет доступность и подписку
5. Отправляет подтверждение
6. Планирует напоминания (24h, 1h, 10min)
7. За 24 часа отправляет квиз для заполнения

**Для кого:** Бэкенд-разработчики, фронтенд (понимание API)

---

### 3. Database Schema (`03-database-schema.mermaid`)
**Что показывает:** ER-диаграмма основных таблиц

**Таблицы:**
- `users` — пользователи (с MIXIN для платформ)
- `master_profiles` — профили мастеров
- `practices` — практики
- `practice_pricing` — ценообразование
- `practice_quizzes` — квизы до/после практик
- `bookings` — брони
- `quiz_responses` — ответы на квизы
- `subscriptions` — подписки
- `payments` — платежи

**Связи:**
- User → MasterProfile (1:1)
- Master → Practices (1:N)
- Practice → Bookings (1:N)
- Practice → Quiz (1:1)
- User → Bookings (1:N)
- Booking → Payment (1:1)

**Для кого:** Database architect, бэкенд-разработчики

---

### 4. Calendar Service: Reminders (`04-calendar-reminders.mermaid`)
**Что показывает:** Как работает APScheduler для напоминаний

**Процесс:**
1. Мастер создаёт практику
2. Calendar Service планирует 3 задачи в APScheduler:
   - 24 часа до практики
   - 1 час до практики
   - 10 минут до практики
3. В назначенное время APScheduler триггерит задачи
4. Notification Service отправляет сообщения всем участникам

**Для кого:** Бэкенд-разработчики (понимание фоновых задач)

---

### 5. Quiz Data Structure (`05-quiz-data-structure.mermaid`)
**Что показывает:** Структура JSON для вопросов и ответов квизов

**Типы вопросов:**
- **Scale** (1-10 слайдер): "Насколько ты тревожен?"
- **Emotion** (эмоджи-пикер): 😌😰😴😊😔
- **Choice** (одиночный выбор): "Что привело тебя на практику?"
- **MultiChoice** (множественный выбор)
- **Text** (свободный текст): "Твоё намерение на сегодня"

**Пример JSON:**
```json
{
  "questions": [
    {
      "id": "q1",
      "type": "scale",
      "question": "How anxious are you?",
      "min_value": 1,
      "max_value": 10
    }
  ]
}
```

**Для кого:** Фронтенд (UI квизов), бэкенд (валидация)

---

### 6. Notification Service (`06-notification-service.mermaid`)
**Что показывает:** Архитектура и типы уведомлений

**Типы отправки:**
1. **User** — личное сообщение (Telegram DM)
2. **Channel** — пост в канал
3. **Group** — сообщение в группу
4. **Thread** — в топик форума (Telegram forum groups)
5. **All Users** — broadcast всем активным пользователям

**Priority levels:**
- 10 — Urgent (практика началась)
- 8 — High (напоминание за 10 минут)
- 5 — Normal (напоминание за 24 часа)
- 3 — Low (маркетинг)
- 1 — Background (аналитика)

**Retry logic:**
- 1-я попытка: +30 секунд
- 2-я попытка: +2 минуты
- 3-я попытка: +10 минут
- После 3 неудач → failed

**Для кого:** Бэкенд (worker processes), DevOps (мониторинг очередей)

---

## Как использовать диаграммы

### Вариант 1: Просмотр в интерфейсе Claude
Все `.mermaid` файлы рендерятся прямо в интерфейсе — просто откройте файл.

### Вариант 2: Онлайн редактор
1. Откройте https://mermaid.live/
2. Скопируйте содержимое `.mermaid` файла
3. Вставьте в редактор
4. Экспортируйте в PNG/SVG

### Вариант 3: draw.io / diagrams.net
1. Откройте https://app.diagrams.net/
2. File → Import from → Advanced → Mermaid
3. Вставьте код
4. Редактируйте визуально

### Вариант 4: VS Code
1. Установите расширение "Mermaid Preview"
2. Откройте `.mermaid` файл
3. Ctrl+Shift+P → "Mermaid: Preview"

### Вариант 5: GitHub/GitLab
Загрузите файлы в репозиторий — GitHub/GitLab автоматически рендерят Mermaid в README.

---

## Следующие шаги

**Для финальной версии нужно добавить:**

1. ✅ State Service — детальная диаграмма интеграции с YON State Engine
2. ✅ Payment Service — Stripe flow (subscription + one-time)
3. ✅ Library Service — S3/CDN для видеозаписей
4. ✅ Deployment diagram — Docker, Kubernetes, CI/CD
5. ✅ Security flows — Authentication, Authorization, Rate limiting

**Вопросы для обсуждения:**

1. Нужны ли более детальные API endpoints (Swagger-style)?
2. Добавить диаграммы для мобильного приложения (когда будет готово)?
3. Нужны ли диаграммы для конкретных edge cases (отмена практики, возврат средств)?

---

**Статус:** v1.0 Final (27.12.2025)

---

**08. Master Verification Flow**
- State diagram верификации мастеров
- pending_verification → verified → suspended/banned
- Права и ограничения для каждого статуса

**Файл:** `08-master-verification-flow.mermaid`

**Для кого:** Product manager, бэкенд (User/Master service)

---

## ✅ Completed Diagrams

All 8 diagrams created and reviewed:
- Architecture overview
- API booking flow  
- Database schema (with JSONB credentials & master_profile)
- Calendar reminders (APScheduler)
- Quiz data structures
- Notification service
- User credentials JSONB pattern
- Master verification flow

**See:** `../index.md` для навигации по всем документам
