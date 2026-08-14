"""
The Clouds — Owner Attention Command Surface.

Unifies explicit owner-attention records with local app and
mission-lane attention signals.

This surface is informational and navigational only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

try:
    from .contracts import (
        AttentionKind,
        AttentionPriority,
        OwnerAttentionItem,
    )
except ImportError:
    from contracts import (
        AttentionKind,
        AttentionPriority,
        OwnerAttentionItem,
    )


class AttentionSourceType(str, Enum):
    OWNER_RECORD = "owner_record"
    APPLICATION = "application"
    MISSION_LANE = "mission_lane"


class AttentionCommandGroup(str, Enum):
    ACTION_REQUIRED = "action_required"
    INFORMATIONAL = "informational"


class AttentionNavigationMode(str, Enum):
    CLOUDS_INTERNAL = "clouds_internal"
    TOWER_HANDOFF = "tower_handoff"
    NONE = "none"


PRIORITY_RANK = {
    AttentionPriority.CRITICAL.value: 1,
    AttentionPriority.HIGH.value: 2,
    AttentionPriority.ELEVATED.value: 3,
    AttentionPriority.ROUTINE.value: 4,
}


KIND_RANK = {
    AttentionKind.BLOCKER.value: 1,
    AttentionKind.RISK.value: 2,
    AttentionKind.DECISION.value: 3,
    AttentionKind.REVIEW.value: 4,
    AttentionKind.OPPORTUNITY.value: 5,
    AttentionKind.INFORMATION.value: 6,
}


@dataclass(frozen=True)
class OwnerAttentionCommand:
    attention_id: str
    title: str
    summary: str

    source_type: str
    source_app_id: str | None
    source_app_name: str | None
    source_lane_id: str | None
    source_lane_name: str | None

    kind: str
    priority: str
    command_group: str

    action_required: bool
    owner_action_label: str

    open_route: str | None
    navigation_mode: str

    source_integrity_verified: bool
    execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "attention_id": self.attention_id,
            "title": self.title,
            "summary": self.summary,
            "source_type": self.source_type,
            "source_app_id": self.source_app_id,
            "source_app_name": self.source_app_name,
            "source_lane_id": self.source_lane_id,
            "source_lane_name": self.source_lane_name,
            "kind": self.kind,
            "priority": self.priority,
            "command_group": self.command_group,
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
class OwnerAttentionSummary:
    total_attention_count: int
    action_required_count: int
    informational_count: int

    critical_count: int
    high_count: int
    elevated_count: int
    routine_count: int

    application_source_count: int
    mission_lane_source_count: int
    owner_record_source_count: int

    source_integrity_verified: bool
    execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_attention_count": (
                self.total_attention_count
            ),
            "group_counts": {
                "action_required": (
                    self.action_required_count
                ),
                "informational": (
                    self.informational_count
                ),
            },
            "priority_counts": {
                "critical": self.critical_count,
                "high": self.high_count,
                "elevated": self.elevated_count,
                "routine": self.routine_count,
            },
            "source_counts": {
                "application": (
                    self.application_source_count
                ),
                "mission_lane": (
                    self.mission_lane_source_count
                ),
                "owner_record": (
                    self.owner_record_source_count
                ),
            },
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "execution_performed": (
                self.execution_performed
            ),
        }


@dataclass(frozen=True)
class OwnerAttentionSurface:
    title: str
    subtitle: str

    summary: OwnerAttentionSummary

    action_required: tuple[OwnerAttentionCommand, ...]
    informational: tuple[OwnerAttentionCommand, ...]
    all_attention: tuple[OwnerAttentionCommand, ...]

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "summary": self.summary.to_dict(),
            "groups": {
                "action_required": [
                    item.to_dict()
                    for item in self.action_required
                ],
                "informational": [
                    item.to_dict()
                    for item in self.informational
                ],
            },
            "all_attention": [
                item.to_dict()
                for item in self.all_attention
            ],
            "boundary_notice": self.boundary_notice,
        }


@dataclass(frozen=True)
class OwnerAttentionDetail:
    command: OwnerAttentionCommand

    owner_questions: tuple[str, ...]
    allowed_clouds_actions: tuple[str, ...]
    prohibited_clouds_actions: tuple[str, ...]

    owning_app_authority_boundary: str | None

    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "command": self.command.to_dict(),
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


def determine_command_group(
    *,
    action_required: bool,
) -> AttentionCommandGroup:
    if action_required:
        return AttentionCommandGroup.ACTION_REQUIRED

    return AttentionCommandGroup.INFORMATIONAL


def determine_navigation_mode(
    *,
    open_route: str | None,
    source_app_id: str | None,
) -> AttentionNavigationMode:
    if not open_route:
        return AttentionNavigationMode.NONE

    if source_app_id == "clouds":
        return AttentionNavigationMode.CLOUDS_INTERNAL

    return AttentionNavigationMode.TOWER_HANDOFF


def owner_attention_sort_key(
    item: OwnerAttentionCommand,
) -> tuple:
    return (
        PRIORITY_RANK[item.priority],
        0 if item.action_required else 1,
        KIND_RANK[item.kind],
        item.attention_id,
    )


def filter_owner_attention(
    items: Iterable[OwnerAttentionCommand],
    *,
    priority: str | None = None,
    kind: str | None = None,
    source_app_id: str | None = None,
    source_lane_id: str | None = None,
    action_required: bool | None = None,
    source_type: str | None = None,
) -> tuple[OwnerAttentionCommand, ...]:
    filtered = []

    for item in items:
        if (
            priority is not None
            and item.priority != priority
        ):
            continue

        if kind is not None and item.kind != kind:
            continue

        if (
            source_app_id is not None
            and item.source_app_id != source_app_id
        ):
            continue

        if (
            source_lane_id is not None
            and item.source_lane_id != source_lane_id
        ):
            continue

        if (
            action_required is not None
            and item.action_required
            is not action_required
        ):
            continue

        if (
            source_type is not None
            and item.source_type != source_type
        ):
            continue

        filtered.append(item)

    return tuple(
        sorted(
            filtered,
            key=owner_attention_sort_key,
        )
    )
