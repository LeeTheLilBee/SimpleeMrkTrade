"""
The Clouds — Owner Command Priority Board.

Defines strategic owner priorities, scoring, ordering,
summaries, filters, and detail contracts.

This module performs no operational execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable


class StrategicPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PriorityCategory(str, Enum):
    REVENUE = "revenue"
    RISK = "risk"
    OPERATIONS = "operations"
    GROWTH = "growth"
    INFRASTRUCTURE = "infrastructure"
    RESEARCH = "research"


class PriorityState(str, Enum):
    READY = "ready"
    WATCH = "watch"
    BLOCKED = "blocked"


class ImpactLevel(str, Enum):
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EffortLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PriorityNavigationMode(str, Enum):
    CLOUDS_INTERNAL = "clouds_internal"
    TOWER_HANDOFF = "tower_handoff"
    NONE = "none"


PRIORITY_RANK = {
    StrategicPriority.CRITICAL.value: 1,
    StrategicPriority.HIGH.value: 2,
    StrategicPriority.MEDIUM.value: 3,
    StrategicPriority.LOW.value: 4,
}


PRIORITY_SCORE_BASE = {
    StrategicPriority.CRITICAL.value: 400,
    StrategicPriority.HIGH.value: 300,
    StrategicPriority.MEDIUM.value: 200,
    StrategicPriority.LOW.value: 100,
}


IMPACT_RANK = {
    ImpactLevel.VERY_HIGH.value: 1,
    ImpactLevel.HIGH.value: 2,
    ImpactLevel.MEDIUM.value: 3,
    ImpactLevel.LOW.value: 4,
}


IMPACT_SCORE = {
    ImpactLevel.VERY_HIGH.value: 40,
    ImpactLevel.HIGH.value: 30,
    ImpactLevel.MEDIUM.value: 20,
    ImpactLevel.LOW.value: 10,
}


EFFORT_RANK = {
    EffortLevel.LOW.value: 1,
    EffortLevel.MEDIUM.value: 2,
    EffortLevel.HIGH.value: 3,
}


EFFORT_SCORE = {
    EffortLevel.LOW.value: 15,
    EffortLevel.MEDIUM.value: 10,
    EffortLevel.HIGH.value: 5,
}


BLOCKED_SCORE = 20


@dataclass(frozen=True)
class PriorityCard:
    priority_id: str
    title: str
    summary: str

    strategic_priority: str
    category: str
    state: str

    expected_impact: str
    estimated_effort: str
    priority_score: int

    recommended_owner_action: str
    expected_result: str
    priority_explanation: str

    source_app_id: str
    source_app_name: str
    source_lane_id: str
    source_lane_name: str

    open_route: str
    navigation_mode: str

    source_integrity_verified: bool
    execution_performed: bool
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "priority_id": self.priority_id,
            "title": self.title,
            "summary": self.summary,
            "strategic_priority": (
                self.strategic_priority
            ),
            "category": self.category,
            "state": self.state,
            "blocked": (
                self.state
                == PriorityState.BLOCKED.value
            ),
            "expected_impact": self.expected_impact,
            "estimated_effort": self.estimated_effort,
            "priority_score": self.priority_score,
            "recommended_owner_action": (
                self.recommended_owner_action
            ),
            "expected_result": self.expected_result,
            "priority_explanation": (
                self.priority_explanation
            ),
            "source_app_id": self.source_app_id,
            "source_app_name": self.source_app_name,
            "source_lane_id": self.source_lane_id,
            "source_lane_name": self.source_lane_name,
            "open_route": self.open_route,
            "navigation_mode": self.navigation_mode,
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "execution_performed": (
                self.execution_performed
            ),
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class PrioritySummary:
    total_priority_count: int

    critical_count: int
    high_count: int
    medium_count: int
    low_count: int

    ready_count: int
    watch_count: int
    blocked_count: int

    revenue_count: int
    risk_count: int
    operations_count: int
    growth_count: int
    infrastructure_count: int
    research_count: int

    highest_priority_score: int
    average_priority_score: float

    source_integrity_verified: bool
    execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_priority_count": (
                self.total_priority_count
            ),
            "priority_counts": {
                "critical": self.critical_count,
                "high": self.high_count,
                "medium": self.medium_count,
                "low": self.low_count,
            },
            "state_counts": {
                "ready": self.ready_count,
                "watch": self.watch_count,
                "blocked": self.blocked_count,
            },
            "category_counts": {
                "revenue": self.revenue_count,
                "risk": self.risk_count,
                "operations": self.operations_count,
                "growth": self.growth_count,
                "infrastructure": (
                    self.infrastructure_count
                ),
                "research": self.research_count,
            },
            "highest_priority_score": (
                self.highest_priority_score
            ),
            "average_priority_score": (
                self.average_priority_score
            ),
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "execution_performed": (
                self.execution_performed
            ),
        }


@dataclass(frozen=True)
class PriorityBoard:
    title: str
    subtitle: str

    summary: PrioritySummary

    critical: tuple[PriorityCard, ...]
    high: tuple[PriorityCard, ...]
    medium: tuple[PriorityCard, ...]
    low: tuple[PriorityCard, ...]

    blocked: tuple[PriorityCard, ...]
    all_priorities: tuple[PriorityCard, ...]

    top_recommendation: PriorityCard | None
    second_recommendation: PriorityCard | None

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "summary": self.summary.to_dict(),
            "priority_bands": {
                "critical": [
                    card.to_dict()
                    for card in self.critical
                ],
                "high": [
                    card.to_dict()
                    for card in self.high
                ],
                "medium": [
                    card.to_dict()
                    for card in self.medium
                ],
                "low": [
                    card.to_dict()
                    for card in self.low
                ],
            },
            "blocked": [
                card.to_dict()
                for card in self.blocked
            ],
            "all_priorities": [
                card.to_dict()
                for card in self.all_priorities
            ],
            "recommendations": {
                "top": (
                    self.top_recommendation.to_dict()
                    if self.top_recommendation
                    else None
                ),
                "second": (
                    self.second_recommendation.to_dict()
                    if self.second_recommendation
                    else None
                ),
            },
            "boundary_notice": self.boundary_notice,
        }


@dataclass(frozen=True)
class PriorityDetail:
    card: PriorityCard

    owner_questions: tuple[str, ...]
    allowed_clouds_actions: tuple[str, ...]
    prohibited_clouds_actions: tuple[str, ...]

    owning_app_authority_boundary: str
    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "card": self.card.to_dict(),
            "owner_questions": list(
                self.owner_questions
            ),
            "allowed_clouds_actions": list(
                self.allowed_clouds_actions
            ),
            "prohibited_clouds_actions": list(
                self.prohibited_clouds_actions
            ),
            "owning_app_authority_boundary": (
                self.owning_app_authority_boundary
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
        }


def calculate_priority_score(
    *,
    strategic_priority: str,
    expected_impact: str,
    estimated_effort: str,
    state: str,
) -> int:
    try:
        score = (
            PRIORITY_SCORE_BASE[strategic_priority]
            + IMPACT_SCORE[expected_impact]
            + EFFORT_SCORE[estimated_effort]
        )
    except KeyError as exc:
        raise ValueError(
            "Unsupported priority scoring value."
        ) from exc

    if state not in {
        PriorityState.READY.value,
        PriorityState.WATCH.value,
        PriorityState.BLOCKED.value,
    }:
        raise ValueError(
            f"Unsupported priority state: {state}"
        )

    if state == PriorityState.BLOCKED.value:
        score += BLOCKED_SCORE

    return score


def priority_sort_key(
    card: PriorityCard,
) -> tuple:
    """
    Sort strategic priorities deterministically.

    Blocked work moves ahead only when strategic priority
    is otherwise equal.
    """

    return (
        PRIORITY_RANK[card.strategic_priority],
        0 if card.state == PriorityState.BLOCKED.value else 1,
        IMPACT_RANK[card.expected_impact],
        EFFORT_RANK[card.estimated_effort],
        card.display_order,
        card.priority_id,
    )


def filter_priority_cards(
    cards: Iterable[PriorityCard],
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
    filtered = []

    for card in cards:
        if (
            strategic_priority is not None
            and card.strategic_priority
            != strategic_priority
        ):
            continue

        if (
            category is not None
            and card.category != category
        ):
            continue

        if state is not None and card.state != state:
            continue

        if (
            expected_impact is not None
            and card.expected_impact
            != expected_impact
        ):
            continue

        if (
            estimated_effort is not None
            and card.estimated_effort
            != estimated_effort
        ):
            continue

        if (
            source_app_id is not None
            and card.source_app_id
            != source_app_id
        ):
            continue

        if (
            source_lane_id is not None
            and card.source_lane_id
            != source_lane_id
        ):
            continue

        if (
            blocked_only
            and card.state
            != PriorityState.BLOCKED.value
        ):
            continue

        filtered.append(card)

    return tuple(
        sorted(
            filtered,
            key=priority_sort_key,
        )
    )
