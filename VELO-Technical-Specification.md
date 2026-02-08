# VELO — Техническое задание

**Версия:** 1.3  
**Дата:** 8 февраля 2026  
**Статус:** Draft

---

## 1. Обзор проекта

### 1.1. Цель MVP

Создать работающую платформу для мастеров практик (медитации, йоги, breathwork), которая:

- Автоматизирует записи и напоминания
- Принимает оплату через Stripe
- Работает как Telegram WebApp
- Снимает рутину с мастеров

### 1.2. Критерии готовности MVP

| Критерий | Описание |
|----------|----------|
| Auth | Вход через Telegram работает |
| Practices | Мастер может создать практику, юзер — записаться |
| Payments | Пополнение баланса, оплата практики, вывод мастером |
| Notifications | Напоминания за 24ч, 1ч, 10мин |
| Admin | Верификация мастеров, базовая модерация |

### 1.3. Вне scope MVP

- OAuth (Google, Apple)
- Подписки (freemium есть, подписки — нет)
- Library (записи практик)
- AI-саммари (только розетка)
- Мобильные приложения (только WebApp)

---

## 2. Фазы разработки

---

## PHASE 0: Инфраструктура

### 0.1: Репозиторий + структура проекта ✅

**Цель:** Базовая структура проекта с линтерами.

**Задачи:**
- [x] GitHub репозиторий `velo` (backend в `backend/` подпапке)
- [x] Структура папок (app/modules, app/core, tests)
- [x] pyproject.toml (dependencies, build-system, black, ruff, mypy)
- [x] .gitignore (корень репо + backend/), .env.example
- [x] README.md с инструкцией по запуску
- [x] pre-commit hooks (.pre-commit-config.yaml в корне репо)
- [x] Makefile (install, run, test, lint, format, clean)
- [x] app/core/config.py (pydantic-settings, загрузка из .env)
- [x] app/core/exceptions.py (VeloError → NotFound/Forbidden/Conflict/BadRequest)
- [x] tests/conftest.py (async client fixture) + test_root.py
- [x] .python-version (pyenv → 3.12)

**Результат:**
```
velo/                              ← GitHub repo root
├── .gitignore                     ← Игнор для .DS_Store, .idea/
├── .pre-commit-config.yaml        ← Hooks: black + ruff + mypy
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                ← FastAPI app (GET / → version)
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py          ← Settings from .env
│   │   │   └── exceptions.py      ← Base exception hierarchy
│   │   └── modules/
│   │       └── __init__.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py            ← Async test client fixture
│   │   └── test_root.py           ← Root endpoint test
│   ├── pyproject.toml             ← Deps + tool config + build-system
│   ├── Makefile                   ← Dev commands (install/run/test/lint)
│   ├── .python-version            ← pyenv → 3.12
│   ├── .env.example
│   ├── .gitignore
│   └── README.md
├── desc/                          ← Project knowledge base (YAML)
├── diagrams/                      ← Mermaid diagrams
├── velo-mockups/                  ← UI prototypes
├── VELO-Design-Document.md
├── VELO-Technical-Specification.md
└── ...
```

**Решения, принятые при реализации:**
- Репо `velo` (не `velo-backend`) — место для будущего фронтенда рядом с бэкендом
- `.pre-commit-config.yaml` в корне репо — pre-commit работает от `.git/`, не от подпапки
- `[build-system]` в pyproject.toml обязателен для `pip install -e .` (регистрация `app` как импортируемого пакета)
- Makefile перенесён из Phase 0.2 — удобнее иметь `make install` с первого дня
- Приложение запускается нативно (не в Docker) для быстрых итераций, Docker — только для сервисов (Phase 0.2)

**Критерий готовности:** `ruff check .`, `mypy .`, `black --check .` проходят без ошибок. ✅
---

### 0.2: Docker Compose ✅

**Цель:** Локальное окружение с PostgreSQL и Redis.

**Задачи:**
- [x] docker-compose.dev.yml (postgres:16 + redis:7-alpine, БЕЗ app)
- [x] docker-compose.yml (postgres + redis + app — для VPS/прода)
- [x] Dockerfile для приложения (multi-stage build, python:3.12-slim)
- [x] .dockerignore (исключение venv, tests, кэшей из Docker-контекста)
- [x] Добавить команды в Makefile (dev-up, dev-down, dev-logs, dev-ps, dev-reset)
- [x] Обновить .env.example (порт 5433, POSTGRES_* переменные)
- [x] Обновить app/core/config.py (postgres_db/user/password поля)

**Результат:**
```
backend/
├── docker-compose.dev.yml   ← Локальная разработка (postgres + redis only)
├── docker-compose.yml       ← Продакшн/VPS (app + postgres + redis)
├── Dockerfile               ← Multi-stage: builder → runtime (~150MB image)
├── .dockerignore            ← Исключения для Docker build context
├── .env.example             ← Обновлён: порт 5433, POSTGRES_* переменные
├── Makefile                 ← Обновлён: dev-up/down/logs/ps/reset
└── app/core/config.py       ← Обновлён: postgres_db/user/password поля
```

**Решения, принятые при реализации:**
- PostgreSQL на порту 5433 (не 5432) — избежание конфликта с нативным Homebrew PostgreSQL
- Два compose-файла: dev (только сервисы) и prod (полный стек) — app не в Docker локально для быстрых итераций
- Multi-stage Dockerfile: builder (deps) → runtime (code only) — образ ~150MB вместо ~400MB
- python:3.12-slim (не alpine) — asyncpg/uvloop требуют glibc, которого нет в Alpine
- Healthchecks на обоих сервисах — `depends_on: condition: service_healthy` гарантирует порядок запуска
- `dev-reset` с подтверждением — защита от случайного удаления данных (`docker compose down -v`)

**Критерий готовности:** `make dev-up` поднимает PostgreSQL + Redis, `make dev-ps` показывает healthy. ✅

---

### 0.3: FastAPI скелет + health checks ✅

**Цель:** Базовый FastAPI с проверками здоровья, CORS, structlog.

**Задачи:**
- [x] app/core/database.py — AsyncEngine + AsyncSession (pool_size=10, max_overflow=20)
- [x] app/core/redis.py — async Redis client с lifecycle (init/close)
- [x] app/core/logging.py — structlog (ConsoleRenderer для dev, JSONRenderer для prod)
- [x] CORS middleware (origins из config.py, настраиваемые через .env)
- [x] GET /health — проверка DB (SELECT 1) + Redis (PING), статусы ok/degraded
- [x] GET / — версия API (было из 0.1)
- [x] Lifespan: startup (structlog + Redis init) → shutdown (Redis close + engine dispose)
- [x] tests/test_health.py — 3 теста с моками (all ok, db down, redis down)

**Результат:**
```
backend/app/core/
├── database.py   ← AsyncEngine, session factory, get_db_session()
├── redis.py      ← init_redis(), close_redis(), get_redis()
├── logging.py    ← setup_logging() — structlog конфигурация
├── config.py     ← Обновлён: cors_origins, redis_url, postgres_* поля
└── exceptions.py ← (из 0.1)

backend/app/main.py  ← Обновлён: lifespan, CORS, /health endpoint
backend/tests/test_health.py ← 3 теста (мокают DB/Redis)
```

**Endpoints:**
```
GET /        → {"name": "VELO API", "version": "0.1.0"}
GET /health  → {"status": "ok", "db": "ok", "redis": "ok"}
             → {"status": "degraded", "db": "error", "redis": "ok"}  (если что-то упало)
```

**Решения, принятые при реализации:**
- CORS origins вынесены в config.py (cors_origins) — настраиваются через .env, не хардкод
- `filter_by_level` убран из structlog processors — несовместим с PrintLoggerFactory
- `expire_on_commit=False` в session factory — объекты доступны после commit без lazy load
- Health check возвращает 200 с `"status": "degraded"` (не 500) — load balancer сам решит
- Тесты мокают DB/Redis через MagicMock + AsyncMock — работают без Docker
- `warn_unused_ignores = false` в mypy — разные версии type stubs между pip и pre-commit

**Критерий готовности:** `curl localhost:8000/health` возвращает 200 с `"status": "ok"`. ✅

---

### 0.4: Alembic + базовые миграции ✅ (механизм)

**Цель:** Система миграций БД.

**Задачи:**
- [x] alembic.ini — конфигурация (URL из config.py, не хардкод)
- [x] migrations/env.py — async runner (asyncpg через run_sync bridge)
- [x] migrations/script.py.mako — шаблон генерации миграций
- [x] app/core/database.py — добавлен Base (DeclarativeBase)
- [x] Первая миграция (пустая, проверка механизма)
- [x] `alembic upgrade head` выполняется без ошибок

**Результат:**
```
backend/
├── alembic.ini
├── migrations/
│   ├── env.py              ← Async migration runner
│   ├── script.py.mako      ← Template for new migrations
│   └── versions/
│       └── 2026_02_06_..._initial_empty.py
└── app/core/database.py    ← Обновлён: добавлен Base
```

**Решения, принятые при реализации:**
- URL берётся из app.core.config (единый источник), а не из alembic.ini
- Async bridge: asyncpg не работает с Alembic напрямую — `run_sync()` оборачивает sync-вызов
- Миксины (TimestampMixin, UUIDMixin) отложены до Phase 1.1 вместе с моделью User
- file_template с датой и slug для читаемых имён файлов миграций

**⚠️ Примечание:** Пустая миграция подтверждает работу механизма. Полноценная проверка autogenerate — в Phase 1.1, когда Alembic сгенерирует CREATE TABLE users.

**Критерий готовности:** `alembic upgrade head` выполняется без ошибок. ✅

---

### 0.5: VPS + деплой ✅

**Цель:** Приложение работает на сервере с HTTPS.

**Задачи:**
- [x] VPS (Inferno, NL, Ubuntu 22.04, 2 CPU / 4GB RAM / 30GB NVMe)
- [x] Домен: `api.talentir.info` → A-запись на VPS
- [x] `install_velo.sh` — единый скрипт установки (Docker, Nginx, Certbot, UFW, SSH deploy key)
- [x] Nginx reverse proxy → `127.0.0.1:8000`
- [x] SSL сертификат (Let's Encrypt) + auto-renewal cron
- [x] Firewall: только 22/80/443
- [x] `.env` на сервере (автогенерация с рандомными паролями)
- [x] Management-скрипт `velo` (start/stop/restart/status/logs/update/backup/db)
- [x] Ежедневный backup cron (4 AM, ротация 7 дней)
- [x] Production hardening — закрытие TD-001..TD-009

**Результат:**
```
VPS (37.1.204.171):
├── /opt/velo/
│   ├── repo/              ← Git clone (deploy key, read-only)
│   │   └── backend/       ← Docker stack (app + postgres + redis)
│   ├── creds/             ← Автосгенерированные креды
│   ├── scripts/manage.sh  ← Management script (symlink: /usr/local/bin/velo)
│   └── backups/           ← Ежедневные бэкапы (pg_dump + .env)
├── /etc/nginx/sites-available/velo  ← Reverse proxy + SSL
└── /etc/letsencrypt/      ← SSL-сертификат для api.talentir.info
```

**Решения, принятые при реализации:**
- Ручной деплой (`velo update`) вместо GitHub Actions — промежуточные пуши для БЗ Claude, не всегда готовы к деплою
- Ubuntu 22.04 (не 24.04) — предустановлена хостером, LTS до 2027, обновление ОС не оправдано
- Deploy key (read-only SSH) вместо personal access token — минимальные права
- `install_velo.sh` генерирует `.env` с рандомными паролями (openssl rand) — без дефолтных кредов
- Postgres/Redis без published портов (Docker internal network only) — TD-004
- App на `127.0.0.1:8000` — только Nginx видит его
- Non-root user в Dockerfile (`USER velo`, UID 1000) — TD-005
- Alembic файлы копируются в Docker image — `velo db migrate` работает внутри контейнера

**Production hardening (закрыто в рамках Phase 0.5):**
- TD-001: SECRET_KEY обязателен в production (validator в config.py)
- TD-002: CORS credentials=False при wildcard origins
- TD-003: `GET /ready` (503 при деградации) + `GET /health` (200 всегда)
- TD-004: Postgres/Redis — no published ports
- TD-005: Docker non-root user
- TD-006: DATABASE_URL обязателен в production
- TD-007: VeloError exception handler + logging
- TD-008: `get_db_reader()` для read-only запросов
- TD-009: Lifespan try/finally — cleanup при падении startup

**Endpoints:**
```
GET /        → {"name": "VELO API", "version": "0.1.0"}
GET /health  → {"status": "ok", "db": "ok", "redis": "ok"}          (200 always)
GET /ready   → {"status": "ok", "db": "ok", "redis": "ok"}          (200 or 503)
```

**Management:**
```
velo status              — Docker ps + health check + external access
velo logs [app|db|redis] — Docker logs -f
velo update              — git pull + rebuild + migrate + restart
velo restart [app]       — Restart all or just app
velo backup              — pg_dump + .env → tar.gz
velo db connect          — psql в контейнер
velo db migrate          — alembic upgrade head
velo ssl renew           — certbot renew
```

**Критерий готовности:** `curl https://api.talentir.info/health` → `{"status":"ok"}`. ✅

---

### 0.6: Logging + Audit → перенесена перед Phase 6

> **Примечание:** Базовый structlog уже работает (Phase 0.3). Полноценный аудит нужен
> только для финансовых операций (Phase 6). Секция перенесена как **Pre-6: Audit** —
> см. перед Phase 6: Payments.

---

## PHASE 1: Auth + Users

### 1.1: Модель User ✅

**Цель:** Базовая модель пользователя.

**Задачи:**
- [x] app/core/mixins.py — UUIDMixin + TimestampMixin
- [x] app/modules/users/models.py — User model + UserRole enum
- [x] Миграция `create_users_table`

**Результат:**
```
backend/app/
├── core/
│   └── mixins.py              ← UUIDMixin, TimestampMixin (DateTime timezone=True)
└── modules/
    └── users/
        ├── __init__.py
        └── models.py          ← UserRole enum + User model
```

**Решения, принятые при реализации:**
- `telegram_id` — отдельная колонка (BigInteger, unique, indexed) для быстрого поиска при логине. Правило: ищем по колонке, храним в JSONB
- `credentials` — JSONB-песочница для данных auth неясной структуры (telegram username, photo, будущие email/password/OAuth)
- `role` хранится как `String(20)` (не PostgreSQL ENUM) — asyncpg не умеет кастить строки в PG ENUM при server_default. Python-side `UserRole(str, Enum)` валидирует
- `balance_user` — `Numeric(18, 2)`, default=0, не трогаем до Phase 6
- Миксины: `UUIDMixin` (uuid4 app-side), `TimestampMixin` (created_at server_default, updated_at ORM-level onupdate)
- Все datetime-колонки — `DateTime(timezone=True)` (TIMESTAMP WITH TIME ZONE)

**Критерий готовности:** Миграция применена, таблица создана. ✅

---

### 1.2: Telegram WebApp Auth ✅

**Цель:** Аутентификация через Telegram initData.

**Задачи:**
- [x] app/modules/auth/service.py — валидация initData (HMAC-SHA256)
- [x] app/modules/auth/router.py — POST /api/v1/auth/telegram
- [x] POST /api/v1/auth/logout — отзыв сессии
- [x] Атомарный upsert юзера при входе (INSERT ON CONFLICT DO UPDATE)
- [x] app/core/exceptions.py — добавлен UnauthorizedError (401)
- [x] Тесты валидации (8 тестов)

**Endpoints:**
```
POST /api/v1/auth/telegram  → AuthResponse {user, session_token}
POST /api/v1/auth/logout    → 204 No Content
```

**Решения, принятые при реализации:**
- `INSERT ... ON CONFLICT DO UPDATE` вместо SELECT+INSERT — атомарно, без race condition при двойном клике
- `session.commit()` ПЕРЕД созданием Redis-сессии — если commit упадёт, orphan-сессии в Redis не будет
- `telegram_bot_token` — пустой дефолт, заполняется в валидаторе (dev: fake token, prod: required)
- initData expiry: 5 минут (защита от replay)

**Критерий готовности:** WebApp может залогинить юзера. ✅

---

### 1.3: Сессии (Redis) ✅

**Цель:** Управление сессиями через Redis.

**Задачи:**
- [x] Сессии в auth/service.py (create/get/delete) — не отдельный файл
- [x] FastAPI Dependency вместо Middleware (решение Phase 0.5 обсуждение)
- [x] app/modules/auth/dependencies.py — get_current_user, get_optional_user, get_current_admin
- [x] TTL 30 дней (настраивается через SESSION_TTL_DAYS)

**Формат сессии в Redis:**
```
Key: session:{token}    (token = secrets.token_urlsafe(48))
Value: {"user_id": "uuid", "telegram_id": 123, "created_at": "iso"}
TTL: 30 days
```

**Dependencies (вместо middleware):**
```python
get_current_user(request, session) → User       # 401 если нет токена
get_optional_user(request, session) → User|None  # None для анонимов
get_current_admin(user) → User                   # 403 если не admin
```

**Решения, принятые при реализации:**
- Dependency вместо Middleware — явная авторизация на уровне эндпоинта, громко падает при отсутствии токена (не молчаливый None в request.state)
- Бесшовная миграция в будущем: при добавлении standalone app (JWT) меняется одна функция get_current_user, ни один роутер не трогаем
- Три уровня: обязательный (get_current_user), опциональный (get_optional_user), админский (get_current_admin)

**Критерий готовности:** Запросы с валидным токеном авторизованы. ✅

---

### 1.4: CRUD профиля юзера

**Цель:** Endpoints для профиля.

**Задачи:**
- [ ] app/modules/users/schemas.py — Pydantic schemas
- [ ] app/modules/users/service.py — get, update
- [ ] app/modules/users/router.py — GET/PATCH /users/me
- [ ] Тесты

**Endpoints:**
```
GET  /api/v1/users/me        → UserResponse
PATCH /api/v1/users/me       → UserResponse (body: UserUpdate)
```

**Критерий готовности:** Юзер может видеть и редактировать свой профиль.

---

## PHASE 2: Masters

### 2.1: MasterProfile + JSONB data

**Цель:** Модель профиля мастера.

**Задачи:**
- [ ] app/modules/masters/models.py
- [ ] MasterProfile с JSONB data
- [ ] Поля frozen_amount и available_amount
- [ ] Миграция

**Модель:**
```python
class MasterProfile(Base):
    __tablename__ = "master_profiles"
    
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    data: Mapped[dict] = mapped_column(JSONB, default=dict)
    # data содержит: account, availability, profile, settings, stats
    
    # Balance fields (updated by listeners on master_ledger)
    frozen_amount: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), default=0)
    available_amount: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), default=0)
    
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())
    
    user: Mapped["User"] = relationship(back_populates="master_profile")
```

**Структура data JSONB:**
```json
{
  "account": {
    "status": "pending|verified|suspended|banned",
    "verification": {
      "verified_at": "datetime",
      "verified_by": "admin_id"
    }
  },
  "availability": {
    "is_accepting": true,
    "note": "В отпуске до 15.02"
  },
  "profile": {
    "bio": "...",
    "short_bio": "...",
    "methods": ["meditation", "breathwork"],
    "experience_years": 5,
    "certifications": []
  },
  "settings": {
    "auto_confirm_bookings": true,
    "max_participants_default": 20
  },
  "stats": {
    "total_practices": 47,
    "total_participants": 312,
    "avg_rating": 4.8
  }
}
```

**Критерий готовности:** Миграция применена.

---

### 2.2: Заявка на мастера

**Цель:** Flow подачи заявки (3 шага из мокапов).

**Задачи:**
- [ ] POST /api/v1/masters/apply — создание заявки
- [ ] Шаг 1: Профиль (имя, email, телефон)
- [ ] Шаг 2: Опыт (направления, сертификаты)
- [ ] Шаг 3: Документы (загрузка)
- [ ] Статус "pending_verification"

**Endpoint:**
```
POST /api/v1/masters/apply
Body: {
  "profile": {...},
  "experience": {...},
  "documents": [...]
}
Response: {"status": "pending_verification"}
```

**Критерий готовности:** Юзер может подать заявку на мастера.

---

### 2.3: Верификация мастера

**Цель:** Админ может верифицировать мастера.

**Задачи:**
- [ ] POST /api/v1/admin/masters/{id}/verify
- [ ] POST /api/v1/admin/masters/{id}/reject
- [ ] Изменение user.role на MASTER при верификации
- [ ] Уведомление мастеру

**Endpoint:**
```
POST /api/v1/admin/masters/{user_id}/verify
Body: {"notes": "Всё ок"}
Response: {"status": "verified"}

POST /api/v1/admin/masters/{user_id}/reject
Body: {"reason": "Недостаточно опыта"}
Response: {"status": "rejected"}
```

**Критерий готовности:** Админ может верифицировать/отклонить заявку.

---

## PHASE 3: Admin

### 3.1: Админские эндпоинты

**Цель:** Базовые админ-функции.

**Задачи:**
- [ ] app/modules/admin/router.py
- [ ] Middleware проверки role=ADMIN
- [ ] GET /api/v1/admin/stats — базовая статистика

**Endpoint:**
```
GET /api/v1/admin/stats
Response: {
  "users_count": 150,
  "masters_count": 12,
  "practices_count": 47,
  "pending_verifications": 2
}
```

**Критерий готовности:** Админ видит статистику.

---

### 3.2: Список юзеров/мастеров

**Цель:** Админ видит всех пользователей.

**Задачи:**
- [ ] GET /api/v1/admin/users — список юзеров (пагинация, фильтры)
- [ ] GET /api/v1/admin/masters — список мастеров
- [ ] GET /api/v1/admin/masters/pending — ожидающие верификации

**Endpoints:**
```
GET /api/v1/admin/users?limit=20&offset=0&role=user
GET /api/v1/admin/masters?status=verified
GET /api/v1/admin/masters/pending
```

**Критерий готовности:** Админ видит списки с фильтрами.

---

### 3.3: Модерация

**Цель:** Базовая система жалоб.

**Задачи:**
- [ ] Модель Report (жалобы)
- [ ] POST /api/v1/reports — создать жалобу (юзер)
- [ ] GET /api/v1/admin/reports — список жалоб
- [ ] POST /api/v1/admin/reports/{id}/resolve

**Модель:**
```python
class Report(Base):
    __tablename__ = "reports"
    
    id: Mapped[UUID]
    reporter_id: Mapped[UUID]  # Кто пожаловался
    target_type: Mapped[str]   # user, master, practice
    target_id: Mapped[UUID]
    reason: Mapped[str]
    status: Mapped[str]        # pending, resolved, dismissed
    resolved_by: Mapped[UUID | None]
    resolution_note: Mapped[str | None]
```

**Критерий готовности:** Жалобы можно создавать и обрабатывать.

---

## PHASE 4: Practices

### 4.1: Модель Practice

**Цель:** Базовая модель практики.

**Задачи:**
- [ ] app/modules/practices/models.py
- [ ] Practice model со всеми типами
- [ ] Миграция

**Модель:**
```python
class PracticeType(str, Enum):
    LIVE = "live"
    SERIES = "series"
    ONE_ON_ONE = "one_on_one"
    REPLAY = "replay"

class PracticeStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Practice(Base):
    __tablename__ = "practices"
    
    id: Mapped[UUID]
    master_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    
    type: Mapped[PracticeType]
    status: Mapped[PracticeStatus] = mapped_column(default=PracticeStatus.DRAFT)
    
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    
    scheduled_at: Mapped[datetime]
    duration_minutes: Mapped[int]
    timezone: Mapped[str] = mapped_column(String(50))
    
    max_participants: Mapped[int | None]
    current_participants: Mapped[int] = mapped_column(default=0)
    
    # Zoom (manual for MVP)
    zoom_link: Mapped[str | None] = mapped_column(String(500))
    
    # Series support
    parent_practice_id: Mapped[UUID | None] = mapped_column(ForeignKey("practices.id"))
    
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
```

**Критерий готовности:** Миграция применена.

---

### 4.2: CRUD для мастера

**Цель:** Мастер может управлять практиками.

**Задачи:**
- [ ] app/modules/practices/service.py
- [ ] app/modules/practices/router.py
- [ ] POST /practices — создание
- [ ] GET /practices/{id} — детали
- [ ] PATCH /practices/{id} — редактирование
- [ ] DELETE /practices/{id} — удаление (soft delete)
- [ ] Проверка ownership

**Endpoints:**
```
POST   /api/v1/practices
GET    /api/v1/practices/{id}
PATCH  /api/v1/practices/{id}
DELETE /api/v1/practices/{id}
GET    /api/v1/masters/me/practices  # Мои практики
```

**Критерий готовности:** Мастер может создать и управлять практикой.

---

### 4.3: Список практик для юзеров

**Цель:** Юзеры видят доступные практики.

**Задачи:**
- [ ] GET /api/v1/practices — публичный список
- [ ] Фильтры: master_id, type, date_from, date_to, status
- [ ] Сортировка: scheduled_at, price
- [ ] Пагинация

**Endpoint:**
```
GET /api/v1/practices?type=live&date_from=2026-02-01&limit=20
Response: {
  "items": [...],
  "total": 45,
  "limit": 20,
  "offset": 0
}
```

**Критерий готовности:** Юзер видит список практик с фильтрами.

---

### 4.4: PracticePricing

**Цель:** Цены практик.

**Задачи:**
- [ ] app/modules/practices/models.py — PracticePricing
- [ ] Связь 1:1 с Practice
- [ ] Миграция

**Модель:**
```python
class PracticePricing(Base):
    __tablename__ = "practice_pricing"
    
    practice_id: Mapped[UUID] = mapped_column(
        ForeignKey("practices.id"), 
        primary_key=True
    )
    
    is_free: Mapped[bool] = mapped_column(default=True)
    price_cents: Mapped[int | None]
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Future
    # early_bird_price_cents: int | None
    # early_bird_until: datetime | None
    
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
```

**Критерий готовности:** Мастер может установить цену практики.

---

## PHASE 5: Bookings

### 5.1: Модель Booking

**Цель:** Бронирования практик.

**Задачи:**
- [ ] app/modules/bookings/models.py
- [ ] Booking model
- [ ] Миграция

**Модель:**
```python
class BookingStatus(str, Enum):
    PENDING = "pending"      # Ждёт оплаты
    CONFIRMED = "confirmed"  # Оплачено
    ATTENDED = "attended"    # Посетил
    NO_SHOW = "no_show"      # Не пришёл
    CANCELLED = "cancelled"  # Отменено

class Booking(Base):
    __tablename__ = "bookings"
    
    id: Mapped[UUID]
    practice_id: Mapped[UUID] = mapped_column(ForeignKey("practices.id"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    
    status: Mapped[BookingStatus] = mapped_column(default=BookingStatus.PENDING)
    
    # Payment reference
    purchase_id: Mapped[UUID | None] = mapped_column(ForeignKey("purchases.id"))
    
    booked_at: Mapped[datetime] = mapped_column(server_default=func.now())
    cancelled_at: Mapped[datetime | None]
    cancellation_reason: Mapped[str | None]
    
    # Attendance
    joined_at: Mapped[datetime | None]
    left_at: Mapped[datetime | None]
    
    # UNIQUE constraint
    __table_args__ = (
        UniqueConstraint("practice_id", "user_id", name="uq_booking_practice_user"),
    )
```

**Критерий готовности:** Миграция применена.

---

### 5.2: Создание/отмена брони

**Цель:** Юзер может записаться и отменить.

**Задачи:**
- [ ] POST /api/v1/bookings — создать бронь
- [ ] DELETE /api/v1/bookings/{id} — отменить
- [ ] Проверка лимита мест
- [ ] Проверка оплаты (если платная)
- [ ] Уведомления

**Endpoints:**
```
POST   /api/v1/bookings
Body: {"practice_id": "uuid"}
Response: {"booking": {...}, "status": "confirmed|pending_payment"}

DELETE /api/v1/bookings/{id}
Response: {"status": "cancelled"}
```

**Критерий готовности:** Юзер может записаться на практику.

---

### 5.3: Waitlist

**Цель:** Очередь ожидания.

**Задачи:**
- [ ] Модель Waitlist
- [ ] POST /api/v1/practices/{id}/waitlist — встать в очередь
- [ ] DELETE /api/v1/waitlist/{id} — выйти из очереди
- [ ] При отмене брони — уведомить первого в очереди
- [ ] 30 минут на подтверждение

**Модель:**
```python
class Waitlist(Base):
    __tablename__ = "waitlist"
    
    id: Mapped[UUID]
    practice_id: Mapped[UUID]
    user_id: Mapped[UUID]
    position: Mapped[int]
    joined_at: Mapped[datetime]
    notified_at: Mapped[datetime | None]
    expires_at: Mapped[datetime | None]
    status: Mapped[str]  # waiting, notified, converted, expired
```

**Критерий готовности:** Waitlist работает автоматически.

---

### 5.4: Attendance tracking

**Цель:** Учёт посещаемости.

**Задачи:**
- [ ] POST /api/v1/bookings/{id}/join — отметить вход
- [ ] POST /api/v1/bookings/{id}/leave — отметить выход
- [ ] Автоматический no_show после окончания практики
- [ ] Статистика для мастера

**Критерий готовности:** Мастер видит кто пришёл.

---

## PRE-6: Logging Hardening + Audit

> Перенесена из Phase 0.6. Базовый structlog уже работает (Phase 0.3).
> Здесь: доработка логирования + аудит финансовых операций, необходимый для Phase 6.

### Pre-6.1: Logging hardening

**Цель:** Довести structlog до production-качества.

**Задачи:**
- [ ] Фильтрация по LOG_LEVEL (structlog `make_filtering_bound_logger`)
- [ ] Идемпотентность `setup_logging()` (защита от двойной инициализации)
- [ ] Middleware для trace_id (X-Trace-ID в каждый запрос/ответ)

**Middleware для trace_id:**
```python
@app.middleware("http")
async def trace_id_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-ID", str(uuid4()))
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(trace_id=trace_id)
    response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id
    return response
```

**Критерий готовности:** `LOG_LEVEL=WARNING` фильтрует debug/info, trace_id в каждом лог-сообщении.

---

### Pre-6.2: Audit Service

**Цель:** Аудит финансовых операций — юридическое требование.

**Задачи:**
- [ ] app/core/audit.py — сервис аудита
- [ ] Модель AuditLog
- [ ] Миграция

**Модель AuditLog:**
```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), index=True)
    
    event: Mapped[str] = mapped_column(String(100), index=True)
    # Events: purchase_created, refund, withdrawal, role_changed, 
    #         master_verified, balance_changed, booking_cancelled, etc.
    
    actor_id: Mapped[UUID | None]  # Who performed action (NULL for system)
    actor_type: Mapped[str] = mapped_column(String(20))  # user, master, admin, system
    
    target_type: Mapped[str] = mapped_column(String(50))  # user, practice, booking, payment
    target_id: Mapped[UUID]
    
    data: Mapped[dict] = mapped_column(JSONB)  # Full context snapshot
    
    ip_address: Mapped[str | None] = mapped_column(String(45))  # IPv6
    user_agent: Mapped[str | None] = mapped_column(String(500))
    trace_id: Mapped[str | None] = mapped_column(String(36))
```

**Сервис аудита:**
```python
class AuditService:
    async def record(
        self,
        event: str,
        target_type: str,
        target_id: UUID,
        data: dict,
        actor_id: UUID | None = None,
        actor_type: str = "system",
        request: Request | None = None,
    ) -> AuditLog:
        log = AuditLog(
            event=event,
            actor_id=actor_id,
            actor_type=actor_type,
            target_type=target_type,
            target_id=target_id,
            data=data,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
            trace_id=structlog.contextvars.get_contextvars().get("trace_id"),
        )
        self.session.add(log)
        await self.session.commit()
        return log
```

**Обязательные события для аудита:**

| Событие | Когда логировать |
|---------|------------------|
| `balance_topup` | Пополнение баланса |
| `purchase_created` | Покупка практики |
| `purchase_refunded` | Возврат |
| `withdrawal_requested` | Запрос на вывод |
| `withdrawal_confirmed` | Подтверждение вывода |
| `master_verified` | Верификация мастера |
| `master_rejected` | Отклонение заявки |
| `role_changed` | Изменение роли |
| `user_blocked` | Блокировка юзера |
| `practice_cancelled` | Отмена практики мастером |

**Retention policy:**
- Application logs (stdout): 30 дней
- Audit logs (БД): 5 лет (законодательные требования для финансов)

**Критерий готовности:** Аудит пишется в БД, trace_id связывает лог + аудит.

---

## PHASE 6: Payments

### 6.1: Ledgers

**Цель:** Три журнала транзакций.

**Задачи:**
- [ ] app/modules/payments/models.py
- [ ] UserLedger, MasterLedger, CompanyLedger
- [ ] Миграции

**Модели:**
```python
class LedgerStatus(str, Enum):
    PENDING = "pending"
    DONE = "done"
    CANCELLED = "cancelled"

class UserLedger(Base):
    __tablename__ = "user_ledger"
    
    id: Mapped[UUID]
    user_id: Mapped[UUID]
    amount: Mapped[Decimal] = mapped_column(DECIMAL(18, 2))
    status: Mapped[LedgerStatus] = mapped_column(default=LedgerStatus.DONE)
    reason: Mapped[str]  # "payment:123", "purchase:practice=456"
    notes: Mapped[str | None]
    created_at: Mapped[datetime]

class MasterLedger(Base):
    __tablename__ = "master_ledger"
    
    id: Mapped[UUID]
    user_id: Mapped[UUID]
    amount: Mapped[Decimal] = mapped_column(DECIMAL(18, 2))
    is_frozen: Mapped[bool] = mapped_column(default=True)  # NEW!
    status: Mapped[LedgerStatus] = mapped_column(default=LedgerStatus.DONE)
    reason: Mapped[str]  # "sale:practice=456", "commission:practice=456"
    practice_id: Mapped[UUID | None]  # Для связи frozen → unfrozen
    notes: Mapped[str | None]
    created_at: Mapped[datetime]
    
class CompanyLedgerType(str, Enum):
    COMMISSION = "commission"
    MARKETING = "marketing"
    REFUND = "refund"
    WITHDRAWAL_FEE = "withdrawal_fee"

class CompanyLedger(Base):
    __tablename__ = "company_ledger"
    
    id: Mapped[UUID]
    amount: Mapped[Decimal] = mapped_column(DECIMAL(18, 2))
    type: Mapped[CompanyLedgerType]
    reason: Mapped[str]
    status: Mapped[LedgerStatus] = mapped_column(default=LedgerStatus.DONE)
    created_at: Mapped[datetime]
```

**Критерий готовности:** Миграции применены.

---

### 6.2: Balance listeners

**Цель:** Автоматический пересчёт балансов.

**Задачи:**
- [ ] app/modules/payments/listeners.py
- [ ] Listener на user_ledger → User.balance_user
- [ ] Listener на master_ledger → MasterProfile.frozen_amount / available_amount
- [ ] Защита от прямого изменения балансов

**Логика:**
```python
# User balance
User.balance_user = SUM(user_ledger.amount) WHERE status='done'

# Master balance (ДВА поля!)
MasterProfile.frozen_amount = SUM(master_ledger.amount) 
    WHERE status='done' AND is_frozen=true
MasterProfile.available_amount = SUM(master_ledger.amount) 
    WHERE status='done' AND is_frozen=false
```

**Критерий готовности:** Балансы автоматически обновляются при записи в ledger.

---

### 6.3: Stripe integration (пополнение)

**Цель:** Пополнение баланса через Stripe.

**Задачи:**
- [ ] app/modules/payments/stripe.py
- [ ] POST /api/v1/payments/topup — создать Stripe session
- [ ] Webhook для подтверждения
- [ ] Запись в user_ledger

**Flow:**
```
1. User: POST /payments/topup {amount: 100}
2. Server: Create Stripe Checkout Session
3. Server: Return {checkout_url: "..."}
4. User: Redirect to Stripe, оплачивает
5. Stripe: Webhook → /webhooks/stripe
6. Server: 
   - payments: direction=in, amount=100, status=confirmed
   - user_ledger: amount=+100, reason="payment:123"
```

**Критерий готовности:** Юзер может пополнить баланс.

---

### 6.4: Purchase flow (frozen → unfrozen)

**Цель:** Покупка практики с заморозкой.

**Задачи:**
- [ ] Модель Purchase
- [ ] POST /api/v1/practices/{id}/purchase
- [ ] Проверка баланса
- [ ] Заморозка у мастера
- [ ] Event на завершение практики → разморозка + комиссия

**Шаг 1: Регистрация на практику**
```python
# При покупке практики ($50):
user_ledger:   amount=-50, reason="purchase:practice=456"
master_ledger: amount=+50, is_frozen=true, reason="sale:practice=456"
purchases:     practice_id=456, amount=50, status=pending
# MasterProfile: frozen_amount += 50
```

**Шаг 2: Практика завершена (event)**
```python
# Practice.status = completed triggers:
master_ledger: UPDATE is_frozen=false WHERE practice_id=456
master_ledger: amount=-7.50, reason="commission:practice=456"
company_ledger: amount=+7.50, type=commission
purchases: UPDATE status=completed
# MasterProfile: frozen=0, available=42.50
```

**Критерий готовности:** Деньги замораживаются при покупке, размораживаются после практики.

---

### 6.5: Cancellations & Refunds

**Цель:** Политика отмен.

**Задачи:**
- [ ] CANCELLATION_DEADLINE_HOURS = 24
- [ ] DELETE /api/v1/bookings/{id} — проверка дедлайна
- [ ] Автовозврат при отмене мастером
- [ ] No-show логика

**Бизнес-правила:**
| Кто отменяет | Когда | Результат |
|--------------|-------|-----------|
| Юзер | > 24ч до практики | 100% возврат |
| Юзер | < 24ч до практики | 0% возврат |
| Мастер | Любое время | 100% возврат всем |
| No-show | После практики | Деньги у мастера |

**Возврат (юзер > 24ч):**
```python
master_ledger: amount=-50, reason="refund:practice=456"
user_ledger:   amount=+50, reason="refund:practice=456"
purchases:     UPDATE status=cancelled
# MasterProfile: frozen_amount -= 50
```

**Отмена мастером:**
```python
# Для КАЖДОГО участника:
master_ledger: amount=-50, reason="refund:practice=456,cancelled_by_master"
user_ledger:   amount=+50, reason="refund:practice=456"
```

**Критерий готовности:** Отмены работают по правилам.

---

### 6.6: Withdrawals

**Цель:** Вывод средств мастером.

**Задачи:**
- [ ] Модель Payment (direction=out)
- [ ] POST /api/v1/masters/me/withdraw
- [ ] Проверка available_amount >= запрос + WITHDRAWAL_FEE
- [ ] Проверка MIN_WITHDRAWAL_AMOUNT
- [ ] Статус pending → ручное подтверждение админом

**Настраиваемые переменные:**
```
MIN_WITHDRAWAL_AMOUNT = 50  # минимум $50
WITHDRAWAL_FEE = 2          # комиссия $2
```

**Flow:**
```python
# Запрос вывода $1000:
master_ledger:  amount=-1000, is_frozen=false, reason="withdrawal:payment=789"
company_ledger: amount=+2, type=withdrawal_fee
payments:       direction=out, amount=998, status=pending
# Админ подтверждает → status=confirmed → ручной перевод
```

**Критерий готовности:** Мастер может запросить вывод из available.

---

### 6.7: Promocodes

**Цель:** Два типа промокодов.

**Задачи:**
- [ ] Модель Promo
- [ ] POST /api/v1/admin/promos — создание Company Promo
- [ ] POST /api/v1/masters/me/promos — создание Master Promo
- [ ] Применение при покупке

**Модель:**
```python
class PromoType(str, Enum):
    COMPANY = "company"  # Компания платит
    MASTER = "master"    # Мастер отказывается от выручки

class Promo(Base):
    __tablename__ = "promos"
    
    id: Mapped[UUID]
    code: Mapped[str] = mapped_column(String(50), unique=True)
    type: Mapped[PromoType]
    
    discount_percent: Mapped[int]  # 5, 25, 50, 75, 100
    
    # Для MASTER promo:
    master_id: Mapped[UUID | None]
    practice_id: Mapped[UUID | None]  # Опционально: только для одной практики
    
    # Лимиты:
    max_uses: Mapped[int | None]
    used_count: Mapped[int] = mapped_column(default=0)
    valid_until: Mapped[datetime | None]
    
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime]
```

**Company Promo (100% скидка WELCOME):**
```python
user_ledger:    amount=0, reason="purchase:practice=456,promo:WELCOME"
master_ledger:  amount=+50, is_frozen=true, reason="sale:practice=456"
company_ledger: amount=-50, type=marketing, reason="promo:WELCOME"
# После практики: комиссия $0 (юзер заплатил $0)
```

**Master Promo (100% скидка ALEX-VIP):**
```python
user_ledger:   amount=0, reason="purchase:practice=456,promo:ALEX-VIP"
master_ledger: amount=0, is_frozen=true, reason="sale:practice=456,promo:ALEX-VIP"
# Мастер отказался от денег. Company ledger не затронут.
```

**Критерий готовности:** Оба типа промокодов работают.

---

### 6.8: Internal transfer (Master → User Balance)

**Цель:** Мастер может перевести деньги с Available на свой User Balance.

**Кейс:** Мастер хочет купить практику другого мастера. Он не может платить с Master Balance напрямую — сначала переводит на User Balance.

**Задачи:**
- [ ] POST /api/v1/masters/me/transfer-to-user
- [ ] Проверка available_amount >= сумма
- [ ] Записи в оба ledger-а

**Endpoint:**
```
POST /api/v1/masters/me/transfer-to-user
Body: {"amount": 50}
Response: {"user_balance": 150, "available_amount": 200}
```

**Записи в системе:**
```python
master_ledger:  user_id=2, amount=-50, is_frozen=false, reason="transfer:internal"
user_ledger:    user_id=2, amount=+50, reason="transfer:internal"
# MasterProfile: available_amount -= 50
# User: balance_user += 50
# Σ = -50 + 50 = 0 ✓
```

**Критерий готовности:** Мастер может перевести себе на user balance для покупок.

---

### 6.9: Розетка для подписок

**Цель:** Таблица подписок без логики.

**Задачи:**
- [ ] Модель Subscription
- [ ] Миграция
- [ ] TODO комментарии в коде

**Модель:**
```python
class Subscription(Base):
    """TODO: Implement subscription logic in future phase."""
    __tablename__ = "subscriptions"
    
    id: Mapped[UUID]
    user_id: Mapped[UUID]
    plan: Mapped[str]  # monthly, yearly
    status: Mapped[str]  # active, cancelled, expired
    stripe_subscription_id: Mapped[str | None]
    current_period_start: Mapped[datetime]
    current_period_end: Mapped[datetime]
```

**Критерий готовности:** Таблица создана, логика отложена.

---

## PHASE 7: Notifications

### 7.1: Модели Notification + Delivery

**Цель:** Система уведомлений.

**Задачи:**
- [ ] app/modules/notifications/models.py
- [ ] Notification + NotificationDelivery
- [ ] Миграции

**Модели:** (из готового кода)
```python
class Notification(Base):
    __tablename__ = "notifications"
    
    id: Mapped[int]
    source: Mapped[str]
    text: Mapped[str]
    buttons: Mapped[str | None]
    
    target_type: Mapped[str]  # user, all, filter
    target_value: Mapped[str]
    
    priority: Mapped[int] = mapped_column(default=5)
    status: Mapped[str] = mapped_column(default="pending")
    
    # ... остальные поля

class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"
    
    id: Mapped[int]
    notification_id: Mapped[int]
    user_id: Mapped[int]
    status: Mapped[str] = mapped_column(default="pending")
    attempts: Mapped[int] = mapped_column(default=0)
```

**Критерий готовности:** Миграции применены.

---

### 7.2: NotificationProcessor

**Цель:** Фоновый воркер для отправки.

**Задачи:**
- [ ] app/modules/notifications/processor.py
- [ ] Polling pending notifications
- [ ] Retry logic (3 попытки)
- [ ] Priority queue

**Критерий готовности:** Уведомления отправляются автоматически.

---

### 7.3: Telegram-бот

**Цель:** Бот для уведомлений.

**Задачи:**
- [ ] app/bot/main.py — aiogram bot
- [ ] Интеграция с NotificationProcessor
- [ ] Отправка сообщений юзерам

**Критерий готовности:** Бот отправляет уведомления в Telegram.

---

### 7.4: Напоминания

**Цель:** Авто-напоминания о практиках.

**Задачи:**
- [ ] При создании booking → планировать 3 напоминания
- [ ] 24 часа до практики
- [ ] 1 час до практики
- [ ] 10 минут до практики
- [ ] APScheduler или Celery Beat

**Критерий готовности:** Напоминания приходят автоматически.

---

## PHASE 8: Diary/State

### 8.1: Check-ins

**Цель:** Состояние до практики.

**Задачи:**
- [ ] app/modules/diary/models.py — Checkin
- [ ] POST /api/v1/practices/{id}/checkin
- [ ] GET /api/v1/users/me/checkins

**Модель:**
```python
class Checkin(Base):
    __tablename__ = "checkins"
    
    id: Mapped[UUID]
    practice_id: Mapped[UUID]
    user_id: Mapped[UUID]
    booking_id: Mapped[UUID]
    
    mood: Mapped[str]  # low, mid, high
    comment: Mapped[str | None]
    
    created_at: Mapped[datetime]
```

**Критерий готовности:** Юзер может отправить check-in.

---

### 8.2: Feedbacks

**Цель:** Обратная связь после практики.

**Задачи:**
- [ ] Модель Feedback
- [ ] POST /api/v1/practices/{id}/feedback
- [ ] GET /api/v1/users/me/feedbacks

**Модель:**
```python
class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id: Mapped[UUID]
    practice_id: Mapped[UUID]
    user_id: Mapped[UUID]
    booking_id: Mapped[UUID]
    
    rating: Mapped[str]  # fire, good, confused
    comment: Mapped[str | None]
    
    created_at: Mapped[datetime]
```

**Критерий готовности:** Юзер может оставить feedback.

---

### 8.3: Diary entries

**Цель:** Личные записи дневника.

**Задачи:**
- [ ] Модель DiaryEntry
- [ ] CRUD /api/v1/diary
- [ ] Не связано с практикой (опционально)

**Модель:**
```python
class DiaryEntry(Base):
    __tablename__ = "diary_entries"
    
    id: Mapped[UUID]
    user_id: Mapped[UUID]
    practice_id: Mapped[UUID | None]  # Optional
    
    title: Mapped[str | None]
    content: Mapped[str]
    mood: Mapped[str | None]
    
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
```

**Критерий готовности:** Юзер может вести дневник.

---

### 8.4: Агрегация для мастера

**Цель:** Мастер видит сводку по практике.

**Задачи:**
- [ ] GET /api/v1/practices/{id}/insights
- [ ] Агрегированные check-ins (анонимно)
- [ ] Агрегированные feedbacks (анонимно)
- [ ] Статистика: % high/mid/low, % fire/good/confused

**Endpoint:**
```
GET /api/v1/practices/{id}/insights
Response: {
  "participants": 15,
  "checkins": {"high": 8, "mid": 5, "low": 2},
  "feedbacks": {"fire": 10, "good": 4, "confused": 1},
  "comments_count": 7
}
```

**Критерий готовности:** Мастер видит аналитику по практике.

---

## PHASE 9: Полировка + розетки

### 9.1: AI-саммари розетка

**Цель:** Интерфейс для будущего AI-сервиса.

**Задачи:**
- [ ] app/modules/ai/interface.py — Protocol
- [ ] app/modules/ai/mock.py — Mock implementation
- [ ] GET /api/v1/practices/{id}/ai-summary (mock)

**Interface:**
```python
class AIService(Protocol):
    async def generate_summary(
        self,
        practice_id: UUID,
        checkins: list[Checkin],
        feedbacks: list[Feedback]
    ) -> str:
        ...
```

**Критерий готовности:** Розетка готова, mock возвращает placeholder.

---

### 9.2: Library розетка

**Цель:** TODO структура для записей.

**Задачи:**
- [ ] Модель Recording (закомментирована)
- [ ] TODO в коде
- [ ] Документация: что нужно для реализации

**Критерий готовности:** Структура задокументирована.

---

### 9.3: Финальное тестирование

**Цель:** Всё работает вместе.

**Задачи:**
- [ ] E2E тесты основных flow
- [ ] Load testing
- [ ] Security audit
- [ ] Документация API (OpenAPI)

**Основные flow для тестирования:**
1. Регистрация → вход → профиль
2. Создание практики мастером
3. Бронирование юзером
4. Оплата
5. Check-in → практика → feedback
6. Вывод средств мастером

**Критерий готовности:** Все flow работают, тесты проходят.

---

## 3. Приложения

### A. API Endpoints (полный список)

#### Auth
```
POST /api/v1/auth/telegram     # Вход через Telegram
POST /api/v1/auth/logout       # Выход
```

#### Users
```
GET  /api/v1/users/me          # Мой профиль
PATCH /api/v1/users/me         # Обновить профиль
```

#### Masters
```
POST /api/v1/masters/apply     # Подать заявку
GET  /api/v1/masters/me        # Мой профиль мастера
PATCH /api/v1/masters/me       # Обновить профиль
GET  /api/v1/masters/{id}      # Профиль мастера (публичный)
POST /api/v1/masters/me/withdraw         # Запросить вывод
POST /api/v1/masters/me/transfer-to-user # Перевод на User Balance
POST /api/v1/masters/me/promos           # Создать Master Promo
```

#### Practices
```
POST   /api/v1/practices           # Создать практику
GET    /api/v1/practices           # Список практик
GET    /api/v1/practices/{id}      # Детали практики
PATCH  /api/v1/practices/{id}      # Обновить практику
DELETE /api/v1/practices/{id}      # Удалить практику
GET    /api/v1/practices/{id}/insights  # Аналитика
```

#### Bookings
```
POST   /api/v1/bookings            # Создать бронь
GET    /api/v1/bookings            # Мои брони
DELETE /api/v1/bookings/{id}       # Отменить бронь
POST   /api/v1/bookings/{id}/join  # Отметить вход
POST   /api/v1/bookings/{id}/leave # Отметить выход
```

#### Waitlist
```
POST   /api/v1/practices/{id}/waitlist  # Встать в очередь
DELETE /api/v1/waitlist/{id}            # Выйти из очереди
```

#### Payments
```
POST /api/v1/payments/topup            # Пополнить баланс (Stripe)
GET  /api/v1/payments                  # История платежей
POST /api/v1/practices/{id}/purchase   # Купить практику
```

#### Masters (дополнительно)
```
POST /api/v1/masters/me/withdraw       # Запросить вывод (из available)
POST /api/v1/masters/me/transfer       # Перевести available → user balance
GET  /api/v1/masters/me/balance        # Получить frozen + available
POST /api/v1/masters/me/promos         # Создать Master Promo
GET  /api/v1/masters/me/promos         # Мои промокоды
```

#### Promos
```
POST /api/v1/promos/apply              # Применить промокод при покупке
GET  /api/v1/promos/{code}/validate    # Проверить валидность
```

#### Diary
```
POST /api/v1/practices/{id}/checkin   # Check-in
POST /api/v1/practices/{id}/feedback  # Feedback
GET  /api/v1/diary                    # Мой дневник
POST /api/v1/diary                    # Новая запись
GET  /api/v1/diary/{id}               # Запись
PATCH /api/v1/diary/{id}              # Редактировать
DELETE /api/v1/diary/{id}             # Удалить
```

#### Admin
```
GET  /api/v1/admin/stats              # Статистика
GET  /api/v1/admin/users              # Список юзеров
GET  /api/v1/admin/masters            # Список мастеров
GET  /api/v1/admin/masters/pending    # Ожидают верификации
POST /api/v1/admin/masters/{id}/verify   # Верифицировать
POST /api/v1/admin/masters/{id}/reject   # Отклонить
GET  /api/v1/admin/reports            # Жалобы
POST /api/v1/admin/reports/{id}/resolve  # Решить жалобу
GET  /api/v1/admin/payments/pending   # Выводы на подтверждение
POST /api/v1/admin/payments/{id}/confirm # Подтвердить вывод
POST /api/v1/admin/promos             # Создать Company Promo
GET  /api/v1/admin/promos             # Все промокоды
PATCH /api/v1/admin/promos/{id}       # Деактивировать промокод
```

#### Webhooks
```
POST /webhooks/stripe                 # Stripe webhook
```

### B. Переменные окружения

```bash
# App
APP_ENV=development
APP_DEBUG=true
APP_SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql+asyncpg://velo:password@postgres:5432/velo

# Redis
REDIS_URL=redis://redis:6379/0

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Payment Settings
PLATFORM_COMMISSION_PERCENT=15
MIN_WITHDRAWAL_AMOUNT=50
WITHDRAWAL_FEE=2
CANCELLATION_DEADLINE_HOURS=24

# Promo Settings
MASTER_PROMO_DISCOUNTS=5,25,50,75,100
```

---

## 10. Реестр технического долга

Замечания, выявленные при код-ревью. Сгруппированы по моменту, когда их следует закрывать.

### Обозначения

- **Среда:** 🧪 Тест (не влияет на тестовый сервер) / 🚀 Прод (обязательно до продакшена)
- **Статус:** ⬜ Open / ✅ Done

### Закрыто в Phase 0.5

| ID | Файл | Проблема | Решение | Статус |
|----|------|----------|---------|--------|
| TD-001 | `config.py` | `SECRET_KEY` с дефолтом | model_validator: обязателен при `APP_ENV!=development` | ✅ |
| TD-002 | `main.py` | `CORS *` + `allow_credentials=True` | `allow_credentials=not _allow_all` | ✅ |
| TD-003 | `main.py` | Health 200 при деградации | Добавлен `GET /ready` (503) | ✅ |
| TD-004 | `docker-compose.yml` | Postgres/Redis на `0.0.0.0` | Убраны published ports; app на `127.0.0.1` | ✅ |
| TD-005 | `Dockerfile` | Образ от `root` | `USER velo` (UID 1000) | ✅ |
| TD-006 | `config.py` | `database_url` с кредами в дефолте | model_validator: обязателен при `APP_ENV!=development` | ✅ |
| TD-007 | `main.py` | `VeloError` handler не зарегистрирован | `@app.exception_handler(VeloError)` + logging | ✅ |
| TD-008 | `database.py` | `get_db_session()` COMMIT на read-only | Добавлен `get_db_reader()` (rollback) | ✅ |
| TD-009 | `main.py` | Lifespan: init_redis() fail → engine leak | `try/finally` в lifespan | ✅ |

### Pre-6: Logging hardening — закрыть перед Phase 6

| ID | Среда | Файл | Проблема | Решение | Статус |
|----|-------|------|----------|---------|--------|
| TD-011 | 🧪🚀 | `logging.py` | structlog не фильтрует по log level — `LOG_LEVEL=WARNING` не работает | `make_filtering_bound_logger` с уровнем из config | ⬜ |
| TD-012 | 🧪🚀 | `logging.py` | `setup_logging()` не идемпотентна — `cache_logger_on_first_use` может закешировать дефолт | Guard-флаг или проверка на повторный вызов | ⬜ |

### Phase 1.4 — закрыть при старте Phase 1.4

| ID | Среда | Файл | Проблема | Решение | Статус |
|----|-------|------|----------|---------|--------|
| TD-019 | 🧪 | `test_auth.py` | `test_auth_telegram_success` требует запущенный PostgreSQL (R-3) | Документировать `make dev-up` в README, или добавить SQLite test fixture | ⬜ |
| TD-020 | 🧪 | `test_auth.py` | Нет тестов для logout, get_current_user, get_optional_user, get_current_admin (R-5) | Написать тесты | ⬜ |
| TD-021 | 🧪🚀 | `auth/service.py` | `_SESSION_TTL` вычисляется при импорте (P-9) — тесты не могут переопределить | Вычислять при вызове или читать из settings | ⬜ |

### Ближайшее касание соответствующего файла

| ID | Среда | Файл | Проблема | Решение | Статус |
|----|-------|------|----------|---------|--------|
| TD-013 | 🧪 | `migrations/env.py` | Engine не dispose-ится если `connect()` упадёт | try/finally вокруг async with | ⬜ |
| TD-014 | 🧪 | Несколько файлов | Версия `0.1.0` захардкожена в 3 местах (main.py, pyproject.toml, ?) | Вынести в одно место, читать из config или `__version__` | ⬜ |
| TD-015 | 🧪 | `config.py` | `postgres_password` дефолт `"velo"` без проверки в проде | Добавить validator (аналогично SECRET_KEY). Сейчас .env генерируется скриптом — риск минимален | ⬜ |

### Косметика — без дедлайна

| ID | Среда | Файл | Проблема | Решение | Статус |
|----|-------|------|----------|---------|--------|
| TD-010 | 🧪 | `.pre-commit-config.yaml` | `ruff-format` дублирует `black` | Убрать `black`, оставить `ruff-format` | ⬜ |
| TD-016 | 🧪 | Разные | Устаревшие комментарии (mypy в Makefile, ValidationError в exceptions.py, Phase 0.3 в conftest) | Обновить при касании файлов | ⬜ |
| TD-017 | 🧪 | `alembic.ini` | Placeholder URL в sqlalchemy.url | Убрать или заменить на комментарий (URL берётся из config) | ⬜ |
| TD-018 | 🧪 | `test_health.py` | Хрупкие патчи (mock engine.connect as async CM) | Рефакторить при добавлении новых тестов | ⬜ |
| TD-022 | 🧪 | `auth/schemas.py` | `balance_user` в AuthResponse — всегда 0 до Phase 6, шум (P-12) | Убрать из AuthResponse, вернуть в Phase 6 | ⬜ |
| TD-023 | 🧪 | `migrations/` | Downgrade не удаляет тип userrole (P-7, неактуально после перехода на String) | Проверить downgrade при следующей миграции | ⬜ |

### Осознанные решения (НЕ является долгом)

Следующие замечания были рассмотрены и признаны **не требующими исправления**:

- `warn_unused_ignores = false` в mypy — осознанный выбор из-за разницы type stubs между pip и pre-commit (Phase 0.3)
- Race condition на `_redis_client` — теоретически возможен, но `init_redis()` вызывается однократно в lifespan до приёма запросов
- `.env` в Docker image — уже исключён через `.dockerignore`

---

**Конец документа**
