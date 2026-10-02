#!/usr/bin/env bash
set -euo pipefail

PORT_VALUE="${PORT:-10000}"
WORKERS_VALUE="${WEB_CONCURRENCY:-1}"
TIMEOUT_VALUE="${GUNICORN_TIMEOUT:-120}"
PYTHON_VALUE="${PYTHON_BIN:-python}"

if [[ "${WORKERS_VALUE}" != "1" ]]; then
    printf '%s\n' "Tower hosted startup denied: WEB_CONCURRENCY must be 1 until a shared atomic handoff store is verified." >&2
    exit 64
fi

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

if [[ "${OB_KEYLESS_ONE_SHOT_SOURCE_PROBE:-0}" == "1" ]]; then
    "${PYTHON_VALUE}" -u -m deploy.hosted_tower.keyless_one_shot_source_probe &
fi

if [[ "${OB_CATALYST_ONE_SHOT_SOURCE_PROBE:-0}" == "1" ]]; then
    "${PYTHON_VALUE}" -u -m deploy.hosted_tower.official_catalyst_one_shot &
fi

# One internal Observatory event socket. This does not imply any upstream
# provider has a native WebSocket or streaming market-data entitlement.
if [[ "${OB_EVENT_WS_ASGI_ENABLED:-0}" == "1" ]]; then
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
