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
    "${PYTHON_VALUE}" -u -m deploy.hosted_tower.ob_publication_observer &
fi

# Owner-requested one-shot live no-key source proof. Explicitly opt-in,
# provider-reviewed, no raw values or login credentials in logs. Runs once per
# opted-in startup, independently of normal owner-only route authorization.
# Never blocks availability and is OFF during ordinary deployments.
if [[ "${OB_KEYLESS_ONE_SHOT_SOURCE_PROBE:-0}" == "1" ]]; then
    "${PYTHON_VALUE}" -u -m deploy.hosted_tower.keyless_one_shot_source_probe &
fi

# Owner-requested opt-in one-shot official research proof; status only and
# never an owner session, quote, model call or recurring background monitor.
if [[ "${OB_CATALYST_ONE_SHOT_SOURCE_PROBE:-0}" == "1" ]]; then
    "${PYTHON_VALUE}" -u -m deploy.hosted_tower.official_catalyst_one_shot &
fi

# Staged WebSocket transport. Same canonical Flask app through ASGI WSGI
# adapter; keep legacy WSGI default until integration/hosted acceptance passes.
# Never infer that a provider itself has a native streaming entitlement.
if [[ "${OB_CATALYST_WS_ASGI_ENABLED:-0}" == "1" ]]; then
    exec "${PYTHON_VALUE}" -m uvicorn web.hosted_tower_asgi:application \
        --host 0.0.0.0 \
        --port "${PORT_VALUE}" \
        --workers 1 \
        --ws-max-size 2048 \
        --ws-ping-interval 20 \
        --ws-ping-timeout 20 \
        --lifespan off \
        --no-access-log
fi

exec "${PYTHON_VALUE}" -m gunicorn \
    --bind "0.0.0.0:${PORT_VALUE}" \
    --workers "${WORKERS_VALUE}" \
    --timeout "${TIMEOUT_VALUE}" \
    --access-logfile - \
    --error-logfile - \
    web.hosted_tower:app
