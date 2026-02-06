# =============================================================================
# VELO Backend — Makefile
# =============================================================================
#
# WHAT IS A MAKEFILE?
#   A collection of shortcut commands. Instead of typing:
#     source .venv/bin/activate && python -m pytest tests/ -v --tb=short
#   You type:
#     make test
#
# HOW IT WORKS:
#   Each section below is a "target". `make <target>` runs the commands under it.
#   .PHONY means "this target is a command, not a file name".
#
# AVAILABLE COMMANDS:
#   make install    — Create venv, install deps, setup pre-commit hooks
#   make run        — Start the development server with hot reload
#   make test       — Run all tests
#   make lint       — Check code quality (black + ruff + mypy)
#   make format     — Auto-fix formatting and lint issues
#   make clean      — Remove caches and generated files
#   make dev-up     — Start PostgreSQL + Redis in Docker
#   make dev-down   — Stop Docker services
#   make dev-logs   — View Docker service logs
#   make dev-ps     — Show Docker service status
#   make dev-reset  — Destroy volumes and start fresh
# =============================================================================

# Use bash for shell commands (macOS default is zsh, but Makefiles expect bash syntax).
SHELL := /bin/bash

# Virtual environment path.
VENV := .venv

# Python inside the virtual environment.
# Why not just "python"? Because system python might be 3.9 while we need 3.12.
# Using the venv python guarantees the correct version and packages.
PYTHON := $(VENV)/bin/python

# pip inside the virtual environment.
PIP := $(VENV)/bin/pip

# Docker Compose file for local development (services only, no app).
COMPOSE_DEV := docker-compose.dev.yml

# Default target: what runs when you type just `make` with no arguments.
.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help message
	@echo "VELO Backend — Development Commands"
	@echo "===================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# SETUP
# =============================================================================

.PHONY: install
install: ## Create venv, install all dependencies, setup pre-commit
	@echo "📦 Creating virtual environment..."
	python3.12 -m venv $(VENV)
	@echo "⬆️  Upgrading pip..."
	$(PIP) install --upgrade pip
	@echo "📥 Installing project + dev dependencies..."
	$(PIP) install -e ".[dev]"
	@echo "🪝 Installing pre-commit hooks..."
	$(VENV)/bin/pre-commit install
	@echo ""
	@echo "✅ Setup complete! Activate venv with:"
	@echo "   source .venv/bin/activate"

# =============================================================================
# DOCKER SERVICES (PostgreSQL + Redis)
# =============================================================================
# These commands manage infrastructure services for local development.
# The app itself runs natively (not in Docker) for faster iteration.
#
# Architecture:
#   Docker Desktop → postgres:16 (port 5433) + redis:7 (port 6379)
#   Native Python  → uvicorn (port 8000) connects to Docker services

.PHONY: dev-up
dev-up: ## Start PostgreSQL + Redis in Docker
	@echo "🐳 Starting services..."
	docker compose -f $(COMPOSE_DEV) up -d
	@echo ""
	@echo "✅ Services running:"
	@echo "   PostgreSQL: localhost:5433"
	@echo "   Redis:      localhost:6379"
	@echo ""
	@echo "   Start the app with: make run"

.PHONY: dev-down
dev-down: ## Stop Docker services (data preserved)
	@echo "🛑 Stopping services..."
	docker compose -f $(COMPOSE_DEV) down
	@echo "✅ Services stopped. Data preserved in Docker volumes."

.PHONY: dev-logs
dev-logs: ## View Docker service logs (follow mode)
	docker compose -f $(COMPOSE_DEV) logs -f

.PHONY: dev-ps
dev-ps: ## Show Docker service status
	docker compose -f $(COMPOSE_DEV) ps

.PHONY: dev-reset
dev-reset: ## Destroy volumes and start fresh (DELETES ALL DATA)
	@echo "⚠️  This will DELETE all PostgreSQL and Redis data!"
	@read -p "Are you sure? (y/N) " confirm && \
		[ "$$confirm" = "y" ] || { echo "Cancelled."; exit 1; }
	docker compose -f $(COMPOSE_DEV) down -v
	@echo "✅ Volumes destroyed. Run 'make dev-up' to start fresh."

# =============================================================================
# DEVELOPMENT
# =============================================================================

.PHONY: run
run: ## Start development server with hot reload
	@# --reload: uvicorn watches for file changes and restarts automatically.
	@# --reload-dir app: only watch the app/ directory (ignore tests, migrations).
	@# This means: save a file → server restarts in ~0.5s → refresh browser.
	$(PYTHON) -m uvicorn app.main:app --reload --reload-dir app --host 0.0.0.0 --port 8000

# =============================================================================
# TESTING
# =============================================================================

.PHONY: test
test: ## Run all tests with verbose output
	@# -v: verbose (show each test name and result).
	@# --tb=short: on failure, show a short traceback (not the full stack).
	$(PYTHON) -m pytest tests/ -v --tb=short

# =============================================================================
# CODE QUALITY
# =============================================================================

.PHONY: lint
lint: ## Check code quality (black + ruff + mypy) — reports issues, doesn't fix
	@echo "🖤 Checking formatting (black)..."
	$(PYTHON) -m black --check .
	@echo "🔍 Linting (ruff)..."
	$(PYTHON) -m ruff check .
	@echo "✅ All checks passed!"

.PHONY: format
format: ## Auto-fix formatting and lint issues
	@echo "🖤 Formatting (black)..."
	$(PYTHON) -m black .
	@echo "🔧 Fixing lint issues (ruff)..."
	$(PYTHON) -m ruff check --fix .
	@echo "✅ Formatting complete!"

# =============================================================================
# CLEANUP
# =============================================================================

.PHONY: clean
clean: ## Remove caches and generated files
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Clean!"
