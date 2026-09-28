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

# Explicit, primary-service-only owner beta observation. Never use a static
# self-certified JSON fixture. The separate observer polls the actual hosted
# HTTP endpoints and writes only short-lived, integrity-checked receipts.
# The feature is OFF by default and grants no trading/financial permission.
if [[ "${TOWER_OWNER_BETA_OB_PUBLICATION_ENABLED:-0}" == "1" ]]; then
    OBSERVED_PATH="/tmp/tower-owner-beta-ob-publication.json"
    if [[ -n "${TOWER_APP_PUBLICATION_STATE_PATH:-}" && "${TOWER_APP_PUBLICATION_STATE_PATH}" != "${OBSERVED_PATH}" ]]; then
        printf '%s\n' "Tower owner-beta observer denied: incompatible existing publication provider path." >&2
        exit 64
    fi
    export TOWER_APP_PUBLICATION_STATE_PATH="${OBSERVED_PATH}"
    rm -f -- "${OBSERVED_PATH}"
    "${PYTHON_VALUE}" -u deploy/hosted_tower/ob_publication_observer.py &
fi

exec "${PYTHON_VALUE}" -m gunicorn \
    --bind "0.0.0.0:${PORT_VALUE}" \
    --workers "${WORKERS_VALUE}" \
    --timeout "${TIMEOUT_VALUE}" \
    --access-logfile - \
    --error-logfile - \
    web.hosted_tower:app
