# VELO Backend

Platform for wellness practice facilitators — meditation, yoga, breathwork.

**Stack:** Python 3.12 · FastAPI · SQLAlchemy 2.0 (async) · PostgreSQL 16 · Redis 7

## Deployment (VPS only)

There is no local development. Code is written in Claude, pushed to GitHub,
and built on the VPS.

### Commands

```
velo update              — Pull, build, migrate, test, restart
velo test                — Run all tests
velo lint                — Run linters (ruff)
velo status              — Health check + Docker status
velo logs [app|db|redis] — View logs
velo restart [app]       — Restart services
velo db connect          — Open psql session
velo db migrate          — Run Alembic migrations
velo backup              — Backup DB + .env
```

### Manual Docker commands

```bash
# Build and start
docker compose up -d --build

# Run migrations
docker compose exec app python -m alembic upgrade head

# Run tests
docker compose exec app python -m pytest tests/ -v --tb=short

# Run linter
docker compose exec app python -m ruff check app/ tests/
```

## Architecture

Modular monolith — each module in `app/modules/` is an isolated domain:

```
backend/app/
├── core/           # DB, Redis, config, exceptions, logging
└── modules/
    ├── auth/       # Telegram WebApp auth, sessions
    ├── users/      # Profiles, roles
    ├── masters/    # Master profiles, verification
    ├── practices/  # CRUD, pricing
    ├── bookings/   # Reservations, waitlist
    ├── payments/   # Double-entry ledgers, Stripe
    └── ...
```

Each module: `models.py → schemas.py → service.py → router.py`
