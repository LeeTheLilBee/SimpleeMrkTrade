from __future__ import annotations

from typing import Any, Mapping


PACKAGE = "GP059"

TITLE = (
    "Private Beta Access Activation Gate"
)


REQUIRED_RUNTIME_TRUE = (
    "tower_authenticated_session_required",
    "tower_authorization_required",
    "revocation_ready",
    "access_receipt_logging_ready",
    "production_deploy_disabled",
    "broker_submission_locked",
    "real_capital_movement_locked",
    "direct_execution_disabled",
    "automated_execution_disabled",
    "permission_mutations_disabled",
    "secret_reveal_disabled",
    "live_auto_locked",
)


def evaluate_private_beta_access_activation_gate(
    grant_package: Mapping[str, Any],
    runtime: Mapping[str, Any],
) -> dict[str, Any]:

    failures: list[str] = []

    if (
        grant_package.get(
            "grant_prepared"
        )
        is not True
    ):
        failures.append(
            "gp058_grant_preparation_required"
        )

    grant = (
        grant_package.get("grant")
        or {}
    )

    required_false = (
        "owner_console_access",
        "manual_live_access",
        "live_auto_access",
        "broker_submission_access",
        "real_capital_access",
        "permission_admin_access",
        "secret_access",
    )

    for key in required_false:
        if grant.get(key) is not False:
            failures.append(
                f"{key}_must_be_false"
            )

    allowed_modes = grant.get(
        "allowed_modes"
    )

    if allowed_modes != [
        "Survey",
        "Paper",
    ]:
        failures.append(
            "allowed_modes_must_be_survey_and_paper"
        )

    for key in REQUIRED_RUNTIME_TRUE:
        if runtime.get(key) is not True:
            failures.append(
                f"{key}_required_true"
            )

    authorizable = not failures

    return {
        "package": PACKAGE,
        "title": TITLE,
        "gate_state": (
            "private_beta_access_activation_gate_sealed"
            if authorizable
            else
            "private_beta_access_activation_gate_hold"
        ),
        "activation_authorizable": authorizable,
        "access_activation_performed": False,
        "private_beta_access_opened": False,
        "tester_credentials_issued": False,
        "tester_session_created": False,
        "permission_mutation_performed": False,
        "manual_live_policy": "OWNER_ONLY",
        "live_auto_policy": "LOCKED",
        "production_deploy": "DISABLED",
        "broker_submission": "LOCKED",
        "real_capital_movement": "LOCKED",
        "failures": failures,
        "recommendation": (
            "GO_FOR_PRIVATE_BETA_ACCESS_AUTHORIZATION_CLOSEOUT"
            if authorizable
            else
            "NO_GO_HOLD_PRIVATE_BETA_ACCESS_ACTIVATION_GATE"
        ),
    }
