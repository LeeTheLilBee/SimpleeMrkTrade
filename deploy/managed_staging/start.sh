#!/usr/bin/env bash
set -euo pipefail

PORT_VALUE="${PORT:-10000}"
WORKERS_VALUE="${WEB_CONCURRENCY:-1}"
TIMEOUT_VALUE="${GUNICORN_TIMEOUT:-120}"
PYTHON_VALUE="${PYTHON_BIN:-python}"

exec "${PYTHON_VALUE}" -m gunicorn   --bind "0.0.0.0:${PORT_VALUE}"   --workers "${WORKERS_VALUE}"   --timeout "${TIMEOUT_VALUE}"   --access-logfile -   --error-logfile -   web.managed_staging:app
