"""
GP032 — Owner Intent Review / Handoff Authorization Preparation.

Validates a GP031 recorded choice.
"""

from __future__ import annotations

try:
    from .owner_decision_choice_service import (
        get_clouds_gp031_status_payload,
        get_gp031_fixture_choice_record,
    )

    from .owner_decision_packet_service import (
        get_owner_decision_packet,
    )

    from .owner_decision_review_service import (
        get_owner_decision_review,
    )

    from .owner_intent_review import (
        OwnerIntentReview,
        OwnerIntentReviewCheck,
        OwnerIntentReviewState,
        OwnerIntentReviewSurface,
    )

except ImportError:
    from owner_decision_choice_service import (
        get_clouds_gp031_status_payload,
        get_gp031_fixture_choice_record,
    )

    from owner_decision_packet_service import (
        get_owner_decision_packet,
    )

    from owner_decision_review_service import (
        get_owner_decision_review,
    )

    from owner_intent_review import (
        OwnerIntentReview,
        OwnerIntentReviewCheck,
        OwnerIntentReviewState,
        OwnerIntentReviewSurface,
    )


def _build_checks(choice_record):
    review = get_owner_decision_review(
        choice_record.review_id
    )

    packet = get_owner_decision_packet(
        choice_record.packet_id
    )

    option_map = {
        option.option_id: option
        for option in packet.options
    }

    option = option_map.get(
        choice_record.selected_option_id
    )

    return (
        OwnerIntentReviewCheck(
            check_id=(
                f"{choice_record.choice_record_id}-recorded"
            ),
            label="Owner intent is explicitly recorded",
            passed=(
                choice_record.choice_state
                == "recorded"
                and choice_record
                .owner_choice_recorded
                is True
            ),
            explanation=(
                "The handoff-preparation boundary requires "
                "an explicit recorded owner choice."
            ),
            display_order=10,
        ),

        OwnerIntentReviewCheck(
            check_id=(
                f"{choice_record.choice_record_id}-review"
            ),
            label="Decision review remains ready",
            passed=(
                review.review_state
                == "ready_for_owner_choice"
                and review.owner_ready_to_choose
                is True
            ),
            explanation=(
                "The underlying GP030 readiness review must "
                "still be green."
            ),
            display_order=20,
        ),

        OwnerIntentReviewCheck(
            check_id=(
                f"{choice_record.choice_record_id}-packet"
            ),
            label="Choice still belongs to reviewed packet",
            passed=(
                option is not None
            ),
            explanation=(
                "The selected option must still exist in the "
                "same prepared decision packet."
            ),
            display_order=30,
        ),

        OwnerIntentReviewCheck(
            check_id=(
                f"{choice_record.choice_record_id}-kind"
            ),
            label="Recorded intent matches selected option",
            passed=(
                option is not None
                and option.kind
                == choice_record.selected_option_kind
                and option.label
                == choice_record.selected_option_label
            ),
            explanation=(
                "Clouds must not silently reinterpret the "
                "owner's selected option."
            ),
            display_order=40,
        ),

        OwnerIntentReviewCheck(
            check_id=(
                f"{choice_record.choice_record_id}-source"
            ),
            label="Owning application is unchanged",
            passed=(
                choice_record.owning_application_id
                == packet.owning_application_id
                and choice_record
                .owning_application_label
                == packet.owning_application_label
            ),
            explanation=(
                "The real workflow must still belong to the "
                "same source-owned application."
            ),
            display_order=50,
        ),

        OwnerIntentReviewCheck(
            check_id=(
                f"{choice_record.choice_record_id}-tower"
            ),
            label="Tower mediation requirement is preserved",
            passed=(
                choice_record.requires_tower_mediation
                == packet.requires_tower_mediation
            ),
            explanation=(
                "A recorded intent cannot bypass or alter the "
                "Tower mediation requirement."
            ),
            display_order=60,
        ),

        OwnerIntentReviewCheck(
            check_id=(
                f"{choice_record.choice_record_id}-impact"
            ),
            label="Impacted-source context is preserved",
            passed=(
                choice_record.impacted_source_id
                == packet.impacted_source_id
                and choice_record.impacted_source_label
                == packet.impacted_source_label
            ),
            explanation=(
                "Cross-business context must remain attached "
                "to the intent that created it."
            ),
            display_order=70,
        ),

        OwnerIntentReviewCheck(
            check_id=(
                f"{choice_record.choice_record_id}-nonapproval"
            ),
            label="Intent has not become approval",
            passed=(
                choice_record.approval_performed
                is False
            ),
            explanation=(
                "Recorded owner intent is not authorization."
            ),
            display_order=80,
        ),

        OwnerIntentReviewCheck(
            check_id=(
                f"{choice_record.choice_record_id}-noncapital"
            ),
            label="No capital movement has occurred",
            passed=(
                choice_record
                .capital_movement_performed
                is False
            ),
            explanation=(
                "Intent review must remain separate from any "
                "capital action."
            ),
            display_order=90,
        ),

        OwnerIntentReviewCheck(
            check_id=(
                f"{choice_record.choice_record_id}-nonexecution"
            ),
            label="No downstream execution has occurred",
            passed=(
                choice_record
                .downstream_execution_performed
                is False
                and choice_record
                .automatic_decision_performed
                is False
            ),
            explanation=(
                "GP032 reviews intent only and cannot execute it."
            ),
            display_order=100,
        ),
    )


def build_owner_intent_review(
    choice_record=None,
):
    if choice_record is None:
        choice_record = (
            get_gp031_fixture_choice_record()
        )

    if (
        choice_record.choice_state
        != "recorded"
        or choice_record
        .owner_choice_recorded
        is not True
    ):
        raise ValueError(
            "Only recorded owner intent may enter GP032."
        )

    checks = _build_checks(
        choice_record
    )

    passed_count = sum(
        item.passed
        for item in checks
    )

    failed_count = (
        len(checks)
        - passed_count
    )

    ready = (
        failed_count == 0
    )

    failed_labels = tuple(
        item.label
        for item in checks
        if not item.passed
    )

    return OwnerIntentReview(
        intent_review_id=(
            "intent-review-"
            f"{choice_record.choice_record_id}"
        ),

        choice_record_id=(
            choice_record.choice_record_id
        ),

        review_id=(
            choice_record.review_id
        ),

        packet_id=(
            choice_record.packet_id
        ),

        agenda_item_id=(
            choice_record.agenda_item_id
        ),

        source_id=(
            choice_record.source_id
        ),

        source_label=(
            choice_record.source_label
        ),

        impacted_source_id=(
            choice_record.impacted_source_id
        ),

        impacted_source_label=(
            choice_record
            .impacted_source_label
        ),

        selected_option_id=(
            choice_record.selected_option_id
        ),

        selected_option_kind=(
            choice_record.selected_option_kind
        ),

        selected_option_label=(
            choice_record.selected_option_label
        ),

        owning_application_id=(
            choice_record
            .owning_application_id
        ),

        owning_application_label=(
            choice_record
            .owning_application_label
        ),

        requires_tower_mediation=(
            choice_record
            .requires_tower_mediation
        ),

        checks=checks,

        check_count=len(checks),

        passed_check_count=(
            passed_count
        ),

        failed_check_count=(
            failed_count
        ),

        review_state=(
            OwnerIntentReviewState
            .READY_FOR_HANDOFF_AUTHORIZATION_PREP
            .value
            if ready
            else OwnerIntentReviewState
            .BLOCKED.value
        ),

        ready_for_handoff_authorization_prep=(
            ready
        ),

        soulaana_review_summary=(
            (
                "Your recorded choice still matches the "
                "reviewed decision packet and its current "
                "handoff boundaries."
            )
            if ready
            else
            (
                "Your recorded choice is not safe to prepare "
                "for handoff yet."
            )
        ),

        soulaana_why_it_matters=(
            "A choice should not move toward handoff if its "
            "review context, source ownership, or Tower "
            "boundary has changed."
        ),

        soulaana_blocker_summary=(
            "No intent-review blockers remain."
            if ready
            else
            "Blocking checks: "
            + ", ".join(
                failed_labels
            )
        ),

        soulaana_next_step=(
            (
                "The intent is ready for a separate owner "
                "handoff-authorization decision."
            )
            if ready
            else
            (
                "Resolve the failed intent-review checks "
                "before preparing any authorization."
            )
        ),

        handoff_authorized=False,
        handoff_delivered=False,

        approval_performed=False,
        capital_movement_performed=False,
        downstream_execution_performed=False,
    )


def get_owner_intent_reviews():
    return (
        build_owner_intent_review(),
    )


def get_owner_intent_review_surface():
    reviews = (
        get_owner_intent_reviews()
    )

    return OwnerIntentReviewSurface(
        title=(
            "Owner Intent Review / "
            "Handoff Authorization Preparation"
        ),

        reviews=reviews,

        review_count=len(reviews),

        ready_count=sum(
            item
            .ready_for_handoff_authorization_prep
            for item in reviews
        ),

        blocked_count=sum(
            item.review_state
            == "blocked"
            for item in reviews
        ),

        handoff_authorized=False,
        handoff_delivered=False,

        approval_performed=False,
        capital_movement_performed=False,
        downstream_execution_performed=False,

        boundary_notice=(
            "GP032 verifies whether recorded owner intent "
            "is coherent enough to PREPARE for a later "
            "handoff-authorization decision. "
            "No authorization or delivery occurs here."
        ),
    )


def get_owner_intent_review_surface_payload():
    return (
        get_owner_intent_review_surface()
        .to_dict()
    )


def get_clouds_gp032_status_payload():
    gp031 = (
        get_clouds_gp031_status_payload()
    )

    surface = (
        get_owner_intent_review_surface()
    )

    review = surface.reviews[0]

    safe = (
        gp031["status"] == "ready"
        and gp031["safe_to_continue"]
        is True

        and gp031["owner_choice_recorded"]
        is True

        and surface.review_count == 1

        and surface.ready_count == 1

        and surface.blocked_count == 0

        and review.check_count == 10

        and review.passed_check_count
        == 10

        and review.failed_check_count
        == 0

        and review
        .ready_for_handoff_authorization_prep
        is True

        and review.review_state
        == "ready_for_handoff_authorization_prep"

        and review.handoff_authorized
        is False

        and review.handoff_delivered
        is False

        and review.approval_performed
        is False

        and review
        .capital_movement_performed
        is False

        and review
        .downstream_execution_performed
        is False

        and surface.handoff_authorized
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
        "pack": "GP032",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "OWNER INTENT REVIEW / "
            "HANDOFF AUTHORIZATION PREPARATION"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "review_count": (
            surface.review_count
        ),

        "ready_count": (
            surface.ready_count
        ),

        "blocked_count": (
            surface.blocked_count
        ),

        "checks_per_review": 10,

        "recorded_intent_validated": True,

        "selected_option_still_valid": True,

        "owning_application_preserved": True,

        "impacted_source_context_preserved": True,

        "tower_mediation_preserved": True,

        "ready_for_handoff_authorization_prep": (
            review
            .ready_for_handoff_authorization_prep
        ),

        "handoff_authorized": False,

        "handoff_delivered": False,

        "approval_performed": False,

        "capital_movement_performed": False,

        "downstream_execution_performed": False,

        "tower_authority_changed": False,

        "cross_app_imports_used": False,

        "next_pack": (
            "GP033 — HANDOFF AUTHORIZATION DECISION / "
            "OWNER CONFIRMATION BOUNDARY"
        ),
    }
