"""
GP036 — Protected Handoff Release Record / Delivery Envelope Preparation.

Builds release artifacts from the exact GP035-authorized
package without releasing or delivering anything.
"""

from __future__ import annotations

import hashlib
import json

try:
    from .protected_handoff_delivery_release_service import (
        get_clouds_gp035_status_payload,
        get_gp035_authorized_fixture,
        get_gp035_declined_fixture,
    )

    from .protected_handoff_release_record import (
        ProtectedDeliveryEnvelopeState,
        ProtectedHandoffDeliveryEnvelope,
        ProtectedHandoffReleasePreparationSurface,
        ProtectedHandoffReleaseRecord,
        ProtectedReleaseRecordState,
    )

except ImportError:
    from protected_handoff_delivery_release_service import (
        get_clouds_gp035_status_payload,
        get_gp035_authorized_fixture,
        get_gp035_declined_fixture,
    )

    from protected_handoff_release_record import (
        ProtectedDeliveryEnvelopeState,
        ProtectedHandoffDeliveryEnvelope,
        ProtectedHandoffReleasePreparationSurface,
        ProtectedHandoffReleaseRecord,
        ProtectedReleaseRecordState,
    )


RELEASE_RECORD_SCHEMA_VERSION = (
    "clouds-protected-handoff-release-record-v1"
)

DELIVERY_ENVELOPE_SCHEMA_VERSION = (
    "clouds-protected-handoff-delivery-envelope-v1"
)


RELEASE_AUTHORIZATION_BINDING_FIELDS = (
    "release_authorization_id",

    "handoff_package_id",
    "package_schema_version",
    "package_integrity_hash",

    "authorization_record_id",
    "intent_review_id",
    "choice_record_id",
    "decision_review_id",
    "decision_packet_id",
    "agenda_item_id",

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

    "owner_release_decision",
    "release_state",

    "owner_confirmation_recorded",

    "package_integrity_verified",
    "package_binding_verified",

    "delivery_release_authorized",
    "delivery_released",
    "handoff_delivered",

    "credentials_included",
    "tower_session_material_included",
    "raw_evidence_included",

    "approval_performed",
    "capital_movement_performed",
    "downstream_execution_performed",
)


RELEASE_RECORD_BINDING_FIELDS = (
    "release_record_id",
    "release_record_schema_version",

    "release_authorization_id",

    "handoff_package_id",
    "package_schema_version",
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

    "owner_release_decision",
    "release_authorization_state",

    "owner_confirmation_recorded",

    "package_integrity_verified",
    "package_binding_verified",

    "release_record_state",
    "release_record_prepared",

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

    "release_record_integrity_hash",
)


def _sha256(payload):
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")

    return hashlib.sha256(
        canonical
    ).hexdigest()


def _canonical_release_authorization():
    return (
        get_gp035_authorized_fixture()
    )


def _release_authorization_binding_matches(
    candidate,
    canonical,
):
    return all(
        getattr(candidate, field)
        == getattr(canonical, field)
        for field
        in RELEASE_AUTHORIZATION_BINDING_FIELDS
    )


def _validate_release_authorization(
    release_authorization,
):
    canonical = (
        _canonical_release_authorization()
    )

    if (
        release_authorization
        .owner_confirmation_recorded
        is not True
    ):
        raise ValueError(
            "Explicit owner release confirmation is required."
        )

    if (
        release_authorization
        .owner_release_decision
        != "authorize_release"
    ):
        raise ValueError(
            "Declined release authorization cannot enter GP036."
        )

    if (
        release_authorization
        .release_state
        != "authorized_for_release"
    ):
        raise ValueError(
            "Release authorization is not in the authorized state."
        )

    if (
        release_authorization
        .package_integrity_verified
        is not True
    ):
        raise ValueError(
            "Package integrity must be verified."
        )

    if (
        release_authorization
        .package_binding_verified
        is not True
    ):
        raise ValueError(
            "Package binding must be verified."
        )

    if (
        release_authorization
        .delivery_release_authorized
        is not True
    ):
        raise ValueError(
            "GP035 release authorization is required."
        )

    if (
        release_authorization
        .delivery_released
        is not False
    ):
        raise ValueError(
            "Already-released handoff cannot enter GP036."
        )

    if (
        release_authorization
        .handoff_delivered
        is not False
    ):
        raise ValueError(
            "Already-delivered handoff cannot enter GP036."
        )

    if (
        release_authorization
        .credentials_included
        is not False
    ):
        raise ValueError(
            "Credentials are prohibited."
        )

    if (
        release_authorization
        .tower_session_material_included
        is not False
    ):
        raise ValueError(
            "Tower session material is prohibited."
        )

    if (
        release_authorization
        .raw_evidence_included
        is not False
    ):
        raise ValueError(
            "Raw evidence is prohibited."
        )

    if (
        release_authorization
        .approval_performed
        is not False
    ):
        raise ValueError(
            "Unexpected approval state."
        )

    if (
        release_authorization
        .capital_movement_performed
        is not False
    ):
        raise ValueError(
            "Unexpected capital movement."
        )

    if (
        release_authorization
        .downstream_execution_performed
        is not False
    ):
        raise ValueError(
            "Unexpected downstream execution."
        )

    if (
        len(
            release_authorization
            .package_integrity_hash
        )
        != 64
    ):
        raise ValueError(
            "Package integrity hash is malformed."
        )

    if (
        release_authorization
        .package_integrity_hash
        != canonical.package_integrity_hash
    ):
        raise ValueError(
            "Package integrity hash changed after GP035."
        )

    if not (
        _release_authorization_binding_matches(
            release_authorization,
            canonical,
        )
    ):
        raise ValueError(
            "GP035 release authorization binding changed."
        )

    return canonical


def _release_record_hash_payload(
    release_authorization,
):
    return {
        "schema_version": (
            RELEASE_RECORD_SCHEMA_VERSION
        ),

        "release_authorization_id": (
            release_authorization
            .release_authorization_id
        ),

        "handoff_package_id": (
            release_authorization
            .handoff_package_id
        ),

        "package_schema_version": (
            release_authorization
            .package_schema_version
        ),

        "package_integrity_hash": (
            release_authorization
            .package_integrity_hash
        ),

        "source_id": (
            release_authorization
            .source_id
        ),

        "impacted_source_id": (
            release_authorization
            .impacted_source_id
        ),

        "selected_option_id": (
            release_authorization
            .selected_option_id
        ),

        "selected_option_kind": (
            release_authorization
            .selected_option_kind
        ),

        "owning_application_id": (
            release_authorization
            .owning_application_id
        ),

        "requires_tower_mediation": (
            release_authorization
            .requires_tower_mediation
        ),

        "delivery_target_kind": (
            release_authorization
            .delivery_target_kind
        ),

        "delivery_target_id": (
            release_authorization
            .delivery_target_id
        ),

        "owner_release_decision": (
            release_authorization
            .owner_release_decision
        ),

        "delivery_release_authorized": True,

        "delivery_release_executed": False,

        "delivery_released": False,

        "delivery_attempted": False,

        "handoff_delivered": False,
    }


def build_protected_handoff_release_record(
    release_authorization,
):
    """
    Freeze the GP035 authorization into a release record.

    Does not execute the release.
    """

    canonical = (
        _validate_release_authorization(
            release_authorization
        )
    )

    record_hash = _sha256(
        _release_record_hash_payload(
            release_authorization
        )
    )

    return ProtectedHandoffReleaseRecord(
        release_record_id=(
            "protected-release-record-"
            f"{release_authorization.release_authorization_id}"
        ),

        release_record_schema_version=(
            RELEASE_RECORD_SCHEMA_VERSION
        ),

        release_authorization_id=(
            release_authorization
            .release_authorization_id
        ),

        handoff_package_id=(
            release_authorization
            .handoff_package_id
        ),

        package_schema_version=(
            release_authorization
            .package_schema_version
        ),

        package_integrity_hash=(
            release_authorization
            .package_integrity_hash
        ),

        authorization_record_id=(
            release_authorization
            .authorization_record_id
        ),

        intent_review_id=(
            release_authorization
            .intent_review_id
        ),

        choice_record_id=(
            release_authorization
            .choice_record_id
        ),

        decision_review_id=(
            release_authorization
            .decision_review_id
        ),

        decision_packet_id=(
            release_authorization
            .decision_packet_id
        ),

        agenda_item_id=(
            release_authorization
            .agenda_item_id
        ),

        source_id=(
            release_authorization
            .source_id
        ),

        source_label=(
            release_authorization
            .source_label
        ),

        impacted_source_id=(
            release_authorization
            .impacted_source_id
        ),

        impacted_source_label=(
            release_authorization
            .impacted_source_label
        ),

        selected_option_id=(
            release_authorization
            .selected_option_id
        ),

        selected_option_kind=(
            release_authorization
            .selected_option_kind
        ),

        selected_option_label=(
            release_authorization
            .selected_option_label
        ),

        owning_application_id=(
            release_authorization
            .owning_application_id
        ),

        owning_application_label=(
            release_authorization
            .owning_application_label
        ),

        requires_tower_mediation=(
            release_authorization
            .requires_tower_mediation
        ),

        delivery_target_kind=(
            release_authorization
            .delivery_target_kind
        ),

        delivery_target_id=(
            release_authorization
            .delivery_target_id
        ),

        owner_release_decision=(
            release_authorization
            .owner_release_decision
        ),

        release_authorization_state=(
            release_authorization
            .release_state
        ),

        owner_confirmation_recorded=(
            release_authorization
            .owner_confirmation_recorded
        ),

        package_integrity_verified=(
            release_authorization
            .package_integrity_hash
            == canonical.package_integrity_hash
        ),

        package_binding_verified=(
            _release_authorization_binding_matches(
                release_authorization,
                canonical,
            )
        ),

        release_record_state=(
            ProtectedReleaseRecordState
            .PREPARED.value
        ),

        release_record_prepared=True,

        delivery_release_authorized=True,

        delivery_release_executed=False,

        delivery_released=False,

        delivery_attempted=False,

        handoff_delivered=False,

        credentials_included=False,

        tower_session_material_included=False,

        raw_evidence_included=False,

        approval_performed=False,

        capital_movement_performed=False,

        downstream_execution_performed=False,

        release_record_integrity_hash=(
            record_hash
        ),

        soulaana_release_record_summary=(
            "I created the protected release record for "
            f"your authorized {release_authorization.source_label} "
            "handoff package."
        ),

        soulaana_why_it_matters=(
            "This record freezes exactly what was authorized "
            "to enter the release lane before anything can "
            "actually leave Clouds."
        ),

        soulaana_release_boundary=(
            "The release record exists, but the release itself "
            "has not been executed and no delivery attempt "
            "has occurred."
        ),

        soulaana_next_step=(
            "Prepare the bounded delivery envelope around "
            "this exact release record."
        ),
    )


def get_gp036_release_record():
    return (
        build_protected_handoff_release_record(
            _canonical_release_authorization()
        )
    )


def _release_record_binding_matches(
    candidate,
    canonical,
):
    return all(
        getattr(candidate, field)
        == getattr(canonical, field)
        for field
        in RELEASE_RECORD_BINDING_FIELDS
    )


def _validate_release_record(
    release_record,
):
    canonical = (
        get_gp036_release_record()
    )

    if (
        release_record.release_record_state
        != "prepared"
    ):
        raise ValueError(
            "Only a prepared release record may be enveloped."
        )

    if (
        release_record.release_record_prepared
        is not True
    ):
        raise ValueError(
            "Release record preparation is incomplete."
        )

    if (
        release_record.delivery_release_authorized
        is not True
    ):
        raise ValueError(
            "Release authorization is missing."
        )

    if (
        release_record.delivery_release_executed
        is not False
    ):
        raise ValueError(
            "Release has already been executed."
        )

    if (
        release_record.delivery_released
        is not False
    ):
        raise ValueError(
            "Release record already reports release."
        )

    if (
        release_record.delivery_attempted
        is not False
    ):
        raise ValueError(
            "Delivery has already been attempted."
        )

    if (
        release_record.handoff_delivered
        is not False
    ):
        raise ValueError(
            "Handoff has already been delivered."
        )

    if (
        release_record.credentials_included
        is not False
    ):
        raise ValueError(
            "Credentials are prohibited."
        )

    if (
        release_record
        .tower_session_material_included
        is not False
    ):
        raise ValueError(
            "Tower session material is prohibited."
        )

    if (
        release_record.raw_evidence_included
        is not False
    ):
        raise ValueError(
            "Raw evidence is prohibited."
        )

    if (
        len(
            release_record
            .release_record_integrity_hash
        )
        != 64
    ):
        raise ValueError(
            "Release-record integrity hash is malformed."
        )

    if (
        release_record.release_record_integrity_hash
        != canonical.release_record_integrity_hash
    ):
        raise ValueError(
            "Release-record integrity hash changed."
        )

    if not _release_record_binding_matches(
        release_record,
        canonical,
    ):
        raise ValueError(
            "Release-record binding changed."
        )

    return canonical


def _delivery_envelope_hash_payload(
    release_record,
):
    return {
        "schema_version": (
            DELIVERY_ENVELOPE_SCHEMA_VERSION
        ),

        "release_record_id": (
            release_record
            .release_record_id
        ),

        "release_record_integrity_hash": (
            release_record
            .release_record_integrity_hash
        ),

        "release_authorization_id": (
            release_record
            .release_authorization_id
        ),

        "handoff_package_id": (
            release_record
            .handoff_package_id
        ),

        "package_integrity_hash": (
            release_record
            .package_integrity_hash
        ),

        "source_id": (
            release_record
            .source_id
        ),

        "impacted_source_id": (
            release_record
            .impacted_source_id
        ),

        "selected_option_id": (
            release_record
            .selected_option_id
        ),

        "selected_option_kind": (
            release_record
            .selected_option_kind
        ),

        "owning_application_id": (
            release_record
            .owning_application_id
        ),

        "requires_tower_mediation": (
            release_record
            .requires_tower_mediation
        ),

        "delivery_target_kind": (
            release_record
            .delivery_target_kind
        ),

        "delivery_target_id": (
            release_record
            .delivery_target_id
        ),

        "delivery_release_authorized": True,

        "delivery_release_executed": False,

        "delivery_released": False,

        "delivery_attempted": False,

        "handoff_delivered": False,

        "credentials_included": False,

        "tower_session_material_included": False,

        "raw_evidence_included": False,
    }


def build_protected_handoff_delivery_envelope(
    release_record,
):
    """
    Wrap the exact GP036 release record in the bounded
    delivery envelope.

    Does not release or send it.
    """

    canonical = (
        _validate_release_record(
            release_record
        )
    )

    envelope_hash = _sha256(
        _delivery_envelope_hash_payload(
            release_record
        )
    )

    return ProtectedHandoffDeliveryEnvelope(
        delivery_envelope_id=(
            "protected-delivery-envelope-"
            f"{release_record.release_record_id}"
        ),

        delivery_envelope_schema_version=(
            DELIVERY_ENVELOPE_SCHEMA_VERSION
        ),

        release_record_id=(
            release_record.release_record_id
        ),

        release_record_integrity_hash=(
            release_record
            .release_record_integrity_hash
        ),

        release_authorization_id=(
            release_record
            .release_authorization_id
        ),

        handoff_package_id=(
            release_record
            .handoff_package_id
        ),

        package_integrity_hash=(
            release_record
            .package_integrity_hash
        ),

        source_id=(
            release_record.source_id
        ),

        source_label=(
            release_record.source_label
        ),

        impacted_source_id=(
            release_record
            .impacted_source_id
        ),

        impacted_source_label=(
            release_record
            .impacted_source_label
        ),

        selected_option_id=(
            release_record
            .selected_option_id
        ),

        selected_option_kind=(
            release_record
            .selected_option_kind
        ),

        selected_option_label=(
            release_record
            .selected_option_label
        ),

        owning_application_id=(
            release_record
            .owning_application_id
        ),

        owning_application_label=(
            release_record
            .owning_application_label
        ),

        requires_tower_mediation=(
            release_record
            .requires_tower_mediation
        ),

        delivery_target_kind=(
            release_record
            .delivery_target_kind
        ),

        delivery_target_id=(
            release_record
            .delivery_target_id
        ),

        envelope_state=(
            ProtectedDeliveryEnvelopeState
            .PREPARED.value
        ),

        envelope_prepared=True,

        delivery_release_authorized=True,

        delivery_release_executed=False,

        delivery_released=False,

        delivery_attempted=False,

        handoff_delivered=False,

        credentials_included=False,

        tower_session_material_included=False,

        raw_evidence_included=False,

        approval_performed=False,

        capital_movement_performed=False,

        downstream_execution_performed=False,

        delivery_envelope_integrity_hash=(
            envelope_hash
        ),

        soulaana_envelope_summary=(
            "I sealed the authorized "
            f"{release_record.source_label} release record "
            "inside its protected delivery envelope."
        ),

        soulaana_why_it_matters=(
            "The envelope carries only the bounded handoff "
            "references needed for the next protected boundary "
            "while keeping credentials, session material, and "
            "raw evidence out."
        ),

        soulaana_delivery_boundary=(
            "The envelope is prepared but has not been "
            "released, transmitted, presented to Tower, "
            "or delivered."
        ),

        soulaana_next_step=(
            "A separate release-execution boundary must "
            "verify this exact envelope before any delivery "
            "attempt may occur."
        ),
    )


def get_gp036_delivery_envelope():
    return (
        build_protected_handoff_delivery_envelope(
            get_gp036_release_record()
        )
    )


def get_protected_handoff_release_preparation_surface():
    release_record = (
        get_gp036_release_record()
    )

    envelope = (
        get_gp036_delivery_envelope()
    )

    return (
        ProtectedHandoffReleasePreparationSurface(
            title=(
                "Protected Handoff Release Record / "
                "Delivery Envelope Preparation"
            ),

            release_records=(
                release_record,
            ),

            delivery_envelopes=(
                envelope,
            ),

            release_record_count=1,

            prepared_release_record_count=1,

            delivery_envelope_count=1,

            prepared_delivery_envelope_count=1,

            blocked_count=0,

            delivery_release_authorized=True,

            delivery_release_executed=False,

            delivery_released=False,

            delivery_attempted=False,

            handoff_delivered=False,

            credentials_included=False,

            tower_session_material_included=False,

            raw_evidence_included=False,

            approval_performed=False,

            capital_movement_performed=False,

            downstream_execution_performed=False,

            boundary_notice=(
                "GP036 creates the release record and delivery "
                "envelope only. Nothing leaves Clouds and no "
                "delivery attempt occurs."
            ),
        )
    )


def get_protected_handoff_release_preparation_surface_payload():
    return (
        get_protected_handoff_release_preparation_surface()
        .to_dict()
    )


def get_clouds_gp036_status_payload():
    gp035 = (
        get_clouds_gp035_status_payload()
    )

    release_record = (
        get_gp036_release_record()
    )

    repeated_release_record = (
        get_gp036_release_record()
    )

    envelope = (
        get_gp036_delivery_envelope()
    )

    repeated_envelope = (
        get_gp036_delivery_envelope()
    )

    surface = (
        get_protected_handoff_release_preparation_surface()
    )

    declined = (
        get_gp035_declined_fixture()
    )

    decline_blocked = False

    try:
        build_protected_handoff_release_record(
            declined
        )

    except ValueError:
        decline_blocked = True


    safe = (
        gp035["status"]
        == "ready"

        and gp035["safe_to_continue"]
        is True

        and gp035[
            "delivery_release_authorized"
        ]
        is True

        and gp035[
            "delivery_released"
        ]
        is False

        and gp035[
            "handoff_delivered"
        ]
        is False

        and gp035[
            "package_integrity_verified"
        ]
        is True

        and gp035[
            "package_binding_verified"
        ]
        is True

        and release_record
        .release_record_state
        == "prepared"

        and release_record
        .release_record_prepared
        is True

        and release_record
        .delivery_release_authorized
        is True

        and release_record
        .delivery_release_executed
        is False

        and release_record
        .delivery_released
        is False

        and release_record
        .delivery_attempted
        is False

        and release_record
        .handoff_delivered
        is False

        and len(
            release_record
            .release_record_integrity_hash
        )
        == 64

        and release_record
        .release_record_integrity_hash
        == repeated_release_record
        .release_record_integrity_hash

        and envelope
        .envelope_state
        == "prepared"

        and envelope
        .envelope_prepared
        is True

        and envelope
        .release_record_integrity_hash
        == release_record
        .release_record_integrity_hash

        and envelope
        .package_integrity_hash
        == release_record
        .package_integrity_hash

        and envelope
        .delivery_release_authorized
        is True

        and envelope
        .delivery_release_executed
        is False

        and envelope
        .delivery_released
        is False

        and envelope
        .delivery_attempted
        is False

        and envelope
        .handoff_delivered
        is False

        and len(
            envelope
            .delivery_envelope_integrity_hash
        )
        == 64

        and envelope
        .delivery_envelope_integrity_hash
        == repeated_envelope
        .delivery_envelope_integrity_hash

        and envelope.credentials_included
        is False

        and envelope
        .tower_session_material_included
        is False

        and envelope.raw_evidence_included
        is False

        and decline_blocked
        is True

        and surface
        .release_record_count
        == 1

        and surface
        .prepared_release_record_count
        == 1

        and surface
        .delivery_envelope_count
        == 1

        and surface
        .prepared_delivery_envelope_count
        == 1

        and surface.blocked_count
        == 0

        and surface
        .delivery_release_authorized
        is True

        and surface
        .delivery_release_executed
        is False

        and surface
        .delivery_released
        is False

        and surface
        .delivery_attempted
        is False

        and surface
        .handoff_delivered
        is False

        and surface
        .approval_performed
        is False

        and surface
        .capital_movement_performed
        is False

        and surface
        .downstream_execution_performed
        is False
    )


    return {
        "pack": "GP036",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "PROTECTED HANDOFF RELEASE RECORD / "
            "DELIVERY ENVELOPE PREPARATION"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": (
            safe
        ),

        "release_record_count": (
            surface.release_record_count
        ),

        "prepared_release_record_count": (
            surface
            .prepared_release_record_count
        ),

        "delivery_envelope_count": (
            surface.delivery_envelope_count
        ),

        "prepared_delivery_envelope_count": (
            surface
            .prepared_delivery_envelope_count
        ),

        "blocked_count": (
            surface.blocked_count
        ),

        "release_record_schema_version": (
            release_record
            .release_record_schema_version
        ),

        "delivery_envelope_schema_version": (
            envelope
            .delivery_envelope_schema_version
        ),

        "release_record_integrity_hash_present": (
            len(
                release_record
                .release_record_integrity_hash
            )
            == 64
        ),

        "release_record_integrity_hash_deterministic": (
            release_record
            .release_record_integrity_hash
            == repeated_release_record
            .release_record_integrity_hash
        ),

        "delivery_envelope_integrity_hash_present": (
            len(
                envelope
                .delivery_envelope_integrity_hash
            )
            == 64
        ),

        "delivery_envelope_integrity_hash_deterministic": (
            envelope
            .delivery_envelope_integrity_hash
            == repeated_envelope
            .delivery_envelope_integrity_hash
        ),

        "gp035_authorization_binding_preserved": True,

        "package_integrity_binding_preserved": True,

        "release_record_binding_preserved": True,

        "selected_option_binding_preserved": True,

        "owning_application_preserved": True,

        "tower_mediation_preserved": True,

        "delivery_target_preserved": True,

        "decline_path_fails_closed": (
            decline_blocked
        ),

        "credentials_included": False,

        "tower_session_material_included": False,

        "raw_evidence_included": False,

        "delivery_release_authorized": True,

        "release_record_prepared": True,

        "delivery_envelope_prepared": True,

        "delivery_release_executed": False,

        "delivery_released": False,

        "delivery_attempted": False,

        "handoff_delivered": False,

        "approval_performed": False,

        "capital_movement_performed": False,

        "downstream_execution_performed": False,

        "tower_authority_changed": False,

        "cross_app_imports_used": False,

        "next_pack": (
            "GP037 — PROTECTED HANDOFF RELEASE EXECUTION / "
            "DELIVERY ATTEMPT BOUNDARY"
        ),
    }
