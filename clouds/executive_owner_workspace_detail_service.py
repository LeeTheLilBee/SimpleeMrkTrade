"""
Service layer for The Clouds Executive Owner Workspace Detail /
Action Intent Surface.

GP011 explains intended next actions without executing them.
"""

from __future__ import annotations

try:
    from .executive_owner_workspace_detail import (
        ExecutiveOwnerWorkspaceDetail,
        ExecutiveOwnerWorkspaceDetailSurface,
        OwnerActionBlocker,
        OwnerActionIntent,
        OwnerActionIntentAuthority,
        OwnerActionIntentKind,
        OwnerActionIntentRisk,
        OwnerActionIntentState,
        OwnerActionPrerequisite,
        blocker_sort_key,
        filter_workspace_details,
        prerequisite_sort_key,
    )
    from .executive_owner_workspace_service import (
        get_clouds_gp010_status_payload,
        get_executive_owner_workspace_item,
        get_executive_owner_workspace_items,
        get_executive_owner_workspace_panels,
    )

except ImportError:
    from executive_owner_workspace_detail import (
        ExecutiveOwnerWorkspaceDetail,
        ExecutiveOwnerWorkspaceDetailSurface,
        OwnerActionBlocker,
        OwnerActionIntent,
        OwnerActionIntentAuthority,
        OwnerActionIntentKind,
        OwnerActionIntentRisk,
        OwnerActionIntentState,
        OwnerActionPrerequisite,
        blocker_sort_key,
        filter_workspace_details,
        prerequisite_sort_key,
    )
    from executive_owner_workspace_service import (
        get_clouds_gp010_status_payload,
        get_executive_owner_workspace_item,
        get_executive_owner_workspace_items,
        get_executive_owner_workspace_panels,
    )


ALLOWED_CLOUDS_ACTIONS = (
    "Explain what a workspace item means",
    "Explain why a workspace item matters",
    "Describe the intended next action",
    "Classify action intent",
    "Display prerequisites",
    "Display blockers",
    "Display Tower requirements",
    "Display owner review questions",
    "Display a safe navigation reference",
    "Filter workspace detail projections",
)


PROHIBITED_CLOUDS_ACTIONS = (
    "Clouds cannot authenticate the owner",
    "Clouds cannot grant application permission",
    "Clouds cannot perform Tower step-up",
    "Clouds cannot bypass Tower",
    "Clouds cannot approve an owner decision",
    "Clouds cannot confirm irreversible execution",
    "Clouds cannot execute an action intent",
    "Clouds cannot launch downstream applications directly",
    "Clouds cannot execute trades",
    "Clouds cannot move money",
    "Clouds cannot retrieve raw Vault evidence",
    "Clouds cannot operate property workflows",
)


def _panel_id_for_item(
    item_id: str,
) -> str | None:
    for panel in (
        get_executive_owner_workspace_panels()
    ):
        if any(
            item.item_id == item_id
            for item in panel.items
        ):
            return panel.panel_id

    return None


def _intent_state_for_item(
    item,
) -> str:
    action = item.navigation_action

    if item.health == "blocked":
        return OwnerActionIntentState.BLOCKED.value

    if action is None:
        return (
            OwnerActionIntentState
            .REVIEW_REQUIRED.value
        )

    if action.requires_tower:
        return (
            OwnerActionIntentState
            .TOWER_REQUIRED.value
        )

    return OwnerActionIntentState.AVAILABLE.value


def _intent_kind_for_item(
    item,
) -> str:
    action = item.navigation_action

    if item.health == "blocked":
        return OwnerActionIntentKind.REVIEW.value

    if action is None:
        return OwnerActionIntentKind.REVIEW.value

    if action.requires_tower:
        return (
            OwnerActionIntentKind
            .REQUEST_TOWER_HANDOFF.value
        )

    if action.navigation_mode == "clouds_internal":
        return (
            OwnerActionIntentKind
            .OPEN_CLOUDS.value
        )

    return OwnerActionIntentKind.REVIEW.value


def _intent_risk_for_item(
    item,
) -> str:
    if item.priority == "critical":
        return OwnerActionIntentRisk.CRITICAL.value

    if item.priority == "high":
        return OwnerActionIntentRisk.HIGH.value

    if item.priority == "elevated":
        return OwnerActionIntentRisk.ELEVATED.value

    return OwnerActionIntentRisk.ROUTINE.value


def _intent_authority_for_item(
    item,
) -> str:
    action = item.navigation_action

    if action is None:
        return OwnerActionIntentAuthority.OWNER.value

    if action.requires_tower:
        return OwnerActionIntentAuthority.TOWER.value

    return OwnerActionIntentAuthority.CLOUDS.value


def _build_prerequisites(
    item,
) -> tuple[
    OwnerActionPrerequisite,
    ...
]:
    action = item.navigation_action

    prerequisites = [
        OwnerActionPrerequisite(
            prerequisite_id=(
                f"{item.item_id}-source-integrity"
            ),
            label="Source integrity verified",
            satisfied=(
                item.source_integrity_verified
            ),
            explanation=(
                "Clouds only presents this intent when "
                "the source projection is internally valid."
            ),
            display_order=10,
        ),
    ]

    if action is not None and action.requires_tower:
        prerequisites.extend(
            [
                OwnerActionPrerequisite(
                    prerequisite_id=(
                        f"{item.item_id}-tower-required"
                    ),
                    label="Tower mediation required",
                    satisfied=True,
                    explanation=(
                        "This destination must remain "
                        "behind Tower-mediated entry."
                    ),
                    display_order=20,
                ),
                OwnerActionPrerequisite(
                    prerequisite_id=(
                        f"{item.item_id}-owner-permission"
                    ),
                    label="Owner permission required",
                    satisfied=(
                        action
                        .requires_owner_permission
                    ),
                    explanation=(
                        "Clouds can display the requirement "
                        "but cannot satisfy it."
                    ),
                    display_order=30,
                ),
                OwnerActionPrerequisite(
                    prerequisite_id=(
                        f"{item.item_id}-step-up"
                    ),
                    label="Step-up may be required",
                    satisfied=(
                        action.requires_step_up
                    ),
                    explanation=(
                        "Tower controls step-up and must "
                        "evaluate it at handoff time."
                    ),
                    display_order=40,
                ),
            ]
        )

    elif action is not None:
        prerequisites.append(
            OwnerActionPrerequisite(
                prerequisite_id=(
                    f"{item.item_id}-clouds-route"
                ),
                label="Clouds internal route available",
                satisfied=(
                    action.open_route is not None
                ),
                explanation=(
                    "The item can be reviewed inside Clouds "
                    "without downstream execution."
                ),
                display_order=20,
            )
        )

    return tuple(
        sorted(
            prerequisites,
            key=prerequisite_sort_key,
        )
    )


def _build_blockers(
    item,
) -> tuple[
    OwnerActionBlocker,
    ...
]:
    blockers = []

    action = item.navigation_action

    if item.health == "blocked":
        blockers.append(
            OwnerActionBlocker(
                blocker_id=(
                    f"{item.item_id}-strategic-blocker"
                ),
                label="Strategic blocker present",
                explanation=(
                    "The underlying item remains blocked. "
                    "Clouds may explain the blocker but "
                    "cannot resolve downstream authority "
                    "or operational constraints."
                ),
                authority=(
                    OwnerActionIntentAuthority
                    .OWNER.value
                ),
                resolvable_in_clouds=False,
                display_order=10,
            )
        )

    if (
        action is not None
        and action.requires_tower
    ):
        blockers.append(
            OwnerActionBlocker(
                blocker_id=(
                    f"{item.item_id}-tower-boundary"
                ),
                label="Tower boundary",
                explanation=(
                    "Clouds cannot cross the Tower access "
                    "boundary or perform the handoff itself."
                ),
                authority=(
                    OwnerActionIntentAuthority
                    .TOWER.value
                ),
                resolvable_in_clouds=False,
                display_order=20,
            )
        )

    return tuple(
        sorted(
            blockers,
            key=blocker_sort_key,
        )
    )


def _build_owner_questions(
    item,
) -> tuple[str, ...]:
    questions = [
        "Do I understand what this item means?",
        "Does this item require action now or only review?",
        "What happens if I leave this item unchanged?",
    ]

    action = item.navigation_action

    if (
        action is not None
        and action.requires_tower
    ):
        questions.append(
            "Am I ready to request Tower-mediated entry?"
        )

    if item.health == "blocked":
        questions.append(
            "What specific condition must change before this can advance?"
        )

    return tuple(questions)


def _build_intent(
    item,
    *,
    display_order: int,
) -> OwnerActionIntent:
    action = item.navigation_action

    kind = _intent_kind_for_item(item)
    state = _intent_state_for_item(item)

    if (
        kind
        == OwnerActionIntentKind
        .REQUEST_TOWER_HANDOFF.value
    ):
        explanation = (
            "The intended next step is to request a "
            "Tower-mediated handoff. Clouds can display "
            "the route and requirements but cannot "
            "perform the handoff."
        )

    elif (
        kind
        == OwnerActionIntentKind
        .OPEN_CLOUDS.value
    ):
        explanation = (
            "The intended next step stays inside Clouds "
            "for additional review or detail."
        )

    else:
        explanation = (
            "The intended next step is owner review. "
            "No execution is implied."
        )

    return OwnerActionIntent(
        intent_id=(
            f"intent-{item.item_id}"
        ),
        kind=kind,
        state=state,
        risk=_intent_risk_for_item(
            item
        ),
        title=(
            f"Intent for {item.title}"
        ),
        explanation=explanation,
        owner_prompt=(
            item.owner_prompt
        ),
        source_item_id=item.item_id,
        source_section_id=(
            item.source_section_id
        ),
        source_app_id=(
            item.source_app_id
        ),
        source_lane_id=(
            item.source_lane_id
        ),
        destination_id=(
            action.destination_id
            if action
            else None
        ),
        open_route=(
            action.open_route
            if action
            else None
        ),
        navigation_mode=(
            action.navigation_mode
            if action
            else "none"
        ),
        authority=(
            _intent_authority_for_item(
                item
            )
        ),
        requires_owner_review=True,
        requires_tower=(
            action.requires_tower
            if action
            else False
        ),
        requires_owner_permission=(
            action.requires_owner_permission
            if action
            else False
        ),
        requires_step_up=(
            action.requires_step_up
            if action
            else False
        ),
        clouds_can_execute=False,
        approval_performed=False,
        execution_performed=False,
        display_order=display_order,
    )


def _what_it_means(
    item,
) -> str:
    if item.kind == "focus":
        return (
            "Clouds has elevated this item into the "
            "owner's immediate focus."
        )

    if item.kind == "priority":
        return (
            "This item represents a strategic priority "
            "within the current executive ordering."
        )

    if item.kind == "attention":
        return (
            "This item is being kept visible for owner "
            "awareness or review."
        )

    if item.kind == "section":
        return (
            "This item is an executive Clouds section "
            "that can be opened for deeper review."
        )

    if item.kind == "destination":
        return (
            "This item represents a downstream application "
            "destination referenced by Clouds."
        )

    if item.kind == "readiness":
        return (
            "This item summarizes the current combined "
            "readiness posture."
        )

    return (
        "This item is part of the executive owner workspace."
    )


def _why_it_matters(
    item,
) -> str:
    if item.health == "blocked":
        return (
            "It matters because a blocked condition can "
            "prevent progress even when other work is healthy."
        )

    if item.health == "attention":
        return (
            "It matters because Clouds believes the owner "
            "should review it before it fades into routine work."
        )

    if item.health == "watch":
        return (
            "It matters because it should remain visible "
            "even though immediate intervention may not be needed."
        )

    return (
        "It matters because it contributes to the owner's "
        "overall command picture."
    )


def _what_to_do_now(
    item,
) -> str:
    action = item.navigation_action

    if action is None:
        return item.owner_prompt

    if action.requires_tower:
        return (
            f"{item.owner_prompt} "
            "If you choose to continue, Tower must mediate "
            "the next step."
        )

    return item.owner_prompt


def _what_can_wait(
    item,
) -> str:
    if item.priority == "critical":
        return (
            "Lower-priority workspace items can wait until "
            "this item has been reviewed."
        )

    if item.priority == "high":
        return (
            "Routine and watch-only work can wait while "
            "this item is reviewed."
        )

    return (
        "No immediate execution is required from Clouds; "
        "this item may remain visible until the owner is ready."
    )


def get_executive_owner_workspace_details(
) -> tuple[
    ExecutiveOwnerWorkspaceDetail,
    ...
]:
    items = (
        get_executive_owner_workspace_items()
    )

    details = []

    for index, item in enumerate(
        items,
        start=1,
    ):
        details.append(
            ExecutiveOwnerWorkspaceDetail(
                item_id=item.item_id,
                panel_id=(
                    _panel_id_for_item(
                        item.item_id
                    )
                ),
                title=item.title,
                summary=item.summary,
                what_it_means=(
                    _what_it_means(item)
                ),
                why_it_matters=(
                    _why_it_matters(item)
                ),
                what_to_do_now=(
                    _what_to_do_now(item)
                ),
                what_can_wait=(
                    _what_can_wait(item)
                ),
                health=item.health,
                priority=item.priority,
                source_section_id=(
                    item.source_section_id
                ),
                source_app_id=(
                    item.source_app_id
                ),
                source_lane_id=(
                    item.source_lane_id
                ),
                action_intent=(
                    _build_intent(
                        item,
                        display_order=index * 10,
                    )
                ),
                prerequisites=(
                    _build_prerequisites(
                        item
                    )
                ),
                blockers=(
                    _build_blockers(
                        item
                    )
                ),
                owner_questions=(
                    _build_owner_questions(
                        item
                    )
                ),
                allowed_clouds_actions=(
                    ALLOWED_CLOUDS_ACTIONS
                ),
                prohibited_clouds_actions=(
                    PROHIBITED_CLOUDS_ACTIONS
                ),
                source_integrity_verified=(
                    item.source_integrity_verified
                ),
                downstream_execution_performed=False,
            )
        )

    return tuple(details)


def get_executive_owner_workspace_detail(
    item_id: str,
) -> ExecutiveOwnerWorkspaceDetail:
    for detail in (
        get_executive_owner_workspace_details()
    ):
        if detail.item_id == item_id:
            return detail

    raise KeyError(
        "Unknown executive owner workspace detail item: "
        f"{item_id}"
    )


def get_executive_owner_workspace_detail_payload(
    item_id: str,
) -> dict:
    return (
        get_executive_owner_workspace_detail(
            item_id
        ).to_dict()
    )


def get_executive_owner_workspace_detail_surface(
) -> ExecutiveOwnerWorkspaceDetailSurface:
    return ExecutiveOwnerWorkspaceDetailSurface(
        title=(
            "Executive Owner Workspace Detail "
            "/ Action Intent"
        ),
        subtitle=(
            "Detailed owner interpretation and "
            "non-executing action intent for every "
            "workspace item."
        ),
        details=(
            get_executive_owner_workspace_details()
        ),
        boundary_notice=(
            "Action intent is descriptive only. Clouds "
            "does not authenticate, authorize, approve, "
            "step-up, hand off, or execute downstream work."
        ),
    )


def get_executive_owner_workspace_detail_surface_payload(
) -> dict:
    return (
        get_executive_owner_workspace_detail_surface()
        .to_dict()
    )


def filter_executive_owner_workspace_details(
    *,
    health: str | None = None,
    priority: str | None = None,
    source_section_id: str | None = None,
    source_app_id: str | None = None,
    source_lane_id: str | None = None,
    intent_kind: str | None = None,
    intent_state: str | None = None,
    requires_tower: bool | None = None,
) -> tuple[
    ExecutiveOwnerWorkspaceDetail,
    ...
]:
    return filter_workspace_details(
        get_executive_owner_workspace_details(),
        health=health,
        priority=priority,
        source_section_id=source_section_id,
        source_app_id=source_app_id,
        source_lane_id=source_lane_id,
        intent_kind=intent_kind,
        intent_state=intent_state,
        requires_tower=requires_tower,
    )


def get_clouds_gp011_status_payload() -> dict:
    gp010 = get_clouds_gp010_status_payload()

    details = (
        get_executive_owner_workspace_details()
    )

    tower_intents = [
        detail
        for detail in details
        if detail.action_intent.requires_tower
    ]

    internal_intents = [
        detail
        for detail in details
        if (
            detail.action_intent.navigation_mode
            == "clouds_internal"
        )
    ]

    safe_to_continue = (
        gp010["status"] == "ready"
        and gp010["safe_to_continue"] is True
        and len(details) == 18
        and all(
            detail.source_integrity_verified
            is True
            for detail in details
        )
        and all(
            detail.action_intent
            .clouds_can_execute
            is False
            for detail in details
        )
        and all(
            detail.action_intent
            .approval_performed
            is False
            for detail in details
        )
        and all(
            detail.action_intent
            .execution_performed
            is False
            for detail in details
        )
        and all(
            detail
            .downstream_execution_performed
            is False
            for detail in details
        )
        and all(
            blocker.resolvable_in_clouds
            is False
            for detail in details
            for blocker in detail.blockers
        )
    )

    return {
        "pack": "GP011",
        "section": (
            "EXECUTIVE OWNER WORKSPACE DETAIL "
            "/ ACTION INTENT SURFACE"
        ),
        "status": (
            "ready"
            if safe_to_continue
            else "blocked"
        ),
        "safe_to_continue": safe_to_continue,
        "detail_count": len(details),
        "tower_intent_count": len(
            tower_intents
        ),
        "internal_intent_count": len(
            internal_intents
        ),
        "source_integrity_verified": all(
            detail.source_integrity_verified
            for detail in details
        ),
        "tower_boundary_preserved": True,
        "approval_performed": False,
        "intent_execution_performed": False,
        "downstream_execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP012 — EXECUTIVE OWNER ACTION INTENT "
            "REVIEW / HANDOFF PREPARATION SURFACE"
        ),
    }
