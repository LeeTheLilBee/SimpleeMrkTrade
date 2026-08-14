"""
Service layer for the Clouds Executive Owner Command Workspace.

GP010 composes existing Clouds executive surfaces into one
read-only owner workspace.

No downstream operational execution occurs here.
"""

from __future__ import annotations

try:
    from .executive_dashboard_detail_service import (
        get_executive_dashboard_sections,
    )
    from .executive_dashboard_service import (
        get_executive_dashboard,
        get_executive_dashboard_summary,
        get_executive_recommendations,
    )
    from .executive_navigation_map_service import (
        get_clouds_gp009_status_payload,
        get_executive_navigation_destination,
        get_executive_navigation_destinations,
        get_executive_navigation_map_summary,
    )
    from .executive_owner_workspace import (
        ExecutiveOwnerWorkspace,
        WorkspaceHeadline,
        WorkspaceHealth,
        WorkspaceItem,
        WorkspaceItemKind,
        WorkspaceNavigationAction,
        WorkspaceNavigationMode,
        WorkspacePanel,
        WorkspacePanelKind,
        WorkspacePriority,
        WorkspaceSummary,
        filter_workspace_items,
        workspace_item_sort_key,
        workspace_panel_sort_key,
    )
    from .owner_attention_surface_service import (
        get_owner_attention_surface,
    )
    from .priority_board_service import (
        get_priority_board,
    )
    from .today_surface_service import (
        get_today_surface,
    )

except ImportError:
    from executive_dashboard_detail_service import (
        get_executive_dashboard_sections,
    )
    from executive_dashboard_service import (
        get_executive_dashboard,
        get_executive_dashboard_summary,
        get_executive_recommendations,
    )
    from executive_navigation_map_service import (
        get_clouds_gp009_status_payload,
        get_executive_navigation_destination,
        get_executive_navigation_destinations,
        get_executive_navigation_map_summary,
    )
    from executive_owner_workspace import (
        ExecutiveOwnerWorkspace,
        WorkspaceHeadline,
        WorkspaceHealth,
        WorkspaceItem,
        WorkspaceItemKind,
        WorkspaceNavigationAction,
        WorkspaceNavigationMode,
        WorkspacePanel,
        WorkspacePanelKind,
        WorkspacePriority,
        WorkspaceSummary,
        filter_workspace_items,
        workspace_item_sort_key,
        workspace_panel_sort_key,
    )
    from owner_attention_surface_service import (
        get_owner_attention_surface,
    )
    from priority_board_service import (
        get_priority_board,
    )
    from today_surface_service import (
        get_today_surface,
    )


ALLOWED_CLOUDS_ACTIONS = (
    "Explain current owner focus",
    "Display current strategic priorities",
    "Display owner attention",
    "Display watch items",
    "Display executive section summaries",
    "Display application navigation references",
    "Display readiness state",
    "Display Tower permission and step-up requirements",
    "Filter workspace items",
    "Recommend the next owner review target",
)


PROHIBITED_CLOUDS_ACTIONS = (
    "Clouds cannot authenticate the owner",
    "Clouds cannot grant application permission",
    "Clouds cannot perform Tower step-up",
    "Clouds cannot bypass Tower",
    "Clouds cannot approve owner decisions",
    "Clouds cannot execute workspace actions",
    "Clouds cannot directly launch downstream applications",
    "Clouds cannot execute trades",
    "Clouds cannot move money",
    "Clouds cannot retrieve raw Vault evidence",
    "Clouds cannot operate property workflows",
)


def _navigation_action(
    destination_id: str | None,
    *,
    action_id: str,
    label: str,
    display_order: int,
) -> WorkspaceNavigationAction | None:
    if destination_id is None:
        return None

    destination = (
        get_executive_navigation_destination(
            destination_id
        )
    )

    return WorkspaceNavigationAction(
        action_id=action_id,
        label=label,
        destination_id=destination.destination_id,
        open_route=destination.open_route,
        navigation_mode=(
            destination.navigation_mode
        ),
        requires_tower=(
            destination.requires_tower
        ),
        requires_owner_permission=(
            destination
            .requires_owner_permission
        ),
        requires_step_up=(
            destination.requires_step_up
        ),
        clouds_executes_navigation=False,
        downstream_execution_performed=False,
        display_order=display_order,
    )


def _map_priority(
    strategic_priority: str,
) -> str:
    return {
        "critical": WorkspacePriority.CRITICAL.value,
        "high": WorkspacePriority.HIGH.value,
        "medium": WorkspacePriority.ELEVATED.value,
        "low": WorkspacePriority.ROUTINE.value,
    }.get(
        strategic_priority,
        WorkspacePriority.ROUTINE.value,
    )


def _map_health(
    value: str,
) -> str:
    if value in {
        WorkspaceHealth.HEALTHY.value,
        WorkspaceHealth.WATCH.value,
        WorkspaceHealth.ATTENTION.value,
        WorkspaceHealth.BLOCKED.value,
    }:
        return value

    return WorkspaceHealth.WATCH.value


def _build_now_items() -> tuple[
    WorkspaceItem,
    ...
]:
    today = get_today_surface()
    priorities = get_priority_board()

    items = []

    if today.focus:
        focus = today.focus[0]

        destination_id = (
            "tower-observatory"
            if focus.source_app_id == "observatory"
            else "clouds-today"
        )

        items.append(
            WorkspaceItem(
                item_id="workspace-now-focus",
                kind=WorkspaceItemKind.FOCUS.value,
                title=focus.title,
                summary=focus.summary,
                explanation=(
                    "This is the highest-priority item "
                    "Clouds currently places in the owner's "
                    "Today focus."
                ),
                owner_prompt=(
                    focus.owner_action_label
                ),
                priority=WorkspacePriority.CRITICAL.value,
                health=WorkspaceHealth.ATTENTION.value,
                source_section_id="today",
                source_app_id=focus.source_app_id,
                source_lane_id=focus.source_lane_id,
                navigation_action=(
                    _navigation_action(
                        destination_id,
                        action_id=(
                            "workspace-now-focus-open"
                        ),
                        label="Review focus",
                        display_order=10,
                    )
                ),
                source_integrity_verified=(
                    focus.source_integrity_verified
                ),
                execution_performed=False,
                display_order=10,
            )
        )

    if priorities.top_recommendation:
        card = priorities.top_recommendation

        destination_id = (
            "tower-observatory"
            if card.source_app_id == "observatory"
            else "clouds-priority-board"
        )

        items.append(
            WorkspaceItem(
                item_id="workspace-now-priority",
                kind=WorkspaceItemKind.PRIORITY.value,
                title=card.title,
                summary=card.summary,
                explanation=(
                    card.priority_explanation
                ),
                owner_prompt=(
                    card.recommended_owner_action
                ),
                priority=_map_priority(
                    card.strategic_priority
                ),
                health=(
                    WorkspaceHealth.BLOCKED.value
                    if card.state == "blocked"
                    else WorkspaceHealth.WATCH.value
                ),
                source_section_id="priorities",
                source_app_id=card.source_app_id,
                source_lane_id=card.source_lane_id,
                navigation_action=(
                    _navigation_action(
                        destination_id,
                        action_id=(
                            "workspace-now-priority-open"
                        ),
                        label="Review priority",
                        display_order=20,
                    )
                ),
                source_integrity_verified=(
                    card.source_integrity_verified
                ),
                execution_performed=False,
                display_order=20,
            )
        )

    return tuple(
        sorted(
            items,
            key=workspace_item_sort_key,
        )
    )


def _build_next_items() -> tuple[
    WorkspaceItem,
    ...
]:
    recommendations = (
        get_executive_recommendations()
    )

    items = []

    for index, recommendation in enumerate(
        recommendations[:3],
        start=1,
    ):
        destination_id = None

        if (
            recommendation.source_app_id
            == "observatory"
        ):
            destination_id = "tower-observatory"

        elif (
            recommendation.source_app_id
            == "teller"
        ):
            destination_id = "tower-teller"

        elif (
            recommendation.source_app_id
            == "grounds"
        ):
            destination_id = "tower-grounds"

        else:
            destination_id = (
                "clouds-priority-board"
            )

        items.append(
            WorkspaceItem(
                item_id=(
                    f"workspace-next-{index}"
                ),
                kind=WorkspaceItemKind.PRIORITY.value,
                title=recommendation.title,
                summary=recommendation.summary,
                explanation=(
                    "This recommendation is derived from "
                    "the executive priority and dashboard "
                    "composition layers."
                ),
                owner_prompt=(
                    recommendation.owner_action
                ),
                priority=(
                    WorkspacePriority.HIGH.value
                    if index == 1
                    else (
                        WorkspacePriority.ELEVATED.value
                    )
                ),
                health=WorkspaceHealth.WATCH.value,
                source_section_id="priorities",
                source_app_id=(
                    recommendation.source_app_id
                ),
                source_lane_id=(
                    recommendation.source_lane_id
                ),
                navigation_action=(
                    _navigation_action(
                        destination_id,
                        action_id=(
                            f"workspace-next-{index}-open"
                        ),
                        label="Review next",
                        display_order=index * 10,
                    )
                ),
                source_integrity_verified=True,
                execution_performed=False,
                display_order=index * 10,
            )
        )

    return tuple(
        sorted(
            items,
            key=workspace_item_sort_key,
        )
    )


def _build_watch_items() -> tuple[
    WorkspaceItem,
    ...
]:
    attention = get_owner_attention_surface()
    today = get_today_surface()

    items = []

    for index, card in enumerate(
        today.watch,
        start=1,
    ):
        destination_id = (
            "tower-teller"
            if card.source_app_id == "teller"
            else "clouds-today"
        )

        items.append(
            WorkspaceItem(
                item_id=(
                    f"workspace-watch-today-{index}"
                ),
                kind=WorkspaceItemKind.ATTENTION.value,
                title=card.title,
                summary=card.summary,
                explanation=(
                    "This item does not outrank the current "
                    "focus, but Clouds is keeping it visible "
                    "for owner awareness."
                ),
                owner_prompt=(
                    card.owner_action_label
                ),
                priority=WorkspacePriority.ELEVATED.value,
                health=WorkspaceHealth.WATCH.value,
                source_section_id="today",
                source_app_id=card.source_app_id,
                source_lane_id=card.source_lane_id,
                navigation_action=(
                    _navigation_action(
                        destination_id,
                        action_id=(
                            f"workspace-watch-today-{index}-open"
                        ),
                        label="Review watch item",
                        display_order=index * 10,
                    )
                ),
                source_integrity_verified=(
                    card.source_integrity_verified
                ),
                execution_performed=False,
                display_order=index * 10,
            )
        )

    offset = 100

    for index, card in enumerate(
        attention.informational,
        start=1,
    ):
        destination_id = (
            "tower-teller"
            if card.source_app_id == "teller"
            else "clouds-owner-attention"
        )

        items.append(
            WorkspaceItem(
                item_id=(
                    f"workspace-watch-attention-{index}"
                ),
                kind=WorkspaceItemKind.ATTENTION.value,
                title=card.title,
                summary=card.summary,
                explanation=(
                    "This is informational owner attention. "
                    "No Clouds execution is implied."
                ),
                owner_prompt=(
                    card.owner_action_label
                ),
                priority=WorkspacePriority.ROUTINE.value,
                health=WorkspaceHealth.WATCH.value,
                source_section_id="attention",
                source_app_id=card.source_app_id,
                source_lane_id=card.source_lane_id,
                navigation_action=(
                    _navigation_action(
                        destination_id,
                        action_id=(
                            f"workspace-watch-attention-{index}-open"
                        ),
                        label="Review attention",
                        display_order=offset + index * 10,
                    )
                ),
                source_integrity_verified=(
                    card.source_integrity_verified
                ),
                execution_performed=False,
                display_order=offset + index * 10,
            )
        )

    return tuple(
        sorted(
            items,
            key=workspace_item_sort_key,
        )
    )


def _build_section_items() -> tuple[
    WorkspaceItem,
    ...
]:
    sections = get_executive_dashboard_sections()

    destination_lookup = {
        "today": "clouds-today",
        "priorities": "clouds-priority-board",
        "attention": "clouds-owner-attention",
        "mission_lanes": "clouds-mission-lanes",
        "applications": "clouds-applications",
        "readiness": "clouds-readiness",
    }

    items = []

    for index, detail in enumerate(
        sections,
        start=1,
    ):
        summary = detail.summary

        items.append(
            WorkspaceItem(
                item_id=(
                    "workspace-section-"
                    f"{summary.section_id}"
                ),
                kind=WorkspaceItemKind.SECTION.value,
                title=summary.title,
                summary=summary.summary,
                explanation=(
                    summary.subtitle
                ),
                owner_prompt=(
                    detail.owner_questions[0]
                    if detail.owner_questions
                    else "Review this section."
                ),
                priority=(
                    WorkspacePriority.HIGH.value
                    if summary.health
                    in {"blocked", "attention"}
                    else WorkspacePriority.ROUTINE.value
                ),
                health=_map_health(
                    summary.health
                ),
                source_section_id=(
                    summary.section_id
                ),
                source_app_id=None,
                source_lane_id=None,
                navigation_action=(
                    _navigation_action(
                        destination_lookup[
                            summary.section_id
                        ],
                        action_id=(
                            "workspace-section-"
                            f"{summary.section_id}-open"
                        ),
                        label=(
                            f"Open {summary.title}"
                        ),
                        display_order=index * 10,
                    )
                ),
                source_integrity_verified=(
                    summary
                    .source_integrity_verified
                ),
                execution_performed=False,
                display_order=index * 10,
            )
        )

    return tuple(
        sorted(
            items,
            key=workspace_item_sort_key,
        )
    )


def _build_application_items() -> tuple[
    WorkspaceItem,
    ...
]:
    destinations = (
        get_executive_navigation_destinations()
    )

    tower_destinations = [
        destination
        for destination in destinations
        if destination.navigation_mode
        == WorkspaceNavigationMode
        .TOWER_HANDOFF.value
    ]

    items = []

    for index, destination in enumerate(
        tower_destinations,
        start=1,
    ):
        items.append(
            WorkspaceItem(
                item_id=(
                    "workspace-app-"
                    f"{destination.destination_id}"
                ),
                kind=(
                    WorkspaceItemKind
                    .DESTINATION.value
                ),
                title=destination.label,
                summary=destination.description,
                explanation=(
                    "This destination is visible in Clouds, "
                    "but Tower retains access authority."
                ),
                owner_prompt=(
                    "Request Tower-mediated entry."
                    if destination.availability
                    != "reserved"
                    else (
                        "Keep this destination visible "
                        "until it becomes available."
                    )
                ),
                priority=(
                    WorkspacePriority.HIGH.value
                    if destination.source_app_id
                    == "observatory"
                    else WorkspacePriority.ROUTINE.value
                ),
                health=(
                    WorkspaceHealth.WATCH.value
                    if destination.availability
                    == "reserved"
                    else WorkspaceHealth.HEALTHY.value
                ),
                source_section_id=(
                    destination.source_section_id
                ),
                source_app_id=(
                    destination.source_app_id
                ),
                source_lane_id=(
                    destination.source_lane_id
                ),
                navigation_action=(
                    WorkspaceNavigationAction(
                        action_id=(
                            "workspace-app-"
                            f"{destination.destination_id}-open"
                        ),
                        label=(
                            f"Open {destination.label}"
                        ),
                        destination_id=(
                            destination.destination_id
                        ),
                        open_route=(
                            destination.open_route
                        ),
                        navigation_mode=(
                            destination.navigation_mode
                        ),
                        requires_tower=(
                            destination.requires_tower
                        ),
                        requires_owner_permission=(
                            destination
                            .requires_owner_permission
                        ),
                        requires_step_up=(
                            destination.requires_step_up
                        ),
                        clouds_executes_navigation=False,
                        downstream_execution_performed=False,
                        display_order=index * 10,
                    )
                ),
                source_integrity_verified=True,
                execution_performed=False,
                display_order=index * 10,
            )
        )

    return tuple(
        sorted(
            items,
            key=workspace_item_sort_key,
        )
    )


def _build_readiness_items() -> tuple[
    WorkspaceItem,
    ...
]:
    summary = (
        get_executive_dashboard_summary()
    )

    destination = (
        get_executive_navigation_destination(
            "clouds-readiness"
        )
    )

    item = WorkspaceItem(
        item_id="workspace-readiness-overall",
        kind=WorkspaceItemKind.READINESS.value,
        title="Overall Readiness",
        summary=(
            f"Combined ecosystem readiness is "
            f"{summary.readiness_score}% "
            f"({summary.readiness_state})."
        ),
        explanation=(
            "This score is a Clouds roll-up of the "
            "application and mission-lane readiness "
            "projections already established in the "
            "executive dashboard."
        ),
        owner_prompt=(
            "Review blocked priorities and active "
            "owner-attention items before broader activation."
        ),
        priority=(
            WorkspacePriority.HIGH.value
            if summary.readiness_score < 50
            else WorkspacePriority.ELEVATED.value
        ),
        health=_map_health(
            summary.health.overall_health
        ),
        source_section_id="readiness",
        source_app_id=None,
        source_lane_id=None,
        navigation_action=(
            WorkspaceNavigationAction(
                action_id=(
                    "workspace-readiness-open"
                ),
                label="Review readiness",
                destination_id=(
                    destination.destination_id
                ),
                open_route=destination.open_route,
                navigation_mode=(
                    destination.navigation_mode
                ),
                requires_tower=False,
                requires_owner_permission=False,
                requires_step_up=False,
                clouds_executes_navigation=False,
                downstream_execution_performed=False,
                display_order=10,
            )
        ),
        source_integrity_verified=(
            summary.source_integrity_verified
        ),
        execution_performed=False,
        display_order=10,
    )

    return (item,)


def _panel(
    *,
    panel_id: str,
    kind: str,
    title: str,
    subtitle: str,
    items: tuple[WorkspaceItem, ...],
    display_order: int,
) -> WorkspacePanel:
    if any(
        item.health == WorkspaceHealth.BLOCKED.value
        for item in items
    ):
        health = WorkspaceHealth.BLOCKED.value

    elif any(
        item.health == WorkspaceHealth.ATTENTION.value
        for item in items
    ):
        health = WorkspaceHealth.ATTENTION.value

    elif any(
        item.health == WorkspaceHealth.WATCH.value
        for item in items
    ):
        health = WorkspaceHealth.WATCH.value

    else:
        health = WorkspaceHealth.HEALTHY.value

    return WorkspacePanel(
        panel_id=panel_id,
        kind=kind,
        title=title,
        subtitle=subtitle,
        items=items,
        item_count=len(items),
        health=health,
        source_integrity_verified=all(
            item.source_integrity_verified
            for item in items
        ),
        execution_performed=False,
        display_order=display_order,
    )


def get_executive_owner_workspace_panels(
) -> tuple[
    WorkspacePanel,
    ...
]:
    panels = (
        _panel(
            panel_id="workspace-panel-now",
            kind=WorkspacePanelKind.NOW.value,
            title="Now",
            subtitle=(
                "The most important owner focus "
                "and strategic priority right now."
            ),
            items=_build_now_items(),
            display_order=10,
        ),
        _panel(
            panel_id="workspace-panel-next",
            kind=WorkspacePanelKind.NEXT.value,
            title="Next",
            subtitle=(
                "The next owner priorities after "
                "the immediate focus."
            ),
            items=_build_next_items(),
            display_order=20,
        ),
        _panel(
            panel_id="workspace-panel-watch",
            kind=WorkspacePanelKind.WATCH.value,
            title="Watch",
            subtitle=(
                "Items Clouds is keeping visible "
                "without moving them ahead of Now."
            ),
            items=_build_watch_items(),
            display_order=30,
        ),
        _panel(
            panel_id="workspace-panel-sections",
            kind=WorkspacePanelKind.SECTIONS.value,
            title="Executive Sections",
            subtitle=(
                "Direct access to the six fixed "
                "executive dashboard sections."
            ),
            items=_build_section_items(),
            display_order=40,
        ),
        _panel(
            panel_id="workspace-panel-applications",
            kind=WorkspacePanelKind.APPLICATIONS.value,
            title="Applications",
            subtitle=(
                "Tower-mediated downstream "
                "application destinations."
            ),
            items=_build_application_items(),
            display_order=50,
        ),
        _panel(
            panel_id="workspace-panel-readiness",
            kind=WorkspacePanelKind.READINESS.value,
            title="Readiness",
            subtitle=(
                "Combined owner-command readiness "
                "and activation awareness."
            ),
            items=_build_readiness_items(),
            display_order=60,
        ),
    )

    return tuple(
        sorted(
            panels,
            key=workspace_panel_sort_key,
        )
    )


def get_executive_owner_workspace_items(
) -> tuple[
    WorkspaceItem,
    ...
]:
    return tuple(
        item
        for panel
        in get_executive_owner_workspace_panels()
        for item
        in panel.items
    )


def get_executive_owner_workspace_panel(
    panel_id: str,
) -> WorkspacePanel:
    for panel in (
        get_executive_owner_workspace_panels()
    ):
        if panel.panel_id == panel_id:
            return panel

    raise KeyError(
        "Unknown executive owner workspace panel: "
        f"{panel_id}"
    )


def get_executive_owner_workspace_item(
    item_id: str,
) -> WorkspaceItem:
    for item in (
        get_executive_owner_workspace_items()
    ):
        if item.item_id == item_id:
            return item

    raise KeyError(
        "Unknown executive owner workspace item: "
        f"{item_id}"
    )


def filter_executive_owner_workspace_items(
    *,
    kind: str | None = None,
    priority: str | None = None,
    health: str | None = None,
    source_section_id: str | None = None,
    source_app_id: str | None = None,
    source_lane_id: str | None = None,
    navigation_mode: str | None = None,
) -> tuple[
    WorkspaceItem,
    ...
]:
    return filter_workspace_items(
        get_executive_owner_workspace_items(),
        kind=kind,
        priority=priority,
        health=health,
        source_section_id=source_section_id,
        source_app_id=source_app_id,
        source_lane_id=source_lane_id,
        navigation_mode=navigation_mode,
    )


def _build_headline() -> WorkspaceHeadline:
    dashboard = get_executive_dashboard()
    summary = dashboard.summary
    today = get_today_surface()

    focus = (
        today.focus[0]
        if today.focus
        else None
    )

    if summary.health.overall_health == "blocked":
        statement = (
            "Your command workspace has active progress, "
            "but at least one strategic priority remains blocked."
        )

    elif summary.health.overall_health == "attention":
        statement = (
            "Your command workspace is moving, with "
            "owner attention required."
        )

    elif summary.health.overall_health == "watch":
        statement = (
            "Your command workspace is stable, with "
            "a few items to keep under watch."
        )

    else:
        statement = (
            "Your command workspace is healthy and "
            "does not currently require intervention."
        )

    explanation = (
        f"Clouds is tracking "
        f"{summary.monitored_application_count} applications, "
        f"{summary.monitored_mission_lane_count} mission lanes, "
        f"{summary.priority_count} strategic priorities, and "
        f"{summary.attention_count} attention items. "
        f"Combined readiness is {summary.readiness_score}%."
    )

    return WorkspaceHeadline(
        title="Owner Command Workspace",
        statement=statement,
        explanation=explanation,
        overall_health=(
            summary.health.overall_health
        ),
        readiness_score=(
            summary.readiness_score
        ),
        readiness_state=(
            summary.readiness_state
        ),
        action_required_count=(
            summary.action_required_count
        ),
        blocked_priority_count=(
            summary.blocked_priority_count
        ),
        top_focus_title=(
            focus.title
            if focus
            else None
        ),
        top_focus_app_id=(
            focus.source_app_id
            if focus
            else None
        ),
        source_integrity_verified=(
            summary.source_integrity_verified
        ),
        execution_performed=False,
    )


def get_executive_owner_workspace_summary(
) -> WorkspaceSummary:
    panels = (
        get_executive_owner_workspace_panels()
    )

    items = tuple(
        item
        for panel in panels
        for item in panel.items
    )

    dashboard_summary = (
        get_executive_dashboard_summary()
    )

    navigation_summary = (
        get_executive_navigation_map_summary()
    )

    internal_navigation_count = sum(
        1
        for item in items
        if (
            item.navigation_action
            is not None
            and item.navigation_action.navigation_mode
            == WorkspaceNavigationMode
            .CLOUDS_INTERNAL.value
        )
    )

    tower_handoff_count = sum(
        1
        for item in items
        if (
            item.navigation_action
            is not None
            and item.navigation_action.navigation_mode
            == WorkspaceNavigationMode
            .TOWER_HANDOFF.value
        )
    )

    tower_boundary_preserved = (
        navigation_summary
        .tower_boundary_preserved
        and all(
            (
                item.navigation_action is None
                or (
                    not item.navigation_action
                    .requires_tower
                )
                or (
                    item.navigation_action
                    .navigation_mode
                    == WorkspaceNavigationMode
                    .TOWER_HANDOFF.value
                    and item.navigation_action
                    .clouds_executes_navigation
                    is False
                )
            )
            for item in items
        )
    )

    return WorkspaceSummary(
        panel_count=len(panels),
        item_count=len(items),
        internal_navigation_count=(
            internal_navigation_count
        ),
        tower_handoff_count=(
            tower_handoff_count
        ),
        action_required_count=(
            dashboard_summary
            .action_required_count
        ),
        blocked_priority_count=(
            dashboard_summary
            .blocked_priority_count
        ),
        readiness_score=(
            dashboard_summary
            .readiness_score
        ),
        overall_health=(
            dashboard_summary
            .health
            .overall_health
        ),
        source_integrity_verified=all(
            panel.source_integrity_verified
            for panel in panels
        ),
        tower_boundary_preserved=(
            tower_boundary_preserved
        ),
        execution_performed=False,
    )


def get_executive_owner_workspace(
) -> ExecutiveOwnerWorkspace:
    return ExecutiveOwnerWorkspace(
        title="Executive Owner Command Workspace",
        subtitle=(
            "A single owner workspace for Now, Next, "
            "Watch, executive sections, applications, "
            "and readiness."
        ),
        headline=_build_headline(),
        summary=(
            get_executive_owner_workspace_summary()
        ),
        panels=(
            get_executive_owner_workspace_panels()
        ),
        allowed_clouds_actions=(
            ALLOWED_CLOUDS_ACTIONS
        ),
        prohibited_clouds_actions=(
            PROHIBITED_CLOUDS_ACTIONS
        ),
        boundary_notice=(
            "Clouds explains, prioritizes, and maps "
            "owner work. Tower retains authentication, "
            "permission, step-up, and downstream entry. "
            "Clouds performs no operational execution."
        ),
    )


def get_executive_owner_workspace_payload(
) -> dict:
    return (
        get_executive_owner_workspace()
        .to_dict()
    )


def get_executive_owner_workspace_panel_payload(
    panel_id: str,
) -> dict:
    return (
        get_executive_owner_workspace_panel(
            panel_id
        ).to_dict()
    )


def get_executive_owner_workspace_item_payload(
    item_id: str,
) -> dict:
    return (
        get_executive_owner_workspace_item(
            item_id
        ).to_dict()
    )


def get_clouds_gp010_status_payload() -> dict:
    gp009 = get_clouds_gp009_status_payload()

    workspace = (
        get_executive_owner_workspace()
    )

    summary = workspace.summary

    safe_to_continue = (
        gp009["status"] == "ready"
        and gp009["safe_to_continue"] is True
        and summary.panel_count == 6
        and summary.item_count == 18
        and summary.source_integrity_verified
        is True
        and summary.tower_boundary_preserved
        is True
        and summary.execution_performed
        is False
        and workspace.headline
        .execution_performed
        is False
        and all(
            panel.execution_performed
            is False
            for panel in workspace.panels
        )
        and all(
            item.execution_performed
            is False
            for panel in workspace.panels
            for item in panel.items
        )
        and all(
            (
                item.navigation_action is None
                or (
                    item.navigation_action
                    .clouds_executes_navigation
                    is False
                    and item.navigation_action
                    .downstream_execution_performed
                    is False
                )
            )
            for panel in workspace.panels
            for item in panel.items
        )
    )

    return {
        "pack": "GP010",
        "section": (
            "EXECUTIVE OWNER COMMAND WORKSPACE SURFACE"
        ),
        "status": (
            "ready"
            if safe_to_continue
            else "blocked"
        ),
        "safe_to_continue": safe_to_continue,
        "panel_count": summary.panel_count,
        "item_count": summary.item_count,
        "internal_navigation_count": (
            summary.internal_navigation_count
        ),
        "tower_handoff_count": (
            summary.tower_handoff_count
        ),
        "action_required_count": (
            summary.action_required_count
        ),
        "blocked_priority_count": (
            summary.blocked_priority_count
        ),
        "readiness_score": (
            summary.readiness_score
        ),
        "overall_health": (
            summary.overall_health
        ),
        "source_integrity_verified": (
            summary.source_integrity_verified
        ),
        "tower_boundary_preserved": (
            summary.tower_boundary_preserved
        ),
        "workspace_execution_performed": False,
        "downstream_execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP011 — EXECUTIVE OWNER WORKSPACE "
            "DETAIL / ACTION INTENT SURFACE"
        ),
    }
