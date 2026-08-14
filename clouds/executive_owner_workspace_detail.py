"""
The Clouds — Executive Owner Workspace Detail / Action Intent.

GP011 adds read-only detail and action-intent contracts for
GP010 workspace items.

Action intent is descriptive. It is not approval or execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable


class OwnerActionIntentKind(str, Enum):
    REVIEW = "review"
    WATCH = "watch"
    OPEN_CLOUDS = "open_clouds"
    REQUEST_TOWER_HANDOFF = "request_tower_handoff"
    PREPARE = "prepare"
    HOLD = "hold"


class OwnerActionIntentState(str, Enum):
    AVAILABLE = "available"
    REVIEW_REQUIRED = "review_required"
    TOWER_REQUIRED = "tower_required"
    RESERVED = "reserved"
    BLOCKED = "blocked"
    NO_ACTION_NEEDED = "no_action_needed"


class OwnerActionIntentRisk(str, Enum):
    ROUTINE = "routine"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"


class OwnerActionIntentAuthority(str, Enum):
    CLOUDS = "clouds"
    TOWER = "tower"
    OWNER = "owner"
    DOWNSTREAM_APPLICATION = "downstream_application"
    NONE = "none"


@dataclass(frozen=True)
class OwnerActionPrerequisite:
    prerequisite_id: str
    label: str
    satisfied: bool
    explanation: str
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "prerequisite_id": self.prerequisite_id,
            "label": self.label,
            "satisfied": self.satisfied,
            "explanation": self.explanation,
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class OwnerActionBlocker:
    blocker_id: str
    label: str
    explanation: str
    authority: str
    resolvable_in_clouds: bool
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "blocker_id": self.blocker_id,
            "label": self.label,
            "explanation": self.explanation,
            "authority": self.authority,
            "resolvable_in_clouds": (
                self.resolvable_in_clouds
            ),
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class OwnerActionIntent:
    intent_id: str
    kind: str
    state: str
    risk: str

    title: str
    explanation: str
    owner_prompt: str

    source_item_id: str
    source_section_id: str | None
    source_app_id: str | None
    source_lane_id: str | None

    destination_id: str | None
    open_route: str | None
    navigation_mode: str

    authority: str

    requires_owner_review: bool
    requires_tower: bool
    requires_owner_permission: bool
    requires_step_up: bool

    clouds_can_execute: bool
    approval_performed: bool
    execution_performed: bool

    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "kind": self.kind,
            "state": self.state,
            "risk": self.risk,
            "title": self.title,
            "explanation": self.explanation,
            "owner_prompt": self.owner_prompt,
            "source_item_id": self.source_item_id,
            "source_section_id": (
                self.source_section_id
            ),
            "source_app_id": self.source_app_id,
            "source_lane_id": self.source_lane_id,
            "destination_id": self.destination_id,
            "open_route": self.open_route,
            "navigation_mode": self.navigation_mode,
            "authority": self.authority,
            "requires_owner_review": (
                self.requires_owner_review
            ),
            "requires_tower": self.requires_tower,
            "requires_owner_permission": (
                self.requires_owner_permission
            ),
            "requires_step_up": (
                self.requires_step_up
            ),
            "clouds_can_execute": (
                self.clouds_can_execute
            ),
            "approval_performed": (
                self.approval_performed
            ),
            "execution_performed": (
                self.execution_performed
            ),
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class ExecutiveOwnerWorkspaceDetail:
    item_id: str
    panel_id: str | None

    title: str
    summary: str

    what_it_means: str
    why_it_matters: str
    what_to_do_now: str
    what_can_wait: str

    health: str
    priority: str

    source_section_id: str | None
    source_app_id: str | None
    source_lane_id: str | None

    action_intent: OwnerActionIntent

    prerequisites: tuple[
        OwnerActionPrerequisite,
        ...
    ]

    blockers: tuple[
        OwnerActionBlocker,
        ...
    ]

    owner_questions: tuple[str, ...]

    allowed_clouds_actions: tuple[str, ...]
    prohibited_clouds_actions: tuple[str, ...]

    source_integrity_verified: bool
    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "panel_id": self.panel_id,
            "title": self.title,
            "summary": self.summary,
            "what_it_means": self.what_it_means,
            "why_it_matters": self.why_it_matters,
            "what_to_do_now": self.what_to_do_now,
            "what_can_wait": self.what_can_wait,
            "health": self.health,
            "priority": self.priority,
            "source_section_id": (
                self.source_section_id
            ),
            "source_app_id": self.source_app_id,
            "source_lane_id": self.source_lane_id,
            "action_intent": (
                self.action_intent.to_dict()
            ),
            "prerequisites": [
                item.to_dict()
                for item in self.prerequisites
            ],
            "blockers": [
                item.to_dict()
                for item in self.blockers
            ],
            "owner_questions": list(
                self.owner_questions
            ),
            "allowed_clouds_actions": list(
                self.allowed_clouds_actions
            ),
            "prohibited_clouds_actions": list(
                self.prohibited_clouds_actions
            ),
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
        }


@dataclass(frozen=True)
class ExecutiveOwnerWorkspaceDetailSurface:
    title: str
    subtitle: str

    details: tuple[
        ExecutiveOwnerWorkspaceDetail,
        ...
    ]

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "details": [
                detail.to_dict()
                for detail in self.details
            ],
            "boundary_notice": self.boundary_notice,
        }


def action_intent_sort_key(
    intent: OwnerActionIntent,
) -> tuple:
    return (
        intent.display_order,
        intent.intent_id,
    )


def prerequisite_sort_key(
    prerequisite: OwnerActionPrerequisite,
) -> tuple:
    return (
        prerequisite.display_order,
        prerequisite.prerequisite_id,
    )


def blocker_sort_key(
    blocker: OwnerActionBlocker,
) -> tuple:
    return (
        blocker.display_order,
        blocker.blocker_id,
    )


def filter_workspace_details(
    details: Iterable[
        ExecutiveOwnerWorkspaceDetail
    ],
    *,
    health: str | None = None,
    priority: str | None = None,
    source_section_id: str | None = None,
    source_app_id: str | None = None,
    source_lane_id: str | None = None,
    intent_kind: str | None = None,
    intent_state: str | None = None,
    requires_tower: bool | None = None,
) -> tuple[
    ExecutiveOwnerWorkspaceDetail,
    ...
]:
    filtered = []

    for detail in details:
        if (
            health is not None
            and detail.health != health
        ):
            continue

        if (
            priority is not None
            and detail.priority != priority
        ):
            continue

        if (
            source_section_id is not None
            and detail.source_section_id
            != source_section_id
        ):
            continue

        if (
            source_app_id is not None
            and detail.source_app_id
            != source_app_id
        ):
            continue

        if (
            source_lane_id is not None
            and detail.source_lane_id
            != source_lane_id
        ):
            continue

        if (
            intent_kind is not None
            and detail.action_intent.kind
            != intent_kind
        ):
            continue

        if (
            intent_state is not None
            and detail.action_intent.state
            != intent_state
        ):
            continue

        if (
            requires_tower is not None
            and detail.action_intent.requires_tower
            is not requires_tower
        ):
            continue

        filtered.append(detail)

    return tuple(
        sorted(
            filtered,
            key=lambda detail: (
                detail.action_intent.display_order,
                detail.item_id,
            ),
        )
    )
