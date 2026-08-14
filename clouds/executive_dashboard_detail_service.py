"""
Service layer for Executive Dashboard Section Details.

Uses only compact local Clouds surfaces from GP002–GP007.
"""

from __future__ import annotations

try:
    from .app_registry_surface_service import (
        get_app_registry_surface,
    )
    from .executive_dashboard_detail import (
        ExecutiveDashboardSectionDetail,
        ExecutiveDashboardSectionSummary,
        ExecutiveDashboardSectionSurface,
        ExecutiveSectionHealth,
        ExecutiveSectionId,
        ExecutiveSectionMetric,
        ExecutiveSectionMetricKind,
        ExecutiveSectionNavigationMode,
        ExecutiveSectionNavigationTarget,
        ExecutiveSectionReadiness,
        ExecutiveSectionRecommendation,
        ExecutiveSectionRecommendationKind,
        filter_section_details,
        metric_sort_key,
        navigation_target_sort_key,
        recommendation_sort_key,
        section_sort_key,
    )
    from .executive_dashboard_service import (
        get_executive_dashboard,
        get_executive_dashboard_summary,
        get_executive_recommendations,
    )
    from .mission_lane_surface_service import (
        get_mission_lane_surface,
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
    from app_registry_surface_service import (
        get_app_registry_surface,
    )
    from executive_dashboard_detail import (
        ExecutiveDashboardSectionDetail,
        ExecutiveDashboardSectionSummary,
        ExecutiveDashboardSectionSurface,
        ExecutiveSectionHealth,
        ExecutiveSectionId,
        ExecutiveSectionMetric,
        ExecutiveSectionMetricKind,
        ExecutiveSectionNavigationMode,
        ExecutiveSectionNavigationTarget,
        ExecutiveSectionReadiness,
        ExecutiveSectionRecommendation,
        ExecutiveSectionRecommendationKind,
        filter_section_details,
        metric_sort_key,
        navigation_target_sort_key,
        recommendation_sort_key,
        section_sort_key,
    )
    from executive_dashboard_service import (
        get_executive_dashboard,
        get_executive_dashboard_summary,
        get_executive_recommendations,
    )
    from mission_lane_surface_service import (
        get_mission_lane_surface,
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
    "Display executive section summaries",
    "Display executive section metrics",
    "Display executive section health",
    "Display executive section readiness",
    "Display section recommendations",
    "Display source application and mission-lane links",
    "Provide safe Clouds and Tower navigation references",
    "Filter executive section details",
)


PROHIBITED_CLOUDS_ACTIONS = (
    "Clouds cannot authenticate the owner",
    "Clouds cannot grant application permission",
    "Clouds cannot perform Tower step-up",
    "Clouds cannot approve an owner decision",
    "Clouds cannot execute a recommendation",
    "Clouds cannot trade capital",
    "Clouds cannot move money",
    "Clouds cannot retrieve raw Vault evidence",
    "Clouds cannot operate property workflows",
)


SECTION_QUESTIONS = {
    ExecutiveSectionId.TODAY.value: (
        "What requires owner attention today?",
        "What should remain under watch?",
        "Which open target should stay visible?",
    ),
    ExecutiveSectionId.PRIORITIES.value: (
        "What strategic priority should advance first?",
        "Which priority remains blocked?",
        "Which owner action creates the greatest progress?",
    ),
    ExecutiveSectionId.ATTENTION.value: (
        "What requires owner review?",
        "What is informational only?",
        "Which application owns the underlying action?",
    ),
    ExecutiveSectionId.MISSION_LANES.value: (
        "Which mission lanes are advancing?",
        "Which lanes remain reserved or held?",
        "Which owning application should be opened?",
    ),
    ExecutiveSectionId.APPLICATIONS.value: (
        "Which applications are active?",
        "Which applications remain reserved?",
        "Which application requires owner awareness?",
    ),
    ExecutiveSectionId.READINESS.value: (
        "What is the combined readiness score?",
        "Which readiness states reduce the score?",
        "What must advance before broader activation?",
    ),
}


def _metric(
    metric_id: str,
    label: str,
    value,
    kind: str,
    meaning: str,
    display_order: int,
) -> ExecutiveSectionMetric:
    return ExecutiveSectionMetric(
        metric_id=metric_id,
        label=label,
        value=value,
        kind=kind,
        meaning=meaning,
        display_order=display_order,
    )


def _recommendation(
    *,
    recommendation_id: str,
    kind: str,
    title: str,
    summary: str,
    owner_action: str,
    source_app_id: str | None,
    source_lane_id: str | None,
    open_route: str | None,
    navigation_mode: str,
    display_order: int,
) -> ExecutiveSectionRecommendation:
    return ExecutiveSectionRecommendation(
        recommendation_id=(
            recommendation_id
        ),
        kind=kind,
        title=title,
        summary=summary,
        owner_action=owner_action,
        source_app_id=source_app_id,
        source_lane_id=source_lane_id,
        open_route=open_route,
        navigation_mode=navigation_mode,
        execution_performed=False,
        display_order=display_order,
    )


def _navigation_target(
    *,
    target_id: str,
    label: str,
    open_route: str,
    navigation_mode: str,
    source_app_id: str | None,
    source_lane_id: str | None,
    display_order: int,
) -> ExecutiveSectionNavigationTarget:
    return ExecutiveSectionNavigationTarget(
        target_id=target_id,
        label=label,
        open_route=open_route,
        navigation_mode=navigation_mode,
        source_app_id=source_app_id,
        source_lane_id=source_lane_id,
        execution_performed=False,
        display_order=display_order,
    )


def _today_detail() -> (
    ExecutiveDashboardSectionDetail
):
    today = get_today_surface()

    focus = today.focus[0] if today.focus else None
    watch = today.watch[0] if today.watch else None
    first_target = (
        today.targets[0]
        if today.targets
        else None
    )

    health = (
        ExecutiveSectionHealth.ATTENTION.value
        if today.header.action_required_count
        else ExecutiveSectionHealth.WATCH.value
    )

    readiness = (
        ExecutiveSectionReadiness.ADVANCING.value
        if today.header.focus_count
        else ExecutiveSectionReadiness.BUILDING.value
    )

    summary = ExecutiveDashboardSectionSummary(
        section_id=ExecutiveSectionId.TODAY.value,
        title="Today",
        subtitle=(
            "The owner's immediate focus, watch list, "
            "and visible open targets."
        ),
        summary=(
            f"{today.header.focus_count} focus item, "
            f"{today.header.watch_count} watch item, and "
            f"{today.header.target_count} open targets."
        ),
        health=health,
        readiness=readiness,
        readiness_score=70,
        primary_metric=today.header.focus_count,
        secondary_metric=(
            today.header.watch_count
        ),
        source_integrity_verified=all(
            item.source_integrity_verified
            for item in today.all_cards
        ),
        execution_performed=False,
    )

    metrics = (
        _metric(
            "today-focus-count",
            "Focus",
            today.header.focus_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "Items requiring immediate owner focus.",
            10,
        ),
        _metric(
            "today-watch-count",
            "Watch",
            today.header.watch_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "Items requiring continued awareness.",
            20,
        ),
        _metric(
            "today-target-count",
            "Open Targets",
            today.header.target_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "Visible future or reserved targets.",
            30,
        ),
        _metric(
            "today-action-required-count",
            "Action Required",
            today.header.action_required_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "Today items requiring owner review.",
            40,
        ),
    )

    recommendations = []

    if focus is not None:
        recommendations.append(
            _recommendation(
                recommendation_id=(
                    "today-section-top"
                ),
                kind=(
                    ExecutiveSectionRecommendationKind
                    .TOP
                    .value
                ),
                title=focus.title,
                summary=focus.summary,
                owner_action=(
                    focus.owner_action_label
                ),
                source_app_id=(
                    focus.source_app_id
                ),
                source_lane_id=(
                    focus.source_lane_id
                ),
                open_route=focus.open_route,
                navigation_mode=(
                    focus.navigation_mode
                ),
                display_order=10,
            )
        )

    if watch is not None:
        recommendations.append(
            _recommendation(
                recommendation_id=(
                    "today-section-second"
                ),
                kind=(
                    ExecutiveSectionRecommendationKind
                    .SECOND
                    .value
                ),
                title=watch.title,
                summary=watch.summary,
                owner_action=(
                    watch.owner_action_label
                ),
                source_app_id=(
                    watch.source_app_id
                ),
                source_lane_id=(
                    watch.source_lane_id
                ),
                open_route=watch.open_route,
                navigation_mode=(
                    watch.navigation_mode
                ),
                display_order=20,
            )
        )

    if first_target is not None:
        recommendations.append(
            _recommendation(
                recommendation_id=(
                    "today-section-watch-next"
                ),
                kind=(
                    ExecutiveSectionRecommendationKind
                    .WATCH_NEXT
                    .value
                ),
                title=first_target.title,
                summary=first_target.summary,
                owner_action=(
                    first_target
                    .owner_action_label
                ),
                source_app_id=(
                    first_target.source_app_id
                ),
                source_lane_id=(
                    first_target.source_lane_id
                ),
                open_route=(
                    first_target.open_route
                ),
                navigation_mode=(
                    first_target.navigation_mode
                ),
                display_order=30,
            )
        )

    navigation_targets = (
        _navigation_target(
            target_id="today-section-open",
            label="Open Today",
            open_route="/clouds/today",
            navigation_mode=(
                ExecutiveSectionNavigationMode
                .CLOUDS_INTERNAL
                .value
            ),
            source_app_id=None,
            source_lane_id=None,
            display_order=10,
        ),
    )

    linked_app_ids = tuple(
        sorted(
            {
                item.source_app_id
                for item in today.all_cards
                if item.source_app_id
            }
        )
    )

    linked_lane_ids = tuple(
        sorted(
            {
                item.source_lane_id
                for item in today.all_cards
                if item.source_lane_id
            }
        )
    )

    return ExecutiveDashboardSectionDetail(
        summary=summary,
        metrics=tuple(
            sorted(
                metrics,
                key=metric_sort_key,
            )
        ),
        recommendations=tuple(
            sorted(
                recommendations,
                key=recommendation_sort_key,
            )
        ),
        navigation_targets=tuple(
            sorted(
                navigation_targets,
                key=navigation_target_sort_key,
            )
        ),
        linked_app_ids=linked_app_ids,
        linked_mission_lane_ids=(
            linked_lane_ids
        ),
        owner_questions=SECTION_QUESTIONS[
            ExecutiveSectionId.TODAY.value
        ],
        allowed_clouds_actions=(
            ALLOWED_CLOUDS_ACTIONS
        ),
        prohibited_clouds_actions=(
            PROHIBITED_CLOUDS_ACTIONS
        ),
        downstream_execution_performed=False,
        display_order=10,
    )


def _priorities_detail() -> (
    ExecutiveDashboardSectionDetail
):
    board = get_priority_board()

    health = (
        ExecutiveSectionHealth.BLOCKED.value
        if board.summary.blocked_count
        else ExecutiveSectionHealth.WATCH.value
    )

    readiness = (
        ExecutiveSectionReadiness.BUILDING.value
        if board.summary.blocked_count
        else ExecutiveSectionReadiness.ADVANCING.value
    )

    summary = ExecutiveDashboardSectionSummary(
        section_id=(
            ExecutiveSectionId.PRIORITIES.value
        ),
        title="Priority Board",
        subtitle=(
            "Strategic owner priorities across the "
            "Simplee ecosystem."
        ),
        summary=(
            f"{board.summary.total_priority_count} "
            "priorities with "
            f"{board.summary.blocked_count} blocked."
        ),
        health=health,
        readiness=readiness,
        readiness_score=60,
        primary_metric=(
            board.summary.critical_count
            + board.summary.high_count
        ),
        secondary_metric=(
            board.summary.blocked_count
        ),
        source_integrity_verified=(
            board.summary.source_integrity_verified
        ),
        execution_performed=False,
    )

    metrics = (
        _metric(
            "priority-total-count",
            "Total Priorities",
            board.summary.total_priority_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "All strategic priorities on the board.",
            10,
        ),
        _metric(
            "priority-critical-count",
            "Critical",
            board.summary.critical_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "Critical strategic priorities.",
            20,
        ),
        _metric(
            "priority-high-count",
            "High",
            board.summary.high_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "High strategic priorities.",
            30,
        ),
        _metric(
            "priority-blocked-count",
            "Blocked",
            board.summary.blocked_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "Priorities currently blocked.",
            40,
        ),
        _metric(
            "priority-highest-score",
            "Highest Score",
            board.summary.highest_priority_score,
            ExecutiveSectionMetricKind.SCORE.value,
            "Highest strategic priority score.",
            50,
        ),
    )

    recommendations = []

    if board.top_recommendation is not None:
        card = board.top_recommendation

        recommendations.append(
            _recommendation(
                recommendation_id=(
                    "priorities-section-top"
                ),
                kind=(
                    ExecutiveSectionRecommendationKind
                    .TOP
                    .value
                ),
                title=card.title,
                summary=(
                    card.priority_explanation
                ),
                owner_action=(
                    card.recommended_owner_action
                ),
                source_app_id=(
                    card.source_app_id
                ),
                source_lane_id=(
                    card.source_lane_id
                ),
                open_route=card.open_route,
                navigation_mode=(
                    card.navigation_mode
                ),
                display_order=10,
            )
        )

    if board.second_recommendation is not None:
        card = board.second_recommendation

        recommendations.append(
            _recommendation(
                recommendation_id=(
                    "priorities-section-second"
                ),
                kind=(
                    ExecutiveSectionRecommendationKind
                    .SECOND
                    .value
                ),
                title=card.title,
                summary=(
                    card.priority_explanation
                ),
                owner_action=(
                    card.recommended_owner_action
                ),
                source_app_id=(
                    card.source_app_id
                ),
                source_lane_id=(
                    card.source_lane_id
                ),
                open_route=card.open_route,
                navigation_mode=(
                    card.navigation_mode
                ),
                display_order=20,
            )
        )

    blocked = (
        board.blocked[0]
        if board.blocked
        else None
    )

    if blocked is not None:
        recommendations.append(
            _recommendation(
                recommendation_id=(
                    "priorities-section-watch-next"
                ),
                kind=(
                    ExecutiveSectionRecommendationKind
                    .WATCH_NEXT
                    .value
                ),
                title=blocked.title,
                summary=blocked.summary,
                owner_action=(
                    blocked.recommended_owner_action
                ),
                source_app_id=(
                    blocked.source_app_id
                ),
                source_lane_id=(
                    blocked.source_lane_id
                ),
                open_route=blocked.open_route,
                navigation_mode=(
                    blocked.navigation_mode
                ),
                display_order=30,
            )
        )

    navigation_targets = (
        _navigation_target(
            target_id="priorities-section-open",
            label="Open Priority Board",
            open_route="/clouds/priorities",
            navigation_mode=(
                ExecutiveSectionNavigationMode
                .CLOUDS_INTERNAL
                .value
            ),
            source_app_id=None,
            source_lane_id=None,
            display_order=10,
        ),
    )

    return ExecutiveDashboardSectionDetail(
        summary=summary,
        metrics=tuple(
            sorted(
                metrics,
                key=metric_sort_key,
            )
        ),
        recommendations=tuple(
            sorted(
                recommendations,
                key=recommendation_sort_key,
            )
        ),
        navigation_targets=navigation_targets,
        linked_app_ids=tuple(
            sorted(
                {
                    item.source_app_id
                    for item in board.all_priorities
                }
            )
        ),
        linked_mission_lane_ids=tuple(
            sorted(
                {
                    item.source_lane_id
                    for item in board.all_priorities
                }
            )
        ),
        owner_questions=SECTION_QUESTIONS[
            ExecutiveSectionId
            .PRIORITIES
            .value
        ],
        allowed_clouds_actions=(
            ALLOWED_CLOUDS_ACTIONS
        ),
        prohibited_clouds_actions=(
            PROHIBITED_CLOUDS_ACTIONS
        ),
        downstream_execution_performed=False,
        display_order=20,
    )


def _attention_detail() -> (
    ExecutiveDashboardSectionDetail
):
    attention = get_owner_attention_surface()

    health = (
        ExecutiveSectionHealth.ATTENTION.value
        if (
            attention.summary
            .action_required_count
        )
        else ExecutiveSectionHealth.HEALTHY.value
    )

    readiness = (
        ExecutiveSectionReadiness.ADVANCING.value
        if attention.summary.source_integrity_verified
        else ExecutiveSectionReadiness.HELD.value
    )

    summary = ExecutiveDashboardSectionSummary(
        section_id=(
            ExecutiveSectionId.ATTENTION.value
        ),
        title="Owner Attention",
        subtitle=(
            "Owner review and awareness across apps "
            "and mission lanes."
        ),
        summary=(
            f"{attention.summary.total_attention_count} "
            "attention items with "
            f"{attention.summary.action_required_count} "
            "requiring owner review."
        ),
        health=health,
        readiness=readiness,
        readiness_score=75,
        primary_metric=(
            attention.summary.action_required_count
        ),
        secondary_metric=(
            attention.summary.informational_count
        ),
        source_integrity_verified=(
            attention.summary
            .source_integrity_verified
        ),
        execution_performed=False,
    )

    metrics = (
        _metric(
            "attention-total-count",
            "Total Attention",
            attention.summary.total_attention_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "All owner-attention records.",
            10,
        ),
        _metric(
            "attention-action-count",
            "Action Required",
            attention.summary.action_required_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "Attention items requiring review.",
            20,
        ),
        _metric(
            "attention-info-count",
            "Informational",
            attention.summary.informational_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "Awareness items without action.",
            30,
        ),
        _metric(
            "attention-high-count",
            "High Priority",
            attention.summary.high_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "High-priority attention items.",
            40,
        ),
    )

    recommendations = []

    if attention.action_required:
        item = attention.action_required[0]

        recommendations.append(
            _recommendation(
                recommendation_id=(
                    "attention-section-top"
                ),
                kind=(
                    ExecutiveSectionRecommendationKind
                    .TOP
                    .value
                ),
                title=item.title,
                summary=item.summary,
                owner_action=(
                    item.owner_action_label
                ),
                source_app_id=(
                    item.source_app_id
                ),
                source_lane_id=(
                    item.source_lane_id
                ),
                open_route=item.open_route,
                navigation_mode=(
                    item.navigation_mode
                ),
                display_order=10,
            )
        )

    if attention.informational:
        item = attention.informational[0]

        recommendations.append(
            _recommendation(
                recommendation_id=(
                    "attention-section-second"
                ),
                kind=(
                    ExecutiveSectionRecommendationKind
                    .SECOND
                    .value
                ),
                title=item.title,
                summary=item.summary,
                owner_action=(
                    item.owner_action_label
                ),
                source_app_id=(
                    item.source_app_id
                ),
                source_lane_id=(
                    item.source_lane_id
                ),
                open_route=item.open_route,
                navigation_mode=(
                    item.navigation_mode
                ),
                display_order=20,
            )
        )

    navigation_targets = (
        _navigation_target(
            target_id="attention-section-open",
            label="Open Owner Attention",
            open_route="/clouds/attention",
            navigation_mode=(
                ExecutiveSectionNavigationMode
                .CLOUDS_INTERNAL
                .value
            ),
            source_app_id=None,
            source_lane_id=None,
            display_order=10,
        ),
    )

    return ExecutiveDashboardSectionDetail(
        summary=summary,
        metrics=metrics,
        recommendations=tuple(
            sorted(
                recommendations,
                key=recommendation_sort_key,
            )
        ),
        navigation_targets=navigation_targets,
        linked_app_ids=tuple(
            sorted(
                {
                    item.source_app_id
                    for item in attention.all_attention
                    if item.source_app_id
                }
            )
        ),
        linked_mission_lane_ids=tuple(
            sorted(
                {
                    item.source_lane_id
                    for item in attention.all_attention
                    if item.source_lane_id
                }
            )
        ),
        owner_questions=SECTION_QUESTIONS[
            ExecutiveSectionId.ATTENTION.value
        ],
        allowed_clouds_actions=(
            ALLOWED_CLOUDS_ACTIONS
        ),
        prohibited_clouds_actions=(
            PROHIBITED_CLOUDS_ACTIONS
        ),
        downstream_execution_performed=False,
        display_order=30,
    )


def _mission_lanes_detail() -> (
    ExecutiveDashboardSectionDetail
):
    lanes = get_mission_lane_surface()

    health = (
        ExecutiveSectionHealth.WATCH.value
        if lanes.summary.watch_lane_count
        else ExecutiveSectionHealth.HEALTHY.value
    )

    readiness = (
        ExecutiveSectionReadiness.BUILDING.value
    )

    summary = ExecutiveDashboardSectionSummary(
        section_id=(
            ExecutiveSectionId
            .MISSION_LANES
            .value
        ),
        title="Mission Lanes",
        subtitle=(
            "Cross-business operating lanes and "
            "their owning applications."
        ),
        summary=(
            f"{lanes.summary.active_lane_count} active "
            "and {lanes.summary.reserved_lane_count} "
            "reserved mission lanes."
        ),
        health=health,
        readiness=readiness,
        readiness_score=50,
        primary_metric=(
            lanes.summary.active_lane_count
        ),
        secondary_metric=(
            lanes.summary.reserved_lane_count
        ),
        source_integrity_verified=True,
        execution_performed=False,
    )

    metrics = (
        _metric(
            "lanes-total-count",
            "Total Lanes",
            lanes.summary.total_lane_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "All registered mission lanes.",
            10,
        ),
        _metric(
            "lanes-active-count",
            "Active",
            lanes.summary.active_lane_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "Currently active mission lanes.",
            20,
        ),
        _metric(
            "lanes-reserved-count",
            "Reserved",
            lanes.summary.reserved_lane_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "Reserved future mission lanes.",
            30,
        ),
        _metric(
            "lanes-watch-count",
            "Watch",
            lanes.summary.watch_lane_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "Mission lanes requiring awareness.",
            40,
        ),
        _metric(
            "lanes-building-count",
            "Building",
            lanes.summary.building_lane_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "Mission lanes in active construction.",
            50,
        ),
    )

    attention_lane = (
        lanes.active_lanes[1]
        if len(lanes.active_lanes) > 1
        else (
            lanes.active_lanes[0]
            if lanes.active_lanes
            else None
        )
    )

    recommendations = []

    if attention_lane is not None:
        recommendations.append(
            _recommendation(
                recommendation_id=(
                    "lanes-section-top"
                ),
                kind=(
                    ExecutiveSectionRecommendationKind
                    .TOP
                    .value
                ),
                title=attention_lane.lane_name,
                summary=(
                    attention_lane.status_summary
                ),
                owner_action=(
                    attention_lane.open_label
                ),
                source_app_id=(
                    attention_lane.owning_app_id
                ),
                source_lane_id=(
                    attention_lane.lane_id
                ),
                open_route=(
                    attention_lane.open_route
                ),
                navigation_mode=(
                    attention_lane.open_mode
                ),
                display_order=10,
            )
        )

    if lanes.reserved_lanes:
        reserved = lanes.reserved_lanes[0]

        recommendations.append(
            _recommendation(
                recommendation_id=(
                    "lanes-section-watch-next"
                ),
                kind=(
                    ExecutiveSectionRecommendationKind
                    .WATCH_NEXT
                    .value
                ),
                title=reserved.lane_name,
                summary=reserved.status_summary,
                owner_action=reserved.open_label,
                source_app_id=(
                    reserved.owning_app_id
                ),
                source_lane_id=reserved.lane_id,
                open_route=reserved.open_route,
                navigation_mode=reserved.open_mode,
                display_order=30,
            )
        )

    navigation_targets = (
        _navigation_target(
            target_id="lanes-section-open",
            label="Open Mission Lanes",
            open_route="/clouds/mission-lanes",
            navigation_mode=(
                ExecutiveSectionNavigationMode
                .CLOUDS_INTERNAL
                .value
            ),
            source_app_id=None,
            source_lane_id=None,
            display_order=10,
        ),
    )

    return ExecutiveDashboardSectionDetail(
        summary=summary,
        metrics=metrics,
        recommendations=tuple(
            sorted(
                recommendations,
                key=recommendation_sort_key,
            )
        ),
        navigation_targets=navigation_targets,
        linked_app_ids=tuple(
            sorted(
                {
                    item.owning_app_id
                    for item in lanes.all_lanes
                }
            )
        ),
        linked_mission_lane_ids=tuple(
            item.lane_id
            for item in lanes.all_lanes
        ),
        owner_questions=SECTION_QUESTIONS[
            ExecutiveSectionId
            .MISSION_LANES
            .value
        ],
        allowed_clouds_actions=(
            ALLOWED_CLOUDS_ACTIONS
        ),
        prohibited_clouds_actions=(
            PROHIBITED_CLOUDS_ACTIONS
        ),
        downstream_execution_performed=False,
        display_order=40,
    )


def _applications_detail() -> (
    ExecutiveDashboardSectionDetail
):
    apps = get_app_registry_surface()

    health = (
        ExecutiveSectionHealth.WATCH.value
        if apps.summary.watch_app_count
        else ExecutiveSectionHealth.HEALTHY.value
    )

    readiness = (
        ExecutiveSectionReadiness.BUILDING.value
    )

    summary = ExecutiveDashboardSectionSummary(
        section_id=(
            ExecutiveSectionId
            .APPLICATIONS
            .value
        ),
        title="Applications",
        subtitle=(
            "Application registry health, readiness, "
            "and safe entry paths."
        ),
        summary=(
            f"{apps.summary.active_app_count} active "
            "and {apps.summary.reserved_app_count} "
            "reserved applications."
        ),
        health=health,
        readiness=readiness,
        readiness_score=55,
        primary_metric=(
            apps.summary.active_app_count
        ),
        secondary_metric=(
            apps.summary.reserved_app_count
        ),
        source_integrity_verified=True,
        execution_performed=False,
    )

    metrics = (
        _metric(
            "apps-total-count",
            "Total Applications",
            apps.summary.total_app_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "All registered applications.",
            10,
        ),
        _metric(
            "apps-active-count",
            "Active",
            apps.summary.active_app_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "Active or summary-ready applications.",
            20,
        ),
        _metric(
            "apps-reserved-count",
            "Reserved",
            apps.summary.reserved_app_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "Applications reserved for later activation.",
            30,
        ),
        _metric(
            "apps-healthy-count",
            "Healthy",
            apps.summary.healthy_app_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "Applications reporting healthy status.",
            40,
        ),
        _metric(
            "apps-watch-count",
            "Watch",
            apps.summary.watch_app_count,
            ExecutiveSectionMetricKind.COUNT.value,
            "Applications requiring awareness.",
            50,
        ),
    )

    watch_app = (
        next(
            (
                item
                for item in apps.all_apps
                if item.health == "watch"
            ),
            None,
        )
    )

    recommendations = []

    if watch_app is not None:
        recommendations.append(
            _recommendation(
                recommendation_id=(
                    "applications-section-top"
                ),
                kind=(
                    ExecutiveSectionRecommendationKind
                    .TOP
                    .value
                ),
                title=watch_app.app_name,
                summary=(
                    watch_app.status_summary
                ),
                owner_action=(
                    watch_app.open_label
                ),
                source_app_id=watch_app.app_id,
                source_lane_id=None,
                open_route=watch_app.open_route,
                navigation_mode=watch_app.open_mode,
                display_order=10,
            )
        )

    if apps.reserved_apps:
        reserved = apps.reserved_apps[0]

        recommendations.append(
            _recommendation(
                recommendation_id=(
                    "applications-section-watch-next"
                ),
                kind=(
                    ExecutiveSectionRecommendationKind
                    .WATCH_NEXT
                    .value
                ),
                title=reserved.app_name,
                summary=(
                    reserved.status_summary
                ),
                owner_action=reserved.open_label,
                source_app_id=reserved.app_id,
                source_lane_id=None,
                open_route=reserved.open_route,
                navigation_mode=reserved.open_mode,
                display_order=30,
            )
        )

    navigation_targets = (
        _navigation_target(
            target_id="applications-section-open",
            label="Open Application Registry",
            open_route="/clouds/applications",
            navigation_mode=(
                ExecutiveSectionNavigationMode
                .CLOUDS_INTERNAL
                .value
            ),
            source_app_id=None,
            source_lane_id=None,
            display_order=10,
        ),
    )

    return ExecutiveDashboardSectionDetail(
        summary=summary,
        metrics=metrics,
        recommendations=tuple(
            sorted(
                recommendations,
                key=recommendation_sort_key,
            )
        ),
        navigation_targets=navigation_targets,
        linked_app_ids=tuple(
            item.app_id
            for item in apps.all_apps
        ),
        linked_mission_lane_ids=(),
        owner_questions=SECTION_QUESTIONS[
            ExecutiveSectionId
            .APPLICATIONS
            .value
        ],
        allowed_clouds_actions=(
            ALLOWED_CLOUDS_ACTIONS
        ),
        prohibited_clouds_actions=(
            PROHIBITED_CLOUDS_ACTIONS
        ),
        downstream_execution_performed=False,
        display_order=50,
    )


def _readiness_detail() -> (
    ExecutiveDashboardSectionDetail
):
    dashboard_summary = (
        get_executive_dashboard_summary()
    )
    dashboard = get_executive_dashboard()

    score = dashboard_summary.readiness_score

    if score >= 85:
        readiness = (
            ExecutiveSectionReadiness.READY.value
        )
    elif score >= 65:
        readiness = (
            ExecutiveSectionReadiness
            .ADVANCING
            .value
        )
    elif score >= 40:
        readiness = (
            ExecutiveSectionReadiness.BUILDING.value
        )
    elif score >= 20:
        readiness = (
            ExecutiveSectionReadiness
            .FOUNDATION
            .value
        )
    else:
        readiness = (
            ExecutiveSectionReadiness.HELD.value
        )

    health = (
        dashboard_summary
        .health
        .overall_health
    )

    summary = ExecutiveDashboardSectionSummary(
        section_id=(
            ExecutiveSectionId.READINESS.value
        ),
        title="Overall Readiness",
        subtitle=(
            "Combined readiness and executive health "
            "across the Clouds owner-command layer."
        ),
        summary=(
            f"Combined readiness is {score}% "
            f"with executive health {health}."
        ),
        health=health,
        readiness=readiness,
        readiness_score=score,
        primary_metric=score,
        secondary_metric=(
            dashboard_summary
            .blocked_priority_count
        ),
        source_integrity_verified=(
            dashboard_summary
            .source_integrity_verified
        ),
        execution_performed=False,
    )

    metrics = (
        _metric(
            "readiness-score",
            "Readiness Score",
            score,
            ExecutiveSectionMetricKind.PERCENTAGE.value,
            "Combined application and mission-lane readiness.",
            10,
        ),
        _metric(
            "readiness-state",
            "Readiness State",
            readiness,
            ExecutiveSectionMetricKind.STATE.value,
            "Executive classification of combined readiness.",
            20,
        ),
        _metric(
            "readiness-blocked-priorities",
            "Blocked Priorities",
            (
                dashboard_summary
                .blocked_priority_count
            ),
            ExecutiveSectionMetricKind.COUNT.value,
            "Strategic priorities currently blocked.",
            30,
        ),
        _metric(
            "readiness-action-required",
            "Action Required",
            (
                dashboard_summary
                .action_required_count
            ),
            ExecutiveSectionMetricKind.COUNT.value,
            "Owner-attention items requiring review.",
            40,
        ),
        _metric(
            "readiness-app-count",
            "Applications Monitored",
            (
                dashboard_summary
                .monitored_application_count
            ),
            ExecutiveSectionMetricKind.COUNT.value,
            "Applications included in readiness roll-up.",
            50,
        ),
        _metric(
            "readiness-lane-count",
            "Mission Lanes Monitored",
            (
                dashboard_summary
                .monitored_mission_lane_count
            ),
            ExecutiveSectionMetricKind.COUNT.value,
            "Mission lanes included in readiness roll-up.",
            60,
        ),
    )

    executive_recommendations = (
        get_executive_recommendations()
    )

    recommendations = []

    for index, item in enumerate(
        executive_recommendations[:3],
        start=1,
    ):
        kind = {
            1: (
                ExecutiveSectionRecommendationKind
                .TOP
                .value
            ),
            2: (
                ExecutiveSectionRecommendationKind
                .SECOND
                .value
            ),
            3: (
                ExecutiveSectionRecommendationKind
                .WATCH_NEXT
                .value
            ),
        }[index]

        recommendations.append(
            _recommendation(
                recommendation_id=(
                    f"readiness-section-{kind}"
                ),
                kind=kind,
                title=item.title,
                summary=item.summary,
                owner_action=item.owner_action,
                source_app_id=(
                    item.source_app_id
                ),
                source_lane_id=(
                    item.source_lane_id
                ),
                open_route=item.open_route,
                navigation_mode=(
                    item.navigation_mode
                ),
                display_order=index * 10,
            )
        )

    navigation_targets = (
        _navigation_target(
            target_id="readiness-section-open",
            label="Open Readiness",
            open_route="/clouds/readiness",
            navigation_mode=(
                ExecutiveSectionNavigationMode
                .CLOUDS_INTERNAL
                .value
            ),
            source_app_id=None,
            source_lane_id=None,
            display_order=10,
        ),
        _navigation_target(
            target_id=(
                "readiness-section-open-dashboard"
            ),
            label="Open Executive Dashboard",
            open_route="/clouds/executive",
            navigation_mode=(
                ExecutiveSectionNavigationMode
                .CLOUDS_INTERNAL
                .value
            ),
            source_app_id=None,
            source_lane_id=None,
            display_order=20,
        ),
    )

    linked_app_ids = tuple(
        sorted(
            {
                item.source_app_id
                for item
                in executive_recommendations
                if item.source_app_id
            }
        )
    )

    linked_lane_ids = tuple(
        sorted(
            {
                item.source_lane_id
                for item
                in executive_recommendations
                if item.source_lane_id
            }
        )
    )

    return ExecutiveDashboardSectionDetail(
        summary=summary,
        metrics=metrics,
        recommendations=tuple(
            sorted(
                recommendations,
                key=recommendation_sort_key,
            )
        ),
        navigation_targets=tuple(
            sorted(
                navigation_targets,
                key=navigation_target_sort_key,
            )
        ),
        linked_app_ids=linked_app_ids,
        linked_mission_lane_ids=(
            linked_lane_ids
        ),
        owner_questions=SECTION_QUESTIONS[
            ExecutiveSectionId.READINESS.value
        ],
        allowed_clouds_actions=(
            ALLOWED_CLOUDS_ACTIONS
        ),
        prohibited_clouds_actions=(
            PROHIBITED_CLOUDS_ACTIONS
        ),
        downstream_execution_performed=False,
        display_order=60,
    )


def get_executive_dashboard_sections() -> tuple[
    ExecutiveDashboardSectionDetail,
    ...
]:
    sections = (
        _today_detail(),
        _priorities_detail(),
        _attention_detail(),
        _mission_lanes_detail(),
        _applications_detail(),
        _readiness_detail(),
    )

    identifiers = [
        section.summary.section_id
        for section in sections
    ]

    if len(identifiers) != len(set(identifiers)):
        raise RuntimeError(
            "Duplicate executive section IDs detected."
        )

    expected = {
        item.value
        for item in ExecutiveSectionId
    }

    if set(identifiers) != expected:
        raise RuntimeError(
            "Executive section registry is incomplete."
        )

    return tuple(
        sorted(
            sections,
            key=section_sort_key,
        )
    )


def get_executive_dashboard_section(
    section_id: str,
) -> ExecutiveDashboardSectionDetail:
    section = next(
        (
            item
            for item
            in get_executive_dashboard_sections()
            if (
                item.summary.section_id
                == section_id
            )
        ),
        None,
    )

    if section is None:
        raise KeyError(
            "Executive dashboard section not found: "
            f"{section_id}"
        )

    return section


def get_executive_dashboard_section_detail(
    section_id: str,
) -> ExecutiveDashboardSectionDetail:
    return get_executive_dashboard_section(
        section_id
    )


def get_executive_dashboard_section_detail_payload(
    section_id: str,
) -> dict:
    return (
        get_executive_dashboard_section_detail(
            section_id
        ).to_dict()
    )


def get_executive_dashboard_section_surface() -> (
    ExecutiveDashboardSectionSurface
):
    return ExecutiveDashboardSectionSurface(
        title=(
            "Executive Dashboard Section Details"
        ),
        subtitle=(
            "Detailed executive summaries, metrics, "
            "recommendations, and navigation across the "
            "six fixed Clouds dashboard sections."
        ),
        sections=(
            get_executive_dashboard_sections()
        ),
        boundary_notice=(
            "Section details deepen owner visibility only. "
            "Clouds does not approve or execute operational "
            "application work."
        ),
    )


def get_executive_dashboard_section_surface_payload() -> dict:
    return (
        get_executive_dashboard_section_surface()
        .to_dict()
    )


def get_executive_section_summary(
    section_id: str,
) -> ExecutiveDashboardSectionSummary:
    return (
        get_executive_dashboard_section(
            section_id
        ).summary
    )


def get_executive_section_metrics(
    section_id: str,
) -> tuple[
    ExecutiveSectionMetric,
    ...
]:
    return (
        get_executive_dashboard_section(
            section_id
        ).metrics
    )


def get_executive_section_recommendations(
    section_id: str,
) -> tuple[
    ExecutiveSectionRecommendation,
    ...
]:
    return (
        get_executive_dashboard_section(
            section_id
        ).recommendations
    )


def get_executive_section_navigation_targets(
    section_id: str,
) -> tuple[
    ExecutiveSectionNavigationTarget,
    ...
]:
    return (
        get_executive_dashboard_section(
            section_id
        ).navigation_targets
    )


def filter_executive_dashboard_sections(
    *,
    section_id: str | None = None,
    health: str | None = None,
    readiness: str | None = None,
    linked_app_id: str | None = None,
    linked_mission_lane_id: str | None = None,
) -> tuple[
    ExecutiveDashboardSectionDetail,
    ...
]:
    return filter_section_details(
        get_executive_dashboard_sections(),
        section_id=section_id,
        health=health,
        readiness=readiness,
        linked_app_id=linked_app_id,
        linked_mission_lane_id=(
            linked_mission_lane_id
        ),
    )


def get_clouds_gp008_status_payload() -> dict:
    surface = (
        get_executive_dashboard_section_surface()
    )

    sections = surface.sections

    return {
        "pack": "GP008",
        "section": (
            "EXECUTIVE DASHBOARD SECTION "
            "DETAIL SURFACE"
        ),
        "status": "ready",
        "safe_to_continue": True,
        "section_count": len(sections),
        "section_ids": [
            item.summary.section_id
            for item in sections
        ],
        "metric_count": sum(
            len(item.metrics)
            for item in sections
        ),
        "recommendation_count": sum(
            len(item.recommendations)
            for item in sections
        ),
        "navigation_target_count": sum(
            len(item.navigation_targets)
            for item in sections
        ),
        "source_integrity_verified": all(
            item.summary
            .source_integrity_verified
            for item in sections
        ),
        "tower_boundary_preserved": True,
        "section_execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP009 — EXECUTIVE DASHBOARD "
            "NAVIGATION MAP"
        ),
    }
