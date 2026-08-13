"""
The Clouds — Executive Owner Handoff Request Owner Decision /
Submission Authorization contracts.

GP014 records owner-side decision state and whether a draft is
authorized for later submission.

It does not submit or deliver anything.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable


class OwnerHandoffDecision(str, Enum):
    APPROVE = "approve"
    DECLINE = "decline"
    HOLD = "hold"
    UNDECIDED = "undecided"


class SubmissionAuthorizationState(str, Enum):
    AUTHORIZED = "authorized"
    NOT_AUTHORIZED = "not_authorized"
    HELD = "held"
    DECLINED = "declined"


class OwnerReviewConfirmationState(str, Enum):
    CONFIRMED = "confirmed"
    NOT_CONFIRMED = "not_confirmed"


@dataclass(frozen=True)
class OwnerHandoffDecisionRecord:
    decision_id: str
    draft_id: str
    envelope_id: str

    decision: str
    review_confirmation: str

    owner_reviewed_destination: bool
    owner_reviewed_permission_requirement: bool
    owner_reviewed_step_up_requirement: bool
    owner_reviewed_boundary_notice: bool

    decision_recorded: bool
    approval_recorded: bool
    decline_recorded: bool
    hold_recorded: bool

    source_integrity_verified: bool

    submission_authorized: bool
    delivery_performed: bool
    tower_request_created: bool
    handoff_executed: bool
    downstream_execution_performed: bool

    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "draft_id": self.draft_id,
            "envelope_id": self.envelope_id,
            "decision": self.decision,
            "review_confirmation": (
                self.review_confirmation
            ),
            "owner_reviewed_destination": (
                self.owner_reviewed_destination
            ),
            "owner_reviewed_permission_requirement": (
                self.owner_reviewed_permission_requirement
            ),
            "owner_reviewed_step_up_requirement": (
                self.owner_reviewed_step_up_requirement
            ),
            "owner_reviewed_boundary_notice": (
                self.owner_reviewed_boundary_notice
            ),
            "decision_recorded": (
                self.decision_recorded
            ),
            "approval_recorded": (
                self.approval_recorded
            ),
            "decline_recorded": (
                self.decline_recorded
            ),
            "hold_recorded": (
                self.hold_recorded
            ),
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "submission_authorized": (
                self.submission_authorized
            ),
            "delivery_performed": (
                self.delivery_performed
            ),
            "tower_request_created": (
                self.tower_request_created
            ),
            "handoff_executed": (
                self.handoff_executed
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class SubmissionAuthorizationRecord:
    authorization_id: str
    draft_id: str
    envelope_id: str
    decision_id: str

    state: str

    owner_decision: str
    owner_review_confirmed: bool

    draft_integrity_verified: bool
    envelope_integrity_verified: bool

    owner_permission_requirement_preserved: bool
    step_up_requirement_preserved: bool
    tower_boundary_preserved: bool

    submission_authorized: bool

    tower_request_created: bool
    delivery_performed: bool
    tower_receipt_created: bool
    handoff_executed: bool
    downstream_execution_performed: bool

    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "draft_id": self.draft_id,
            "envelope_id": self.envelope_id,
            "decision_id": self.decision_id,
            "state": self.state,
            "owner_decision": self.owner_decision,
            "owner_review_confirmed": (
                self.owner_review_confirmed
            ),
            "draft_integrity_verified": (
                self.draft_integrity_verified
            ),
            "envelope_integrity_verified": (
                self.envelope_integrity_verified
            ),
            "owner_permission_requirement_preserved": (
                self.owner_permission_requirement_preserved
            ),
            "step_up_requirement_preserved": (
                self.step_up_requirement_preserved
            ),
            "tower_boundary_preserved": (
                self.tower_boundary_preserved
            ),
            "submission_authorized": (
                self.submission_authorized
            ),
            "tower_request_created": (
                self.tower_request_created
            ),
            "delivery_performed": (
                self.delivery_performed
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
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class OwnerHandoffAuthorizationSurface:
    title: str
    subtitle: str

    decisions: tuple[
        OwnerHandoffDecisionRecord,
        ...
    ]

    authorizations: tuple[
        SubmissionAuthorizationRecord,
        ...
    ]

    decision_count: int
    authorized_count: int
    declined_count: int
    held_count: int

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "decisions": [
                decision.to_dict()
                for decision in self.decisions
            ],
            "authorizations": [
                authorization.to_dict()
                for authorization
                in self.authorizations
            ],
            "decision_count": (
                self.decision_count
            ),
            "authorized_count": (
                self.authorized_count
            ),
            "declined_count": (
                self.declined_count
            ),
            "held_count": (
                self.held_count
            ),
            "boundary_notice": (
                self.boundary_notice
            ),
        }


def filter_authorizations(
    records: Iterable[
        SubmissionAuthorizationRecord
    ],
    *,
    state: str | None = None,
    submission_authorized: bool | None = None,
    owner_decision: str | None = None,
) -> tuple[
    SubmissionAuthorizationRecord,
    ...
]:
    result = []

    for record in records:
        if (
            state is not None
            and record.state != state
        ):
            continue

        if (
            submission_authorized is not None
            and record.submission_authorized
            is not submission_authorized
        ):
            continue

        if (
            owner_decision is not None
            and record.owner_decision
            != owner_decision
        ):
            continue

        result.append(record)

    return tuple(result)
