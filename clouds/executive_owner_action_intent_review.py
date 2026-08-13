"""
The Clouds — Executive Owner Action Intent Review /
Handoff Preparation contracts.

GP012 prepares a read-only review packet describing what
would need to happen next.

Preparation is not approval.
Preparation is not authorization.
Preparation is not execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable


class IntentReviewState(str, Enum):
    READY_FOR_OWNER_REVIEW = "ready_for_owner_review"
    TOWER_HANDOFF_PREPARED = "tower_handoff_prepared"
    INTERNAL_REVIEW_PREPARED = "internal_review_prepared"
    BLOCKED = "blocked"
    RESERVED = "reserved"
    NO_ACTION_REQUIRED = "no_action_required"


class HandoffPreparationState(str, Enum):
    PREPARED = "prepared"
    NOT_PREPARED = "not_prepared"
    NOT_REQUIRED = "not_required"


class IntentReviewAuthority(str, Enum):
    CLOUDS = "clouds"
    OWNER = "owner"
    TOWER = "tower"
    DOWNSTREAM_APPLICATION = "downstream_application"
    NONE = "none"


class IntentReviewDecision(str, Enum):
    UNDECIDED = "undecided"


@dataclass(frozen=True)
class ReviewRequirement:
    requirement_id: str
    label: str
    required: bool
    satisfied_for_preparation: bool
    authority: str
    explanation: str
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "label": self.label,
            "required": self.required,
            "satisfied_for_preparation": (
                self.satisfied_for_preparation
            ),
            "authority": self.authority,
            "explanation": self.explanation,
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class ReviewBlocker:
    blocker_id: str
    label: str
    explanation: str
    authority: str
    blocks_preparation: bool
    resolvable_in_clouds: bool
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "blocker_id": self.blocker_id,
            "label": self.label,
            "explanation": self.explanation,
            "authority": self.authority,
            "blocks_preparation": self.blocks_preparation,
            "resolvable_in_clouds": (
                self.resolvable_in_clouds
            ),
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class HandoffPreparation:
    preparation_id: str

    state: str

    destination_id: str | None
    open_route: str | None
    navigation_mode: str

    requires_tower: bool
    requires_owner_permission: bool
    requires_step_up: bool

    tower_authority_required: bool
    downstream_authority_required: bool

    owner_approval_recorded: bool
    tower_request_created: bool
    tower_handoff_executed: bool
    downstream_execution_performed: bool

    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "preparation_id": self.preparation_id,
            "state": self.state,
            "destination_id": self.destination_id,
            "open_route": self.open_route,
            "navigation_mode": self.navigation_mode,
            "requires_tower": self.requires_tower,
            "requires_owner_permission": (
                self.requires_owner_permission
            ),
            "requires_step_up": self.requires_step_up,
            "tower_authority_required": (
                self.tower_authority_required
            ),
            "downstream_authority_required": (
                self.downstream_authority_required
            ),
            "owner_approval_recorded": (
                self.owner_approval_recorded
            ),
            "tower_request_created": (
                self.tower_request_created
            ),
            "tower_handoff_executed": (
                self.tower_handoff_executed
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class OwnerIntentReviewPacket:
    review_id: str
    item_id: str
    intent_id: str

    title: str
    summary: str

    what_is_being_considered: str
    why_owner_review_matters: str
    prepared_next_step: str

    review_state: str
    preparation_state: str
    decision: str

    authority: str

    source_section_id: str | None
    source_app_id: str | None
    source_lane_id: str | None

    requirements: tuple[
        ReviewRequirement,
        ...
    ]

    blockers: tuple[
        ReviewBlocker,
        ...
    ]

    handoff_preparation: HandoffPreparation

    owner_review_questions: tuple[str, ...]

    source_integrity_verified: bool
    owner_approval_recorded: bool
    tower_request_created: bool
    execution_performed: bool

    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "review_id": self.review_id,
            "item_id": self.item_id,
            "intent_id": self.intent_id,
            "title": self.title,
            "summary": self.summary,
            "what_is_being_considered": (
                self.what_is_being_considered
            ),
            "why_owner_review_matters": (
                self.why_owner_review_matters
            ),
            "prepared_next_step": (
                self.prepared_next_step
            ),
            "review_state": self.review_state,
            "preparation_state": self.preparation_state,
            "decision": self.decision,
            "authority": self.authority,
            "source_section_id": self.source_section_id,
            "source_app_id": self.source_app_id,
            "source_lane_id": self.source_lane_id,
            "requirements": [
                requirement.to_dict()
                for requirement
                in self.requirements
            ],
            "blockers": [
                blocker.to_dict()
                for blocker
                in self.blockers
            ],
            "handoff_preparation": (
                self.handoff_preparation.to_dict()
            ),
            "owner_review_questions": list(
                self.owner_review_questions
            ),
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "owner_approval_recorded": (
                self.owner_approval_recorded
            ),
            "tower_request_created": (
                self.tower_request_created
            ),
            "execution_performed": (
                self.execution_performed
            ),
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class OwnerIntentReviewSurface:
    title: str
    subtitle: str

    reviews: tuple[
        OwnerIntentReviewPacket,
        ...
    ]

    review_count: int
    prepared_count: int
    tower_prepared_count: int
    blocked_count: int

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "reviews": [
                review.to_dict()
                for review in self.reviews
            ],
            "review_count": self.review_count,
            "prepared_count": self.prepared_count,
            "tower_prepared_count": (
                self.tower_prepared_count
            ),
            "blocked_count": self.blocked_count,
            "boundary_notice": self.boundary_notice,
        }


def requirement_sort_key(
    requirement: ReviewRequirement,
) -> tuple:
    return (
        requirement.display_order,
        requirement.requirement_id,
    )


def review_blocker_sort_key(
    blocker: ReviewBlocker,
) -> tuple:
    return (
        blocker.display_order,
        blocker.blocker_id,
    )


def review_packet_sort_key(
    review: OwnerIntentReviewPacket,
) -> tuple:
    return (
        review.display_order,
        review.review_id,
    )


def filter_review_packets(
    reviews: Iterable[
        OwnerIntentReviewPacket
    ],
    *,
    review_state: str | None = None,
    preparation_state: str | None = None,
    authority: str | None = None,
    source_app_id: str | None = None,
    source_lane_id: str | None = None,
    requires_tower: bool | None = None,
    blocked: bool | None = None,
) -> tuple[
    OwnerIntentReviewPacket,
    ...
]:
    filtered = []

    for review in reviews:
        if (
            review_state is not None
            and review.review_state
            != review_state
        ):
            continue

        if (
            preparation_state is not None
            and review.preparation_state
            != preparation_state
        ):
            continue

        if (
            authority is not None
            and review.authority
            != authority
        ):
            continue

        if (
            source_app_id is not None
            and review.source_app_id
            != source_app_id
        ):
            continue

        if (
            source_lane_id is not None
            and review.source_lane_id
            != source_lane_id
        ):
            continue

        if (
            requires_tower is not None
            and review
            .handoff_preparation
            .requires_tower
            is not requires_tower
        ):
            continue

        if blocked is not None:
            is_blocked = (
                review.review_state
                == IntentReviewState.BLOCKED.value
            )

            if is_blocked is not blocked:
                continue

        filtered.append(review)

    return tuple(
        sorted(
            filtered,
            key=review_packet_sort_key,
        )
    )
