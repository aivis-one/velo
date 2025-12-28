# YON Master Rooms — Technical Specification

**Version:** 1.0 (Draft)  
**Date:** December 27, 2025  
**Status:** MVP Architecture Design  
**Team:** 2-person startup team  

---

## Document Purpose

Этот документ фиксирует архитектурные решения для MVP YON Master Rooms — платформы для мастеров практик (медитация, дыхательные техники, йога) и их пользователей.

**Целевая аудитория:**
- Заказчик (понимание структуры и возможностей)
- Бэкенд-разработчики (implementation guide)
- Фронтенд-разработчики (API contracts)
- DevOps (deployment requirements)

---

## Key Architectural Decisions

### ✅ Decision 1: Microservices from Day 1

**Решение:** Сразу делаем микросервисную архитектуру (не монолит)

**Обоснование:**
- После web MVP сразу запуск мобильного приложения (iOS + Android)
- Бэкэнд должен быть готов к multi-platform с первого дня
- Проще масштабировать отдельные сервисы (Notification Service под нагрузкой)
- Легче разделять ответственность в команде из 2 человек

**Trade-offs:**
- ✅ Готовность к scale с первого дня
- ✅ Каждый сервис можно деплоить независимо
- ⚠️ Сложнее на старте (больше инфраструктуры)
- ⚠️ Нужна orchestration (Docker Compose / K8s)

---

### ✅ Decision 2: Telegram Authentication (No JWT on MVP)

**Решение:** Аутентификация через Telegram WebApp (без классического JWT)

**Обоснование:**
- Мастера и пользователи уже в Telegram
- Telegram WebApp даёт готовую аутентификацию
- Нет необходимости в email-регистрации на MVP
- Session management через Redis (session tokens)

**Implementation:**
- Telegram initData validation (hash check)
- Redis-based sessions (TTL 30 days)
- Future: добавим web email/password без breaking changes

---

### ✅ Decision 3: JSONB for User Credentials

**Решение:** Хранить платформенные креды в JSONB поле `credentials`

**Структура:**
```json
{
  "telegram": {"id": 123456789, "username": "john_doe"},
  "web": {"email": "...", "password_hash": "..."},  // Future
  "discord": {"id": "...", "username": "..."}        // Future
}
```

**Обоснование:**
- Гибкость — добавление новой платформы без ALTER TABLE
- Нет NULL полей для неиспользуемых платформ
- Безопасные миграции (просто добавляем ключ в JSON)

**Performance:**
- SELECT по telegram_id: ~2-4ms (vs 0.8ms для native column)
- Для MVP (<10k users, <100 req/sec) — некритично
- Запросы к Telegram API займут больше времени чем к БД
- С правильными индексами производительность приемлемая

**Trade-offs:**
- ✅ Максимальная гибкость для будущих платформ
- ✅ Чистая схема без NULL полей
- ⚠️ Немного медленнее чем native columns (2-3x)
- ⚠️ Требует GIN + partial indexes

**See:** `diagrams/07-user-credentials-jsonb.mermaid` для деталей

---

### ✅ Decision 4: Zoom Integration (No Custom Video MVP)

**Решение:** Используем Zoom API для видео-практик

**Обоснование:**
- Мастера уже привыкли к Zoom
- Собственный WebRTC слишком сложен для MVP
- Zoom API даёт enterprise-grade качество из коробки
- Можем переключиться на custom video позже (API не изменится)

**Implementation:**
- Practice Service создаёт Zoom meetings via API
- Пользователи получают join links
- Zoom handles all video infrastructure

---

### ✅ Decision 5: APScheduler for Calendar & Reminders

**Решение:** APScheduler (AsyncIO) + Redis job store

**Обоснование:**
- Proven solution (используется в MLM Scheduler из БЗ)
- Timezone-aware scheduling
- Persistent jobs (Redis хранит состояние)
- Auto-retry на сбоях

**Use cases:**
- Practice reminders (24h, 1h, 10min before)
- Recurring practices (series: weekly, monthly)
- Payment retries
- Scheduled notifications

**See:** `diagrams/04-calendar-reminders.mermaid`

---

### ✅ Decision 6: PostgreSQL + Redis

**Решение:** PostgreSQL для persistence, Redis для cache & queues

**PostgreSQL:**
- Все persistent data (users, practices, bookings, payments)
- JSONB support (для credentials и quiz data)
- Relational integrity (foreign keys, constraints)

**Redis:**
- Session tokens (TTL-based)
- APScheduler job store
- Notification queue
- Rate limiting counters

---

## Services Architecture

### 9 Microservices + API Gateway

```
API Gateway → Kong/Traefik
  │
  ├─ User Service        (Auth, profiles, masters)
  ├─ Practice Service    (CRUD практик, Zoom API)
  ├─ Quiz Service        (Pre/Post практики квизы)
  ├─ Calendar Service    (APScheduler, reminders)
  ├─ Notification Service (Telegram: user/channel/group)
  ├─ Booking Service     (Reservations, access control)
  ├─ Payment Service     (Stripe, subscriptions)
  ├─ State Service       (Check-ins, YON State Engine API)
  └─ Library Service     (S3/CDN recordings)
```

**See:** `diagrams/01-architecture-overview.mermaid`

---

## Service Responsibilities

### 1. User Service

**責任:**
- Telegram authentication (initData validation)
- User profiles (clients)
- Master profiles (approach, experience, certifications)
- RBAC (client/master/admin roles)

**Database:** `users_db` (PostgreSQL)

**Key models:**
- `users` — с JSONB credentials
- `master_profiles` — расширенная информация для мастеров

**API endpoints:**
```
POST   /api/v1/auth/telegram
GET    /api/v1/users/me
PATCH  /api/v1/users/me
GET    /api/v1/masters/{master_id}
PATCH  /api/v1/masters/me
```

**See:** `user-model-jsonb-pattern.md` для детальной документации

---

### 2. Practice Service

**Ответственность:**
- CRUD практик (Live, Series, 1:1, Replay)
- Zoom integration (create meetings, get join URLs)
- Practice lifecycle (draft → scheduled → live → completed)
- Pricing management

**Database:** `practices_db` (PostgreSQL)

**Key models:**
- `practices` — основная таблица
- `practice_pricing` — ценообразование

**API endpoints:**
```
POST   /api/v1/practices
GET    /api/v1/practices/{id}
PATCH  /api/v1/practices/{id}
DELETE /api/v1/practices/{id}
POST   /api/v1/practices/{id}/zoom
GET    /api/v1/practices (filters: master_id, status, tags, date)
```

**Zoom Integration:**
- Использует Zoom API для создания meetings
- Хранит zoom_meeting_id, zoom_join_url, zoom_host_url
- Master получает host URL, users получают join URL

---

### 3. Quiz Service (NEW!)

**Ответственность:**
- Pre-practice quizzes (check-in: "Как ты себя чувствуешь?")
- Post-practice quizzes (рефлексия: "Как изменилось состояние?")
- Aggregated results для мастера (anonymous)
- Quiz templates (создание мастерами)

**Database:** `quizzes_db` (PostgreSQL)

**Key models:**
- `practice_quizzes` — шаблоны квизов
- `quiz_responses` — ответы пользователей

**Question types:**
- **Scale** (1-10 слайдер): "Насколько ты тревожен?"
- **Emotion** (эмоджи-пикер): 😌😰😴😊😔
- **Choice** (одиночный выбор)
- **MultiChoice** (множественный выбор)
- **Text** (свободный текст)

**API endpoints:**
```
POST   /api/v1/practices/{id}/quiz
GET    /api/v1/practices/{id}/quiz
POST   /api/v1/quizzes/{id}/responses
GET    /api/v1/practices/{id}/quiz/results (aggregated, for master)
```

**See:** `diagrams/05-quiz-data-structure.mermaid`

---

### 4. Calendar Service (NEW!)

**Ответственность:**
- Manage practice schedules
- Auto-reminders (24h, 1h, 10min before practice)
- Recurring practices (series: weekly, monthly)
- Timezone-aware scheduling

**Tech:** APScheduler + Redis job store

**Features:**
- При создании практики → автоматически планируются 3 напоминания
- Trigger через APScheduler → вызывает Notification Service
- Отмена практики → удаляются все scheduled jobs

**API endpoints:**
```
GET    /api/v1/calendar/upcoming
GET    /api/v1/calendar/master/{master_id}
POST   /api/v1/calendar/reminders/{id} (manual trigger)
```

**See:** `diagrams/04-calendar-reminders.mermaid`

---

### 5. Notification Service

**Ответственность:**
- Telegram notifications (personal DM, channels, groups/threads)
- Queue management (priority-based)
- Template rendering (Jinja2)
- Delivery tracking & retry logic

**Database:** `notifications_db` (PostgreSQL)

**Key models:**
- `notifications` — основная таблица
- `notification_deliveries` — для broadcasts

**Notification types:**
1. **User** — личное сообщение (Telegram DM)
2. **Channel** — пост в канал
3. **Group** — сообщение в группу (с поддержкой threads для forum groups)
4. **All Users** — broadcast всем активным пользователям

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

**API endpoints:**
```
POST   /api/v1/notifications
GET    /api/v1/notifications/{id}
GET    /api/v1/notifications/user/{user_id}
POST   /api/v1/notifications/channel
POST   /api/v1/notifications/group
```

**See:** `diagrams/06-notification-service.mermaid`

---

### 6. Booking Service

**Ответственность:**
- Бронирование мест в практиках
- Access control (кто может join)
- Waitlist (если практика заполнена)
- Attendance tracking

**Database:** `bookings_db` (PostgreSQL)

**Key models:**
- `bookings` — брони
- `waitlist` — очередь ожидания

**Booking statuses:**
- `pending` — забронировано, но не оплачено (если требуется оплата)
- `confirmed` — оплачено, готов к join
- `attended` — реально присоединился
- `no_show` — не пришёл
- `cancelled` — отменено

**API endpoints:**
```
POST   /api/v1/bookings
GET    /api/v1/bookings/{id}
DELETE /api/v1/bookings/{id}
GET    /api/v1/practices/{id}/bookings
GET    /api/v1/users/{user_id}/bookings
POST   /api/v1/bookings/{id}/access-token
```

**See:** `diagrams/02-api-flow-booking.mermaid` для полного flow

---

### 7. Payment Service

**Ответственность:**
- Stripe integration
- Subscriptions (monthly/yearly membership)
- One-time payments (для платных практик)
- Payouts для мастеров
- Commission tracking

**Database:** `payments_db` (PostgreSQL)

**Key models:**
- `subscriptions` — подписки пользователей
- `payments` — разовые платежи
- `payouts` — выплаты мастерам
- `commissions` — комиссии платформы

**Subscription types:**
- Monthly ($19.99/mo)
- Yearly ($199/year, 2 months free)

**Payment types:**
- `practice` — разовая оплата за практику
- `one_on_one` — индивидуальная сессия
- `recording` — доступ к записи
- `topup` — пополнение баланса

**API endpoints:**
```
POST   /api/v1/subscriptions
GET    /api/v1/subscriptions/{user_id}
POST   /api/v1/subscriptions/{id}/cancel
POST   /api/v1/payments
GET    /api/v1/payments/{payment_id}
GET    /api/v1/payments/user/{user_id}
POST   /api/v1/payouts
GET    /api/v1/payouts/master/{master_id}
```

---

### 8. State Service

**Ответственность:**
- Check-ins перед практикой (состояние пользователя)
- Check-outs после практики (рефлексия)
- Aggregated group state для мастера
- Integration с YON State Engine (external API)
- Анонимизация данных

**Database:** `states_db` (PostgreSQL)

**Key models:**
- `checkins` — состояния до практики
- `checkouts` — состояния после практики

**External API:**
- YON State Engine (пока за скобками MVP)
- Формат интеграции: HTTP API calls

**API endpoints:**
```
POST   /api/v1/checkins
GET    /api/v1/checkins/{practice_id}
POST   /api/v1/checkouts
GET    /api/v1/checkouts/{practice_id}
GET    /api/v1/practices/{id}/group-state (aggregated, for master)
POST   /api/v1/states/analyze (call to YON State Engine)
```

---

### 9. Library Service

**Ответственность:**
- Хранение записей практик
- Tags и метаданные
- Search & filtering
- Access control (subscription-based)
- S3/CDN integration

**Database:** `library_db` (PostgreSQL)

**Storage:** S3-compatible storage (AWS S3 / MinIO / Cloudflare R2)

**Key models:**
- `recordings` — записи практик

**API endpoints:**
```
POST   /api/v1/recordings
GET    /api/v1/recordings/{id}
GET    /api/v1/recordings (filters: master_id, tags)
PATCH  /api/v1/recordings/{id}
DELETE /api/v1/recordings/{id}
GET    /api/v1/recordings/{id}/access-url (signed URL)
```

---

## Database Design

### Schema Strategy

**Multi-schema PostgreSQL:**
```
users_db       → users, master_profiles
practices_db   → practices, practice_pricing
quizzes_db     → practice_quizzes, quiz_responses
bookings_db    → bookings, waitlist
payments_db    → subscriptions, payments, payouts, commissions
states_db      → checkins, checkouts
library_db     → recordings
notifications_db → notifications, notification_deliveries
calendar_db    → (APScheduler uses Redis, not PostgreSQL)
```

**Rationale:**
- Каждый сервис владеет своей схемой
- Легко разделить на отдельные databases при scale
- Foreign keys работают внутри схемы, между схемами — только по ID

**See:** `diagrams/03-database-schema.mermaid`

---

### Key Tables Overview

#### users (User Service)
```
id              UUID PK
role            ENUM (client, master, admin)
credentials     JSONB (platform-specific auth)
first_name      VARCHAR
last_name       VARCHAR
avatar_url      VARCHAR
timezone        VARCHAR
language        VARCHAR
is_active       BOOLEAN
is_verified     BOOLEAN
created_at      TIMESTAMP
updated_at      TIMESTAMP
last_login_at   TIMESTAMP
```

**Indexes:**
- GIN on `credentials`
- Partial on `credentials->'telegram'->>'id'`
- Partial on `credentials->'web'->>'email'`

---

#### practices (Practice Service)
```
id                  UUID PK
master_id           UUID FK → users.id
type                ENUM (live, series, one_on_one, replay)
title               VARCHAR
description         TEXT
scheduled_at        TIMESTAMP
duration_minutes    INT
timezone            VARCHAR
parent_practice_id  UUID FK → practices.id (for series)
series_metadata     JSONB
format              ENUM (silent, guided, music)
level               ENUM (beginner, intermediate, advanced, all)
state_tags          JSONB (array)
max_participants    INT
current_participants INT
zoom_meeting_id     VARCHAR
zoom_join_url       TEXT
zoom_host_url       TEXT
zoom_password       VARCHAR
status              ENUM (draft, scheduled, live, completed, cancelled)
created_at          TIMESTAMP
updated_at          TIMESTAMP
starts_at           TIMESTAMP (actual start)
ends_at             TIMESTAMP (actual end)
```

---

#### bookings (Booking Service)
```
id                  UUID PK
practice_id         UUID FK → practices.id
user_id             UUID FK → users.id
access_token        VARCHAR UNIQUE (single-use for Zoom)
access_granted_at   TIMESTAMP
access_expires_at   TIMESTAMP
status              ENUM (pending, confirmed, attended, no_show, cancelled)
payment_id          UUID FK → payments.id
joined_at           TIMESTAMP
left_at             TIMESTAMP
created_at          TIMESTAMP
updated_at          TIMESTAMP
```

**UNIQUE:** (practice_id, user_id) — пользователь не может забронировать практику дважды

---

## Technology Stack

### Backend (All Services)

```yaml
Language: Python 3.12
Framework: FastAPI
ORM: SQLAlchemy 2.0 (async)
Database: PostgreSQL 16
Cache: Redis 7
Queue: Redis (for APScheduler & Notifications)
Validation: Pydantic v2
Testing: pytest, pytest-asyncio
```

### External Services

```yaml
Video: Zoom API
Payments: Stripe API
AI: YON State Engine (external HTTP API)
Storage: S3-compatible (AWS S3 / MinIO)
Telegram: aiogram 3.x (Bot API)
```

### Infrastructure

```yaml
Containerization: Docker
Orchestration: Docker Compose (dev) → K8s (prod)
API Gateway: Kong / Traefik
Reverse Proxy: Nginx
Monitoring: Prometheus + Grafana
Logging: ELK stack (Elasticsearch, Logstash, Kibana)
CI/CD: GitHub Actions
```

---

## API Design Principles

### REST API Standards

**Base URL:** `https://api.masterrooms.yon.app/api/v1`

**Versioning:** URL-based (`/api/v1`, `/api/v2`)

**Authentication:**
- Session token in header: `Authorization: Bearer <token>`
- Token получается через `POST /auth/telegram`
- TTL: 30 days (Redis-based)

**Response format:**
```json
{
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2025-12-27T10:00:00Z"
  },
  "errors": null
}
```

**Error format:**
```json
{
  "data": null,
  "meta": { ... },
  "errors": [
    {
      "code": "PRACTICE_NOT_FOUND",
      "message": "Practice with ID ... not found",
      "field": "practice_id"
    }
  ]
}
```

**Pagination:**
```
GET /api/v1/practices?limit=20&offset=40
```

**Filtering:**
```
GET /api/v1/practices?master_id=...&status=scheduled&tags=anxiety,focus
```

**Sorting:**
```
GET /api/v1/practices?sort_by=scheduled_at&order=asc
```

---

## Inter-Service Communication

### Synchronous (HTTP)

**Pattern:** Service A вызывает Service B через HTTP

**Example:**
```python
# Booking Service → Payment Service
async def check_user_subscription(user_id: UUID) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://payment-service:8000/api/v1/subscriptions/{user_id}"
        )
        return response.json()["data"]["status"] == "active"
```

**Retry strategy:** exponential backoff (1s, 2s, 4s)

**Circuit breaker:** после 5 consecutive failures → open circuit на 60s

---

### Asynchronous (Events via Redis Pub/Sub)

**Pattern:** Service A публикует event, Service B подписан

**Example:**
```python
# Practice Service → publishes "practice.created"
await redis.publish("events:practice.created", json.dumps({
    "practice_id": str(practice.id),
    "master_id": str(practice.master_id),
    "scheduled_at": practice.scheduled_at.isoformat()
}))

# Calendar Service → subscribes to "practice.created"
async def handle_practice_created(event_data):
    await calendar_service.schedule_practice_reminders(
        practice_id=event_data["practice_id"],
        scheduled_at=event_data["scheduled_at"]
    )
```

**Events:**
- `practice.created` → Calendar Service (schedule reminders)
- `practice.cancelled` → Calendar Service (cancel reminders), Notification Service (notify users)
- `booking.confirmed` → Notification Service (send confirmation)
- `payment.succeeded` → Booking Service (grant access)

---

## Deployment Strategy

### Development (Docker Compose)

```yaml
# docker-compose.yml
version: '3.8'

services:
  api-gateway:
    image: kong:latest
    ports:
      - "8000:8000"
  
  user-service:
    build: ./services/user-service
    environment:
      DATABASE_URL: postgresql://...
      REDIS_URL: redis://redis:6379
  
  practice-service:
    build: ./services/practice-service
  
  # ... остальные сервисы
  
  postgres:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

### Production (Kubernetes)

**Architecture:**
```
Ingress (Nginx)
  │
  ├─ API Gateway (Kong) → 3 replicas
  │    │
  │    ├─ User Service → 2 replicas
  │    ├─ Practice Service → 2 replicas
  │    ├─ Notification Service → 3 replicas (high load)
  │    └─ ... other services → 2 replicas each
  │
  ├─ PostgreSQL (StatefulSet) → Primary + 2 Replicas
  └─ Redis (StatefulSet) → Sentinel cluster (3 nodes)
```

**Horizontal Pod Autoscaler:**
- Target CPU: 70%
- Min replicas: 2
- Max replicas: 10

**Health checks:**
- Liveness probe: `GET /health/live`
- Readiness probe: `GET /health/ready`

---

## Security Considerations

### Authentication & Authorization

**Session management:**
- Redis-based sessions (TTL 30 days)
- Token rotation каждые 7 days
- Secure cookie flags (httpOnly, secure, sameSite=strict)

**Rate limiting:**
- API Gateway level: 100 req/min per IP
- Per-user level: 1000 req/hour per user_id

**Input validation:**
- Pydantic models на всех endpoints
- SQL injection protection (SQLAlchemy parameterized queries)
- XSS protection (escape user input)

---

### Data Protection

**Sensitive data:**
- Passwords → bcrypt hashing (cost=12)
- Payment tokens → encrypted at rest (AES-256)
- Telegram auth data → validated via hash

**GDPR compliance:**
- User data export endpoint
- User data deletion (soft delete + anonymization)
- Consent tracking

---

## Monitoring & Observability

### Metrics (Prometheus)

**Application metrics:**
- Request rate, latency, error rate per endpoint
- Database query duration
- Cache hit/miss ratio
- Queue length (notifications, APScheduler jobs)

**Business metrics:**
- Active users (DAU, MAU)
- Practices created/completed
- Bookings created/confirmed
- Payments succeeded/failed
- Subscription churn rate

---

### Logging (ELK)

**Structured logging:**
```json
{
  "timestamp": "2025-12-27T10:00:00Z",
  "level": "INFO",
  "service": "practice-service",
  "trace_id": "abc123",
  "user_id": "user-uuid",
  "message": "Practice created",
  "context": {
    "practice_id": "practice-uuid",
    "master_id": "master-uuid"
  }
}
```

**Log levels:**
- DEBUG — development only
- INFO — application events
- WARNING — потенциальные проблемы
- ERROR — ошибки, требующие внимания
- CRITICAL — system failures

---

### Tracing (Jaeger)

**Distributed tracing:**
- Каждый request получает unique `trace_id`
- `trace_id` передаётся между сервисами (в headers)
- Jaeger собирает spans для визуализации потока запросов

**Example:**
```
trace_id: abc123
│
├─ API Gateway (10ms)
│   └─ User Service: validate_session (5ms)
│
├─ Practice Service: get_practice (15ms)
│   ├─ PostgreSQL: SELECT practices (8ms)
│   └─ Redis: get_cache (2ms)
│
└─ Booking Service: create_booking (50ms)
    ├─ PostgreSQL: INSERT booking (10ms)
    ├─ Payment Service: check_subscription (30ms)
    └─ Notification Service: send_confirmation (10ms)
```

---

## Testing Strategy

### Unit Tests

**Coverage target:** 80%+

**Tools:** pytest, pytest-asyncio, pytest-mock

**Example:**
```python
# tests/unit/test_user_service.py

@pytest.mark.asyncio
async def test_create_user_with_telegram_credentials():
    user = User(
        first_name="John",
        credentials={"telegram": {"id": 123456789}}
    )
    assert user.telegram_id == 123456789
    assert user.primary_platform == "telegram"
```

---

### Integration Tests

**Scope:** Service + Database (Docker Compose)

**Tools:** pytest-docker, testcontainers

**Example:**
```python
@pytest.mark.integration
async def test_booking_flow_with_payment(db_session):
    # 1. Create user
    user = await create_test_user(db_session)
    
    # 2. Create practice
    practice = await create_test_practice(db_session)
    
    # 3. Create subscription
    subscription = await create_test_subscription(db_session, user.id)
    
    # 4. Create booking
    booking = await booking_service.create_booking(
        practice_id=practice.id,
        user_id=user.id
    )
    
    # 5. Verify booking confirmed (subscription active)
    assert booking.status == "confirmed"
```

---

### E2E Tests

**Scope:** Full system (all services)

**Tools:** Playwright (для web UI), pytest + httpx (для API)

**Example:**
```python
@pytest.mark.e2e
async def test_full_booking_flow():
    # 1. Authenticate via Telegram
    session_token = await authenticate_telegram(telegram_id=123456789)
    
    # 2. Get upcoming practices
    practices = await get_practices(session_token)
    
    # 3. Create booking
    booking = await create_booking(
        session_token=session_token,
        practice_id=practices[0]["id"]
    )
    
    # 4. Verify notification sent
    assert await check_notification_sent(user_id)
```

---

## Next Steps

### Phase 1: Core Infrastructure (Week 1-2)

**Tasks:**
- [x] Architecture design ✅
- [ ] Docker Compose setup
- [ ] PostgreSQL schemas creation
- [ ] Redis configuration
- [ ] API Gateway setup (Kong)

**Deliverables:**
- Working local environment
- Database migrations
- Health check endpoints

---

### Phase 2: User & Auth (Week 3)

**Tasks:**
- [ ] User Service implementation
- [ ] Telegram authentication
- [ ] Session management (Redis)
- [ ] Master profiles

**Deliverables:**
- `POST /auth/telegram`
- `GET /users/me`
- `PATCH /users/me`
- `GET /masters/{id}`

---

### Phase 3: Practice Management (Week 4)

**Tasks:**
- [ ] Practice Service implementation
- [ ] Zoom API integration
- [ ] Quiz Service implementation
- [ ] Calendar Service implementation

**Deliverables:**
- Practice CRUD endpoints
- Zoom meeting creation
- Pre/post practice quizzes
- Auto-reminders (24h, 1h, 10min)

---

### Phase 4: Booking & Payments (Week 5)

**Tasks:**
- [ ] Booking Service implementation
- [ ] Payment Service implementation
- [ ] Stripe integration
- [ ] Notification Service implementation

**Deliverables:**
- Booking flow (от выбора практики до подтверждения)
- Subscription management
- Payment processing
- Telegram notifications

---

### Phase 5: Library & State (Week 6)

**Tasks:**
- [ ] Library Service implementation
- [ ] S3 integration (video uploads)
- [ ] State Service implementation
- [ ] YON State Engine integration (stub for MVP)

**Deliverables:**
- Recording upload/download
- Check-in/check-out system
- Aggregated state для мастера

---

### Phase 6: Testing & Deployment (Week 7-8)

**Tasks:**
- [ ] Unit tests (80%+ coverage)
- [ ] Integration tests
- [ ] E2E tests
- [ ] Production deployment (K8s)
- [ ] Monitoring setup (Prometheus + Grafana)

**Deliverables:**
- Stable MVP ready for beta testing
- Production environment
- Monitoring dashboards

---

## Open Questions

### Technical

1. **Zoom API limits** — сколько meetings можем создать в день? (нужна платная подписка?)
2. **S3 provider** — AWS S3 vs MinIO vs Cloudflare R2? (стоимость + performance)
3. **K8s hosting** — AWS EKS vs GCP GKE vs DigitalOcean Kubernetes? (стоимость для MVP)

### Business

1. **Платные практики на MVP** — включать ли или только subscription?
2. **Комиссия платформы** — 20% стандарт или кастомизируется мастером?
3. **Бесплатные практики** — можно ли мастеру делать бесплатные практики?

### Product

1. **Replay практик** — записывать автоматически или по запросу мастера?
2. **1:1 сессии** — отдельный тип практики или подкатегория?
3. **Сертификация мастеров** — нужна ли верификация или open marketplace?

---

## References

### Diagrams

- `diagrams/01-architecture-overview.mermaid` — общая архитектура
- `diagrams/02-api-flow-booking.mermaid` — booking flow
- `diagrams/03-database-schema.mermaid` — ER diagram
- `diagrams/04-calendar-reminders.mermaid` — APScheduler reminders
- `diagrams/05-quiz-data-structure.mermaid` — Quiz JSON structures
- `diagrams/06-notification-service.mermaid` — Notification architecture
- `diagrams/07-user-credentials-jsonb.mermaid` — User JSONB credentials

### Documentation

- `user-model-jsonb-pattern.md` — User model deep dive
- `master-rooms-specification.md` — Business requirements
- `master-rooms-architecture-v2.md` — Technical architecture

---

**Last Updated:** December 27, 2025  
**Version:** 1.0 (Draft for discussion)
