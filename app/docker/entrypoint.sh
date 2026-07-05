#!/bin/sh
# Container entrypoint: optionally apply migrations, then launch the ASGI server.
# All tools (alembic, uvicorn) are on PATH via the virtualenv.
set -e

# Apply database migrations before serving traffic. Set RUN_MIGRATIONS=false
# to skip (e.g. when running migrations out-of-band in a separate job).
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    echo "[entrypoint] Applying database migrations..."
    alembic upgrade head
fi

echo "[entrypoint] Starting uvicorn: ${APP_MODULE}"
# shellcheck disable=SC2086  # intentional word-splitting of UVICORN_EXTRA
exec uvicorn "${APP_MODULE}" \
    --host "${HOST:-0.0.0.0}" \
    --port "${PORT:-8000}" \
    ${UVICORN_EXTRA:-}
