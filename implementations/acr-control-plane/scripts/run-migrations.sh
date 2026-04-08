#!/usr/bin/env sh
# Apply all pending Alembic migrations and exit.
#
# Used by:
#   * the K8s gateway initContainer (deploy/k8s/base/gateway-deployment.yaml)
#   * the docker-compose `acr-migrate` one-shot service
#   * CI / local development
#
# Idempotent: re-running on an up-to-date schema is a no-op. Multiple
# replicas racing each other are safe — Alembic wraps each migration in a
# transaction, so the loser of the race observes the schema as already at
# head and exits 0.

set -eu

# Resolve the application root regardless of where the script is invoked
# from. The runtime image stores the app at /app, but local devs may run
# this from anywhere inside the repo.
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
APP_ROOT="$(CDPATH= cd -- "${SCRIPT_DIR}/.." && pwd)"

# /app inside the runtime image, repo path locally — both contain alembic.ini.
if [ -f "/app/alembic.ini" ]; then
    APP_ROOT="/app"
fi

cd "${APP_ROOT}"

if [ -z "${DATABASE_URL:-}" ]; then
    echo "[run-migrations] FATAL: DATABASE_URL is not set" >&2
    exit 2
fi

echo "[run-migrations] applying alembic upgrade head against ${DATABASE_URL%%@*}@<redacted>"
alembic -c "${APP_ROOT}/alembic.ini" upgrade head
echo "[run-migrations] migrations complete"
