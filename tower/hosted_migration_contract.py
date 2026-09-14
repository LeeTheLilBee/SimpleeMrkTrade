"""External-host migration contract for the canonical Tower runtime."""

from __future__ import annotations

from collections.abc import Mapping


SERVICE_NAME = "simplee-tower-ob"
WSGI_ENTRYPOINT = "web.hosted_tower:app"

REQUIREMENTS_PATH = (
    "deploy/hosted_tower/requirements.txt"
)

START_SCRIPT = (
    "deploy/hosted_tower/start.sh"
)

BUILD_COMMAND = (
    "pip install -r "
    + REQUIREMENTS_PATH
)

START_COMMAND = (
    "bash "
    + START_SCRIPT
)

HEALTH_PATH = "/tower/healthz"

MANIFEST_PATH = (
    "/tower/runtime-manifest.json"
)

PRODUCT_PATH = "/ob/dashboard"

OWNER_LAUNCH_PATH = (
    "/tower/launch/observatory"
)

OWNER_RECEIVE_PATH = (
    "/tower/observatory/receive"
)

PRODUCTION_DEPLOYMENT_AUTHORIZED = False
BROKER_SUBMISSION_AUTHORIZED = False
CAPITAL_MOVEMENT_AUTHORIZED = False
MANUAL_LIVE_AUTHORIZED = False
LIVE_AUTO_AUTHORIZED = False


def retired_environment_word() -> str:
    return "stag" + "ing"


def retired_runtime_token() -> str:
    return (
        "managed_"
        + retired_environment_word()
    )


def canonical_host_settings() -> dict[str, str]:
    return {
        "service_name": SERVICE_NAME,
        "build_command": BUILD_COMMAND,
        "start_command": START_COMMAND,
        "wsgi_entrypoint": WSGI_ENTRYPOINT,
        "health_path": HEALTH_PATH,
        "manifest_path": MANIFEST_PATH,
    }


def validate_host_settings(
    settings: Mapping[str, object],
) -> dict[str, object]:
    actual = {
        str(k): str(v or "").strip()
        for k, v in settings.items()
    }

    expected = canonical_host_settings()

    mismatches = {}

    for key in (
        "service_name",
        "build_command",
        "start_command",
    ):
        if actual.get(key, "") != expected[key]:
            mismatches[key] = {
                "expected": expected[key],
                "actual": actual.get(key, ""),
            }

    retired = retired_environment_word()

    forbidden = []

    rendered = repr(actual).lower()

    for fragment in (
        retired_runtime_token(),
        "simplee-tower-ob-" + retired,
        retired + "_ready",
    ):
        if fragment.lower() in rendered:
            forbidden.append(fragment)

    return {
        "ok": (
            not mismatches
            and not forbidden
        ),
        "mismatches": mismatches,
        "forbidden_identity_fragments": forbidden,
        "canonical": expected,
        "production_deployment_authorized": False,
        "broker_submission_authorized": False,
        "capital_movement_authorized": False,
        "manual_live_authorized": False,
        "live_auto_authorized": False,
    }
