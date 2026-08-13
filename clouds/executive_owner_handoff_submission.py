"""
The Clouds — Executive Owner Handoff Submission /
Tower Intake Preparation contracts.

Submission preparation is not Tower delivery.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class SubmissionPreparationState(str, Enum):
    READY = "ready"
    BLOCKED = "blocked"


class TowerIntakeRequirementKind(str, Enum):
    OWNER_APPROVAL = "owner_approval"
    SUBMISSION_AUTHORIZATION = "submission_authorization"
    DESTINATION = "destination"
    PERMISSION = "permission"
    STEP_UP = "step_up"
    INTEGRITY = "integrity"


@dataclass(frozen=True)
class TowerIntakeRequirement:
    requirement_id: str
    kind: str
    label: str
    required: bool
    preserved: bool
    satisfied_for_preparation: bool
    explanation: str
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "kind": self.kind,
            "label": self.label,
            "required": self.required,
            "preserved": self.preserved,
            "satisfied_for_preparation": (
                self.satisfied_for_preparation
            ),
            "explanation": self.explanation,
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class HandoffSubmissionPacket:
    submission_id: str

    authorization_id: str
    decision_id: str
    draft_id: str
    envelope_id: str

    destination_id: str
    open_route: str

    owner_decision: str
    owner_review_confirmed: bool
    submission_authorized: bool

    requires_owner_permission: bool
    requires_step_up: bool

    source_integrity_verified: bool
    tower_boundary_preserved: bool

    requirements: tuple[
        TowerIntakeRequirement,
        ...
    ]

    preparation_state: str
    submission_hash: str

    tower_request_created: bool
    delivered_to_tower: bool
    tower_receipt_created: bool
    handoff_executed: bool
    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "submission_id": self.submission_id,
            "authorization_id": self.authorization_id,
            "decision_id": self.decision_id,
            "draft_id": self.draft_id,
            "envelope_id": self.envelope_id,
            "destination_id": self.destination_id,
            "open_route": self.open_route,
            "owner_decision": self.owner_decision,
            "owner_review_confirmed": (
                self.owner_review_confirmed
            ),
            "submission_authorized": (
                self.submission_authorized
            ),
            "requires_owner_permission": (
                self.requires_owner_permission
            ),
            "requires_step_up": (
                self.requires_step_up
            ),
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "tower_boundary_preserved": (
                self.tower_boundary_preserved
            ),
            "requirements": [
                item.to_dict()
                for item in self.requirements
            ],
            "preparation_state": (
                self.preparation_state
            ),
            "submission_hash": self.submission_hash,
            "tower_request_created": (
                self.tower_request_created
            ),
            "delivered_to_tower": (
                self.delivered_to_tower
            ),
            "tower_receipt_created": (
                self.tower_receipt_created
            ),
            "handoff_executed": (
                self.handoff_executed
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
        }


@dataclass(frozen=True)
class TowerIntakePreparationSurface:
    title: str
    subtitle: str

    submissions: tuple[
        HandoffSubmissionPacket,
        ...
    ]

    submission_count: int
    ready_count: int
    blocked_count: int

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "submissions": [
                item.to_dict()
                for item in self.submissions
            ],
            "submission_count": self.submission_count,
            "ready_count": self.ready_count,
            "blocked_count": self.blocked_count,
            "boundary_notice": self.boundary_notice,
        }
