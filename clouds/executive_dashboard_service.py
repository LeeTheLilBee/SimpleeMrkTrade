"""
Service layer for The Clouds Executive Owner Dashboard.

The dashboard composes compact local Clouds surfaces only.
It does not import or execute downstream applications.
"""

from __future__ import annotations

try:
    from .app_registry_surface_service import (
        get_app_registry_surface,
    )
    from .executive_dashboard import (
        ExecutiveCardPriority,
        ExecutiveDashboard,
        ExecutiveDashboardCard,
        ExecutiveDashboardDetail,
        ExecutiveDashboardSummary,
        ExecutiveHealth,
        ExecutiveHealthSummary,
        ExecutiveNavigationMode,
        ExecutiveRecommendation,
        ExecutiveRecommendationKind,
        ExecutiveSection,
        calculate_readiness_score,
        determine_executive_health,
        determine_readiness_state,
        executive_card_sort_key,
        executive_recommendation_sort_key,
        filter_executive_cards,
    )
    from .mission_lane_surface_service import (
        get_mission_lane_surface,
    )
    from .owner_attention_surface_service import (
        get_owner_attention_surface,
    )
    from .priority_board_service import (
        get_priority_board,
        get_priority_card,
    )
    from .today_surface_service import (
        get_today_surface,
    )
except ImportError:
    from app_registry_surface_service import (
        get_app_registry_surface,
    )
    from executive_dashboard import (
        ExecutiveCardPriority,
        ExecutiveDashboard,
        ExecutiveDashboardCard,
        ExecutiveDashboardDetail,
        ExecutiveDashboardSummary,
        ExecutiveHealth,
        ExecutiveHealthSummary,
        ExecutiveNavigationMode,
        ExecutiveRecommendation,
        ExecutiveRecommendationKind,
        ExecutiveSection,
        calculate_readiness_score,
        determine_executive_health,
        determine_readiness_state,
        executive_card_sort_key,
        executive_recommendation_sort_key,
        filter_executive_cards,
    )
    from mission_lane_surface_service import (
        get_mission_lane_surface,
    )
    from owner_attention_surface_service import (
        get_owner_attention_surface,
    )
    from priority_board_service import (
        get_priority_board,
        get_priority_card,
    )
    from today_surface_service import (
        get_today_surface,
    )


OWNER_QUESTIONS = {
    ExecutiveSection.TODAY.value: (
        "What requires owner attention today?",
        "What should be watched today?",
        "Which target should remain visible?",
    ),
    ExecutiveSection.PRIORITIES.value: (
        "What strategic priority comes first?",
        "What blocked priority requires awareness?",
        "What owner action creates the greatest progress?",
    ),
    ExecutiveSection.ATTENTION.value: (
        "What requires owner review?",
        "What is informational rather than actionable?",
        "Which application owns the underlying work?",
    ),
    ExecutiveSection.MISSION_LANES.value: (
        "Which mission lane is advancing?",
        "Which lane remains held or not started?",
        "Which owning application should be opened?",
    ),
    ExecutiveSection.APPLICATIONS.value: (
        "Which applications are active?",
        "Which applications remain reserved?",
        "Which application currently requires attention?",
    ),
    ExecutiveSection.READINESS.value: (
        "What is the combined readiness score?",
        "Which readiness states reduce the score?",
        "What should advance before broader activation?",
    ),
}


ALLOWED_CLOUDS_ACTIONS = (
    "Compose compact Clouds owner summaries",
    "Display executive health and readiness",
    "Display fixed executive sections",
    "Prioritize executive recommendations",
    "Filter executive dashboard cards",
    "Provide safe navigation handoffs",
    "Display owner review questions",
)


PROHIBITED_CLOUDS_ACTIONS = (
    "Clouds cannot approve an executive recommendation",
    "Clouds cannot execute dashboard actions",
    "Clouds cannot authenticate or authorize",
    "Clouds cannot perform Tower step-up",
    "Clouds cannot trade capital",
    "Clouds cannot move money",
    "Clouds cannot retrieve raw Vault evidence",
    "Clouds cannot operate property workflows",
)


def _build_executive_summary() -> (
    ExecutiveDashboardSummary
):
    app_surface = get_app_registry_surface()
    lane_surface = get_mission_lane_surface()
    attention_surface = (
        get_owner_attention_surface()
    )
    today_surface = get_today_surface()
    priority_board = get_priority_board()

    readiness_values = [
        card.readiness
        for card in app_surface.all_apps
    ] + [
        card.readiness
        for card in lane_surface.all_lanes
    ]

    readiness_score = calculate_readiness_score(
        readiness_values
    )

    attention_system_count = (
        app_surface.summary.attention_app_count
        + lane_surface.summary.attention_lane_count
    )

    watch_system_count = (
        app_surface.summary.watch_app_count
        + lane_surface.summary.watch_lane_count
    )

    overall_health = determine_executive_health(
        blocked_priority_count=(
            priority_board.summary.blocked_count
        ),
        action_required_count=(
            attention_surface.summary
            .action_required_count
        ),
        attention_system_count=(
            attention_system_count
        ),
        watch_system_count=watch_system_count,
    )

    health = ExecutiveHealthSummary(
        overall_health=overall_health,
        healthy_application_count=(
            app_surface.summary.healthy_app_count
        ),
        watch_application_count=(
            app_surface.summary.watch_app_count
        ),
        attention_application_count=(
            app_surface.summary.attention_app_count
        ),
        blocked_application_count=(
            app_surface.summary.blocked_app_count
        ),
        unknown_application_count=(
            app_surface.summary.unknown_app_count
        ),
        healthy_lane_count=(
            lane_surface.summary.healthy_lane_count
        ),
        watch_lane_count=(
            lane_surface.summary.watch_lane_count
        ),
        attention_lane_count=(
            lane_surface.summary
            .attention_lane_count
        ),
        blocked_lane_count=(
            lane_surface.summary.blocked_lane_count
        ),
        unknown_lane_count=(
            lane_surface.summary.unknown_lane_count
        ),
        blocked_priority_count=(
            priority_board.summary.blocked_count
        ),
        action_required_count=(
            attention_surface.summary
            .action_required_count
        ),
    )

    source_integrity_verified = all(
        (
            app_surface.summary
            .owner_execution_performed
            is False,
            lane_surface.summary
            .clouds_execution_performed
            is False,
            attention_surface.summary
            .source_integrity_verified,
            priority_board.summary
            .source_integrity_verified,
            all(
                card.source_integrity_verified
                for card in today_surface.all_cards
            ),
        )
    )

    return ExecutiveDashboardSummary(
        monitored_application_count=(
            app_surface.summary.total_app_count
        ),
        monitored_mission_lane_count=(
            lane_surface.summary.total_lane_count
        ),
        today_card_count=len(
            today_surface.all_cards
        ),
        priority_count=(
            priority_board.summary
            .total_priority_count
        ),
        attention_count=(
            attention_surface.summary
            .total_attention_count
        ),
        action_required_count=(
            attention_surface.summary
            .action_required_count
        ),
        blocked_priority_count=(
            priority_board.summary.blocked_count
        ),
        readiness_score=readiness_score,
        readiness_state=(
            determine_readiness_state(
                readiness_score
            )
        ),
        health=health,
        source_integrity_verified=(
            source_integrity_verified
        ),
        execution_performed=False,
    )


def _build_dashboard_cards() -> tuple[
    ExecutiveDashboardCard,
    ...
]:
    today = get_today_surface()
    priorities = get_priority_board()
    attention = get_owner_attention_surface()
    lanes = get_mission_lane_surface()
    apps = get_app_registry_surface()
    summary = _build_executive_summary()

    top_priority = priorities.top_recommendation

    cards = (
        ExecutiveDashboardCard(
            card_id="executive-card-today",
            section=ExecutiveSection.TODAY.value,
            title="Today",
            summary=(
                f"{today.header.focus_count} focus, "
                f"{today.header.watch_count} watch, and "
                f"{today.header.target_count} open targets."
            ),
            recommendation=(
                "Begin with the highest-priority focus "
                "item, then review watch items."
            ),
            priority=(
                ExecutiveCardPriority.HIGH.value
                if today.header.action_required_count
                else ExecutiveCardPriority.ROUTINE.value
            ),
            health=(
                ExecutiveHealth.ATTENTION.value
                if today.header.action_required_count
                else ExecutiveHealth.WATCH.value
            ),
            primary_count=today.header.focus_count,
            secondary_count=(
                today.header.watch_count
                + today.header.target_count
            ),
            source_app_id=(
                today.focus[0].source_app_id
                if today.focus
                else None
            ),
            source_lane_id=(
                today.focus[0].source_lane_id
                if today.focus
                else None
            ),
            open_route="/clouds/today",
            navigation_mode=(
                ExecutiveNavigationMode
                .CLOUDS_INTERNAL
                .value
            ),
            source_integrity_verified=all(
                card.source_integrity_verified
                for card in today.all_cards
            ),
            execution_performed=False,
            display_order=10,
        ),
        ExecutiveDashboardCard(
            card_id="executive-card-priorities",
            section=(
                ExecutiveSection.PRIORITIES.value
            ),
            title="Priority Board",
            summary=(
                f"{priorities.summary.total_priority_count} "
                "strategic priorities with "
                f"{priorities.summary.blocked_count} blocked."
            ),
            recommendation=(
                top_priority.recommended_owner_action
                if top_priority
                else "No strategic priority is available."
            ),
            priority=(
                ExecutiveCardPriority.CRITICAL.value
                if priorities.summary.critical_count
                else ExecutiveCardPriority.HIGH.value
            ),
            health=(
                ExecutiveHealth.BLOCKED.value
                if priorities.summary.blocked_count
                else ExecutiveHealth.WATCH.value
            ),
            primary_count=(
                priorities.summary.critical_count
                + priorities.summary.high_count
            ),
            secondary_count=(
                priorities.summary.medium_count
                + priorities.summary.low_count
            ),
            source_app_id=(
                top_priority.source_app_id
                if top_priority
                else None
            ),
            source_lane_id=(
                top_priority.source_lane_id
                if top_priority
                else None
            ),
            open_route="/clouds/priorities",
            navigation_mode=(
                ExecutiveNavigationMode
                .CLOUDS_INTERNAL
                .value
            ),
            source_integrity_verified=(
                priorities.summary
                .source_integrity_verified
            ),
            execution_performed=False,
            display_order=20,
        ),
        ExecutiveDashboardCard(
            card_id="executive-card-attention",
            section=(
                ExecutiveSection.ATTENTION.value
            ),
            title="Owner Attention",
            summary=(
                f"{attention.summary.total_attention_count} "
                "attention items, including "
                f"{attention.summary.action_required_count} "
                "requiring owner review."
            ),
            recommendation=(
                "Review action-required items before "
                "informational attention."
            ),
            priority=(
                ExecutiveCardPriority.HIGH.value
                if (
                    attention.summary
                    .action_required_count
                )
                else ExecutiveCardPriority.ROUTINE.value
            ),
            health=(
                ExecutiveHealth.ATTENTION.value
                if (
                    attention.summary
                    .action_required_count
                )
                else ExecutiveHealth.HEALTHY.value
            ),
            primary_count=(
                attention.summary
                .action_required_count
            ),
            secondary_count=(
                attention.summary.informational_count
            ),
            source_app_id=(
                attention.action_required[0]
                .source_app_id
                if attention.action_required
                else None
            ),
            source_lane_id=(
                attention.action_required[0]
                .source_lane_id
                if attention.action_required
                else None
            ),
            open_route="/clouds/attention",
            navigation_mode=(
                ExecutiveNavigationMode
                .CLOUDS_INTERNAL
                .value
            ),
            source_integrity_verified=(
                attention.summary
                .source_integrity_verified
            ),
            execution_performed=False,
            display_order=30,
        ),
        ExecutiveDashboardCard(
            card_id="executive-card-mission-lanes",
            section=(
                ExecutiveSection.MISSION_LANES.value
            ),
            title="Mission Lanes",
            summary=(
                f"{lanes.summary.active_lane_count} active "
                "and "
                f"{lanes.summary.reserved_lane_count} "
                "reserved mission lanes."
            ),
            recommendation=(
                "Keep the Investment Engine first while "
                "preserving future operating lanes."
            ),
            priority=(
                ExecutiveCardPriority.ELEVATED.value
            ),
            health=(
                ExecutiveHealth.WATCH.value
                if lanes.summary.watch_lane_count
                else ExecutiveHealth.HEALTHY.value
            ),
            primary_count=(
                lanes.summary.active_lane_count
            ),
            secondary_count=(
                lanes.summary.reserved_lane_count
            ),
            source_app_id=None,
            source_lane_id=None,
            open_route="/clouds/mission-lanes",
            navigation_mode=(
                ExecutiveNavigationMode
                .CLOUDS_INTERNAL
                .value
            ),
            source_integrity_verified=True,
            execution_performed=False,
            display_order=40,
        ),
        ExecutiveDashboardCard(
            card_id="executive-card-applications",
            section=(
                ExecutiveSection.APPLICATIONS.value
            ),
            title="Applications",
            summary=(
                f"{apps.summary.active_app_count} active "
                "and "
                f"{apps.summary.reserved_app_count} "
                "reserved applications."
            ),
            recommendation=(
                "Continue active application corridors "
                "without prematurely activating reserved apps."
            ),
            priority=(
                ExecutiveCardPriority.ELEVATED.value
            ),
            health=(
                ExecutiveHealth.WATCH.value
                if apps.summary.watch_app_count
                else ExecutiveHealth.HEALTHY.value
            ),
            primary_count=(
                apps.summary.active_app_count
            ),
            secondary_count=(
                apps.summary.reserved_app_count
            ),
            source_app_id=None,
            source_lane_id=None,
            open_route="/clouds/applications",
            navigation_mode=(
                ExecutiveNavigationMode
                .CLOUDS_INTERNAL
                .value
            ),
            source_integrity_verified=True,
            execution_performed=False,
            display_order=50,
        ),
        ExecutiveDashboardCard(
            card_id="executive-card-readiness",
            section=(
                ExecutiveSection.READINESS.value
            ),
            title="Overall Readiness",
            summary=(
                f"Combined ecosystem readiness is "
                f"{summary.readiness_score}% "
                f"({summary.readiness_state})."
            ),
            recommendation=(
                "Advance active build corridors while "
                "keeping held and not-started surfaces "
                "fail-closed."
            ),
            priority=(
                ExecutiveCardPriority.HIGH.value
                if summary.readiness_score < 50
                else ExecutiveCardPriority.ELEVATED.value
            ),
            health=summary.health.overall_health,
            primary_count=summary.readiness_score,
            secondary_count=(
                summary.blocked_priority_count
            ),
            source_app_id=None,
            source_lane_id=None,
            open_route="/clouds/readiness",
            navigation_mode=(
                ExecutiveNavigationMode
                .CLOUDS_INTERNAL
                .value
            ),
            source_integrity_verified=(
                summary.source_integrity_verified
            ),
            execution_performed=False,
            display_order=60,
        ),
    )

    identifiers = [
        card.card_id
        for card in cards
    ]

    if len(identifiers) != len(set(identifiers)):
        raise RuntimeError(
            "Duplicate executive dashboard card IDs."
        )

    return tuple(
        sorted(
            cards,
            key=executive_card_sort_key,
        )
    )


def _build_recommendations() -> tuple[
    ExecutiveRecommendation,
    ...
]:
    board = get_priority_board()
    attention = get_owner_attention_surface()

    top = board.top_recommendation
    second = board.second_recommendation

    teller_priority = get_priority_card(
        "clouds-priority-teller-alignment"
    )

    grounds_priority = get_priority_card(
        "clouds-priority-grounds-planning"
    )

    recommendations = (
        ExecutiveRecommendation(
            recommendation_id=(
                "executive-recommendation-top"
            ),
            kind=(
                ExecutiveRecommendationKind
                .TOP
                .value
            ),
            title=(
                top.title
                if top
                else "No top recommendation"
            ),
            summary=(
                top.priority_explanation
                if top
                else "No priority data is available."
            ),
            owner_action=(
                top.recommended_owner_action
                if top
                else "No owner action is available."
            ),
            source_priority_id=(
                top.priority_id
                if top
                else None
            ),
            source_app_id=(
                top.source_app_id
                if top
                else None
            ),
            source_lane_id=(
                top.source_lane_id
                if top
                else None
            ),
            open_route=(
                top.open_route
                if top
                else None
            ),
            navigation_mode=(
                top.navigation_mode
                if top
                else (
                    ExecutiveNavigationMode
                    .NONE
                    .value
                )
            ),
            execution_performed=False,
            display_order=10,
        ),
        ExecutiveRecommendation(
            recommendation_id=(
                "executive-recommendation-second"
            ),
            kind=(
                ExecutiveRecommendationKind
                .SECOND
                .value
            ),
            title=(
                second.title
                if second
                else "No second recommendation"
            ),
            summary=(
                second.priority_explanation
                if second
                else "No secondary priority is available."
            ),
            owner_action=(
                second.recommended_owner_action
                if second
                else "No owner action is available."
            ),
            source_priority_id=(
                second.priority_id
                if second
                else None
            ),
            source_app_id=(
                second.source_app_id
                if second
                else None
            ),
            source_lane_id=(
                second.source_lane_id
                if second
                else None
            ),
            open_route=(
                second.open_route
                if second
                else None
            ),
            navigation_mode=(
                second.navigation_mode
                if second
                else (
                    ExecutiveNavigationMode
                    .NONE
                    .value
                )
            ),
            execution_performed=False,
            display_order=20,
        ),
        ExecutiveRecommendation(
            recommendation_id=(
                "executive-recommendation-watch-next"
            ),
            kind=(
                ExecutiveRecommendationKind
                .WATCH_NEXT
                .value
            ),
            title=teller_priority.title,
            summary=(
                attention.informational[0].summary
                if attention.informational
                else teller_priority.summary
            ),
            owner_action=(
                teller_priority
                .recommended_owner_action
            ),
            source_priority_id=(
                teller_priority.priority_id
            ),
            source_app_id=(
                teller_priority.source_app_id
            ),
            source_lane_id=(
                teller_priority.source_lane_id
            ),
            open_route=teller_priority.open_route,
            navigation_mode=(
                teller_priority.navigation_mode
            ),
            execution_performed=False,
            display_order=30,
        ),
        ExecutiveRecommendation(
            recommendation_id=(
                "executive-recommendation-future"
            ),
            kind=(
                ExecutiveRecommendationKind
                .FUTURE_OPPORTUNITY
                .value
            ),
            title=grounds_priority.title,
            summary=(
                grounds_priority
                .priority_explanation
            ),
            owner_action=(
                grounds_priority
                .recommended_owner_action
            ),
            source_priority_id=(
                grounds_priority.priority_id
            ),
            source_app_id=(
                grounds_priority.source_app_id
            ),
            source_lane_id=(
                grounds_priority.source_lane_id
            ),
            open_route=grounds_priority.open_route,
            navigation_mode=(
                grounds_priority.navigation_mode
            ),
            execution_performed=False,
            display_order=40,
        ),
    )

    return tuple(
        sorted(
            recommendations,
            key=(
                executive_recommendation_sort_key
            ),
        )
    )


def get_executive_dashboard() -> (
    ExecutiveDashboard
):
    summary = _build_executive_summary()
    cards = _build_dashboard_cards()
    recommendations = _build_recommendations()

    return ExecutiveDashboard(
        title="Executive Owner Dashboard",
        subtitle=(
            "One high-level command view across Today, "
            "priorities, owner attention, mission lanes, "
            "applications, and ecosystem readiness."
        ),
        summary=summary,
        cards=cards,
        recommendations=recommendations,
        boundary_notice=(
            "The Executive Dashboard summarizes and "
            "recommends. Clouds does not approve or execute "
            "the underlying operational work."
        ),
    )


def get_executive_dashboard_payload() -> dict:
    return get_executive_dashboard().to_dict()


def get_executive_dashboard_cards(
    *,
    section: str | None = None,
    priority: str | None = None,
    health: str | None = None,
    source_app_id: str | None = None,
    source_lane_id: str | None = None,
) -> tuple[ExecutiveDashboardCard, ...]:
    return filter_executive_cards(
        _build_dashboard_cards(),
        section=section,
        priority=priority,
        health=health,
        source_app_id=source_app_id,
        source_lane_id=source_lane_id,
    )


def get_executive_dashboard_card(
    card_id: str,
) -> ExecutiveDashboardCard:
    card = next(
        (
            item
            for item in _build_dashboard_cards()
            if item.card_id == card_id
        ),
        None,
    )

    if card is None:
        raise KeyError(
            "Executive dashboard card not found: "
            f"{card_id}"
        )

    return card


def get_executive_dashboard_detail(
    card_id: str,
) -> ExecutiveDashboardDetail:
    card = get_executive_dashboard_card(
        card_id
    )

    return ExecutiveDashboardDetail(
        card=card,
        owner_questions=tuple(
            OWNER_QUESTIONS.get(
                card.section,
                (),
            )
        ),
        allowed_clouds_actions=(
            ALLOWED_CLOUDS_ACTIONS
        ),
        prohibited_clouds_actions=(
            PROHIBITED_CLOUDS_ACTIONS
        ),
        downstream_execution_performed=False,
    )


def get_executive_dashboard_detail_payload(
    card_id: str,
) -> dict:
    return get_executive_dashboard_detail(
        card_id
    ).to_dict()


def get_executive_dashboard_summary() -> (
    ExecutiveDashboardSummary
):
    return _build_executive_summary()


def get_executive_dashboard_health() -> (
    ExecutiveHealthSummary
):
    return _build_executive_summary().health


def get_executive_recommendations() -> tuple[
    ExecutiveRecommendation,
    ...
]:
    return _build_recommendations()


def get_clouds_gp007_status_payload() -> dict:
    dashboard = get_executive_dashboard()

    return {
        "pack": "GP007",
        "section": (
            "EXECUTIVE OWNER DASHBOARD SURFACE"
        ),
        "status": "ready",
        "safe_to_continue": True,
        "dashboard_card_count": len(
            dashboard.cards
        ),
        "recommendation_count": len(
            dashboard.recommendations
        ),
        "monitored_application_count": (
            dashboard.summary
            .monitored_application_count
        ),
        "monitored_mission_lane_count": (
            dashboard.summary
            .monitored_mission_lane_count
        ),
        "readiness_score": (
            dashboard.summary.readiness_score
        ),
        "overall_health": (
            dashboard.summary
            .health
            .overall_health
        ),
        "source_integrity_verified": (
            dashboard.summary
            .source_integrity_verified
        ),
        "tower_boundary_preserved": True,
        "dashboard_execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP008 — EXECUTIVE DASHBOARD "
            "SECTION DETAIL SURFACE"
        ),
    }
