from __future__ import annotations

from typing import Any, Mapping


PACKAGE = "GP056"

TITLE = (
    "Private Beta Access Authorization"
)


REQUIRED_TRUE = (
    "staging_ready",
    "tower_staging_accepted",
    "beta_launch_preparation_closeout_ready",
    "production_deploy_disabled",
    "broker_submission_locked",
    "real_capital_movement_locked",
    "direct_execution_disabled",
    "automated_execution_disabled",
    "permission_mutations_disabled",
    "secret_reveal_disabled",
    "live_auto_locked",
)


REQUIRED_FALSE = (
    "private_beta_access_opened",
    "tester_credentials_issued",
)


def authorize_private_beta_access(
    state: Mapping[str, Any],
) -> dict[str, Any]:

    failures: list[str] = []

    for key in REQUIRED_TRUE:
        if state.get(key) is not True:
            failures.append(
                f"{key}_required_true"
            )

    for key in REQUIRED_FALSE:
        if state.get(key) is not False:
            failures.append(
                f"{key}_required_false"
            )

    ready = not failures

    return {
        "package": PACKAGE,
        "title": TITLE,
        "gate_state": (
            "private_beta_access_authorization_sealed"
            if ready
            else
            "private_beta_access_authorization_hold"
        ),
        "access_authorization_ready": ready,
        "private_beta_access_opened": False,
        "tester_credentials_issued": False,
        "tester_session_created": False,
        "permission_mutation_performed": False,
        "allowed_beta_modes": [
            "Survey",
            "Paper",
        ],
        "manual_live_policy": "OWNER_ONLY",
        "live_auto_policy": "LOCKED",
        "production_deploy": "DISABLED",
        "broker_submission": "LOCKED",
        "real_capital_movement": "LOCKED",
        "direct_execution": "DISABLED",
        "automated_execution": "DISABLED",
        "permission_mutation": "DISABLED",
        "secret_reveal": "DISABLED",
        "failures": failures,
        "recommendation": (
            "GO_FOR_PRIVATE_BETA_TESTER_ELIGIBILITY_REVIEW"
            if ready
            else
            "NO_GO_HOLD_PRIVATE_BETA_ACCESS_AUTHORIZATION"
        ),
    }
