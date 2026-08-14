"""
GP037 — Protected Handoff Release Execution / Delivery Attempt Boundary.
"""

from __future__ import annotations

try:
    from .protected_handoff_release_execution import (
        ProtectedHandoffReleaseExecution,
        ProtectedReleaseExecutionState,
    )

    from .protected_handoff_release_record_service import (
        get_clouds_gp036_status_payload,
        get_gp036_delivery_envelope,
    )

except ImportError:
    from protected_handoff_release_execution import (
        ProtectedHandoffReleaseExecution,
        ProtectedReleaseExecutionState,
    )

    from protected_handoff_release_record_service import (
        get_clouds_gp036_status_payload,
        get_gp036_delivery_envelope,
    )


ENVELOPE_BINDING_FIELDS = (
    "delivery_envelope_id",
    "delivery_envelope_schema_version",

    "release_record_id",
    "release_record_integrity_hash",

    "release_authorization_id",

    "handoff_package_id",
    "package_integrity_hash",

    "source_id",
    "source_label",

    "impacted_source_id",
    "impacted_source_label",

    "selected_option_id",
    "selected_option_kind",
    "selected_option_label",

    "owning_application_id",
    "owning_application_label",

    "requires_tower_mediation",

    "delivery_target_kind",
    "delivery_target_id",

    "envelope_state",
    "envelope_prepared",

    "delivery_release_authorized",
    "delivery_release_executed",
    "delivery_released",
    "delivery_attempted",
    "handoff_delivered",

    "credentials_included",
    "tower_session_material_included",
    "raw_evidence_included",

    "approval_performed",
    "capital_movement_performed",
    "downstream_execution_performed",

    "delivery_envelope_integrity_hash",
)


def _canonical_envelope():
    return (
        get_gp036_delivery_envelope()
    )


def _binding_matches(
    candidate,
    canonical,
):
    return all(
        getattr(candidate, field)
        == getattr(canonical, field)
        for field in ENVELOPE_BINDING_FIELDS
    )


def execute_protected_handoff_release(
    envelope,
):
    """
    Execute Clouds-side release to the external boundary.

    No external transport is invoked.
    """

    canonical = (
        _canonical_envelope()
    )

    if (
        envelope.envelope_state
        != "prepared"
    ):
        raise ValueError(
            "Envelope is not prepared."
        )

    if (
        envelope.envelope_prepared
        is not True
    ):
        raise ValueError(
            "Envelope preparation incomplete."
        )

    if (
        envelope.delivery_release_authorized
        is not True
    ):
        raise ValueError(
            "Release authorization missing."
        )

    if (
        envelope.delivery_release_executed
        is not False
    ):
        raise ValueError(
            "Release already executed."
        )

    if (
        envelope.delivery_released
        is not False
    ):
        raise ValueError(
            "Envelope already released."
        )

    if (
        envelope.delivery_attempted
        is not False
    ):
        raise ValueError(
            "Delivery already attempted."
        )

    if (
        envelope.handoff_delivered
        is not False
    ):
        raise ValueError(
            "Handoff already delivered."
        )

    if (
        envelope.credentials_included
        is not False
        or envelope
        .tower_session_material_included
        is not False
        or envelope.raw_evidence_included
        is not False
    ):
        raise ValueError(
            "Protected envelope contains prohibited material."
        )

    if (
        envelope.delivery_envelope_integrity_hash
        != canonical.delivery_envelope_integrity_hash
    ):
        raise ValueError(
            "Envelope integrity hash changed."
        )

    if not _binding_matches(
        envelope,
        canonical,
    ):
        raise ValueError(
            "Envelope binding changed."
        )

    return ProtectedHandoffReleaseExecution(
        release_execution_id=(
            "protected-release-execution-"
            f"{envelope.delivery_envelope_id}"
        ),

        release_record_id=(
            envelope.release_record_id
        ),

        release_record_integrity_hash=(
            envelope.release_record_integrity_hash
        ),

        delivery_envelope_id=(
            envelope.delivery_envelope_id
        ),

        delivery_envelope_integrity_hash=(
            envelope.delivery_envelope_integrity_hash
        ),

        release_authorization_id=(
            envelope.release_authorization_id
        ),

        handoff_package_id=(
            envelope.handoff_package_id
        ),

        package_integrity_hash=(
            envelope.package_integrity_hash
        ),

        source_id=envelope.source_id,
        source_label=envelope.source_label,

        impacted_source_id=(
            envelope.impacted_source_id
        ),

        impacted_source_label=(
            envelope.impacted_source_label
        ),

        selected_option_id=(
            envelope.selected_option_id
        ),

        selected_option_kind=(
            envelope.selected_option_kind
        ),

        selected_option_label=(
            envelope.selected_option_label
        ),

        owning_application_id=(
            envelope.owning_application_id
        ),

        owning_application_label=(
            envelope.owning_application_label
        ),

        requires_tower_mediation=(
            envelope.requires_tower_mediation
        ),

        delivery_target_kind=(
            envelope.delivery_target_kind
        ),

        delivery_target_id=(
            envelope.delivery_target_id
        ),

        release_execution_state=(
            ProtectedReleaseExecutionState
            .RELEASED_TO_EXTERNAL_BOUNDARY.value
        ),

        delivery_release_authorized=True,
        delivery_release_executed=True,

        released_to_delivery_boundary=True,

        external_transport_invoked=False,
        tower_contacted=False,
        external_delivery_attempted=False,
        external_receipt_present=False,

        handoff_delivered=False,

        approval_performed=False,
        capital_movement_performed=False,
        downstream_execution_performed=False,

        soulaana_summary=(
            "I released the sealed handoff envelope "
            "to the edge of Clouds."
        ),

        soulaana_what_this_means=(
            "Clouds has completed its internal release step. "
            "The envelope is now ready for a separate external "
            "delivery adapter."
        ),

        soulaana_what_did_not_happen=(
            "Tower was not contacted, no external transport "
            "ran, no receipt was received, and nothing "
            "downstream executed."
        ),

        soulaana_next_step=(
            "Prepare the external delivery-attempt record "
            "without claiming that Tower has received anything."
        ),
    )


def get_gp037_release_execution():
    return execute_protected_handoff_release(
        _canonical_envelope()
    )


def get_clouds_gp037_status_payload():
    gp036 = (
        get_clouds_gp036_status_payload()
    )

    execution = (
        get_gp037_release_execution()
    )

    safe = (
        gp036["status"] == "ready"
        and gp036["safe_to_continue"] is True

        and gp036["delivery_release_authorized"] is True
        and gp036["delivery_release_executed"] is False
        and gp036["delivery_attempted"] is False
        and gp036["handoff_delivered"] is False

        and execution.release_execution_state
        == "released_to_external_boundary"

        and execution.delivery_release_executed
        is True

        and execution.released_to_delivery_boundary
        is True

        and execution.external_transport_invoked
        is False

        and execution.tower_contacted
        is False

        and execution.external_delivery_attempted
        is False

        and execution.external_receipt_present
        is False

        and execution.handoff_delivered
        is False

        and execution.downstream_execution_performed
        is False
    )

    return {
        "pack": "GP037",
        "phase": "CLOUDS_PHASE_II",

        "section": (
            "PROTECTED HANDOFF RELEASE EXECUTION / "
            "DELIVERY ATTEMPT BOUNDARY"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "release_execution_state": (
            execution.release_execution_state
        ),

        "delivery_release_authorized": True,

        "delivery_release_executed": True,

        "released_to_delivery_boundary": True,

        "external_transport_invoked": False,

        "tower_contacted": False,

        "external_delivery_attempted": False,

        "external_receipt_present": False,

        "handoff_delivered": False,

        "approval_performed": False,

        "capital_movement_performed": False,

        "downstream_execution_performed": False,

        "next_pack": (
            "GP038 — DELIVERY ATTEMPT RECORD / "
            "EXTERNAL RECEIPT PREPARATION"
        ),
    }
