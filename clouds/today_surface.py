"""
The Clouds — Owner Command Today Surface.

Provides a compact owner-facing view of what matters today.

This module consumes only local Clouds summary contracts.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable


class TodayCardKind(str, Enum):
    FOCUS = "focus"
    WATCH = "watch"
    TARGET = "target"


class TodayNavigationMode(str, Enum):
    CLOUDS_INTERNAL = "clouds_internal"
    TOWER_HANDOFF = "tower_handoff"
    NONE = "none"


class TodayPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    ELEVATED = "elevated"
    ROUTINE = "routine"


PRIORITY_RANK = {
    TodayPriority.CRITICAL.value: 1,
    TodayPriority.HIGH.value: 2,
    TodayPriority.ELEVATED.value: 3,
    TodayPriority.ROUTINE.value: 4,
}


KIND_RANK = {
    TodayCardKind.FOCUS.value: 1,
    TodayCardKind.WATCH.value: 2,
    TodayCardKind.TARGET.value: 3,
}


# Canonical owner order for equally urgent Today targets.
# Generated IDs must not define strategic display order.
TODAY_TARGET_ORDER = {
    "today-target-app-teller": 10,
    "today-target-app-grounds": 20,
    "today-target-lane-people_and_payments": 30,
}


@dataclass(frozen=True)
class TodayHeader:
    title: str
    subtitle: str
    focus_count: int
    watch_count: int
    target_count: int
    action_required_count: int
    overall_state: str
    execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "focus_count": self.focus_count,
            "watch_count": self.watch_count,
            "target_count": self.target_count,
            "action_required_count": (
                self.action_required_count
            ),
            "overall_state": self.overall_state,
            "execution_performed": (
                self.execution_performed
            ),
        }


@dataclass(frozen=True)
class TodayCard:
    card_id: str
    title: str
    summary: str

    kind: str
    priority: str

    source_app_id: str | None
    source_app_name: str | None
    source_lane_id: str | None
    source_lane_name: str | None

    action_required: bool
    owner_action_label: str

    open_route: str | None
    navigation_mode: str

    source_integrity_verified: bool
    execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "card_id": self.card_id,
            "title": self.title,
            "summary": self.summary,
            "kind": self.kind,
            "priority": self.priority,
            "source_app_id": self.source_app_id,
            "source_app_name": self.source_app_name,
            "source_lane_id": self.source_lane_id,
            "source_lane_name": self.source_lane_name,
            "action_required": self.action_required,
            "owner_action_label": (
                self.owner_action_label
            ),
            "open_route": self.open_route,
            "navigation_mode": self.navigation_mode,
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "execution_performed": (
                self.execution_performed
            ),
        }


@dataclass(frozen=True)
class TodaySurface:
    header: TodayHeader

    focus: tuple[TodayCard, ...]
    watch: tuple[TodayCard, ...]
    targets: tuple[TodayCard, ...]

    all_cards: tuple[TodayCard, ...]

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "header": self.header.to_dict(),
            "sections": {
                "focus": [
                    card.to_dict()
                    for card in self.focus
                ],
                "watch": [
                    card.to_dict()
                    for card in self.watch
                ],
                "targets": [
                    card.to_dict()
                    for card in self.targets
                ],
            },
            "all_cards": [
                card.to_dict()
                for card in self.all_cards
            ],
            "boundary_notice": self.boundary_notice,
        }


@dataclass(frozen=True)
class TodayDetail:
    card: TodayCard
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


def today_sort_key(
    card: TodayCard,
) -> tuple:
    """
    Sort Today cards by urgency, section, and owner order.

    Equally urgent targets use the canonical target order
    before falling back to the stable card identifier.
    """

    target_order = TODAY_TARGET_ORDER.get(
        card.card_id,
        10_000,
    )

    return (
        PRIORITY_RANK[card.priority],
        KIND_RANK[card.kind],
        0 if card.action_required else 1,
        target_order,
        card.card_id,
    )


def filter_today_cards(
    cards: Iterable[TodayCard],
    *,
    kind: str | None = None,
    priority: str | None = None,
    source_app_id: str | None = None,
    source_lane_id: str | None = None,
    action_required: bool | None = None,
) -> tuple[TodayCard, ...]:
    filtered = []

    for card in cards:
        if kind is not None and card.kind != kind:
            continue

        if (
            priority is not None
            and card.priority != priority
        ):
            continue

        if (
            source_app_id is not None
            and card.source_app_id != source_app_id
        ):
            continue

        if (
            source_lane_id is not None
            and card.source_lane_id != source_lane_id
        ):
            continue

        if (
            action_required is not None
            and card.action_required
            is not action_required
        ):
            continue

        filtered.append(card)

    return tuple(
        sorted(
            filtered,
            key=today_sort_key,
        )
    )
