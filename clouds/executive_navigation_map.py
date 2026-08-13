"""
The Clouds — Executive Dashboard Navigation Map contracts.

GP009 provides a read-only owner navigation map for the
executive dashboard.

The map describes destinations and navigation boundaries.
It does not authenticate, authorize, perform Tower step-up,
launch downstream applications, or execute operational work.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable


class ExecutiveNavigationMode(str, Enum):
    CLOUDS_INTERNAL = "clouds_internal"
    TOWER_HANDOFF = "tower_handoff"
    NONE = "none"


class ExecutiveNavigationDestinationKind(str, Enum):
    DASHBOARD = "dashboard"
    SECTION = "section"
    APPLICATION = "application"
    MISSION_LANE = "mission_lane"
    OWNER_ATTENTION = "owner_attention"
    PRIORITY = "priority"
    TODAY = "today"
    READINESS = "readiness"


class ExecutiveNavigationAvailability(str, Enum):
    AVAILABLE = "available"
    REFERENCED = "referenced"
    RESERVED = "reserved"
    HELD = "held"


class ExecutiveNavigationAuthority(str, Enum):
    CLOUDS = "clouds"
    TOWER = "tower"
    DOWNSTREAM_APPLICATION = "downstream_application"
    NONE = "none"


DESTINATION_KIND_ORDER = {
    ExecutiveNavigationDestinationKind.DASHBOARD.value: 10,
    ExecutiveNavigationDestinationKind.TODAY.value: 20,
    ExecutiveNavigationDestinationKind.PRIORITY.value: 30,
    ExecutiveNavigationDestinationKind.OWNER_ATTENTION.value: 40,
    ExecutiveNavigationDestinationKind.MISSION_LANE.value: 50,
    ExecutiveNavigationDestinationKind.APPLICATION.value: 60,
    ExecutiveNavigationDestinationKind.READINESS.value: 70,
    ExecutiveNavigationDestinationKind.SECTION.value: 80,
}


NAVIGATION_MODE_ORDER = {
    ExecutiveNavigationMode.CLOUDS_INTERNAL.value: 10,
    ExecutiveNavigationMode.TOWER_HANDOFF.value: 20,
    ExecutiveNavigationMode.NONE.value: 30,
}


AVAILABILITY_ORDER = {
    ExecutiveNavigationAvailability.AVAILABLE.value: 10,
    ExecutiveNavigationAvailability.REFERENCED.value: 20,
    ExecutiveNavigationAvailability.RESERVED.value: 30,
    ExecutiveNavigationAvailability.HELD.value: 40,
}


@dataclass(frozen=True)
class ExecutiveNavigationDestination:
    destination_id: str
    label: str
    description: str

    kind: str
    open_route: str | None
    navigation_mode: str
    availability: str
    authority: str

    source_section_id: str | None
    source_app_id: str | None
    source_lane_id: str | None

    requires_tower: bool
    requires_owner_permission: bool
    requires_step_up: bool

    clouds_executes_navigation: bool
    downstream_execution_performed: bool

    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "destination_id": self.destination_id,
            "label": self.label,
            "description": self.description,
            "kind": self.kind,
            "open_route": self.open_route,
            "navigation_mode": self.navigation_mode,
            "availability": self.availability,
            "authority": self.authority,
            "source_section_id": self.source_section_id,
            "source_app_id": self.source_app_id,
            "source_lane_id": self.source_lane_id,
            "requires_tower": self.requires_tower,
            "requires_owner_permission": (
                self.requires_owner_permission
            ),
            "requires_step_up": self.requires_step_up,
            "clouds_executes_navigation": (
                self.clouds_executes_navigation
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class ExecutiveNavigationSectionMap:
    section_id: str
    section_label: str

    destination_ids: tuple[str, ...]
    default_destination_id: str | None

    clouds_internal_count: int
    tower_handoff_count: int

    source_integrity_verified: bool
    execution_performed: bool

    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "section_id": self.section_id,
            "section_label": self.section_label,
            "destination_ids": list(
                self.destination_ids
            ),
            "default_destination_id": (
                self.default_destination_id
            ),
            "clouds_internal_count": (
                self.clouds_internal_count
            ),
            "tower_handoff_count": (
                self.tower_handoff_count
            ),
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "execution_performed": (
                self.execution_performed
            ),
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class ExecutiveNavigationMapSummary:
    destination_count: int
    section_count: int

    clouds_internal_count: int
    tower_handoff_count: int
    unavailable_count: int

    source_integrity_verified: bool
    tower_boundary_preserved: bool
    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "destination_count": self.destination_count,
            "section_count": self.section_count,
            "clouds_internal_count": (
                self.clouds_internal_count
            ),
            "tower_handoff_count": (
                self.tower_handoff_count
            ),
            "unavailable_count": (
                self.unavailable_count
            ),
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "tower_boundary_preserved": (
                self.tower_boundary_preserved
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
        }


@dataclass(frozen=True)
class ExecutiveNavigationMap:
    title: str
    subtitle: str

    summary: ExecutiveNavigationMapSummary

    destinations: tuple[
        ExecutiveNavigationDestination,
        ...
    ]

    sections: tuple[
        ExecutiveNavigationSectionMap,
        ...
    ]

    allowed_clouds_actions: tuple[str, ...]
    prohibited_clouds_actions: tuple[str, ...]

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "summary": self.summary.to_dict(),
            "destinations": [
                destination.to_dict()
                for destination in self.destinations
            ],
            "sections": [
                section.to_dict()
                for section in self.sections
            ],
            "allowed_clouds_actions": list(
                self.allowed_clouds_actions
            ),
            "prohibited_clouds_actions": list(
                self.prohibited_clouds_actions
            ),
            "boundary_notice": self.boundary_notice,
        }


def navigation_destination_sort_key(
    destination: ExecutiveNavigationDestination,
) -> tuple:
    return (
        destination.display_order,
        DESTINATION_KIND_ORDER[
            destination.kind
        ],
        NAVIGATION_MODE_ORDER[
            destination.navigation_mode
        ],
        destination.destination_id,
    )


def navigation_section_sort_key(
    section: ExecutiveNavigationSectionMap,
) -> tuple:
    return (
        section.display_order,
        section.section_id,
    )


def filter_navigation_destinations(
    destinations: Iterable[
        ExecutiveNavigationDestination
    ],
    *,
    kind: str | None = None,
    navigation_mode: str | None = None,
    availability: str | None = None,
    source_section_id: str | None = None,
    source_app_id: str | None = None,
    source_lane_id: str | None = None,
    requires_tower: bool | None = None,
) -> tuple[
    ExecutiveNavigationDestination,
    ...
]:
    filtered = []

    for destination in destinations:
        if (
            kind is not None
            and destination.kind != kind
        ):
            continue

        if (
            navigation_mode is not None
            and destination.navigation_mode
            != navigation_mode
        ):
            continue

        if (
            availability is not None
            and destination.availability
            != availability
        ):
            continue

        if (
            source_section_id is not None
            and destination.source_section_id
            != source_section_id
        ):
            continue

        if (
            source_app_id is not None
            and destination.source_app_id
            != source_app_id
        ):
            continue

        if (
            source_lane_id is not None
            and destination.source_lane_id
            != source_lane_id
        ):
            continue

        if (
            requires_tower is not None
            and destination.requires_tower
            is not requires_tower
        ):
            continue

        filtered.append(destination)

    return tuple(
        sorted(
            filtered,
            key=navigation_destination_sort_key,
        )
    )
