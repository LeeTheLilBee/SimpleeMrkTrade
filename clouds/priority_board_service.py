"""
Service layer for The Clouds Owner Command Priority Board.

Uses local Clouds definitions and compact summary contracts.
No operational application is imported or executed.
"""

from __future__ import annotations

from dataclasses import dataclass

try:
    from .priority_board import (
        EffortLevel,
        ImpactLevel,
        PriorityBoard,
        PriorityCard,
        PriorityCategory,
        PriorityDetail,
        PriorityNavigationMode,
        PriorityState,
        PrioritySummary,
        StrategicPriority,
        calculate_priority_score,
        filter_priority_cards,
        priority_sort_key,
    )
    from .registry import (
        get_app,
        get_mission_lane,
    )
except ImportError:
    from priority_board import (
        EffortLevel,
        ImpactLevel,
        PriorityBoard,
        PriorityCard,
        PriorityCategory,
        PriorityDetail,
        PriorityNavigationMode,
        PriorityState,
        PrioritySummary,
        StrategicPriority,
        calculate_priority_score,
        filter_priority_cards,
        priority_sort_key,
    )
    from registry import (
        get_app,
        get_mission_lane,
    )


@dataclass(frozen=True)
class PrioritySeed:
    priority_id: str
    title: str
    summary: str

    strategic_priority: str
    category: str
    state: str

    expected_impact: str
    estimated_effort: str

    recommended_owner_action: str
    expected_result: str
    priority_explanation: str

    source_app_id: str
    source_lane_id: str
    display_order: int


PRIORITY_SEEDS = (
    PrioritySeed(
        priority_id=(
            "clouds-priority-ob-manual-live-readiness"
        ),
        title="Observatory Manual Live Readiness",
        summary=(
            "Continue the controlled Tower and Observatory "
            "readiness corridor toward owner Manual Live."
        ),
        strategic_priority=(
            StrategicPriority.CRITICAL.value
        ),
        category=PriorityCategory.REVENUE.value,
        state=PriorityState.READY.value,
        expected_impact=ImpactLevel.VERY_HIGH.value,
        estimated_effort=EffortLevel.MEDIUM.value,
        recommended_owner_action=(
            "Continue the next verified Observatory and "
            "Tower readiness corridor."
        ),
        expected_result=(
            "Move the investment engine closer to safe "
            "owner Manual Live readiness."
        ),
        priority_explanation=(
            "The investment engine is the primary near-term "
            "capital and business-funding path."
        ),
        source_app_id="observatory",
        source_lane_id="investment_engine",
        display_order=10,
    ),
    PrioritySeed(
        priority_id=(
            "clouds-priority-atm-route-readiness"
        ),
        title="ATM Route Readiness",
        summary=(
            "Prepare the ATM operating lane for route "
            "research, acquisition, vault cash, and launch."
        ),
        strategic_priority=StrategicPriority.HIGH.value,
        category=PriorityCategory.GROWTH.value,
        state=PriorityState.WATCH.value,
        expected_impact=ImpactLevel.HIGH.value,
        estimated_effort=EffortLevel.LOW.value,
        recommended_owner_action=(
            "Define the first ATM route acquisition "
            "checklist and funding requirements."
        ),
        expected_result=(
            "Create a clear first-route operating path for "
            "SimpleeOnTheGo."
        ),
        priority_explanation=(
            "ATM operations are the first planned expansion "
            "lane after the investment engine reaches its "
            "capital milestone."
        ),
        source_app_id="teller",
        source_lane_id="atm_operations",
        display_order=20,
    ),
    PrioritySeed(
        priority_id=(
            "clouds-priority-teller-alignment"
        ),
        title="Teller Workflow Alignment",
        summary=(
            "Bring Teller boundaries and workflows into "
            "alignment with the current ecosystem doctrine."
        ),
        strategic_priority=StrategicPriority.MEDIUM.value,
        category=PriorityCategory.OPERATIONS.value,
        state=PriorityState.BLOCKED.value,
        expected_impact=ImpactLevel.HIGH.value,
        estimated_effort=EffortLevel.MEDIUM.value,
        recommended_owner_action=(
            "Schedule the Teller alignment pass after the "
            "current higher-priority application corridors."
        ),
        expected_result=(
            "Restore a clean payment, payroll, people, and "
            "workflow boundary beneath Tower."
        ),
        priority_explanation=(
            "Teller is strategically important but remains "
            "held until its focused alignment pass begins."
        ),
        source_app_id="teller",
        source_lane_id="people_and_payments",
        display_order=30,
    ),
    PrioritySeed(
        priority_id=(
            "clouds-priority-grounds-planning"
        ),
        title="Grounds Planning",
        summary=(
            "Prepare the future office, server-room, and "
            "property acquisition operating lane."
        ),
        strategic_priority=StrategicPriority.MEDIUM.value,
        category=(
            PriorityCategory.INFRASTRUCTURE.value
        ),
        state=PriorityState.READY.value,
        expected_impact=ImpactLevel.MEDIUM.value,
        estimated_effort=EffortLevel.MEDIUM.value,
        recommended_owner_action=(
            "Preserve the office-first property sequence and "
            "prepare Grounds requirements for its build day."
        ),
        expected_result=(
            "Maintain a coherent path from managed hosting "
            "to the office building and future properties."
        ),
        priority_explanation=(
            "Grounds is not the immediate build priority, "
            "but its acquisition sequence affects long-term "
            "infrastructure planning."
        ),
        source_app_id="grounds",
        source_lane_id="real_estate",
        display_order=40,
    ),
)


OWNER_QUESTIONS = {
    PriorityCategory.REVENUE.value: (
        "What revenue or capital milestone does this advance?",
        "What owner action creates the most progress?",
        "Which operating application owns execution?",
    ),
    PriorityCategory.GROWTH.value: (
        "What business expansion does this unlock?",
        "What preparation is required first?",
        "What milestone confirms readiness?",
    ),
    PriorityCategory.OPERATIONS.value: (
        "What operating workflow is blocked or incomplete?",
        "What dependency must be resolved first?",
        "Which application owns the correction?",
    ),
    PriorityCategory.INFRASTRUCTURE.value: (
        "What infrastructure milestone comes next?",
        "What sequencing constraint matters?",
        "What should be prepared without premature execution?",
    ),
    PriorityCategory.RISK.value: (
        "What risk is being reduced?",
        "What happens if the work remains incomplete?",
        "Which application owns mitigation?",
    ),
    PriorityCategory.RESEARCH.value: (
        "What question needs evidence?",
        "What decision will the research support?",
        "Which application owns the source material?",
    ),
}


ALLOWED_CLOUDS_ACTIONS = (
    "Display strategic owner priorities",
    "Score and order priorities deterministically",
    "Show blocked and ready states",
    "Show expected impact and estimated effort",
    "Display linked applications and mission lanes",
    "Provide safe navigation handoffs",
    "Display recommended owner actions",
)


PROHIBITED_CLOUDS_ACTIONS = (
    "Clouds cannot execute a recommended action",
    "Clouds cannot approve a strategic direction",
    "Clouds cannot authenticate or authorize",
    "Clouds cannot perform Tower step-up",
    "Clouds cannot trade capital",
    "Clouds cannot move money",
    "Clouds cannot retrieve raw Vault evidence",
    "Clouds cannot operate property workflows",
)


def _build_priority_card(
    seed: PrioritySeed,
) -> PriorityCard:
    app = get_app(
        seed.source_app_id
    )

    lane = get_mission_lane(
        seed.source_lane_id
    )

    verified = (
        app is not None
        and lane is not None
        and lane.owning_app_id
        == seed.source_app_id
    )

    if not verified:
        raise RuntimeError(
            "Priority source integrity validation failed "
            f"for {seed.priority_id}."
        )

    if seed.source_app_id == "clouds":
        navigation_mode = (
            PriorityNavigationMode
            .CLOUDS_INTERNAL
            .value
        )
    else:
        navigation_mode = (
            PriorityNavigationMode
            .TOWER_HANDOFF
            .value
        )

    score = calculate_priority_score(
        strategic_priority=(
            seed.strategic_priority
        ),
        expected_impact=seed.expected_impact,
        estimated_effort=seed.estimated_effort,
        state=seed.state,
    )

    return PriorityCard(
        priority_id=seed.priority_id,
        title=seed.title,
        summary=seed.summary,
        strategic_priority=(
            seed.strategic_priority
        ),
        category=seed.category,
        state=seed.state,
        expected_impact=seed.expected_impact,
        estimated_effort=seed.estimated_effort,
        priority_score=score,
        recommended_owner_action=(
            seed.recommended_owner_action
        ),
        expected_result=seed.expected_result,
        priority_explanation=(
            seed.priority_explanation
        ),
        source_app_id=seed.source_app_id,
        source_app_name=app.app_name,
        source_lane_id=seed.source_lane_id,
        source_lane_name=lane.lane_name,
        open_route=app.owner_surface_route,
        navigation_mode=navigation_mode,
        source_integrity_verified=True,
        execution_performed=False,
        display_order=seed.display_order,
    )


def get_priority_cards() -> tuple[
    PriorityCard,
    ...
]:
    cards = tuple(
        _build_priority_card(seed)
        for seed in PRIORITY_SEEDS
    )

    identifiers = [
        card.priority_id
        for card in cards
    ]

    if len(identifiers) != len(set(identifiers)):
        raise RuntimeError(
            "Duplicate priority IDs detected."
        )

    return tuple(
        sorted(
            cards,
            key=priority_sort_key,
        )
    )


def get_priority_board() -> PriorityBoard:
    cards = get_priority_cards()

    critical = tuple(
        card
        for card in cards
        if card.strategic_priority
        == StrategicPriority.CRITICAL.value
    )

    high = tuple(
        card
        for card in cards
        if card.strategic_priority
        == StrategicPriority.HIGH.value
    )

    medium = tuple(
        card
        for card in cards
        if card.strategic_priority
        == StrategicPriority.MEDIUM.value
    )

    low = tuple(
        card
        for card in cards
        if card.strategic_priority
        == StrategicPriority.LOW.value
    )

    blocked = tuple(
        card
        for card in cards
        if card.state == PriorityState.BLOCKED.value
    )

    scores = [
        card.priority_score
        for card in cards
    ]

    summary = PrioritySummary(
        total_priority_count=len(cards),
        critical_count=len(critical),
        high_count=len(high),
        medium_count=len(medium),
        low_count=len(low),
        ready_count=sum(
            card.state == PriorityState.READY.value
            for card in cards
        ),
        watch_count=sum(
            card.state == PriorityState.WATCH.value
            for card in cards
        ),
        blocked_count=len(blocked),
        revenue_count=sum(
            card.category
            == PriorityCategory.REVENUE.value
            for card in cards
        ),
        risk_count=sum(
            card.category
            == PriorityCategory.RISK.value
            for card in cards
        ),
        operations_count=sum(
            card.category
            == PriorityCategory.OPERATIONS.value
            for card in cards
        ),
        growth_count=sum(
            card.category
            == PriorityCategory.GROWTH.value
            for card in cards
        ),
        infrastructure_count=sum(
            card.category
            == PriorityCategory.INFRASTRUCTURE.value
            for card in cards
        ),
        research_count=sum(
            card.category
            == PriorityCategory.RESEARCH.value
            for card in cards
        ),
        highest_priority_score=max(scores),
        average_priority_score=round(
            sum(scores) / len(scores),
            2,
        ),
        source_integrity_verified=all(
            card.source_integrity_verified
            for card in cards
        ),
        execution_performed=False,
    )

    return PriorityBoard(
        title="Owner Priority Board",
        subtitle=(
            "A strategic owner view of what should be "
            "advanced first across the Simplee ecosystem."
        ),
        summary=summary,
        critical=critical,
        high=high,
        medium=medium,
        low=low,
        blocked=blocked,
        all_priorities=cards,
        top_recommendation=(
            cards[0]
            if cards
            else None
        ),
        second_recommendation=(
            cards[1]
            if len(cards) > 1
            else None
        ),
        boundary_notice=(
            "Priority cards recommend owner direction and "
            "navigation only. Clouds does not execute the "
            "underlying operational work."
        ),
    )


def get_priority_board_payload() -> dict:
    return get_priority_board().to_dict()


def get_priority_queue(
    *,
    strategic_priority: str | None = None,
    category: str | None = None,
    state: str | None = None,
    expected_impact: str | None = None,
    estimated_effort: str | None = None,
    source_app_id: str | None = None,
    source_lane_id: str | None = None,
    blocked_only: bool = False,
) -> tuple[PriorityCard, ...]:
    return filter_priority_cards(
        get_priority_cards(),
        strategic_priority=strategic_priority,
        category=category,
        state=state,
        expected_impact=expected_impact,
        estimated_effort=estimated_effort,
        source_app_id=source_app_id,
        source_lane_id=source_lane_id,
        blocked_only=blocked_only,
    )


def get_priority_card(
    priority_id: str,
) -> PriorityCard:
    card = next(
        (
            item
            for item in get_priority_cards()
            if item.priority_id == priority_id
        ),
        None,
    )

    if card is None:
        raise KeyError(
            f"Priority card not found: {priority_id}"
        )

    return card


def get_priority_detail(
    priority_id: str,
) -> PriorityDetail:
    card = get_priority_card(
        priority_id
    )

    app = get_app(
        card.source_app_id
    )

    if app is None:
        raise RuntimeError(
            "Priority source application disappeared "
            "after integrity validation."
        )

    return PriorityDetail(
        card=card,
        owner_questions=tuple(
            OWNER_QUESTIONS.get(
                card.category,
                (),
            )
        ),
        allowed_clouds_actions=(
            ALLOWED_CLOUDS_ACTIONS
        ),
        prohibited_clouds_actions=(
            PROHIBITED_CLOUDS_ACTIONS
        ),
        owning_app_authority_boundary=(
            app.authority_boundary
        ),
        downstream_execution_performed=False,
    )


def get_priority_detail_payload(
    priority_id: str,
) -> dict:
    return get_priority_detail(
        priority_id
    ).to_dict()


def get_priority_summary() -> PrioritySummary:
    return get_priority_board().summary


def get_clouds_gp006_status_payload() -> dict:
    board = get_priority_board()

    return {
        "pack": "GP006",
        "section": (
            "OWNER COMMAND PRIORITY BOARD"
        ),
        "status": "ready",
        "safe_to_continue": True,
        "total_priority_count": (
            board.summary.total_priority_count
        ),
        "critical_count": (
            board.summary.critical_count
        ),
        "high_count": board.summary.high_count,
        "medium_count": (
            board.summary.medium_count
        ),
        "blocked_count": (
            board.summary.blocked_count
        ),
        "top_recommendation_id": (
            board.top_recommendation.priority_id
            if board.top_recommendation
            else None
        ),
        "source_integrity_verified": (
            board.summary
            .source_integrity_verified
        ),
        "tower_boundary_preserved": True,
        "priority_execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP007 — EXECUTIVE OWNER DASHBOARD SURFACE"
        ),
    }
