"""
GP038 — Delivery Attempt Record / External Receipt Preparation.
"""

from __future__ import annotations

try:
    from .protected_handoff_delivery_attempt import (
        ProtectedDeliveryAttemptState,
        ProtectedHandoffDeliveryAttemptRecord,
    )

    from .protected_handoff_release_execution_service import (
        get_clouds_gp037_status_payload,
        get_gp037_release_execution,
    )

except ImportError:
    from protected_handoff_delivery_attempt import (
        ProtectedDeliveryAttemptState,
        ProtectedHandoffDeliveryAttemptRecord,
    )

    from protected_handoff_release_execution_service import (
        get_clouds_gp037_status_payload,
        get_gp037_release_execution,
    )


def build_delivery_attempt_record(
    release_execution,
):
    if (
        release_execution.release_execution_state
        != "released_to_external_boundary"
    ):
        raise ValueError(
            "Release has not reached the external boundary."
        )

    if (
        release_execution.delivery_release_executed
        is not True
    ):
        raise ValueError(
            "Release execution is incomplete."
        )

    if (
        release_execution.released_to_delivery_boundary
        is not True
    ):
        raise ValueError(
            "Envelope has not reached delivery boundary."
        )

    if (
        release_execution.external_transport_invoked
        is not False
    ):
        raise ValueError(
            "Unexpected external transport state."
        )

    if (
        release_execution.tower_contacted
        is not False
    ):
        raise ValueError(
            "Tower must not already be contacted."
        )

    if (
        release_execution.external_delivery_attempted
        is not False
    ):
        raise ValueError(
            "External delivery already attempted."
        )

    if (
        release_execution.handoff_delivered
        is not False
    ):
        raise ValueError(
            "Handoff already delivered."
        )

    return ProtectedHandoffDeliveryAttemptRecord(
        delivery_attempt_record_id=(
            "protected-delivery-attempt-"
            f"{release_execution.release_execution_id}"
        ),

        release_execution_id=(
            release_execution.release_execution_id
        ),

        delivery_envelope_id=(
            release_execution.delivery_envelope_id
        ),

        delivery_envelope_integrity_hash=(
            release_execution
            .delivery_envelope_integrity_hash
        ),

        release_record_id=(
            release_execution.release_record_id
        ),

        release_record_integrity_hash=(
            release_execution
            .release_record_integrity_hash
        ),

        handoff_package_id=(
            release_execution.handoff_package_id
        ),

        package_integrity_hash=(
            release_execution.package_integrity_hash
        ),

        source_id=release_execution.source_id,
        source_label=release_execution.source_label,

        selected_option_id=(
            release_execution.selected_option_id
        ),

        selected_option_kind=(
            release_execution.selected_option_kind
        ),

        selected_option_label=(
            release_execution.selected_option_label
        ),

        owning_application_id=(
            release_execution.owning_application_id
        ),

        owning_application_label=(
            release_execution.owning_application_label
        ),

        requires_tower_mediation=(
            release_execution.requires_tower_mediation
        ),

        delivery_target_kind=(
            release_execution.delivery_target_kind
        ),

        delivery_target_id=(
            release_execution.delivery_target_id
        ),

        attempt_state=(
            ProtectedDeliveryAttemptState
            .AWAITING_EXTERNAL_TRANSPORT.value
        ),

        delivery_attempt_record_prepared=True,

        external_transport_required=True,

        external_transport_invoked=False,

        tower_contacted=False,

        external_delivery_attempted=False,

        external_receipt_required=True,

        external_receipt_present=False,

        external_acceptance_verified=False,

        handoff_delivered=False,

        approval_performed=False,
        capital_movement_performed=False,
        downstream_execution_performed=False,

        soulaana_summary=(
            "The external delivery-attempt record is ready."
        ),

        soulaana_what_this_means=(
            "Clouds has prepared everything needed to describe "
            "the next external delivery step without pretending "
            "that the step already happened."
        ),

        soulaana_what_can_wait=(
            "Nothing needs to be marked delivered until an "
            "actual external adapter returns a real receipt."
        ),

        soulaana_next_step=(
            "Accept only a verifiable external delivery receipt "
            "that binds back to this exact attempt and envelope."
        ),
    )


def get_gp038_delivery_attempt_record():
    return build_delivery_attempt_record(
        get_gp037_release_execution()
    )


def get_clouds_gp038_status_payload():
    gp037 = (
        get_clouds_gp037_status_payload()
    )

    record = (
        get_gp038_delivery_attempt_record()
    )

    safe = (
        gp037["status"] == "ready"
        and gp037["safe_to_continue"] is True

        and gp037["delivery_release_executed"]
        is True

        and gp037["tower_contacted"]
        is False

        and gp037["external_delivery_attempted"]
        is False

        and gp037["handoff_delivered"]
        is False

        and record.attempt_state
        == "awaiting_external_transport"

        and record.delivery_attempt_record_prepared
        is True

        and record.external_transport_required
        is True

        and record.external_transport_invoked
        is False

        and record.tower_contacted
        is False

        and record.external_delivery_attempted
        is False

        and record.external_receipt_required
        is True

        and record.external_receipt_present
        is False

        and record.external_acceptance_verified
        is False

        and record.handoff_delivered
        is False
    )

    return {
        "pack": "GP038",
        "phase": "CLOUDS_PHASE_II",

        "section": (
            "DELIVERY ATTEMPT RECORD / "
            "EXTERNAL RECEIPT PREPARATION"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "attempt_state": (
            record.attempt_state
        ),

        "delivery_attempt_record_prepared": True,

        "external_transport_required": True,

        "external_transport_invoked": False,

        "tower_contacted": False,

        "external_delivery_attempted": False,

        "external_receipt_required": True,

        "external_receipt_present": False,

        "external_acceptance_verified": False,

        "handoff_delivered": False,

        "downstream_execution_performed": False,

        "next_pack": (
            "GP039 — EXTERNAL RECEIPT / "
            "ACCEPTANCE VALIDATION CONTRACT"
        ),
    }
