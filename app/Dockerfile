# syntax=docker/dockerfile:1.7
#
# Multi-stage build for the FastAPI DDD backend.
# - Builder:  resolves + installs dependencies into a virtualenv with uv.
# - Runtime:  slim image with only the venv + source, runs as non-root.
#
# ASGI entrypoint is configurable via APP_MODULE (default: src.main:app).

# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------
FROM python:3.13-slim AS builder

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# uv version pinned to match the lockfile (revision 3) generated locally.
COPY --from=ghcr.io/astral-sh/uv:0.9.17 /uv /uvx /bin/

WORKDIR /app

# Install dependencies first so this layer is cached independently of source.
# --frozen:             honour uv.lock exactly, no resolver, no network for solve.
# --no-install-project: deps only; the project source is never "installed" — it is
#                       imported in place as a namespace package (src.*), so no
#                       build backend is required.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:${PATH}" \
    APP_MODULE="src.main:app" \
    HOST="0.0.0.0" \
    PORT="8000" \
    RUN_MIGRATIONS="true"

WORKDIR /app

# Non-root user.
RUN groupadd --system --gid 1001 app \
 && useradd --system --uid 1001 --gid app --create-home --home-dir /home/app app \
 && chown -R app:app /app

# Virtualenv from the builder (absolute paths line up: /app/.venv in both stages).
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Application source + Alembic config. pyproject is copied for metadata only.
COPY --chown=app:app pyproject.toml alembic.ini ./
COPY --chown=app:app src ./src
COPY --chown=app:app migrations ./migrations
COPY --chown=app:app docker/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

USER app

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
