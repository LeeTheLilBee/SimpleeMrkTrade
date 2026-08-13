"""
GP030 — Owner Decision Review / Readiness Gate.

Validates whether GP029 packets are ready for owner choice.
"""

from __future__ import annotations

try:
    from .owner_decision_packet_service import (
        get_clouds_gp029_status_payload,
        get_owner_decision_packet,
        get_owner_decision_packets,
    )

    from .owner_decision_review import (
        DecisionReviewCheck,
        DecisionReviewState,
        OwnerDecisionReview,
        OwnerDecisionReviewSurface,
    )

except ImportError:
    from owner_decision_packet_service import (
        get_clouds_gp029_status_payload,
        get_owner_decision_packet,
        get_owner_decision_packets,
    )

    from owner_decision_review import (
        DecisionReviewCheck,
        DecisionReviewState,
        OwnerDecisionReview,
        OwnerDecisionReviewSurface,
    )


def _build_checks(packet):
    required_evidence = tuple(
        item
        for item in packet.evidence_items
        if item.required_before_decision
    )

    options = packet.options

    return (
        DecisionReviewCheck(
            check_id=(
                f"{packet.packet_id}-packet-state"
            ),
            label="Decision packet ready",
            passed=(
                packet.packet_state
                == "ready_for_owner_review"
            ),
            explanation=(
                "The GP029 packet must be ready for owner review."
            ),
            display_order=10,
        ),

        DecisionReviewCheck(
            check_id=(
                f"{packet.packet_id}-question"
            ),
            label="Decision question is clear",
            passed=bool(
                packet.decision_question
            ),
            explanation=(
                "The owner should know exactly what is being decided."
            ),
            display_order=20,
        ),

        DecisionReviewCheck(
            check_id=(
                f"{packet.packet_id}-options"
            ),
            label="Decision options are present",
            passed=(
                len(options) >= 3
                and all(
                    option.requires_owner_choice
                    is True
                    and option.executes_automatically
                    is False
                    for option in options
                )
            ),
            explanation=(
                "The owner must have non-executing choices to compare."
            ),
            display_order=30,
        ),

        DecisionReviewCheck(
            check_id=(
                f"{packet.packet_id}-consequences"
            ),
            label="Consequences are explained",
            passed=all(
                (
                    bool(
                        packet
                        .do_nothing_consequence
                    ),
                    all(
                        option.expected_benefit
                        and option
                        .expected_cost_or_risk
                        and option
                        .what_happens_next
                        for option in options
                    ),
                )
            ),
            explanation=(
                "Benefits, risks, next effects, and the "
                "do-nothing consequence must be visible."
            ),
            display_order=40,
        ),

        DecisionReviewCheck(
            check_id=(
                f"{packet.packet_id}-evidence"
            ),
            label="Required evidence references exist",
            passed=(
                len(required_evidence) >= 1
                and all(
                    item.source_id
                    and item.explanation
                    and item.raw_evidence_loaded
                    is False
                    for item
                    in required_evidence
                )
            ),
            explanation=(
                "Clouds references source-owned evidence but "
                "does not pretend raw evidence has already been reviewed."
            ),
            display_order=50,
        ),

        DecisionReviewCheck(
            check_id=(
                f"{packet.packet_id}-impact"
            ),
            label="Cross-business impact acknowledged",
            passed=(
                bool(
                    packet.impact_summary
                )
                and (
                    packet.impacted_source_id
                    is not None
                    or
                    "No additional impacted source"
                    in packet.impact_summary
                )
            ),
            explanation=(
                "The owner should know whether another "
                "Simplee source is affected."
            ),
            display_order=60,
        ),

        DecisionReviewCheck(
            check_id=(
                f"{packet.packet_id}-owner-prompts"
            ),
            label="Owner review prompts are complete",
            passed=(
                len(
                    packet.owner_review_prompts
                )
                >= 5
                and all(
                    bool(item)
                    for item
                    in packet.owner_review_prompts
                )
            ),
            explanation=(
                "The owner receives explicit review prompts "
                "before any choice boundary."
            ),
            display_order=70,
        ),

        DecisionReviewCheck(
            check_id=(
                f"{packet.packet_id}-application"
            ),
            label="Owning application identified",
            passed=all(
                (
                    bool(
                        packet.owning_application_id
                    ),
                    bool(
                        packet.owning_application_label
                    ),
                )
            ),
            explanation=(
                "The real workflow must remain owned by "
                "the correct downstream application."
            ),
            display_order=80,
        ),

        DecisionReviewCheck(
            check_id=(
                f"{packet.packet_id}-tower"
            ),
            label="Tower mediation requirement preserved",
            passed=(
                isinstance(
                    packet.requires_tower_mediation,
                    bool,
                )
            ),
            explanation=(
                "Protected application entry remains subject "
                "to the Tower boundary where required."
            ),
            display_order=90,
        ),

        DecisionReviewCheck(
            check_id=(
                f"{packet.packet_id}-nonexecution"
            ),
            label="No decision or execution has occurred",
            passed=all(
                (
                    packet
                    .automatic_decision_performed
                    is False,
                    packet.approval_performed
                    is False,
                    packet
                    .capital_movement_performed
                    is False,
                    packet
                    .downstream_execution_performed
                    is False,
                )
            ),
            explanation=(
                "GP030 is review only. Nothing may be "
                "approved, moved, or executed."
            ),
            display_order=100,
        ),
    )


def build_owner_decision_review(
    packet_id,
):
    packet = get_owner_decision_packet(
        packet_id
    )

    checks = _build_checks(
        packet
    )

    passed_count = sum(
        check.passed
        for check in checks
    )

    failed_count = (
        len(checks)
        - passed_count
    )

    ready = (
        failed_count == 0
    )

    failed_labels = tuple(
        check.label
        for check in checks
        if not check.passed
    )

    return OwnerDecisionReview(
        review_id=(
            "decision-review-"
            f"{packet.packet_id}"
        ),

        packet_id=packet.packet_id,
        agenda_item_id=(
            packet.agenda_item_id
        ),

        source_id=packet.source_id,
        source_label=(
            packet.source_label
        ),

        review_state=(
            DecisionReviewState
            .READY_FOR_OWNER_CHOICE.value
            if ready
            else DecisionReviewState
            .BLOCKED.value
        ),

        checks=checks,

        check_count=len(checks),

        passed_check_count=(
            passed_count
        ),

        failed_check_count=(
            failed_count
        ),

        owner_ready_to_choose=ready,

        soulaana_readiness_summary=(
            (
                f"This {packet.source_label} decision packet "
                "has the context, choices, consequences, and "
                "boundaries needed for you to make the choice."
            )
            if ready
            else
            (
                f"This {packet.source_label} decision is "
                "not ready for your choice yet."
            )
        ),

        soulaana_blocker_summary=(
            "No review blockers remain."
            if ready
            else
            "Blocking checks: "
            + ", ".join(
                failed_labels
            )
        ),

        soulaana_next_step=(
            (
                "You may move to the owner-choice boundary. "
                "Nothing will execute until a later protected "
                "workflow explicitly handles your choice."
            )
            if ready
            else
            (
                "Resolve the failed review checks before "
                "presenting this packet for owner choice."
            )
        ),

        automatic_decision_performed=False,
        approval_performed=False,
        owner_choice_recorded=False,
        capital_movement_performed=False,
        downstream_execution_performed=False,
    )


def get_owner_decision_reviews():
    return tuple(
        build_owner_decision_review(
            packet.packet_id
        )
        for packet
        in get_owner_decision_packets()
    )


def get_owner_decision_review(
    review_id,
):
    for review in (
        get_owner_decision_reviews()
    ):
        if review.review_id == review_id:
            return review

    raise KeyError(
        "Unknown owner decision review: "
        f"{review_id}"
    )


def get_owner_decision_review_by_packet(
    packet_id,
):
    for review in (
        get_owner_decision_reviews()
    ):
        if review.packet_id == packet_id:
            return review

    raise KeyError(
        "No owner decision review for packet: "
        f"{packet_id}"
    )


def get_owner_decision_review_surface():
    reviews = (
        get_owner_decision_reviews()
    )

    return OwnerDecisionReviewSurface(
        title=(
            "Owner Decision Review / Readiness Gate"
        ),

        reviews=reviews,

        review_count=len(reviews),

        ready_review_count=sum(
            review.review_state
            == "ready_for_owner_choice"
            for review in reviews
        ),

        blocked_review_count=sum(
            review.review_state
            == "blocked"
            for review in reviews
        ),

        automatic_decision_performed=False,
        approval_performed=False,
        owner_choice_recorded=False,
        capital_movement_performed=False,
        downstream_execution_performed=False,

        boundary_notice=(
            "GP030 verifies readiness for owner choice only. "
            "It does not record the owner's choice, approve "
            "anything, move capital, or execute work."
        ),
    )


def get_owner_decision_review_surface_payload():
    return (
        get_owner_decision_review_surface()
        .to_dict()
    )


def get_clouds_gp030_status_payload():
    gp029 = (
        get_clouds_gp029_status_payload()
    )

    surface = (
        get_owner_decision_review_surface()
    )

    reviews = surface.reviews

    safe = (
        gp029["status"] == "ready"
        and gp029["safe_to_continue"]
        is True

        and surface.review_count
        == gp029["packet_count"]

        and surface.ready_review_count
        == surface.review_count

        and surface.blocked_review_count
        == 0

        and all(
            review.check_count == 10
            and review.passed_check_count
            == 10
            and review.failed_check_count
            == 0
            and review.owner_ready_to_choose
            is True
            and review.review_state
            == "ready_for_owner_choice"
            and review
            .automatic_decision_performed
            is False
            and review.approval_performed
            is False
            and review.owner_choice_recorded
            is False
            and review
            .capital_movement_performed
            is False
            and review
            .downstream_execution_performed
            is False
            for review in reviews
        )

        and surface
        .automatic_decision_performed
        is False

        and surface.approval_performed
        is False

        and surface.owner_choice_recorded
        is False

        and surface.capital_movement_performed
        is False

        and surface
        .downstream_execution_performed
        is False
    )

    return {
        "pack": "GP030",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "OWNER DECISION REVIEW / "
            "READINESS GATE"
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

        "ready_review_count": (
            surface.ready_review_count
        ),

        "blocked_review_count": (
            surface.blocked_review_count
        ),

        "checks_per_review": 10,

        "decision_packet_reviewed": True,
        "consequences_reviewed": True,
        "impact_acknowledged": True,
        "owning_application_confirmed": True,
        "tower_mediation_preserved": True,

        "owner_ready_to_choose": (
            safe
        ),

        "automatic_decision_performed": False,
        "approval_performed": False,
        "owner_choice_recorded": False,
        "capital_movement_performed": False,
        "downstream_execution_performed": False,

        "cross_app_imports_used": False,

        "next_pack": (
            "GP031 — OWNER DECISION CHOICE / "
            "INTENT RECORDING BOUNDARY"
        ),
    }
