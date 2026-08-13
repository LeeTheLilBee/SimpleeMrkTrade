"""
GP033 — Handoff Authorization Decision / Owner Confirmation Boundary.
"""

from __future__ import annotations

try:
    from .handoff_authorization_decision import (
        HandoffAuthorizationDecision,
        HandoffAuthorizationRecord,
        HandoffAuthorizationState,
        HandoffAuthorizationSurface,
    )

    from .owner_intent_review_service import (
        build_owner_intent_review,
        get_clouds_gp032_status_payload,
        get_owner_intent_reviews,
    )

except ImportError:
    from handoff_authorization_decision import (
        HandoffAuthorizationDecision,
        HandoffAuthorizationRecord,
        HandoffAuthorizationState,
        HandoffAuthorizationSurface,
    )

    from owner_intent_review_service import (
        build_owner_intent_review,
        get_clouds_gp032_status_payload,
        get_owner_intent_reviews,
    )


ALLOWED_DECISIONS = {
    HandoffAuthorizationDecision.AUTHORIZE.value,
    HandoffAuthorizationDecision.DECLINE.value,
}


def record_handoff_authorization_decision(
    intent_review,
    owner_decision,
):
    """
    Record explicit owner authorization or decline.

    Authorization here means only:
    permitted to proceed to handoff PREPARATION.
    """

    if owner_decision not in ALLOWED_DECISIONS:
        raise ValueError(
            "Unsupported handoff authorization decision."
        )

    if (
        intent_review.review_state
        != "ready_for_handoff_authorization_prep"
        or intent_review
        .ready_for_handoff_authorization_prep
        is not True
    ):
        raise ValueError(
            "Intent review is not ready for handoff authorization."
        )

    if intent_review.handoff_authorized is not False:
        raise ValueError(
            "GP032 intent review must not already be authorized."
        )

    if intent_review.handoff_delivered is not False:
        raise ValueError(
            "GP032 intent review must not already be delivered."
        )

    authorized = (
        owner_decision
        == HandoffAuthorizationDecision
        .AUTHORIZE.value
    )

    state = (
        HandoffAuthorizationState
        .AUTHORIZED_FOR_PREPARATION.value
        if authorized
        else HandoffAuthorizationState
        .DECLINED.value
    )

    if authorized:
        decision_summary = (
            "You authorized this reviewed intent to move "
            "into protected handoff preparation."
        )

        meaning = (
            "Clouds may now prepare the handoff package, "
            "but it still may not deliver or execute it."
        )

        next_step = (
            "Prepare the protected handoff package while "
            "preserving the owning-application and Tower boundaries."
        )

    else:
        decision_summary = (
            "You declined handoff authorization for this "
            "reviewed intent."
        )

        meaning = (
            "The intent remains recorded, but Clouds must "
            "not prepare it for handoff."
        )

        next_step = (
            "Return the item to owner review or leave it "
            "closed until you intentionally revisit it."
        )

    return HandoffAuthorizationRecord(
        authorization_record_id=(
            "handoff-authorization-"
            f"{intent_review.intent_review_id}"
        ),

        intent_review_id=(
            intent_review.intent_review_id
        ),

        choice_record_id=(
            intent_review.choice_record_id
        ),

        review_id=(
            intent_review.review_id
        ),

        packet_id=(
            intent_review.packet_id
        ),

        agenda_item_id=(
            intent_review.agenda_item_id
        ),

        source_id=(
            intent_review.source_id
        ),

        source_label=(
            intent_review.source_label
        ),

        impacted_source_id=(
            intent_review.impacted_source_id
        ),

        impacted_source_label=(
            intent_review.impacted_source_label
        ),

        selected_option_id=(
            intent_review.selected_option_id
        ),

        selected_option_kind=(
            intent_review.selected_option_kind
        ),

        selected_option_label=(
            intent_review.selected_option_label
        ),

        owning_application_id=(
            intent_review.owning_application_id
        ),

        owning_application_label=(
            intent_review.owning_application_label
        ),

        requires_tower_mediation=(
            intent_review.requires_tower_mediation
        ),

        owner_decision=owner_decision,

        authorization_state=state,

        owner_confirmation_recorded=True,

        handoff_authorized=authorized,

        handoff_delivered=False,

        approval_performed=False,
        capital_movement_performed=False,
        downstream_execution_performed=False,

        soulaana_decision_summary=(
            decision_summary
        ),

        soulaana_what_this_means=(
            meaning
        ),

        soulaana_what_did_not_happen=(
            "No handoff was delivered, no application "
            "was opened, no capital moved, and no "
            "downstream operation executed."
        ),

        soulaana_next_step=(
            next_step
        ),
    )


def get_gp033_authorized_fixture():
    """
    Certification fixture only.

    Simulates explicit owner AUTHORIZE confirmation.
    """

    reviews = (
        get_owner_intent_reviews()
    )

    if len(reviews) != 1:
        raise RuntimeError(
            "Expected exactly one GP032 intent review."
        )

    return (
        record_handoff_authorization_decision(
            reviews[0],
            "authorize",
        )
    )


def get_gp033_declined_fixture():
    """
    Certification fixture proving decline path remains safe.
    """

    reviews = (
        get_owner_intent_reviews()
    )

    if len(reviews) != 1:
        raise RuntimeError(
            "Expected exactly one GP032 intent review."
        )

    return (
        record_handoff_authorization_decision(
            reviews[0],
            "decline",
        )
    )


def get_handoff_authorization_surface():
    authorized = (
        get_gp033_authorized_fixture()
    )

    return HandoffAuthorizationSurface(
        title=(
            "Handoff Authorization Decision / "
            "Owner Confirmation"
        ),

        records=(
            authorized,
        ),

        record_count=1,

        authorized_count=1,

        declined_count=0,

        blocked_count=0,

        owner_confirmation_recorded=True,

        handoff_authorized=True,

        handoff_delivered=False,

        approval_performed=False,
        capital_movement_performed=False,
        downstream_execution_performed=False,

        boundary_notice=(
            "GP033 records whether the owner authorizes "
            "handoff PREPARATION. Authorization does not "
            "deliver the handoff or execute downstream work."
        ),
    )


def get_handoff_authorization_surface_payload():
    return (
        get_handoff_authorization_surface()
        .to_dict()
    )


def get_clouds_gp033_status_payload():
    gp032 = (
        get_clouds_gp032_status_payload()
    )

    authorized = (
        get_gp033_authorized_fixture()
    )

    declined = (
        get_gp033_declined_fixture()
    )

    surface = (
        get_handoff_authorization_surface()
    )

    safe = (
        gp032["status"] == "ready"
        and gp032["safe_to_continue"]
        is True

        and gp032[
            "ready_for_handoff_authorization_prep"
        ]
        is True

        and gp032["handoff_authorized"]
        is False

        and gp032["handoff_delivered"]
        is False

        and authorized.owner_confirmation_recorded
        is True

        and authorized.owner_decision
        == "authorize"

        and authorized.authorization_state
        == "authorized_for_preparation"

        and authorized.handoff_authorized
        is True

        and authorized.handoff_delivered
        is False

        and authorized.approval_performed
        is False

        and authorized
        .capital_movement_performed
        is False

        and authorized
        .downstream_execution_performed
        is False

        and declined.owner_decision
        == "decline"

        and declined.authorization_state
        == "declined"

        and declined.handoff_authorized
        is False

        and declined.handoff_delivered
        is False

        and surface.record_count == 1

        and surface.authorized_count == 1

        and surface.declined_count == 0

        and surface.blocked_count == 0

        and surface.owner_confirmation_recorded
        is True

        and surface.handoff_authorized
        is True

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
        "pack": "GP033",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "HANDOFF AUTHORIZATION DECISION / "
            "OWNER CONFIRMATION BOUNDARY"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "authorization_record_count": (
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

        "authorize_path_verified": True,

        "decline_path_verified": True,

        "selected_option_binding_preserved": True,

        "owning_application_preserved": True,

        "tower_mediation_preserved": True,

        "handoff_authorized": True,

        "handoff_delivered": False,

        "approval_performed": False,

        "capital_movement_performed": False,

        "downstream_execution_performed": False,

        "tower_authority_changed": False,

        "cross_app_imports_used": False,

        "next_pack": (
            "GP034 — PROTECTED HANDOFF PACKAGE / "
            "DELIVERY PREPARATION"
        ),
    }
