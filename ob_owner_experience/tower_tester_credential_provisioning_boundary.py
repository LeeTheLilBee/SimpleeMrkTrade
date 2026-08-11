from __future__ import annotations

from typing import Any, Mapping


PACKAGE = "GP062"

TITLE = (
    "Tower Tester Credential Provisioning Boundary"
)


def prepare_tower_tester_credential_boundary(
    issuance: Mapping[str, Any],
) -> dict[str, Any]:

    failures: list[str] = []

    if (
        issuance.get(
            "entitlement_record_issued"
        )
        is not True
    ):
        failures.append(
            "gp061_entitlement_required"
        )

    if (
        issuance.get(
            "tower_managed"
        )
        is not True
    ):
        failures.append(
            "tower_managed_access_required"
        )

    if (
        issuance.get(
            "credential_material_issued"
        )
        is not False
    ):
        failures.append(
            "credential_material_must_not_already_exist"
        )

    if (
        issuance.get(
            "secret_revealed"
        )
        is not False
    ):
        failures.append(
            "secret_reveal_must_be_false"
        )

    if (
        issuance.get(
            "external_beta_access_opened"
        )
        is not False
    ):
        failures.append(
            "external_beta_access_must_remain_closed"
        )

    ready = not failures

    request = {
        "tester_id": (
            issuance.get(
                "tester_id"
            )
        ),
        "access_id": (
            issuance.get(
                "access_id"
            )
        ),
        "credential_authority": "Tower",
        "provisioning_method": (
            "one_time_setup_through_tower"
        ),
        "mfa_required": True,
        "password_storage": (
            "tower_managed_hash_only"
        ),
        "plaintext_password_storage": False,
        "raw_token_storage": False,
        "credential_secret_in_ob": False,
        "credential_secret_in_evidence": False,
        "credential_secret_in_logs": False,
        "credential_secret_in_git": False,
        "revocation_required": True,
        "rotation_supported": True,
    }

    return {
        "package": PACKAGE,
        "title": TITLE,
        "gate_state": (
            "tower_tester_credential_provisioning_boundary_sealed"
            if ready
            else
            "tower_tester_credential_provisioning_boundary_hold"
        ),
        "credential_boundary_ready": ready,
        "provisioning_request": request,
        "credential_material_created": False,
        "password_created": False,
        "token_created": False,
        "secret_revealed": False,
        "credential_sent": False,
        "tester_session_created": False,
        "tester_session_activated": False,
        "external_beta_access_opened": False,
        "failures": failures,
        "recommendation": (
            "GO_FOR_PRIVATE_BETA_TESTER_SESSION_ACTIVATION_GATE"
            if ready
            else
            "NO_GO_HOLD_TOWER_TESTER_CREDENTIAL_PROVISIONING_BOUNDARY"
        ),
    }
