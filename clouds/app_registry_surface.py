"""
The Clouds — Owner Command App Registry Surface.

Projects the canonical GP001 application registry into
owner-facing cards, groups, summaries, and detail views.

This module does not import or call operational applications.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

try:
    from .contracts import (
        AppConnectionState,
        AppDefinition,
        AppStatus,
        HealthState,
        ReadinessState,
    )
except ImportError:
    from contracts import (
        AppConnectionState,
        AppDefinition,
        AppStatus,
        HealthState,
        ReadinessState,
    )


class AppRegistryGroup(str, Enum):
    ACTIVE = "active"
    RESERVED = "reserved"


class AppRegistryAttentionState(str, Enum):
    CLEAR = "clear"
    WATCH = "watch"
    ATTENTION = "attention"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class AppOpenMode(str, Enum):
    TOWER_HANDOFF = "tower_handoff"
    CLOUDS_INTERNAL = "clouds_internal"


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
class AppRegistryCard:
    app_id: str
    app_name: str
    purpose: str

    group: str
    connection_state: str
    health: str
    readiness: str

    status_summary: str
    attention_count: int
    attention_state: str

    open_route: str
    open_mode: str
    open_label: str

    authority_boundary: str
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_id": self.app_id,
            "app_name": self.app_name,
            "purpose": self.purpose,
            "group": self.group,
            "connection_state": self.connection_state,
            "health": self.health,
            "readiness": self.readiness,
            "status_summary": self.status_summary,
            "attention_count": self.attention_count,
            "attention_state": self.attention_state,
            "open_route": self.open_route,
            "open_mode": self.open_mode,
            "open_label": self.open_label,
            "authority_boundary": (
                self.authority_boundary
            ),
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class AppRegistrySummary:
    total_app_count: int
    active_app_count: int
    reserved_app_count: int
    connected_app_count: int
    summary_ready_app_count: int

    healthy_app_count: int
    watch_app_count: int
    attention_app_count: int
    blocked_app_count: int
    unknown_app_count: int

    total_attention_count: int
    owner_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_app_count": self.total_app_count,
            "active_app_count": self.active_app_count,
            "reserved_app_count": self.reserved_app_count,
            "connected_app_count": (
                self.connected_app_count
            ),
            "summary_ready_app_count": (
                self.summary_ready_app_count
            ),
            "health_counts": {
                "healthy": self.healthy_app_count,
                "watch": self.watch_app_count,
                "attention": self.attention_app_count,
                "blocked": self.blocked_app_count,
                "unknown": self.unknown_app_count,
            },
            "total_attention_count": (
                self.total_attention_count
            ),
            "owner_execution_performed": (
                self.owner_execution_performed
            ),
        }


@dataclass(frozen=True)
class AppRegistrySurface:
    title: str
    subtitle: str
    summary: AppRegistrySummary
    active_apps: tuple[AppRegistryCard, ...]
    reserved_apps: tuple[AppRegistryCard, ...]
    all_apps: tuple[AppRegistryCard, ...]
    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "summary": self.summary.to_dict(),
            "groups": {
                "active": [
                    card.to_dict()
                    for card in self.active_apps
                ],
                "reserved": [
                    card.to_dict()
                    for card in self.reserved_apps
                ],
            },
            "all_apps": [
                card.to_dict()
                for card in self.all_apps
            ],
            "boundary_notice": self.boundary_notice,
        }


@dataclass(frozen=True)
class AppRegistryDetail:
    card: AppRegistryCard
    capabilities: tuple[str, ...]
    clouds_permissions: tuple[str, ...]
    clouds_prohibitions: tuple[str, ...]
    navigation_requires_tower: bool
    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "card": self.card.to_dict(),
            "capabilities": list(self.capabilities),
            "clouds_permissions": list(
                self.clouds_permissions
            ),
            "clouds_prohibitions": list(
                self.clouds_prohibitions
            ),
            "navigation_requires_tower": (
                self.navigation_requires_tower
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
        }


def determine_registry_group(
    app: AppDefinition,
) -> AppRegistryGroup:
    if (
        app.connection_state
        == AppConnectionState.RESERVED.value
    ):
        return AppRegistryGroup.RESERVED

    return AppRegistryGroup.ACTIVE


def determine_attention_state(
    status: AppStatus,
) -> AppRegistryAttentionState:
    if status.health == HealthState.BLOCKED.value:
        return AppRegistryAttentionState.BLOCKED

    if status.health == HealthState.ATTENTION.value:
        return AppRegistryAttentionState.ATTENTION

    if (
        status.health == HealthState.WATCH.value
        or status.attention_count > 0
    ):
        return AppRegistryAttentionState.WATCH

    if status.health == HealthState.UNKNOWN.value:
        return AppRegistryAttentionState.UNKNOWN

    return AppRegistryAttentionState.CLEAR


def determine_open_mode(
    app: AppDefinition,
) -> AppOpenMode:
    if app.app_id == "clouds":
        return AppOpenMode.CLOUDS_INTERNAL

    return AppOpenMode.TOWER_HANDOFF


def build_app_registry_card(
    app: AppDefinition,
    status: AppStatus,
) -> AppRegistryCard:
    if app.app_id != status.app_id:
        raise ValueError(
            "App definition and app status IDs must match."
        )

    group = determine_registry_group(app)
    attention_state = determine_attention_state(
        status
    )
    open_mode = determine_open_mode(app)

    if open_mode == AppOpenMode.CLOUDS_INTERNAL:
        open_label = "Open in Clouds"
    elif group == AppRegistryGroup.RESERVED:
        open_label = "View reserved app"
    else:
        open_label = f"Open {app.app_name}"

    return AppRegistryCard(
        app_id=app.app_id,
        app_name=app.app_name,
        purpose=app.purpose,
        group=group.value,
        connection_state=app.connection_state,
        health=status.health,
        readiness=status.readiness,
        status_summary=status.summary,
        attention_count=status.attention_count,
        attention_state=attention_state.value,
        open_route=status.open_route,
        open_mode=open_mode.value,
        open_label=open_label,
        authority_boundary=app.authority_boundary,
        display_order=app.display_order,
    )


def app_registry_sort_key(
    card: AppRegistryCard,
) -> tuple:
    return (
        card.display_order,
        card.app_name.lower(),
        card.app_id,
    )


def app_attention_sort_key(
    card: AppRegistryCard,
) -> tuple:
    return (
        HEALTH_RANK[card.health],
        -card.attention_count,
        READINESS_RANK[card.readiness],
        card.display_order,
        card.app_id,
    )


def filter_registry_cards(
    cards: Iterable[AppRegistryCard],
    *,
    group: str | None = None,
    health: str | None = None,
    readiness: str | None = None,
    attention_only: bool = False,
) -> tuple[AppRegistryCard, ...]:
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
            attention_only
            and card.attention_state
            == AppRegistryAttentionState.CLEAR.value
        ):
            continue

        filtered.append(card)

    return tuple(
        sorted(
            filtered,
            key=app_registry_sort_key,
        )
    )
