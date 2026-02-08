# VELO Backend

Platform for wellness practice facilitators — meditation, yoga, breathwork.

**Stack:** Python 3.12 · FastAPI · SQLAlchemy 2.0 (async) · PostgreSQL 16 · Redis 7

## Quick Start

### Prerequisites

- Python 3.12 (via [pyenv](https://github.com/pyenv/pyenv))
- Docker Desktop (for PostgreSQL + Redis)
- Git

### Setup

```bash
# 1. Clone and navigate to backend
cd velo/backend

# 2. Install everything (creates venv, installs deps, sets up pre-commit hooks)
make install

# 3. Create your .env file from the template
cp .env.example .env

# 4. Start PostgreSQL + Redis (Phase 0.2)
# make dev

# 5. Activate virtual environment
source .venv/bin/activate

# 6. Run the server
make run
```

Visit: http://localhost:8000/docs — Swagger UI with all endpoints.

## Testing

Tests run on the **test VPS** (`api.talentir.info`), not locally.

Integration tests (auth flow, CRUD) use the real PostgreSQL and Redis
running in Docker on the test server — no mocks, close to production.

```bash
# 1. Push your changes to GitHub
git push

# 2. SSH into test VPS and update
velo update        # pulls repo, rebuilds, runs migrations

# 3. Run tests inside the app container
docker compose exec app python -m pytest tests/ -v --tb=short
```

> **Why not locally?** Some tests (`test_auth_telegram_success`, profile CRUD)
> require a real PostgreSQL with asyncpg. The test VPS has all infrastructure
> running, so tests execute in a production-like environment. (TD-019)

## Development Commands

| Command        | Description                                      |
|----------------|--------------------------------------------------|
| `make install` | Create venv, install deps, setup pre-commit      |
| `make run`     | Start dev server with hot reload                 |
| `make test`    | Run all tests                                    |
| `make lint`    | Check code quality (black + ruff + mypy)         |
| `make format`  | Auto-fix formatting and lint issues              |
| `make clean`   | Remove caches and generated files                |

## Project Structure

```
backend/
├── app/
│   ├── main.py            # FastAPI application entry point
│   ├── core/
│   │   ├── config.py      # Settings from .env (pydantic-settings)
│   │   └── exceptions.py  # Base exception hierarchy
│   └── modules/           # Domain modules (auth, users, practices, etc.)
├── tests/
│   ├── conftest.py        # Shared test fixtures
│   └── test_root.py       # Root endpoint test
├── pyproject.toml         # Dependencies + tool configuration
├── Makefile               # Development commands
└── .pre-commit-config.yaml # Git hooks (black, ruff, mypy)
```

## Architecture

Modular monolith — each module in `app/modules/` is an isolated domain:

| Module         | Responsibility                          |
|----------------|-----------------------------------------|
| `auth`         | Telegram WebApp auth, sessions          |
| `users`        | Profiles, roles                         |
| `masters`      | Master profiles, verification           |
| `practices`    | CRUD, pricing                           |
| `bookings`     | Reservations, waitlist                  |
| `payments`     | Double-entry ledgers, Stripe            |
| `notifications`| Telegram bot, reminders                 |
| `diary`        | Check-ins, feedbacks, journal entries   |
| `admin`        | Verification, moderation                |

Each module follows: `models.py → schemas.py → service.py → router.py`