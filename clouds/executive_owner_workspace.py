"""
The Clouds — Executive Owner Command Workspace.

GP010 composes executive dashboard, section detail, priority,
attention, readiness, and navigation projections into one
owner-oriented workspace.

This module contains contracts only.

No authentication, authorization, Tower step-up, downstream
execution, or operational action is performed here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable


class WorkspacePanelKind(str, Enum):
    NOW = "now"
    NEXT = "next"
    WATCH = "watch"
    SECTIONS = "sections"
    APPLICATIONS = "applications"
    READINESS = "readiness"


class WorkspaceHealth(str, Enum):
    HEALTHY = "healthy"
    WATCH = "watch"
    ATTENTION = "attention"
    BLOCKED = "blocked"


class WorkspacePriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    ELEVATED = "elevated"
    ROUTINE = "routine"


class WorkspaceItemKind(str, Enum):
    FOCUS = "focus"
    PRIORITY = "priority"
    ATTENTION = "attention"
    SECTION = "section"
    DESTINATION = "destination"
    READINESS = "readiness"


class WorkspaceNavigationMode(str, Enum):
    CLOUDS_INTERNAL = "clouds_internal"
    TOWER_HANDOFF = "tower_handoff"
    NONE = "none"


PANEL_ORDER = {
    WorkspacePanelKind.NOW.value: 10,
    WorkspacePanelKind.NEXT.value: 20,
    WorkspacePanelKind.WATCH.value: 30,
    WorkspacePanelKind.SECTIONS.value: 40,
    WorkspacePanelKind.APPLICATIONS.value: 50,
    WorkspacePanelKind.READINESS.value: 60,
}


PRIORITY_ORDER = {
    WorkspacePriority.CRITICAL.value: 10,
    WorkspacePriority.HIGH.value: 20,
    WorkspacePriority.ELEVATED.value: 30,
    WorkspacePriority.ROUTINE.value: 40,
}


@dataclass(frozen=True)
class WorkspaceNavigationAction:
    action_id: str
    label: str

    destination_id: str | None
    open_route: str | None

    navigation_mode: str

    requires_tower: bool
    requires_owner_permission: bool
    requires_step_up: bool

    clouds_executes_navigation: bool
    downstream_execution_performed: bool

    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "label": self.label,
            "destination_id": self.destination_id,
            "open_route": self.open_route,
            "navigation_mode": self.navigation_mode,
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
class WorkspaceItem:
    item_id: str
    kind: str

    title: str
    summary: str
    explanation: str
    owner_prompt: str

    priority: str
    health: str

    source_section_id: str | None
    source_app_id: str | None
    source_lane_id: str | None

    navigation_action: (
        WorkspaceNavigationAction
        | None
    )

    source_integrity_verified: bool
    execution_performed: bool

    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "kind": self.kind,
            "title": self.title,
            "summary": self.summary,
            "explanation": self.explanation,
            "owner_prompt": self.owner_prompt,
            "priority": self.priority,
            "health": self.health,
            "source_section_id": (
                self.source_section_id
            ),
            "source_app_id": self.source_app_id,
            "source_lane_id": self.source_lane_id,
            "navigation_action": (
                self.navigation_action.to_dict()
                if self.navigation_action
                else None
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
class WorkspacePanel:
    panel_id: str
    kind: str

    title: str
    subtitle: str

    items: tuple[
        WorkspaceItem,
        ...
    ]

    item_count: int

    health: str
    source_integrity_verified: bool
    execution_performed: bool

    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "panel_id": self.panel_id,
            "kind": self.kind,
            "title": self.title,
            "subtitle": self.subtitle,
            "items": [
                item.to_dict()
                for item in self.items
            ],
            "item_count": self.item_count,
            "health": self.health,
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "execution_performed": (
                self.execution_performed
            ),
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class WorkspaceHeadline:
    title: str
    statement: str
    explanation: str

    overall_health: str
    readiness_score: int
    readiness_state: str

    action_required_count: int
    blocked_priority_count: int

    top_focus_title: str | None
    top_focus_app_id: str | None

    source_integrity_verified: bool
    execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "statement": self.statement,
            "explanation": self.explanation,
            "overall_health": self.overall_health,
            "readiness_score": self.readiness_score,
            "readiness_state": self.readiness_state,
            "action_required_count": (
                self.action_required_count
            ),
            "blocked_priority_count": (
                self.blocked_priority_count
            ),
            "top_focus_title": (
                self.top_focus_title
            ),
            "top_focus_app_id": (
                self.top_focus_app_id
            ),
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "execution_performed": (
                self.execution_performed
            ),
        }


@dataclass(frozen=True)
class WorkspaceSummary:
    panel_count: int
    item_count: int

    internal_navigation_count: int
    tower_handoff_count: int

    action_required_count: int
    blocked_priority_count: int

    readiness_score: int
    overall_health: str

    source_integrity_verified: bool
    tower_boundary_preserved: bool
    execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "panel_count": self.panel_count,
            "item_count": self.item_count,
            "internal_navigation_count": (
                self.internal_navigation_count
            ),
            "tower_handoff_count": (
                self.tower_handoff_count
            ),
            "action_required_count": (
                self.action_required_count
            ),
            "blocked_priority_count": (
                self.blocked_priority_count
            ),
            "readiness_score": self.readiness_score,
            "overall_health": self.overall_health,
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "tower_boundary_preserved": (
                self.tower_boundary_preserved
            ),
            "execution_performed": (
                self.execution_performed
            ),
        }


@dataclass(frozen=True)
class ExecutiveOwnerWorkspace:
    title: str
    subtitle: str

    headline: WorkspaceHeadline
    summary: WorkspaceSummary

    panels: tuple[
        WorkspacePanel,
        ...
    ]

    allowed_clouds_actions: tuple[str, ...]
    prohibited_clouds_actions: tuple[str, ...]

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "headline": self.headline.to_dict(),
            "summary": self.summary.to_dict(),
            "panels": [
                panel.to_dict()
                for panel in self.panels
            ],
            "allowed_clouds_actions": list(
                self.allowed_clouds_actions
            ),
            "prohibited_clouds_actions": list(
                self.prohibited_clouds_actions
            ),
            "boundary_notice": self.boundary_notice,
        }


def workspace_item_sort_key(
    item: WorkspaceItem,
) -> tuple:
    return (
        item.display_order,
        PRIORITY_ORDER[item.priority],
        item.item_id,
    )


def workspace_panel_sort_key(
    panel: WorkspacePanel,
) -> tuple:
    return (
        PANEL_ORDER[panel.kind],
        panel.display_order,
        panel.panel_id,
    )


def filter_workspace_items(
    items: Iterable[WorkspaceItem],
    *,
    kind: str | None = None,
    priority: str | None = None,
    health: str | None = None,
    source_section_id: str | None = None,
    source_app_id: str | None = None,
    source_lane_id: str | None = None,
    navigation_mode: str | None = None,
) -> tuple[
    WorkspaceItem,
    ...
]:
    filtered = []

    for item in items:
        if (
            kind is not None
            and item.kind != kind
        ):
            continue

        if (
            priority is not None
            and item.priority != priority
        ):
            continue

        if (
            health is not None
            and item.health != health
        ):
            continue

        if (
            source_section_id is not None
            and item.source_section_id
            != source_section_id
        ):
            continue

        if (
            source_app_id is not None
            and item.source_app_id
            != source_app_id
        ):
            continue

        if (
            source_lane_id is not None
            and item.source_lane_id
            != source_lane_id
        ):
            continue

        if navigation_mode is not None:
            action = item.navigation_action

            if (
                action is None
                or action.navigation_mode
                != navigation_mode
            ):
                continue

        filtered.append(item)

    return tuple(
        sorted(
            filtered,
            key=workspace_item_sort_key,
        )
    )
