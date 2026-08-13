"""
Service layer for The Clouds Executive Owner Action Intent
Review / Handoff Preparation Surface.

GP012 prepares descriptive owner review packets only.

No approval, Tower request creation, handoff execution,
or downstream execution occurs here.
"""

from __future__ import annotations

try:
    from .executive_owner_action_intent_review import (
        HandoffPreparation,
        HandoffPreparationState,
        IntentReviewAuthority,
        IntentReviewDecision,
        IntentReviewState,
        OwnerIntentReviewPacket,
        OwnerIntentReviewSurface,
        ReviewBlocker,
        ReviewRequirement,
        filter_review_packets,
        requirement_sort_key,
        review_blocker_sort_key,
        review_packet_sort_key,
    )

    from .executive_owner_workspace_detail_service import (
        get_clouds_gp011_status_payload,
        get_executive_owner_workspace_details,
    )

except ImportError:
    from executive_owner_action_intent_review import (
        HandoffPreparation,
        HandoffPreparationState,
        IntentReviewAuthority,
        IntentReviewDecision,
        IntentReviewState,
        OwnerIntentReviewPacket,
        OwnerIntentReviewSurface,
        ReviewBlocker,
        ReviewRequirement,
        filter_review_packets,
        requirement_sort_key,
        review_blocker_sort_key,
        review_packet_sort_key,
    )

    from executive_owner_workspace_detail_service import (
        get_clouds_gp011_status_payload,
        get_executive_owner_workspace_details,
    )


def _review_authority(
    detail,
) -> str:
    intent = detail.action_intent

    if intent.requires_tower:
        return IntentReviewAuthority.TOWER.value

    if (
        intent.navigation_mode
        == "clouds_internal"
    ):
        return IntentReviewAuthority.CLOUDS.value

    return IntentReviewAuthority.OWNER.value


def _requirements(
    detail,
) -> tuple[
    ReviewRequirement,
    ...
]:
    intent = detail.action_intent

    requirements = [
        ReviewRequirement(
            requirement_id=(
                f"{detail.item_id}-source-integrity"
            ),
            label="Source integrity verified",
            required=True,
            satisfied_for_preparation=(
                detail
                .source_integrity_verified
            ),
            authority=(
                IntentReviewAuthority
                .CLOUDS.value
            ),
            explanation=(
                "The owner review packet must be based "
                "on a valid Clouds source projection."
            ),
            display_order=10,
        ),

        ReviewRequirement(
            requirement_id=(
                f"{detail.item_id}-owner-review"
            ),
            label="Owner review required",
            required=True,
            satisfied_for_preparation=True,
            authority=(
                IntentReviewAuthority
                .OWNER.value
            ),
            explanation=(
                "GP012 may prepare the packet for owner "
                "review, but does not record the owner's "
                "decision."
            ),
            display_order=20,
        ),
    ]

    if intent.requires_tower:
        requirements.extend(
            [
                ReviewRequirement(
                    requirement_id=(
                        f"{detail.item_id}-tower"
                    ),
                    label="Tower mediation required",
                    required=True,
                    satisfied_for_preparation=True,
                    authority=(
                        IntentReviewAuthority
                        .TOWER.value
                    ),
                    explanation=(
                        "Clouds may prepare the handoff "
                        "description, but Tower owns the "
                        "protected boundary."
                    ),
                    display_order=30,
                ),

                ReviewRequirement(
                    requirement_id=(
                        f"{detail.item_id}-permission"
                    ),
                    label="Owner permission check required",
                    required=(
                        intent
                        .requires_owner_permission
                    ),
                    satisfied_for_preparation=True,
                    authority=(
                        IntentReviewAuthority
                        .TOWER.value
                    ),
                    explanation=(
                        "Tower must evaluate owner permission "
                        "before any protected entry."
                    ),
                    display_order=40,
                ),

                ReviewRequirement(
                    requirement_id=(
                        f"{detail.item_id}-step-up"
                    ),
                    label="Step-up evaluation required",
                    required=(
                        intent.requires_step_up
                    ),
                    satisfied_for_preparation=True,
                    authority=(
                        IntentReviewAuthority
                        .TOWER.value
                    ),
                    explanation=(
                        "Clouds only exposes the requirement. "
                        "Tower decides whether step-up is "
                        "satisfied."
                    ),
                    display_order=50,
                ),
            ]
        )

    else:
        requirements.append(
            ReviewRequirement(
                requirement_id=(
                    f"{detail.item_id}-internal-route"
                ),
                label="Clouds review route available",
                required=True,
                satisfied_for_preparation=(
                    intent.open_route is not None
                ),
                authority=(
                    IntentReviewAuthority
                    .CLOUDS.value
                ),
                explanation=(
                    "Internal review remains inside Clouds "
                    "and does not represent downstream "
                    "execution."
                ),
                display_order=30,
            )
        )

    return tuple(
        sorted(
            requirements,
            key=requirement_sort_key,
        )
    )


def _blockers(
    detail,
) -> tuple[
    ReviewBlocker,
    ...
]:
    blockers = []

    for index, blocker in enumerate(
        detail.blockers,
        start=1,
    ):
        blocks_preparation = (
            detail.health == "blocked"
            and blocker.blocker_id.endswith(
                "-strategic-blocker"
            )
        )

        blockers.append(
            ReviewBlocker(
                blocker_id=(
                    f"review-{blocker.blocker_id}"
                ),
                label=blocker.label,
                explanation=blocker.explanation,
                authority=blocker.authority,
                blocks_preparation=(
                    blocks_preparation
                ),
                resolvable_in_clouds=False,
                display_order=index * 10,
            )
        )

    return tuple(
        sorted(
            blockers,
            key=review_blocker_sort_key,
        )
    )


def _preparation_state(
    detail,
    blockers,
    requirements,
) -> str:
    if any(
        blocker.blocks_preparation
        for blocker in blockers
    ):
        return (
            HandoffPreparationState
            .NOT_PREPARED.value
        )

    if not all(
        (
            not requirement.required
            or requirement
            .satisfied_for_preparation
        )
        for requirement in requirements
    ):
        return (
            HandoffPreparationState
            .NOT_PREPARED.value
        )

    if (
        detail.action_intent.requires_tower
        or detail.action_intent
        .navigation_mode
        == "clouds_internal"
    ):
        return (
            HandoffPreparationState
            .PREPARED.value
        )

    return (
        HandoffPreparationState
        .NOT_REQUIRED.value
    )


def _review_state(
    detail,
    preparation_state,
) -> str:
    intent = detail.action_intent

    if preparation_state == (
        HandoffPreparationState
        .NOT_PREPARED.value
    ):
        return IntentReviewState.BLOCKED.value

    if intent.requires_tower:
        return (
            IntentReviewState
            .TOWER_HANDOFF_PREPARED.value
        )

    if (
        intent.navigation_mode
        == "clouds_internal"
    ):
        return (
            IntentReviewState
            .INTERNAL_REVIEW_PREPARED.value
        )

    return (
        IntentReviewState
        .READY_FOR_OWNER_REVIEW.value
    )


def _handoff_preparation(
    detail,
    *,
    preparation_state,
) -> HandoffPreparation:
    intent = detail.action_intent

    if intent.requires_tower:
        explanation = (
            "The descriptive Tower handoff packet is "
            "prepared for owner review. No Tower request "
            "has been created and no handoff has occurred."
        )

    elif (
        intent.navigation_mode
        == "clouds_internal"
    ):
        explanation = (
            "The internal Clouds review path is prepared. "
            "No downstream application execution is implied."
        )

    else:
        explanation = (
            "No protected handoff is required for this "
            "review packet."
        )

    return HandoffPreparation(
        preparation_id=(
            f"preparation-{detail.item_id}"
        ),
        state=preparation_state,
        destination_id=(
            intent.destination_id
        ),
        open_route=(
            intent.open_route
        ),
        navigation_mode=(
            intent.navigation_mode
        ),
        requires_tower=(
            intent.requires_tower
        ),
        requires_owner_permission=(
            intent.requires_owner_permission
        ),
        requires_step_up=(
            intent.requires_step_up
        ),
        tower_authority_required=(
            intent.requires_tower
        ),
        downstream_authority_required=(
            intent.requires_tower
        ),
        owner_approval_recorded=False,
        tower_request_created=False,
        tower_handoff_executed=False,
        downstream_execution_performed=False,
        explanation=explanation,
    )


def _prepared_next_step(
    detail,
    review_state,
) -> str:
    if review_state == (
        IntentReviewState
        .TOWER_HANDOFF_PREPARED.value
    ):
        return (
            "Owner may review whether to request a "
            "Tower-mediated handoff. GP012 does not "
            "create that request."
        )

    if review_state == (
        IntentReviewState
        .INTERNAL_REVIEW_PREPARED.value
    ):
        return (
            "Owner may continue into the referenced "
            "Clouds review surface."
        )

    if review_state == (
        IntentReviewState.BLOCKED.value
    ):
        return (
            "Do not advance. Review the blocker first."
        )

    return (
        "Owner review is prepared. No execution occurs."
    )


def get_owner_intent_review_packets(
) -> tuple[
    OwnerIntentReviewPacket,
    ...
]:
    details = (
        get_executive_owner_workspace_details()
    )

    packets = []

    for index, detail in enumerate(
        details,
        start=1,
    ):
        requirements = _requirements(
            detail
        )

        blockers = _blockers(
            detail
        )

        preparation_state = (
            _preparation_state(
                detail,
                blockers,
                requirements,
            )
        )

        review_state = _review_state(
            detail,
            preparation_state,
        )

        handoff = _handoff_preparation(
            detail,
            preparation_state=(
                preparation_state
            ),
        )

        packets.append(
            OwnerIntentReviewPacket(
                review_id=(
                    f"review-{detail.item_id}"
                ),
                item_id=detail.item_id,
                intent_id=(
                    detail.action_intent
                    .intent_id
                ),
                title=detail.title,
                summary=detail.summary,
                what_is_being_considered=(
                    detail.action_intent
                    .explanation
                ),
                why_owner_review_matters=(
                    detail.why_it_matters
                ),
                prepared_next_step=(
                    _prepared_next_step(
                        detail,
                        review_state,
                    )
                ),
                review_state=review_state,
                preparation_state=(
                    preparation_state
                ),
                decision=(
                    IntentReviewDecision
                    .UNDECIDED.value
                ),
                authority=(
                    _review_authority(
                        detail
                    )
                ),
                source_section_id=(
                    detail.source_section_id
                ),
                source_app_id=(
                    detail.source_app_id
                ),
                source_lane_id=(
                    detail.source_lane_id
                ),
                requirements=requirements,
                blockers=blockers,
                handoff_preparation=handoff,
                owner_review_questions=(
                    detail.owner_questions
                ),
                source_integrity_verified=(
                    detail
                    .source_integrity_verified
                ),
                owner_approval_recorded=False,
                tower_request_created=False,
                execution_performed=False,
                display_order=index * 10,
            )
        )

    return tuple(
        sorted(
            packets,
            key=review_packet_sort_key,
        )
    )


def get_owner_intent_review_packet(
    item_id: str,
) -> OwnerIntentReviewPacket:
    for packet in (
        get_owner_intent_review_packets()
    ):
        if packet.item_id == item_id:
            return packet

    raise KeyError(
        "Unknown owner intent review item: "
        f"{item_id}"
    )


def get_owner_intent_review_packet_payload(
    item_id: str,
) -> dict:
    return (
        get_owner_intent_review_packet(
            item_id
        ).to_dict()
    )


def filter_owner_intent_review_packets(
    *,
    review_state: str | None = None,
    preparation_state: str | None = None,
    authority: str | None = None,
    source_app_id: str | None = None,
    source_lane_id: str | None = None,
    requires_tower: bool | None = None,
    blocked: bool | None = None,
) -> tuple[
    OwnerIntentReviewPacket,
    ...
]:
    return filter_review_packets(
        get_owner_intent_review_packets(),
        review_state=review_state,
        preparation_state=(
            preparation_state
        ),
        authority=authority,
        source_app_id=source_app_id,
        source_lane_id=source_lane_id,
        requires_tower=requires_tower,
        blocked=blocked,
    )


def get_owner_intent_review_surface(
) -> OwnerIntentReviewSurface:
    reviews = (
        get_owner_intent_review_packets()
    )

    prepared = [
        review
        for review in reviews
        if review.preparation_state
        == HandoffPreparationState
        .PREPARED.value
    ]

    tower_prepared = [
        review
        for review in reviews
        if review.review_state
        == IntentReviewState
        .TOWER_HANDOFF_PREPARED.value
    ]

    blocked = [
        review
        for review in reviews
        if review.review_state
        == IntentReviewState
        .BLOCKED.value
    ]

    return OwnerIntentReviewSurface(
        title=(
            "Executive Owner Action Intent Review "
            "/ Handoff Preparation"
        ),
        subtitle=(
            "Owner review packets and non-executing "
            "handoff preparation across the Clouds "
            "command workspace."
        ),
        reviews=reviews,
        review_count=len(reviews),
        prepared_count=len(prepared),
        tower_prepared_count=(
            len(tower_prepared)
        ),
        blocked_count=len(blocked),
        boundary_notice=(
            "Prepared does not mean approved, "
            "authorized, requested, handed off, or "
            "executed. Tower and downstream applications "
            "retain their authority."
        ),
    )


def get_owner_intent_review_surface_payload(
) -> dict:
    return (
        get_owner_intent_review_surface()
        .to_dict()
    )


def get_clouds_gp012_status_payload() -> dict:
    gp011 = get_clouds_gp011_status_payload()

    surface = (
        get_owner_intent_review_surface()
    )

    reviews = surface.reviews

    safe_to_continue = (
        gp011["status"] == "ready"
        and gp011["safe_to_continue"] is True
        and surface.review_count == 18
        and all(
            review.source_integrity_verified
            is True
            for review in reviews
        )
        and all(
            review.decision
            == IntentReviewDecision
            .UNDECIDED.value
            for review in reviews
        )
        and all(
            review.owner_approval_recorded
            is False
            for review in reviews
        )
        and all(
            review.tower_request_created
            is False
            for review in reviews
        )
        and all(
            review.execution_performed
            is False
            for review in reviews
        )
        and all(
            review
            .handoff_preparation
            .owner_approval_recorded
            is False
            for review in reviews
        )
        and all(
            review
            .handoff_preparation
            .tower_request_created
            is False
            for review in reviews
        )
        and all(
            review
            .handoff_preparation
            .tower_handoff_executed
            is False
            for review in reviews
        )
        and all(
            review
            .handoff_preparation
            .downstream_execution_performed
            is False
            for review in reviews
        )
        and all(
            blocker.resolvable_in_clouds
            is False
            for review in reviews
            for blocker in review.blockers
        )
    )

    return {
        "pack": "GP012",
        "section": (
            "EXECUTIVE OWNER ACTION INTENT REVIEW "
            "/ HANDOFF PREPARATION SURFACE"
        ),
        "status": (
            "ready"
            if safe_to_continue
            else "blocked"
        ),
        "safe_to_continue": safe_to_continue,
        "review_count": (
            surface.review_count
        ),
        "prepared_count": (
            surface.prepared_count
        ),
        "tower_prepared_count": (
            surface.tower_prepared_count
        ),
        "blocked_count": (
            surface.blocked_count
        ),
        "source_integrity_verified": all(
            review.source_integrity_verified
            for review in reviews
        ),
        "tower_boundary_preserved": True,
        "owner_decision_recorded": False,
        "owner_approval_recorded": False,
        "tower_request_created": False,
        "handoff_executed": False,
        "downstream_execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP013 — EXECUTIVE OWNER HANDOFF "
            "REQUEST DRAFT / TOWER DELIVERY "
            "ENVELOPE SURFACE"
        ),
    }
