from __future__ import annotations

from typing import Any, Mapping


PACKAGE = "GP065"

TITLE = (
    "Private Beta Tester Access Launch Closeout"
)


def closeout_private_beta_tester_access_launch(
    gp061: Mapping[str, Any],
    gp062: Mapping[str, Any],
    gp063: Mapping[str, Any],
    gp064: Mapping[str, Any],
) -> dict[str, Any]:

    failures: list[str] = []

    required = (
        (
            "gp061_entitlement_record",
            gp061.get(
                "entitlement_record_issued"
            ),
        ),
        (
            "gp062_credential_boundary",
            gp062.get(
                "credential_boundary_ready"
            ),
        ),
        (
            "gp063_session_activation_gate",
            gp063.get(
                "session_activation_gate_ready"
            ),
        ),
        (
            "gp064_first_access_audit",
            gp064.get(
                "first_access_audit_ready"
            ),
        ),
    )

    for label, passed in required:
        if (
            passed
            is not True
        ):
            failures.append(
                f"{label}_required"
            )

    forbidden_true = (
        (
            "credential_material_created",
            gp062.get(
                "credential_material_created"
            ),
        ),
        (
            "tester_session_activated",
            gp063.get(
                "tester_session_activated"
            ),
        ),
        (
            "external_beta_access_opened",
            gp063.get(
                "external_beta_access_opened"
            ),
        ),
        (
            "first_access_occurred",
            gp064.get(
                "first_access_occurred"
            ),
        ),
        (
            "receipt_recorded",
            gp064.get(
                "receipt_recorded"
            ),
        ),
    )

    for label, value in forbidden_true:
        if (
            value
            is not False
        ):
            failures.append(
                f"{label}_must_be_false"
            )

    ready = not failures

    return {
        "package": PACKAGE,
        "title": TITLE,
        "gate_state": (
            "private_beta_tester_access_launch_closeout_sealed"
            if ready
            else
            "private_beta_tester_access_launch_closeout_hold"
        ),
        "launch_preparation_closeout_ready": ready,

        "tester_entitlement_record_ready": (
            gp061.get(
                "entitlement_record_issued"
            )
            is True
        ),

        "tower_credential_boundary_ready": (
            gp062.get(
                "credential_boundary_ready"
            )
            is True
        ),

        "tester_session_activation_gate_ready": (
            gp063.get(
                "session_activation_gate_ready"
            )
            is True
        ),

        "first_access_audit_ready": (
            gp064.get(
                "first_access_audit_ready"
            )
            is True
        ),

        "credential_material_created": False,
        "password_created": False,
        "token_created": False,
        "tester_session_created": False,
        "tester_session_activated": False,
        "external_tester_invited": False,
        "external_beta_access_opened": False,
        "first_external_tester_launched": False,
        "first_access_occurred": False,

        "owner_walkthrough_required": True,
        "owner_walkthrough_completed": False,
        "owner_walkthrough_accepted": False,

        "owner_console_tester_access": False,
        "manual_live_owner_only": True,
        "live_auto_locked": True,
        "broker_submission_locked": True,
        "real_capital_movement_locked": True,
        "direct_execution_disabled": True,
        "automated_execution_disabled": True,
        "production_deploy_disabled": True,
        "secret_reveal_disabled": True,

        "walkthrough_timing": (
            "NOW_AFTER_GP065_REMOTE_VERIFICATION_BEFORE_FIRST_EXTERNAL_TESTER"
        ),

        "walkthrough_scope": [
            "Tower owner login",
            "Tower Access Home",
            "Tower to Observatory launch",
            "Dashboard",
            "Market Map",
            "Symbol Page",
            "Trade Center",
            "Review Center",
            "Owner Console owner-only verification",
            "Survey mode verification",
            "Paper mode verification",
            "Manual Live owner-only verification",
            "Live Auto locked verification",
            "Tester Owner Console denial verification",
            "Tester broker submission denial verification",
            "Tester real-capital denial verification",
            "Return to Tower",
            "Session continuity",
            "Receipts and audit visibility",
        ],

        "first_external_tester_launch_authorized": False,

        "next_build": (
            "Owner Private Beta Walkthrough Acceptance "
            "and First Tester Launch Authorization / GP066"
        ),

        "failures": failures,

        "recommendation": (
            "GO_FOR_OWNER_PRIVATE_BETA_WALKTHROUGH_BEFORE_FIRST_TESTER"
            if ready
            else
            "NO_GO_HOLD_PRIVATE_BETA_TESTER_ACCESS_LAUNCH_CLOSEOUT"
        ),
    }
