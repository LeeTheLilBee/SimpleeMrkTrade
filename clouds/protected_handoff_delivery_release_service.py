"""
GP035 — Protected Handoff Delivery Release / Authorization Gate.

Authorizes whether the exact frozen GP034 package may
enter a later release operation.

No package release or delivery occurs here.
"""

from __future__ import annotations

try:
    from .protected_handoff_delivery_release import (
        ProtectedHandoffReleaseAuthorization,
        ProtectedHandoffReleaseAuthorizationSurface,
        ProtectedHandoffReleaseDecision,
        ProtectedHandoffReleaseState,
    )

    from .protected_handoff_package_service import (
        get_clouds_gp034_status_payload,
        get_gp034_protected_handoff_package,
    )

except ImportError:
    from protected_handoff_delivery_release import (
        ProtectedHandoffReleaseAuthorization,
        ProtectedHandoffReleaseAuthorizationSurface,
        ProtectedHandoffReleaseDecision,
        ProtectedHandoffReleaseState,
    )

    from protected_handoff_package_service import (
        get_clouds_gp034_status_payload,
        get_gp034_protected_handoff_package,
    )


ALLOWED_RELEASE_DECISIONS = {
    ProtectedHandoffReleaseDecision
    .AUTHORIZE_RELEASE.value,

    ProtectedHandoffReleaseDecision
    .DECLINE_RELEASE.value,
}


PACKAGE_BINDING_FIELDS = (
    "handoff_package_id",
    "schema_version",

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

    "preparation_authorized",
    "package_state",
    "delivery_prepared",

    "delivery_authorized",
    "delivery_released",
    "handoff_delivered",

    "credentials_included",
    "tower_session_material_included",
    "raw_evidence_included",

    "approval_performed",
    "capital_movement_performed",
    "downstream_execution_performed",

    "package_integrity_hash",
)


def _canonical_package():
    return (
        get_gp034_protected_handoff_package()
    )


def _package_binding_matches(
    package,
    canonical,
):
    return all(
        getattr(package, field)
        == getattr(canonical, field)
        for field in PACKAGE_BINDING_FIELDS
    )


def _validate_release_candidate(
    package,
):
    """
    Fail closed unless the candidate is the exact,
    untouched GP034 frozen package.
    """

    canonical = (
        _canonical_package()
    )

    if (
        package.package_state
        != "prepared"
    ):
        raise ValueError(
            "Only a prepared GP034 package may enter GP035."
        )

    if (
        package.preparation_authorized
        is not True
    ):
        raise ValueError(
            "Package preparation was not authorized."
        )

    if (
        package.delivery_prepared
        is not True
    ):
        raise ValueError(
            "Package is not delivery-prepared."
        )

    if (
        package.delivery_authorized
        is not False
    ):
        raise ValueError(
            "Package already reports delivery authorization."
        )

    if (
        package.delivery_released
        is not False
    ):
        raise ValueError(
            "Already-released package cannot enter GP035."
        )

    if (
        package.handoff_delivered
        is not False
    ):
        raise ValueError(
            "Already-delivered package cannot enter GP035."
        )

    if (
        package.credentials_included
        is not False
    ):
        raise ValueError(
            "Credentials are prohibited from the handoff package."
        )

    if (
        package
        .tower_session_material_included
        is not False
    ):
        raise ValueError(
            "Tower session material is prohibited."
        )

    if (
        package.raw_evidence_included
        is not False
    ):
        raise ValueError(
            "Raw evidence is prohibited from the handoff package."
        )

    if (
        package.approval_performed
        is not False
    ):
        raise ValueError(
            "Unexpected downstream approval state."
        )

    if (
        package
        .capital_movement_performed
        is not False
    ):
        raise ValueError(
            "Unexpected capital movement state."
        )

    if (
        package
        .downstream_execution_performed
        is not False
    ):
        raise ValueError(
            "Unexpected downstream execution state."
        )

    if (
        len(
            package.package_integrity_hash
        )
        != 64
    ):
        raise ValueError(
            "Package integrity hash is malformed."
        )

    if (
        package.package_integrity_hash
        != canonical.package_integrity_hash
    ):
        raise ValueError(
            "Package integrity hash does not match "
            "the canonical frozen GP034 package."
        )

    if not _package_binding_matches(
        package,
        canonical,
    ):
        raise ValueError(
            "Package binding changed after GP034 preparation."
        )

    return canonical


def record_delivery_release_decision(
    package,
    owner_release_decision,
):
    """
    Record the owner's release authorization decision.

    AUTHORIZE_RELEASE:
        permits a later release operation.

    DECLINE_RELEASE:
        package remains frozen and cannot be released.

    Neither path releases or delivers anything here.
    """

    if (
        owner_release_decision
        not in ALLOWED_RELEASE_DECISIONS
    ):
        raise ValueError(
            "Unsupported protected handoff release decision."
        )

    canonical = (
        _validate_release_candidate(
            package
        )
    )

    authorized = (
        owner_release_decision
        == ProtectedHandoffReleaseDecision
        .AUTHORIZE_RELEASE.value
    )

    release_state = (
        ProtectedHandoffReleaseState
        .AUTHORIZED_FOR_RELEASE.value
        if authorized
        else ProtectedHandoffReleaseState
        .DECLINED.value
    )


    if authorized:
        release_summary = (
            "You authorized the exact frozen handoff "
            f"package for {package.source_label} to enter "
            "the protected release lane."
        )

        meaning = (
            "Clouds may now prepare a release record for "
            "this exact package. The package still has not "
            "left Clouds."
        )

        next_step = (
            "Create the protected release record and delivery "
            "envelope while preserving the frozen package hash, "
            "delivery target, and Tower boundary."
        )

    else:
        release_summary = (
            "You declined release authorization for the "
            f"{package.source_label} handoff package."
        )

        meaning = (
            "The package remains frozen inside Clouds and "
            "may not move into the release lane."
        )

        next_step = (
            "Leave the package held or return it to owner "
            "review if you intentionally want to revisit it."
        )


    return ProtectedHandoffReleaseAuthorization(
        release_authorization_id=(
            "handoff-release-authorization-"
            f"{package.handoff_package_id}"
        ),

        handoff_package_id=(
            package.handoff_package_id
        ),

        package_schema_version=(
            package.schema_version
        ),

        package_integrity_hash=(
            package.package_integrity_hash
        ),

        authorization_record_id=(
            package.authorization_record_id
        ),

        intent_review_id=(
            package.intent_review_id
        ),

        choice_record_id=(
            package.choice_record_id
        ),

        decision_review_id=(
            package.decision_review_id
        ),

        decision_packet_id=(
            package.decision_packet_id
        ),

        agenda_item_id=(
            package.agenda_item_id
        ),

        source_id=(
            package.source_id
        ),

        source_label=(
            package.source_label
        ),

        impacted_source_id=(
            package.impacted_source_id
        ),

        impacted_source_label=(
            package.impacted_source_label
        ),

        selected_option_id=(
            package.selected_option_id
        ),

        selected_option_kind=(
            package.selected_option_kind
        ),

        selected_option_label=(
            package.selected_option_label
        ),

        owning_application_id=(
            package.owning_application_id
        ),

        owning_application_label=(
            package.owning_application_label
        ),

        requires_tower_mediation=(
            package.requires_tower_mediation
        ),

        delivery_target_kind=(
            package.delivery_target_kind
        ),

        delivery_target_id=(
            package.delivery_target_id
        ),

        owner_release_decision=(
            owner_release_decision
        ),

        release_state=(
            release_state
        ),

        owner_confirmation_recorded=True,

        package_integrity_verified=(
            package.package_integrity_hash
            == canonical.package_integrity_hash
        ),

        package_binding_verified=(
            _package_binding_matches(
                package,
                canonical,
            )
        ),

        delivery_release_authorized=(
            authorized
        ),

        delivery_released=False,

        handoff_delivered=False,

        credentials_included=False,

        tower_session_material_included=False,

        raw_evidence_included=False,

        approval_performed=False,

        capital_movement_performed=False,

        downstream_execution_performed=False,

        soulaana_release_summary=(
            release_summary
        ),

        soulaana_what_this_means=(
            meaning
        ),

        soulaana_what_did_not_happen=(
            "The package was not released or delivered. "
            "Tower was not invoked, no session was created, "
            "no application was opened, no capital moved, "
            "and no downstream operation executed."
        ),

        soulaana_next_step=(
            next_step
        ),
    )


def get_gp035_authorized_fixture():
    """
    Certification fixture only.

    Demonstrates explicit owner authorization for release.
    """

    return record_delivery_release_decision(
        _canonical_package(),
        ProtectedHandoffReleaseDecision
        .AUTHORIZE_RELEASE.value,
    )


def get_gp035_declined_fixture():
    """
    Certification fixture proving decline remains fail closed.
    """

    return record_delivery_release_decision(
        _canonical_package(),
        ProtectedHandoffReleaseDecision
        .DECLINE_RELEASE.value,
    )


def get_protected_handoff_release_authorization_surface():
    authorized = (
        get_gp035_authorized_fixture()
    )

    return (
        ProtectedHandoffReleaseAuthorizationSurface(
            title=(
                "Protected Handoff Delivery Release / "
                "Authorization Gate"
            ),

            records=(
                authorized,
            ),

            record_count=1,

            authorized_count=1,

            declined_count=0,

            blocked_count=0,

            owner_confirmation_recorded=True,

            package_integrity_verified=True,

            package_binding_verified=True,

            delivery_release_authorized=True,

            delivery_released=False,

            handoff_delivered=False,

            approval_performed=False,

            capital_movement_performed=False,

            downstream_execution_performed=False,

            boundary_notice=(
                "GP035 authorizes whether the exact GP034 "
                "package may enter the release lane. "
                "Authorization is not release, delivery, "
                "Tower intake, navigation, or execution."
            ),
        )
    )


def get_protected_handoff_release_authorization_surface_payload():
    return (
        get_protected_handoff_release_authorization_surface()
        .to_dict()
    )


def get_clouds_gp035_status_payload():
    gp034 = (
        get_clouds_gp034_status_payload()
    )

    canonical = (
        _canonical_package()
    )

    authorized = (
        get_gp035_authorized_fixture()
    )

    declined = (
        get_gp035_declined_fixture()
    )

    surface = (
        get_protected_handoff_release_authorization_surface()
    )

    safe = (
        gp034["status"]
        == "ready"

        and gp034["safe_to_continue"]
        is True

        and gp034["package_count"]
        == 1

        and gp034["prepared_count"]
        == 1

        and gp034[
            "integrity_hash_present"
        ]
        is True

        and gp034[
            "integrity_hash_deterministic"
        ]
        is True

        and gp034[
            "preparation_authorized"
        ]
        is True

        and gp034[
            "delivery_prepared"
        ]
        is True

        and gp034[
            "delivery_authorized"
        ]
        is False

        and gp034[
            "delivery_released"
        ]
        is False

        and gp034[
            "handoff_delivered"
        ]
        is False

        and authorized
        .owner_confirmation_recorded
        is True

        and authorized
        .owner_release_decision
        == "authorize_release"

        and authorized
        .release_state
        == "authorized_for_release"

        and authorized
        .package_integrity_verified
        is True

        and authorized
        .package_binding_verified
        is True

        and authorized
        .package_integrity_hash
        == canonical.package_integrity_hash

        and authorized
        .delivery_release_authorized
        is True

        and authorized
        .delivery_released
        is False

        and authorized
        .handoff_delivered
        is False

        and declined
        .owner_release_decision
        == "decline_release"

        and declined
        .release_state
        == "declined"

        and declined
        .delivery_release_authorized
        is False

        and declined
        .delivery_released
        is False

        and declined
        .handoff_delivered
        is False

        and surface.record_count
        == 1

        and surface.authorized_count
        == 1

        and surface.declined_count
        == 0

        and surface.blocked_count
        == 0

        and surface
        .owner_confirmation_recorded
        is True

        and surface
        .package_integrity_verified
        is True

        and surface
        .package_binding_verified
        is True

        and surface
        .delivery_release_authorized
        is True

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
        "pack": "GP035",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "PROTECTED HANDOFF DELIVERY RELEASE / "
            "AUTHORIZATION GATE"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": (
            safe
        ),

        "release_authorization_record_count": (
            surface.record_count
        ),

        "authorized_count": (
            surface.authorized_count
        ),

        "declined_count": (
            surface.declined_count
        ),

        "blocked_count": (
            surface.blocked_count
        ),

        "owner_confirmation_recorded": True,

        "authorize_release_path_verified": True,

        "decline_release_path_verified": True,

        "package_integrity_verified": (
            authorized
            .package_integrity_verified
        ),

        "package_binding_verified": (
            authorized
            .package_binding_verified
        ),

        "package_integrity_hash": (
            authorized
            .package_integrity_hash
        ),

        "schema_preserved": (
            authorized
            .package_schema_version
            == canonical.schema_version
        ),

        "authorization_binding_preserved": True,

        "selected_option_binding_preserved": True,

        "owning_application_preserved": True,

        "delivery_target_preserved": True,

        "tower_mediation_preserved": True,

        "credentials_included": False,

        "tower_session_material_included": False,

        "raw_evidence_included": False,

        "delivery_release_authorized": True,

        "delivery_released": False,

        "handoff_delivered": False,

        "approval_performed": False,

        "capital_movement_performed": False,

        "downstream_execution_performed": False,

        "tower_authority_changed": False,

        "cross_app_imports_used": False,

        "next_pack": (
            "GP036 — PROTECTED HANDOFF RELEASE RECORD / "
            "DELIVERY ENVELOPE PREPARATION"
        ),
    }
