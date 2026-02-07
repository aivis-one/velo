# =============================================================================
# VELO Backend — Dockerfile
# =============================================================================
#
# MULTI-STAGE BUILD:
#   Stage 1 ("builder"): installs dependencies into a virtual environment.
#   Stage 2 ("runtime"): copies only the venv + app code. No build tools.
#
# WHY MULTI-STAGE?
#   Build tools (gcc, pip, setuptools) add ~200MB to the image.
#   The final image only needs Python + our code + installed packages.
#   Result: ~150MB image instead of ~400MB.
#
# WHY python:3.12-slim (not alpine)?
#   Alpine uses musl libc instead of glibc. Some Python packages (asyncpg,
#   uvloop) need glibc and fail to compile on Alpine. slim = Debian minimal
#   with glibc — best balance of size and compatibility.
#
# SECURITY (TD-005):
#   Runtime stage runs as non-root user "velo" (UID 1000).
#   Even if the app is compromised, attacker has limited OS access.
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Builder — install dependencies
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /build

# Install only the files needed for dependency resolution.
# Docker caches each layer — if pyproject.toml doesn't change,
# dependencies won't be reinstalled on every build. Huge time savings.
COPY pyproject.toml ./

# Create a venv inside the builder and install production deps only.
# --no-cache-dir: don't store pip's download cache (smaller image).
# We don't install [dev] deps — no pytest/black/ruff in production.
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir .

# ---------------------------------------------------------------------------
# Stage 2: Runtime — minimal image with only what we need
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

WORKDIR /app

# Create non-root user for running the application. (TD-005)
# Using fixed UID/GID for consistency across rebuilds.
RUN groupadd --gid 1000 velo && \
    useradd --uid 1000 --gid velo --shell /bin/sh velo

# Copy the pre-built venv from the builder stage.
# This contains all our installed packages — no build tools needed.
COPY --from=builder /opt/venv /opt/venv

# Copy application code.
COPY app/ ./app/

# Copy Alembic files for database migrations.
# Needed for: docker compose exec app alembic upgrade head
COPY alembic.ini ./
COPY migrations/ ./migrations/

# Put venv's Python and scripts first in PATH.
# This means `python` and `uvicorn` resolve to the venv versions.
ENV PATH="/opt/venv/bin:$PATH"

# Prevent Python from writing .pyc files (unnecessary in containers).
# Force unbuffered output so logs appear immediately (not batched).
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to non-root user. (TD-005)
# Everything above runs as root (needed for apt/useradd).
# Everything below (and the CMD) runs as "velo".
USER velo

# Document which port the app listens on.
# This doesn't actually publish the port — that's done in docker-compose.
EXPOSE 8000

# Start the application.
# --host 0.0.0.0: listen on all interfaces (required inside Docker).
# --workers 2: run 2 worker processes (adjust based on VPS CPU cores).
# --proxy-headers: trust X-Forwarded-* headers from Nginx reverse proxy.
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2", \
     "--proxy-headers"]
