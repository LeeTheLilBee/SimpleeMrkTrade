"""
The Clouds — Owner Command Mission Lane Surface.

Projects canonical mission-lane definitions and local lane
statuses into owner-facing cards, groups, queues, and details.

No operational application is imported or called.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

try:
    from .contracts import (
        HealthState,
        MissionLaneDefinition,
        MissionLaneStatus,
        ReadinessState,
    )
except ImportError:
    from contracts import (
        HealthState,
        MissionLaneDefinition,
        MissionLaneStatus,
        ReadinessState,
    )


class MissionLaneGroup(str, Enum):
    ACTIVE = "active"
    RESERVED = "reserved"


class MissionLaneAttentionState(str, Enum):
    CLEAR = "clear"
    WATCH = "watch"
    ATTENTION = "attention"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class MissionLaneOpenMode(str, Enum):
    CLOUDS_INTERNAL = "clouds_internal"
    TOWER_APP_HANDOFF = "tower_app_handoff"


HEALTH_RANK = {
    HealthState.BLOCKED.value: 1,
    HealthState.ATTENTION.value: 2,
    HealthState.WATCH.value: 3,
    HealthState.UNKNOWN.value: 4,
    HealthState.HEALTHY.value: 5,
}


READINESS_RANK = {
    ReadinessState.HELD.value: 1,
    ReadinessState.NOT_STARTED.value: 2,
    ReadinessState.FOUNDATION.value: 3,
    ReadinessState.BUILDING.value: 4,
    ReadinessState.READY_FOR_REVIEW.value: 5,
    ReadinessState.READY.value: 6,
}


@dataclass(frozen=True)
class MissionLaneCard:
    lane_id: str
    lane_name: str
    business_name: str
    purpose: str

    owning_app_id: str
    owning_app_name: str

    group: str
    active: bool
    health: str
    readiness: str
    status_summary: str

    attention_count: int
    attention_state: str

    open_route: str
    open_mode: str
    open_label: str

    execution_owned_by_clouds: bool
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "lane_id": self.lane_id,
            "lane_name": self.lane_name,
            "business_name": self.business_name,
            "purpose": self.purpose,
            "owning_app_id": self.owning_app_id,
            "owning_app_name": self.owning_app_name,
            "group": self.group,
            "active": self.active,
            "health": self.health,
            "readiness": self.readiness,
            "status_summary": self.status_summary,
            "attention_count": self.attention_count,
            "attention_state": self.attention_state,
            "open_route": self.open_route,
            "open_mode": self.open_mode,
            "open_label": self.open_label,
            "execution_owned_by_clouds": (
                self.execution_owned_by_clouds
            ),
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class MissionLaneSummary:
    total_lane_count: int
    active_lane_count: int
    reserved_lane_count: int

    healthy_lane_count: int
    watch_lane_count: int
    attention_lane_count: int
    blocked_lane_count: int
    unknown_lane_count: int

    building_lane_count: int
    foundation_lane_count: int
    not_started_lane_count: int
    held_lane_count: int

    total_attention_count: int
    clouds_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_lane_count": self.total_lane_count,
            "active_lane_count": self.active_lane_count,
            "reserved_lane_count": (
                self.reserved_lane_count
            ),
            "health_counts": {
                "healthy": self.healthy_lane_count,
                "watch": self.watch_lane_count,
                "attention": self.attention_lane_count,
                "blocked": self.blocked_lane_count,
                "unknown": self.unknown_lane_count,
            },
            "readiness_counts": {
                "building": self.building_lane_count,
                "foundation": self.foundation_lane_count,
                "not_started": (
                    self.not_started_lane_count
                ),
                "held": self.held_lane_count,
            },
            "total_attention_count": (
                self.total_attention_count
            ),
            "clouds_execution_performed": (
                self.clouds_execution_performed
            ),
        }


@dataclass(frozen=True)
class MissionLaneSurface:
    title: str
    subtitle: str

    summary: MissionLaneSummary

    active_lanes: tuple[MissionLaneCard, ...]
    reserved_lanes: tuple[MissionLaneCard, ...]
    all_lanes: tuple[MissionLaneCard, ...]

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "summary": self.summary.to_dict(),
            "groups": {
                "active": [
                    card.to_dict()
                    for card in self.active_lanes
                ],
                "reserved": [
                    card.to_dict()
                    for card in self.reserved_lanes
                ],
            },
            "all_lanes": [
                card.to_dict()
                for card in self.all_lanes
            ],
            "boundary_notice": self.boundary_notice,
        }


@dataclass(frozen=True)
class MissionLaneDetail:
    card: MissionLaneCard

    owner_questions: tuple[str, ...]
    clouds_permissions: tuple[str, ...]
    clouds_prohibitions: tuple[str, ...]

    owning_app_authority_boundary: str

    navigation_requires_tower: bool
    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "card": self.card.to_dict(),
            "owner_questions": list(
                self.owner_questions
            ),
            "clouds_permissions": list(
                self.clouds_permissions
            ),
            "clouds_prohibitions": list(
                self.clouds_prohibitions
            ),
            "owning_app_authority_boundary": (
                self.owning_app_authority_boundary
            ),
            "navigation_requires_tower": (
                self.navigation_requires_tower
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
        }


def determine_lane_group(
    lane: MissionLaneDefinition,
) -> MissionLaneGroup:
    if lane.active:
        return MissionLaneGroup.ACTIVE

    return MissionLaneGroup.RESERVED


def determine_lane_attention_state(
    status: MissionLaneStatus,
) -> MissionLaneAttentionState:
    if status.health == HealthState.BLOCKED.value:
        return MissionLaneAttentionState.BLOCKED

    if status.health == HealthState.ATTENTION.value:
        return MissionLaneAttentionState.ATTENTION

    if (
        status.health == HealthState.WATCH.value
        or status.attention_count > 0
    ):
        return MissionLaneAttentionState.WATCH

    if status.health == HealthState.UNKNOWN.value:
        return MissionLaneAttentionState.UNKNOWN

    return MissionLaneAttentionState.CLEAR


def determine_lane_open_mode(
    owning_app_id: str,
) -> MissionLaneOpenMode:
    if owning_app_id == "clouds":
        return MissionLaneOpenMode.CLOUDS_INTERNAL

    return MissionLaneOpenMode.TOWER_APP_HANDOFF


def build_mission_lane_card(
    lane: MissionLaneDefinition,
    status: MissionLaneStatus,
    *,
    owning_app_name: str,
    owning_app_route: str,
) -> MissionLaneCard:
    if lane.lane_id != status.lane_id:
        raise ValueError(
            "Mission lane definition and status IDs "
            "must match."
        )

    group = determine_lane_group(lane)
    attention_state = (
        determine_lane_attention_state(status)
    )
    open_mode = determine_lane_open_mode(
        lane.owning_app_id
    )

    if open_mode == MissionLaneOpenMode.CLOUDS_INTERNAL:
        open_label = "Open owner command lane"
    elif group == MissionLaneGroup.RESERVED:
        open_label = (
            f"View reserved lane in {owning_app_name}"
        )
    else:
        open_label = f"Open in {owning_app_name}"

    return MissionLaneCard(
        lane_id=lane.lane_id,
        lane_name=lane.lane_name,
        business_name=lane.business_name,
        purpose=lane.purpose,
        owning_app_id=lane.owning_app_id,
        owning_app_name=owning_app_name,
        group=group.value,
        active=lane.active,
        health=status.health,
        readiness=status.readiness,
        status_summary=status.summary,
        attention_count=status.attention_count,
        attention_state=attention_state.value,
        open_route=owning_app_route,
        open_mode=open_mode.value,
        open_label=open_label,
        execution_owned_by_clouds=False,
        display_order=lane.display_order,
    )


def mission_lane_sort_key(
    card: MissionLaneCard,
) -> tuple:
    return (
        card.display_order,
        card.lane_name.lower(),
        card.lane_id,
    )


def mission_lane_attention_sort_key(
    card: MissionLaneCard,
) -> tuple:
    """
    Sort owner-attention lanes by urgency first.

    When health and attention count are equal, preserve the
    canonical owner display order before readiness.

    This keeps major owner lanes in their intended strategic
    order instead of allowing an earlier readiness phase to
    outrank a more important lane.
    """

    return (
        HEALTH_RANK[card.health],
        -card.attention_count,
        card.display_order,
        READINESS_RANK[card.readiness],
        card.lane_id,
    )


def filter_mission_lane_cards(
    cards: Iterable[MissionLaneCard],
    *,
    group: str | None = None,
    health: str | None = None,
    readiness: str | None = None,
    owning_app_id: str | None = None,
    attention_only: bool = False,
) -> tuple[MissionLaneCard, ...]:
    filtered = []

    for card in cards:
        if group is not None and card.group != group:
            continue

        if health is not None and card.health != health:
            continue

        if (
            readiness is not None
            and card.readiness != readiness
        ):
            continue

        if (
            owning_app_id is not None
            and card.owning_app_id != owning_app_id
        ):
            continue

        if (
            attention_only
            and card.attention_state
            == MissionLaneAttentionState.CLEAR.value
        ):
            continue

        filtered.append(card)

    return tuple(
        sorted(
            filtered,
            key=mission_lane_sort_key,
        )
    )
