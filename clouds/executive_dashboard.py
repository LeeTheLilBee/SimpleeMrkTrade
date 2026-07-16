"""
The Clouds — Executive Owner Dashboard contracts.

This module assembles compact Clouds projections into one
executive owner surface.

It contains no operational application imports or execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable


class ExecutiveSection(str, Enum):
    TODAY = "today"
    PRIORITIES = "priorities"
    ATTENTION = "attention"
    MISSION_LANES = "mission_lanes"
    APPLICATIONS = "applications"
    READINESS = "readiness"


class ExecutiveHealth(str, Enum):
    HEALTHY = "healthy"
    WATCH = "watch"
    ATTENTION = "attention"
    BLOCKED = "blocked"


class ExecutiveCardPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    ELEVATED = "elevated"
    ROUTINE = "routine"


class ExecutiveNavigationMode(str, Enum):
    CLOUDS_INTERNAL = "clouds_internal"
    TOWER_HANDOFF = "tower_handoff"
    NONE = "none"


class ExecutiveRecommendationKind(str, Enum):
    TOP = "top"
    SECOND = "second"
    WATCH_NEXT = "watch_next"
    FUTURE_OPPORTUNITY = "future_opportunity"


SECTION_ORDER = {
    ExecutiveSection.TODAY.value: 10,
    ExecutiveSection.PRIORITIES.value: 20,
    ExecutiveSection.ATTENTION.value: 30,
    ExecutiveSection.MISSION_LANES.value: 40,
    ExecutiveSection.APPLICATIONS.value: 50,
    ExecutiveSection.READINESS.value: 60,
}


CARD_PRIORITY_RANK = {
    ExecutiveCardPriority.CRITICAL.value: 1,
    ExecutiveCardPriority.HIGH.value: 2,
    ExecutiveCardPriority.ELEVATED.value: 3,
    ExecutiveCardPriority.ROUTINE.value: 4,
}


READINESS_SCORE = {
    "ready": 100,
    "ready_for_review": 85,
    "building": 70,
    "foundation": 45,
    "not_started": 10,
    "held": 0,
}


@dataclass(frozen=True)
class ExecutiveDashboardCard:
    card_id: str
    section: str

    title: str
    summary: str
    recommendation: str

    priority: str
    health: str

    primary_count: int
    secondary_count: int

    source_app_id: str | None
    source_lane_id: str | None

    open_route: str | None
    navigation_mode: str

    source_integrity_verified: bool
    execution_performed: bool
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "card_id": self.card_id,
            "section": self.section,
            "title": self.title,
            "summary": self.summary,
            "recommendation": self.recommendation,
            "priority": self.priority,
            "health": self.health,
            "primary_count": self.primary_count,
            "secondary_count": self.secondary_count,
            "source_app_id": self.source_app_id,
            "source_lane_id": self.source_lane_id,
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
class ExecutiveHealthSummary:
    overall_health: str

    healthy_application_count: int
    watch_application_count: int
    attention_application_count: int
    blocked_application_count: int
    unknown_application_count: int

    healthy_lane_count: int
    watch_lane_count: int
    attention_lane_count: int
    blocked_lane_count: int
    unknown_lane_count: int

    blocked_priority_count: int
    action_required_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_health": self.overall_health,
            "application_health": {
                "healthy": (
                    self.healthy_application_count
                ),
                "watch": self.watch_application_count,
                "attention": (
                    self.attention_application_count
                ),
                "blocked": (
                    self.blocked_application_count
                ),
                "unknown": (
                    self.unknown_application_count
                ),
            },
            "mission_lane_health": {
                "healthy": self.healthy_lane_count,
                "watch": self.watch_lane_count,
                "attention": self.attention_lane_count,
                "blocked": self.blocked_lane_count,
                "unknown": self.unknown_lane_count,
            },
            "blocked_priority_count": (
                self.blocked_priority_count
            ),
            "action_required_count": (
                self.action_required_count
            ),
        }


@dataclass(frozen=True)
class ExecutiveDashboardSummary:
    monitored_application_count: int
    monitored_mission_lane_count: int

    today_card_count: int
    priority_count: int
    attention_count: int
    action_required_count: int
    blocked_priority_count: int

    readiness_score: int
    readiness_state: str

    health: ExecutiveHealthSummary

    source_integrity_verified: bool
    execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "monitored_application_count": (
                self.monitored_application_count
            ),
            "monitored_mission_lane_count": (
                self.monitored_mission_lane_count
            ),
            "today_card_count": self.today_card_count,
            "priority_count": self.priority_count,
            "attention_count": self.attention_count,
            "action_required_count": (
                self.action_required_count
            ),
            "blocked_priority_count": (
                self.blocked_priority_count
            ),
            "readiness_score": self.readiness_score,
            "readiness_state": self.readiness_state,
            "health": self.health.to_dict(),
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "execution_performed": (
                self.execution_performed
            ),
        }


@dataclass(frozen=True)
class ExecutiveRecommendation:
    recommendation_id: str
    kind: str

    title: str
    summary: str
    owner_action: str

    source_priority_id: str | None
    source_app_id: str | None
    source_lane_id: str | None

    open_route: str | None
    navigation_mode: str

    execution_performed: bool
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "recommendation_id": (
                self.recommendation_id
            ),
            "kind": self.kind,
            "title": self.title,
            "summary": self.summary,
            "owner_action": self.owner_action,
            "source_priority_id": (
                self.source_priority_id
            ),
            "source_app_id": self.source_app_id,
            "source_lane_id": self.source_lane_id,
            "open_route": self.open_route,
            "navigation_mode": self.navigation_mode,
            "execution_performed": (
                self.execution_performed
            ),
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class ExecutiveDashboard:
    title: str
    subtitle: str

    summary: ExecutiveDashboardSummary
    cards: tuple[ExecutiveDashboardCard, ...]
    recommendations: tuple[
        ExecutiveRecommendation,
        ...
    ]

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "summary": self.summary.to_dict(),
            "cards": [
                card.to_dict()
                for card in self.cards
            ],
            "recommendations": [
                item.to_dict()
                for item in self.recommendations
            ],
            "section_order": [
                section.value
                for section in ExecutiveSection
            ],
            "boundary_notice": self.boundary_notice,
        }


@dataclass(frozen=True)
class ExecutiveDashboardDetail:
    card: ExecutiveDashboardCard

    owner_questions: tuple[str, ...]
    allowed_clouds_actions: tuple[str, ...]
    prohibited_clouds_actions: tuple[str, ...]

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
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
        }


def calculate_readiness_score(
    readiness_values: Iterable[str],
) -> int:
    values = tuple(readiness_values)

    if not values:
        raise ValueError(
            "At least one readiness value is required."
        )

    try:
        scores = [
            READINESS_SCORE[value]
            for value in values
        ]
    except KeyError as exc:
        raise ValueError(
            "Unsupported readiness value."
        ) from exc

    return round(
        sum(scores) / len(scores)
    )


def determine_readiness_state(
    score: int,
) -> str:
    if score >= 85:
        return "ready"

    if score >= 65:
        return "advancing"

    if score >= 40:
        return "building"

    if score >= 20:
        return "foundation"

    return "held"


def determine_executive_health(
    *,
    blocked_priority_count: int,
    action_required_count: int,
    attention_system_count: int,
    watch_system_count: int,
) -> str:
    if blocked_priority_count > 0:
        return ExecutiveHealth.BLOCKED.value

    if (
        action_required_count > 0
        or attention_system_count > 0
    ):
        return ExecutiveHealth.ATTENTION.value

    if watch_system_count > 0:
        return ExecutiveHealth.WATCH.value

    return ExecutiveHealth.HEALTHY.value


def executive_card_sort_key(
    card: ExecutiveDashboardCard,
) -> tuple:
    return (
        SECTION_ORDER[card.section],
        card.display_order,
        CARD_PRIORITY_RANK[card.priority],
        card.card_id,
    )


def executive_recommendation_sort_key(
    recommendation: ExecutiveRecommendation,
) -> tuple:
    return (
        recommendation.display_order,
        recommendation.recommendation_id,
    )


def filter_executive_cards(
    cards: Iterable[ExecutiveDashboardCard],
    *,
    section: str | None = None,
    priority: str | None = None,
    health: str | None = None,
    source_app_id: str | None = None,
    source_lane_id: str | None = None,
) -> tuple[ExecutiveDashboardCard, ...]:
    filtered = []

    for card in cards:
        if (
            section is not None
            and card.section != section
        ):
            continue

        if (
            priority is not None
            and card.priority != priority
        ):
            continue

        if health is not None and card.health != health:
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

        filtered.append(card)

    return tuple(
        sorted(
            filtered,
            key=executive_card_sort_key,
        )
    )
