from __future__ import annotations

from typing import Any, Mapping


PACKAGE = "GP063"

TITLE = (
    "Private Beta Tester Session Activation Gate"
)


REQUIRED_RUNTIME_TRUE = (
    "tower_identity_gate_ready",
    "tower_authentication_required",
    "mfa_required",
    "session_expiration_required",
    "session_revocation_ready",
    "access_receipt_required",
    "anonymous_default_deny",
    "non_owner_owner_console_deny",
    "manual_live_owner_only",
    "live_auto_locked",
    "broker_submission_locked",
    "real_capital_movement_locked",
    "direct_execution_disabled",
    "automated_execution_disabled",
    "production_deploy_disabled",
)


def evaluate_private_beta_tester_session_activation_gate(
    credential_boundary: Mapping[str, Any],
    runtime: Mapping[str, Any],
) -> dict[str, Any]:

    failures: list[str] = []

    if (
        credential_boundary.get(
            "credential_boundary_ready"
        )
        is not True
    ):
        failures.append(
            "gp062_credential_boundary_required"
        )

    if (
        credential_boundary.get(
            "credential_material_created"
        )
        is not False
    ):
        failures.append(
            "credential_material_must_remain_uncreated"
        )

    if (
        credential_boundary.get(
            "external_beta_access_opened"
        )
        is not False
    ):
        failures.append(
            "external_beta_access_must_remain_closed"
        )

    for key in REQUIRED_RUNTIME_TRUE:
        if (
            runtime.get(key)
            is not True
        ):
            failures.append(
                f"{key}_required_true"
            )

    ready = not failures

    return {
        "package": PACKAGE,
        "title": TITLE,
        "gate_state": (
            "private_beta_tester_session_activation_gate_sealed"
            if ready
            else
            "private_beta_tester_session_activation_gate_hold"
        ),
        "session_activation_gate_ready": ready,
        "session_activation_authorizable_after_real_credential_setup": ready,
        "tester_session_created": False,
        "tester_session_activated": False,
        "credential_material_created": False,
        "external_beta_access_opened": False,
        "anonymous_access_allowed": False,
        "owner_console_access_allowed": False,
        "manual_live_allowed": False,
        "live_auto_allowed": False,
        "broker_submission_allowed": False,
        "real_capital_allowed": False,
        "failures": failures,
        "recommendation": (
            "GO_FOR_PRIVATE_BETA_FIRST_ACCESS_RECEIPT_AUDIT_TRAIL"
            if ready
            else
            "NO_GO_HOLD_PRIVATE_BETA_TESTER_SESSION_ACTIVATION_GATE"
        ),
    }
