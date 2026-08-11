from __future__ import annotations

from typing import Any, Mapping


PACKAGE = "GP064"

TITLE = (
    "Private Beta First-Access Receipt & Audit Trail"
)


REQUIRED_RECEIPT_FIELDS = (
    "receipt_id",
    "tester_id",
    "access_id",
    "tower_session_reference",
    "event_type",
    "mode",
    "room",
    "occurred_at_utc",
    "access_result",
    "policy_snapshot",
)


def prepare_private_beta_first_access_receipt_audit_trail(
    session_gate: Mapping[str, Any],
    issuance: Mapping[str, Any],
) -> dict[str, Any]:

    failures: list[str] = []

    if (
        session_gate.get(
            "session_activation_gate_ready"
        )
        is not True
    ):
        failures.append(
            "gp063_session_gate_required"
        )

    if (
        session_gate.get(
            "tester_session_activated"
        )
        is not False
    ):
        failures.append(
            "tester_session_must_not_yet_be_active"
        )

    if (
        session_gate.get(
            "external_beta_access_opened"
        )
        is not False
    ):
        failures.append(
            "external_beta_access_must_remain_closed"
        )

    tester_id = (
        issuance.get(
            "tester_id"
        )
    )

    access_id = (
        issuance.get(
            "access_id"
        )
    )

    if not tester_id:
        failures.append(
            "tester_id_required"
        )

    if not access_id:
        failures.append(
            "access_id_required"
        )

    ready = not failures

    receipt_schema = {
        "required_fields": list(
            REQUIRED_RECEIPT_FIELDS
        ),
        "event_type": (
            "private_beta_first_access"
        ),
        "allowed_modes": [
            "Survey",
            "Paper",
        ],
        "owner_console_access": False,
        "manual_live_access": False,
        "live_auto_access": False,
        "broker_submission_access": False,
        "real_capital_access": False,
        "secret_capture_allowed": False,
        "credential_capture_allowed": False,
        "append_only": True,
        "tamper_evident_required": True,
        "tower_session_reference_required": True,
        "policy_snapshot_required": True,
    }

    audit_schema = {
        "tester_id": tester_id,
        "access_id": access_id,
        "record_login_result": True,
        "record_room_entry": True,
        "record_mode": True,
        "record_denied_actions": True,
        "record_session_expiry": True,
        "record_revocation": True,
        "record_owner_console_denial": True,
        "record_manual_live_denial": True,
        "record_live_auto_denial": True,
        "record_broker_submission_denial": True,
        "record_real_capital_denial": True,
        "record_credentials": False,
        "record_secrets": False,
    }

    return {
        "package": PACKAGE,
        "title": TITLE,
        "gate_state": (
            "private_beta_first_access_receipt_audit_trail_sealed"
            if ready
            else
            "private_beta_first_access_receipt_audit_trail_hold"
        ),
        "first_access_audit_ready": ready,
        "receipt_schema": receipt_schema,
        "audit_schema": audit_schema,
        "first_access_occurred": False,
        "receipt_recorded": False,
        "tester_session_activated": False,
        "external_beta_access_opened": False,
        "credential_secret_recorded": False,
        "failures": failures,
        "recommendation": (
            "GO_FOR_PRIVATE_BETA_TESTER_ACCESS_LAUNCH_CLOSEOUT"
            if ready
            else
            "NO_GO_HOLD_PRIVATE_BETA_FIRST_ACCESS_AUDIT"
        ),
    }
