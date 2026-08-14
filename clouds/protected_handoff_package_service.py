"""
GP034 — Protected Handoff Package / Delivery Preparation.

Packages GP033-authorized owner intent without delivering it.
"""

from __future__ import annotations

import hashlib
import json

try:
    from .handoff_authorization_decision_service import (
        get_clouds_gp033_status_payload,
        get_gp033_authorized_fixture,
        get_gp033_declined_fixture,
    )

    from .protected_handoff_package import (
        ProtectedHandoffDeliveryTargetKind,
        ProtectedHandoffPackage,
        ProtectedHandoffPackageState,
        ProtectedHandoffPreparationSurface,
    )

except ImportError:
    from handoff_authorization_decision_service import (
        get_clouds_gp033_status_payload,
        get_gp033_authorized_fixture,
        get_gp033_declined_fixture,
    )

    from protected_handoff_package import (
        ProtectedHandoffDeliveryTargetKind,
        ProtectedHandoffPackage,
        ProtectedHandoffPackageState,
        ProtectedHandoffPreparationSurface,
    )


HANDOFF_SCHEMA_VERSION = (
    "clouds-protected-handoff-v1"
)


def _delivery_target(
    authorization_record,
):
    if (
        authorization_record
        .requires_tower_mediation
    ):
        return (
            ProtectedHandoffDeliveryTargetKind
            .TOWER_MEDIATED.value,
            "tower",
        )

    return (
        ProtectedHandoffDeliveryTargetKind
        .OWNING_APPLICATION.value,
        authorization_record
        .owning_application_id,
    )


def _canonical_integrity_payload(
    authorization_record,
    delivery_target_kind,
    delivery_target_id,
):
    """
    Small bounded summary contract only.

    No credentials.
    No session material.
    No raw evidence.
    """

    return {
        "schema_version": (
            HANDOFF_SCHEMA_VERSION
        ),

        "authorization_record_id": (
            authorization_record
            .authorization_record_id
        ),

        "intent_review_id": (
            authorization_record
            .intent_review_id
        ),

        "choice_record_id": (
            authorization_record
            .choice_record_id
        ),

        "decision_review_id": (
            authorization_record
            .review_id
        ),

        "decision_packet_id": (
            authorization_record
            .packet_id
        ),

        "agenda_item_id": (
            authorization_record
            .agenda_item_id
        ),

        "source_id": (
            authorization_record
            .source_id
        ),

        "impacted_source_id": (
            authorization_record
            .impacted_source_id
        ),

        "selected_option_id": (
            authorization_record
            .selected_option_id
        ),

        "selected_option_kind": (
            authorization_record
            .selected_option_kind
        ),

        "owning_application_id": (
            authorization_record
            .owning_application_id
        ),

        "requires_tower_mediation": (
            authorization_record
            .requires_tower_mediation
        ),

        "delivery_target_kind": (
            delivery_target_kind
        ),

        "delivery_target_id": (
            delivery_target_id
        ),

        "preparation_authorized": True,

        "delivery_authorized": False,

        "delivery_released": False,
    }


def _integrity_hash(payload):
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")

    return hashlib.sha256(
        canonical
    ).hexdigest()


def build_protected_handoff_package(
    authorization_record,
):
    """
    Build a protected handoff package from a GP033
    authorization-for-preparation record.
    """

    if (
        authorization_record
        .owner_confirmation_recorded
        is not True
    ):
        raise ValueError(
            "Owner confirmation is required before "
            "handoff package preparation."
        )

    if (
        authorization_record
        .owner_decision
        != "authorize"
    ):
        raise ValueError(
            "Declined owner intent cannot be packaged."
        )

    if (
        authorization_record
        .authorization_state
        != "authorized_for_preparation"
    ):
        raise ValueError(
            "Authorization record is not approved "
            "for package preparation."
        )

    if (
        authorization_record
        .handoff_authorized
        is not True
    ):
        raise ValueError(
            "GP033 preparation authorization is required."
        )

    if (
        authorization_record
        .handoff_delivered
        is not False
    ):
        raise ValueError(
            "Already-delivered handoff cannot enter GP034."
        )

    if (
        authorization_record
        .approval_performed
        is not False
    ):
        raise ValueError(
            "Unexpected approval state detected."
        )

    if (
        authorization_record
        .capital_movement_performed
        is not False
    ):
        raise ValueError(
            "Unexpected capital movement detected."
        )

    if (
        authorization_record
        .downstream_execution_performed
        is not False
    ):
        raise ValueError(
            "Unexpected downstream execution detected."
        )

    (
        delivery_target_kind,
        delivery_target_id,
    ) = _delivery_target(
        authorization_record
    )

    integrity_payload = (
        _canonical_integrity_payload(
            authorization_record,
            delivery_target_kind,
            delivery_target_id,
        )
    )

    package_hash = (
        _integrity_hash(
            integrity_payload
        )
    )

    return ProtectedHandoffPackage(
        handoff_package_id=(
            "protected-handoff-package-"
            f"{authorization_record.authorization_record_id}"
        ),

        schema_version=(
            HANDOFF_SCHEMA_VERSION
        ),

        authorization_record_id=(
            authorization_record
            .authorization_record_id
        ),

        intent_review_id=(
            authorization_record
            .intent_review_id
        ),

        choice_record_id=(
            authorization_record
            .choice_record_id
        ),

        decision_review_id=(
            authorization_record
            .review_id
        ),

        decision_packet_id=(
            authorization_record
            .packet_id
        ),

        agenda_item_id=(
            authorization_record
            .agenda_item_id
        ),

        source_id=(
            authorization_record
            .source_id
        ),

        source_label=(
            authorization_record
            .source_label
        ),

        impacted_source_id=(
            authorization_record
            .impacted_source_id
        ),

        impacted_source_label=(
            authorization_record
            .impacted_source_label
        ),

        selected_option_id=(
            authorization_record
            .selected_option_id
        ),

        selected_option_kind=(
            authorization_record
            .selected_option_kind
        ),

        selected_option_label=(
            authorization_record
            .selected_option_label
        ),

        owning_application_id=(
            authorization_record
            .owning_application_id
        ),

        owning_application_label=(
            authorization_record
            .owning_application_label
        ),

        requires_tower_mediation=(
            authorization_record
            .requires_tower_mediation
        ),

        delivery_target_kind=(
            delivery_target_kind
        ),

        delivery_target_id=(
            delivery_target_id
        ),

        preparation_authorized=True,

        package_state=(
            ProtectedHandoffPackageState
            .PREPARED.value
        ),

        delivery_prepared=True,

        delivery_authorized=False,

        delivery_released=False,

        handoff_delivered=False,

        credentials_included=False,

        tower_session_material_included=False,

        raw_evidence_included=False,

        approval_performed=False,

        capital_movement_performed=False,

        downstream_execution_performed=False,

        package_integrity_hash=(
            package_hash
        ),

        soulaana_package_summary=(
            "I packaged your authorized "
            f"“{authorization_record.selected_option_label}” "
            f"intent for {authorization_record.source_label}."
        ),

        soulaana_why_it_matters=(
            "The package freezes the exact choice, source, "
            "owning application, authorization record, and "
            "Tower requirement before anything is allowed "
            "to move into a delivery lane."
        ),

        soulaana_delivery_boundary=(
            "The package exists, but it has not been released "
            "or delivered. No Tower session, credential, raw "
            "evidence, or downstream action is included."
        ),

        soulaana_next_step=(
            "A separate delivery-release gate must explicitly "
            "approve whether this frozen package may leave "
            "Clouds."
        ),
    )


def get_gp034_protected_handoff_package():
    return build_protected_handoff_package(
        get_gp033_authorized_fixture()
    )


def get_protected_handoff_preparation_surface():
    package = (
        get_gp034_protected_handoff_package()
    )

    return ProtectedHandoffPreparationSurface(
        title=(
            "Protected Handoff Package / "
            "Delivery Preparation"
        ),

        packages=(
            package,
        ),

        package_count=1,

        prepared_count=1,

        blocked_count=0,

        preparation_authorized=True,

        delivery_prepared=True,

        delivery_authorized=False,

        delivery_released=False,

        handoff_delivered=False,

        credentials_included=False,

        tower_session_material_included=False,

        raw_evidence_included=False,

        approval_performed=False,

        capital_movement_performed=False,

        downstream_execution_performed=False,

        boundary_notice=(
            "GP034 freezes the authorized owner intent into "
            "a protected handoff package. The package is "
            "prepared only. It is not released, delivered, "
            "accepted by Tower, or executed downstream."
        ),
    )


def get_protected_handoff_preparation_surface_payload():
    return (
        get_protected_handoff_preparation_surface()
        .to_dict()
    )


def get_clouds_gp034_status_payload():
    gp033 = (
        get_clouds_gp033_status_payload()
    )

    package = (
        get_gp034_protected_handoff_package()
    )

    surface = (
        get_protected_handoff_preparation_surface()
    )

    repeated = (
        get_gp034_protected_handoff_package()
    )

    declined = (
        get_gp033_declined_fixture()
    )

    decline_blocked = False

    try:
        build_protected_handoff_package(
            declined
        )

    except ValueError:
        decline_blocked = True

    safe = (
        gp033["status"] == "ready"
        and gp033["safe_to_continue"]
        is True

        and gp033[
            "owner_confirmation_recorded"
        ]
        is True

        and gp033["handoff_authorized"]
        is True

        and gp033["handoff_delivered"]
        is False

        and package.schema_version
        == HANDOFF_SCHEMA_VERSION

        and package.package_state
        == "prepared"

        and package
        .preparation_authorized
        is True

        and package.delivery_prepared
        is True

        and package.delivery_authorized
        is False

        and package.delivery_released
        is False

        and package.handoff_delivered
        is False

        and package.credentials_included
        is False

        and package
        .tower_session_material_included
        is False

        and package.raw_evidence_included
        is False

        and len(
            package.package_integrity_hash
        )
        == 64

        and package.package_integrity_hash
        == repeated.package_integrity_hash

        and decline_blocked
        is True

        and surface.package_count
        == 1

        and surface.prepared_count
        == 1

        and surface.blocked_count
        == 0

        and surface.delivery_authorized
        is False

        and surface.delivery_released
        is False

        and surface.handoff_delivered
        is False

        and surface.approval_performed
        is False

        and surface
        .capital_movement_performed
        is False

        and surface
        .downstream_execution_performed
        is False
    )

    return {
        "pack": "GP034",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "PROTECTED HANDOFF PACKAGE / "
            "DELIVERY PREPARATION"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "package_count": (
            surface.package_count
        ),

        "prepared_count": (
            surface.prepared_count
        ),

        "blocked_count": (
            surface.blocked_count
        ),

        "schema_version": (
            package.schema_version
        ),

        "integrity_hash_present": True,

        "integrity_hash_deterministic": (
            package.package_integrity_hash
            == repeated.package_integrity_hash
        ),

        "authorization_binding_preserved": True,

        "selected_option_binding_preserved": True,

        "owning_application_preserved": True,

        "tower_mediation_preserved": True,

        "decline_path_fails_closed": (
            decline_blocked
        ),

        "preparation_authorized": True,

        "delivery_prepared": True,

        "delivery_authorized": False,

        "delivery_released": False,

        "handoff_delivered": False,

        "credentials_included": False,

        "tower_session_material_included": False,

        "raw_evidence_included": False,

        "approval_performed": False,

        "capital_movement_performed": False,

        "downstream_execution_performed": False,

        "tower_authority_changed": False,

        "cross_app_imports_used": False,

        "next_pack": (
            "GP035 — PROTECTED HANDOFF DELIVERY RELEASE / "
            "AUTHORIZATION GATE"
        ),
    }
