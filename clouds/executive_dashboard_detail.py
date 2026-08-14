"""
The Clouds — Executive Dashboard Section Detail contracts.

These contracts deepen the six fixed executive dashboard
sections without adding operational authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable


class ExecutiveSectionId(str, Enum):
    TODAY = "today"
    PRIORITIES = "priorities"
    ATTENTION = "attention"
    MISSION_LANES = "mission_lanes"
    APPLICATIONS = "applications"
    READINESS = "readiness"


class ExecutiveSectionHealth(str, Enum):
    HEALTHY = "healthy"
    WATCH = "watch"
    ATTENTION = "attention"
    BLOCKED = "blocked"


class ExecutiveSectionReadiness(str, Enum):
    READY = "ready"
    ADVANCING = "advancing"
    BUILDING = "building"
    FOUNDATION = "foundation"
    HELD = "held"


class ExecutiveSectionMetricKind(str, Enum):
    COUNT = "count"
    PERCENTAGE = "percentage"
    SCORE = "score"
    STATE = "state"


class ExecutiveSectionRecommendationKind(str, Enum):
    TOP = "top"
    SECOND = "second"
    WATCH_NEXT = "watch_next"


class ExecutiveSectionNavigationMode(str, Enum):
    CLOUDS_INTERNAL = "clouds_internal"
    TOWER_HANDOFF = "tower_handoff"
    NONE = "none"


SECTION_ORDER = {
    ExecutiveSectionId.TODAY.value: 10,
    ExecutiveSectionId.PRIORITIES.value: 20,
    ExecutiveSectionId.ATTENTION.value: 30,
    ExecutiveSectionId.MISSION_LANES.value: 40,
    ExecutiveSectionId.APPLICATIONS.value: 50,
    ExecutiveSectionId.READINESS.value: 60,
}


RECOMMENDATION_ORDER = {
    ExecutiveSectionRecommendationKind.TOP.value: 10,
    ExecutiveSectionRecommendationKind.SECOND.value: 20,
    ExecutiveSectionRecommendationKind.WATCH_NEXT.value: 30,
}


METRIC_ORDER = {
    "primary": 10,
    "secondary": 20,
    "tertiary": 30,
    "quaternary": 40,
    "quinary": 50,
    "senary": 60,
}


@dataclass(frozen=True)
class ExecutiveSectionMetric:
    metric_id: str
    label: str
    value: int | float | str
    kind: str
    meaning: str
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "label": self.label,
            "value": self.value,
            "kind": self.kind,
            "meaning": self.meaning,
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class ExecutiveSectionRecommendation:
    recommendation_id: str
    kind: str

    title: str
    summary: str
    owner_action: str

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
class ExecutiveSectionNavigationTarget:
    target_id: str
    label: str
    open_route: str
    navigation_mode: str

    source_app_id: str | None
    source_lane_id: str | None

    execution_performed: bool
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "label": self.label,
            "open_route": self.open_route,
            "navigation_mode": self.navigation_mode,
            "source_app_id": self.source_app_id,
            "source_lane_id": self.source_lane_id,
            "execution_performed": (
                self.execution_performed
            ),
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class ExecutiveDashboardSectionSummary:
    section_id: str
    title: str
    subtitle: str
    summary: str

    health: str
    readiness: str
    readiness_score: int

    primary_metric: int | float | str
    secondary_metric: int | float | str

    source_integrity_verified: bool
    execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "section_id": self.section_id,
            "title": self.title,
            "subtitle": self.subtitle,
            "summary": self.summary,
            "health": self.health,
            "readiness": self.readiness,
            "readiness_score": self.readiness_score,
            "primary_metric": self.primary_metric,
            "secondary_metric": self.secondary_metric,
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "execution_performed": (
                self.execution_performed
            ),
        }


@dataclass(frozen=True)
class ExecutiveDashboardSectionDetail:
    summary: ExecutiveDashboardSectionSummary

    metrics: tuple[
        ExecutiveSectionMetric,
        ...
    ]

    recommendations: tuple[
        ExecutiveSectionRecommendation,
        ...
    ]

    navigation_targets: tuple[
        ExecutiveSectionNavigationTarget,
        ...
    ]

    linked_app_ids: tuple[str, ...]
    linked_mission_lane_ids: tuple[str, ...]

    owner_questions: tuple[str, ...]
    allowed_clouds_actions: tuple[str, ...]
    prohibited_clouds_actions: tuple[str, ...]

    downstream_execution_performed: bool
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary.to_dict(),
            "metrics": [
                metric.to_dict()
                for metric in self.metrics
            ],
            "recommendations": [
                item.to_dict()
                for item in self.recommendations
            ],
            "navigation_targets": [
                target.to_dict()
                for target in self.navigation_targets
            ],
            "linked_app_ids": list(
                self.linked_app_ids
            ),
            "linked_mission_lane_ids": list(
                self.linked_mission_lane_ids
            ),
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
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class ExecutiveDashboardSectionSurface:
    title: str
    subtitle: str

    sections: tuple[
        ExecutiveDashboardSectionDetail,
        ...
    ]

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "sections": [
                section.to_dict()
                for section in self.sections
            ],
            "section_order": [
                section.summary.section_id
                for section in self.sections
            ],
            "boundary_notice": self.boundary_notice,
        }


def section_sort_key(
    section: ExecutiveDashboardSectionDetail,
) -> tuple:
    return (
        SECTION_ORDER[
            section.summary.section_id
        ],
        section.display_order,
        section.summary.section_id,
    )


def metric_sort_key(
    metric: ExecutiveSectionMetric,
) -> tuple:
    return (
        metric.display_order,
        metric.metric_id,
    )


def recommendation_sort_key(
    recommendation: (
        ExecutiveSectionRecommendation
    ),
) -> tuple:
    return (
        RECOMMENDATION_ORDER[
            recommendation.kind
        ],
        recommendation.display_order,
        recommendation.recommendation_id,
    )


def navigation_target_sort_key(
    target: ExecutiveSectionNavigationTarget,
) -> tuple:
    return (
        target.display_order,
        target.target_id,
    )


def filter_section_details(
    sections: Iterable[
        ExecutiveDashboardSectionDetail
    ],
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
    filtered = []

    for section in sections:
        if (
            section_id is not None
            and section.summary.section_id
            != section_id
        ):
            continue

        if (
            health is not None
            and section.summary.health
            != health
        ):
            continue

        if (
            readiness is not None
            and section.summary.readiness
            != readiness
        ):
            continue

        if (
            linked_app_id is not None
            and linked_app_id
            not in section.linked_app_ids
        ):
            continue

        if (
            linked_mission_lane_id
            is not None
            and linked_mission_lane_id
            not in section.linked_mission_lane_ids
        ):
            continue

        filtered.append(section)

    return tuple(
        sorted(
            filtered,
            key=section_sort_key,
        )
    )
