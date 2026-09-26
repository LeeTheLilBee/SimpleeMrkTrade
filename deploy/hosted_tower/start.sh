#!/usr/bin/env bash
set -euo pipefail

PORT_VALUE="${PORT:-10000}"
WORKERS_VALUE="${WEB_CONCURRENCY:-1}"
TIMEOUT_VALUE="${GUNICORN_TIMEOUT:-120}"
PYTHON_VALUE="${PYTHON_BIN:-python}"

# TWR198: Teller's one-time handoff store is local to a Python process.
# Until an explicitly tested shared atomic store is introduced, more than
# one Gunicorn worker can route issue and consume to different stores.
# Fail at startup instead of allowing intermittent handoff denial.
if [[ "${WORKERS_VALUE}" != "1" ]]; then
    printf '%s\n' "Tower hosted startup denied: WEB_CONCURRENCY must be 1 until a shared atomic handoff store is verified." >&2
    exit 64
fi

exec "${PYTHON_VALUE}" -m gunicorn \
    --bind "0.0.0.0:${PORT_VALUE}" \
    --workers "${WORKERS_VALUE}" \
    --timeout "${TIMEOUT_VALUE}" \
    --access-logfile - \
    --error-logfile - \
    web.hosted_tower:app
