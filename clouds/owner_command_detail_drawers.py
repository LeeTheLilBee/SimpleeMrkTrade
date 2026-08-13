"""
GP022 — Owner Command Detail Drawers /
Guided Attention Experience.

Progressive disclosure only.
No persistence mutation or downstream execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable


class DetailDrawerKind(str, Enum):
    EXPLANATION = "explanation"
    WHY_IT_MATTERS = "why_it_matters"
    CURRENT_STATE = "current_state"
    CAN_WAIT = "can_wait"
    NEXT_STEP = "next_step"
    STATUS_DETAILS = "status_details"
    EVIDENCE = "evidence"


class DetailDrawerDisclosure(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    DEEP = "deep"
    TECHNICAL = "technical"


class GuidedAttentionAction(str, Enum):
    REVIEW_NOW = "review_now"
    KEEP_WATCHING = "keep_watching"
    SNOOZE = "snooze"
    DISMISS_INFORMATIONAL = "dismiss_informational"
    OPEN_DETAILS = "open_details"
    OPEN_PROTECTED_APP = "open_protected_app"
    NO_ACTION = "no_action"


@dataclass(frozen=True)
class OwnerCommandDrawer:
    drawer_id: str
    source_id: str

    kind: str
    disclosure_level: str

    title: str
    content: str

    hidden_by_default: bool
    owner_action_required: bool

    technical: bool
    execution_performed: bool

    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class GuidedAttentionStep:
    step_id: str
    source_id: str

    action: str
    label: str
    explanation: str

    recommended: bool
    mutates_persistent_state: bool
    executes_downstream_action: bool

    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class OwnerCommandDetailExperience:
    source_id: str
    source_label: str

    soulaana_summary: str

    drawers: tuple[
        OwnerCommandDrawer,
        ...
    ]

    guided_steps: tuple[
        GuidedAttentionStep,
        ...
    ]

    drawer_count: int
    guided_step_count: int

    evidence_hidden_by_default: bool
    persistent_state_mutated: bool
    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_label": self.source_label,
            "soulaana_summary": (
                self.soulaana_summary
            ),
            "drawers": [
                item.to_dict()
                for item in self.drawers
            ],
            "guided_steps": [
                item.to_dict()
                for item in self.guided_steps
            ],
            "drawer_count": self.drawer_count,
            "guided_step_count": (
                self.guided_step_count
            ),
            "evidence_hidden_by_default": (
                self.evidence_hidden_by_default
            ),
            "persistent_state_mutated": (
                self.persistent_state_mutated
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
        }


@dataclass(frozen=True)
class GuidedAttentionSurface:
    title: str

    experiences: tuple[
        OwnerCommandDetailExperience,
        ...
    ]

    source_count: int

    primary_attention_source_id: str | None
    watch_source_ids: tuple[str, ...]
    quiet_source_ids: tuple[str, ...]

    evidence_hidden_by_default: bool
    persistent_state_mutated: bool
    downstream_execution_performed: bool

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "experiences": [
                item.to_dict()
                for item in self.experiences
            ],
            "source_count": self.source_count,
            "primary_attention_source_id": (
                self.primary_attention_source_id
            ),
            "watch_source_ids": list(
                self.watch_source_ids
            ),
            "quiet_source_ids": list(
                self.quiet_source_ids
            ),
            "evidence_hidden_by_default": (
                self.evidence_hidden_by_default
            ),
            "persistent_state_mutated": (
                self.persistent_state_mutated
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
            "boundary_notice": (
                self.boundary_notice
            ),
        }


def filter_detail_experiences(
    experiences: Iterable[
        OwnerCommandDetailExperience
    ],
    *,
    source_id: str | None = None,
    drawer_kind: str | None = None,
    action: str | None = None,
):
    result = []

    for experience in experiences:
        if (
            source_id is not None
            and experience.source_id
            != source_id
        ):
            continue

        if drawer_kind is not None:
            if not any(
                drawer.kind == drawer_kind
                for drawer
                in experience.drawers
            ):
                continue

        if action is not None:
            if not any(
                step.action == action
                for step
                in experience.guided_steps
            ):
                continue

        result.append(experience)

    return tuple(result)
