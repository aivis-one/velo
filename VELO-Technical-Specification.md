# VELO -- Техническое задание

**Версия:** 1.6
**Дата:** 11 февраля 2026
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
| Practices | Мастер может создать практику, юзер -- записаться |
| Payments | Пополнение баланса, оплата практики, вывод мастером |
| Notifications | Напоминания за 24ч, 1ч, 10мин |
| Admin | Верификация мастеров, базовая модерация |

### 1.3. Вне scope MVP

- OAuth (Google, Apple)
- Подписки (freemium есть, подписки -- нет)
- Library (записи практик)
- AI-саммари (только розетка)
- Мобильные приложения (только WebApp)

---

### Стилевое соглашение (введено Phase 2.3, Audit Round 6)

В комментариях и docstrings в коде:
- Вместо `→` используется `->` (ASCII)
- Вместо `—` (EN DASH) используется `--` (двойной дефис)
- ТЗ и документация вне кода могут использовать Unicode-символы

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
- [x] docker-compose.yml (postgres:16 + redis:7-alpine)
- [x] Порты: Postgres 5433 (не 5432), Redis 6379 (стандарт)
- [x] Volume для данных postgres (persistent)
- [x] Healthchecks для обоих сервисов

**Критерий готовности:** `docker compose up -d` поднимает pg + redis. ✅

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
│   ├── scripts/manage.sh  ← Management script (symlink: /usr/local/bin/velo)
│   └── backups/           ← Ежедневные бэкапы (pg_dump + .env)
├── /etc/nginx/sites-available/velo  ← Reverse proxy + SSL
└── /etc/letsencrypt/      ← SSL-сертификат для api.talentir.info
```

**Решения, принятые при реализации:**
- Ручной деплой (`velo update`) вместо GitHub Actions — промежуточные пуши для БЗ Claude, не всегда готовы к деплою
- Ubuntu 22.04 (не 24.04) — предустановлена хостером, LTS до 2027, обновление ОС не оправдано
- Deploy key (read-only SSH) вместо personal access token — минимальные права
- `install_velo.sh` генерирует `.env` с рандомными паролями (openssl rand) — без дефолтных кредов. Спрашивает TELEGRAM_BOT_TOKEN интерактивно
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
velo test                — Run all tests inside container
velo lint                — Run ruff linter inside container
velo update              — git pull + rebuild + migrate + test + restart
velo restart [app]       — Restart all or just app
velo backup              — pg_dump + .env → tar.gz
velo db connect          — psql в контейнер
velo db migrate          — python -m alembic upgrade head
velo ssl renew           — certbot renew
```

**Критерий готовности:** `curl https://api.talentir.info/health` → `{"status":"ok"}`. ✅

---

### 0.6: VPS-only infrastructure rewrite ✅

**Цель:** Убрать все артефакты локальной разработки. Единственная среда — VPS через Docker.

**Контекст:** Phases 0.1–0.5 создавались итеративно и оставили артефакты для macOS/локальной разработки (docker-compose.dev.yml, Makefile, .python-version, .pre-commit-config.yaml, black). Эта фаза — одноразовая чистка.

**Удалено:**
- `docker-compose.dev.yml` — локальная разработка не используется
- `Makefile` — все команды через `velo` на VPS
- `.python-version` — pyenv не нужен (Docker image содержит Python)
- `.pre-commit-config.yaml` — pre-commit не используется (ruff через `velo lint`)

**Заменено:**

| Файл | Что изменилось |
|------|----------------|
| `Dockerfile` | Dev-зависимости всегда устанавливаются (`pip install ".[dev]"`). tests/ и pyproject.toml копируются в runtime image. |
| `docker-compose.yml` | Единственный compose-файл. Postgres/Redis без published портов. App на `127.0.0.1:8000`. |
| `.dockerignore` | tests/ и pyproject.toml НЕ исключены (нужны в контейнере). |
| `.env.example` | Хосты: `postgres:5432`, `redis:6379` (Docker service names, не localhost). |
| `README.md` | Только VPS-инструкции. |

**install_velo.sh обновлён:**
- `docker compose down -v` при переустановке (удаляет volumes, чтобы новый пароль PG работал)
- `cd "$INSTALL_BASE"` перед `rm -rf` (фикс CWD-бага — shell терял рабочую директорию)
- `.env` всегда генерируется заново (убрана проверка `if exists`)
- `TELEGRAM_BOT_TOKEN` спрашивается интерактивно через `read -p`
- Убран `$INSTALL_BASE/creds/credentials.txt` (дубликат паролей из .env — бессмысленно и опасно)
- `velo update`: pull → build → down → up → `python -m alembic upgrade head` → `python -m pytest` → health check. Тесты упали — exit 1
- `velo test`, `velo lint` — новые команды
- `velo db migrate`: `python -m alembic` вместо `alembic` (PYTHONPATH)

**Результат:**
```
backend/
├── app/
│   ├── core/
│   │   ├── database.py        ← Lazy engine: get_engine() / dispose_engine()
│   │   ├── redis.py
│   │   ├── logging.py
│   │   ├── config.py
│   │   ├── mixins.py
│   │   └── exceptions.py
│   ├── modules/
│   │   ├── auth/
│   │   └── users/
│   └── main.py                ← Uses get_engine(), not module-level engine
├── tests/
│   ├── conftest.py            ← Session-scoped, pytest-asyncio 0.26 compatible
│   ├── test_auth.py
│   ├── test_health.py         ← Patches get_engine(), real DB for success tests
│   └── test_root.py
├── migrations/
├── docker-compose.yml         ← Single compose file (no dev/prod split)
├── Dockerfile                 ← Dev deps always installed, tests in image
├── .dockerignore
├── .env.example
├── pyproject.toml             ← No black/pre-commit, pytest cache_dir=/tmp
├── alembic.ini
└── README.md                  ← VPS-only instructions
```

**Решения, принятые при реализации:**
- pytest-asyncio 0.26: `asyncio_default_fixture_loop_scope = "session"` + `asyncio_default_test_loop_scope = "session"` — все тесты и fixtures на одном event loop. Кастомный `event_loop` fixture удалён (deprecated в 0.26)
- Миграции в conftest через subprocess — `env.py` использует `asyncio.run()`, который нельзя вложить в pytest event loop
- `cache_dir = "/tmp/.pytest_cache"` — контейнер работает от user `velo`, а `/app` принадлежит root
- Тесты запускаются в том же Docker image, что и приложение — нет разницы между test и prod окружением

**Критерий готовности:** `velo test` → 18 passed, 0 warnings. `velo update` включает тесты. ✅

---

### 0.7: Logging + Audit → перенесена перед Phase 6

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

### 1.4: CRUD профиля юзера ✅

**Цель:** Endpoints для профиля.

**Задачи:**
- [x] app/modules/users/schemas.py — UserResponse (перенесён из auth/schemas.py), UserUpdate
- [x] app/modules/users/service.py — update_user (partial update через merge + exclude_unset)
- [x] app/modules/users/router.py — GET/PATCH /api/v1/users/me
- [x] auth/schemas.py — импортирует UserResponse из users/schemas.py (без дупликации)
- [x] main.py — include_router(users_router)
- [x] tests/helpers.py — общие хелперы (build_init_data, login_user, auth_headers)
- [x] tests/test_users.py — 10 тестов
- [x] tests/test_auth.py — рефакторинг на shared helpers

**Endpoints:**
```
GET  /api/v1/users/me        → UserResponse
PATCH /api/v1/users/me       → UserResponse (body: UserUpdate)
```

**Результат:**
```
backend/app/modules/users/
├── __init__.py
├── models.py           ← (из Phase 1.1)
├── schemas.py          ← UserResponse + UserUpdate
├── service.py          ← update_user()
└── router.py           ← GET/PATCH /users/me

backend/tests/
├── helpers.py          ← Shared: build_init_data, login_user, auth_headers
├── test_auth.py        ← Рефакторинг: импорты из helpers
└── test_users.py       ← 10 тестов (GET, PATCH, auth, validation)
```

**Решения, принятые при реализации:**
- `UserResponse` перенесён в users/schemas.py (домен users), auth/schemas.py импортирует оттуда — при распиле на микросервисы оба варианта эквивалентны (всё равно дупликация или shared-lib)
- `session.merge(user)` в service — user приходит из read-only сессии (get_db_reader), PATCH пишет через get_db_session. Merge переносит объект в write-сессию
- `exclude_unset=True` — различаем "поле не отправлено" и "поле отправлено как null". Пустой body `{}` = ничего не меняем, 200
- `min_length=1` на всех полях UserUpdate — пустые строки отклоняются (422). Очистка поля — через null
- `avatar_url` не входит в UserUpdate — управляется Telegram (будущее: Bot API getUserProfilePhotos)
- Тестовые хелперы вынесены в tests/helpers.py (не conftest — это функции, не fixtures). Устранена дупликация между test_auth.py и test_users.py
- telegram_id ranges: auth тесты 77xxx/99xxx, users тесты 88xxx — без конфликтов
- Closes TD-021

**Критерий готовности:** Юзер может видеть и редактировать свой профиль. 31 тест, 0 warnings. ✅

---

## PHASE 2: Masters

### 2.1: MasterProfile + JSONB data ✅

**Цель:** Модель профиля мастера.

**Задачи:**
- [x] app/modules/masters/models.py
- [x] MasterProfile с JSONB data
- [x] Поля frozen_amount и available_amount
- [x] Миграция

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

**Решения, принятые при реализации:**
- Relationship: unidirectional (`MasterProfile → User`, без `back_populates` на User) — избегает циклических импортов при старте app
- Миграция написана вручную (нет локальной БД для autogenerate)
- `MasterProfile` наследует `JSONBMixin` — см. архитектурное правило ниже

**Критерий готовности:** Миграция применена. ✅

---

### Архитектурное правило: JSONBMixin (введено Phase 2.1)

**Контекст:** SQLAlchemy не детектит изменения JSONB-колонок при прямом
присвоении dict (shallow copy сохраняет ссылки на вложенные объекты,
SQLAlchemy сравнивает identity и считает значение неизменённым).
Это приводит к silent bugs — данные не сохраняются в БД.

**Правило:**
```python
# ❌ ЗАПРЕЩЕНО — SQLAlchemy может не увидеть изменение:
profile.data = new_data
profile.data["account"]["status"] = "verified"

# ✅ ОБЯЗАТЕЛЬНО — гарантирует UPDATE:
profile.set_jsonb("data", new_data)
```

**Реализация:** `JSONBMixin` в `app/core/mixins.py`:
```python
from sqlalchemy.orm.attributes import flag_modified

class JSONBMixin:
    def set_jsonb(self, field: str, value: dict) -> None:
        setattr(self, field, value)
        flag_modified(self, field)
```

**Где применяется:**
- `MasterProfile(JSONBMixin, Base)` — колонка `data`
- `User` — колонка `credentials` (пока мутируется только через raw SQL INSERT ON CONFLICT; JSONBMixin добавить при первой ORM-мутации)
- Все будущие модели с JSONB-колонками обязаны наследовать `JSONBMixin`

**TD-024:** Добавить `JSONBMixin` к `User` при первой ORM-мутации `credentials`.

---

### Архитектурное правило: Session Commit (введено Phase 2.2)

**Контекст:** `get_db_session()` автоматически делает `commit()` после `yield`
и `rollback()` при исключении. Явный `commit()` в роутере создаёт двойной
коммит, что может привести к `InvalidRequestError` или частичному коммиту.

**Правило:**
```python
# ❌ ЗАПРЕЩЕНО — двойной коммит:
await session.commit()

# ✅ ОБЯЗАТЕЛЬНО — flush для DB-generated значений:
await session.flush()
await session.refresh(obj)
```

**Сессии в VELO:**
- `get_db_session()` — write: auto-commit после yield, rollback при ошибке
- `get_db_reader()` — read-only: всегда rollback (TD-008)
- В роутерах **никогда** не вызывать `session.commit()` и `session.rollback()`
- В service-слое допустим `session.rollback()` только внутри `try/except IntegrityError`

---

### 2.2: Заявка на мастера ✅

**Цель:** Flow подачи заявки (3 шага из мокапов).

**Задачи:**
- [x] POST /api/v1/masters/apply — создание заявки
- [x] Шаг 1: Профиль (имя, email, телефон)
- [x] Шаг 2: Опыт (направления, сертификаты)
- [x] Шаг 3: Документы (загрузка)
- [x] Статус "pending"
- [x] Повторная заявка после rejection (с сохранением истории)
- [x] Race condition guard (IntegrityError + rollback)
- [x] tests/test_masters.py — 8 тестов

**Endpoint:**
```
POST /api/v1/masters/apply
Body: {
  "profile": {...},
  "experience": {...},
  "documents": [...]
}
Response: {"user_id": "...", "status": "pending", "created_at": "..."}
```

**Критерий готовности:** Юзер может подать заявку на мастера. ✅

---

### 2.3: Верификация мастера ✅

**Цель:** Админ может верифицировать или отклонить заявку мастера.

**Задачи:**
- [x] POST /api/v1/admin/masters/{user_id}/verify
- [x] POST /api/v1/admin/masters/{user_id}/reject
- [x] Изменение user.role на MASTER при верификации
- [x] app/modules/admin/ — ВРЕМЕННЫЙ модуль (см. примечание ниже)
- [x] tests/test_admin_masters.py — 10 тестов

**Endpoints:**
```
POST /api/v1/admin/masters/{user_id}/verify
Body: {"notes": "Всё ок"}      (notes — опционально)
Response: {"user_id": "...", "status": "verified"}

POST /api/v1/admin/masters/{user_id}/reject
Body: {"reason": "Недостаточно опыта"}     (reason — обязательно, min_length=1)
Response: {"user_id": "...", "status": "rejected"}
```

**Результат:**
```
backend/app/modules/admin/       ← ⚠️ ВРЕМЕННЫЙ модуль
├── __init__.py
├── schemas.py          ← VerifyMasterRequest, RejectMasterRequest, AdminMasterActionResponse
├── service.py          ← verify_master(), reject_master(), _load_pending_profile()
└── router.py           ← 2 POST-эндпоинта, get_current_admin

backend/tests/
└── test_admin_masters.py  ← 10 тестов (telegram_id range: 56xxx)
```

**Решения, принятые при реализации:**
- **Временный admin-модуль:** содержит только verify/reject. Phase 3 ДОЛЖНА переработать его в полноценный admin-модуль (stats, user lists, moderation). Не добавлять сюда новый код без плана Phase 3
- `_load_pending_profile()` использует `SELECT ... FOR UPDATE` (P-07) — защита от race condition при двух админах одновременно
- Все JSONB-мутации через `copy.deepcopy()` + `set_jsonb()` (P-03)
- Никакого `session.commit()` в роутере (P-01) — только `flush()` + `refresh()`
- Сообщение ConflictError: `"Application is not pending"` без интерполяции текущего статуса (P-08)
- Verify выполняет ДВЕ операции: `profile.set_jsonb(...)` + `user.role = UserRole.MASTER`
- Reject НЕ меняет роль — пользователь остаётся USER и может reapply
- Verification info записывается в `data.account.verification` (verified_at, verified_by, notes)
- Rejection info записывается в `data.account` (rejected_at, rejection_reason, rejected_by)
- `get_current_admin` dependency на обоих эндпоинтах
- structlog (P-10) для логирования всех действий
- CORS fix: `settings.cors_origins.split(",")` — исправлен наследственный баг (str vs list)
- telegram_id ranges: 56001-56099 (аппликанты), 56900-56999 (админы)

**Аудит:**
- Round 5: найдены 4 проблемы (race condition MEDIUM, CORS LOW, status leak LOW, lint). Все исправлены
- Round 6: чистый проход, только косметика (ASCII стиль в комментариях)
- Предсказанные ошибки из LLM Code Review Guide (P-01, P-03, P-10, forgotten role change) — все избежаны

**Критерий готовности:** Админ может верифицировать/отклонить заявку. 49 тестов, 0 warnings. ✅

---

---

## PHASE 3: Admin

### 3.1: Админские эндпоинты + реструктуризация admin-модуля ✅

**Цель:** Базовые админ-функции + переработка временного admin-модуля из Phase 2.3.

**Задачи:**
- [x] Переработать app/modules/admin/ из плоской структуры в sub-packages
- [x] Перенести verify/reject в admin/masters/ (без изменений логики)
- [x] GET /api/v1/admin/stats — базовая статистика
- [x] tests/test_admin_stats.py — 6 тестов

**Endpoint:**
```
GET /api/v1/admin/stats
Response: {
  "users_count": 150,
  "masters_count": 12,
  "practices_count": 0,
  "pending_verifications": 2
}
```

> **⚠️ STUB:** `practices_count` всегда 0. Заменить реальным COUNT в Phase 4.1
> после создания модели Practice.

**Результат:**
```
backend/app/modules/admin/
├── __init__.py              ← модуль (убран TEMPORARY)
├── router.py                ← агрегатор: include masters + stats sub-routers
├── masters/
│   ├── __init__.py
│   ├── schemas.py           ← перенос из Phase 2.3
│   ├── service.py           ← перенос из Phase 2.3 (FOR UPDATE)
│   └── router.py            ← POST verify/reject (prefix=/masters)
└── stats/
    ├── __init__.py
    ├── schemas.py           ← AdminStatsResponse
    ├── service.py           ← get_stats(): 3 real COUNTs + 1 stub
    └── router.py            ← GET /stats (get_db_reader)

backend/tests/
└── test_admin_stats.py      ← 6 тестов (telegram_id range: 57xxx)
```

**Решения, принятые при реализации:**
- Sub-packages вместо плоской структуры — готовность к Phase 3.2 (users/), 3.3 (reports/) без раздувания файлов
- `admin/router.py` — агрегатор, include sub-routers. Импорт в main.py не меняется: `from app.modules.admin.router import router`
- Stats использует `get_db_reader` (read-only) — не write session
- JSONB filter: `MasterProfile.data["account"]["status"].as_string() == "pending"` — sequential scan на master_profiles (таблица маленькая, GIN-индекс не нужен для MVP)
- `practices_count: 0` — осознанная заглушка, не фича. Удалить и заменить реальным запросом в Phase 4.1
- telegram_id ranges: stats тесты 57xxx (не пересекаются с 55xxx masters, 56xxx admin_masters)

**Аудит:** 2 замечания (LOW docstring, LINT formatting). Исправлены.

**Критерий готовности:** Админ видит статистику. 55 тестов, 0 warnings. ✅

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

> **Примечание (P-09):** При реализации использовать `enum.StrEnum` вместо `(str, Enum)`.
> ТЗ написано в старом стиле — это legacy, не копировать буквально.

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
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ATTENDED = "attended"
    NO_SHOW = "no_show"
    CANCELLED = "cancelled"

class Booking(Base):
    __tablename__ = "bookings"
    
    id: Mapped[UUID]
    practice_id: Mapped[UUID] = mapped_column(ForeignKey("practices.id"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    
    status: Mapped[BookingStatus] = mapped_column(default=BookingStatus.PENDING)
    
    purchase_id: Mapped[UUID | None] = mapped_column(ForeignKey("purchases.id"))
    
    booked_at: Mapped[datetime] = mapped_column(server_default=func.now())
    cancelled_at: Mapped[datetime | None]
    cancellation_reason: Mapped[str | None]
    
    joined_at: Mapped[datetime | None]
    left_at: Mapped[datetime | None]
    
    __table_args__ = (
        UniqueConstraint("practice_id", "user_id", name="uq_booking_practice_user"),
    )
```

> **Примечание (P-09):** При реализации использовать `enum.StrEnum`.

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
    actor_id: Mapped[UUID | None]
    actor_type: Mapped[str] = mapped_column(String(20))
    
    target_type: Mapped[str] = mapped_column(String(50))
    target_id: Mapped[UUID]
    
    data: Mapped[dict] = mapped_column(JSONB)
    
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(500))
    trace_id: Mapped[str | None] = mapped_column(String(36))
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
    reason: Mapped[str]
    notes: Mapped[str | None]
    created_at: Mapped[datetime]

class MasterLedger(Base):
    __tablename__ = "master_ledger"
    
    id: Mapped[UUID]
    user_id: Mapped[UUID]
    amount: Mapped[Decimal] = mapped_column(DECIMAL(18, 2))
    is_frozen: Mapped[bool] = mapped_column(default=True)
    status: Mapped[LedgerStatus] = mapped_column(default=LedgerStatus.DONE)
    reason: Mapped[str]
    practice_id: Mapped[UUID | None]
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

> **Примечание (P-09):** При реализации использовать `enum.StrEnum`.

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

**Критерий готовности:** Отмены работают по правилам.

---

### 6.6: Withdrawals

**Цель:** Вывод средств мастером.

**Задачи:**
- [ ] POST /api/v1/masters/me/withdraw — запрос на вывод
- [ ] POST /api/v1/admin/withdrawals/{id}/confirm — подтверждение админом
- [ ] Проверка MIN_WITHDRAWAL_AMOUNT
- [ ] Комиссия WITHDRAWAL_FEE

**Критерий готовности:** Мастер может запросить вывод, админ подтверждает.

---

### 6.7: Promos

**Цель:** Промокоды.

**Задачи:**
- [ ] Модель Promo
- [ ] POST /api/v1/purchases/{id}/apply-promo
- [ ] Два типа: Company Promo, Master Promo
- [ ] Валидация лимитов

**Критерий готовности:** Промокоды работают при покупке.

---

### 6.8: Data Consistency Semaphores

**Цель:** Автоматические проверки консистентности данных.

**Задачи:**
- [ ] GET /api/v1/admin/consistency — запуск всех семафоров
- [ ] Проверки: COUNT=COUNT, SUM=0, Computed=Actual, Orphans, Invariants
- [ ] Алерты при расхождении

**Полная документация:** `VELO-Data-Consistency-Semaphores.md`

**Критерий готовности:** Семафоры запускаются и показывают OK/ALERT.

---

## PHASE 7: Notifications

### 7.1: Модель Notification

**Цель:** Хранение уведомлений.

**Задачи:**
- [ ] app/modules/notifications/models.py
- [ ] Notification + NotificationDelivery
- [ ] Миграция

**Модель:**
```python
class Notification(Base):
    __tablename__ = "notifications"
    
    id: Mapped[int]  # НЕ UUID — автоинкремент
    user_id: Mapped[UUID]
    type: Mapped[str]  # reminder, booking_confirmed, etc.
    title: Mapped[str]
    body: Mapped[str]
    data: Mapped[dict] = mapped_column(JSONB)
    
    scheduled_at: Mapped[datetime]
    status: Mapped[str]  # pending, sent, failed
    
    created_at: Mapped[datetime]
```

**Критерий готовности:** Миграция применена.

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

## 3. Реестр технического долга

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

### Закрыто в Phase 0.6

| ID | Файл | Проблема | Решение | Статус |
|----|------|----------|---------|--------|
| TD-010 | `.pre-commit-config.yaml` | `ruff-format` дублирует `black` | Оба удалены: нет pre-commit, нет black. Ruff через `velo lint` | ✅ |
| TD-016 | Разные | Устаревшие комментарии (mypy в Makefile и т.д.) | Makefile удалён целиком. .python-version удалён | ✅ |
| TD-018 | `test_health.py` | Хрупкие патчи (mock engine.connect as async CM) | Патчит `get_engine()`, success-тесты на реальной БД | ✅ |
| TD-019 | `test_auth.py` | Требует запущенный PostgreSQL | Тесты запускаются внутри Docker — БД всегда доступна | ✅ |
| TD-020 | `test_auth.py` | Нет тестов для logout | Добавлены test_logout_success, test_logout_no_token, test_logout_invalid_token, test_logout_inactive_user | ✅ |

### Закрыто в Phase 1.4

| ID | Файл | Проблема | Решение | Статус |
|----|------|----------|---------|--------|
| TD-021 | `auth/service.py` | `_SESSION_TTL` вычисляется при импорте — тесты не могут переопределить | `_get_session_ttl()` вычисляет при каждом вызове | ✅ |

### Закрыто в Phase 2.3

| ID | Файл | Проблема | Решение | Статус |
|----|------|----------|---------|--------|
| TD-031 | `main.py` | CORS: `settings.cors_origins == ["*"]` сравнивает str с list | `_cors_origins = [o.strip() for o in settings.cors_origins.split(",")]` | ✅ |

### Pre-6: Logging hardening — закрыть перед Phase 6

| ID | Среда | Файл | Проблема | Решение | Статус |
|----|-------|------|----------|---------|--------|
| TD-011 | 🧪🚀 | `logging.py` | structlog не фильтрует по log level — `LOG_LEVEL=WARNING` не работает | `make_filtering_bound_logger` с уровнем из config | ⬜ |
| TD-012 | 🧪🚀 | `logging.py` | `setup_logging()` не идемпотентна — `cache_logger_on_first_use` может закешировать дефолт | Guard-флаг или проверка на повторный вызов | ⬜ |

### Косметика — без дедлайна

| ID | Среда | Файл | Проблема | Решение | Статус |
|----|-------|------|----------|---------|--------|
| TD-013 | 🧪 | `migrations/env.py` | Engine не dispose-ится если `connect()` упадёт | try/finally вокруг async with | ⬜ |
| TD-014 | 🧪 | Несколько файлов | Версия `0.1.0` захардкожена в 3 местах (main.py, pyproject.toml, ?) | Вынести в одно место, читать из config или `__version__` | ⬜ |
| TD-015 | 🧪 | `config.py` | `postgres_password` дефолт `"velo"` без проверки в проде | Добавить validator (аналогично SECRET_KEY). Сейчас .env генерируется скриптом — риск минимален | ⬜ |
| TD-017 | 🧪 | `alembic.ini` | Placeholder URL в sqlalchemy.url | Убрать или заменить на комментарий (URL берётся из config) | ⬜ |
| TD-022 | 🧪 | `auth/schemas.py` | `balance_user` в AuthResponse — всегда 0 до Phase 6, шум | Убрать из AuthResponse, вернуть в Phase 6 | ⬜ |
| TD-023 | 🧪 | `migrations/` | Downgrade не удаляет тип userrole (неактуально после перехода на String) | Проверить downgrade при следующей миграции | ⬜ |
| TD-024 | 🧪 | `users/models.py` | `User` не наследует `JSONBMixin` для `credentials` | Добавить при первой ORM-мутации `credentials` | ⬜ |

### Phase 2.2 аудит — backlog

| ID | Среда | Файл | Проблема | Решение | Статус |
|----|-------|------|----------|---------|--------|
| TD-025 | 🚀 | Все роутеры | Нет rate limiting на auth и masters endpoints | `slowapi` middleware или custom limiter (Redis-based) | ⬜ |
| TD-026 | 🚀 | `docker-compose.yml` | Redis без пароля — доступ без аутентификации | `requirepass` в Redis + `REDIS_PASSWORD` в .env + config.py | ⬜ |
| TD-027 | 🚀 | `main.py` / `config.py` | CORS `"*"` по умолчанию — в production нужен явный список origins | При деплое фронта заменить на конкретные домены | ⬜ |
| TD-028 | 🧪 | `masters/schemas.py` | `documents: list[dict]` — содержимое dict'ов не ограничено | Типизировать при реализации S3/file upload | ⬜ |
| TD-029 | 🧪 | `users/router.py` | 2 DB-сессии на `PATCH /users/me` (reader + writer) | Одна write-сессия или передача user_id вместо объекта | ⬜ |
| TD-030 | 🧪 | `main.py` | Health checks не различают timeout vs connection error | Разные статусы/сообщения для timeout и connection refused | ⬜ |

### Осознанные решения (НЕ является долгом)

Следующие замечания были рассмотрены и признаны **не требующими исправления**:

- Race condition на `_redis_client` — теоретически возможен, но `init_redis()` вызывается однократно в lifespan до приёма запросов
- `.env` в Docker image — уже исключён через `.dockerignore`
- Dev-зависимости в production image — осознанный выбор: тесты запускаются в том же контейнере через `velo test`. Образ чуть больше, но единая среда (Phase 0.6)

---

**Конец документа**
